"""Check the ENTROPY2D reading-the-score lesson: code blocks, score formula, differences, hand example, failures, measurements.

Without --judge only the checks that need no public grader run (about 20 s): header-free
assembly of every stage, a reference grader written from the problem contract for this check,
mirror/grader agreement on random small instances (the lesson's entropy is compared with a
plain O(n^2) pair sum before every move), the O(1) single-step difference and the relocation
difference against a full recomputation, the hand-calculated example, failing variants that
must be detected, the lower bound and the disk reference recomputed independently, the
figures, and agreement between the lesson tables and the stored measurement JSON.

With --judge /path/to/ENTROPY2D/main.cpp the public grader is compiled with a local patch
(logging and a hand-sized init only) and the stored scores are re-measured. --output writes
the JSON from a fresh measurement. The solution code uses no grader internals.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpp_library import check_submission_code  # noqa: E402
from lesson_text import check_hub_summary, read_lesson_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LESSON_ID = "reading-the-score"
ASSETS = ROOT / "lessons/reading-the-score/lesson-assets"
DATA = ASSETS / "entropy2d-benchmark.json"
SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
SAN = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
COMMON = ("ent-state", "ent-score", "ent-axis", "ent-act")
STAGES = {
    0: ("기준선", COMMON + ("ent-baseline",)),
    1: ("중앙으로 밀기", COMMON + ("ent-naive",)),
    2: ("차분 탐욕", COMMON + ("ent-greedy", "ent-entry-greedy")),
    3: ("큰 이득부터", COMMON + ("ent-greedy", "ent-entry-threshold")),
    4: ("빈 칸 경로 재배치", COMMON + ("ent-greedy", "ent-relocate", "ent-entry-final")),
    5: ("목표 배치 짝짓기", COMMON + ("ent-target", "ent-match")),
}
PASS_SCORE = 1917000
HAND_POINTS = [(0, 0), (0, 4), (3, 0), (3, 4), (1, 2)]
HAND_H, HAND_W = 4, 5
ALL_BLOCKS = {b for _, names in STAGES.values() for b in names} | {"ent-hand"}


def snippets() -> dict[str, str]:
    found: dict[str, str] = {}
    for name, code in SNIP_RE.findall(read_lesson_text(LESSON_ID)):
        assert name not in found, f"duplicate snippet {name}"
        check_submission_code(code, name)
        found[name] = code + "\n"
    assert ALL_BLOCKS <= set(found), f"missing snippets: {ALL_BLOCKS - set(found)}"
    return found


def assemble(stage: int, sn: dict[str, str], edits: list[tuple[str, str]] | None = None, blocks: tuple[str, ...] | None = None) -> str:
    parts = [sn[n] for n in (blocks or STAGES[stage][1])]
    for old, new in edits or []:
        for i, part in enumerate(parts):
            if re.search(old, part):
                parts[i] = re.sub(old, new, part, count=1)
                break
        else:
            raise AssertionError(f"edit target not found: {old}")
    return "\n".join(parts)


def with_const(name: str, value: str) -> list[tuple[str, str]]:
    return [(rf"(const (?:int|long long) {name} = )[\d.]+;", rf"\g<1>{value};")]


def compile_to(exe: Path, sources: list[Path], extra: list[str]) -> None:
    done = subprocess.run(["c++", "-std=c++17", *extra, *map(str, sources), "-o", str(exe)],
                          capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError(done.stderr[:2000])


def run(exe: Path, *args: str, timeout: int = 300) -> str:
    return subprocess.run([str(exe), *args], check=True, capture_output=True, text=True, timeout=timeout).stdout


# ---------------------------------------------------------------- reference grader (this check only)
REF = r'''
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cassert>
#include <string>

static bool rg[180][180];
static int rH, rW;
static long long rUsed, rLimit, rE0;
static bool rIn;
static int rLogN, rLog[64][3];          // successful moves of the current run (first 64), for the traced example
static unsigned long long rs;
static unsigned rnd() { rs = rs * 6364136223846793005ULL + 1442695040888963407ULL; return (unsigned)(rs >> 33); }

// The statement's definition written directly: every pair once, |dy| + |dx|.
static long long refEntropy() {
    static int py[32400], px[32400];
    int n = 0;
    for (int y = 0; y < rH; ++y) for (int x = 0; x < rW; ++x) if (rg[y][x]) { py[n] = y; px[n] = x; ++n; }
    long long e = 0;
    for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) e += abs(py[i] - py[j]) + abs(px[i] - px[j]);
    return e;
}
static int refCount() { int n = 0; for (int y = 0; y < rH; ++y) for (int x = 0; x < rW; ++x) n += rg[y][x]; return n; }
int getHeight() { return rH; }
int getWidth() { return rW; }
int getParticleCount() { return refCount(); }
long long getMoveLimit() { return rLimit; }
long long getMoveCount() { return rUsed; }
int getCell(int y, int x) { return (y < 0 || y >= rH || x < 0 || x >= rW) ? -1 : rg[y][x]; }
int moveParticle(int y, int x, int dir) {
    if (rIn) {     // the lesson's mirror must equal the real state before every call
        assert(ent::G.entropy == refEntropy());
        assert(ent::G.used == rUsed);
    }
    if (rUsed >= rLimit) return 0;
    ++rUsed;
    if (y < 0 || y >= rH || x < 0 || x >= rW || dir < 0 || dir > 3 || !rg[y][x]) return 0;
    static const int dy[4] = {-1, 0, 1, 0}, dx[4] = {0, 1, 0, -1};
    int ny = y + dy[dir], nx = x + dx[dir];
    if (ny < 0 || ny >= rH || nx < 0 || nx >= rW || rg[ny][nx]) return 0;
    rg[y][x] = false; rg[ny][nx] = true;
    if (rLogN < 64) { rLog[rLogN][0] = y; rLog[rLogN][1] = x; rLog[rLogN][2] = dir; }
    ++rLogN;
    return 1;
}
static long long refScore(long long e0, long long e) {
    long long imp = e0 - e; if (imp < 0) imp = 0;
    double ratio = (double)imp / (double)e0;
    return (long long)(1000000.0 * ratio * ratio) + (rLimit - rUsed) / 100;
}
static void load(int H, int W, int permille, unsigned long long seed) {
    rH = H; rW = W; rs = seed * 7919ULL + 13; memset(rg, 0, sizeof rg);
    for (int y = 0; y < H; ++y) for (int x = 0; x < W; ++x) rg[y][x] = rnd() % 1000 < (unsigned)permille;
    rLimit = (long long)H * W * 40; rUsed = 0; rE0 = refEntropy();
}
static int gTc;
static void hook(long long s, long long e0, long long e, long long used, int refused, int mismatch) {
    printf("TC %d MIRROR %lld %lld %lld %lld %d %d\n", gTc, s, e0, e, used, refused, mismatch);
}
static void dumpGrid(const char* tag, int tc) {
    printf("TC %d GRID %s %d %d\n", tc, tag, rH, rW);
    for (int y = 0; y < rH; ++y) { for (int x = 0; x < rW; ++x) putchar(rg[y][x] ? '#' : '.'); putchar('\n'); }
}
static void runOne(int tc, int H, int W, int pm, unsigned long long seed) {
    load(H, W, pm, seed); gTc = tc; ent::hook = hook; rIn = true;
    dumpGrid("I", tc);
    process();
    rIn = false;
    dumpGrid("F", tc);
#ifdef LOCAL_OPT
    if (ent::G.used < ent::G.limit)      // the greedy stopped because no legal single move lowers the entropy
        for (int i = 0; i < ent::G.n; ++i) for (int d = 0; d < 4; ++d)
            assert(!(ent::canMove(ent::G.py[i], ent::G.px[i], d) && ent::delta(ent::G.py[i], ent::G.px[i], d) < 0));
#endif
    long long e = refEntropy();
    printf("TC %d SCORE %lld\n", tc, refScore(rE0, e));
    printf("TC %d REF %lld %lld %lld\n", tc, rE0, e, rUsed);
}
static void teleport(int i, int y, int x) {
    ent::G.occ[ent::G.py[i]][ent::G.px[i]] = false;
    ent::G.py[i] = y; ent::G.px[i] = x; ent::G.occ[y][x] = true;
}
int main(int argc, char** argv) {
    std::string mode = argv[1];
    if (mode == "run") {
        for (int i = 2; i < argc; ++i) {
            int H, W, pm; unsigned long long seed;
            sscanf(argv[i], "%d:%d:%d:%llu", &H, &W, &pm, &seed);
            runOne(i - 1, H, W, pm, seed);
        }
    } else if (mode == "big") {
        load(180, 180, 500, 5);
        ent::init();
        printf("BIG n=%d mirror=%lld pairs=%lld ref=%lld\n", ent::G.n, ent::G.e0, ent::entropyPairs(), rE0);
    } else if (mode == "delta") {
        long long checked = 0, relocated = 0;
        for (int t = 0; t < 30; ++t) {
            int H = 5 + rnd() % 12, W = 5 + rnd() % 12;
            load(H, W, 250 + rnd() % 300, 100 + t);
            ent::init();
            assert(ent::G.e0 == ent::entropyPairs() && ent::G.e0 == rE0);
            for (int k = 0; k < 300; ++k) {
                int i = rnd() % ent::G.n, d = rnd() % 4, y = ent::G.py[i], x = ent::G.px[i];
                if (!ent::canMove(y, x, d)) continue;
                long long before = ent::entropyPairs(), pred = ent::delta(y, x, d);
                int ny = y + ent::DY[d], nx = x + ent::DX[d];
                teleport(i, ny, nx);
                assert(ent::entropyPairs() - before == pred);
                teleport(i, y, x);
                ++checked;
#ifdef HAS_RELOC
                int by = rnd() % H, bx = rnd() % W;
                if (!ent::G.occ[by][bx]) {
                    ent::buildPre(); ent::buildF();
                    long long p2 = ent::relocateDelta(y, x, by, bx);
                    teleport(i, by, bx);
                    assert(ent::entropyPairs() - before == p2);
                    teleport(i, y, x);
                    ent::buildPre();
                    ++relocated;
                }
#endif
                // random real move so the cumulative sums are exercised in many states
                if (rnd() % 3 == 0) { ent::act(i, d); }
            }
            ent::buildPre();
            assert(ent::entropyAxis() == ent::entropyPairs());
        }
        printf("DELTA OK single=%lld relocate=%lld\n", checked, relocated);
    } else if (mode == "shift") {
#ifdef HAS_SHIFT
        long long pairs = 0, moves = 0;
        for (int t = 0; t < 40; ++t) {
            int H = 5 + rnd() % 12, W = 5 + rnd() % 12;
            load(H, W, 150 + rnd() % 650, 300 + t);
            ent::init();
            if (ent::G.n == 0 || ent::G.n == H * W) continue;
            for (int i = 0; i < ent::G.n; ++i) ent::who[ent::G.py[i]][ent::G.px[i]] = i;
            for (int k = 0; k < 60; ++k) {
                int ay, ax, by, bx;
                do { ay = rnd() % H; ax = rnd() % W; } while (!rg[ay][ax]);
                do { by = rnd() % H; bx = rnd() % W; } while (rg[by][bx]);
                static bool want[180][180];
                memcpy(want, rg, sizeof rg);
                want[ay][ax] = false; want[by][bx] = true;
                long long used0 = rUsed;
                rIn = true;
                bool ok = ent::shiftAlong(ay, ax, by, bx);
                rIn = false;
                assert(ok && memcmp(want, rg, sizeof rg) == 0);                       // only a emptied and b filled
                assert(rUsed - used0 == abs(ay - by) + abs(ax - bx));                  // exactly |a - b| moves
                assert(ent::G.entropy == refEntropy() && ent::G.mismatch == 0 && ent::G.refused == 0);
                for (int y = 0; y < H; ++y) for (int x = 0; x < W; ++x) assert(ent::G.occ[y][x] == rg[y][x]);
                ++pairs; moves += rUsed - used0;
            }
        }
        printf("SHIFT OK pairs=%lld moves=%lld\n", pairs, moves);
        load(1, 4, 0, 1);                           // the lesson's trace: 1 0 1 0 -> 0 0 1 1
        rg[0][0] = rg[0][2] = true; rLimit = 160; rUsed = 0; rLogN = 0;
        ent::init();
        for (int i = 0; i < ent::G.n; ++i) ent::who[ent::G.py[i]][ent::G.px[i]] = i;
        bool ok = ent::shiftAlong(0, 0, 0, 3);
        printf("SHIFT TRACE ok=%d moves=%d", ok, rLogN);
        for (int i = 0; i < rLogN; ++i) printf(" %d,%d,%d", rLog[i][0], rLog[i][1], rLog[i][2]);
        printf(" final=%d%d%d%d\n", rg[0][0], rg[0][1], rg[0][2], rg[0][3]);
#endif
    } else if (mode == "hand") {
        load(4, 5, 0, 1);
        memset(rg, 0, sizeof rg);
        static const int pts[5][2] = {{0, 0}, {0, 4}, {3, 0}, {3, 4}, {1, 2}};
        for (auto& p : pts) rg[p[0]][p[1]] = true;
        rLimit = (long long)rH * rW * 40; rUsed = 0; rE0 = refEntropy();
        ent::init();
        printf("HAND E0 %lld %lld %lld LIMIT %lld\n", rE0, ent::entropyPairs(), ent::G.e0, rLimit);
        auto find = [&](int y, int x) { for (int i = 0; i < ent::G.n; ++i) if (ent::G.py[i] == y && ent::G.px[i] == x) return i; return -1; };
        rIn = true;
        bool a = ent::act(find(0, 0), 1);
        printf("HAND STEP1 ok=%d entropy=%lld pairs=%lld refused=%d\n", a, ent::G.entropy, ent::entropyPairs(), ent::G.refused);
        moveParticle(0, 4, 1); ++ent::G.used;      // out of the grid: fails but is counted
        bool c = ent::act(find(3, 0), 0);
        rIn = false;
        printf("HAND STEP3 ok=%d entropy=%lld pairs=%lld used=%lld rused=%lld\n", c, ent::G.entropy, ent::entropyPairs(), ent::G.used, rUsed);
        long long e = refEntropy();
        printf("HAND SCORES my=%lld ref=%lld direct=%lld\n", ent::myScore(rE0, e, rUsed, rLimit), refScore(rE0, e), ent::myScore(42, 38, 3, 800));
    }
}
'''


def build_ref(code: str, folder: Path, name: str, extra: list[str]) -> Path:
    src, exe = folder / f"{name}.cpp", folder / name
    src.write_text(code + "\n" + REF)
    compile_to(exe, [src], extra + (["-DHAS_RELOC"] if "relocateDelta" in code else []) + (["-DHAS_SHIFT"] if "shiftAlong" in code else []))
    return exe


def parse_ref(text: str) -> dict:
    score = {int(a): int(b) for a, b in re.findall(r"^TC (\d+) SCORE (-?\d+)$", text, re.M)}
    mirror = {int(m[0]): tuple(map(int, m[1:])) for m in re.findall(
        r"^TC (\d+) MIRROR (-?\d+) (-?\d+) (-?\d+) (-?\d+) (\d+) (\d+)$", text, re.M)}
    ref = {int(m[0]): tuple(map(int, m[1:])) for m in re.findall(r"^TC (\d+) REF (-?\d+) (-?\d+) (-?\d+)$", text, re.M)}
    return {"score": score, "mirror": mirror, "ref": ref}


SMALL = ["8:9:400:1", "5:5:500:2", "13:7:300:3", "12:12:450:4", "6:14:350:5", "10:10:400:6"]
CHAIN = ["8:9:400:1", "5:5:500:2", "12:12:300:3", "8:9:400:1"]
FAILURES = {
    "쌍을 두 번 센다": [(r"for \(int j = i \+ 1; j < G\.n; \+\+j\)", "for (int j = 0; j < G.n; ++j)")],
    "int 누적": [(r"long long e = 0;\n    for \(int r = 0; r \+ 1 < G\.H", "int e = 0;\n    for (int r = 0; r + 1 < G.H"),
               (r"e \+= \(long long\)G\.preY\[r\]", "e += G.preY[r]"),
               (r"e \+= \(long long\)G\.preX\[c\]", "e += G.preX[c]")],
    "위쪽 차분 off-by-one": [(r"if \(dir == 0\) return n - 1 - 2LL \* \(y > 0 \? G\.preY\[y - 1\] : 0\);",
                          "if (dir == 0) return n - 1 - 2LL * G.preY[y];")],
}


FAILURES5 = {
    "번호 표 갱신 누락": [(r"            who\[cy\[i \+ 1\]\]\[cx\[i \+ 1\]\] = p;\n", "")],
}


def hungarian(cost: list[list[int]]) -> int:
    """Minimum assignment cost (e-maxx O(n^3) Hungarian method) for a square matrix."""
    n, inf = len(cost), 10 ** 18
    u, v, p, way = [0] * (n + 1), [0] * (n + 1), [0] * (n + 1), [0] * (n + 1)
    for i in range(1, n + 1):
        p[0], j0 = i, 0
        minv, used = [inf] * (n + 1), [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], inf, 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
    return -v[0]


def parse_grids(text: str) -> dict[tuple[int, str], list[tuple[int, int]]]:
    lines, grids, i = text.splitlines(), {}, 0
    while i < len(lines):
        m = re.fullmatch(r"TC (\d+) GRID ([IF]) (\d+) (\d+)", lines[i])
        if m:
            h = int(m.group(3))
            grids[(int(m.group(1)), m.group(2))] = [(y, x) for y, row in enumerate(lines[i + 1:i + 1 + h]) for x, ch in enumerate(row) if ch == "#"]
            i += h
        i += 1
    return grids


def pair_sum(pts: list[tuple[int, int]]) -> int:
    return sum(abs(a[0] - b[0]) + abs(a[1] - b[1]) for i, a in enumerate(pts) for b in pts[i + 1:])


def margin_bound(a: list[tuple[int, int]], b: list[tuple[int, int]], h: int, w: int) -> int:
    """Each move crosses one row or column boundary, so |prefix count difference| summed over boundaries is a lower bound."""
    total = 0
    for axis, size in ((0, h), (1, w)):
        for c in range(size):
            total += abs(sum(p[axis] <= c for p in a) - sum(p[axis] <= c for p in b))
    return total


def check_plan(exe: Path) -> list[float]:
    """Stage 5 on small instances, checked independently in Python: entropies, move lower bounds, self-consistent target."""
    text = run(exe, "run", *SMALL)
    out, grids, ratios = parse_ref(text), parse_grids(text), []
    for k, spec in enumerate(SMALL, 1):
        h, w = map(int, spec.split(":")[:2])
        a, b = grids[(k, "I")], grids[(k, "F")]
        m, e0, e, used, _, _ = out["mirror"][k]
        assert len(a) == len(b) and (e0, e) == (pair_sum(a), pair_sum(b)), (k, e0, e)
        lb = margin_bound(a, b, h, w)
        emd = hungarian([[abs(p[0] - q[0]) + abs(p[1] - q[1]) for q in b] for p in a])
        assert lb <= emd <= used, (k, lb, emd, used)               # no sequence of moves can beat the transport cost
        # the final layout must be a self-consistent target: its n cells have the smallest F-keys of the layout itself
        fy = [sum(abs(r - q[0]) for q in b) for r in range(h)]
        fx = [sum(abs(c - q[1]) for q in b) for c in range(w)]
        inside = {q for q in b}
        worst_in = max(fy[q[0]] + fx[q[1]] for q in b)
        best_out = min(fy[y] + fx[x] for y in range(h) for x in range(w) if (y, x) not in inside)
        assert worst_in <= best_out, (k, worst_in, best_out)
        ratios.append(used / emd)
    return ratios


def check_reference(sn: dict[str, str]) -> dict:
    extra: dict = {}
    with tempfile.TemporaryDirectory(prefix="lesson-entropy-") as tmp:
        folder = Path(tmp)
        with concurrent.futures.ThreadPoolExecutor() as pool:
            exes = list(pool.map(lambda s: build_ref(assemble(s, sn), folder, f"stage{s}", SAN + (["-DLOCAL_OPT"] if s in (2, 3) else [])), STAGES))
            big = pool.submit(build_ref, assemble(0, sn), folder, "big", ["-O2"])
            bad = {name: pool.submit(build_ref, assemble(4, sn, edits), folder, f"bad{k}", ["-O1"])
                   for k, (name, edits) in enumerate(FAILURES.items())}
            bad_san = pool.submit(build_ref, assemble(4, sn, FAILURES["int 누적"]), folder, "badsan", SAN)
            bad5 = {name: pool.submit(build_ref, assemble(5, sn, edits), folder, f"bad5{k}", SAN)
                    for k, (name, edits) in enumerate(FAILURES5.items())}
        for s in STAGES:     # the submission-style composition must also be warning free
            done = subprocess.run(["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", "-x", "c++", "-"],
                                  input=assemble(s, sn), text=True, capture_output=True)
            assert done.returncode == 0, done.stderr[:500]
        for s, exe in zip(STAGES, exes):
            out = parse_ref(run(exe, "run", *SMALL))
            assert len(out["score"]) == len(SMALL)
            for tc, real in out["score"].items():
                m, e0, e, used, refused, mismatch = out["mirror"][tc]
                r_e0, r_e, r_used = out["ref"][tc]
                assert (m, e0, e, used) == (real, r_e0, r_e, r_used) and (refused == 0 or s == 1) and mismatch == 0, (s, tc, out["mirror"][tc], real)
            chain = parse_ref(run(exe, "run", *CHAIN))["score"]
            assert chain[1] == chain[4], (s, chain)
            print(f"OK: stage {s} ({STAGES[s][0]}): mirror == reference grader on {len(SMALL)} instances"
                  f"{', no legal single move lowers the entropy at the end' if s in (2, 3) else ''}, "
                  f"mismatch 0 (refused {'only in the pushing stage' if s == 1 else 0}), chained TC reproduces ({chain[1]})")
        stage4 = exes[4]
        out = run(stage4, "delta")
        assert out.strip() == "DELTA OK single=4861 relocate=3049", out
        print("OK:", out.strip(), "(single-step and relocation differences equal full recomputation)")
        out = run(exes[5], "shift")
        m = re.search(r"^SHIFT OK pairs=(\d+) moves=(\d+)$", out, re.M)
        assert m and int(m.group(1)) >= 2000, out
        assert "SHIFT TRACE ok=1 moves=3 0,0,1 0,2,1 0,1,1 final=0011" in out, out     # the lesson's 1 0 1 0 example
        print(f"OK: shiftAlong on {m.group(1)} random pairs: only a emptied and b filled, exactly |a - b| moves ({m.group(2)} in all), "
              "mirror == reference at every call; the 1 0 1 0 trace is 3 moves")
        ratios = check_plan(exes[5])
        print("OK: stage 5 on small instances: entropies == pair sums, margin bound <= optimal transport (Hungarian) <= moves used "
              f"(moves / transport {min(ratios):.2f}~{max(ratios):.2f}), final layout is its own lowest-F-key set")
        extra["plan_ratio_max"] = max(ratios)
        for name, fut in bad5.items():
            # A stale particle table moves the wrong particle, but the mirror records that same move, so the
            # entropy comparison still passes. The shift test catches it: after shiftAlong(a, b) only a may
            # be emptied and only b filled. (Running a full TC fails only when the stale index is out of range.)
            try:
                run(fut.result(), "shift")
                raise AssertionError(f"{name} must be detected")
            except subprocess.CalledProcessError:
                pass
            print(f"OK: failure '{name}': shiftAlong no longer empties only a and fills only b")
        out = run(big.result(), "big")
        m = re.fullmatch(r"BIG n=(\d+) mirror=(\d+) pairs=(\d+) ref=(\d+)\n?", out)
        assert m and m.group(2) == m.group(3) == m.group(4) and int(m.group(4)) > 2 ** 31, out
        print(f"OK: 180x180 instance n={m.group(1)}: axis form == pair sum == reference = {m.group(2)} (> 2^31)")
        # 1) doubled pair sum: the score is unchanged (it is a ratio) but the entropy value is not
        exe = bad["쌍을 두 번 센다"].result()
        base = parse_ref(run(exes[4], "run", *SMALL))["score"]
        assert parse_ref(run(exe, "run", *SMALL))["score"] == base, "a doubled entropy leaves the ratio-based score alone"
        try:
            run(exe, "delta")
            raise AssertionError("doubled pair sum must break the entropy comparison")
        except subprocess.CalledProcessError:
            pass
        print("OK: failure '쌍을 두 번 센다': scores are identical to the correct code, the entropy comparison fails")
        # 2) int accumulation: wrong value on the 180x180 instance, and UBSan traps the signed overflow
        exe = bad["int 누적"].result()
        m = re.fullmatch(r"BIG n=(\d+) mirror=(-?\d+) pairs=(\d+) ref=(\d+)\n?", run(exe, "big"))
        assert m and not (m.group(2) == m.group(3) == m.group(4)), "int accumulation should give a wrong value"
        assert subprocess.run([str(bad_san.result()), "big"], capture_output=True).returncode != 0, "UBSan should trap"
        print("OK: failure 'int 누적': the 180x180 entropy is wrong and UBSan aborts on the signed overflow")
        # 3) off-by-one difference: the mirror leaves the real state at the next call
        exe = bad["위쪽 차분 off-by-one"].result()
        try:
            run(exe, "run", *SMALL)
            raise AssertionError("off-by-one difference must be detected")
        except subprocess.CalledProcessError:
            pass
        print("OK: failure '위쪽 차분 off-by-one': the mirror entropy differs from the reference before the next call")
    return extra


def check_hand(sn: dict[str, str]) -> dict:
    with tempfile.TemporaryDirectory(prefix="lesson-entropy-hand-") as tmp:
        exe = build_ref(assemble(4, sn), Path(tmp), "hand", SAN)
        out = run(exe, "hand")
    # values written by hand in the lesson
    assert "HAND E0 42 42 42 LIMIT 800" in out, out
    assert "HAND STEP1 ok=1 entropy=40 pairs=40 refused=0" in out, out
    assert "HAND STEP3 ok=1 entropy=38 pairs=38 used=3 rused=3" in out, out
    assert "HAND SCORES my=9077 ref=9077 direct=9077" in out, out
    # independent Python recomputation of the same numbers
    def pairs(pts):
        return sum(abs(a[0] - b[0]) + abs(a[1] - b[1]) for i, a in enumerate(pts) for b in pts[i + 1:])
    def cuts(vals, size):
        n = len(vals)
        pre = [sum(v <= c for v in vals) for c in range(size)]
        return [pre[c] * (n - pre[c]) for c in range(size - 1)]
    pts = list(HAND_POINTS)
    assert pairs(pts) == 42
    assert cuts([p[1] for p in pts], HAND_W) == [6, 6, 6, 6] and cuts([p[0] for p in pts], HAND_H) == [6, 6, 6]
    pts[0] = (0, 1)
    assert pairs(pts) == 40
    pts[2] = (2, 0)
    assert pairs(pts) == 38
    ratio = (42 - 38) / 42
    doubled = ((2 * 42 - 2 * 38) / (2 * 42))
    assert doubled == ratio or abs(doubled - ratio) < 1e-15    # doubling E0 and E leaves the ratio, hence the score
    assert int(1e6 * ratio * ratio) == 9070 and (800 - 3) // 100 == 7 and round((800 - 3) / 100) == 8
    # per-step differences quoted in the lesson
    n = 5
    assert 2 * 2 - 1 - n == -2 and n - 1 - 2 * 3 == -2
    print("OK: hand example (42 -> 40 -> 38, 3 calls, 9070 + 7 = 9077) recomputed by the lesson code and in Python")
    return {"score": 9077}


# ---------------------------------------------------------------- bounds and references
def axis_lower(n: int, cap: int) -> int:
    m = -(-n // cap)
    return sum(j * cap * (n - j * cap) for j in range(1, m))


def axis_lower_exact(n: int, cap: int, size: int) -> int:
    best = None

    def rec(c: int, pre: int, acc: int) -> None:
        nonlocal best
        if c == size - 1:
            if pre <= n <= pre + cap:
                total = acc
                best = total if best is None or total < best else best
            return
        for take in range(0, cap + 1):
            if pre + take <= n:
                rec(c + 1, pre + take, acc + (pre + take) * (n - pre - take))
    rec(0, 0, 0)
    return best


def disk_reference(n: int, H: int, W: int) -> int | None:
    """Entropy of the n cells nearest to a centre, best over the four centre offsets; None if it does not fit."""
    best = None
    for oy in (0.0, 0.5):
        for ox in (0.0, 0.5):
            r = int(math.sqrt(n / math.pi)) + 4
            cells = [(y, x) for y in range(-r, r + 1) for x in range(-r, r + 1)]
            cells.sort(key=lambda p: ((p[0] - oy) ** 2 + (p[1] - ox) ** 2, p))
            cells = cells[:n]
            ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
            if max(ys) - min(ys) + 1 > H or max(xs) - min(xs) + 1 > W:
                continue
            e = 0
            for vals in (sorted(ys), sorted(xs)):
                e += sum((2 * k - n + 1) * v for k, v in enumerate(vals))
            best = e if best is None or e < best else best
    return best


def check_bounds() -> None:
    for n in range(2, 9):
        for cap in range(1, 5):
            for size in range(-(-n // cap), 7):
                assert axis_lower(n, cap) == axis_lower_exact(n, cap, size), (n, cap, size)
    print("OK: the full-column lower bound equals an exhaustive minimum over column counts on small cases")


def tc_reference(info: dict) -> dict:
    n, H, W = info["n"], info["H"], info["W"]
    return {"lower": axis_lower(n, H) + axis_lower(n, W), "disk": disk_reference(n, H, W)}


# ---------------------------------------------------------------- public grader
def patched_judge(judge: Path, folder: Path, hand: bool = False) -> Path:
    text = judge.read_text()

    def once(old: str, new: str) -> None:
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new)

    if not hand:     # the hand run uses a three-call process() without the mirror
        once("static long long sInitialEntropy, sEntropy, sTotalScore;",
             "static long long sInitialEntropy, sEntropy, sTotalScore;\n"
             "namespace ent { extern void (*hook)(long long, long long, long long, long long, int, int); }\n"
             "static int gTcNow;\n"
             "static void logHook(long long s, long long e0, long long e, long long u, int r, int m) {\n"
             "    printf(\"TC %d MIRROR %lld %lld %lld %lld %d %d\\n\", gTcNow, s, e0, e, u, r, m); }")
        once("        process();", "        gTcNow = tc + 1; ent::hook = logHook;\n        process();")
        # move lower bound from the grader's own grids (measurement only): sum over row/column boundaries of
        # |particles before the boundary now - at the start|; one move crosses exactly one boundary
        once("static int sPy[MAX_HW * MAX_HW], sPx[MAX_HW * MAX_HW];",
             "static int sPy[MAX_HW * MAX_HW], sPx[MAX_HW * MAX_HW];\n"
             "static long long sLbY0[MAX_HW], sLbX0[MAX_HW];\n"
             "static void lbCount(long long* ry, long long* rx) {\n"
             "    for (int i = 0; i < MAX_HW; i++) ry[i] = rx[i] = 0;\n"
             "    for (int y = 0; y < sH; y++) for (int x = 0; x < sW; x++) if (sUniverse[y][x]) { ry[y]++; rx[x]++; }\n"
             "    for (int i = 1; i < MAX_HW; i++) { ry[i] += ry[i - 1]; rx[i] += rx[i - 1]; }\n}\n"
             "static long long lbNow() {\n"
             "    long long ry[MAX_HW], rx[MAX_HW], s = 0; lbCount(ry, rx);\n"
             "    for (int i = 0; i < MAX_HW; i++) { s += ry[i] > sLbY0[i] ? ry[i] - sLbY0[i] : sLbY0[i] - ry[i];\n"
             "                                       s += rx[i] > sLbX0[i] ? rx[i] - sLbX0[i] : sLbX0[i] - rx[i]; }\n"
             "    return s;\n}")
        once("    sInitialEntropy = calc_entropy();\n}", "    sInitialEntropy = calc_entropy();\n    lbCount(sLbY0, sLbX0);\n}")
    once("        printf(\"TC %d SCORE: %lld\\n\", tc + 1, score);",
         "        printf(\"TC %d SCORE: %lld\\n\", tc + 1, score);\n"
         "        printf(\"TC %d INFO %d %d %d %lld %lld %lld\\n\", tc + 1, sH, sW, sParticleCount, sInitialEntropy, sEntropy, sMoveCount);"
         + ("" if hand else "\n        printf(\"TC %d LB %lld\\n\", tc + 1, lbNow());"))
    if hand:
        start, stop = text.index("static void init()"), text.index("int getHeight()")
        text = text[:start] + (
            "static void init()\n{\n    sH = 4; sW = 5; sParticleCount = 5;\n"
            "    for (int y = 0; y < sH; y++) for (int x = 0; x < sW; x++) sUniverse[y][x] = 0;\n"
            "    sUniverse[0][0] = sUniverse[0][4] = sUniverse[3][0] = sUniverse[3][4] = sUniverse[1][2] = 1;\n"
            "    sMoveCount = 0; sMoveLimit = (long long)sH * sW * 40; sInitialEntropy = calc_entropy();\n}\n\n") + text[stop:]
        once("    for (int tc = 0; tc < MAX_TC; tc++) {", "    for (int tc = 0; tc < 1; tc++) {")
    path = folder / ("judge_hand.cpp" if hand else "judge_patched.cpp")
    path.write_text(text)
    return path


def parse_judge(text: str) -> dict:
    score = {int(a): int(b) for a, b in re.findall(r"^TC (\d+) SCORE: (-?\d+)$", text, re.M)}
    mirror = {int(m[0]): tuple(map(int, m[1:])) for m in re.findall(
        r"^TC (\d+) MIRROR (-?\d+) (-?\d+) (-?\d+) (-?\d+) (\d+) (\d+)$", text, re.M)}
    info = {int(m[0]): tuple(map(int, m[1:])) for m in re.findall(
        r"^TC (\d+) INFO (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)$", text, re.M)}
    lb = {int(a): int(b) for a, b in re.findall(r"^TC (\d+) LB (\d+)$", text, re.M)}
    ratio = [int(v) for v in re.findall(r"^RATIO (-?\d+)$", text, re.M)]
    total = re.search(r"^SCORE: (\d+)$", text, re.M)
    ms = re.search(r"^Result : (\d+) ms$", text, re.M)
    return {"score": score, "mirror": mirror, "info": info, "lb": lb, "ratio": ratio,
            "total": int(total.group(1)) if total else sum(score.values()), "ms": int(ms.group(1)) if ms else None}


def judge_run(judge_src: Path, code: str, folder: Path, name: str, flags: list[str], repeat: int = 1, timeout: int = 400) -> dict:
    user = folder / f"{name}.cpp"
    exe = folder / name
    user.write_text(code)
    compile_to(exe, [judge_src, user], flags)
    results = [parse_judge(run(exe, timeout=timeout)) for _ in range(repeat)]
    first = results[0]
    assert all(r["score"] == first["score"] for r in results)
    first["ms_runs"] = [r["ms"] for r in results]
    first["ms"] = int(statistics.median(first["ms_runs"]))
    return first


def row_from(label: str, r: dict) -> dict:
    tcs = sorted(r["score"])
    mirror = [r["mirror"][t] for t in tcs]
    return {"label": label, "total": r["total"], "tcs": [r["score"][t] for t in tcs],
            "mirror_total": sum(m[0] for m in mirror), "refused_total": sum(m[4] for m in mirror),
            "mismatch_total": sum(m[5] for m in mirror),
            "entropy": [m[2] for m in mirror], "used": [m[3] for m in mirror],
            "lb": [r["lb"][t] for t in tcs], "ratio": r["ratio"],
            "ms": r["ms"], "ms_runs": r["ms_runs"]}


def check_hand_judge(judge: Path, sn: dict[str, str]) -> None:
    with tempfile.TemporaryDirectory(prefix="lesson-entropy-handjudge-") as tmp:
        folder = Path(tmp)
        src = patched_judge(judge, folder, hand=True)
        user = folder / "hand_user.cpp"
        user.write_text(sn["ent-hand"])
        exe = folder / "hand"
        compile_to(exe, [src, user], ["-O2"])
        out = run(exe)
    assert re.search(r"^TC 1 SCORE: 9077$", out, re.M), out
    print("OK: the public grader on the 4x5 hand layout gives 9077 (hand value, myScore, grader all equal)")


SWEEPS = [("KEEP", ["4", "7"]), ("MINPER", ["1", "100", "300"])]
ARR5 = STAGES[5][1][len(COMMON):]
BASE5 = f"5단계 {STAGES[5][0]}"
# edits that turn the stage 5 code into the variants of the on/off table (the lesson text keeps the plain code)
GATE_PRE = """double minRatio = 1e18;
void fillHoles() {
    long long eR = 0;
    for (int pre = 0, r = 0; r + 1 < G.H; ++r) { pre += cntY[r]; eR += (long long)pre * (G.n - pre); }
    for (int pre = 0, c = 0; c + 1 < G.W; ++c) { pre += cntX[c]; eR += (long long)pre * (G.n - pre); }
    double mu = 0.01 * G.e0 / (2e6 * (1.0 - (double)eR / G.e0));      // score value of one move in entropy units
"""
GATE_SHIFT = """{ int d0 = absv(fy - hy) + absv(fx - hx);
            double g = gy[fy] + gx[fx] - gy[hy] - gx[hx] + d0;        // entropy decrease of this pair
            if (g / d0 < minRatio) minRatio = g / d0;
            if (g >= mu * d0) shiftAlong(fy, fx, hy, hx); }"""
def ablations() -> list[tuple[str, int, tuple[str, ...] | None, list]]:
    gate = [(r"void fillHoles\(\) \{\n", lambda m: GATE_PRE), (r"shiftAlong\(fy, fx, hy, hx\);", lambda m: GATE_SHIFT),
            (r"void process\(\) \{\n    ent::init\(\);", lambda m: "#include <cstdio>\nvoid process() {\n    ent::init();\n    ent::minRatio = 1e18;"),
            (r"ent::finish\(\);", lambda m: 'ent::finish();\n    printf("RATIO %lld\\n", (long long)ent::minRatio);')]
    per_hole = [(r"    for \(int d = 1; d <= G\.H \+ G\.W; \+\+d\)\n        for \(int hy = 0; hy < G\.H; \+\+hy\) for \(int hx = 0; hx < G\.W; \+\+hx\) \{\n([^\n]*\n)",
                 lambda m: "        for (int hy = 0; hy < G.H; ++hy) for (int hx = 0; hx < G.W; ++hx) {\n" + m.group(1) + "            for (int d = 1; d <= G.H + G.W; ++d) {\n"),
                (r"            if \(fy >= 0\) shiftAlong\(fy, fx, hy, hx\);\n        \}",
                 lambda m: "            if (fy >= 0) { shiftAlong(fy, fx, hy, hx); break; }\n            }\n        }")]
    out = [("ROUNDS 1", 5, None, with_const("ROUNDS", "1")),
           ("빈 칸 순서대로 짝짓기", 5, None, per_hole),
           ("3단계를 먼저 실행", 5, COMMON + ("ent-greedy",) + ARR5, [(r"ent::init\(\);", lambda m: "ent::init();\n    ent::thresholdSweeps();")]),
           ("문턱 켬", 5, None, gate),
           ("4단계 TC별 문턱 ×10", 4, None,
            [(r"const long long MINPER = 10;", lambda m: "long long MINPER = 10;"),
             (r"ent::init\(\);", lambda m: "ent::init();\n    ent::MINPER = (long long)(10 * 0.01 * ent::G.e0 / (2e6 * 0.43)) + 1;")])]
    return out


def measure(judge: Path, sn: dict[str, str]) -> dict:
    result = {"date": datetime.date.today().isoformat(), "platform": platform.platform(), "machine": platform.machine(),
              "compiler": subprocess.run(["c++", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
              "flags": "-std=c++17 -O2", "judge_sha256": hashlib.sha256(judge.read_bytes()).hexdigest(),
              "rows": [], "sweeps": [], "failures": [], "ablations": [], "tcs": []}
    with tempfile.TemporaryDirectory(prefix="lesson-entropy-judge-") as tmp:
        folder = Path(tmp)
        src = patched_judge(judge, folder)

        def record(label: str, stage: int, edits=None, repeat=1, bucket="rows", timeout=400, blocks=None):
            r = judge_run(src, assemble(stage, sn, edits, blocks), folder, "m", ["-O2"], repeat, timeout)
            row = row_from(label, r)
            result[bucket].append(row)
            print(json.dumps({k: row[k] for k in ("label", "total", "mirror_total", "mismatch_total", "ms")}, ensure_ascii=False), flush=True)
            return r
        for s, (label, _) in STAGES.items():
            r = record(f"{s}단계 {label}", s, repeat=9)
            if s == 0:
                result["tcs"] = [{"tc": t, "H": r["info"][t][0], "W": r["info"][t][1], "n": r["info"][t][2],
                                  "e0": r["info"][t][3], "limit": r["info"][t][0] * r["info"][t][1] * 40} for t in sorted(r["info"])]
        for name, values in SWEEPS:
            for v in values:
                record(f"{name} {v}", 4, with_const(name, v), bucket="sweeps")
        record("MINPER 0", 4, with_const("MINPER", "0"), bucket="failures", timeout=600)
        for name in ("int 누적", "위쪽 차분 off-by-one"):    # the doubled pair sum never reaches the score
            record(name, 4, FAILURES[name], bucket="failures", timeout=600)
        for label, stage, blocks, edits in ablations():
            record(label, stage, edits, bucket="ablations", timeout=600, blocks=blocks)
        for s in STAGES:         # sanitizer pass on the public grader
            judge_run(src, assemble(s, sn), folder, "san", SAN, timeout=900)
        result["sanitizer"] = "0~5단계가 공개 채점기에서 ASan+UBSan을 통과"
        for t in result["tcs"]:
            t.update(tc_reference(t))
    return result


def table_lines(data: dict) -> dict[str, list[str]]:
    """The measured tables of the lesson, generated from the stored JSON (the lesson must contain them verbatim)."""
    by = {r["label"]: r for r in data["rows"] + data["sweeps"] + data["failures"] + data["ablations"]}
    limit_sum = sum(t["limit"] for t in data["tcs"])
    out: dict[str, list[str]] = {k: [] for k in ("stage_rows", "tc_rows", "ref_rows", "sweep_rows", "fail_rows", "abl_rows")}
    for r in data["rows"]:
        out["stage_rows"].append(f"| {r['label']} | {r['total']} | {r['ms']} | {sum(r['used'])} / {limit_sum} |")
        out["tc_rows"].append(f"| {r['label']} | " + " | ".join(map(str, r["tcs"])) + " |")
    r4, r5 = by["4단계 빈 칸 경로 재배치"], by[BASE5]
    for i, t in enumerate(data["tcs"]):
        e = r4["entropy"][i]
        out["ref_rows"].append(f"| {t['tc']} | {t['H']} × {t['W']} | {t['n']} | {t['e0']} | {e} | {1 - e / t['e0']:.4f} "
                               f"| {1 - t['disk'] / t['e0']:.4f} | {1 - t['lower'] / t['e0']:.4f} "
                               f"| {r5['used'][i]} | {r5['lb'][i]} |")
    out["sweep_rows"].append(f"| 기본값 (MINPER 10, KEEP 6) | {r4['total']} | {r4['ms']} |")
    for label in ("MINPER 100", "MINPER 300"):
        out["sweep_rows"].append(f"| {label} | {by[label]['total']} | {by[label]['ms']} |")
    for label in ("int 누적", "위쪽 차분 off-by-one"):
        out["fail_rows"].append(f"| {label} | {by[label]['total']} | {by[label]['mirror_total']} | {by[label]['ms']} |")
    out["abl_rows"].append(f"| 5단계 전체 | {r5['total']} | {sum(r5['used'])} | {r5['ms']} | |")
    for r in data["ablations"]:
        d = paired(by, r["label"], BASE5)
        out["abl_rows"].append(f"| {r['label']} | {r['total']} | {sum(r['used'])} | {r['ms']} | {d['mean']:.1f} ({d['err']:.1f}) |")
    return out


def paired(by: dict, a: str, b: str) -> dict:
    diff = [x - y for x, y in zip(by[a]["tcs"], by[b]["tcs"])]
    mean, err = statistics.mean(diff), statistics.stdev(diff) / len(diff) ** 0.5
    return {"mean": mean, "err": err, "lo": mean - 2 * err, "hi": mean + 2 * err, "wins": sum(d > 0 for d in diff)}


def check_tables(data: dict) -> None:
    text = read_lesson_text(LESSON_ID)
    lines = set(text.splitlines())
    for name, expected in table_lines(data).items():
        for line in expected:
            assert line in lines, f"lesson table line missing or stale ({name}): {line}"
    by = {r["label"]: r for r in data["rows"] + data["sweeps"] + data["failures"] + data["ablations"]}
    for row in data["rows"]:
        assert row["mirror_total"] == row["total"] and row["mismatch_total"] == 0 and (row["refused_total"] == 0 or row["label"].startswith("1단계")), row["label"]
    for t in data["tcs"]:
        assert tc_reference(t) == {"lower": t["lower"], "disk": t["disk"]}, t["tc"]
        assert t["disk"] >= t["lower"], t["tc"]
    r2, r3, r4, r5 = (by[k] for k in ("2단계 차분 탐욕", "3단계 큰 이득부터", "4단계 빈 칸 경로 재배치", BASE5))
    base = "4단계 빈 칸 경로 재배치"
    assert r4["total"] < PASS_SCORE <= r5["total"]
    limit_sum = sum(t["limit"] for t in data["tcs"])
    assert round(100 * sum(r2["used"]) / limit_sum) == round(100 * sum(r3["used"]) / limit_sum) == 26
    assert sum(t["e0"] > 2 ** 31 - 1 for t in data["tcs"]) == 4 and all(t["e0"] > 2 ** 31 - 1 for t in data["tcs"] if t["tc"] in (4, 5, 9, 10))
    ratio = [1 - e / t["e0"] for e, t in zip(r4["entropy"], data["tcs"])]
    thr = [0.01 * t["e0"] / (2e6 * r) for r, t in zip(ratio, data["tcs"])]
    thr5 = [0.01 * t["e0"] / (2e6 * (1 - e / t["e0"])) for e, t in zip(r5["entropy"], data["tcs"])]
    q = [r4["entropy"][i] / t["disk"] for i, t in enumerate(data["tcs"])]
    low = [1 - t["lower"] / t["e0"] for t in data["tcs"]]
    sweeps = [paired(by, a, b) for a, b in (("3단계 큰 이득부터", "2단계 차분 탐욕"), ("4단계 빈 칸 경로 재배치", "3단계 큰 이득부터"))]
    s45 = paired(by, BASE5, base)
    cmp = {k: paired(by, k, base) for k in ("MINPER 0", "MINPER 1", "MINPER 100", "MINPER 300", "KEEP 4", "KEEP 7")}
    cmp["300/100"] = paired(by, "MINPER 300", "MINPER 100")
    abl = {r["label"]: paired(by, r["label"], BASE5) for r in data["ablations"]}
    x10 = paired(by, "4단계 TC별 문턱 ×10", base)
    assert sweeps[0]["lo"] < 0 < sweeps[0]["hi"] and sweeps[0]["wins"] == 4 and sweeps[1]["wins"] == 10 and s45["wins"] == 10 and s45["lo"] > 0
    assert cmp["MINPER 0"]["wins"] == cmp["MINPER 1"]["wins"] == 0 and cmp["MINPER 100"]["wins"] == 10
    assert cmp["300/100"]["lo"] < 0 < cmp["300/100"]["hi"] and cmp["KEEP 7"]["lo"] < 0 < cmp["KEEP 7"]["hi"]
    assert cmp["KEEP 4"]["hi"] < 0
    assert all(abl[k]["wins"] == 0 and abl[k]["hi"] < 0 for k in ("ROUNDS 1", "빈 칸 순서대로 짝짓기", "3단계를 먼저 실행", "4단계 TC별 문턱 ×10"))
    gate = by["문턱 켬"]
    assert gate["tcs"] == r5["tcs"] and gate["used"] == r5["used"] and gate["entropy"] == r5["entropy"]    # no pair is skipped
    assert x10["wins"] == 10 and r5["total"] - by["4단계 TC별 문턱 ×10"]["total"] > 0
    e45 = [a / b for a, b in zip(r5["entropy"], r4["entropy"])]
    lb_ratio = sum(r5["used"]) / sum(r5["lb"])
    assert all(u >= l for u, l in zip(r5["used"], r5["lb"])) and lb_ratio < 1.002
    gate_min = min(r / t for r, t in zip(gate["ratio"], thr5))
    spread = max(abs(by[k]["total"] - r4["total"]) for k in cmp if "/" not in k) / r4["total"]
    used = lambda k: sum(by[k]["used"]) - sum(r5["used"])
    needles = [data["date"], PASS_SCORE, f"{PASS_SCORE - r4['total']}점 부족", f"{r5['total'] - PASS_SCORE}점 넘",
               sum(r4["used"]), sum(r4["used"]) // 100, sum(r5["used"]), sum(r5["used"]) // 100, sum(r4["used"]) - sum(r5["used"]), sum(r5["lb"]), f"{lb_ratio:.3f}배",
               f"{min(r5['ms_runs'])}~{max(r5['ms_runs'])} ms", f"{min(e45):.6f}~{max(e45):.6f}배",
               f"{min(q):.5f}~{max(q):.5f}", f"{min(low):.3f}~{max(low):.3f}", f"{min(ratio):.2f}~{max(ratio):.2f}",
               f"약 {thr[0]:.1f}", f"약 {thr[-1]:.1f}", f"{r3['ms'] / r2['ms']:.1f}배", f"{spread * 100:.2f}%",
               f"{min(gate['ratio'])}~{max(gate['ratio'])}로", f"{gate_min:.1f}배 이상",
               f"{-used('ROUNDS 1')}번 줄지만", f"{used('빈 칸 순서대로 짝짓기')}번 늘어", f"{used('3단계를 먼저 실행')}번 늘어"]
    for key in ("mean", "err", "lo", "hi"):
        needles += [f"{sweeps[0][key]:.1f}", f"{sweeps[1][key]:.1f}", f"{s45[key]:.1f}"]
    for k, v in cmp.items():
        needles += [f"{v['mean']:.1f}"] + ([f"{v['err']:.1f}"] if k in ("MINPER 100", "MINPER 300", "300/100", "KEEP 4", "KEEP 7") else [])
    for k, v in list(abl.items()) + [("x10/4", x10)]:
        needles += [f"{v['mean']:.1f}", f"{v['err']:.1f}"]
    for n in needles:
        assert str(n) in text, f"number missing or stale in lesson: {n}"
    hub_rows = check_hub_summary(LESSON_ID, [(r["label"], r["total"]) for r in data["rows"]])
    print(f"OK: hub summary table matches the stored stage totals ({hub_rows} rows)")
    print(f"OK: lesson tables and quoted numbers match {DATA.name} "
          f"({sum(len(v) for v in table_lines(data).values())} table lines, {len(needles)} numbers, {len(text.splitlines())} lines)")


def check_svgs() -> None:
    text = read_lesson_text(LESSON_ID)
    svgs = sorted(p for p in ASSETS.glob("*.svg") if p.name in ("axis-split.svg", "one-move.svg"))  # 손으로 쓴 그림. 차트는 generate_charts.py --check가 검사
    assert len(svgs) == 2, svgs
    for svg in svgs:
        body = svg.read_text()
        assert 'role="img"' in body and "<title" in body and "<desc" in body and 'viewBox="0 0 720 ' in body, svg.name
        sizes = [float(s) for s in re.findall(r'font-size="([\d.]+)"', body)]
        assert sizes and min(sizes) >= 16 and max(sizes) <= 28, (svg.name, min(sizes), max(sizes))
        assert f"lesson-assets/{svg.name}" in text and f"https://git.readiz.com/h-contest-lesson/lessons/reading-the-score/lesson-assets/{svg.name}" in text, svg.name
    for alt in re.findall(r"!\[([^\]]*)\]\((?:\.\./)?lesson-assets/", text):
        assert "[" not in alt and "]" not in alt and len(alt) > 30
    print("OK: two figures have role/title/desc, width 720, font sizes 16~28 and a large-view link")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", type=Path, help="ENTROPY2D main.cpp (optional)")
    parser.add_argument("--output", type=Path, help="write a fresh measurement (needs --judge)")
    parser.add_argument("--tables", action="store_true", help="print the lesson tables generated from the stored JSON")
    args = parser.parse_args()
    if args.tables:
        for name, rows in table_lines(json.loads(DATA.read_text())).items():
            print(f"@@{name}@@")
            print("\n".join(rows))
        return
    sn = snippets()
    if args.judge and args.output:
        data = measure(args.judge, sn)
        args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        return
    check_bounds()
    check_reference(sn)
    check_hand(sn)
    data = json.loads(DATA.read_text())
    if args.judge:
        assert hashlib.sha256(args.judge.read_bytes()).hexdigest() == data["judge_sha256"], "judge differs from the measured one"
        check_hand_judge(args.judge, sn)
        with tempfile.TemporaryDirectory(prefix="lesson-entropy-judge-") as tmp:
            folder = Path(tmp)
            src = patched_judge(args.judge, folder)
            for s in STAGES:
                r = judge_run(src, assemble(s, sn), folder, "m", ["-O2"])
                row = next(x for x in data["rows"] if x["label"].startswith(f"{s}단계"))
                assert r["total"] == row["total"] and [r["score"][t] for t in sorted(r["score"])] == row["tcs"], s
                assert sum(v[0] for v in r["mirror"].values()) == r["total"] and all((v[4] == 0 or s == 1) and v[5] == 0 for v in r["mirror"].values())
            for s in STAGES:
                judge_run(src, assemble(s, sn), folder, "san", SAN, timeout=900)
        print("OK: public grader re-run reproduces the stored scores, mirror == grader, ASan/UBSan clean")
    check_svgs()
    check_tables(data)


if __name__ == "__main__":
    main()
