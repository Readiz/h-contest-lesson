"""Check the neighborhood-and-delta lesson: code blocks, difference == full recomputation, hand examples,
neighborhood sizes and connectivity, common mistakes, measurements.

What runs (about 40 s):
  * every code block is extracted, rejected if it uses a header / STL / dynamic allocation, assembled with the
    `array` and `random` library blocks and compiled header-free with -Wall -Wextra -Werror -fsyntax-only;
  * a harness (standard headers allowed there) including the lesson code runs under ASan/UBSan: reference
    cost and validity written independently for this check, delta == full recomputation for every move on
    small instances, undo restores arrays and caches, checkDelta on the default sizes, trajectory identity of
    the two loops, neighborhood sizes, breadth-first search over small neighborhoods, the hand examples;
  * the instance generator and the hand examples are recomputed in Python, independently of the lesson code;
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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpp_library import assemble_library, check_submission_code  # noqa: E402
from lesson_text import check_hub_summary, read_lesson_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LESSON_ID = "neighborhood-and-delta"
DATA = ROOT / "lessons" / LESSON_ID / "lesson-assets" / "measurements.json"
HARNESS = ROOT / "scripts" / "neighborhood_and_delta_harness.cpp"
SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
BLOCKS = ("nd-frame", "nd-route", "nd-assign", "nd-gen", "nd-run")
SEEDS = list(range(1, 21))
M64 = (1 << 64) - 1

# ------------------------------------------------------------------ the experiments' definition
ROUTE_BUDGETS = [20000, 100000, 500000, 2000000]
ASSIGN_BUDGETS = [1000, 5000, 20000, 100000]
ROUTE_MASKS = [(4, "구간 뒤집기"), (1, "두 점 교환"), (2, "한 점 옮기기"), (8, "이웃한 두 점 교환"),
               (5, "교환 + 뒤집기"), (6, "옮기기 + 뒤집기"), (7, "교환 + 옮기기 + 뒤집기"), (15, "넷 모두")]
ASSIGN_MASKS = [(3, "옮기기 + 맞바꾸기"), (1, "옮기기만"), (2, "맞바꾸기만")]
WIN = 15   # of 20 seeds: a one-sided sign test at p < 0.05 (two-sided 0.041)


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
    return assemble_library(["array", "random"]) + "\n" + "\n".join(parts)


def build(code: str, workdir: Path, name: str, sanitize: bool) -> Path:
    (workdir / "lesson.cpp").write_text(code)
    exe = workdir / name
    flags = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"] if sanitize else ["-O1"]
    done = subprocess.run(["c++", "-std=c++17", *flags, f"-I{workdir}", str(HARNESS), "-o", str(exe)],
                          capture_output=True, text=True)
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


def gen_route(seed: int, n: int = 200):
    g = Gen(seed)
    px, py = [], []
    for _ in range(n):
        px.append(g.next(1000))
        py.append(g.next(1000))
    return px, py


def route_cost(px, py, order) -> int:
    return sum(abs(px[order[k]] - px[order[k + 1]]) + abs(py[order[k]] - py[order[k + 1]]) for k in range(len(order) - 1))


def gen_assign(seed: int, n=120, m=8):
    g = Gen(seed)
    d, c = [], []
    for _ in range(n):
        d.append(1 + g.next(100))
        c.append([g.next(51) for _ in range(m)])
    return d, c


def assign_cost(d, c, a, m=8) -> int:
    load = [0] * m
    for i, j in enumerate(a):
        load[j] += d[i]
    return sum(x * x for x in load) // 100 + sum(c[i][j] for i, j in enumerate(a))


def check_gen(rows):
    seen = 0
    for kind, which, seed, h, cost, ref in rows:
        seed = int(seed)
        if which == "route":
            px, py = gen_route(seed)
            assert int(h) == fnv(px + py) or int(h) == fnv(py, fnv(px)), "route generator differs from the independent one"
            assert int(cost) == int(ref) == route_cost(px, py, list(range(200)))
        else:
            d, c = gen_assign(seed)
            hh = fnv(d)
            for row in c:
                hh = fnv(row, hh)
            assert int(h) == hh, "assign generator differs from the independent one"
            assert int(cost) == int(ref) == assign_cost(d, c, [i % 8 for i in range(120)])
        seen += 1
    assert seen == 40
    return seen


# hand examples ---------------------------------------------------------------
HAND_PTS = [(1, 1), (8, 2), (2, 4), (7, 5), (3, 8), (9, 7), (5, 9)]
HAND_D = [53, 28, 41, 19, 62, 7]
HAND_C = [[12, 30, 5], [20, 8, 12], [40, 15, 22], [3, 27, 18], [25, 10, 35], [14, 38, 9]]
HAND_ROUTE_MOVES = [(0, 1, 4), (1, 5, 1), (2, 2, 4), (2, 4, 6), (0, 2, 3)]
HAND_ASSIGN_MOVES = [(0, 1, 2), (1, 0, 2), (0, 0, 2)]


def hand_route():
    px = [p[0] for p in HAND_PTS]
    py = [p[1] for p in HAND_PTS]
    order = list(range(7))
    out = {"start": route_cost(px, py, order), "moves": []}
    for kind, a, b in HAND_ROUTE_MOVES:
        q = order[:]
        if kind == 0:
            q[a], q[b] = q[b], q[a]
        elif kind == 1:
            x = q.pop(a)
            q.insert(b, x)
        else:
            q[a:b + 1] = q[a:b + 1][::-1]
        before = {frozenset((order[k], order[k + 1])) for k in range(6)}
        after = {frozenset((q[k], q[k + 1])) for k in range(6)}
        rem = sorted((tuple(sorted(e)) for e in before - after))
        add = sorted((tuple(sorted(e)) for e in after - before))
        dist = lambda e: abs(px[e[0]] - px[e[1]]) + abs(py[e[0]] - py[e[1]])
        out["moves"].append({"move": [kind, a, b], "order": q, "cost": route_cost(px, py, q),
                             "delta": route_cost(px, py, q) - out["start"],
                             "removed": [[list(e), dist(e)] for e in rem], "added": [[list(e), dist(e)] for e in add]})
    return out


def hand_assign():
    a0 = [0, 1, 2, 0, 1, 2]

    def cost(a):
        load = [0, 0, 0]
        for i, j in enumerate(a):
            load[j] += HAND_D[i]
        sq = sum(x * x for x in load)
        cc = sum(HAND_C[i][j] for i, j in enumerate(a))
        return sq // 100 + cc, load, sq, cc

    start = cost(a0)
    out = {"start": list(start), "moves": []}
    for kind, i, y in HAND_ASSIGN_MOVES:
        a = a0[:]
        if kind == 0:
            a[i] = y
        else:
            a[i], a[y] = a[y], a[i]
        new = cost(a)
        out["moves"].append({"move": [kind, i, y], "cost": new[0], "delta": new[0] - start[0], "load": new[1], "sq": new[2], "c": new[3]})
    return out


def check_hand(rows):
    hr, ha = hand_route(), hand_assign()
    got = [r for r in rows if r[:2] == ["hand", "route"]]
    assert int(got[0][3]) == hr["start"], "hand route start"
    for r, m in zip(got[1:], hr["moves"]):
        assert [int(x) for x in r[2:5]] == m["move"] and int(r[5]) == m["delta"] and int(r[6]) == m["cost"], (r, m)
        assert [int(x) for x in r[7:]] == m["order"]
    got = [r for r in rows if r[:2] == ["hand", "assign"]]
    assert int(got[0][3]) == ha["start"][0] and [int(x) for x in got[0][4:7]] == ha["start"][1] and int(got[0][7]) == ha["start"][2]
    for r, m in zip(got[1:], ha["moves"]):
        assert [int(x) for x in r[2:5]] == m["move"] and int(r[5]) == m["delta"] and int(r[6]) == m["cost"], (r, m)
        assert [int(x) for x in r[7:10]] == m["load"] and int(r[10]) == m["sq"]
    # the two wrong formulas the lesson shows
    px = [p[0] for p in HAND_PTS]
    py = [p[1] for p in HAND_PTS]
    order = list(range(7))
    w = lambda u, v: 0 if u < 0 or v < 0 else abs(px[u] - px[v]) + abs(py[u] - py[v])
    at = lambda k: order[k] if 0 <= k < 7 else -1
    a, b = 2, 3
    u, v = order[a], order[b]
    naive = (w(at(a - 1), v) + w(v, at(a + 1)) + w(at(b - 1), u) + w(u, at(b + 1))
             - w(at(a - 1), u) - w(u, at(a + 1)) - w(at(b - 1), v) - w(v, at(b + 1)))
    wrong = {"adjacent_swap_naive": naive}
    # job 1 to machine 2: floor per machine; job 0 to machine 2: truncated dS / 100
    flo = lambda x: x * x // 100
    wrong["per_machine_floor_move1"] = (flo(62) + flo(76) - flo(90) - flo(48)) + (HAND_C[1][2] - HAND_C[1][1])
    wrong["ds_over_100_move0"] = (19 * 19 + 101 * 101 - 72 * 72 - 48 * 48) // 100 + (HAND_C[0][2] - HAND_C[0][0])
    return {"route": hr, "assign": ha, "wrong": wrong}


# ------------------------------------------------------------------ connectivity in Python
def py_connectivity():
    out = {}
    n = 6
    perms = list(itertools.permutations(range(n)))

    def neigh(p, kind):
        res = set()
        for a in range(n):
            for b in range(n):
                if a == b:
                    continue
                q = list(p)
                if kind == "swap" and a < b:
                    q[a], q[b] = q[b], q[a]
                elif kind == "insert":
                    q = list(p); x = q.pop(a); q.insert(b, x)
                elif kind == "reverse" and a < b:
                    q[a:b + 1] = q[a:b + 1][::-1]
                elif kind == "adjacent" and b == a + 1:
                    q[a], q[b] = q[b], q[a]
                else:
                    continue
                res.add(tuple(q))
        return res

    for kind in ("swap", "insert", "reverse", "adjacent"):
        dist = {tuple(range(n)): 0}
        frontier = [tuple(range(n))]
        while frontier:
            nxt = []
            for p in frontier:
                for q in neigh(p, kind):
                    if q not in dist:
                        dist[q] = dist[p] + 1
                        nxt.append(q)
            frontier = nxt
        out[kind] = [len(dist), max(dist.values())]
    for k in (2, 3):
        valid = [a for a in itertools.product(range(3), repeat=6) if all(a.count(j) <= k for j in range(3))]
        out[f"valid_k{k}"] = len(valid)
        start = (0, 1, 2, 0, 1, 2)
        for kinds in (1, 2, 3):
            seen = {start}
            frontier = [start]
            while frontier:
                nxt = []
                for a in frontier:
                    for i in range(6):
                        if kinds & 1:
                            for t in range(3):
                                if t != a[i] and a.count(t) < k:
                                    q = list(a); q[i] = t; q = tuple(q)
                                    if q not in seen:
                                        seen.add(q); nxt.append(q)
                        if kinds & 2:
                            for j in range(i + 1, 6):
                                if a[i] != a[j]:
                                    q = list(a); q[i], q[j] = q[j], q[i]; q = tuple(q)
                                    if q not in seen:
                                        seen.add(q); nxt.append(q)
                frontier = nxt
            out[f"reach_k{k}_kinds{kinds}"] = len(seen)
    return out


def check_connectivity(rows):
    py = py_connectivity()
    got = {}
    for r in rows:
        if r[:2] == ["bfs", "route"]:
            got[r[2]] = [int(r[4]), int(r[5])]
            assert int(r[4]) == py[r[2]][0] and int(r[5]) == py[r[2]][1], (r, py[r[2]])
        elif r[:2] == ["bfs", "assign"]:
            k, kinds = int(r[2]), int(r[3])
            assert int(r[5]) == py[f"reach_k{k}_kinds{kinds}"], (r, py)
            got[f"k{k}_kinds{kinds}"] = [int(r[4]), int(r[5])]
        else:
            raise AssertionError(r)
    sizes = {r[2]: [int(r[3]), int(r[4])] for r in rows if False}
    return {"python": py, "lesson": got}


# ------------------------------------------------------------------ measurements
def med(xs):
    return int(statistics.median_low(xs))


def group(rows, tag):
    return [r[1:] for r in rows if r[0] == tag]


def measure(exe: Path) -> dict:
    rows = run(exe, "exp")
    start = {"route": [], "assign": []}
    for r in rows:
        if r[0] == "start":
            start[r[1]].append(int(r[3]))
    meas: dict = {"seeds": SEEDS, "start": {k: med(v) for k, v in start.items()}}
    # A: full recomputation versus difference
    meas["budget"] = {}
    for frame, budgets in (("route", ROUTE_BUDGETS), ("assign", ASSIGN_BUDGETS)):
        entries = []
        for b in budgets:
            per = {0: {}, 1: {}}
            props = {0: [], 1: []}
            for r in rows:
                if r[0] == "A" and r[1] == frame and int(r[2]) == b:
                    full, seed, cost, pr, ref = int(r[3]), int(r[4]), int(r[5]), int(r[6]), int(r[7])
                    assert cost == ref, f"tracked cost differs from the reference ({frame} {b} {full} {seed})"
                    per[full][seed] = cost
                    props[full].append(pr)
            better = sum(per[0][s] < per[1][s] for s in SEEDS)
            worse = sum(per[0][s] > per[1][s] for s in SEEDS)
            entries.append({"budget": b, "full": med(per[1].values()), "delta": med(per[0].values()),
                            "deltaBetter": better, "deltaWorse": worse,
                            "fullProposals": med(props[1]), "deltaProposals": med(props[0])})
        meas["budget"][frame] = entries
    # B: neighbourhoods
    meas["neighborhood"] = {}
    for frame, masks, ref_mask in (("route", ROUTE_MASKS, 4), ("assign", ASSIGN_MASKS, 3)):
        per: dict = {}
        flags: dict = {}
        for r in rows:
            if r[0] == "B" and r[1] == frame:
                mask, seed, cost = int(r[2]), int(r[3]), int(r[4])
                lo = int(r[5])
                ref = int(r[-1])
                assert cost == ref
                per.setdefault(mask, {})[seed] = cost
                flags.setdefault(mask, []).append((lo, int(r[6]) if frame == "assign" else 0))
        entries = []
        for mask, name in masks:
            better = sum(per[mask][s] < per[ref_mask][s] for s in SEEDS)
            worse = sum(per[mask][s] > per[ref_mask][s] for s in SEEDS)
            entries.append({"mask": mask, "name": name, "median": med(per[mask].values()), "better": better, "worse": worse,
                            "localOptimum": sum(f[0] for f in flags[mask]), "counts15": sum(f[1] for f in flags[mask])})
        meas["neighborhood"][frame] = {"reference": ref_mask, "rows": entries}
    # C: where one proposal's work goes
    split = {}
    for r in rows:
        if r[0] == "C":
            frame, mask, full, seed, props, ops, writes, cost = r[1], int(r[2]), int(r[3]), int(r[4]), int(r[5]), int(r[6]), int(r[7]), int(r[8])
            split.setdefault((frame, mask, full), []).append((props, ops, writes, cost))
    meas["split"] = []
    for (frame, mask, full), v in sorted(split.items()):
        others = split[(frame, mask, 1 - full)]
        assert [x[3] for x in v] == [x[3] for x in others], "the two loops must reach the same cost"
        meas["split"].append({"frame": frame, "mask": mask, "full": full, "proposals": v[0][0],
                              "terms": med([x[1] - x[2] for x in v]), "writes": med([x[2] for x in v]),
                              "total": med([x[0] + x[1] for x in v])})
    return meas


def verify_hub_solutions(exe_rows):
    """The final solutions printed for the hub-table configurations must have the tracked cost."""
    finals = {}
    for r in exe_rows:
        if r[0] == "final":
            finals[(r[1], int(r[2]), int(r[3]))] = [int(x) for x in r[4:]]
    tracked = {}
    for r in exe_rows:
        if r[0] == "A" and ((r[1] == "route" and int(r[2]) == ROUTE_BUDGETS[-1]) or (r[1] == "assign" and int(r[2]) == ASSIGN_BUDGETS[2])):
            tracked[(r[1], int(r[3]), int(r[4]))] = int(r[5])
    count = 0
    for (frame, full, seed), sol in finals.items():
        if frame == "route":
            px, py = gen_route(seed)
            assert sorted(sol) == list(range(200))
            assert route_cost(px, py, sol) == tracked[(frame, full, seed)]
        else:
            d, c = gen_assign(seed)
            assert all(0 <= j < 8 for j in sol) and max(sol.count(j) for j in range(8)) <= 18
            assert assign_cost(d, c, sol) == tracked[(frame, full, seed)]
        count += 1
    assert count == 80
    return count


# ------------------------------------------------------------------ mistakes
MUTATIONS = {
    "adjacent": ("if (mv.kind == 2 || (mv.kind == 0 && b == a + 1))", "if (mv.kind == 2)"),
    "floor": ("return (sq + dS) / 100 - sq / 100 + dc;", "return dS / 100 + dc;"),
    "capacity": ("if (to == as[i] || cnt[to] >= k) return false;", "if (to == as[i]) return false;"),
    "undo-cache": ("if (mv.kind == 0) place(mv.a, mv.old);", "if (mv.kind == 0) as[mv.a] = mv.old;"),
    "modulo": ("return (int)(((unsigned long long)rng.next() * (unsigned)bound) >> 32);", "return (int)rng.below((unsigned)bound);"),
}


def detect(rows) -> dict:
    d1 = next(r for r in rows if r[0] == "D1")
    d2 = [(int(r[2]), int(r[3])) for r in rows if r[0] == "D2"]
    d3 = [(int(r[2]), int(r[3])) for r in rows if r[0] == "D3"]
    d5 = int(next(r for r in rows if r[0] == "D5")[1])
    fails = lambda xs: sorted(x for x in xs if x)
    return {"exhaustiveMoves": int(d1[1]), "exhaustiveMismatch": int(d1[2]),
            "route200Found": len(fails(x[0] for x in d2)), "route200Median": med(fails(x[0] for x in d2)) if fails(x[0] for x in d2) else 0,
            "route8Found": len(fails(x[1] for x in d2)), "route8Median": med(fails(x[1] for x in d2)) if fails(x[1] for x in d2) else 0,
            "assign120Found": len(fails(x[0] for x in d3)), "assign120Median": med(fails(x[0] for x in d3)) if fails(x[0] for x in d3) else 0,
            "tightFound": len(fails(x[1] for x in d3)), "tightMedian": med(fails(x[1] for x in d3)) if fails(x[1] for x in d3) else 0,
            "coverage": d5}


def run_mistakes(sn, workdir: Path) -> dict:
    out = {"clean": detect(run(build(assemble(sn), workdir, "h_clean", True), "detect"))}
    for name, edit in MUTATIONS.items():
        out[name] = detect(run(build(assemble(sn, [edit]), workdir, f"h_{name}", False), "detect"))
    return out


def check_mistakes(m: dict) -> None:
    c = m["clean"]
    assert c["exhaustiveMismatch"] == 0 and c["route200Found"] == c["route8Found"] == c["assign120Found"] == c["tightFound"] == 0
    assert c["coverage"] == 19900
    assert m["adjacent"]["exhaustiveMismatch"] > 0 and m["adjacent"]["route200Found"] == 20 and m["adjacent"]["route8Found"] == 20
    assert m["floor"]["assign120Found"] == 20 and m["floor"]["tightFound"] == 20
    assert m["capacity"]["tightFound"] == 20 and m["capacity"]["tightMedian"] == 1
    assert m["capacity"]["assign120Found"] == 20
    assert m["undo-cache"]["assign120Found"] == 20
    assert m["modulo"]["coverage"] < 19900 and m["modulo"]["exhaustiveMismatch"] == 0


# ------------------------------------------------------------------ tables as they appear in the lesson
def fmt(x) -> str:
    return f"{int(x):,}"


def table_rows(meas: dict) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for frame in ("route", "assign"):
        rows[f"budget_{frame}"] = [
            f"| {fmt(e['budget'])} | {fmt(e['full'])} | {fmt(e['delta'])} | {e['deltaBetter']} / 20 |" for e in meas["budget"][frame]]
        last = meas["budget"][frame][-1]
        rows[f"proposals_{frame}"] = [f"| {fmt(last['budget'])} | {fmt(last['fullProposals'])} | {fmt(last['deltaProposals'])} |"]
        rows[f"neighborhood_{frame}"] = []
        for e in meas["neighborhood"][frame]["rows"]:
            if e["mask"] == meas["neighborhood"][frame]["reference"]:
                verdict = "기준"
                cmp = "-"
            else:
                verdict = "더 좋음" if e["better"] >= WIN else ("더 나쁨" if e["worse"] >= WIN else "결정 못 함")
                cmp = f"{e['better']} / {e['worse']}"
            extra = f"{e['localOptimum']} / 20" if frame == "route" else f"{e['localOptimum']} / 20 | {e['counts15']} / 20"
            rows[f"neighborhood_{frame}"].append(f"| {e['name']} | {fmt(e['median'])} | {cmp} | {verdict} | {extra} |")
    names = {("route", 4): "순서 틀, 구간 뒤집기", ("route", 1): "순서 틀, 두 점 교환", ("assign", 3): "배정 틀, 옮기기 + 맞바꾸기"}
    rows["split"] = []
    for e in meas["split"]:
        label = names[(e["frame"], e["mask"])]
        how = "적용 후 복구(전체 재계산)" if e["full"] else "차분(계산만)"
        rows["split"].append(f"| {label} | {how} | {fmt(e['proposals'])} | {fmt(e['terms'])} | {fmt(e['writes'])} | {fmt(e['total'])} |")
    return rows


def hub_expected(meas: dict) -> list[tuple[str, str]]:
    r, a = meas["budget"]["route"][-1], meas["budget"]["assign"][2]
    return [("순서 틀 · 시작(번호 순서)", fmt(meas["start"]["route"])),
            (f"순서 틀 · 전체 재계산, 연산 {fmt(r['budget'])}", fmt(r["full"])),
            (f"순서 틀 · 차분, 연산 {fmt(r['budget'])}", fmt(r["delta"])),
            ("배정 틀 · 시작(라운드 로빈)", fmt(meas["start"]["assign"])),
            (f"배정 틀 · 전체 재계산, 연산 {fmt(a['budget'])}", fmt(a["full"])),
            (f"배정 틀 · 차분, 연산 {fmt(a['budget'])}", fmt(a["delta"]))]


def check_text_tables(meas: dict) -> int:
    text = read_lesson_text(LESSON_ID)
    count = 0
    for name, rows in table_rows(meas).items():
        for row in rows:
            assert row in text, f"lesson table row missing or differs ({name}): {row}"
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
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "syntax.cpp").write_text(code)
        done = subprocess.run(["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", str(work / "syntax.cpp")],
                              capture_output=True, text=True)
        assert done.returncode == 0, done.stderr[:2000]
        exe = build(code, work, "harness", True)

        rows = run(exe, "gen")
        n_gen = check_gen(rows)
        ex = run(exe, "exhaustive")
        assert ex[0][:2] == ["exhaustive", "route"] and ex[0][3] == "0" and ex[0][4] == "0" and int(ex[0][2]) == 26880, ex
        assert ex[1][:2] == ["exhaustive", "assign"] and ex[1][3] == ex[1][4] == ex[1][5] == "0" and int(ex[1][2]) > 5000, ex
        assert all(r[-1] == "0" for r in run(exe, "random")), "checkDelta must pass on the default sizes"
        ident = run(exe, "identity")
        assert len(ident) == 20 and all(r[4] == "1" and r[5] == r[6] == r[7] for r in ident), "the two loops must follow the same trajectory"
        hand = check_hand(run(exe, "hand"))
        conn = check_connectivity(run(exe, "bfs"))
        sizes = {}
        for r in run(exe, "sizes"):
            sizes["_".join(r[1:3]) if r[1] == "route" else "assign"] = [int(x) for x in (r[3:] if r[1] == "route" else r[2:])]
        assert sizes == {"route_swap": [19900, 19900], "route_insert": [39800, 39601], "route_reverse": [19900, 19900], "assign": [840, 6300]}, sizes

        exp_rows = run(exe, "exp")
        n_final = verify_hub_solutions(exp_rows)
        meas = measure(exe)
        mistakes = run_mistakes(sn, work)
        check_mistakes(mistakes)

    meas.update({"schema": 1, "hand": hand, "connectivity": conn, "sizes": sizes, "mistakes": mistakes,
                 "rule": f"한쪽이 {WIN} / 20 시드 이상 나으면 차이가 있다고 보고, 아니면 결정 못 함",
                 "problems": {"route": "N=200, 좌표 0..999, 맨해튼 거리 합", "assign": "N=120, M=8, K=18, 부하 제곱합/100 + 추가 비용"}})
    if args.output:
        DATA.write_text(json.dumps(meas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {DATA.relative_to(ROOT)}")
    if args.print_tables:
        for name, tr in table_rows(meas).items():
            print(f"[{name}]")
            print("\n".join(tr))
        return
    stored = json.loads(DATA.read_text(encoding="utf-8"))
    assert stored == json.loads(json.dumps(meas)), "measurements.json differs from a fresh measurement (run with --output)"
    n_rows = check_text_tables(stored)
    print(f"neighborhood-and-delta ok: {len(BLOCKS)} code blocks, {n_gen} generated instances checked against Python, "
          f"{ex[0][2]} + {ex[1][2]} exhaustive moves, {n_final} final solutions recomputed, "
          f"5 injected mistakes detected, {n_rows} table rows matched the measurements")


if __name__ == "__main__":
    main()
