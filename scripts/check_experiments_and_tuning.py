"""Check the experiments-and-tuning lesson: code blocks, statistics against exact arithmetic, the annealing target against
an independent Python implementation, the experiments (paired comparison, multiple comparisons, hold-out, one-at-a-time
tuning, grid versus random search, transfer), the injected mistakes and the tables in the text.

What runs (about 40 s on 4 cores):
  * every code block is extracted, rejected if it uses a header / STL / dynamic allocation, assembled with the `array` and
    `random` library blocks and compiled header-free with -Wall -Wextra -Werror -fsyntax-only;
  * a harness (standard headers allowed there) including the lesson code runs under ASan/UBSan: input generators against
    independent Python generators, every proposal of short annealing runs against a full recomputation, the annealing result
    against a Python re-implementation (integers only, so platform independent), the statistics functions against
    math.comb and fractions, and a smoke run of the tuning code;
  * the experiments are run in an optimised build of the same code, summarised here and compared with
    lesson-assets/measurements.json and with the tables in the lesson text (a differing key is printed);
  * the probabilities in the text (binomial tails, ties, power, multiple comparisons) are computed here with fractions;
  * mistakes are injected into the statistics code and must be detected by known-answer checks (only "detected" is recorded).
--output writes measurements.json from a fresh run; --sync rewrites the tables in the text that are marked with
`<!-- check:table NAME -->`; --print-tables prints them.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpp_library import assemble_library, check_submission_code  # noqa: E402
from lesson_text import check_hub_summary, lesson_files, read_lesson_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LESSON_ID = "experiments-and-tuning"
DATA = ROOT / "lessons" / LESSON_ID / "lesson-assets" / "measurements.json"
HARNESS = ROOT / "scripts" / "experiments_and_tuning_harness.cpp"
SNIP_RE = re.compile(r"```cpp[^\n]*\bsnippet=([\w-]+)[^\n]*\n(.*?)\n```", re.S)
TABLE_RE = re.compile(r"<!-- check:table ([\w-]+) -->\n(\|[^\n]*\n\|[^\n]*\n)((?:\|[^\n]*\n?)+)")
BLOCKS = ("et-stats", "et-frame", "et-route", "et-assign", "et-gen", "et-run", "et-tune")
M64 = (1 << 64) - 1
M32 = (1 << 32) - 1
WIN = 15

NAMES = {"hot": "거의 0도 (1, 1)", "c0": "일정 온도 (128, 128)", "c1": "고른 설정 (256, 32)"}
HOT, C0, C1 = (1, 1, 0), (128, 128, 0), (256, 32, 0)
B_ROUTE, B_ASSIGN = 300000, 100000
FAIL_TARGET = 14000


def snippets() -> dict[str, str]:
    found: dict[str, str] = {}
    for name, code in SNIP_RE.findall(read_lesson_text(LESSON_ID)):
        assert name not in found, f"duplicate snippet {name}"
        check_submission_code(code, name)
        found[name] = code + "\n"
    assert set(BLOCKS) == set(found), f"snippets differ: {set(BLOCKS) ^ set(found)}"
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


def build(code: str, workdir: Path, name: str, flags: list[str]) -> Path:
    d = workdir / name
    d.mkdir()
    (d / "lesson.cpp").write_text(code)
    exe = d / "harness"
    done = subprocess.run(["c++", "-std=c++17", *flags, f"-I{d}", str(HARNESS), "-o", str(exe)], capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError(done.stderr[:3000])
    return exe


def run(exe: Path, mode: str) -> list[list[str]]:
    out = subprocess.run([str(exe), mode], check=True, capture_output=True, text=True, timeout=900).stdout
    return [line.split() for line in out.splitlines() if line.strip()]


# ------------------------------------------------------------------ independent references
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


def gen_route(seed: int, n: int = 200, family: int = 0):
    g = Gen(seed)
    px, py = [], []
    cx, cy = [], []
    if family == 1:
        for _ in range(8):
            cx.append(g.next(1000))
            cy.append(g.next(1000))
    for _ in range(n):
        if family == 0:
            px.append(g.next(1000))
            py.append(g.next(1000))
        else:
            c = g.next(8)
            x = cx[c] + g.next(101) - 50
            y = cy[c] + g.next(101) - 50
            px.append(min(max(x, 0), 999))
            py.append(min(max(y, 0), 999))
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


class HcRandom:
    def __init__(self, seed: int):
        self.s = seed & M32

    def next(self) -> int:
        self.s = (self.s * 1664525 + 1013904223) & M32
        return self.s


def pick(rng: HcRandom, bound: int) -> int:
    return (rng.next() * bound) >> 32


TS, XS, XMAX, ONE = 65536, 64, 1280, 1 << 30
ACC = [ONE]
for _q in range(1, XMAX + 1):
    ACC.append((ACC[-1] * 1057095000) >> 30)


def accept_worse(d: int, t: int, rng: HcRandom) -> bool:
    q = d * XS * TS // t
    r = rng.next() >> 2
    return q < XMAX and r < ACC[q]


def ref_anneal(cost_fn, propose, cfg, budget: int, rng: HcRandom, start: int):
    """Independent annealing loop: the schedule and the acceptance are re-implemented here; deltas are full recomputations."""
    t0, t1 = cfg[0] * TS // 8, cfg[1] * TS // 8
    t1 = t1 if t1 > 0 else 1
    stages, t = 0, t0
    while t > t1 and (t >> 5) > 0:
        stages += 1
        t -= t >> 5
    cur, stage = t0, 0
    best = cost = start
    for e in range(budget):
        s = e * stages // budget
        while stage < s:
            cur -= cur >> 5
            stage += 1
        mv = propose(rng)
        if mv is None:
            continue
        new_cost = mv()
        d = new_cost[0] - cost
        if d > 0 and not accept_worse(d, cur, rng):
            continue
        new_cost[1]()
        cost += d
        best = min(best, cost)
    return best


def ref_route_run(cfg, seed: int, n: int, budget: int) -> int:
    px, py = gen_route(seed, n)
    order = list(range(n))
    rng = HcRandom(seed)

    def propose(rng):
        a = pick(rng, n)
        b = pick(rng, n)
        ins = pick(rng, 100) < cfg[2]
        if a == b:
            return None
        if not ins and a > b:
            a, b = b, a
        q = order[:]
        if ins:
            x = q.pop(a)
            q.insert(b, x)
        else:
            q[a:b + 1] = q[a:b + 1][::-1]

        def commit():
            order[:] = q
        return lambda: (route_cost(px, py, q), commit)

    return ref_anneal(None, propose, cfg, budget, rng, route_cost(px, py, order))


def ref_assign_run(cfg, seed: int, budget: int) -> int:
    n, m, k = 120, 8, 18
    d, c = gen_assign(seed)
    a = [i % m for i in range(n)]
    rng = HcRandom(seed)

    def propose(rng):
        i = pick(rng, n)
        if pick(rng, 2) == 0:
            to = pick(rng, m)
            if to == a[i] or a.count(to) >= k:
                return None
            q = a[:]
            q[i] = to
        else:
            j = pick(rng, n)
            if a[i] == a[j]:
                return None
            q = a[:]
            q[i], q[j] = q[j], q[i]

        def commit():
            a[:] = q
        return lambda: (assign_cost(d, c, q), commit)

    return ref_anneal(None, propose, cfg, budget, rng, assign_cost(d, c, a))


# ------------------------------------------------------------------ exact statistics
def tail(n: int, k: int) -> int:
    return sum(math.comb(n, j) for j in range(k, n + 1))


def need_wins(n: int, den: int) -> int:
    for k in range(n // 2 + 1, n + 1):
        if 2 * tail(n, k) * den <= (1 << n):
            return k
    return n + 1


def dec(fr: Fraction, places: int = 4) -> str:
    """Round half up with integers; the digits are exact, independent of the platform."""
    scaled = (fr.numerator * 10 ** places * 2 + fr.denominator) // (2 * fr.denominator)
    s = str(scaled).rjust(places + 1, "0")
    return s[:-places] + "." + s[-places:]


def two_sided(n: int, k: int) -> Fraction:
    return Fraction(2 * tail(n, k), 1 << n)


def false_rate_with_ties(t: Fraction, n: int = 20, k: int = WIN) -> Fraction:
    total = Fraction(0)
    for j in range(n + 1):
        nn = n - j
        p_here = math.comb(n, j) * t ** j * (1 - t) ** nn
        if nn >= k:
            total += p_here * two_sided(nn, k)
    return total


def power(p: Fraction, n: int = 20, k: int = WIN) -> Fraction:
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(n + 1) if j >= k or n - j >= k)


def exact_tables() -> dict:
    out: dict = {}
    out["tails"] = [[k, tail(20, k), dec(Fraction(tail(20, k), 1 << 20)), dec(two_sided(20, k))] for k in range(12, 19)]
    out["need"] = [[n, need_wins(n, 20), dec(two_sided(n, need_wins(n, 20)))] for n in (9, 10, 15, 18, 19, 20, 25, 30, 40)]
    out["ties"] = [[f"{t.numerator}/{t.denominator}" if t else "0", dec(false_rate_with_ties(t))]
                   for t in (Fraction(0), Fraction(1, 10), Fraction(1, 4), Fraction(1, 2))]
    out["power"] = [[f"{p.numerator}/{p.denominator}", dec(power(p))] for p in (Fraction(6, 10), Fraction(7, 10), Fraction(8, 10), Fraction(9, 10))]
    alpha = two_sided(20, WIN)
    out["alpha"] = [alpha.numerator, alpha.denominator]
    out["multi"] = [[m, dec(1 - (1 - alpha) ** m), need_wins(20, 20 * m), dec(two_sided(20, need_wins(20, 20 * m)))] for m in (1, 2, 5, 10, 20, 40, 46)]
    pmf = [[j, math.comb(20, j)] for j in range(21)]
    out["pmf_half"] = pmf
    return out


# ------------------------------------------------------------------ checks against the harness
def check_gen(rows):
    seen = 0
    for kind, which, seed, h, cost, ref, lastprint in rows:
        seed = int(seed)
        if which in ("route0", "route1"):
            px, py = gen_route(seed, 200, int(which[-1]))
            assert int(h) == fnv(py, fnv(px)), f"{which} generator differs from the independent one"
            assert int(cost) == int(ref) == route_cost(px, py, list(range(200)))
            if which == "route0":
                assert int(lastprint) == int(h), "lastPrint differs from the input fingerprint"
        else:
            d, c = gen_assign(seed)
            hh = fnv(d)
            for row in c:
                hh = fnv(row, hh)
            assert int(h) == hh and int(lastprint) == hh, "assign generator or fingerprint differs from the independent one"
            assert int(cost) == int(ref) == assign_cost(d, c, [i % 8 for i in range(120)])
        seen += 1
    assert seen == 45
    return seen


def check_trace(rows):
    n = 0
    shorts = 0
    cfgs = [C0, C1, (64, 64, 50)]
    for r in rows:
        if r[0] == "trace":
            frame, seed, ci, lesson, check, mism = (int(x) for x in r[1:])
            assert mism == 0, f"delta or cost tracking differs from the full recomputation ({r})"
            assert lesson == check, f"anneal differs from the checking loop ({r})"
            ref = ref_route_run(cfgs[ci], seed, 60, 3000) if frame == 0 else ref_assign_run(cfgs[ci], seed, 3000)
            assert ref == lesson, f"anneal differs from the independent python implementation ({r}) python {ref}"
            n += 1
        elif r[0] == "short":
            seed, val = int(r[2]), int(r[3])
            ref = ref_route_run(C1, seed, 40, 2000) if r[1] == "route" else ref_assign_run(C1, seed, 2000)
            assert ref == val, f"short {r[1]} run differs from the python implementation: {val} vs {ref}"
            shorts += 1
    assert n == 24 and shorts == 6
    return n + shorts


def check_stats(rows):
    for r in rows:
        if r[0] == "tail":
            n = int(r[1])
            assert [int(x) for x in r[2:]] == [tail(n, k) for k in range(n + 1)], f"tailCount differs for n={n}"
        elif r[0] == "need":
            n = int(r[1])
            assert [int(x) for x in r[2:]] == [need_wins(n, d) for d in (20, 40, 100, 200, 400, 1000)], f"needWins differs for n={n}"
        elif r[0] == "pair":
            n, w, l, t = (int(x) for x in r[1:5])
            med, q1, q3 = (int(x) for x in r[5:8])
            vals = [int(x) for x in r[9:]]
            a, b = vals[0::2], vals[1::2]
            assert (w, l, t) == (sum(x < y for x, y in zip(a, b)), sum(x > y for x, y in zip(a, b)), sum(x == y for x, y in zip(a, b)))
            s = sorted(a)
            assert (med, q1, q3) == (s[(n + 1) // 2 - 1], s[(n + 3) // 4 - 1], s[(3 * n + 1) // 4 - 1])
        elif r[0] == "known":
            assert r[1:] == ["1", "2", "1"], r
        elif r[0] == "known2":
            assert r[1:] == [str(tail(20, 15)), "15", "16", "18"], r
        elif r[0] == "known3":
            assert r[1:] == ["1", "0", "1", "0"], r
    return len(rows)


# ------------------------------------------------------------------ measurements
def rank(v, r):
    return sorted(v)[r - 1]


def quart(v):
    n = len(v)
    return [rank(v, (n + 3) // 4), rank(v, (n + 1) // 2), rank(v, (3 * n + 1) // 4)]


def cmp3(a, b):
    """a better than b (smaller cost) / b better than a / equal."""
    return [sum(x < y for x, y in zip(a, b)), sum(x > y for x, y in zip(a, b)), sum(x == y for x, y in zip(a, b))]


def vd(c) -> str:
    return "더 좋음" if c[0] >= WIN else ("더 나쁨" if c[1] >= WIN else "결정 못 함")


def seeds_of(d, lo, hi):
    return [d[s] for s in range(lo, hi + 1)]


def measure(raw: dict) -> dict:
    m: dict = {"rule": f"한쪽이 {WIN} / 20 시드 이상 나으면 차이가 있다고 보고, 아니면 결정 못 함", "tuneSeeds": [1, 20], "confirmSeeds": [21, 40]}
    # ---- x1: what to measure
    rt: dict = {}
    asg: dict = {}
    for r in raw["x1"]:
        if r[1] == "route":
            rt.setdefault((int(r[2]), int(r[3])), {})[int(r[4])] = int(r[5])
        else:
            asg.setdefault((int(r[2]), int(r[3])), {})[int(r[4])] = [int(r[5]), int(r[6]), int(r[7])]
    names = ["hot", "c0", "c1"]
    curve = []
    for b in (30000, 100000, 300000, 1000000):
        v = [[rt[(ci, b)][s] for s in range(1, 21)] for ci in range(3)]
        entry = {"budget": b, "fail": [sum(x > FAIL_TARGET for x in v[ci]) for ci in range(3)]}
        for ci, nm in enumerate(names):
            entry[nm] = quart(v[ci])
        entry["c1VsHot"] = cmp3(v[2], v[0])
        curve.append(entry)
    m["curve"] = {"failTarget": FAIL_TARGET, "rows": curve}
    arows = []
    for ci, nm in ((0, "hot"), (2, "c1")):
        for b in (10000, 100000):
            v = asg[(ci, b)]
            costs = [v[s][0] for s in range(1, 21)]
            props = sum(v[s][1] for s in range(1, 21))
            blocked = sum(v[s][2] for s in range(1, 21))
            arows.append({"cfg": nm, "budget": b, "quart": quart(costs), "blockedPermille": (blocked * 1000 * 2 + props) // (2 * props), "props": props, "blocked": blocked})
    m["assignMetrics"] = arows
    # ---- x2: pairing
    A, B, PA, PB = {}, {}, {}, {}
    S: dict = {}
    for r in raw["x2"]:
        if r[1] == "A":
            A[int(r[2])], PA[int(r[2])] = int(r[3]), int(r[4])
        elif r[1] == "B":
            B[int(r[2])], PB[int(r[2])] = int(r[3]), int(r[4])
        else:
            S.setdefault(int(r[2]), {})[int(r[3])] = int(r[4])
    assert all(PA[s] == PB[s] for s in range(1, 21)), "A and B must see the same inputs"
    a20 = seeds_of(A, 1, 20)
    b20 = seeds_of(B, 1, 20)
    pairing = {"paired": cmp3(b20, a20), "shifts": []}
    for off in (20, 40, 60, 80):
        assert all(PB[s + off] != PA[s] for s in range(1, 21)), "shifted inputs must differ"
        pairing["shifts"].append({"offset": off, "cmp": cmp3(seeds_of(B, 1 + off, 20 + off), a20)})
    pairing["spread"] = {"inputsC1": quart(b20), "inputsC0": quart(a20),
                         "searchSeeds": [quart(list(S[i].values())) for i in (1, 2, 3)],
                         "diff": quart([x - y for x, y in zip(a20, b20)])}
    hand = [[s, A[s], B[s], A[s] - B[s]] for s in range(1, 7)]
    pairing["hand"] = hand
    # assign: HOT vs C1 at 100000, cyclic shifts inside the same 20 inputs
    h = [asg[(0, 100000)][s][0] for s in range(1, 21)]
    c = [asg[(2, 100000)][s][0] for s in range(1, 21)]
    pairing["assign"] = {"paired": cmp3(c, h), "shifts": [{"k": k, "cmp": cmp3(c[k:] + c[:k], h)} for k in (5, 10)],
                         "inputs": quart(h), "diff": quart([x - y for x, y in zip(c, h)]), "hot": h, "c1": c}
    m["pairing"] = pairing
    # ---- x3: 40 identical configurations compared with the same baseline
    X: dict = {}
    for r in raw["x3"]:
        X.setdefault(int(r[1]), {})[int(r[2])] = int(r[3])
    base_t, base_h = seeds_of(X[0], 1, 20), seeds_of(X[0], 21, 40)
    flagged = []
    for j in range(1, 41):
        ct = cmp3(seeds_of(X[j], 1, 20), base_t)
        if max(ct[0], ct[1]) >= WIN:
            flagged.append({"salt": j, "tune": ct, "confirm": cmp3(seeds_of(X[j], 21, 40), base_h)})
    m["salt"] = {"comparisons": 40, "flagged": flagged,
                 "sumWins": sum(cmp3(seeds_of(X[j], 1, 20), base_t)[0] for j in range(1, 41)),
                 "spreadWins": [min(cmp3(seeds_of(X[j], 1, 20), base_t)[0] for j in range(1, 41)), max(cmp3(seeds_of(X[j], 1, 20), base_t)[0] for j in range(1, 41))]}
    # ---- x5: interaction and one-at-a-time
    cfg: dict = {}
    for r in raw["x5"]:
        if r[1] == "cfg":
            cfg.setdefault((int(r[2]), int(r[3]), int(r[4])), {})[int(r[5])] = int(r[6])
    base = cfg[C0]
    inter = []
    for label, c_ in (("start", C0), ("t0x2", (256, 128, 0)), ("t1d4", (128, 32, 0)), ("both", C1)):
        v = cfg[c_]
        t = [v[s] for s in range(1, 21)]
        h = [v[s] for s in range(21, 41)]
        ct = cmp3(t, seeds_of(base, 1, 20))
        ch = cmp3(h, seeds_of(base, 21, 40))
        inter.append({"label": label, "cfg": list(c_), "tuneMedian": rank(t, 10), "tune": ct, "confirmMedian": rank(h, 10), "confirm": ch,
                      "all": [ct[0] + ch[0], ct[1] + ch[1], ct[2] + ch[2]]})
    m["interaction"] = inter
    singles = []
    for c_ in ((256, 128, 0), (64, 64, 0), (128, 64, 0), (128, 128, 25), (128, 32, 0), (512, 128, 0), (256, 64, 0), (256, 32, 0), (256, 16, 0), (512, 32, 0), (512, 16, 0)):
        v = cfg[c_]
        singles.append({"cfg": list(c_), "tune": cmp3(seeds_of(v, 1, 20), seeds_of(base, 1, 20)), "confirm": cmp3(seeds_of(v, 21, 40), seeds_of(base, 21, 40))})
    m["steps"] = singles
    paths: dict = {}
    for r in raw["x5"]:
        if r[1] == "step":
            need = int(r[2])
            paths.setdefault(need, {"steps": []})["steps"].append(
                {"step": int(r[3]), "from": [int(x) for x in r[4:7]], "bestWins": int(r[7]), "moved": bool(int(r[8])), "to": [int(x) for x in r[9:12]]})
        elif r[1] == "end":
            paths[int(r[2])]["end"] = [int(x) for x in r[3:6]]
    endc: dict = {}
    for r in raw["x5"]:
        if r[1] == "endcost":
            endc.setdefault(int(r[2]), {})[int(r[3])] = int(r[4])
    for need, p in paths.items():
        v = endc[need]
        p["tune"] = cmp3(seeds_of(v, 1, 20), seeds_of(base, 1, 20))
        p["confirm"] = cmp3(seeds_of(v, 21, 40), seeds_of(base, 21, 40))
        p["tuneMedian"], p["confirmMedian"] = rank(seeds_of(v, 1, 20), 10), rank(seeds_of(v, 21, 40), 10)
    m["paths"] = {str(k): v for k, v in sorted(paths.items())}
    # ---- x6: lattice, multiple comparisons, grid versus random
    lat: dict = {}
    draws = []
    for r in raw["x6"]:
        if r[0] == "x6":
            lat[(int(r[1]), int(r[2]))] = [int(x) for x in r[3:]]
        else:
            draws.append([int(x) for x in r[2:]])
    assert len(lat) == 46 and len(draws) == 40 and all(len(set(d)) == 9 for d in draws)
    t_c0, h_c0 = seeds_of(base, 1, 20), seeds_of(base, 21, 40)
    need46 = need_wins(20, 20 * len(lat))
    flag_t = [k for k, v in lat.items() if cmp3(v[:20], t_c0)[0] >= WIN]
    flag_t_strict = [k for k, v in lat.items() if cmp3(v[:20], t_c0)[0] >= need46]
    m["lattice"] = {"configs": len(lat), "strictNeed": need46,
                    "flagTune": len(flag_t), "flagTuneAlsoConfirm": sum(cmp3(lat[k][20:], h_c0)[0] >= WIN for k in flag_t),
                    "flagConfirm": sum(cmp3(v[20:], h_c0)[0] >= WIN for v in lat.values()),
                    "strictTune": len(flag_t_strict), "strictTuneAlsoConfirm": sum(cmp3(lat[k][20:], h_c0)[0] >= need46 for k in flag_t_strict)}
    order = sorted(lat, key=lambda k: (rank(lat[k][:20], 10), k))
    conf_order = sorted(lat, key=lambda k: (rank(lat[k][20:], 10), k))
    m["top"] = [{"cfg": list(k), "tune": rank(lat[k][:20], 10), "confirm": rank(lat[k][20:], 10), "confirmRank": conf_order.index(k) + 1} for k in order[:5]]
    m["bestOnConfirm"] = {"cfg": list(conf_order[0]), "confirm": rank(lat[conf_order[0]][20:], 10), "tune": rank(lat[conf_order[0]][:20], 10)}
    m["lattice"]["bestIsC1"] = order[0] == (C1[0], C1[1])
    ids = [(64 << i, 4 << j) for i in range(7) for j in range(7) if (4 << j) <= (64 << i)]
    grid = [(a, b) for a in (128, 512, 2048) for b in (8, 32, 128)]
    g = min(grid, key=lambda k: (rank(lat[k][:20], 10), grid.index(k)))
    rnd = []
    for d in draws:
        best = min(d, key=lambda i: (rank(lat[(64 << (i // 7), 4 << (i % 7))][:20], 10), d.index(i)))
        k = (64 << (best // 7), 4 << (best % 7))
        assert k in lat
        rnd.append((rank(lat[k][:20], 10), rank(lat[k][20:], 10), k))
    gc = rank(lat[g][20:], 10)
    m["gridRandom"] = {"grid": {"cfg": list(g), "tune": rank(lat[g][:20], 10), "confirm": gc},
                       "randomTuneMedian": rank([x[0] for x in rnd], 20), "randomConfirmMedian": rank([x[1] for x in rnd], 20),
                       "randomBetter": sum(x[1] < gc for x in rnd), "randomWorse": sum(x[1] > gc for x in rnd), "randomSame": sum(x[1] == gc for x in rnd),
                       "gridDistinct": [3, 3], "randomDistinctT1Median": rank([len({k[1] for k in [(64 << (i // 7), 4 << (i % 7)) for i in d]}) for d in draws], 20)}
    assert len(ids) == 46
    # ---- x7: transfer
    tr: dict = {}
    for r in raw["x7"]:
        tr.setdefault((int(r[1]), int(r[2])), {})[int(r[3])] = int(r[4])
    labels = ["확인 시드 21~40 (같은 입력 가족)", "점 100개", "점 400개", "점이 8개 뭉치에 모인 분포", "배정 틀 (예산 100,000)", "예산 100,000", "예산 1,000,000"]
    rows = []
    for cs in range(7):
        v = [[tr[(cs, ci)][s] for s in range(1, 21)] for ci in range(3)]
        rows.append({"case": labels[cs], "c0": rank(v[0], 10), "c1": rank(v[1], 10), "hot": rank(v[2], 10),
                     "c1VsC0": cmp3(v[1], v[0]), "c1VsHot": cmp3(v[1], v[2])})
    m["transfer"] = rows
    m["exact"] = exact_tables()
    return m


# ------------------------------------------------------------------ mistakes
MUTATIONS = {
    "direction": ("if (a[i] < b[i]) ++t.win; else if (a[i] > b[i]) ++t.lose;", "if (a[i] > b[i]) ++t.win; else if (a[i] < b[i]) ++t.lose;"),
    "tail": ("for (int j = k; j <= n; ++j) s += row[j];", "for (int j = k + 1; j <= n; ++j) s += row[j];"),
    "both-sides": ("2 * tailCount(n, k) * (unsigned long long)den", "tailCount(n, k) * (unsigned long long)den"),
    "prints": ("for (int i = 0; i < n; ++i) if (pa[i] != pb[i]) return false;", "for (int i = 0; i < n - 1; ++i) if (pa[i] != pb[i]) return false;"),
    "disjoint": ("firstA + nA <= firstB || firstB + nB <= firstA", "firstA + nA < firstB || firstB + nB < firstA"),
}
MUT_EXPECT = ["mut", "1", "2", "1", str(tail(20, 15)), "15", "16", "18", "0", "1", "0"]


# ------------------------------------------------------------------ tables in the text
def fmt(x) -> str:
    return f"{int(x):,}"


def pct1(permille: int) -> str:
    return f"{permille // 10}.{permille % 10}%"


def tables(meas: dict) -> dict[str, list[str]]:
    t: dict[str, list[str]] = {}
    ex = meas["exact"]
    t["curve"] = [f"| {fmt(e['budget'])} | {fmt(e['hot'][1])} | {fmt(e['c0'][1])} | {fmt(e['c1'][1])} | {fmt(e['c1'][0])} – {fmt(e['c1'][2])} | {e['c1VsHot'][0]} / {e['c1VsHot'][1]} {vd(e['c1VsHot'])} |"
                  for e in meas["curve"]["rows"]]
    t["fail"] = [f"| {fmt(e['budget'])} | {e['fail'][0]} / 20 | {e['fail'][1]} / 20 | {e['fail'][2]} / 20 |" for e in meas["curve"]["rows"]]
    t["assign-metrics"] = [f"| {fmt(e['budget'])} | {NAMES[e['cfg']]} | {fmt(e['quart'][0])} – {fmt(e['quart'][1])} – {fmt(e['quart'][2])} | {pct1(e['blockedPermille'])} |"
                           for e in meas["assignMetrics"]]
    p = meas["pairing"]
    t["pairing"] = [f"| 같은 입력끼리(짝지음) | 시드 1~20 대 시드 1~20 | {p['paired'][0]} / {p['paired'][1]} | {vd(p['paired'])} |"]
    for s in p["shifts"]:
        t["pairing"].append(f"| 다른 입력끼리(짝짓지 않음) | 고른 설정은 시드 {1 + s['offset']}~{20 + s['offset']} | {s['cmp'][0]} / {s['cmp'][1]} | {vd(s['cmp'])} |")
    a = p["assign"]
    t["pairing-assign"] = [f"| 같은 입력끼리(짝지음) | {a['paired'][0]} / {a['paired'][1]} | {vd(a['paired'])} |"]
    for s in a["shifts"]:
        t["pairing-assign"].append(f"| 입력을 {s['k']}칸 밀어서(짝짓지 않음) | {s['cmp'][0]} / {s['cmp'][1]} | {vd(s['cmp'])} |")
    sp = p["spread"]
    t["spread"] = [f"| 입력 20개(시드 1~20)에서 고른 설정의 비용 | {fmt(sp['inputsC1'][0])} | {fmt(sp['inputsC1'][1])} | {fmt(sp['inputsC1'][2])} |"]
    for i, q in enumerate(sp["searchSeeds"], 1):
        t["spread"].append(f"| 입력 시드 {i} 하나에서 탐색 시드 20개 | {fmt(q[0])} | {fmt(q[1])} | {fmt(q[2])} |")
    t["spread"].append(f"| 같은 시드끼리 두 설정의 차이(일정 온도 − 고른 설정) | {fmt(sp['diff'][0])} | {fmt(sp['diff'][1])} | {fmt(sp['diff'][2])} |")
    t["hand"] = [f"| {s} | {fmt(x)} | {fmt(y)} | {d:+,} | {'고른 설정' if d > 0 else ('일정 온도' if d < 0 else '같음')} |" for s, x, y, d in p["hand"]]
    t["tails"] = [f"| {k} | {fmt(c)} | {a} | {b} |" for k, c, a, b in ex["tails"]]
    t["need"] = [f"| {n} | {k} | {pp} |" for n, k, pp in ex["need"]]
    t["ties"] = [f"| {tt} | {v} |" for tt, v in ex["ties"]]
    t["power"] = [f"| {pp} | {v} |" for pp, v in ex["power"]]
    t["multi"] = [f"| {mm} | {a} | {k} / 20 | {b} |" for mm, a, k, b in ex["multi"]]
    s = meas["salt"]
    t["salt"] = [f"| {fl['salt']} | {fl['tune'][0]} / {fl['tune'][1]} | {fl['confirm'][0]} / {fl['confirm'][1]} |" for fl in s["flagged"]]
    lt = meas["lattice"]
    t["lattice"] = [f"| 15 / 20 규칙(15개 이상) | {lt['flagTune']} | {lt['flagTuneAlsoConfirm']} |",
                    f"| 비교 {lt['configs']}개에 맞춘 엄한 기준({lt['strictNeed']}개 이상) | {lt['strictTune']} | {lt['strictTuneAlsoConfirm']} |"]
    t["top"] = [f"| {i} | {tp['cfg'][0]} | {tp['cfg'][1]} | {fmt(tp['tune'])} | {fmt(tp['confirm'])} | {tp['confirmRank']} |" for i, tp in enumerate(meas["top"], 1)]
    t["interaction"] = []
    names = {"start": "시작(일정 온도)", "t0x2": "`t0`만 두 배", "t1d4": "`t1`만 1/4", "both": "둘 다(`t0` 두 배, `t1` 1/4)"}
    for e in meas["interaction"]:
        c = e["cfg"]
        if e["label"] == "start":
            t["interaction"].append(f"| {names[e['label']]} | {c[0]} | {c[1]} | {fmt(e['tuneMedian'])} | - | {fmt(e['confirmMedian'])} | - | - |")
        else:
            t["interaction"].append(f"| {names[e['label']]} | {c[0]} | {c[1]} | {fmt(e['tuneMedian'])} | {e['tune'][0]} / {e['tune'][1]} {vd(e['tune'])} | {fmt(e['confirmMedian'])} | {e['confirm'][0]} / {e['confirm'][1]} {vd(e['confirm'])} | {e['all'][0]} / {e['all'][1]} |")
    t["steps"] = [f"| {c['cfg'][0]} | {c['cfg'][1]} | {c['cfg'][2]} | {c['tune'][0]} / {c['tune'][1]} {vd(c['tune'])} | {c['confirm'][0]} / {c['confirm'][1]} {vd(c['confirm'])} |" for c in meas["steps"]]
    t["path11"] = []
    for st in meas["paths"]["11"]["steps"]:
        fr, to = st["from"], st["to"]
        t["path11"].append(f"| {st['step'] + 1} | {fr[0]} / {fr[1]} / {fr[2]} | {st['bestWins']} / 20 | {'옮김' if st['moved'] else '멈춤'} | {to[0]} / {to[1]} / {to[2]} |")
    pth = meas["paths"]
    t["paths"] = []
    for need in ("15", "11"):
        p_ = pth[need]
        e = p_["end"]
        t["paths"].append(f"| {need} / 20 | {len(p_['steps'])} | {e[0]} / {e[1]} / {e[2]} | {fmt(p_['tuneMedian'])} ({p_['tune'][0]} / {p_['tune'][1]} {vd(p_['tune'])}) | {fmt(p_['confirmMedian'])} ({p_['confirm'][0]} / {p_['confirm'][1]} {vd(p_['confirm'])}) |")
    gr = meas["gridRandom"]
    t["grid"] = [f"| 격자 3 × 3 | 9 | {gr['grid']['cfg'][0]} / {gr['grid']['cfg'][1]} | {fmt(gr['grid']['tune'])} | {fmt(gr['grid']['confirm'])} |",
                 f"| 무작위 9개(40번 반복의 중앙값) | 9 | 반복마다 다름 | {fmt(gr['randomTuneMedian'])} | {fmt(gr['randomConfirmMedian'])} |"]
    t["transfer"] = [f"| {r['case']} | {fmt(r['c0'])} | {fmt(r['c1'])} | {fmt(r['hot'])} | {r['c1VsC0'][0]} / {r['c1VsC0'][1]} {vd(r['c1VsC0'])} | {r['c1VsHot'][0]} / {r['c1VsHot'][1]} {vd(r['c1VsHot'])} |" for r in meas["transfer"]]
    return t


def hub_expected(meas: dict) -> list[tuple[str, str]]:
    i = {e["label"]: e for e in meas["interaction"]}
    return [("일정 온도 `t0 = t1 = 128`, 시드 1~20", fmt(i["start"]["tuneMedian"])),
            ("고른 설정 `t0 = 256, t1 = 32`, 시드 1~20", fmt(i["both"]["tuneMedian"])),
            ("일정 온도, 확인 시드 21~40", fmt(i["start"]["confirmMedian"])),
            ("고른 설정, 확인 시드 21~40", fmt(i["both"]["confirmMedian"]))]


def read_pages() -> dict[Path, str]:
    return {p: p.read_text(encoding="utf-8") for p in lesson_files(LESSON_ID)}


def sync_tables(tb: dict[str, list[str]]) -> int:
    n = 0
    for path, text in read_pages().items():
        def repl(match):
            nonlocal n
            name = match.group(1)
            assert name in tb, f"unknown table marker {name}"
            n += 1
            return f"<!-- check:table {name} -->\n{match.group(2)}" + "\n".join(tb[name]) + "\n"
        new = TABLE_RE.sub(repl, text)
        if new != text:
            path.write_text(new, encoding="utf-8")
    return n


def check_text_tables(tb: dict[str, list[str]]) -> int:
    seen: set[str] = set()
    n = 0
    for text in read_pages().values():
        for match in TABLE_RE.finditer(text):
            name = match.group(1)
            got = [ln for ln in match.group(3).splitlines() if ln.strip()]
            assert got == tb[name], f"table {name} in the text differs from the measurement\n got  {got}\n want {tb[name]}"
            seen.add(name)
            n += len(got)
    assert seen == set(tb), f"tables without a marker in the text: {set(tb) - seen}"
    return n


def quotes(meas: dict) -> list[str]:
    ex = meas["exact"]
    i = {e["label"]: e for e in meas["interaction"]}
    p = meas["pairing"]
    out = [fmt(i["start"]["tuneMedian"]), fmt(i["both"]["tuneMedian"]), fmt(i["both"]["confirmMedian"]),
           f"{i['both']['all'][0]} / {i['both']['all'][1]}", f"{i['t1d4']['all'][0]} / {i['t1d4']['all'][1]}", f"{i['t0x2']['all'][0]} / {i['t0x2']['all'][1]}",
           ex["multi"][4][1], ex["tails"][3][3], f"{p['paired'][0]} / {p['paired'][1]}",
           f"{fmt(meas['top'][0]['tune'])}", f"{fmt(meas['top'][0]['confirm'])}"]
    sp = p["spread"]
    widths = [q3 - q1 for q1, _, q3 in sp["searchSeeds"]]
    out += [f"{min(widths)}에서 {max(widths)}", f"({sp['inputsC1'][2] - sp['inputsC1'][0]})", f"{sp['diff'][0]}에서 {sp['diff'][2]}",
            f"{p['assign']['diff'][0]} – {p['assign']['diff'][1]} – {p['assign']['diff'][2]}",
            f"{p['assign']['shifts'][0]['cmp'][0]} / {p['assign']['shifts'][0]['cmp'][1]}", f"{p['assign']['shifts'][1]['cmp'][0]} / {p['assign']['shifts'][1]['cmp'][1]}"]
    be = meas["bestOnConfirm"]
    gr = meas["gridRandom"]
    out += [fmt(be["confirm"]), fmt(be["tune"]), f"{gr['randomBetter']}번", f"{gr['randomWorse']}번", f"{gr['randomSame']}번",
            f"중앙값 {gr['randomDistinctT1Median']}가지", fmt(gr["randomConfirmMedian"]), ex["multi"][5][1], ex["multi"][6][1],
            f"{i['start']['confirmMedian'] - i['start']['tuneMedian']} 올랐고 고른 설정은 {i['both']['confirmMedian'] - i['both']['tuneMedian']}"]
    s = meas["salt"]
    out += [f"{len(s['flagged'])}개", f"{s['spreadWins'][0]}에서 {s['spreadWins'][1]}", f"{s['flagged'][0]['confirm'][0]} / {s['flagged'][0]['confirm'][1]}"]
    pth = meas["paths"]
    out += [f"{pth['11']['confirm'][0]} / {pth['11']['confirm'][1]}", f"{pth['11']['steps'][0]['bestWins']} / 20", f"{pth['15']['steps'][0]['bestWins']} / 20"]
    for r in meas["transfer"]:
        out.append(f"{r['c1VsC0'][0]} / {r['c1VsC0'][1]}")
    return out


def check_quotes(meas: dict) -> int:
    text = read_lesson_text(LESSON_ID)
    q = quotes(meas)
    for frag in q:
        assert frag in text, f"quoted number missing or differs in the text: {frag}"
    for want in ("0.0414", "0.0207"):
        assert want in text, f"exact probability missing from the text: {want}"
    return len(q)


def diff(x, y, path, out):
    if len(out) >= 20:
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
    ap.add_argument("--sync", action="store_true", help="rewrite the marked tables in the text from a fresh run")
    ap.add_argument("--print-tables", action="store_true")
    args = ap.parse_args()

    sn = snippets()
    code = assemble(sn)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "syntax.cpp").write_text(code)
        done = subprocess.run(["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", str(work / "syntax.cpp")], capture_output=True, text=True)
        assert done.returncode == 0, done.stderr[:2000]
        san_flags = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
        with ThreadPoolExecutor(max_workers=8) as pool:
            f_san = pool.submit(build, code, work, "san", san_flags)
            f_opt = pool.submit(build, code, work, "opt", ["-O2"])
            f_mut = {name: pool.submit(build, assemble(sn, [edit]), work, f"mut_{name}", ["-O0"]) for name, edit in MUTATIONS.items()}
            san, opt = f_san.result(), f_opt.result()
            fut = {mode: pool.submit(run, opt, mode) for mode in ("x1", "x2", "x3", "x5", "x6", "x7")}
            f_checks = {mode: pool.submit(run, san, mode) for mode in ("gen", "trace", "stats", "smoke")}
            gen_rows = f_checks["gen"].result()
            n_gen = check_gen(gen_rows)
            n_trace = check_trace(f_checks["trace"].result())
            n_stats = check_stats(f_checks["stats"].result())
            smoke = f_checks["smoke"].result()
            assert len(smoke) == 1 and smoke[0][0] == "smoke" and smoke[0][5] == "46", smoke
            mutations = {}
            clean = run(opt, "mut")[0]
            assert clean == MUT_EXPECT, f"known-answer run differs: {clean}"
            for name, fu in f_mut.items():
                got = run(fu.result(), "mut")[0]
                assert got != MUT_EXPECT, f"mistake {name} was not detected"
                mutations[name] = "detected"
            raw = {mode: f.result() for mode, f in fut.items()}
        meas = measure(raw)
    meas["mistakes"] = mutations
    meas["schema"] = 1
    meas["problems"] = {"route": "N=200, 좌표 0..999, 맨해튼 거리 합, 평가 300,000", "assign": "N=120, M=8, K=18, 평가 100,000"}
    tb = tables(meas)
    if args.output:
        DATA.parent.mkdir(parents=True, exist_ok=True)
        DATA.write_text(json.dumps(meas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {DATA.relative_to(ROOT)}")
    if args.sync:
        print(f"synced {sync_tables(tb)} tables")
    if args.print_tables:
        for name, rows in tb.items():
            print(f"[{name}]")
            print("\n".join(rows))
        return
    stored = json.loads(DATA.read_text(encoding="utf-8"))
    fresh = json.loads(json.dumps(meas))
    if stored != fresh:
        out: list[str] = []
        diff(stored, fresh, "", out)
        print("\n".join(out))
        raise AssertionError("measurements.json differs from a fresh measurement (run with --output)")
    n_rows = check_text_tables(tb)
    n_hub = check_hub_summary(LESSON_ID, hub_expected(stored))
    n_quotes = check_quotes(stored)
    print(f"experiments-and-tuning ok: {len(BLOCKS)} code blocks, {n_gen} generated instances checked against Python, "
          f"{n_trace} annealing runs equal to the independent Python implementation, {n_stats} statistics rows recomputed exactly, "
          f"{len(mutations)} injected mistakes detected, {n_rows + n_hub} table rows and {n_quotes} quoted numbers matched the measurements")


if __name__ == "__main__":
    main()
