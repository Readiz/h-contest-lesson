"""Check the explore-unknown-map (ROBOTCLEAN) lesson: code blocks, frame transform, planners, hand example, failures, measurements.

Without --judge only the checks that need no public grader run: header-free assembly of the
lesson blocks, a reference grader written for this check (rules from the problem statement, scan
rotation done by rotating the 3 x 3 window, not by the grader's switch), the claim "my map equals
the observed part of the true map" after every API call, pose agreement, the own-cost versus
reference-cost agreement, back-to-back runs (stale-state detection), the two planners against
independent oracles written in Python, the hand-calculated example, failing variants, the heap
capacity bound, and agreement between the lesson tables and the stored measurement JSON.

With --judge /path/to/ROBOTCLEAN/main.cpp the public grader is compiled with a logging-only patch
and the stored scores are re-measured and compared. --output rewrites the JSON from a fresh
measurement.
"""
from __future__ import annotations

import argparse
import atexit
import concurrent.futures
import datetime
import hashlib
import heapq
import json
from collections import deque
from pathlib import Path
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "lessons/explore-unknown-map/lesson.md"
DATA = ROOT / "lessons/explore-unknown-map/lesson-assets/measurements.json"
sys.path.insert(0, str(ROOT / "scripts"))
from cpp_library import check_submission_code, read_library_snippets  # noqa: E402

SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
SAN = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-g", "-O1"]
NEEDED = ("rc-state", "rc-baseline", "rc-bfs", "rc-dijkstra")


def snippets() -> dict[str, str]:
    found: dict[str, str] = {}
    for name, code in SNIP_RE.findall(LESSON.read_text()):
        assert name not in found, f"duplicate snippet {name}"
        check_submission_code(code, name)
        found[name] = code
    for name in NEEDED:
        assert name in found, f"missing snippet {name}"
    return found


def assemble(kind: str, sn: dict[str, str], edits: list[tuple[str, str]] | None = None) -> str:
    lib = read_library_snippets()
    parts = {"baseline": [sn["rc-state"], sn["rc-baseline"]],
             "bfs": [lib["queue"], sn["rc-state"], sn["rc-bfs"]],
             "dijkstra": [lib["min-heap"], sn["rc-state"], sn["rc-dijkstra"]]}[kind]
    code = "\n".join(parts) + "\n"
    for old, new in edits or []:
        code, n = re.subn(old, new, code, count=1)
        assert n == 1, f"edit target not found: {old}"
    return code


def with_param(name: str, value: str) -> list[tuple[str, str]]:
    return [(rf"(const int {name} = )\d+;", rf"\g<1>{value};")]


def compile_to(exe: Path, sources: list[Path], extra: list[str]) -> None:
    subprocess.run(["c++", "-std=c++17", *extra, *map(str, sources), "-o", str(exe)], check=True)


# ---------------------------------------------------------------- reference grader and harness
HARNESS = r'''#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

// ---- reference grader: rules from the statement, written independently of main.cpp ----
static const int GD[4][2] = {{-1, 0}, {0, -1}, {1, 0}, {0, 1}};   // 0 up, 1 left, 2 down, 3 right
static std::vector<std::string> gMap;
static int gY, gX, gDir;                 // true pose
static int gSY, gSX, gH0;                // start pose of this run
static std::vector<std::vector<char>> gClean;
static long long gCost; static int gScans, gMoves, gBumps, gTurns;
static bool gTrace = false;
static bool gCheck = true;

static bool wall(int y, int x) { return gMap[y][x] == '#'; }

static void verify(const char* where) {
    if (!gCheck) return;
    {   // pose: my (y,x) -> true via the start pose; my dir = (true dir - start dir) mod 4
        int u = rc::R.y - rc::C, v = rc::R.x - rc::C;
        int ty = gSY - u * GD[gH0][0] - v * GD[(gH0 + 1) % 4][0];
        int tx = gSX - u * GD[gH0][1] - v * GD[(gH0 + 1) % 4][1];
        if (ty != gY || tx != gX || (gH0 + rc::R.dir) % 4 != gDir) {
            printf("MISMATCH pose at %s: mine (%d,%d,%d) true (%d,%d,%d)\n", where, ty, tx, (gH0 + rc::R.dir) % 4, gY, gX, gDir);
            exit(3);
        }
    }
    int H = (int)gMap.size(), W = (int)gMap[0].size();
    for (int y = 0; y < rc::S; ++y) for (int x = 0; x < rc::S; ++x) {
        int st = rc::R.cell[y][x];
        if (st == rc::UNK) { if (rc::R.seen[y][x]) { printf("MISMATCH seen on unknown at %s\n", where); exit(3); } continue; }
        int u = y - rc::C, v = x - rc::C;
        int ty = gSY - u * GD[gH0][0] - v * GD[(gH0 + 1) % 4][0];
        int tx = gSX - u * GD[gH0][1] - v * GD[(gH0 + 1) % 4][1];
        bool inside = ty >= 0 && ty < H && tx >= 0 && tx < W;
        bool realWall = !inside || wall(ty, tx);
        if ((st == rc::WALL) != realWall) { printf("MISMATCH map cell my(%d,%d) true(%d,%d) mine=%d at %s\n", y, x, ty, tx, st, where); exit(3); }
        if (rc::R.seen[y][x] && !gClean[ty][tx]) { printf("MISMATCH seen but not cleaned at %s\n", where); exit(3); }
    }
}

void scan(int f[3][3]) {
    verify("scan");
    gCost += 20; ++gScans;
    int win[3][3];
    for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) win[i][j] = wall(gY - 1 + i, gX - 1 + j);
    for (int k = 0; k < gDir; ++k) {                   // facing direction k -> rotate the window clockwise k times
        int t[3][3];
        for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) t[i][j] = win[2 - j][i];
        memcpy(win, t, sizeof win);
    }
    memcpy(f, win, sizeof win);
    if (gTrace) {
        printf("T SCAN true=(%d,%d,%d) mine=(%d,%d,%d) f=", gY, gX, gDir, rc::R.y, rc::R.x, rc::R.dir);
        for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) printf("%d", f[i][j]);
        printf("\n");
    }
}
int move(void) {
    verify("move");
    gCost += 10;
    int ny = gY + GD[gDir][0], nx = gX + GD[gDir][1];
    bool ok = !wall(ny, nx);
    if (ok) { gY = ny; gX = nx; gClean[gY][gX] = 1; ++gMoves; } else ++gBumps;
    if (gTrace) printf("T MOVE %s true=(%d,%d,%d) mine=(%d,%d,%d)\n", ok ? "ok" : "bump", gY, gX, gDir, rc::R.y, rc::R.x, rc::R.dir);
    return ok ? 1 : 0;
}
void turn(int cmd) {
    verify("turn");
    gCost += 15; ++gTurns;
    if (cmd == 1) gDir = (gDir + 1) % 4; else if (cmd == 2) gDir = (gDir + 2) % 4; else if (cmd == 3) gDir = (gDir + 3) % 4;
    if (gTrace) printf("T TURN %d true=(%d,%d,%d) mine=(%d,%d,%d)\n", cmd, gY, gX, gDir, rc::R.y, rc::R.x, rc::R.dir);
}


#ifdef HAS_PLAN
static void snapshot() {
    int y0 = rc::S, y1 = -1, x0 = rc::S, x1 = -1;
    for (int y = 0; y < rc::S; ++y) for (int x = 0; x < rc::S; ++x) if (rc::R.cell[y][x] != rc::UNK) {
        if (y < y0) y0 = y; if (y > y1) y1 = y; if (x < x0) x0 = x; if (x > x1) x1 = x; }
    printf("SNAP %d %d %d %d\n", y0 - rc::C, x0 - rc::C, y1 - rc::C, x1 - rc::C);
    for (int y = y0; y <= y1; ++y) {
        printf("ROW ");
        for (int x = x0; x <= x1; ++x) {
            char ch = rc::R.cell[y][x] == rc::UNK ? '?' : rc::R.cell[y][x] == rc::WALL ? '#' : rc::R.seen[y][x] ? 'o' : '.';
            printf("%c", ch);
        }
        printf("\n");
    }
}
static int driver() {
    gTrace = true;
    rc::reset();
    int dec = 0;
    if (rc::unknownAround() >= rc::SCAN_MIN) rc::doScan();
    for (;;) {
        snapshot();
        int n = rc::plan();
        if (n <= 0) { printf("END\n"); break; }
        int y = rc::R.y, x = rc::R.x, d = rc::R.dir, cost = 0;
        for (int i = 0; i < n; ++i) { if (rc::path[i] != d) { cost += 15; d = rc::path[i]; } cost += 10; y += rc::DY[d]; x += rc::DX[d]; }
        printf("DEC %d pos %d %d dir %d target %d %d len %d cost %d\n", dec++, rc::R.y - rc::C, rc::R.x - rc::C, rc::R.dir, y - rc::C, x - rc::C, n, cost);
        rc::walk(n);
    }
    return 0;
}
#endif

extern void cleanHouse();

static bool readMap() {
    int H, W;
    if (scanf("%d %d", &H, &W) != 2) return false;
    gMap.assign(H, "");
    for (int i = 0; i < H; ++i) { char buf[256]; if (scanf("%s", buf) != 1) return false; gMap[i] = buf; }
    return true;
}

int main(int argc, char** argv) {
    std::string mode = argv[1];
#ifdef HAS_PLAN
    if (mode == "hand") {
        if (!readMap()) return 1;
        scanf("%d %d %d", &gSY, &gSX, &gH0);
        gY = gSY; gX = gSX; gDir = gH0;
        gClean.assign(gMap.size(), std::vector<char>(gMap[0].size(), 0)); gClean[gY][gX] = 1;
        init();
        driver();
        printf("TOTAL %lld SCANS %d MOVES %d BUMPS %d TURNS %d MINE %lld\n", gCost, gScans, gMoves, gBumps, gTurns, rc::T.cost);
        return 0;
    }
#endif
    if (mode == "cases" || mode == "trace") {
        gTrace = mode == "trace";
        int n; if (scanf("%d", &n) != 1) return 1;
        init();
        for (int i = 0; i < n; ++i) {
            if (!readMap()) return 1;
            scanf("%d %d %d", &gSY, &gSX, &gH0);
            gY = gSY; gX = gSX; gDir = gH0;
            int H = (int)gMap.size(), W = (int)gMap[0].size();
            gClean.assign(H, std::vector<char>(W, 0)); gClean[gY][gX] = 1;
            long long c0 = gCost; int s0 = gScans, m0 = gMoves, b0 = gBumps, t0 = gTurns;
            cleanHouse();
            verify("end");
            int missing = 0, free = 0;
            for (int y = 0; y < H; ++y) for (int x = 0; x < W; ++x) if (!wall(y, x)) { ++free; if (!gClean[y][x]) ++missing; }
            printf("CASE %d COST %lld SCANS %d MOVES %d BUMPS %d TURNS %d FREE %d MISSING %d MINE %lld\n", i, gCost - c0, gScans - s0,
                   gMoves - m0, gBumps - b0, gTurns - t0, free, missing, rc::T.cost);
        }
        printf("DONE %lld %lld\n", gCost, rc::T.cost);
#ifdef HAS_PLAN
    } else if (mode == "plan") {
        int n; if (scanf("%d", &n) != 1) return 1;
        gCheck = false;
        for (int i = 0; i < n; ++i) {
            int H, W, py, px, pd; scanf("%d %d", &H, &W);
            std::vector<std::string> rows(H);
            for (int r = 0; r < H; ++r) { char buf[256]; scanf("%s", buf); rows[r] = buf; }
            scanf("%d %d %d", &py, &px, &pd);
            rc::reset();
            for (int y = 0; y < rc::S; ++y) for (int x = 0; x < rc::S; ++x) { rc::R.cell[y][x] = rc::UNK; rc::R.seen[y][x] = false; }
            for (int r = 0; r < H; ++r) for (int c = 0; c < W; ++c) {
                char ch = rows[r][c];
                int y = 20 + r, x = 20 + c;
                if (ch == '#') rc::R.cell[y][x] = rc::WALL;
                else if (ch == '.') rc::R.cell[y][x] = rc::FREE;
                else if (ch == 'o') { rc::R.cell[y][x] = rc::FREE; rc::R.seen[y][x] = true; }
            }
            rc::R.y = 20 + py; rc::R.x = 20 + px; rc::R.dir = pd;
            int len = rc::plan();
            printf("PLAN %d", len);
            for (int k = 0; k < len; ++k) printf(" %d", rc::path[k]);
            printf("\n");
        }
#ifdef HAS_HEAPSTAT
        printf("HEAP %d %d\n", rc::heapMax, rc::heapFail);
#endif
#endif
    }
    return 0;
}
'''


_BUILD_DIR = Path(tempfile.mkdtemp(prefix="lesson-robot-build-"))
atexit.register(shutil.rmtree, _BUILD_DIR, ignore_errors=True)
_BUILT: dict[str, Path] = {}


def build_harness(code: str, folder: Path, name: str, extra: list[str], defines: list[str] | None = None) -> Path:
    """Compile lesson code + reference grader once per distinct (code, flags); the same binary serves every mode."""
    key = hashlib.sha1("\0".join([code, *extra, "|", *(defines or [])]).encode()).hexdigest()[:16]
    if key not in _BUILT:
        src = _BUILD_DIR / f"{key}.cpp"
        exe = _BUILD_DIR / key
        plan = ["-DHAS_PLAN"] if "int plan()" in code else []
        src.write_text(code + "\n" + HARNESS)
        compile_to(exe, [src], extra + plan + (defines or []))
        _BUILT[key] = exe
    return _BUILT[key]


def prebuild(jobs: list[tuple[str, list[str], list[str] | None]]) -> None:
    """Compile independent harness variants in parallel (the checks below then reuse the binaries)."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda j: build_harness(j[0], _BUILD_DIR, "x", j[1], j[2]), jobs))


class Rng:
    """Small deterministic generator so maps do not depend on the Python version."""
    def __init__(self, seed: int) -> None:
        self.s = (seed * 2654435761 + 12345) & 0xFFFFFFFF

    def next(self) -> int:
        self.s = (self.s * 1664525 + 1013904223) & 0xFFFFFFFF
        return self.s >> 8

    def below(self, n: int) -> int:
        return self.next() % n

    def chance(self, percent: int) -> bool:
        return self.below(100) < percent


def largest_component(g: list[list[str]]) -> list[tuple[int, int]]:
    h, w = len(g), len(g[0])
    seen: set = set()
    best: list = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if g[y][x] == "." and (y, x) not in seen:
                comp = [(y, x)]
                seen.add((y, x))
                i = 0
                while i < len(comp):
                    cy, cx = comp[i]
                    i += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        n = (cy + dy, cx + dx)
                        if g[n[0]][n[1]] == "." and n not in seen:
                            seen.add(n)
                            comp.append(n)
                if len(comp) > len(best):
                    best = comp
    return best


def keep_largest(g: list[list[str]]) -> tuple[list[str], list[tuple[int, int]]]:
    best = largest_component(g)
    out = [["#"] * len(g[0]) for _ in g]
    for y, x in best:
        out[y][x] = "."
    return ["".join(r) for r in out], best


def small_cases(count: int, seed: int) -> str:
    rng = Rng(seed)
    lines = [str(count)]
    for i in range(count):
        h, w = 5 + rng.below(20), 5 + rng.below(20)
        dens = (0, 10, 25, 40)[rng.below(4)]
        g = [["#"] * w for _ in range(h)]
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                g[y][x] = "#" if rng.chance(dens) else "."
        rows, comp = keep_largest(g)
        if len(comp) < 2:
            rows = ["#" * w] + ["#" + "." * (w - 2) + "#" for _ in range(h - 2)] + ["#" * w]
            comp = [(y, x) for y in range(1, h - 1) for x in range(1, w - 1)]
        sy, sx = comp[rng.below(len(comp))]
        lines += [f"{h} {w}", *rows, f"{sy} {sx} {rng.below(4)}"]
        if i % 7 == 3:                      # the same run again right after: leftovers must not matter
            lines[0] = str(int(lines[0]) + 1)
            lines += [f"{h} {w}", *rows, f"{sy} {sx} {rng.below(4)}"]
    return "\n".join(lines) + "\n"


def run_cases(exe: Path, text: str) -> subprocess.CompletedProcess:
    return subprocess.run([str(exe), "cases"], input=text, capture_output=True, text=True, timeout=120)


def case_rows(out: str) -> list[dict]:
    rows = []
    for m in re.finditer(r"^CASE (\d+) COST (\d+) SCANS (\d+) MOVES (\d+) BUMPS (\d+) TURNS (\d+) FREE (\d+) MISSING (\d+) MINE (\d+)$", out, re.M):
        rows.append(dict(zip(("i", "cost", "scans", "moves", "bumps", "turns", "free", "missing", "mine"), map(int, m.groups()))))
    return rows


def judge_ok(proc: subprocess.CompletedProcess) -> tuple[bool, str]:
    """True when every API call kept my map and pose equal to the truth and every free cell was cleaned."""
    if proc.returncode != 0:
        first = next((l for l in proc.stdout.splitlines() if l.startswith("MISMATCH")), f"exit {proc.returncode}")
        return False, first
    rows = case_rows(proc.stdout)
    if not rows:
        return False, "no output"
    if any(r["missing"] for r in rows):
        return False, "uncleaned cells"
    return True, "ok"


REF_PLANS = (("baseline", "baseline", []), ("bfs", "bfs", []), ("dijkstra", "dijkstra", []),
             ("bfs SCAN_MIN 0", "bfs", with_param("SCAN_MIN", "0")),
             ("dijkstra SCAN_MIN 9", "dijkstra", with_param("SCAN_MIN", "9")))
HEAP_EDITS = [(r"hc::MinHeap<1 << 18> H;", "hc::MinHeap<1 << 18> H; int heapMax, heapFail;"),
              (r"    H\.push\(nd, b\);", "    if (!H.push(nd, b)) ++heapFail;\n    if (H.size > heapMax) heapMax = H.size;")]


def check_reference(sn: dict[str, str]) -> dict:
    info: dict = {}
    text = small_cases(70, 7)
    n_runs = int(text.splitlines()[0])
    with tempfile.TemporaryDirectory(prefix="lesson-robot-") as tmp:
        folder = Path(tmp)
        for label, kind, edits in REF_PLANS:
            exe = build_harness(assemble(kind, sn, edits), folder, "ref", SAN)
            proc = run_cases(exe, text)
            ok, why = judge_ok(proc)
            assert ok, (label, why, proc.stderr[:300])
            rows = case_rows(proc.stdout)
            assert len(rows) == n_runs
            done = re.search(r"^DONE (\d+) (\d+)$", proc.stdout, re.M)
            assert done and done.group(1) == done.group(2), (label, "my cost differs from reference cost")
            assert all(r["cost"] == 10 * (r["moves"] + r["bumps"]) + 20 * r["scans"] + 15 * r["turns"] for r in rows)
            print(f"OK: {label}: {n_runs} runs, map and pose equal the truth after every call, all free cells cleaned, "
                  f"my cost == reference cost ({done.group(1)})")
            info[label] = int(done.group(1))
    return info


# ---------------------------------------------------------------- planners against Python oracles
DIRS = ((-1, 0), (0, -1), (1, 0), (0, 1))


def knowledge_state(rng: Rng) -> tuple[list[str], tuple[int, int, int]]:
    h, w = 6 + rng.below(7), 6 + rng.below(7)
    dens = (0, 15, 30)[rng.below(3)]
    real = [[("#" if (y in (0, h - 1) or x in (0, w - 1) or rng.chance(dens)) else ".") for x in range(w)] for y in range(h)]
    free = [(y, x) for y in range(h) for x in range(w) if real[y][x] == "."]
    if not free:
        real[1][1] = "."
        free = [(1, 1)]
    ry, rx = free[rng.below(len(free))]
    visited = {(ry, rx)}
    frontier = [(ry, rx)]
    target = 1 + rng.below(len(free))
    while frontier and len(visited) < target:
        y, x = frontier.pop(rng.below(len(frontier)))
        for dy, dx in DIRS:
            n = (y + dy, x + dx)
            if real[n[0]][n[1]] == "." and n not in visited and len(visited) < target and rng.chance(70):
                visited.add(n)
                frontier.append(n)
        if rng.chance(50):
            frontier.append((y, x))
    near = {(y + dy, x + dx) for (y, x) in visited for dy in (-1, 0, 1) for dx in (-1, 0, 1)}
    rows = []
    for y in range(h):
        row = ""
        for x in range(w):
            if (y, x) in visited:
                row += "o"
            elif real[y][x] == "#":
                row += "#" if (y, x) in near and rng.chance(60) else "?"
            else:
                row += "." if (y, x) in near and rng.chance(55) else "?"
        rows.append(row)
    return rows, (ry, rx, rng.below(4))


def cell_at(rows: list[str], y: int, x: int) -> str:
    return rows[y][x] if 0 <= y < len(rows) and 0 <= x < len(rows[0]) else "?"


def oracle(rows: list[str], pose: tuple[int, int, int]) -> tuple[int | None, int | None]:
    """(cheapest cost to an unvisited non-wall cell with turn 15 / move 10, fewest moves), None when nothing is left."""
    ry, rx, rd = pose
    best_cost = None
    dist = {(ry, rx, rd): 0}
    heap = [(0, ry, rx, rd)]
    while heap:
        c, y, x, d = heapq.heappop(heap)
        if dist.get((y, x, d), 1 << 60) < c:
            continue
        if cell_at(rows, y, x) != "o":
            best_cost = c
            break
        for nd in range(4):
            if nd != d and c + 15 < dist.get((y, x, nd), 1 << 60):
                dist[(y, x, nd)] = c + 15
                heapq.heappush(heap, (c + 15, y, x, nd))
        ny, nx = y + DIRS[d][0], x + DIRS[d][1]
        if cell_at(rows, ny, nx) != "#" and c + 10 < dist.get((ny, nx, d), 1 << 60):
            dist[(ny, nx, d)] = c + 10
            heapq.heappush(heap, (c + 10, ny, nx, d))
    best_steps = None
    seen = {(ry, rx)}
    q = deque([(ry, rx, 0)])
    while q:
        y, x, s = q.popleft()
        for dy, dx in DIRS:
            ny, nx = y + dy, x + dx
            ch = cell_at(rows, ny, nx)
            if ch == "#" or (ny, nx) in seen:
                continue
            seen.add((ny, nx))
            if ch != "o":
                best_steps = s + 1
                q.clear()
                break
            q.append((ny, nx, s + 1))
    return best_cost, best_steps


def path_cost(rows: list[str], pose: tuple[int, int, int], path: list[int]) -> tuple[int, int]:
    """Validate a planned direction list and return (cost with turns, moves). The last cell must be the first unvisited one."""
    y, x, d = pose
    cost = 0
    for i, nd in enumerate(path):
        if nd != d:
            cost += 15
            d = nd
        y, x = y + DIRS[d][0], x + DIRS[d][1]
        cost += 10
        ch = cell_at(rows, y, x)
        assert ch != "#", "path crosses a known wall"
        assert (ch == "o") == (i < len(path) - 1), "path must walk visited cells and end on the first unvisited cell"
    return cost, len(path)


def check_planners(sn: dict[str, str]) -> None:
    rng = Rng(99)
    states = [knowledge_state(rng) for _ in range(400)]
    enclosed = (["######", "#oo###", "######"], (1, 1, 0))
    lines = [str(len(states) + 1)]
    for rows, pose in states + [enclosed]:
        lines += [f"{len(rows)} {len(rows[0])}", *rows, "%d %d %d" % pose]
    text = "\n".join(lines) + "\n"
    with tempfile.TemporaryDirectory(prefix="lesson-robot-plan-") as tmp:
        folder = Path(tmp)
        for kind in ("bfs", "dijkstra"):
            exe = build_harness(assemble(kind, sn), folder, "plan", SAN)
            out = subprocess.run([str(exe), "plan"], input=text, capture_output=True, text=True, timeout=120, check=True).stdout
            plans = [list(map(int, l.split()[1:])) for l in out.splitlines() if l.startswith("PLAN")]
            for l in plans:
                assert int(l[0]) == len(l) - 1
            assert len(plans) == len(states) + 1
            tight = 0
            for (rows, pose), p in zip(states + [enclosed], plans):
                n, path = p[0], p[1:]
                best_cost, best_steps = oracle(rows, pose)
                if best_cost is None:
                    assert n == 0, (rows, pose, p)
                    continue
                cost, moves = path_cost(rows, pose, path)
                if kind == "bfs":
                    assert moves == best_steps, (kind, rows, pose, p, best_steps)
                else:
                    assert cost == best_cost, (kind, rows, pose, p, cost, best_cost)
                tight += cost == best_cost
            what = "fewest moves (BFS)" if kind == "bfs" else "cheapest (cell, direction) cost (Dijkstra)"
            print(f"OK: {kind} planner returns the {what} on {len(states)} random knowledge states and 0 when enclosed"
                  f" ({tight} of them also cheapest in turn cost)")
    # heap capacity: every state of a 62 x 62 room is visited, the only target is the far corner
    rows = ["#" * 64] + ["#" + "o" * 62 + "#" for _ in range(62)] + ["#" * 64]
    rows[62] = "#" + "o" * 61 + "." + "#"
    text = f"1\n64 64\n" + "\n".join(rows) + "\n1 1 0\n"
    code = assemble("dijkstra", sn, HEAP_EDITS)
    with tempfile.TemporaryDirectory(prefix="lesson-robot-heap-") as tmp:
        exe = build_harness(code, Path(tmp), "heap", SAN, ["-DHAS_HEAPSTAT"])
        out = subprocess.run([str(exe), "plan"], input=text, capture_output=True, text=True, timeout=120, check=True).stdout
    heap = re.search(r"^HEAP (\d+) (\d+)$", out, re.M)
    peak, fail = int(heap.group(1)), int(heap.group(2))
    assert fail == 0 and peak < (1 << 18) // 2 and re.search(r"^PLAN [1-9]", out, re.M)
    print(f"OK: worst case for the heap (62 x 62 visited room, far corner target): peak {peak} items, no overflow of {1 << 18}")
    return {"heap_peak": peak}


# ---------------------------------------------------------------- failing variants
FAILURES = {
    "관측을 회전하지 않고 기록": [(r"R\.cell\[R\.y \+ ahead \* fy \+ right \* ry\]\[R\.x \+ ahead \* fx \+ right \* rx\]",
                          "R.cell[R.y + sy - 1][R.x + sx - 1]")],
    "막혀도 위치를 갱신": [(r"\+\+T\.bumps; return 0; \}", "++T.bumps; }")],
    "이전 실행의 지도가 남음": [(r"    for \(int y = 0; y < S; \+\+y\) for \(int x = 0; x < S; \+\+x\) \{ R\.cell\[y\]\[x\] = UNK; R\.seen\[y\]\[x\] = false; \}\n", "")],
    "회전 부호를 반대로 셈": [(r"int k = \(d - R\.dir \+ 4\) % 4;", "int k = (R.dir - d + 4) % 4;")],
}


def check_failures(sn: dict[str, str]) -> dict:
    text = small_cases(70, 7)
    found = {}
    with tempfile.TemporaryDirectory(prefix="lesson-robot-bad-") as tmp:
        folder = Path(tmp)
        for name, edits in FAILURES.items():
            exe = build_harness(assemble("dijkstra", sn, edits), folder, "bad", ["-O1", "-g"])
            proc = run_cases(exe, text)
            ok, why = judge_ok(proc)
            assert not ok, f"failure variant not detected: {name}"
            found[name] = why
            print(f"OK: failure '{name}' is detected: {why[:110]}")
    return found


# ---------------------------------------------------------------- hand example
HAND_MAP = ["########", "#......#", "#..#...#", "#..#...#", "#......#", "########"]
HAND_START = (3, 4, 1)          # row, column, heading: 1 = facing left (west)


def hand_text() -> str:
    h, w = len(HAND_MAP), len(HAND_MAP[0])
    return f"{h} {w}\n" + "\n".join(HAND_MAP) + "\n%d %d %d\n" % HAND_START


def py_scan(y: int, x: int, heading: int) -> str:
    """The 3 x 3 window seen from (y, x) facing `heading`, written by rotating the window clockwise `heading` times."""
    win = [[1 if HAND_MAP[y - 1 + i][x - 1 + j] == "#" else 0 for j in range(3)] for i in range(3)]
    for _ in range(heading):
        win = [list(r) for r in zip(*win[::-1])]
    return "".join(str(v) for r in win for v in r)


def parse_hand(out: str) -> dict:
    snaps, decs, scans, calls = [], [], [], []
    lines = out.splitlines()
    i = 0
    while i < len(lines):
        l = lines[i]
        if l.startswith("SNAP"):
            box = tuple(map(int, l.split()[1:]))
            rows = []
            while i + 1 < len(lines) and lines[i + 1].startswith("ROW "):
                i += 1
                rows.append(lines[i][4:])
            snaps.append((box, rows))
        elif l.startswith("DEC"):
            decs.append(tuple(map(int, re.findall(r"-?\d+", l))))
        elif l.startswith("T SCAN"):
            m = re.match(r"T SCAN true=\((\d+),(\d+),(\d+)\) mine=\((\d+),(\d+),(\d+)\) f=(\d{9})", l)
            scans.append((tuple(map(int, m.groups()[:3])), tuple(map(int, m.groups()[3:6])), m.group(7)))
        if l.startswith("T "):
            calls.append(l)
        i += 1
    total = re.search(r"^TOTAL (\d+) SCANS (\d+) MOVES (\d+) BUMPS (\d+) TURNS (\d+) MINE (\d+)$", out, re.M)
    return {"snaps": snaps, "decs": decs, "scans": scans, "calls": calls, "total": tuple(map(int, total.groups()))}


def hand_run(sn: dict[str, str], folder: Path) -> dict:
    exe = build_harness(assemble("dijkstra", sn), folder, "hand", SAN)
    out = subprocess.run([str(exe), "hand"], input=hand_text(), capture_output=True, text=True, timeout=60, check=True).stdout
    return parse_hand(out)


def check_hand(sn: dict[str, str], need_text: bool = True) -> dict:
    with tempfile.TemporaryDirectory(prefix="lesson-robot-hand-") as tmp:
        res = hand_run(sn, Path(tmp))
    sy, sx, h0 = HAND_START
    # the first scan is the rotated window of the true map
    (true0, mine0, f0) = res["scans"][0]
    assert true0 == HAND_START and mine0 == (64, 64, 0) and f0 == py_scan(sy, sx, h0) == "011000000", (true0, mine0, f0)
    # every known cell of every snapshot equals the true map through the frame transform
    for box, rows in res["snaps"]:
        y0, x0 = box[0], box[1]
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch == "?":
                    continue
                u, v = y0 + r, x0 + c                                      # offset from my start cell
                ty = sy - u * DIRS[h0][0] - v * DIRS[(h0 + 1) % 4][0]
                tx = sx - u * DIRS[h0][1] - v * DIRS[(h0 + 1) % 4][1]
                assert (HAND_MAP[ty][tx] == "#") == (ch == "#"), (u, v, ty, tx, ch)
    # every decision's cost equals the independent oracle on the snapshot printed just before it
    for (box, rows), dec in zip(res["snaps"], res["decs"]):
        k, py, px, pd, ty, tx, n, cost = dec
        pose = (py - box[0], px - box[1], pd)
        best, _ = oracle(rows, pose)
        assert cost == best, (dec, best)
    d = res["decs"]
    want = [(0, 0, 0, 0, 0, -1, 1, 25), (1, 0, -1, 1, 0, -2, 1, 10), (2, 0, -1, 1, -1, -1, 1, 25)]
    assert d[:3] == want, d[:3]
    assert res["total"][0] == res["total"][5] and res["total"][:5] == (805, 4, 34, 10, 19), res["total"]
    calls = res["calls"]
    assert calls[0].startswith("T SCAN") and calls[1].startswith("T TURN 1") and calls[2].startswith("T MOVE ok")
    assert calls[3].startswith("T MOVE bump") and calls[4].startswith("T TURN 3") and calls[5].startswith("T MOVE ok")
    text = LESSON.read_text()
    if need_text:
        for needle in ("011000000", "| 25 |", "| 10 |", "805", "(64, 64)", "(64, 63)"):
            assert needle in text, f"hand example number missing from lesson: {needle}"
    print("OK: hand example (scan 011000000, targets (0,-1) 25, (0,-2) 10 bump, (-1,-1) 25, total 805) recomputed by the lesson code and the oracle")
    return {"total": res["total"][0]}


# ---------------------------------------------------------------- hold-out maps (not used for tuning)
def holdout_maps() -> list[list[str]]:
    maps = []
    for kind, seed in (("rooms", 1), ("rooms", 2), ("rooms", 3), ("blocks", 1), ("blocks", 2), ("blocks", 3),
                       ("maze", 1), ("maze", 2), ("cave", 1), ("cave", 2)):
        rng = Rng(1000 * (("rooms", "blocks", "maze", "cave").index(kind) + 1) + seed)
        n = 64
        g = [["#"] * n for _ in range(n)]
        if kind == "rooms":
            for y in range(1, n - 1):
                for x in range(1, n - 1):
                    g[y][x] = "."
            cuts = [20 + rng.below(6), 40 + rng.below(6)]
            for c in cuts:
                for i in range(1, n - 1):
                    g[c][i] = "#"
                    g[i][c] = "#"
            for c in cuts:                       # two doors per wall segment
                for a, b in ((1, cuts[0]), (cuts[0] + 1, cuts[1]), (cuts[1] + 1, n - 1)):
                    for _ in range(2):
                        p = a + rng.below(b - a)
                        g[c][p] = "."
                        g[p][c] = "."
            for _ in range(10):
                y, x, h, w = 2 + rng.below(58), 2 + rng.below(58), 1 + rng.below(4), 1 + rng.below(4)
                for yy in range(y, min(y + h, n - 1)):
                    for xx in range(x, min(x + w, n - 1)):
                        g[yy][xx] = "#"
        elif kind == "blocks":
            for y in range(1, n - 1):
                for x in range(1, n - 1):
                    g[y][x] = "."
            for _ in range(28):
                y, x, h, w = 1 + rng.below(60), 1 + rng.below(60), 2 + rng.below(9), 2 + rng.below(9)
                for yy in range(y, min(y + h, n - 1)):
                    for xx in range(x, min(x + w, n - 1)):
                        g[yy][xx] = "#"
        elif kind == "maze":
            cells = 31
            visited = [[False] * cells for _ in range(cells)]
            stack = [(rng.below(cells), rng.below(cells))]
            visited[stack[0][0]][stack[0][1]] = True
            g[1 + 2 * stack[0][0]][1 + 2 * stack[0][1]] = "."
            while stack:
                cy, cx = stack[-1]
                opts = [(cy + dy, cx + dx) for dy, dx in DIRS if 0 <= cy + dy < cells and 0 <= cx + dx < cells and not visited[cy + dy][cx + dx]]
                if not opts:
                    stack.pop()
                    continue
                ny, nx = opts[rng.below(len(opts))]
                visited[ny][nx] = True
                g[1 + 2 * ny][1 + 2 * nx] = "."
                g[1 + cy + ny][1 + cx + nx] = "."
                stack.append((ny, nx))
            for _ in range(40):                  # a few loops
                y, x = 1 + rng.below(61), 1 + rng.below(61)
                if (y + x) % 2 == 1:
                    g[y][x] = "."
        else:
            for y in range(1, n - 1):
                for x in range(1, n - 1):
                    g[y][x] = "#" if rng.chance(42) else "."
            for _ in range(4):
                new = [row[:] for row in g]
                for y in range(1, n - 1):
                    for x in range(1, n - 1):
                        walls = sum(g[y + dy][x + dx] == "#" for dy in (-1, 0, 1) for dx in (-1, 0, 1))
                        new[y][x] = "#" if walls >= 5 else "."
                g = new
        rows, comp = keep_largest(g)
        assert len(comp) >= 1500, (kind, seed, len(comp))
        maps.append(rows)
    return maps


def write_input(path: Path, maps: list[list[str]]) -> None:
    path.write_text("\n".join(" ".join("1" if ch == "#" else "0" for ch in row) for m in maps for row in m) + "\n")


# ---------------------------------------------------------------- public grader
def patched_judge(judge: Path, folder: Path) -> Path:
    text = judge.read_text()

    def once(old: str, new: str) -> None:
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new)

    once("extern void init(void);",
         "extern void init(void);\nnamespace rc { struct Tally { long long cost; int scans, moves, bumps, turns; }; extern Tally T; }")
    once('		printf("TC %d SCORE: %lld\\n", tc, SCORE - tcScoreBefore);',
         '		printf("TC %d SCORE: %lld\\n", tc, SCORE - tcScoreBefore);\n'
         '		printf("TC %d MIRROR %lld %d %d %d %d\\n", tc, rc::T.cost, rc::T.scans, rc::T.moves, rc::T.bumps, rc::T.turns);')
    once('	printf("SCORE: %lld\\n", SCORE);',
         '	printf("SCORE: %lld\\n", SCORE);\n	printf("Result : %d\\n", (int)((clock() - start) * 1000 / CLOCKS_PER_SEC));')
    path = folder / "judge_patched.cpp"
    path.write_text(text)
    return path


def parse_judge(text: str) -> dict:
    score = [int(b) for b in re.findall(r"^TC \d+ SCORE: (-?\d+)$", text, re.M)]
    mirror = [list(map(int, m)) for m in re.findall(r"^TC \d+ MIRROR (\d+) (\d+) (\d+) (\d+) (\d+)$", text, re.M)]
    total = re.search(r"^SCORE: (\d+)$", text, re.M)
    ms = re.search(r"^Result : (\d+)$", text, re.M)
    return {"tcs": score, "mirror": mirror, "total": int(total.group(1)) if total else None,
            "ms": int(ms.group(1)) if ms else None}


def judge_run(judge_src: Path, code: str, folder: Path, name: str, flags: list[str], data_dir: Path, repeat: int = 1) -> dict:
    user = folder / f"{name}.cpp"
    exe = folder / name
    user.write_text(code)
    compile_to(exe, [judge_src, user], flags)
    results = []
    for _ in range(repeat):
        proc = subprocess.run([str(exe)], cwd=data_dir, capture_output=True, text=True, timeout=300)
        r = parse_judge(proc.stdout)
        r["exit"] = proc.returncode
        results.append(r)
    first = results[0]
    assert all(r["tcs"] == first["tcs"] for r in results)
    first["ms_runs"] = [r["ms"] for r in results]
    first["ms"] = statistics.median(first["ms_runs"]) if first["ms"] is not None else None
    return first


def row_of(label: str, r: dict) -> dict:
    mt = [sum(m[i] for m in r["mirror"]) for i in range(5)]
    return {"label": label, "total": r["total"], "tcs": r["tcs"], "mirror_total": mt[0], "scans": mt[1], "moves": mt[2],
            "bumps": mt[3], "turns": mt[4], "ms": r["ms"], "ms_runs": r["ms_runs"]}


STAGES = [("기준선 DFS", "baseline", []),
          ("정책 1 SCAN_MIN 0", "bfs", with_param("SCAN_MIN", "0")),
          ("정책 1 SCAN_MIN 1", "bfs", with_param("SCAN_MIN", "1")),
          ("정책 1 SCAN_MIN 6", "bfs", []),
          ("정책 2 SCAN_MIN 1", "dijkstra", with_param("SCAN_MIN", "1")),
          ("정책 2 SCAN_MIN 6", "dijkstra", [])]
SWEEPS = [("SCAN_MIN", [str(v) for v in range(10)]), ("TURN_W", ["0", "5", "10", "15", "20", "30"]),
          ("UNK_PEN", ["0", "5", "10", "20"])]
HOLD_SWEEPS = [("SCAN_MIN", [str(v) for v in range(10)]), ("TURN_W", ["5", "15"])]


def measure(judge: Path, sn: dict[str, str]) -> dict:
    sample = judge.parent / "sample_input.txt"
    result = {"date": datetime.date.today().isoformat(), "platform": platform.platform(), "machine": platform.machine(),
              "compiler": subprocess.run(["c++", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
              "flags": "-std=c++17 -O2", "judge_sha256": hashlib.sha256(judge.read_bytes()).hexdigest(),
              "input_sha256": hashlib.sha256(sample.read_bytes()).hexdigest(),
              "rows": [], "sweeps": [], "holdout_rows": [], "holdout_sweeps": [], "failures": []}
    maps = holdout_maps()
    result["holdout_free_cells"] = [sum(r.count(".") for r in m) for m in maps]
    with tempfile.TemporaryDirectory(prefix="lesson-robot-judge-") as tmp:
        folder = Path(tmp)
        src = patched_judge(judge, folder)
        hold_dir = folder / "hold"
        hold_dir.mkdir()
        write_input(hold_dir / "sample_input.txt", maps)
        off_dir = folder / "official"
        off_dir.mkdir()
        (off_dir / "sample_input.txt").write_bytes(sample.read_bytes())

        def record(bucket: str, label: str, kind: str, edits, data_dir: Path, repeat: int = 1) -> dict:
            r = judge_run(src, assemble(kind, sn, edits), folder, "m", ["-O2"], data_dir, repeat)
            row = row_of(label, r)
            result[bucket].append(row)
            print(json.dumps({k: row[k] for k in ("label", "total", "mirror_total", "scans", "moves", "bumps", "turns", "ms")}, ensure_ascii=False), flush=True)
            return r

        for label, kind, edits in STAGES:
            record("rows", label, kind, edits, off_dir, repeat=5)
        for param, values in SWEEPS:
            for v in values:
                record("sweeps", f"{param} {v}", "dijkstra", with_param(param, v), off_dir)
        for label, kind, edits in STAGES:
            record("holdout_rows", label, kind, edits, hold_dir)
        for param, values in HOLD_SWEEPS:
            for v in values:
                record("holdout_sweeps", f"{param} {v}", "dijkstra", with_param(param, v), hold_dir)
        for name, edits in FAILURES.items():
            r = judge_run(src, assemble("dijkstra", sn, edits), folder, "m", ["-O2"], off_dir)
            row = {"label": name, "total": r["total"], "tcs": r["tcs"], "exit": r["exit"],
                   "mirror_total": sum(m[0] for m in r["mirror"]) if r["mirror"] else None}
            result["failures"].append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
        for kind in ("baseline", "bfs", "dijkstra"):
            judge_run(src, assemble(kind, sn), folder, "san", SAN, off_dir)
        result["sanitizer"] = "baseline/bfs/dijkstra passed ASan+UBSan on the public grader"
    return result


def stats(a: list[int], b: list[int]) -> dict:
    """Paired comparison on the same inputs; positive mean means a costs more than b."""
    diff = [x - y for x, y in zip(a, b)]
    mean = statistics.mean(diff)
    err = statistics.stdev(diff) / len(diff) ** 0.5
    return {"mean": mean, "err": err, "low": mean - 2 * err, "high": mean + 2 * err, "worse": sum(d > 0 for d in diff), "n": len(diff)}


def lookup(data: dict) -> dict:
    return {("official", r["label"]): r for r in data["rows"]} \
        | {("sweep", r["label"]): r for r in data["sweeps"]} | {("hold", r["label"]): r for r in data["holdout_rows"]} \
        | {("holdsweep", r["label"]): r for r in data["holdout_sweeps"]}


COMPARISONS = [
    ("DFS 대비 정책 1", ("official", "기준선 DFS"), ("official", "정책 1 SCAN_MIN 1")),
    ("BFS 대 Dijkstra (SCAN_MIN 6)", ("official", "정책 1 SCAN_MIN 6"), ("official", "정책 2 SCAN_MIN 6")),
    ("SCAN_MIN 6 대 5", ("sweep", "SCAN_MIN 6"), ("sweep", "SCAN_MIN 5")),
    ("SCAN_MIN 6 대 7", ("sweep", "SCAN_MIN 6"), ("sweep", "SCAN_MIN 7")),
    ("TURN_W 15 대 5", ("sweep", "TURN_W 15"), ("sweep", "TURN_W 5")),
    ("UNK_PEN 10 대 0", ("sweep", "UNK_PEN 10"), ("sweep", "UNK_PEN 0")),
    ("홀드아웃 BFS 대 Dijkstra", ("hold", "정책 1 SCAN_MIN 6"), ("hold", "정책 2 SCAN_MIN 6")),
    ("홀드아웃 SCAN_MIN 6 대 3", ("holdsweep", "SCAN_MIN 6"), ("holdsweep", "SCAN_MIN 3")),
]


def check_tables(data: dict, extra: dict) -> None:
    text = LESSON.read_text()
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in text.splitlines() if line.startswith("|")]

    def present(label: str, *needles: object) -> None:
        for cells in rows:
            if cells and cells[0] == label and all(str(n) in cells for n in needles):
                return
        raise AssertionError(f"lesson table row missing or stale: {label} {needles}")

    for bucket in ("rows", "sweeps", "holdout_rows", "holdout_sweeps"):
        for row in data[bucket]:
            if bucket in ("rows", "holdout_rows"):
                present(row["label"], row["total"], row["mirror_total"], row["scans"], row["moves"], row["bumps"], row["turns"])
            else:
                present(row["label"], row["total"])
    for row in data["failures"]:
        present(row["label"], row["total"] if row["total"] is not None else "비정상 종료")
    by = lookup(data)
    for name, a, b in COMPARISONS:
        s = stats(by[a]["tcs"], by[b]["tcs"])
        for needle in (f"{s['mean']:.0f}", f"{s['err']:.0f}", f"{s['low']:.0f}", f"{s['high']:.0f}", f"{s['worse']}개"):
            assert needle in text, f"comparison '{name}' value not in lesson: {needle}"
    for needle in (str(data["date"]), str(extra["heap_peak"]), str(extra["hand_total"])):
        assert needle in text, f"value not in lesson: {needle}"
    print(f"OK: lesson tables match {DATA.name} ({sum(len(data[b]) for b in ('rows', 'sweeps', 'holdout_rows', 'holdout_sweeps', 'failures'))} rows, "
          f"{len(COMPARISONS)} paired comparisons)")


def recheck_judge(judge: Path, sn: dict[str, str], data: dict) -> None:
    assert hashlib.sha256(judge.read_bytes()).hexdigest() == data["judge_sha256"], "judge file differs from the measured one"
    sample = judge.parent / "sample_input.txt"
    assert hashlib.sha256(sample.read_bytes()).hexdigest() == data["input_sha256"], "input file differs from the measured one"
    maps = holdout_maps()
    assert [sum(r.count(".") for r in m) for m in maps] == data["holdout_free_cells"], "hold-out maps changed"
    with tempfile.TemporaryDirectory(prefix="lesson-robot-judge-") as tmp:
        folder = Path(tmp)
        src = patched_judge(judge, folder)
        hold_dir = folder / "hold"
        hold_dir.mkdir()
        write_input(hold_dir / "sample_input.txt", maps)
        off_dir = folder / "official"
        off_dir.mkdir()
        (off_dir / "sample_input.txt").write_bytes(sample.read_bytes())
        for label, kind, edits in STAGES:
            for bucket, d in (("rows", off_dir), ("holdout_rows", hold_dir)):
                r = judge_run(src, assemble(kind, sn, edits), folder, "m", ["-O2"], d)
                row = next(x for x in data[bucket] if x["label"] == label)
                assert r["total"] == row["total"] and r["tcs"] == row["tcs"], (bucket, label)
                assert sum(m[0] for m in r["mirror"]) == r["total"], (bucket, label, "my cost != grader score")
        for kind in ("baseline", "bfs", "dijkstra"):
            judge_run(src, assemble(kind, sn), folder, "san", SAN, off_dir)
    print("OK: public grader re-run reproduces the stored stage scores (official and hold-out), my cost == grader score, ASan/UBSan clean")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", type=Path, help="ROBOTCLEAN main.cpp (optional; sample_input.txt must be next to it)")
    parser.add_argument("--output", type=Path, help="write fresh measurements (needs --judge)")
    parser.add_argument("--tables", action="store_true", help="print table rows from the stored JSON")
    args = parser.parse_args()
    if args.tables:
        data = json.loads(DATA.read_text())
        for bucket in ("rows", "sweeps", "holdout_rows", "holdout_sweeps"):
            for r in data[bucket]:
                print(f"| {bucket} {r['label']} | {r['total']} | {r['mirror_total']} | {r['scans']} | {r['moves']} | {r['bumps']} | {r['turns']} | {r['ms']} |")
        for r in data["failures"]:
            print(f"| {r['label']} | {r['total']} | exit {r['exit']} | {r['mirror_total']} | tcs {r['tcs']} |")
        by = lookup(data)
        for name, a, b in COMPARISONS:
            s = stats(by[a]["tcs"], by[b]["tcs"])
            print(f"{name}: mean {s['mean']:.1f} err {s['err']:.1f} [{s['low']:.1f}, {s['high']:.1f}] worse {s['worse']}/{s['n']}")
        return
    sn = snippets()
    if args.judge and args.output:
        data = measure(args.judge, sn)
        args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        return
    extra = {}
    jobs = [(assemble(k, sn, e), SAN, None) for _, k, e in REF_PLANS]
    jobs.append((assemble("dijkstra", sn, HEAP_EDITS), SAN, ["-DHAS_HEAPSTAT"]))
    jobs += [(assemble("dijkstra", sn, e), ["-O1", "-g"], None) for e in FAILURES.values()]
    prebuild(jobs)
    check_reference(sn)
    extra.update(check_planners(sn))
    extra["hand_total"] = check_hand(sn)["total"]
    check_failures(sn)
    data = json.loads(DATA.read_text())
    if args.judge:
        recheck_judge(args.judge, sn, data)
    check_tables(data, extra)


if __name__ == "__main__":
    main()
