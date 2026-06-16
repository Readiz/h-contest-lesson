from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
LESSONS_JSON = ROOT / "lessons.json"
LESSON_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,62}[a-z0-9])?$")
IMAGE_LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def first_h1(markdown: str) -> str | None:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def markdown_asset_links(markdown: str) -> list[str]:
    return [match.group(1) for match in IMAGE_LINK_RE.finditer(markdown)]


def is_external_or_embedded_link(link: str) -> bool:
    parsed = urlparse(link)
    return parsed.scheme in {"http", "https", "data", "blob"}


def normalize_local_link(link: str) -> Path:
    parsed = urlparse(link)
    path = unquote(parsed.path)
    return Path(path)


def main() -> None:
    data = json.loads(LESSONS_JSON.read_text(encoding="utf-8"))
    lessons = data.get("lessons")

    if not isinstance(lessons, list):
        fail("lessons.json must contain a lessons array")

    seen_ids: set[str] = set()
    seen_orders: set[int] = set()

    for lesson in lessons:
        if not isinstance(lesson, dict):
            fail("each lesson entry must be an object")

        lesson_id = lesson.get("lessonId")
        title = lesson.get("title")
        order = lesson.get("order")

        if not isinstance(lesson_id, str) or not LESSON_ID_RE.fullmatch(lesson_id):
            fail(f"invalid lessonId: {lesson_id!r}")
        if lesson_id in seen_ids:
            fail(f"duplicated lessonId: {lesson_id}")
        seen_ids.add(lesson_id)

        if not isinstance(title, str) or not title.strip():
            fail(f"title is required for {lesson_id}")

        if not isinstance(order, int):
            fail(f"order must be an integer for {lesson_id}")
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

        for link in markdown_asset_links(markdown):
            if is_external_or_embedded_link(link):
                continue
            local_link = normalize_local_link(link)
            if local_link.is_absolute() or ".." in local_link.parts:
                fail(f"unsafe asset link in {lesson_id}: {link}")
            asset_path = lesson_path.parent / local_link
            if not asset_path.exists():
                fail(f"missing asset in {lesson_id}: {link}")

    print(f"OK: {len(lessons)} lessons validated")


if __name__ == "__main__":
    main()
