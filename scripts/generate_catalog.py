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


README_HEADER = """# h-contest lesson content

This repository is the source of truth for h-contest algorithm lessons. Lesson source lives in `lessons/` and `lessons.json`; `README.md` and `index.html` are generated entry points.

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

## 카테고리 요약

"""


INDEX_PREFIX = """<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>h-contest lessons</title>
<link rel="icon" href="data:,">
<style>
:root{color-scheme:light;--text:#172033;--muted:#596579;--line:#d9dde5;--panel:#ffffff;--bg:#f6f7f9;--accent:#0f766e;--accent-soft:#dff5f0;--warn-soft:#fff4d8}
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
.tag-list{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}
.tag{font-size:12px;color:#526070;background:#f0f2f5;border-radius:999px;padding:1px 7px}
.path-row{margin-top:10px;font-size:13px;color:var(--muted)}
.path-row strong{color:#39465a}
.path-row a{margin-right:7px}
.page-list{margin:10px 0 0;padding-left:18px;font-size:14px}
@media (max-width:560px){body{margin-top:24px;padding-inline:14px}h1{font-size:27px}.lesson-grid{grid-template-columns:1fr}.lesson-heading{display:block}.lesson-id{display:inline-block;margin-top:6px}}
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


def status_label(status: str | None) -> str | None:
    if status is None or status == "published":
        return None
    return status


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
            if lesson_type:
                safe_lesson_type = escape(lesson_type, quote=True)
                lines.append(f'<span class="badge">{safe_lesson_type}</span>\n')
            if status:
                safe_status = escape(status, quote=True)
                lines.append(f'<span class="badge">{safe_status}</span>\n')
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
