# 구현: 후보 목록·예산 틀과 두 문제 유형

[원리와 손계산](idea.md)의 절차를 코드로 옮깁니다. 코드는 문제와 상관없이 그대로 쓰는 부분(예산 계획, 탐색 루프, 마무리, 남은 비율로 값을 정하는 함수)과 문제마다 채우는 부분(해의 표현, 후보 목록 만들기, 후보에서 이동 하나 만들기, 점수 변화 계산)으로 나눕니다. 채우는 부분에는 같은 이름의 멤버를 두므로 문제가 바뀌어도 루프는 한 글자도 고치지 않습니다. 두 가지 문제 유형(순서·배정)은 [연습용 문제 틀](idea.md)에서 크기를 키운 것입니다.

> **코드 환경: h-contest 제출용 코드.** 표준 헤더·STL·동적 할당 없이 고정 배열로 씁니다. 공통 블록 `array`, `random`([공통 라이브러리](https://h.readiz.com/learn/cpp-common-library))을 먼저 붙이고, 이 페이지의 `tb-frame`, `tb-route`, `tb-assign`, `tb-gen`, `tb-run`을 이 순서로 이어 붙이면 한 번역 단위로 컴파일됩니다. 입출력이 없는 라이브러리 형태이며, 실제 문제에 쓸 때는 문제의 입력으로 `Route`나 `Assign`의 배열을 채우는 부분만 바꿉니다. 시간을 재는 코드는 표준 헤더가 필요해서 [실험과 점검](practice.md)의 "자기 환경에서 재는 방법"에 따로 있습니다.

[근방 설계와 차분 평가](https://h.readiz.com/learn/neighborhood-and-delta)의 `Move`, `pick`, 구간 뒤집기와 작업 옮기기의 `delta`·`apply`는 그대로 쓰며 같은 이름과 같은 연산 세기 규칙입니다. 다시 설명하지 않고 이 강의 코드만 이어 붙여도 컴파일되도록 필요한 만큼만 다시 실었습니다. 이 페이지에서 새로 생긴 것은 `byRemaining`, `Plan`, `proposeCand`, `sweepAll`, `climbPlan`과 각 문제의 칸·초기해·후보 목록 부분입니다.

## 문제와 무관한 부분: 계획, 후보 이동, 두 단계의 루프

탐색 루프가 문제에 요구하는 것은 아래 멤버입니다. 3번 강의의 `propose`가 "후보에서 이동 하나를 만든다"는 `cand`와 "후보 없이 무작위로 만든다"는 `any`로 나뉘었습니다.

| 멤버 | 하는 일 | 지켜야 할 점 |
| --- | --- | --- |
| `int items()` | 후보를 낼 수 있는 항목의 수. 순서 틀은 (위치, 방향) 쌍이라 점 수의 2배, 배정 틀은 작업 수 | |
| `bool cand(item, r, mv)` | 항목의 `r`번째 후보로 이동 하나를 만든다. 무효하거나 변화가 없으면 `false` | `r`은 목록 길이 안. 만든 이동은 모두 유효 |
| `bool any(rng, mv)` | 후보 목록 없이 이동 하나를 무작위로 만든다(비교용 기준) | 같은 이동 가족 전체에서 고른다 |
| `long long delta(mv)` | 적용하지 않고 비용 변화량만 계산한다 | 해와 캐시를 바꾸지 않는다 |
| `void apply(mv)` | 해와 캐시를 바꾼다 | 위치 역배열(`pos`) 같은 캐시도 함께 |
| `long long ops, props, reads` | 연산 계수기, 제안 수, 시계를 읽은 횟수 | 예산의 단위. 제출할 때 지워도 동작이 같다 |

`Plan`은 한 번의 실행 계획입니다. 상한 `limit`은 초기해와 후보 목록을 만드는 데 쓴 연산도 포함하며, `finish`만큼은 마무리 단계에 남겨 둡니다. 탐색 단계에서 후보 수는 `byRemaining`으로 남은 비율에 묶여 `kFirst`에서 `kLast`로 줄거나 늘고, 둘이 같으면 고정입니다. `every`와 `clockCost`는 시계를 읽는 간격과 한 번 읽는 비용입니다(연산 수 모형이며, 제출에서는 실제 시계 읽기가 이 자리에 들어갑니다).

```cpp snippet=tb-frame
struct Move { int kind, a, b, old; };

// [0, bound) 안의 값. 상위 비트를 쓴다(3번 강의의 `pick`과 같다).
int pick(hc::Random& rng, int bound) { return (int)(((unsigned long long)rng.next() * (unsigned)bound) >> 32); }

// 남은 연산이 total이면 hi, 0이면 lo가 되도록 정수로 선형으로 잇는다. 크기·후보 수를 남은 비율에 묶는 틀.
int byRemaining(int hi, int lo, long long remaining, long long total) {
    if (remaining < 0) remaining = 0;
    return lo + (int)(((long long)(hi - lo) * remaining) / total);
}

// 한 번의 실행 계획. 모든 길이는 연산 수로 잰다(제출에서는 시계로 바꾼다).
struct Plan {
    long long limit;       // 연산 수 상한. 초기해와 후보 목록을 만드는 데 쓴 연산도 포함한다
    long long finish;      // 마무리 단계에 남겨 둘 연산 수(0이면 마무리 없음)
    int every;             // 시계를 읽는 간격: 제안 every번에 한 번 읽는다
    int clockCost;         // 시계를 한 번 읽는 비용(연산 수로 본 모형)
    int kFirst, kLast;     // 후보 수: 탐색 단계의 시작 때와 끝 때(0이면 후보 목록 없이 무작위 이동)
    int kFinish;           // 마무리 단계가 훑는 후보 수
};

// 이동 하나를 만든다. k <= 0이면 후보 목록 없이 무작위로, 아니면 무작위 항목의 앞쪽 k개 후보 중 하나로 만든다.
template <class P>
bool proposeCand(P& p, hc::Random& rng, int k, Move& mv) {
    if (k <= 0) return p.any(rng, mv);
    return p.cand(pick(rng, p.items()), pick(rng, k), mv);
}

// 마무리: 모든 항목의 앞쪽 k개 후보를 차례로 한 번씩 평가하고 좋아지면 받는다.
template <class P>
long long sweepAll(P& p, long long cost, int k, long long limit) {
    for (int it = 0; it < p.items() && p.ops < limit; ++it)
        for (int r = 0; r < k; ++r) {
            ++p.ops; ++p.props;
            Move mv;
            if (!p.cand(it, r, mv)) continue;
            const long long d = p.delta(mv);
            if (d < 0) { p.apply(mv); cost += d; }
        }
    return cost;
}

// 탐색 단계(좋아질 때만 받는다) + 마무리 단계. 시계는 every번에 한 번만 읽고, 읽을 때마다 후보 수를 다시 정한다.
template <class P>
long long climbPlan(P& p, hc::Random& rng, long long cost, const Plan& pl) {
    const long long stop = pl.limit - pl.finish, begin = p.ops;
    int k = pl.kFirst, since = pl.every;                 // 첫 반복에서 바로 읽는다
    while (true) {
        if (++since >= pl.every) {
            since = 0; p.ops += pl.clockCost; ++p.reads;
            if (p.ops >= stop) break;
            k = byRemaining(pl.kFirst, pl.kLast, stop - p.ops, stop - begin);
        }
        ++p.ops; ++p.props;
        Move mv;
        if (!proposeCand(p, rng, k, mv)) continue;
        const long long d = p.delta(mv);
        if (d < 0) { p.apply(mv); cost += d; }
    }
    if (pl.finish > 0) cost = sweepAll(p, cost, pl.kFinish, pl.limit);
    return cost;
}
```

`climbPlan`이 한 일은 세 가지입니다. 먼저 시계를 `every`번 제안마다 한 번만 읽습니다(읽을 때마다 `clockCost`를 치르며, 그 횟수는 `reads`에 남습니다). 읽을 때 후보 수를 남은 비율로 다시 정합니다. 탐색 단계가 `limit - finish`에 닿으면 마무리 단계로 넘어가 모든 항목의 앞쪽 `kFinish`개 후보를 한 번씩 훑습니다. 시계를 읽는 사이에 연산이 상한을 넘을 수 있으므로 끝난 뒤의 `ops`는 `limit`보다 조금 클 수 있고, 그 넘침의 상한은 `every`에 한 번의 제안이 쓸 수 있는 가장 큰 연산을 곱한 값입니다([실험과 점검](practice.md)의 시계 읽기 실험).

## 순서 틀 채우기: `Route`

해는 방문 순서 `p[]`이고 위치의 역배열 `pos[]`를 함께 들고 있습니다. 후보 이동은 "점 `p[a]`와 그 점의 `r`번째 이웃 `v`를 이웃으로 만드는" 구간 뒤집기이며, `v`의 위치가 `pos[v]`이므로 뒤집을 구간을 바로 정합니다. 두 점의 위치가 `lo < hi`일 때 둘을 이웃으로 만드는 구간은 `[lo+1, hi]`와 `[lo, hi-1]` 둘이라서 항목을 (위치, 방향)으로 둡니다. 그래서 `apply`가 `pos`를 같이 갱신해야 하고, 빼먹으면 이동은 계속 만들어지는데 의도한 이웃 간선이 생기지 않습니다([실험과 점검](practice.md)의 흔한 실수 2).

구성은 세 부분입니다.

- **칸과 초기해:** `buildCells`가 점을 칸 번호로 계수 정렬하고(칸마다 점이 연속 구간에 놓임), `initSnake`가 칸을 한 줄씩 방향을 바꿔 가며 훑어 첫 순서를 만듭니다. 같은 칸 구조를 이웃 목록 만들기가 다시 씁니다.
- **이웃 목록:** `buildNbBrute`는 모든 점의 쌍을 보는 전수, `buildNbGrid`는 가까운 칸부터 한 겹씩 넓히며 보는 칸 탐색입니다. 둘 다 (거리, 번호) 순의 같은 목록을 만들어야 하며, 거리가 같으면 번호가 작은 점이 앞섭니다. 칸 탐색은 한 겹(`r`)을 다 본 뒤 `k`번째 거리가 `r * cs` 이하이면 멈춥니다. 안 본 칸의 점은 칸 좌표가 `r + 1`칸 이상 떨어져 있어 거리가 `r * cs + 1` 이상이기 때문입니다.
- **이동:** `cand`는 항목 (위치 `a`, 방향)과 후보 번호 `r`로 뒤집을 구간을 정하고, 두 점이 이미 이웃이면 `false`입니다. `any`는 3번 강의처럼 두 위치를 무작위로 뽑습니다.

연산을 세는 규칙은 3번 강의와 같고 새 항목이 둘 있습니다. 칸을 정렬하는 데는 점마다 2번(세기, 놓기)과 칸마다 1번(누적합), 칸을 한 번 방문할 때 1, 후보 거리 하나를 계산할 때 1, 후보 목록의 원소를 한 칸 밀 때 1을 셉니다. `pos`는 `p`와 함께 쓰므로 원소 쓰기 1에 포함합니다.

```cpp snippet=tb-route
const int RN = 10000, KMAX = 32, CELLS = 40000;     // 점 수, 이웃 목록 길이, 칸 수의 상한
struct Route {
    int n, px[RN], py[RN], p[RN], pos[RN];           // 좌표, p[k] = k번째로 지나는 점, pos[v] = 점 v가 놓인 위치
    int kk, nb[RN][KMAX];                            // 이웃 목록: nb[u][r] = u에서 r번째로 가까운 점(거리, 번호 순), r < kk
    int cs, g, cellStart[CELLS + 1], cellPts[RN];    // 칸 한 변, 한 줄의 칸 수, 칸별 점 목록(계수 정렬)
    long long ops, writes, props, reads;

    void wrote(int c) { ops += c; writes += c; }
    int at(int k) { return (k < 0 || k >= n) ? -1 : p[k]; }
    int dist(int u, int v) {
        const int dx = px[u] - px[v], dy = py[u] - py[v];
        return (dx < 0 ? -dx : dx) + (dy < 0 ? -dy : dy);
    }
    long long w(int u, int v) { if (u < 0 || v < 0) return 0; ++ops; return dist(u, v); }
    long long fullCost() { long long s = 0; for (int k = 0; k + 1 < n; ++k) s += w(p[k], p[k + 1]); return s; }
    bool valid() {                                   // p는 순열이고 pos는 p의 역이다
        static bool seen[RN];
        hc::fill(seen, RN, false);
        for (int k = 0; k < n; ++k) {
            if (p[k] < 0 || p[k] >= n || seen[p[k]] || pos[p[k]] != k) return false;
            seen[p[k]] = true;
        }
        return true;
    }

    // ---- 칸과 초기해: 점을 칸 번호로 정렬하고, 칸을 한 줄씩 뱀처럼 훑어 첫 순서를 만든다
    void buildCells(int side) {
        cs = side; g = (1000 + cs - 1) / cs;
        static int cell[RN], fillPos[CELLS];
        hc::fill(cellStart, g * g + 1, 0);
        for (int v = 0; v < n; ++v) { cell[v] = (py[v] / cs) * g + px[v] / cs; ++cellStart[cell[v] + 1]; }
        for (int c = 0; c < g * g; ++c) cellStart[c + 1] += cellStart[c];
        hc::copy(fillPos, cellStart, g * g);
        for (int v = 0; v < n; ++v) cellPts[fillPos[cell[v]]++] = v;
        ops += 2 * n + g * g;                        // 세기, 놓기, 누적합
    }
    void initSnake() {                               // 칸 줄마다 방향을 바꿔 가며 칸 안의 점을 이어 붙인다
        int k = 0;
        for (int cy = 0; cy < g; ++cy)
            for (int i = 0; i < g; ++i) {
                const int cx = (cy % 2 == 0) ? i : g - 1 - i, c = cy * g + cx;
                for (int t = cellStart[c]; t < cellStart[c + 1]; ++t) p[k++] = cellPts[t];
            }
        for (int i = 0; i < n; ++i) pos[p[i]] = i;
        wrote(n);
    }

    // ---- 이웃 목록: 점마다 가까운 kk개를 (거리, 번호) 순으로
    int bd[KMAX], bi[KMAX], bc;                      // 지금 만드는 한 점의 목록과 길이
    void offer(int v, int d) {
        if (bc == kk && (d > bd[bc - 1] || (d == bd[bc - 1] && v > bi[bc - 1]))) return;
        int i = bc < kk ? bc++ : bc - 1;
        for (; i > 0 && (bd[i - 1] > d || (bd[i - 1] == d && bi[i - 1] > v)); --i) { bd[i] = bd[i - 1]; bi[i] = bi[i - 1]; ++ops; }
        bd[i] = d; bi[i] = v;
    }
    void takeList(int u) { for (int r = 0; r < kk; ++r) nb[u][r] = bi[r]; }
    void buildNbBrute(int k) {                       // 전수: 모든 쌍의 거리를 본다
        kk = k;
        for (int u = 0; u < n; ++u) {
            bc = 0;
            for (int v = 0; v < n; ++v) if (v != u) { ++ops; offer(v, dist(u, v)); }
            takeList(u);
        }
    }
    void scanCell(int u, int x, int y) {
        if (x < 0 || y < 0 || x >= g || y >= g) return;
        ++ops;
        const int c = y * g + x;
        for (int t = cellStart[c]; t < cellStart[c + 1]; ++t) {
            const int v = cellPts[t];
            if (v != u) { ++ops; offer(v, dist(u, v)); }
        }
    }
    void buildNbGrid(int k) {                        // 칸: 가까운 칸부터 한 겹씩 넓히며 본다
        kk = k;
        for (int u = 0; u < n; ++u) {
            bc = 0;
            const int cx = px[u] / cs, cy = py[u] / cs;
            for (int r = 0; r < g; ++r) {
                for (int y = cy - r; y <= cy + r; ++y) {
                    const int step = (y == cy - r || y == cy + r) ? 1 : 2 * r;   // 위아래 줄은 전부, 가운데 줄은 양 끝 칸만
                    for (int x = cx - r; x <= cx + r; x += step) scanCell(u, x, y);
                }
                if (bc == kk && bd[kk - 1] <= r * cs) break;   // 안 본 점은 모두 r*cs보다 멀다
            }
            takeList(u);
        }
    }

    // ---- 이동: 구간 뒤집기만. 항목 = (위치, 방향). 점 p[a]와 r번째 이웃이 이웃해지도록 뒤집는다
    int items() { return 2 * n; }
    bool cand(int item, int r, Move& mv) {
        const int a = item / 2, b = pos[nb[p[a]][r]];
        const int lo = a < b ? a : b, hi = a < b ? b : a;
        if (hi < lo + 2) return false;                       // 이미 이웃이다
        mv.a = (item % 2 == 0) ? lo + 1 : lo;                // 두 점을 이웃으로 만드는 구간은 둘: [lo+1, hi]와 [lo, hi-1]
        mv.b = (item % 2 == 0) ? hi : hi - 1;
        mv.kind = 2; mv.old = 0;
        return true;
    }
    bool any(hc::Random& rng, Move& mv) {
        int a = pick(rng, n), b = pick(rng, n);
        if (a == b) return false;
        if (a > b) hc::swap(a, b);
        mv.kind = 2; mv.a = a; mv.b = b; mv.old = 0;
        return true;
    }
    long long delta(const Move& mv) {                        // 안쪽 간선은 거리가 같아 경계 둘만 바뀐다
        const int a = mv.a, b = mv.b;
        return w(at(a - 1), p[b]) + w(p[a], at(b + 1)) - w(at(a - 1), p[a]) - w(p[b], at(b + 1));
    }
    void apply(const Move& mv) {
        for (int i = mv.a, j = mv.b; i < j; ++i, --j) hc::swap(p[i], p[j]);
        for (int i = mv.a; i <= mv.b; ++i) pos[p[i]] = i;
        wrote(mv.b - mv.a + 1);
    }
    void undo(const Move& mv) { apply(mv); }
};
```

`delta`는 3번 강의의 구간 뒤집기 식 그대로입니다. 구간 안쪽 간선은 거리가 대칭이라 그대로이고 경계 간선 둘만 바뀝니다.

## 배정 틀 채우기: `Assign`

크기를 키운 변형은 작업 2,000개, 기계 200대, 기계 한 대에 14개까지입니다(기계당 평균 10개). 점수식과 캐시(`load`, `cnt`, `sq`)는 3번 강의와 같고, 이동은 "작업 하나를 다른 기계로 옮기기"만 씁니다(맞바꾸기는 이 강의의 쟁점이 아니라 뺍니다). 후보는 작업마다 추가 비용 `c[i][·]`이 낮은 기계 `kk`대의 목록입니다. 추가 비용이 `0..50`의 작은 정수라 계수 정렬로 (비용, 기계 번호) 순의 목록을 만듭니다.

```cpp snippet=tb-assign
const int AN = 2000, AM = 200, AK = 32;             // 작업 수, 기계 수, 후보 기계 목록 길이의 상한
struct Assign {
    int n, m, k;                                     // 작업 수, 기계 수, 기계 한 대의 작업 수 상한
    int d[AN], c[AN][AM], as[AN];                    // 길이, 추가 비용, 배정(as[i] = 작업 i를 맡은 기계)
    int load[AM], cnt[AM];                           // 캐시: 기계별 부하 합, 작업 수
    long long sq;                                    // 캐시: 부하 제곱의 합
    int kk, cl[AN][AK];                              // 후보 기계 목록: cl[i][r] = 작업 i의 추가 비용이 r번째로 낮은 기계
    long long ops, writes, props, reads;

    void init() {                                    // 라운드 로빈 배정. 연산 수에 넣지 않는다
        for (int i = 0; i < n; ++i) as[i] = i % m;
        for (int j = 0; j < m; ++j) load[j] = cnt[j] = 0;
        for (int i = 0; i < n; ++i) { load[as[i]] += d[i]; ++cnt[as[i]]; }
        sq = 0;
        for (int j = 0; j < m; ++j) sq += (long long)load[j] * load[j];
        ops = writes = props = reads = 0;
    }
    long long jobTerm(int i, int j) { ++ops; return c[i][j]; }
    long long loadTerm(long long l) { ++ops; return l * l; }
    long long fullCost() {
        long long L[AM], s = 0, sumSq = 0;
        for (int j = 0; j < m; ++j) L[j] = 0;
        for (int i = 0; i < n; ++i) { L[as[i]] += d[i]; s += jobTerm(i, as[i]); }
        for (int j = 0; j < m; ++j) sumSq += loadTerm(L[j]);
        return sumSq / 100 + s;
    }
    bool valid() {
        int count[AM];
        for (int j = 0; j < m; ++j) count[j] = 0;
        for (int i = 0; i < n; ++i) {
            if (as[i] < 0 || as[i] >= m) return false;
            if (++count[as[i]] > k) return false;
        }
        return true;
    }

    // ---- 후보 기계 목록: 작업마다 추가 비용이 낮은 기계 kk대를 (비용, 기계 번호) 순으로. 비용이 0..50이라 계수 정렬을 쓴다
    void buildCand(int kc) {
        kk = kc;
        for (int i = 0; i < n; ++i) {
            int start[52], order[AM];
            hc::fill(start, 52, 0);
            for (int j = 0; j < m; ++j) ++start[c[i][j] + 1];
            for (int v = 0; v < 51; ++v) start[v + 1] += start[v];
            for (int j = 0; j < m; ++j) order[start[c[i][j]]++] = j;
            for (int r = 0; r < kk; ++r) cl[i][r] = order[r];
            ops += 2 * m + 51;                       // 세기, 놓기, 누적합
        }
    }

    // ---- 이동: 작업을 후보 기계로 옮기기만
    int items() { return n; }
    bool cand(int i, int r, Move& mv) {
        const int y = cl[i][r];
        if (y == as[i] || cnt[y] >= k) return false;       // 받는 쪽이 가득 차면 무효: 만들지 않는다
        mv.kind = 0; mv.a = i; mv.b = y; mv.old = as[i];
        return true;
    }
    bool any(hc::Random& rng, Move& mv) {
        const int i = pick(rng, n), y = pick(rng, m);
        if (y == as[i] || cnt[y] >= k) return false;
        mv.kind = 0; mv.a = i; mv.b = y; mv.old = as[i];
        return true;
    }
    long long delta(const Move& mv) {                        // 작업 항 하나와 기계 항 둘
        const int i = mv.a, x = as[i], y = mv.b;
        const long long dc = jobTerm(i, y) - jobTerm(i, x);
        const long long dS = loadTerm(load[x] - d[i]) + loadTerm(load[y] + d[i]) - loadTerm(load[x]) - loadTerm(load[y]);
        return (sq + dS) / 100 - sq / 100 + dc;
    }
    void apply(const Move& mv) {
        const int i = mv.a, x = as[i], y = mv.b;
        sq -= (long long)load[x] * load[x] + (long long)load[y] * load[y];
        load[x] -= d[i]; load[y] += d[i];
        sq += (long long)load[x] * load[x] + (long long)load[y] * load[y];
        --cnt[x]; ++cnt[y]; as[i] = y; ++ops; ++writes;
    }
    void undo(const Move& mv) { Move back = mv; back.b = mv.old; apply(back); }
};
```

후보 목록을 만드는 연산은 작업마다 `2m + 51`입니다(기계 수 `m`을 두 번 훑고 비용 값의 개수 51을 누적합). 작업 2,000개와 기계 200대에서는 이 목록 하나가 902,000이므로 예산이 그보다 작으면 목록을 만드는 일 자체가 손해입니다([실험과 점검](practice.md)).

## 입력 생성과 실행

입력은 [연습용 문제 틀](idea.md)의 규칙(난수 `(x >> 33) % 범위`)대로 시드 하나에서 만듭니다. 점의 좌표는 `x`, `y` 순서로, 배정은 작업마다 길이 다음에 기계 순서로 추가 비용을 뽑습니다. 점 수 `n`과 기계 수만 키웠습니다. 탐색에 쓰는 `hc::Random`은 같은 시드로 따로 시작합니다.

```cpp snippet=tb-gen
struct Gen {                             // 입력 생성용 64비트 난수. 탐색용 hc::Random과 따로 둔다.
    unsigned long long x;
    void reset(unsigned long long seed) { x = seed; }
    int next(int range) {                // [0, range)
        x = x * 6364136223846793005ULL + 1442695040888963407ULL;
        return (int)((x >> 33) % (unsigned long long)range);
    }
};

int isqrt(int v) { int r = 0; while ((r + 1) * (r + 1) <= v) ++r; return r; }

void genRoute(Route& r, unsigned long long seed, int n) {
    Gen g; g.reset(seed);
    r.n = n;
    for (int i = 0; i < n; ++i) { r.px[i] = g.next(1000); r.py[i] = g.next(1000); }
    r.ops = r.writes = r.props = r.reads = 0; r.kk = 0;
}

void genAssign(Assign& a, unsigned long long seed, int n, int m, int k) {
    Gen g; g.reset(seed);
    a.n = n; a.m = m; a.k = k;
    for (int i = 0; i < n; ++i) {
        a.d[i] = 1 + g.next(100);
        for (int j = 0; j < m; ++j) a.c[i][j] = g.next(51);
    }
    a.init();
}
```

```cpp snippet=tb-run
static Route route;
static Assign assign;

// 한 칸에 점이 2개쯤 들어오는 한 변: 점 하나가 차지하는 넓이 10^6 / n의 두 배의 제곱근.
int defaultSide(int n) { const int s = isqrt(2000000 / n); return s < 5 ? 5 : s; }

// 순서 문제: 시드 seed의 점 n개. 초기해(칸 뱀 순서) → 이웃 목록 k개(grid면 칸, 아니면 전수) → 계획 pl대로 탐색.
// 시작 비용을 구하는 fullCost 호출은 예산에 넣지 않으려고 계수기를 되돌린다.
long long runRoute(unsigned long long seed, int n, int k, bool grid, const Plan& pl) {
    genRoute(route, seed, n);
    route.buildCells(defaultSide(n));
    route.initSnake();
    if (k > 0) { if (grid) route.buildNbGrid(k); else route.buildNbBrute(k); }
    const long long saved = route.ops;
    const long long start = route.fullCost();
    route.ops = saved;
    hc::Random rng; rng.reset((unsigned)seed);
    return climbPlan(route, rng, start, pl);
}

// 배정 문제: 작업 2000개, 기계 200대, 기계당 14개. 후보 기계 목록은 k개(0이면 목록 없이 무작위 기계).
long long runAssign(unsigned long long seed, int k, const Plan& pl) {
    genAssign(assign, seed, 2000, 200, 14);
    if (k > 0) assign.buildCand(k);
    const long long saved = assign.ops;
    const long long start = assign.fullCost();
    assign.ops = saved;
    hc::Random rng; rng.reset((unsigned)seed);
    return climbPlan(assign, rng, start, pl);
}
```

두 실행 함수는 같은 순서로 일합니다. 입력 → 초기해와 후보 목록(연산 수에 포함) → 계획대로 탐색. 점의 칸 한 변은 한 칸에 점이 2개쯤 들어오도록(`n = 2000`이면 31, `n = 10000`이면 14) 정합니다. 시작 비용을 구하는 `fullCost`는 보고용이라 계수기를 되돌립니다. [실험과 점검](practice.md)의 표는 모두 이 두 함수로 시드 1~20을 돌린 값입니다.

## 검사 틀을 쓰는 법

후보를 줄이는 코드의 오류는 대부분 조용합니다. 컴파일도 실행도 되고 점수만 조금 나빠집니다. 그래서 아래 다섯 가지를 문제와 별도로 둡니다.

1. **목록 대 전수:** 칸으로 만든 이웃 목록이 전수로 만든 목록과 같은지 점마다 비교합니다. 전수 쪽은 `buildNbBrute`와 따로 정렬로 만든 참조도 대조합니다. 입력은 점 2,000개(시드 20개 전부)와 10,000개(시드 1개)입니다.
2. **불변식:** 탐색이 끝난 뒤 `valid()`(순열이고 `pos`가 `p`의 역)가 참입니다.
3. **후보 이동이 의도한 것을 만드는지:** `cand`로 만든 이동을 적용하면 점 `p[a]`와 후보 이웃이 실제로 이웃해야 하고, `delta`는 적용 전후의 전체 재계산 차이와 같아야 합니다.
4. **남은 비율의 방향:** 후보 수가 `kFirst`에서 `kLast`로 줄어드는 계획이라면 초반에 `kFirst` 근처를, 종반에 `kLast` 근처를 씁니다. 이동을 만들지 않는 가짜 문제(`items() = 1`)에 루프를 돌려 초반·종반에 요청된 가장 큰 후보 번호를 재면 됩니다.
5. **상한 넘침:** 끝난 뒤의 `ops - limit`이 `every`에 한 번의 제안이 쓸 수 있는 가장 큰 연산을 곱한 값 이하입니다.

## 코드를 다른 문제에 옮길 때 바뀌는 곳

| 부분 | 순서 틀 | 배정 틀 | 새 문제에서 |
| --- | --- | --- | --- |
| 해와 캐시 | `p[]`, `pos[]` | `as[]`, `load`, `cnt`, `sq` | 해와 `delta`가 쓰는 캐시. 위치처럼 후보 이동이 읽는 역배열 |
| 후보 목록 | 점마다 가까운 `kk`개(칸 탐색) | 작업마다 싼 `kk`대(계수 정렬) | 항목마다 "좋은 이동을 만들 만한" 상대의 목록. 정렬 기준이 점수식에서 나온다 |
| `items`, `cand` | (위치, 방향), 구간 뒤집기 | 작업, 옮기기 | 항목 수와 후보로 이동을 만드는 규칙 |
| `any` | 두 위치 무작위 | 작업·기계 무작위 | 후보 없는 기준 방식 |
| `delta`, `apply` | 3번 강의 | 3번 강의 | 건드리는 항의 새 값 − 옛 값 |
| 연산 세기 | 점수식 항, 쓰기, 목록 만들기 | 같음 | 새로 생긴 일에 단위를 하나 정해 센다 |
| 계획, `climbPlan`, `sweepAll`, `byRemaining` | 그대로 | 그대로 | 그대로 |
