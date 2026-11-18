"""Check the SCHEDULX local-search lesson: extracted code, hand example, stored benchmark.

Without --judge only the checks that need no grader run: header-free composition,
every move/swap difference against a full recomputation (ASan/UBSan), the hand-example
table, a failing max-difference variant, and the stored benchmark against the lesson tables.
With --judge /path/to/SCHEDULX/main.cpp --output FILE the measurements are repeated and
FILE (normally lessons/assignment-local-search/lesson-assets/schedulx-benchmark.json) is written.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import re
import statistics
import subprocess
import tempfile

from cpp_library import check_submission_code, read_library_snippets
from lesson_text import check_hub_summary, read_lesson_text

ROOT = Path(__file__).resolve().parents[1]
LESSON_ID = "assignment-local-search"
ASSET = ROOT / "lessons/assignment-local-search/lesson-assets/schedulx-benchmark.json"
FIGURE = ROOT / "lessons/assignment-local-search/lesson-assets/hand-moves.svg"
MAX_TC = 6
SEGMENTS = 5
SEEDS = list(range(1, 10))
FACTORS = [0.03, 0.1, 0.3, 1.0, 3.0]
WEIGHTS = [0.0, 1.0, 2.0, 4.0, 8.0]

# Hand example: jobs 0..4, machines 0..1, processing_time[job][machine].
HAND_TIME = [[8, 9], [1, 3], [1, 5], [6, 9], [1, 6]]
HAND_START = [0, 1, 1, 0, 1]
HAND_PATH = [("move", 2, 0), ("swap", 0, 4), ("move", 1, 0)]


def snippet(name: str) -> str:
    found = re.findall(r"```cpp[^\n]*\bsnippet=" + re.escape(name) + r"\n(.*?)\n```", read_lesson_text(LESSON_ID), re.S)
    assert len(found) == 1, name
    return found[0] + "\n"


def sources() -> dict[str, str]:
    random = read_library_snippets()["random"]
    blocks = {name: snippet(name) for name in ("assign-baseline", "assign-plan", "assign-delta", "assign-anneal", "assign-entry")}
    for name, code in blocks.items():
        check_submission_code(code, name)
    common = "\n".join([random, blocks["assign-plan"], blocks["assign-delta"], blocks["assign-anneal"]])
    return {"baseline": blocks["assign-baseline"], "common": common, "final": common + "\n" + blocks["assign-entry"]}


# ---------------------------------------------------------------- hand example
def full_loads(assign: list[int], machines: int = 2) -> list[int]:
    loads = [0] * machines
    for job, machine in enumerate(assign):
        loads[machine] += HAND_TIME[job][machine]
    return loads


def hand_neighbors() -> list[tuple[str, list[int]]]:
    rows = []
    for job in range(len(HAND_START)):
        to = 1 - HAND_START[job]
        moved = list(HAND_START)
        moved[job] = to
        rows.append((f"작업 {job} → 기계 {to}", full_loads(moved)))
    for x, y in itertools.combinations(range(len(HAND_START)), 2):
        if HAND_START[x] != HAND_START[y]:
            swapped = list(HAND_START)
            swapped[x], swapped[y] = swapped[y], swapped[x]
            rows.append((f"작업 {x} ↔ 작업 {y}", full_loads(swapped)))
    return rows


def hand_table() -> str:
    lines = ["| 이웃 | 기계 0 부하 | 기계 1 부하 | 최대 부하 |", "| --- | ---: | ---: | ---: |"]
    lines.append(f"| 시작 상태 | {full_loads(HAND_START)[0]} | {full_loads(HAND_START)[1]} | {max(full_loads(HAND_START))} |")
    for label, loads in hand_neighbors():
        lines.append(f"| {label} | {loads[0]} | {loads[1]} | {max(loads)} |")
    return "\n".join(lines)


def hand_time_table() -> str:
    lines = ["| 작업 | 기계 0에서 | 기계 1에서 |", "| --- | ---: | ---: |"]
    for job, (a, b) in enumerate(HAND_TIME):
        lines.append(f"| {job} | {a} | {b} |")
    return "\n".join(lines)


def hand_facts() -> dict:
    start = max(full_loads(HAND_START))
    neighbors = hand_neighbors()
    assert min(max(loads) for _, loads in neighbors) > start
    # Brute force over every assignment.
    optimum = min(max(full_loads(list(a))) for a in itertools.product(range(2), repeat=len(HAND_START)))
    path = [list(HAND_START)]
    for kind, x, y in HAND_PATH:
        a = list(path[-1])
        if kind == "move":
            a[x] = y
        else:
            a[x], a[y] = a[y], a[x]
        path.append(a)
    return {"start": start, "optimum": optimum, "path": [max(full_loads(a)) for a in path],
            "equal": sum(1 for _, l in neighbors if max(l) == start), "count": len(neighbors)}


# ---------------------------------------------------------------- C++ harness
HARNESS = r'''
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <random>
#include <vector>

static const int HAND[5][MAX_MACHINE_COUNT] = {{8, 9}, {1, 3}, {1, 5}, {6, 9}, {1, 6}};
static int bigTime[4000][MAX_MACHINE_COUNT];

static long long fullMakespan(int n, int m, const int t[][MAX_MACHINE_COUNT], const int a[]) {
    long long load[MAX_MACHINE_COUNT] = {0};
    for (int j = 0; j < n; ++j) { assert(0 <= a[j] && a[j] < m); load[a[j]] += t[j][a[j]]; }
    long long best = 0;
    for (int k = 0; k < m; ++k) best = std::max(best, load[k]);
    return best;
}

static void sameAsRebuild(const sched::Plan& p) {
    sched::Plan q = p;
    q.rebuild();
    assert(q.total == p.total && q.makespan == p.makespan);
    for (int k = 0; k < p.m; ++k) assert(q.load[k] == p.load[k]);
    assert(p.makespan == fullMakespan(p.n, p.m, p.time, p.machine));
}

static void handExample() {
    sched::Plan p;
    p.n = 5; p.m = 2; p.time = HAND;
    int start[5] = {0, 1, 1, 0, 1};
    for (int j = 0; j < 5; ++j) p.machine[j] = start[j];
    p.rebuild();
    assert(p.load[0] == 14 && p.load[1] == 14 && p.makespan == 14 && p.total == 28);
    sched::Plan g = p;
    sched::greedy(g);
    for (int j = 0; j < 5; ++j) assert(g.machine[j] == start[j]);
    for (int j = 0; j < 5; ++j) {
        sched::Change c = sched::tryMove(p, j, 1 - start[j]);
        sched::Plan q = p;
        sched::Move mv = {0, j, 1 - start[j], c};
        sched::apply(q, mv);
        sameAsRebuild(q);
        assert(c.makespan == q.makespan);
        std::printf("HAND move %d %d %lld %lld\n", j, 1 - start[j], q.load[0], q.load[1]);
    }
    for (int x = 0; x < 5; ++x) for (int y = x + 1; y < 5; ++y) {
        if (start[x] == start[y]) continue;
        sched::Change c = sched::trySwap(p, x, y);
        sched::Plan q = p;
        sched::Move mv = {1, x, y, c};
        sched::apply(q, mv);
        sameAsRebuild(q);
        assert(c.makespan == q.makespan);
        std::printf("HAND swap %d %d %lld %lld\n", x, y, q.load[0], q.load[1]);
    }
    sched::Move one = {0, 2, 0, sched::tryMove(p, 2, 0)};
    sched::apply(p, one);
    assert(p.makespan == 15 && p.load[0] == 15 && p.load[1] == 9);
    sched::Move two = {1, 0, 4, sched::trySwap(p, 0, 4)};
    sched::apply(p, two);
    assert(p.makespan == 12 && p.load[0] == 8 && p.load[1] == 12);
    sched::Move three = {0, 1, 0, sched::tryMove(p, 1, 0)};
    sched::apply(p, three);
    assert(p.makespan == 9 && p.load[0] == 9 && p.load[1] == 9);
    sameAsRebuild(p);
}

static void randomInstance(std::mt19937& rng, int n, int m, int top) {
    for (int j = 0; j < n; ++j) for (int k = 0; k < m; ++k) bigTime[j][k] = 1 + (int)(rng() % top);
}

static void stress() {
    std::mt19937 rng(20261118);
    const int tops[] = {3, 50, 1000000000};
    for (int trial = 0; trial < 300; ++trial) {
        int n = 2 + (int)(rng() % 30), m = 2 + (int)(rng() % 7);
        randomInstance(rng, n, m, tops[trial % 3]);
        sched::Plan p;
        p.n = n; p.m = m; p.time = bigTime;
        for (int j = 0; j < n; ++j) p.machine[j] = (int)(rng() % m);
        p.rebuild();
        sameAsRebuild(p);
        // Every move and swap difference against the full recomputation.
        for (int j = 0; j < n; ++j) for (int to = 0; to < m; ++to) {
            if (to == p.machine[j]) continue;
            sched::Change c = sched::tryMove(p, j, to);
            sched::Plan q = p;
            q.machine[j] = to;
            q.rebuild();
            assert(c.makespan == q.makespan && c.total == q.total);
        }
        for (int x = 0; x < n; ++x) for (int y = x + 1; y < n; ++y) {
            if (p.machine[x] == p.machine[y]) continue;
            sched::Change c = sched::trySwap(p, x, y);
            sched::Plan q = p;
            std::swap(q.machine[x], q.machine[y]);
            q.rebuild();
            assert(c.makespan == q.makespan && c.total == q.total);
        }
        // Applying proposals keeps the cached values equal to a rebuild.
        hc::Random r;
        r.reset(trial + 1u);
        for (int step = 0; step < 200; ++step) {
            sched::Move mv = sched::propose(p, r, 50);
            if (mv.kind == 1) assert(p.machine[mv.x] != p.machine[mv.y]);
            else assert(mv.y != p.machine[mv.x] && 0 <= mv.y && mv.y < m);
            sched::apply(p, mv);
            sameAsRebuild(p);
        }
    }
}

static void annealing() {
    std::mt19937 rng(20261119);
    for (int trial = 0; trial < 120; ++trial) {
        int n = trial < 3 ? trial : 2 + (int)(rng() % 40);
        int m = trial % 5 == 0 ? 1 : 2 + (int)(rng() % 6);
        if (n == 0) n = 1;
        randomInstance(rng, n, m, trial % 2 ? 40 : 100000);
        sched::Plan base;
        base.n = n; base.m = m; base.time = bigTime;
        sched::greedy(base);
        sameAsRebuild(base);
        for (long long attempts : {0LL, 1LL, 600LL}) for (double hot : {0.0, 30.0}) for (double weight : {0.0, 2.0}) {
            sched::Params prm = {attempts, (unsigned)rng(), hot, hot / 50.0, weight, 50};
            sched::Plan a = base, b = base;
            int bestA[4000], bestB[4000];
            sched::Stats sa = sched::anneal(a, prm, bestA);
            sched::Stats sb = sched::anneal(b, prm, bestB);
            assert(sa.bestMakespan == sb.bestMakespan);
            for (int j = 0; j < n; ++j) assert(bestA[j] == bestB[j]);
            sameAsRebuild(a);
            assert(fullMakespan(n, m, bigTime, bestA) == sa.bestMakespan);
            assert(sa.bestMakespan <= base.makespan && sa.bestMakespan <= a.makespan);
            assert(sa.initialMakespan == base.makespan);
            long long worse = 0;
            for (int s = 0; s < sched::SEGMENTS; ++s) {
                worse += sa.acceptedWorse[s];
                assert(sa.acceptedWorse[s] <= sa.proposedWorse[s]);
            }
            if (hot == 0.0) assert(worse == 0);
            if (n < 2 || m < 2 || attempts == 0) {
                for (int j = 0; j < n; ++j) assert(bestA[j] == base.machine[j]);
            }
        }
        double l1 = sched::medianLoss(base, 7u, 500, 2.0, 50);
        sched::Plan before = base;
        double l2 = sched::medianLoss(base, 7u, 500, 2.0, 50);
        assert(l1 == l2 && l1 > 0.0);
        for (int j = 0; j < n; ++j) assert(before.machine[j] == base.machine[j]);
        sameAsRebuild(base);
    }
    for (int i = 0; i <= 3200; ++i) {
        double x = i / 100.0, v = sched::expNegative(x);
        assert(0.0 <= v && v <= 1.0 && std::abs(v - std::exp(-x)) < 1e-11);
    }
}

static void entry() {
    std::mt19937 rng(20261120);
    const int shapes[][2] = {{1, 1}, {1, 2}, {2, 1}, {7, 3}, {60, 6}};
    for (auto shape : shapes) {
        int n = shape[0], m = shape[1];
        randomInstance(rng, n, m, 500);
        int a[4000];
        for (int j = 0; j < n; ++j) a[j] = -1;
        schedule_jobs(n, m, bigTime, a);
        sched::Plan g;
        g.n = n; g.m = m; g.time = bigTime;
        sched::greedy(g);
        assert(fullMakespan(n, m, bigTime, a) <= g.makespan);
    }
}

int main() {
    handExample();
    stress();
    annealing();
    entry();
    std::puts("HARNESS OK");
}
'''

# Experiment entry used only for measurements; the lesson's own entry is built separately.
EXP_ENTRY = r'''
#include <stdio.h>
#include <stdlib.h>
static double envNumber(const char* key, double fallback) {
    const char* v = getenv(key);
    return v ? atof(v) : fallback;
}
void schedule_jobs(int job_count, int machine_count, const int processing_time[][MAX_MACHINE_COUNT], int assignment[]) {
    sched::Plan plan;
    plan.n = job_count; plan.m = machine_count; plan.time = processing_time;
    sched::greedy(plan);
    long long greedyMakespan = plan.makespan;
    {   // Share of 2000 proposals from the greedy start that leave the real score unchanged / lower it.
        hc::Random probe;
        probe.reset(1u);
        int same = 0, lower = 0;
        for (int i = 0; i < 2000; ++i) {
            sched::Move mv = sched::propose(plan, probe, 50);
            if (mv.after.makespan == plan.makespan) ++same;
            else if (mv.after.makespan < plan.makespan) ++lower;
        }
        fprintf(stderr, "PLATEAU %d %d %d\n", job_count, same, lower);
    }
    int mode = (int)envNumber("MODE", 2);  // 0 greedy, 1 hill climbing, 2 SA
    double weight = envNumber("WEIGHT", 2.0);
    int swapPercent = (int)envNumber("SWAP", 50);
    double factor = envNumber("FACTOR", 0.1), ratio = envNumber("RATIO", 0.02);
    unsigned seed = (unsigned)envNumber("SEED", 20261118);
    sched::Params prm;
    prm.attempts = (long long)envNumber("ATTEMPTS", 2000000);
    prm.seed = seed; prm.weight = weight; prm.swapPercent = swapPercent;
    prm.startTemp = prm.endTemp = 0.0;
    if (mode == 2) {
        double loss = sched::medianLoss(plan, seed ^ 0x5bd1e995u, 2000, weight, swapPercent);
        fprintf(stderr, "LOSS %d %.3f\n", job_count, loss);
        prm.startTemp = factor * loss;
        prm.endTemp = ratio * prm.startTemp;
    }
    sched::Stats st;
    if (mode == 0) {
        for (int s = 0; s < sched::SEGMENTS; ++s) st.proposedWorse[s] = st.acceptedWorse[s] = st.acceptedOther[s] = 0;
        st.bestMakespan = greedyMakespan;
        for (int j = 0; j < job_count; ++j) assignment[j] = plan.machine[j];
    } else {
        st = sched::anneal(plan, prm, assignment);
    }
    fprintf(stderr, "EXP %d %lld %lld", job_count, greedyMakespan, st.bestMakespan);
    for (int s = 0; s < sched::SEGMENTS; ++s) fprintf(stderr, " %lld %lld", st.proposedWorse[s], st.acceptedWorse[s]);
    fprintf(stderr, "\n");
}
'''

# Own instances (not the judge's generator): 3 machine types, heavy-tailed sizes.
OWN_MAIN = r'''
#include <random>
static int ownTime[4000][MAX_MACHINE_COUNT];
static int ownAssign[4000];
int main() {
    const int jobs[6] = {150, 300, 700, 1200, 2000, 3500};
    const int machines[6] = {5, 7, 9, 11, 14, 18};
    long long total = 0;
    for (int tc = 0; tc < 6; ++tc) {
        std::mt19937 rng(777 + tc);
        int n = jobs[tc], m = machines[tc];
        int speed[MAX_MACHINE_COUNT];
        for (int k = 0; k < m; ++k) speed[k] = 70 + (int)(rng() % 71);
        for (int j = 0; j < n; ++j) {
            int pref = (int)(rng() % 3);
            double u = (rng() % 10000) / 10000.0;
            int base = 20 + (int)(1400.0 * u * u * u);
            for (int k = 0; k < m; ++k) {
                int gap = (k % 3 - pref + 3) % 3;  // 0, 1, 2
                int factor = gap == 0 ? 100 : (gap == 1 ? 140 : 210);
                ownTime[j][k] = (base * factor) / speed[k] + 3 + (int)(rng() % 25);
            }
        }
        schedule_jobs(n, m, ownTime, ownAssign);
        long long load[MAX_MACHINE_COUNT] = {0}, best = 0;
        for (int j = 0; j < n; ++j) load[ownAssign[j]] += ownTime[j][ownAssign[j]];
        for (int k = 0; k < m; ++k) if (load[k] > best) best = load[k];
        total += best;
    }
    printf("OWN %lld\n", total);
}
'''

BUGGY_FINISH = '''static Change finish(const Plan& p, int a, int b, long long newA, long long newB, long long newTotal) {
    long long best = newA > newB ? newA : newB;
    if (p.makespan > best) best = p.makespan;  // 나머지 기계 최댓값 대신 옛 최댓값을 쓴다.
    Change c = {best, newTotal};
    return c;
}'''


def compile_run(code: str, flags: list[str], extra: list[str] | None = None, expect_ok: bool = True, timeout: int = 180):
    with tempfile.TemporaryDirectory(prefix="lesson-assign-") as folder:
        src = Path(folder) / "check.cpp"
        exe = Path(folder) / "check"
        src.write_text(code)
        subprocess.run(["c++", "-std=c++17", *flags, str(src), "-o", str(exe)], check=True)
        result = subprocess.run([str(exe)], capture_output=True, text=True, timeout=timeout)
    if expect_ok:
        assert result.returncode == 0, result.stderr[-2000:]
    return result


def function_text(code: str, name: str) -> str:
    start = code.index(f"static Change {name}(")
    end = code.index("\n}\n", start) + 3
    return code[start:end].rstrip("\n")


def run_checks(values: dict[str, str]) -> dict:
    sanitize = ["-O1", "-g", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
    result = compile_run(values["final"] + "\n" + HARNESS, sanitize)
    assert "HARNESS OK" in result.stdout
    facts = hand_facts()
    assert facts["start"] == 14 and facts["path"] == [14, 15, 12, 9] and facts["optimum"] == 9, facts
    expected = {}
    for label, loads in hand_neighbors():
        key = re.sub(r"작업 (\d+) → 기계 (\d+)", r"move \1 \2", label)
        key = re.sub(r"작업 (\d+) ↔ 작업 (\d+)", r"swap \1 \2", key)
        expected[key] = f"{loads[0]} {loads[1]}"
    printed = {}
    for line in result.stdout.splitlines():
        if line.startswith("HAND "):
            _, kind, a, b, l0, l1 = line.split()
            printed[f"{kind} {a} {b}"] = f"{l0} {l1}"
    assert printed == expected, (printed, expected)
    # The wrong max difference must be caught by the same harness.
    finish = function_text(values["final"], "finish")
    assert BUGGY_FINISH.splitlines()[2] in read_lesson_text(LESSON_ID) and "나머지 기계 최댓값 대신" in read_lesson_text(LESSON_ID)
    buggy = values["final"].replace(finish, BUGGY_FINISH)
    assert buggy != values["final"]
    caught = compile_run(buggy + "\n" + HARNESS, sanitize, expect_ok=False)
    assert caught.returncode != 0, "buggy max difference was not detected"
    print("OK: composition, every move/swap difference, hand example (14 -> 15 -> 12 -> 9), SA best/current, buggy max difference detected (ASan/UBSan)")
    return facts


# ---------------------------------------------------------------- benchmark
def build_judge(judge_text: str, user_code: str, folder: Path, name: str) -> Path:
    assert judge_text.count("int main(void)") == 1
    driver = ("#include <chrono>\n#include <stdlib.h>\n" + judge_text.replace("int main(void)", "int judge_run(void)") + r'''
int main() {
    const char* r = getenv("ROUNDS");
    int rounds = r ? atoi(r) : 1;
    for (int run = 0; run < rounds; ++run) {
        auto start = std::chrono::steady_clock::now();
        judge_run();
        auto end = std::chrono::steady_clock::now();
        fprintf(stderr, "BENCH %.6f\n", std::chrono::duration<double, std::milli>(end - start).count());
    }
}
''')
    (folder / f"{name}-judge.cpp").write_text(driver)
    (folder / f"{name}-user.cpp").write_text(user_code)
    exe = folder / name
    subprocess.run(["c++", "-std=c++17", "-O2", str(folder / f"{name}-judge.cpp"), str(folder / f"{name}-user.cpp"), "-o", str(exe)], check=True)
    return exe


def run_judge(exe: Path, env: dict[str, str], rounds: int = 1) -> dict:
    full = dict(os.environ, ROUNDS=str(rounds), **env)
    r = subprocess.run([str(exe)], capture_output=True, text=True, env=full, timeout=300, check=True)
    totals = [int(v) for v in re.findall(r"^SCORE: (\d+)$", r.stdout, re.M)]
    cases = [int(v) for v in re.findall(r"^TC \d+ SCORE: (\d+)$", r.stdout, re.M)]
    assert len(totals) == rounds and len(cases) == MAX_TC * rounds and max(cases) < 10**12
    assert len(set(totals)) == 1 and all(cases[i:i + MAX_TC] == cases[:MAX_TC] for i in range(0, len(cases), MAX_TC))
    times = [float(v) for v in re.findall(r"BENCH ([\d.]+)", r.stderr)]
    exp = []
    for line in r.stderr.splitlines():
        if line.startswith("EXP "):
            f = [int(v) for v in line.split()[1:]]
            exp.append({"n": f[0], "greedy": f[1], "best": f[2], "proposed_worse": f[3::2][:SEGMENTS], "accepted_worse": f[4::2][:SEGMENTS]})
    exp = exp[:MAX_TC]
    plateau = [[int(v) for v in line.split()[1:]] for line in r.stderr.splitlines() if line.startswith("PLATEAU ")][:MAX_TC]
    loss = [float(line.split()[2]) for line in r.stderr.splitlines() if line.startswith("LOSS ")][:MAX_TC]
    return {"total": totals[0], "costs": cases[:MAX_TC], "times": times, "exp": exp, "plateau": plateau, "loss": loss}


def median(values):
    return statistics.median(values)


def benchmark(values: dict[str, str], judge: Path, output: Path) -> None:
    judge_text = judge.read_text()
    exp_code = values["common"] + "\n" + EXP_ENTRY
    data: dict = {
        "judge_sha256": hashlib.sha256(judge.read_bytes()).hexdigest(),
        "measured_at": datetime.date.today().isoformat(),
        "environment": f"{platform.system()} {platform.mac_ver()[0]} {platform.machine()} / "
                       + subprocess.run(["c++", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
                       + " / -std=c++17 -O2",
        "attempts": 2000000, "swap_percent": 50, "weight": 2.0, "start_factor": 0.1, "end_ratio": 0.02,
        "timing_rounds": 9, "warmup_rounds": 1, "seeds": SEEDS,
    }
    with tempfile.TemporaryDirectory(prefix="lesson-assign-bench-") as folder_name:
        folder = Path(folder_name)
        exp = build_judge(judge_text, "#define MAX_MACHINE_COUNT 20\n" + "\n".join(
            line for line in exp_code.splitlines() if line.strip() != "#define MAX_MACHINE_COUNT 20"), folder, "exp")
        final = build_judge(judge_text, values["final"], folder, "final")
        base = build_judge(judge_text, values["baseline"], folder, "base")
        stage_defs = [
            ("baseline", "작업 번호 % 기계 수", base, {}),
            ("greedy", "탐욕 초기해", exp, {"MODE": "0"}),
            ("hill-0", "hill climbing, 실제 점수만", exp, {"MODE": "1", "WEIGHT": "0"}),
            ("hill-2", "hill climbing, 평균 부하 항 포함", exp, {"MODE": "1", "WEIGHT": "2"}),
            ("sa-0", "SA, 실제 점수만", exp, {"MODE": "2", "WEIGHT": "0"}),
            ("sa-2", "SA, 평균 부하 항 포함", exp, {"MODE": "2", "WEIGHT": "2"}),
            ("final", "본문 제출 코드", final, {}),
        ]
        stages = []
        for key, label, exe, env in stage_defs:
            r = run_judge(exe, env, rounds=9)
            row = {"key": key, "label": label, "total": r["total"], "costs": r["costs"],
                   "median_ms": median(r["times"][1:]), "runs_ms": r["times"][1:]}
            if r["loss"]:
                row["median_loss"] = r["loss"]
            stages.append(row)
            print(json.dumps({k: row[k] for k in ("key", "total", "median_ms")}), flush=True)
        by = {s["key"]: s for s in stages}
        assert by["final"]["costs"] == by["sa-2"]["costs"], "experiment entry differs from the lesson entry"
        data["stages"] = stages

        temps = []
        for factor in [0.0] + FACTORS:
            runs = []
            for seed in SEEDS:
                env = {"SEED": str(seed), "WEIGHT": "2"}
                env.update({"MODE": "1"} if factor == 0.0 else {"MODE": "2", "FACTOR": str(factor)})
                r = run_judge(exp, env)
                prop = [sum(e["proposed_worse"][s] for e in r["exp"]) for s in range(SEGMENTS)]
                acc = [sum(e["accepted_worse"][s] for e in r["exp"]) for s in range(SEGMENTS)]
                runs.append({"seed": seed, "total": r["total"], "costs": r["costs"], "proposed_worse": prop, "accepted_worse": acc})
            rates = [median([run["accepted_worse"][s] / run["proposed_worse"][s] if run["proposed_worse"][s] else 0.0 for run in runs])
                     for s in range(SEGMENTS)]
            temps.append({"factor": factor, "median_total": median([r["total"] for r in runs]),
                          "min_total": min(r["total"] for r in runs), "max_total": max(r["total"] for r in runs),
                          "median_costs": [median([r["costs"][t] for r in runs]) for t in range(MAX_TC)],
                          "worse_accept_rate": rates, "runs": runs})
            print(json.dumps({k: temps[-1][k] for k in ("factor", "median_total", "min_total", "max_total", "worse_accept_rate")}), flush=True)
        data["temperatures"] = temps

        weights = []
        for weight in WEIGHTS:
            totals = [run_judge(exp, {"SEED": str(seed), "WEIGHT": str(weight), "MODE": "2"})["total"] for seed in SEEDS]
            weights.append({"weight": weight, "median_total": median(totals), "min_total": min(totals), "max_total": max(totals), "totals": totals})
            print(json.dumps({k: weights[-1][k] for k in ("weight", "median_total")}), flush=True)
        data["weights"] = weights
        probe = run_judge(exp, {"MODE": "0"})["plateau"]
        data["plateau"] = [{"n": n, "same_makespan": same, "lower_makespan": lower, "proposals": 2000} for n, same, lower in probe]
        print(json.dumps(data["plateau"]), flush=True)

        # A wrong max difference: the cached makespan never goes down, so best never updates.
        finish = function_text(values["final"], "finish")
        buggy = build_judge(judge_text, values["final"].replace(finish, BUGGY_FINISH), folder, "buggy")
        r = run_judge(buggy, {})
        data["buggy_max"] = {"total": r["total"], "costs": r["costs"]}

        # Own instances, same code and parameters, not used for choosing them.
        own = []
        for mode, label in (("0", "탐욕 초기해"), ("1", "hill climbing"), ("2", "SA")):
            totals = []
            for seed in range(1, 6):
                code = ("#define MAX_MACHINE_COUNT 20\n#include <stdio.h>\n" + "\n".join(
                    line for line in exp_code.splitlines() if line.strip() != "#define MAX_MACHINE_COUNT 20") + OWN_MAIN)
                src = folder / "own.cpp"
                src.write_text(code)
                subprocess.run(["c++", "-std=c++17", "-O2", str(src), "-o", str(folder / "own")], check=True)
                out = subprocess.run([str(folder / "own")], capture_output=True, text=True, check=True, timeout=120,
                                     env=dict(os.environ, MODE=mode, SEED=str(seed), WEIGHT="2"))
                totals.append(int(re.search(r"^OWN (\d+)$", out.stdout, re.M).group(1)))
            own.append({"mode": mode, "label": label, "totals": totals, "median_total": median(totals)})
            print(json.dumps(own[-1]), flush=True)
        data["own_instances"] = own
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


# ---------------------------------------------------------------- tables
def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def stage_table(data: dict) -> str:
    greedy = next(s for s in data["stages"] if s["key"] == "greedy")["total"]
    lines = ["| 방식 | TC 1 | TC 2 | TC 3 | TC 4 | TC 5 | TC 6 | 합 ↓ | 탐욕 대비 | 시간(ms) |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for s in data["stages"]:
        if s["key"] == "final":
            continue
        cost = " | ".join(str(c) for c in s["costs"])
        diff = "-" if s["key"] in ("baseline", "greedy") else f"{100 * (s['total'] - greedy) / greedy:+.1f}%"
        lines.append(f"| {s['label']} | {cost} | {s['total']} | {diff} | {s['median_ms']:.1f} |")
    return "\n".join(lines)


def temp_table(data: dict) -> str:
    lines = ["| 시작 온도 | 합의 중앙값 ↓ | 최소~최대 | 구간 1 | 구간 2 | 구간 3 | 구간 4 | 구간 5 |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for t in data["temperatures"]:
        label = "0 (나쁜 이동 거절)" if t["factor"] == 0.0 else f"중앙 손해의 {t['factor']:g}배"
        rates = " | ".join("-" if t["factor"] == 0.0 else pct(r) for r in t["worse_accept_rate"])
        lines.append(f"| {label} | {t['median_total']:.0f} | {t['min_total']}~{t['max_total']} | {rates} |")
    return "\n".join(lines)


def weight_table(data: dict) -> str:
    lines = ["| 평균 부하 항 가중치 | 합의 중앙값 ↓ | 최소~최대 |", "| ---: | ---: | ---: |"]
    for w in data["weights"]:
        lines.append(f"| {w['weight']:g} | {w['median_total']:.0f} | {w['min_total']}~{w['max_total']} |")
    return "\n".join(lines)


def own_table(data: dict) -> str:
    lines = ["| 방식 | 6개 입력 비용 합의 중앙값 ↓ | solver seed 5개의 최소~최대 |", "| --- | ---: | ---: |"]
    for o in data["own_instances"]:
        lines.append(f"| {o['label']} | {o['median_total']:.0f} | {min(o['totals'])}~{max(o['totals'])} |")
    return "\n".join(lines)


def loss_table(data: dict) -> str:
    sa = next(s for s in data["stages"] if s["key"] == "sa-2")
    plateau = data["plateau"]
    lines = ["| TC | 작업 수 × 기계 수 | 중앙 손해 | 시작 온도 0.1배 | 끝 온도 | 점수가 그대로인 제안 |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    shapes = [(200, 6), (400, 8), (800, 10), (1500, 12), (2500, 16), (4000, 20)]
    for i, ((n, m), loss) in enumerate(zip(shapes, sa["median_loss"]), start=1):
        assert plateau[i - 1]["n"] == n
        same = 100 * plateau[i - 1]["same_makespan"] / plateau[i - 1]["proposals"]
        lines.append(f"| {i} | {n} × {m} | {loss:.1f} | {0.1 * loss:.1f} | {0.1 * loss * 0.02:.2f} | {same:.0f}% |")
    return "\n".join(lines)


def tables(data: dict) -> dict[str, str]:
    return {"handtime": hand_time_table(), "hand": hand_table(), "stages": stage_table(data), "losses": loss_table(data), "temperatures": temp_table(data),
            "weights": weight_table(data), "own": own_table(data)}


def table_after(markdown: str, key: str) -> str:
    match = re.search(r"<!-- check:" + re.escape(key) + r" -->\n((?:\|[^\n]*\n?)+)", markdown)
    assert match, f"missing table marker: {key}"
    return match.group(1).rstrip("\n")


def check_stored(facts: dict) -> None:
    data = json.loads(ASSET.read_text())
    markdown = read_lesson_text(LESSON_ID)
    for key, expected in tables(data).items():
        assert table_after(markdown, key) == expected, f"lesson table '{key}' differs from the stored measurement/recomputation"
    hub_rows = check_hub_summary(LESSON_ID, [(s["label"], s["total"]) for s in data["stages"] if s["key"] != "final"])
    print(f"OK: hub summary table matches the stored stage totals ({hub_rows} rows)")
    greedy = next(s for s in data["stages"] if s["key"] == "greedy")
    final = next(s for s in data["stages"] if s["key"] == "final")
    assert final["costs"] == next(s for s in data["stages"] if s["key"] == "sa-2")["costs"]
    for needle in [str(s["total"]) for s in data["stages"]] + [str(data["buggy_max"]["total"]), data["judge_sha256"][:12],
                                                               data["measured_at"], data["environment"].split(" / ")[0]]:
        assert needle in markdown, needle
    figure2 = ASSET.parent / "acceptance-by-temperature.svg"
    if figure2.exists():
        text = figure2.read_text()
        for t in data["temperatures"]:
            if t["factor"] > 0:
                assert f"{t['median_total']:.0f}" in text and f"×{t['factor']:g} " in text, t["factor"]
    if FIGURE.exists():
        figure = FIGURE.read_text()
        assert all(token in figure for token in ("14", "15", "12", "9"))
    print("OK: lesson tables match the recomputed hand example and the stored SCHEDULX measurement")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--judge", type=Path, help="path to SCHEDULX main.cpp (read only)")
    parser.add_argument("--output", type=Path, help="measurement JSON to write when --judge is given")
    parser.add_argument("--print-tables", action="store_true", help="print the generated Markdown tables")
    args = parser.parse_args()
    values = sources()
    facts = run_checks(values)
    if args.judge:
        if not args.output:
            parser.error("--judge requires --output")
        benchmark(values, args.judge, args.output)
    stored = args.output or ASSET
    if args.print_tables:
        for key, text in tables(json.loads(stored.read_text())).items():
            print(f"<!-- check:{key} -->\n{text}\n")
        return
    if stored.exists():
        check_stored(facts)
    else:
        print("note: stored benchmark not found; table comparison skipped")


if __name__ == "__main__":
    main()
