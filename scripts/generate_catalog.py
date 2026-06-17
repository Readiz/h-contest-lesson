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
- `lessons.json`

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
<style>body{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:880px;margin:40px auto;padding:0 20px;line-height:1.55}code{background:#f2f2f2;padding:2px 4px;border-radius:4px}a{color:#0b63ce}</style>
<h1>h-contest lessons</h1>
<p><a href="lessons.json">lessons.json</a></p>
<ul>
"""


def load_lessons() -> list[dict]:
    data = json.loads(LESSONS_JSON.read_text(encoding="utf-8"))
    lessons = data["lessons"]
    return sorted(
        lessons,
        key=lambda lesson: (
            lesson["order"],
            lesson["title"],
            lesson["lessonId"],
        ),
    )


def build_readme(lessons: list[dict]) -> str:
    lines = [README_HEADER]
    for lesson in lessons:
        lesson_id = lesson["lessonId"]
        title = lesson["title"]
        lines.append(f"- [{title}](lessons/{lesson_id}/lesson.md)\n")
    return "".join(lines)


def build_index(lessons: list[dict]) -> str:
    lines = [INDEX_PREFIX]
    for lesson in lessons:
        lesson_id = escape(lesson["lessonId"], quote=True)
        title = escape(lesson["title"], quote=True)
        lines.append(
            f'<li><a href="lessons/{lesson_id}/lesson.md">{title}</a> '
            f"<code>{lesson_id}</code></li>\n"
        )
    lines.append("</ul>\n</html>\n")
    return "".join(lines)


def expected_files() -> dict[Path, str]:
    lessons = load_lessons()
    return {
        README: build_readme(lessons),
        INDEX: build_index(lessons),
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
