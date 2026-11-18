"""Check the observe-and-act (MINEEXPLORE) lesson: code blocks, hand example, failures, measurements.

Without --judge only the checks that need no grader run: header-free assembly, a
reference grader written for this check, mirror/score agreement, chained-TC
independence, BFS gain against an independent DP, the hand-calculated example,
and agreement between the lesson tables and the stored measurement JSON.

With --judge /path/to/main.cpp the public grader is compiled with a local patch
(logging only) and the scores in the JSON are re-measured. --output rewrites the
JSON (scores, times, sweeps, failures, calibration) from a fresh measurement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import statistics
import subprocess
import tempfile
import datetime

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "lessons/observe-and-act/lesson.md"
DATA = ROOT / "lessons/observe-and-act/lesson-assets/measurements.json"
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from cpp_library import check_submission_code, read_library_snippets  # noqa: E402

SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
SAN = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-g", "-O1"]


def snippets() -> dict[str, str]:
    found: dict[str, str] = {}
    for name, code in SNIP_RE.findall(LESSON.read_text()):
        assert name not in found, f"duplicate snippet {name}"
        check_submission_code(code, name)
        found[name] = code
    for name in ("mine-state", "mine-baseline", "mine-reach", "mine-policy", "mine-entry"):
        assert name in found, f"missing snippet {name}"
    return found


def assemble(kind: str, sn: dict[str, str], edits: list[tuple[str, str]] | None = None) -> str:
    queue = read_library_snippets()["queue"]
    state, reach, policy, entry = sn["mine-state"], sn["mine-reach"], sn["mine-policy"], sn["mine-entry"]
    for old, new in edits or []:
        hit = False
        for i, part in enumerate((state, reach, policy, entry)):
            if re.search(old, part):
                part = re.sub(old, new, part, count=1)
                if i == 0: state = part
                elif i == 1: reach = part
                elif i == 2: policy = part
                else: entry = part
                hit = True
                break
        assert hit, f"edit target not found: {old}"
    if kind == "baseline":
        return state + "\n" + sn["mine-baseline"] + "\n"
    if kind in ("policy1", "policy2"):
        entry = re.sub(r"const int POLICY = \d;", f"const int POLICY = {kind[-1]};", entry)
        return "\n".join([queue, state, reach, policy, entry]) + "\n"
    raise ValueError(kind)


def with_param(sn: dict[str, str], name: str, value: str) -> list[tuple[str, str]]:
    return [(rf"(const (?:int|double) {name} = )[\d.]+;", rf"\g<1>{value};")]


def compile_to(exe: Path, sources: list[Path], extra: list[str]) -> None:
    subprocess.run(["c++", "-std=c++17", *extra, *map(str, sources), "-o", str(exe)], check=True)


# ---------------------------------------------------------------- reference grader
REF = r'''
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cassert>
#include <vector>
#include <algorithm>
#include <string>

static int gMap[30][30], gBak[30][30];
static bool gVis[30][30];
static int gY, gX, gDay, gToday, gTc;
static bool gInvalid;
static long long gScore;
void move(int dir) {
    if (gInvalid) return;
    if (dir < 0 || dir > 3 || gToday >= 10) { gInvalid = true; return; }
    int ny = gY + mine::DY[dir], nx = gX + mine::DX[dir];
    if (ny < 0 || ny >= 30 || nx < 0 || nx >= 30) { gInvalid = true; return; }
    gY = ny; gX = nx; ++gToday;
    if (!gVis[gY][gX]) { gVis[gY][gX] = true; gScore += gMap[gY][gX]; }
}
void nextDay(void) {
    if (gInvalid) return;
    if (gDay >= 10) { gInvalid = true; return; }
    ++gDay; gToday = 0;
}
static unsigned long long seed;
static int rnd() { seed = seed * 6364136223846793005ULL + 1442695040888963407ULL; return (int)((seed >> 33) & 0x3fffffff); }
static void make(char kind, int s, int& sy, int& sx) {
    seed = s * 7919ULL + 13; memset(gMap, 0, sizeof gMap);
    sy = rnd() % 30; sx = rnd() % 30;
    if (kind == 'z') return;
    for (int y = 0; y < 30; ++y) for (int x = 0; x < 30; ++x) if (rnd() % 100 >= 70) gMap[y][x] = rnd() % 10 + 1;
    int peaks = 6 + rnd() % 5;
    for (int p = 0; p < peaks; ++p) {
        int py = rnd() % 30, px = rnd() % 30, r = 4 + rnd() % 4, h = 80 + rnd() % 121;
        for (int y = 0; y < 30; ++y) for (int x = 0; x < 30; ++x) {
            int d2 = (y - py) * (y - py) + (x - px) * (x - px);
            if (d2 > r * r) continue;
            gMap[y][x] = std::max(gMap[y][x], h * (r * r - d2) / (r * r) + rnd() % 9);
        }
    }
    if (kind == 'c') { sy = 0; sx = 0; }
    if (kind == 'e') { sy = 29; sx = 29; }
    gMap[sy][sx] = 0;
}
static void hook(int d, int g, int a) { printf("LOG %d %d %d %d\n", gTc, d, g, a); }
static void startCase(int tc) {
    memcpy(gBak, gMap, sizeof gMap); memset(gVis, 0, sizeof gVis);
    gDay = 1; gToday = 0; gInvalid = false; gScore = 0; gTc = tc;
}
static void runOne(int tc, char kind, int s) {
    int sy, sx; make(kind, s, sy, sx);
    startCase(tc); gY = sy; gX = sx; gVis[sy][sx] = true;
    mine::hook = hook;
    process(gBak, sy, sx);
    printf("TC %d SCORE: %lld\n", tc, gInvalid ? 0LL : gScore);
    printf("TC %d MIRROR %lld REFUSED %d\n", tc, mine::mirrorScore, mine::refused);
}
static int runHand() {
    memset(gMap, 0, sizeof gMap);
    gMap[1][1] = 3; gMap[2][2] = 2; gMap[0][0] = 2; gMap[2][5] = 40; gMap[2][6] = 60;
    return 0;
}
int main(int argc, char** argv) {
    std::string mode = argv[1];
    if (mode == "run") {
        for (int i = 2; i < argc; ++i) runOne(i - 1, argv[i][0], atoi(argv[i] + 2));
#ifdef HAS_POLICY
    } else if (mode == "reach") {
        // BFS gain against an independent DP over the bounding rectangle.
        for (int t = 0; t < 40; ++t) {
            int sy, sx; make('h', t, sy, sx);
            memcpy(gBak, gMap, sizeof gMap);
            mine::resetCase(gBak, sy, sx);
            for (int k = 0; k < 150; ++k) mine::M.seen[rnd() % 30][rnd() % 30] = true;
            mine::M.seen[sy][sx] = true;
            mine::M.movesLeft = 1 + rnd() % 100;
            mine::bfs();
            for (int y = 0; y < 30; ++y) for (int x = 0; x < 30; ++x) {
                int d = abs(y - sy) + abs(x - sx);
                if (d > mine::M.movesLeft) { assert(mine::R.dist[y][x] == -1); continue; }
                assert(mine::R.dist[y][x] == d);
                int sgy = y >= sy ? 1 : -1, sgx = x >= sx ? 1 : -1;
                static int dp[30][30];
                for (int yy = sy; yy != y + sgy; yy += sgy) for (int xx = sx; xx != x + sgx; xx += sgx) {
                    int best = -1;
                    if (yy != sy) best = std::max(best, dp[yy - sgy][xx]);
                    if (xx != sx) best = std::max(best, dp[yy][xx - sgx]);
                    dp[yy][xx] = (best < 0 ? 0 : best) + ((yy == sy && xx == sx) || mine::M.seen[yy][xx] ? 0 : gMap[yy][xx]);
                }
                assert(mine::R.gain[y][x] == dp[y][x]);
            }
        }
        printf("REACH OK\n");
    } else if (mode == "hand") {
        runHand();
        for (int which = 1; which <= 2; ++which) {
            memcpy(gBak, gMap, sizeof gMap);
            startCase(which); gY = 2; gX = 3; gVis[2][3] = true;
            mine::resetCase(gBak, 2, 3);
            mine::M.movesLeft = 6;
            int used = 0;
            while (mine::M.movesLeft > 0) {
                mine::bfs();
                if (which == 2 && used == 0) {
                    static const int cand[5][2] = {{2,2},{2,5},{2,6},{1,1},{0,0}};
                    for (auto& c : cand) printf("KEY %d %d d=%d g=%d h=%d key=%.4f\n", c[0], c[1],
                        mine::R.dist[c[0]][c[1]], mine::R.gain[c[0]][c[1]], mine::around(c[0], c[1]), mine::key(c[0], c[1]));
                }
                int ty, tx;
                bool f = which == 1 ? mine::pickNearest(ty, tx) : mine::pickRatio(ty, tx);
                if (!f) break;
                printf("PICK %d %d %d d=%d\n", which, ty, tx, mine::R.dist[ty][tx]);
                used += mine::R.dist[ty][tx];
                mine::walkTo(ty, tx);
            }
            printf("HAND %d SCORE %lld MIRROR %lld USED %d REFUSED %d\n", which, gScore, mine::mirrorScore, used, mine::refused);
            assert(gScore == mine::mirrorScore && !gInvalid);
        }
#endif
    }
}
'''


def build_ref(code: str, folder: Path, name: str, extra: list[str]) -> Path:
    src = folder / f"{name}.cpp"
    exe = folder / name
    src.write_text(code + "\n" + REF)
    compile_to(exe, [src], extra + (["-DHAS_POLICY"] if "struct Reach" in code else []))
    return exe


def parse_scores(text: str) -> dict:
    score = {int(a): int(b) for a, b in re.findall(r"^TC (\d+) SCORE: (-?\d+)$", text, re.M)}
    mirror = {int(a): (int(b), int(c)) for a, b, c in re.findall(r"^TC (\d+) MIRROR (-?\d+) REFUSED (\d+)$", text, re.M)}
    logs = [tuple(map(int, m)) for m in re.findall(r"^LOG (\d+) (\d+) (-?\d+) (\d+)$", text, re.M)]
    total = re.search(r"^SCORE: (\d+)$", text, re.M)
    ms = re.search(r"^Result : (\d+)$", text, re.M)
    return {"score": score, "mirror": mirror, "logs": logs,
            "total": int(total.group(1)) if total else sum(score.values()),
            "ms": int(ms.group(1)) if ms else None}


def run(exe: Path, *args: str) -> str:
    return subprocess.run([str(exe), *args], check=True, capture_output=True, text=True, timeout=120).stdout


# ---------------------------------------------------------------- reference-grader checks
FAILURES = {
    "seen 초기화 누락": [(r"for \(int y = 0; y < N; \+\+y\) for \(int x = 0; x < N; \+\+x\) M\.seen\[y\]\[x\] = false;", "")],
    "seen 갱신 누락": [(r"M\.seen\[M\.y\]\[M\.x\] = true;", "")],
    "nextDay 누락": [(r"(?s)if \(M\.dayMoves == DAILY\) \{.*?\n    \}\n", "")],
}
CHAIN = ["h:1", "z:0", "c:2", "e:3", "h:1"]


def check_reference(sn: dict[str, str]) -> None:
    with tempfile.TemporaryDirectory(prefix="lesson-observe-") as tmp:
        folder = Path(tmp)
        for kind in ("baseline", "policy1", "policy2"):
            exe = build_ref(assemble(kind, sn), folder, kind, SAN)
            specs = [f"{k}:{s}" for k in "hce" for s in range(1, 7)] + ["z:0"]
            out = parse_scores(run(exe, "run", *specs))
            assert len(out["score"]) == len(specs)
            for tc in out["score"]:
                real = out["score"][tc]
                mirror, refused = out["mirror"][tc]
                assert refused == 0 and mirror == real, (kind, tc, real, mirror, refused)
            assert out["score"][len(specs)] == 0     # an all-zero map leaves nothing to find
            # chained TCs of different shapes: the repeated input must give the same score
            chain = parse_scores(run(exe, "run", *CHAIN))["score"]
            alone = parse_scores(run(exe, "run", CHAIN[0]))["score"][1]
            assert chain[1] == chain[5] == alone, (kind, chain, alone)
            print(f"OK: {kind}: mirror == reference score, refused 0, chained TCs reproduce ({alone})")
        exe = build_ref(assemble("policy2", sn), folder, "reach", SAN)
        assert run(exe, "reach").strip() == "REACH OK"
        print("OK: BFS dist/gain match the independent rectangle DP (40 maps, random seen sets)")
        for name, edits in FAILURES.items():
            exe = build_ref(assemble("policy2", sn, edits), folder, "bad", ["-O1"])
            res = parse_scores(run(exe, "run", *CHAIN))
            caught = any(res["mirror"][tc][0] != res["score"][tc] or res["mirror"][tc][1] for tc in res["score"])
            assert caught, name
            print(f"OK: failure '{name}' is detected by mirror != reference score")
        exe = build_ref(assemble("policy2", sn, FAILURES["seen 초기화 누락"]), folder, "stale", ["-O1"])
        res = parse_scores(run(exe, "run", *CHAIN))["score"]
        assert res[1] != res[5] or res[1] == 0
        print(f"OK: stale seen changes a repeated input: first {res[1]}, repeat {res[5]}")
        return {"chain_ok": alone, "chain_stale": res[5]}


# hand-calculated values written independently of the code (see the lesson text)
HAND_KEYS = {(2, 2): (1, 2, 43, 3.15), (2, 5): (2, 40, 62, 15.4), (2, 6): (3, 100, 40, 26.0),
             (1, 1): (3, 5, 4, 1.35), (0, 0): (5, 7, 3, 7.3 / 6)}


def check_hand(sn: dict[str, str], need_text: bool = True) -> dict:
    with tempfile.TemporaryDirectory(prefix="lesson-observe-hand-") as tmp:
        exe = build_ref(assemble("policy2", sn), Path(tmp), "hand", SAN)
        out = run(exe, "hand")
    keys = re.findall(r"^KEY (\d+) (\d+) d=(\d+) g=(\d+) h=(\d+) key=([\d.]+)$", out, re.M)
    assert len(keys) == 5
    for y, x, d, g, h, key in keys:
        want = HAND_KEYS[(int(y), int(x))]
        assert (int(d), int(g), int(h)) == want[:3] and abs(float(key) - want[3]) < 5e-5, (y, x, d, g, h, key)
    picks = re.findall(r"^PICK (\d) (\d+) (\d+) d=(\d+)$", out, re.M)
    p1 = [(int(y), int(x)) for w, y, x, d in picks if w == "1"]
    p2 = [(int(y), int(x)) for w, y, x, d in picks if w == "2"]
    assert p1 == [(2, 2), (1, 1), (0, 0)] and p2 == [(2, 6)], (p1, p2)
    hands = re.findall(r"^HAND (\d) SCORE (\d+) MIRROR (\d+) USED (\d+) REFUSED (\d+)$", out, re.M)
    assert hands == [("1", "7", "7", "5", "0"), ("2", "100", "100", "3", "0")], hands
    text = LESSON.read_text()
    for needle in (() if not need_text else ("3.15", "15.4", "26.0", "1.35", "1.217", "| 7 |", "| 100 |")):
        assert needle in text, f"hand example number missing from lesson: {needle}"
    print("OK: hand example (keys, targets 1:(2,2)->(1,1)->(0,0) = 7, 2:(2,6) = 100) recomputed by the lesson code")
    return {"policy1": 7, "policy2": 100}


# ---------------------------------------------------------------- public grader
def patched_judge(judge: Path, folder: Path) -> Path:
    text = judge.read_text()

    def once(old: str, new: str) -> None:
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new)

    once("static long long SCORE;",
         "static long long SCORE;\n"
         "namespace mine { extern long long mirrorScore; extern int refused; extern void (*hook)(int, int, int); }\n"
         "static int gTcNow;\n"
         "static void logHook(int d, int g, int a) { printf(\"LOG %d %d %d %d\\n\", gTcNow, d, g, a); }")
    once("        process(gMapInfoBak, gPosY, gPosX);",
         "        gTcNow = tc; mine::hook = logHook;\n        process(gMapInfoBak, gPosY, gPosX);")
    once("        printf(\"TC %d SCORE: %lld\\n\", tc, finalScore);",
         "        printf(\"TC %d SCORE: %lld\\n\", tc, finalScore);\n"
         "        printf(\"TC %d MIRROR %lld REFUSED %d\\n\", tc, mine::mirrorScore, mine::refused);")
    path = folder / "judge_patched.cpp"
    path.write_text(text)
    return path


def judge_run(judge_src: Path, code: str, folder: Path, name: str, flags: list[str], repeat: int = 1) -> dict:
    user = folder / f"{name}.cpp"
    exe = folder / name
    user.write_text(code)
    compile_to(exe, [judge_src, user], flags)
    results = [parse_scores(run(exe)) for _ in range(repeat)]
    first = results[0]
    assert all(r["score"] == first["score"] for r in results)
    first["ms_runs"] = [r["ms"] for r in results]
    first["ms"] = statistics.median(first["ms_runs"])
    return first


def calibration(logs: list[tuple[int, int, int, int]]) -> dict:
    # For each decision k, around_k predicted nearby value; the next decision's path gain is what
    # was actually collected next. Both are summed over the same TC.
    pairs = []
    for tc in sorted({l[0] for l in logs}):
        rows = [l for l in logs if l[0] == tc]
        pairs += [(rows[i][3], rows[i + 1][2]) for i in range(len(rows) - 1)]
    around, nxt = sum(p[0] for p in pairs), sum(p[1] for p in pairs)
    return {"decisions": len(pairs), "sum_around": around, "sum_next_gain": nxt,
            "next_gain_per_around": round(nxt / around, 4)}


SWEEPS = {"RADIUS": ["1", "2", "3", "4", "5", "6"],
          "WEIGHT": ["0.0", "0.05", "0.1", "0.25", "0.5", "1.0", "2.0"],
          "COST": ["0.0", "1.0", "2.0", "4.0", "8.0", "16.0"]}


def measure(judge: Path, sn: dict[str, str]) -> dict:
    result = {"date": datetime.date.today().isoformat(), "platform": platform.platform(),
              "machine": platform.machine(),
              "compiler": subprocess.run(["c++", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
              "flags": "-std=c++17 -O2", "judge_sha256": hashlib.sha256(judge.read_bytes()).hexdigest(),
              "rows": [], "sweeps": [], "failures": []}
    with tempfile.TemporaryDirectory(prefix="lesson-observe-judge-") as tmp:
        folder = Path(tmp)
        src = patched_judge(judge, folder)
        def record(label: str, kind: str, edits=None, repeat=1, bucket="rows"):
            r = judge_run(src, assemble(kind, sn, edits), folder, "m", ["-O2"], repeat)
            mirror = [r["mirror"][tc][0] for tc in sorted(r["mirror"])]
            refused = [r["mirror"][tc][1] for tc in sorted(r["mirror"])]
            row = {"label": label, "total": r["total"], "tcs": [r["score"][tc] for tc in sorted(r["score"])],
                   "mirror_total": sum(mirror), "refused_total": sum(refused), "ms": r["ms"], "ms_runs": r["ms_runs"]}
            result[bucket].append(row)
            print(json.dumps({k: row[k] for k in ("label", "total", "mirror_total", "refused_total", "ms")}), flush=True)
            return r
        record("기준선", "baseline", repeat=9)
        record("정책 1", "policy1", repeat=9)
        base = record("정책 2", "policy2", repeat=9)
        result["calibration"] = calibration(base["logs"])
        for param, values in SWEEPS.items():
            for value in values:
                record(f"{param} {value}", "policy2", with_param(sn, param, value), bucket="sweeps")
        for name, edits in FAILURES.items():
            record(name, "policy2", edits, bucket="failures")
        for kind in ("baseline", "policy1", "policy2"):     # sanitizer pass on the public grader
            judge_run(src, assemble(kind, sn), folder, "san", SAN)
        result["sanitizer"] = "baseline/policy1/policy2 passed ASan+UBSan on the public grader"
    return result


def check_tables(data: dict, extra: dict) -> None:
    text = LESSON.read_text()
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in text.splitlines() if line.startswith("|")]
    def present(label: str, *needles: object) -> None:
        for cells in rows:
            if cells and cells[0] == label and all(str(n) in cells for n in needles):
                return
        raise AssertionError(f"lesson table row missing or stale: {label} {needles}")
    for bucket in ("rows", "sweeps", "failures"):
        for row in data[bucket]:
            present(row["label"], row["total"])
    for row in data["rows"]:
        present(row["label"], *row["tcs"])
    # paired comparison of the default against WEIGHT 0.0 (same 10 inputs)
    by = {r["label"]: r for r in data["rows"] + data["sweeps"]}
    diff = [a - b for a, b in zip(by["정책 2"]["tcs"], by["WEIGHT 0.0"]["tcs"])]
    mean = statistics.mean(diff)
    err = statistics.stdev(diff) / len(diff) ** 0.5
    assert mean - 2 * err < 0 < mean + 2 * err, "the lesson says this interval contains 0"
    wins = sum(a > b for a, b in zip(by["정책 2"]["tcs"], by["정책 1"]["tcs"]))
    text_numbers = [f"{mean:.1f}", f"{err:.1f}", f"{mean - 2 * err:.1f}", f"{mean + 2 * err:.1f}",
                    f"{wins}개", str(extra["chain_ok"]), str(extra["chain_stale"]),
                    str(data["calibration"]["next_gain_per_around"]),
                    str(data["calibration"]["decisions"]), str(data["calibration"]["sum_around"]),
                    str(data["calibration"]["sum_next_gain"]), str(data["date"])]
    for n in text_numbers:
        assert n in text, f"calibration/date not in lesson: {n}"
    print(f"OK: lesson tables match {DATA.name} ({sum(len(data[b]) for b in ('rows', 'sweeps', 'failures'))} rows)")


def recheck_judge(judge: Path, sn: dict[str, str], data: dict) -> None:
    assert hashlib.sha256(judge.read_bytes()).hexdigest() == data["judge_sha256"], "judge file differs from the measured one"
    with tempfile.TemporaryDirectory(prefix="lesson-observe-judge-") as tmp:
        folder = Path(tmp)
        src = patched_judge(judge, folder)
        for label, kind in (("기준선", "baseline"), ("정책 1", "policy1"), ("정책 2", "policy2")):
            r = judge_run(src, assemble(kind, sn), folder, "m", ["-O2"])
            row = next(x for x in data["rows"] if x["label"] == label)
            assert r["total"] == row["total"] and [r["score"][t] for t in sorted(r["score"])] == row["tcs"], label
            assert sum(v[0] for v in r["mirror"].values()) == r["total"] and all(v[1] == 0 for v in r["mirror"].values())
        for kind in ("baseline", "policy1", "policy2"):
            judge_run(src, assemble(kind, sn), folder, "san", SAN)
    print("OK: public grader re-run reproduces the stored scores, mirror == grader, ASan/UBSan clean")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", type=Path, help="MINEEXPLORE main.cpp (optional)")
    parser.add_argument("--output", type=Path, help="write fresh measurements (needs --judge)")
    parser.add_argument("--tables", action="store_true", help="print table rows from the stored JSON")
    args = parser.parse_args()
    sn = snippets()
    if not args.tables:
        extra = check_reference(sn)
        check_hand(sn, need_text=not (args.judge and args.output))
    if args.tables:
        for bucket in ("rows", "sweeps", "failures"):
            for r in json.loads(DATA.read_text())[bucket]:
                print(f"| {r['label']} | {r['total']} | {r['mirror_total']} | {r['refused_total']} | {int(r['ms'])} |")
                if bucket == "rows":
                    print(f"| {r["label"]} | " + " | ".join(map(str, r['tcs'])) + " |")
        return
    if args.judge and args.output:
        data = measure(args.judge, sn)
        args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        return
    data = json.loads(DATA.read_text())
    if args.judge:
        recheck_judge(args.judge, sn, data)
    check_tables(data, extra)


if __name__ == "__main__":
    main()
