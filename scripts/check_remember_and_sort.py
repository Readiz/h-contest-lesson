"""Check the remember-and-sort (DRONESORT) lesson: code blocks, mirror vs real state, hand examples, failures, measurements.

Without --judge only the checks that need no public grader run: header-free
assembly, a reference simulator written for this check (the rules of the problem
statement, any warehouse size), a comparison of the lesson's mirror with the real
state before every API call on small random warehouses, chained TCs, stage
variants, the hand-calculated sorting and flight examples, failure variants that
must be detected, and agreement between the lesson tables and the stored
measurement JSON.

With --judge /path/to/main.cpp the public grader is compiled with a logging-only
patch and the stored scores are re-measured. --output rewrites the JSON from a
fresh measurement (this takes a few minutes).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import platform
import re
import statistics
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LESSON_ID = "remember-and-sort"
DATA = ROOT / "lessons/remember-and-sort/lesson-assets/measurements.json"
sys.path.insert(0, str(ROOT / "scripts"))
from cpp_library import check_submission_code  # noqa: E402
from lesson_text import check_hub_summary, read_lesson_text  # noqa: E402

SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
ORDER = ("drone-mirror", "drone-clear", "drone-sort", "drone-entry")
SAN = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-g", "-O1"]
SEEDS = [5, 101, 202, 303, 404]          # 5 is the public grader's seed


def snippets() -> dict[str, str]:
    found: dict[str, str] = {}
    for name, code in SNIP_RE.findall(read_lesson_text(LESSON_ID)):
        assert name not in found, f"duplicate snippet {name}"
        check_submission_code(code, name)
        found[name] = code
    for name in ORDER:
        assert name in found, f"missing snippet {name}"
    return found


def edit(code: str, edits: list[tuple[str, str]] | None) -> str:
    for old, new in edits or []:
        code, n = re.subn(old, new, code, count=1)
        assert n == 1, f"edit target not found: {old}"
    return code


def assemble(sn: dict[str, str], edits: list[tuple[str, str]] | None = None, n: int | None = None) -> str:
    code = "\n".join(sn[name] for name in ORDER) + "\n"
    if n is not None:
        edits = [(r"const int N = 100;", f"const int N = {n};")] + list(edits or [])
    return edit(code, edits)


def flag(name: str, value: bool) -> tuple[str, str]:
    return (rf"(const bool {name} = )(?:true|false);", rf"\g<1>{'true' if value else 'false'};")


STAGES = {
    "기준선": [flag("TERRAIN", False), flag("CHOOSE_PATH", False), flag("PATIENCE", False)],
    "1단계": [flag("PATIENCE", False)],
    "2단계": [],
}
VARIANTS = {
    "x 먼저만": [flag("CHOOSE_PATH", False)],
    "임시 칸 4개": [flag("DIAGONAL", False)],
}


def compile_to(exe: Path, sources: list[Path], extra: list[str]) -> None:
    subprocess.run(["c++", "-std=c++17", *extra, *map(str, sources), "-o", str(exe)], check=True)


# ---------------------------------------------------------------- reference simulator
HARNESS = r'''
#include <cstdio>
#include <cstdlib>
#include <cstring>

static const int NN = dr::N;
struct Box { int dx, dy, w; };
static Box boxesArr[300000];
static int cellH[NN][NN];
static int cellBox[NN][NN][NN];
static int ax, ay, az, ahold = -1;
static long long calls, stageCalls[3], picks, drops, moveCalls, limitCalls;
static bool checking = true;
static int totalBoxes, dumpAt;

[[noreturn]] static void die(const char* kind, const char* detail, int code) {
    printf("FAIL %s %s calls=%lld stage=%d\n", kind, detail, calls, dr::stage);
    exit(code);
}

static void verifyCell(int x, int y) {
    if (dr::H[y][x] != cellH[y][x]) die("MIRROR", "height", 3);
    if (dr::orig[y][x] < 0 || dr::orig[y][x] > cellH[y][x]) die("MIRROR", "orig", 3);
    for (int h = dr::orig[y][x]; h < cellH[y][x]; ++h) {
        const Box& b = boxesArr[cellBox[y][x][h]];
        if (dr::bd[y][x][h] != b.dy * NN + b.dx || dr::bw[y][x][h] != b.w) die("MIRROR", "content", 3);
    }
}
// position and hold every call; the cell under the drone every call; the whole warehouse every 997th call
static void verifyMirror(bool full = false) {
    if (dr::px != ax || dr::py != ay || dr::pz != az || dr::hold != (ahold >= 0)) die("MIRROR", "position", 3);
    if (!checking || dr::stage == 0) return;
    verifyCell(ax, ay);
    if (full || calls % 997 == 0)
        for (int y = 0; y < NN; ++y) for (int x = 0; x < NN; ++x) verifyCell(x, y);
}
static void enter() {
    ++calls; ++stageCalls[dr::stage];
    if (limitCalls && calls > limitCalls) die("RUNAWAY", "call limit", 4);
    verifyMirror();
}

bool move(int dir) {
    enter(); ++moveCalls;
    static const int dx[6] = {1, -1, 0, 0, 0, 0}, dy[6] = {0, 0, 1, -1, 0, 0}, dz[6] = {0, 0, 0, 0, 1, -1};
    if (dir < 0 || dir >= 6) return false;
    int x = ax + dx[dir], y = ay + dy[dir], z = az + dz[dir];
    if (x < 0 || y < 0 || z < 0 || x >= NN || y >= NN || z >= NN) return false;
    int h = cellH[y][x];
    if (ahold < 0 ? z < h : z <= h) return false;
    ax = x; ay = y; az = z;
    return true;
}
bool pick(int& destX, int& destY, int& weight) {
    enter(); ++picks;
    if (ahold >= 0) return false;
    int h = cellH[ay][ax];
    if (h == 0 || h != az) return false;
    ahold = cellBox[ay][ax][--cellH[ay][ax]];
    destX = boxesArr[ahold].dx; destY = boxesArr[ahold].dy; weight = boxesArr[ahold].w;
    return true;
}
static void dumpScratch(int cx, int cy) {
    int j = 0;
    for (int dy = -1; dy <= 1; ++dy) for (int dx = -1; dx <= 1; ++dx) {
        int x = cx + dx, y = cy + dy;
        if ((!dx && !dy) || x < 0 || y < 0 || x >= NN || y >= NN) continue;
        printf("DUMP %d", j++);
        for (int h = 0; h < cellH[y][x]; ++h) printf(" %d", boxesArr[cellBox[y][x][h]].w);
        printf("\n");
    }
}
bool drop() {
    enter(); ++drops;
    int h = cellH[ay][ax];
    if (h == NN - 2 || h != az - 1 || ahold < 0) return false;
    cellBox[ay][ax][h] = ahold; ++cellH[ay][ax]; ahold = -1;
    if (dumpAt && drops == dumpAt) dumpScratch(5, 5);
    return true;
}

static unsigned long long rs;
static int rnd() { rs = rs * 6364136223846793005ULL + 1442695040888963407ULL; return (int)((rs >> 33) & 0x3fffffff); }

static void generate(int bpc, bool skew) {
    memset(cellH, 0, sizeof cellH);
    totalBoxes = bpc * NN * NN;
    int area = skew ? (NN * 3) / 5 : NN;               // skew: every source lies in a 60% x 60% corner
    for (int i = 0; i < totalBoxes; ++i) {
        int sx = rnd() % area, sy = rnd() % area;
        boxesArr[i] = {rnd() % NN, rnd() % NN, rnd() % 1000 + 1};
        if (cellH[sy][sx] == NN - 2) { --i; continue; }
        cellBox[sy][sx][cellH[sy][sx]++] = i;
    }
    ax = ay = az = NN - 1; ahold = -1;
}

static bool finalOk() {
    int cnt = 0;
    for (int y = 0; y < NN; ++y) for (int x = 0; x < NN; ++x) {
        for (int h = 0; h < cellH[y][x]; ++h) {
            const Box& b = boxesArr[cellBox[y][x][h]];
            if (b.dx != x || b.dy != y) return false;
            if (h > 0 && b.w > boxesArr[cellBox[y][x][h - 1]].w) return false;
            ++cnt;
        }
    }
    return cnt == totalBoxes && ahold < 0;
}

extern void process();

int main(int argc, char** argv) {
    const char* mode = argv[1];
    if (!strcmp(mode, "run")) {                         // run <seed> <boxes per cell> <TCs> <skew> <check> <limit>
        long long seed = atoll(argv[2]);
        int bpc = atoi(argv[3]), ntc = atoi(argv[4]);
        bool skew = atoi(argv[5]) != 0;
        checking = atoi(argv[6]) != 0;
        limitCalls = atoll(argv[7]);
        for (int tc = 1; tc <= ntc; ++tc) {
            rs = seed * 7919ULL + tc * 104729ULL + 13;
            generate(bpc, skew);
            calls = stageCalls[0] = stageCalls[1] = stageCalls[2] = 0;
            process();
            verifyMirror(true);
            bool ok = finalOk();
            printf("TC %d CALLS %lld S0 %lld S1 %lld S2 %lld REFUSED %d MISMATCH %d DEFERRED %d FALLBACKS %d VALID %d\n",
                   tc, calls, stageCalls[0], stageCalls[1], stageCalls[2], dr::refused, dr::mismatch, dr::deferred,
                   dr::fallbacks, ok ? 1 : 0);
            if (!ok) return 5;
        }
    } else if (!strcmp(mode, "sortdemo")) {             // one cell, seven known weights, nothing else in the warehouse
        static const int w[7] = {4, 9, 2, 7, 7, 3, 8};
        memset(cellH, 0, sizeof cellH);
        for (int i = 0; i < 7; ++i) {
            boxesArr[i] = {5, 5, w[i]};
            cellBox[5][5][i] = i;
            dr::bd[5][5][i] = 5 * NN + 5; dr::bw[5][5][i] = w[i];
        }
        cellH[5][5] = dr::H[5][5] = 7; dr::orig[5][5] = 0;
        totalBoxes = 7;
        ax = dr::px = 5; ay = dr::py = 5; az = dr::pz = 7; ahold = -1; dr::hold = false; dr::stage = 2;
        dumpAt = 7;
        dr::sortCell(5, 5);
        verifyMirror(true);
        printf("SORT picks %lld drops %lld moves %lld\nORDER", picks, drops, moveCalls);
        for (int h = 0; h < cellH[5][5]; ++h) printf(" %d", boxesArr[cellBox[5][5][h]].w);
        printf("\nVALID %d\n", finalOk() ? 1 : 0);
    } else if (!strcmp(mode, "flight")) {               // heights of a 4 x 2 patch, drone carries a box from (0,0,4)
        static const int hts[2][4] = {{3, 6, 2, 4}, {2, 2, 8, 1}};
        memset(cellH, 0, sizeof cellH);
        int id = 0;
        for (int y = 0; y < 2; ++y) for (int x = 0; x < 4; ++x) {
            for (int h = 0; h < hts[y][x]; ++h) { boxesArr[id] = {0, 0, 1}; cellBox[y][x][h] = id++; }
            cellH[y][x] = dr::H[y][x] = hts[y][x];
        }
        boxesArr[id] = {0, 0, 1};
        ahold = id; dr::hold = true;
        ax = dr::px = 0; ay = dr::py = 0; az = dr::pz = 4; dr::stage = 2;
        checking = false;
        dr::goTo(3, 1, 2);
        printf("FLIGHT moves %lld refused %d pos %d %d %d\n", moveCalls, dr::refused, ax, ay, az);
    }
    return 0;
}
'''


def build(code: str, folder: Path, name: str, extra: list[str]) -> Path:
    src, exe = folder / f"{name}.cpp", folder / name
    src.write_text(code + "\n" + HARNESS)
    compile_to(exe, [src], extra)
    return exe


def run(exe: Path, *args: object, ok_codes: tuple[int, ...] = (0,), timeout: int = 300) -> subprocess.CompletedProcess:
    res = subprocess.run([str(exe), *map(str, args)], capture_output=True, text=True, timeout=timeout)
    assert res.returncode in ok_codes, (res.returncode, res.stdout[-300:], res.stderr[-300:])
    return res


TC_RE = re.compile(r"^TC (\d+) CALLS (\d+) S0 (\d+) S1 (\d+) S2 (\d+) REFUSED (\d+) MISMATCH (\d+) DEFERRED (\d+) FALLBACKS (\d+) VALID (\d)$", re.M)


def parse_tcs(text: str) -> list[dict]:
    keys = ("tc", "calls", "s0", "s1", "s2", "refused", "mismatch", "deferred", "fallbacks", "valid")
    return [dict(zip(keys, map(int, m))) for m in TC_RE.findall(text)]


# ---------------------------------------------------------------- reference checks
# (N, boxes per cell): small warehouses leave height room for the algorithm's temporary stacking
CONFIGS = [(12, 1), (16, 2), (20, 3), (24, 3), (30, 4)]


def check_reference(sn: dict[str, str], tmp: Path) -> dict:
    summary = {"tcs": 0, "deferred": 0, "fallbacks": 0}
    jobs = {}
    with concurrent.futures.ThreadPoolExecutor() as pool:
        for n, bpc in CONFIGS:
            jobs[(n, bpc, "2단계")] = pool.submit(build, assemble(sn, n=n), tmp, f"ref_{n}", SAN)
        for label, edits in STAGES.items():
            if label != "2단계":
                jobs[(20, 3, label)] = pool.submit(build, assemble(sn, edits, n=20), tmp, f"stage_{label[0]}", SAN)
        for i, (label, edits) in enumerate(VARIANTS.items()):
            jobs[(16, 2, label)] = pool.submit(build, assemble(sn, edits, n=16), tmp, f"var_{i}", SAN)
        exes = {k: f.result() for k, f in jobs.items()}
    for (n, bpc, label), exe in exes.items():
        for seed in (1, 2):
            tcs = parse_tcs(run(exe, "run", seed, bpc, 3, 0, 1, 20000000).stdout)    # 3 chained TCs, mirror checked per call
            assert len(tcs) == 3, (n, bpc, label)
            for t in tcs:
                assert t["valid"] == 1 and t["refused"] == 0 and t["mismatch"] == 0, (n, bpc, label, t)
                summary["tcs"] += 1; summary["deferred"] += t["deferred"]; summary["fallbacks"] += t["fallbacks"]
    # skewed sources: a corner region holds all the boxes at the start
    exe = exes[(30, 4, "2단계")]
    tcs = parse_tcs(run(exe, "run", 3, 2, 2, 1, 1, 20000000).stdout)
    assert all(t["valid"] == 1 and t["refused"] == 0 and t["mismatch"] == 0 for t in tcs) and len(tcs) == 2
    assert summary["deferred"] > 0, "the interleaving case (a box destined for the neighbor q) was never exercised"
    assert summary["fallbacks"] > 0, "the insertion fallback was never exercised"
    print(f"OK: reference simulator: {summary['tcs']} TCs on {len(CONFIGS)} warehouse sizes and 5 stage variants, "
          f"mirror == real state before every call, valid, refused 0 "
          f"(neighbor-destined boxes met {summary['deferred']} times, insertion fallback {summary['fallbacks']} times)")
    return summary


FAILURES = {
    "높이 갱신 누락": [(r"int h = H\[py\]\[px\]\+\+;", "int h = H[py][px];")],
    "맡긴 칸의 상자 가정": [(r"else \{ goTo\(rx, ry, H\[ry\]\[rx\] \+ 1\); \+\+moved; \}[^\n]*", "else goTo(cx, cy, H[cy][cx] + 1);")],
    "TC 시작 위치 초기화 누락": [(r"px = py = pz = N - 1; hold = false;[^\n]*", ""), (r"int px, py, pz;", "int px = N - 1, py = N - 1, pz = N - 1;")],
    "병합에서 가벼운 윗면 먼저": [(r"int best = -1, bt = -1;", "int best = -1, bt = 1001;"), (r"if \(w > bt\)", "if (w < bt)")],
}


def check_failures(sn: dict[str, str], tmp: Path) -> dict:
    found = {}
    with concurrent.futures.ThreadPoolExecutor() as pool:
        futs = {name: pool.submit(build, assemble(sn, edits, n=16), tmp, f"bad_{i}", ["-O1"])
                for i, (name, edits) in enumerate(FAILURES.items())}
        exes = {name: f.result() for name, f in futs.items()}
    for name, exe in exes.items():
        res = run(exe, "run", 1, 2, 3, 0, 1, 3000000, ok_codes=(0, 3, 4, 5))
        tcs = parse_tcs(res.stdout)
        fail = re.search(r"^FAIL (\w+) (\w+)", res.stdout, re.M)
        detected = bool(fail) or res.returncode == 5 or any(t["refused"] or t["mismatch"] or not t["valid"] for t in tcs)
        assert detected, f"failure variant not detected: {name}"
        found[name] = fail.group(0) if fail else f"exit {res.returncode}"
    expect = {"높이 갱신 누락": "FAIL MIRROR height", "맡긴 칸의 상자 가정": "exit 5",
              "TC 시작 위치 초기화 누락": "FAIL MIRROR position", "병합에서 가벼운 윗면 먼저": "exit 5"}
    assert found == expect, found                      # the lesson table says where each one is caught
    print("OK: failure variants detected:", "; ".join(f"{k} -> {v}" for k, v in found.items()))
    # the one that needs more than one TC to show: the position mirror survives only if it is reset per TC
    exe = exes["TC 시작 위치 초기화 누락"]
    first = run(exe, "run", 1, 2, 1, 0, 1, 3000000, ok_codes=(0, 3, 4, 5))
    assert parse_tcs(first.stdout) and parse_tcs(first.stdout)[0]["valid"] == 1, "TC 1 alone must still be fine"
    return found


# ---------------------------------------------------------------- hand-calculated examples
SORT_STACKS = {0: [8, 9], 1: [3, 7, 7], 2: [2, 4]}
SORT_ORDER = [9, 8, 7, 7, 4, 3, 2]


def check_hand(sn: dict[str, str], tmp: Path, need_text: bool = True) -> dict:
    exe = build(assemble(sn, n=20), tmp, "hand_sort", SAN)
    out = run(exe, "sortdemo").stdout
    dump = {int(j): list(map(int, rest.split())) for j, rest in re.findall(r"^DUMP (\d+)[ \t]*(.*)$", out, re.M)}
    got = {j: v for j, v in dump.items() if v}
    assert got == SORT_STACKS, got
    picks = int(re.search(r"SORT picks (\d+) drops (\d+)", out).group(1))
    order = list(map(int, re.search(r"^ORDER (.*)$", out, re.M).group(1).split()))
    assert order == SORT_ORDER and picks == 14 and "VALID 1" in out, out
    ins = build(assemble(sn, [flag("PATIENCE", False)], n=20), tmp, "hand_ins", SAN)
    out2 = run(ins, "sortdemo").stdout
    ins_picks = int(re.search(r"SORT picks (\d+)", out2).group(1))
    assert list(map(int, re.search(r"^ORDER (.*)$", out2, re.M).group(1).split())) == SORT_ORDER
    # independent count: the insertion sort moves k - keep boxes out, then 2*j + 1 per box
    w = [4, 9, 2, 7, 7, 3, 8]
    keep = 1
    while keep < 7 and w[keep] <= w[keep - 1]:
        keep += 1
    sorted_part = w[:keep]
    want = 7 - keep
    pending = list(w[keep:])                            # they were moved top-first so pending[0] is taken first
    for x in pending:
        j = sum(1 for y in sorted_part if y < x)
        want += 2 * j + 1
        sorted_part = sorted(sorted_part + [x], reverse=True)
    assert ins_picks == want, (ins_picks, want)
    fl = build(assemble(sn), tmp, "hand_fly", ["-O1"])
    terrain = run(fl, "flight").stdout
    fixed = run(build(assemble(sn, [flag("TERRAIN", False)]), tmp, "hand_fly0", ["-O1"]), "flight").stdout
    # hand calculation: x first needs 7, y first needs 9; 3 up + 4 across + 5 down = 12 moves
    assert "FLIGHT moves 12 refused 0 pos 3 1 2" in terrain, terrain
    assert "FLIGHT moves 196 refused 0 pos 3 1 2" in fixed, fixed
    if need_text:
        text = read_lesson_text(LESSON_ID)
        for needle in ("14번", str(ins_picks) + "번", "12번", "196번"):
            assert needle in text, f"hand example number missing from lesson: {needle}"
    print(f"OK: hand examples: patience 14 shifts -> {SORT_ORDER}, insertion {ins_picks} shifts, flight 12 moves terrain-following vs 196 at z=99")
    return {"patience": 14, "insertion": ins_picks, "terrain": 12, "fixed": 196}


# ---------------------------------------------------------------- public grader
def patched_judge(judge: Path, folder: Path, seed: int = 5) -> Path:
    text = judge.read_text()

    def once(old: str, new: str) -> None:
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new)

    once("static unsigned long long seed = 5;", f"static unsigned long long seed = {seed};")
    once("extern void process();",
         "namespace dr { extern int stage, refused, mismatch, deferred, fallbacks; }\n"
         "static long long gCalls[3][4];\n"
         "static long long lowerBound() {\n"
         "    long long sum = 0;\n"
         "    for (int y = 0; y < MAX_N; y++) for (int x = 0; x < MAX_N; x++) for (int h = 0; h < gBoxHeight[y][x]; h++) {\n"
         "        const BoxInfo* b = gBox[h][y][x];\n"
         "        int d = (b->destX > x ? b->destX - x : x - b->destX) + (b->destY > y ? b->destY - y : y - b->destY);\n"
         "        if (d > 0) sum += d + 2;\n"
         "    }\n"
         "    return sum;\n"
         "}\n"
         "extern void process();")
    once("bool move(int dir) {\n    gTotalScore++;", "bool move(int dir) {\n    gTotalScore++; gCalls[dr::stage][dir >= 4 ? 1 : 0]++;")
    once("bool pick(int& destX, int& destY, int& weight) {\n    gTotalScore++;", "bool pick(int& destX, int& destY, int& weight) {\n    gTotalScore++; gCalls[dr::stage][2]++;")
    once("bool drop() {\n    gTotalScore++;", "bool drop() {\n    gTotalScore++; gCalls[dr::stage][3]++;")
    once("        process();\n",
         "        printf(\"TC %d LB %lld\\n\", tc + 1, lowerBound());\n"
         "        for (auto& r : gCalls) for (auto& c : r) c = 0;\n"
         "        process();\n"
         "        printf(\"TC %d STATE refused %d mismatch %d deferred %d fallbacks %d\\n\", tc + 1, dr::refused, dr::mismatch, dr::deferred, dr::fallbacks);\n"
         "        printf(\"TC %d CALLS\", tc + 1);\n"
         "        for (auto& r : gCalls) for (auto& c : r) printf(\" %lld\", c);\n"
         "        printf(\"\\n\");\n")
    path = folder / f"judge_patched_{seed}.cpp"
    path.write_text(text)
    return path


def parse_judge(text: str) -> dict:
    score = {int(a): int(b) for a, b in re.findall(r"^TC (\d+) SCORE: (-?\d+)$", text, re.M)}
    lb = {int(a): int(b) for a, b in re.findall(r"^TC (\d+) LB (\d+)$", text, re.M)}
    state = {int(a): tuple(map(int, rest)) for a, *rest in re.findall(r"^TC (\d+) STATE refused (\d+) mismatch (\d+) deferred (\d+) fallbacks (\d+)$", text, re.M)}
    calls = {int(m.group(1)): list(map(int, m.group(2).split())) for m in re.finditer(r"^TC (\d+) CALLS ([\d ]+)$", text, re.M)}
    total = re.search(r"^SCORE: (\d+)$", text, re.M)
    ms = re.search(r"^Result : (\d+)$", text, re.M)
    return {"score": score, "lb": lb, "state": state, "calls": calls,
            "total": int(total.group(1)) if total else None, "ms": int(ms.group(1)) if ms else None}


def judge_run(judge_src: Path, code: str, folder: Path, name: str, flags: list[str], repeat: int = 1, timeout: int = 120) -> dict:
    user = folder / f"{name}.cpp"
    exe = folder / name
    user.write_text(code)
    compile_to(exe, [judge_src, user], flags)
    results = []
    for _ in range(repeat):
        res = subprocess.run([str(exe)], capture_output=True, text=True, timeout=timeout)
        results.append(parse_judge(res.stdout))
    first = results[0]
    assert all(r["score"] == first["score"] for r in results)
    first["wall_runs"] = None
    return first


def timed_run(exe: Path, repeat: int, timeout: int = 120) -> list[float]:
    import time
    out = []
    for _ in range(repeat):
        t = time.perf_counter()
        subprocess.run([str(exe)], capture_output=True, text=True, timeout=timeout)
        out.append(round(time.perf_counter() - t, 2))
    return out


def measure(judge: Path, sn: dict[str, str]) -> dict:
    result = {"date": datetime.date.today().isoformat(), "platform": platform.platform(), "machine": platform.machine(),
              "compiler": subprocess.run(["c++", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
              "flags": "-std=c++17 -O2", "judge_sha256": hashlib.sha256(judge.read_bytes()).hexdigest(),
              "stages": [], "experiments": [], "failures": [], "own": []}
    with tempfile.TemporaryDirectory(prefix="lesson-drone-judge-") as tmp:
        folder = Path(tmp)
        src = {s: patched_judge(judge, folder, s) for s in SEEDS}

        def record(label: str, edits, seed: int = 5, name: str = "m", repeat_time: int = 0) -> dict:
            r = judge_run(src[seed], assemble(sn, edits), folder, f"{name}_{seed}", ["-O2"])
            tcs = [r["score"][t] for t in sorted(r["score"])]
            row = {"label": label, "seed": seed, "total": r["total"], "tcs": tcs,
                   "lb_total": sum(r["lb"].values()),
                   "refused": sum(v[0] for v in r["state"].values()), "mismatch": sum(v[1] for v in r["state"].values()),
                   "deferred": sum(v[2] for v in r["state"].values()), "fallbacks": sum(v[3] for v in r["state"].values()),
                   "phase": [[sum(r["calls"][t][s * 4 + k] for t in r["calls"]) for k in range(4)] for s in range(3)]}
            if repeat_time:
                row["wall_s"] = timed_run(folder / f"{name}_{seed}", repeat_time)
            print(json.dumps({k: row[k] for k in ("label", "seed", "total", "refused", "mismatch")}), flush=True)
            return row

        for label, edits in STAGES.items():
            result["stages"].append(record(label, edits, repeat_time=3))
        for seed in SEEDS:
            for label in ("1단계", "2단계"):
                result["experiments"].append(record(label, STAGES[label], seed))
            for label, edits in VARIANTS.items():
                result["experiments"].append(record(label, edits, seed))
        for name, edits in FAILURES.items():
            code = assemble(sn, edits)
            user = folder / "bad.cpp"
            user.write_text(code)
            exe = folder / "bad"
            compile_to(exe, [src[5], user], ["-O2"])
            try:
                res = subprocess.run([str(exe)], capture_output=True, text=True, timeout=20)
                p = parse_judge(res.stdout)
                first_bad = next((t for t in sorted(p["score"]) if p["score"][t] >= 10 ** 13), None)
                result["failures"].append({"label": name, "outcome": "penalty", "first_bad_tc": first_bad,
                                           "scores": [p["score"][t] for t in sorted(p["score"])], "total": p["total"]})
            except subprocess.TimeoutExpired:
                result["failures"].append({"label": name, "outcome": "timeout", "seconds": 20})
            print(json.dumps(result["failures"][-1], ensure_ascii=False), flush=True)
        for label in ("기준선", "2단계"):               # sanitizer pass on the public grader
            judge_run(src[5], assemble(sn, STAGES[label]), folder, "san", SAN, timeout=3000)
        result["sanitizer"] = "기준선과 2단계가 공개 채점기에서 ASan+UBSan을 통과"
        # own input: a warehouse the public generator never makes (skewed sources), reference simulator at full size
        for label in ("1단계", "2단계"):
            exe = build(assemble(sn, STAGES[label]), folder, f"own_{label[0]}", ["-O2"])
            tcs = parse_tcs(run(exe, "run", 7, 10, 3, 1, 0, 0, timeout=900).stdout)
            assert all(t["valid"] == 1 and t["refused"] == 0 and t["mismatch"] == 0 for t in tcs), label
            result["own"].append({"label": label, "calls": [t["calls"] for t in tcs], "boxes_per_cell": 10, "skew": True})
            print(json.dumps(result["own"][-1], ensure_ascii=False), flush=True)
    return result


def recheck_judge(judge: Path, sn: dict[str, str], data: dict) -> None:
    assert hashlib.sha256(judge.read_bytes()).hexdigest() == data["judge_sha256"], "judge file differs from the measured one"
    with tempfile.TemporaryDirectory(prefix="lesson-drone-judge-") as tmp:
        folder = Path(tmp)
        src = patched_judge(judge, folder, 5)
        for row in data["stages"]:
            r = judge_run(src, assemble(sn, STAGES[row["label"]]), folder, "m", ["-O2"])
            assert [r["score"][t] for t in sorted(r["score"])] == row["tcs"] and r["total"] == row["total"], row["label"]
            assert all(v[0] == 0 and v[1] == 0 for v in r["state"].values())
        for label in ("기준선", "2단계"):
            judge_run(src, assemble(sn, STAGES[label]), folder, "san", SAN, timeout=3000)
    print("OK: public grader re-run reproduces the stored stage scores (refused 0, mismatch 0), ASan/UBSan clean")


# ---------------------------------------------------------------- tables vs JSON
def fmt(n: int) -> str:
    return f"{n:,}"


def eok_pass() -> int:
    return 250_000_000


CATCH = {"높이 갱신 누락": "첫 호출 직전의 높이 대조", "맡긴 칸의 상자 가정": "최종 상태 검증",
         "TC 시작 위치 초기화 누락": "TC 2 첫 호출 직전의 위치 대조", "병합에서 가벼운 윗면 먼저": "최종 상태 검증"}
NAMES = ["높이 재기", "비우기", "정렬"]


def derived(data: dict) -> tuple[dict[str, str], list[str]]:
    """Every number the lesson quotes from the measurements, as the strings the text must contain."""
    st = {r["label"]: r for r in data["stages"]}
    exp: dict[str, list[int]] = {}
    for r in data["experiments"]:
        exp.setdefault(r["label"], []).append(r["total"])
    lb = st["2단계"]["lb_total"]
    p = eok_pass()
    v = {"LB": fmt(lb), "PASSX": f"{p / lb:.1f}", "DEFERRED": str(st["2단계"]["deferred"]), "DATE": data["date"],
         "MARGIN": fmt(p - st["2단계"]["total"]), "XLB": f"{st['2단계']['total'] / lb:.1f}",
         "R01": f"{st['기준선']['total'] / st['1단계']['total']:.1f}", "PERBOX1": f"{st['1단계']['total'] / 1_000_000:.0f}"}
    for i, lab in enumerate(("기준선", "1단계", "2단계")):
        r = st[lab]
        v[f"T{i}"] = fmt(r["total"]); v[f"X{i}"] = f"{r['total'] / p:.2f}"
        v[f"W{i}"] = f"{statistics.median(r['wall_s']):.2f}"
    v["SORT_SHARE1"] = f"{100 * sum(st['1단계']['phase'][2]) / st['1단계']['total']:.0f}"
    v["SHARE_CLEAR"] = f"{100 * st['2단계']['phase'][1][0] / st['2단계']['total']:.0f}"
    lines = []
    for lab in ("기준선", "1단계", "2단계"):
        for s_i, nm in enumerate(NAMES):
            hz, vt, pk, dr = st[lab]["phase"][s_i]
            lines.append(f"| {lab} · {nm} | {fmt(hz)} | {fmt(vt)} | {fmt(pk + dr)} | {fmt(hz + vt + pk + dr)} |")
    spreads = []
    for lab in ("2단계", "x 먼저만", "임시 칸 4개"):
        vals = sorted(exp[lab])
        assert len(vals) == len(SEEDS), lab
        spreads.append(vals[-1] - vals[0])
        lines.append(f"| {lab} | {fmt(int(statistics.median(vals)))} | {fmt(vals[0])} | {fmt(vals[-1])} |")
    v["SPREAD"] = fmt(max(spreads))
    med = {lab: int(statistics.median(vals)) for lab, vals in exp.items()}
    for key, lab in (("DCP", "x 먼저만"), ("DDIAG", "임시 칸 4개")):
        v[key] = f"{fmt(med[lab] - med['2단계'])}({100 * (med[lab] - med['2단계']) / med['2단계']:.1f}%)"
    for r in data["own"]:
        lines.append(f"| {r['label']} (직접 만든 입력) | " + " | ".join(fmt(c) for c in r["calls"]) + " |")
    for r in data["failures"]:
        if r["outcome"] == "timeout":
            res = f"timeout: {r['seconds']}초 안에 끝나지 않음"
        else:
            res = f"TC {r['first_bad_tc']}에서 10,000,000,000,000점" + ("" if r["first_bad_tc"] == 1 else f" (TC 1은 {fmt(r['scores'][0])})")
        lines.append(f"| {r['label']} | {res} | {CATCH[r['label']]} |")
    return v, lines


def check_tables(data: dict, hand: dict, ref: dict) -> None:
    text = read_lesson_text(LESSON_ID)
    v, lines = derived(data)
    for line in lines:
        assert line in text.splitlines(), f"lesson table row missing or stale: {line}"
    for key, value in v.items():
        assert value in text, f"lesson text missing {key}: {value}"
    for key in ("tcs", "deferred", "fallbacks"):
        assert str(ref[key]) in text, f"reference-check count {key}={ref[key]} not in lesson"
    st = {r["label"]: r for r in data["stages"]}
    # the claims the lesson makes in words
    base, one, two = (st[k] for k in ("기준선", "1단계", "2단계"))
    assert base["total"] > 12 * eok_pass() and two["total"] <= eok_pass() < one["total"], "stage ordering/threshold claims"
    assert all(r["refused"] == 0 and r["mismatch"] == 0 for r in data["stages"] + data["experiments"])
    assert sum(base["phase"][1][:2]) < sum(base["phase"][2][:2]) and base["phase"][2][1] / base["total"] > 0.7
    assert statistics.median(base["wall_s"]) > 10, "the lesson says the baseline exceeds the 10 s limit here"
    assert one["phase"][1] == two["phase"][1] and one["phase"][2] != two["phase"][2], "stage 2 must only change the sorting part"
    own = {r["label"]: r["calls"] for r in data["own"]}
    assert all(b < a for a, b in zip(own["1단계"], own["2단계"])), "2단계 must beat 1단계 on each own TC"
    by = {}
    for r in data["experiments"]:
        by.setdefault(r["label"], []).append(r["total"])
    assert min(by["x 먼저만"]) > max(by["2단계"]) and min(by["임시 칸 4개"]) > max(by["2단계"]), "variants must beat the seed spread"
    assert two["fallbacks"] > 0 and 80 <= two["deferred"] <= 90
    hub_rows = check_hub_summary(LESSON_ID, [(lab, fmt(st[lab]["total"])) for lab in ("기준선", "1단계", "2단계")])
    print(f"OK: hub summary table matches the stored stage totals ({hub_rows} rows)")
    print(f"OK: lesson tables and quoted numbers match {DATA.name}")


def check_svgs() -> None:
    text = read_lesson_text(LESSON_ID)
    svgs = sorted((ROOT / "lessons/remember-and-sort/lesson-assets").glob("*.svg"))
    assert len(svgs) == 2, svgs
    for svg in svgs:
        body = svg.read_text()
        assert 'role="img"' in body and "<title" in body and "<desc" in body and 'viewBox="0 0 720 ' in body, svg.name
        sizes = [float(x) for x in re.findall(r'font-size="([\d.]+)"', body)]
        assert sizes and min(sizes) >= 16 and max(sizes) <= 28, (svg.name, min(sizes), max(sizes))
        desc = re.search(r"<desc[^>]*>(.*?)</desc>", body, re.S).group(1)
        assert "[" not in desc and "]" not in desc
        assert f"lesson-assets/{svg.name}" in text and f"https://git.readiz.com/h-contest-lesson/lessons/remember-and-sort/lesson-assets/{svg.name}" in text, svg.name
    for alt in re.findall(r"!\[([^\]]*)\]\((?:\.\./)?lesson-assets/", text):
        assert "[" not in alt and "]" not in alt and len(alt) > 30
    st = {r["label"]: r["total"] for r in json.loads(DATA.read_text())["stages"]}
    stage_svg = (ROOT / "lessons/remember-and-sort/lesson-assets/stage-scores.svg").read_text()
    for label in ("기준선", "1단계", "2단계"):                        # the figure quotes the measured totals in 억/만
        a, b = divmod(round(st[label] / 10000), 10000)
        assert f"{a}억 {b}만" in stage_svg, (label, a, b)
    print("OK: two figures have role/title/desc, width 720, font sizes 16~28, a large-view link, and the measured totals")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", type=Path, help="DRONESORT main.cpp (optional)")
    parser.add_argument("--output", type=Path, help="write fresh measurements (needs --judge)")
    args = parser.parse_args()
    sn = snippets()
    fresh = bool(args.judge and args.output)
    with tempfile.TemporaryDirectory(prefix="lesson-drone-") as t:
        tmp = Path(t)
        ref = check_reference(sn, tmp)
        check_failures(sn, tmp)
        hand = check_hand(sn, tmp, need_text=not fresh)
    if fresh:
        data = measure(args.judge, sn)
        args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        return
    data = json.loads(DATA.read_text())
    if args.judge:
        recheck_judge(args.judge, sn, data)
    check_tables(data, hand, ref)
    check_svgs()


if __name__ == "__main__":
    main()
