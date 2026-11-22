"""Check the destroy-and-repair lesson: code blocks, the loop's invariants, hand examples, measurements, mistakes, figures.

What runs (well under a minute):
  * every code block is extracted, rejected if it uses a header / STL / dynamic allocation, assembled with the
    `array` and `random` library blocks and compiled header-free with -Wall -Wextra -Werror -fsyntax-only;
  * a harness (standard headers allowed there) including the lesson code runs under ASan/UBSan: reference cost and
    validity written independently for this check, `checkDR` on every destroy kind x repair rule x accept rule x
    restore method (also a completely full input), destroy/rollback exactness, copy and log restore following the
    same trajectory, the small-move baseline, the integer exp, the two hand examples;
  * the instance generator, the hand examples (small-move neighbourhoods by enumeration, brute-force optimum,
    insertion and regret traces), the integer exp and the small-move local optima printed by the experiments are
    recomputed in Python, independently of the lesson code;
  * the common mistakes are injected into the lesson code and must be detected;
  * the experiments are re-run (-O2 build, integer arithmetic only, so the numbers do not depend on the platform),
    summarised here, compared with lesson-assets/measurements.json and with the tables in the lesson text.
--output writes measurements.json from a fresh run; --print-tables prints the markdown table rows.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import statistics
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpp_library import assemble_library, check_submission_code  # noqa: E402
from lesson_text import check_hub_summary, read_hub_text, read_lesson_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LESSON_ID = "destroy-and-repair"
LESSON_DIR = ROOT / "lessons" / LESSON_ID
DATA = LESSON_DIR / "lesson-assets" / "measurements.json"
HARNESS = ROOT / "scripts" / "destroy_and_repair_harness.cpp"
SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
BLOCKS = ("dr-frame", "dr-route", "dr-assign", "dr-run")
FIGURES = ("stuck-and-rebuild.svg", "destroy-repair-loop.svg", "destroy-kinds.svg", "size-spectrum.svg", "iteration-flow.svg")
SITE_PROBLEMS = ("ORDERING", "SCHEDULX", "MINEEXPLORE", "AIRCONTECH", "TAXIASSIGN", "MULTIDRONE", "COUPANG", "LANDINGX",
                 "ALLOCATE", "CLUSTERX", "CHIPDESIGN", "TENSORALLOC", "ROBOTCLEAN", "DRONESORT", "FRIEGHTFIX",
                 "ANTENNAS", "TELEVISION", "GERMMATCH", "ENTROPY2D", "CITYSUM2D", "FUNCSUM1", "SORTTEST")
SEEDS = list(range(1, 21))
WIN = 15   # of 20 seeds: a one-sided sign test at p < 0.05 (two-sided 0.041)
M64 = (1 << 64) - 1

# ------------------------------------------------------------------ the experiments' definition
ROUTE_BUDGETS = [1000000, 2000000, 4000000]
ASSIGN_BUDGETS = [400000, 1000000, 2000000]
ROUTE_KINDS = [(0, 8, "무작위"), (1, 8, "연속 구간"), (2, 8, "가까운 점"), (3, 8, "비용 기여")]
ASSIGN_KINDS = [(0, 8, "무작위 작업 8개"), (1, 1, "기계 1대의 작업 전부"), (1, 2, "기계 2대의 작업 전부"), (2, 8, "비용 기여 작업 8개")]
ROUTE_REPAIRS = [(2, 8, 0), (2, 8, 1), (1, 8, 0), (1, 8, 1)]
ASSIGN_REPAIRS = [(0, 8, 0), (0, 8, 1), (1, 2, 0), (1, 2, 1)]
ROUTE_DESTROY_NAME = {0: "무작위", 1: "연속 구간", 2: "가까운 점", 3: "비용 기여"}
ASSIGN_DESTROY_NAME = {(0, 8): "무작위 작업 8개", (1, 2): "기계 2대", (1, 1): "기계 1대", (2, 8): "비용 기여 작업 8개"}
REPAIR_NAME = {0: "가장 싼 자리", 1: "후회 기준"}
ROUTE_ACCEPTS = [(1, 0), (2, 30), (2, 300), (2, 1000)]
ASSIGN_ACCEPTS = [(1, 0), (2, 1), (2, 10), (2, 100)]
ROUTE_SIZES = [1, 2, 3, 5, 8, 13, 21, 40, 80, 200]
ASSIGN_SIZES = [1, 2, 4, 8, 16, 32, 64, 120]
STUCK_ROUTE_SIZES = [1, 2, 3, 5, 8, 13, 21]
STUCK_ASSIGN = [(0, 1), (0, 2), (0, 4), (0, 8), (0, 15), (1, 1), (1, 2)]
STUCK_ASSIGN_NAME = {(0, 1): "무작위 작업 1개", (0, 2): "무작위 작업 2개", (0, 4): "무작위 작업 4개", (0, 8): "무작위 작업 8개",
                     (0, 15): "무작위 작업 15개", (1, 1): "기계 1대의 작업 전부", (1, 2): "기계 2대의 작업 전부"}


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


def build(code: str, workdir: Path, name: str, sanitize: bool, opt: str = "-O1") -> Path:
    folder = workdir / name
    folder.mkdir(exist_ok=True)
    (folder / "lesson.cpp").write_text(code)
    exe = folder / "harness"
    flags = [opt, "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"] if sanitize else [opt]
    done = subprocess.run(["c++", "-std=c++17", *flags, f"-I{folder}", str(HARNESS), "-o", str(exe)], capture_output=True, text=True)
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


def check_gen(rows) -> int:
    seen = 0
    for _, which, seed, h, cost, ref in rows:
        seed = int(seed)
        if which == "route":
            px, py = gen_route(seed)
            assert int(h) == fnv(py, fnv(px)), "route generator differs from the independent one"
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


def route_no_improving(px, py, p) -> bool:
    """No improving move among all one-point moves and segment reversals (deltas by the boundary edges)."""
    n = len(p)

    def w(u, v):
        return 0 if u < 0 or v < 0 else abs(px[u] - px[v]) + abs(py[u] - py[v])

    def at(k):
        return p[k] if 0 <= k < n else -1

    for a in range(n):
        for b in range(a + 1, n):
            if w(at(a - 1), p[b]) + w(p[a], at(b + 1)) - w(at(a - 1), p[a]) - w(p[b], at(b + 1)) < 0:
                return False
    for a in range(n):
        x = p[a]
        base_rem = w(at(a - 1), x) + w(x, at(a + 1))
        base_add = w(at(a - 1), at(a + 1))
        for b in range(n):
            if a == b:
                continue
            if a < b:
                d = base_add + w(p[b], x) + w(x, at(b + 1)) - base_rem - w(p[b], at(b + 1))
            else:
                d = base_add + w(at(b - 1), x) + w(x, p[b]) - base_rem - w(at(b - 1), p[b])
            if d < 0:
                return False
    return True


def assign_no_improving(d, c, a, k, m=8) -> bool:
    load = [0] * m
    cnt = [0] * m
    for i, j in enumerate(a):
        load[j] += d[i]
        cnt[j] += 1
    cost = assign_cost(d, c, a, m)
    for i in range(len(a)):
        for y in range(m):
            if y != a[i] and cnt[y] < k:
                b = a[:]
                b[i] = y
                if assign_cost(d, c, b, m) < cost:
                    return False
        for j in range(i + 1, len(a)):
            if a[i] != a[j]:
                b = a[:]
                b[i], b[j] = b[j], b[i]
                if assign_cost(d, c, b, m) < cost:
                    return False
    return True


# ------------------------------------------------------------------ hand examples (independent of the lesson code)
HAND_PTS = [(4, 9), (0, 7), (1, 0), (5, 0), (2, 1), (2, 4), (8, 4)]
HAND_D = [28, 24, 12, 18, 31, 60]
HAND_C = [[26, 29, 23], [21, 27, 27], [3, 15, 18], [4, 20, 16], [1, 25, 13], [25, 4, 1]]
HAND_AS = [1, 1, 2, 0, 0, 2]
BIGV = 10 ** 12


def hand_route() -> dict:
    px = [p[0] for p in HAND_PTS]
    py = [p[1] for p in HAND_PTS]
    n = 7
    order = list(range(n))
    cost = lambda o: route_cost(px, py, o)  # noqa: E731
    start = cost(order)
    fam = {"swap": [], "insert": [], "reverse": []}
    for a in range(n):
        for b in range(a + 1, n):
            q = order[:]
            q[a], q[b] = q[b], q[a]
            fam["swap"].append((cost(q) - start, a, b))
            q = order[:]
            q[a:b + 1] = q[a:b + 1][::-1]
            fam["reverse"].append((cost(q) - start, a, b))
    for a in range(n):
        for b in range(n):
            if a != b:
                q = order[:]
                x = q.pop(a)
                q.insert(b, x)
                fam["insert"].append((cost(q) - start, a, b))
    summary = {}
    for k, v in fam.items():
        real = [t for t in v if not (k == "reverse" and t[1] == 0 and t[2] == n - 1)]   # the whole path read backwards is not a move
        summary[k] = {"moves": len(v), "improving": sum(1 for t in v if t[0] < 0), "best": min(t[0] for t in real)}
    # destroy positions 4, 5 and rebuild by the cheapest slot, in the removal order
    removed = [order[4], order[5]]
    path = [x for x in order if x not in removed]
    steps = [{"path": path[:], "cost": cost(path), "slots": None, "slot": None}]
    for x in removed:
        slots = []
        for s in range(len(path) + 1):
            slots.append(cost(path[:s] + [x] + path[s:]) - cost(path))
        best = slots.index(min(slots))
        path = path[:best] + [x] + path[best:]
        steps.append({"path": path[:], "cost": cost(path), "slots": slots, "slot": best})
    optimum = min(cost(list(p)) for p in itertools.permutations(range(n)))
    alone = []
    for x in (4, 5):                                  # moving only one of the two points to the same place
        q = [v for v in order if v != x]
        q.insert(2, x)
        alone.append({"point": x, "path": q, "cost": cost(q)})
    return {"start": start, "families": summary, "steps": steps, "optimum": optimum, "alone": alone}


def hand_assign() -> dict:
    d, c, a0, m, k = HAND_D, HAND_C, HAND_AS, 3, 2
    cost = lambda a: assign_cost(d, c, a, m)  # noqa: E731
    load = [sum(d[i] for i in range(6) if a0[i] == j) for j in range(m)]
    start = {"cost": cost(a0), "load": load, "sq": sum(x * x for x in load), "c": sum(c[i][a0[i]] for i in range(6))}
    swaps = []
    for i in range(6):
        for j in range(i + 1, 6):
            if a0[i] != a0[j]:
                b = a0[:]
                b[i], b[j] = b[j], b[i]
                swaps.append(cost(b) - start["cost"])
    moves = sum(1 for i in range(6) for y in range(m) if y != a0[i] and sum(1 for t in a0 if t == y) < k)
    pool = [i for i in range(6) if a0[i] in (1, 2)]
    first = a0[:]                                     # the two swaps (0 <-> 2, then 1 <-> 5) that make the same change
    first[0], first[2] = first[2], first[0]
    both = first[:]
    both[1], both[5] = both[5], both[1]
    double = {"first": cost(first), "both": cost(both), "asBoth": both}

    def repair(rule: int):
        a = [-1 if i in pool else a0[i] for i in range(6)]
        ld = [sum(d[i] for i in range(6) if a[i] == j) for j in range(m)]
        cn = [sum(1 for i in range(6) if a[i] == j) for j in range(m)]
        todo = pool[:]
        rounds = []
        while todo:
            info = {}
            for j in todo:
                keys = sorted((((2 * ld[mm] + d[j]) * d[j] + 100 * c[j][mm]), mm) for mm in range(m) if cn[mm] < k)
                best, second = keys[0][0], (keys[1][0] if len(keys) > 1 else BIGV)
                info[j] = (best, second, keys[0][1])
            if rule == 0:
                pick = todo[0]
            else:
                pick = max(todo, key=lambda j: (info[j][1] - info[j][0], -info[j][0], -j))
            rounds.append({"regret": {j: info[j][1] - info[j][0] for j in todo}, "pick": pick, "machine": info[pick][2],
                           "best": info[pick][0], "second": info[pick][1]})
            a[pick] = info[pick][2]
            ld[info[pick][2]] += d[pick]
            cn[info[pick][2]] += 1
            todo.remove(pick)
        ldf = [sum(d[i] for i in range(6) if a[i] == j) for j in range(m)]
        return {"as": a, "cost": cost(a), "rounds": rounds, "load": ldf, "sq": sum(x * x for x in ldf), "c": sum(c[i][a[i]] for i in range(6))}

    assert first == repair(0)["as"], "the cheapest-slot repair must give the state after the first swap"
    return {"start": start, "swaps": {"count": len(swaps), "improving": sum(1 for s in swaps if s < 0), "best": min(swaps)},
            "moves": moves, "pool": pool, "cheapest": repair(0), "regret": repair(1), "double": double}


def check_hand(rows) -> dict:
    hr, ha = hand_route(), hand_assign()
    got = {" ".join(r[1:3]): r[3:] for r in rows if r[0] == "hand"}
    assert int(got["route start"][0]) == hr["start"]
    lines = [r for r in rows if r[0] == "hand" and r[1] == "route"]
    slots = [[int(x) for x in r[3:]] for r in lines if r[2] == "slots4"][0]
    assert slots == hr["steps"][1]["slots"], (slots, hr["steps"][1]["slots"])
    slots5 = [[int(x) for x in r[3:]] for r in lines if r[2] == "slots5"][0]
    assert slots5 == hr["steps"][2]["slots"]
    for r in lines:
        if r[2] == "partial":
            assert [int(x) for x in r[6:]] == hr["steps"][0]["path"] and int(r[4]) == hr["steps"][0]["cost"] == int(r[5])
        if r[2] == "repaired":
            assert [int(x) for x in r[6:]] == hr["steps"][2]["path"] and int(r[4]) == hr["steps"][2]["cost"] == int(r[5])
    assigns = [r for r in rows if r[0] == "hand" and r[1] == "assign"]
    starts = [r for r in assigns if r[2] == "start"]
    for r in starts:
        assert int(r[3]) == ha["start"]["cost"] and [int(x) for x in r[4:7]] == ha["start"]["load"]
        assert int(r[7]) == ha["start"]["sq"] and int(r[8]) == ha["start"]["c"]
    for r in assigns:
        if r[2] == "repaired":
            rule = int(r[4])
            want = ha["regret" if rule else "cheapest"]
            assert int(r[5]) == int(r[6]) == want["cost"] and [int(x) for x in r[7:13]] == want["as"], (r, want)
        if r[2] == "rolled":
            assert int(r[3]) == ha["start"]["cost"] and r[4] == "1"
        if r[2] == "seed":
            assert [int(x) for x in r[9:]] == ha["pool"], r
    return {"route": hr, "assign": ha}


# ------------------------------------------------------------------ measurements
def med(xs):
    return int(statistics.median_low(xs))


def wins(a: dict, b: dict) -> tuple[int, int]:
    return sum(a[s] < b[s] for s in SEEDS), sum(a[s] > b[s] for s in SEEDS)


def verdict(better: int, worse: int) -> str:
    return "더 좋음" if better >= WIN else ("더 나쁨" if worse >= WIN else "결정 못 함")


def collect(rows, tag, frame, key_len):
    """{key: {seed: [values...]}} for rows `tag frame key... seed values...`."""
    out: dict = {}
    for r in rows:
        if r[0] == tag and r[1] == frame:
            key = tuple(r[2:2 + key_len])
            out.setdefault(key, {})[int(r[2 + key_len])] = [int(x) for x in r[3 + key_len:]]
    return out


def series(group: dict, idx: int = 0) -> dict:
    return {s: v[idx] for s, v in group.items()}


def summarise_exp(rows) -> dict:
    meas: dict = {"seeds": SEEDS}
    start = {"route": [], "assign": []}
    for r in rows:
        if r[0] == "start":
            start[r[1]].append(int(r[3]))
    meas["start"] = {k: med(v) for k, v in start.items()}
    # A: same budget, small moves only / destroy and repair only / small moves first
    meas["budget"] = {}
    for frame, budgets in (("route", ROUTE_BUDGETS), ("assign", ASSIGN_BUDGETS)):
        a = collect(rows, "A", frame, 2)
        entries = []
        for b in budgets:
            per = {method: a[(str(b), str(method))] for method in range(3)}
            for method in range(3):
                for s in SEEDS:
                    assert per[method][s][0] == per[method][s][3], f"tracked best differs from the recomputed one ({frame} {b} {method} {s})"
            small = series(per[0])
            better, worse = wins(series(per[2]), small)
            entries.append({"budget": b, "small": med(small.values()), "dr": med(series(per[1]).values()), "hybrid": med(series(per[2]).values()),
                            "hybridBetter": better, "hybridWorse": worse,
                            "drOnlyBetter": wins(series(per[1]), small)[0], "drOnlyWorse": wins(series(per[1]), small)[1],
                            "drIters": med(series(per[1], 1).values()), "hybridIters": med(series(per[2], 1).values())})
        meas["budget"][frame] = entries
    # K: destroy kinds; R: repair rules; C: accept rules; S: sizes
    meas["kinds"], meas["repair"], meas["accept"], meas["size"] = {}, {}, {}, {}
    for frame, kinds in (("route", ROUTE_KINDS), ("assign", ASSIGN_KINDS)):
        k = collect(rows, "K", frame, 2)
        base = series(k[(str(kinds[0][0]), str(kinds[0][1]))])
        entries = []
        for kind, size, name in kinds:
            g = k[(str(kind), str(size))]
            for s in SEEDS:
                assert g[s][0] == g[s][3]
            better, worse = wins(series(g), base)
            entries.append({"kind": kind, "size": size, "name": name, "median": med(series(g).values()), "better": better, "worse": worse,
                            "iters": med(series(g, 1).values()), "accepted": med(series(g, 2).values())})
        meas["kinds"][frame] = {"reference": [kinds[0][0], kinds[0][1]], "rows": entries}
    for frame, combos in (("route", ROUTE_REPAIRS), ("assign", ASSIGN_REPAIRS)):
        r = collect(rows, "R", frame, 3)
        entries = []
        for kind, size, rule in combos:
            g = r[(str(kind), str(size), str(rule))]
            ref = series(r[(str(kind), str(size), "0")])
            better, worse = wins(series(g), ref)
            entries.append({"kind": kind, "size": size, "rule": rule, "median": med(series(g).values()),
                            "iters": med(series(g, 1).values()), "better": better, "worse": worse})
        meas["repair"][frame] = entries
    for frame, accepts_, kindkey in (("route", ROUTE_ACCEPTS, (2, 8)), ("assign", ASSIGN_ACCEPTS, (0, 8))):
        c = collect(rows, "C", frame, 2)
        k = collect(rows, "K", frame, 2)
        base_group = k[(str(kindkey[0]), str(kindkey[1]))]
        base = series(base_group)
        entries = [{"accept": 0, "t0": 0, "median": med(base.values()), "better": 0, "worse": 0, "accepted": med(series(base_group, 2).values())}]
        for accept, t0 in accepts_:
            g = c[(str(accept), str(t0))]
            better, worse = wins(series(g), base)
            entries.append({"accept": accept, "t0": t0, "median": med(series(g).values()), "better": better, "worse": worse,
                            "accepted": med(series(g, 2).values())})
        meas["accept"][frame] = entries
    for frame, sizes in (("route", ROUTE_SIZES), ("assign", ASSIGN_SIZES)):
        s_ = collect(rows, "S", frame, 1)
        a = collect(rows, "A", frame, 2)
        last = (ROUTE_BUDGETS if frame == "route" else ASSIGN_BUDGETS)[-1]
        small = series(a[(str(last), "0")])
        entries = []
        for size in sizes:
            g = s_[(str(size),)]
            better, worse = wins(series(g), small)
            entries.append({"size": size, "median": med(series(g).values()), "iters": med(series(g, 1).values()),
                            "accepted": med(series(g, 2).values()), "better": better, "worse": worse})
        meas["size"][frame] = {"small": med(small.values()), "rows": entries}
    # H: seeds that were not used to choose the settings
    meas["holdout"] = {}
    for frame in ("route", "assign"):
        h = collect(rows, "H", frame, 1)
        small, hyb = {s - 20: v for s, v in series(h[("0",)]).items()}, {s - 20: v for s, v in series(h[("1",)]).items()}
        for s in range(21, 41):
            assert h[("0",)][s][0] == h[("0",)][s][3] and h[("1",)][s][0] == h[("1",)][s][3]
        better, worse = wins(hyb, small)
        meas["holdout"][frame] = {"small": med(small.values()), "hybrid": med(hyb.values()), "better": better, "worse": worse}
    # L: restore methods; O: where one iteration's work goes
    l = {}
    for r in rows:
        if r[0] == "L":
            kind, size, rule, lg, seed = (int(x) for x in r[2:7])
            cost, iters, writes, ops = (int(x) for x in r[7:11])
            l.setdefault((kind, size, rule, lg), []).append((cost, iters, writes, ops))
    meas["restore"] = [{"kind": k[0], "size": k[1], "rule": k[2], "log": k[3], "iters": med([x[1] for x in v]),
                        "writes": med([x[2] // x[1] for x in v]), "ops": med([x[3] // x[1] for x in v]), "cost": med([x[0] for x in v])}
                       for k, v in sorted(l.items())]
    o = {"route": [], "assign": []}
    for r in rows:
        if r[0] == "O":
            cost, iters, writes, ops = (int(x) for x in r[3:7])
            o[r[1]].append((iters, writes, ops))
    meas["opsplit"] = {frame: {"ops": med([x[2] // x[0] for x in v]), "writes": med([x[1] // x[0] for x in v]),
                                "terms": med([(x[2] - x[1] - x[0]) // x[0] for x in v])} for frame, v in o.items()}
    return meas


def summarise_stuck(rows) -> dict:
    out: dict = {"localOptimum": {}}
    lo = {"route": [], "assign": []}
    for r in rows:
        if r[0] == "lo":
            lo[r[1]].append(int(r[3]))
    out["localOptimum"] = {k: med(v) for k, v in lo.items()}
    route = {}
    for r in rows:
        if r[0] == "U" and r[1] == "route":
            route.setdefault((int(r[2]), int(r[3])), []).append(int(r[5]))
    out["route"] = [{"kind": k, "size": s, "median": med(v), "seeds": sum(1 for x in v if x > 0)} for (k, s), v in sorted(route.items())]
    asg = {}
    for r in rows:
        if r[0] == "U" and r[1] == "assign":
            asg.setdefault((int(r[2]), int(r[3]), int(r[4])), []).append(int(r[6]))
    out["assign"] = [{"kind": k, "size": s, "rule": rule, "median": med(v), "seeds": sum(1 for x in v if x > 0)} for (k, s, rule), v in sorted(asg.items())]
    for e in out["route"]:
        if e["size"] == 1:
            assert e["median"] == 0 and e["seeds"] == 0, "destroying one point and reinserting it cheaply must stay inside the move neighbourhood"
    for e in out["assign"]:
        if e["kind"] == 0 and e["size"] == 1:
            assert e["median"] == 0 and e["seeds"] == 0
    return out


def verify_local_optima(rows) -> int:
    count = 0
    for r in rows:
        if r[0] == "lo" and r[1] == "route":
            seed = int(r[2])
            sol = [int(x) for x in r[4:]]
            px, py = gen_route(seed)
            assert sorted(sol) == list(range(200)) and route_cost(px, py, sol) == int(r[3]), "local optimum (route) is not a valid path of the stated cost"
            assert route_no_improving(px, py, sol), f"route local optimum of seed {seed} still has an improving move"
            count += 1
        if r[0] == "lo" and r[1] == "assign":
            seed = int(r[2])
            sol = [int(x) for x in r[4:]]
            d, c = gen_assign(seed)
            assert all(0 <= j < 8 for j in sol) and max(sol.count(j) for j in range(8)) <= 18
            assert assign_cost(d, c, sol) == int(r[3])
            assert assign_no_improving(d, c, sol, 18), f"assign local optimum of seed {seed} still has an improving move"
            count += 1
    assert count == 40
    return count


def verify_final_solutions(rows) -> int:
    finals = {}
    for r in rows:
        if r[0] == "final":
            finals[(r[1], int(r[2]), int(r[3]))] = [int(x) for x in r[4:]]
    tracked = {}
    for r in rows:
        if r[0] == "A" and ((r[1] == "route" and int(r[2]) == ROUTE_BUDGETS[-1]) or (r[1] == "assign" and int(r[2]) == ASSIGN_BUDGETS[-1])):
            tracked[(r[1], int(r[3]), int(r[4]))] = int(r[5])
    count = 0
    for (frame, method, seed), sol in finals.items():
        if frame == "route":
            px, py = gen_route(seed)
            assert sorted(sol) == list(range(200)) and route_cost(px, py, sol) == tracked[(frame, method, seed)]
        else:
            d, c = gen_assign(seed)
            assert all(0 <= j < 8 for j in sol) and max(sol.count(j) for j in range(8)) <= 18
            assert assign_cost(d, c, sol) == tracked[(frame, method, seed)]
        count += 1
    assert count == 120, count
    return count


def check_expo(rows) -> list[dict]:
    out = []
    values = []
    for r in rows:
        assert r[0] == "expo"
        num, den, v = int(r[1]), int(r[2]), int(r[3])
        if den == 64:
            x = num / den
            values.append(v)
            assert abs(v / 65536 - math.exp(-x)) <= 0.0015, (x, v)
            out.append({"x": x, "approx": v, "exact": math.exp(-x)})
        elif num == 5 and den == 0:
            assert v == 0
        elif num == 1000:
            assert v == 0
        else:
            assert v == 0
    assert values == sorted(values, reverse=True) and values[0] == 65536 and values[-1] == 0
    return out


# ------------------------------------------------------------------ mistakes
MUTATIONS = {
    "copy-cache": ("sq = sSq; csum = sCsum;", ""),
    "no-log": ("logJob[nlog] = i; logOld[nlog] = as[i]; ++nlog;", ""),
    "capacity": ("if (cnt[j] >= k) continue;", ""),
    "best": ("if (cur < best) { best = cur; p.saveBest(); }", "{ best = cur; p.saveBest(); }"),
    "greedy-top": ("for (int t = 0; t < 4; ++t) {\n                    const int i = pick(rng, n);", "for (int t = 0; t < n; ++t) {\n                    const int i = t;"),
}


def detect(rows) -> dict:
    d1 = [[int(x) for x in r[2:]] for r in rows if r[0] == "D1"]
    d2 = [[int(x) for x in r[2:]] for r in rows if r[0] == "D2"]
    d3 = next(int(r[1]) for r in rows if r[0] == "D3")

    def found(col):
        v = sorted(x[col] for x in d1 if x[col])
        return len(v), (med(v) if v else 0)

    out = {}
    for col, name in enumerate(("route", "assignCopy", "assignLog", "tight")):
        out[name + "Found"], out[name + "Median"] = found(col)
    out["bestMismatchRoute"] = sum(1 for x in d2 if x[0] != x[1] or x[0] != x[2])
    out["bestMismatchAssign"] = sum(1 for x in d2 if x[3] != x[4] or x[3] != x[5])
    out["distinctSets"] = d3
    return out


def run_mistakes(sn, workdir: Path, clean_exe: Path) -> dict:
    out = {"clean": detect(run(clean_exe, "detect"))}
    exes = {}
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {name: pool.submit(build, assemble(sn, [edit]), workdir, f"m_{name}", False) for name, edit in MUTATIONS.items()}
        for name, fut in futures.items():
            exes[name] = fut.result()
    for name in MUTATIONS:
        out[name] = detect(run(exes[name], "detect"))
    # the effect of picking the largest contributions deterministically, on the same settings and seeds as the kinds table
    tours = {}
    for label, exe in (("clean", clean_exe), ("greedy-top", exes["greedy-top"])):
        t = {0: {}, 3: {}}
        for r in run(exe, "tour"):
            assert r[0] == "T" and r[3] == r[4]
            t[int(r[1])][int(r[2])] = int(r[3])
        tours[label] = t
    assert tours["clean"][0] == tours["greedy-top"][0], "the random kind must not change under the mutation"
    better, worse = wins(tours["greedy-top"][3], tours["clean"][0])
    out["greedy-top"].update({"tourCost": med(tours["greedy-top"][3].values()), "tourRandomCost": med(tours["clean"][0].values()),
                              "tourBetter": better, "tourWorse": worse, "tourCleanCost": med(tours["clean"][3].values())})
    return out


def check_mistakes(m: dict) -> None:
    c = m["clean"]
    assert all(c[k] == 0 for k in ("routeFound", "assignCopyFound", "assignLogFound", "tightFound", "bestMismatchRoute", "bestMismatchAssign")), c
    assert c["distinctSets"] == 200
    assert m["copy-cache"]["assignCopyFound"] == 20 and m["copy-cache"]["assignLogFound"] == 0
    assert m["no-log"]["assignLogFound"] == 20 and m["no-log"]["assignCopyFound"] == 0
    assert m["capacity"]["tightFound"] == 20 and m["capacity"]["tightMedian"] == 1
    assert m["best"]["bestMismatchRoute"] + m["best"]["bestMismatchAssign"] > 0
    assert m["greedy-top"]["distinctSets"] == 1


# ------------------------------------------------------------------ tables as they appear in the lesson
def fmt(x) -> str:
    return f"{int(x):,}"


def signed(x: int) -> str:
    return f"+{x}" if x > 0 else str(x)


def path_text(path) -> str:
    return " ".join(str(v) for v in path)


def hand_rows(hand: dict) -> dict[str, list[str]]:
    hr, ha = hand["route"], hand["assign"]
    rows: dict[str, list[str]] = {}
    names = {"swap": "두 점 교환", "insert": "한 점 옮기기", "reverse": "구간 뒤집기"}
    rows["hand_route_moves"] = [f"| {names[k]} | {v['moves']} | {v['improving']} | {signed(v['best'])} |" for k, v in hr["families"].items()]
    rows["hand_route_alone"] = [f"| P{a['point']}만 자리 2로 | {path_text(a['path'])} | {a['cost']} | {signed(a['cost'] - hr['start'])} |" for a in hr["alone"]]
    st = hr["steps"]
    rows["hand_route_steps"] = [
        f"| 떼어 낸 뒤 | {path_text(st[0]['path'])} | {st[0]['cost']} | | |",
        f"| P4를 끼움 | {path_text(st[1]['path'])} | {st[1]['cost']} | {', '.join(str(x) for x in st[1]['slots'])} | {st[1]['slot']} |",
        f"| P5를 끼움 | {path_text(st[2]['path'])} | {st[2]['cost']} | {', '.join(str(x) for x in st[2]['slots'])} | {st[2]['slot']} |"]
    s = ha["start"]
    rows["hand_assign_start"] = [f"| {i} | {HAND_D[i]} | {HAND_C[i][0]} | {HAND_C[i][1]} | {HAND_C[i][2]} | {HAND_AS[i]} |" for i in range(6)]
    rows["hand_assign_moves"] = [f"| 한 작업 옮기기 | {ha['moves']} | 0 | - |",
                                 f"| 두 작업 맞바꾸기 | {ha['swaps']['count']} | {ha['swaps']['improving']} | {signed(ha['swaps']['best'])} |"]
    trace = []
    for t, rd in enumerate(ha["regret"]["rounds"], 1):
        cells = []
        for j in ha["pool"]:
            cells.append("-" if j not in rd["regret"] else ("후보 1개" if rd["regret"][j] > BIGV // 2 else str(rd["regret"][j])))
        trace.append(f"| {t} | {' | '.join(cells)} | 작업 {rd['pick']} → 기계 {rd['machine']} |")
    rows["hand_assign_regret"] = trace
    ch = ha["cheapest"]
    rows["hand_assign_cheapest"] = [f"| {t} | 작업 {rd['pick']} → 기계 {rd['machine']} |" for t, rd in enumerate(ch["rounds"], 1)]
    return rows


def table_rows(meas: dict, stuck: dict, expo: list[dict]) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    # T1: what a destroy/repair try finds at a small-move local optimum
    by = {(e["kind"], e["size"]): e for e in stuck["route"]}
    rows["stuck_route"] = [f"| {size} | " + " | ".join(f"{by[(kind, size)]['median']} / {by[(kind, size)]['seeds']}" for kind in range(4)) + " |"
                           for size in STUCK_ROUTE_SIZES]
    ba = {(e["kind"], e["size"], e["rule"]): e for e in stuck["assign"]}
    rows["stuck_assign"] = [f"| {STUCK_ASSIGN_NAME[(kind, size)]} | " + " | ".join(f"{ba[(kind, size, rule)]['median']} / {ba[(kind, size, rule)]['seeds']}" for rule in (0, 1)) + " |"
                            for kind, size in STUCK_ASSIGN]
    # T2: budgets
    for frame in ("route", "assign"):
        rows[f"budget_{frame}"] = [f"| {fmt(e['budget'])} | {fmt(e['small'])} | {fmt(e['dr'])} | {fmt(e['hybrid'])} | {e['hybridBetter']} / {e['hybridWorse']} |"
                                   for e in meas["budget"][frame]]
        rows[f"budget_iters_{frame}"] = [f"| {fmt(e['budget'])} | {fmt(e['drIters'])} | {fmt(e['hybridIters'])} |" for e in meas["budget"][frame]]
    # T3: kinds
    for frame in ("route", "assign"):
        ref = meas["kinds"][frame]["reference"]
        out = []
        for e in meas["kinds"][frame]["rows"]:
            if [e["kind"], e["size"]] == ref:
                out.append(f"| {e['name']} | {fmt(e['median'])} | - | 기준 | {fmt(e['accepted'])} |")
            else:
                out.append(f"| {e['name']} | {fmt(e['median'])} | {e['better']} / {e['worse']} | {verdict(e['better'], e['worse'])} | {fmt(e['accepted'])} |")
        rows[f"kinds_{frame}"] = out
    # T4: repair rules
    for frame in ("route", "assign"):
        out = []
        for e in meas["repair"][frame]:
            dn = ROUTE_DESTROY_NAME[e["kind"]] if frame == "route" else ASSIGN_DESTROY_NAME[(e["kind"], e["size"])]
            cmp = "-" if e["rule"] == 0 else f"{e['better']} / {e['worse']}"
            vd = "기준" if e["rule"] == 0 else verdict(e["better"], e["worse"])
            out.append(f"| {dn} | {REPAIR_NAME[e['rule']]} | {fmt(e['median'])} | {fmt(e['iters'])} | {cmp} | {vd} |")
        rows[f"repair_{frame}"] = out
    # T5: accept rules
    for frame in ("route", "assign"):
        out = []
        for e in meas["accept"][frame]:
            if e["accept"] == 0:
                out.append(f"| 좋아질 때만 | {fmt(e['median'])} | - | 기준 | {fmt(e['accepted'])} |")
                continue
            label = "같아도 받기" if e["accept"] == 1 else f"담금질식, 시작 온도 {e['t0']}"
            out.append(f"| {label} | {fmt(e['median'])} | {e['better']} / {e['worse']} | {verdict(e['better'], e['worse'])} | {fmt(e['accepted'])} |")
        rows[f"accept_{frame}"] = out
    # T6: sizes
    for frame in ("route", "assign"):
        s = meas["size"][frame]
        out = [f"| 작은 이동만 | {fmt(s['small'])} | - | - | - | 기준 |"]
        for e in s["rows"]:
            out.append(f"| {e['size']} | {fmt(e['median'])} | {fmt(e['iters'])} | {fmt(e['accepted'])} | {e['better']} / {e['worse']} | {verdict(e['better'], e['worse'])} |")
        rows[f"size_{frame}"] = out
    # T7: restore
    out = []
    for e in meas["restore"]:
        dn = ASSIGN_DESTROY_NAME[(e["kind"], e["size"])]
        out.append(f"| {dn} | {REPAIR_NAME[e['rule']]} | {'기록' if e['log'] else '복사'} | {fmt(e['iters'])} | {fmt(e['writes'])} | {fmt(e['ops'])} | {fmt(e['cost'])} |")
    rows["restore"] = out
    o = meas["opsplit"]
    rows["opsplit"] = [f"| 순서 틀 | {fmt(o['route']['ops'])} | {fmt(o['route']['terms'])} | {fmt(o['route']['writes'])} |",
                       f"| 배정 틀 | {fmt(o['assign']['ops'])} | {fmt(o['assign']['terms'])} | {fmt(o['assign']['writes'])} |"]
    m = meas["mistakes"]
    rows["mistakes"] = [
        f"| 복사 방식에서 캐시 복원 누락 | {m['copy-cache']['assignCopyFound']} / 20 | {m['copy-cache']['assignCopyMedian']} |",
        f"| 기록 방식에서 떼어 낸 작업의 기록 누락 | {m['no-log']['assignLogFound']} / 20 | {m['no-log']['assignLogMedian']} |",
        f"| 다시 놓을 때 기계의 여유 확인 누락(모든 기계가 가득 찬 입력) | {m['capacity']['tightFound']} / 20 | {m['capacity']['tightMedian']} |",
        f"| 최고해를 따로 보관하지 않음(받는 기준이 나쁜 해를 받는 설정) | 순서 틀 {m['best']['bestMismatchRoute']} / 20, 배정 틀 {m['best']['bestMismatchAssign']} / 20 | - |",
        f"| 비용 기여가 큰 점을 결정적으로 고름 | 서로 다른 부분 {m['greedy-top']['distinctSets']}개 / 200번 | - |"]
    rows["holdout"] = [f"| {'순서 틀' if f == 'route' else '배정 틀'} | {fmt(meas['holdout'][f]['small'])} | {fmt(meas['holdout'][f]['hybrid'])} | {meas['holdout'][f]['better']} / {meas['holdout'][f]['worse']} | {verdict(meas['holdout'][f]['better'], meas['holdout'][f]['worse'])} |"
                       for f in ("route", "assign")]
    # exp table (implementation page)
    pick = {0.25: None, 0.5: None, 1.0: None, 2.0: None, 4.0: None, 8.0: None}
    rows["expo"] = []
    for e in expo:
        if e["x"] in pick:
            rows["expo"].append(f"| {e['x']:g} | {e['exact']:.4f} | {e['approx'] / 65536:.4f} |")
    return rows


def hub_expected(meas: dict) -> list[tuple[str, str]]:
    r, a = meas["budget"]["route"][-1], meas["budget"]["assign"][-1]
    return [("순서 틀 · 시작(번호 순서)", fmt(meas["start"]["route"])),
            (f"순서 틀 · 작은 이동만, 연산 {fmt(r['budget'])}", fmt(r["small"])),
            (f"순서 틀 · 부수고 다시 짓기만, 연산 {fmt(r['budget'])}", fmt(r["dr"])),
            (f"순서 틀 · 작은 이동 1/4 + 부수고 다시 짓기, 연산 {fmt(r['budget'])}", fmt(r["hybrid"])),
            ("배정 틀 · 시작(라운드 로빈)", fmt(meas["start"]["assign"])),
            (f"배정 틀 · 작은 이동만, 연산 {fmt(a['budget'])}", fmt(a["small"])),
            (f"배정 틀 · 부수고 다시 짓기만, 연산 {fmt(a['budget'])}", fmt(a["dr"])),
            (f"배정 틀 · 작은 이동 1/4 + 부수고 다시 짓기, 연산 {fmt(a['budget'])}", fmt(a["hybrid"]))]


def check_svg(path: Path) -> None:
    svg = path.read_text(encoding="utf-8")
    assert re.search(r'viewBox="0 0 720 \d+"', svg), f"{path.name}: viewBox width must be 720"
    assert 'role="img"' in svg and "<title" in svg and "<desc" in svg, f"{path.name}: role/title/desc"
    sizes = [float(v) for v in re.findall(r'font-size="([\d.]+)"', svg)]
    assert sizes and min(sizes) >= 16 and max(sizes) <= 28, f"{path.name}: font sizes {sorted(set(sizes))}"
    assert 27 in sizes, f"{path.name}: title must be 27px"
    height = int(re.search(r'viewBox="0 0 720 (\d+)"', svg).group(1))
    colors = set(re.findall(r'(?:fill|stroke)="(#[0-9a-fA-F]{6})"', svg))
    assert len(colors) <= 12, f"{path.name}: too many colors {len(colors)}"
    for m_ in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)" font-size="([\d.]+)"([^>]*)>([^<]*)</text>', svg):
        x, y, size, attrs, body = float(m_.group(1)), float(m_.group(2)), float(m_.group(3)), m_.group(4), m_.group(5)
        width = sum(size * (1.0 if ord(ch) > 0x2E80 else 0.55) for ch in body)
        if 'text-anchor="end"' in attrs:
            left, right = x - width, x
        elif 'text-anchor="middle"' in attrs:
            left, right = x - width / 2, x + width / 2
        else:
            left, right = x, x + width
        assert left >= 8 and right <= 712 and y <= height - 4, f"{path.name}: text may leave the figure: {body!r}"


def prose_facts(meas: dict, stuck: dict, hand: dict) -> list[str]:
    """Sentences (or fragments) of the lesson that quote measured or recomputed numbers; each must appear verbatim."""
    hr, ha = hand["route"], hand["assign"]
    br, ba = meas["budget"]["route"], meas["budget"]["assign"]
    ho = meas["holdout"]
    g = meas["mistakes"]["greedy-top"]
    sz_r = {e["size"]: e for e in meas["size"]["route"]["rows"]}
    sz_a = {e["size"]: e for e in meas["size"]["assign"]["rows"]}
    kr = {e["name"]: e for e in meas["kinds"]["route"]["rows"]}
    rs = meas["restore"]
    d, c, a0 = HAND_D, HAND_C, HAND_AS
    load = ha["start"]["load"]
    ch, rg = ha["cheapest"], ha["regret"]
    r1 = rg["rounds"][0]
    facts = [
        # idea page: route example
        f"합계는 {hr['start']}입니다", f"모든 순서 5,040개를 훑어 구한 최소 비용도 {hr['optimum']}",
        f"(비용 {hr['steps'][0]['cost']})입니다", f"{hr['start']}보다 {hr['start'] - hr['steps'][2]['cost']}가 줄었습니다",
        f"비용이 {hr['start']}에서 {hr['alone'][0]['cost']}",
        # idea page: assignment example
        f"기계 0이 `{d[3]} + {d[4]} = {load[0]}`, 기계 1이 `{d[0]} + {d[1]} = {load[1]}`, 기계 2가 `{d[2]} + {d[5]} = {load[2]}`",
        f"`{ha['start']['sq']} / 100 = {ha['start']['sq'] // 100}`",
        "`" + " + ".join(str(c[i][a0[i]]) for i in range(6)) + f" = {ha['start']['c']}`",
        f"비용은 `{ha['start']['sq'] // 100} + {ha['start']['c']} = {ha['start']['cost']}`",
        f"추가 비용의 합만 `{ha['start']['c']}`에서 `{rg['c']}`로 줄어 비용이 {rg['cost']}",
        f"첫 번째 맞바꿈만 한 해의 비용은 {ha['double']['first']}로, 부하가 {ch['load'][1]}과 {ch['load'][2]}로",
        f"비용이 {ch['cost']}입니다", f"부하 제곱의 합이 {ch['sq']}({ch['sq'] // 100})로 늘고 추가 비용은 {ch['c']}",
        f"작업 0이 가장 크고, 작업 0은 기계 {r1['machine']}에 놓입니다(비교 값 {r1['best']} 대 {r1['second']})",
        f"`as = {rg['as']}`, 비용 {rg['cost']}",
        # implementation page
        f"`n + 2m + 2 = {120 + 2 * 8 + 2}`",
        # practice page: local optima
        f"비용 중앙값은 순서 틀 {fmt(stuck['localOptimum']['route'])}, 배정 틀 {fmt(stuck['localOptimum']['assign'])}",
        # budgets
        f"(예산 {fmt(br[-1]['budget'])}에서 {fmt(br[-1]['dr'])} 대 {fmt(br[-1]['small'])}, 20개 중 {br[-1]['drOnlyWorse']}개 시드가 나쁨)",
        f"같은 예산에서 {fmt(br[-1]['drIters'])}번밖에 돌지 못합니다",
        f"(18 / 2와 20 / 0, 중앙값 {fmt(br[1]['hybrid'])}와 {fmt(br[2]['hybrid'])}, 작은 이동만의 {fmt(br[1]['small'])}과 {fmt(br[2]['small'])})",
        f"예산 {fmt(br[0]['budget'])}에서는 결정하지 못했습니다({br[0]['hybridBetter']} / {br[0]['hybridWorse']})",
        f"{fmt(br[0]['small'])}에서 {fmt(br[2]['small'])}까지만 내려가며",
        f"중앙값 {fmt(ba[-1]['small'])}에 머물고 혼합은 예산 {fmt(ba[-1]['budget'])}에서 {fmt(ba[-1]['hybrid'])}(18 / 2, 더 좋음)로 비용의 0.1%도 안 되는 {ba[-1]['small'] - ba[-1]['hybrid']}",
        f"시작 {fmt(meas['start']['assign'])}에서 {fmt(ba[-1]['small'])}까지 {fmt(meas['start']['assign'] - ba[-1]['small'])}를 내려온",
        f"{fmt(ba[0]['small'])}에 미치지 못했습니다({fmt(ba[0]['hybrid'])})",
        f"차이({ho['assign']['small'] - ho['assign']['hybrid']})는 비용의 0.02%",
        # kinds
        f"무작위 8개의 {fmt(kr['무작위']['median'])}는 작은 이동만({fmt(br[-1]['small'])})과 같은 수준",
        f"비용 {fmt(g['tourCost'])}로, 무작위({fmt(g['tourRandomCost'])})보다 {g['tourWorse']}개 시드 모두에서 나빴습니다({g['tourBetter']} / {g['tourWorse']})",
        # sizes
        f"(받은 횟수 0, {fmt(sz_r[200]['median'])}가 그대로 남음)", f"반복 수가 순서 틀에서 {fmt(sz_r[1]['iters'])}번에서 {fmt(sz_r[200]['iters'])}번으로 줄고",
        f"예산 {fmt(br[0]['budget'])}에서 얻은 {fmt(br[0]['small'])}",
        f"{fmt(sz_a[1]['iters'])}",
        # restore
        f"{fmt(rs[0]['writes'])}번으로 늘고, 기록은 떼어 낸 작업만 되돌려 {rs[1]['writes']}번",
        f"반복당 연산 {fmt(rs[0]['ops'])}대 {fmt(rs[1]['ops'])}", f"({fmt(rs[0]['iters'])}번 대 {fmt(rs[1]['iters'])}번)",
        f"({fmt(rs[2]['ops'])} 대 {fmt(rs[3]['ops'])}, 반복 {fmt(rs[2]['iters'])}번 대 {fmt(rs[3]['iters'])}번)",
        f"(반복 {fmt(rs[4]['iters'])}번 대 {fmt(rs[5]['iters'])}번)",
    ]
    return facts


def check_text(meas: dict, stuck: dict, hand: dict, expo: list[dict]) -> int:
    text = read_lesson_text(LESSON_ID)
    hub = read_hub_text(LESSON_ID)
    lines = hub.rstrip("\n").splitlines()
    assert 40 <= len(lines) <= 60, f"hub must be 40..60 lines, has {len(lines)}"
    count = 0
    for tables in (table_rows(meas, stuck, expo), hand_rows(hand)):
        for name, rows in tables.items():
            for row in rows:
                assert row in text, f"lesson table row missing or differs ({name}): {row}"
                count += 1
    count += check_hub_summary(LESSON_ID, hub_expected(meas))
    facts = prose_facts(meas, stuck, hand)
    missing = [f for f in facts if f not in text]
    assert not missing, "sentences quoting a measured number are missing or differ:\n" + "\n".join(missing)
    count += len(facts)
    fig = (LESSON_DIR / "lesson-assets" / "size-spectrum.svg").read_text(encoding="utf-8")
    rows = {e["size"]: e for e in meas["size"]["route"]["rows"]}
    for needle in (fmt(rows[1]["iters"]), fmt(rows[200]["iters"]), fmt(ROUTE_BUDGETS[-1])):
        assert needle in fig, f"size-spectrum.svg must quote {needle}"
    for page in ("pages/idea.md", "pages/implementation.md", "pages/practice.md"):
        assert f"]({page})" in hub, f"hub must link {page}"
    # site problems are named only in the application section of practice.md
    for page in ("lesson.md", "pages/idea.md", "pages/implementation.md", "pages/practice.md"):
        body = (LESSON_DIR / page).read_text(encoding="utf-8")
        if page == "pages/practice.md":
            assert "## 적용 사례" in body, "practice.md needs an 적용 사례 section"
            head, rest = body.split("## 적용 사례", 1)
            tail = re.split(r"\n## ", rest, maxsplit=1)
            body = head + ("\n## " + tail[1] if len(tail) > 1 else "")
        for name in SITE_PROBLEMS:
            assert name not in body, f"site problem {name} named outside the 적용 사례 section ({page})"
        if page != "pages/practice.md":
            assert "/practice/" not in body, f"problem link outside the 적용 사례 section ({page})"
    for heading in ("언제 쓰고 언제 쓰지 않는가", "흔한 실수", "다른 문제에 옮길 때", "적용 사례"):
        assert re.search(r"^## .*" + heading, text, re.M), f"missing section: {heading}"
    checklist = re.search(r"## 다른 문제에 옮길 때[^\n]*\n(.*?)(?=\n## )", text, re.S)
    assert checklist and 5 <= len(re.findall(r"^\d+\. ", checklist.group(1), re.M)) <= 8, "checklist needs 5-8 questions"
    assert "> **코드 환경: h-contest 제출용 코드.**" in text
    for fig in FIGURES:
        assert re.search(r"!\[[^\]\[]+\]\((?:\.\./)?lesson-assets/" + re.escape(fig) + r"\)\n\n\[그림 크게 보기\]\(https://git\.readiz\.com/h-contest-lesson/lessons/"
                         + LESSON_ID + "/lesson-assets/" + re.escape(fig) + r"\)", text), f"figure {fig} is not embedded with its enlarge link"
        check_svg(LESSON_DIR / "lesson-assets" / fig)
    for token in ("hill-climbing-and-annealing", "construction-heuristics", "neighborhood-and-delta"):
        assert f"https://h.readiz.com/learn/{token}" in text, f"missing link to {token}"
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
        done = subprocess.run(["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", str(work / "syntax.cpp")], capture_output=True, text=True)
        assert done.returncode == 0, done.stderr[:2000]
        with ThreadPoolExecutor(max_workers=2) as pool:
            f_san = pool.submit(build, code, work, "san", True)
            f_fast = pool.submit(build, code, work, "fast", False, "-O2")
            san, fast = f_san.result(), f_fast.result()

        n_gen = check_gen(run(san, "gen"))
        chk = run(san, "check")
        assert all(r[-1] == "0" for r in chk if r[0] in ("check",)), "checkDR must pass for every option"
        for r in chk:
            if r[0] in ("destroyroute", "destroyassign", "rollbackroute"):
                assert r[2] == "0", f"{r[0]}: {r[1]} cases, {r[2]} bad"
        n_check = sum(1 for r in chk if r[0] == "check")
        ident = run(san, "identity")
        assert len(ident) == 20 and all(r[5] == "1" and r[8] == r[9] and int(r[6]) > int(r[7]) for r in ident), "copy and log must follow the same trajectory; log must cost fewer operations"
        small = run(san, "small")
        for r in small:
            assert r[3] == "1" and r[4] == "1" and r[5] == r[6]
            if r[1] == "assign":
                assert r[7] == "1"
        expo = check_expo(run(san, "expo"))
        hand = check_hand(run(san, "hand"))

        exp_rows = run(fast, "exp")
        n_final = verify_final_solutions(exp_rows)
        meas = summarise_exp(exp_rows)
        stuck_rows = run(fast, "stuck")
        n_lo = verify_local_optima(stuck_rows)
        stuck = summarise_stuck(stuck_rows)
        mistakes = run_mistakes(sn, work, fast)
        check_mistakes(mistakes)

    meas.update({"schema": 1, "stuck": stuck, "hand": hand, "mistakes": mistakes,
                 "expo": [{"x": e["x"], "approx": e["approx"]} for e in expo],
                 "rule": f"한쪽이 {WIN} / 20 시드 이상 나으면 차이가 있다고 보고, 아니면 결정 못 함",
                 "problems": {"route": "N=200, 좌표 0..999, 맨해튼 거리 합", "assign": "N=120, M=8, K=18, 부하 제곱합/100 + 추가 비용"}})
    if args.output:
        DATA.parent.mkdir(parents=True, exist_ok=True)
        DATA.write_text(json.dumps(meas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {DATA.relative_to(ROOT)}")
    if args.print_tables:
        for name, tr in {**table_rows(meas, stuck, expo), **hand_rows(hand)}.items():
            print(f"[{name}]")
            print("\n".join(tr))
        print("[hub]")
        for label, value in hub_expected(meas):
            print(f"| {label} | {value} |")
        return
    stored = json.loads(DATA.read_text(encoding="utf-8"))
    assert stored == json.loads(json.dumps(meas)), "measurements.json differs from a fresh measurement (run with --output)"
    n_rows = check_text(meas, stuck, hand, expo)
    print(f"destroy-and-repair ok: {len(BLOCKS)} code blocks, {n_gen} generated instances checked against Python, "
          f"{n_check} checkDR configurations, {n_lo} small-move local optima and {n_final} final solutions recomputed, "
          f"{len(MUTATIONS)} injected mistakes detected, {len(FIGURES)} figures, {n_rows} table rows matched")


if __name__ == "__main__":
    main()
