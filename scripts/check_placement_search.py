"""Check the LANDINGX placement-search lesson: extracted code, hand example, failures, stored benchmark.

Without --judge only the checks that need no grader run: header-free composition, candidate
generation against a brute-force enumeration of the statement rule, move differences and
apply/undo against a full recomputation (ASan/UBSan), the hand-example table recomputed in
Python, two failing variants that must be detected, and the stored benchmark against the
lesson tables. With --judge /path/to/LANDINGX/main.cpp --output FILE the measurements are
repeated and FILE (normally lessons/placement-search/lesson-assets/landingx-benchmark.json)
is written. The grader is only compiled and run; the solution code uses none of its internals.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpp_library import check_submission_code, read_library_snippets  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "lessons/placement-search/lesson.md"
ASSETS = ROOT / "lessons/placement-search/lesson-assets"
ASSET = ASSETS / "landingx-benchmark.json"
MAX_TC = 10
PASS_SCORE = 3001673
SEEDS = list(range(1, 10))
STAGE_BUDGET = 1000000
BUDGETS = [10000, 30000, 100000, 300000, 1000000]
TABLE_BUDGET = 100000
BLOCKS = ("land-state", "land-build", "land-greedy", "land-local", "land-destroy", "land-entry")
SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
SAN = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
MODE_NAMES = {0: "한 영역", 1: "무작위 k개", 2: "낮은 점수 k개"}
DESTROY_GRID = [(0, 1), (0, 4), (0, 16), (1, 1), (1, 4), (1, 16), (2, 2), (2, 8)]
NOISES = [0, 30, 100, 200, 400]

# Hand example: a 4 x 6 map and four spaceships (height, width).
HAND_MAP = [[0, 0, 0, 3, 0, 9],
            [3, 0, 9, 9, 5, 0],
            [0, 9, 9, 3, 0, 9],
            [5, 0, 0, 0, 3, 0]]
HAND_SHIPS = [(2, 5), (2, 2), (3, 3), (2, 5)]


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
    sn = snippets()
    lib = read_library_snippets()
    common = "\n".join([lib["random"], lib["sort"]] + [sn[n] for n in BLOCKS[:-1]])
    return {"common": common, "final": common + "\n" + sn["land-entry"], "blocks": sn}


# ---------------------------------------------------------------- hand example (independent of the C++ code)
def weight(a: int, b: int) -> int:
    return a * b * min(a, b)


def kind_of(a: int, b: int) -> tuple[int, int]:
    return (min(a, b), max(a, b))


def hand_candidates() -> list[tuple[int, int, int, int]]:
    """(row, col, a, b) in the lesson code's order: kinds ascending, upright then turned."""
    rows, cols = len(HAND_MAP), len(HAND_MAP[0])
    out = []
    for lo, hi in sorted({kind_of(*s) for s in HAND_SHIPS}):
        for a, b in ([(lo, hi)] if lo == hi else [(lo, hi), (hi, lo)]):
            for r in range(rows - a + 1):
                for c in range(cols - b + 1):
                    v = [HAND_MAP[r][c], HAND_MAP[r][c + b - 1], HAND_MAP[r + a - 1][c], HAND_MAP[r + a - 1][c + b - 1]]
                    if max(v) - min(v) <= 6:
                        out.append((r, c, a, b))
    return out


def cells(x: tuple[int, int, int, int]) -> set[tuple[int, int]]:
    return {(y, z) for y in range(x[0], x[0] + x[2]) for z in range(x[1], x[1] + x[3])}


def hand_limits() -> dict[tuple[int, int], int]:
    limit: dict[tuple[int, int], int] = {}
    for s in HAND_SHIPS:
        limit[kind_of(*s)] = limit.get(kind_of(*s), 0) + 1
    return limit


def feasible(sel: list[int], cands: list[tuple[int, int, int, int]]) -> bool:
    used: set[tuple[int, int]] = set()
    have: dict[tuple[int, int], int] = {}
    limit = hand_limits()
    for i in sel:
        cs = cells(cands[i])
        if used & cs:
            return False
        used |= cs
        k = kind_of(cands[i][2], cands[i][3])
        have[k] = have.get(k, 0) + 1
        if have[k] > limit.get(k, 0):
            return False
    return True


def hand_facts() -> dict:
    cands = hand_candidates()
    w = [weight(c[2], c[3]) for c in cands]
    order = sorted(range(len(cands)), key=lambda i: (-w[i], i))
    sel: list[int] = []
    for i in order:
        if feasible(sel + [i], cands):
            sel.append(i)
    score = sum(w[i] for i in sel)
    best, best_sel = 0, []
    for mask in range(1 << len(cands)):
        s = [i for i in range(len(cands)) if mask >> i & 1]
        if feasible(s, cands) and sum(w[i] for i in s) > best:
            best, best_sel = sum(w[i] for i in s), s
    limit = hand_limits()
    rows = []
    for x in range(len(cands)):
        if x in sel:
            continue
        conf = [y for y in sel if cells(cands[x]) & cells(cands[y])]
        k = kind_of(cands[x][2], cands[x][3])
        have = sum(1 for y in sel if kind_of(cands[y][2], cands[y][3]) == k) - sum(1 for y in conf if kind_of(cands[y][2], cands[y][3]) == k)
        if len(conf) > 1:
            rows.append((x, len(conf), 0, 0))
        elif have >= limit[k]:
            rows.append((x, len(conf), 0, 0))
        else:
            rows.append((x, len(conf), 1, w[x] - sum(w[y] for y in conf)))
    # Plateau closure: states reachable by equal-score single moves, and any improving single move there.
    seen = {frozenset(sel)}
    stack = [frozenset(sel)]
    improving = 0
    while stack:
        state = stack.pop()
        for x in range(len(cands)):
            if x in state:
                continue
            conf = [y for y in state if cells(cands[x]) & cells(cands[y])]
            if len(conf) > 1:
                continue
            new = (set(state) - set(conf)) | {x}
            if not feasible(sorted(new), cands):
                continue
            d = w[x] - sum(w[y] for y in conf)
            improving += d > 0
            if d == 0 and frozenset(new) not in seen:
                seen.add(frozenset(new))
                stack.append(frozenset(new))
    return {"cands": cands, "weights": w, "greedy": sel, "greedy_score": score, "best": best, "best_sel": best_sel,
            "rows": rows, "plateau_states": len(seen), "improving": improving}


def cand_name(c: tuple[int, int, int, int]) -> str:
    return f"{c[2]}×{c[3]} @({c[0]},{c[1]})"


def hand_table() -> str:
    f = hand_facts()
    c, w = f["cands"], f["weights"]
    lines = ["| 후보 | 점수 | 겹치는 선택 후보 | 판정 | 점수 변화 |", "| --- | ---: | ---: | --- | ---: |"]
    for x in f["greedy"]:
        lines.append(f"| {cand_name(c[x])} | {w[x]} | - | 선택됨 | - |")
    for x, n, ok, delta in f["rows"]:
        if n > 1:
            lines.append(f"| {cand_name(c[x])} | {w[x]} | {n} | 제안하지 않음 | - |")
        elif not ok:
            lines.append(f"| {cand_name(c[x])} | {w[x]} | {n} | 거절: 종류 한도 | - |")
        else:
            lines.append(f"| {cand_name(c[x])} | {w[x]} | {n} | 교체 | {delta:+d} |")
    return "\n".join(lines)


# ---------------------------------------------------------------- C++ harness
HARNESS = r'''
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <random>
#include <set>
#include <vector>

static int world[MAP_SIZE][MAP_SIZE];
static Spaceship fleet[SPACESHIP_SIZE];
static land::Board board, other, snap;
static int ansRow[SPACESHIP_SIZE], ansCol[SPACESHIP_SIZE], ansDir[SPACESHIP_SIZE];

// Outside the live R x C area every rectangle has two corners that differ by more than 6.
static void walls(int R, int C) {
    for (int y = 0; y < MAP_SIZE; ++y)
        for (int x = 0; x < MAP_SIZE; ++x)
            if (y >= R || x >= C) world[y][x] = 1000 + 20 * (y % 11) + 20 * (x % 11);
}

// The statement's rule, written separately from land::reason.
static bool specOk(int r, int c, int a, int b) {
    if (r < 0 || c < 0 || r + a > MAP_SIZE || c + b > MAP_SIZE) return false;
    int v[4] = {world[r][c], world[r][c + b - 1], world[r + a - 1][c], world[r + a - 1][c + b - 1]};
    return *std::max_element(v, v + 4) - *std::min_element(v, v + 4) <= 6;
}

static std::set<std::vector<int>> bruteCandidates(int R, int C, int n) {
    std::set<std::vector<int>> out;
    for (int i = 0; i < n; ++i) {
        int hw[2][2] = {{fleet[i].height, fleet[i].width}, {fleet[i].width, fleet[i].height}};
        for (auto& f : hw)
            for (int r = 0; r + f[0] <= R; ++r)
                for (int c = 0; c + f[1] <= C; ++c)
                    if (specOk(r, c, f[0], f[1])) out.insert({r, c, f[0], f[1]});
    }
    return out;
}

static std::set<std::vector<int>> builtCandidates() {
    std::set<std::vector<int>> out;
    for (int c = 0; c < land::candCount; ++c)
        out.insert({land::candRow[c], land::candCol[c], land::candH[c], land::candW[c]});
    assert((int)out.size() == land::candCount);
    return out;
}

// Same rule as the public grader's verify(): false for any invalid placement.
static bool judgeVerify(int n, long long& score) {
    static bool occ[MAP_SIZE][MAP_SIZE];
    for (int y = 0; y < MAP_SIZE; ++y)
        for (int x = 0; x < MAP_SIZE; ++x) occ[y][x] = false;
    score = 0;
    for (int i = 0; i < n; ++i) {
        if (ansRow[i] == -1 || ansCol[i] == -1 || ansDir[i] == -1) continue;
        int y1 = ansRow[i], x1 = ansCol[i], y2, x2;
        int h = fleet[i].height, w = fleet[i].width;
        if (ansDir[i] == 0) { y2 = y1 + h - 1; x2 = x1 + w - 1; }
        else { y2 = y1 + w - 1; x2 = x1 + h - 1; }
        if (y1 < 0 || x1 < 0 || y2 >= MAP_SIZE || x2 >= MAP_SIZE) return false;
        int v[4] = {world[y1][x1], world[y1][x2], world[y2][x1], world[y2][x2]};
        if (*std::max_element(v, v + 4) - *std::min_element(v, v + 4) > 6) return false;
        for (int y = y1; y <= y2; ++y)
            for (int x = x1; x <= x2; ++x) {
                if (occ[y][x]) return false;
                occ[y][x] = true;
            }
        score += h * w * std::min(h, w);
    }
    return true;
}

// Rebuild the occupancy grid from picked[] by the book and compare every cell.
static void sameGrid(const land::Board& bd) {
    static int fresh[MAP_SIZE][MAP_SIZE];
    for (int y = 0; y < MAP_SIZE; ++y)
        for (int x = 0; x < MAP_SIZE; ++x) fresh[y][x] = -1;
    long long score = 0;
    for (int i = 0; i < bd.count; ++i) {
        int c = bd.picked[i];
        for (int y = land::candRow[c]; y < land::candRow[c] + land::candH[c]; ++y)
            for (int x = land::candCol[c]; x < land::candCol[c] + land::candW[c]; ++x) {
                assert(fresh[y][x] == -1);  // two selected candidates overlap
                fresh[y][x] = c;
            }
        score += land::candWeight[c];
    }
    assert(score == bd.score);
    int have[land::KINDS] = {0};
    for (int i = 0; i < bd.count; ++i) ++have[land::candKind[bd.picked[i]]];
    for (int k = 0; k < land::KINDS; ++k) assert(have[k] == bd.have[k] && have[k] <= land::kindLimit[k]);
    for (int y = 0; y < MAP_SIZE; ++y)
        for (int x = 0; x < MAP_SIZE; ++x) assert(fresh[y][x] == bd.owner[y][x]);
}

static void submitAndJudge(int n) {
    for (int i = 0; i < n; ++i) ansRow[i] = ansCol[i] = ansDir[i] = -2;
    land::submit(board, ansRow, ansCol, ansDir);
    long long score;
    assert(judgeVerify(n, score));
    assert(score == board.score);
    int placed = 0;
    for (int i = 0; i < n; ++i) placed += ansRow[i] >= 0;
    assert(placed == board.count);
}

static long long gKey[land::MAX_CAND];
static int gOrd[land::MAX_CAND], gTmp[land::MAX_CAND];
static void greedyByWeight() {
    land::evaluations = 0;
    for (int c = 0; c < land::candCount; ++c) gKey[c] = -(long long)land::candWeight[c];
    land::sweep(board, gKey, gOrd, gTmp);
}

static int improvingMoves() {
    int n = 0;
    for (int x = 0; x < land::candCount; ++x) {
        int drop;
        long long delta;
        if (board.slot[x] < 0 && land::evaluate(board, x, drop, delta) && delta > 0) ++n;
    }
    return n;
}

static void handExample() {
    const int M[4][6] = {{0, 0, 0, 3, 0, 9}, {3, 0, 9, 9, 5, 0}, {0, 9, 9, 3, 0, 9}, {5, 0, 0, 0, 3, 0}};
    for (int y = 0; y < 4; ++y) for (int x = 0; x < 6; ++x) world[y][x] = M[y][x];
    walls(4, 6);
    const int S[4][2] = {{2, 5}, {2, 2}, {3, 3}, {2, 5}};
    for (int i = 0; i < 4; ++i) { fleet[i].height = S[i][0]; fleet[i].width = S[i][1]; }
    land::clear(board);
    land::build(world, fleet, 4, board);
    land::buildBuckets();
    for (int c = 0; c < land::candCount; ++c)
        std::printf("HANDCAND %d %d %d %d %d\n", c, land::candRow[c], land::candCol[c], land::candH[c], land::candW[c]);
    greedyByWeight();
    std::printf("HANDGREEDY %lld %d\n", board.score, board.count);
    for (int i = 0; i < board.count; ++i) std::printf("HANDPICK %d\n", board.picked[i]);
    for (int x = 0; x < land::candCount; ++x) {
        if (board.slot[x] >= 0) continue;
        int own[25];
        int n = land::owners(board, x, own);
        int drop;
        long long delta = 0;
        bool ok = land::evaluate(board, x, drop, delta);
        std::printf("HANDMOVE %d %d %d %lld\n", x, n, ok ? 1 : 0, ok ? delta : 0LL);
    }
    assert(improvingMoves() == 0);
    // Repairing in the same score order gives the same layout back.
    land::DestroyParams same = {land::REGION, 2, 0};
    hc::Random rng;
    rng.reset(1u);
    for (int i = 0; i < 50; ++i) land::destroyRepair(board, rng, same);
    assert(board.score == 35);
    // Random repair multipliers find the better layout; iterations to the first 40 for seeds 1..9.
    land::DestroyParams noisy = {land::REGION, 2, 200};
    int worst = 0;
    for (unsigned seed = 1; seed <= 9; ++seed) {
        land::clear(board);
        greedyByWeight();
        rng.reset(seed);
        int iters = 0;
        while (board.score < 40 && iters < 1000) { land::destroyRepair(board, rng, noisy); ++iters; }
        assert(board.score == 40);
        sameGrid(board);
        worst = std::max(worst, iters);
        std::printf("HANDSEED %u %d\n", seed, iters);
    }
    std::printf("HANDWORST %d\n", worst);
    // Remove both chosen candidates by hand and place the two 2x5 candidates.
    land::clear(board);
    greedyByWeight();
    land::take(board, board.picked[0]);
    land::take(board, board.picked[0]);
    assert(board.count == 0 && board.score == 0);
    sameGrid(board);
    assert(land::candRow[3] == 0 && land::candCol[3] == 0 && land::candRow[5] == 2 && land::candCol[5] == 0);
    assert(land::canAdd(board, 3));
    land::put(board, 3);
    assert(land::canAdd(board, 5));
    land::put(board, 5);
    assert(board.score == 40);
    sameGrid(board);
    land::clear(board);
}

static void randomWorld(std::mt19937& rng, int R, int C, int maxHeight, int n) {
    for (int y = 0; y < R; ++y) for (int x = 0; x < C; ++x) world[y][x] = (int)(rng() % (maxHeight + 1));
    walls(R, C);
    for (int i = 0; i < n; ++i) { fleet[i].height = 2 + (int)(rng() % 4); fleet[i].width = 2 + (int)(rng() % 4); }
}

static void sameAsSnapshot() {
    assert(board.count == snap.count && board.score == snap.score);
    for (int k = 0; k < land::KINDS; ++k) assert(board.have[k] == snap.have[k]);
    for (int y = 0; y < MAP_SIZE; ++y)
        for (int x = 0; x < MAP_SIZE; ++x) assert(board.owner[y][x] == snap.owner[y][x]);
    std::set<int> a(board.picked, board.picked + board.count), b(snap.picked, snap.picked + snap.count);
    assert(a == b);
}

static bool overlap(int x, int y) {
    using namespace land;
    return !(candRow[x] + candH[x] <= candRow[y] || candRow[y] + candH[y] <= candRow[x] ||
             candCol[x] + candW[x] <= candCol[y] || candCol[y] + candW[y] <= candCol[x]);
}

// Exhaustive optimum over all subsets (candCount <= 16) with the per-kind limit.
static long long optimum() {
    int n = land::candCount;
    long long best = 0;
    for (int mask = 0; mask < (1 << n); ++mask) {
        int have[land::KINDS] = {0};
        long long w = 0;
        bool ok = true;
        for (int i = 0; i < n && ok; ++i) {
            if (!(mask >> i & 1)) continue;
            if (++have[land::candKind[i]] > land::kindLimit[land::candKind[i]]) ok = false;
            w += land::candWeight[i];
            for (int j = 0; j < i && ok; ++j)
                if ((mask >> j & 1) && overlap(i, j)) ok = false;
        }
        if (ok && w > best) best = w;
    }
    return best;
}

static void stress() {
    std::mt19937 rng(20261118);
    int smallCount = 0, hitGreedy = 0, hitHill = 0, hitDR = 0;
    for (int trial = 0; trial < 100; ++trial) {
        int R = 3 + (int)(rng() % 13), C = 3 + (int)(rng() % 13);
        int n = 1 + (int)(rng() % 30);
        int maxHeight = trial % 3 == 0 ? 6 : (trial % 3 == 1 ? 12 : 30);
        randomWorld(rng, R, C, maxHeight, n);
        land::clear(board);
        land::build(world, fleet, n, board);
        assert(builtCandidates() == bruteCandidates(R, C, n));
        int limitSum = 0;
        for (int k = 0; k < land::KINDS; ++k) limitSum += land::kindLimit[k];
        assert(limitSum == n);
        land::buildBuckets();
        hc::Random hr;
        hr.reset(trial + 1u);
        // 1. one move: the predicted delta equals the recomputed score; the grid stays exact
        greedyByWeight();
        sameGrid(board);
        long long greedyScore = board.score;
        for (int rep = 0; rep < 6 && land::candCount > 0; ++rep) {
            int x = (int)(rng() % land::candCount);
            int drop;
            long long delta;
            if (board.slot[x] < 0 && land::evaluate(board, x, drop, delta)) {
                other = board;
                long long before = other.score;
                if (drop >= 0) land::take(other, drop);
                land::put(other, x);
                assert(other.score == before + delta);
                sameGrid(other);
            }
        }
        // 2. the undo log restores the exact earlier state, including the grid
        for (int rep = 0; rep < 4; ++rep) {
            snap = board;
            land::opCount = 0;
            for (int s = 0; s < 6 && board.count > 0; ++s) land::change(board, board.picked[rng() % board.count], false);
            for (int s = 0; s < 12 && land::candCount > 0; ++s) {
                int x = (int)(rng() % land::candCount);
                if (land::canAdd(board, x)) land::change(board, x, true);
            }
            sameGrid(board);
            land::undo(board);
            sameAsSnapshot();
        }
        // 3. destroy/repair never lowers the score, leaves no log behind, keeps the grid exact
        land::DestroyParams params[] = {{land::REGION, 0, 0}, {land::REGION, 3, 200}, {land::REGION, 40, 200},
                                        {land::RANDOM_K, 1, 100}, {land::RANDOM_K, 5, 200}, {land::RANDOM_K, 900, 200},
                                        {land::LOWEST_K, 4, 200}};
        for (auto& prm : params) {
            for (int it = 0; it < 4; ++it) {
                long long before = board.score;
                land::destroyRepair(board, hr, prm);
                assert(board.score >= before && land::opCount == 0);
            }
            sameGrid(board);
        }
        // 4. hill climbing never lowers the score; on small inputs it ends without an improving move
        long long before = board.score;
        land::hillClimb(board, hr, 3000);
        assert(board.score >= before);
        sameGrid(board);
        if (land::candCount <= 40) {
            land::hillClimb(board, hr, 20000);
            assert(improvingMoves() == 0);
        }
        // 5. the answer is valid under the grader's rule
        submitAndJudge(n);
        // 6. small inputs: nothing beats the exhaustive optimum
        if (land::candCount <= 16) {
            long long opt = optimum();
            assert(board.score <= opt && greedyScore <= opt);
            ++smallCount;
            hitGreedy += greedyScore == opt;
            land::clear(board);
            greedyByWeight();
            land::hillClimb(board, hr, 2000);
            assert(board.score <= opt);
            hitHill += board.score == opt;
            land::clear(board);
            greedyByWeight();
            land::DestroyParams prm = {land::REGION, 3, 200};
            for (long long stop = land::evaluations + 2000; land::evaluations < stop;) land::destroyRepair(board, hr, prm);
            assert(board.score <= opt);
            hitDR += board.score == opt;
        }
        land::clear(board);
    }
    std::printf("SMALL %d %d %d %d\n", smallCount, hitGreedy, hitHill, hitDR);
}

static void edges() {
    // No candidate at all: every stage must return quietly.
    for (int y = 0; y < 5; ++y) for (int x = 0; x < 5; ++x) world[y][x] = (x + y) * 20;
    walls(5, 5);
    for (int i = 0; i < 3; ++i) { fleet[i].height = 2; fleet[i].width = 3; }
    land::clear(board);
    land::build(world, fleet, 3, board);
    assert(land::candCount == 0);
    land::buildBuckets();
    hc::Random rng;
    rng.reset(3u);
    greedyByWeight();
    land::hillClimb(board, rng, 100);
    land::DestroyParams prm = {land::REGION, 3, 200};
    for (long long stop = land::evaluations + 100; land::evaluations < stop;) land::destroyRepair(board, rng, prm);
    assert(board.count == 0);
    sameGrid(board);
    submitAndJudge(3);
    // One spaceship, many candidates: never more than one is selected.
    for (int y = 0; y < 8; ++y) for (int x = 0; x < 8; ++x) world[y][x] = 0;
    walls(8, 8);
    fleet[0].height = 3; fleet[0].width = 2;
    land::clear(board);
    land::build(world, fleet, 1, board);
    assert(land::candCount == 84);  // 3x2: 6 x 7 positions, 2x3: 7 x 6 positions
    land::buildBuckets();
    greedyByWeight();
    land::hillClimb(board, rng, 3000);
    for (long long stop = land::evaluations + 3000; land::evaluations < stop;) land::destroyRepair(board, rng, prm);
    assert(board.count == 1 && board.score == 12);  // 3 * 2 * min(3, 2)
    submitAndJudge(1);
    land::clear(board);
}

static void entry() {
    std::mt19937 rng(20261120);
    for (int round = 0; round < 2; ++round) {
        for (int y = 0; y < 24; ++y) for (int x = 0; x < 24; ++x) world[y][x] = (int)(rng() % 9);
        walls(24, 24);
        for (int i = 0; i < SPACESHIP_SIZE; ++i) { fleet[i].height = 2 + (int)(rng() % 4); fleet[i].width = 2 + (int)(rng() % 4); }
        init(world, fleet);
        for (int i = 0; i < SPACESHIP_SIZE; ++i) ansRow[i] = ansCol[i] = ansDir[i] = -1;
        process(ansRow, ansCol, ansDir);
        long long score;
        assert(judgeVerify(SPACESHIP_SIZE, score));
        assert(score == layout.score);
        sameGrid(layout);
        assert(score > 0);
    }
}

int main() {
    handExample();
    stress();
    edges();
    entry();
    std::puts("HARNESS OK");
}
'''

# Experiment entry used only for measurements; the lesson's own entry is built separately.
EXP_ENTRY = r'''
#include <stdio.h>
#include <stdlib.h>
#include <chrono>
static double envNumber(const char* key, double fallback) {
    const char* v = getenv(key);
    return v ? atof(v) : fallback;
}
static land::Board expBoard, expSaved;
static int expOrder[land::MAX_CAND], expTemp[land::MAX_CAND];
static long long expKey[land::MAX_CAND];

void init(int map[MAP_SIZE][MAP_SIZE], Spaceship spaceships[]) {
    land::clear(expBoard);
    land::build(map, spaceships, SPACESHIP_SIZE, expBoard);
    land::buildBuckets();
}

static double micros(std::chrono::steady_clock::time_point a, std::chrono::steady_clock::time_point b) {
    return std::chrono::duration<double, std::micro>(b - a).count();
}

void process(int row[], int col[], int dir[]) {
    using namespace land;
    int greedy = (int)envNumber("GREEDY", 1);   // 0 candidate order (baseline), 1 largest weight first
    int mode = (int)envNumber("MODE", 2);       // 0 greedy only, 1 hill climbing, 2 destroy/repair
    long long budget = (long long)envNumber("BUDGET", 1000000);
    unsigned seed = (unsigned)envNumber("SEED", 20261118);
    evaluations = 0;
    {
        long long all = 0;
        int cnt[KINDS] = {0}, wt[KINDS] = {0};
        for (int c = 0; c < candCount; ++c) { ++cnt[candKind[c]]; wt[candKind[c]] = candWeight[c]; }
        for (int k = 0; k < KINDS; ++k) all += (long long)wt[k] * (cnt[k] < kindLimit[k] ? cnt[k] : kindLimit[k]);
        fprintf(stderr, "BOUND %lld\n", all);
    }
    for (int c = 0; c < candCount; ++c) expKey[c] = greedy == 1 ? -(long long)candWeight[c] : c;
    sweep(expBoard, expKey, expOrder, expTemp);
    long long greedyScore = expBoard.score, greedyEval = evaluations;
    hc::Random rng;
    rng.reset(seed);
    DestroyParams prm;
    prm.mode = (int)envNumber("DMODE", 0);
    prm.size = (int)envNumber("SIZE", 8);
    prm.noise = (int)envNumber("NOISE", 200);
    long long removedTotal = 0, iters = 0;
    if (mode == 1) hillClimb(expBoard, rng, budget);
    else if (mode == 2) {
        long long stop = evaluations + budget;
        while (evaluations < stop) { removedTotal += destroyRepair(expBoard, rng, prm); ++iters; }
    }
    long long used = evaluations;
    int improving = 0;  // how many improving single moves remain: evaluate every unselected candidate
    for (int x = 0; x < candCount; ++x) {
        int drop;
        long long delta;
        if (expBoard.slot[x] < 0 && evaluate(expBoard, x, drop, delta) && delta > 0) ++improving;
    }
    fprintf(stderr, "EXP %d %lld %lld %lld %lld %lld %d %d %lld\n", candCount, greedyScore, greedyEval, expBoard.score, removedTotal, iters, expBoard.count, improving, used);
    if (envNumber("COPYTEST", 0) > 0) {
        int n = 300;
        auto t0 = std::chrono::steady_clock::now();
        for (int i = 0; i < n; ++i) destroyRepair(expBoard, rng, prm);
        auto t1 = std::chrono::steady_clock::now();
        double copyMicros = 0;
        for (int i = 0; i < n; ++i) {
            auto a = std::chrono::steady_clock::now();
            expSaved = expBoard;
            asm volatile("" ::: "memory");  // keep the copy from being optimized away
            expBoard = expSaved;
            asm volatile("" ::: "memory");
            auto b = std::chrono::steady_clock::now();
            copyMicros += micros(a, b);
            destroyRepair(expBoard, rng, prm);
        }
        fprintf(stderr, "COPY %.3f %.3f\n", micros(t0, t1) / n, copyMicros / n);
    }
    submit(expBoard, row, col, dir);
    clear(expBoard);
}
'''

BUGGY_UNDO_OLD = "        else put(bd, op.cand);"
BUGGY_UNDO_NEW = "        else { ++bd.have[candKind[op.cand]]; bd.slot[op.cand] = bd.count; bd.picked[bd.count++] = op.cand; bd.score += candWeight[op.cand]; }"
BUGGY_LIMIT_OLD = "bd.have[candKind[c]] < kindLimit[candKind[c]] && "
BUGGY_LIMIT_NEW = ""
BUGGY_LIMIT_FRAGMENT = "    return reason(bd, candRow[c], candCol[c], candH[c], candW[c]) == 0;"


def compile_run(code: str, flags: list[str], expect_ok: bool = True, timeout: int = 600):
    with tempfile.TemporaryDirectory(prefix="lesson-landing-") as folder:
        src = Path(folder) / "check.cpp"
        exe = Path(folder) / "check"
        src.write_text(code)
        subprocess.run(["c++", "-std=c++17", *flags, str(src), "-o", str(exe)], check=True)
        result = subprocess.run([str(exe)], capture_output=True, text=True, timeout=timeout)
    if expect_ok:
        assert result.returncode == 0, result.stderr[-2000:] + result.stdout[-500:]
    return result


def mutate(code: str, old: str, new: str) -> str:
    assert code.count(old) == 1, old
    return code.replace(old, new)


def run_checks(values: dict[str, str]) -> dict:
    final = values["final"]
    result = compile_run(final + "\n" + HARNESS, SAN)
    assert "HARNESS OK" in result.stdout
    facts = hand_facts()
    assert facts["greedy_score"] == 35 and facts["best"] == 40 and facts["improving"] == 0 and facts["plateau_states"] == 1, facts
    cands = facts["cands"]
    printed_cands = {}
    printed_moves = {}
    seeds = {}
    printed_pick = []
    for line in result.stdout.splitlines():
        f = line.split()
        if line.startswith("HANDCAND "):
            printed_cands[int(f[1])] = tuple(int(v) for v in f[2:6])
        elif line.startswith("HANDMOVE "):
            printed_moves[int(f[1])] = (int(f[2]), int(f[3]), int(f[4]))
        elif line.startswith("HANDPICK "):
            printed_pick.append(int(f[1]))
        elif line.startswith("HANDSEED "):
            seeds[int(f[1])] = int(f[2])
        elif line.startswith("HANDGREEDY "):
            assert int(f[1]) == facts["greedy_score"]
        elif line.startswith("SMALL "):
            small = [int(v) for v in f[1:]]
    assert [printed_cands[i] for i in range(len(cands))] == cands, (printed_cands, cands)
    assert sorted(printed_pick) == sorted(facts["greedy"]), (printed_pick, facts["greedy"])
    expected_moves = {x: (n, ok, delta) for x, n, ok, delta in facts["rows"]}
    assert printed_moves == expected_moves, (printed_moves, expected_moves)
    worst = max(seeds.values())
    assert len(seeds) == 9
    # Two wrong variants must be caught by the same harness.
    sn = values["blocks"]
    lesson = LESSON.read_text()
    assert BUGGY_UNDO_NEW.strip() in lesson and BUGGY_LIMIT_FRAGMENT.strip() in lesson
    buggy_undo = mutate(final, BUGGY_UNDO_OLD, BUGGY_UNDO_NEW)
    caught = compile_run(buggy_undo + "\n" + HARNESS, SAN, expect_ok=False)
    assert caught.returncode != 0, "undo without grid restore was not detected"
    buggy_limit = mutate(final, BUGGY_LIMIT_OLD, BUGGY_LIMIT_NEW)
    caught = compile_run(buggy_limit + "\n" + HARNESS, SAN, expect_ok=False)
    assert caught.returncode != 0, "missing per-kind limit was not detected"
    print("OK: composition, candidates vs brute force, every move difference, undo exactness, grid rebuild, "
          "hand example (35 -> stuck -> 40), small-input optimum, edge cases, two broken variants detected (ASan/UBSan)")
    return {"facts": facts, "hand_seed_worst": worst, "small": small}


# ---------------------------------------------------------------- benchmark
def build_judge(judge_text: str, user_code: str, folder: Path, name: str, flags: list[str] | None = None,
                seed: int = 5, modulus: int = 125) -> Path:
    text = judge_text
    assert text.count("int main()") == 1
    text = text.replace("int main()", "int judge_run()")
    assert "static unsigned long long seed = 5;" in text and text.count("pseudo_rand() % 125;") == 1
    text = text.replace("pseudo_rand() % 125;", f"pseudo_rand() % {modulus};")
    assert text.count("    SCORE = 0;\n    for (int tc") == 1
    text = text.replace("    SCORE = 0;\n    for (int tc", f"    SCORE = 0;\n    seed = {seed}ULL;\n    for (int tc")
    driver = ("#include <chrono>\n#include <stdlib.h>\n" + text + r'''
int main() {
    const char* r = getenv("ROUNDS");
    int rounds = r ? atoi(r) : 1;
    for (int run = 0; run < rounds; ++run) {
        auto start = std::chrono::steady_clock::now();
        judge_run();
        auto end = std::chrono::steady_clock::now();
        fprintf(stderr, "BENCH %.6f\n", std::chrono::duration<double, std::milli>(end - start).count());
    }
}
''')
    (folder / f"{name}-judge.cpp").write_text(driver)
    (folder / f"{name}-user.cpp").write_text(user_code)
    exe = folder / name
    subprocess.run(["c++", "-std=c++17", "-Wno-register", *(flags or ["-O2"]), str(folder / f"{name}-judge.cpp"),
                    str(folder / f"{name}-user.cpp"), "-o", str(exe)], check=True)
    return exe


def run_judge(exe: Path, env: dict[str, str], rounds: int = 1, lenient: bool = False) -> dict:
    full = dict(os.environ, ROUNDS=str(rounds), **env)
    r = subprocess.run([str(exe)], capture_output=True, text=True, env=full, timeout=900)
    if not lenient:
        assert r.returncode == 0, r.stderr[-1500:]
    totals = [int(v) for v in re.findall(r"^SCORE: (\d+)$", r.stdout, re.M)]
    cases = [int(v) for v in re.findall(r"^TC \d+ SCORE: (\d+)$", r.stdout, re.M)]
    times = [float(v) for v in re.findall(r"BENCH ([\d.]+)", r.stderr)]
    if not lenient:
        assert len(totals) == rounds and len(cases) == MAX_TC * rounds, (r.stdout[-300:], r.stderr[-300:])
        assert len(set(totals)) == 1 and all(cases[i:i + MAX_TC] == cases[:MAX_TC] for i in range(0, len(cases), MAX_TC))
    exp = []
    for line in r.stderr.splitlines():
        if line.startswith("EXP "):
            f = [int(v) for v in line.split()[1:]]
            exp.append({"cands": f[0], "greedy": f[1], "greedy_eval": f[2], "score": f[3], "removed": f[4], "iters": f[5],
                        "picked": f[6], "improving": f[7], "evals": f[8]})
    bound = [int(line.split()[1]) for line in r.stderr.splitlines() if line.startswith("BOUND ")]
    copy = [[float(v) for v in line.split()[1:]] for line in r.stderr.splitlines() if line.startswith("COPY ")]
    return {"total": totals[0] if totals else None, "costs": cases[:MAX_TC], "times": times, "exp": exp[:MAX_TC],
            "bound": bound[:MAX_TC], "copy": copy, "stdout": r.stdout}


def median(values):
    return statistics.median(values)


def spread(totals: list[int]) -> dict:
    return {"median": median(totals), "min": min(totals), "max": max(totals), "totals": totals}


def benchmark(values: dict[str, str], judge: Path, output: Path, checks: dict) -> None:
    judge_text = judge.read_text()
    exp_code = values["common"] + "\n" + EXP_ENTRY
    data: dict = {
        "judge_sha256": hashlib.sha256(judge.read_bytes()).hexdigest(),
        "measured_at": datetime.date.today().isoformat(),
        "environment": f"{platform.system()} {platform.mac_ver()[0]} {platform.machine()} / "
                       + subprocess.run(["c++", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
                       + " / -std=c++17 -O2 -Wno-register",
        "pass_score": PASS_SCORE, "stage_budget": STAGE_BUDGET, "timing_rounds": 9, "warmup_rounds": 1,
        "seeds": SEEDS, "table_budget": TABLE_BUDGET, "small": checks["small"], "hand_seed_worst": checks["hand_seed_worst"],
    }
    with tempfile.TemporaryDirectory(prefix="lesson-landing-bench-") as folder_name:
        folder = Path(folder_name)
        exp = build_judge(judge_text, exp_code, folder, "exp")
        final = build_judge(judge_text, values["final"], folder, "final")

        stage_defs = [
            ("first-fit", "기준선: 후보 번호 순 first-fit", {"GREEDY": "0", "MODE": "0"}),
            ("weight", "탐욕: 점수 큰 후보부터", {"GREEDY": "1", "MODE": "0"}),
            ("hill", "국소 이동(hill climbing)", {"GREEDY": "1", "MODE": "1"}),
            ("dr", "destroy/repair(한 영역)", {"GREEDY": "1", "MODE": "2"}),
        ]
        stages = []
        for key, label, env in stage_defs:
            r = run_judge(exp, env, rounds=9)
            evals = round(statistics.mean(e["evals"] for e in r["exp"]))
            row = {"key": key, "label": label, "total": r["total"], "costs": r["costs"], "evals_per_tc": evals,
                   "median_ms": median(r["times"][1:]), "runs_ms": r["times"][1:],
                   "improving_left": sum(e["improving"] for e in r["exp"])}
            if key == "weight":
                data["bound_total"] = sum(r["bound"])
                data["candidates_per_tc"] = [e["cands"] for e in r["exp"]]
            stages.append(row)
            print(json.dumps({k: row[k] for k in ("key", "total", "median_ms", "evals_per_tc")}), flush=True)
        r = run_judge(final, {}, rounds=9)
        stages.append({"key": "final", "label": "본문 제출 코드", "total": r["total"], "costs": r["costs"],
                       "median_ms": median(r["times"][1:]), "runs_ms": r["times"][1:]})
        by = {s["key"]: s for s in stages}
        assert by["final"]["costs"] == by["dr"]["costs"], "experiment entry differs from the lesson entry"
        data["stages"] = stages

        # Same code under ASan/UBSan against the real grader.
        san = build_judge(judge_text, values["final"], folder, "san", flags=SAN)
        rs = run_judge(san, {})
        assert rs["costs"] == by["final"]["costs"]
        data["sanitizer_total"] = rs["total"]

        def seeds_run(env: dict[str, str]) -> dict:
            totals, removed, iters, ms = [], [], [], []
            for seed in SEEDS:
                r = run_judge(exp, dict(env, SEED=str(seed)))
                totals.append(r["total"])
                ms.append(r["times"][0])
                removed.append(sum(e["removed"] for e in r["exp"]))
                iters.append(sum(e["iters"] for e in r["exp"]))
            return {**spread(totals), "removed": removed, "iters": iters, "median_ms": median(ms)}

        budgets = []
        for budget in BUDGETS:
            row = {"budget": budget,
                   "hill": seeds_run({"GREEDY": "1", "MODE": "1", "BUDGET": str(budget)}),
                   "dr": seeds_run({"GREEDY": "1", "MODE": "2", "BUDGET": str(budget)})}
            budgets.append(row)
            print(json.dumps({"budget": budget, "hill": row["hill"]["median"], "dr": row["dr"]["median"]}), flush=True)
        data["budgets"] = budgets

        destroy = []
        for mode, size in DESTROY_GRID:
            s = seeds_run({"GREEDY": "1", "MODE": "2", "BUDGET": str(TABLE_BUDGET), "DMODE": str(mode), "SIZE": str(size)})
            mean_removed = sum(s["removed"]) / sum(s["iters"])
            destroy.append({"mode": mode, "size": size, "median": s["median"], "min": s["min"], "max": s["max"],
                            "totals": s["totals"], "mean_removed": mean_removed, "median_iters": median(s["iters"])})
            print(json.dumps({k: destroy[-1][k] for k in ("mode", "size", "median", "mean_removed")}), flush=True)
        data["destroy"] = destroy

        noise = []
        for value in NOISES:
            s = seeds_run({"GREEDY": "1", "MODE": "2", "BUDGET": str(TABLE_BUDGET), "NOISE": str(value)})
            noise.append({"noise": value, "median": s["median"], "min": s["min"], "max": s["max"], "totals": s["totals"]})
            print(json.dumps({k: noise[-1][k] for k in ("noise", "median")}), flush=True)
        data["noise"] = noise

        # Cost of undo: log undo per iteration vs. copying the whole board twice.
        r = run_judge(exp, {"GREEDY": "1", "MODE": "2", "BUDGET": "200000", "COPYTEST": "1"})
        data["undo_cost"] = {"log_us": median([c[0] for c in r["copy"]]), "copy_us": median([c[1] for c in r["copy"]]),
                             "board_bytes": 4 * 1000 * 1000 + 4 * 32768 * 2 + 4 * 16 + 16}

        # Inputs not used for choosing parameters: other grader seeds and a flatter height range.
        unseen = []
        for label, seed, modulus in (("다른 seed 101", 101, 125), ("다른 seed 102", 102, 125), ("다른 seed 103", 103, 125), ("고도 범위 0~109, seed 101", 101, 110), ("고도 범위 0~149, seed 101", 101, 150)):
            exe = build_judge(judge_text, exp_code, folder, f"unseen{seed}x{modulus}", seed=seed, modulus=modulus)
            row = {"label": label, "seed": seed, "modulus": modulus}
            row["first_fit"] = run_judge(exe, {"GREEDY": "0", "MODE": "0"})["total"]
            row["weight"] = run_judge(exe, {"GREEDY": "1", "MODE": "0"})["total"]
            for key, env in (("hill", {"MODE": "1"}), ("dr", {"MODE": "2"})):
                totals = [run_judge(exe, dict(env, GREEDY="1", SEED=str(s)))["total"] for s in range(1, 6)]
                row[key] = spread(totals)
            unseen.append(row)
            print(json.dumps({k: row[k] for k in ("label", "first_fit", "weight")}), flush=True)
        data["unseen"] = unseen

        # Failing variants against the real grader.
        failures = {}
        for key, old, new in (("undo", BUGGY_UNDO_OLD, BUGGY_UNDO_NEW), ("limit", BUGGY_LIMIT_OLD, BUGGY_LIMIT_NEW)):
            exe = build_judge(judge_text, mutate(values["final"], old, new), folder, f"bug-{key}")
            r = run_judge(exe, {}, lenient=True)
            failures[key] = {"total": r["total"], "costs": r["costs"]}
            print(json.dumps({"failure": key, **failures[key]}), flush=True)
        data["failures"] = failures
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


# ---------------------------------------------------------------- tables
def num(n) -> str:
    return f"{int(round(n))}"


def stage_table(data: dict) -> str:
    lines = ["| 방식 | 합 ↑ | 통과 기준 3001673과의 차 | 후보 검사(TC당 평균) | 시간(ms) |", "| --- | ---: | ---: | ---: | ---: |"]
    for s in data["stages"]:
        if s["key"] == "final":
            continue
        lines.append(f"| {s['label']} | {s['total']} | {s['total'] - data['pass_score']:+d} | {s['evals_per_tc']} | {s['median_ms']:.0f} |")
    return "\n".join(lines)


def budget_table(data: dict) -> str:
    greedy = next(s for s in data["stages"] if s["key"] == "weight")["total"]
    lines = ["| 탐욕 뒤 추가 후보 검사(TC당) | 국소 이동 중앙값 | 최소~최대 | 시간(ms) | destroy/repair 중앙값 | 최소~최대 | 시간(ms) |",
             "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for b in data["budgets"]:
        h, d = b["hill"], b["dr"]
        lines.append(f"| {b['budget']:,} | {num(h['median'])} | {h['min']}~{h['max']} | {h['median_ms']:.0f} | {num(d['median'])} | {d['min']}~{d['max']} | {d['median_ms']:.0f} |")
    return "\n".join(lines)


def destroy_table(data: dict) -> str:
    lines = ["| destroy 방식 | 크기 | 합의 중앙값 ↑ | 최소~최대 | 한 번에 뺀 평균 개수 | 반복 수(중앙값) |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for d in data["destroy"]:
        size = f"여백 {d['size']}칸" if d["mode"] == 0 else f"k = {d['size']}"
        lines.append(f"| {MODE_NAMES[d['mode']]} | {size} | {num(d['median'])} | {d['min']}~{d['max']} | {d['mean_removed']:.1f} | {num(d['median_iters'])} |")
    return "\n".join(lines)


def noise_table(data: dict) -> str:
    lines = ["| 다시 채울 때의 무작위 배율 | 합의 중앙값 ↑ | 최소~최대 |", "| --- | ---: | ---: |"]
    for n in data["noise"]:
        label = "없음(점수 순서 그대로)" if n["noise"] == 0 else f"1배 ~ {1 + n['noise'] / 100:g}배"
        lines.append(f"| {label} | {num(n['median'])} | {n['min']}~{n['max']} |")
    return "\n".join(lines)


def unseen_table(data: dict) -> str:
    lines = ["| 입력 | 기준선 | 점수 큰 순 탐욕 | 국소 이동 중앙값 | 최소~최대 | destroy/repair 중앙값 | 최소~최대 |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for u in data["unseen"]:
        h, d = u["hill"], u["dr"]
        lines.append(f"| {u['label']} | {u['first_fit']} | {u['weight']} | {num(h['median'])} | {h['min']}~{h['max']} | {num(d['median'])} | {d['min']}~{d['max']} |")
    return "\n".join(lines)


def tables(data: dict) -> dict[str, str]:
    return {"hand": hand_table(), "stages": stage_table(data), "budgets": budget_table(data),
            "destroy": destroy_table(data), "noise": noise_table(data), "unseen": unseen_table(data)}


def table_after(markdown: str, key: str) -> str:
    match = re.search(r"<!-- check:" + re.escape(key) + r" -->\n((?:\|[^\n]*\n?)+)", markdown)
    assert match, f"missing table marker: {key}"
    return match.group(1).rstrip("\n")


def check_claims(data: dict, by: dict, markdown: str) -> None:
    """The sentences of the lesson that compare ranges, orderings and ratios, asserted on the stored data."""
    pass_score = data["pass_score"]
    bud = {b["budget"]: b for b in data["budgets"]}
    assert str(min(data["candidates_per_tc"])) in markdown and str(max(data["candidates_per_tc"])) in markdown
    assert 1.145 < data["bound_total"] / pass_score < 1.155, "the lesson says the bound is 15% above the pass score"
    # budget table: ranges overlap at 10,000 and separate from 30,000; the local search stops by 300,000
    assert bud[10000]["dr"]["min"] <= bud[10000]["hill"]["max"]
    for budget in (30000, 100000, 300000, 1000000):
        assert bud[budget]["dr"]["min"] > bud[budget]["hill"]["max"], budget
    assert bud[300000]["hill"]["min"] == bud[300000]["hill"]["max"] == bud[1000000]["hill"]["median"] == by["hill"]["total"]
    assert bud[1000000]["dr"]["median"] == by["dr"]["total"] == pass_score
    assert abs(bud[100000]["dr"]["median_ms"] - bud[1000000]["hill"]["median_ms"]) < 0.2 * bud[1000000]["hill"]["median_ms"], "similar time claim"
    assert bud[100000]["dr"]["median"] > bud[1000000]["hill"]["median"]
    # destroy table
    row = {(d["mode"], d["size"]): d for d in data["destroy"]}
    big = row[(0, 16)]
    assert big["median"] == max(d["median"] for d in data["destroy"]) and abs(big["mean_removed"] - 11.0) < 0.05
    assert big["min"] > row[(0, 1)]["max"] and all(big["min"] > row[(1, k)]["max"] for k in (1, 4, 16))
    assert big["min"] <= row[(0, 4)]["max"]
    others = [d for d in data["destroy"] if d["mode"] != 2 and (d["mode"], d["size"]) != (0, 16)]
    assert all(a["min"] <= b["max"] and b["min"] <= a["max"] for a in others for b in others), "remaining settings overlap pairwise"
    assert row[(0, 1)]["mean_removed"] < 1.3
    assert max(d["max"] for d in data["destroy"] if d["mode"] == 2) < bud[100000]["hill"]["min"]
    # noise table
    noise = {n["noise"]: n for n in data["noise"]}
    assert noise[0]["median"] == noise[0]["min"] == noise[0]["max"] == by["weight"]["total"]
    assert noise[30]["max"] < noise[200]["min"] and noise[100]["max"] < noise[200]["min"] and noise[400]["min"] <= noise[200]["max"]
    # unseen inputs: same ordering, separated ranges
    for u in data["unseen"]:
        assert u["first_fit"] < u["weight"] < u["hill"]["median"] < u["dr"]["median"] and u["dr"]["min"] > u["hill"]["max"], u["label"]
    # failures
    assert data["failures"]["undo"]["total"] == 0 and len(data["failures"]["undo"]["costs"]) == 1
    assert data["failures"]["limit"]["total"] == by["final"]["total"]
    assert len(hand_facts()["cands"]) == 7


def check_stored(checks: dict) -> None:
    data = json.loads(ASSET.read_text())
    markdown = LESSON.read_text()
    for key, expected in tables(data).items():
        assert table_after(markdown, key) == expected, f"lesson table '{key}' differs from the stored measurement/recomputation"
    by = {s["key"]: s for s in data["stages"]}
    assert by["final"]["costs"] == by["dr"]["costs"]
    assert data["sanitizer_total"] == by["final"]["total"]
    assert data["small"] == checks["small"] and data["hand_seed_worst"] == checks["hand_seed_worst"]
    assert by["hill"]["improving_left"] == 0 and by["dr"]["improving_left"] == 0
    needles = [str(s["total"]) for s in data["stages"]] + [data["judge_sha256"][:12], data["measured_at"], data["environment"].split(" / ")[0],
                                                           str(data["bound_total"]), str(data["failures"]["undo"]["total"]),
                                                           str(data["failures"]["limit"]["total"])]
    for needle in needles:
        assert needle in markdown.replace(",", ""), needle
    cost = data["undo_cost"]
    for needle in (f"{cost['log_us']:.1f}", f"{cost['copy_us']:.0f}"):
        assert needle in markdown, needle
    small = data["small"]
    assert f"{small[0]}개" in markdown and f"{small[1]}개" in markdown and f"{small[2]}개" in markdown and f"{small[3]}개" in markdown
    for name in ("stuck-and-repair.svg", "budget-curves.svg"):
        assert (ASSETS / name).exists(), name
    figure = (ASSETS / "stuck-and-repair.svg").read_text()
    flat = [v for row in HAND_MAP for v in row]
    shown = [int(v) for v in re.findall(r'font-size="18" fill="#3f5069" text-anchor="end">(\d+)</text>', figure)]
    assert shown == flat + flat, "figure heights differ from the hand map"
    for token in ("35점", "40점", "3×3 27", "2×2 8", "2×5 20"):
        assert token in figure, token
    curve = (ASSETS / "budget-curves.svg").read_text()
    labels = {10000: "1만", 30000: "3만", 100000: "10만", 300000: "30만", 1000000: "100만"}
    for b in data["budgets"]:
        assert f">{labels[b['budget']]}<" in curve, b["budget"]
    last = data["budgets"][-1]
    greedy = by["weight"]["total"]
    for number in (data["pass_score"] - greedy, round(data["pass_score"] - last["hill"]["median"]), round(data["pass_score"] - last["dr"]["median"])):
        assert f"{number:,}" in curve, number
    check_claims(data, by, markdown)
    print("OK: lesson tables match the recomputed hand example and the stored LANDINGX measurement")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--judge", type=Path, help="path to LANDINGX main.cpp (read only)")
    parser.add_argument("--output", type=Path, help="measurement JSON to write when --judge is given")
    parser.add_argument("--print-tables", action="store_true", help="print the generated Markdown tables")
    args = parser.parse_args()
    values = sources()
    checks = run_checks(values)
    if args.judge:
        if not args.output:
            parser.error("--judge requires --output")
        benchmark(values, args.judge, args.output, checks)
    stored = args.output or ASSET
    if args.print_tables:
        for key, text in tables(json.loads(stored.read_text())).items():
            print(f"<!-- check:{key} -->\n{text}\n")
        return
    if stored.exists():
        check_stored(checks)
    else:
        print("note: stored benchmark not found; table comparison skipped")


if __name__ == "__main__":
    main()
