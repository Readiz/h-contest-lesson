"""Shared reader for lessons that are split into a hub plus pages.

Practical lessons keep a short hub (`lesson.md`) and sub pages listed in the
`pages` array of `lessons.json`. The per-lesson check scripts read the hub and
the pages in manifest order as one text, so code blocks, tables, markers and
figures are found no matter which page holds them.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB_SUMMARY_MARKER = "<!-- check:hub-summary -->"


def lesson_files(lesson_id: str) -> list[Path]:
    """Hub first, then the pages in manifest order."""
    base = ROOT / "lessons" / lesson_id
    manifest = json.loads((ROOT / "lessons.json").read_text(encoding="utf-8"))
    entry = next(lesson for lesson in manifest["lessons"] if lesson["lessonId"] == lesson_id)
    pages = sorted(entry.get("pages", []), key=lambda p: (p["order"], p["title"], p["pageId"]))
    return [base / "lesson.md"] + [base / page["file"] for page in pages]


def read_lesson_text(lesson_id: str, include_hub: bool = True) -> str:
    """Hub and pages joined in manifest order. Use include_hub=False when a row lookup must not
    be satisfied by the hub's summary table."""
    files = lesson_files(lesson_id)
    if not include_hub:
        files = files[1:]
    return "\n".join(path.read_text(encoding="utf-8") for path in files)


def read_hub_text(lesson_id: str) -> str:
    return (ROOT / "lessons" / lesson_id / "lesson.md").read_text(encoding="utf-8")


def hub_summary_rows(lesson_id: str) -> list[list[str]]:
    """Data rows (cells) of the hub's `<!-- check:hub-summary -->` table."""
    hub = read_hub_text(lesson_id)
    match = re.search(re.escape(HUB_SUMMARY_MARKER) + r"\n((?:\|[^\n]*\n?)+)", hub)
    assert match, f"{lesson_id}: hub summary table marker is missing"
    lines = match.group(1).rstrip("\n").splitlines()
    assert len(lines) >= 3, f"{lesson_id}: hub summary table has no data rows"
    return [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines[2:]]


def check_hub_summary(lesson_id: str, expected: list[tuple[str, str]]) -> int:
    """The hub's stage summary must equal (stage label, value) rows built from the measurement data."""
    rows = hub_summary_rows(lesson_id)
    got = [(row[0], row[1]) for row in rows]
    assert all(len(row) == 2 for row in rows), f"{lesson_id}: hub summary table must have two columns"
    assert got == [(label, str(value)) for label, value in expected], (
        f"{lesson_id}: hub summary table differs from the measurement\n got {got}\n want {expected}")
    return len(got)
