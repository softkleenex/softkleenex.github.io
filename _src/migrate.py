"""이관 마크다운 18편의 frontmatter를 정규화하고 자기참조 블록을 제거한다.

한 번만 쓰는 스크립트다. 원본은 coding_training 저장소에 그대로 남아 있다.
"""
import json
import re
import sys
from pathlib import Path

SRC = Path(__file__).parent / "posts"
DATA = json.loads((Path(__file__).parent / "posts.json").read_text(encoding="utf-8"))
META = {p["slug"]: p for p in DATA["posts"]}

# 카테고리 → 표시 라벨과 kicker 접두
CAT_LABEL = {
    "DACON": "DACON",
    "Kaggle": "Kaggle",
    "회고": "회고",
    "제작기": "제작기",
    "기획": "공모전",
    "기록": "기록",
}


def strip_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    return {}, text[end + 4 :].lstrip("\n")


def strip_section(body, heading):
    """## heading 부터 다음 ## 또는 문서 끝까지 제거한다."""
    pat = re.compile(
        r"^##[ \t]+" + re.escape(heading) + r"[ \t]*$.*?(?=^##[ \t]|\Z)",
        re.M | re.S,
    )
    return pat.sub("", body)


def clean_body(body):
    body = re.sub(r"^#[ \t]+.*$", "", body, count=1, flags=re.M)  # H1 제거
    body = strip_section(body, "한눈에 보기")
    body = strip_section(body, "연결")
    # 남은 위키링크를 평문으로
    body = re.sub(r"\[\[[^|\]]*\|([^\]]*)\]\]", r"\1", body)
    body = re.sub(r"\[\[([^\]]*)\]\]", r"\1", body)
    # coding_training 자기참조 링크 제거 (마크다운 링크 통째로)
    body = re.sub(
        r"\[[^\]]*\]\(https://softkleenex\.github\.io/coding_training[^)]*\)", "", body
    )
    body = re.sub(r"https://softkleenex\.github\.io/coding_training\S*", "", body)
    # 빈 리스트 항목과 3연속 이상 개행 정리
    body = re.sub(r"^[-*][ \t]*$", "", body, flags=re.M)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


def yaml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_frontmatter(m):
    lines = ["---"]
    lines.append(f"title: {yaml_str(m['title'])}")
    lines.append(f"subtitle: {yaml_str(m['sub'])}")
    lines.append(f"date: {m['date']}")
    lines.append(f"category: {yaml_str(CAT_LABEL.get(m['cat'], m['cat']))}")
    lines.append(f"description: {yaml_str(m.get('description', m['sub']))}")
    if m.get("repo"):
        lines.append(f"repo: {yaml_str(m['repo'])}")
    if m.get("dateBasis"):
        lines.append(f"date_basis: {yaml_str(m['dateBasis'])}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def main():
    changed = 0
    for slug, m in META.items():
        f = SRC / f"{slug}.md"
        if not f.exists():
            print(f"  건너뜀 (파일 없음): {slug}")
            continue
        raw = f.read_text(encoding="utf-8")
        _, body = strip_frontmatter(raw)
        if m["src"] != "root":
            body = clean_body(body)
        else:
            body = re.sub(r"^#[ \t]+.*$", "", body, count=1, flags=re.M).strip() + "\n"
        f.write_text(build_frontmatter(m) + body, encoding="utf-8")
        changed += 1
    print(f"{changed}편 정규화 완료")


if __name__ == "__main__":
    sys.exit(main())
