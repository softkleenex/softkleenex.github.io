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
import struct
import subprocess
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

# 재구축 전에 쓰던 주소. 옛 색인과 외부 링크를 새 주소로 넘긴다.
# GitHub Pages 는 301 을 만들 수 없어 meta refresh + canonical 로 대신한다.
REDIRECTS = {
    "coding_training": "/posts/",
    "blog": "/posts/",
    "blog/dacon-etri-human-understanding": "/posts/dacon-etri-human-understanding/",
    "dacon-etri-human-understanding": "/posts/dacon-etri-human-understanding/",
}

# og:image 후보. 외부 URL 과 SVG 는 제외한다 -
# 카카오·네이버 미리보기가 SVG 를 렌더링하지 않는다.
IMG_RE = re.compile(r"!\[[^\]]*\]\((/assets/[^)\s]+\.(?:png|jpg|jpeg))\)", re.I)


def png_size(path):
    """PNG 헤더에서 가로·세로를 읽는다. og:image:width 를 추측하지 않기 위해서다."""
    try:
        head = path.read_bytes()[:24]
    except OSError:
        return None
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def cover_image(meta, body):
    """frontmatter 의 image 가 우선, 없으면 본문 첫 로컬 이미지를 쓴다."""
    rel = meta.get("image")
    if not rel:
        m = IMG_RE.search(body)
        rel = m.group(1) if m else None
    if not rel:
        return None
    size = png_size(ROOT / rel.lstrip("/"))
    if not size:
        return None
    return {"url": rel, "w": size[0], "h": size[1]}


def git_date(path, fallback):
    """마지막 커밋 날짜. 커밋 전 수정본이면 오늘로 본다.

    sitemap 의 lastmod 가 발행일에 묶여 있으면 본문을 고쳐도
    검색엔진에 재수집 신호가 가지 않는다.
    """
    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        if dirty.returncode == 0 and dirty.stdout.strip():
            return datetime.now(KST).date()
        log = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        if log.returncode == 0 and log.stdout.strip():
            return datetime.strptime(log.stdout.strip(), "%Y-%m-%d").date()
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    return fallback


def read_posts():
    posts = []
    for f in sorted(POSTS.glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            raise SystemExit(f"frontmatter 없음: {f.name}")
        end = raw.find("\n---", 3)
        if end == -1:
            raise SystemExit(f"frontmatter 닫는 --- 없음: {f.name}")
        meta = yaml.safe_load(raw[3:end])
        if not isinstance(meta, dict):
            raise SystemExit(f"frontmatter 파싱 실패: {f.name}")
        for key in ("title", "date", "description"):
            if not meta.get(key):
                raise SystemExit(f"frontmatter 의 {key} 가 비어 있음: {f.name}")
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
                "cover": cover_image(meta, body),
                "updated": git_date(f.relative_to(ROOT), d),
            }
        )
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    for i, p in enumerate(posts):
        p["next"] = posts[i - 1] if i > 0 else None
        p["prev"] = posts[i + 1] if i + 1 < len(posts) else None
    return posts


VALID_CATS = {name for name, _, _ in CATEGORIES}
ANCHORS = {anchor for _, anchor, _ in CATEGORIES}


def check_slugs(posts):
    """슬러그와 카테고리 앵커는 /posts/<name>/ 을 공유한다.

    겹치면 카테고리 페이지가 나중에 쓰여 글 페이지를 덮어쓰는데,
    목록과 피드는 여전히 그 URL 을 글로 링크하므로 조용히 깨진다.
    """
    clash = sorted({p["slug"] for p in posts} & ANCHORS)
    if clash:
        raise SystemExit(
            "슬러그가 카테고리 앵커와 충돌한다: "
            + ", ".join(clash)
            + f"\n예약된 이름: {', '.join(sorted(ANCHORS))}"
        )


def check_categories(posts):
    """오타 하나로 글이 탐색기에서 조용히 사라지는 것을 막는다."""
    bad = [(p["slug"], p["category"]) for p in posts if p["category"] not in VALID_CATS]
    if bad:
        known = ", ".join(sorted(VALID_CATS))
        lines = "\n".join(f"  {s}: {c!r}" for s, c in bad)
        raise SystemExit(f"알 수 없는 category:\n{lines}\n허용: {known}")


def make_groups(posts):
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
    check_categories(posts)
    check_slugs(posts)
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
                twitter_card="summary_large_image" if p["cover"] else "summary",
                og_image=p["cover"]["url"] if p["cover"] else None,
                og_w=p["cover"]["w"] if p["cover"] else None,
                og_h=p["cover"]["h"] if p["cover"] else None,
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

    # 목록 + 카테고리별 페이지
    def by_year_of(items):
        return [
            (y, [p for p in items if p["date"].year == y])
            for y in sorted({p["date"].year for p in items}, reverse=True)
        ]

    def render_list(items, out, url, title, desc, category=None):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            env.get_template("list.html").render(
                site=SITE,
                posts=items,
                by_year=by_year_of(items),
                groups=groups,
                category=category,
                current=None,
                page_title=title,
                description=desc,
                url=url,
                nav="posts",
                # 카테고리는 /posts/ 의 부분집합이라 중복으로 잡힌다.
                # 링크는 계속 따라가도록 follow 는 남긴다.
                robots="noindex,follow" if category else "index,follow",
                jsonld=[
                    ld(
                        {
                            "@context": "https://schema.org",
                            "@type": "CollectionPage",
                            "name": category["name"] if category else "글 목록",
                            "url": f"{SITE['url']}{url}",
                            "inLanguage": "ko-KR",
                            "isPartOf": {"@id": f"{SITE['url']}/#website"},
                            "mainEntity": {
                                "@type": "ItemList",
                                "itemListOrder": "https://schema.org/ItemListOrderDescending",
                                "numberOfItems": len(items),
                                "itemListElement": [
                                    {
                                        "@type": "ListItem",
                                        "position": i + 1,
                                        "url": f"{SITE['url']}/posts/{p['slug']}/",
                                        "name": p["title"],
                                    }
                                    for i, p in enumerate(items)
                                ],
                            },
                        }
                    ),
                    jsonld_crumbs(
                        [("홈", f"{SITE['url']}/"), ("글", f"{SITE['url']}/posts/"), (category["name"], None)]
                        if category
                        else [("홈", f"{SITE['url']}/"), ("글", None)]
                    ),
                ],
            ),
            encoding="utf-8",
        )

    render_list(
        posts,
        ROOT / "posts" / "index.html",
        "/posts/",
        f"글 목록 | {SITE['title']}",
        f"{SITE['title']}에 쓴 대회 회고와 제작기 {len(posts)}편 전체 목록입니다.",
    )
    for g in groups:
        render_list(
            g["posts"],
            ROOT / "posts" / g["anchor"] / "index.html",
            f"/posts/{g['anchor']}/",
            f"{g['name']} | {SITE['title']}",
            f"{g['blurb']}. {SITE['title']}의 {g['name']} 글 {len(g['posts'])}편.",
            category=g,
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
    latest = max(p["updated"] for p in posts)
    urls = [("/", "weekly", "1.0", latest), ("/posts/", "weekly", "0.9", latest)]
    # 카테고리 목록은 noindex 라 사이트맵에 넣지 않는다. 색인 요청과 모순된다.
    urls += [(f"/posts/{p['slug']}/", "monthly", "0.8", p["updated"]) for p in posts]
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

    # 404 페이지. 개편 전 주소를 새 주소로 넘기는 마지막 그물이다.
    (ROOT / "404.html").write_text(
        env.get_template("404.html").render(
            site=SITE,
            recent=posts[:3],
            groups=groups,
            current=None,
            page_title=f"페이지를 찾을 수 없습니다 | {SITE['title']}",
            description="주소가 바뀌었거나 삭제된 페이지입니다.",
            url="/404.html",
            robots="noindex,follow",
            nav=None,
            jsonld=[],
            slugs=json.dumps([p["slug"] for p in posts], ensure_ascii=False),
        ),
        encoding="utf-8",
    )

    # 옛 주소 리다이렉트
    for src, dst in REDIRECTS.items():
        out = ROOT / src / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex,follow">
    <meta http-equiv="refresh" content="0; url={dst}">
    <link rel="canonical" href="{SITE['url']}{dst}">
    <title>Redirecting | Softkleenex</title>
</head>
<body>
    <p>Moved to <a href="{dst}">{dst}</a>.</p>
</body>
</html>
""",
            encoding="utf-8",
        )

    known = {p["slug"] for p in posts} | {g["anchor"] for g in groups}
    orphans = [
        d.name
        for d in (ROOT / "posts").iterdir()
        if d.is_dir() and d.name not in known
    ]
    if orphans:
        print("\n[경고] 사이트맵·목록·탐색기에 없는 고아 페이지가 남아 있다:")
        for o in sorted(orphans):
            print(f"  posts/{o}/")
        print("  제거: /usr/bin/trash " + " ".join(f"posts/{o}" for o in sorted(orphans)))

    print(f"글 {len(posts)}편")
    for g in groups:
        print(f"  {g['name']:<8} {len(g['posts'])}편")
    print("생성: 404.html")
    print(f"리다이렉트 {len(REDIRECTS)}개: " + ", ".join(f"/{k}/" for k in REDIRECTS))
    print(f"생성: index.html, posts/index.html, posts/*/index.html, feed.xml, sitemap.xml")


if __name__ == "__main__":
    main()
