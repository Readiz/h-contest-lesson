from __future__ import annotations

import argparse
import difflib
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS_JSON = ROOT / "lessons.json"
README = ROOT / "README.md"
INDEX = ROOT / "index.html"


README_HEADER = """# h-contest heuristic notes

This repository is the source of truth for h-contest heuristic notes. Lesson source lives in `lessons/` and `lessons.json`; `README.md` and `index.html` are generated entry points.

## 탐색

- 전체 카탈로그: [index.html](index.html)
- Published manifest: https://blog.readiz.com/h-contest-lesson/lessons.json
- API mirror: https://h.readiz.com/api/lessons
- 공개 기록: [CHANGELOG.md](CHANGELOG.md)
- 미공개 후보와 practice TODO: [ROADMAP.md](ROADMAP.md)
- 기여 절차: [CONTRIBUTING.md](CONTRIBUTING.md)

## 작업 흐름

1. `lessons/<lessonId>/lesson.md`와 필요 시 `lessons/<lessonId>/pages/*.md`를 수정합니다.
2. `lessons.json`에서 metadata, page 목록, 선수/다음/연관 레슨을 맞춥니다.
3. 아래 명령으로 파생 파일과 검증 상태를 맞춥니다.

```bash
python3 scripts/generate_catalog.py
python3 scripts/validate_lessons.py
```

이미지나 보조 자료는 `lessons/<lessonId>/lesson-assets/`에 둡니다.

## 학습 로드맵

처음 보는 주제라면 아래 순서로 훑는 것을 권장합니다. 이미 익숙한 내용은 건너뛰고, 각 레슨의 `prerequisites`와 `nextLessons` 메타데이터를 참고해 앞뒤 개념을 확인하세요.

1. 입문 0단계: 복잡도 감각, 대회용 C++ 기본기
2. 입문 1단계: 정렬, 누적합, 이분 탐색, 투 포인터
3. 입문 2단계: BFS/DFS, 그리디, 우선순위 큐, Union-Find, 좌표 압축
4. 중급 1단계: DP, Dijkstra, 위상 정렬, Fenwick Tree, Segment Tree, 모듈러 연산
5. 중급 2단계: 트리 심화, TSP, Treap, 휴리스틱
6. 심화 확장: 문자열 매칭, SCC/2-SAT, Flow, 정수론 심화, 기하, 오프라인 쿼리, 검증/증명
7. 참고 노트: 현재 문제 대비 우선순위는 낮지만 휴리스틱 아이디어 확장에 도움이 되는 연구/레퍼런스 주제

"""


QUICK_GUIDES = [
    {
        "title": "구간 질의/업데이트",
        "description": "질의가 많은 문제에서 온라인/오프라인, 업데이트, 좌표 크기, 시간축을 먼저 나눕니다.",
        "rows": [
            ("정적 구간 합", ["prefix-sum-difference"]),
            ("점 업데이트 + 구간 질의", ["fenwick-tree", "segment-tree"], " / "),
            ("구간 업데이트/블록 처리", ["segment-tree", "sqrt-decomposition"], " / "),
            ("좌표가 크다", ["coordinate-compression", "dynamic-segment-tree"], " / "),
            ("질의를 재정렬할 수 있다", ["offline-time-axis-techniques", "sqrt-decomposition"], " / "),
            ("되돌리기/버전이 필요하다", ["versioned-data-structures", "offline-time-axis-techniques"], " / "),
        ],
    },
    {
        "title": "최적화",
        "description": "답을 판정으로 바꿀지, DP 전이를 줄일지, 제약을 완화할지부터 구분합니다.",
        "rows": [
            ("단조 판정", ["binary-search", "parametric-optimization"]),
            (
                "DP 전이 최적화",
                [
                    "divide-and-conquer-dp-optimization",
                    "knuth-optimization",
                    "monge-smawk",
                    "convex-dp-optimization",
                ],
                " / ",
            ),
            ("정확히 K개/penalty", ["parametric-optimization", "convex-cost-flow"], " / "),
            ("convex 비용", ["convex-dp-optimization", "convex-cost-flow", "online-convex-optimization"], " / "),
            ("검증/증명", ["quadrangle-inequality-proofs", "proof-and-invariants", "testing-and-stress"], " / "),
        ],
    },
    {
        "title": "그래프",
        "description": "탐색, 최단거리, DAG, 트리, flow/cut, 동적 변화 순서로 문제 신호를 좁힙니다.",
        "rows": [
            ("탐색/연결성", ["bfs-dfs-grid", "graph-tree-basics", "union-find"], " / "),
            ("최단거리", ["zero-one-bfs", "dijkstra", "bellman-ford-negative-cycle", "floyd-warshall"], " / "),
            ("DAG 순서", ["topological-sort-dag"]),
            ("트리", ["tree-advanced", "link-cut-tree", "euler-tour-tree"], " / "),
            ("Flow/Cut", ["max-flow-min-cut", "min-cost-flow", "flow-with-lower-bound", "graph-cut-structures"], " / "),
            ("동적/오프라인", ["offline-time-axis-techniques", "dynamic-network-optimization"], " / "),
        ],
    },
    {
        "title": "수학/모델링",
        "description": "계산 루틴과 모델링 도구를 분리해, 수식 처리가 필요한 이유부터 확인합니다.",
        "rows": [
            ("기본 계산", ["modular-arithmetic", "gcd-extended-euclid-crt", "combinatorics-ncr"], " / "),
            ("행렬/점화식", ["matrix-exponentiation", "polynomial-recurrence-algorithms"], " / "),
            (
                "정수론 변환",
                ["mobius-inversion", "dirichlet-convolution", "multiplicative-functions", "summatory-number-theory"],
                " / ",
            ),
            (
                "선형대수 모델링",
                [
                    "linear-basis-xor",
                    "black-box-linear-algebra",
                    "sparse-linear-systems",
                    "linear-algebra-applications",
                ],
                " / ",
            ),
            ("확률/게임/의사결정", ["probability-expected-value", "game-theory-grundy", "probabilistic-decision-ai"], " / "),
        ],
    },
]


TRACK_GUIDES = [
    {
        "title": "최적화 트랙",
        "description": "최적화는 하나의 선형 순서가 아니라 판정, 전이 축소, 제약 완화, 증명 검증이 서로 교차합니다.",
        "rows": [
            ("A. 판정으로 바꾸기", ["binary-search", "parametric-optimization"]),
            (
                "B. DP 전이 줄이기",
                [
                    "divide-and-conquer-dp-optimization",
                    "knuth-optimization",
                    "monge-smawk",
                    "convex-dp-optimization",
                ],
                " / ",
            ),
            ("C. 제약 완화", ["parametric-optimization", "convex-cost-flow"], " / "),
            ("D. 증명/검증", ["proof-and-invariants", "quadrangle-inequality-proofs", "testing-and-stress"], " / "),
        ],
    },
    {
        "title": "그래프 트랙",
        "description": "저장소 폴더와 별개로, 학습 목차는 탐색에서 동적 네트워크까지 단계별로 읽습니다.",
        "rows": [
            ("그래프 기본", ["bfs-dfs-grid", "graph-tree-basics", "topological-sort-dag", "union-find"], " / "),
            ("최단거리", ["zero-one-bfs", "dijkstra", "bellman-ford-negative-cycle", "floyd-warshall"], " / "),
            ("트리", ["tree-advanced", "link-cut-tree", "euler-tour-tree"], " / "),
            ("Flow/Cut", ["max-flow-min-cut", "min-cost-flow", "flow-with-lower-bound", "graph-cut-structures"], " / "),
            ("동적/오프라인 그래프", ["offline-time-axis-techniques", "dynamic-network-optimization"], " / "),
        ],
    },
    {
        "title": "수학 트랙",
        "description": "계산 도구와 모델링 도구를 분리하면 advanced 수학 레슨의 어려운 이유가 더 선명해집니다.",
        "rows": [
            ("수학 기본 계산", ["modular-arithmetic", "gcd-extended-euclid-crt", "combinatorics-ncr", "matrix-exponentiation"], " / "),
            ("정수론 변환", ["mobius-inversion", "dirichlet-convolution", "multiplicative-functions", "summatory-number-theory"], " / "),
            ("선형대수 모델링", ["linear-basis-xor", "linear-basis-applications", "black-box-linear-algebra", "linear-algebra-applications"], " / "),
            ("확률/게임", ["probability-expected-value", "game-theory-grundy", "game-theory-applications", "probabilistic-decision-ai"], " / "),
        ],
    },
    {
        "title": "기하 트랙",
        "description": "predicate에서 시작해 convex, sweep, arrangement, duality와 robustness로 확장합니다.",
        "rows": [
            ("기하 입문", ["geometry-ccw-segment-intersection", "rotating-calipers"], " / "),
            ("Convex polygon", ["minkowski-sum", "rotating-calipers-applications", "shape-distance-modeling"], " / "),
            ("Sweep/Arrangement", ["sweep-line-geometry", "closest-pair-sweep", "line-arrangement", "circle-arrangement"], " / "),
            ("Half-plane/Voronoi", ["half-plane-intersection", "voronoi-delaunay", "geometry-robustness-and-duality"], " / "),
            ("Robustness/Advanced", ["geometry-robustness-and-duality", "inversion-geometry"], " / "),
        ],
    },
]


METADATA_GUIDE = [
    ("난이도", "beginner / intermediate / advanced"),
    ("난이도 축", "implementation / proof / modeling / selection"),
    ("성격", "core / implementation / overview / reference / experimental"),
    ("완성도", "concept-only / partial / full"),
    ("연습", "none / todo / linked / verified"),
    ("대상", "contest-core / advanced-contest / research-reference"),
]


INDEX_PREFIX = """<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>h-contest lessons</title>
<link rel="icon" href="data:,">
<style>
:root{color-scheme:light;--text:#172033;--muted:#596579;--line:#d9dde5;--panel:#ffffff;--bg:#f6f7f9;--accent:#0f766e;--accent-soft:#dff5f0;--warn-soft:#fff4d8;--axis-soft:#ecf7ff;--axis-text:#24516c;--type-soft:#e9f1ff;--type-text:#244b7c;--practice-soft:#e8f8ef;--practice-text:#1f6a3f;--impl-soft:#f3edff;--impl-text:#59418a;--audience-soft:#f9ece4;--audience-text:#7a4630}
*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:1120px;margin:36px auto;padding:0 20px 56px;line-height:1.55;color:var(--text);background:var(--bg)}
a{color:#0b63ce;text-decoration:none}
a:hover{text-decoration:underline}
code{background:#edf0f3;padding:2px 5px;border-radius:4px;font-size:.92em}
.manifest-link{margin:0 0 28px}
section{margin-top:34px}
h1{margin:0 0 8px;font-size:32px;line-height:1.15}
h2{margin:0 0 6px;font-size:22px}
h3{margin:0;font-size:18px;line-height:1.25}
p{margin:0;color:var(--muted)}
.guide-section{margin-top:28px}
.guide-intro{max-width:820px}
.guide-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin-top:14px}
.guide-card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px;min-width:0}
.guide-card p{margin-top:6px}
.guide-routes{display:grid;gap:8px;list-style:none;margin:12px 0 0;padding:0}
.guide-routes li{display:grid;grid-template-columns:minmax(116px,.42fr) 1fr;gap:8px;border-top:1px solid #eef1f5;padding-top:8px}
.guide-routes strong{color:#39465a;font-size:13px}
.guide-routes span{color:var(--muted);font-size:13px}
.meta-legend{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.meta-legend span{display:inline-flex;gap:6px;align-items:center;border:1px solid var(--line);border-radius:8px;background:var(--panel);padding:6px 9px;color:var(--muted);font-size:13px}
.meta-legend strong{color:#39465a}
.folder-description{margin-bottom:14px}
.lesson-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.lesson-card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:16px;min-width:0}
.lesson-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;margin-bottom:8px}
.lesson-id{white-space:nowrap;color:#4f5b6d}
.lesson-description{margin:0 0 12px}
.meta-row{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.badge{display:inline-flex;align-items:center;min-height:24px;padding:2px 8px;border-radius:999px;background:#eef2f7;color:#39465a;font-size:13px}
.badge.level{background:var(--accent-soft);color:#075f55}
.badge.time{background:var(--warn-soft);color:#76520a}
.badge.axis{background:var(--axis-soft);color:var(--axis-text)}
.badge.type{background:var(--type-soft);color:var(--type-text)}
.badge.practice{background:var(--practice-soft);color:var(--practice-text)}
.badge.implementation{background:var(--impl-soft);color:var(--impl-text)}
.badge.audience{background:var(--audience-soft);color:var(--audience-text)}
.tag-list{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}
.tag{font-size:12px;color:#526070;background:#f0f2f5;border-radius:999px;padding:1px 7px}
.path-row{margin-top:10px;font-size:13px;color:var(--muted)}
.path-row strong{color:#39465a}
.path-row a{margin-right:7px}
.page-list{margin:10px 0 0;padding-left:18px;font-size:14px}
@media (max-width:560px){body{margin-top:24px;padding-inline:14px}h1{font-size:27px}.lesson-grid,.guide-grid{grid-template-columns:1fr}.lesson-heading{display:block}.lesson-id{display:inline-block;margin-top:6px}.guide-routes li{grid-template-columns:1fr;gap:2px}}
</style>
<h1>h-contest lessons</h1>
<p class="manifest-link"><a href="lessons.json">lessons.json</a></p>
"""


FALLBACK_FOLDER = {
    "folderId": "uncategorized",
    "title": "기타",
    "description": "아직 폴더가 지정되지 않은 레슨입니다.",
    "order": 9999,
}


def sort_key(item: dict) -> tuple[int, str, str]:
    return (
        item["order"],
        item["title"],
        item.get("lessonId", item.get("folderId", "")),
    )


def page_sort_key(item: dict) -> tuple[int, str, str]:
    return (
        item["order"],
        item["title"],
        item.get("pageId", ""),
    )


def load_catalog() -> tuple[list[dict], list[dict]]:
    data = json.loads(LESSONS_JSON.read_text(encoding="utf-8"))
    folders = sorted(data.get("folders", []), key=sort_key)
    lessons = sorted(data["lessons"], key=sort_key)
    used_folder_ids = {lesson.get("folderId", FALLBACK_FOLDER["folderId"]) for lesson in lessons}
    known_folder_ids = {folder["folderId"] for folder in folders}
    if used_folder_ids - known_folder_ids:
        folders.append(FALLBACK_FOLDER)
    return folders, lessons


def group_lessons_by_folder(lessons: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for lesson in lessons:
        folder_id = lesson.get("folderId", FALLBACK_FOLDER["folderId"])
        grouped.setdefault(folder_id, []).append(lesson)
    return grouped


def level_label(level: str) -> str:
    return {
        "beginner": "입문",
        "intermediate": "중급",
        "advanced": "심화",
    }.get(level, level)


def lesson_type_label(lesson_type: str | None) -> str | None:
    if lesson_type is None:
        return None
    return {
        "core": "core",
        "implementation": "implementation",
        "overview": "overview",
        "reference": "reference",
        "experimental": "experimental",
    }.get(lesson_type, lesson_type)


def implementation_status_label(implementation_status: str | None) -> str | None:
    if implementation_status is None:
        return None
    return {
        "concept-only": "concept-only",
        "partial": "partial",
        "full": "full",
    }.get(implementation_status, implementation_status)


def practice_status_label(practice_status: str | None) -> str | None:
    if practice_status is None:
        return None
    return {
        "none": "none",
        "todo": "todo",
        "linked": "linked",
        "verified": "verified",
    }.get(practice_status, practice_status)


def audience_label(audience: str | None) -> str | None:
    if audience is None:
        return None
    return {
        "contest-core": "contest-core",
        "advanced-contest": "advanced-contest",
        "research-reference": "research-reference",
    }.get(audience, audience)


def difficulty_axes_label(difficulty_axes: list[str] | None) -> str | None:
    if not difficulty_axes:
        return None
    labels = {
        "implementation": "구현형",
        "proof": "증명형",
        "modeling": "모델링형",
        "selection": "선택지도형",
    }
    return " / ".join(labels.get(axis, axis) for axis in difficulty_axes)


def status_label(status: str | None) -> str | None:
    if status is None or status == "published":
        return None
    return status


def guide_row_label(row: tuple) -> str:
    return row[0]


def guide_row_items(row: tuple) -> list[str | tuple[str, str]]:
    return row[1]


def guide_row_separator(row: tuple) -> str:
    return row[2] if len(row) > 2 else " → "


def guide_item_id_and_label(item: str | tuple[str, str]) -> tuple[str, str | None]:
    if isinstance(item, tuple):
        return item[0], item[1]
    return item, None


def markdown_lesson_link(item: str | tuple[str, str], lessons_by_id: dict[str, dict]) -> str:
    lesson_id, label = guide_item_id_and_label(item)
    lesson = lessons_by_id.get(lesson_id)
    title = label or (lesson["title"] if lesson else lesson_id)
    if lesson is None:
        return f"`{title}`"
    return f"[{title}](lessons/{lesson_id}/lesson.md)"


def html_lesson_link(item: str | tuple[str, str], lessons_by_id: dict[str, dict]) -> str:
    lesson_id, label = guide_item_id_and_label(item)
    lesson = lessons_by_id.get(lesson_id)
    title = label or (lesson["title"] if lesson else lesson_id)
    safe_title = escape(title, quote=True)
    if lesson is None:
        return f"<code>{safe_title}</code>"
    safe_id = escape(lesson_id, quote=True)
    return f'<a href="lessons/{safe_id}/lesson.md">{safe_title}</a>'


def render_markdown_guide_section(
    title: str,
    intro: str,
    guides: list[dict],
    lessons_by_id: dict[str, dict],
) -> str:
    lines = [f"## {title}\n\n{intro}\n\n"]
    for guide in guides:
        lines.append(f"### {guide['title']}\n\n")
        description = guide.get("description")
        if description:
            lines.append(f"{description}\n\n")
        for row in guide["rows"]:
            links = guide_row_separator(row).join(
                markdown_lesson_link(item, lessons_by_id) for item in guide_row_items(row)
            )
            lines.append(f"- {guide_row_label(row)}: {links}\n")
        lines.append("\n")
    return "".join(lines)


def render_markdown_metadata_guide() -> str:
    lines = ["## 카드 배지 기준\n\n"]
    for label, values in METADATA_GUIDE:
        lines.append(f"- {label}: `{values}`\n")
    lines.append("\n")
    return "".join(lines)


def render_html_guide_section(
    title: str,
    intro: str,
    guides: list[dict],
    lessons_by_id: dict[str, dict],
) -> str:
    lines = ['<section class="guide-section">\n']
    lines.append(f"<h2>{escape(title, quote=True)}</h2>\n")
    lines.append(f'<p class="guide-intro">{escape(intro, quote=True)}</p>\n')
    lines.append('<div class="guide-grid">\n')
    for guide in guides:
        lines.append('<article class="guide-card">\n')
        lines.append(f"<h3>{escape(guide['title'], quote=True)}</h3>\n")
        description = guide.get("description")
        if description:
            lines.append(f"<p>{escape(description, quote=True)}</p>\n")
        lines.append('<ul class="guide-routes">\n')
        for row in guide["rows"]:
            links = guide_row_separator(row).join(
                html_lesson_link(item, lessons_by_id) for item in guide_row_items(row)
            )
            lines.append(
                f"<li><strong>{escape(guide_row_label(row), quote=True)}</strong>"
                f"<span>{links}</span></li>\n"
            )
        lines.append("</ul>\n")
        lines.append("</article>\n")
    lines.append("</div>\n")
    lines.append("</section>\n")
    return "".join(lines)


def render_html_metadata_guide() -> str:
    lines = ['<section class="guide-section">\n']
    lines.append("<h2>카드 배지 기준</h2>\n")
    lines.append('<div class="meta-legend">\n')
    for label, values in METADATA_GUIDE:
        lines.append(
            f"<span><strong>{escape(label, quote=True)}</strong>"
            f"{escape(values, quote=True)}</span>\n"
        )
    lines.append("</div>\n")
    lines.append("</section>\n")
    return "".join(lines)


def lesson_links(lesson_ids: list[str], lessons_by_id: dict[str, dict]) -> str:
    links = []
    for lesson_id in lesson_ids:
        lesson = lessons_by_id.get(lesson_id)
        title = lesson["title"] if lesson else lesson_id
        safe_id = escape(lesson_id, quote=True)
        safe_title = escape(title, quote=True)
        links.append(f'<a href="lessons/{safe_id}/lesson.md">{safe_title}</a>')
    return " ".join(links) if links else "없음"


def build_readme(folders: list[dict], lessons: list[dict]) -> str:
    lines = [README_HEADER]
    grouped = group_lessons_by_folder(lessons)
    lessons_by_id = {lesson["lessonId"]: lesson for lesson in lessons}
    lines.append(
        render_markdown_guide_section(
            "문제 신호별 빠른 길찾기",
            "두 노트 분류와 별개로, 문제에서 먼저 보이는 신호로 읽을 수 있는 개념 지도입니다.",
            QUICK_GUIDES,
            lessons_by_id,
        )
    )
    lines.append(
        render_markdown_guide_section(
            "심화 트랙 지도",
            "고급 주제는 선형 난이도보다 여러 축의 선택 문제에 가깝습니다. 아래 지도는 허브끼리의 관계를 먼저 보여 줍니다.",
            TRACK_GUIDES,
            lessons_by_id,
        )
    )
    lines.append(render_markdown_metadata_guide())
    lines.append("## 카테고리 요약\n\n")
    lines.append("| 카테고리 | 설명 | 레슨 수 |\n")
    lines.append("| --- | --- | ---: |\n")
    for folder in folders:
        folder_lessons = grouped.get(folder["folderId"], [])
        if not folder_lessons:
            continue
        lines.append(
            f"| {folder['title']} | {folder.get('description', '')} | {len(folder_lessons)} |\n"
        )
    lines.append("\n전체 레슨과 하위 페이지 링크는 [index.html](index.html)에서 확인합니다.\n")
    return f"{''.join(lines).rstrip()}\n"


def build_index(folders: list[dict], lessons: list[dict]) -> str:
    lines = [INDEX_PREFIX]
    grouped = group_lessons_by_folder(lessons)
    lessons_by_id = {lesson["lessonId"]: lesson for lesson in lessons}
    lines.append(
        render_html_guide_section(
            "문제 신호별 빠른 길찾기",
            "두 노트 분류와 별개로, 문제에서 먼저 보이는 신호로 읽을 수 있는 개념 지도입니다.",
            QUICK_GUIDES,
            lessons_by_id,
        )
    )
    lines.append(
        render_html_guide_section(
            "심화 트랙 지도",
            "고급 주제는 선형 난이도보다 여러 축의 선택 문제에 가깝습니다. 아래 지도는 허브끼리의 관계를 먼저 보여 줍니다.",
            TRACK_GUIDES,
            lessons_by_id,
        )
    )
    lines.append(render_html_metadata_guide())
    for folder in folders:
        folder_lessons = grouped.get(folder["folderId"], [])
        if not folder_lessons:
            continue
        title = escape(folder["title"], quote=True)
        description = escape(folder.get("description", ""), quote=True)
        lines.append(f"<section>\n<h2>{title}</h2>\n")
        if description:
            lines.append(f'<p class="folder-description">{description}</p>\n')
        lines.append('<div class="lesson-grid">\n')
        for lesson in folder_lessons:
            lesson_id = escape(lesson["lessonId"], quote=True)
            lesson_title = escape(lesson["title"], quote=True)
            lesson_description = escape(lesson["description"], quote=True)
            level = escape(level_label(lesson["level"]), quote=True)
            minutes = escape(str(lesson["estimatedMinutes"]), quote=True)
            lesson_type = lesson_type_label(lesson.get("lessonType"))
            status = status_label(lesson.get("status"))
            practice_status = practice_status_label(lesson.get("practiceStatus"))
            implementation_status = implementation_status_label(lesson.get("implementationStatus"))
            audience = audience_label(lesson.get("audience"))
            difficulty_axes = difficulty_axes_label(lesson.get("difficultyAxes"))
            tags = [escape(tag, quote=True) for tag in lesson.get("tags", [])]
            prerequisites = lesson_links(lesson.get("prerequisites", []), lessons_by_id)
            next_lessons = lesson_links(lesson.get("nextLessons", []), lessons_by_id)
            related_lessons = lesson_links(lesson.get("relatedLessons", []), lessons_by_id)
            lines.append('<article class="lesson-card">\n')
            lines.append('<div class="lesson-heading">\n')
            lines.append(f'<h3><a href="lessons/{lesson_id}/lesson.md">{lesson_title}</a></h3>\n')
            lines.append(f'<code class="lesson-id">{lesson_id}</code>\n')
            lines.append("</div>\n")
            lines.append(f'<p class="lesson-description">{lesson_description}</p>\n')
            lines.append('<div class="meta-row">\n')
            lines.append(f'<span class="badge level">{level}</span>\n')
            lines.append(f'<span class="badge time">{minutes}분</span>\n')
            if difficulty_axes:
                safe_difficulty_axes = escape(difficulty_axes, quote=True)
                lines.append(f'<span class="badge axis">축 {safe_difficulty_axes}</span>\n')
            if lesson_type:
                safe_lesson_type = escape(lesson_type, quote=True)
                lines.append(f'<span class="badge type">성격 {safe_lesson_type}</span>\n')
            if implementation_status:
                safe_implementation_status = escape(implementation_status, quote=True)
                lines.append(f'<span class="badge implementation">구현 {safe_implementation_status}</span>\n')
            if practice_status:
                safe_practice_status = escape(practice_status, quote=True)
                lines.append(f'<span class="badge practice">연습 {safe_practice_status}</span>\n')
            if audience:
                safe_audience = escape(audience, quote=True)
                lines.append(f'<span class="badge audience">대상 {safe_audience}</span>\n')
            if status:
                safe_status = escape(status, quote=True)
                lines.append(f'<span class="badge">상태 {safe_status}</span>\n')
            lines.append("</div>\n")
            if tags:
                lines.append('<div class="tag-list">\n')
                for tag in tags:
                    lines.append(f'<span class="tag">{tag}</span>\n')
                lines.append("</div>\n")
            lines.append(f'<p class="path-row"><strong>선수:</strong> {prerequisites}</p>\n')
            lines.append(f'<p class="path-row"><strong>다음:</strong> {next_lessons}</p>\n')
            lines.append(f'<p class="path-row"><strong>연관:</strong> {related_lessons}</p>\n')
            pages = sorted(lesson.get("pages", []), key=page_sort_key)
            if pages:
                lines.append('<ul class="page-list">\n')
                for page in pages:
                    page_title = escape(page["title"], quote=True)
                    page_file = escape(page["file"], quote=True)
                    page_id = escape(page["pageId"], quote=True)
                    lines.append(
                        f'<li><a href="lessons/{lesson_id}/{page_file}">{page_title}</a> '
                        f"<code>{page_id}</code></li>\n"
                    )
                lines.append("</ul>\n")
            lines.append("</article>\n")
        lines.append("</div>\n</section>\n")
    lines.append("</html>\n")
    return "".join(lines)


def expected_files() -> dict[Path, str]:
    folders, lessons = load_catalog()
    return {
        README: build_readme(folders, lessons),
        INDEX: build_index(folders, lessons),
    }


def write_files() -> None:
    for path, content in expected_files().items():
        path.write_text(content, encoding="utf-8")


def check_files() -> bool:
    ok = True
    for path, expected in expected_files().items():
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current == expected:
            continue
        ok = False
        diff = difflib.unified_diff(
            current.splitlines(keepends=True),
            expected.splitlines(keepends=True),
            fromfile=str(path.relative_to(ROOT)),
            tofile=f"{path.relative_to(ROOT)} (generated)",
        )
        print("".join(diff), end="")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="check generated files without writing")
    args = parser.parse_args()

    if args.check:
        if not check_files():
            raise SystemExit("README.md or index.html is out of date. Run python3 scripts/generate_catalog.py")
        return

    write_files()


if __name__ == "__main__":
    main()
