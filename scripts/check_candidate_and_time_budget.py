"""Check the candidate-and-time-budget lesson: code blocks, grid lists == brute-force lists, hand examples,
candidate-move correctness, injected mistakes, operation-count experiments, measurements.

What runs (about 40 s wall time; the independent runs go in parallel):
  * every code block is extracted, rejected if it uses a header / STL / dynamic allocation, assembled with the
    `array` and `random` library blocks and compiled header-free with -Wall -Wextra -Werror -fsyntax-only;
    the timing program of the practice page (general C++17 page) is compiled with standard headers and run;
  * a harness (standard headers allowed there) including the lesson code runs under ASan/UBSan for the
    correctness modes (generator, lists, delta against recomputation, hand examples) and optimised for the
    experiments; reference costs, validity and k-nearest lists are written independently here and in Python;
  * the injected mistakes are put into the lesson code and must be caught. The mutated builds are never asked
    to produce numbers that depend on out-of-range reads: only "caught or not" is used;
  * the experiments (operation counts only, no wall-clock time) are re-run, summarised here, compared with
    lesson-assets/measurements.json and with the tables in the lesson text. When the stored measurement and a
    fresh one differ, the keys that differ are printed.
--output writes measurements.json from a fresh run; --print-tables prints the markdown table rows.
"""
from __future__ import annotations

import argparse
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
LESSON_ID = "candidate-and-time-budget"
DATA = ROOT / "lessons" / LESSON_ID / "lesson-assets" / "measurements.json"
HARNESS = ROOT / "scripts" / "candidate_and_time_budget_harness.cpp"
SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
BLOCKS = ("tb-frame", "tb-route", "tb-assign", "tb-gen", "tb-run")
TIMING = "tb-timing"
SEEDS = list(range(1, 21))
M64 = (1 << 64) - 1
WIN = 15   # of 20 seeds: one-sided sign test at p < 0.05 (two-sided 0.041)
KS = [0, 2, 4, 8, 16, 32]
REF_K = 8
STAGE_NAMES = ["고정 8", "고정 16", "넓게 시작 16 → 4", "좁게 시작 4 → 16", "고정 8 + 마무리 10%"]
ROUTE_N = {2000: 2000000, 10000: 12000000}          # the ample budgets
TIGHT = {2000: 400000, 10000: 3000000}
ASSIGN_BUDGET = 2000000
LIST_CASES = [("route", 2000, 400000), ("route", 2000, 2000000), ("route", 10000, 3000000), ("route", 10000, 12000000), ("assign", 2000, 2000000)]
EVERYS = [1, 4, 16, 64, 256, 1024, 4096]
CLOCK_COST = 40


def snippets(text: str | None = None) -> dict[str, str]:
    found: dict[str, str] = {}
    for name, code in SNIP_RE.findall(text if text is not None else read_lesson_text(LESSON_ID)):
        assert name not in found, f"duplicate snippet {name}"
        if name != TIMING:                       # the timing program needs standard headers (general C++17 page)
            check_submission_code(code, name)
        found[name] = code + "\n"
    assert set(BLOCKS) | {TIMING} <= set(found), f"missing snippets: {(set(BLOCKS) | {TIMING}) - set(found)}"
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
    return assemble_library(["array", "random"]) + "\n" + "\n".join(parts)


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


def isqrt(v: int) -> int:
    r = 0
    while (r + 1) * (r + 1) <= v:
        r += 1
    return r


def gen_route(seed: int, n: int):
    g = Gen(seed)
    px, py = [], []
    for _ in range(n):
        px.append(g.next(1000))
        py.append(g.next(1000))
    return px, py


def dist(px, py, u, v) -> int:
    return abs(px[u] - px[v]) + abs(py[u] - py[v])


def route_cost(px, py, order) -> int:
    return sum(dist(px, py, order[k], order[k + 1]) for k in range(len(order) - 1))


def snake(px, py, side: int):
    """Points ordered by cell (row by row, alternating direction), ties by index."""
    g = (1000 + side - 1) // side
    cells: dict[int, list[int]] = {}
    for v in range(len(px)):
        cells.setdefault((py[v] // side) * g + px[v] // side, []).append(v)
    order = []
    for cy in range(g):
        cols = range(g) if cy % 2 == 0 else range(g - 1, -1, -1)
        for cx in cols:
            order += cells.get(cy * g + cx, [])
    return order


def default_side(n: int) -> int:
    return max(5, isqrt(2000000 // n))


def knn_lists(px, py, k: int):
    n = len(px)
    return [[v for _, v in sorted((dist(px, py, u, v), v) for v in range(n) if v != u)[:k]] for u in range(n)]


AN, AM, AK = 2000, 200, 14


def gen_assign(seed: int):
    g = Gen(seed)
    d, c = [], []
    for _ in range(AN):
        d.append(1 + g.next(100))
        c.append([g.next(51) for _ in range(AM)])
    return d, c


def assign_cost(d, c, a) -> int:
    load = [0] * AM
    for i, j in enumerate(a):
        load[j] += d[i]
    return sum(x * x for x in load) // 100 + sum(c[i][j] for i, j in enumerate(a))


def check_gen(rows):
    seen = 0
    for r in rows:
        if r[:2] == ["gen", "route"]:
            n, seed = int(r[2]), int(r[3])
            px, py = gen_route(seed, n)
            assert int(r[4]) == fnv(px + py) or int(r[4]) == fnv(py, fnv(px)), "route generator differs from the independent one"
            order = snake(px, py, default_side(n))
            assert int(r[8]) == default_side(n) and int(r[7]) == fnv(order), "initial snake order differs from the independent one"
            assert int(r[5]) == int(r[6]) == route_cost(px, py, order)
        else:
            seed = int(r[2])
            d, c = gen_assign(seed)
            hh = fnv(d)
            for row in c:
                hh = fnv(row, hh)
            assert int(r[3]) == hh, "assign generator differs from the independent one"
            assert int(r[4]) == int(r[5]) == assign_cost(d, c, [i % AM for i in range(AN)])
        seen += 1
    assert seen == 43
    return seen


# ------------------------------------------------------------------ hand example (independent re-implementation of the ring search)
HAND_PTS = [(90, 430), (390, 780), (760, 10), (770, 870), (910, 440), (90, 400), (460, 400), (620, 900)]
HAND_SIDE = 250
HAND_K = 3


def hand_python():
    px = [p[0] for p in HAND_PTS]
    py = [p[1] for p in HAND_PTS]
    n = len(px)
    side = HAND_SIDE
    g = (1000 + side - 1) // side
    order = snake(px, py, side)
    cells: dict[int, list[int]] = {}
    for v in range(n):
        cells.setdefault((py[v] // side) * g + px[v] // side, []).append(v)
    k = HAND_K
    out = {"points": [{"id": v, "xy": [px[v], py[v]], "cell": [px[v] // side, py[v] // side]} for v in range(n)],
           "snake": order, "snakeCost": route_cost(px, py, order)}

    ops = {"n": 0}

    def make_offer(best):
        def offer(v, d):                         # the same insertion as the lesson's offer(), shifts counted
            if len(best) == k and (d, v) > best[-1]:
                return
            if len(best) < k:
                best.append((d, v))
                i = len(best) - 1
            else:
                i = k - 1
            while i > 0 and best[i - 1] > (d, v):
                best[i] = best[i - 1]
                ops["n"] += 1
                i -= 1
            best[i] = (d, v)
        return offer

    grid_lists, trace = [], []
    ops["n"] = 0
    for u in range(n):
        best: list[tuple[int, int]] = []
        offer = make_offer(best)
        cx, cy = px[u] // side, py[u] // side
        visited = dists = 0
        r_final = 0
        for r in range(g):
            for y in range(cy - r, cy + r + 1):
                step = 1 if (y == cy - r or y == cy + r) else 2 * r
                for x in range(cx - r, cx + r + 1, step):
                    if x < 0 or y < 0 or x >= g or y >= g:
                        continue
                    ops["n"] += 1
                    visited += 1
                    for v in cells.get(y * g + x, []):
                        if v != u:
                            ops["n"] += 1
                            dists += 1
                            offer(v, dist(px, py, u, v))
            r_final = r
            if len(best) == k and best[-1][0] <= r * side:
                break
        grid_lists.append([v for _, v in best])
        trace.append({"id": u, "rings": r_final, "cells": visited, "distances": dists, "list": [[v, d] for d, v in best]})
    grid_ops = ops["n"]
    brute_lists = []
    ops["n"] = 0
    for u in range(n):
        best = []
        offer = make_offer(best)
        for v in range(n):
            if v != u:
                ops["n"] += 1
                offer(v, dist(px, py, u, v))
        brute_lists.append([v for _, v in best])
    assert grid_lists == brute_lists == knn_lists(px, py, k), "hand lists differ"
    out.update({"gridOps": grid_ops, "bruteOps": ops["n"], "lists": grid_lists, "trace": trace})
    # ring-by-ring record of one search (point 5, two nearest) for the hand-worked table
    u, k2 = 5, 2
    best2: list[tuple[int, int]] = []
    cx, cy = px[u] // side, py[u] // side
    rings = []
    for r in range(g):
        seen_cells, offered = [], []
        for y in range(cy - r, cy + r + 1):
            step = 1 if (y == cy - r or y == cy + r) else 2 * r
            for x in range(cx - r, cx + r + 1, step):
                if x < 0 or y < 0 or x >= g or y >= g:
                    continue
                seen_cells.append([x, y])
                for v in cells.get(y * g + x, []):
                    if v != u:
                        offered.append([v, dist(px, py, u, v)])
        for v, d in offered:
            best2 = sorted(best2 + [(d, v)])[:k2]
        stop = len(best2) == k2 and best2[-1][0] <= r * side
        rings.append({"ring": r, "cells": len(seen_cells), "offered": offered, "list": [[v, d] for d, v in best2], "limit": r * side, "stop": stop})
        if stop:
            break
    assert [v for _, v in best2] == [v for _, v in sorted((dist(px, py, u, v), v) for v in range(n) if v != u)[:k2]]
    out["ringTrace"] = {"point": u, "k": k2, "rings": rings}
    pos = {v: i for i, v in enumerate(order)}
    revs = {}
    base = route_cost(px, py, order)
    rank = {}
    for item in range(2 * n):                    # item = (position, direction), as in the lesson's cand()
        a = item // 2
        for q in range(k):
            b = pos[grid_lists[order[a]][q]]
            lo, hi = min(a, b), max(a, b)
            if hi < lo + 2:
                continue
            lr = (lo + 1, hi) if item % 2 == 0 else (lo, hi - 1)
            rank[lr] = min(rank.get(lr, 99), q)
    for l in range(n - 1):
        for r in range(l + 1, n):
            q = order[:l] + order[l:r + 1][::-1] + order[r + 1:]
            revs[(l, r)] = (route_cost(px, py, q) - base, rank.get((l, r), 255))
    out["revs"] = {f"{l},{r}": list(v) for (l, r), v in revs.items()}
    best_move = min(revs, key=lambda m: (revs[m][0], m))
    out["best"] = {"move": list(best_move), "delta": revs[best_move][0], "rank": revs[best_move][1]}
    improving = sorted((v[0], m) for m, v in revs.items() if v[0] < 0)
    out["improving"] = [[m[0], m[1], dl, revs[m][1]] for dl, m in improving]
    return out


def check_hand(rows):
    h = hand_python()
    snake_row = next(r for r in rows if r[:3] == ["hand", "route", "snake"])
    assert int(snake_row[3]) == 2 * 8 + 16 + 8 and [int(x) for x in snake_row[4:12]] == h["snake"] and int(snake_row[12]) == h["snakeCost"]
    lists_row = next(r for r in rows if r[:2] == ["hand", "lists"])
    assert int(lists_row[2]) == h["gridOps"] and int(lists_row[3]) == h["bruteOps"] and int(lists_row[4]) == 0, (lists_row, h["gridOps"], h["bruteOps"])
    for r in rows:
        if r[:2] == ["hand", "nb"]:
            assert [int(x) for x in r[3:6]] == h["lists"][int(r[2])]
        elif r[:2] == ["hand", "rev"]:
            dl, rank = h["revs"][f"{r[2]},{r[3]}"]
            assert int(r[4]) == dl and int(r[5]) == rank, (r, dl, rank)
    assert sum(1 for r in rows if r[:2] == ["hand", "rev"]) == 28
    # assignment: six jobs, four machines, at most two jobs per machine
    a = hand_assign_python()
    assert int(next(r for r in rows if r[:3] == ["hand", "assign", "start"])[3]) == a["start"]
    for r in rows:
        if r[:2] == ["hand", "alist"]:
            assert [int(x) for x in r[3:6]] == a["lists"][int(r[2])]
    got = {(int(r[2]), int(r[3])): (int(r[4]), int(r[5])) for r in rows if r[:2] == ["hand", "amove"]}
    assert got == {(i, y): v for i, y, v in a["moves"]}, (got, a["moves"])
    h["assign"] = {"start": a["start"], "lists": a["lists"], "moves": [[i, y, dl, rk] for i, y, (dl, rk) in a["moves"]]}
    # clock reading: five operations per proposal, one read costs four, limit 60
    h["clock"] = {}
    for r in rows:
        if r[:2] == ["hand", "clock"]:
            every = int(r[2])
            sim = clock_sim(60, 4, every, 5)
            assert [int(x) for x in r[3:6]] == list(sim), (r, sim)
            h["clock"][str(every)] = {"proposals": sim[0], "reads": sim[1], "ops": sim[2]}
    assert set(h["clock"]) == {"1", "4"}
    # remaining-budget schedule: 800 operations of search left at the start
    h["sched"] = {}
    for r in rows:
        if r[:2] == ["hand", "sched"]:
            rem = int(r[2])
            want_a, want_b = 4 + 12 * rem // 800, 16 - 12 * rem // 800
            assert int(r[3]) == want_a and int(r[4]) == want_b, (r, want_a, want_b)
            h["sched"][str(rem)] = [want_a, want_b]
    assert len(h["sched"]) == 5
    return h


HAND_D = [70, 30, 40, 30, 80, 60]
HAND_C = [[10, 10, 10, 40], [10, 30, 30, 40], [0, 30, 0, 0], [0, 0, 40, 20], [10, 30, 20, 30], [40, 30, 20, 40]]


def hand_assign_python():
    m, cap = 4, 2
    start_as = [i % m for i in range(6)]

    def cost(a):
        load = [0] * m
        for i, j in enumerate(a):
            load[j] += HAND_D[i]
        return sum(x * x for x in load) // 100 + sum(HAND_C[i][j] for i, j in enumerate(a))

    base = cost(start_as)
    lists = [[j for _, j in sorted((HAND_C[i][j], j) for j in range(m))[:3]] for i in range(6)]
    moves = []
    for i in range(6):
        for y in range(m):
            if y == start_as[i] or start_as.count(y) >= cap:
                continue
            b = start_as[:]
            b[i] = y
            moves.append((i, y, (cost(b) - base, lists[i].index(y) if y in lists[i] else 255)))
    return {"start": base, "lists": lists, "moves": moves}


def clock_sim(limit: int, clock_cost: int, every: int, per_proposal: int):
    ops = props = reads = 0
    since = every
    while True:
        since += 1
        if since >= every:
            since = 0
            ops += clock_cost
            reads += 1
            if ops >= limit:
                break
        ops += per_proposal
        props += 1
    return props, reads, ops


# ------------------------------------------------------------------ measurements
def med(xs):
    return int(statistics.median_low(list(xs)))


def split_rows(rows):
    out: dict[str, list[list[str]]] = {}
    for r in rows:
        out.setdefault(r[0], []).append(r)
    return out


def compare(per: dict[int, int], ref: dict[int, int]):
    better = sum(per[s] < ref[s] for s in SEEDS)
    worse = sum(per[s] > ref[s] for s in SEEDS)
    return better, worse


def verdict(better: int, worse: int) -> str:
    return "더 좋음" if better >= WIN else ("더 나쁨" if worse >= WIN else "결정 못 함")


def measure(exp_rows, lists_rows, miss_rows) -> dict:
    by = split_rows(exp_rows)
    meas: dict = {"seeds": SEEDS, "clockCost": CLOCK_COST, "budgets": {"route": {str(n): b for n, b in ROUTE_N.items()}, "assign": 2000000}}
    # starts
    t2: dict = {}
    for r in by["T2"]:
        frame, n, budget, k, seed = r[1], int(r[2]), int(r[3]), int(r[4]), int(r[5])
        cost, props, ops, writes, built, start, ref, reads = (int(x) for x in r[6:14])
        assert cost == ref, f"tracked cost differs from the reference ({frame} {n} {k} {seed})"
        t2.setdefault((frame, n, budget, k), {})[seed] = {"cost": cost, "props": props, "ops": ops, "writes": writes, "built": built, "start": start}
    meas["start"] = {"route2000": med(t2[("route", 2000, 2000000, 0)][s]["start"] for s in SEEDS),
                     "route10000": med(t2[("route", 10000, 12000000, 0)][s]["start"] for s in SEEDS),
                     "assign": med(t2[("assign", 2000, 2000000, 0)][s]["start"] for s in SEEDS)}
    # build costs (k = 8, n = 2000 and 10000), cell sizes
    b2000 = [r for r in lists_rows if r[0] == "build" and r[1] == "2000"]
    b10000 = [r for r in lists_rows if r[0] == "build" and r[1] == "10000"]
    big = next(r for r in lists_rows if r[0] == "lists10000")
    assert big[2] == "0", "grid lists differ from brute-force lists at n = 10000"
    meas["build"] = {
        "2000": {"cells": med(int(r[3]) for r in b2000), "grid": med(int(r[4]) - int(r[3]) for r in b2000), "brute": med(int(r[5]) for r in b2000), "side": default_side(2000), "g": (1000 + default_side(2000) - 1) // default_side(2000)},
        "10000": {"cells": med(int(r[3]) for r in b10000), "grid": med(int(r[4]) - int(r[3]) for r in b10000), "bruteSeed1": int(big[4]), "side": default_side(10000), "g": int(big[5])}}
    sides = {}
    for r in lists_rows:
        if r[0] == "side":
            sides.setdefault(int(r[1]), []).append((int(r[3]), int(r[4])))
    meas["sides"] = [{"side": s, "g": v[0][1], "ops": med(x[0] for x in v)} for s, v in sorted(sides.items())]
    # composition of the budget and cost per evaluation
    meas["compose"] = []
    for frame, n, k in (("route", 2000, 8), ("route", 10000, 8), ("assign", 2000, 4)):
        v = [t2[(frame, n, ASSIGN_BUDGET if frame == "assign" else ROUTE_N[n], k)][s] for s in SEEDS]
        meas["compose"].append({"frame": frame, "n": n, "k": k, "ops": med(x["ops"] for x in v), "built": med(x["built"] for x in v),
                                 "terms": med(x["ops"] - x["built"] - x["writes"] for x in v), "proposals": med(x["props"] for x in v),
                                 "writes": med(x["writes"] for x in v), "perProposal": statistics.median_low([(x["ops"] - x["built"] - x["writes"]) * 100 // x["props"] for x in v])})
    # list size comparison
    meas["lists"] = {}
    for frame, n, budget in LIST_CASES:
        ref_costs = {s: t2[(frame, n, budget, REF_K)][s]["cost"] for s in SEEDS}
        entries = []
        for k in KS:
            c = {s: t2[(frame, n, budget, k)][s]["cost"] for s in SEEDS}
            better, worse = compare(c, ref_costs)
            entries.append({"k": k, "median": med(c.values()), "better": better, "worse": worse, "proposals": med(t2[(frame, n, budget, k)][s]["props"] for s in SEEDS),
                            "built": med(t2[(frame, n, budget, k)][s]["built"] for s in SEEDS)})
        meas["lists"][f"{frame}{n}@{budget}"] = entries
    ref_costs = {s: t2[("route", 2000, 2000000, REF_K)][s]["cost"] for s in SEEDS}
    brute = {int(r[4]): (int(r[5]), int(r[6]), int(r[7]), int(r[8])) for r in by["T2b"]}
    bc = {s: v[0] for s, v in brute.items()}
    better, worse = compare(bc, ref_costs)
    meas["bruteLists2000"] = {"median": med(bc.values()), "better": better, "worse": worse, "built": med(v[3] for v in brute.values()), "proposals": med(v[1] for v in brute.values())}
    # assignment: list build cost against the budget
    c1 = {}
    for r in by["T2c"]:
        c1.setdefault(int(r[3]), {})[int(r[4])] = int(r[5])
    meas["assignBudget"] = []
    for budget, get in ((1000000, lambda k: c1[k]), (2000000, lambda k: {s: t2[("assign", 2000, 2000000, k)][s]["cost"] for s in SEEDS})):
        a, b = get(0), get(4)
        better, worse = compare(b, a)       # list (k = 4) against no list
        meas["assignBudget"].append({"budget": budget, "none": med(a.values()), "list": med(b.values()), "listBetter": better, "listWorse": worse})
    # stages
    st: dict = {}
    for r in by["T4"]:
        st.setdefault((r[1], int(r[2])), {})[int(r[3])] = int(r[4])
    meas["stages"] = {}
    for frame in ("route", "assign"):
        entries = []
        for ci, name in enumerate(STAGE_NAMES):
            per = st[(frame, ci)]
            better, worse = compare(per, st[(frame, 0)])
            better16, worse16 = compare(per, st[(frame, 1)])
            entries.append({"name": name, "median": med(per.values()), "better": better, "worse": worse, "better16": better16, "worse16": worse16})
        meas["stages"][frame] = entries
    # doubling
    db: dict = {}
    for r in by["T5"]:
        db.setdefault((r[1], int(r[2]), int(r[3])), {})[int(r[4])] = int(r[5])
    meas["doubling"] = {}
    for key in sorted({(f, n) for f, n, _ in db}):
        budgets = sorted(b for f, n, b in db if (f, n) == key)
        rows_ = []
        prev = None
        for b in budgets:
            m = med(db[(key[0], key[1], b)].values())
            rows_.append({"budget": b, "median": m, "drop": None if prev is None else prev - m})
            prev = m
        meas["doubling"][f"{key[0]}{key[1]}"] = rows_
    # clock
    ck: dict = {}
    for r in by["T6"]:
        ck.setdefault((r[1], int(r[2])), []).append((int(r[4]), int(r[5]), int(r[6]), int(r[7])))
    meas["clock"] = {}
    for frame in ("route", "assign"):
        meas["clock"][frame] = [{"every": e, "reads": med(x[1] for x in ck[(frame, e)]), "share": med(x[1] * CLOCK_COST * 1000 // 2000000 for x in ck[(frame, e)]),
                                 "proposals": med(x[3] for x in ck[(frame, e)]), "cost": med(x[0] for x in ck[(frame, e)]),
                                 "overshoot": max(x[2] - 2000000 for x in ck[(frame, e)])} for e in EVERYS]
    # misses
    ms: dict = {}
    for r in miss_rows:
        ms.setdefault((r[1], int(r[2])), []).append([int(x) for x in r[4:]])
    meas["miss"] = {}
    for frame in ("route", "assign"):
        out = []
        for state in (0, 1):
            v = ms[(frame, state)]
            assert len(v) == 20
            per_k = []
            left = [x for x in v if x[0] < 0]
            for q, k in enumerate((2, 4, 8, 16, 32)):
                inside = sum(1 for x in left if x[0] == x[1 + q])
                ratio = (sum(x[1 + q] for x in left) * 1000) // sum(x[0] for x in left)      # sum of best gains inside the list / sum of best gains overall
                per_k.append({"k": k, "inside": inside, "permille": ratio})
            out.append({"state": state, "perK": per_k, "seedsLeft": len(left), "improving": med(x[6] for x in v), "improvingIn8": med(x[7] for x in v),
                        "cost": med(x[8] for x in v)})
        meas["miss"][frame] = out
    return meas


def verify_finals(exp_rows) -> int:
    """The final solutions printed for the hub-table configurations must have the tracked cost."""
    finals = {}
    for r in exp_rows:
        if r[0] == "final":
            finals[(r[1], int(r[2]), int(r[3]), int(r[4]))] = [int(x) for x in r[5:]]
    tracked = {}
    for r in exp_rows:
        if r[0] == "T2" and int(r[3]) == (ASSIGN_BUDGET if r[1] == "assign" else ROUTE_N[int(r[2])]):
            tracked[(r[1], int(r[2]), int(r[4]), int(r[5]))] = int(r[6])
    count = 0
    cache: dict = {}
    for (frame, n, k, seed), sol in finals.items():
        if frame == "route":
            if (n, seed) not in cache:
                cache[(n, seed)] = gen_route(seed, n)
            px, py = cache[(n, seed)]
            assert sorted(sol) == list(range(n))
            assert route_cost(px, py, sol) == tracked[(frame, n, k, seed)]
        else:
            if ("a", seed) not in cache:
                cache[("a", seed)] = gen_assign(seed)
            d, c = cache[("a", seed)]
            assert len(sol) == AN and all(0 <= j < AM for j in sol) and max(sol.count(j) for j in range(AM)) <= AK
            assert assign_cost(d, c, sol) == tracked[(frame, n, k, seed)]
        count += 1
    assert count == 4 * 20 + 2 * 20, count
    return count


# ------------------------------------------------------------------ mistakes
MUTATIONS = {
    "ring": ("if (bc == kk && bd[kk - 1] <= r * cs) break;", "if (bc == kk && bd[kk - 1] <= (r + 1) * cs) break;"),
    "pos": ("        for (int i = mv.a; i <= mv.b; ++i) pos[p[i]] = i;\n", ""),
    "direction": ("k = byRemaining(pl.kFirst, pl.kLast, stop - p.ops, stop - begin);", "k = byRemaining(pl.kFirst, pl.kLast, p.ops - begin, stop - begin);"),
}


def detect(rows) -> dict:
    d = next(r for r in rows if r[0] == "D")
    s = next(r for r in rows if r[0] == "S")
    return {"listsWrongSeeds": int(d[1]), "posWrongSeeds": int(d[2]), "earlyMaxK": int(s[1]), "lateMaxK": int(s[2])}


def run_mistakes(sn, workdir: Path) -> dict:
    clean = detect(run(build(assemble(sn), workdir, "h_clean", False), "detect"))
    out = {"clean": clean}
    for name, edit in MUTATIONS.items():
        out[name] = detect(run(build(assemble(sn, [edit]), workdir, f"h_{name}", False), "detect"))
    return out


def check_mistakes(m: dict) -> None:
    c = m["clean"]
    assert c["listsWrongSeeds"] == 0 and c["posWrongSeeds"] == 0 and c["earlyMaxK"] == 15 and c["lateMaxK"] == 4, c
    assert m["ring"]["listsWrongSeeds"] > 0 and m["ring"]["posWrongSeeds"] == 0
    assert m["pos"]["posWrongSeeds"] == 20 and m["pos"]["listsWrongSeeds"] == 0
    assert m["direction"]["earlyMaxK"] < m["direction"]["lateMaxK"] and m["direction"]["listsWrongSeeds"] == 0


# ------------------------------------------------------------------ timing program of the practice page
def check_timing(sn: dict[str, str], workdir: Path) -> None:
    code = sn[TIMING]
    includes = [ln for ln in code.splitlines() if ln.startswith("#include")]
    body = "\n".join(ln for ln in code.splitlines() if not ln.startswith("#include"))
    sub = workdir / "timing"
    sub.mkdir()
    full = "\n".join(includes) + "\n" + assemble(sn) + "\n" + body + "\n"
    (sub / "t.cpp").write_text(full)
    done = subprocess.run(["c++", "-std=c++17", "-O1", "-Wall", "-Wextra", "-Werror", str(sub / "t.cpp"), "-o", str(sub / "t")], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr[:3000]
    out = subprocess.run([str(sub / "t")], check=True, capture_output=True, text=True, timeout=60).stdout
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) >= 3, f"the timing program must print its three calibration lines: {out}"


# ------------------------------------------------------------------ tables as they appear in the lesson
def fmt(x) -> str:
    return f"{int(x):,}"


def pct(num: int, den: int) -> str:
    return f"{num * 100 / den:.1f}%"


def table_rows(meas: dict) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    b = meas["build"]
    rows["build"] = [
        f"| 2,000 | {b['2000']['side']} ({b['2000']['g']} × {b['2000']['g']}) | {fmt(b['2000']['brute'])} | {fmt(b['2000']['grid'])} |",
        f"| 10,000 | {b['10000']['side']} ({b['10000']['g']} × {b['10000']['g']}) | {fmt(b['10000']['bruteSeed1'])} | {fmt(b['10000']['grid'])} |"]
    rows["sides"] = [f"| {e['side']} | {e['g']} × {e['g']} | {10000 / (e['g'] * e['g']):.1f} | {fmt(e['ops'])} |" for e in meas["sides"]]
    rows["compose"] = []
    names = {("route", 2000): "순서 틀 N = 2,000", ("route", 10000): "순서 틀 N = 10,000", ("assign", 2000): "배정 틀 N = 2,000"}
    for e in meas["compose"]:
        rows["compose"].append(f"| {names[(e['frame'], e['n'])]} | {e['k']} | {fmt(e['ops'])} | {fmt(e['built'])} | {fmt(e['terms'])} | {fmt(e['writes'])} | {e['perProposal'] / 100:.2f} |")
    for frame, n, budget in LIST_CASES:
        key = f"{frame}{n}@{budget}"
        entries = meas["lists"][key]
        rows[f"lists_{key}"] = []
        for e in entries:
            if e["k"] == REF_K:
                v, cmp_ = "기준", "-"
            else:
                v, cmp_ = verdict(e["better"], e["worse"]), f"{e['better']} / {e['worse']}"
            label = "목록 없이" if e["k"] == 0 else str(e["k"])
            rows[f"lists_{key}"].append(f"| {label} | {fmt(e['median'])} | {cmp_} | {v} | {fmt(e['proposals'])} | {fmt(e['built'])} |")
    bl = meas["bruteLists2000"]
    rows["brute2000"] = [f"| 8, 전수로 만든 목록 | {fmt(bl['median'])} | {bl['better']} / {bl['worse']} | {verdict(bl['better'], bl['worse'])} | {fmt(bl['proposals'])} | {fmt(bl['built'])} |"]
    rows["assign_budget"] = [f"| {fmt(e['budget'])} | {fmt(e['none'])} | {fmt(e['list'])} | {e['listBetter']} / {e['listWorse']} | {verdict(e['listBetter'], e['listWorse'])} |" for e in meas["assignBudget"]]
    for frame in ("route", "assign"):
        rows[f"stages_{frame}"] = []
        for i, e in enumerate(meas["stages"][frame]):
            if i == 0:
                v, cmp_ = "기준", "-"
            else:
                v, cmp_ = verdict(e["better"], e["worse"]), f"{e['better']} / {e['worse']}"
            if i == 1:
                v16, cmp16 = "기준", "-"
            else:
                v16, cmp16 = verdict(e["better16"], e["worse16"]), f"{e['better16']} / {e['worse16']}"
            rows[f"stages_{frame}"].append(f"| {e['name']} | {fmt(e['median'])} | {cmp_} | {v} | {cmp16} | {v16} |")
    for key, entries in meas["doubling"].items():
        rows[f"doubling_{key}"] = [f"| {fmt(e['budget'])} | {fmt(e['median'])} | {'-' if e['drop'] is None else fmt(e['drop'])} |" for e in entries]
    for frame in ("route", "assign"):
        rows[f"clock_{frame}"] = [f"| {fmt(e['every'])} | {fmt(e['reads'])} | {e['share'] / 10:.1f}% | {fmt(e['proposals'])} | {fmt(e['cost'])} | {fmt(e['overshoot'])} |" for e in meas["clock"][frame]]
    for frame in ("route", "assign"):
        rows[f"miss_{frame}"] = []
        for st in meas["miss"][frame]:
            for e in st["perK"]:
                if st["state"] == 1 and e["k"] <= 8:
                    continue                       # the 8-candidate local optimum has no improving move inside 8 by construction
                rows[f"miss_{frame}"].append(f"| {'시작' if st['state'] == 0 else '후보 8개의 지역 최적'} | {e['k']} | {e['inside']} / {st['seedsLeft']} | {e['permille'] / 10:.1f}% |")
        rows[f"miss_left_{frame}"] = [f"| {'시작' if st['state'] == 0 else '후보 8개의 지역 최적'} | {fmt(st['improving'])} | {fmt(st['improvingIn8'])} | {st['seedsLeft']} / 20 |" for st in meas["miss"][frame]]
    rows.update(budget_rows(meas))
    rows.update(hand_rows(meas["hand"]))
    return rows


def sgn(d: int) -> str:
    return f"+{d}" if d > 0 else (f"−{-d}" if d < 0 else "0")


def budget_rows(meas: dict) -> dict[str, list[str]]:
    """Operation counts that are formulas (evaluations x operations per evaluation) next to measured preparation costs."""
    out = {}
    n, limit = 10000, ROUTE_N[10000]
    full, lst = n * (n - 1) // 2, 2 * n * 8
    b = meas["build"]["10000"]
    out["budget_route"] = [
        f"| 전체 근방 한 번 훑기 | 평가 {fmt(full)}회 × 5 | {fmt(full * 5)} | {full * 5 * 100 / limit:,.1f}% |",
        f"| 이웃 8개 목록으로 한 번 훑기 | 평가 {fmt(lst)}회 × 5 | {fmt(lst * 5)} | {lst * 5 * 100 / limit:,.1f}% |",
        f"| 이웃 목록 만들기, 전수 | 시드 1 실측 | {fmt(b['bruteSeed1'])} | {b['bruteSeed1'] * 100 / limit:,.1f}% |",
        f"| 이웃 목록 만들기, 칸 | 중앙값 | {fmt(b['grid'])} | {b['grid'] * 100 / limit:,.1f}% |"]
    n, m, k, limit = AN, AM, 4, ASSIGN_BUDGET
    full, lst = n * (m - 1), n * k
    build = n * (2 * m + 51)
    out["budget_assign"] = [
        f"| 전체 근방 한 번 훑기 | 평가 {fmt(full)}회 × 7 | {fmt(full * 7)} | {full * 7 * 100 / limit:,.1f}% |",
        f"| 싼 기계 4대 목록으로 한 번 훑기 | 평가 {fmt(lst)}회 × 7 | {fmt(lst * 7)} | {lst * 7 * 100 / limit:,.1f}% |",
        f"| 후보 기계 목록 만들기 | 작업 {fmt(n)}개 × (2 × {m} + 51) | {fmt(build)} | {build * 100 / limit:,.1f}% |"]
    return out


def hand_rows(h: dict) -> dict[str, list[str]]:
    pts = h["points"]
    px = [p["xy"][0] for p in pts]
    py = [p["xy"][1] for p in pts]
    snake_order = h["snake"]
    pos = {v: i for i, v in enumerate(snake_order)}
    lists = h["lists"]
    rows: dict[str, list[str]] = {}
    rows["hand_points"] = [f"| P{p['id']} | ({p['xy'][0]}, {p['xy'][1]}) | ({p['cell'][0]}, {p['cell'][1]}) | {pos[p['id']]} |" for p in pts]
    rows["hand_lists"] = [f"| P{u} | " + " | ".join(f"P{v} ({dist(px, py, u, v)})" for v in lists[u]) + " |" for u in range(len(pts))]
    rows["hand_trace"] = []
    for r in h["ringTrace"]["rings"]:
        offered = ", ".join(f"P{v} ({fmt(d)})" for v, d in r["offered"]) or "없음"
        kept = ", ".join(f"P{v}" for v, _ in r["list"])
        if len(r["list"]) < h["ringTrace"]["k"]:
            test = f"목록 {len(r['list'])}개로 아직 덜 참"
        else:
            kth = r["list"][-1][1]
            test = f"{kth} ≤ {r['limit']}: {'예, 멈춤' if r['stop'] else '아니오'}"
        rows["hand_trace"].append(f"| {r['ring']} | {r['cells']} | {offered} | {kept} | {test} |")

    def edge_rank(u, v):
        ranks = [lists[a].index(b) for a, b in ((u, v), (v, u)) if b in lists[a]]
        return min(ranks) if ranks else None

    rows["hand_moves"] = []
    for l, r, dl, rank in h["improving"]:
        edges = []
        if l > 0:
            edges.append((snake_order[l - 1], snake_order[r]))
        if r < len(pts) - 1:
            edges.append((snake_order[l], snake_order[r + 1]))
        text = ", ".join(f"P{u}–P{v} ({'목록 밖' if edge_rank(u, v) is None else str(edge_rank(u, v) + 1) + '번째'})" for u, v in edges)
        ok2 = "예" if rank < 2 else "아니오"
        ok3 = "예" if rank < 3 else "아니오"
        rows["hand_moves"].append(f"| [{l}, {r}] | {sgn(dl)} | {text} | {ok2} | {ok3} |")
    a = h["assign"]
    rows["hand_assign_jobs"] = [f"| {i} | {HAND_D[i]} | {', '.join(str(x) for x in HAND_C[i])} | {', '.join(str(x) for x in a['lists'][i])} |" for i in range(6)]
    rows["hand_assign_moves"] = []
    for i, y, dl, rank in sorted(a["moves"], key=lambda m: (m[2], m[0], m[1])):
        rows["hand_assign_moves"].append(f"| 작업 {i} → 기계 {y} | {sgn(dl)} | {'목록 밖' if rank == 255 else str(rank + 1) + '번째'} | {'예' if rank < 2 else '아니오'} | {'예' if rank < 3 else '아니오'} |")
    rows["hand_clock"] = [f"| {e} | {v['proposals']} | {v['reads']} | {v['ops']} | {v['ops'] - 60} |" for e, v in h["clock"].items()]
    rows["hand_sched"] = [f"| {rem} | {v[0]} | {v[1]} |" for rem, v in h["sched"].items()]
    return rows


def hub_expected(meas: dict) -> list[tuple[str, str]]:
    r = {e["k"]: e for e in meas["lists"]["route10000@12000000"]}
    a = {e["k"]: e for e in meas["lists"]["assign2000@2000000"]}
    return [("순서 틀 · N = 10,000 · 시작(칸 뱀 순서)", fmt(meas["start"]["route10000"])),
            ("순서 틀 · 목록 없이 무작위 쌍, 연산 12,000,000", fmt(r[0]["median"])),
            ("순서 틀 · 가까운 8개 목록, 연산 12,000,000", fmt(r[8]["median"])),
            ("배정 틀 · N = 2,000 · 시작(라운드 로빈)", fmt(meas["start"]["assign"])),
            ("배정 틀 · 목록 없이 무작위 기계, 연산 2,000,000", fmt(a[0]["median"])),
            ("배정 틀 · 싼 기계 4대 목록, 연산 2,000,000", fmt(a[4]["median"]))]


def check_text_tables(meas: dict, hand: dict) -> int:
    text = read_lesson_text(LESSON_ID)
    count = 0
    for name, rows in table_rows(meas).items():
        for row in rows:
            assert row in text, f"lesson table row missing or differs ({name}): {row}"
            count += 1
    count += check_hub_summary(LESSON_ID, hub_expected(meas))
    count += check_claims(meas, text)
    return count


def check_claims(meas: dict, text: str) -> int:
    """Sentences of the lesson that quote numbers or verdicts: each must still follow from the measurements."""
    count = 0

    def need(phrase: str) -> None:
        nonlocal count
        assert phrase in text, f"lesson sentence missing or differs: {phrase}"
        count += 1

    L = meas["lists"]
    by_k = {key: {e["k"]: e for e in entries} for key, entries in L.items()}
    cases = [f"route2000@{TIGHT[2000]}", f"route2000@{ROUTE_N[2000]}", f"route10000@{TIGHT[10000]}", f"route10000@{ROUTE_N[10000]}"]
    for key in cases + ["assign2000@2000000"]:
        assert by_k[key][0]["better"] == 0 and by_k[key][0]["worse"] >= WIN, key                 # no list: always worse than the reference
    assert [(by_k[c][2]["better"], by_k[c][2]["worse"]) for c in cases] == [(1, 19), (0, 20), (0, 20), (0, 20)]
    need("(1 / 19, 0 / 20, 0 / 20, 0 / 20)")
    tight2000, tight10000, ample2000, ample10000 = by_k[cases[0]], by_k[cases[2]], by_k[cases[1]], by_k[cases[3]]
    assert (tight2000[4]["better"], tight2000[4]["worse"]) == (20, 0) and (tight10000[4]["better"], tight10000[4]["worse"]) == (15, 5)
    need("`k = 4`가 `k = 8`보다 좋았고(20 / 0, 15 / 5)")
    assert tight2000[16]["worse"] == 20 and tight10000[16]["worse"] == 20
    assert tight2000[32]["median"] == meas["start"]["route2000"] and tight10000[32]["median"] == meas["start"]["route10000"]
    assert tight2000[32]["built"] == 776045 and tight10000[32]["built"] == 4000780
    need("(776,045, 4,000,780)")
    assert [(ample2000[16]["better"], ample2000[16]["worse"]), (ample2000[32]["better"], ample2000[32]["worse"])] == [(17, 3), (16, 4)]
    assert [(ample10000[16]["better"], ample10000[16]["worse"]), (ample10000[32]["better"], ample10000[32]["worse"])] == [(15, 5), (18, 2)]
    need("(17 / 3, 16 / 4와 15 / 5, 18 / 2)")
    assert (ample2000[4]["better"], ample2000[4]["worse"]) == (6, 14) and (ample10000[4]["better"], ample10000[4]["worse"]) == (0, 20)
    need("결정 못 함(6 / 14), `N = 10,000`에서 더 나쁨(0 / 20)")
    a = by_k["assign2000@2000000"]
    assert (a[4]["better"], a[4]["worse"]) == (19, 1) and all(a[k]["worse"] >= WIN for k in (2, 16, 32))
    need("`k = 4`가 `k = 8`보다 19 / 1로 좋았고")
    need(f"{fmt(ample10000[0]['proposals'])}개와 `k = 8`의 {fmt(ample10000[8]['proposals'])}개")
    assert meas["bruteLists2000"]["median"] == meas["start"]["route2000"] and meas["bruteLists2000"]["worse"] >= WIN
    need(f"연산 {fmt(meas['build']['2000']['brute'])}으로 넉넉한 예산 2,000,000의 {meas['build']['2000']['brute'] / 2000000:.1f}배")
    for e in meas["assignBudget"]:
        assert e["listBetter"] == 20
    # preparation shares
    comp = {(e["frame"], e["n"]): e for e in meas["compose"]}
    need(f"목록·초기해가 {pct(comp[('route', 10000)]['built'], comp[('route', 10000)]['ops'])}, 원소 쓰기가 {pct(comp[('route', 10000)]['writes'], comp[('route', 10000)]['ops'])}")
    need(f"후보 목록이 총 연산의 {pct(comp[('assign', 2000)]['built'], comp[('assign', 2000)]['ops'])}")
    assert comp[("route", 10000)]["perProposal"] == 405 and comp[("assign", 2000)]["perProposal"] == 574
    need("4.05연산")
    need("5.74연산")
    # cell sizes
    ops_by_side = {e["side"]: e["ops"] for e in meas["sides"]}
    assert min(ops_by_side, key=ops_by_side.get) == 10 and sorted(ops_by_side, key=ops_by_side.get)[1] == 14
    # misses
    mr, ma = meas["miss"]["route"], meas["miss"]["assign"]
    assert [e["inside"] for e in mr[0]["perK"]] == [11, 15, 19, 20, 20]
    need("20개 중 11개, `k = 8`은 19개, `k = 16`부터 20개 모두")
    assert (mr[0]["improving"], mr[0]["improvingIn8"]) == (1213, 1157)
    need("중앙값 1,213개이고 후보 8개 안에는 1,157개")
    assert mr[1]["seedsLeft"] == 19 and mr[1]["improving"] == 3
    need("20개 시드 중 19개에 전체 근방의 개선 이동이 남아 있었고 중앙값은 3개")
    assert [e["inside"] for e in ma[0]["perK"]] == [1, 1, 2, 7, 9]
    need("`k = 2`와 `k = 4`에서 20개 중 1개씩이고, `k = 32`도 9개뿐")
    assert ma[0]["perK"][1]["permille"] == 863
    need("`k = 4`에서 86.3%")
    assert ma[1]["seedsLeft"] == 5 and ma[1]["perK"][3]["inside"] == 5 and ma[1]["perK"][4]["inside"] == 5
    need("20개 시드 중 5개에만 개선 이동이 남아 있었고")
    # stages
    sr, sa = meas["stages"]["route"], meas["stages"]["assign"]
    assert (sr[1]["better"], sr[1]["worse"]) == (17, 3) and (sr[4]["better"], sr[4]["worse"]) == (17, 0) and (sr[4]["better16"], sr[4]["worse16"]) == (4, 16)
    need("(17 / 3)")
    need("(17 / 0)")
    need("(4 / 16)")
    assert verdict(sr[2]["better16"], sr[2]["worse16"]) == "결정 못 함" and verdict(sr[3]["better16"], sr[3]["worse16"]) == "결정 못 함"
    assert (sr[2]["better16"], sr[2]["worse16"]) == (8, 12) and (sr[3]["better16"], sr[3]["worse16"]) == (8, 12)
    need("`고정 16`과 결정 못 함(8 / 12 두 개)")
    assert (sa[1]["better"], sa[1]["worse"]) == (1, 19) and (sa[2]["better"], sa[2]["worse"]) == (1, 19)
    assert (sa[3]["better"], sa[3]["worse"]) == (14, 6) and (sa[4]["better"], sa[4]["worse"]) == (7, 1)
    need("(1 / 19) `4 → 16`과 마무리를 붙인 계획은 `고정 8`과 결정 못 함(14 / 6, 7 / 1)")
    # doubling
    d10, d2 = meas["doubling"]["route10000"], meas["doubling"]["route2000"]
    assert [e["drop"] for e in d10[1:]] == [16302, 1827, 0, 0] and [e["drop"] for e in d2[1:]] == [7654, 343, 0, 0, 0]
    need("`N = 10,000`은 16,302, 1,827, 0으로, `N = 2,000`은 7,654, 343, 0으로")
    # clock
    cr, ca = meas["clock"]["route"], meas["clock"]["assign"]
    assert (cr[0]["share"], ca[0]["share"]) == (791, 477) and (cr[0]["proposals"], ca[0]["proposals"]) == (39553, 23852)
    need("예산의 79.1%(순서 틀)와 47.7%(배정 틀)를 먹어 제안 수가 39,553과 23,852로")
    assert (cr[3]["share"], ca[3]["share"], cr[4]["share"], ca[4]["share"], cr[5]["share"], ca[5]["share"]) == (115, 53, 32, 14, 8, 3)
    need("시계 비중이 11.5%와 5.3%가 되고 256에서 3.2%와 1.4%, 1,024에서 0.8%와 0.3%")
    assert [e["cost"] for e in cr] == [48090] + [47113] * 6 and [e["cost"] for e in ca] == [522437, 521868] + [521866] * 5
    need("(48,090, 나머지 47,113)")
    need("(522,437, 521,868, 나머지 521,866)")
    assert (cr[6]["overshoot"], ca[6]["overshoot"]) == (16575, 23887)
    need("(순서 틀 4,096에서 16,575, 배정 틀 23,887)")
    assert abs(cr[6]["overshoot"] / 4096 - 4.0) < 0.1 and abs(ca[6]["overshoot"] / 4096 - 5.8) < 0.1
    # mistakes
    m = meas["mistakes"]
    assert m["ring"]["listsWrongSeeds"] == 20 and m["pos"]["posWrongSeeds"] == 20
    assert (m["clean"]["earlyMaxK"], m["clean"]["lateMaxK"], m["direction"]["earlyMaxK"], m["direction"]["lateMaxK"]) == (15, 4, 4, 15)
    need("올바른 코드는 15와 4(초반 5%와 종반 5%), 반대로 쓴 코드는 4와 15")
    need("순서 틀 20개 시드 중 19개에 개선 이동이 남아 있었습니다")
    assert 40 / (0.02 * 4.05) > 493 and 40 / (0.02 * 4.05) < 494
    need("간격은 약 494 이상")
    return count


def diff_keys(a, b, path="") -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += diff_keys(a.get(k), b.get(k), f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff_keys(x, y, f"{path}[{i}]")
        return out
    return [] if a == b else [f"{path}: stored {a!r} != fresh {b!r}"]


# ------------------------------------------------------------------ main
STATIC_FIGURES = ["frame-and-fill.svg", "proposal-order.svg"]  # 손으로 쓴 구조 그림(차트는 generate_charts.py --check가 본다)


def check_static_figures() -> int:
    """손으로 쓴 구조 그림의 규격(폭 720, 글자 16~28, 제목 27, role·title·desc)과 본문 삽입을 확인한다."""
    pages = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "lessons" / LESSON_ID / "pages").glob("*.md"))
    for name in STATIC_FIGURES:
        svg = (ROOT / "lessons" / LESSON_ID / "lesson-assets" / name).read_text(encoding="utf-8")
        assert re.search(r'viewBox="0 0 720 \d+"', svg) and 'role="img"' in svg and "<title" in svg and "<desc" in svg, name
        sizes = [int(v) for v in re.findall(r'font-size="(\d+)"', svg)]
        assert sizes and min(sizes) >= 16 and max(sizes) <= 28 and 27 in sizes, (name, sorted(set(sizes)))
        link = f"https://git.readiz.com/h-contest-lesson/lessons/{LESSON_ID}/lesson-assets/{name}"
        assert re.search(r"!\[[^\]\[]+\]\(\.\./lesson-assets/" + re.escape(name) + r"\)\n\n\[그림 크게 보기\]\(" + re.escape(link) + r"\)", pages), name
    return len(STATIC_FIGURES)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", action="store_true", help="write lesson-assets/measurements.json from a fresh run")
    ap.add_argument("--print-tables", action="store_true")
    args = ap.parse_args()

    check_static_figures()
    sn = snippets()
    code = assemble(sn)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "syntax.cpp").write_text(code)
        done = subprocess.run(["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", str(work / "syntax.cpp")], capture_output=True, text=True)
        assert done.returncode == 0, done.stderr[:2000]
        with ThreadPoolExecutor(max_workers=4) as pool:
            f_san = pool.submit(build, code, work, "h_san", True)
            f_opt = pool.submit(build, code, work, "h_opt", False)
            f_mut = pool.submit(run_mistakes, sn, work)
            f_time = pool.submit(check_timing, sn, work)
            san, opt = f_san.result(), f_opt.result()
            jobs = {"exp": pool.submit(run, opt, "exp"), "lists": pool.submit(run, opt, "lists"), "miss": pool.submit(run, opt, "miss"),
                    "gen": pool.submit(run, san, "gen"), "check": pool.submit(run, san, "check"), "hand": pool.submit(run, san, "hand")}
            res = {k: v.result() for k, v in jobs.items()}
            mistakes = f_mut.result()
            f_time.result()
        n_gen = check_gen(res["gen"])
        hand = check_hand(res["hand"])
        # grid lists == brute-force lists == reference sort, all seeds; Python's independent lists for two seeds
        lists_rows = res["lists"]
        for r in lists_rows:
            if r[0] == "lists":
                assert r[2] == "0" and r[3] == "0", f"grid lists differ from brute force / reference sort: {r}"
            if r[0] == "alists":
                assert r[2] == "0", f"assignment lists differ from the reference sort: {r}"
        for r in lists_rows:
            if r[0] == "lists" and int(r[1]) <= 2:
                px, py = gen_route(int(r[1]), 2000)
                lst = knn_lists(px, py, 8)
                assert int(r[6]) == fnv([v for row in lst for v in row]), "k-nearest lists differ from the independent Python lists"
            if r[0] == "alists" and int(r[1]) <= 2:
                d, c = gen_assign(int(r[1]))
                flat = []
                for i in range(AN):
                    flat += [j for _, j in sorted((c[i][j], j) for j in range(AM))[:8]]
                assert int(r[3]) == fnv(flat), "assignment lists differ from the independent Python lists"
        chk = {r[1]: [int(x) for x in r[2:]] for r in res["check"] if r[0] == "check"}
        assert chk["route"][1:] == [0, 0, 0, 0] and chk["route"][0] > 30000, chk
        assert chk["assign"][1:] == [0, 0, 0] and chk["assign"][0] > 20000, chk
        runs = [r for r in res["check"] if r[0] == "run"]
        assert len(runs) == 6 and all(r[3] == r[4] and r[5] == "1" and r[6] == "1" for r in runs), runs
        over = next(r for r in res["check"] if r[0] == "overshoot")
        assert 0 <= int(over[2]) <= 64 * 12000, "the stop check must not overshoot by more than every * one iteration's worst case"
        check_mistakes(mistakes)
        n_final = verify_finals(res["exp"])
        meas = measure(res["exp"], lists_rows, res["miss"])
    meas.update({"schema": 1, "hand": hand, "mistakes": mistakes,
                 "rule": f"한쪽이 {WIN} / 20 시드 이상 나으면 차이가 있다고 보고, 아니면 결정 못 함",
                 "problems": {"route": "N=2000·10000, 좌표 0..999, 맨해튼 거리 합", "assign": "N=2000, M=200, K=14, 부하 제곱합/100 + 추가 비용"}})
    if args.output:
        DATA.write_text(json.dumps(meas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {DATA.relative_to(ROOT)}")
    if args.print_tables:
        for name, tr in table_rows(meas).items():
            print(f"[{name}]")
            print("\n".join(tr))
        return
    stored = json.loads(DATA.read_text(encoding="utf-8"))
    fresh = json.loads(json.dumps(meas))
    if stored != fresh:
        print("\n".join(diff_keys(stored, fresh)[:40]))
        raise AssertionError("measurements.json differs from a fresh measurement (the keys that differ are listed above; run with --output)")
    n_rows = check_text_tables(stored, hand)
    print(f"candidate-and-time-budget ok: {len(BLOCKS)} code blocks + timing program, {n_gen} generated instances checked against Python, "
          f"{n_final} final solutions recomputed, 3 injected mistakes detected, {n_rows} table rows matched the measurements")


if __name__ == "__main__":
    main()
