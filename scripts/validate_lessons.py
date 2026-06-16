from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
LESSONS_JSON = ROOT / "lessons.json"
LESSON_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,62}[a-z0-9])?$")
IMAGE_LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^```(.*)$")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def first_h1(markdown: str) -> str | None:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def markdown_asset_links(markdown: str) -> list[str]:
    return [match.group(1) for match in IMAGE_LINK_RE.finditer(markdown)]


def markdown_regular_links(markdown: str) -> list[str]:
    return [match.group(1) for match in MARKDOWN_LINK_RE.finditer(markdown)]


def is_external_or_embedded_link(link: str) -> bool:
    parsed = urlparse(link)
    return parsed.scheme in {"http", "https", "data", "blob", "mailto"}


def normalize_local_link(link: str) -> Path:
    parsed = urlparse(link)
    path = unquote(parsed.path)
    return Path(path)


def strip_anchor(link: str) -> str:
    return link.split("#", 1)[0]


def validate_local_link(base_path: Path, lesson_id: str, link: str) -> None:
    link = strip_anchor(link)
    if not link:
        return
    if is_external_or_embedded_link(link):
        return

    local_link = normalize_local_link(link)
    if local_link.is_absolute() or ".." in local_link.parts:
        fail(f"unsafe local link in {lesson_id}: {link}")

    target = base_path.parent / local_link
    if not target.exists():
        fail(f"missing local link target in {lesson_id}: {link}")


def validate_code_fences(markdown: str, lesson_id: str) -> None:
    inside = False
    for line_no, line in enumerate(markdown.splitlines(), start=1):
        match = FENCE_RE.match(line)
        if not match:
            continue

        if not inside:
            lang = match.group(1).strip()
            if not lang:
                fail(f"missing code fence language in {lesson_id}:{line_no}")
            inside = True
        else:
            inside = False

    if inside:
        fail(f"unclosed code fence in {lesson_id}")


def validate_manifest_entry(lesson: object) -> dict:
    if not isinstance(lesson, dict):
        fail("each lesson entry must be an object")

    lesson_id = lesson.get("lessonId")
    title = lesson.get("title")
    description = lesson.get("description")
    summary = lesson.get("summary")
    order = lesson.get("order")
    tags = lesson.get("tags")

    if not isinstance(lesson_id, str) or not LESSON_ID_RE.fullmatch(lesson_id):
        fail(f"invalid lessonId: {lesson_id!r}")
    if not isinstance(title, str) or not title.strip():
        fail(f"title is required for {lesson_id}")
    if not isinstance(description, str) or not description.strip():
        fail(f"description is required for {lesson_id}")
    if not isinstance(summary, str) or not summary.strip():
        fail(f"summary is required for {lesson_id}")
    if not isinstance(order, int):
        fail(f"order must be an integer for {lesson_id}")
    if not isinstance(tags, list) or not tags:
        fail(f"tags must be a non-empty array for {lesson_id}")
    if not all(isinstance(tag, str) and tag.strip() for tag in tags):
        fail(f"tags must contain only non-empty strings for {lesson_id}")

    return lesson


def validate_generated_files() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_catalog.py", "--check"],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    data = json.loads(LESSONS_JSON.read_text(encoding="utf-8"))
    lessons_raw = data.get("lessons")

    if not isinstance(lessons_raw, list):
        fail("lessons.json must contain a lessons array")

    lessons = [validate_manifest_entry(lesson) for lesson in lessons_raw]
    sorted_lessons = sorted(
        lessons,
        key=lambda lesson: (lesson["order"], lesson["title"], lesson["lessonId"]),
    )
    if lessons != sorted_lessons:
        fail("lessons.json must be sorted by order, title, lessonId")

    seen_ids: set[str] = set()
    seen_orders: set[int] = set()

    for lesson in lessons:
        lesson_id = lesson["lessonId"]
        title = lesson["title"]
        order = lesson["order"]

        if lesson_id in seen_ids:
            fail(f"duplicated lessonId: {lesson_id}")
        seen_ids.add(lesson_id)

        if order in seen_orders:
            fail(f"duplicated order: {order}")
        seen_orders.add(order)

        lesson_path = ROOT / "lessons" / lesson_id / "lesson.md"
        if not lesson_path.exists():
            fail(f"missing lesson file: {lesson_path.relative_to(ROOT)}")

        markdown = lesson_path.read_text(encoding="utf-8")
        h1 = first_h1(markdown)
        if h1 != title:
            fail(f"title mismatch for {lesson_id}: lessons.json={title!r}, h1={h1!r}")

        validate_code_fences(markdown, lesson_id)

        for link in markdown_asset_links(markdown):
            validate_local_link(lesson_path, lesson_id, link)

        for link in markdown_regular_links(markdown):
            validate_local_link(lesson_path, lesson_id, link)

    validate_generated_files()

    print(f"OK: {len(lessons)} lessons validated")


if __name__ == "__main__":
    main()
