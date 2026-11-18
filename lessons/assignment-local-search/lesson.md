# 배정 문제의 지역 탐색과 SA

```cpp snippet=assign-baseline
#define MAX_MACHINE_COUNT 20

void schedule_jobs(int job_count, int machine_count, const int processing_time[][MAX_MACHINE_COUNT], int assignment[]) {
    for (int job = 0; job < job_count; ++job) {
        assignment[job] = job % machine_count;
    }
}
```

```cpp snippet=assign-plan
#define MAX_MACHINE_COUNT 20

namespace sched {
const int MAX_JOB = 4000;

struct Plan {
    int n, m;
    const int (*time)[MAX_MACHINE_COUNT];
    int machine[MAX_JOB];
    long long load[MAX_MACHINE_COUNT];
    long long total;     // load[]의 합
    long long makespan;  // load[]의 최댓값. 실제 점수

    // machine[]만 믿고 load, total, makespan을 처음부터 다시 계산한다.
    void rebuild() {
        for (int k = 0; k < m; ++k) load[k] = 0;
        for (int j = 0; j < n; ++j) load[machine[j]] += time[j][machine[j]];
        total = 0;
        makespan = 0;
        for (int k = 0; k < m; ++k) {
            total += load[k];
            if (load[k] > makespan) makespan = load[k];
        }
    }
};

// 작업을 입력 순서대로, 놓은 뒤 부하가 가장 작아지는 기계에 넣는다.
void greedy(Plan& p) {
    for (int k = 0; k < p.m; ++k) p.load[k] = 0;
    for (int j = 0; j < p.n; ++j) {
        int best = 0;
        for (int k = 1; k < p.m; ++k) {
            if (p.load[k] + p.time[j][k] < p.load[best] + p.time[j][best]) best = k;
        }
        p.machine[j] = best;
        p.load[best] += p.time[j][best];
    }
    p.rebuild();
}
}
```

```cpp snippet=assign-delta
namespace sched {
struct Change {
    long long makespan, total;  // 이동 뒤의 값
};

// 두 기계의 새 부하와, 그 둘을 뺀 나머지 기계의 최댓값으로 새 makespan을 만든다.
static Change finish(const Plan& p, int a, int b, long long newA, long long newB, long long newTotal) {
    long long best = newA > newB ? newA : newB;
    for (int k = 0; k < p.m; ++k) {
        if (k != a && k != b && p.load[k] > best) best = p.load[k];
    }
    Change c = {best, newTotal};
    return c;
}

// job을 to 기계로 옮긴 결과. p는 바꾸지 않는다. 전제: to != p.machine[job]
Change tryMove(const Plan& p, int job, int to) {
    int from = p.machine[job];
    long long newFrom = p.load[from] - p.time[job][from];
    long long newTo = p.load[to] + p.time[job][to];
    return finish(p, from, to, newFrom, newTo, p.total + p.time[job][to] - p.time[job][from]);
}

// 서로 다른 기계에 있는 두 작업의 교환. 전제: p.machine[x] != p.machine[y]
Change trySwap(const Plan& p, int x, int y) {
    int a = p.machine[x], b = p.machine[y];
    long long newA = p.load[a] - p.time[x][a] + p.time[y][a];
    long long newB = p.load[b] - p.time[y][b] + p.time[x][b];
    long long newTotal = p.total + (p.time[y][a] - p.time[x][a]) + (p.time[x][b] - p.time[y][b]);
    return finish(p, a, b, newA, newB, newTotal);
}

struct Move {
    int kind;  // 0: x번 작업을 y번 기계로, 1: x번과 y번 작업 교환
    int x, y;
    Change after;
};

// 전제: n >= 2, m >= 2. 같은 기계의 두 작업을 고르면 한 작업 이동으로 바꾼다.
Move propose(const Plan& p, hc::Random& rng, int swapPercent) {
    Move mv;
    mv.x = (int)rng.below((unsigned)p.n);
    if ((int)rng.below(100u) < swapPercent) {
        mv.y = (int)rng.below((unsigned)p.n);
        if (p.machine[mv.x] != p.machine[mv.y]) {
            mv.kind = 1;
            mv.after = trySwap(p, mv.x, mv.y);
            return mv;
        }
    }
    mv.y = (int)rng.below((unsigned)(p.m - 1));
    if (mv.y >= p.machine[mv.x]) ++mv.y;
    mv.kind = 0;
    mv.after = tryMove(p, mv.x, mv.y);
    return mv;
}

void apply(Plan& p, const Move& mv) {
    if (mv.kind == 0) {
        int from = p.machine[mv.x];
        p.load[from] -= p.time[mv.x][from];
        p.load[mv.y] += p.time[mv.x][mv.y];
        p.machine[mv.x] = mv.y;
    } else {
        int a = p.machine[mv.x], b = p.machine[mv.y];
        p.load[a] += p.time[mv.y][a] - p.time[mv.x][a];
        p.load[b] += p.time[mv.x][b] - p.time[mv.y][b];
        p.machine[mv.x] = b;
        p.machine[mv.y] = a;
    }
    p.total = mv.after.total;
    p.makespan = mv.after.makespan;
}

// 탐색용 에너지 변화: 실제 점수 변화 + weight * 평균 부하 변화
double energyChange(const Plan& p, const Change& c, double weight) {
    return (double)(c.makespan - p.makespan) + weight * (double)(c.total - p.total) / p.m;
}
}
```

```cpp snippet=assign-anneal
namespace sched {
const int SEGMENTS = 5;

// x >= 0. 헤더 없이 exp(-x)를 근사한다. (search-strategies의 ordering_sa::expNegative와 같은 방식)
double expNegative(double x) {
    if (x >= 32.0) return 0.0;
    int halves = 0;
    while (x > 0.5) { x *= 0.5; ++halves; }
    double sum = 1.0, term = 1.0;
    for (int k = 1; k <= 12; ++k) {
        term *= -x / k;
        sum += term;
    }
    for (int k = 0; k < halves; ++k) sum *= sum;
    return sum;
}

// 현재 해에서 무작위 이동을 samples번 제안해 양수 손해의 중앙값을 돌려준다. p는 바꾸지 않는다.
double medianLoss(const Plan& p, unsigned seed, int samples, double weight, int swapPercent) {
    static double loss[4096];
    if (p.n < 2 || p.m < 2) return 1.0;
    if (samples > 4096) samples = 4096;
    hc::Random rng;
    rng.reset(seed);
    int count = 0;
    for (int i = 0; i < samples; ++i) {
        Move mv = propose(p, rng, swapPercent);
        double d = energyChange(p, mv.after, weight);
        if (d <= 0.0) continue;
        int pos = count++;  // 삽입 정렬
        while (pos > 0 && loss[pos - 1] > d) { loss[pos] = loss[pos - 1]; --pos; }
        loss[pos] = d;
    }
    return count == 0 ? 1.0 : loss[count / 2];
}

struct Params {
    long long attempts;
    unsigned seed;
    double startTemp, endTemp;
    double weight;
    int swapPercent;
};

struct Stats {
    long long initialMakespan, bestMakespan;
    long long proposedWorse[SEGMENTS], acceptedWorse[SEGMENTS], acceptedOther[SEGMENTS];
};

// p에서 시작해 best[]에 가장 좋았던 배정을 남긴다. p는 current로 계속 움직인다.
Stats anneal(Plan& p, const Params& prm, int best[]) {
    Stats st;
    st.initialMakespan = st.bestMakespan = p.makespan;
    for (int s = 0; s < SEGMENTS; ++s) st.proposedWorse[s] = st.acceptedWorse[s] = st.acceptedOther[s] = 0;
    for (int j = 0; j < p.n; ++j) best[j] = p.machine[j];
    if (p.n < 2 || p.m < 2 || prm.attempts <= 0) return st;

    hc::Random rng;
    rng.reset(prm.seed);
    for (long long step = 0; step < prm.attempts; ++step) {
        double progress = prm.attempts == 1 ? 0.0 : (double)step / (double)(prm.attempts - 1);
        double temperature = prm.startTemp + (prm.endTemp - prm.startTemp) * progress;
        int seg = (int)(step * SEGMENTS / prm.attempts);
        Move mv = propose(p, rng, prm.swapPercent);
        double d = energyChange(p, mv.after, prm.weight);
        double u = (rng.next() >> 8) / 16777216.0;  // 개선 이동에서도 난수를 하나 쓴다.
        bool accept = d <= 0.0;
        if (d > 0.0) {
            ++st.proposedWorse[seg];
            if (temperature > 0.0) accept = u < expNegative(d / temperature);
        }
        if (!accept) continue;  // 거절한 이동은 p를 건드리지 않았으므로 되돌릴 것이 없다.
        apply(p, mv);
        if (d > 0.0) ++st.acceptedWorse[seg]; else ++st.acceptedOther[seg];
        if (p.makespan < st.bestMakespan) {
            st.bestMakespan = p.makespan;
            for (int j = 0; j < p.n; ++j) best[j] = p.machine[j];
        }
    }
    return st;
}
}
```

```cpp snippet=assign-entry
void schedule_jobs(int job_count, int machine_count, const int processing_time[][MAX_MACHINE_COUNT], int assignment[]) {
    sched::Plan plan;
    plan.n = job_count;
    plan.m = machine_count;
    plan.time = processing_time;
    sched::greedy(plan);

    sched::Params prm;
    prm.attempts = 2000000;
    prm.seed = 20261118u;
    prm.weight = 2.0;
    prm.swapPercent = 50;
    double loss = sched::medianLoss(plan, prm.seed ^ 0x5bd1e995u, 2000, prm.weight, prm.swapPercent);
    prm.startTemp = 0.1 * loss;
    prm.endTemp = 0.02 * prm.startTemp;
    sched::anneal(plan, prm, assignment);
}
```


```cpp
    if (p.makespan > best) best = p.makespan;  // 나머지 기계 최댓값 대신 옛 최댓값을 쓴다.
```
