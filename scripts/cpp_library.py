"""Read the canonical header-free library blocks from the published lesson."""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "lessons/cpp-common-library/lesson.md"
BLOCK_NAMES = ("array", "random", "sort", "queue", "min-heap")
SNIPPET_RE = re.compile(r"```cpp compile-check snippet=([\w-]+)\n(.*?)\n```", re.S)


def check_submission_code(code: str, name: str) -> None:
    # Comments and string/character literals are not executable dependencies.
    code = re.sub(r'''//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' ''',
                  " ", code, flags=re.S | re.X)
    forbidden = r"^\s*#\s*(include|pragma)\b|\bstd\s*::|\busing\s+namespace\s+std\b|\b(new|delete)\b|\b(malloc|calloc|realloc|free)\s*\("
    if re.search(forbidden, code, re.M):
        raise ValueError(f"submission-incompatible construct in {name}")


def read_library_snippets() -> dict[str, str]:
    snippets = {}
    for name, code in SNIPPET_RE.findall(LIBRARY.read_text()):
        if name in snippets:
            raise ValueError(f"duplicate library block: {name}")
        check_submission_code(code, name)
        snippets[name] = code
    if set(snippets) != set(BLOCK_NAMES):
        raise ValueError(f"unexpected library blocks: {set(snippets) ^ set(BLOCK_NAMES)}")
    return {name: snippets[name] for name in BLOCK_NAMES}


def assemble_library(names: list[str]) -> str:
    snippets = read_library_snippets()
    unknown = set(names) - set(snippets)
    if unknown:
        raise ValueError(f"unknown library blocks: {', '.join(sorted(unknown))}")
    return "\n\n".join("// hc block: " + name + "\n" + snippets[name]
                       for name in dict.fromkeys(names)) + "\n"
