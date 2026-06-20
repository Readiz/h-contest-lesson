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

This repository is the source of truth for h-contest algorithm lessons.
The public API is generated from or synchronized with this repository.

- Published manifest: https://blog.readiz.com/h-contest-lesson/lessons.json
- API mirror: https://h.readiz.com/api/lessons

## Contributing

Pull requests should edit this repository directly. For details, see [CONTRIBUTING.md](CONTRIBUTING.md).

When adding a new lesson, update these source files:

- `lessons/<lessonId>/lesson.md`
- `lessons.json` (`folderId` included)

Then regenerate derived files:

```bash
python3 scripts/generate_catalog.py
```

Generated files:

- `README.md`
- `index.html`

If the lesson uses images or other local assets, add them under `lessons/<lessonId>/lesson-assets/`.

## Lessons

"""


INDEX_PREFIX = """<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>h-contest lessons</title>
<style>body{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:880px;margin:40px auto;padding:0 20px 48px;line-height:1.55;color:#172033}code{background:#f2f2f2;padding:2px 4px;border-radius:4px}a{color:#0b63ce}section{margin-top:28px}h2{margin:0 0 6px;font-size:22px}p{margin:0 0 10px;color:#526070}ul{margin-top:8px}</style>
<h1>h-contest lessons</h1>
<p><a href="lessons.json">lessons.json</a></p>
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


def build_readme(folders: list[dict], lessons: list[dict]) -> str:
    lines = [README_HEADER]
    grouped = group_lessons_by_folder(lessons)
    for folder in folders:
        folder_lessons = grouped.get(folder["folderId"], [])
        if not folder_lessons:
            continue
        lines.append(f"### {folder['title']}\n\n")
        if folder.get("description"):
            lines.append(f"{folder['description']}\n\n")
        for lesson in folder_lessons:
            lesson_id = lesson["lessonId"]
            title = lesson["title"]
            lines.append(f"- [{title}](lessons/{lesson_id}/lesson.md)\n")
        lines.append("\n")
    return f"{''.join(lines).rstrip()}\n"


def build_index(folders: list[dict], lessons: list[dict]) -> str:
    lines = [INDEX_PREFIX]
    grouped = group_lessons_by_folder(lessons)
    for folder in folders:
        folder_lessons = grouped.get(folder["folderId"], [])
        if not folder_lessons:
            continue
        title = escape(folder["title"], quote=True)
        description = escape(folder.get("description", ""), quote=True)
        lines.append(f"<section>\n<h2>{title}</h2>\n")
        if description:
            lines.append(f"<p>{description}</p>\n")
        lines.append("<ul>\n")
        for lesson in folder_lessons:
            lesson_id = escape(lesson["lessonId"], quote=True)
            lesson_title = escape(lesson["title"], quote=True)
            lines.append(
                f'<li><a href="lessons/{lesson_id}/lesson.md">{lesson_title}</a> '
                f"<code>{lesson_id}</code></li>\n"
            )
        lines.append("</ul>\n</section>\n")
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
