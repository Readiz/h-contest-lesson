"""Check the `heuristic` map hub and the `heuristic-case-studies` hub.

The map hub must keep its figure to the shared figure rules, link all nine method
lessons and the case-study lesson (every id must exist in lessons.json), and name
site problems only in the "적용 사례" column of the selection table and in the
sentence right below that table. The case-study hub must list its four pages.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METHOD_IDS = [
    "problem-modeling", "construction-heuristics", "neighborhood-and-delta",
    "hill-climbing-and-annealing", "beam-search", "destroy-and-repair",
    "candidate-and-time-budget", "partial-information", "experiments-and-tuning",
]
CASE_ID = "heuristic-case-studies"
CASE_PAGES = ["ordering-route-improvement", "search-strategies", "placement-and-repair", "aircontech-beam-search"]
FIGURE = "lesson-assets/method-map.svg"
LEARN_RE = re.compile(r"https://h\.readiz\.com/learn/([a-z0-9-]+)")
PROBLEM_NAME_RE = re.compile(r"\b[A-Z]{5,}[0-9]?\b")


def manifest_ids() -> set[str]:
    data = json.loads((ROOT / "lessons.json").read_text(encoding="utf-8"))
    return {lesson["lessonId"] for lesson in data["lessons"]}


def check_figure(hub: str) -> None:
    path = ROOT / "lessons/heuristic" / FIGURE
    svg = path.read_text(encoding="utf-8")
    match = re.search(r'viewBox="0 0 720 (\d+)"', svg)
    assert match, "method-map.svg: viewBox width must be 720"
    height = int(match.group(1))
    assert 'role="img"' in svg and "<title" in svg and "<desc" in svg, "method-map.svg: role/title/desc"
    sizes = [float(v) for v in re.findall(r'font-size="([\d.]+)"', svg)]
    assert sizes and min(sizes) >= 16 and max(sizes) <= 28, ("method-map.svg font sizes", min(sizes), max(sizes))
    assert 27 in sizes, "method-map.svg: title must be 27px"
    colors = set(re.findall(r'(?:fill|stroke)="(#[0-9a-fA-F]{6})"', svg))
    assert len(colors) <= 8, f"method-map.svg: too many colors {sorted(colors)}"
    for m in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)" font-size="([\d.]+)"([^>]*)>([^<]*)</text>', svg):
        x, y, size, attrs, body = float(m[1]), float(m[2]), float(m[3]), m[4], m[5]
        width = sum(size * (1.0 if ord(ch) > 0x2E80 else 0.55) for ch in body)
        if 'text-anchor="end"' in attrs:
            left, right = x - width, x
        elif 'text-anchor="middle"' in attrs:
            left, right = x - width / 2, x + width / 2
        else:
            left, right = x, x + width
        assert left >= 8 and right <= 712 and y <= height - 4, f"method-map.svg: text may leave the figure: {body!r}"
    images = re.findall(r"!\[([^\]]*)\]\(([^)\s]+)\)", hub)
    assert [path for _, path in images] == [FIGURE], images
    assert images[0][0].strip(), "method-map.svg: alt text is empty"
    big = f"[그림 크게 보기](https://git.readiz.com/h-contest-lesson/lessons/heuristic/{FIGURE})"
    assert big in hub, "missing '그림 크게 보기' link line"


def table_and_after(hub: str) -> tuple[list[str], str, str]:
    """Rows of the selection table, the paragraph right below it, and the hub text without them."""
    lines = hub.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("## 탐색 방법 고르기"))
    first = next(i for i in range(start, len(lines)) if lines[i].startswith("|"))
    last = first
    while last + 1 < len(lines) and lines[last + 1].startswith("|"):
        last += 1
    rows = lines[first + 2:last + 1]
    after_index = next(i for i in range(last + 1, len(lines)) if lines[i].strip())
    stripped = ["|".join(row.split("|")[:-2]) + "|" for row in rows]
    rest = lines[:first + 2] + stripped + lines[last + 1:after_index] + lines[after_index + 1:]
    return rows, lines[after_index], "\n".join(rest)


def check_map_hub() -> None:
    hub = (ROOT / "lessons/heuristic/lesson.md").read_text(encoding="utf-8")
    count = len(hub.rstrip("\n").splitlines())
    assert 60 <= count <= 110, f"heuristic hub has {count} lines"
    assert hub.startswith("# 휴리스틱 방법론 지도\n"), "heuristic hub title"
    assert "demo=" not in hub, "the map hub must not contain demo cards"
    ids = manifest_ids()
    linked = set(LEARN_RE.findall(hub))
    for lesson_id in METHOD_IDS + [CASE_ID]:
        assert lesson_id in linked, f"heuristic hub does not link {lesson_id}"
    for lesson_id in linked:
        assert lesson_id in ids, f"heuristic hub links a lesson that is not in lessons.json: {lesson_id}"
    check_figure(hub)
    rows, after, rest = table_and_after(hub)
    assert len(rows) == 5, f"selection table must have 5 rows, found {len(rows)}"
    for row in rows:
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        assert len(cells) == 4, row
        assert any(f"/learn/{i}" in cells[2] for i in METHOD_IDS), f"row has no method lesson link: {row[:40]}"
    names = sorted(set(PROBLEM_NAME_RE.findall(rest)))
    assert not names, f"problem names outside the selection table and its next sentence: {names}"
    assert after.strip(), "the sentence below the table is missing"


def check_case_hub() -> None:
    hub = (ROOT / "lessons" / CASE_ID / "lesson.md").read_text(encoding="utf-8")
    count = len(hub.rstrip("\n").splitlines())
    assert 30 <= count <= 45, f"{CASE_ID} hub has {count} lines"
    for page in CASE_PAGES:
        assert (ROOT / "lessons" / CASE_ID / "pages" / f"{page}.md").exists(), page
        assert f"pages/{page}.md" in hub, f"{CASE_ID} hub does not link {page}"
    for lesson_id in LEARN_RE.findall(hub):
        assert lesson_id in manifest_ids(), lesson_id
    data = json.loads((ROOT / "lessons.json").read_text(encoding="utf-8"))
    by_id = {lesson["lessonId"]: lesson for lesson in data["lessons"]}
    assert [p["pageId"] for p in by_id[CASE_ID]["pages"]] == CASE_PAGES
    assert by_id["heuristic"]["pages"] == [], "heuristic map has no sub pages"
    assert "method" not in by_id[CASE_ID]["tags"]


def main() -> None:
    check_map_hub()
    check_case_hub()
    print("OK: heuristic map hub and case-study hub")


if __name__ == "__main__":
    main()
