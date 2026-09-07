"""Compile and execute the exact STL-free snippets from the C++ foundation lesson."""
from __future__ import annotations

import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "lessons/cpp-contest-basics"
EXPECTED = {"array", "random", "index-sort", "queue", "min-heap", "state-reset", "ordering-baseline"}


def read_snippets() -> dict[str, str]:
    snippets = {}
    for page in sorted(LESSON.rglob("*.md")):
        for name, code in re.findall(r"```cpp compile-check snippet=([\w-]+)\n(.*?)\n```", page.read_text(), re.S):
            if name in snippets:
                raise ValueError(f"duplicate snippet: {name}")
            if re.search(r"^\s*#\s*(include|pragma)\b|\bstd\s*::|\bextern\s*\"", code, re.M):
                raise ValueError(f"submission-incompatible construct in {name}")
            snippets[name] = code
    if set(snippets) != EXPECTED:
        raise ValueError(f"unexpected snippet set: {set(snippets) ^ EXPECTED}")
    return snippets


# Reference implementations and assertions below belong only to the local harness.
HARNESS = r'''
#include <algorithm>
#include <cassert>
#include <functional>
#include <queue>
#include <random>
#include <utility>
#include <vector>

int main() {
    int src[] = {4, 9, 2}, dst[] = {-1, -1, -1};
    hc::copy(dst, src, 0); assert(dst[0] == -1);
    hc::copy(dst, src, 3); dst[0] = 7; assert(src[0] == 4);
    hc::swap(src[1], src[1]); assert(src[1] == 9);
    hc::fill(src, 3, src[1]); assert(src[0] == 9 && src[2] == 9);
    hc::fill(src, 0, 2); assert(src[0] == 9);
    hc::iota(src, 3); assert(src[0] == 0 && src[2] == 2);

    hc::Random r, same;
    r.reset(1);
    assert(r.next() == 1015568748u);
    assert(r.next() == 1586005467u);
    assert(r.next() == 2165703038u);
    r.reset(42); same.reset(42);
    for (int i = 0; i < 1000; ++i) assert(r.next() == same.next());
    for (unsigned bound : {1u, 2u, 7u, 100u, 2147483649u, 4294967295u})
        for (int i = 0; i < 1000; ++i) assert(r.below(bound) < bound);
    for (int n : {0, 1, 2, 100}) {
        int order[102], other[102];
        hc::iota(order, 102); hc::iota(other, 102);
        r.reset(55); same.reset(55);
        if (n > 1) { r.shuffle(order + 1, n - 1); same.shuffle(other + 1, n - 1); }
        else { r.shuffle(order, n); same.shuffle(other, n); }
        assert(order[0] == 0 && order[n] == n);
        assert(std::equal(order, order + 102, other));
        std::sort(order, order + n);
        for (int i = 0; i < n; ++i) assert(order[i] == i);
    }

    std::mt19937 referenceRng(20260908);
    for (int n : {0, 1, 2, 3, 31, 100, 4097, 1000000}) {
        std::vector<long long> key(n);
        std::vector<int> id(n), temp(n), expected(n);
        for (int i = 0; i < n; ++i) {
            key[i] = ((int)(referenceRng() % 17) - 8) * 10000000000LL;
            id[i] = i;
        }
        std::shuffle(id.begin(), id.end(), referenceRng); expected = id;
        std::sort(expected.begin(), expected.end(), [&](int a, int b) {
            return std::make_pair(key[a], a) < std::make_pair(key[b], b);
        });
        hc::sortIds(id.data(), temp.data(), n, key.data());
        assert(id == expected);
    }

    hc::Queue<3> q; q.clear();
    int value = 99;
    assert(!q.pop(value) && value == 99);
    assert(q.push(7) && q.push(3) && q.push(5));
    assert(!q.push(8));
    for (int want : {7, 3, 5}) assert(q.pop(value) && value == want);
    assert(!q.pop(value) && !q.push(9)); // Cumulative capacity until clear.
    q.clear(); assert(q.push(11) && q.pop(value) && value == 11);

    hc::MinHeap<257> heap; heap.clear();
    using Pair = std::pair<long long, int>;
    std::priority_queue<Pair, std::vector<Pair>, std::greater<Pair>> expectedHeap;
    hc::HeapItem item = {123, 456};
    assert(!heap.pop(item) && item.key == 123 && item.id == 456);
    for (int i = 0; i < 20000; ++i) {
        if (referenceRng() % 3 != 0) {
            Pair candidate = {((int)(referenceRng() % 23) - 11) * 10000000000LL, (int)(referenceRng() % 20)};
            bool fits = expectedHeap.size() < 257;
            assert(heap.push(candidate.first, candidate.second) == fits);
            if (fits) expectedHeap.push(candidate);
        } else {
            bool have = !expectedHeap.empty();
            assert(heap.pop(item) == have);
            if (have) { assert(Pair(item.key, item.id) == expectedHeap.top()); expectedHeap.pop(); }
        }
    }
    while (!expectedHeap.empty()) {
        assert(heap.pop(item) && Pair(item.key, item.id) == expectedHeap.top());
        expectedHeap.pop();
    }
    assert(!heap.pop(item));
    assert(heap.push(1, 0)); heap.clear(); assert(!heap.pop(item));
    hc::MinHeap<1> one; one.clear();
    assert(one.push(5, 7) && !one.push(0, 0));
    assert(one.pop(item) && item.key == 5 && item.id == 7 && !one.pop(item));

    for (int n : {4000, 1, 0, 4000}) {
        hc::fill(hc_example::used, 4000, 7);
        hc_example::totalCost = 123;
        assert(hc_example::resetCase(n));
        assert(hc_example::itemCount == n && hc_example::totalCost == 0);
        for (int i = 0; i < n; ++i) assert(hc_example::used[i] == 0);
    }
    assert(!hc_example::resetCase(-1) && !hc_example::resetCase(4001));
    int points[100][2] = {}, order[102];
    for (int n : {100, 4, 1, 0, 100}) {
        hc::fill(order, 102, -1);
        build_path(n, points, order + 1);
        assert(order[0] == -1 && order[n + 1] == -1);
        for (int i = 0; i < n; ++i) assert(order[i + 1] == i);
    }
}
'''


def main() -> None:
    snippets = read_snippets()
    with tempfile.TemporaryDirectory(prefix="hcontest-cpp-basics-") as directory:
        work = Path(directory)
        source = work / "check.cpp"
        binary = work / "check"
        source.write_text("\n\n".join(snippets.values()) + "\n" + HARNESS)
        compiler = shlex.split(os.environ.get("CXX", "c++"))
        subprocess.run(compiler + ["-std=c++17", "-O1", "-g", "-Wall", "-Wextra",
                                  "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                                  str(source), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True, timeout=30)
    print(f"OK: {len(snippets)} STL-free lesson snippets; boundary, differential and sanitizer checks passed")


if __name__ == "__main__":
    main()
