"""Compile actual header-free lesson compositions and compare independent oracles."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile

from cpp_library import assemble_library, check_submission_code

ROOT = Path(__file__).resolve().parents[1]
PROTECTED = {"cpp-contest-basics", "cpp-common-library", "sorting", "greedy",
             "priority-queue-heap", "heuristic", "testing-and-stress"}
CPP = re.compile(r"```(?:cpp|c\+\+)(?:[^\n]*)\n(.*?)\n```", re.S)


def check_flow_policy() -> int:
    count = 0
    manifest = json.loads((ROOT / "lessons.json").read_text())
    found = set()
    for lesson in manifest["lessons"]:
        lesson_id = lesson["lessonId"]
        if lesson_id not in PROTECTED:
            continue
        found.add(lesson_id)
        base = ROOT / "lessons" / lesson_id
        paths = [base / "lesson.md"] + [base / p["file"] for p in lesson.get("pages", [])]
        for path in paths:
            for code in CPP.findall(path.read_text()):
                check_submission_code(code, str(path.relative_to(ROOT)))
                count += 1
    if found != PROTECTED:
        raise ValueError(f"missing protected lesson: {PROTECTED - found}")
    return count


HEADERS = r'''
#include <algorithm>
#include <cassert>
#include <numeric>
#include <random>
#include <utility>
#include <vector>
'''

SORTING = r'''
int main() {
    std::mt19937 rng(20260922);
    for (int n : {0, 1, 2, 37, 4000, 1, 0, 4096}) {
        std::vector<Meeting> a(n), temp(n);
        for (auto& v : a) v = {(int)(rng() % 11), (int)(rng() % 13)};
        auto expected = a;
        std::sort(expected.begin(), expected.end(), [](Meeting x, Meeting y) {
            return std::make_pair(x.end, x.start) < std::make_pair(y.end, y.start);
        });
        sortMeetings(a.data(), temp.data(), n);
        for (int i = 0; i < n; ++i)
            assert(a[i].start == expected[i].start && a[i].end == expected[i].end);

        std::vector<int> values(n), buffer(n);
        for (int& v : values) v = (int)(rng() % 25) - 12;
        auto want = values;
        std::sort(want.begin(), want.end());
        auto uniqueEnd = std::unique(want.begin(), want.end());
        assert(countGroups(values.data(), buffer.data(), n) == uniqueEnd - want.begin());
        assert(std::is_sorted(values.begin(), values.end()));

        for (int k : {1, 2, 1000}) {
            for (int& v : values) v = rng() % k;
            want = values;
            std::sort(want.begin(), want.end());
            countingSort(values.data(), n, k);
            assert(values == want);
            std::vector<int> key(n), id(n);
            for (int& v : key) v = rng() % k;
            std::iota(id.begin(), id.end(), 0);
            std::shuffle(id.begin(), id.end(), rng);
            want = id;
            std::stable_sort(want.begin(), want.end(), [&](int x, int y) { return key[x] < key[y]; });
            countingSortIds(key.data(), id.data(), buffer.data(), n, k);
            assert(id == want); // Tie order is the input ID order, not ascending ID.
        }
    }
    for (int n : {0, 1, 2, 65537, 1, 4000000, 0}) {
        std::vector<unsigned> values(n);
        for (auto& v : values) v = rng();
        if (n >= 5) {
            values[0] = 0; values[1] = 0xffffffffU;
            values[2] = 65535; values[3] = 65536; values[4] = 0x80000000U;
        }
        auto expected = values;
        std::sort(expected.begin(), expected.end());
        radix_sort_u32(n, values.data());
        assert(values == expected);
    }
}
'''

GREEDY = r'''
int roomOracle(const std::vector<ClassPeriod>& classes) {
    std::vector<std::pair<long long, int>> events;
    for (auto c : classes) { events.push_back({c.start, 1}); events.push_back({c.end, -1}); }
    std::sort(events.begin(), events.end()); // End events precede equal-time starts.
    int live = 0, peak = 0;
    for (auto e : events) { live += e.second; peak = std::max(peak, live); }
    return peak;
}
long long taskOracle(const std::vector<Task>& tasks) {
    long long best = 0;
    for (unsigned mask = 0; mask < (1u << tasks.size()); ++mask) {
        std::vector<int> deadlines;
        long long sum = 0;
        for (unsigned i = 0; i < tasks.size(); ++i) if ((mask >> i) & 1u) {
            deadlines.push_back(tasks[i].deadline); sum += tasks[i].score;
        }
        std::sort(deadlines.begin(), deadlines.end());
        bool feasible = true;
        for (int i = 0; i < (int)deadlines.size(); ++i)
            if (deadlines[i] < i + 1) feasible = false;
        if (feasible) best = std::max(best, sum);
    }
    return best;
}
int main() {
    std::mt19937 rng(20260922);
    for (int trial = 0; trial < 300; ++trial) {
        int n = rng() % 13;
        std::vector<ClassPeriod> classes(n), ctemp(n);
        for (auto& c : classes) {
            c.start = (int)(rng() % 20) - 10;
            c.end = c.start + 1 + rng() % 10;
        }
        int rooms = roomOracle(classes);
        assert(minimumRooms(classes.data(), ctemp.data(), n) == rooms);
        std::vector<Task> tasks(n), ttemp(n);
        for (auto& t : tasks) t = {1 + (int)(rng() % 15), (long long)(rng() % 1000000001u)};
        long long score = taskOracle(tasks);
        assert(maximumScore(tasks.data(), ttemp.data(), n) == score);
    }
    // Capacity, 64-bit totals, equal boundaries, and large-small-large TC reset.
    for (int n : {200000, 1, 0, 200000}) {
        std::vector<ClassPeriod> classes(n), ctemp(n);
        for (int i = 0; i < n; ++i) classes[i] = {i, i + 1LL};
        assert(minimumRooms(classes.data(), ctemp.data(), n) == (n > 0));
        for (auto& c : classes) c = {0, 1};
        assert(minimumRooms(classes.data(), ctemp.data(), n) == n);
        std::vector<Task> tasks(n, {n + 1, 1000000000LL}), ttemp(n);
        assert(maximumScore(tasks.data(), ttemp.data(), n) == n * 1000000000LL);
        for (auto& t : tasks) t.deadline = 1;
        assert(maximumScore(tasks.data(), ttemp.data(), n) == (n ? 1000000000LL : 0));
    }
    assert(minimumRooms(nullptr, nullptr, -1) == -1);
    assert(minimumRooms(nullptr, nullptr, MAX_CLASS + 1) == -1);
    assert(maximumScore(nullptr, nullptr, -1) == -1);
    assert(maximumScore(nullptr, nullptr, MAX_TASK + 1) == -1);
}
'''

HEAP = r'''
int main() {
    std::mt19937 rng(20260922);
    for (int trial = 0; trial < 160; ++trial) {
        int n = rng() % 61;
        std::vector<int> values(n);
        for (int& v : values) v = ((int)(rng() % 21) - 10) * 100000000;
        for (int k = 0; k <= n; ++k) {
            std::vector<long long> result(n + 2, 123);
            assert(topKSums(values.data(), n, k, result.data() + 1));
            assert(result.front() == 123 && result.back() == 123);
            for (int i = 0; i < n; ++i) {
                std::vector<int> prefix(values.begin(), values.begin() + i + 1);
                std::sort(prefix.rbegin(), prefix.rend());
                long long want = 0;
                for (int j = 0; j < std::min(k, i + 1); ++j) want += prefix[j];
                assert(result[i + 1] == want);
            }
        }
    }
    for (int n : {200000, 1, 0, 200000}) {
        std::vector<int> values(n, 1000000000);
        std::vector<long long> result(n);
        assert(topKSums(values.data(), n, n, result.data()));
        for (int i = 0; i < n; ++i) assert(result[i] == (i + 1LL) * 1000000000LL);
        assert(topKSums(values.data(), n, 0, result.data()));
        for (auto v : result) assert(v == 0);
    }
    long long sentinel = 7;
    assert(!topKSums(nullptr, -1, 0, &sentinel));
    assert(!topKSums(nullptr, MAX_TOP_K + 1, 0, &sentinel));
    assert(!topKSums(nullptr, 0, -1, &sentinel));
    assert(!topKSums(nullptr, 0, 1, &sentinel));
    assert(sentinel == 7);
}
'''


def main() -> None:
    count = check_flow_policy()
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    with tempfile.TemporaryDirectory(prefix="hcontest-submission-examples-") as directory:
        work = Path(directory)
        # Exercise the documented exporter itself, including duplicate selection.
        export = work / "selected.cpp"
        subprocess.run([sys.executable, str(ROOT / "scripts/export_cpp_library.py"),
                        "--blocks", "array", "sort", "array", "--output", str(export)],
                       check=True, capture_output=True, text=True)
        assert export.read_text() == assemble_library(["array", "sort"])
        subprocess.run(compiler + ["-std=c++17", "-fsyntax-only", str(export)], check=True)
        before = export.read_bytes()
        bad = subprocess.run([sys.executable, str(ROOT / "scripts/export_cpp_library.py"),
                              "--blocks", "not-a-block", "--output", str(export)],
                             capture_output=True, text=True)
        assert bad.returncode != 0 and export.read_bytes() == before
        for lesson_id, blocks, harness in [
            ("sorting", ["sort"], SORTING),
            ("greedy", ["sort", "min-heap"], GREEDY),
            ("priority-queue-heap", ["min-heap"], HEAP),
        ]:
            markdown = (ROOT / "lessons" / lesson_id / "lesson.md").read_text()
            source = assemble_library(blocks) + "\n\n".join(CPP.findall(markdown))
            path = work / f"{lesson_id}.cpp"
            binary = work / lesson_id
            path.write_text(source)
            # The lesson must compile before harness headers are visible.
            subprocess.run(compiler + ["-std=c++17", "-Wall", "-Wextra", "-fsyntax-only", str(path)], check=True)
            path.write_text(source + HEADERS + harness)
            subprocess.run(compiler + ["-std=c++17", "-O1", "-g", "-Wall", "-Wextra",
                                      "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                                      "-fno-omit-frame-pointer", str(path), "-o", str(binary)], check=True)
            subprocess.run([str(binary)], check=True, timeout=45)
    print(f"OK: {count} submission-flow blocks; exporter and 3 header-free lesson compositions passed differential/boundary/sanitizer checks")


if __name__ == "__main__":
    main()
