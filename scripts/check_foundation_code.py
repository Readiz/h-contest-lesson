"""Run the header-free code of the converted foundation lessons.

For every lesson below this script
  1. extracts all ```cpp blocks of lesson.md (the code a reader pastes into user.cpp),
  2. puts the named common library blocks in front and compiles the result WITHOUT
     any header (forbidden constructs are rejected first),
  3. appends a local harness (the only place that may use standard headers) and
     compiles it with ASan/UBSan (-fno-sanitize-recover=all),
  4. runs the harness: differential tests against independent simple implementations,
     consecutive test cases of different sizes in one process (stale-state check),
     capacity-boundary and empty inputs,
  5. feeds the lesson's `exercise=` sample input to the harness's local reader and
     compares the printed answer with the lesson's sample output.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile

from cpp_library import assemble_library, check_submission_code

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts/foundation_code"
CPP = re.compile(r"```cpp[^\n]*\n(.*?)\n```", re.S)
EXERCISE = re.compile(r"```text exercise=([\w-]+) role=(input|output)\n(.*?)\n```", re.S)

# lesson id -> common library blocks that must be pasted in front of the lesson code
LESSONS = {
    "bfs-dfs-grid": ["queue"],
    "dijkstra": ["min-heap"],
    "union-find": ["array"],
    "prefix-sum-difference": [],
    "binary-search": ["sort"],
    "two-pointers-sliding-window": ["sort"],
    "coordinate-compression": ["sort"],
    "zero-one-bfs": [],
    "graph-tree-basics": ["array", "queue", "sort"],
    "topological-sort-dag": ["queue", "min-heap"],
}
# Code the lesson tells the reader to paste in front (lesson id, index of its ```cpp block).
LESSON_PREFIX = {"graph-tree-basics": [("union-find", 0)]}
NO_LOCAL_EXERCISE = {"union-find", "graph-tree-basics"}  # no standard-input exercise
COMPILER = shlex.split(os.environ.get("CXX", "c++"))
SANITIZE = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
            "-fno-omit-frame-pointer"]


def run(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    result = subprocess.run(command, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        raise SystemExit(f"FAIL: {' '.join(command[:3])} ...\n{result.stdout}{result.stderr}")
    return result


def check_lesson(lesson_id: str, work: Path) -> str:
    base = ROOT / "lessons" / lesson_id
    markdown = (base / "lesson.md").read_text()
    blocks = CPP.findall(markdown)
    assert blocks, lesson_id
    # Sub-pages of a lesson (pages/*.md) continue the same program after lesson.md.
    for page in sorted((base / "pages").glob("*.md")):
        blocks += CPP.findall(page.read_text())
    for number, code in enumerate(blocks):
        check_submission_code(code, f"{lesson_id} block {number}")
    prefix = [CPP.findall((ROOT / "lessons" / other / "lesson.md").read_text())[index]
              for other, index in LESSON_PREFIX.get(lesson_id, [])]
    submission = assemble_library(LESSONS[lesson_id]) + "\n\n".join(prefix + blocks) + "\n"
    path = work / f"{lesson_id}.cpp"
    path.write_text(submission)
    # No header is visible here: a missing #include would fail this step.
    run(COMPILER + ["-std=c++17", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", str(path)])

    harness = (HARNESS / f"{lesson_id}.cpp").read_text()
    path.write_text(submission + "\n" + (HARNESS / "common.inc").read_text() + harness)
    binary = work / lesson_id
    run(COMPILER + ["-std=c++17", "-Wall", "-Wextra"] + SANITIZE + [str(path), "-o", str(binary)])
    selftest = run([str(binary)], timeout=50).stdout.strip()

    examples = EXERCISE.findall(markdown)
    if lesson_id in NO_LOCAL_EXERCISE:
        assert not examples, lesson_id
        return f"{lesson_id}: {len(blocks)} blocks, {selftest}; no local exercise"
    assert [(s, role) for s, role, _ in examples] == [(lesson_id, "input"), (lesson_id, "output")], lesson_id
    sample = run([str(binary), "sample"], input=examples[0][2] + "\n", timeout=20).stdout
    assert sample.split() == examples[1][2].split(), (lesson_id, sample, examples[1][2])
    return f"{lesson_id}: {len(blocks)} blocks, {selftest}; sample output matches"


def main() -> None:
    selected = [name for name in sys.argv[1:] if name in LESSONS] or list(LESSONS)
    with tempfile.TemporaryDirectory(prefix="hcontest-foundation-code-") as directory:
        work = Path(directory)
        with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 2)) as pool:
            for line in pool.map(lambda lesson: check_lesson(lesson, work), selected):
                print("PASS:", line, flush=True)
    print(f"OK: {len(selected)} converted foundation lessons compile header-free and pass "
          "differential, consecutive-TC, capacity-boundary and sample checks with ASan/UBSan")


if __name__ == "__main__":
    main()
