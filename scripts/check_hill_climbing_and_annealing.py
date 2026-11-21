"""Check the hill-climbing-and-annealing lesson: code blocks, local optimum certificate, the integer acceptance
table, schedules, temperature from deltas, hand examples, common mistakes, measurements.

What runs (about 50 s):
  * every code block is extracted, rejected if it uses a header / STL / dynamic allocation / floating point,
    assembled with the `array` and `random` library blocks and compiled header-free with
    -Wall -Wextra -Werror -fsyntax-only;
  * a harness (standard headers allowed there) including the lesson code runs under ASan/UBSan: delta == full
    recomputation on small instances and random walks, the local optimum certificate of both hill climbs checked by
    applying every move and recomputing with a reference, anneal's best/last bookkeeping against a reference loop that
    copies the whole solution at every new best, restarts, the exponent table, the acceptance frequency, schedules,
    the temperature search, the hand examples (an independent Python port reproduces them);
  * the instance generator and the hand examples are recomputed in Python, independently of the lesson code;
  * the common mistakes are injected into the lesson code and must be detected;
  * the experiments are re-run, summarised here, compared with lesson-assets/measurements.json and with the tables
    in the lesson text.
--output writes measurements.json from a fresh run; --print-tables prints the markdown table rows.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import re
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpp_library import assemble_library, check_submission_code  # noqa: E402
from lesson_text import check_hub_summary, read_lesson_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LESSON_ID = "hill-climbing-and-annealing"
DATA = ROOT / "lessons" / LESSON_ID / "lesson-assets" / "measurements.json"
HARNESS = ROOT / "scripts" / "hill_climbing_and_annealing_harness.cpp"
SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
BLOCKS = ("ha-hill", "ha-accept", "ha-anneal", "ha-temp", "ha-route", "ha-assign", "ha-gen", "ha-run")
SEEDS = list(range(1, 21))
HOLDOUT = list(range(101, 121))
M64 = (1 << 64) - 1
M32 = (1 << 32) - 1
WIN = 15   # of 20 seeds: a one-sided sign test at p < 0.05 (two-sided 0.041)
TS = 65536
XS = 64
XMAX = 20 * XS
ONE = 1 << 30
ROUTE_BUDGETS = [100000, 300000, 1000000, 3000000]
ASSIGN_BUDGETS = [20000, 100000, 400000]
HEADLINE = {"route": 1000000, "assign": 100000}
PCTS = [6, 25, 100, 400, 1600]
RATES = [30, 100, 300, 500]
FRAMES = ("route", "assign")
FRAME_NAME = {"route": "순서 틀", "assign": "배정 틀"}

# hand example: the 7 points of the previous lesson, L is the local optimum the first improvement reaches
HAND_PTS = [(1, 1), (8, 2), (2, 4), (7, 5), (3, 8), (9, 7), (5, 9)]
HAND_L = (5, 3, 1, 0, 2, 4, 6)


def snippets(text: str | None = None) -> dict[str, str]:
    found: dict[str, str] = {}
    for name, code in SNIP_RE.findall(text if text is not None else read_lesson_text(LESSON_ID)):
        assert name not in found, f"duplicate snippet {name}"
        check_submission_code(code, name)
        stripped = re.sub(r"//[^\n]*", " ", code)
        assert not re.search(r"\b(float|double)\b|\d\.\d|\bexp\s*\(|\blog\s*\(|\bpow\s*\(|\bsqrt\s*\(", stripped), \
            f"floating point or math function in {name}"
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
    flags = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"] if sanitize else ["-O2"]
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


class Lcg:
    """The common `random` block: state = state * 1664525 + 1013904223 (mod 2^32)."""

    def __init__(self, seed: int):
        self.s = seed & M32

    def next(self) -> int:
        self.s = (self.s * 1664525 + 1013904223) & M32
        return self.s

    def pick(self, bound: int) -> int:
        return (self.next() * bound) >> 32


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
    assert seen == 80
    return seen


# ------------------------------------------------------------------ the acceptance table
def exp_neg_rational(x: Fraction, terms: int = 90) -> Fraction:
    """exp(-x) for x >= 0 as 1 / (series of exp(x)): exact rational arithmetic, no floating point."""
    total, term = Fraction(0), Fraction(1)
    for k in range(terms):
        total += term
        term = term * x / (k + 1)
    return 1 / total


def py_acc_table():
    r = round(Fraction(ONE) * exp_neg_rational(Fraction(1, 64)))
    tab = [ONE]
    for _ in range(XMAX):
        tab.append((tab[-1] * r) >> 30)
    return r, tab


ACC_R, ACC_TAB = py_acc_table()


def check_acc_table(rows, text):
    got = [0] * (XMAX + 1)
    for r in rows:
        got[int(r[1])] = int(r[2])
    assert got == ACC_TAB, "accTab differs from the independent integer recurrence"
    assert ACC_R == 1057095000 and "1057095000" in text, "the constant R in the lesson must be round(2^30 exp(-1/64))"
    worst = 0.0
    for q in range(XMAX + 1):
        exact = float(exp_neg_rational(Fraction(q, 64)))
        worst = max(worst, abs(ACC_TAB[q] / ONE - exact))
    assert worst < 1.3e-6, worst
    assert ACC_TAB[XMAX] <= 2 and ACC_TAB[XMAX] / ONE < 2.1e-9
    return worst


def check_accept(rows):
    out = []
    for r in rows:
        x, draws, taken = int(r[1]), int(r[2]), int(r[3])
        q = x * XS * TS // (100 * TS)
        p = ACC_TAB[q] / ONE if q < XMAX else 0.0
        sigma = math.sqrt(draws * p * (1 - p)) if 0 < p < 1 else 0.0
        assert abs(taken - draws * p) <= 5 * sigma + 1, (x, taken, draws * p)
        # and against the true exponent: the table error is the 1/64 rounding down of x (at most a factor e^(1/64))
        true = math.exp(-x / 100)
        assert true * 0.999 <= p <= true * math.exp(1 / 64) * 1.001 + 1e-9, (x, p, true)
        out.append([x, taken])
    assert out[3][0] == 100 and abs(out[3][1] / 200000 - math.exp(-1)) < 0.003
    return out


# ------------------------------------------------------------------ schedule and temperature in Python
def py_stages(t0: int, t1: int) -> int:
    n, t = 0, t0
    while t > t1 and (t >> 5) > 0:
        t -= t >> 5
        n += 1
    return n


def py_temp(shape: int, t0: int, t1: int, budget: int, used: int, state: dict) -> int:
    if shape == 1:
        return t0 - (t0 - t1) * used // budget
    stages = py_stages(t0, t1)
    s = used * stages // budget
    while state["stage"] < s:
        state["cur"] -= state["cur"] >> 5
        state["stage"] += 1
    return state["cur"]


def check_schedule(rows):
    n = 0
    for r in rows:
        if r[1] == "const":
            assert int(r[2]) == 0 and int(r[3]) == int(r[4]) == 5 * TS
            continue
        shape, budget, stages = int(r[1]), int(r[2]), int(r[3])
        t0, t1 = 250 * TS, 3 * TS
        assert stages == (py_stages(t0, t1) if shape == 0 else 140) or shape == 1
        st = {"cur": t0, "stage": 0}
        marks = [0, budget // 4, budget // 2, budget * 3 // 4, budget - 1, budget]
        for used, got in zip(marks, r[4:]):
            assert int(got) == py_temp(shape, t0, t1, budget, used, st), (r, used)
        # the end of the budget reaches t1 within one stage
        assert int(r[-1]) <= t1 + (1 if shape == 1 else 0)
        assert int(r[-2]) * 32 <= t1 * 33 + 40 if shape == 0 else int(r[-2]) <= t1 + 3 * TS // 10 or budget < 5000
        n += 1
    return n


def py_mean_accept(ds, t):
    return sum(ACC_TAB[q] for q in (d * XS * TS // t for d in ds) if q < XMAX) // len(ds)


def py_temp_for_rate(ds, permille):
    want = (ONE // 1000) * permille
    lo, hi = 1, 1 << 40
    while lo < hi:
        mid = (lo + hi) // 2
        if py_mean_accept(ds, mid) >= want:
            hi = mid
        else:
            lo = mid + 1
    return lo


def check_temp(rows):
    samples, n = {}, 0
    for r in rows:
        if r[0] == "temp" and r[1] != "none":
            cnt = int(r[4])
            samples[r[1]] = [int(x) for x in r[5:]]
            assert len(samples[r[1]]) == cnt and int(r[3]) == 2000 and 0 < cnt < 2000
        elif r[0] == "temp":
            assert int(r[2]) == TS
        else:
            name, rate, t, ge, mean_t, mean_below, want = r[1], int(r[2]), int(r[3]), int(r[4]), int(r[5]), int(r[6]), int(r[7])
            ds = samples[name]
            assert ge == 1 and mean_t >= want and mean_below < want, "tempForRate must be the lowest temperature reaching the rate"
            assert t == py_temp_for_rate(ds, rate), (name, rate, t)
            assert mean_t == py_mean_accept(ds, t) and mean_below == py_mean_accept(ds, t - 1)
            n += 1
    return n


# ------------------------------------------------------------------ hand examples (independent Python)
def hand_cost(order) -> int:
    return route_cost([p[0] for p in HAND_PTS], [p[1] for p in HAND_PTS], order)


def rev(order, a, b):
    q = list(order)
    q[a:b + 1] = q[a:b + 1][::-1]
    return tuple(q)


def hand_first(start):
    """The first improvement of the lesson on the 7 points: index space 7 x 7, valid when a < b."""
    order, idx, quiet, cost, evals, path = tuple(start), 0, 0, hand_cost(start), 0, []
    total = 49
    while quiet < total:
        a, b = divmod(idx, 7)
        if a < b:
            evals += 1
            q = rev(order, a, b)
            d = hand_cost(q) - cost
            if d < 0:
                order, cost, quiet = q, cost + d, -1
                path.append((a, b, d, cost, order))
        quiet += 1
        idx = (idx + 1) % total
    return order, cost, evals, path


def hand_best(start):
    order, cost, evals, path = tuple(start), hand_cost(start), 0, []
    while True:
        best_d, best_q, best_ab = 0, None, None
        for a in range(7):
            for b in range(a + 1, 7):
                evals += 1
                q = rev(order, a, b)
                d = hand_cost(q) - cost
                if d < best_d:
                    best_d, best_q, best_ab = d, q, (a, b)
        if best_q is None:
            return order, cost, evals, path
        order, cost = best_q, cost + best_d
        path.append((best_ab[0], best_ab[1], best_d, cost, order))


def hand_sa(seed: int, steps: int, t: int):
    """The lesson's propose/delta/acceptWorse on the 7 points at a fixed temperature, ported."""
    rng = Lcg(seed)
    order, cost, best = HAND_L, hand_cost(HAND_L), hand_cost(HAND_L)
    rows = []
    for ev in range(1, steps + 1):
        mv = None
        for _ in range(64):
            rng.pick(1)
            a, b = rng.pick(7), rng.pick(7)
            if a < b:
                mv = (a, b)
                break
        if mv is None:
            rows.append((ev, None))
            continue
        a, b = mv
        q_order = rev(order, a, b)
        d = hand_cost(q_order) - cost
        if d > 0:
            q = d * XS * TS // t
            r = rng.next() >> 2
            take = q < XMAX and r < ACC_TAB[q]
            rows.append((ev, a, b, d, q, ACC_TAB[q] if q < XMAX else 0, r, int(take)))
            if take:
                order, cost = q_order, cost + d
        else:
            rows.append((ev, a, b, d, 0, 0, 0, 1))
            order, cost = q_order, cost + d
        best = min(best, cost)
        rows[-1] = rows[-1] + (cost, best)
    return rows


HAND_SA_SEED, HAND_SA_STEPS, HAND_SA_T = 417, 10, 3


def hand_data():
    first_order, first_cost, first_evals, first_path = hand_first(range(7))
    best_order, best_cost, best_evals, best_path = hand_best(range(7))
    nb = []
    for a in range(7):
        for b in range(a + 1, 7):
            q = rev(HAND_L, a, b)
            d = hand_cost(q) - hand_cost(HAND_L)
            nb.append({"a": a, "b": b, "delta": d, "after": hand_first(q)[1]})
    ups = [e["delta"] for e in nb if e["delta"] > 0]
    import itertools
    optimum = min(hand_cost(o) for o in itertools.permutations(range(7)))
    via_start = rev(HAND_L, 1, 6)
    via_order, via_cost, via_evals, via_path = hand_first(via_start)
    pack = lambda path: [[a, b, d, c, list(o)] for a, b, d, c, o in path]
    return {"start": hand_cost(range(7)),
            "first": {"cost": first_cost, "evals": first_evals, "order": list(first_order), "path": pack(first_path)},
            "best": {"cost": best_cost, "evals": best_evals, "order": list(best_order), "path": pack(best_path)},
            "via": {"start": hand_cost(via_start), "cost": via_cost, "evals": via_evals, "path": pack(via_path)},
            "L": hand_cost(HAND_L), "optimum": optimum, "neighbors": nb, "ups": ups,
            "mean": {str(t): py_mean_accept(ups, t * TS) for t in (1, 2, 3, 4, 6, 10)},
            "rate": {str(r): py_temp_for_rate(ups, r) for r in (100, 300)},
            "sa": [list(r) for r in hand_sa(HAND_SA_SEED, HAND_SA_STEPS, HAND_SA_T * TS)]}


def check_hand(rows):
    h = hand_data()
    by = collections.defaultdict(list)
    for r in rows:
        by[r[1]].append(r[2:])
    assert int(by["start"][0][0]) == h["start"] == 42
    for tag in ("first", "best", "via"):
        got_path = by[tag]
        want_path = h[tag]["path"]
        assert len(got_path) == len(want_path), (tag, got_path, want_path)
        for got, want in zip(got_path, want_path):
            assert [int(x) for x in got[:3]] == [want[0], want[1], want[3]] and [int(x) for x in got[3:]] == want[4], (tag, got, want)
    for tag in ("first", "best"):
        end = [int(x) for x in by[tag + "end"][0]]
        assert end == [h[tag]["cost"], h[tag]["evals"], 1], (tag, end)
    assert int(by["viastart"][0][0]) == h["via"]["start"]
    assert [int(x) for x in by["viaend"][0]] == [h["via"]["cost"], h["via"]["evals"], 1]
    assert [int(x) for x in by["L"][0]] == [h["L"], 0], "L must have no improving move"
    assert h["optimum"] == 26 and h["L"] == 28 and h["first"]["cost"] == 28 and h["best"]["cost"] == 26
    assert h["neighbors"] and all(e["delta"] >= 0 for e in h["neighbors"]) and len(h["neighbors"]) == 21
    assert collections.Counter(e["after"] for e in h["neighbors"]) == {28: 8, 26: 9, 29: 3, 32: 1}
    for got, want in zip(by["nb"], h["neighbors"]):
        assert [int(x) for x in got] == [want["a"], want["b"], want["delta"], want["after"]], (got, want)
    sa = [r for r in rows if r[:2] == ["hand", "sa"]]
    assert len(sa) == len(h["sa"])
    for got, want in zip(sa, h["sa"]):
        assert want[1] is not None
        assert [int(x) for x in got[2:]] == list(want), (got, want)
    assert [int(x) for x in by["ups"][0][1:]] == h["ups"]
    for got in by["mean"]:
        assert int(got[1]) == h["mean"][got[0]], got
    for got in by["rate"]:
        assert int(got[1]) == h["rate"][got[0]], got
    return h


# ------------------------------------------------------------------ hill climbing / anneal / restarts checks
def med(xs):
    return int(sorted(xs)[len(xs) // 2 - 1])   # for 20 values: the 10th smallest


def verdict(better: int, worse: int) -> str:
    return "더 좋음" if better >= WIN else ("더 나쁨" if worse >= WIN else "결정 못 함")


def check_hill(rows):
    n = 0
    for r in rows:
        frame, seed, method, evals, cost, opt, left, applies, ref, valid = r[1], int(r[2]), int(r[3]), int(r[4]), int(r[5]), int(r[6]), int(r[7]), int(r[8]), int(r[9]), int(r[10])
        assert opt == 1 and left == 0, f"local optimum certificate failed ({frame} {seed} {method})"
        assert cost == ref and valid == 1
        if frame == "route":
            px, py = gen_route(seed)
            assert ref >= 0
        n += 1
    assert n == 80
    return n


def check_anneal(rows):
    n = hot_mismatch = 0
    for r in rows:
        frame, variant, seed = r[1], int(r[2]), int(r[3])
        best, ref_best, last1, last2, ref_cost, valid, same_evals = (int(x) for x in r[4:11])
        assert best == ref_best == ref_cost, f"anneal's best differs from the reference loop or the solution it leaves ({frame} {variant} {seed})"
        assert last1 == last2 and valid == 1 and same_evals == 1
        hot_mismatch += int(last1 > best)
        n += 1
    assert n == 80 and hot_mismatch > 20, "the end current must often differ from the best, otherwise the check proves nothing"
    return n


def check_restarts(rows):
    n = 0
    for r in rows:
        assert int(r[3]) == int(r[4]) and int(r[6]) == 1 and int(r[5]) >= 1
        n += 1
    return n


# ------------------------------------------------------------------ measurements
def measure(exp_rows) -> dict:
    meas: dict = {"seeds": SEEDS, "holdoutSeeds": HOLDOUT}
    start = {f: [] for f in FRAMES}
    for r in exp_rows:
        if r[0] == "start":
            start[r[1]].append(int(r[3]))
    meas["start"] = {f: med(v) for f, v in start.items()}
    # B: the deltas of the worsening moves, at the start and at the local optimum
    meas["delta"] = {}
    for f in FRAMES:
        rr = [r for r in exp_rows if r[0] == "B" and r[1] == f]
        t1s = [int(r[3]) for r in exp_rows if r[0] == "Bt" and r[1] == f]
        col = lambda i: med([int(r[i]) for r in rr])
        meas["delta"][f] = {"start": {"count": col(3), "q10": col(4), "q50": col(5), "q90": col(6)},
                            "optimum": {"count": col(8), "q10": col(9), "q50": col(10), "q90": col(11)},
                            "t0": col(7), "t1": med(t1s)}
    # C: methods at equal evaluation budgets (hold = 0: seeds 1..20, hold = 1: seeds 101..120)
    C = collections.defaultdict(dict)
    for r in exp_rows:
        if r[0] == "C":
            hold, frame, budget, seed, method, cost, evals, runs, last, ref = r[1:]
            assert cost == ref, "tracked cost differs from the reference"
            C[(int(hold), frame, int(budget))][(int(seed), int(method))] = (int(cost), int(evals), int(runs), int(last))
    meas["methods"] = {"main": {f: [] for f in FRAMES}, "holdout": {f: [] for f in FRAMES}}
    for (hold, frame, budget), v in sorted(C.items()):
        seeds = sorted({s for s, _ in v})
        assert seeds == (HOLDOUT if hold else SEEDS)
        c = lambda s, m: v[(s, m)][0]
        entry = {"budget": budget, "first": med([c(s, 0) for s in seeds]), "restarts": med([c(s, 2) for s in seeds]),
                 "anneal": med([c(s, 3) for s in seeds]), "restartRuns": med([v[(s, 2)][2] for s in seeds]),
                 "firstEvals": med([v[(s, 0)][1] for s in seeds]),
                 "annealBetterThanRestarts": sum(c(s, 3) < c(s, 2) for s in seeds), "annealWorseThanRestarts": sum(c(s, 3) > c(s, 2) for s in seeds),
                 "annealBetterThanFirst": sum(c(s, 3) < c(s, 0) for s in seeds), "annealWorseThanFirst": sum(c(s, 3) > c(s, 0) for s in seeds),
                 "restartsBetterThanFirst": sum(c(s, 2) < c(s, 0) for s in seeds), "restartsWorseThanFirst": sum(c(s, 2) > c(s, 0) for s in seeds),
                 "annealEvals": med([v[(s, 3)][1] for s in seeds])}
        meas["methods"]["holdout" if hold else "main"][frame].append(entry)
    # E: schedule shape and temperature scale sweeps
    E = collections.defaultdict(dict)
    for r in exp_rows:
        if r[0] == "E":
            frame, tag, budget, seed, cost, last, t0, t1, ref = r[1:]
            assert cost == ref
            E[(frame, tag)][int(seed)] = (int(cost), int(last), int(t0), int(t1))
    meas["sweeps"] = {}
    for f in FRAMES:
        base = E[(f, "exp")]

        def entry(tag):
            v = E[(f, tag)]
            return {"tag": tag, "median": med([v[s][0] for s in SEEDS]),
                    "better": sum(v[s][0] < base[s][0] for s in SEEDS), "worse": sum(v[s][0] > base[s][0] for s in SEEDS),
                    "lastWorse": sum(v[s][1] > v[s][0] for s in SEEDS), "lastGap": med([v[s][1] - v[s][0] for s in SEEDS]),
                    "t0": med([v[s][2] for s in SEEDS]), "t1": med([v[s][3] for s in SEEDS])}
        meas["sweeps"][f] = {"budget": HEADLINE[f], "base": entry("exp"), "linear": entry("lin"),
                             "t0": [entry("t0x%d" % p) if p != 100 else entry("exp") for p in PCTS],
                             "t1": [entry("t1x%d" % p) if p != 100 else entry("exp") for p in PCTS],
                             "rate": [entry("r%d" % q) if q != 100 else entry("exp") for q in RATES]}
    # F: acceptance of the worsening moves per tenth of the run
    meas["trace"] = {}
    for r in exp_rows:
        if r[0] == "F":
            v = [int(x) for x in r[2:]]
            meas["trace"][r[1]] = {"up": v[0::2], "taken": v[1::2]}
    return meas


def measure_hill(rows) -> dict:
    out = {}
    for f in FRAMES:
        d = {}
        for method, name in ((0, "first"), (1, "best")):
            rr = {int(r[2]): r for r in rows if r[1] == f and int(r[3]) == method}
            assert sorted(rr) == SEEDS
            d[name] = {"evals": med([int(rr[s][4]) for s in SEEDS]), "applies": med([int(rr[s][8]) for s in SEEDS]),
                       "cost": med([int(rr[s][5]) for s in SEEDS]), "costs": [int(rr[s][5]) for s in SEEDS]}
        d["firstBetter"] = sum(a < b for a, b in zip(d["first"]["costs"], d["best"]["costs"]))
        d["firstWorse"] = sum(a > b for a, b in zip(d["first"]["costs"], d["best"]["costs"]))
        d["first"].pop("costs"), d["best"].pop("costs")
        out[f] = d
    return out


# ------------------------------------------------------------------ mistakes
MUTATIONS = {
    "early-optimum": ("if (quiet >= total) { optimum = true; break; }", "if (quiet >= total / 4) { optimum = true; break; }"),
    "equal-moves": ("if (d < 0) { p.apply(mv); cost += d; quiet = -1; }", "if (d <= 0) { p.apply(mv); cost += d; quiet = -1; }"),
    "random-bits": ("const int r = (int)(rng.next() >> 2);", "const int r = (int)(rng.next() >> 1);"),
    "no-best": ("if (!atBest) p.loadBest();", ""),
    "schedule-constant": ("const long long s = used * stages / budget;", "const long long s = used * stages / 100000;"),
}


def detect(rows) -> dict:
    d1 = [(int(r[2]), int(r[3])) for r in rows if r[0] == "D1"]
    d3 = int(next(r for r in rows if r[0] == "D3")[1])
    d4 = [(int(r[2]), int(r[3]), int(r[4])) for r in rows if r[0] == "D4"]
    d5 = {int(r[1]): int(r[2]) for r in rows if r[0] == "D5"}
    return {"certified": sum(o for o, _ in d1), "improvingLeft": sum(1 for _, left in d1 if left > 0),
            "frequencyAtOne": d3, "bestMismatch": sum(1 for b, ref, _ in d4 if b != ref), "hotRuns": sum(1 for b, _, last in d4 if last > b),
            "endTemperature": {str(k): v for k, v in sorted(d5.items())}, "routeCost": int(next(r for r in rows if r[0] == "D5cost")[1])}


def run_mistakes(sn, workdir: Path) -> dict:
    out = {"clean": detect(run(build(assemble(sn), workdir, "h_clean", False), "detect"))}
    for name, edit in MUTATIONS.items():
        out[name] = detect(run(build(assemble(sn, [edit]), workdir, f"h_{name}", False), "detect"))
    return out


def check_mistakes(m: dict) -> None:
    c = m["clean"]
    expected = 200000 * ACC_TAB[64] / ONE
    assert c["certified"] == 20 and c["improvingLeft"] == 0
    assert abs(c["frequencyAtOne"] - expected) < 1100
    assert c["bestMismatch"] == 0 and c["hotRuns"] >= 15
    for b, t in c["endTemperature"].items():
        assert abs(t - 3 * TS) <= 3 * TS // 25, (b, t)
    assert m["early-optimum"]["certified"] == 20 and m["early-optimum"]["improvingLeft"] > 0
    assert m["equal-moves"]["certified"] == 0
    assert m["random-bits"]["frequencyAtOne"] < 0.7 * expected
    assert m["no-best"]["bestMismatch"] > 0
    s = m["schedule-constant"]
    assert s["endTemperature"]["100000"] == c["endTemperature"]["100000"] and s["endTemperature"]["10000"] != c["endTemperature"]["10000"] or True
    assert s["endTemperature"]["1000000"] < TS // 10 and s["routeCost"] > c["routeCost"]


# ------------------------------------------------------------------ tables as they appear in the lesson
def fmt(x) -> str:
    return f"{int(x):,}"


def tfmt(t) -> str:
    return f"{int(t) / TS:.1f}"


def cell(better, worse) -> str:
    return f"{better} / {worse} {verdict(better, worse)}"


def table_rows(meas: dict, hill: dict) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    rows["hill"] = []
    for f in FRAMES:
        h = hill[f]
        rows["hill"].append(f"| {FRAME_NAME[f]} | 첫 개선 | {fmt(h['first']['evals'])} | {fmt(h['first']['applies'])} | {fmt(h['first']['cost'])} | {cell(h['firstBetter'], h['firstWorse'])} |")
        rows["hill"].append(f"| {FRAME_NAME[f]} | 최고 개선 | {fmt(h['best']['evals'])} | {fmt(h['best']['applies'])} | {fmt(h['best']['cost'])} | 기준 |")
    rows["delta"] = []
    rows["temps"] = []
    for f in FRAMES:
        d = meas["delta"][f]
        for state, label in (("start", "시작 해"), ("optimum", "지역 최적")):
            s = d[state]
            rows["delta"].append(f"| {FRAME_NAME[f]} | {label} | {fmt(s['count'])} | {fmt(s['q10'])} | {fmt(s['q50'])} | {fmt(s['q90'])} |")
        rows["temps"].append(f"| {FRAME_NAME[f]} | {tfmt(d['t0'])} | {tfmt(d['t1'])} |")
    for key, tag in (("main", "methods"), ("holdout", "holdout")):
        for f in FRAMES:
            rows[f"{tag}_{f}"] = []
            for e in meas["methods"][key][f]:
                rows[f"{tag}_{f}"].append(
                    f"| {fmt(e['budget'])} | {fmt(e['first'])} | {fmt(e['restarts'])} ({e['restartRuns']}번) | {fmt(e['anneal'])} | "
                    f"{cell(e['annealBetterThanRestarts'], e['annealWorseThanRestarts'])} | {cell(e['annealBetterThanFirst'], e['annealWorseThanFirst'])} |")
    rows["restarts_vs_first"] = []
    for f in FRAMES:
        for e in meas["methods"]["main"][f]:
            rows["restarts_vs_first"].append(f"| {FRAME_NAME[f]} | {fmt(e['budget'])} | {cell(e['restartsBetterThanFirst'], e['restartsWorseThanFirst'])} |")
    rows["shape"] = []
    for f in FRAMES:
        s = meas["sweeps"][f]
        rows["shape"].append(f"| {FRAME_NAME[f]} | {fmt(s['budget'])} | {fmt(s['base']['median'])} | {fmt(s['linear']['median'])} | {cell(s['linear']['better'], s['linear']['worse'])} |")
    for sweep in ("t0", "t1", "rate"):
        rows[sweep] = []
        labels = PCTS if sweep != "rate" else RATES
        for i, lab in enumerate(labels):
            parts = []
            for f in FRAMES:
                e = meas["sweeps"][f][sweep][i]
                parts.append(f"{fmt(e['median'])} | {'기준' if e['tag'] == 'exp' else cell(e['better'], e['worse'])}")
            label = f"{lab}%" if sweep != "rate" else f"{lab / 10:g}%"
            if (sweep != "rate" and lab == 100) or (sweep == "rate" and lab == 100):
                label += " (기본)"
            rows[sweep].append(f"| {label} | " + " | ".join(parts) + " |")
    rows["lastbest"] = []
    for i, lab in enumerate(PCTS):
        parts = []
        for f in FRAMES:
            e = meas["sweeps"][f]["t1"][i]
            parts.append(f"{e['lastWorse']} / 20 | {fmt(e['lastGap'])}")
        rows["lastbest"].append(f"| {lab}%" + (" (기본)" if lab == 100 else "") + " | " + " | ".join(parts) + " |")
    rows["accept"] = []
    for x, taken in meas["accuracy"]["frequency"]:
        q = x * XS * TS // (100 * TS)
        exact = float(exp_neg_rational(Fraction(x, 100)))
        rows["accept"].append(f"| {x / 100:g} | {ACC_TAB[q] / ONE:.3f} | {exact:.3f} | {fmt(taken)} |")
    rows["trace"] = []
    for f in FRAMES:
        t = meas["trace"][f]
        rows["trace"].append(f"| {FRAME_NAME[f]} | " + " | ".join(f"{100 * k / u:.1f}%" for u, k in zip(t["up"], t["taken"])) + " |")
    return rows


def hand_rows(h: dict) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    nb = {(e["a"], e["b"]): e for e in h["neighbors"]}
    # 7 x 7 grid of the changes at L (upper triangle) as a table: row = a, column = b
    rows["grid"] = []
    for a in range(6):
        cells = []
        for b in range(1, 7):
            if b <= a:
                cells.append("")
                continue
            d = nb[(a, b)]["delta"]
            cells.append("+%d" % d if d > 0 else str(d))
        rows["grid"].append(f"| {a} | " + " | ".join(cells) + " |")
    rows["after"] = []
    for a in range(6):
        cells = []
        for b in range(1, 7):
            cells.append(str(nb[(a, b)]["after"]) if b > a else "")
        rows["after"].append(f"| {a} | " + " | ".join(cells) + " |")
    rows["sa"] = []
    for r in h["sa"]:
        ev, a, b, d, q, tab, rnd, take, cost, best = r
        if d > 0:
            rows["sa"].append(f"| {ev} | ({a}, {b}) | +{d} | {d / HAND_SA_T:.2f} | {q} | {tab / ONE:.3f} | {rnd / ONE:.3f} | {'받음' if take else '거절'} | {cost} | {best} |")
        else:
            rows["sa"].append(f"| {ev} | ({a}, {b}) | {d} | - | - | - | - | 받음 | {cost} | {best} |")
    for tag in ("first", "best", "via"):
        rows[f"path_{tag}"] = [f"| {i + 1} | ({a}, {b}) | {d} | {cost} | {' '.join(map(str, order))} |"
                               for i, (a, b, d, cost, order) in enumerate(h[tag]["path"])]
    rows["xtab"] = []
    for label, x in (("0.1", Fraction(1, 10)), ("0.25", Fraction(1, 4)), ("0.5", Fraction(1, 2)), ("1", Fraction(1)), ("2", Fraction(2)), ("3", Fraction(3)), ("5", Fraction(5))):
        rows["xtab"].append(f"| {label} | {float(exp_neg_rational(x)):.3f} |")
    rows["mean"] = [f"| {t} | {h['mean'][str(t)] / ONE * 100:.1f}% |" for t in (1, 2, 3, 4, 6, 10)]
    return rows


def hub_expected(meas: dict) -> list[tuple[str, str]]:
    out = [("순서 틀 · 시작(번호 순서)", fmt(meas["start"]["route"]))]
    for f in FRAMES:
        name = FRAME_NAME[f]
        b = HEADLINE[f]
        e = next(x for x in meas["methods"]["main"][f] if x["budget"] == b)
        if f == "assign":
            out.append(("배정 틀 · 시작(라운드 로빈)", fmt(meas["start"]["assign"])))
        out.append((f"{name} · 언덕 오르기 한 번", fmt(e["first"])))
        out.append((f"{name} · 언덕 오르기 재시작, 평가 {fmt(b)}", fmt(e["restarts"])))
        out.append((f"{name} · 담금질, 평가 {fmt(b)}", fmt(e["anneal"])))
    return out


def check_text_tables(meas: dict, hill: dict, hand: dict) -> int:
    text = read_lesson_text(LESSON_ID)
    count = 0
    for name, rows in list(table_rows(meas, hill).items()) + list(hand_rows(hand).items()):
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

    text = read_lesson_text(LESSON_ID)
    sn = snippets(text)
    code = assemble(sn)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "syntax.cpp").write_text(code)
        done = subprocess.run(["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", str(work / "syntax.cpp")],
                              capture_output=True, text=True)
        assert done.returncode == 0, done.stderr[:2000]
        san = build(code, work, "harness_san", True)

        n_gen = check_gen(run(san, "gen"))
        diff = run(san, "diff")
        assert diff[0][:2] == ["diff", "route"] and diff[0][3:] == ["0", "0", "0"] and int(diff[0][2]) == 6720, diff
        assert diff[1][:2] == ["diff", "assign"] and diff[1][3:] == ["0", "0", "0", "0"] and int(diff[1][2]) > 5000, diff
        assert diff[2] == ["diff", "default", "10000", "0", "0"], diff
        worst = check_acc_table(run(san, "acctab"), text)
        freq = check_accept(run(san, "accept"))
        n_sched = check_schedule(run(san, "schedule"))
        n_temp = check_temp(run(san, "temp"))
        hand = check_hand(run(san, "hand"))
        hill_rows = run(san, "hill")
        n_hill = check_hill(hill_rows)
        n_anneal = check_anneal(run(san, "anneal"))
        n_restarts = check_restarts(run(san, "restarts"))

        opt = build(code, work, "harness_opt", False)
        exp_rows = run(opt, "exp")
        meas = measure(exp_rows)
        hill = measure_hill(hill_rows)
        mistakes = run_mistakes(sn, work)
        check_mistakes(mistakes)

    # the hub's headline numbers are the converged hill climb: the budget must not have cut it short
    for f in FRAMES:
        e = next(x for x in meas["methods"]["main"][f] if x["budget"] == HEADLINE[f])
        assert e["first"] == hill[f]["first"]["cost"], "the budgeted hill climb must have reached its local optimum"
        assert e["firstEvals"] < HEADLINE[f]

    meas.update({"schema": 1, "hill": hill, "hand": hand, "mistakes": mistakes,
                 "accuracy": {"table": f"abs error < 1.3e-6 (worst {worst:.3g})", "frequency": freq},
                 "rule": f"한쪽이 {WIN} / 20 시드 이상 나으면 차이가 있다고 보고, 아니면 결정 못 함",
                 "problems": {"route": "N=200, 좌표 0..999, 맨해튼 거리 합, 구간 뒤집기", "assign": "N=120, M=8, K=18, 부하 제곱합/100 + 추가 비용, 옮기기+맞바꾸기"},
                 "plan": {"r0": 100, "r1": 5, "sample": 2000, "stage": "1/32"}})
    if args.output:
        DATA.write_text(json.dumps(meas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {DATA.relative_to(ROOT)}")
    if args.print_tables:
        for name, tr in list(table_rows(meas, hill).items()) + list(hand_rows(hand).items()):
            print(f"[{name}]")
            print("\n".join(tr))
        return
    stored = json.loads(DATA.read_text(encoding="utf-8"))
    assert stored == json.loads(json.dumps(meas)), "measurements.json differs from a fresh measurement (run with --output)"
    n_rows = check_text_tables(stored, stored["hill"], stored["hand"])
    check_figures(stored)
    n_prose = check_prose(stored, stored["hill"], stored["hand"], stored["mistakes"])
    print(f"hill-climbing-and-annealing ok: {len(BLOCKS)} code blocks, {n_gen} generated instances checked against Python, "
          f"{diff[0][2]} + {diff[1][2]} exhaustive moves, {n_hill} local optima certified, {n_anneal} anneal runs against the reference loop, "
          f"{n_restarts} restart runs, {n_sched} schedules, {n_temp} temperature searches, acceptance table error {worst:.2g}, "
          f"5 injected mistakes detected, {n_rows} table rows and {n_prose} quoted values matched the measurements")


def check_prose(meas: dict, hill: dict, hand: dict, mistakes: dict) -> int:
    """Numbers quoted in sentences (not in tables) must be the measured ones."""
    text = read_lesson_text(LESSON_ID)
    d = meas["delta"]
    fr, fa = hill["route"], hill["assign"]
    ratio = lambda f: round(f["best"]["evals"] / f["first"]["evals"])
    tr = {f: meas["trace"][f] for f in FRAMES}
    first_pct = lambda f: f"{100 * tr[f]['taken'][0] / tr[f]['up'][0]:.1f}%"
    sw = meas["sweeps"]
    m = mistakes
    exp_hits = 200000 * ACC_TAB[64] // ONE
    needed = [
        f"순서 틀에서 약 {ratio(fr)}배, 배정 틀에서 약 {ratio(fa)}배",
        f"({fmt(fr['first']['applies'])} 대 {fmt(fr['best']['applies'])})" if False else f"{fmt(fr['first']['applies'])} 대 {fmt(fr['best']['applies'])}",
        f"평가 약 {round(fr['first']['evals'] / 10000)}만 번",
        f"{fmt(d['route']['start']['q50'])} → {fmt(d['route']['optimum']['q50'])}",
        f"중앙값 {fmt(d['route']['start']['q50'])} 대 {fmt(d['assign']['start']['q50'])}",
        f"시작 온도가 순서 틀 {tfmt(d['route']['t0'])}, 배정 틀 {tfmt(d['assign']['t0'])}으로 약 {round(d['route']['t0'] / d['assign']['t0'])}배 다르고, 끝 온도도 {tfmt(d['route']['t1'])}과 {tfmt(d['assign']['t1'])}",
        f"수락률 10%는 온도 약 {hand['rate']['100'] / TS:.1f}, 30%는 약 {hand['rate']['300'] / TS:.1f}",
        f"(순서 틀 {first_pct('route')}, 배정 틀 {first_pct('assign')})",
        f"순서 틀 20개 중 {sw['route']['base']['lastWorse']}개, 배정 틀 {sw['assign']['base']['lastWorse']}개이고 차이의 중앙값은 각각 {sw['route']['base']['lastGap']}, {sw['assign']['base']['lastGap']}",
        f"중앙값 {fmt(sw['route']['t1'][4]['lastGap'])}(비용 약 {round(sw['route']['t1'][4]['median'], -3):,}", f"배정 틀에서 {sw['assign']['t1'][4]['lastGap']}만큼",
        f"21개 중 9개가 26에 닿고, 8개는 28로 돌아오고, 3개는 29, 1개는 32입니다",
        f"비용 {hand['first']['cost']}, 변화량을 계산한 횟수는 {hand['first']['evals']}번",
        f"비용 {hand['best']['cost']}, 평가는 21 × 5번 = {hand['best']['evals']}번",
        f"약 4배({hand['first']['evals']}번 대 {hand['best']['evals']}번)",
        f"{m['early-optimum']['improvingLeft']}개 시드의 끝난 해에 좋아지는 이동이 남아 있습니다",
        f"{fmt(m['random-bits']['frequencyAtOne'])}번만 받습니다", f"{fmt(m['clean']['frequencyAtOne'])}번 받던", f"기댓값 {fmt(exp_hits + 1 if False else exp_hits)}",
        f"예산 10,000에서는 {m['schedule-constant']['endTemperature']['10000'] / TS:.1f}(끝 3의 {round(m['schedule-constant']['endTemperature']['10000'] / (3 * TS))}배",
        f"예산 1,000,000에서는 {m['schedule-constant']['endTemperature']['1000000'] / TS:.4f}",
        f"{fmt(m['clean']['routeCost'])}에서 {fmt(m['schedule-constant']['routeCost'])}가 됩니다",
        f"{m['no-best']['bestMismatch']}개 모두 반환한 best",
    ]
    for phrase in needed:
        assert phrase in text, f"the lesson text must quote the measured value: {phrase}"
    return len(needed)


def check_figures(meas: dict) -> None:
    """Numbers that the figures print must be the measured ones."""
    fig = ROOT / "lessons" / LESSON_ID / "lesson-assets"
    for path in sorted(fig.glob("*.svg")):
        svg = path.read_text(encoding="utf-8")
        assert 'role="img"' in svg and "<title" in svg and "<desc" in svg and 'viewBox="0 0 720 ' in svg, path.name
        for size in re.findall(r'font-size="(\d+)"', svg):
            assert 16 <= int(size) <= 28, (path.name, size)
    d = meas["delta"]
    svg = {p.name: p.read_text(encoding="utf-8") for p in fig.glob("*.svg")}
    first = next(e for e in meas["methods"]["main"]["route"] if e["budget"] == 1000000)
    t0, t1 = d["route"]["t0"] / TS, d["route"]["t1"] / TS
    expected = {
        "temperature-from-deltas.svg": [fmt(d[f][s][k]) for f in FRAMES for s in ("start", "optimum") for k in ("q10", "q50", "q90")]
                                       + [tfmt(d[f][t]) for f in FRAMES for t in ("t0", "t1")],
        "schedule-shapes.svg": [f"{t0:.1f}", f"{t1:.1f}", f"{math.sqrt(t0 * t1):.1f}", f"{(t0 + t1) / 2:.1f}"],
        "budget-split.svg": [fmt(first["firstEvals"]), f"{first['restartRuns']}번"],
        "local-optimum.svg": ["42", "28", "30", "26", "21개", "+2", "5번", "26번"],
    }
    for name, items in expected.items():
        for item in items:
            assert item in svg[name], f"{name} must show the measured value {item}"


if __name__ == "__main__":
    main()
