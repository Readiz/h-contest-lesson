"""Check the TAXIASSIGN lesson (assignment + route): extracted code, hand example, failures, measurements.

Without --judge only the checks that need no grader run: header-free composition, every
relocate/swap difference against a full recomputation written independently of the lesson code
(ASan/UBSan), the hand example (all 16 assignments by brute force), the two failing variants
(they must be detected), and the stored benchmark against the lesson tables.
With --judge /path/to/TAXIASSIGN/main.cpp --output FILE the measurements are repeated and
FILE (normally lessons/assignment-with-routes/lesson-assets/taxiassign-benchmark.json) is written.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import itertools
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpp_library import check_submission_code, read_library_snippets  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "lessons/assignment-with-routes/lesson.md"
ASSETS = ROOT / "lessons/assignment-with-routes/lesson-assets"
ASSET = ASSETS / "taxiassign-benchmark.json"
FIG_HAND = ASSETS / "hand-two-answers.svg"
FIG_MOVE = ASSETS / "hand-neighbors.svg"
MAX_TC = 5
PASS_LINE = 431_000_000
SEEDS = list(range(1, 10))
SNIPPETS = ("taxi-contract", "taxi-baseline", "taxi-plan", "taxi-delta", "taxi-stages", "taxi-greedy", "taxi-climb", "taxi-entry")

# Hand example: 2 drivers, 4 passengers, (y, x) coordinates. Passenger = (departure, arrival).
HAND_DRIVERS = [(2, 7), (9, 2)]
HAND_PAS = [((8, 7), (7, 11)), ((11, 5), (7, 4)), ((4, 7), (6, 2)), ((1, 6), (8, 2))]
GREEDY_ROUTES = [[2, 0], [1, 3]]


def snippet(name: str) -> str:
    found = re.findall(r"```cpp[^\n]*\bsnippet=" + re.escape(name) + r"\n(.*?)\n```", LESSON.read_text(), re.S)
    assert len(found) == 1, name
    return found[0] + "\n"


def sources() -> dict[str, str]:
    random = read_library_snippets()["random"]
    blocks = {name: snippet(name) for name in SNIPPETS}
    for name, code in blocks.items():
        check_submission_code(code, name)
    contract, baseline, plan, delta, stages, greedy, climb, entry = (blocks[n] for n in SNIPPETS)
    common = "\n".join([random, contract, plan, delta, stages, greedy, climb])   # + stages for the experiments
    final = "\n".join([random, contract, plan, delta, greedy, climb, entry])      # what is submitted
    return {"baseline": contract + "\n" + baseline, "common": common, "with_entry": common + "\n" + entry, "final": final, "blocks": blocks, "random": random}


# ---------------------------------------------------------------- hand example (independent of the lesson code)
def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def route_load(driver, order):
    pos, total = HAND_DRIVERS[driver], 0
    for i in order:
        dep, arr = HAND_PAS[i]
        total += dist(pos, dep) + dist(dep, arr)
        pos = arr
    return total


def best_order(driver, ids):
    if not ids:
        return 0, ()
    return min((route_load(driver, perm), perm) for perm in itertools.permutations(ids))


def model_cost(driver, i):
    dep, arr = HAND_PAS[i]
    return dist(HAND_DRIVERS[driver], dep) + dist(dep, arr)


def hand_rows() -> list[dict]:
    rows = []
    for mask in range(16):
        sets = [[i for i in range(4) if (mask >> i) & 1], [i for i in range(4) if not (mask >> i) & 1]]
        model = [sum(model_cost(d, i) for i in sets[d]) for d in (0, 1)]
        best = [best_order(d, sets[d]) for d in (0, 1)]
        rows.append({"sets": sets, "model": model, "best": best, "real": max(best[0][0], best[1][0])})
    return rows


def hand_facts() -> dict:
    rows = hand_rows()
    model_min = min(max(r["model"]) for r in rows)
    real_min = min(r["real"] for r in rows)
    model_opt = [r for r in rows if max(r["model"]) == model_min]
    real_opt = [r for r in rows if r["real"] == real_min]
    assert len(model_opt) == 1 and len(real_opt) == 1 and model_opt[0] is not real_opt[0]
    return {"rows": rows, "model_min": model_min, "model_opt": model_opt[0], "real_min": real_min, "real_opt": real_opt[0]}


def fmt_set(s):
    return "{" + ",".join(map(str, s)) + "}"


def fmt_best(load, perm):
    return f"{load}" + (f" ({'→'.join(map(str, perm))})" if perm else "")


def hand_table() -> str:
    facts = hand_facts()
    lines = ["| 기사 0 / 기사 1 | 배정만 본 부하 | 최적 순서의 실제 부하 | 실제 점수 |", "| --- | --- | --- | ---: |"]
    for r in facts["rows"]:
        label = f"{fmt_set(r['sets'][0])} / {fmt_set(r['sets'][1])}"
        model = f"{r['model'][0]} / {r['model'][1]} → {max(r['model'])}"
        real = f"{fmt_best(*r['best'][0])} / {fmt_best(*r['best'][1])}"
        score = str(r["real"])
        if r is facts["model_opt"]:
            label, model, score = f"**{label}**", f"**{model}**", f"**{score}**"
        if r is facts["real_opt"]:
            label, score = f"**{label}**", f"**{score}**"
        lines.append(f"| {label} | {model} | {real} | {score} |")
    return "\n".join(lines)


def hand_text() -> str:
    pas = ", ".join(f"승객 {i} ({dep[0]},{dep[1]})→({arr[0]},{arr[1]}) 탑승 {dist(dep, arr)}" for i, (dep, arr) in enumerate(HAND_PAS))
    return f"기사 0은 ({HAND_DRIVERS[0][0]},{HAND_DRIVERS[0][1]}), 기사 1은 ({HAND_DRIVERS[1][0]},{HAND_DRIVERS[1][1]})에서 출발하고, {pas}입니다."


def trap_neighbors(routes: list[list[int]]) -> int:
    """Smallest max load over every relocation (any gap) and slot swap of the given state, brute force."""
    best = 10**9
    for x in range(4):
        a = 0 if x in routes[0] else 1
        for b in (0, 1):
            base = [list(routes[0]), list(routes[1])]
            base[a].remove(x)
            for pos in range(len(base[b]) + 1):
                r = [list(base[0]), list(base[1])]
                r[b].insert(pos, x)
                if r != routes:
                    best = min(best, max(route_load(0, r[0]), route_load(1, r[1])))
    for x in routes[0]:
        for y in routes[1]:
            r = [[y if v == x else v for v in routes[0]], [x if v == y else v for v in routes[1]]]
            best = min(best, max(route_load(0, r[0]), route_load(1, r[1])))
    return best


def expected_moves() -> dict:
    """Independent numbers for the moves used in the text (state: GREEDY_ROUTES)."""
    out = {}
    base = [list(r) for r in GREEDY_ROUTES]
    out["start"] = [route_load(d, base[d]) for d in (0, 1)]
    swap = [list(r) for r in base]
    swap[0][swap[0].index(2)], swap[1][swap[1].index(3)] = 3, 2
    out["swap"] = [route_load(d, swap[d]) for d in (0, 1)]
    out["swap_routes"] = swap
    reloc = []
    for pos in range(3):
        r = [list(base[0]), [1]]
        r[0] = [2, 0]
        r[0].insert(pos, 3)
        reloc.append([route_load(0, r[0]), route_load(1, [1])])
    out["reloc"] = reloc
    return out


# ---------------------------------------------------------------- C++ harness
HARNESS = r'''
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <random>
#include <vector>

static std::vector<int> got[taxi::MAX_M];
bool assign_driver(int d, int n, int ids[]) { got[d].assign(ids, ids + n); return true; }

static taxi::Plan P, Q;

static int ab(int v) { return v < 0 ? -v : v; }
typedef std::vector<std::vector<int>> Routes;

// Reference cost written from the problem statement, independent of the lesson's hop().
static long long refLoad(const taxi::Plan& p, int d, const std::vector<int>& r) {
    long long s = 0;
    int y = p.ay[p.k + d], x = p.ax[p.k + d];
    for (int q : r) {
        s += ab(y - p.dy[q]) + ab(x - p.dx[q]) + ab(p.ay[q] - p.dy[q]) + ab(p.ax[q] - p.dx[q]);
        y = p.ay[q]; x = p.ax[q];
    }
    return s;
}
static Routes routesOf(const taxi::Plan& p) {
    Routes r(p.m);
    for (int d = 0; d < p.m; ++d) for (int i = 0; i < p.len[d]; ++i) r[d].push_back(p.route[d][i]);
    return r;
}
static void sameAsReference(const taxi::Plan& p) {
    Routes r = routesOf(p);
    long long total = 0, mx = 0;
    std::vector<int> seen(p.k, 0);
    for (int d = 0; d < p.m; ++d) {
        long long l = refLoad(p, d, r[d]);
        assert(l == p.load[d]);
        total += l; mx = std::max(mx, l);
        for (int i = 0; i < (int)r[d].size(); ++i) {
            assert(p.owner[r[d][i]] == d && p.pos[r[d][i]] == i);
            ++seen[r[d][i]];
        }
    }
    for (int i = 0; i < p.k; ++i) assert(seen[i] == 1);
    assert(total == p.total && mx == p.maxLoad);
}
static void expectChange(const taxi::Plan& p, const Routes& after, const taxi::Change& c) {
    long long total = 0, mx = 0;
    for (int d = 0; d < p.m; ++d) {
        long long l = refLoad(p, d, after[d]);
        total += l; mx = std::max(mx, l);
        if (d == c.a) assert(l == c.loadA);
        if (d == c.b && c.a != c.b) assert(l == c.loadB);
    }
    assert(total == c.total && mx == c.maxLoad);
}
static Routes relocated(const taxi::Plan& p, int x, int q) {
    Routes r = routesOf(p);
    r[p.owner[x]].erase(std::find(r[p.owner[x]].begin(), r[p.owner[x]].end(), x));
    if (q >= p.k) r[q - p.k].insert(r[q - p.k].begin(), x);
    else { auto& v = r[p.owner[q]]; v.insert(std::find(v.begin(), v.end(), q) + 1, x); }
    return r;
}
static Routes swapped(const taxi::Plan& p, int x, int y) {
    Routes r = routesOf(p);
    *std::find(r[p.owner[x]].begin(), r[p.owner[x]].end(), x) = y;
    *std::find(r[p.owner[y]].begin(), r[p.owner[y]].end(), y) = x;
    return r;
}

static Coordinate drv[taxi::MAX_M];
static Passenger pas[taxi::MAX_K];
static void randomInstance(std::mt19937& rng, int m, int k, int range) {
    for (int d = 0; d < m; ++d) { drv[d].y = (int)(rng() % range); drv[d].x = (int)(rng() % range); }
    for (int i = 0; i < k; ++i) {
        pas[i].departure.y = (int)(rng() % range); pas[i].departure.x = (int)(rng() % range);
        pas[i].arrival.y = (int)(rng() % range); pas[i].arrival.x = (int)(rng() % range);
    }
    taxi::init(P, m, drv, k, pas);
}
static void randomRoutes(taxi::Plan& p, std::mt19937& rng) {
    for (int d = 0; d < p.m; ++d) p.len[d] = 0;
    std::vector<int> ids(p.k);
    for (int i = 0; i < p.k; ++i) ids[i] = i;
    std::shuffle(ids.begin(), ids.end(), rng);
    for (int i : ids) { int d = (int)(rng() % p.m); p.route[d][p.len[d]++] = i; }
    taxi::rebuild(p);
}

static void handExample() {
    const int dy[2] = {2, 9}, dx[2] = {7, 2};
    const int py[4][4] = {{8, 7, 7, 11}, {11, 5, 7, 4}, {4, 7, 6, 2}, {1, 6, 8, 2}};
    for (int d = 0; d < 2; ++d) { drv[d].y = dy[d]; drv[d].x = dx[d]; }
    for (int i = 0; i < 4; ++i) {
        pas[i].departure.y = py[i][0]; pas[i].departure.x = py[i][1];
        pas[i].arrival.y = py[i][2]; pas[i].arrival.x = py[i][3];
    }
    taxi::init(P, 2, drv, 4, pas);
    // all 16 assignments, every order, by brute force
    for (int mask = 0; mask < 16; ++mask) {
        long long best[2];
        for (int d = 0; d < 2; ++d) {
            std::vector<int> ids;
            for (int i = 0; i < 4; ++i) if (((mask >> i) & 1) == (d == 0 ? 1 : 0)) ids.push_back(i);
            std::sort(ids.begin(), ids.end());
            best[d] = refLoad(P, d, ids);
            while (std::next_permutation(ids.begin(), ids.end())) best[d] = std::min(best[d], refLoad(P, d, ids));
        }
        std::printf("HANDROW %d %lld %lld\n", mask, best[0], best[1]);
    }
    taxi::nearestFree(P);
    assert(P.len[0] == 2 && P.route[0][0] == 2 && P.route[0][1] == 0);
    assert(P.len[1] == 2 && P.route[1][0] == 1 && P.route[1][1] == 3);
    std::printf("HANDGREEDY %lld %lld\n", P.load[0], P.load[1]);
    sameAsReference(P);
    // swap 2 <-> 3: both drivers are optimal afterwards
    taxi::Change s = taxi::finish(P, taxi::swapChange(P, 2, 3));
    expectChange(P, swapped(P, 2, 3), s);
    std::printf("HANDSWAP %lld %lld %lld\n", s.loadA, s.loadB, s.maxLoad);
    // relocate 3 to driver 0 after node q: front (driver node), after 2, after 0
    const int qs[3] = {P.k + 0, 2, 0};
    for (int i = 0; i < 3; ++i) {
        taxi::Change c = taxi::finish(P, taxi::relocateChange(P, 3, qs[i]));
        expectChange(P, relocated(P, 3, qs[i]), c);
        std::printf("HANDRELOC %d %lld %lld %lld\n", i, c.loadB, c.loadA, c.maxLoad);
    }
    // the search from the greedy state, solver seeds 1..9: it ends at 23 or in the model-optimal trap 29
    for (unsigned seed = 1; seed <= 9; ++seed) {
        taxi::nearestFree(P);
        taxi::Params prm = {3000, seed, 8.0, 30, 60, 3};
        long long best = taxi::climb(P, prm);
        sameAsReference(P);
        assert(best == P.maxLoad);
        std::printf("HANDCLIMB %u %lld\n", seed, best);
    }
}

static void stress() {
    std::mt19937 rng(20261118);
    const int ranges[] = {3, 50, 1000000};
    for (int trial = 0; trial < 240; ++trial) {
        int m = 2 + (int)(rng() % 5), k = 2 + (int)(rng() % 24);
        randomInstance(rng, m, k, ranges[trial % 3]);
        randomRoutes(P, rng);
        sameAsReference(P);
        for (int x = 0; x < k; ++x) {
            for (int q = 0; q < k + m; ++q) {
                if (q == x || q == taxi::prevOf(P, x)) continue;
                taxi::Change c = taxi::finish(P, taxi::relocateChange(P, x, q));
                expectChange(P, relocated(P, x, q), c);
            }
            for (int y = 0; y < k; ++y) {
                if (P.owner[x] == P.owner[y]) continue;
                taxi::Change c = taxi::finish(P, taxi::swapChange(P, x, y));
                expectChange(P, swapped(P, x, y), c);
            }
        }
        // apply every kind of proposal and compare the cached state with the reference
        hc::Random r;
        r.reset(trial + 1u);
        taxi::Params prm = {0, 1u, 8.0, 40, 50, 1 + trial % 4};
        for (int step = 0; step < 200; ++step) {
            int worst = 0;
            for (int d = 1; d < m; ++d) if (P.load[d] > P.load[worst]) worst = d;
            taxi::Move mv = taxi::propose(P, r, prm, worst);
            if (mv.kind < 0) continue;
            if (mv.kind == 1) { assert(P.owner[mv.x] != P.owner[mv.y]); taxi::applySwap(P, mv.x, mv.y, mv.after); }
            else { taxi::applyRelocate(P, mv.x, mv.y, mv.after); }
            sameAsReference(P);
        }
    }
}

static void stagesAndClimb() {
    std::mt19937 rng(20261119);
    for (int trial = 0; trial < 60; ++trial) {
        int m = 1 + (int)(rng() % 6), k = 1 + (int)(rng() % 40);
        randomInstance(rng, m, k, trial % 2 ? 40 : 100000);
        taxi::balanceRides(P);             sameAsReference(P);
        long long before = P.maxLoad;
        for (int d = 0; d < m; ++d) { long long l = P.load[d]; taxi::improveRoute(P, d); assert(P.load[d] <= l); }
        sameAsReference(P);
        (void)before;
        if (m >= 2) { long long l = P.maxLoad; taxi::alternate(P); assert(P.maxLoad <= l); sameAsReference(P); }
        taxi::nearestFree(P);              sameAsReference(P);
        for (long long attempts : {0LL, 1LL, 400LL}) for (double w : {0.0, 8.0}) {
            std::memcpy(&Q, &P, sizeof(P));
            taxi::Params prm = {attempts, (unsigned)rng(), w, 30, 60, 3};
            long long b1 = taxi::climb(P, prm);
            sameAsReference(P);
            assert(P.maxLoad == b1 && b1 <= Q.maxLoad);
            taxi::Plan* keep = &P; (void)keep;
            std::vector<std::vector<int>> r1 = routesOf(P);
            std::memcpy(&P, &Q, sizeof(P));
            long long b2 = taxi::climb(P, prm);
            assert(b1 == b2 && routesOf(P) == r1);  // same seed, same answer
            if (attempts == 0 || k < 2 || m < 2) assert(b1 == Q.maxLoad);
        }
    }
}

static void entry() {
    std::mt19937 rng(20261120);
    const int shapes[][2] = {{1, 1}, {1, 3}, {3, 5}, {7, 2}, {40, 6}, {2000, 51}};
    for (auto s : shapes) {
        int k = s[0], m = s[1];
        std::vector<Coordinate> d(m);
        std::vector<Passenger> ps(k);
        for (auto& c : d) { c.y = (int)(rng() % 1000000); c.x = (int)(rng() % 1000000); }
        for (auto& q : ps) { q.departure.y = (int)(rng() % 1000000); q.departure.x = (int)(rng() % 1000000); q.arrival.y = (int)(rng() % 1000000); q.arrival.x = (int)(rng() % 1000000); }
        for (int i = 0; i < m; ++i) got[i].clear();
        run(1000000, m, d.data(), k, ps.data());
        std::vector<int> seen(k, 0);
        for (int i = 0; i < m; ++i) for (int q : got[i]) { assert(0 <= q && q < k); ++seen[q]; }
        for (int i = 0; i < k; ++i) assert(seen[i] == 1);
    }
}

int main() {
    handExample();
    stress();
    stagesAndClimb();
    entry();
    std::puts("HARNESS OK");
}
'''

# Experiment entry used only for measurements; the lesson's own entry is built separately.
EXP_ENTRY = r'''
#include <stdio.h>
#include <stdlib.h>
static double envNumber(const char* key, double fallback) {
    const char* v = getenv(key);
    return v ? atof(v) : fallback;
}
void run(int N, int M, Coordinate mDriver[], int K, Passenger mPassenger[]) {
    static taxi::Plan plan;
    taxi::init(plan, M, mDriver, K, mPassenger);
    int init = (int)envNumber("INIT", 4);     // 0 번호, 1 탑승합 균형, 2 +경로, 3 +번갈아, 4 결합 탐욕
    int search = (int)envNumber("SEARCH", 1); // 0 없음, 1 결합 이웃 탐색
    if (init == 0) {
        for (int i = 0; i < plan.k; ++i) plan.route[i % plan.m][plan.len[i % plan.m]++] = i;
        taxi::rebuild(plan);
    } else if (init == 4) taxi::nearestFree(plan);
    else {
        taxi::balanceRides(plan);
        if (init >= 2) for (int d = 0; d < plan.m; ++d) taxi::improveRoute(plan, d);
        if (init >= 3) taxi::alternate(plan);
    }
    long long initMax = plan.maxLoad, bestMax = initMax;
    if (search > 0) {
        taxi::Params prm;
        prm.attempts = (long long)envNumber("ATTEMPTS", 400000);
        prm.seed = (unsigned)envNumber("SEED", 20261118);
        prm.weight = envNumber("WEIGHT", 8.0);
        prm.swapPercent = (int)envNumber("SWAP", 30);
        prm.focusPercent = (int)envNumber("FOCUS", 60);
        prm.choices = (int)envNumber("CHOICES", 3);
        bestMax = taxi::climb(plan, prm);
    }
    taxi::rebuild(plan);
    if (plan.maxLoad != bestMax) fprintf(stderr, "BROKEN %lld %lld\n", plan.maxLoad, bestMax);
    long long ridesum = 0;
    for (int i = 0; i < K; ++i) ridesum += plan.ride[i];
    taxi::submit(plan);
    fprintf(stderr, "EXP %d %d %lld %lld %lld\n", K, M, initMax, bestMax, ridesum / M);
}
'''

EXPERIMENTS = [
    ("본문 설정", {}),
    ("교환 없이 이동만", {"SWAP": "0"}),
    ("승객을 무작위로만 고름(집중 0%)", {"FOCUS": "0"}),
    ("평균 부하 항 가중치 0", {"WEIGHT": "0"}),
    ("가중치 1", {"WEIGHT": "1"}),
    ("가중치 16", {"WEIGHT": "16"}),
    ("대상 기사 후보 1명", {"CHOICES": "1"}),
    ("대상 기사 후보 6명", {"CHOICES": "6"}),
    ("제안 100,000개", {"ATTEMPTS": "100000"}),
    ("제안 2,000,000개", {"ATTEMPTS": "2000000"}),
]

# Failing variants shown in the lesson: (old text, new text) in the delta block.
BUG_CUT = ("    if (na >= 0) cut += hop(p, x, na) - hop(p, pa, na);  // pa에서 na로 바로 이어진다.",
           "    if (na >= 0) cut += hop(p, x, na);                   // pa에서 na로 바로 이어지는 구간을 빠뜨린다.")
BUG_AT = ("    int a = p.owner[x], b = c.b;\n    for (int j = p.pos[x]",
          "    int a = p.owner[x], b = c.b, stale = q >= p.k ? 0 : p.pos[q] + 1;  // 빼기 전의 위치\n    for (int j = p.pos[x]")
BUG_AT2 = ("    int at = q >= p.k ? 0 : p.pos[q] + 1;            // 같은 기사라면 pos[q]는 이미 당겨진 값이다.",
           "    int at = stale;")


def apply_bug(code: str, edits: list[tuple[str, str]]) -> str:
    for old, new in edits:
        assert old in code, old
        code = code.replace(old, new, 1)
    return code


def compile_run(code: str, flags: list[str], expect_ok: bool = True, timeout: int = 300):
    with tempfile.TemporaryDirectory(prefix="lesson-taxi-") as folder:
        src, exe = Path(folder) / "check.cpp", Path(folder) / "check"
        src.write_text(code)
        subprocess.run(["c++", "-std=c++17", *flags, str(src), "-o", str(exe)], check=True)
        result = subprocess.run([str(exe)], capture_output=True, text=True, timeout=timeout)
    if expect_ok:
        assert result.returncode == 0, result.stderr[-2000:] + result.stdout[-500:]
    return result


def run_checks(values: dict) -> dict:
    sanitize = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
    # The submitted file must compile on its own (only the grader-provided symbol is missing).
    stub = "bool assign_driver(int, int, int[]) { return true; }\nint main() {}\n"
    compile_run(values["final"] + "\n" + stub, ["-O1", "-Wall", "-Werror"])
    compile_run(values["baseline"] + "\n" + stub, ["-O1", "-Wall", "-Werror"])
    result = compile_run(values["with_entry"] + "\n" + HARNESS, sanitize)
    assert "HARNESS OK" in result.stdout
    # hand example against the independent brute force
    rows = hand_rows()
    printed = {}
    for line in result.stdout.splitlines():
        if line.startswith("HANDROW "):
            _, mask, a, b = line.split()
            printed[int(mask)] = (int(a), int(b))
    for mask, row in enumerate(rows):
        assert printed[mask] == (row["best"][0][0], row["best"][1][0]), (mask, printed[mask], row)
    exp = expected_moves()
    lines = {l.split()[0]: l.split()[1:] for l in result.stdout.splitlines() if l.startswith(("HANDGREEDY", "HANDSWAP"))}
    climbs = [int(l.split()[2]) for l in result.stdout.splitlines() if l.startswith("HANDCLIMB")]
    assert [int(v) for v in lines["HANDGREEDY"]] == exp["start"], lines
    assert [int(v) for v in lines["HANDSWAP"][:2]] == exp["swap"], lines
    relocs = [l.split()[1:] for l in result.stdout.splitlines() if l.startswith("HANDRELOC")]
    for i, (idx, load_b, load_a, mx) in enumerate(relocs):
        assert [int(load_b), int(load_a)] == exp["reloc"][i], (relocs, exp)
    facts = hand_facts()
    assert len(climbs) == 9 and set(climbs) <= {facts["real_min"], facts["model_opt"]["real"]}, climbs
    facts["climb_best"] = sum(1 for v in climbs if v == facts["real_min"])
    assert exp["start"] == [21, 29] and exp["swap"] == [23, 23] and [r[0] for r in exp["reloc"]] == [41, 39, 43], exp
    assert route_load(1, [1, 2]) == 23 and route_load(1, [2, 1]) == 30
    assert route_load(0, [2, 3]) == 29 and route_load(0, [3, 2]) == 29
    assert trap_neighbors([[2, 3], [1, 0]]) >= 29 and trap_neighbors(GREEDY_ROUTES) < 29, "trap state"
    assert facts["model_min"] == 22 and facts["model_opt"]["real"] == 29 and facts["real_min"] == 23
    # The failing variants must be caught by the same harness.
    text = LESSON.read_text()
    assert BUG_CUT[1].split("//")[0].strip() in text and "빠뜨린다" in text
    assert BUG_AT[1].split("//")[0].strip() in text and BUG_AT2[1].strip() in text
    for name, edits in (("cut", [BUG_CUT]), ("at", [BUG_AT, BUG_AT2])):
        buggy = apply_bug(values["with_entry"], edits)
        caught = compile_run(buggy + "\n" + HARNESS, sanitize, expect_ok=False)
        assert caught.returncode != 0, f"buggy variant '{name}' was not detected"
    print("OK: composition (header-free, -Wall -Werror), every relocate/swap difference and applied move, "
          f"16-assignment hand table, hand climb 23 in {facts['climb_best']}/9 seeds, climb best/reproducibility, both buggy variants detected (ASan/UBSan)")
    return facts


# ---------------------------------------------------------------- benchmark
def build_judge(judge_text: str, user_code: str, folder: Path, name: str) -> Path:
    (folder / f"{name}-judge.cpp").write_text(judge_text)
    (folder / f"{name}-user.cpp").write_text(user_code)
    exe = folder / name
    subprocess.run(["c++", "-std=c++17", "-O2", str(folder / f"{name}-judge.cpp"), str(folder / f"{name}-user.cpp"), "-o", str(exe)], check=True)
    return exe


def run_judge(exe: Path, env: dict[str, str]) -> dict:
    full = dict(os.environ, **env)
    start = time.perf_counter()
    r = subprocess.run([str(exe)], capture_output=True, text=True, env=full, timeout=600, check=True)
    ms = (time.perf_counter() - start) * 1000
    totals = [int(v) for v in re.findall(r"^SCORE: (\d+)$", r.stdout, re.M)]
    cases = [int(v) for v in re.findall(r"^TC \d+ SCORE: (\d+)$", r.stdout, re.M)]
    assert len(totals) == 1 and len(cases) == MAX_TC and max(cases) < 10**12, r.stdout
    assert "BROKEN" not in r.stderr, r.stderr
    exp = [[int(v) for v in line.split()[1:]] for line in r.stderr.splitlines() if line.startswith("EXP ")]
    return {"total": totals[0], "costs": cases, "ms": ms, "exp": exp}


def median(values):
    return statistics.median(values)


def timed_stage(exe: Path, env: dict[str, str], rounds: int = 9) -> dict:
    runs = [run_judge(exe, env) for _ in range(rounds)]
    assert len({r["total"] for r in runs}) == 1
    return {"total": runs[0]["total"], "costs": runs[0]["costs"], "median_ms": median([r["ms"] for r in runs[1:]]),
            "runs_ms": [r["ms"] for r in runs[1:]], "exp": runs[0]["exp"]}


def sweep(exe: Path, base: dict[str, str], key: str, values: list, workers: int = 4) -> list[dict]:
    jobs = [(v, s) for v in values for s in SEEDS]
    with ThreadPoolExecutor(workers) as pool:
        results = list(pool.map(lambda j: run_judge(exe, {**base, key: str(j[0]), "SEED": str(j[1])}), jobs))
    out = []
    for i, v in enumerate(values):
        totals = [r["total"] for r in results[i * len(SEEDS):(i + 1) * len(SEEDS)]]
        out.append({"value": v, "median_total": median(totals), "min_total": min(totals), "max_total": max(totals), "totals": totals})
        print(json.dumps({k: out[-1][k] for k in ("value", "median_total", "min_total", "max_total")}), flush=True)
    return out


def benchmark(values: dict, judge: Path, output: Path) -> None:
    judge_text = judge.read_text()
    exp_code = values["common"] + "\n" + EXP_ENTRY
    data: dict = {
        "judge_sha256": hashlib.sha256(judge.read_bytes()).hexdigest(),
        "measured_at": datetime.date.today().isoformat(),
        "environment": f"{platform.system()} {platform.mac_ver()[0]} {platform.machine()} / "
                       + subprocess.run(["c++", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
                       + " / -std=c++17 -O2",
        "pass_line": PASS_LINE, "timing_rounds": 9, "warmup_rounds": 1, "seeds": SEEDS,
    }
    with tempfile.TemporaryDirectory(prefix="lesson-taxi-bench-") as folder_name:
        folder = Path(folder_name)
        exp = build_judge(judge_text, exp_code, folder, "exp")
        final = build_judge(judge_text, values["final"], folder, "final")
        base = build_judge(judge_text, values["baseline"], folder, "base")
        stage_defs = [
            ("baseline", "승객 번호 % 기사 수", base, {}),
            ("balance", "배정만: 탑승 거리의 합을 맞춤", exp, {"INIT": "1", "SEARCH": "0"}),
            ("route", "+ 경로만: 기사 안에서 순서 개선", exp, {"INIT": "2", "SEARCH": "0"}),
            ("alternate", "+ 번갈아: 끝에 붙이기와 경로 개선", exp, {"INIT": "3", "SEARCH": "0"}),
            ("greedy", "결합 탐욕 초기해", exp, {"INIT": "4", "SEARCH": "0"}),
            ("alt-climb", "번갈아 결과 + 결합 이웃 탐색", exp, {"INIT": "3", "SEARCH": "1"}),
            ("climb", "결합 탐욕 + 결합 이웃 탐색", exp, {"INIT": "4", "SEARCH": "1"}),
            ("final", "본문 제출 코드", final, {}),
        ]
        stages = []
        for key, label, exe, env in stage_defs:
            r = timed_stage(exe, env)
            row = {"key": key, "label": label, "total": r["total"], "costs": r["costs"], "median_ms": r["median_ms"], "runs_ms": r["runs_ms"]}
            if key == "climb":
                row["rides_per_driver"] = [e[4] for e in r["exp"]]
                row["shapes"] = [[e[0], e[1]] for e in r["exp"]]
            stages.append(row)
            print(json.dumps({k: row[k] for k in ("key", "total", "median_ms")}), flush=True)
        by = {s["key"]: s for s in stages}
        assert by["final"]["costs"] == by["climb"]["costs"], "experiment entry differs from the lesson entry"
        data["stages"] = stages

        experiments = []
        for label, env in EXPERIMENTS:
            totals, times = [], []
            for seed in SEEDS:
                r = run_judge(exp, {"INIT": "4", **env, "SEED": str(seed)})
                totals.append(r["total"]); times.append(r["ms"])
            experiments.append({"label": label, "env": env, "median_total": median(totals), "min_total": min(totals),
                                "max_total": max(totals), "median_ms": median(times), "totals": totals})
            print(json.dumps({k: experiments[-1][k] for k in ("label", "median_total", "min_total", "max_total", "median_ms")}, ensure_ascii=False), flush=True)
        data["experiments"] = experiments

        # Wrong variants through the real grader. An invalid answer is allowed here: it is the measurement.
        data["failures"] = {}
        for name, edits in (("cut", [BUG_CUT]), ("at", [BUG_AT, BUG_AT2])):
            buggy = build_judge(judge_text, apply_bug(values["final"], edits), folder, "bug-" + name)
            r = subprocess.run([str(buggy)], capture_output=True, text=True, timeout=600, check=True)
            total = int(re.search(r"^SCORE: (\d+)$", r.stdout, re.M).group(1))
            cases = [int(v) for v in re.findall(r"^TC \d+ SCORE: (\d+)$", r.stdout, re.M)]
            data["failures"][name] = {"total": total, "costs": cases, "penalty": total >= 10**12}
            print(name, total, cases, flush=True)

    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


# ---------------------------------------------------------------- tables
def stage_table(data: dict) -> str:
    base = next(s for s in data["stages"] if s["key"] == "baseline")["total"]
    lines = ["| 방식 | TC 1 | TC 2 | TC 3 | TC 4 | TC 5 | 합 ↓ | 번호 대비 | 시간(ms) |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for s in data["stages"]:
        if s["key"] == "final":
            continue
        cost = " | ".join(str(c) for c in s["costs"])
        diff = "-" if s["key"] == "baseline" else f"{100 * (s['total'] - base) / base:+.1f}%"
        lines.append(f"| {s['label']} | {cost} | {s['total']} | {diff} | {s['median_ms']:.0f} |")
    rides = next(s for s in data["stages"] if s["key"] == "climb")["rides_per_driver"]
    lines.append("| 하한 참고: 탑승 거리 합 / 기사 수 | " + " | ".join(str(v) for v in rides) + f" | {sum(int(v) for v in rides)} | - | - |")
    return "\n".join(lines)


def setup_table(data: dict) -> str:
    lines = ["| 설정 | 합의 중앙값 ↓ | 최소~최대 | 전체 시간(ms) |", "| --- | ---: | ---: | ---: |"]
    for e in data["experiments"]:
        lines.append(f"| {e['label']} | {e['median_total']:.0f} | {e['min_total']}~{e['max_total']} | {e['median_ms']:.0f} |")
    return "\n".join(lines)


def tables(data: dict) -> dict[str, str]:
    return {"hand": hand_table(), "stages": stage_table(data), "setups": setup_table(data)}


def table_after(markdown: str, key: str) -> str:
    match = re.search(r"<!-- check:" + re.escape(key) + r" -->\n((?:\|[^\n]*\n?)+)", markdown)
    assert match, f"missing table marker: {key}"
    return match.group(1).rstrip("\n")


def check_stored(facts: dict) -> None:
    data = json.loads(ASSET.read_text())
    markdown = LESSON.read_text()
    for key, expected in tables(data).items():
        assert table_after(markdown, key) == expected, f"lesson table '{key}' differs from the stored measurement/recomputation"
    by = {s["key"]: s for s in data["stages"]}
    assert by["final"]["costs"] == by["climb"]["costs"]
    assert by["final"]["total"] <= PASS_LINE, "the submitted code no longer passes"
    needles = [str(by["baseline"]["total"]), str(by["greedy"]["total"]), str(by["final"]["total"]), data["judge_sha256"][:12],
               data["measured_at"], data["environment"].split(" / ")[0]]
    for name in ("cut", "at"):
        f = data["failures"][name]
        needles.append("10^13" if f["penalty"] else str(f["total"]))
    for needle in needles:
        assert needle in markdown, needle
    assert hand_text() in markdown, "hand example data in the text"
    assert f"seed 1~9 중 {facts['climb_best']}개" in markdown, f"hand climb count {facts['climb_best']} in the text"
    if FIG_HAND.exists():
        fig = FIG_HAND.read_text()
        assert all(token in fig for token in ("29", "23", "22")), "hand figure numbers"
    if FIG_MOVE.exists():
        fig = FIG_MOVE.read_text()
        assert all(token in fig for token in ("41", "39", "43", "29", "23")), "neighbor figure numbers"
    print("OK: lesson tables match the recomputed hand table and the stored TAXIASSIGN measurement")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--judge", type=Path, help="path to TAXIASSIGN main.cpp (read only)")
    parser.add_argument("--output", type=Path, help="measurement JSON to write when --judge is given")
    parser.add_argument("--print-tables", action="store_true", help="print the generated Markdown tables")
    args = parser.parse_args()
    values = sources()
    facts = run_checks(values)
    if args.judge:
        if not args.output:
            parser.error("--judge requires --output")
        benchmark(values, args.judge, args.output)
    stored = args.output or ASSET
    if args.print_tables:
        print(f"<!-- check:hand -->\n{hand_table()}\n")
        if stored.exists():
            for key, text in tables(json.loads(stored.read_text())).items():
                if key != "hand":
                    print(f"<!-- check:{key} -->\n{text}\n")
        return
    if stored.exists():
        check_stored(facts)
    else:
        print("note: stored benchmark not found; table comparison skipped")


if __name__ == "__main__":
    main()
