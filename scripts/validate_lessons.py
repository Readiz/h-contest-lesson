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
FOLDER_ID_RE = LESSON_ID_RE
PAGE_ID_RE = LESSON_ID_RE
IMAGE_LINK_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^```(.*)$")
LESSON_LEVELS = {"beginner", "intermediate", "advanced"}
LESSON_STATUSES = {"draft", "review", "published"}
LESSON_TYPES = {"core", "implementation", "overview", "reference", "experimental"}
PRACTICE_STATUSES = {"none", "todo", "linked", "verified"}
IMPLEMENTATION_STATUSES = {"concept-only", "partial", "full"}
AUDIENCES = {"contest-core", "advanced-contest", "research-reference"}
LESSON_REFERENCE_FIELDS = ("prerequisites", "nextLessons", "relatedLessons")
HCONTEST_PROBLEM_ROUTE_RE = re.compile(
    r"^/practice/[A-Z0-9]{8,16}(?:/(?:editorial|submissions/[0-9]+))?$",
)
PRACTICE_HEADING_RE = re.compile(r"^#{2,3}\s+.*연습 문제\s*$")
PRACTICE_TABLE_HEADER = "| 단계 | 문제 | 목표 | 힌트 키워드 |"
TODO_RE = re.compile(r"\bTODO\b")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def first_h1(markdown: str) -> str | None:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def markdown_asset_links(markdown: str) -> list[str]:
    return [match.group(2) for match in IMAGE_LINK_RE.finditer(markdown)]


def validate_image_alt_text(markdown: str, lesson_id: str) -> None:
    for match in IMAGE_LINK_RE.finditer(markdown):
        alt = match.group(1).strip()
        if not alt:
            fail(f"empty image alt text in {lesson_id}: {match.group(2)}")


def markdown_regular_links(markdown: str) -> list[str]:
    return [match.group(1) for match in MARKDOWN_LINK_RE.finditer(markdown)]


def is_external_or_embedded_link(link: str) -> bool:
    parsed = urlparse(link)
    return parsed.scheme in {"http", "https", "data", "blob", "mailto"}


def is_hcontest_problem_route_link(link: str) -> bool:
    parsed = urlparse(link)
    return not parsed.scheme and HCONTEST_PROBLEM_ROUTE_RE.fullmatch(parsed.path) is not None


def normalize_local_link(link: str) -> Path:
    parsed = urlparse(link)
    path = unquote(parsed.path)
    return Path(path)


def strip_anchor(link: str) -> str:
    return link.split("#", 1)[0]


def validate_local_link(base_path: Path, lesson_id: str, link: str, safe_root: Path) -> None:
    link = strip_anchor(link)
    if not link:
        return
    if is_external_or_embedded_link(link):
        return
    if is_hcontest_problem_route_link(link):
        return

    local_link = normalize_local_link(link)
    if local_link.is_absolute():
        fail(f"unsafe local link in {lesson_id}: {link}")

    target = base_path.parent / local_link
    resolved_target = target.resolve()
    resolved_root = safe_root.resolve()
    if resolved_target != resolved_root and resolved_root not in resolved_target.parents:
        fail(f"unsafe local link in {lesson_id}: {link}")
    if not resolved_target.exists():
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


def validate_compile_check_blocks(markdown: str, lesson_id: str) -> None:
    inside = False
    info = ""
    block_lines: list[str] = []
    start_line = 0

    for line_no, line in enumerate(markdown.splitlines(), start=1):
        match = FENCE_RE.match(line)
        if match:
            if not inside:
                inside = True
                info = match.group(1).strip()
                block_lines = []
                start_line = line_no
            else:
                tokens = set(info.split())
                lang = info.split()[0] if info.split() else ""
                if lang in {"cpp", "c++"} and "compile-check" in tokens:
                    code = "\n".join(block_lines)
                    try:
                        result = subprocess.run(
                            ["c++", "-std=c++17", "-fsyntax-only", "-x", "c++", "-"],
                            input=code,
                            text=True,
                            capture_output=True,
                            check=False,
                        )
                    except FileNotFoundError:
                        fail("c++ compiler is required for cpp compile-check blocks")
                    if result.returncode != 0:
                        detail = result.stderr.strip().splitlines()
                        first_error = detail[0] if detail else "unknown compiler error"
                        fail(f"cpp compile-check failed in {lesson_id}:{start_line}: {first_error}")
                inside = False
            continue

        if inside:
            block_lines.append(line)


def practice_sections(markdown: str) -> list[str]:
    lines = markdown.splitlines()
    sections: list[str] = []
    current: list[str] | None = None
    for line in lines:
        if PRACTICE_HEADING_RE.match(line):
            if current:
                sections.append("\n".join(current))
            current = [line]
            continue
        if current is not None and line.startswith("## ") and not PRACTICE_HEADING_RE.match(line):
            sections.append("\n".join(current))
            current = None
            continue
        if current is not None:
            current.append(line)
    if current:
        sections.append("\n".join(current))
    return sections


def validate_practice_section(markdown: str, lesson_id: str) -> None:
    sections = practice_sections(markdown)
    if not sections:
        fail(f"missing practice section for {lesson_id}")

    combined = "\n\n".join(sections)
    if PRACTICE_TABLE_HEADER not in combined:
        fail(f"practice table must include hint keyword column for {lesson_id}")
    if "/practice/" not in combined and TODO_RE.search(combined) is None:
        fail(f"practice section must include a /practice/ link or TODO for {lesson_id}")


def validate_folder_entry(folder: object) -> dict:
    if not isinstance(folder, dict):
        fail("each folder entry must be an object")

    folder_id = folder.get("folderId")
    title = folder.get("title")
    description = folder.get("description")
    order = folder.get("order")

    if not isinstance(folder_id, str) or not FOLDER_ID_RE.fullmatch(folder_id):
        fail(f"invalid folderId: {folder_id!r}")
    if not isinstance(title, str) or not title.strip():
        fail(f"title is required for folder {folder_id}")
    if not isinstance(description, str) or not description.strip():
        fail(f"description is required for folder {folder_id}")
    if not isinstance(order, int):
        fail(f"order must be an integer for folder {folder_id}")

    return folder


def validate_page_file_path(value: object, lesson_id: str, page_id: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"file is required for {lesson_id}/{page_id}")

    file_path = Path(value.strip())
    if file_path.is_absolute() or ".." in file_path.parts:
        fail(f"unsafe file path for {lesson_id}/{page_id}: {value!r}")
    if not file_path.parts or any(not part for part in file_path.parts):
        fail(f"invalid file path for {lesson_id}/{page_id}: {value!r}")
    if file_path.suffix != ".md":
        fail(f"page file must be a markdown file for {lesson_id}/{page_id}: {value!r}")

    return file_path.as_posix()


def validate_page_entry(page: object, lesson_id: str) -> dict:
    if not isinstance(page, dict):
        fail(f"each page entry must be an object for {lesson_id}")

    page_id = page.get("pageId")
    title = page.get("title")
    description = page.get("description")
    order = page.get("order")

    if not isinstance(page_id, str) or not PAGE_ID_RE.fullmatch(page_id):
        fail(f"invalid pageId for {lesson_id}: {page_id!r}")
    if not isinstance(title, str) or not title.strip():
        fail(f"title is required for {lesson_id}/{page_id}")
    if not isinstance(description, str) or not description.strip():
        fail(f"description is required for {lesson_id}/{page_id}")
    if not isinstance(order, int):
        fail(f"order must be an integer for {lesson_id}/{page_id}")

    page["file"] = validate_page_file_path(page.get("file"), lesson_id, page_id)
    return page


def validate_lesson_reference_list(value: object, lesson_id: str, field_name: str) -> list[str]:
    if not isinstance(value, list):
        fail(f"{field_name} must be an array for {lesson_id}")
    refs: list[str] = []
    seen_refs: set[str] = set()
    for raw_ref in value:
        if not isinstance(raw_ref, str) or not LESSON_ID_RE.fullmatch(raw_ref):
            fail(f"invalid {field_name} reference for {lesson_id}: {raw_ref!r}")
        if raw_ref == lesson_id:
            fail(f"{field_name} must not reference itself for {lesson_id}")
        if raw_ref in seen_refs:
            fail(f"duplicated {field_name} reference for {lesson_id}: {raw_ref}")
        refs.append(raw_ref)
        seen_refs.add(raw_ref)
    return refs


def validate_manifest_entry(lesson: object, folder_ids: set[str]) -> dict:
    if not isinstance(lesson, dict):
        fail("each lesson entry must be an object")

    lesson_id = lesson.get("lessonId")
    title = lesson.get("title")
    description = lesson.get("description")
    summary = lesson.get("summary")
    order = lesson.get("order")
    folder_id = lesson.get("folderId")
    level = lesson.get("level")
    estimated_minutes = lesson.get("estimatedMinutes")
    tags = lesson.get("tags")
    pages_raw = lesson.get("pages", [])
    status = lesson.get("status")
    lesson_type = lesson.get("lessonType")
    series_id = lesson.get("seriesId")
    parent_lesson_id = lesson.get("parentLessonId")
    practice_status = lesson.get("practiceStatus")
    implementation_status = lesson.get("implementationStatus")
    audience = lesson.get("audience")

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
    if not isinstance(folder_id, str) or folder_id not in folder_ids:
        fail(f"folderId must reference a folder for {lesson_id}: {folder_id!r}")
    if not isinstance(level, str) or level not in LESSON_LEVELS:
        fail(f"level must be one of {sorted(LESSON_LEVELS)} for {lesson_id}: {level!r}")
    if not isinstance(estimated_minutes, int) or estimated_minutes <= 0:
        fail(f"estimatedMinutes must be a positive integer for {lesson_id}")
    if not isinstance(tags, list) or not tags:
        fail(f"tags must be a non-empty array for {lesson_id}")
    if not all(isinstance(tag, str) and tag.strip() for tag in tags):
        fail(f"tags must contain only non-empty strings for {lesson_id}")
    if not isinstance(pages_raw, list):
        fail(f"pages must be an array for {lesson_id}")
    if status is not None and (not isinstance(status, str) or status not in LESSON_STATUSES):
        fail(f"status must be one of {sorted(LESSON_STATUSES)} for {lesson_id}: {status!r}")
    if lesson_type is not None and (
        not isinstance(lesson_type, str) or lesson_type not in LESSON_TYPES
    ):
        fail(f"lessonType must be one of {sorted(LESSON_TYPES)} for {lesson_id}: {lesson_type!r}")
    if series_id is not None and (not isinstance(series_id, str) or not LESSON_ID_RE.fullmatch(series_id)):
        fail(f"invalid seriesId for {lesson_id}: {series_id!r}")
    if parent_lesson_id is not None:
        if not isinstance(parent_lesson_id, str) or not LESSON_ID_RE.fullmatch(parent_lesson_id):
            fail(f"invalid parentLessonId for {lesson_id}: {parent_lesson_id!r}")
        if parent_lesson_id == lesson_id:
            fail(f"parentLessonId must not reference itself for {lesson_id}")
    if practice_status is not None and (
        not isinstance(practice_status, str) or practice_status not in PRACTICE_STATUSES
    ):
        fail(
            f"practiceStatus must be one of {sorted(PRACTICE_STATUSES)} "
            f"for {lesson_id}: {practice_status!r}"
        )
    if implementation_status is not None and (
        not isinstance(implementation_status, str)
        or implementation_status not in IMPLEMENTATION_STATUSES
    ):
        fail(
            f"implementationStatus must be one of {sorted(IMPLEMENTATION_STATUSES)} "
            f"for {lesson_id}: {implementation_status!r}"
        )
    if audience is not None and (not isinstance(audience, str) or audience not in AUDIENCES):
        fail(f"audience must be one of {sorted(AUDIENCES)} for {lesson_id}: {audience!r}")
    if (
        status == "published"
        and lesson_type in {"core", "implementation"}
        and practice_status in {"none", "todo"}
    ):
        fail(f"published {lesson_type} lesson must not have practiceStatus={practice_status!r}: {lesson_id}")

    for field_name in LESSON_REFERENCE_FIELDS:
        lesson[field_name] = validate_lesson_reference_list(lesson.get(field_name), lesson_id, field_name)

    pages = [validate_page_entry(page, lesson_id) for page in pages_raw]
    sorted_pages = sorted(
        pages,
        key=lambda page: (page["order"], page["title"], page["pageId"]),
    )
    if pages != sorted_pages:
        fail(f"pages must be sorted by order, title, pageId for {lesson_id}")

    seen_page_ids: set[str] = set()
    seen_page_orders: set[int] = set()
    for page in pages:
        page_id = page["pageId"]
        page_order = page["order"]
        if page_id in seen_page_ids:
            fail(f"duplicated pageId for {lesson_id}: {page_id}")
        seen_page_ids.add(page_id)
        if page_order in seen_page_orders:
            fail(f"duplicated page order for {lesson_id}: {page_order}")
        seen_page_orders.add(page_order)

    return lesson


def validate_lesson_references(lessons: list[dict], lesson_ids: set[str]) -> None:
    for lesson in lessons:
        lesson_id = lesson["lessonId"]
        for field_name in LESSON_REFERENCE_FIELDS:
            for ref in lesson[field_name]:
                if ref not in lesson_ids:
                    fail(f"{field_name} for {lesson_id} references missing lessonId: {ref}")
        parent_lesson_id = lesson.get("parentLessonId")
        if parent_lesson_id is not None and parent_lesson_id not in lesson_ids:
            fail(f"parentLessonId for {lesson_id} references missing lessonId: {parent_lesson_id}")


def validate_generated_files() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_catalog.py", "--check"],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    data = json.loads(LESSONS_JSON.read_text(encoding="utf-8"))
    folders_raw = data.get("folders")
    lessons_raw = data.get("lessons")

    if not isinstance(folders_raw, list):
        fail("lessons.json must contain a folders array")
    if not isinstance(lessons_raw, list):
        fail("lessons.json must contain a lessons array")

    folders = [validate_folder_entry(folder) for folder in folders_raw]
    sorted_folders = sorted(
        folders,
        key=lambda folder: (folder["order"], folder["title"], folder["folderId"]),
    )
    if folders != sorted_folders:
        fail("folders must be sorted by order, title, folderId")

    seen_folder_ids: set[str] = set()
    seen_folder_orders: set[int] = set()
    for folder in folders:
        folder_id = folder["folderId"]
        order = folder["order"]
        if folder_id in seen_folder_ids:
            fail(f"duplicated folderId: {folder_id}")
        seen_folder_ids.add(folder_id)
        if order in seen_folder_orders:
            fail(f"duplicated folder order: {order}")
        seen_folder_orders.add(order)

    lessons = [validate_manifest_entry(lesson, seen_folder_ids) for lesson in lessons_raw]
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
        lesson_root = ROOT / "lessons" / lesson_id
        if not lesson_path.exists():
            fail(f"missing lesson file: {lesson_path.relative_to(ROOT)}")

        markdown = lesson_path.read_text(encoding="utf-8")
        h1 = first_h1(markdown)
        if h1 != title:
            fail(f"title mismatch for {lesson_id}: lessons.json={title!r}, h1={h1!r}")

        validate_code_fences(markdown, lesson_id)
        validate_compile_check_blocks(markdown, lesson_id)
        validate_image_alt_text(markdown, lesson_id)

        for link in markdown_asset_links(markdown):
            validate_local_link(lesson_path, lesson_id, link, lesson_root)

        for link in markdown_regular_links(markdown):
            validate_local_link(lesson_path, lesson_id, link, lesson_root)

        lesson_markdown_parts = [markdown]

        for page in lesson.get("pages", []):
            page_id = page["pageId"]
            page_path = ROOT / "lessons" / lesson_id / page["file"]
            if not page_path.exists():
                fail(f"missing lesson page file: {page_path.relative_to(ROOT)}")

            page_markdown = page_path.read_text(encoding="utf-8")
            lesson_markdown_parts.append(page_markdown)
            page_h1 = first_h1(page_markdown)
            if not page_h1:
                fail(f"missing page title for {lesson_id}/{page_id}")

            link_context = f"{lesson_id}/{page_id}"
            validate_code_fences(page_markdown, link_context)
            validate_compile_check_blocks(page_markdown, link_context)
            validate_image_alt_text(page_markdown, link_context)

            for link in markdown_asset_links(page_markdown):
                validate_local_link(page_path, link_context, link, lesson_root)

            for link in markdown_regular_links(page_markdown):
                validate_local_link(page_path, link_context, link, lesson_root)

        validate_practice_section("\n\n".join(lesson_markdown_parts), lesson_id)

    validate_lesson_references(lessons, seen_ids)
    validate_generated_files()

    print(f"OK: {len(lessons)} lessons validated")


if __name__ == "__main__":
    main()
