"""Check the COUPANG1 large-input lesson: extracted code, bucket search vs brute force, hand example, failures, measurements.

Without --judge only the checks that need no grader run (about 20 seconds): header-free composition,
the bucket search against a brute-force scan of the statement rule (random small instances, several cell
sizes, ASan/UBSan), trips and the route improvement against an independent cost, whole programs against a
mini grader written from the statement, the hand example recomputed in Python and in the lesson code, two
failing variants that must be detected, and the stored measurement against the lesson tables.
With --judge /path/to/COUPANG1/main.cpp --output FILE the measurements are repeated (about 15 minutes)
and FILE (normally lessons/large-input-search/lesson-assets/coupang1-benchmark.json) is written.
The grader is only compiled and run; the solution code uses none of its internals.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
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
from cpp_library import check_submission_code  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "lessons/large-input-search/lesson.md"
ASSETS = ROOT / "lessons/large-input-search/lesson-assets"
ASSET = ASSETS / "coupang1-benchmark.json"
FIG_HAND = ASSETS / "bucket-walk.svg"
FIG_TRADE = ASSETS / "budget-tradeoff.svg"
PASS_LINE = 15_000_000_000
PENALTY = 10**12
K_DELIVERIES = 1_000_000
ROUNDS = 5
BLOCKS = ("coupang-contract", "coupang-state", "coupang-send", "coupang-baseline", "coupang-search", "coupang-trip", "coupang-entry")
SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
SAN = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"]

CELL_LINE = "const int SIDE = 1000, CELL = 16;"
CUT_RULE = ("        if (bestDist <= (r - 1) * CELL) break;", "        if (bestDist <= r * CELL) break;")
KEEP_LINE = ("    const int w = where[id], g = cellOf(slot[w].y, slot[w].x), last = cellStart[g] + --cellLive[g], p = slot[w].prod;",
             "    const int w = where[id], g = cellOf(slot[w].y, slot[w].x), last = cellStart[g] + cellLive[g] - 1, p = slot[w].prod;")
PROBE_RING = ("        if (bestDist <= (r - 1) * CELL) break;\n", "        if (bestDist <= (r - 1) * CELL) break;\n        ++probeRings;\n")
PROBE_ITEMS = ("                const Item* it = slot + cellStart[g];\n", "                const Item* it = slot + cellStart[g];\n                probeItems += cellLive[g];\n")
PROBE_DECL = "static long long probeRings = 0, probeItems = 0;\n"
CHECK_LINE = "                    if (stock[c][it[j].prod] == 0) continue;\n"
PROBE_CHECK = ("                    if (stock[c][it[j].prod] == 0) continue;\n", "                    ++probeChecks;\n                    if (stock[c][it[j].prod] == 0) continue;\n")

# Hand example: a 16 x 16 map cut into 4 x 4 cells, one center at (5, 5) holding A x1 and B x2 (no C).
HAND_CENTER = (5, 5)
HAND_STOCK = {"A": 1, "B": 2}
HAND_ITEMS = [(5, 6, "C"), (7, 7, "A"), (5, 8, "B"), (1, 1, "A"), (10, 10, "B"), (11, 2, "A"),
              (2, 5, "C"), (9, 5, "B"), (0, 8, "B"), (14, 13, "A"), (13, 14, "B"), (3, 14, "B")]
HAND_SIDE, HAND_CELL = 16, 4

HARNESS = r'''
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <vector>

// ------------------------------------------------------------------ independent mini judge (written from the statement)
struct Inst {
    int n, m, k;
    std::vector<Coordinates> cpos;
    std::vector<std::vector<Product>> cprod;  // duplicates of one product id are possible
    std::vector<Coordinates> dpos;
    std::vector<int> dprod;
    Coordinates truck;
};

static int ab(int v) { return v < 0 ? -v : v; }
static int manhattan(Coordinates a, Coordinates b) { return ab(a.y - b.y) + ab(a.x - b.x); }

static Inst gInst;
static std::vector<int> jStock;       // [center * M + product] (total of the duplicated lines)
static std::vector<int> jNeed;        // product still needed by delivery i, -1 once delivered
static Coordinates jTruck;
static std::vector<int> jLoad;
static long long jCost;
static int jBadLoading, jBadMove;

int truckLoading(int centerID, int list[], int size) {
    if (centerID < 0 || centerID >= gInst.n) { ++jBadLoading; return 0; }
    jCost += (long long)manhattan(jTruck, gInst.cpos[centerID]) * (100 + 10 * (int)jLoad.size());
    jTruck = gInst.cpos[centerID];
    if (size + (int)jLoad.size() > 50) { ++jBadLoading; return 0; }
    int got = 0;
    for (int i = 0; i < size; ++i) {
        int& s = jStock[(size_t)centerID * gInst.m + list[i]];
        if (s > 0) { --s; jLoad.push_back(list[i]); ++got; }
    }
    if (got != size) ++jBadLoading;
    return got == size ? 1 : 0;
}

int truckMove(int id) {
    if (id < 0 || id >= gInst.k) { ++jBadMove; return 0; }
    jCost += (long long)manhattan(jTruck, gInst.dpos[id]) * (100 + 10 * (int)jLoad.size());
    jTruck = gInst.dpos[id];
    if (jNeed[id] < 0) { ++jBadMove; return 0; }
    for (size_t i = 0; i < jLoad.size(); ++i) {
        if (jLoad[i] == jNeed[id]) { jNeed[id] = -1; jLoad.erase(jLoad.begin() + i); return 1; }
    }
    ++jBadMove;
    return 0;
}

static Inst makeInst(std::mt19937& rng, int n, int m, int k, int range) {
    Inst in;
    in.n = n; in.m = m; in.k = k;
    std::vector<long long> total(m, 0);
    for (int c = 0; c < n; ++c) {
        in.cpos.push_back(Coordinates(rng() % range, rng() % range));
        int lines = 1 + (int)(rng() % std::min(m, 8));
        in.cprod.push_back({});
        for (int j = 0; j < lines; ++j) {
            Product p((int)(rng() % m), 1 + (int)(rng() % 5));
            in.cprod[c].push_back(p);
            total[p.id] += p.count;
        }
    }
    for (int i = 0; i < k; ++i) {
        int p;
        int guard = 0;
        do { p = (int)(rng() % m); } while (total[p] == 0 && ++guard < 100000);
        if (total[p] == 0) { in.k = k = i; break; }
        in.dprod.push_back(p);
        in.dpos.push_back(Coordinates(rng() % range, rng() % range));
        --total[p];
    }
    in.truck = Coordinates(rng() % range, rng() % range);
    return in;
}

static Coordinates gCenterPos[ship::N];
static Product gCenterList[ship::N][100];
static int gCenterSize[ship::N];
static Coordinates gDeliveryPos[ship::K > 5000 ? 5000 : ship::K];
static int gDeliveryProd[5000];

static void feed(const Inst& in) {
    gInst = in;
    for (int c = 0; c < in.n; ++c) {
        gCenterPos[c] = in.cpos[c];
        gCenterSize[c] = (int)in.cprod[c].size();
        for (size_t j = 0; j < in.cprod[c].size(); ++j) gCenterList[c][j] = in.cprod[c][j];
    }
    for (int i = 0; i < in.k; ++i) { gDeliveryPos[i] = in.dpos[i]; gDeliveryProd[i] = in.dprod[i]; }
    jStock.assign((size_t)in.n * in.m, 0);
    for (int c = 0; c < in.n; ++c) for (auto& p : in.cprod[c]) jStock[(size_t)c * in.m + p.id] += p.count;
    jNeed = in.dprod;
    jTruck = in.truck; jLoad.clear(); jCost = 0; jBadLoading = jBadMove = 0;
}

static void judged(const Inst& in, const char* what) {
    for (int i = 0; i < in.k; ++i) if (jNeed[i] >= 0) { std::printf("UNDELIVERED %s %d\n", what, i); std::abort(); }
    if (jBadLoading || jBadMove) { std::printf("BAD CALLS %s %d %d\n", what, jBadLoading, jBadMove); std::abort(); }
    if (!jLoad.empty()) { std::printf("TRUCK NOT EMPTY %s\n", what); std::abort(); }
}

static void loadLesson(const Inst& in) {
    feed(in);
    sendCenterList(in.n, in.m, gCenterPos, gCenterList, gCenterSize);
    sendDeliveryList(in.k, gDeliveryPos, gDeliveryProd);
}

// ------------------------------------------------------------------ reference state for the bucket search
struct Ref {
    std::vector<int> stock, demand;
    std::vector<char> taken;
};
static Ref makeRef(const Inst& in) {
    Ref r;
    r.stock.assign((size_t)in.n * in.m, 0);
    for (int c = 0; c < in.n; ++c) for (auto& p : in.cprod[c]) r.stock[(size_t)c * in.m + p.id] += p.count;
    r.demand.assign(in.m, 0);
    for (int i = 0; i < in.k; ++i) ++r.demand[in.dprod[i]];
    r.taken.assign(in.k, 0);
    return r;
}
// smallest distance to an untaken delivery that center c can load now; -1 if none
static int bruteNearest(const Inst& in, const Ref& r, int c, int y, int x) {
    int best = -1;
    for (int i = 0; i < in.k; ++i) {
        if (r.taken[i] || r.stock[(size_t)c * in.m + in.dprod[i]] == 0) continue;
        int d = ab(in.dpos[i].y - y) + ab(in.dpos[i].x - x);
        if (best < 0 || d < best) best = d;
    }
    return best;
}
static void sameState(const Inst& in, const Ref& r) {
    for (int c = 0; c < in.n; ++c) {
        long long mass = 0;
        for (int p = 0; p < in.m; ++p) {
            assert(ship::stock[c][p] == r.stock[(size_t)c * in.m + p]);
            mass += std::min(r.stock[(size_t)c * in.m + p], r.demand[p]);
        }
        assert(ship::mass[c] == mass);
    }
    for (int p = 0; p < in.m; ++p) assert(ship::demand[p] == r.demand[p]);
    int live = 0;
    for (int g = 0; g < ship::G * ship::G; ++g) {
        live += ship::cellLive[g];
        for (int j = 0; j < ship::cellLive[g]; ++j) {
            const ship::Item& it = ship::slot[ship::cellStart[g] + j];
            assert(!r.taken[it.id] && ship::where[it.id] == ship::cellStart[g] + j);
            assert(it.y == in.dpos[it.id].y && it.x == in.dpos[it.id].x && it.prod == in.dprod[it.id]);
            assert(ship::cellOf(it.y, it.x) == g);
        }
    }
    int expect = 0;
    for (int i = 0; i < in.k; ++i) expect += r.taken[i] ? 0 : 1;
    assert(live == expect);
}

static void searchTest(std::mt19937& rng, int rounds) {
    const int ranges[] = {4, 30, 200, 1000};
    for (int trial = 0; trial < rounds; ++trial) {
        const int range = ranges[trial % 4];
        Inst in = makeInst(rng, 1 + (int)(rng() % 6), 2 + (int)(rng() % 12), 1 + (int)(rng() % 150), range);
        loadLesson(in);
        ship::prepare();
        Ref ref = makeRef(in);
        sameState(in, ref);
        for (int step = 0; step < in.k + 3; ++step) {
            const int c = (int)(rng() % in.n), y = (int)(rng() % range), x = (int)(rng() % range);
            const int expect = bruteNearest(in, ref, c, y, x);
            const int id = ship::nearest(y, x, c, -1);
            if (expect < 0) { assert(id < 0); continue; }
            assert(id >= 0 && !ref.taken[id] && ref.stock[(size_t)c * in.m + in.dprod[id]] > 0);
            assert(ab(in.dpos[id].y - y) + ab(in.dpos[id].x - x) == expect);  // the bucket search finds a true nearest
            for (int extra = 0; extra <= 2; ++extra) {                           // the approximate cut still returns a valid candidate
                int a = ship::nearest(y, x, c, extra);
                assert(a >= 0 && !ref.taken[a] && ref.stock[(size_t)c * in.m + in.dprod[a]] > 0);
                assert(ab(in.dpos[a].y - y) + ab(in.dpos[a].x - x) >= expect);
            }
            if (rng() % 3 != 0) {  // take: both states change
                ship::take(id, c);
                ref.taken[id] = 1;
                --ref.stock[(size_t)c * in.m + in.dprod[id]];
                --ref.demand[in.dprod[id]];
                sameState(in, ref);
            }
        }
    }
}

// ------------------------------------------------------------------ trips
static long long tripCostRef(const ship::Trip& t) {  // from the statement: distance times (100 + 10 * load)
    long long s = 0;
    for (int i = 1; i <= t.n; ++i)
        s += (long long)(ab(t.s[i].y - t.s[i - 1].y) + ab(t.s[i].x - t.s[i - 1].x)) * (100 + 10 * (t.n - i + 1));
    return s;
}

static void runTrips(const Inst& in, int load, int extra, int passes, int beta, const char* what) {
    ship::prepare();
    ship::makeSpacing();
    Ref ref = makeRef(in);
    int ty = in.truck.y, tx = in.truck.x;
    static ship::Trip trip;
    for (int left = in.k; left > 0;) {
        const int c = ship::chooseCenter(ty, tx, beta);
        if (c < 0) { std::printf("NO CENTER %s left %d\n", what, left); std::abort(); }
        // the first stop of build() must be a true nearest from the center
        ship::build(trip, c, load, extra);
        assert(trip.n >= 1 && trip.n <= load && trip.n <= left);
        const long long before = tripCostRef(trip);
        int idsBefore[ship::CAP], cnt = trip.n;
        for (int i = 0; i < cnt; ++i) idsBefore[i] = trip.s[i + 1].id;
        ship::improve(trip, passes);
        assert(trip.n == cnt && tripCostRef(trip) <= before);
        std::vector<int> a(idsBefore, idsBefore + cnt), b;
        for (int i = 1; i <= cnt; ++i) b.push_back(trip.s[i].id);
        std::sort(a.begin(), a.end()); std::sort(b.begin(), b.end());
        assert(a == b);
        for (int i = 1; i <= cnt; ++i) {
            const int id = trip.s[i].id;
            assert(!ref.taken[id] && in.dpos[id].y == trip.s[i].y && in.dprod[id] == trip.s[i].prod);
            ref.taken[id] = 1;
            --ref.stock[(size_t)c * in.m + trip.s[i].prod];
            --ref.demand[trip.s[i].prod];
        }
        sameState(in, ref);
        int prods[ship::CAP];
        for (int i = 0; i < cnt; ++i) prods[i] = trip.s[i + 1].prod;
        assert(truckLoading(c, prods, cnt) == 1);
        for (int i = 1; i <= cnt; ++i) assert(truckMove(trip.s[i].id) == 1);
        ty = trip.s[cnt].y; tx = trip.s[cnt].x;
        left -= cnt;
    }
    judged(in, what);
}

static void tripTest(std::mt19937& rng, int rounds) {
    const int ranges[] = {5, 40, 1000};
    for (int trial = 0; trial < rounds; ++trial) {
        Inst in = makeInst(rng, 1 + (int)(rng() % 8), 2 + (int)(rng() % 20), 1 + (int)(rng() % 120), ranges[trial % 3]);
        loadLesson(in);
        const int loads[] = {1, 3, 20, 50};
        runTrips(in, loads[trial % 4], trial % 3 - 1, trial % 4, (trial % 5) * 20, "trips");
    }
}

static void entryTest(std::mt19937& rng, int rounds) {
    const int ranges[] = {5, 40, 1000};
    for (int trial = 0; trial < rounds; ++trial) {
        Inst in = makeInst(rng, 1 + (int)(rng() % 10), 2 + (int)(rng() % 30), 1 + (int)(rng() % 400), ranges[trial % 3]);
        loadLesson(in);
        solve(in.truck);
        judged(in, "entry");
        loadLesson(in);
        solveBaseline(in.truck);
        judged(in, "baseline");
    }
}

// ------------------------------------------------------------------ the hand example of the lesson
static void handExample() {
    Inst in;
    in.n = 1; in.m = 3; in.k = 0;
    in.cpos.push_back(Coordinates(5, 5));
    in.cprod.push_back({Product(0, 1), Product(1, 2)});  // product 0 = A (1 piece), product 1 = B (2 pieces), product 2 = C (none)
    const int pts[12][3] = {{5, 6, 2}, {7, 7, 0}, {5, 8, 1}, {1, 1, 0}, {10, 10, 1}, {11, 2, 0},
                            {2, 5, 2}, {9, 5, 1}, {0, 8, 1}, {14, 13, 0}, {13, 14, 1}, {3, 14, 1}};
    for (auto& p : pts) { in.dpos.push_back(Coordinates(p[0], p[1])); in.dprod.push_back(p[2]); ++in.k; }
    in.truck = Coordinates(5, 5);
    loadLesson(in);
    ship::prepare();
    int y = 5, x = 5;
    std::printf("HANDMASS0 %d\n", ship::mass[0]);
    for (int step = 1; step <= 3; ++step) {
        probeItems = 0; probeRings = 0;
        const int id = ship::nearest(y, x, 0, -1);
        std::printf("HANDSTEP %d %d %d %lld %lld %d\n", step, y, x, probeRings, probeItems, id);
        y = in.dpos[id].y; x = in.dpos[id].x;
        ship::take(id, 0);
    }
    std::printf("HANDMASS %d\n", ship::mass[0]);
}

int main(int argc, char** argv) {
    std::mt19937 rng(20261118);
    if (argc > 1 && std::strcmp(argv[1], "hand") == 0) { handExample(); return 0; }
    searchTest(rng, argc > 1 && std::strcmp(argv[1], "search") == 0 ? 200 : 120);
    if (argc > 1 && std::strcmp(argv[1], "search") == 0) { std::puts("HARNESS OK"); return 0; }
    tripTest(rng, 150);
    entryTest(rng, 80);
    handExample();
    std::puts("HARNESS OK");
}
'''


# ---------------------------------------------------------------- sources
def snippets() -> dict[str, str]:
    found: dict[str, str] = {}
    for name, code in SNIP_RE.findall(LESSON.read_text()):
        assert name not in found, f"duplicate snippet {name}"
        check_submission_code(code, name)
        found[name] = code + "\n"
    for name in BLOCKS:
        assert name in found, f"missing snippet {name}"
    return found


def sources() -> dict[str, str]:
    b = snippets()
    state, search, trip, entry = b["coupang-state"], b["coupang-search"], b["coupang-trip"], b["coupang-entry"]
    assert CELL_LINE in state, "cell constants"
    for old, _ in (CUT_RULE, KEEP_LINE, PROBE_RING, PROBE_ITEMS, PROBE_CHECK):
        assert old in state + search, old
    head = "\n".join([b["coupang-contract"], state, b["coupang-send"]])
    return {
        "blocks": b,
        "final": "\n".join([head, search, trip, entry]),
        "baseline": "\n".join([head, b["coupang-baseline"]]),
        "head": head, "state": state, "search": search, "trip": trip, "entry": entry,
        "contract": b["coupang-contract"], "send": b["coupang-send"],
    }


def compose(values: dict, cell: tuple[int, int] | None = None, edits: list | None = None, probes: bool = False, entry: str | None = None,
            baseline: bool = False) -> str:
    """Final program (or variants): optional cell constants, text edits and probe counters."""
    state, search = values["state"], values["search"]
    if cell:
        state = state.replace(CELL_LINE, f"const int SIDE = {cell[0]}, CELL = {cell[1]};")
    if probes:
        search = search.replace(*PROBE_RING).replace(*PROBE_ITEMS).replace(*PROBE_CHECK)
    program = "\n".join([values["contract"], state, values["send"], search, values["trip"], entry or values["entry"]])
    for old, new in edits or []:
        assert old in program, old
        program = program.replace(old, new, 1)
    if probes:
        program = PROBE_DECL + "static long long probeChecks = 0;\n" + program
    return program


# ---------------------------------------------------------------- hand example (independent of the lesson code)
def hand_nearest(live: set, stock: dict, y: int, x: int, rule: str = "correct") -> tuple[int, int, int]:
    """Ring walk written from the description: returns (item, rings looked at, items checked)."""
    g = HAND_SIDE // HAND_CELL
    gy0, gx0 = y // HAND_CELL, x // HAND_CELL
    best, best_d, rings, checked = -1, 1 << 30, 0, 0
    for r in range(g):
        bound = (r - 1) * HAND_CELL if rule == "correct" else r * HAND_CELL
        if best_d <= bound:
            break
        rings += 1
        for gy in range(gy0 - r, gy0 + r + 1):
            for gx in range(gx0 - r, gx0 + r + 1):
                if max(abs(gy - gy0), abs(gx - gx0)) != r or not (0 <= gy < g and 0 <= gx < g):
                    continue
                for i in sorted(live):
                    iy, ix, prod = HAND_ITEMS[i]
                    if iy // HAND_CELL != gy or ix // HAND_CELL != gx:
                        continue
                    checked += 1
                    d = abs(iy - y) + abs(ix - x)
                    if stock.get(prod, 0) > 0 and d < best_d:
                        best, best_d = i, d
    return best, rings, checked


def hand_brute(live: set, stock: dict, y: int, x: int) -> tuple[int, int]:
    cands = [(abs(HAND_ITEMS[i][0] - y) + abs(HAND_ITEMS[i][1] - x), i) for i in live if stock.get(HAND_ITEMS[i][2], 0) > 0]
    return min(cands) if cands else (-1, -1)


def hand_steps() -> list[dict]:
    live, stock = set(range(len(HAND_ITEMS))), dict(HAND_STOCK)
    y, x = HAND_CENTER
    rows = []
    for step in range(1, 4):
        item, rings, checked = hand_nearest(live, stock, y, x)
        d_min, i_min = hand_brute(live, stock, y, x)
        bad, _, _ = hand_nearest(live, stock, y, x, rule="cut")
        iy, ix, prod = HAND_ITEMS[item]
        assert abs(iy - y) + abs(ix - x) == d_min, "bucket walk differs from brute force"
        rows.append({"step": step, "from": (y, x), "rings": rings, "checked": checked, "live": len(live), "item": item,
                     "at": (iy, ix, prod), "dist": d_min, "bad_item": bad, "bad_dist": abs(HAND_ITEMS[bad][0] - y) + abs(HAND_ITEMS[bad][1] - x)})
        live.remove(item)
        stock[prod] -= 1
        y, x = iy, ix
    return rows


def hand_table() -> str:
    lines = ["| 고르기 | 출발점 | 본 링 | 검사한 후보 / 남은 배송 | 고른 배송 | 거리 | 전수 탐색의 최솟값 |", "| --- | --- | ---: | ---: | --- | ---: | ---: |"]
    for r in hand_steps():
        iy, ix, prod = r["at"]
        lines.append(f"| {r['step']}번째 | ({r['from'][0]},{r['from'][1]}) | {r['rings']} | {r['checked']} / {r['live']} | 배송 {r['item']} ({iy},{ix}) {prod} | {r['dist']} | {r['dist']} |")
    return "\n".join(lines)


def hand_text() -> str:
    items = ", ".join(f"{i} ({y},{x}) {p}" for i, (y, x, p) in enumerate(HAND_ITEMS))
    return f"센터는 ({HAND_CENTER[0]},{HAND_CENTER[1]})에 있고 A를 {HAND_STOCK['A']}개, B를 {HAND_STOCK['B']}개 가집니다. 배송은 {items}입니다."


def hand_facts() -> dict:
    rows = hand_steps()
    first = rows[0]
    assert first["bad_item"] != first["item"] and first["bad_dist"] > first["dist"], "the early cut must give a worse first pick"
    return {"rows": rows, "first": first}


# ---------------------------------------------------------------- compile / run helpers
def compile_run(code: str, flags: list[str], args: list[str] | None = None, expect_ok: bool = True, timeout: int = 300):
    with tempfile.TemporaryDirectory(prefix="lesson-coupang-") as folder:
        src, exe = Path(folder) / "check.cpp", Path(folder) / "check"
        src.write_text(code)
        subprocess.run(["c++", "-std=c++17", *flags, str(src), "-o", str(exe)], check=True)
        result = subprocess.run([str(exe), *(args or [])], capture_output=True, text=True, timeout=timeout)
    if expect_ok:
        assert result.returncode == 0, result.stderr[-2000:] + result.stdout[-800:]
    return result


def harness_program(values: dict, cell: tuple[int, int] | None = None, edits: list | None = None, hand: bool = False) -> str:
    baseline_solve = "void solveBaseline(" + values["blocks"]["coupang-baseline"].split("void solve(", 1)[1]
    program = compose(values, cell=cell, edits=edits, probes=True)
    return program + "\n" + baseline_solve + "\n" + HARNESS


def run_checks(values: dict) -> dict:
    # 1. the submitted programs compile on their own: only the two functions of the grader are missing.
    stub = "int truckMove(int) { return 0; }\nint truckLoading(int, int[], int) { return 0; }\nint main() {}\n"
    compile_run(values["final"] + "\n" + stub, ["-O1", "-Wall", "-Werror"])
    compile_run(values["baseline"] + "\n" + stub, ["-O1", "-Wall", "-Werror", "-Wno-unused-const-variable"])

    jobs = {}
    with ThreadPoolExecutor(6) as pool:
        # 2. all tests with the lesson cell size; 3. search tests with other cell sizes (cell 1000 = one cell, cell 1 = one point per cell)
        jobs["main"] = pool.submit(compile_run, harness_program(values), SAN)
        for side, cell in ((1000, 1), (1000, 5), (1000, 64), (1000, 1000)):
            jobs[f"cell{cell}"] = pool.submit(compile_run, harness_program(values, cell=(side, cell)), SAN, ["search"])
        # 4. failing variants: must be detected
        jobs["cut"] = pool.submit(compile_run, harness_program(values, edits=[CUT_RULE]), SAN, None, False)
        jobs["keep"] = pool.submit(compile_run, harness_program(values, edits=[KEEP_LINE]), SAN, None, False)
        # 5. the hand example in the lesson code (cells of 4 on a 16 x 16 map), correct and early-cut rule
        jobs["hand"] = pool.submit(compile_run, harness_program(values, cell=(HAND_SIDE, HAND_CELL)), ["-O1"], ["hand"])
        jobs["hand-cut"] = pool.submit(compile_run, harness_program(values, cell=(HAND_SIDE, HAND_CELL), edits=[CUT_RULE]), ["-O1"], ["hand"])
        results = {k: f.result() for k, f in jobs.items()}
    assert "HARNESS OK" in results["main"].stdout
    for cell in (1, 5, 64, 1000):
        assert "HARNESS OK" in results[f"cell{cell}"].stdout, cell
    for name in ("cut", "keep"):
        assert results[name].returncode != 0, f"buggy variant '{name}' was not detected"

    facts = hand_facts()
    steps = [line.split() for line in results["hand"].stdout.splitlines() if line.startswith("HANDSTEP")]
    assert len(steps) == 3
    for row, got in zip(facts["rows"], steps):
        assert [int(v) for v in got[1:]] == [row["step"], row["from"][0], row["from"][1], row["rings"], row["checked"], row["item"]], (got, row)
    assert "HANDMASS0 3" in results["hand"].stdout and "HANDMASS 0" in results["hand"].stdout
    cut_first = [line.split() for line in results["hand-cut"].stdout.splitlines() if line.startswith("HANDSTEP")][0]
    assert int(cut_first[6]) == facts["first"]["bad_item"], cut_first
    print("OK: composition (header-free, -Wall -Werror), bucket search = brute force (cells 1, 5, 16, 64, 1000), take/mass/stock state, "
          "trips and route improvement against an independent cost, whole programs on a mini grader, hand example in code and Python, "
          "both buggy variants detected (ASan/UBSan)")
    return facts


# ---------------------------------------------------------------- benchmark
EXP_ENTRY = r'''
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
static int envInt(const char* key, int fallback) {
    const char* v = getenv(key);
    return v ? atoi(v) : fallback;
}
// BRUTE=1: scan every live delivery for each pick, 300 picks, then stop (time per check)
static void bruteProbe(int ty, int tx) {
    clock_t start = clock();
    long long checks = 0;
    for (int round = 0; round < 300; ++round) {
        const int c = ship::chooseCenter(ty, tx, 0);
        int best = -1, bd = 1 << 30;
        for (int g = 0; g < ship::G * ship::G; ++g) {
            for (int j = 0; j < ship::cellLive[g]; ++j) {
                const ship::Item& it = ship::slot[ship::cellStart[g] + j];
                ++checks;
                if (ship::stock[c][it.prod] == 0) continue;
                const int d = ship::absInt(it.y - ty) + ship::absInt(it.x - tx);
                if (d < bd) { bd = d; best = it.id; }
            }
        }
        if (best < 0) break;
        ship::take(best, c);
    }
    fprintf(stderr, "BRUTE %lld %.6f\n", checks, (double)(clock() - start) / CLOCKS_PER_SEC);
    exit(0);
}
void solve(Coordinates truckCoordinates) {
    ship::prepare();
    ship::makeSpacing();
    int ty = truckCoordinates.y, tx = truckCoordinates.x;
    const int load = envInt("LOAD", 20), extra = envInt("EXTRA", -1), passes = envInt("PASSES", 3), beta = envInt("BETA", 25);
    if (envInt("BRUTE", 0)) bruteProbe(ty, tx);
    long long trips = 0;
    for (int left = ship::deliveryCount; left > 0;) {
        const int c = ship::chooseCenter(ty, tx, beta);
        if (c < 0) { fprintf(stderr, "NOCENTER %d\n", left); break; }
        static ship::Trip trip;
        ship::build(trip, c, load, extra);
        ship::improve(trip, passes);
        int prods[ship::CAP];
        for (int i = 0; i < trip.n; ++i) prods[i] = trip.s[i + 1].prod;
        truckLoading(c, prods, trip.n);
        for (int i = 1; i <= trip.n; ++i) truckMove(trip.s[i].id);
        ty = trip.s[trip.n].y; tx = trip.s[trip.n].x;
        left -= trip.n; ++trips;
    }
    fprintf(stderr, "TRIPS %lld\n", trips);
    fprintf(stderr, "PROBES %lld %lld %lld\n", probeChecks, probeItems, probeRings);
}
'''

# experiment settings: (key, label, env)
STAGES = [
    ("trip50", "가까운 센터에서 50개씩", {"LOAD": "50", "BETA": "0", "PASSES": "0"}),
    ("trip20", "+ 적재 20개", {"LOAD": "20", "BETA": "0", "PASSES": "0"}),
    ("choose", "+ 센터 선택에 후보 밀도 반영", {"LOAD": "20", "BETA": "25", "PASSES": "0"}),
    ("improve", "+ 운행 안 순서 개선(최대 3회)", {}),
]
CELLS = [4, 8, 16, 32, 64]
EXTRAS = [0, 1, 2]
LOADS = [10, 15, 20, 30, 50]
BETAS = [0, 10, 25, 100, 400]
PASSES = [0, 1, 3, 10]


def build_judge(judge_text: str, user_code: str, folder: Path, name: str, flags: list[str] | None = None) -> Path:
    (folder / f"{name}-judge.cpp").write_text(judge_text)
    (folder / f"{name}-user.cpp").write_text(user_code)
    exe = folder / name
    subprocess.run(["c++", "-std=c++17", *(flags or ["-O2"]), str(folder / f"{name}-judge.cpp"), str(folder / f"{name}-user.cpp"), "-o", str(exe)], check=True)
    return exe


def run_judge(exe: Path, env: dict[str, str], timeout: int = 900) -> dict:
    import os
    start = time.perf_counter()
    r = subprocess.run([str(exe)], capture_output=True, text=True, env=dict(os.environ, **env), timeout=timeout, check=True)
    ms = (time.perf_counter() - start) * 1000
    total = [int(v) for v in re.findall(r"^SCORE: (\d+)$", r.stdout, re.M)]
    assert len(total) == 1, r.stdout + r.stderr[-500:]
    out = {"total": total[0], "ms": ms}
    for line in r.stderr.splitlines():
        parts = line.split()
        if parts and parts[0] == "TRIPS":
            out["trips"] = int(parts[1])
        elif parts and parts[0] == "PROBES":
            out["checks"], out["items"], out["rings"] = (int(v) for v in parts[1:4])
        elif parts and parts[0] == "BRUTE":
            out["brute_checks"], out["brute_seconds"] = int(parts[1]), float(parts[2])
    return out


def timed(exe: Path, env: dict[str, str], rounds: int = ROUNDS) -> dict:
    runs = [run_judge(exe, env) for _ in range(rounds)]
    assert len({r["total"] for r in runs}) == 1, "the score must not depend on the run"
    return {"total": runs[0]["total"], "median_ms": statistics.median(r["ms"] for r in runs), "runs_ms": [round(r["ms"]) for r in runs],
            "trips": runs[0].get("trips")}


def benchmark(values: dict, judge: Path, output: Path) -> None:
    judge_text = judge.read_text()
    import os
    data: dict = {
        "judge_sha256": hashlib.sha256(judge.read_bytes()).hexdigest(),
        "measured_at": datetime.date.today().isoformat(),
        "environment": f"{platform.system()} {platform.mac_ver()[0]} {platform.machine()} / "
                       + subprocess.run(["c++", "--version"], capture_output=True, text=True).stdout.splitlines()[0] + " / -std=c++17 -O2",
        "pass_line": PASS_LINE, "timing_rounds": ROUNDS, "load_average": os.getloadavg()[0],
    }
    with tempfile.TemporaryDirectory(prefix="lesson-coupang-bench-") as folder_name:
        folder = Path(folder_name)
        exp_prog = lambda **kw: compose(values, entry=EXP_ENTRY, **kw)  # noqa: E731
        exp = build_judge(judge_text, exp_prog(probes=True), folder, "exp")
        final = build_judge(judge_text, values["final"], folder, "final")
        base = build_judge(judge_text, values["baseline"], folder, "base")

        stages = []
        row = timed(base, {})
        stages.append({"key": "baseline", "label": "번호 순서, 상품을 가진 가까운 센터에서 1개씩", **row})
        print(json.dumps({k: stages[-1][k] for k in ("key", "total", "median_ms")}), flush=True)
        for key, label, env in STAGES:
            row = timed(exp, env)
            stages.append({"key": key, "label": label, **row})
            print(json.dumps({k: stages[-1][k] for k in ("key", "total", "median_ms")}), flush=True)
        row = timed(final, {})
        stages.append({"key": "final", "label": "본문 제출 코드", **row})
        assert stages[-1]["total"] == next(s for s in stages if s["key"] == "improve")["total"], "experiment entry differs from the lesson entry"
        data["stages"] = stages

        def sweep(rows: list, make_env, make_build=None):
            out = []
            for v in rows:
                env = make_env(v)
                exe = make_build(v) if make_build else exp
                t = timed(exe, env)
                probe = run_judge(exe, env)
                assert probe["total"] == t["total"]
                out.append({"value": v, **t, "checks": probe["checks"], "items": probe["items"], "rings": probe["rings"]})
                print(json.dumps({k: out[-1][k] for k in ("value", "total", "median_ms", "checks")}), flush=True)
            return out

        cell_exes = {c: build_judge(judge_text, exp_prog(probes=True, cell=(1000, c)), folder, f"exp-cell{c}") for c in CELLS if c != 16}
        cell_exes[16] = exp
        data["cells"] = sweep(CELLS, lambda c: {}, lambda c: cell_exes[c])
        data["extras"] = sweep([-1] + EXTRAS, lambda e: {"EXTRA": str(e)})
        data["loads"] = sweep(LOADS, lambda v: {"LOAD": str(v)})
        data["betas"] = sweep(BETAS, lambda v: {"BETA": str(v)})
        data["passes"] = sweep(PASSES, lambda v: {"PASSES": str(v)})

        brute = [run_judge(exp, {"BRUTE": "1"}) for _ in range(3)]
        sec = statistics.median(b["brute_seconds"] for b in brute)
        checks = brute[0]["brute_checks"]
        per_check = sec / checks
        total_checks = K_DELIVERIES * (K_DELIVERIES + 1) // 2
        data["brute"] = {"checks": checks, "seconds": sec, "ns_per_check": per_check * 1e9, "total_checks": total_checks,
                         "extrapolated_seconds": per_check * total_checks}
        print(json.dumps(data["brute"]), flush=True)

        # wrong variants through the real grader (an invalid answer is the measurement)
        data["failures"] = {}
        for name, edits in (("cut", [CUT_RULE]), ("keep", [KEEP_LINE])):
            exe = build_judge(judge_text, compose(values, edits=edits), folder, "bug-" + name)
            t0 = time.perf_counter()
            r = subprocess.run([str(exe)], capture_output=True, text=True, timeout=900, check=True)
            ms = (time.perf_counter() - t0) * 1000
            total = int(re.search(r"^SCORE: (\d+)$", r.stdout, re.M).group(1))
            data["failures"][name] = {"total": total, "penalty": total >= PENALTY, "ms": round(ms)}
            print(name, data["failures"][name], flush=True)

        # sanitizer run of the submitted code on the real input (judge compiled with the same flags)
        san = build_judge(judge_text, values["final"], folder, "san", SAN)
        t0 = time.perf_counter()
        r = run_judge(san, {})
        data["sanitizer"] = {"total": r["total"], "seconds": round(time.perf_counter() - t0, 1)}
        assert data["sanitizer"]["total"] == next(s for s in stages if s["key"] == "final")["total"]
        print(data["sanitizer"], flush=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


# ---------------------------------------------------------------- tables
def fmt_ms(ms: float) -> str:
    return f"{ms / 1000:.1f}"


def stage_table(data: dict) -> str:
    base = data["stages"][0]["total"]
    lines = ["| 단계 | 점수 ↓ | 통과 기준 대비 | 운행 수 | 시간(초) |", "| --- | ---: | ---: | ---: | ---: |"]
    for s in data["stages"]:
        if s["key"] == "final":
            continue
        ratio = f"{s['total'] / PASS_LINE:.2f}배"
        trips = f"{s['trips']:,}" if s.get("trips") else f"{K_DELIVERIES:,}"
        lines.append(f"| {s['label']} | {s['total']:,} | {ratio} | {trips} | {fmt_ms(s['median_ms'])} |")
    del base
    return "\n".join(lines)


def cell_table(data: dict) -> str:
    lines = ["| 칸 한 변 | 칸 수 | 후보 검사 수 | 점수 | 시간(초) |", "| ---: | ---: | ---: | ---: | ---: |"]
    for r in data["cells"]:
        g = (1000 + r["value"] - 1) // r["value"]
        lines.append(f"| {r['value']} | {g * g:,} | {r['checks']:,} | {r['total']:,} | {fmt_ms(r['median_ms'])} |")
    return "\n".join(lines)


def extra_table(data: dict) -> str:
    lines = ["| 첫 후보 뒤에 더 보는 링 | 후보 검사 수 | 점수 | 점수 변화 | 시간(초) |", "| --- | ---: | ---: | ---: | ---: |"]
    exact = next(r for r in data["extras"] if r["value"] == -1)
    for r in sorted(data["extras"], key=lambda r: (r["value"] == -1, r["value"])):
        label = "정확한 종료 조건" if r["value"] == -1 else f"{r['value']}링"
        diff = "-" if r["value"] == -1 else f"{100 * (r['total'] - exact['total']) / exact['total']:+.1f}%"
        lines.append(f"| {label} | {r['checks']:,} | {r['total']:,} | {diff} | {fmt_ms(r['median_ms'])} |")
    return "\n".join(lines)


def param_table(data: dict) -> str:
    lines = ["| 바꾼 값 | 점수 ↓ | 시간(초) |", "| --- | ---: | ---: |"]
    for key, name, unit in (("loads", "적재", "개"), ("betas", "밀도 항 가중치", ""), ("passes", "순서 개선 반복", "회")):
        for r in data[key]:
            lines.append(f"| {name} {r['value']}{unit} | {r['total']:,} | {fmt_ms(r['median_ms'])} |")
    return "\n".join(lines)


def tables(data: dict) -> dict[str, str]:
    return {"hand": hand_table(), "stages": stage_table(data), "cells": cell_table(data), "extras": extra_table(data), "params": param_table(data)}


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
    assert by["final"]["total"] == by["improve"]["total"] and by["final"]["total"] <= PASS_LINE, "the submitted code no longer passes"
    assert by["baseline"]["total"] > PASS_LINE, "the baseline is meant to be valid but over the pass line"
    brute = data["brute"]
    needles = [data["judge_sha256"][:12], data["measured_at"], data["environment"].split(" / ")[0],
               f"{by['baseline']['total']:,}", f"{by['final']['total']:,}", f"{brute['total_checks']:.1e}".replace("e+", "×10^").replace("×10^0", "×10^"),
               f"{brute['extrapolated_seconds']:.0f}초", f"{data['sanitizer']['seconds']:.0f}초"]
    for name in ("cut", "keep"):
        f = data["failures"][name]
        needles.append("10^12" if f["penalty"] else f"{f['total']:,}")
    for needle in needles:
        assert needle in markdown, needle
    assert hand_text() in markdown, "hand example data in the text"
    if FIG_HAND.exists():
        fig = FIG_HAND.read_text()
        assert all(token in fig for token in ("(5,5)", "(5,8)", "(7,7)")), "hand figure"
    if FIG_TRADE.exists():
        fig = FIG_TRADE.read_text()
        assert f"{by['final']['total']:,}" in fig or f"{by['final']['total'] / 1e9:.2f}" in fig, "tradeoff figure"
    print("OK: lesson tables match the recomputed hand table and the stored COUPANG1 measurement")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--judge", type=Path, help="path to COUPANG1 main.cpp (read only)")
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
