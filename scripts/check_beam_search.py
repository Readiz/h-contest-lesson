"""Check the beam-search lesson: code blocks, the beam against an independent reference, state keys, replay of
returned paths, optima on small inputs, hand examples, common mistakes, measurements.

What runs:
  * every code block is extracted, rejected if it uses a header / STL / dynamic allocation, assembled with the
    `random`, `min-heap` and `sort` library blocks and compiled header-free with -Wall -Wextra -Werror -fsyntax-only;
  * a harness (standard headers allowed there) includes the lesson code: 198 beam runs are compared with a
    reference beam written for this check (plain vectors, exact state comparison, full copies, so also the real
    copy counts), `mergeBySort` against `mergeSame`, the state keys against exact state identity on small inputs,
    the lower bound `sum of nn` against the best completion, and the lesson's replay functions against independent
    ones; a smaller battery of the same paths runs under ASan/UBSan;
  * the instance generators, the optima of the small inputs and the hand examples are recomputed in Python,
    independently of the lesson code;
  * the common mistakes are injected into the lesson code and must be detected;
  * the experiments are re-run, summarised here, compared with lesson-assets/measurements.json and with the
    tables in the lesson text.
--output writes measurements.json from a fresh run; --print-tables prints the markdown table rows.
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import statistics
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpp_library import assemble_library, check_submission_code  # noqa: E402
from lesson_text import check_hub_summary, read_lesson_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LESSON_ID = "beam-search"
DATA = ROOT / "lessons" / LESSON_ID / "lesson-assets" / "measurements.json"
HARNESS = ROOT / "scripts" / "beam_search_harness.cpp"
SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
BLOCKS = ("bs-frame", "bs-merge-sort", "bs-grid", "bs-route", "bs-gen", "bs-run", "bs-check")
LIBRARY = ["random", "min-heap", "sort"]
SEEDS = list(range(1, 21))
M64 = (1 << 64) - 1
WIN = 15   # of 20 seeds: a one-sided sign test at p < 0.05 (two-sided 0.041)
GRID_WIDTHS = [1, 2, 4, 8, 16, 64, 256, 1024]
ROUTE_WIDTHS = {0: [1, 2, 4, 8, 16, 64, 256], 1: [1, 2, 4, 8, 16, 64, 256], 2: [1, 2, 4, 8]}
GRID_NAMES = {0: "추정 없음", 1: "가까운 값의 합", 2: "거리 벌점"}
ROUTE_NAMES = {0: "추정 없음", 1: "낙관적 합", 2: "탐욕 완성"}
DIV_NAMES = [("base", "합침(기준)"), ("nomerge", "합치지 않음"), ("q1", "묶음 상한 1"), ("q2", "묶음 상한 2"), ("q4", "묶음 상한 4"),
             ("j4", "평가값 흔들기 4"), ("j16", "평가값 흔들기 16")]
ROUTE_DIV_NAMES = [(0, "합침(기준)"), (1, "합치지 않음"), (2, "합침 + 묶음 상한 1"), (3, "합침 + 묶음 상한 2")]


def snippets(text: str | None = None) -> dict[str, str]:
    found: dict[str, str] = {}
    for name, code in SNIP_RE.findall(text if text is not None else read_lesson_text(LESSON_ID)):
        assert name not in found, f"duplicate snippet {name}"
        check_submission_code(code, name)
        found[name] = code + "\n"
    assert set(BLOCKS) <= set(found), f"missing snippets: {set(BLOCKS) - set(found)}"
    return found


def assemble(sn: dict[str, str], edits: list[tuple[str, str]] | None = None) -> str:
    parts = [sn[n] for n in BLOCKS]
    for old, new in edits or []:
        for i, part in enumerate(parts):
            if old in part:
                parts[i] = part.replace(old, new, 1)
                break
        else:
            raise AssertionError(f"edit target not found: {old}")
    return assemble_library(LIBRARY) + "\n" + "\n".join(parts)


def build(code: str, workdir: Path, name: str, sanitize: bool) -> Path:
    sub = workdir / name
    sub.mkdir()
    (sub / "lesson.cpp").write_text(code)
    exe = sub / "harness"
    flags = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"] if sanitize else ["-O2"]
    done = subprocess.run(["c++", "-std=c++17", *flags, f"-I{sub}", str(HARNESS), "-o", str(exe)], capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError(done.stderr[:3000])
    return exe


def run(exe: Path, mode: str) -> list[list[str]]:
    done = subprocess.run([str(exe), mode], capture_output=True, text=True, timeout=600)
    if done.returncode:
        raise RuntimeError(f"{exe} {mode} failed:\n{done.stderr[:3000]}")
    return [line.split() for line in done.stdout.splitlines() if line.strip()]


# ------------------------------------------------------------------ independent Python references
class Gen:
    def __init__(self, seed: int):
        self.x = seed

    def next(self, bound: int) -> int:
        self.x = (self.x * 6364136223846793005 + 1442695040888963407) & M64
        return (self.x >> 33) % bound


def fnv(values, h=1469598103934665603):
    for v in values:
        h ^= v & 0xFFFFFFFF
        h = (h * 1099511628211) & M64
    return h


def gen_grid(seed: int, n: int = 400):
    g = Gen(seed)
    out = []
    for _ in range(n):
        u = g.next(10)
        out.append(0 if u < 6 else 1 + g.next(9))
    return out


def gen_route(seed: int, n: int = 200):
    g = Gen(seed)
    px, py = [], []
    for _ in range(n):
        px.append(g.next(1000))
        py.append(g.next(1000))
    return px, py


def check_gen(rows):
    seen = 0
    for kind, which, seed, h in rows:
        assert kind == "gen"
        seed = int(seed)
        if which == "grid":
            assert int(h) == fnv(gen_grid(seed)), "grid generator differs from the independent one"
        else:
            px, py = gen_route(seed)
            assert int(h) == fnv(py, fnv(px)), "route generator differs from the independent one"
        seen += 1
    assert seen == 40
    return seen


# ---- a beam search written independently in Python for the hand-size inputs (same rules, spelled out)
DIRS = ((-1, 0), (0, 1), (1, 0), (0, -1))


def grid_neighbors(pos, h, w):
    y, x = divmod(pos, w)
    return [(y + dy) * w + (x + dx) for dy, dx in DIRS if 0 <= y + dy < h and 0 <= x + dx < w]


def grid_estimate(v, h, w, vis, a, est, radius):
    ay, ax = divmod(a, w)
    total, nearest = 0, 0
    for c in range(h * w):
        d = abs(c // w - ay) + abs(c % w - ax)
        if 1 <= d <= radius and c not in vis:
            total += v[c] * (radius + 1 - d)
            if v[c] > 0 and (nearest == 0 or d < nearest):
                nearest = d
    if est == 1:
        return total
    if est == 2:
        return -nearest if nearest else -(radius + 1)
    return 0


def grid_beam(v, h, w, steps, width, est=0, scale=1, radius=1, merge=True):
    beam = [(frozenset([0]), 0, v[0], [])]
    trace, evals = [], 0
    for _ in range(steps):
        cands = []
        for i, (vis, pos, got, path) in enumerate(beam):
            for a in grid_neighbors(pos, h, w):
                g2 = got + (0 if a in vis else v[a])
                cands.append(dict(eval=g2 * scale + grid_estimate(v, h, w, vis | {a}, a, est, radius), parent=i, act=a, got=g2,
                                  est=grid_estimate(v, h, w, vis | {a}, a, est, radius), vis=vis | {a}, path=path + [a], dead=False))
        evals += len(cands)
        if merge:
            held = {}
            for idx, c in enumerate(cands):
                key = (c["vis"], c["act"])
                if key in held:
                    j = held[key]
                    if c["eval"] > cands[j]["eval"]:
                        cands[j]["dead"] = True
                        held[key] = idx
                    else:
                        c["dead"] = True
                else:
                    held[key] = idx
        order = sorted((i for i, c in enumerate(cands) if not c["dead"]), key=lambda i: (-cands[i]["eval"], i))
        top = order[:width]
        trace.append((beam, cands, top))
        beam = [(cands[i]["vis"], cands[i]["act"], cands[i]["got"], cands[i]["path"]) for i in reversed(top)]
    best = max(range(len(beam)), key=lambda j: (beam[j][2], -j))
    return beam[best][2], beam[best][3], evals, trace


def grid_optimum(v, h, w, steps):
    best = 0

    def dfs(pos, t, vis, got):
        nonlocal best
        if t == steps:
            best = max(best, got)
            return
        for a in grid_neighbors(pos, h, w):
            dfs(a, t + 1, vis | {a}, got + (0 if a in vis else v[a]))

    dfs(0, 0, frozenset([0]), v[0])
    return best


def rdist(p, a, b):
    return abs(p[a][0] - p[b][0]) + abs(p[a][1] - p[b][1])


def route_nn(p):
    return [min(rdist(p, u, v) for v in range(len(p)) if v != u) for u in range(len(p))]


def route_beam(p, width, est, merge=True):
    n, nn = len(p), route_nn(p)
    beam = [(frozenset(), -1, 0, [])]
    trace, evals = [], 0
    for _ in range(n):
        cands = []
        for i, (vis, last, cost, path) in enumerate(beam):
            for a in range(n):
                if a in vis:
                    continue
                c2 = cost + (0 if last < 0 else rdist(p, last, a))
                rest = sum(nn[u] for u in range(n) if u not in vis and u != a)
                cands.append(dict(eval=-(c2 + (rest if est >= 1 else 0)), parent=i, act=a, cost=c2, rest=rest, vis=vis | {a}, path=path + [a], dead=False))
        evals += len(cands)
        if merge:
            held = {}
            for idx, c in enumerate(cands):
                key = (c["vis"], c["act"])
                if key in held:
                    j = held[key]
                    if c["eval"] > cands[j]["eval"]:
                        cands[j]["dead"] = True
                        held[key] = idx
                    else:
                        c["dead"] = True
                else:
                    held[key] = idx
        order = sorted((i for i, c in enumerate(cands) if not c["dead"]), key=lambda i: (-cands[i]["eval"], i))
        top = order[:width]
        trace.append((beam, cands, top))
        beam = [(cands[i]["vis"], cands[i]["act"], cands[i]["cost"], cands[i]["path"]) for i in reversed(top)]
    best = max(range(len(beam)), key=lambda j: (-beam[j][2], -j))
    return beam[best][2], beam[best][3], evals, trace


def route_optimum(p):
    n = len(p)
    INF = 1 << 29
    dp = [[INF] * n for _ in range(1 << n)]
    for j in range(n):
        dp[1 << j][j] = 0
    for m in range(1, 1 << n):
        for j in range(n):
            if not (m >> j & 1) or dp[m][j] >= INF:
                continue
            for k in range(n):
                if not (m >> k & 1):
                    nm = m | 1 << k
                    dp[nm][k] = min(dp[nm][k], dp[m][j] + rdist(p, j, k))
    return min(dp[(1 << n) - 1])


HAND_GRID = [0, 6, 0, 0, 0, 0, 9, 8, 4]
HAND_POINTS = [(1, 1), (6, 5), (1, 7), (9, 8), (7, 4), (2, 6)]
MINUS = "−"


def pstr(path):
    return " ".join(str(x) for x in path)


def hand_tables() -> dict:
    """Expected data rows of the hand-example tables, computed with the Python beams above."""
    out: dict = {}
    res = {w: grid_beam(HAND_GRID, 3, 3, 4, w) for w in (1, 2, 3)}
    rows = []
    for d in range(4):
        row = [str(d + 1)]
        for w in (1, 2, 3):
            _, cands, top = res[w][3][d]
            row.append(", ".join(f"{pstr(cands[i]['path'])} : {cands[i]['got']}" for i in top))
        rows.append(row)
    rows.append(["평가 횟수"] + [str(res[w][2]) for w in (1, 2, 3)])
    rows.append(["최고 점수"] + [str(res[w][0]) for w in (1, 2, 3)])
    out["hand-grid"] = rows
    full = grid_beam(HAND_GRID, 3, 3, 4, 100)   # wide enough that nothing is dropped: the full search
    est = grid_beam(HAND_GRID, 3, 3, 4, 1, est=1, scale=2, radius=1)
    rows = []
    for d, (beam, cands, top) in enumerate(est[3]):
        for i, c in enumerate(cands):
            kept = "칸 " + " → ".join(str(x) for x in c["path"]) if i in top and d > 0 else (f"칸 {c['act']}" if i in top else "")
            rows.append([str(d + 1), f"칸 {c['act']}", str(c["got"]), str(c["est"]), str(c["eval"]), kept])
    out["hand-estimate"] = rows
    r = {w: route_beam(HAND_POINTS, w, 1) for w in (1, 2, 3)}
    nomerge = route_beam(HAND_POINTS, 2, 1, merge=False)
    full_r = route_beam(HAND_POINTS, 1536, 1)
    est0 = {w: route_beam(HAND_POINTS, w, 0) for w in (1, 2)}
    rows = []
    for d in range(6):
        _, cands, top = r[2][3][d]
        rows.append([str(d + 1), ", ".join(f"{pstr(cands[i]['path'])} : {cands[i]['cost']} + {cands[i]['rest']} = {-cands[i]['eval']}" for i in top)])
    out["hand-route"] = rows
    _, cands, top = r[2][3][3]
    rows = []
    for i, c in enumerate(cands):
        if c["dead"]:
            status = "합침"
        elif i in top:
            status = "남김"
        else:
            status = "남지만 상위 2개에 못 듦"
        rows.append([pstr(c["path"]), "{" + ", ".join(str(x) for x in sorted(c["vis"])) + "}", str(c["act"]), str(c["cost"]), str(c["rest"]),
                     MINUS + str(-c["eval"]), status])
    out["hand-merge"] = rows
    out["hand-route-widths"] = [["폭 1", str(r[1][0])], ["폭 2", str(r[2][0])], ["폭 2, 합치지 않음", str(nomerge[0])], ["폭 3", str(r[3][0])],
                                ["폭 1,536(아무것도 버리지 않음)", str(full_r[0])]]
    facts = {
        "gridOptimum": grid_optimum(HAND_GRID, 3, 3, 4), "gridFullEvals": full[2], "gridFullScore": full[0],
        "gridEstimateScore": est[0], "routeOptimum": route_optimum(HAND_POINTS), "nn": route_nn(HAND_POINTS),
        "routeEst0W1": est0[1][0], "routeEst0W2": est0[2][0], "gridPaths": {w: res[w][1] for w in (1, 2, 3)},
        "routeW2Path": r[2][1], "routeW3Path": r[3][1],
        # prose facts of the route table
        "depth1DroppedBest": -max(c["eval"] for i, c in enumerate(r[2][3][0][1]) if i not in r[2][3][0][2]),
    }
    d2 = r[2][3][1]
    facts["depth2TiedDropped"] = [pstr(d2[1][i]["path"]) for i in range(len(d2[1])) if i not in d2[2] and d2[1][i]["eval"] == d2[1][d2[2][0]]["eval"]]
    out["facts"] = facts
    return out


def check_hand(lines, tables):
    """The lesson code's results on the hand inputs against the Python beams."""
    grid = {}
    route = {}
    for r in lines:
        if r[:2] == ["hand", "grid"]:
            est, scale, radius, width, merge = (int(x) for x in r[2:7])
            grid[(est, scale, radius, width, merge)] = dict(score=int(r[7]), evals=int(r[8]), dropped=int(r[9]), path=[int(x) for x in r[10:]])
        elif r[:2] == ["hand", "route"]:
            est, width, merge = int(r[2]), int(r[3]), int(r[4])
            route[(est, width, merge)] = dict(cost=int(r[5]), evals=int(r[6]), dropped=int(r[7]), path=[int(x) for x in r[8:]])
    checked = 0
    for w in (1, 2, 3):
        py = grid_beam(HAND_GRID, 3, 3, 4, w)
        g = grid[(0, 1, 1, w, 1)]
        assert (g["score"], g["evals"], g["path"]) == (py[0], py[2], py[1]), (w, g, py[:3])
        checked += 1
    for w in (1, 2):
        py = grid_beam(HAND_GRID, 3, 3, 4, w, est=1, scale=2, radius=1)
        g = grid[(1, 2, 1, w, 1)]
        assert (g["score"], g["evals"], g["path"]) == (py[0], py[2], py[1]), (w, g, py[:3])
        checked += 1
    py = grid_beam(HAND_GRID, 3, 3, 4, 100)
    g = grid[(0, 1, 1, 100, 1)]
    assert (g["score"], g["evals"], g["path"], g["dropped"]) == (py[0], py[2], py[1], 0)
    checked += 1
    for est, width, merge in [(0, 1, 1), (0, 2, 1), (1, 1, 1), (1, 2, 1), (1, 2, 0), (1, 3, 1), (1, 1536, 1)]:
        py = route_beam(HAND_POINTS, width, est, bool(merge))
        g = route[(est, width, merge)]
        assert (g["cost"], g["evals"], g["path"]) == (py[0], py[2], py[1]), (est, width, merge, g, py[:3])
        checked += 1
    assert route[(1, 1536, 1)]["dropped"] == 0 and route[(1, 1536, 1)]["cost"] == route_optimum(HAND_POINTS)
    return checked


def check_hand_text(tables):
    """The hand tables in the lesson text against the expected rows."""
    text = read_lesson_text(LESSON_ID)
    count = 0
    for name in ("hand-grid", "hand-estimate", "hand-route", "hand-merge", "hand-route-widths"):
        match = re.search(re.escape(f"<!-- check:{name} -->") + r"\n((?:\|[^\n]*\n?)+)", text)
        assert match, f"hand table marker missing: {name}"
        lines = match.group(1).rstrip("\n").splitlines()
        got = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines[2:]]
        assert got == tables[name], f"hand table {name} differs from the Python beam\n got  {got}\n want {tables[name]}"
        count += len(got)
    return count


# ---- small-input optima and the brute-force cross-check
def check_small(rows):
    n = 0
    seen = set()
    for r in rows:
        if r[0] == "S1":
            seed, opt = int(r[4]), int(r[6])
            if seed not in seen:
                px, py = gen_route(seed, 10)
                assert route_optimum(list(zip(px, py))) == opt, f"route optimum differs for seed {seed}"
                seen.add(seed)
                n += 1
    assert len(seen) == 20
    seen = set()
    for r in rows:
        if r[0] == "S3" and r[1] == "0" and r[2] == "1":
            seed, opt = int(r[3]), int(r[5])
            v = gen_grid(seed, 25)
            assert grid_optimum(v, 5, 5, 8) == opt, f"grid optimum differs for seed {seed}"
            seen.add(seed)
            n += 1
    assert len(seen) == 20
    return n


# ------------------------------------------------------------------ measurements
def med(xs):
    return int(statistics.median_low(list(xs)))


def verdict(better: int, worse: int) -> str:
    return "더 좋음" if better >= WIN else ("더 나쁨" if worse >= WIN else "결정 못 함")


def measure(rows) -> dict:
    meas: dict = {"seeds": SEEDS}
    # grid: estimate x width
    g1: dict = {}
    for r in rows:
        if r[0] == "G1":
            est, w, s = int(r[1]), int(r[2]), int(r[3])
            score, evals, work, copied, whole, replay = (int(x) for x in r[4:10])
            assert score == replay, f"returned grid score differs from the replay ({est} {w} {s})"
            g1.setdefault((est, w), {})[s] = dict(score=score, ops=evals + work, evals=evals, work=work, copied=copied, whole=whole)
    meas["grid"] = {"widths": GRID_WIDTHS, "est": {}}
    for est in range(3):
        entries = []
        for w in GRID_WIDTHS:
            d = g1[(est, w)]
            entries.append({"width": w, "median": med(v["score"] for v in d.values()), "ops": med(v["ops"] for v in d.values()),
                            "evals": med(v["evals"] for v in d.values()), "work": med(v["work"] for v in d.values()),
                            "copied": med(v["copied"] for v in d.values()), "whole": med(v["whole"] for v in d.values())})
        pairs = []
        for a, b in zip(GRID_WIDTHS, GRID_WIDTHS[1:]):
            better = sum(g1[(est, b)][s]["score"] > g1[(est, a)][s]["score"] for s in SEEDS)
            worse = sum(g1[(est, b)][s]["score"] < g1[(est, a)][s]["score"] for s in SEEDS)
            pairs.append({"from": a, "to": b, "better": better, "worse": worse})
        wide_worse = 0
        for s in SEEDS:
            sc = [g1[(est, w)][s]["score"] for w in GRID_WIDTHS]
            wide_worse += any(sc[j] < sc[i] for i in range(len(sc)) for j in range(i + 1, len(sc)))
        meas["grid"]["est"][str(est)] = {"rows": entries, "pairs": pairs, "seedsWiderWorse": wide_worse}
    meas["grid"]["equalOps"] = []
    for (ea, wa), (eb, wb) in (((1, 1), (0, 16)), ((2, 1), (0, 8)), ((1, 4), (0, 64)), ((1, 16), (0, 256))):
        meas["grid"]["equalOps"].append({
            "with": {"est": ea, "width": wa, "median": med(v["score"] for v in g1[(ea, wa)].values()), "ops": med(v["ops"] for v in g1[(ea, wa)].values())},
            "without": {"est": eb, "width": wb, "median": med(v["score"] for v in g1[(eb, wb)].values()), "ops": med(v["ops"] for v in g1[(eb, wb)].values())},
            "withoutBetter": sum(g1[(eb, wb)][s]["score"] > g1[(ea, wa)][s]["score"] for s in SEEDS),
            "withoutWorse": sum(g1[(eb, wb)][s]["score"] < g1[(ea, wa)][s]["score"] for s in SEEDS)})
    # distinct cells of the first walks
    g4: dict = {}
    for r in rows:
        if r[0] == "G4":
            g4.setdefault((int(r[1]), int(r[2])), []).append((int(r[4]), int(r[5])))
    meas["gridDistinct"] = [{"est": e, "width": w, "median": med(x[0] for x in v), "back": med(x[1] for x in v)} for (e, w), v in sorted(g4.items())]
    # weight and radius
    for key in ("scale", "radius"):
        d: dict = {}
        for r in rows:
            if r[0] == "G2" and r[1] == key:
                assert int(r[5]) == int(r[6]), "returned grid score differs from the replay"
                d.setdefault((int(r[2]), int(r[3])), []).append(int(r[5]))
        meas[key] = [{"value": v, "widths": {str(w): med(d[(v, w)]) for w in (1, 4, 16)}} for v in sorted({k[0] for k in d})]
    # diversity on the grid
    g3: dict = {}
    for r in rows:
        if r[0] == "G3":
            name, est, w, s = r[1], int(r[2]), int(r[3]), int(r[4])
            score, dsum, ssum, replay = (int(x) for x in r[5:9])
            assert score == replay
            g3.setdefault((name, est, w), {})[s] = (score, dsum, ssum)
    meas["gridDiversity"] = []
    for est in (0, 1):
        for name, label in DIV_NAMES:
            entry = {"est": est, "name": name, "label": label, "widths": {}}
            for w in (16, 64):
                base, d = g3[("base", est, w)], g3[(name, est, w)]
                entry["widths"][str(w)] = {"median": med(d[s][0] for s in SEEDS), "better": sum(d[s][0] > base[s][0] for s in SEEDS),
                                           "worse": sum(d[s][0] < base[s][0] for s in SEEDS),
                                           "distinct": round(sum(d[s][1] for s in SEEDS) / sum(d[s][2] for s in SEEDS), 3)}
            meas["gridDiversity"].append(entry)
    # route
    r1: dict = {}
    for r in rows:
        if r[0] == "R1" and len(r) > 5:
            est, w, s = int(r[1]), int(r[2]), int(r[3])
            cost, evals, refined, work, copied, whole = (int(x) for x in r[4:10])
            r1.setdefault((est, w), {})[s] = dict(cost=cost, ops=evals + work, evals=evals, refined=refined, work=work, copied=copied, whole=whole)
        elif r[0] == "R1":
            raise AssertionError("route replay mismatch")
    meas["route"] = {"est": {}}
    for est in range(3):
        entries, pairs = [], []
        ws = ROUTE_WIDTHS[est]
        for w in ws:
            d = r1[(est, w)]
            entries.append({"width": w, "median": med(v["cost"] for v in d.values()), "ops": med(v["ops"] for v in d.values()),
                            "evals": med(v["evals"] for v in d.values()), "work": med(v["work"] for v in d.values()),
                            "refined": med(v["refined"] for v in d.values()), "copied": med(v["copied"] for v in d.values()),
                            "whole": med(v["whole"] for v in d.values())})
        for a, b in zip(ws, ws[1:]):
            better = sum(r1[(est, b)][s]["cost"] < r1[(est, a)][s]["cost"] for s in SEEDS)
            worse = sum(r1[(est, b)][s]["cost"] > r1[(est, a)][s]["cost"] for s in SEEDS)
            pairs.append({"from": a, "to": b, "better": better, "worse": worse})
        wide_worse = 0
        for s in SEEDS:
            cs = [r1[(est, w)][s]["cost"] for w in ws]
            wide_worse += any(cs[j] > cs[i] for i in range(len(cs)) for j in range(i + 1, len(cs)))
        vs = [{"width": w, "better": sum(r1[(est, w)][s]["cost"] < r1[(est, 1)][s]["cost"] for s in SEEDS),
               "worse": sum(r1[(est, w)][s]["cost"] > r1[(est, 1)][s]["cost"] for s in SEEDS)} for w in ws[1:]]
        meas["route"]["est"][str(est)] = {"rows": entries, "pairs": pairs, "seedsWiderWorse": wide_worse, "vsGreedy": vs}
    meas["route"]["equalOps"] = []
    for (ea, wa), (eb, wb) in (((2, 1), (0, 256)), ((2, 1), (1, 256))):
        meas["route"]["equalOps"].append({
            "with": {"est": ea, "width": wa, "median": med(v["cost"] for v in r1[(ea, wa)].values()), "ops": med(v["ops"] for v in r1[(ea, wa)].values())},
            "without": {"est": eb, "width": wb, "median": med(v["cost"] for v in r1[(eb, wb)].values()), "ops": med(v["ops"] for v in r1[(eb, wb)].values())},
            "withBetter": sum(r1[(ea, wa)][s]["cost"] < r1[(eb, wb)][s]["cost"] for s in SEEDS),
            "withWorse": sum(r1[(ea, wa)][s]["cost"] > r1[(eb, wb)][s]["cost"] for s in SEEDS)})
    r2: dict = {}
    for r in rows:
        if r[0] == "R2" and len(r) > 5:
            variant, est, w, s = int(r[1]), int(r[2]), int(r[3]), int(r[4])
            r2.setdefault((variant, est, w), {})[s] = (int(r[5]), int(r[6]), int(r[7]))
        elif r[0] == "R2":
            raise AssertionError("route replay mismatch")
    meas["routeDiversity"] = []
    for est in (0, 1):
        for variant, label in ROUTE_DIV_NAMES:
            entry = {"est": est, "variant": variant, "label": label, "widths": {}}
            for w in (4, 16, 64):
                base, d = r2[(0, est, w)], r2[(variant, est, w)]
                entry["widths"][str(w)] = {"median": med(d[s][0] for s in SEEDS), "better": sum(d[s][0] < base[s][0] for s in SEEDS),
                                           "worse": sum(d[s][0] > base[s][0] for s in SEEDS),
                                           "distinct": round(sum(d[s][1] for s in SEEDS) / sum(d[s][2] for s in SEEDS), 3)}
            meas["routeDiversity"].append(entry)
    # small inputs
    s1: dict = {}
    for r in rows:
        if r[0] == "S1":
            est, merge, w, s = int(r[1]), int(r[2]), int(r[3]), int(r[4])
            s1.setdefault((est, merge, w), {})[s] = (int(r[5]), int(r[6]), int(r[7]))
    meas["smallRoute"] = []
    for w in (1, 2, 4, 8, 16, 64, 256, 1536):
        entry = {"width": w}
        for key, (est, merge) in (("est0", (0, 1)), ("est1", (1, 1)), ("est1nomerge", (1, 0))):
            d = s1[(est, merge, w)]
            entry[key] = {"optimal": sum(v[0] == v[1] for v in d.values()), "gap": med(v[0] - v[1] for v in d.values()),
                          "noDrop": sum(v[2] == 0 for v in d.values())}
        meas["smallRoute"].append(entry)
    s2: dict = {}
    for r in rows:
        if r[0] == "S2":
            s2.setdefault((int(r[1]), int(r[2])), {})[int(r[3])] = (int(r[4]), int(r[5]), int(r[6]))
    meas["smallGrid"] = []
    for w in (1, 2, 4, 8, 16, 64, 256):
        entry = {"width": w}
        for est in (0, 1):
            d = s2[(est, w)]
            entry[f"est{est}"] = {"optimal": sum(v[0] == v[1] for v in d.values()), "gap": med(v[1] - v[0] for v in d.values()),
                                  "noDrop": sum(v[2] == 0 for v in d.values())}
        meas["smallGrid"].append(entry)
    s3: dict = {}
    for r in rows:
        if r[0] == "S3":
            s3.setdefault((int(r[1]), int(r[2])), {})[int(r[3])] = (int(r[4]), int(r[5]), int(r[6]))
    meas["tinyGrid"] = []
    for w in (1, 2, 4, 8, 8192):
        entry = {"width": w}
        for est in (0, 1):
            d = s3[(est, w)]
            entry[f"est{est}"] = {"optimal": sum(v[0] == v[1] for v in d.values()), "noDrop": sum(v[2] == 0 for v in d.values())}
        meas["tinyGrid"].append(entry)
    return meas


# ------------------------------------------------------------------ mistakes
MUTATIONS = {
    "key": [("c.key = (s.vkey ^ (fresh ? zcell[a] : 0ULL)) ^ zpos[a];", "c.key = s.vkey ^ (fresh ? zcell[a] : 0ULL);"),
            ("c.key = (s.vkey ^ zpt[a]) ^ zlast[a];", "c.key = s.vkey ^ zpt[a];")],
    "parent": [("logParent[d][j] = c.parent;", "logParent[d][j] = pick[j];")],
    "inplace": [("p.apply(a[c.parent], c.act, b[j]);", "p.apply(a[c.parent], c.act, a[c.parent]); b[j] = a[c.parent];")],
    "keepworse": [("if (cand[i].eval > o.eval)", "if (cand[i].eval < o.eval)")],
    "sign": [("c.eval = -((long long)cost + (est >= 1 ? rest : 0));", "c.eval = (long long)cost + (est >= 1 ? rest : 0);")],
}


def detect(rows, tables) -> dict:
    d = {r[1]: [int(x) for x in r[2:]] for r in rows if r[0] == "D"}
    hand = [r for r in rows if r[:1] == ["hand"]]
    hand_bad = 0
    grid_expect = {(0, 1, 1, w, 1): grid_beam(HAND_GRID, 3, 3, 4, w) for w in (1, 2, 3)}
    grid_expect[(0, 1, 1, 100, 1)] = grid_beam(HAND_GRID, 3, 3, 4, 100)
    for (est, scale, radius, w) in ((1, 2, 1, 1), (1, 2, 1, 2)):
        grid_expect[(est, scale, radius, w, 1)] = grid_beam(HAND_GRID, 3, 3, 4, w, est=est, scale=scale, radius=radius)
    route_expect = {(est, w, m): route_beam(HAND_POINTS, w, est, bool(m)) for est, w, m in [(0, 1, 1), (0, 2, 1), (1, 1, 1), (1, 2, 1), (1, 2, 0), (1, 3, 1), (1, 1536, 1)]}
    total = 0
    for r in hand:
        if r[1] == "grid":
            key = tuple(int(x) for x in r[2:7])
            key = (key[0], key[1], key[2], key[3], key[4])
            if key in grid_expect:
                total += 1
                hand_bad += int(r[7]) != grid_expect[key][0] or [int(x) for x in r[10:]] != grid_expect[key][1]
        elif r[1] == "route":
            key = (int(r[2]), int(r[3]), int(r[4]))
            if key in route_expect:
                total += 1
                hand_bad += int(r[5]) != route_expect[key][0] or [int(x) for x in r[8:]] != route_expect[key][1]
    return {"diffRuns": d["diff"][0], "diffBad": d["diff"][1], "keysBad": d["keys"][0], "replayGrid": d["replay"][0], "replayRoute": d["replay"][1],
            "optimumEst0": d["optimum"][0], "optimumEst1": d["optimum"][1], "handChecked": total, "handBad": hand_bad}


def run_mistakes(sn, workdir: Path, tables) -> dict:
    def one(name, edit):
        exe = build(assemble(sn, edit), workdir, f"m_{name}", False)
        return name, detect(run(exe, "detect"), tables)

    jobs = [("clean", None)] + list(MUTATIONS.items())
    with ThreadPoolExecutor(max_workers=6) as pool:
        return dict(pool.map(lambda j: one(*j), jobs))


def check_mistakes(m: dict) -> None:
    c = m["clean"]
    assert c["diffBad"] == 0 and c["keysBad"] == 0 and c["replayGrid"] == c["replayRoute"] == 0 and c["optimumEst0"] == c["optimumEst1"] == 20 and c["handBad"] == 0, c
    assert c["diffRuns"] == 198 and c["handChecked"] == 13
    assert m["key"]["keysBad"] > 0 and m["key"]["diffBad"] > 0 and m["key"]["optimumEst0"] < 20
    assert m["parent"]["replayGrid"] == 20 and m["parent"]["replayRoute"] == 20 and m["parent"]["handBad"] > 0
    assert m["inplace"]["replayGrid"] > 0 and m["inplace"]["replayRoute"] > 0
    assert m["keepworse"]["optimumEst0"] < 20 and m["keepworse"]["optimumEst1"] < 20 and m["keepworse"]["handBad"] > 0
    assert m["sign"]["replayGrid"] == m["sign"]["replayRoute"] == 0 and m["sign"]["handBad"] > 0 and m["sign"]["diffBad"] > 0
    for name in MUTATIONS:
        assert m[name]["diffBad"] > 0, f"the reference comparison must catch {name}"


# ------------------------------------------------------------------ tables as they appear in the lesson
def fmt(x) -> str:
    return f"{int(x):,}"


def pair_cell(p, better_is_more=True) -> str:
    return f"{p['better']} / {p['worse']} {verdict(p['better'], p['worse'])}"


def table_rows(meas: dict) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    g = meas["grid"]["est"]
    rows["grid_score"] = [f"| {fmt(w)} | " + " | ".join(fmt(g[str(e)]["rows"][i]["median"]) for e in range(3)) + " |" for i, w in enumerate(GRID_WIDTHS)]
    rows["grid_ops"] = [f"| {fmt(w)} | " + " | ".join(f"{fmt(g[str(e)]['rows'][i]['evals'])} / {fmt(g[str(e)]['rows'][i]['work'])}" for e in range(3)) + " |"
                        for i, w in enumerate(GRID_WIDTHS)]
    rows["grid_pairs"] = [f"| {fmt(p['from'])} → {fmt(p['to'])} | " + " | ".join(pair_cell(g[str(e)]["pairs"][i]) for e in range(3)) + " |"
                          for i, p in enumerate(g["0"]["pairs"])]
    rows["grid_equal_ops"] = []
    for e in meas["grid"]["equalOps"]:
        a, b = e["with"], e["without"]
        rows["grid_equal_ops"].append(f"| {GRID_NAMES[a['est']]}, 폭 {fmt(a['width'])} | {fmt(a['ops'])} | {fmt(a['median'])} | {GRID_NAMES[b['est']]}, 폭 {fmt(b['width'])} | "
                                      f"{fmt(b['ops'])} | {fmt(b['median'])} | {e['withoutBetter']} / {e['withoutWorse']} {verdict(e['withoutBetter'], e['withoutWorse'])} |")
    rows["grid_wider_worse"] = [f"| {GRID_NAMES[e]} | {g[str(e)]['seedsWiderWorse']} / 20 |" for e in range(3)]
    for key in ("scale", "radius"):
        rows[f"grid_{key}"] = [f"| {e['value']} | " + " | ".join(fmt(e["widths"][str(w)]) for w in (1, 4, 16)) + " |" for e in meas[key]]
    rows["grid_distinct"] = [f"| {GRID_NAMES[e['est']]} | {e['width']} | {e['median']} | {e['back']} |" for e in meas["gridDistinct"]]
    rows["grid_div"] = []
    for e in meas["gridDiversity"]:
        cells = []
        for w in ("16", "64"):
            x = e["widths"][w]
            cells.append(fmt(x["median"]) if e["name"] == "base" else f"{fmt(x['median'])} ({x['better']} / {x['worse']} {verdict(x['better'], x['worse'])})")
        rows["grid_div"].append(f"| {GRID_NAMES[e['est']]} | {e['label']} | {cells[0]} | {cells[1]} | {e['widths']['16']['distinct']:.3f} |")
    rt = meas["route"]["est"]
    rows["route_score"] = []
    rows["route_ops"] = []
    for w in ROUTE_WIDTHS[0]:
        cells, opc = [], []
        for e in range(3):
            hit = [x for x in rt[str(e)]["rows"] if x["width"] == w]
            cells.append(fmt(hit[0]["median"]) if hit else "-")
            opc.append(f"{fmt(hit[0]['evals'])} / {fmt(hit[0]['work'])}" if hit else "-")
        rows["route_score"].append(f"| {fmt(w)} | " + " | ".join(cells) + " |")
        rows["route_ops"].append(f"| {fmt(w)} | " + " | ".join(opc) + " |")
    rows["route_vs_greedy"] = []
    for w in ROUTE_WIDTHS[0][1:]:
        cells = []
        for e in range(3):
            hit = [p for p in rt[str(e)]["vsGreedy"] if p["width"] == w]
            cells.append(pair_cell(hit[0]) if hit else "-")
        rows["route_vs_greedy"].append(f"| {w} | " + " | ".join(cells) + " |")
    rows["route_equal_ops"] = []
    for e in meas["route"]["equalOps"]:
        a, b = e["with"], e["without"]
        rows["route_equal_ops"].append(f"| {ROUTE_NAMES[a['est']]}, 폭 {fmt(a['width'])} | {fmt(a['ops'])} | {fmt(a['median'])} | {ROUTE_NAMES[b['est']]}, 폭 {fmt(b['width'])} | "
                                       f"{fmt(b['ops'])} | {fmt(b['median'])} | {e['withBetter']} / {e['withWorse']} {verdict(e['withBetter'], e['withWorse'])} |")
    rows["route_wider_worse"] = [f"| {ROUTE_NAMES[e]} | {rt[str(e)]['seedsWiderWorse']} / 20 |" for e in range(3)]
    rows["route_div"] = []
    for e in meas["routeDiversity"]:
        cells = []
        for w in ("4", "16", "64"):
            x = e["widths"][w]
            cells.append(fmt(x["median"]) if e["variant"] == 0 else f"{fmt(x['median'])} ({x['better']} / {x['worse']} {verdict(x['better'], x['worse'])})")
        rows["route_div"].append(f"| {ROUTE_NAMES[e['est']]} | {e['label']} | " + " | ".join(cells) + f" | {e['widths']['16']['distinct']:.3f} |")
    rows["small_route"] = [f"| {fmt(e['width'])} | " + " | ".join(f"{e[k]['optimal']} / 20 · {fmt(e[k]['gap'])}" for k in ("est0", "est1", "est1nomerge")) + " |"
                           for e in meas["smallRoute"]]
    rows["small_grid"] = [f"| {fmt(e['width'])} | " + " | ".join(f"{e[k]['optimal']} / 20 · {fmt(e[k]['gap'])}" for k in ("est0", "est1")) + " |" for e in meas["smallGrid"]]
    rows["tiny_grid"] = [f"| {fmt(e['width'])} | " + " | ".join(f"{e[k]['optimal']} / 20 · 버린 후보 없는 시드 {e[k]['noDrop']}" for k in ("est0", "est1")) + " |"
                         for e in meas["tinyGrid"]]
    gr = {(e, x["width"]): x for e in range(3) for x in g[str(e)]["rows"]}
    rr = {(e, x["width"]): x for e in range(3) for x in rt[str(e)]["rows"]}
    copy_cfg = [("격자 수집, 가까운 값의 합, 폭 16", gr[(1, 16)]), ("격자 수집, 가까운 값의 합, 폭 256", gr[(1, 256)]),
                ("순서 문제, 낙관적 합, 폭 16", rr[(1, 16)]), ("순서 문제, 낙관적 합, 폭 64", rr[(1, 64)])]
    rows["copy"] = [f"| {name} | {fmt(x['copied'])} | {fmt(x['whole'])} | {x['whole'] / x['copied']:.1f} |" for name, x in copy_cfg]
    return rows


def mistake_rows(m: dict) -> list[str]:
    labels = {"key": "키에서 현재 칸·마지막 점 빠뜨림", "parent": "부모 번호 자리에 후보 번호 기록", "inplace": "부모 상태를 직접 고쳐 씀",
              "keepworse": "합칠 때 나쁜 쪽을 남김", "sign": "최소화 문제의 평가값 부호"}
    out = []
    for name, label in labels.items():
        x = m[name]
        out.append(f"| {label} | {x['replayGrid'] + x['replayRoute']} / 40 | {x['keysBad']} | {x['optimumEst0'] + x['optimumEst1']} / 40 | {x['handBad']} / 13 | {x['diffBad']} / 198 |")
    return out


def hub_expected(meas: dict) -> list[tuple[str, str]]:
    g, r = meas["grid"]["est"], meas["route"]["est"]
    gv = lambda e, w: next(x for x in g[str(e)]["rows"] if x["width"] == w)
    rv = lambda e, w: next(x for x in r[str(e)]["rows"] if x["width"] == w)
    return [("격자 틀 · 폭 1, 추정 없음 (↑)", fmt(gv(0, 1)["median"])),
            ("격자 틀 · 폭 1, 가까운 값의 합 (↑)", fmt(gv(1, 1)["median"])),
            ("격자 틀 · 폭 16, 추정 없음 (↑)", fmt(gv(0, 16)["median"])),
            ("격자 틀 · 폭 1,024, 가까운 값의 합 (↑)", fmt(gv(1, 1024)["median"])),
            ("순서 틀 · 폭 1, 추정 없음 (↓)", fmt(rv(0, 1)["median"])),
            ("순서 틀 · 폭 64, 추정 없음 (↓)", fmt(rv(0, 64)["median"])),
            ("순서 틀 · 폭 1, 탐욕 완성 (↓)", fmt(rv(2, 1)["median"]))]


def prose_checks(meas: dict, mistakes: dict) -> list[str]:
    """Numbers quoted in the running text (not in tables) must come from the measurements."""
    g, r = meas["grid"]["est"], meas["route"]["est"]
    gv = lambda e, w: next(x for x in g[str(e)]["rows"] if x["width"] == w)
    rv = lambda e, w: next(x for x in r[str(e)]["rows"] if x["width"] == w)
    d = {(x["est"], x["width"]): x for x in meas["gridDistinct"]}
    eq = meas["grid"]["equalOps"]
    wins = [x["withoutBetter"] for x in eq]
    div = {(x["est"], x["name"]): x for x in meas["gridDiversity"]}
    rdiv = {(x["est"], x["variant"]): x for x in meas["routeDiversity"]}
    sm = {x["width"]: x for x in meas["smallRoute"]}
    cp_grid = gv(1, 16)["whole"] / gv(1, 16)["copied"]
    cp_route = rv(1, 16)["whole"] / rv(1, 16)["copied"]
    scale = {x["value"]: x["widths"] for x in meas["scale"]}
    radius = {x["value"]: x["widths"] for x in meas["radius"]}
    out = [
        f"점수가 {fmt(gv(0, 1)['median'])}로", f"추정이 있는 {fmt(gv(1, 1)['median'])}, {fmt(gv(2, 1)['median'])}",
        f"61칸 가운데 {d[(0, 1)]['median']}칸만", f"60걸음 중 {60 - (d[(0, 1)]['median'] - 1)}걸음",
        f"({d[(0, 2)]['median']}칸)", f"되돌아간 걸음은 {d[(0, 1)]['back']}번", f"{d[(1, 1)]['back']}번",
        f"(첫 줄은 {fmt(gv(1, 1)['evals'])} 대 {fmt(gv(0, 16)['evals'])})",
        f"20개 중 {min(wins)}~{max(wins)}개 시드",
        f"폭 4는 {gv(1, 4)['median']}, 폭 8은 {gv(1, 8)['median']}, 폭 16은 {gv(1, 16)['median']}",
        f"`scale = 1`에서는 폭 1의 점수가 {scale[1]['1']}로, 추정이 없는 폭 1({gv(0, 1)['median']})보다", f"`scale = 1`은 {scale[1]['16']}",
        f"폭 1에서 같은 {radius[1]['1']}였고, 폭 16에서는 1이 {radius[1]['16']}, 5가 {radius[5]['16']}으로 3({radius[3]['16']})·2({radius[2]['16']})보다",
        f"({div[(0, 'nomerge')]['widths']['16']['distinct']}, {div[(1, 'nomerge')]['widths']['16']['distinct']})",
        f"(점수 {gv(1, 16)['median']}에서 {div[(1, 'q1')]['widths']['16']['median']}, {div[(1, 'q2')]['widths']['16']['median']}으로)",
        f"폭 1({fmt(rv(2, 1)['median'])})이 이미 폭 256의 추정 없음({fmt(rv(0, 256)['median'])})·낙관적 합({fmt(rv(1, 256)['median'])})보다",
        f"후보 {fmt(rv(2, 1)['evals'])}개 중 {fmt(rv(2, 1)['refined'])}개에만",
        f"추정 없음 {rdiv[(0, 1)]['widths']['16']['distinct']}, 낙관적 합 {rdiv[(1, 1)]['widths']['16']['distinct']}",
        f"(폭 16에서 {sm[16]['est1']['optimal']} 대 {sm[16]['est0']['optimal']})",
        f"({sm[8]['est1']['optimal']}에서 {sm[8]['est1nomerge']['optimal']}, {sm[16]['est1']['optimal']}에서 {sm[16]['est1nomerge']['optimal']})",
        f"격자에서 {round(cp_grid)}배, 순서 문제에서 약 {round(cp_route, -1):.0f}배",
        f"(추정 없음 {gv(0, 1)['median']}에서 {gv(0, 1024)['median']}, 가까운 값의 합 {gv(1, 1)['median']}에서 {gv(1, 1024)['median']})",
        f"(충돌 {mistakes['key']['keysBad']}개)", f"손계산(3 / 13)" if mistakes["keepworse"]["handBad"] == 3 else "손계산(?)",
        f"손계산({mistakes['sign']['handBad']} / 13)",
    ]
    assert sm[1536]["est0"]["optimal"] == sm[1536]["est1"]["optimal"] == 20 and sm[1536]["est0"]["noDrop"] == sm[1536]["est1"]["noDrop"] == 20
    assert sm[1536]["est1nomerge"]["noDrop"] < 20
    return out


def check_text_tables(meas: dict, mistakes: dict) -> int:
    text = read_lesson_text(LESSON_ID)
    count = 0
    for frag in prose_checks(meas, mistakes):
        assert frag in text, f"quoted number missing or differs in the text: {frag}"
        count += 1
    for name, rows in table_rows(meas).items():
        for row in rows:
            assert row in text, f"lesson table row missing or differs ({name}): {row}"
            count += 1
    for row in mistake_rows(mistakes):
        assert row in text, f"mistake table row missing or differs: {row}"
        count += 1
    count += check_hub_summary(LESSON_ID, hub_expected(meas))
    return count


# ------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", action="store_true", help="write lesson-assets/measurements.json from a fresh run")
    ap.add_argument("--print-tables", action="store_true")
    args = ap.parse_args()

    sn = snippets()
    code = assemble(sn)
    tables = hand_tables()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "syntax.cpp").write_text(code)
        done = subprocess.run(["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", str(work / "syntax.cpp")], capture_output=True, text=True)
        assert done.returncode == 0, done.stderr[:2000]
        with ThreadPoolExecutor(max_workers=3) as pool:
            f_san = pool.submit(build, code, work, "san", True)
            f_fast = pool.submit(build, code, work, "fast", False)
            f_mut = pool.submit(run_mistakes, sn, work, tables)
            san, fast = f_san.result(), f_fast.result()
            with ThreadPoolExecutor(max_workers=3) as runs:
                r_gen = runs.submit(run, san, "gen")
                r_memory = runs.submit(run, san, "memory")
                r_correct = runs.submit(run, fast, "correct")
                r_exp = runs.submit(run, fast, "exp")
                r_hand = runs.submit(run, fast, "hand")
                gen_rows, correct, exp_rows, hand_rows = r_gen.result(), r_correct.result(), r_exp.result(), r_hand.result()
                memory = r_memory.result()
            mistakes = f_mut.result()
        n_gen = check_gen(gen_rows)
        c = {r[0]: [int(x) for x in r[1:]] for r in correct}
        assert c["diff"][1] == 0 and c["diff"][0] == 198, f"the beam must agree with the reference beam: {c['diff']}"
        assert c["replay"][1] == 0, "the lesson's replay functions must agree with the independent ones"
        assert c["merges"][1] == 0 and c["merges"][0] == 10 and c["merges"][2] > 10000, "mergeBySort must kill the same candidates as mergeSame"
        assert c["keys"][:2] == [0, 0] and c["keys"][2] > 100 and c["keys"][3] > 100, "state keys must match exact state identity"
        assert c["lowerbound"][1] == 0 and c["lowerbound"][2] > 0 and c["lowerbound"][0] == 20480, "the nn lower bound must not exceed the best completion"
        assert memory == [["memory", "66", "0", "0", "0"]], f"the sanitizer build must run a clean battery: {memory}"
        n_hand = check_hand(hand_rows, tables)
        n_hand_text = check_hand_text(tables)
        facts = tables["facts"]
        assert facts["gridOptimum"] == 23 and facts["gridFullEvals"] == 72 and facts["gridFullScore"] == 23 and facts["gridEstimateScore"] == 23
        assert facts["routeOptimum"] == 21 and facts["nn"] == [6, 2, 2, 6, 2, 2] and sum(facts["nn"]) == 20
        assert facts["routeEst0W1"] == 21 and facts["routeEst0W2"] == 28 and facts["depth1DroppedBest"] == 18 and facts["depth2TiedDropped"] == ["0 2", "0 5"]
        assert facts["routeW2Path"] == [3, 4, 1, 5, 2, 0] and facts["routeW3Path"] == [3, 1, 4, 5, 2, 0]
        n_small = check_small(exp_rows)
        meas = measure(exp_rows)
        check_mistakes(mistakes)

    meas.update({"schema": 1, "hand": {k: v for k, v in tables.items() if k != "facts"}, "handFacts": tables["facts"], "mistakes": mistakes,
                 "rule": f"한쪽이 {WIN} / 20 시드 이상 나으면 차이가 있다고 보고, 아니면 결정 못 함",
                 "problems": {"grid": "H=W=20, T=60, 값 0..9(60%는 0), 시작 칸 0", "route": "N=200, 좌표 0..999, 맨해튼 거리 합, 시작점 자유"}})
    if args.output:
        DATA.write_text(json.dumps(meas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {DATA.relative_to(ROOT)}")
    if args.print_tables:
        for name, tr in table_rows(meas).items():
            print(f"[{name}]")
            print("\n".join(tr))
        print("[mistakes]")
        print("\n".join(mistake_rows(mistakes)))
        print("[hub]")
        print("\n".join(f"| {a} | {b} |" for a, b in hub_expected(meas)))
        for name in ("hand-grid", "hand-estimate", "hand-route", "hand-merge", "hand-route-widths"):
            print(f"[{name}]")
            for row in tables[name]:
                print("| " + " | ".join(row) + " |")
        return
    stored = json.loads(DATA.read_text(encoding="utf-8"))
    assert stored == json.loads(json.dumps(meas)), "measurements.json differs from a fresh measurement (run with --output)"
    n_rows = check_text_tables(stored, mistakes)
    print(f"beam-search ok (sanitizer battery of 66 runs clean): {len(BLOCKS)} code blocks, {n_gen} generated instances checked against Python, 198 beam runs equal to the reference beam, "
          f"{c['keys'][2]} + {c['keys'][3]} states keyed, {c['lowerbound'][0]} states bounded, {n_small} small optima recomputed, "
          f"{n_hand} hand results + {n_hand_text} hand-table rows matched, 5 injected mistakes detected, {n_rows} table rows matched the measurements")


if __name__ == "__main__":
    main()
