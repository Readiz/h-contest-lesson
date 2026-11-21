"""Check the partial-information lesson: code blocks, mirror state against the judge, hidden-information test,
hand examples, measurements, injected mistakes.

What runs (about 40 s):
  * every code block is extracted, rejected if it uses a header / STL / dynamic allocation, assembled with the
    `array` and `sort` library blocks and compiled header-free with -Wall -Wextra -Werror -fsyntax-only;
  * a harness (standard headers allowed there) including the lesson code runs under ASan/UBSan: replays every
    walk / assignment with an independent reference, compares the mirror with the judge after every step,
    runs the hidden-information test, compares the beam planner with brute force on small maps;
  * the instance generators and the hand examples are recomputed in Python, independently of the lesson code;
  * the beam-search lesson's own Beam is run on the same grids as a cross-check of the compact planner;
  * the common mistakes are injected into the lesson code and must be detected;
  * the experiments are re-run, summarised here, compared with lesson-assets/measurements.json and with the
    tables in the lesson text.
--output writes measurements.json from a fresh run; --print-tables prints the markdown table rows.
When the stored measurement and a fresh run differ, the differing keys are printed with both values.
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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpp_library import assemble_library, check_submission_code  # noqa: E402
from lesson_text import check_hub_summary, read_lesson_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LESSON_ID = "partial-information"
DATA = ROOT / "lessons" / LESSON_ID / "lesson-assets" / "measurements.json"
HARNESS = ROOT / "scripts" / "partial_information_harness.cpp"
HARNESS5 = ROOT / "scripts" / "partial_information_beam5_harness.cpp"
SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
BLOCKS = ("pi-grid", "pi-plan", "pi-policy", "pi-online", "pi-gen", "pi-run")
SEEDS = list(range(1, 21))
M64 = (1 << 64) - 1
WIN = 15   # of 20 seeds: a one-sided sign test at p < 0.05 (two-sided 0.041)

# ------------------------------------------------------------------ the experiments' definition
EST_ROWS = [(0, "비관: 모르는 칸 = 0"), (100, "모르는 칸 = 1"), (-1, "평균: 아는 칸의 평균"), (300, "모르는 칸 = 3"),
            (500, "모르는 칸 = 5"), (900, "낙관: 모르는 칸 = 9(최댓값)")]
EST1_ROWS = [(0, "비관"), (-1, "평균"), (900, "낙관")]
RADII = [0, 1, 2, 3, 4, 5, 99]
PERIODS = [1, 2, 3, 4, 6, 12]
HORIZONS = [2, 4, 8, 12, 20]
WIDTHS = [1, 4, 16, 64]
DENSITIES = [(2, "20%"), (6, "60%"), (9, "90%")]
DENSITY_EST = [(0, "비관"), (-1, "평균"), (900, "낙관")]
FUT_ROWS = [(-2, "탐욕: 앞일을 보지 않음"), (0, "앞으로 올 작업 길이 = 0"), (1, "앞으로 올 작업 길이 = 1"),
            (-1, "앞으로 올 작업 길이 = 도착한 작업의 평균"), (100, "앞으로 올 작업 길이 = 100(최댓값)")]
DMAXES = [100, 20]
DEFAULT = {"rad": 2, "est": -1, "H": 12, "per": 1, "W": 16, "z": 6}


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
    return assemble_library(["array", "sort"]) + "\n" + "\n".join(parts)


def build(code: str, workdir: Path, name: str, sanitize: bool, harness: Path = HARNESS) -> Path:
    sub = workdir / name
    sub.mkdir()
    (sub / "lesson.cpp").write_text(code)
    exe = sub / "run"
    flags = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"] if sanitize else ["-O1"]
    done = subprocess.run(["c++", "-std=c++17", *flags, f"-I{sub}", str(harness), "-o", str(exe)], capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError(done.stderr[:3000])
    return exe


def run(exe: Path, mode: str) -> list[list[str]]:
    out = subprocess.run([str(exe), mode], check=True, capture_output=True, text=True, timeout=300).stdout
    return [line.split() for line in out.splitlines() if line.strip()]


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


def gen_grid(seed: int, zeros10: int, n: int = 400):
    g = Gen(seed)
    out = []
    for _ in range(n):
        u = g.next(10)
        out.append(0 if u < zeros10 else 1 + g.next(9))
    return out


def gen_online(seed: int, dmax: int, n: int = 120, m: int = 8):
    g = Gen(seed)
    d, c = [], []
    for _ in range(n):
        d.append(1 + g.next(dmax))
        c.append([g.next(51) for _ in range(m)])
    return d, c


def online_cost(d, c, a, m):
    load = [0] * m
    for i, q in enumerate(a):
        load[q] += d[i]
    return sum(x * x for x in load) // 100 + sum(c[i][q] for i, q in enumerate(a))


def online_lower_bound(d, c, m):
    total = sum(d)
    return ((total * total + m - 1) // m) // 100 + sum(min(row) for row in c)


def check_gen(rows):
    seen = 0
    for kind, which, p1, seed, h, *rest in rows:
        seed = int(seed)
        if which == "grid":
            v = gen_grid(seed, int(p1))
            assert int(h) == fnv(v), "grid generator differs from the independent one"
            assert int(rest[0]) == sum(v)
        else:
            d, c = gen_online(seed, int(p1))
            hh = fnv(d)
            for row in c:
                hh = fnv(row, hh)
            assert int(h) == hh, "online generator differs from the independent one"
            assert int(rest[0]) == online_cost(d, c, [i % 8 for i in range(120)], 8)
            assert int(rest[1]) == online_lower_bound(d, c, 8)
        seen += 1
    assert seen == 100
    return seen


# hand examples ---------------------------------------------------------------
HAND_GRID = [0, 3, 0, 5, 0,
             2, 0, 0, 0, 1,
             0, 0, 6, 0, 0,
             0, 4, 0, 0, 0,
             7, 0, 0, 2, 0]
HAND_D = [36, 39, 46, 35, 53, 5]
HAND_C = [[0, 42, 46], [32, 50, 20], [20, 26, 0], [40, 45, 33], [46, 19, 19], [21, 1, 12]]


def view(pos: int, rad: int = 2, h: int = 5, w: int = 5):
    y, x = divmod(pos, w)
    return [c for c in range(h * w) if abs(c // w - y) + abs(c % w - x) <= rad]


def neighbours(pos: int, h: int = 5, w: int = 5):
    y, x = divmod(pos, w)
    out = []
    if y > 0: out.append(pos - w)
    if x + 1 < w: out.append(pos + 1)
    if y + 1 < h: out.append(pos + w)
    if x > 0: out.append(pos - 1)
    return out


def hand_grid():
    seen_at = [-1] * 25
    val = [0] * 25
    n_seen = sum_seen = 0
    dbl_n = dbl_sum = 0

    def observe(pos, t):
        nonlocal n_seen, sum_seen, dbl_n, dbl_sum
        for c in view(pos):
            if seen_at[c] < 0:
                n_seen += 1
                sum_seen += HAND_GRID[c]
            dbl_n += 1
            dbl_sum += HAND_GRID[c]
            val[c] = HAND_GRID[c]
            seen_at[c] = t

    observe(0, 0)
    out = {"first": {"cells": view(0), "values": [HAND_GRID[c] for c in view(0)], "n": n_seen, "sum": sum_seen,
                     "mean100": 100 * sum_seen // n_seen}}
    mean100 = out["first"]["mean100"]
    walks = []

    def rec(pos, depth, path):
        if depth == 0:
            walks.append(path)
            return
        for a in neighbours(pos):
            rec(a, depth - 1, path + [a])
    rec(0, 4, [])
    nodes = sum(len({tuple(w[:k]) for w in walks}) for k in range(1, 5))
    out["walks"] = len(walks)
    out["nodes"] = nodes
    plans = {}
    for est in (0, mean100, 900):
        best = None
        gains = []
        for w in walks:
            vis = {0}
            g = 0
            for a in w:
                if a not in vis:
                    vis.add(a)
                    g += 100 * HAND_GRID[a] if seen_at[a] >= 0 else est
            gains.append((g, w))
        top = max(g for g, _ in gains)
        plans[est] = {"best": top, "paths": sorted({tuple(w) for g, w in gains if g == top})}
    out["plans"] = {str(k): v["best"] for k, v in plans.items()}
    out["bestPaths"] = {str(k): [list(p) for p in v["paths"]] for k, v in plans.items()}
    # named candidates
    def path_gain(path, est):
        vis = {0}
        g = 0
        for a in path:
            if a not in vis:
                vis.add(a)
                g += 100 * HAND_GRID[a] if seen_at[a] >= 0 else est
        return g
    out["candidates"] = {name: {str(e): path_gain(p, e) for e in (0, mean100, 900)} for name, p in
                         (("K", [1, 6, 5, 10]), ("U", [1, 2, 3, 4]), ("D", [5, 10, 15, 20]))}
    # walk right, right, down
    mir = []
    for k, c in enumerate([1, 2, 7]):
        observe(c, k + 1)
        mir.append({"step": k + 1, "pos": c, "nSeen": n_seen, "sumSeen": sum_seen, "mean100": 100 * sum_seen // n_seen,
                    "doubleN": dbl_n, "doubleSum": dbl_sum})
    out["mirror"] = mir
    out["seenAt"] = list(seen_at)
    return out


def hand_online():
    def choose(load, cnt, ln, row, lam):
        best, bs = None, 0
        for q in range(3):
            if cnt[q] >= 3:
                continue
            s = 100 * row[q] + max(load[q] + ln, lam) ** 2 - max(load[q], lam) ** 2
            if best is None or s < bs:
                best, bs = q, s
        return best

    def cost(a):
        load = [0] * 3
        for i, q in enumerate(a):
            load[q] += HAND_D[i]
        return sum(x * x for x in load) // 100 + sum(HAND_C[i][q] for i, q in enumerate(a)), load

    out = {}
    for name, mode in (("greedy", -2), ("mean", -1)):
        load, cnt, a, dsum, rows = [0] * 3, [0] * 3, [], 0, []
        for i in range(6):
            ln = HAND_D[i]
            dsum += ln
            seen = i + 1
            lam = 0 if mode == -2 else (dsum + (6 - seen) * (dsum // seen)) // 3
            scores = [100 * HAND_C[i][q] + max(load[q] + ln, lam) ** 2 - max(load[q], lam) ** 2 for q in range(3)]
            q = choose(load, cnt, ln, HAND_C[i], lam)
            rows.append({"task": i, "lam": lam, "load": list(load), "scores": scores, "to": q})
            a.append(q); load[q] += ln; cnt[q] += 1
        out[name] = {"rows": rows, "cost": cost(a)[0], "load": cost(a)[1], "assign": a}
    valid = [a for a in itertools.product(range(3), repeat=6) if all(a.count(q) <= 3 for q in range(3))]
    out["valid"] = len(valid)
    out["optimum"] = min(cost(a)[0] for a in valid)
    out["roundRobin"] = cost([i % 3 for i in range(6)])[0]
    total = sum(HAND_D)
    out["lowerBound"] = ((total * total + 2) // 3) // 100 + sum(min(r) for r in HAND_C)
    # offline: true total, arrival order and longest first
    for name, order in (("offlineArrival", list(range(6))), ("offlineLongest", sorted(range(6), key=lambda i: (-HAND_D[i], i)))):
        load, cnt, a = [0] * 3, [0] * 3, [0] * 6
        for i in order:
            q = choose(load, cnt, HAND_D[i], HAND_C[i], total // 3)
            a[i] = q; load[q] += HAND_D[i]; cnt[q] += 1
        out[name] = cost(a)[0]
    return out


def check_hand(rows):
    hg, ho = hand_grid(), hand_online()
    g = {tuple(r[:2]): r for r in rows if r[0] == "hand" and r[1] in ("seen", "mean100", "mirrorok")}
    assert int(g[("hand", "seen")][2]) == hg["first"]["n"] and int(g[("hand", "seen")][3]) == hg["first"]["sum"]
    assert int(g[("hand", "mean100")][2]) == hg["first"]["mean100"]
    plans = [r for r in rows if r[:2] == ["hand", "plan"]]
    for r, est in zip(plans, (0, hg["first"]["mean100"], 900)):
        assert int(r[2]) == est or (est == hg["first"]["mean100"] and int(r[2]) == -1)
        assert int(r[3]) == hg["plans"][str(est)], (r, hg["plans"])
        assert int(r[4]) == hg["nodes"], "planner must evaluate every walk prefix when the width never prunes"
        path = [int(x) for x in r[5:9]]
        assert path in hg["bestPaths"][str(est)], (path, hg["bestPaths"][str(est)])
    mir = [r for r in rows if r[:2] == ["hand", "mirror"]]
    for r, m in zip(mir, hg["mirror"]):
        assert [int(r[2]), int(r[3]), int(r[4]), int(r[5])] == [m["step"], m["nSeen"], m["sumSeen"], m["pos"]], (r, m)
        assert int(r[8]) == m["mean100"]
    assert g[("hand", "mirrorok")][2] == "1"
    seen_row = next(r for r in rows if len(r) == 25 and all(x.lstrip("-").isdigit() for x in r))
    assert [int(x) for x in seen_row] == hg["seenAt"]
    for f, name in ((0, "greedy"), (1, "mean")):
        got = [r for r in rows if r[:2] == ["hand", "online"] and int(r[2]) == f]
        for r, want in zip(got, ho[name]["rows"]):
            assert int(r[3]) == want["task"] + 1 and int(r[4]) == want["lam"], (r, want)
            assert [int(x) for x in r[5:8]] == want["scores"] and int(r[9]) == want["to"], (r, want)
        fin = next(r for r in rows if r[:2] == ["hand", "onlinecost"] and int(r[2]) == f)
        assert int(fin[3]) == ho[name]["cost"] and [int(x) for x in fin[4:7]] == ho[name]["load"]
    off = next(r for r in rows if r[:2] == ["hand", "offline"])
    assert [int(x) for x in off[2:6]] == [ho["offlineArrival"], ho["offlineLongest"], ho["lowerBound"], ho["roundRobin"]]
    return {"grid": hg, "online": ho}


# ------------------------------------------------------------------ measurements
def med(xs):
    return int(statistics.median_low(list(xs)))


def verdict(better: int, worse: int) -> str:
    return "더 좋음" if better >= WIN else ("더 나쁨" if worse >= WIN else "결정 못 함")


def measure(rows, b5_rows) -> dict:
    G: dict = {}
    for r in rows:
        if r[0] == "G":
            tag, rad, est, H, per, W, z, seed = r[1], *[int(x) for x in r[2:9]]
            score, nseen, evals, plans = int(r[9]), int(r[10]), int(r[11]), int(r[12])
            G.setdefault((tag, rad, est, H, per, W, z), {})[seed] = (score, nseen, evals, plans)

    def series(key):
        d = G[key]
        return [d[s] for s in SEEDS]

    def pair(base_key, key, higher_better=True):
        a, b = series(base_key), series(key)
        better = sum((y[0] > x[0]) if higher_better else (y[0] < x[0]) for x, y in zip(a, b))
        worse = sum((y[0] < x[0]) if higher_better else (y[0] > x[0]) for x, y in zip(a, b))
        return better, worse

    d = DEFAULT
    base = ("est", d["rad"], d["est"], d["H"], d["per"], d["W"], d["z"])
    meas: dict = {"seeds": SEEDS, "grid": {}, "online": {}}
    gm = meas["grid"]
    gm["estimate"] = []
    for est, name in EST_ROWS:
        key = ("est", 2, est, 12, 1, 16, 6)
        better, worse = pair(base, key)
        s = series(key)
        gm["estimate"].append({"est": est, "name": name, "median": med(x[0] for x in s), "better": better, "worse": worse,
                               "known": med(x[1] for x in s)})
    gm["estimateRad1"] = []
    for est, name in EST1_ROWS:
        key = ("est1", 1, est, 12, 1, 16, 6)
        s = series(key)
        gm["estimateRad1"].append({"est": est, "name": name, "median": med(x[0] for x in s), "known": med(x[1] for x in s)})
    gm["radius"] = []
    for rad in RADII:
        key = ("rad", rad, -1, 12, 1, 16, 6)
        s = series(key)
        gm["radius"].append({"rad": rad, "median": med(x[0] for x in s), "known": med(x[1] for x in s)})
    gm["period"] = []
    pbase = ("per", 2, -1, 12, 1, 16, 6)
    for per in PERIODS:
        key = ("per", 2, -1, 12, per, 16, 6)
        better, worse = pair(pbase, key)
        s = series(key)
        gm["period"].append({"period": per, "median": med(x[0] for x in s), "better": better, "worse": worse,
                             "evals": med(x[2] for x in s), "plans": med(x[3] for x in s)})
    gm["horizon"] = []
    for hz in HORIZONS:
        key = ("hor", 2, -1, hz, 1, 16, 6)
        better, worse = pair(("hor", 2, -1, 12, 1, 16, 6), key)
        s = series(key)
        gm["horizon"].append({"horizon": hz, "median": med(x[0] for x in s), "better": better, "worse": worse, "evals": med(x[2] for x in s)})
    gm["width"] = []
    for w in WIDTHS:
        key = ("wid", 2, -1, 12, 1, w, 6)
        better, worse = pair(("wid", 2, -1, 12, 1, 16, 6), key)
        s = series(key)
        gm["width"].append({"width": w, "median": med(x[0] for x in s), "better": better, "worse": worse, "evals": med(x[2] for x in s)})
    # full information
    F: dict = {}
    for r in rows:
        if r[0] == "F":
            w, z, seed, score, ref, ev, ub = (int(x) for x in r[1:8])
            assert score == ref, "planFull score differs from the independent replay"
            F.setdefault((w, z), {})[seed] = (score, ev, ub)
    gm["full"] = {}
    for z, name in DENSITIES:
        e = {}
        for w in (16, 64):
            s = [F[(w, z)][sd] for sd in SEEDS]
            e[str(w)] = {"median": med(x[0] for x in s), "evals": med(x[1] for x in s)}
        ub = [F[(16, z)][sd][2] for sd in SEEDS]
        e["bound"] = med(ub)
        gm["full"][str(z)] = e
    # information cost: full(16) - partial(default), per seed
    part = series(base)
    full16 = [F[(16, 6)][sd][0] for sd in SEEDS]
    loss = [f - p[0] for f, p in zip(full16, part)]
    gm["cost"] = {"partial": med(x[0] for x in part), "full16": med(full16), "loss": med(loss),
                  "partialAtLeastFull": sum(p[0] >= f for f, p in zip(full16, part)),
                  "fullBetter": sum(f > p[0] for f, p in zip(full16, part))}
    # density
    gm["density"] = []
    for z, name in DENSITIES:
        row = {"zeros": name, "full": gm["full"][str(z)]["16"]["median"]}
        for est, ename in DENSITY_EST:
            s = series(("den", 2, est, 12, 1, 16, z))
            row[str(est)] = med(x[0] for x in s)
        gm["density"].append(row)
    # the beam-search lesson's own Beam on the same grids
    b5 = {}
    for r in b5_rows:
        b5.setdefault(int(r[1]), {})[int(r[2])] = int(r[3])
    gm["lesson5"] = {str(w): med(b5[w][s] for s in SEEDS) for w in sorted(b5)}
    # online
    A: dict = {}
    for r in rows:
        if r[0] == "A":
            fut, dmax, seed, cost, ref = (int(x) for x in r[1:6])
            assert cost == ref, "online cost differs from the independent replay"
            A.setdefault((fut, dmax), {})[seed] = cost
    O: dict = {}
    for r in rows:
        if r[0] == "O":
            dmax, seed, rr, oa, ol, lb = (int(x) for x in r[1:7])
            O.setdefault(dmax, {})[seed] = (rr, oa, ol, lb)
    om = meas["online"]
    for dmax in DMAXES:
        ref = A[(-1, dmax)]
        rowsd = []
        for fut, name in FUT_ROWS:
            costs = [A[(fut, dmax)][s] for s in SEEDS]
            better = sum(A[(fut, dmax)][s] < ref[s] for s in SEEDS)
            worse = sum(A[(fut, dmax)][s] > ref[s] for s in SEEDS)
            rowsd.append({"fut": fut, "name": name, "median": med(costs), "better": better, "worse": worse})
        extra = []
        for idx, name in ((0, "라운드 로빈(아무것도 보지 않음)"), (1, "전체 정보: 총 길이를 알고 도착 순서대로"),
                          (2, "전체 정보: 총 길이를 알고 긴 작업부터"), (3, "하한")):
            vals = [O[dmax][s][idx] for s in SEEDS]
            better = sum(O[dmax][s][idx] < ref[s] for s in SEEDS)
            worse = sum(O[dmax][s][idx] > ref[s] for s in SEEDS)
            extra.append({"name": name, "median": med(vals), "better": better, "worse": worse})
        om[str(dmax)] = {"policies": rowsd, "others": extra}
    return meas


# ------------------------------------------------------------------ mistakes
MUTATIONS = {
    "grid-unknown-zero": [("map100[c] = m.seenAt[c] >= 0 ? 100 * m.val[c] : guess;", "map100[c] = 100 * m.val[c];")],
    "grid-double-mean": [("if (seenAt[c] < 0) { ++nSeen; sumSeen += v[k]; }", "{ ++nSeen; sumSeen += v[k]; }")],
    "grid-stepped": [("if (!stepped[pos]) { stepped[pos] = true; got += val[pos]; }", "{ got += val[pos]; }")],
    "grid-no-observe": [("m.step(c); m.observe(j);", "m.step(c);")],
    "grid-peek": [("struct GridPolicy {", "const GridJudge* gPeek = 0;\nstruct GridPolicy {"),
                  ("map100[c] = m.seenAt[c] >= 0 ? 100 * m.val[c] : guess;", "map100[c] = m.seenAt[c] >= 0 ? 100 * m.val[c] : 100 * gPeek->v[c];"),
                  ("j.start(); m.begin(j); m.observe(j);", "j.start(); gPeek = &j; m.begin(j); m.observe(j);")],
    "online-stale-count": [("load[q] += len; ++cnt[q]; cSum += row[q];", "load[q] += len; cSum += row[q];")],
    "online-double-sum": [("load[q] += len; ++cnt[q]; cSum += row[q];", "load[q] += len; ++cnt[q]; cSum += row[q]; dSum += len;")],
    "online-peek": [("struct OnlinePolicy {", "const OnlineJudge* gPeekO = 0;\nlong long peekTotal() { long long t = 0; for (int i = 0; i < gPeekO->n; ++i) t += gPeekO->d[i]; return t; }\nstruct OnlinePolicy {"),
                    ("return (m.dSum + (long long)(m.n - m.seen) * each) / m.m;", "return peekTotal() / m.m;"),
                    ("if (firstBad) *firstBad = -1;", "if (firstBad) *firstBad = -1; gPeekO = &j;")],
}


def detect(rows) -> dict:
    out = {}
    for which in ("grid", "online"):
        sel = [r for r in rows if r[:2] == ["D", which]]
        assert len(sel) == 20
        bad = [int(r[3]) for r in sel]
        found = sorted(b for b in bad if b >= 0)
        peek_fail = sum(r[4] == "0" and int(r[5]) >= 0 for r in sel)   # an invalid run has no decisions to compare
        invalid = sum(int(r[5]) < 0 for r in sel)
        out[which] = {"mirrorFound": len(found), "mirrorFirstMedian": med(found) if found else 0,
                      "peekFound": peek_fail, "invalidRuns": invalid}
    return out


def run_mistakes(sn, workdir: Path) -> dict:
    out = {"clean": detect(run(build(assemble(sn), workdir, "h_clean", True), "detect"))}
    for name, edits in MUTATIONS.items():
        which = name.split("-")[0]
        out[name] = detect(run(build(assemble(sn, edits), workdir, "h_" + name.replace("-", "_"), False), "detect"))[which]
    return out


def check_mistakes(m: dict) -> None:
    for which in ("grid", "online"):
        c = m["clean"][which]
        assert c == {"mirrorFound": 0, "mirrorFirstMedian": 0, "peekFound": 0, "invalidRuns": 0}, (which, c)
    for name in ("grid-double-mean", "grid-stepped", "grid-no-observe", "online-stale-count", "online-double-sum"):
        assert m[name]["mirrorFound"] == 20, (name, m[name])
    assert m["grid-unknown-zero"]["mirrorFound"] >= 18, m["grid-unknown-zero"]
    assert m["grid-peek"]["peekFound"] == 20 and m["online-peek"]["peekFound"] == 20, (m["grid-peek"], m["online-peek"])
    for name in ("grid-double-mean", "grid-stepped", "grid-no-observe", "grid-unknown-zero", "online-double-sum", "online-peek", "grid-peek"):
        assert m[name]["peekFound"] == 0 or "peek" in name, (name, m[name])
    assert m["online-stale-count"]["invalidRuns"] > 0, m["online-stale-count"]


# ------------------------------------------------------------------ tables as they appear in the lesson
def fmt(x) -> str:
    return f"{int(x):,}"


def table_rows(meas: dict) -> dict[str, list[str]]:
    g, o = meas["grid"], meas["online"]
    rows: dict[str, list[str]] = {}
    rows["estimate"] = []
    for e in g["estimate"]:
        if e["est"] == -1:
            rows["estimate"].append(f"| {e['name']} | {fmt(e['median'])} | - | 기준 | {e['known']} |")
        else:
            rows["estimate"].append(f"| {e['name']} | {fmt(e['median'])} | {e['better']} / {e['worse']} | {verdict(e['better'], e['worse'])} | {e['known']} |")
    rows["estimate_rad1"] = [f"| {e['name']} | {fmt(e['median'])} | {e['known']} |" for e in g["estimateRad1"]]
    rows["radius"] = [f"| {'전체' if e['rad'] == 99 else e['rad']} | {fmt(e['median'])} | {e['known']} |" for e in g["radius"]]
    rows["period"] = []
    for e in g["period"]:
        if e["period"] == 1:
            rows["period"].append(f"| {e['period']} | {fmt(e['median'])} | - | 기준 | {fmt(e['plans'])} | {fmt(e['evals'])} |")
        else:
            rows["period"].append(f"| {e['period']} | {fmt(e['median'])} | {e['better']} / {e['worse']} | {verdict(e['better'], e['worse'])} | {fmt(e['plans'])} | {fmt(e['evals'])} |")
    for tag, key, name in (("horizon", "horizon", "깊이"), ("width", "width", "폭")):
        rows[tag] = []
        ref = 12 if tag == "horizon" else 16
        for e in g[key]:
            if e[key] == ref:
                rows[tag].append(f"| {e[key]} | {fmt(e['median'])} | - | 기준 | {fmt(e['evals'])} |")
            else:
                rows[tag].append(f"| {e[key]} | {fmt(e['median'])} | {e['better']} / {e['worse']} | {verdict(e['better'], e['worse'])} | {fmt(e['evals'])} |")
    c = g["cost"]
    rows["cost"] = [f"| 부분 정보(보이는 거리 2, 평균 추정) | {fmt(c['partial'])} |",
                    f"| 전체 정보 기준선(`planFull`, 폭 16) | {fmt(c['full16'])} |",
                    f"| 전체 정보 − 부분 정보의 시드별 차이(10번째로 작은 값) | {fmt(c['loss'])} |"]
    rows["lesson5"] = [f"| 5번 강의의 `Beam`(합치기 포함), 폭 {w} | {fmt(v)} |" for w, v in g["lesson5"].items()]
    rows["density"] = []
    for e in g["density"]:
        rows["density"].append(f"| {e['zeros']} | {fmt(e['0'])} | {fmt(e['-1'])} | {fmt(e['900'])} | {fmt(e['full'])} | {fmt(g['full'][{'20%': '2', '60%': '6', '90%': '9'}[e['zeros']]]['bound'])} |")
    for dmax in DMAXES:
        tag = f"online_{dmax}"
        rows[tag] = []
        for e in o[str(dmax)]["policies"]:
            if e["fut"] == -1:
                rows[tag].append(f"| {e['name']} | {fmt(e['median'])} | - | 기준 |")
            else:
                rows[tag].append(f"| {e['name']} | {fmt(e['median'])} | {e['better']} / {e['worse']} | {verdict(e['better'], e['worse'])} |")
        for e in o[str(dmax)]["others"]:
            rows[tag].append(f"| {e['name']} | {fmt(e['median'])} | {e['better']} / {e['worse']} | {verdict(e['better'], e['worse'])} |")
    return rows


def hub_expected(meas: dict) -> list[tuple[str, str]]:
    g, o = meas["grid"], meas["online"]
    est = {e["est"]: e for e in g["estimate"]}
    pol = {e["fut"]: e for e in o["100"]["policies"]}
    oth = {e["name"]: e for e in o["100"]["others"]}
    return [("격자 · 비관(모르는 칸 = 0) ↑", fmt(est[0]["median"])),
            ("격자 · 평균 추정 ↑", fmt(est[-1]["median"])),
            ("격자 · 전체 정보 기준선(폭 16) ↑", fmt(g["cost"]["full16"])),
            ("배정 · 탐욕(앞일을 보지 않음) ↓", fmt(pol[-2]["median"])),
            ("배정 · 앞으로 올 작업 길이 = 평균 ↓", fmt(pol[-1]["median"])),
            ("배정 · 전체 정보(총 길이를 앎, 도착 순서) ↓", fmt(oth["전체 정보: 총 길이를 알고 도착 순서대로"]["median"]))]


def mistake_rows(m: dict) -> list[str]:
    names = [("grid-unknown-zero", "격자: 모르는 칸을 0으로 읽음"), ("grid-double-mean", "격자: 다시 보인 칸을 평균에 또 더함"),
             ("grid-stepped", "격자: 밟은 칸 표시를 빠뜨림"), ("grid-no-observe", "격자: 움직인 뒤 보기를 빠뜨림"),
             ("grid-peek", "격자: 못 본 칸의 진짜 값을 읽음"), ("online-stale-count", "배정: 기계별 작업 수 갱신을 빠뜨림"),
             ("online-double-sum", "배정: 도착한 길이를 두 번 더함"), ("online-peek", "배정: 앞으로 올 작업의 진짜 총 길이를 읽음")]
    rows = []
    for key, label in names:
        e = m[key]
        first = f"{e['mirrorFound']} / 20" + (f"(첫 어긋남 {e['mirrorFirstMedian']}번째)" if e["mirrorFound"] else "")
        rows.append(f"| {label} | {first} | {e['peekFound']} / 20 | {e['invalidRuns']} / 20 |")
    return rows


def check_text_tables(meas: dict, mistakes: dict) -> int:
    text = read_lesson_text(LESSON_ID)
    count = 0
    for name, rows in table_rows(meas).items():
        for row in rows:
            assert row in text, f"lesson table row missing or differs ({name}): {row}"
            count += 1
    for row in mistake_rows(mistakes):
        assert row in text, f"mistake table row missing or differs: {row}"
        count += 1
    count += check_hub_summary(LESSON_ID, hub_expected(meas))
    return count


def diff(x, y, path, out):
    if len(out) >= 30:
        return
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            diff(x.get(k), y.get(k), f"{path}.{k}", out)
    elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        for i, (u, v) in enumerate(zip(x, y)):
            diff(u, v, f"{path}[{i}]", out)
    elif x != y:
        out.append(f"{path}: stored {x!r} fresh {y!r}")


# ------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", action="store_true", help="write lesson-assets/measurements.json from a fresh run")
    ap.add_argument("--print-tables", action="store_true")
    args = ap.parse_args()

    sn = snippets()
    code = assemble(sn)
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_beam_search as cb  # the beam-search lesson's own code, for the cross-check
    cb_code = cb.assemble(cb.snippets())
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "syntax.cpp").write_text(code)
        done = subprocess.run(["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", str(work / "syntax.cpp")],
                              capture_output=True, text=True)
        assert done.returncode == 0, done.stderr[:2000]
        exe = build(code, work, "harness", True)

        n_gen = check_gen(run(exe, "gen"))
        ref = run(exe, "ref")
        n_ref = 0
        for r in ref:
            kind, which, cfg, seed, score, refscore, bad, peek = r
            assert int(score) == int(refscore) >= 0, f"score differs from the independent replay: {r}"
            assert int(bad) == -1, f"mirror differs from the judge: {r}"
            assert peek == "1", f"decision depends on hidden information: {r}"
            n_ref += 1
        assert n_ref == 4 * 20 + 6 * 20
        beam_rows = run(exe, "beam")
        assert beam_rows[0] == ["beam", "120", "0"], f"planBeam differs from brute force: {beam_rows[0]}"
        assert all(r[2] == r[3] for r in beam_rows[1:]), "planFull path does not replay to its score"
        hand = check_hand(run(exe, "hand"))
        exp_rows = run(exe, "exp")
        b5_exe = build(cb_code, work, "beam5", False, HARNESS5)
        b5_rows = run(b5_exe, "")
        meas = measure(exp_rows, b5_rows)
        mistakes = run_mistakes(sn, work)
        check_mistakes(mistakes)

    meas.update({"schema": 1, "hand": hand, "mistakes": mistakes,
                 "rule": f"한쪽이 {WIN} / 20 시드 이상 나으면 차이가 있다고 보고, 아니면 결정 못 함",
                 "problems": {"grid": "H=W=20, T=60, 값 0..9(60%는 0), 보이는 거리 2, 시작 칸 0",
                              "online": "N=120, M=8, K=18, 부하 제곱합/100 + 추가 비용, 작업은 번호 순서로 도착"}})
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
        return
    stored = json.loads(DATA.read_text(encoding="utf-8"))
    fresh = json.loads(json.dumps(meas))
    if stored != fresh:
        out: list[str] = []
        diff(stored, fresh, "", out)
        print("\n".join(out))
        raise AssertionError("measurements.json differs from a fresh measurement (run with --output)")
    n_rows = check_text_tables(stored, stored["mistakes"])
    print(f"partial-information ok: {len(BLOCKS)} code blocks, {n_gen} generated instances checked against Python, "
          f"{n_ref} runs replayed by the independent reference with the mirror equal to the judge, planner equal to brute force on {beam_rows[0][1]} small maps, "
          f"8 injected mistakes detected, {n_rows} table rows matched the measurements")


if __name__ == "__main__":
    main()
