"""Check the construction-heuristics lesson: extracted code, hand examples, stored measurements, figures.

Runs without any judge. It extracts the lesson's code blocks, compiles them header-free with
-Wall -Wextra -Werror, builds a harness with ASan/UBSan, recomputes every number in the lesson
tables on the practice frames from fixed seeds (input seeds 1..20), compares the lesson text and
lessons/construction-heuristics/lesson-assets/measurements.json with the fresh values, replays the
deterministic constructors in an independent Python implementation, and shows that each common
mistake is caught by the same harness.

    python3 scripts/check_construction_heuristics.py            # verify
    python3 scripts/check_construction_heuristics.py --update   # rewrite measurements.json
    python3 scripts/check_construction_heuristics.py --tables   # print the tables used in the lesson
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from cpp_library import check_submission_code, read_library_snippets
from lesson_text import check_hub_summary, read_hub_text, read_lesson_text

ROOT = Path(__file__).resolve().parents[1]
LESSON_ID = "construction-heuristics"
LESSON_DIR = ROOT / "lessons" / LESSON_ID
ASSET = LESSON_DIR / "lesson-assets" / "measurements.json"
FIGURES = ["construction-loop.svg", "hand-path.svg", "regret-gap.svg", "restart-spread.svg",
           "construction-cost.svg", "strip-count.svg", "restart-budget.svg", "construction-frame.svg"]
SEEDS = list(range(1, 21))
BLOCKS = ("cons-core", "cons-path", "cons-jobs", "cons-improve", "cons-entry")
SITE_PROBLEMS = ("ORDERING", "SCHEDULX", "TAXIASSIGN", "LANDINGX", "COUPANG", "MINEEXPLORE", "AIRCONTECH",
                 "ENTROPY2D", "ROBOTCLEAN", "DRONESORT", "ALLOCATE", "CLUSTERX", "MULTIDRONE", "CHIPDESIGN",
                 "TENSORALLOC", "GERMMATCH", "ANTENNAS", "TELEVISION", "FRIEGHTFIX")

# ---------------------------------------------------------------- independent reference (plain Python)
MASK = (1 << 64) - 1
BIG = 10 ** 12


class Gen:
    def __init__(self, seed: int):
        self.x = seed & MASK

    def next(self, rng: int) -> int:
        self.x = (self.x * 6364136223846793005 + 1442695040888963407) & MASK
        return (self.x >> 33) % rng


def make_path(n: int, seed: int) -> list[tuple[int, int]]:
    g = Gen(seed)
    pts = []
    for _ in range(n):
        x = g.next(1000)
        y = g.next(1000)
        pts.append((x, y))
    return pts


def make_jobs(n: int, m: int, seed: int) -> tuple[list[int], list[list[int]]]:
    g = Gen(seed)
    d, c = [], []
    for _ in range(n):
        d.append(1 + g.next(100))
        c.append([g.next(51) for _ in range(m)])
    return d, c


def dist(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def path_cost(pts, order) -> int:
    return sum(dist(pts[order[i]], pts[order[i + 1]]) for i in range(len(order) - 1))


def jobs_cost(d, c, m, assign) -> int:
    load = [0] * m
    extra = 0
    for j, mc in enumerate(assign):
        load[mc] += d[j]
        extra += c[j][mc]
    return sum(v * v for v in load) // 100 + extra


def is_perm(order, n) -> bool:
    return sorted(order) == list(range(n))


def jobs_valid(assign, n, m, k) -> bool:
    return len(assign) == n and all(0 <= a < m for a in assign) and all(assign.count(i) <= k for i in range(m))


def rule_key(t, rule):
    item, slot, best, second, weight = t
    if rule == "cheapest":
        return best
    if rule == "regret":
        return -(second - best)
    if rule == "heaviest":
        return -weight
    return item


def slot_costs(pts, order, p, any_slot):
    length = len(order)
    out = []
    for s in (range(length + 1) if any_slot else [length]):
        if s == 0:
            v = dist(pts[p], pts[order[0]])
        elif s == length:
            v = dist(pts[order[-1]], pts[p])
        else:
            a, b = pts[order[s - 1]], pts[order[s]]
            v = dist(a, pts[p]) + dist(pts[p], b) - dist(a, b)
        out.append((s, v))
    return out


def path_candidates(pts, order, used, any_slot, rule):
    cands = []
    for p in range(len(pts)):
        if p in used:
            continue
        costs = slot_costs(pts, order, p, any_slot)
        best_s, best = min(costs, key=lambda sv: (sv[1], sv[0]))
        vs = sorted(v for _, v in costs)
        second = vs[1] if len(vs) > 1 else BIG
        weight = min(dist(pts[p], pts[q]) for q in order) if rule == "heaviest" else 0
        cands.append((p, best_s, best, second, weight))
    cands.sort(key=lambda t: (rule_key(t, rule), t[2], t[0]))
    return cands


def construct_path(pts, rule, any_slot):
    order = [0]
    used = {0}
    while len(order) < len(pts):
        p, s = path_candidates(pts, order, used, any_slot, rule)[0][:2]
        order.insert(s, p)
        used.add(p)
    return order


def jobs_candidates(d, c, m, k, load, cnt, left, rule):
    cands = []
    for j in sorted(left):
        costs = [((2 * load[mc] + d[j]) * d[j] + 100 * c[j][mc], mc) for mc in range(m) if cnt[mc] < k]
        best, bs = min(costs)
        vs = sorted(v for v, _ in costs)
        second = vs[1] if len(vs) > 1 else BIG
        cands.append((j, bs, best, second, d[j]))
    cands.sort(key=lambda t: (rule_key(t, rule), t[2], t[0]))
    return cands


def construct_jobs(d, c, m, k, rule):
    n = len(d)
    load, cnt, assign, left = [0] * m, [0] * m, [-1] * n, set(range(n))
    while left:
        j, mc = jobs_candidates(d, c, m, k, load, cnt, left, rule)[0][:2]
        assign[j] = mc
        load[mc] += d[j]
        cnt[mc] += 1
        left.discard(j)
    return assign


def improve_adjacent_ref(pts, order):
    order = list(order)
    changed = True
    while changed:
        changed = False
        for i in range(len(order) - 1):
            before = path_cost(pts, order)
            order[i], order[i + 1] = order[i + 1], order[i]
            if path_cost(pts, order) < before:
                changed = True
            else:
                order[i], order[i + 1] = order[i + 1], order[i]
    return order


def improve_move_ref(d, c, m, k, assign):
    assign = list(assign)
    n = len(d)

    def scaled(a):
        load = [0] * m
        for j, mc in enumerate(a):
            load[mc] += d[j]
        return sum(v * v for v in load) + 100 * sum(c[j][a[j]] for j in range(n))

    changed = True
    while changed:
        changed = False
        for j in range(n):
            cur = scaled(assign)
            best, to = 0, -1
            for mc in range(m):
                if mc == assign[j] or assign.count(mc) >= k:
                    continue
                trial = list(assign)
                trial[j] = mc
                change = scaled(trial) - cur
                if change < best:
                    best, to = change, mc
            if to >= 0:
                assign[j] = to
                changed = True
    return assign


# ---------------------------------------------------------------- hand examples (Python side of the tables)
HAND_PTS = [(5, 5), (3, 3), (7, 3), (6, 2), (6, 9), (5, 0), (5, 7)]
HAND_D = [10, 20, 55, 20, 10, 25]
HAND_C = [[10, 10], [5, 25], [20, 45], [40, 5], [35, 35], [5, 45]]
HAND_M, HAND_K = 2, 3
HAND_PATH_RESULT = {"nn": 22, "cheapest": 19, "farthest": 20, "regret": 18}
HAND_JOBS_RESULT = {"index": 261, "heaviest": 206, "cheapest": 207, "regret": 196}


def hand_path_facts() -> dict:
    out = {}
    for name, rule, any_slot in (("nn", "cheapest", False), ("cheapest", "cheapest", True),
                                 ("farthest", "heaviest", True), ("regret", "regret", True)):
        order = construct_path(HAND_PTS, rule, any_slot)
        out[name] = {"order": order, "cost": path_cost(HAND_PTS, order)}
    out["optimum"] = min(path_cost(HAND_PTS, list(p)) for p in itertools.permutations(range(7)))
    return out


def hand_jobs_facts() -> dict:
    out = {}
    for name, rule in (("index", "index"), ("heaviest", "heaviest"), ("cheapest", "cheapest"), ("regret", "regret")):
        a = construct_jobs(HAND_D, HAND_C, HAND_M, HAND_K, rule)
        load = [sum(HAND_D[j] for j in range(6) if a[j] == mc) for mc in range(HAND_M)]
        extra = sum(HAND_C[j][a[j]] for j in range(6))
        out[name] = {"assign": a, "load": load, "extra": extra, "cost": jobs_cost(HAND_D, HAND_C, HAND_M, a)}
    out["optimum"] = min(jobs_cost(HAND_D, HAND_C, HAND_M, list(a)) for a in itertools.product(range(HAND_M), repeat=6)
                         if jobs_valid(list(a), 6, HAND_M, HAND_K))
    return out


def hand_nn_rows() -> list[list[str]]:
    rows, order, used = [], [0], {0}
    while len(order) < 7:
        end = order[-1]
        options = [(p, dist(HAND_PTS[end], HAND_PTS[p])) for p in range(7) if p not in used]
        pick = min(options, key=lambda t: (t[1], t[0]))
        rows.append([str(len(order)), f"점 {end}", ", ".join(f"{p}: {v}" for p, v in options), f"점 {pick[0]}"])
        order.append(pick[0])
        used.add(pick[0])
    return rows


def hand_insertion_rows(rule: str) -> list[list[str]]:
    rows, order, used = [], [0], {0}
    while len(order) < 7:
        cands = path_candidates(HAND_PTS, order, used, True, rule)
        p, s, best, _, _ = cands[0]
        before = " ".join(map(str, order))
        order.insert(s, p)
        used.add(p)
        rows.append([str(len(order) - 1), before, f"점 {p}", str(s), str(best), " ".join(map(str, order))])
    return rows


def hand_divergence_rows() -> list[list[str]]:
    order, used = [0], {0}
    for _ in range(2):
        p, s = path_candidates(HAND_PTS, order, used, True, "cheapest")[0][:2]
        order.insert(s, p)
        used.add(p)
    assert order == [4, 6, 0]
    cands = sorted(path_candidates(HAND_PTS, order, used, True, "regret"), key=lambda t: t[0])
    return [[f"점 {p}", str(s), str(best), str(second), str(second - best)] for p, s, best, second, _ in cands]


def hand_jobs_first_rows() -> list[list[str]]:
    rows = []
    for j in range(6):
        v = [(d := HAND_D[j]) * d + 100 * HAND_C[j][mc] for mc in range(2)]
        rows.append([str(j), str(HAND_D[j]), f"{v[0]:,}", f"{v[1]:,}", f"{min(v):,}", f"{abs(v[0] - v[1]):,}"])
    return rows


def hand_regret_trace_rows() -> list[list[str]]:
    d, c, m, k = HAND_D, HAND_C, HAND_M, HAND_K
    load, cnt, left, rows = [0] * m, [0] * m, set(range(6)), []
    step = 0
    while left:
        step += 1
        cands = jobs_candidates(d, c, m, k, load, cnt, left, "regret")
        j, mc = cands[0][:2]
        regrets = ", ".join(f"{t[0]}: {(t[3] - t[2]) if t[3] < BIG else '∞'}" for t in sorted(cands, key=lambda t: t[0]))
        rows.append([str(step), f"{load[0]} / {load[1]}", f"{cnt[0]} / {cnt[1]}", regrets, f"작업 {j} → 기계 {mc}"])
        load[mc] += d[j]
        cnt[mc] += 1
        left.discard(j)
    return rows


def md_table(header: list[str], rows: list[list[str]], align: list[str] | None = None) -> str:
    align = align or ["---"] * len(header)
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(align) + " |"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(lines)


# ---------------------------------------------------------------- lesson code
def snippet(name: str) -> str:
    found = re.findall(r"```cpp[^\n]*\bsnippet=" + re.escape(name) + r"\n(.*?)\n```", read_lesson_text(LESSON_ID), re.S)
    assert len(found) == 1, f"snippet {name}: {len(found)} blocks"
    return found[0] + "\n"


def assemble() -> tuple[str, dict[str, str]]:
    library = read_library_snippets()
    blocks = {name: snippet(name) for name in BLOCKS}
    for name, code in blocks.items():
        check_submission_code(code, name)
    code = "\n".join([library["random"], library["sort"]] + [blocks[name] for name in BLOCKS])
    return code, blocks


HARNESS = r'''// Harness: standard headers are allowed here. The lesson code (libraries + blocks) is included from code.cpp.
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "code.cpp"

using namespace cons;

static int g_fail = 0;
#define CHECK(cond, ...) do { if (!(cond)) { ++g_fail; if (g_fail <= 5) { std::printf("CHECK FAILED line %d: %s\n", __LINE__, #cond); } } } while (0)

// ---------------------------------------------------------------- independent recomputation (plain loops)
static long long pathLen(const Path& p, const int* ord, int len) {
    long long s = 0;
    for (int i = 0; i + 1 < len; ++i)
        s += std::abs(p.px[ord[i]] - p.px[ord[i + 1]]) + std::abs(p.py[ord[i]] - p.py[ord[i + 1]]);
    return s;
}
static bool isPerm(const int* a, int n) {
    std::vector<int> seen(n, 0);
    for (int i = 0; i < n; ++i) { if (a[i] < 0 || a[i] >= n || seen[a[i]]) return false; seen[a[i]] = 1; }
    return true;
}
static long long jobsScore(const Jobs& q, const int* a) {
    long long load[16] = {0}, extra = 0, sq = 0;
    for (int j = 0; j < q.n; ++j) { load[a[j]] += q.d[j]; extra += q.c[j][a[j]]; }
    for (int i = 0; i < q.m; ++i) sq += load[i] * load[i];
    return sq / 100 + extra;
}
static bool jobsValid(const Jobs& q, const int* a) {
    int cnt[16] = {0};
    for (int j = 0; j < q.n; ++j) { if (a[j] < 0 || a[j] >= q.m) return false; ++cnt[a[j]]; }
    for (int i = 0; i < q.m; ++i) if (cnt[i] > q.k) return false;
    return true;
}

// ---------------------------------------------------------------- checked subclasses (brute-force candidate and state checks)
struct CheckedPath : Path {
    int candidates(Cand out[], int rule) {
        const int count = Path::candidates(out, rule);
        for (int t = 0; t < count; ++t) {
            const int item = out[t].item;
            long long costs[Path::MAXN + 1];
            int ns = 0, lo = anySlot ? 0 : len;
            for (int s = lo; s <= len; ++s) {
                int tmp[Path::MAXN + 1];
                int w = 0;
                for (int i = 0; i < s; ++i) tmp[w++] = order[i];
                tmp[w++] = item;
                for (int i = s; i < len; ++i) tmp[w++] = order[i];
                costs[ns++] = pathLen(*this, tmp, len + 1) - pathLen(*this, order, len);
            }
            int bs = 0;
            for (int i = 1; i < ns; ++i) if (costs[i] < costs[bs]) bs = i;
            std::vector<long long> sorted(costs, costs + ns);
            std::sort(sorted.begin(), sorted.end());
            CHECK(out[t].best == costs[bs]);
            CHECK(out[t].slot == lo + bs);
            CHECK(out[t].second == (ns > 1 ? sorted[1] : BIG));
        }
        return count;
    }
    void place(int p, int s) {
        Path::place(p, s);
        CHECK(length == pathLen(*this, order, len));
        for (int i = 0; i < len; ++i) for (int j = i + 1; j < len; ++j) CHECK(order[i] != order[j]);
    }
};

struct CheckedJobs : Jobs {
    long long scaled() const {   // sum of load^2 + 100 * extra over placed jobs, recomputed
        long long ld[16] = {0}, extra = 0, sq = 0;
        for (int j = 0; j < n; ++j) if (done[j]) { ld[assign[j]] += d[j]; extra += c[j][assign[j]]; }
        for (int i = 0; i < m; ++i) sq += ld[i] * ld[i];
        return sq + 100 * extra;
    }
    int candidates(Cand out[], int rule) {
        const int count = Jobs::candidates(out, rule);
        const long long base = scaled();
        for (int t = 0; t < count; ++t) {
            const int j = out[t].item;
            std::vector<long long> costs;
            int bs = -1;
            long long bv = BIG;
            for (int mc = 0; mc < m; ++mc) {
                if (cnt[mc] >= k) continue;
                CheckedJobs copy = *this;
                copy.done[j] = true; copy.assign[j] = mc;
                const long long v = copy.scaled() - base;
                costs.push_back(v);
                if (v < bv) { bv = v; bs = mc; }
            }
            std::sort(costs.begin(), costs.end());
            CHECK(!costs.empty());
            if (costs.empty()) continue;
            CHECK(out[t].best == costs[0] && out[t].slot == bs);
            CHECK(out[t].second == (costs.size() > 1 ? costs[1] : BIG));
            CHECK(out[t].weight == d[j]);
        }
        return count;
    }
    void place(int j, int mc) {
        CHECK(mc >= 0 && mc < m && cnt[mc] < k);
        if (mc < 0 || mc >= m) return;
        Jobs::place(j, mc);
    }
};

static Plan plan(int rule, int width, int percent, bool randomFirst) { Plan p; p.rule = rule; p.width = width; p.percent = percent; p.randomFirst = randomFirst; return p; }

// ---------------------------------------------------------------- builders shared by measure and tests
enum PathKind { P_IDENTITY, P_STRIP8, P_NN, P_CHEAPEST, P_FARTHEST, P_REGRET };
static const char* pathNames[] = {"identity", "strip8", "nn", "cheapest", "farthest", "regret"};

template<class PathT> static void buildPath(PathT& p, int kind) {
    hc::Random rng; rng.reset(1);
    if (kind == P_IDENTITY) { int ids[Path::MAXN]; for (int i = 0; i < p.n; ++i) ids[i] = i; setOrder(p, ids); }
    else if (kind == P_STRIP8) stripOrder(p, 8);
    else {
        p.anySlot = kind != P_NN;
        const int rule = kind == P_FARTHEST ? RULE_HEAVIEST : kind == P_REGRET ? RULE_REGRET : RULE_CHEAPEST;
        construct(p, plan(rule, 1, 0, false), 0, rng);
    }
}

enum JobKind { J_INDEX, J_LIGHTEST, J_HEAVIEST, J_CHEAPEST, J_REGRET };
static const char* jobNames[] = {"index", "lightest", "heaviest", "cheapest", "regret"};

template<class JobsT> static void buildJobs(JobsT& q, int kind) {
    hc::Random rng; rng.reset(1);
    const int rule = kind == J_HEAVIEST ? RULE_HEAVIEST : kind == J_CHEAPEST ? RULE_CHEAPEST : kind == J_REGRET ? RULE_REGRET : RULE_INDEX;
    construct(q, plan(rule, 1, 0, false), 0, rng);
}

static void printSol(const char* tag, const char* name, int seed, const int* a, int n) {
    std::printf("%s %s %d", tag, name, seed);
    for (int i = 0; i < n; ++i) std::printf(" %d", a[i]);
    std::printf("\n");
}

static Path gp;
static Jobs gj, gj2;
static int sol[256];

// ---------------------------------------------------------------- measurements
static void measure() {
    const int SEEDS = 20;
    for (int seed = 1; seed <= SEEDS; ++seed) {
        for (int kind = 0; kind <= P_REGRET; ++kind) {
            makePath(gp, 200, seed);
            buildPath(gp, kind);
            CHECK(isPerm(gp.order, gp.n) && gp.length == pathLen(gp, gp.order, gp.n));
            std::printf("PATH %s %d %lld %lld\n", pathNames[kind], seed, gp.length, gp.evals);
            printSol("PSOL", pathNames[kind], seed, gp.order, gp.n);
            const long long e = improveAdjacent(gp);
            CHECK(isPerm(gp.order, gp.n) && gp.length == pathLen(gp, gp.order, gp.n));
            std::printf("PATHF %s %d %lld %lld\n", pathNames[kind], seed, gp.length, e);
        }
        for (int strips : {2, 4, 6, 8, 10, 12, 16, 24}) {
            makePath(gp, 200, seed);
            stripOrder(gp, strips);
            std::printf("STRIP %d %d %lld\n", strips, seed, gp.length);
        }
        for (int kind = 0; kind <= J_REGRET; ++kind) {
            makeJobs(gj, 120, 8, 18, seed);
            if (kind == J_LIGHTEST) {   // 작은 것부터: 번호를 길이 오름차순으로 다시 매기고 번호 순으로 구성
                makeJobs(gj2, 120, 8, 18, seed);
                int perm[120];
                for (int i = 0; i < 120; ++i) perm[i] = i;
                std::stable_sort(perm, perm + 120, [&](int a, int b) { return gj2.d[a] < gj2.d[b]; });
                for (int i = 0; i < 120; ++i) { gj.d[i] = gj2.d[perm[i]]; for (int m = 0; m < 8; ++m) gj.c[i][m] = gj2.c[perm[i]][m]; }
            }
            buildJobs(gj, kind);
            CHECK(jobsValid(gj, gj.assign) && gj.score() == jobsScore(gj, gj.assign));
            std::printf("JOBS %s %d %lld %lld\n", jobNames[kind], seed, gj.score(), gj.evals);
            if (kind != J_LIGHTEST) printSol("JSOL", jobNames[kind], seed, gj.assign, gj.n);
            const long long e = improveMove(gj);
            CHECK(jobsValid(gj, gj.assign) && gj.score() == jobsScore(gj, gj.assign));
            std::printf("JOBSF %s %d %lld %lld\n", jobNames[kind], seed, gj.score(), e);
        }
        for (int K : {18, 16, 15}) {
            for (int kind : {J_INDEX, J_HEAVIEST, J_CHEAPEST, J_REGRET}) {
                makeJobs(gj, 120, 8, K, seed);
                buildJobs(gj, kind);
                CHECK(jobsValid(gj, gj.assign));
                std::printf("JK %s %d %d %lld\n", jobNames[kind], K, seed, gj.score());
            }
        }
        // randomization, path
        struct PCfg { const char* name; Plan plan; bool any; int runs; };
        const PCfg pcfgs[] = {
            {"nn1", plan(RULE_CHEAPEST, 1, 0, false), false, 1},
            {"nn4", plan(RULE_CHEAPEST, 1, 0, true), false, 4},
            {"nn16", plan(RULE_CHEAPEST, 1, 0, true), false, 16},
            {"nn64", plan(RULE_CHEAPEST, 1, 0, true), false, 64},
            {"nnShake64", plan(RULE_CHEAPEST, 3, 10, true), false, 64},
            {"regret1", plan(RULE_REGRET, 1, 0, false), true, 1},
            {"regretShake5", plan(RULE_REGRET, 3, 25, true), true, 5},
        };
        for (const PCfg& c : pcfgs) {
            makePath(gp, 200, seed);
            gp.anySlot = c.any;
            hc::Random rng; rng.reset(7u * (unsigned)seed + 1u);
            const long long best = bestOf(gp, c.plan, c.runs, rng, sol);
            CHECK(isPerm(sol, gp.n) && pathLen(gp, sol, gp.n) == best);
            std::printf("RP %s %d %lld %lld\n", c.name, seed, best, gp.evals);
        }
        struct JCfg { const char* name; Plan plan; int runs; };
        const JCfg jcfgs[] = {
            {"regret1", plan(RULE_REGRET, 1, 0, false), 1},
            {"regretRepeat20", plan(RULE_REGRET, 1, 0, false), 20},
            {"regretShake20", plan(RULE_REGRET, 3, 25, false), 20},
            {"heaviest1", plan(RULE_HEAVIEST, 1, 0, false), 1},
            {"heaviestShake20", plan(RULE_HEAVIEST, 3, 25, false), 20},
            {"cheapest1", plan(RULE_CHEAPEST, 1, 0, false), 1},
            {"cheapestShake20", plan(RULE_CHEAPEST, 3, 25, false), 20},
        };
        for (const JCfg& c : jcfgs) {
            makeJobs(gj, 120, 8, 18, seed);
            hc::Random rng; rng.reset(7u * (unsigned)seed + 1u);
            const long long best = bestOf(gj, c.plan, c.runs, rng, sol);
            CHECK(jobsValid(gj, sol) && jobsScore(gj, sol) == best);
            std::printf("RJ %s %d %lld %lld\n", c.name, seed, best, gj.evals);
        }
    }
    // 같은 규칙을 흔들지 않고 20번 만들면 모두 같은 해, 흔들면 서로 다른 해가 나온다(입력 시드 1)
    for (int shake = 0; shake <= 1; ++shake) {
        makeJobs(gj, 120, 8, 18, 1);
        hc::Random rng; rng.reset(8);
        long long costs[20];
        const Plan pl = plan(RULE_REGRET, shake ? 3 : 1, shake ? 25 : 0, false);
        int distinct = 0;
        for (int r = 0; r < 20; ++r) {
            construct(gj, pl, 0, rng);
            costs[r] = gj.score();
            bool seen = false;
            for (int t = 0; t < r; ++t) if (costs[t] == costs[r]) seen = true;
            if (!seen) ++distinct;
        }
        std::printf("DISTINCT %s %d\n", shake ? "shake" : "repeat", distinct);
    }
    // the 64 single constructions of "nn64" on input seed 1 (figure) and consistency with bestOf
    {
        makePath(gp, 200, 1);
        gp.anySlot = false;
        hc::Random rng; rng.reset(8);
        long long run[64];
        const Plan pl = plan(RULE_CHEAPEST, 1, 0, true);
        for (int r = 0; r < 64; ++r) {
            construct(gp, pl, (int)rng.below(200u), rng);
            run[r] = gp.length;
            std::printf("SPREAD %d %lld\n", r, run[r]);
        }
        for (int R : {4, 16, 64}) {
            makePath(gp, 200, 1);
            gp.anySlot = false;
            hc::Random rng2; rng2.reset(8);
            const long long best = bestOf(gp, pl, R, rng2, sol);
            long long mn = run[0];
            for (int r = 1; r < R; ++r) if (run[r] < mn) mn = run[r];
            CHECK(best == mn);
        }
    }
}

// ---------------------------------------------------------------- tests
static void testCandidatesPath() {
    for (int seed = 1; seed <= 3; ++seed)
        for (int n : {12, 40}) {
            for (int any = 0; any <= 1; ++any)
                for (int rule : {RULE_INDEX, RULE_CHEAPEST, RULE_REGRET, RULE_HEAVIEST}) {
                    static CheckedPath cp;
                    makePath(cp, n, seed);
                    cp.anySlot = any != 0;
                    hc::Random rng; rng.reset(5);
                    construct(cp, plan(rule, 1, 0, false), 0, rng);
                    CHECK(isPerm(cp.order, cp.n) && cp.len == n);
                    makePath(cp, n, seed);
                    cp.anySlot = any != 0;
                    construct(cp, plan(rule, 3, 30, true), (int)rng.below((unsigned)n), rng);
                    CHECK(isPerm(cp.order, cp.n) && cp.len == n);
                }
        }
}

static void testCapacityJobs() {
    const int K[] = {18, 16, 15};
    for (int seed = 1; seed <= 4; ++seed)
        for (int ki = 0; ki < 3; ++ki)
            for (int kind : {J_INDEX, J_HEAVIEST, J_CHEAPEST, J_REGRET}) {
                makeJobs(gj, 120, 8, K[ki], seed);
                buildJobs(gj, kind);
                CHECK(jobsValid(gj, gj.assign));
                CHECK(gj.score() == jobsScore(gj, gj.assign));
                if (K[ki] == 15) for (int i = 0; i < 8; ++i) CHECK(gj.cnt[i] == 15);
            }
}

static void testCandidatesJobs() {
    for (int seed = 1; seed <= 3; ++seed) {
        struct Shape { int n, m, k; };
        for (Shape sh : {Shape{30, 4, 8}, Shape{120, 8, 18}, Shape{120, 8, 15}})
            for (int rule : {RULE_INDEX, RULE_CHEAPEST, RULE_REGRET, RULE_HEAVIEST}) {
                static CheckedJobs cj;
                makeJobs(cj, sh.n, sh.m, sh.k, seed);
                hc::Random rng; rng.reset(9);
                construct(cj, plan(rule, 1, 0, false), 0, rng);
                CHECK(jobsValid(cj, cj.assign));
                makeJobs(cj, sh.n, sh.m, sh.k, seed);
                construct(cj, plan(rule, 3, 50, false), 0, rng);
                CHECK(jobsValid(cj, cj.assign));
            }
    }
}

static void testBestOf() {
    for (int seed = 1; seed <= 3; ++seed) {
        makePath(gp, 60, seed);
        hc::Random rng; rng.reset(3);
        const long long best = bestOf(gp, plan(RULE_CHEAPEST, 2, 40, true), 8, rng, sol);
        CHECK(isPerm(sol, gp.n) && pathLen(gp, sol, gp.n) == best);
        makeJobs(gj, 60, 6, 11, seed);
        hc::Random rng2; rng2.reset(3);
        const long long b2 = bestOf(gj, plan(RULE_REGRET, 3, 40, false), 8, rng2, sol);
        CHECK(jobsValid(gj, sol) && jobsScore(gj, sol) == b2);
    }
}

static void testImprove() {
    for (int seed = 1; seed <= 4; ++seed) {
        for (int kind = 0; kind <= P_REGRET; ++kind) {
            makePath(gp, 200, seed);
            buildPath(gp, kind);
            const long long before = gp.length;
            improveAdjacent(gp);
            CHECK(gp.length <= before && gp.length == pathLen(gp, gp.order, gp.n) && isPerm(gp.order, gp.n));
            for (int i = 0; i + 1 < gp.n; ++i) {   // local optimum of adjacent swaps
                int tmp[200];
                for (int t = 0; t < gp.n; ++t) tmp[t] = gp.order[t];
                std::swap(tmp[i], tmp[i + 1]);
                CHECK(pathLen(gp, tmp, gp.n) >= gp.length);
            }
        }
        for (int kind : {J_INDEX, J_HEAVIEST, J_CHEAPEST, J_REGRET}) {
            makeJobs(gj, 120, 8, 18, seed);
            buildJobs(gj, kind);
            const long long before = gj.score();
            improveMove(gj);
            CHECK(gj.score() <= before && jobsValid(gj, gj.assign) && gj.score() == jobsScore(gj, gj.assign));
            // load/cnt kept consistent with assign
            int cnt[8] = {0}, load[8] = {0};
            for (int j = 0; j < 120; ++j) { ++cnt[gj.assign[j]]; load[gj.assign[j]] += gj.d[j]; }
            for (int i = 0; i < 8; ++i) CHECK(cnt[i] == gj.cnt[i] && load[i] == gj.load[i]);
            // local optimum of single moves in the scaled objective
            for (int j = 0; j < 120; ++j)
                for (int mc = 0; mc < 8; ++mc) {
                    if (mc == gj.assign[j] || gj.cnt[mc] >= gj.k) continue;
                    int tmp[120];
                    for (int t = 0; t < 120; ++t) tmp[t] = gj.assign[t];
                    tmp[j] = mc;
                    long long a[8] = {0}, b[8] = {0}, extra1 = 0, extra2 = 0, s1 = 0, s2 = 0;
                    for (int t = 0; t < 120; ++t) { a[gj.assign[t]] += gj.d[t]; b[tmp[t]] += gj.d[t]; extra1 += gj.c[t][gj.assign[t]]; extra2 += gj.c[t][tmp[t]]; }
                    for (int i = 0; i < 8; ++i) { s1 += a[i] * a[i]; s2 += b[i] * b[i]; }
                    CHECK(s2 + 100 * extra2 >= s1 + 100 * extra1);
                }
        }
    }
}

static void testDeterminismAndPick() {
    for (int seed = 1; seed <= 2; ++seed) {
        long long first = 0;
        for (int rep = 0; rep < 2; ++rep) {
            makePath(gp, 80, seed);
            hc::Random rng; rng.reset(11);
            const long long b = bestOf(gp, plan(RULE_REGRET, 3, 25, true), 4, rng, sol);
            if (rep == 0) first = b; else CHECK(b == first);
        }
        // percent 0 or width 1 never shakes: same result as the plain rule
        makePath(gp, 80, seed);
        hc::Random r1; r1.reset(1);
        construct(gp, plan(RULE_REGRET, 1, 0, false), 0, r1);
        int a[80]; for (int i = 0; i < 80; ++i) a[i] = gp.order[i];
        makePath(gp, 80, seed);
        hc::Random r2; r2.reset(99);
        construct(gp, plan(RULE_REGRET, 3, 0, false), 0, r2);
        for (int i = 0; i < 80; ++i) CHECK(a[i] == gp.order[i]);
    }
}

static void testEntry() {
    for (int seed = 1; seed <= 3; ++seed) {
        makePath(gp, 200, seed);
        const long long s = solveOrder(gp);
        CHECK(isPerm(gp.order, gp.n) && s == pathLen(gp, gp.order, gp.n));
        makeJobs(gj, 120, 8, 18, seed);
        const long long t = solveJobs(gj);
        CHECK(jobsValid(gj, gj.assign) && t == jobsScore(gj, gj.assign));
    }
}

// hand examples through the lesson code
static void hand() {
    static const int hx[7] = {5, 3, 7, 6, 6, 5, 5}, hy[7] = {5, 3, 3, 2, 9, 0, 7};
    for (int kind = P_NN; kind <= P_REGRET; ++kind) {
        gp.n = 7; gp.evals = 0;
        for (int i = 0; i < 7; ++i) { gp.px[i] = hx[i]; gp.py[i] = hy[i]; }
        buildPath(gp, kind);
        std::printf("HANDPATH %s %lld", pathNames[kind], gp.length);
        for (int i = 0; i < 7; ++i) std::printf(" %d", gp.order[i]);
        std::printf("\n");
    }
    static const int hd[6] = {10, 20, 55, 20, 10, 25};
    static const int hc2[6][2] = {{10, 10}, {5, 25}, {20, 45}, {40, 5}, {35, 35}, {5, 45}};
    for (int kind : {J_INDEX, J_HEAVIEST, J_CHEAPEST, J_REGRET}) {
        gj.n = 6; gj.m = 2; gj.k = 3; gj.evals = 0;
        for (int j = 0; j < 6; ++j) { gj.d[j] = hd[j]; for (int m = 0; m < 2; ++m) gj.c[j][m] = hc2[j][m]; }
        buildJobs(gj, kind);
        std::printf("HANDJOBS %s %lld", jobNames[kind], gj.score());
        for (int j = 0; j < 6; ++j) std::printf(" %d", gj.assign[j]);
        std::printf("\n");
    }
}

int main(int argc, char** argv) {
    const std::string mode = argc > 1 ? argv[1] : "tests";
    if (mode == "measure") measure();
    else if (mode == "tests") {
        testCandidatesPath(); testCapacityJobs(); testCandidatesJobs(); testBestOf(); testImprove(); testDeterminismAndPick(); testEntry();
        hand();
    }
    else if (mode == "m-capacity") testCapacityJobs();
    else if (mode == "m-slot") testCandidatesPath();
    else if (mode == "m-best") testBestOf();
    std::printf("FAILS %d\n", g_fail);
    return g_fail == 0 ? 0 : 1;
}
'''


def cxx(args: list[str], src: Path, exe: Path | None, syntax_only: bool = False) -> None:
    cmd = ["c++", "-std=c++17", *args]
    cmd += ["-fsyntax-only", "-x", "c++", str(src)] if syntax_only else [str(src), "-o", str(exe)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr[-3000:]


def build_harness(code: str, sanitize: bool, folder: Path, tag: str) -> Path:
    sub = folder / tag
    sub.mkdir()
    (sub / "code.cpp").write_text(code)
    (sub / "harness.cpp").write_text(HARNESS)
    flags = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"] if sanitize else ["-O1"]
    cxx(["-Wall", "-Wextra", *flags], sub / "harness.cpp", sub / "run")
    return sub / "run"


def run_mode(exe: Path, mode: str) -> subprocess.CompletedProcess:
    return subprocess.run([str(exe), mode], capture_output=True, text=True, timeout=300)


# ---------------------------------------------------------------- measurements
def parse_measure(text: str) -> dict:
    raw: dict = defaultdict(lambda: defaultdict(dict))
    for line in text.splitlines():
        p = line.split()
        if not p:
            continue
        kind = p[0]
        if kind in ("PATH", "PATHF", "JOBS", "JOBSF", "RP", "RJ"):
            raw[kind][p[1]][int(p[2])] = (int(p[3]), int(p[4]))
        elif kind == "STRIP":
            raw[kind][p[1]][int(p[2])] = int(p[3])
        elif kind == "JK":
            raw[kind][f"{p[1]}:{p[2]}"][int(p[3])] = int(p[4])
        elif kind in ("PSOL", "JSOL"):
            raw[kind][p[1]][int(p[2])] = [int(v) for v in p[3:]]
        elif kind == "SPREAD":
            raw[kind]["nn"][int(p[1])] = int(p[2])
        elif kind == "DISTINCT":
            raw[kind][p[1]][0] = int(p[2])
    return raw


def series(d: dict, idx: int | None = None) -> list[int]:
    out = []
    for s in SEEDS:
        v = d[s]
        out.append(v[idx] if idx is not None else v)
    return out


def build_measurements(raw: dict) -> dict:
    m: dict = {
        "meta": {
            "inputSeeds": SEEDS,
            "path": {"n": 200, "coordinateRange": 1000},
            "jobs": {"n": 120, "m": 8, "k": 18},
            "solverSeed": "7 * inputSeed + 1 (hc::Random), 두 번째 흔들기 실험도 같은 값",
            "generator": "x = x * 6364136223846793005 + 1442695040888963407 (unsigned 64), value = (x >> 33) % range",
            "evaluation": "비용 변화 한 번 계산 = 1회(구성에서는 항목-자리 쌍, 개선에서는 이동 후보)",
        },
        "path": {}, "strips": {}, "jobs": {}, "capacity": {}, "randomPath": {}, "randomJobs": {},
    }
    for name in raw["PATH"]:
        m["path"][name] = {"init": series(raw["PATH"][name], 0), "initEvals": series(raw["PATH"][name], 1),
                           "final": series(raw["PATHF"][name], 0), "improveEvals": series(raw["PATHF"][name], 1)}
    for s in raw["STRIP"]:
        m["strips"][s] = series(raw["STRIP"][s])
    for name in raw["JOBS"]:
        m["jobs"][name] = {"init": series(raw["JOBS"][name], 0), "initEvals": series(raw["JOBS"][name], 1),
                           "final": series(raw["JOBSF"][name], 0), "improveEvals": series(raw["JOBSF"][name], 1)}
    for key in raw["JK"]:
        m["capacity"][key] = series(raw["JK"][key])
    for name in raw["RP"]:
        m["randomPath"][name] = {"cost": series(raw["RP"][name], 0), "evals": series(raw["RP"][name], 1)}
    for name in raw["RJ"]:
        m["randomJobs"][name] = {"cost": series(raw["RJ"][name], 0), "evals": series(raw["RJ"][name], 1)}
    m["spread"] = [raw["SPREAD"]["nn"][i] for i in range(64)]
    m["distinct"] = {k: raw["DISTINCT"][k][0] for k in raw["DISTINCT"]}
    return m


def med(values: list[int]):
    v = sorted(values)
    n = len(v)
    total = v[n // 2 - 1] + v[n // 2]
    return total // 2 if total % 2 == 0 else total / 2


def fmt(x) -> str:
    return f"{x:,.1f}" if isinstance(x, float) else f"{x:,}"


def wins(a: list[int], b: list[int]) -> tuple[int, int]:
    return sum(1 for x, y in zip(a, b) if x < y), sum(1 for x, y in zip(a, b) if x > y)


def verdict(w: int, l: int) -> str:
    if w >= 15:
        return "앞섬"
    if l >= 15:
        return "뒤짐"
    return "결정 못 함"


def reduction_permille(init: list[int], final: list[int]) -> str:
    p = med([(i - f) * 1000 // i for i, f in zip(init, final)])
    p = int(p) if isinstance(p, int) else int(p)
    return f"{p // 10}.{p % 10}%"


PATH_LABELS = [("identity", "번호 순서"), ("strip8", "정렬 기준: 세로 띠 8개"), ("nn", "가장 가까운 점 잇기(NN)"),
               ("cheapest", "가장 싼 삽입"), ("farthest", "가장 먼 점 삽입"), ("regret", "후회 삽입")]
JOB_LABELS = [("index", "번호 순서대로, 가장 싼 기계"), ("lightest", "작은 것부터, 가장 싼 기계"), ("heaviest", "큰 것부터, 가장 싼 기계"),
              ("cheapest", "가장 싼 (작업, 기계) 쌍부터"), ("regret", "후회가 큰 작업부터")]


def constructor_table(data: dict, labels, ref: str, ref_label: str) -> str:
    rows = []
    ri, rf = data[ref]["init"], data[ref]["final"]
    for key, label in labels:
        e = data[key]
        if key == ref:
            vs = "기준"
        else:
            w1, w2 = wins(e["init"], ri)[0], wins(e["final"], rf)[0]
            vs = f"{w1} / {w2}"
        rows.append([label, fmt(med(e["init"])), fmt(med(e["final"])), reduction_permille(e["init"], e["final"]),
                     f"{fmt(med(e['initEvals']))} / {fmt(med(e['improveEvals']))}", vs])
    return md_table(["구성법", "구성 직후 ↓", "단순 개선 뒤 ↓", "개선이 줄인 비율", "평가 횟수 (구성 / 개선)", f"{ref_label}보다 앞선 시드 (직후 / 개선 뒤)"],
                    rows, ["---", "---:", "---:", "---:", "---:", "---:"])


def strips_table(m: dict) -> str:
    keys = ["2", "4", "6", "8", "10", "12", "16", "24"]
    return md_table(["띠 수"] + keys, [["비용 중앙값 ↓"] + [fmt(med(m["strips"][k])) for k in keys]], ["---"] + ["---:"] * len(keys))


PATH_RANDOM = [("nn1", "NN, 첫 점 0", "1"), ("nn4", "NN, 첫 점 무작위, 가장 좋은 것", "4"), ("nn16", "NN, 첫 점 무작위, 가장 좋은 것", "16"),
               ("nn64", "NN, 첫 점 무작위, 가장 좋은 것", "64"), ("nnShake64", "NN, 첫 점 무작위, 10% 흔들기, 가장 좋은 것", "64"),
               ("regret1", "후회 삽입", "1"), ("regretShake5", "후회 삽입, 첫 점 무작위, 25% 흔들기, 가장 좋은 것", "5")]


def random_path_table(m: dict) -> str:
    ref = m["randomPath"]["regret1"]["cost"]
    rows = []
    for key, label, runs in PATH_RANDOM:
        e = m["randomPath"][key]
        if key == "regret1":
            vs, vd = "기준", "-"
        else:
            w, l = wins(e["cost"], ref)
            vs, vd = f"{w} / {l}", verdict(w, l)
        rows.append([label, runs, fmt(med(e["cost"])), fmt(med(e["evals"])), vs, vd])
    return md_table(["방법", "만든 횟수", "비용 중앙값 ↓", "평가 횟수", "후회 삽입 1번보다 앞선 / 뒤진 시드", "판정"], rows,
                    ["---", "---:", "---:", "---:", "---:", "---"])


JOB_RANDOM = [("regret1", "후회 기준", "1", None), ("regretRepeat20", "후회 기준, 흔들지 않고 반복", "20", "regret1"),
              ("regretShake20", "후회 기준, 25% 흔들기", "20", "regret1"), ("heaviest1", "큰 것부터", "1", "regret1"),
              ("heaviestShake20", "큰 것부터, 25% 흔들기", "20", "heaviest1"), ("cheapest1", "가장 싼 쌍부터", "1", "regret1"),
              ("cheapestShake20", "가장 싼 쌍부터, 25% 흔들기", "20", "cheapest1")]
JOB_REF_LABEL = {"regret1": "후회 1번", "heaviest1": "큰 것부터 1번", "cheapest1": "가장 싼 쌍 1번"}


def random_jobs_table(m: dict) -> str:
    rows = []
    for key, label, runs, ref in JOB_RANDOM:
        e = m["randomJobs"][key]
        if ref is None:
            vs, vd = "기준", "-"
        else:
            w, l = wins(e["cost"], m["randomJobs"][ref]["cost"])
            vs, vd = f"{w} / {l} ({JOB_REF_LABEL[ref]})", verdict(w, l)
        rows.append([label, runs, fmt(med(e["cost"])), fmt(med(e["evals"])), vs, vd])
    return md_table(["방법", "만든 횟수", "비용 중앙값 ↓", "평가 횟수", "비교 대상보다 앞선 / 뒤진 시드", "판정"], rows,
                    ["---", "---:", "---:", "---:", "---:", "---"])


def capacity_table(m: dict) -> str:
    rows = []
    for key, label in (("index", "번호 순서대로"), ("heaviest", "큰 것부터"), ("cheapest", "가장 싼 쌍부터"), ("regret", "후회가 큰 작업부터")):
        rows.append([label] + [fmt(med(m["capacity"][f"{key}:{k}"])) for k in (18, 16, 15)])
    return md_table(["기준 (중앙값 ↓)", "K = 18", "K = 16", "K = 15 (빈 자리 없음)"], rows, ["---", "---:", "---:", "---:"])


def hub_rows(m: dict) -> list[tuple[str, str]]:
    rows = [(f"순서 틀 · {label}", fmt(med(m["path"][key]["init"]))) for key, label in PATH_LABELS]
    rows += [(f"배정 틀 · {label}", fmt(med(m["jobs"][key]["init"]))) for key, label in JOB_LABELS]
    return rows


def tables(m: dict) -> dict[str, str]:
    out = {
        "path": constructor_table(m["path"], PATH_LABELS, "nn", "NN"),
        "jobs": constructor_table(m["jobs"], JOB_LABELS, "index", "번호 순서"),
        "strips": strips_table(m),
        "randomPath": random_path_table(m),
        "randomJobs": random_jobs_table(m),
        "capacity": capacity_table(m),
        "hub": md_table(["구성법 (입력 시드 20개의 중앙값)", "비용 ↓"], [[a, b] for a, b in hub_rows(m)], ["---", "---:"]),
        "handNN": md_table(["단계", "지금 끝", "남은 점까지의 거리(점: 거리)", "고른 점"], hand_nn_rows(), ["---:", "---", "---", "---"]),
        "handCheapest": md_table(["단계", "끼우기 전 경로", "고른 점", "자리", "늘어난 길이", "끼운 뒤 경로"], hand_insertion_rows("cheapest"),
                                 ["---:", "---", "---", "---:", "---:", "---"]),
        "handDivergence": md_table(["남은 점", "가장 싼 자리", "가장 싼 비용", "두 번째로 싼 비용", "후회"], hand_divergence_rows(),
                                   ["---", "---:", "---:", "---:", "---:"]),
        "handJobsFirst": md_table(["작업", "길이", "기계 0에 둘 때(100배)", "기계 1에 둘 때(100배)", "가장 싼 값", "두 값의 차(후회)"], hand_jobs_first_rows(),
                                  ["---:", "---:", "---:", "---:", "---:", "---:"]),
        "handRegretTrace": md_table(["단계", "부하 (기계 0 / 1)", "담은 개수 (0 / 1)", "남은 작업의 후회", "고른 것"], hand_regret_trace_rows(),
                                    ["---:", "---", "---", "---", "---"]),
    }
    hp, hj = hand_path_facts(), hand_jobs_facts()
    out["handPathResult"] = md_table(
        ["구성법", "경로", "길이"],
        [[label, " → ".join(map(str, hp[k]["order"])), str(hp[k]["cost"])] for k, label in
         (("nn", "가장 가까운 점 잇기"), ("cheapest", "가장 싼 삽입"), ("farthest", "가장 먼 점 삽입"), ("regret", "후회 삽입"))],
        ["---", "---", "---:"])
    out["handJobsResult"] = md_table(
        ["기준", "작업 0~5의 기계", "부하 (기계 0 / 1)", "부하² 합 / 100", "추가 비용 합", "점수 ↓"],
        [[label, " ".join(map(str, hj[k]["assign"])), f"{hj[k]['load'][0]} / {hj[k]['load'][1]}",
          str((hj[k]['load'][0] ** 2 + hj[k]['load'][1] ** 2) // 100), str(hj[k]["extra"]), str(hj[k]["cost"])]
         for k, label in (("index", "번호 순서대로"), ("heaviest", "큰 것부터"), ("cheapest", "가장 싼 쌍부터"), ("regret", "후회가 큰 작업부터"))],
        ["---", "---", "---", "---:", "---:", "---:"])
    out["handPtsTable"] = md_table(["점"] + [str(i) for i in range(7)], [["(x, y)"] + [f"({x}, {y})" for x, y in HAND_PTS]])
    out["handJobsTable"] = md_table(["작업", "길이 d", "추가 비용 c[기계 0]", "추가 비용 c[기계 1]"],
                                    [[str(j), str(HAND_D[j]), str(HAND_C[j][0]), str(HAND_C[j][1])] for j in range(6)], ["---:", "---:", "---:", "---:"])
    return out


# ---------------------------------------------------------------- checks
def verify_against_reference(raw: dict) -> None:
    n, m, k = 200, 8, 18
    for seed in SEEDS:
        pts = make_path(n, seed)
        d, c = make_jobs(120, m, seed)
        for name in raw["PATH"]:
            order = raw["PSOL"][name][seed]
            assert is_perm(order, n), (name, seed)
            assert path_cost(pts, order) == raw["PATH"][name][seed][0], (name, seed)
            if name in ("identity", "nn") or seed <= 1:
                pass
        assert raw["PSOL"]["identity"][seed] == list(range(n))
        assert raw["PSOL"]["nn"][seed] == construct_path(pts, "cheapest", False), seed
        fin = improve_adjacent_ref(pts, raw["PSOL"]["nn"][seed])
        assert path_cost(pts, fin) == raw["PATHF"]["nn"][seed][0], seed
        for name, rule in (("index", "index"), ("heaviest", "heaviest"), ("cheapest", "cheapest"), ("regret", "regret")):
            a = raw["JSOL"][name][seed]
            assert jobs_valid(a, 120, m, k) and jobs_cost(d, c, m, a) == raw["JOBS"][name][seed][0], (name, seed)
            assert a == construct_jobs(d, c, m, k, rule), (name, seed)
        for name in ("index", "regret"):
            if seed <= 4:
                fin = improve_move_ref(d, c, m, k, raw["JSOL"][name][seed])
                assert jobs_valid(fin, 120, m, k) and jobs_cost(d, c, m, fin) == raw["JOBSF"][name][seed][0], (name, seed)
    # insertion rules replayed in Python on two inputs (the full 20 seeds run only in C++)
    for seed in (1, 2):
        pts = make_path(n, seed)
        for name, rule in (("cheapest", "cheapest"), ("farthest", "heaviest"), ("regret", "regret")):
            assert raw["PSOL"][name][seed] == construct_path(pts, rule, True), (name, seed)
    # capacity runs: every K variant stays valid (validity is also checked inside the harness)
    for seed in SEEDS:
        d, c = make_jobs(120, m, seed)
        for kk in (16, 15):
            for rule in ("index", "regret"):
                a = construct_jobs(d, c, m, kk, rule)
                assert jobs_valid(a, 120, m, kk)
                assert jobs_cost(d, c, m, a) == raw["JK"][f"{rule}:{kk}"][seed], (rule, kk, seed)
    print("OK: 20-seed deterministic solutions match the independent Python constructors, scores and improvement")


def verify_hand(out: str) -> None:
    hp, hj = hand_path_facts(), hand_jobs_facts()
    assert {k: hp[k]["cost"] for k in HAND_PATH_RESULT} == HAND_PATH_RESULT, hp
    assert hj["optimum"] == 196 and hp["optimum"] == 18
    assert {k: hj[k]["cost"] for k in HAND_JOBS_RESULT} == HAND_JOBS_RESULT, hj
    got_p, got_j = {}, {}
    for line in out.splitlines():
        p = line.split()
        if p and p[0] == "HANDPATH":
            got_p[p[1]] = (int(p[2]), [int(v) for v in p[3:]])
        if p and p[0] == "HANDJOBS":
            got_j[p[1]] = (int(p[2]), [int(v) for v in p[3:]])
    assert got_p == {k: (hp[k]["cost"], hp[k]["order"]) for k in HAND_PATH_RESULT}, got_p
    assert got_j == {k: (hj[k]["cost"], hj[k]["assign"]) for k in HAND_JOBS_RESULT}, got_j
    print("OK: hand examples (path 22/19/20/18, optimum 18; jobs 261/206/207/196, optimum 196) equal the lesson code")


def run_all(code: str, blocks: dict[str, str]) -> tuple[dict, dict]:
    with tempfile.TemporaryDirectory(prefix="lesson-construct-") as folder_name:
        folder = Path(folder_name)
        src = folder / "composed.cpp"
        src.write_text(code)
        cxx(["-Wall", "-Wextra", "-Werror"], src, None, syntax_only=True)
        print("OK: header-free composition compiles with -Wall -Wextra -Werror")

        mutations = {
            "m-capacity": ("if (cnt[mc] >= k) continue;", ""),
            "m-slot": ("for (int s = anySlot ? 0 : len; s <= len; ++s) {", "for (int s = anySlot ? 1 : len; s <= len; ++s) {"),
            "m-best": ("for (int i = 0; i < p.n; ++i) bestSol[i] = p.solution()[i];", ""),
        }
        builds = {"san": (code, True), "plain": (code, False)}
        for tag, (old, repl) in mutations.items():
            assert code.count(old) == 1, f"mutation anchor for {tag} not found exactly once"
            builds[tag] = (code.replace(old, repl), False)
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {tag: pool.submit(build_harness, c, san, folder, tag) for tag, (c, san) in builds.items()}
            exes = {tag: f.result() for tag, f in futures.items()}
        with ThreadPoolExecutor(max_workers=6) as pool:
            runs = {"tests": pool.submit(run_mode, exes["san"], "tests"), "measure": pool.submit(run_mode, exes["san"], "measure")}
            for tag in mutations:
                runs["ok-" + tag] = pool.submit(run_mode, exes["plain"], tag)
                runs[tag] = pool.submit(run_mode, exes[tag], tag)
            results = {tag: f.result() for tag, f in runs.items()}
        tests, measure = results["tests"], results["measure"]
        assert tests.returncode == 0 and "FAILS 0" in tests.stdout, tests.stdout[-1500:] + tests.stderr[-1500:]
        assert measure.returncode == 0 and "FAILS 0" in measure.stdout, measure.stdout[-1500:] + measure.stderr[-1500:]
        print("OK: tests (candidate costs = brute force, state = recomputation, local optima, determinism) and measurements ran under ASan/UBSan")
        verify_hand(tests.stdout)
        for tag in mutations:
            ok, bad = results["ok-" + tag], results[tag]
            assert ok.returncode == 0 and "FAILS 0" in ok.stdout, (tag, ok.stdout[-500:])
            assert bad.returncode != 0 and "FAILS 0" not in bad.stdout, f"mistake {tag} was not detected"
        print("OK: capacity filter removed, first slot dropped, best solution not copied: each caught by the harness")
        raw = parse_measure(measure.stdout)
    return raw, build_measurements(raw)


# ---------------------------------------------------------------- figures and text
def check_figures() -> int:
    for name in FIGURES:
        path = LESSON_DIR / "lesson-assets" / name
        svg = path.read_text(encoding="utf-8")
        assert re.search(r'viewBox="0 0 720 \d+"', svg), name
        assert 'role="img"' in svg and "<title" in svg and "<desc" in svg, name
        sizes = [float(v) for v in re.findall(r'font-size="([\d.]+)"', svg)]
        assert sizes and min(sizes) >= 16 and max(sizes) <= 28, (name, min(sizes), max(sizes))
        assert any(s == 27 for s in sizes), f"{name}: title must be 27px"
        height = int(re.search(r'viewBox="0 0 720 (\d+)"', svg).group(1))
        for m_ in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)" font-size="([\d.]+)"([^>]*)>([^<]*)</text>', svg):
            x, y, size, attrs, body = float(m_.group(1)), float(m_.group(2)), float(m_.group(3)), m_.group(4), m_.group(5)
            width = sum(size * (1.0 if ord(ch) > 0x2E80 else 0.55) for ch in body)
            if "text-anchor=\"end\"" in attrs:
                left, right = x - width, x
            elif "text-anchor=\"middle\"" in attrs:
                left, right = x - width / 2, x + width / 2
            else:
                left, right = x, x + width
            assert left >= 8 and right <= 712 and y <= height - 4, f"{name}: text may leave the figure: {body!r}"
    return len(FIGURES)


def check_text(m: dict) -> None:
    text = read_lesson_text(LESSON_ID)
    hub = read_hub_text(LESSON_ID)
    lines = hub.rstrip("\n").splitlines()
    assert 40 <= len(lines) <= 62, f"hub has {len(lines)} lines"
    t = tables(m)
    for name, table in t.items():
        if name == "hub":
            continue
        assert table in text, f"table {name} in the lesson differs from the recomputed table:\n{table}"
    check_hub_summary(LESSON_ID, hub_rows(m))
    stored = json.loads(ASSET.read_text(encoding="utf-8"))
    assert stored == json.loads(json.dumps(m)), "measurements.json differs from the recomputed values (run with --update)"
    # figures are embedded with the standard enlarge link
    for name in FIGURES:
        assert re.search(r"!\[[^\]]+\]\(\.\./lesson-assets/" + re.escape(name) + r"\)\n\n\[그림 크게 보기\]\(https://git\.readiz\.com/h-contest-lesson/lessons/"
                         + LESSON_ID + "/lesson-assets/" + re.escape(name) + r"\)", text) or \
               re.search(r"!\[[^\]]+\]\(lesson-assets/" + re.escape(name) + r"\)\n\n\[그림 크게 보기\]", text), f"figure {name} is not embedded with its link"
    # no site problem names outside the application section
    head, sep, _ = text.partition("## 적용 사례")
    assert sep, "practice page needs a '## 적용 사례' section"
    for name in SITE_PROBLEMS:
        assert name not in head, f"site problem {name} appears outside the application section"
    for heading in ("언제 쓰고 언제 쓰지 않는가", "흔한 실수", "다른 문제에 옮길 때", "적용 사례"):
        assert re.search(r"^## .*" + heading, text, re.M), f"missing section: {heading}"
    checklist = re.search(r"## 다른 문제에 옮길 때[^\n]*\n(.*?)(?=\n## )", text, re.S)
    assert checklist and 5 <= len(re.findall(r"^\d+\. ", checklist.group(1), re.M)) <= 8, "checklist needs 5-8 questions"
    assert text.count("코드 환경") >= 1
    print(f"OK: {len(t) - 1} tables, hub summary and measurements.json equal the recomputed values; sections, figures and application section present")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--tables", action="store_true")
    args = parser.parse_args()
    code, blocks = assemble()
    raw, m = run_all(code, blocks)
    verify_against_reference(raw)
    if args.update:
        ASSET.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {ASSET.relative_to(ROOT)}")
    if args.tables:
        for name, table in tables(m).items():
            print(f"### {name}\n{table}\n")
        return
    check_text(m)
    print(f"OK: {check_figures()} figures")


if __name__ == "__main__":
    main()
