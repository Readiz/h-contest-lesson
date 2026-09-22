"""Check the published ORDERING search blocks and optionally benchmark a local judge."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def blocks(path: str) -> list[str]:
    return re.findall(r"```cpp[^\n]*\n(.*?)\n```", (ROOT / path).read_text(), re.S)


def snippet(path: str, name: str) -> str:
    text = (ROOT / path).read_text()
    found = re.findall(r"```cpp[^\n]*\bsnippet=" + re.escape(name) + r"\n(.*?)\n```", text, re.S)
    assert len(found) == 1, (path, name)
    return found[0]


def sources() -> dict[str, str]:
    basics = "lessons/cpp-contest-basics/pages/"
    search = "lessons/heuristic/pages/search-strategies.md"
    route = blocks("lessons/heuristic/pages/ordering-route-improvement.md")[-1]
    assert route.count("void build_path(") == 1
    initial = route.replace("void build_path(", "void build_initial_path(")
    random = snippet("lessons/cpp-common-library/lesson.md", "random")
    anneal = snippet(search, "ordering-sa")
    entry = snippet(search, "ordering-sa-entry")
    common = "\n".join([initial, random, anneal])
    values = {
        "numbered": snippet(basics + "submission-and-state.md", "ordering-baseline"),
        "nearest": route[:route.index("    for (int pass = 0;")] + "}\n",
        "two-opt": route,
        "hill-climbing": common + "\n" + entry.replace("128.0, 1.0", "0.0, 0.0"),
        "annealing": common + "\n" + entry,
        "common": common,
    }
    for name, code in values.items():
        assert not re.search(r"^\s*#\s*(include|pragma)\b|\bstd\s*::|\bextern\s*\"", code, re.M), name
    return values


HARNESS = r'''
#include <algorithm>
#include <cassert>
#include <cmath>
#include <random>
#include <vector>

int points[100][2], countPoints;
int get_dist(int a, int b) {
    assert(0 <= a && a < countPoints && 0 <= b && b < countPoints);
    return std::abs(points[a][0] - points[b][0]) + std::abs(points[a][1] - points[b][1]);
}
int get_path_dist(const int a[], int n) {
    int answer = 0;
    for (int i = 1; i < n; ++i) answer += get_dist(a[i-1], a[i]);
    return answer;
}
void valid(const int a[], int n) {
    assert(a[0] == 0);
    std::vector<int> sorted(a, a+n);
    std::sort(sorted.begin(), sorted.end());
    for (int i = 0; i < n; ++i) assert(sorted[i] == i);
}
int main() {
    for (int i = 0; i <= 320000; ++i) {
        double x = i / 10000.0;
        double actual = ordering_sa::expNegative(x);
        assert(0.0 <= actual && actual <= 1.0);
        assert(std::abs(actual - std::exp(-x)) < 1e-11);
    }
    countPoints = 6;
    const int fixed[6][2] = {{18,8},{17,4},{18,12},{9,4},{2,12},{12,19}};
    for (int i = 0; i < 6; ++i) for (int j = 0; j < 2; ++j) points[i][j] = fixed[i][j];
    int trapped[] = {0,1,3,4,2,5};
    assert(get_path_dist(trapped, 6) == 57);
    for (int l = 1; l < 5; ++l) for (int r = l+1; r < 6; ++r)
        assert(ordering_sa::delta(6, trapped, l, r) > 0);
    reverse_range(trapped, 1, 3); assert(get_path_dist(trapped, 6) == 65);
    reverse_range(trapped, 1, 4); assert(get_path_dist(trapped, 6) == 53);
    int permutation[] = {0,1,2,3,4,5}, optimum = 1000000;
    do { optimum = std::min(optimum, get_path_dist(permutation, 6)); }
    while (std::next_permutation(permutation+1, permutation+6));
    assert(optimum == 53);

    std::mt19937 reference(20260922);
    const int boundarySizes[] = {1,2,3,99,100};
    for (int trial = 0; trial < 200; ++trial) {
        int n = trial < 5 ? boundarySizes[trial] : 3 + reference()%10;
        countPoints = n;
        for (int i = 0; i < n; ++i) {
            points[i][0] = trial%7 == 0 ? 0 : reference()%1000;
            points[i][1] = trial%7 == 0 ? 0 : reference()%1000;
        }
        int initial[100];
        for (int i = 0; i < n; ++i) initial[i] = i;
        std::shuffle(initial+1, initial+n, reference);
        int original = get_path_dist(initial, n);
        for (int l = 1; l < n-1; ++l) for (int r = l+1; r < n; ++r) {
            int predicted = ordering_sa::delta(n, initial, l, r);
            reverse_range(initial, l, r);
            assert(get_path_dist(initial, n) - original == predicted);
            reverse_range(initial, l, r);
            assert(get_path_dist(initial, n) == original);
        }
        build_initial_path(n, points, initial);
        valid(initial, n);
        for (int attempts : {0,1,500}) for (double temperature : {0.0,128.0}) {
            int a[100], b[100];
            std::copy(initial, initial+n, a); std::copy(initial, initial+n, b);
            unsigned seed = reference();
            auto one = ordering_sa::improve(n, a, attempts, seed, temperature, 0.0);
            auto two = ordering_sa::improve(n, b, attempts, seed, temperature, 0.0);
            valid(a, n); valid(b, n);
            assert(std::equal(a, a+n, b));
            assert(one.bestCost == two.bestCost && one.currentCost == two.currentCost);
            assert(one.accepted == two.accepted && one.acceptedWorse == two.acceptedWorse);
            assert(one.bestCost == get_path_dist(a, n));
            assert(one.bestCost <= get_path_dist(initial, n));
            assert(one.bestCost <= one.currentCost);
            if (temperature == 0.0) assert(one.acceptedWorse == 0);
            if (attempts == 0 || n <= 2) {
                assert(std::equal(a, a+n, initial));
                assert(one.accepted == 0);
            }
        }
    }
}
'''


def run_checks(values: dict[str, str]) -> None:
    # Callbacks follow the lesson declarations; headers belong only to this harness.
    with tempfile.TemporaryDirectory(prefix="lesson-heuristic-") as folder:
        src = Path(folder) / "check.cpp"
        exe = Path(folder) / "check"
        src.write_text(values["common"] + "\n" + HARNESS)
        subprocess.run(["c++", "-std=c++17", "-O1", "-g", "-fsanitize=address,undefined",
                        "-fno-sanitize-recover=all", str(src), "-o", str(exe)], check=True)
        subprocess.run([str(exe)], check=True, timeout=60)
    print("OK: ORDERING local minimum, all-move deltas, SA bounds/best/replay, no-header composition (ASan/UBSan)")


def benchmark(values: dict[str, str], judge: Path, output: Path) -> None:
    original = judge.read_text()
    assert original.count("int main(void)") == 1
    driver = '#include <chrono>\n' + original.replace("int main(void)", "int judge_run(void)") + r'''
int main() {
    for (int run = 0; run < 9; ++run) {
        auto start = std::chrono::steady_clock::now();
        judge_run();
        auto end = std::chrono::steady_clock::now();
        double ms = std::chrono::duration<double, std::milli>(end-start).count();
        fprintf(stderr, "BENCH %.9f\n", ms);
    }
}
'''
    result = {"judge_sha256": hashlib.sha256(judge.read_bytes()).hexdigest(), "seed": 20260922,
              "additional_attempts": 30000, "rounds": 9, "warmup_rounds": 1, "rows": []}
    with tempfile.TemporaryDirectory(prefix="lesson-ordering-bench-") as folder:
        d = Path(folder)
        (d / "judge.cpp").write_text(driver)
        for optimization in ("-O0", "-O2"):
            for name in ("numbered", "nearest", "two-opt", "hill-climbing", "annealing"):
                (d / "user.cpp").write_text(values[name])
                subprocess.run(["c++", "-std=c++17", optimization, str(d / "judge.cpp"), str(d / "user.cpp"), "-o", str(d / "bench")], check=True)
                r = subprocess.run([str(d / "bench")], check=True, capture_output=True, text=True, timeout=60)
                totals = [int(v) for v in re.findall(r"^SCORE: (\d+)$", r.stdout, re.M)]
                cases = [int(v) for v in re.findall(r"^TC \d+ SCORE: (\d+)$", r.stdout, re.M)]
                times = [float(v) for v in re.findall(r"BENCH ([\d.]+)", r.stderr)]
                assert len(totals) == len(times) == 9 and len(cases) == 90
                assert len(set(totals)) == 1 and max(cases) < 10**12
                assert all(cases[i:i+10] == cases[:10] for i in range(0, 90, 10))
                row = {"name": name, "optimization": optimization, "total": totals[0], "costs": cases[:10],
                       "median_ms": statistics.median(times[1:]), "runs_ms": times[1:]}
                result["rows"].append(row)
                print(json.dumps(row), flush=True)
    output.write_text(json.dumps(result, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    values = sources()
    run_checks(values)
    if args.judge:
        if not args.output:
            parser.error("--judge requires --output")
        benchmark(values, args.judge, args.output)


if __name__ == "__main__":
    main()
