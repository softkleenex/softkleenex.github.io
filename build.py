#!/usr/bin/env python3
"""Softkleenex Archive 정적 사이트 생성기.

_src/posts/*.md 의 frontmatter를 단일 진실원으로 삼아
글 페이지, 홈, 목록, RSS, 사이트맵을 모두 생성한다.

    ./.venv/bin/python build.py

제목을 고칠 때는 마크다운 frontmatter만 고치면 된다.
HTML, RSS, 사이트맵은 전부 여기서 파생된다.
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
SRC = ROOT / "_src"
POSTS = SRC / "posts"
KST = timezone(timedelta(hours=9))

SITE = {
    "url": "https://softkleenex.github.io",
    "title": "Softkleenex Archive",
    "desc": "AI 대회 회고와 생성형 디자인 제작기. 결과보다 어디서 막혔는지를 남깁니다.",
    "adsense": "ca-pub-8567091536004202",
    "naver": "07d8e8da57a2f02b48c11e909923ec67",
    "year": 2026,
}

# 탐색기와 홈에서 쓰는 카테고리 순서·설명
CATEGORIES = [
    ("DACON", "dacon", "국내 AI 경진대회 회고"),
    ("Kaggle", "kaggle", "해외 대회와 자동화 실험"),
    ("대회", "competition", "NYPC와 양자 AI 대회"),
    ("공모전", "contest", "기획과 디자인 출품작"),
    ("기록", "notes", "운영 방식과 템플릿"),
]

ACCENT = {"2026-the-color-house": "rose"}


def read_posts():
    posts = []
    for f in sorted(POSTS.glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            raise SystemExit(f"frontmatter 없음: {f.name}")
        end = raw.find("\n---", 3)
        meta = yaml.safe_load(raw[3:end])
        body = raw[end + 4 :].lstrip("\n")

        md = markdown.Markdown(
            extensions=["tables", "fenced_code", "attr_list", "sane_lists", "footnotes"]
        )
        html = md.convert(body)
        html = re.sub(r"<table>", '<div class="table-wrap"><table>', html)
        html = re.sub(r"</table>", "</table></div>", html)

        d = meta["date"]
        if isinstance(d, str):
            d = datetime.strptime(d, "%Y-%m-%d").date()

        posts.append(
            {
                "slug": f.stem,
                "title": meta["title"],
                "subtitle": meta.get("subtitle", ""),
                "description": meta["description"],
                "category": meta.get("category", "기록"),
                "repo": meta.get("repo"),
                "date": d,
                "date_ko": f"{d.year}년 {d.month}월 {d.day}일",
                "html": html,
                "accent": ACCENT.get(f.stem),
            }
        )
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    for i, p in enumerate(posts):
        p["next"] = posts[i - 1] if i > 0 else None
        p["prev"] = posts[i + 1] if i + 1 < len(posts) else None
    return posts


def make_groups(posts, current=None):
    groups = []
    for name, anchor, blurb in CATEGORIES:
        items = [p for p in posts if p["category"] == name]
        if items:
            groups.append(
                {"name": name, "anchor": anchor, "blurb": blurb, "posts": items}
            )
    return groups


def jsonld_graph():
    return ld(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Person",
                    "@id": f"{SITE['url']}/#person",
                    "name": "softkleenex",
                    "url": SITE["url"],
                },
                {
                    "@type": "WebSite",
                    "@id": f"{SITE['url']}/#website",
                    "url": SITE["url"],
                    "name": SITE["title"],
                    "description": SITE["desc"],
                    "inLanguage": "ko-KR",
                    "publisher": {"@id": f"{SITE['url']}/#person"},
                },
                {
                    "@type": "Blog",
                    "@id": f"{SITE['url']}/#blog",
                    "url": f"{SITE['url']}/posts/",
                    "name": SITE["title"],
                    "isPartOf": {"@id": f"{SITE['url']}/#website"},
                },
            ],
        }
    )


def jsonld_post(p):
    return ld(
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": p["title"],
            "alternativeHeadline": p["subtitle"],
            "description": p["description"],
            "datePublished": str(p["date"]),
            "inLanguage": "ko-KR",
            "url": f"{SITE['url']}/posts/{p['slug']}/",
            "mainEntityOfPage": {"@id": f"{SITE['url']}/posts/{p['slug']}/"},
            "author": {"@id": f"{SITE['url']}/#person"},
            "publisher": {"@id": f"{SITE['url']}/#person"},
            "isPartOf": {"@id": f"{SITE['url']}/#blog"},
            "image": f"{SITE['url']}/assets/softkleenex-avatar.png",
        }
    )


def jsonld_crumbs(items):
    return ld(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": name,
                    **({"item": url} if url else {}),
                }
                for i, (name, url) in enumerate(items)
            ],
        }
    )


def ld(obj):
    """JSON-LD를 <script> 안에 안전하게 넣는다. </script> 조기 종료를 막는다."""
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def rfc822(d):
    return datetime(d.year, d.month, d.day, 9, 0, 0, tzinfo=KST).strftime(
        "%a, %d %b %Y %H:%M:%S %z"
    )


def esc(s):
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def main():
    posts = read_posts()
    groups = make_groups(posts)
    env = Environment(
        loader=FileSystemLoader(SRC / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=False,
        lstrip_blocks=False,
    )

    # 글 페이지
    for p in posts:
        out = ROOT / "posts" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        ctx = dict(p)
        out.write_text(
            env.get_template("post.html").render(
                site=SITE,
                post=ctx,
                groups=groups,
                current=p["slug"],
                page_title=f"{p['title']} | {SITE['title']}",
                description=p["description"],
                url=f"/posts/{p['slug']}/",
                og_type="article",
                published=str(p["date"]),
                twitter_card="summary",
                accent=p["accent"],
                nav="posts",
                jsonld=[
                    jsonld_post(p),
                    jsonld_crumbs(
                        [
                            ("홈", f"{SITE['url']}/"),
                            ("글", f"{SITE['url']}/posts/"),
                            (p["title"], None),
                        ]
                    ),
                ],
            ),
            encoding="utf-8",
        )

    # 목록
    by_year = []
    for y in sorted({p["date"].year for p in posts}, reverse=True):
        by_year.append((y, [p for p in posts if p["date"].year == y]))
    (ROOT / "posts").mkdir(exist_ok=True)
    (ROOT / "posts" / "index.html").write_text(
        env.get_template("list.html").render(
            site=SITE,
            posts=posts,
            by_year=by_year,
            groups=groups,
            current=None,
            page_title=f"글 목록 | {SITE['title']}",
            description=f"{SITE['title']}에 쓴 대회 회고와 제작기 {len(posts)}편 전체 목록입니다.",
            url="/posts/",
            nav="posts",
            jsonld=[
                ld(
                    {
                        "@context": "https://schema.org",
                        "@type": "CollectionPage",
                        "name": "글 목록",
                        "url": f"{SITE['url']}/posts/",
                        "inLanguage": "ko-KR",
                        "isPartOf": {"@id": f"{SITE['url']}/#website"},
                        "mainEntity": {
                            "@type": "ItemList",
                            "itemListOrder": "https://schema.org/ItemListOrderDescending",
                            "numberOfItems": len(posts),
                            "itemListElement": [
                                {
                                    "@type": "ListItem",
                                    "position": i + 1,
                                    "url": f"{SITE['url']}/posts/{p['slug']}/",
                                    "name": p["title"],
                                }
                                for i, p in enumerate(posts)
                            ],
                        },
                    }
                ),
                jsonld_crumbs([("홈", f"{SITE['url']}/"), ("글", None)]),
            ],
        ),
        encoding="utf-8",
    )

    # 홈
    (ROOT / "index.html").write_text(
        env.get_template("home.html").render(
            site=SITE,
            posts=posts,
            recent=posts[:3],
            groups=groups,
            current=None,
            page_title=f"{SITE['title']} | AI 대회 회고와 제작기",
            description=SITE["desc"],
            url="/",
            nav="home",
            jsonld=[jsonld_graph()],
        ),
        encoding="utf-8",
    )

    # RSS
    items = "\n".join(
        f"""    <item>
      <title>{esc(p['title'])}</title>
      <link>{SITE['url']}/posts/{p['slug']}/</link>
      <guid isPermaLink="true">{SITE['url']}/posts/{p['slug']}/</guid>
      <pubDate>{rfc822(p['date'])}</pubDate>
      <category>{esc(p['category'])}</category>
      <description>{esc(p['description'])}</description>
    </item>"""
        for p in posts
    )
    (ROOT / "feed.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SITE['title']}</title>
    <link>{SITE['url']}/</link>
    <description>{esc(SITE['desc'])}</description>
    <language>ko</language>
    <copyright>© {SITE['year']} Softkleenex</copyright>
    <lastBuildDate>{rfc822(posts[0]['date'])}</lastBuildDate>
    <atom:link href="{SITE['url']}/feed.xml" rel="self" type="application/rss+xml" />
    <image>
      <url>{SITE['url']}/assets/softkleenex-avatar.png</url>
      <title>{SITE['title']}</title>
      <link>{SITE['url']}/</link>
    </image>
{items}
  </channel>
</rss>
""",
        encoding="utf-8",
    )

    # 사이트맵
    urls = [("/", "weekly", "1.0", posts[0]["date"]), ("/posts/", "weekly", "0.9", posts[0]["date"])]
    urls += [(f"/posts/{p['slug']}/", "monthly", "0.8", p["date"]) for p in posts]
    body = "\n".join(
        f"""  <url>
    <loc>{SITE['url']}{loc}</loc>
    <lastmod>{d}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>"""
        for loc, freq, pri, d in urls
    )
    (ROOT / "sitemap.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
""",
        encoding="utf-8",
    )

    print(f"글 {len(posts)}편")
    for g in groups:
        print(f"  {g['name']:<8} {len(g['posts'])}편")
    print(f"생성: index.html, posts/index.html, posts/*/index.html, feed.xml, sitemap.xml")


if __name__ == "__main__":
    main()
