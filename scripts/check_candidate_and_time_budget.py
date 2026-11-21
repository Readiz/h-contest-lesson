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
    pos = {v: i for i, v in enumerate(order)}
    revs = {}
    base = route_cost(px, py, order)
    rank = {}
    for a in range(n):
        for q in range(k):
            b = pos[grid_lists[order[a]][q]]
            if b >= a + 2:
                lr = (a + 1, b)
            elif b <= a - 2:
                lr = (b, a - 1)
            else:
                continue
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
    return h


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
            entries.append({"name": name, "median": med(per.values()), "better": better, "worse": worse})
        meas["stages"][frame] = entries
        better, worse = compare(st[(frame, 4)], st[(frame, 1)])
        meas.setdefault("stagePair", {})[frame] = {"better": better, "worse": worse}
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
                ratio = med((x[1 + q] * 1000) // x[0] for x in left)
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
            rows[f"stages_{frame}"].append(f"| {e['name']} | {fmt(e['median'])} | {cmp_} | {v} |")
    rows["stage_pair"] = [f"| {'순서 틀' if f == 'route' else '배정 틀'} | {e['better']} / {e['worse']} | {verdict(e['better'], e['worse'])} |" for f, e in meas["stagePair"].items()]
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
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", action="store_true", help="write lesson-assets/measurements.json from a fresh run")
    ap.add_argument("--print-tables", action="store_true")
    args = ap.parse_args()

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
