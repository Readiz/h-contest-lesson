# 구현: 빔 서치 틀과 두 문제 유형

[원리와 손계산](idea.md)을 코드로 옮깁니다. 코드는 두 부분입니다. 문제와 상관없이 그대로 쓰는 `Beam`(평가 → 합치기와 묶음 상한 → 상위 `W`개 → 상태 만들기와 (부모, 행동) 기록 → 경로 복원)과, 문제마다 채우는 `Grid`, `Route`입니다. 채우는 쪽에는 같은 이름의 멤버를 두므로 문제가 바뀌어도 `Beam`은 한 글자도 고치지 않습니다. 두 문제 유형은 [연습용 문제 틀](idea.md)에 정의한 격자 수집(주 예시)과 순서 문제입니다.

> **코드 환경: h-contest 제출용 코드.** 표준 헤더·STL·동적 할당 없이 고정 배열로 씁니다. 공통 블록 `random`, `min-heap`, `sort`([공통 라이브러리](https://h.readiz.com/learn/cpp-common-library))를 먼저 붙이고, 이 페이지의 `bs-frame`, `bs-merge-sort`, `bs-grid`, `bs-route`, `bs-gen`, `bs-run`, `bs-check`를 이 순서로 이어 붙이면 한 번역 단위로 컴파일됩니다. 이 강의의 코드는 입출력이 없는 라이브러리 형태이며, 실제 문제에 쓸 때는 문제의 입력으로 `Grid`나 `Route`의 배열을 채우는 부분만 바꿉니다. `bs-merge-sort`는 합치기를 정렬로 하는 대안이라 `Beam`이 쓰지 않으며, `sort` 블록은 이것만 씁니다.

## 문제와 무관한 부분: `Beam`

`Beam<P, WMAX, CMAX>`는 문제 `P`를 한 번 돌려 행동의 열을 `path[]`에 남깁니다. `WMAX`는 폭의 상한, `CMAX`는 한 단계의 후보 수의 상한(`WMAX × 행동 수의 상한`)이고 둘 다 배열 크기로 쓰입니다. 채우는 쪽(`P`)이 가져야 할 멤버는 아래와 같습니다.

| 멤버 | 하는 일 | 지켜야 할 점 |
| --- | --- | --- |
| `State` | 상태 하나를 담는 고정 크기 구조체 | 요약만 담는다. 경로는 넣지 않는다. 복사가 싸야 한다 |
| `MAXA`, `DEPTH`, `GROUPS`, `ELEMS` | 행동 수·깊이·묶음 수의 상한, 상태의 원소 수 | 배열 크기와 복사량 계수에 쓴다 |
| `steps` | 결정 횟수 | `DEPTH` 이하 |
| `root(s)` | 시작 상태 | |
| `actions(s, act)` | 가능한 행동을 `act[]`에 담고 개수를 돌려준다 | 무효한 행동은 만들지 않는다. 담는 순서가 동점 규칙이 된다 |
| `evalChild(s, a, c)` | 상태를 복사하지 않고 행동 `a`를 한 뒤의 평가값·키·묶음 번호를 `c`에 채운다 | 평가값은 클수록 좋다. 같은 상태는 같은 키 |
| `refine(s, a, c)` | 비싼 2단계 평가로 `c.eval`을 바꾼다 | 쓰지 않으면 빈 함수 |
| `apply(s, a, out)` | 자식 상태를 `out`에 만든다 | 부모 `s`를 바꾸지 않는다 |
| `score(s)` | 상태의 실제 점수 | 추정이 들어가지 않는다. 클수록 좋게(최소화 문제는 음수) |

`Beam`의 설정과 계수기는 아래와 같습니다. 계수기는 실험용이며 제출할 때 지워도 동작이 같습니다.

| 이름 | 뜻 |
| --- | --- |
| `width` | 폭 `W`. `WMAX` 이하여야 한다 |
| `refineK` | 2단계 평가에 올릴 후보 수. `width`보다 크면 쓰고, 아니면 쓰지 않는다. `WMAX` 이하여야 한다 |
| `quota` | 묶음(예: 후보가 가는 칸)마다 남길 후보의 상한. 0이면 쓰지 않는다. `QMAX = 8` 이하 |
| `jitter` | 평가값에 `0 .. jitter − 1`의 무작위 값을 섞는다(평가값은 `jitter`배 해서 비교). 1이면 쓰지 않는다 |
| `merge` | 같은 상태 합치기 |
| `evals`, `refined` | 평가한 후보 수, 2단계 평가한 후보 수 |
| `copied`, `copiedWhole` | 새 상태를 만들며 복사한 원소 수, 후보마다 상태와 경로를 통째로 복사했다면 들었을 원소 수 |
| `dropped` | 폭 때문에 버린 후보 수(합치기·묶음 상한으로 버린 것은 제외) |
| `distinctSum`, `sizeSum` | 단계마다 빔 안의 서로 다른 상태 수의 합, 빔 크기의 합 |

```cpp snippet=bs-frame
struct Cand {
    long long eval;                    // 클수록 좋다(최소화 문제는 음수로 둔다)
    unsigned long long key;            // 같은 상태면 같은 값
    int parent, act, group;            // 지금 빔 안의 부모 번호, 행동, 다양성 묶음 번호
    bool dead;                         // 합쳐지거나 묶음 상한에 걸려 버려졌다
};

unsigned long long mix64(unsigned long long x) {          // 상태 키를 만드는 섞기(splitmix64)
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

template <class P, int WMAX, int CMAX>
struct Beam {
    typedef typename P::State S;
    static const int QMAX = 8, HS = 4 * CMAX;
    S bufA[WMAX], bufB[WMAX];
    int logParent[P::DEPTH][WMAX], logAct[P::DEPTH][WMAX];     // 단계마다 (부모 번호, 행동)만 남긴다
    Cand cand[CMAX];
    int hidx[HS]; unsigned hstamp[HS], hnow;                   // 같은 키를 찾는 해시 표(단계마다 hnow를 올려 비운다)
    int gcnt[P::GROUPS], gbest[P::GROUPS][QMAX]; unsigned gstamp[P::GROUPS], gnow;
    hc::MinHeap<WMAX> heap;
    int pick[WMAX], path[P::DEPTH];
    int width, refineK, quota, jitter;                         // 설정: 폭, 2단계 평가에 올릴 후보 수(0이면 없음), 묶음당 상한(0이면 없음), 평가값 흔들기(1이면 없음)
    bool merge;                                                // 같은 상태 합치기
    long long evals, refined, copied, copiedWhole, dropped;    // 센 값: 평가·2단계 평가 횟수, 복사한 원소 수, 통째 복사 방식이었다면의 원소 수, 폭 때문에 버린 후보 수
    long long distinctSum, sizeSum;                            // 진단: 단계마다 빔 안의 서로 다른 상태 수의 합, 빔 크기의 합
    S* fin; int finalSize, lastC;                              // 마지막 빔과 마지막 단계의 후보 수(검사용)

    void mergeSame(int C) {                                    // 키가 같은 후보 중 평가값이 큰 것 하나만 남긴다
        ++hnow;
        for (int i = 0; i < C; ++i) {
            int h = (int)(cand[i].key % HS);
            while (hstamp[h] == hnow) {
                Cand& o = cand[hidx[h]];
                if (o.key == cand[i].key) {
                    if (cand[i].eval > o.eval) { o.dead = true; hidx[h] = i; } else cand[i].dead = true;
                    break;
                }
                if (++h == HS) h = 0;
            }
            if (!cand[i].dead && hstamp[h] != hnow) { hstamp[h] = hnow; hidx[h] = i; }
        }
    }
    int countDistinct(int m) {                                 // 고른 후보 중 서로 다른 키의 수
        ++hnow;
        int distinct = 0;
        for (int j = 0; j < m; ++j) {
            const unsigned long long key = cand[pick[j]].key;
            int h = (int)(key % HS);
            bool found = false;
            while (hstamp[h] == hnow) {
                if (cand[hidx[h]].key == key) { found = true; break; }
                if (++h == HS) h = 0;
            }
            if (!found) { hstamp[h] = hnow; hidx[h] = pick[j]; ++distinct; }
        }
        return distinct;
    }
    void capGroups(int C) {                                    // 묶음마다 평가값이 큰 quota개만 남긴다
        ++gnow;
        for (int i = 0; i < C; ++i) {
            if (cand[i].dead) continue;
            const int g = cand[i].group;
            if (gstamp[g] != gnow) { gstamp[g] = gnow; gcnt[g] = 0; }
            int pos;
            if (gcnt[g] < quota) pos = gcnt[g]++;
            else if (cand[i].eval <= cand[gbest[g][quota - 1]].eval) continue;
            else pos = quota - 1;
            while (pos > 0 && cand[gbest[g][pos - 1]].eval < cand[i].eval) { gbest[g][pos] = gbest[g][pos - 1]; --pos; }
            gbest[g][pos] = i;
        }
        for (int i = 0; i < C; ++i) {
            if (cand[i].dead) continue;
            const int g = cand[i].group;
            bool keep = false;
            for (int t = 0; t < gcnt[g]; ++t) if (gbest[g][t] == i) keep = true;
            if (!keep) cand[i].dead = true;
        }
    }
    int pickBest(int C, int k) {                               // 살아 있는 후보 중 평가값 상위 k개(동점은 앞선 후보). pick[]에 번호를 담는다
        heap.clear();
        for (int i = 0; i < C; ++i) {
            if (cand[i].dead) continue;
            if (heap.size < k) heap.push(cand[i].eval, CMAX - 1 - i);
            else {
                hc::HeapItem top;
                heap.top(top);
                if (cand[i].eval > top.key) { hc::HeapItem out; heap.pop(out); heap.push(cand[i].eval, CMAX - 1 - i); }
            }
        }
        int m = 0;
        hc::HeapItem it;
        while (heap.pop(it)) pick[m++] = CMAX - 1 - it.id;
        return m;
    }

    long long run(P& p, hc::Random& rng) {                     // 반환: 마지막 빔의 최고 점수. 경로는 path[0..steps)
        S* a = bufA; S* b = bufB;
        int n = 1;
        p.root(a[0]);
        evals = refined = copied = copiedWhole = dropped = distinctSum = sizeSum = 0;
        for (int d = 0; d < p.steps; ++d) {
            int C = 0, acts[P::MAXA];
            for (int i = 0; i < n; ++i) {                      // 1. 빔의 상태마다 모든 행동을 평가한다(상태는 복사하지 않는다)
                const int na = p.actions(a[i], acts);
                for (int k = 0; k < na; ++k) {
                    Cand& c = cand[C++];
                    c.parent = i; c.act = acts[k]; c.dead = false;
                    p.evalChild(a[i], acts[k], c);
                    if (jitter > 1) c.eval = c.eval * jitter + (long long)rng.below((unsigned)jitter);
                }
            }
            evals += C; lastC = C;
            copiedWhole += (long long)C * (P::ELEMS + d + 1);
            if (merge) mergeSame(C);                           // 2. 같은 상태를 합치고 묶음별 상한을 건다
            if (quota > 0) capGroups(C);
            int alive = 0;
            for (int i = 0; i < C; ++i) if (!cand[i].dead) ++alive;
            int m = pickBest(C, refineK > width ? refineK : width);    // 3. 상위만 남긴다
            if (refineK > width) {                             // 비싼 평가는 남은 후보에만 한다
                for (int i = 0; i < C; ++i) cand[i].dead = true;
                for (int j = 0; j < m; ++j) { Cand& c = cand[pick[j]]; c.dead = false; p.refine(a[c.parent], c.act, c); }
                refined += m;
                m = pickBest(C, width);
            }
            dropped += alive - m;
            sizeSum += m;
            distinctSum += countDistinct(m);
            for (int j = 0; j < m; ++j) {                      // 4. 살아남은 것만 상태를 만들고 (부모, 행동)을 기록한다
                const Cand& c = cand[pick[j]];
                logParent[d][j] = c.parent; logAct[d][j] = c.act;
                p.apply(a[c.parent], c.act, b[j]);
                copied += P::ELEMS;
            }
            S* t = a; a = b; b = t;
            n = m;
        }
        int best = 0;
        for (int j = 1; j < n; ++j) if (p.score(a[j]) > p.score(a[best])) best = j;
        fin = a; finalSize = n;
        int j = best;
        for (int d = p.steps - 1; d >= 0; --d) { path[d] = logAct[d][j]; j = logParent[d][j]; }   // 5. 경로를 거꾸로 복원한다
        return p.score(a[best]);
    }
};
```

한 단계는 `run`의 `for` 안에서 번호 순서대로 일어납니다.

1. **평가.** 빔의 상태 `a[i]`와 행동 `acts[k]`마다 `Cand` 하나를 만들고 `evalChild`로 평가값·키·묶음을 채웁니다. 상태는 복사하지 않습니다. `Cand`에는 부모 번호 `parent`(= 지금 빔 안의 `i`)와 행동만 있습니다.
2. **합치기와 묶음 상한.** `mergeSame`은 키가 같은 후보 중 평가값이 큰 것 하나만 남깁니다. 키 → 후보 번호의 해시 표는 열린 주소 방식이고, 단계마다 `hnow`를 올려 표 전체를 비우지 않고 씁니다. `capGroups`는 묶음마다 평가값이 큰 `quota`개만 남깁니다.
3. **추리기.** `pickBest`는 크기 `k`의 `min-heap`에 후보를 넣어 평가값 상위 `k`개를 고릅니다. 힙의 맨 위(가장 작은 값)가 지금까지 고른 것 중 가장 나쁜 후보이므로, 새 후보가 그보다 크면 맨 위를 빼고 넣습니다. 평가값이 같은 후보 사이에서는 번호가 앞선 후보가 남습니다(힙의 `id`를 `CMAX − 1 − 후보 번호`로 넣어 번호가 큰 후보가 먼저 밀려납니다). `refineK`가 있으면 먼저 `refineK`개로 추려 `refine`으로 평가값을 바꾸고 다시 `width`개로 추립니다. 비싼 평가는 소수의 후보에만 합니다.
4. **상태 만들기와 기록.** 남은 후보에 대해서만 `apply`로 새 상태를 만들고 `logParent[d][j]`(이전 단계 빔 안의 부모 번호), `logAct[d][j]`(행동)를 적습니다. 새 빔의 `j`번째 상태는 `b[j]`이고 `pick[j]`번 후보에서 나왔습니다. 부모 번호는 후보의 `parent`이며 후보 번호 `pick[j]`가 아닙니다.
5. **경로 복원.** 마지막 빔에서 `score`가 가장 큰 상태를 고르고, `logParent`를 따라 `d`를 줄이며 `logAct`를 읽습니다.

상태를 새로 만드는 곳은 4번뿐이고 복사량은 단계마다 `width × ELEMS`입니다. 후보마다 상태와 지금까지의 경로를 복사하는 방식이었다면 단계 `d`에서 `후보 수 × (ELEMS + d + 1)`개를 복사했을 것이고, 이 값을 `copiedWhole`에 더해 둡니다. 두 값의 차이가 [실험과 점검](practice.md)의 복사 비용 표입니다.

### 합치기를 정렬로 하기

해시 표 대신 후보를 키 순서로 정렬하면 같은 키가 이웃하므로 이웃한 것끼리만 비교하면 됩니다. 시간은 후보 수 `C`에 대해 `O(C log C)`로, 해시 표의 `O(C)`보다 크지만 표가 필요 없습니다. 아래 함수는 위 `mergeSame`과 같은 후보를 버립니다(검사 스크립트가 같은 후보 집합에서 두 결과를 대조합니다).

```cpp snippet=bs-merge-sort
// 합치기를 정렬로 하는 방법: 후보 번호를 키 순서로 늘어놓으면 같은 키가 이웃하므로, 이웃한 것끼리만 비교하면 된다.
// keyBuf, id, tmp는 호출하는 쪽이 후보 수 이상으로 준비한다. 동점이면 번호가 앞선 후보가 남는다(mergeSame과 같다).
void mergeBySort(Cand cand[], int C, long long keyBuf[], int id[], int tmp[]) {
    for (int i = 0; i < C; ++i) { keyBuf[i] = (long long)cand[i].key; id[i] = i; }
    hc::sortIds(id, tmp, C, keyBuf);                           // 키, 같으면 번호 순서
    int held = C > 0 ? id[0] : -1;                             // 지금 키에서 남기기로 한 후보
    for (int s = 1; s < C; ++s) {
        const int i = id[s];
        if (cand[i].key != cand[held].key) { held = i; continue; }
        if (cand[i].eval > cand[held].eval) { cand[held].dead = true; held = i; } else cand[i].dead = true;
    }
}
```

## 격자 수집 채우기: `Grid`

상태는 밟은 칸의 비트 집합 `vis`, 그 집합의 키 `vkey`, 현재 칸 `pos`, 얻은 값 `got`이고, 행동은 도착할 칸 번호입니다. 같은 상태의 키는 밟은 칸의 키(칸마다 난수를 XOR한 값)와 현재 칸의 난수를 XOR한 값입니다. 칸을 처음 밟을 때만 `vkey`에 그 칸이 들어가므로, 어떤 순서로 밟았는지와 무관하게 같은 집합은 같은 `vkey`가 됩니다. 현재 칸의 난수를 빼면 마지막 칸이 다른 상태가 같은 키가 되어 합쳐집니다([실험과 점검](practice.md)의 흔한 실수 1).

평가값은 `얻은 값 × scale + estimate`이고 `estimate`가 평가 함수의 설계 부분입니다. `est`로 고릅니다.

- `est = 0`: 추정 없음. 평가값이 얻은 값입니다.
- `est = 1`: 가까운 값의 합. 후보가 가는 칸에서 거리 `d ≤ radius`인 안 밟은 칸의 `값 × (radius + 1 − d)`의 합입니다. 가까울수록 크게 세어 앞으로 얻을 값을 추정합니다.
- `est = 2`: 거리 벌점. 값이 있는(0보다 큰) 가장 가까운 안 밟은 칸까지의 거리를 뺍니다. 반경 안에 없으면 `radius + 1`을 뺍니다.

`scale`은 점수 한 점이 추정의 몇 단위인지입니다. 기본은 `scale = 8`, `radius = 3`입니다. 추정이 점수를 이기지 않도록 `scale`을 추정의 크기에 맞춥니다([실험과 점검](practice.md)의 무게 표). `work`는 추정이 살펴본 칸 수로, 추정의 비용을 셉니다.

```cpp snippet=bs-grid
struct GridState { unsigned long long vis[7]; unsigned long long vkey; int pos, got; };   // 밟은 칸 비트, 밟은 칸의 키, 위치, 얻은 값

struct Grid {                                      // 순차 결정 틀(격자 수집). 행동 = 도착할 칸 번호
    typedef GridState State;
    static const int MAXA = 4, DEPTH = 60, GROUPS = 400, ELEMS = 10;   // 행동 수·깊이·묶음 수의 상한, 상태의 원소 수
    int h, w, steps;                               // 크기, 움직일 횟수
    int est, scale, radius;                        // 추정 방식(0 없음, 1 가까운 값의 합, 2 가까운 값까지의 거리 벌점), 점수 한 점의 무게, 살필 거리
    int v[400];
    unsigned long long zcell[400], zpos[400];      // 키 재료: 밟은 칸마다, 현재 칸마다
    long long work;                                // 추정에서 살펴본 칸 수

    bool seen(const State& s, int c) const { return (s.vis[c >> 6] >> (c & 63)) & 1ULL; }
    void root(State& s) {
        for (int i = 0; i < 7; ++i) s.vis[i] = 0;
        s.vis[0] = 1; s.vkey = zcell[0]; s.pos = 0; s.got = v[0];
    }
    int actions(const State& s, int act[]) {       // 위, 오른쪽, 아래, 왼쪽 순서
        int n = 0;
        const int y = s.pos / w, x = s.pos % w;
        if (y > 0) act[n++] = s.pos - w;
        if (x + 1 < w) act[n++] = s.pos + 1;
        if (y + 1 < h) act[n++] = s.pos + w;
        if (x > 0) act[n++] = s.pos - 1;
        return n;
    }
    long long estimate(const State& s, int a) {    // a로 간 뒤 앞으로 얻을 값의 추정. 단위는 점수 한 점 = scale
        if (est == 0) return 0;
        const int ay = a / w, ax = a % w;
        long long sum = 0;
        int nearest = 0;
        for (int d = 1; d <= radius; ++d) {        // a에서 거리 d인 칸을 살핀다
            for (int dy = -d; dy <= d; ++dy) {
                const int y = ay + dy, rest = d - (dy < 0 ? -dy : dy);
                if (y < 0 || y >= h) continue;
                for (int k = 0; k < (rest == 0 ? 1 : 2); ++k) {
                    const int x = ax + (k == 0 ? rest : -rest);
                    if (x < 0 || x >= w) continue;
                    ++work;
                    const int c = y * w + x;
                    if (seen(s, c)) continue;
                    if (est == 1) sum += (long long)v[c] * (radius + 1 - d);
                    else if (v[c] > 0 && nearest == 0) nearest = d;
                }
            }
            if (est == 2 && nearest > 0) break;
        }
        if (est == 1) return sum;                  // 가까울수록 크게 센 남은 값의 합
        return nearest > 0 ? -nearest : -(radius + 1);   // 남은 값까지의 거리 벌점(반경 안에 없으면 가장 큰 벌점)
    }
    void evalChild(const State& s, int a, Cand& c) {
        const bool fresh = !seen(s, a);
        const int got = s.got + (fresh ? v[a] : 0);
        c.key = (s.vkey ^ (fresh ? zcell[a] : 0ULL)) ^ zpos[a];   // 밟은 칸의 집합과 현재 칸이 같으면 같은 키
        c.group = a;
        c.eval = (long long)got * scale + estimate(s, a);
    }
    void refine(const State&, int, Cand&) {}       // 2단계 평가를 쓰지 않는다
    void apply(const State& s, int a, State& out) {
        out = s;
        if (!seen(s, a)) { out.vis[a >> 6] |= 1ULL << (a & 63); out.vkey ^= zcell[a]; out.got += v[a]; }
        out.pos = a;
    }
    long long score(const State& s) const { return s.got; }
};
```

## 순서 문제 채우기: `Route`

상태는 지난 점의 비트 집합 `vis`, 그 키 `vkey`, 마지막 점 `last`, 비용 `cost`, 안 간 점의 `nn` 합 `rest`입니다. 행동은 아직 안 간 점 번호입니다. 점수는 비용이므로 `score`와 평가값에 음수를 씁니다. `est`로 평가 함수를 고릅니다.

- `est = 0`: 추정 없음. 평가값이 `−비용`입니다.
- `est = 1`: 낙관적 합. `−(비용 + rest)`이고, `rest`는 안 간 점 `u`마다 `u`에서 가장 가까운 다른 점까지의 거리 `nn[u]`의 합입니다. 안 간 점은 모두 앞으로 한 번씩 들어와야 하고, 들어오는 간선의 길이는 그 점의 `nn` 이상이므로 `rest`는 남은 비용의 하한입니다. `nn`은 입력에서 한 번만 구하고(`prepare`), 상태에는 합만 들고 다니며 점을 지날 때 `nn[a]`를 뺍니다.
- `est = 2`: `est = 1`로 `refineK`개의 후보를 추린 뒤, 그 후보에 `refine`으로 평가값을 `−(비용 + 탐욕 완성 비용)`으로 바꿉니다. 탐욕 완성 비용은 후보의 점에서 시작해 가장 가까운 안 간 점으로 끝까지 가는 비용입니다(가까운 점이 여럿이면 번호가 작은 점). `est = 2`를 쓸 때는 `refineK`를 `width`보다 크게 줍니다.

`rollout`은 후보 하나에 안 간 점 수의 제곱에 비례하는 일을 하므로, 모든 후보가 아니라 상위 `refineK`개에만 합니다. `work`는 `rollout`이 살펴본 점 수입니다.

```cpp snippet=bs-route
struct RouteState { unsigned long long vis[4]; unsigned long long vkey; int last, cost, rest; };   // 지난 점 비트, 지난 점의 키, 마지막 점, 비용, 남은 점의 nn 합

struct Route {                                     // 순차 결정으로 본 순서 틀. 행동 = 다음에 갈 점 번호
    typedef RouteState State;
    static const int MAXA = 200, DEPTH = 200, GROUPS = 200, ELEMS = 8;
    int n, steps;                                  // 점 수, 결정 횟수(= n)
    int est;                                       // 추정 방식(0 없음, 1 남은 점의 하한 합, 2 = 1 + 상위 후보에 탐욕 완성 비용)
    int px[200], py[200], nn[200];                 // 좌표, nn[u] = u에서 가장 가까운 다른 점까지의 거리
    unsigned long long zpt[200], zlast[200];       // 키 재료: 지난 점마다, 마지막 점마다
    long long work;                                // 추정에서 살펴본 점 수

    int dist(int u, int v) const { return (px[u] < px[v] ? px[v] - px[u] : px[u] - px[v]) + (py[u] < py[v] ? py[v] - py[u] : py[u] - py[v]); }
    bool seen(const State& s, int c) const { return (s.vis[c >> 6] >> (c & 63)) & 1ULL; }
    void prepare() {                               // 입력에서 한 번만 만드는 값
        for (int u = 0; u < n; ++u) {
            int best = 1 << 30;
            for (int v = 0; v < n; ++v) if (v != u && dist(u, v) < best) best = dist(u, v);
            nn[u] = best;
        }
    }
    void root(State& s) {
        for (int i = 0; i < 4; ++i) s.vis[i] = 0;
        s.vkey = 0; s.last = -1; s.cost = 0; s.rest = 0;
        for (int u = 0; u < n; ++u) s.rest += nn[u];
    }
    int actions(const State& s, int act[]) {       // 아직 안 간 점 모두
        int m = 0;
        for (int u = 0; u < n; ++u) if (!seen(s, u)) act[m++] = u;
        return m;
    }
    void evalChild(const State& s, int a, Cand& c) {
        const int cost = s.cost + (s.last < 0 ? 0 : dist(s.last, a));
        const int rest = s.rest - nn[a];           // 남은 점마다 들어오는 간선이 하나씩 있고 그 길이는 nn 이상이다
        c.key = (s.vkey ^ zpt[a]) ^ zlast[a];      // 지난 점의 집합과 마지막 점이 같으면 같은 키
        c.group = a;
        c.eval = -((long long)cost + (est >= 1 ? rest : 0));
    }
    long long rollout(const State& s, int a) {     // a에서 시작해 가장 가까운 안 간 점으로 끝까지 갈 때의 남은 비용
        bool done[200];
        int left = 0;
        for (int u = 0; u < n; ++u) { done[u] = seen(s, u) || u == a; if (!done[u]) ++left; }
        long long total = 0;
        int cur = a;
        while (left > 0) {
            int next = -1, best = 1 << 30;
            for (int u = 0; u < n; ++u) {
                if (done[u]) continue;
                ++work;
                if (dist(cur, u) < best) { best = dist(cur, u); next = u; }
            }
            total += best; done[next] = true; cur = next; --left;
        }
        return total;
    }
    void refine(const State& s, int a, Cand& c) { // est 2: 비용 + 탐욕 완성 비용으로 평가값을 바꾼다
        const int cost = s.cost + (s.last < 0 ? 0 : dist(s.last, a));
        c.eval = -((long long)cost + rollout(s, a));
    }
    void apply(const State& s, int a, State& out) {
        out = s;
        out.cost += (s.last < 0 ? 0 : dist(s.last, a));
        out.rest -= nn[a];
        out.vis[a >> 6] |= 1ULL << (a & 63);
        out.vkey ^= zpt[a];
        out.last = a;
    }
    long long score(const State& s) const { return -(long long)s.cost; }   // 최소화 문제라 음수
};
```

## 입력 생성과 실행

입력은 [연습용 문제 틀](idea.md)의 규칙대로 시드 하나에서 만듭니다. 생성용 난수 `Gen`은 64비트 선형 합동 생성기이고, 탐색용 `hc::Random`과 따로 둡니다. 키 재료는 `mix64`로 칸과 점의 번호에서 만든 고정 값입니다.

```cpp snippet=bs-gen
struct Gen {                             // 입력 생성용 64비트 난수. 탐색용 hc::Random과 따로 둔다.
    unsigned long long x;
    void reset(unsigned long long seed) { x = seed; }
    int next(int range) {                // [0, range)
        x = x * 6364136223846793005ULL + 1442695040888963407ULL;
        return (int)((x >> 33) % (unsigned long long)range);
    }
};

void genGrid(Grid& g, unsigned long long seed, int h, int w, int steps) {
    Gen r; r.reset(seed);
    g.h = h; g.w = w; g.steps = steps; g.est = 0; g.scale = 1; g.radius = 3; g.work = 0;
    for (int c = 0; c < h * w; ++c) {
        const int u = r.next(10);
        g.v[c] = u < 6 ? 0 : 1 + r.next(9);
        g.zcell[c] = mix64(1 + c); g.zpos[c] = mix64(1001 + c);
    }
}

void genRoute(Route& rt, unsigned long long seed, int n) {
    Gen r; r.reset(seed);
    rt.n = n; rt.steps = n; rt.est = 0; rt.work = 0;
    for (int i = 0; i < n; ++i) {
        rt.px[i] = r.next(1000); rt.py[i] = r.next(1000);
        rt.zpt[i] = mix64(1 + i); rt.zlast[i] = mix64(1001 + i);
    }
    rt.prepare();
}
```

실행 함수는 같은 시드를 입력 시드와 탐색 시드로 함께 씁니다. `Beam`은 크기가 큰 배열을 가지고 합치기 표(`hstamp`, `gstamp`)가 0으로 시작해야 하므로 전역 또는 정적 변수로 둡니다. `routeBeam`은 점 200개용이고, `routeSmallBeam`은 점 10개 이하의 작은 입력에서 폭을 상태 수(최대 약 1,260) 이상으로 줄 때 씁니다.

```cpp snippet=bs-run
static Grid grid;
static Route route;
static Beam<Grid, 8192, 32768> gridBeam;
static Beam<Route, 256, 51200> routeBeam;
static Beam<Route, 1536, 16384> routeSmallBeam;      // 점 10개 이하의 작은 입력에서 폭을 상태 수 이상으로 줄 때

// 격자 수집: 시드 seed의 입력(20 × 20, 60번 움직임)을 빔 폭 width로 푼다. 반환값은 얻은 값의 합(클수록 좋음)이고 경로는 gridBeam.path에 있다.
long long solveGrid(unsigned long long seed, int est, int width) {
    genGrid(grid, seed, 20, 20, 60);
    grid.est = est; grid.scale = 8; grid.radius = 3;          // 추정 방식과 그 무게·반경
    gridBeam.width = width; gridBeam.refineK = 0; gridBeam.quota = 0; gridBeam.jitter = 1; gridBeam.merge = true;
    hc::Random rng; rng.reset((unsigned)seed);
    return gridBeam.run(grid, rng);
}

// 순서 문제: 점 200개를 한 점씩 정해 간다. 반환값은 이동 비용(작을수록 좋음)이고 경로(점 번호의 열)는 routeBeam.path에 있다.
long long solveRoute(unsigned long long seed, int est, int width) {
    genRoute(route, seed, 200);
    route.est = est;
    routeBeam.width = width; routeBeam.refineK = est == 2 ? 4 * width : 0; routeBeam.quota = 0; routeBeam.jitter = 1; routeBeam.merge = true;
    hc::Random rng; rng.reset((unsigned)seed);
    return -routeBeam.run(route, rng);
}

// 점 n개(10 이하)의 작은 입력을 폭 width로 푼다. 폭이 상태 수 이상이면 아무것도 버리지 않아 완전 탐색과 같다.
long long solveRouteSmall(unsigned long long seed, int n, int est, int width) {
    genRoute(route, seed, n);
    route.est = est;
    routeSmallBeam.width = width; routeSmallBeam.refineK = 0; routeSmallBeam.quota = 0; routeSmallBeam.jitter = 1; routeSmallBeam.merge = true;
    hc::Random rng; rng.reset((unsigned)seed);
    return -routeSmallBeam.run(route, rng);
}
```

## 검사 틀을 쓰는 법

빔 서치의 오류는 대개 조용히 나쁜 답을 냅니다. 컴파일도 되고 실행도 되고 유효한 답도 나옵니다. 아래 검사를 문제와 별도로 둡니다. 문제마다 `replay*`와 입력의 최적을 구하는 방법만 바뀝니다.

1. **경로 재생.** `run`이 돌려준 점수가 `replayGrid(g, path)`, `replayRoute(r, path)`가 경로를 처음부터 다시 걸어 구한 점수와 같은지, 경로가 규칙을 지키는지 확인합니다. 아래 `bs-check`가 그 함수입니다. 부모 번호 기록이 틀리거나 상태를 잘못 복사하면 경로와 점수가 어긋납니다.
2. **키 대조.** 작은 입력에서 가능한 모든 상태를 만들어 "같은 상태이면 같은 키, 다른 상태이면 다른 키"를 확인합니다. 이 검사가 없으면 키가 상태를 덜 구별해도 점수는 그럴듯하게 나옵니다.
3. **작은 입력의 최적.** 폭을 상태 수 이상으로 주면(`dropped == 0`) 아무것도 버리지 않는 완전 탐색이므로 결과가 독립적인 완전 탐색(모든 걸음, 부분집합 DP)의 최적과 같아야 합니다. 합치기 방향이나 평가 부호를 틀리면 이 검사에서 어긋납니다.
4. **손계산과 대조.** [원리](idea.md)의 작은 예의 표와 코드의 결과(점수, 경로, 평가 횟수)가 같은지 확인합니다.

```cpp snippet=bs-check
// 경로를 처음부터 다시 걸어 점수를 구한다. 규칙을 어기면 -1. 탐색 코드와 따로 쓴 정답지다.
long long replayGrid(const Grid& g, const int path[]) {
    bool seen[400] = {};
    int y = 0, x = 0;
    long long sum = g.v[0];
    seen[0] = true;
    for (int t = 0; t < g.steps; ++t) {
        const int c = path[t];
        if (c < 0 || c >= g.h * g.w) return -1;
        const int cy = c / g.w, cx = c % g.w;
        const int dy = cy > y ? cy - y : y - cy, dx = cx > x ? cx - x : x - cx;
        if (dy + dx != 1) return -1;                  // 이웃한 칸으로만 움직인다
        y = cy; x = cx;
        if (!seen[c]) { seen[c] = true; sum += g.v[c]; }
    }
    return sum;
}

// 점 번호의 열을 처음부터 이어 비용을 구한다. 모든 점을 한 번씩이 아니면 -1.
long long replayRoute(const Route& r, const int path[]) {
    bool seen[200] = {};
    long long cost = 0;
    for (int t = 0; t < r.n; ++t) {
        const int u = path[t];
        if (u < 0 || u >= r.n || seen[u]) return -1;
        seen[u] = true;
        if (t > 0) cost += r.dist(path[t - 1], u);
    }
    return cost;
}
```

## 코드를 다른 문제에 옮길 때 바뀌는 곳

| 부분 | 격자 수집 | 순서 문제 | 새 문제에서 |
| --- | --- | --- | --- |
| `State` | 밟은 칸 비트, 키, 위치, 얻은 값 | 지난 점 비트, 키, 마지막 점, 비용, `nn` 합 | 앞으로의 선택지와 점수를 정하는 요약만 |
| 행동 | 이웃한 칸 | 안 간 점 | 상태에서 할 수 있는 선택(무효는 만들지 않는다) |
| 키 | 밟은 칸의 집합 + 현재 칸 | 지난 점의 집합 + 마지막 점 | 상태를 정하는 요약 전체. 빠진 것이 있으면 다른 상태가 합쳐진다 |
| 평가값 | 얻은 값 × `scale` + 추정 | −(비용 + 추정) | 지금까지 + 앞으로의 추정, 단위를 맞춘다 |
| 묶음 | 도착 칸 | 마지막 점 | 비슷한 상태끼리 묶는 기준 |
| `apply` | 비트·키·얻은 값을 갱신 | 비용·`nn` 합·키를 갱신 | 부모를 바꾸지 않고 자식을 만든다 |
| `score`·`replay` | 얻은 값 | −비용 | 평가값과 별도로 점수식에서 처음부터 |
| `Beam`, `mergeBySort` | 그대로 | 그대로 | 그대로 |
