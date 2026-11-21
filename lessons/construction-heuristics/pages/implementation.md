# 코드 틀과 두 문제 유형 적용

구성 틀은 문제와 무관한 고정 부분과 문제마다 채우는 부분으로 나뉩니다. 이 페이지는 고정 부분을 먼저 보이고, 같은 틀에 순서 틀과 배정 틀을 각각 채워 넣습니다.

| 구분 | 내용 | 코드 |
| --- | --- | --- |
| 고정 | 후보 요약 `Cand`, 선택 기준 `ruleKey`와 동률 규칙 `better`, 흔들기를 포함한 `pick`, 구성 반복 `construct`, 여러 번 만들기 `bestOf`, 입력 생성기 `Gen` | `cons-core` |
| 채움 | `begin`, `remaining`, `candidates`, `place`, `score`, `solution`과 해당 문제의 상태 | `cons-path`, `cons-jobs` |
| 문제에 맞춘 고정 개선 | 구성 뒤에 붙이는 가장 단순한 개선 | `cons-improve` |

> **코드 환경: h-contest 제출용 코드.** 공통 라이브러리의 `random`, `sort` 블록을 먼저 붙인 뒤 아래 블록을 순서대로 붙입니다. 표준 헤더·STL·동적 할당은 쓰지 않습니다. 큰 배열은 함수 안 `static`과 구조체 고정 배열이며, 상한은 순서 틀 점 200개, 배정 틀 작업 120개·기계 8대입니다. 상한을 넘기려면 `MAXN`, `MAXM`을 함께 키웁니다.

## 고정 부분: 구성 틀

`construct`는 `begin(first)`, `remaining()`, `candidates(cand, rule)`, `place(item, slot)`만 부릅니다. `candidates`는 남은 항목마다 가장 싼 자리와 그 비용, 두 번째로 싼 자리의 비용, 항목의 "큰 정도"(`weight`)를 채웁니다. 선택은 `pick`이 `Plan`에 따라 합니다. `Plan`의 `width`와 `percent`가 흔드는 정도이고 `width == 1`이면 난수를 쓰지 않으므로 같은 입력에서 같은 해가 나옵니다. 동률은 항상 같은 순서로 풀어야 결과를 재현할 수 있어서 `better`가 키, `best`, 항목 번호 순으로 정합니다.

```cpp snippet=cons-core
namespace cons {
const long long BIG = 1000000000000LL;   // "자리가 없음"을 뜻하는 비용

// 남은 항목 하나의 요약: 어디에 두면 가장 싼지(slot)와 그 비용(best), 두 번째로 싼 자리의 비용(second).
struct Cand {
    int item, slot;
    long long best, second, weight;      // weight: 문제가 정하는 "큰 정도"
};

enum Rule { RULE_INDEX, RULE_CHEAPEST, RULE_REGRET, RULE_HEAVIEST };

// 한 번의 구성을 정하는 값: 선택 기준, 그리고 얼마나 흔들지(percent% 확률로 앞선 width개 중 하나를 무작위로 고른다).
struct Plan {
    int rule, width, percent;
    bool randomFirst;                    // 첫 항목을 무작위로 정할지(경로의 첫 점)
};

// 작을수록 먼저 고른다. 후회 = second - best 는 클수록 먼저이므로 부호를 바꾼다.
long long ruleKey(const Cand& c, int rule) {
    if (rule == RULE_CHEAPEST) return c.best;
    if (rule == RULE_REGRET) return -(c.second - c.best);
    if (rule == RULE_HEAVIEST) return -c.weight;
    return c.item;
}

// 같은 키이면 best가 작은 쪽, 그다음 item이 작은 쪽을 먼저 둔다(동률 규칙).
bool better(const Cand& a, const Cand& b, int rule) {
    const long long ka = ruleKey(a, rule), kb = ruleKey(b, rule);
    if (ka != kb) return ka < kb;
    if (a.best != b.best) return a.best < b.best;
    return a.item < b.item;
}

// 규칙으로 가장 앞선 후보를 고른다. 흔드는 단계에서는 앞선 width개를 추려 그중 하나를 무작위로 고른다.
// width == 1이면 난수를 쓰지 않는다(width <= 8).
int pick(const Cand cand[], int n, const Plan& plan, hc::Random& rng) {
    const int rule = plan.rule;
    int chosen[8], count = 0;
    int width = plan.width;
    if (width > 1 && (int)rng.below(100) >= plan.percent) width = 1;
    if (width > n) width = n;
    for (int r = 0; r < width; ++r) {
        int bestIdx = -1;
        for (int i = 0; i < n; ++i) {
            bool taken = false;
            for (int t = 0; t < count; ++t) if (chosen[t] == i) taken = true;
            if (taken) continue;
            if (bestIdx < 0 || better(cand[i], cand[bestIdx], rule)) bestIdx = i;
        }
        chosen[count++] = bestIdx;
    }
    return chosen[width == 1 ? 0 : (int)rng.below((unsigned)width)];
}

// 문제와 무관한 구성 틀. P가 채워 넣을 것: begin, remaining, candidates, place.
template<class P> void construct(P& p, const Plan& plan, int first, hc::Random& rng) {
    static Cand cand[P::MAXN];
    p.begin(first);
    while (p.remaining() > 0) {
        const int n = p.candidates(cand, plan.rule);     // 채울 부분 1: 남은 항목마다 가장 싼 자리
        const int c = pick(cand, n, plan, rng);          // 고정 부분: 규칙으로 하나 고른다
        p.place(cand[c].item, cand[c].slot);             // 채울 부분 2: 상태 갱신
    }
}

// 같은 규칙으로 runs번 만들어 점수가 가장 좋은(작은) 것을 bestSol에 남긴다.
template<class P> long long bestOf(P& p, const Plan& plan, int runs, hc::Random& rng, int bestSol[]) {
    long long best = BIG;
    for (int r = 0; r < runs; ++r) {
        construct(p, plan, plan.randomFirst ? (int)rng.below((unsigned)p.n) : 0, rng);
        if (p.score() < best) {
            best = p.score();
            for (int i = 0; i < p.n; ++i) bestSol[i] = p.solution()[i];
        }
    }
    return best;
}

struct Gen {                             // 연습용 입력 생성기: 64비트 LCG
    unsigned long long x;
    void reset(unsigned long long seed) { x = seed; }
    int next(int range) {                // 0 .. range-1
        x = x * 6364136223846793005ULL + 1442695040888963407ULL;
        return (int)((x >> 33) % (unsigned long long)range);
    }
};

inline int iabs(int v) { return v < 0 ? -v : v; }
}
```

`construct` 안의 `static Cand cand[P::MAXN]`은 후보 요약을 담는 배열로, 구성을 시작할 때마다 `candidates`가 앞에서부터 다시 채웁니다. `bestOf`는 가장 좋은 해를 **복사해서** 남깁니다. 점수만 갱신하고 해를 복사하지 않으면 마지막에 만든 해가 반환되므로 [흔한 실수](practice.md)에서 이 경우를 검사합니다.

## 채움 1: 순서 틀

상태는 지금까지 만든 경로 `order[0..len-1]`와 길이 `length`입니다. `place`가 길이를 증분으로 갱신하고, 전체를 다시 계산한 값과 같은지는 검사 스크립트가 매 단계 확인합니다. `anySlot`이 `false`이면 끝에만 붙이는 가장 가까운 점 잇기, `true`이면 모든 자리를 보는 삽입입니다. 가장 먼 점 삽입(`RULE_HEAVIEST`)은 `weight`에 경로의 가장 가까운 점까지의 거리를 채웁니다. 이 계산도 평가 횟수에 넣습니다.

정렬 기준만으로 한 번에 만드는 구성법은 `stripOrder`입니다. 점을 세로 띠로 나누고 띠 안에서 `y`를 오름·내림으로 번갈아 잇습니다. `construct`를 거치지 않고 `sort` 블록의 `sortIds`로 순서를 정한 뒤 `setOrder`로 경로를 만듭니다.

```cpp snippet=cons-path
namespace cons {
// 순서 틀: 점을 한 번씩 지나는 열린 경로. 비용 = 이웃한 점 사이 맨해튼 거리의 합.
struct Path {
    static const int MAXN = 200;
    int n, px[MAXN], py[MAXN];
    int order[MAXN], len;                // order[0..len-1]: 지금까지 만든 경로
    bool used[MAXN];
    bool anySlot;                        // false: 끝에만 붙인다 / true: 어느 자리에든 끼운다
    long long length, evals;             // 경로 길이(증분 갱신), 비용 평가 횟수

    int dist(int a, int b) const { return iabs(px[a] - px[b]) + iabs(py[a] - py[b]); }

    // 점 p를 order[slot] 앞에 끼울 때 늘어나는 길이. slot == len이면 끝에 붙인다.
    long long delta(int p, int slot) const {
        if (len == 0) return 0;
        if (slot == 0) return dist(p, order[0]);
        if (slot == len) return dist(order[len - 1], p);
        return dist(order[slot - 1], p) + dist(p, order[slot]) - dist(order[slot - 1], order[slot]);
    }

    void begin(int first) {
        len = 0; length = 0;
        for (int i = 0; i < n; ++i) used[i] = false;
        place(first, 0);
    }
    int remaining() const { return n - len; }

    int candidates(Cand out[], int rule) {
        int count = 0;
        for (int p = 0; p < n; ++p) {
            if (used[p]) continue;
            Cand c;
            c.item = p; c.slot = len; c.best = BIG; c.second = BIG; c.weight = 0;
            for (int s = anySlot ? 0 : len; s <= len; ++s) {
                const long long v = delta(p, s);
                ++evals;
                if (v < c.best) { c.second = c.best; c.best = v; c.slot = s; }
                else if (v < c.second) c.second = v;
            }
            if (rule == RULE_HEAVIEST) {            // 경로의 가장 가까운 점까지의 거리
                c.weight = BIG;
                for (int i = 0; i < len; ++i) {
                    const long long v = dist(p, order[i]);
                    ++evals;
                    if (v < c.weight) c.weight = v;
                }
            }
            out[count++] = c;
        }
        return count;
    }

    void place(int p, int slot) {
        length += delta(p, slot);
        for (int i = len; i > slot; --i) order[i] = order[i - 1];
        order[slot] = p; used[p] = true; ++len;
    }

    long long score() const { return length; }
    const int* solution() const { return order; }
};

void makePath(Path& p, int n, unsigned long long seed) {
    Gen g; g.reset(seed);
    p.n = n; p.anySlot = true; p.evals = 0;
    for (int i = 0; i < n; ++i) { p.px[i] = g.next(1000); p.py[i] = g.next(1000); }
}

// 정해 둔 순서(ids)를 그대로 경로로 만든다. 정렬 기준만으로 한 번에 만드는 구성법이 쓴다.
void setOrder(Path& p, const int ids[]) {
    p.len = 0; p.length = 0;
    for (int i = 0; i < p.n; ++i) p.place(ids[i], p.len);
}

// 세로 띠(strips개)로 나누고, 띠 안에서 y를 번갈아 오름·내림 순으로 잇는다.
void stripOrder(Path& p, int strips) {
    static long long key[Path::MAXN];
    static int id[Path::MAXN], temp[Path::MAXN];
    for (int i = 0; i < p.n; ++i) {
        const int s = p.px[i] * strips / 1000;
        key[i] = (long long)s * 1000 + (s % 2 == 0 ? p.py[i] : 999 - p.py[i]);
        id[i] = i;
    }
    hc::sortIds(id, temp, p.n, key);
    setOrder(p, id);
}
}
```

## 채움 2: 배정 틀

상태는 작업별 기계 `assign`, 기계별 부하 `load`와 개수 `cnt`입니다. 기계가 가득 차면(`cnt >= k`) 그 기계를 후보 자리에서 뺍니다. 이것이 개수 제한을 지키는 부분이며, 두 번째 자리가 없으면 `second`가 `BIG`으로 남아 후회가 매우 큰 항목으로 취급됩니다. 비교에는 부하 제곱의 변화에 100을 곱한 정수 값을 써서 실수 연산과 나눗셈을 피하고, 점수 `score()`에서만 합에 대해 한 번 나눕니다.

`N ≤ M × K`가 전제입니다. 이 전제가 깨지면 후보가 없는 항목이 생기고 `place(j, -1)`이 배열 범위를 벗어납니다.

```cpp snippet=cons-jobs
namespace cons {
// 배정 틀: 작업 n개를 기계 m대에 맡긴다. 한 기계에는 k개까지.
// 비용 = (기계별 부하 제곱의 합) / 100 + 추가 비용의 합. 비교에는 100을 곱한 값(부하 제곱의 합 + 100 * 추가 비용)을 쓴다.
struct Jobs {
    static const int MAXN = 120, MAXM = 8;
    int n, m, k;
    int d[MAXN], c[MAXN][MAXM];
    int assign[MAXN], load[MAXM], cnt[MAXM], placed;
    bool done[MAXN];
    long long evals;

    // 작업 j를 기계 mc에 더할 때 늘어나는 값(100배): (load + d)^2 - load^2 + 100 * c
    long long delta(int j, int mc) const { return (long long)(2 * load[mc] + d[j]) * d[j] + 100LL * c[j][mc]; }

    void begin(int) {
        placed = 0;
        for (int j = 0; j < n; ++j) { done[j] = false; assign[j] = -1; }
        for (int i = 0; i < m; ++i) load[i] = cnt[i] = 0;
    }
    int remaining() const { return n - placed; }

    int candidates(Cand out[], int) {
        int count = 0;
        for (int j = 0; j < n; ++j) {
            if (done[j]) continue;
            Cand x;
            x.item = j; x.slot = -1; x.best = BIG; x.second = BIG; x.weight = d[j];
            for (int mc = 0; mc < m; ++mc) {
                if (cnt[mc] >= k) continue;              // 가득 찬 기계는 후보에서 뺀다
                const long long v = delta(j, mc);
                ++evals;
                if (v < x.best) { x.second = x.best; x.best = v; x.slot = mc; }
                else if (v < x.second) x.second = v;
            }
            out[count++] = x;
        }
        return count;
    }

    void place(int j, int mc) {
        assign[j] = mc; done[j] = true; ++placed;
        load[mc] += d[j]; ++cnt[mc];
    }

    long long score() const {
        long long sq = 0, extra = 0;
        for (int i = 0; i < m; ++i) sq += (long long)load[i] * load[i];
        for (int j = 0; j < n; ++j) extra += c[j][assign[j]];
        return sq / 100 + extra;
    }
    const int* solution() const { return assign; }
};

void makeJobs(Jobs& q, int n, int m, int k, unsigned long long seed) {
    Gen g; g.reset(seed);
    q.n = n; q.m = m; q.k = k; q.evals = 0;
    for (int j = 0; j < n; ++j) q.d[j] = 1 + g.next(100);
    for (int j = 0; j < n; ++j) for (int i = 0; i < m; ++i) q.c[j][i] = g.next(51);
}
}
```

## 단순 개선

개선은 구성법 뒤에 같은 방식으로 붙는 고정 절차입니다. 순서 틀은 인접한 두 점 교환, 배정 틀은 작업 하나를 다른 기계로 옮기기만 씁니다. 두 절차 모두 비용이 줄 때만 받고, 한 바퀴 내내 바뀐 것이 없으면 멈추므로 시드나 시간 없이 결정적입니다. 반환값은 비용 변화를 계산한 횟수입니다. 더 좋은 이동과 차분 설계는 [근방 설계와 차분 평가](https://h.readiz.com/learn/neighborhood-and-delta)에서, 나쁜 이동을 받는 탐색은 [언덕 오르기와 담금질](https://h.readiz.com/learn/hill-climbing-and-annealing)에서 다룹니다.

```cpp snippet=cons-improve
namespace cons {
// 구성법 뒤에 붙이는 가장 단순한 개선: 인접한 두 점을 바꿔 짧아지면 받는다. 한 바퀴 내내 바뀐 것이 없으면 멈춘다.
// 반환값은 비용 변화를 계산한 횟수. 이동의 설계와 더 좋은 탐색은 이웃 강의(근방 설계, 담금질)에서 다룬다.
long long improveAdjacent(Path& p) {
    long long evals = 0;
    bool changed = true;
    while (changed) {
        changed = false;
        for (int i = 0; i + 1 < p.len; ++i) {
            const int a = p.order[i], b = p.order[i + 1];
            long long change = 0;
            if (i > 0) change += p.dist(p.order[i - 1], b) - p.dist(p.order[i - 1], a);
            if (i + 2 < p.len) change += p.dist(a, p.order[i + 2]) - p.dist(b, p.order[i + 2]);
            ++evals;
            if (change < 0) { p.order[i] = b; p.order[i + 1] = a; p.length += change; changed = true; }
        }
    }
    return evals;
}

// 배정 틀의 같은 역할: 작업 하나를 다른 기계로 옮겨 비용이 줄면 받는다(가득 찬 기계로는 옮기지 않는다).
long long improveMove(Jobs& q) {
    long long evals = 0;
    bool changed = true;
    while (changed) {
        changed = false;
        for (int j = 0; j < q.n; ++j) {
            const int from = q.assign[j];
            const long long out = -(long long)(2 * q.load[from] - q.d[j]) * q.d[j] - 100LL * q.c[j][from];
            long long bestChange = 0;
            int to = -1;
            for (int mc = 0; mc < q.m; ++mc) {
                if (mc == from || q.cnt[mc] >= q.k) continue;
                const long long change = out + q.delta(j, mc);
                ++evals;
                if (change < bestChange) { bestChange = change; to = mc; }
            }
            if (to < 0) continue;
            q.load[from] -= q.d[j]; --q.cnt[from];
            q.load[to] += q.d[j]; ++q.cnt[to];
            q.assign[j] = to; changed = true;
        }
    }
    return evals;
}
}
```

## 사용 예

아래 두 함수는 구성과 개선을 이어 붙인 가장 짧은 사용 예입니다. 구성 틀은 그대로이고 문제 구조체와 규칙만 다릅니다.

```cpp snippet=cons-entry
namespace cons {
// 순서 틀의 사용 예: 후회 삽입으로 한 번 만들고 인접 교환으로 다듬는다. 반환값은 경로 길이.
long long solveOrder(Path& p) {
    hc::Random rng;
    rng.reset(1);
    p.anySlot = true;
    construct(p, Plan{RULE_REGRET, 1, 0, false}, 0, rng);
    improveAdjacent(p);
    return p.score();
}

// 배정 틀의 사용 예: 후회가 큰 작업부터 배정하고, 작업 하나 옮기기로 다듬는다. 반환값은 비용.
long long solveJobs(Jobs& q) {
    hc::Random rng;
    rng.reset(1);
    construct(q, Plan{RULE_REGRET, 1, 0, false}, 0, rng);
    improveMove(q);
    return q.score();
}
}
```

입력을 만드는 방법은 `makePath(p, n, seed)`와 `makeJobs(q, n, m, k, seed)`입니다. 난수는 `x = x * 6364136223846793005 + 1442695040888963407`(64비트)에서 `(x >> 33) % 범위`를 쓰며 시드를 `x`의 처음 값으로 둡니다. 순서 틀은 점마다 `x`, `y` 순으로 `0..999`, 배정 틀은 모든 작업의 길이 `d`(`1..100`)를 먼저, 그다음 추가 비용 `c[작업][기계]`(`0..50`)를 작업 순서대로 뽑습니다.
