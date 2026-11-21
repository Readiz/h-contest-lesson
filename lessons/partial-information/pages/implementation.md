# 구현: 거울·추정 지도·계획기와 두 문제 유형

[원리와 손계산](idea.md)을 코드로 옮깁니다. 코드는 두 부분입니다. 문제와 상관없이 같은 모양으로 쓰는 부분(보고 → 결정 → 행동 → 거울 갱신의 한 판 루프, 거울과 채점기의 대조, 엿보기 검사)과 문제마다 채우는 부분(채점기가 보여 주는 것, 거울이 기억하는 것, 모르는 것의 추정, 결정)입니다. 채우는 부분에는 같은 이름의 멤버를 두어 두 문제 유형(격자 수집·온라인 배정, 정의는 [원리](idea.md)의 연습용 문제 틀)이 같은 틀에 들어가게 합니다.

> **코드 환경: h-contest 제출용 코드.** 표준 헤더·STL·동적 할당 없이 고정 배열로 씁니다. 공통 블록 `array`, `sort`([공통 라이브러리](https://h.readiz.com/learn/cpp-common-library))를 먼저 붙이고, 이 페이지의 `pi-grid`, `pi-plan`, `pi-policy`, `pi-online`, `pi-gen`, `pi-run`을 이 순서로 이어 붙이면 한 번역 단위로 컴파일됩니다. 이 강의의 코드는 입출력이 없는 라이브러리 형태입니다. 채점기(`GridJudge`, `OnlineJudge`)는 로컬 실험용 모의이며, 실제 문제에서는 문제가 주는 입력과 호출 함수가 그 자리를 맡고 거울·정책·검사 쪽만 남습니다.

## 문제와 무관한 부분과 채우는 부분

한 판의 흐름은 두 문제에서 같습니다. 채점기가 보여 주는 것을 거울에 기록하고(`observe`), 거울과 추정만으로 행동을 정하고(`act`, 격자에서는 필요할 때 `replan`), 행동을 채점기에 전하고, 그 결과를 거울에 적습니다(`step`, `commit`). 채우는 쪽이 가져야 할 것은 아래와 같습니다.

| 이름 | 하는 일 | 지켜야 할 점 |
| --- | --- | --- |
| `look()`, `arrive()` | (채점기) 지금 보이는 것만 알려 준다 | 감춰진 정보를 다른 길로 주지 않는다 |
| `begin(j)` | 규칙(크기, 이동 횟수, 작업 수)만 읽고 거울을 비운다 | 이전 판의 기록을 남기지 않는다(테스트 케이스마다 초기화) |
| `observe` | 보인 것을 기록한다 | 모르는 것과 본 값을 구분해 둔다. 평균 재료는 처음 본 것만 더한다 |
| `step`, `commit` | 내가 한 행동을 적는다 | 채점기에 되묻지 않고 기억한 값으로 센다 |
| 추정 `guess100`, `lambda` | 모르는 값을 얼마로 칠지 | 관측한 것에서만 만든다 |
| 결정 `act` | 거울과 추정만으로 행동을 정한다 | 채점기의 감춰진 필드를 읽지 않는다 |
| `...MirrorOk`, `...NoPeek` | 검사 | 감춰진 값을 읽는 곳은 검사뿐이다 |

## 격자 수집 채우기 1: 채점기와 거울

`GridJudge`는 진짜 격자를 가지고 `look()`으로 현재 칸에서 거리 `rad` 이내인 칸의 값만 내줍니다. 보여 준 칸을 `shown`에 적어 두는 것은 검사용입니다. `GridMirror`가 이 강의의 핵심 자료구조입니다. 값 `val`과 "마지막으로 본 걸음 번호" `seenAt`을 따로 두고, `seenAt`이 `-1`이면 값을 모르는 칸입니다. 값 `0`을 모름의 표시로 쓰면 "본 0"과 "못 본 칸"이 섞입니다([실험과 점검](practice.md)의 흔한 실수 1). 이 격자의 값은 변하지 않으므로 `seenAt`은 앎 여부를 나타내는 데만 쓰입니다. 값이 바뀌는 환경이라면 이 시점이 "기억한 값이 얼마나 낡았는가"를 알려 줍니다.

평균 재료 `nSeen`, `sumSeen`은 처음 본 칸만 더합니다. 같은 칸이 여러 번 보이므로(걸을 때마다 거리 2 이내가 다시 보입니다) 보일 때마다 더하면 평균이 걸어 다닌 길 주변으로 치우칩니다.

```cpp snippet=pi-grid
const int GN = 400;                        // 칸 수의 상한(20 x 20)

struct GridJudge {                         // 로컬 채점기. 진짜 격자는 여기에만 있다(대회에서는 문제의 입력과 함수가 이 자리를 맡는다).
    int h, w, T, rad;                      // 크기, 이동 횟수, 보이는 거리(맨해튼)
    int v[GN];                             // 칸의 값: 감춰진 정보
    bool got[GN], shown[GN];               // 밟은 칸, 한 번이라도 보여 준 칸(검사용)
    int pos, used;                         // 현재 칸, 쓴 이동 수
    long long score;                       // 지금까지 얻은 값의 합

    void start() {
        hc::fill(got, GN, false); hc::fill(shown, GN, false);
        pos = 0; used = 0; got[0] = true; score = v[0];
    }
    int look(int cell[], int val[]) {      // 현재 칸에서 거리 rad 이내인 칸의 번호와 값을 알려 준다. 개수를 돌려준다.
        int n = 0;
        const int y = pos / w, x = pos % w;
        for (int c = 0; c < h * w; ++c) {
            const int dy = c / w - y, dx = c % w - x;
            if ((dy < 0 ? -dy : dy) + (dx < 0 ? -dx : dx) > rad) continue;
            cell[n] = c; val[n] = v[c]; shown[c] = true; ++n;
        }
        return n;
    }
    bool move(int c) {                     // 이웃한 칸으로 한 걸음. 규칙을 어기면 false(무효)
        if (used >= T || c < 0 || c >= h * w) return false;
        const int dy = c / w - pos / w, dx = c % w - pos % w;
        if ((dy < 0 ? -dy : dy) + (dx < 0 ? -dx : dx) != 1) return false;
        pos = c; ++used;
        if (!got[c]) { got[c] = true; score += v[c]; }
        return true;
    }
};

struct GridMirror {                        // 내 쪽의 거울: 규칙(아는 것), 본 값(기억한 것), 못 본 칸(모르는 것)
    int h, w, T;                           // 아는 것: 규칙
    int val[GN], seenAt[GN];               // 기억한 것: 본 값, 마지막으로 본 걸음 번호(-1이면 한 번도 못 봄 = 값을 모른다)
    bool stepped[GN];                      // 밟은 칸
    int pos, t;                            // 내 위치, 쓴 이동 수
    long long got;                         // 내가 센 얻은 값
    int nSeen; long long sumSeen;          // 값을 아는 칸의 수와 그 값의 합(평균 추정용)

    void begin(const GridJudge& j) {       // 규칙만 읽고 나머지는 비운다
        h = j.h; w = j.w; T = j.T;
        hc::fill(seenAt, GN, -1); hc::fill(val, GN, 0); hc::fill(stepped, GN, false);
        pos = 0; t = 0; got = 0; nSeen = 0; sumSeen = 0;
    }
    void observe(GridJudge& j) {           // 보인 칸을 기록한다. 이미 아는 칸은 시점만 고친다
        int cell[GN], v[GN];
        const int n = j.look(cell, v);
        for (int k = 0; k < n; ++k) {
            const int c = cell[k];
            if (seenAt[c] < 0) { ++nSeen; sumSeen += v[k]; }   // 처음 본 칸만 평균에 넣는다
            val[c] = v[k]; seenAt[c] = t;
        }
        if (!stepped[pos]) { stepped[pos] = true; got += val[pos]; }   // 서 있는 칸의 값은 보인다. 처음 밟는 칸이면 채점기에 묻지 않고 기억한 값으로 센다
    }
    void step(int c) { pos = c; ++t; }     // 내가 움직인 것을 적는다. 도착한 칸의 값은 도착한 뒤 observe에서 센다
};
```

## 격자 수집 채우기 2: 계획기

추정 지도 위에서 앞 몇 걸음을 계획하는 `planBeam`입니다. [빔 서치](https://h.readiz.com/learn/beam-search)의 `Beam`에서 같은 상태 합치기와 (부모, 행동) 기록을 빼고 상태에 경로를 직접 넣은 압축판이라, 같은 경로를 여러 번 세는 후보가 남습니다. 평가값은 5번 강의의 추정 1(`얻은 값 × 8 +` 거리 3 이내 안 밟은 칸의 값 `× (4 − 거리)`의 합)을 씁니다. 입력은 값 지도 `val100`(값의 100배)과 밟은 칸 `stepped`이며 계획기는 이 지도가 진짜인지 추정인지 모릅니다. 진짜 지도를 넣으면 전체 정보 기준선이고, 거울에서 만든 추정 지도를 넣으면 부분 정보의 계획입니다. 폭은 `BW`(128) 이하, 깊이는 `BD`(64) 이하여야 합니다.

```cpp snippet=pi-plan
// 계획기: 값 지도 val100[](x100)와 밟은 칸 stepped[] 위에서 pos에서 출발하는 depth걸음 경로를 빔 서치로 찾는다.
// 5번 강의의 Beam에서 같은 상태 합치기와 부모 기록을 뺀 압축판이다. 지도가 진짜 값이면 전체 정보 기준선, 거울 위의 추정 지도이면 부분 정보의 계획이다.
const int BW = 128, BD = 64;               // 폭과 깊이의 상한
struct BeamState { unsigned long long vis[7]; int pos, gain; unsigned short path[BD]; };   // 밟은 칸 비트, 위치, 얻은 값(x100), 지금까지의 경로

// 반환: 경로가 얻는 값(x100). path[0..depth)에 칸 번호. evals에 평가한 후보 수를 더한다.
long long planBeam(const int val100[], const bool stepped[], int h, int w, int pos, int depth, int width, int path[], long long& evals) {
    static BeamState A[BW], B[BW];
    static int par[4 * BW], cellOf[4 * BW], id[4 * BW], tmp[4 * BW];
    static long long key[4 * BW];
    BeamState* cur = A; BeamState* nxt = B;
    for (int i = 0; i < 7; ++i) cur[0].vis[i] = 0;
    for (int c = 0; c < h * w; ++c) if (stepped[c]) cur[0].vis[c >> 6] |= 1ULL << (c & 63);
    cur[0].pos = pos; cur[0].gain = 0;
    int n = 1;
    for (int t = 0; t < depth; ++t) {
        int C = 0;
        for (int s = 0; s < n; ++s) {
            const BeamState& st = cur[s];
            const int y = st.pos / w, x = st.pos % w;
            int nb[4], k = 0;
            if (y > 0) nb[k++] = st.pos - w;
            if (x + 1 < w) nb[k++] = st.pos + 1;
            if (y + 1 < h) nb[k++] = st.pos + w;
            if (x > 0) nb[k++] = st.pos - 1;
            for (int q = 0; q < k; ++q) {
                const int a = nb[q];
                const bool fresh = !((st.vis[a >> 6] >> (a & 63)) & 1ULL);
                const int gain = st.gain + (fresh ? val100[a] : 0);
                long long near = 0;                                   // 5번 강의의 추정 1: 거리 3 이내 안 밟은 칸의 값 x (4 - 거리)
                const int ay = a / w, ax = a % w;
                for (int dy = -3; dy <= 3; ++dy) for (int dx = -3; dx <= 3; ++dx) {
                    const int d = (dy < 0 ? -dy : dy) + (dx < 0 ? -dx : dx);
                    const int cy = ay + dy, cx = ax + dx;
                    if (d < 1 || d > 3 || cy < 0 || cy >= h || cx < 0 || cx >= w) continue;
                    const int c = cy * w + cx;
                    if (!((st.vis[c >> 6] >> (c & 63)) & 1ULL)) near += (long long)val100[c] * (4 - d);
                }
                ++evals;
                par[C] = s; cellOf[C] = a; key[C] = -((long long)gain * 8 + near); id[C] = C; ++C;
            }
        }
        hc::sortIds(id, tmp, C, key);                                 // 좋은 평가값부터, 같으면 앞선 후보
        n = C < width ? C : width;
        for (int r = 0; r < n; ++r) {
            const int c = id[r], a = cellOf[c];
            nxt[r] = cur[par[c]];
            if (!((nxt[r].vis[a >> 6] >> (a & 63)) & 1ULL)) { nxt[r].vis[a >> 6] |= 1ULL << (a & 63); nxt[r].gain += val100[a]; }
            nxt[r].pos = a; nxt[r].path[t] = (unsigned short)a;
        }
        BeamState* sw = cur; cur = nxt; nxt = sw;
    }
    int best = 0;
    for (int r = 1; r < n; ++r) if (cur[r].gain > cur[best].gain) best = r;
    for (int t = 0; t < depth; ++t) path[t] = cur[best].path[t];
    return cur[best].gain;
}
```

## 격자 수집 채우기 3: 정책, 검사, 한 판

`GridPolicy`가 모르는 칸의 추정(`guess100`), 추정 지도(`buildMap`), 계획(`replan`), 행동(`act`)을 맡습니다. `est100`이 모르는 칸을 얼마로 칠지(100배)이며 `-1`이면 값을 아는 칸의 평균입니다. 비관은 `0`, 낙관은 가능한 최댓값 `900`입니다. `horizon`은 한 번에 계획하는 걸음 수, `period`는 그중 몇 걸음을 실행하고 다시 계획하는지입니다. `period = 1`이면 새로 보일 때마다 계획을 다시 세웁니다.

검사 세 가지가 같은 블록에 있습니다. `gridMirrorOk`는 거울이 채점기와 같은지(위치, 얻은 값, 밟은 칸, 보여 준 칸과 값, 평균 재료), `gridMapOk`는 추정 지도의 아는 칸이 진짜 값이고 모르는 칸이 모두 같은 추정값인지, `gridNoPeek`는 한 번도 보여 주지 않은 칸의 값을 바꿔도 같은 걸음이 나오는지 확인합니다. `playGrid`는 `firstBad`를 주면 매 걸음 뒤 앞의 두 검사를 하고 처음 어긋난 걸음 번호를 적습니다. `planFull`은 진짜 값 지도에서 `T`걸음을 한 번에 계획하는 전체 정보 기준선입니다.

```cpp snippet=pi-policy
struct GridPolicy {
    int est100;                            // 모르는 칸의 값을 얼마로 칠지(x100). -1이면 값을 아는 칸의 평균
    int horizon, period, width;            // 한 번에 계획하는 걸음 수(BD 이하), 그중 몇 걸음 실행하고 다시 계획하는가(horizon 이하), 빔 폭
    int plan[BD], len, at;                 // 지금 계획: 경로, 길이, 다음에 실행할 위치
    long long plans, evals;                // 센 값: 계획한 횟수, 평가한 후보 수

    int guess100(const GridMirror& m) const {          // 모르는 칸 하나의 값(x100)
        if (est100 >= 0) return est100;
        return m.nSeen > 0 ? (int)(100 * m.sumSeen / m.nSeen) : 0;
    }
    void buildMap(const GridMirror& m, int map100[]) const {   // 추정 지도: 아는 칸은 본 값, 모르는 칸은 추정값
        const int guess = guess100(m);
        for (int c = 0; c < m.h * m.w; ++c) map100[c] = m.seenAt[c] >= 0 ? 100 * m.val[c] : guess;
    }
    void replan(const GridMirror& m) {                 // 거울과 추정만으로 계획한다
        int map100[GN];
        buildMap(m, map100);
        const int left = m.T - m.t;
        len = horizon < left ? horizon : left; at = 0;
        planBeam(map100, m.stepped, m.h, m.w, m.pos, len, width, plan, evals);
        ++plans;
    }
    int act(const GridMirror& m) {                     // 다음 걸음. 계획을 다 썼거나 period만큼 실행했으면 다시 계획한다
        if (at >= len || at >= period) replan(m);
        return plan[at++];
    }
};

// 검사용: 거울이 채점기와 같은가. 위치·점수, 밟은 칸, 보여 준 칸과 그 값, 평균 재료를 대조한다(채점기의 감춰진 값을 읽는 곳은 검사뿐이다).
bool gridMirrorOk(const GridJudge& j, const GridMirror& m) {
    if (m.pos != j.pos || m.t != j.used || m.got != j.score) return false;
    int n = 0; long long s = 0;
    for (int c = 0; c < j.h * j.w; ++c) {
        if (m.stepped[c] != j.got[c]) return false;
        if ((m.seenAt[c] >= 0) != j.shown[c]) return false;      // 보여 준 칸만 안다고 적었는가
        if (m.seenAt[c] >= 0) { if (m.val[c] != j.v[c]) return false; ++n; s += j.v[c]; }
    }
    return n == m.nSeen && s == m.sumSeen;
}

// 검사용: 추정 지도가 맞는가. 아는 칸은 진짜 값 x 100, 모르는 칸은 모두 같은 추정값이어야 한다.
bool gridMapOk(const GridJudge& j, const GridMirror& m, const GridPolicy& p) {
    int map100[GN];
    p.buildMap(m, map100);
    const int guess = p.guess100(m);
    for (int c = 0; c < j.h * j.w; ++c)
        if (map100[c] != (j.shown[c] ? 100 * j.v[c] : guess)) return false;
    return true;
}

// 한 판: 보고(observe), 필요하면 다시 계획하고(plan), 한 걸음 움직이고(act), 다시 본다. 반환값은 얻은 값, 규칙 위반이면 -1.
// moves가 있으면 걸음을 적고, firstBad가 있으면 거울·추정 지도가 처음 어긋난 걸음 번호를 적는다(0은 시작 직후, -1은 어긋남 없음).
long long playGrid(GridJudge& j, GridMirror& m, GridPolicy& p, int moves[], int* firstBad) {
    j.start(); m.begin(j); m.observe(j);
    p.len = p.at = 0; p.plans = p.evals = 0;
    if (firstBad) *firstBad = gridMirrorOk(j, m) && gridMapOk(j, m, p) ? -1 : 0;
    while (j.used < j.T) {
        const int c = p.act(m);
        if (moves) moves[j.used] = c;
        if (!j.move(c)) return -1;
        m.step(c); m.observe(j);
        if (firstBad && *firstBad < 0 && !(gridMirrorOk(j, m) && gridMapOk(j, m, p))) *firstBad = m.t;
    }
    return j.score;
}

// 감춰진 정보를 쓰지 않는지: 한 번도 보여 주지 않은 칸의 값을 바꿔도 같은 걸음이 나와야 한다. 같으면 true.
bool gridNoPeek(const GridJudge& base, GridMirror& m, GridPolicy& p) {
    static GridJudge a, b;
    static int mvA[GN], mvB[GN];
    a = base; b = base;
    hc::fill(mvA, GN, -1); hc::fill(mvB, GN, -1);
    playGrid(a, m, p, mvA, 0);
    for (int c = 0; c < a.h * a.w; ++c) if (!a.shown[c]) b.v[c] = (a.v[c] + 1 + c % 9) % 10;   // 모든 못 본 칸의 값이 달라진다
    playGrid(b, m, p, mvB, 0);
    for (int t = 0; t < a.T; ++t) if (mvA[t] != mvB[t]) return false;
    return true;
}

// 전체 정보 기준선: 진짜 값 지도 위에서 T걸음을 한 번에 계획한다. 반환값은 그 경로가 얻는 값이고 path[0..T)에 경로가 있다.
long long planFull(const GridJudge& j, int width, int path[], long long& evals) {
    int map100[GN]; bool stepped[GN];
    for (int c = 0; c < j.h * j.w; ++c) { map100[c] = 100 * j.v[c]; stepped[c] = c == 0; }
    return j.v[0] + planBeam(map100, stepped, j.h, j.w, 0, j.T, width, path, evals) / 100;
}
```

## 온라인 배정 채우기

작업이 하나씩 도착하고 도착한 순간 기계를 정합니다. 채점기는 도착한 작업의 길이와 기계별 추가 비용만 보여 주고, 거울은 기계별 부하와 작업 수(내가 센 값), 도착한 작업 길이의 합 `dSum`(평균과 총량 추정의 재료)을 기억합니다. 모르는 것은 앞으로 올 작업의 길이입니다.

결정은 `chooseMachine`입니다. 기계 `q`에 맡길 때의 점수는 `100 × 추가 비용 + (부하 제곱의 증가)`이고, 부하를 `lam` 아래로는 "앞으로 채워진다"고 보고 `lam`으로 올려 셉니다. 마지막에 기계 하나가 맡을 부하 `lam`은 도착한 작업과 가정한 앞으로의 작업을 기계 수로 나눈 값입니다(`lambda`). `lam = 0`이면 앞일을 고려하지 않는 평범한 탐욕입니다. 앞으로 올 작업의 길이는 `fut`로 가정합니다. `FUT_MEAN`이면 도착한 작업의 평균, 0 이상이면 그 값, `FUT_OFF`이면 `lam = 0`입니다. 같은 `chooseMachine`을 전체 정보 기준선(`offlineGreedy`)도 쓰며 거기서는 `lam`이 진짜 총 길이에서 정해집니다.

```cpp snippet=pi-online
const int AN = 120, AM = 8;                // 작업 수와 기계 수의 상한

struct OnlineJudge {                       // 로컬 채점기. 작업이 하나씩 도착하고, 도착한 순간 기계를 정해야 한다.
    int n, m, k;                           // 작업 수, 기계 수, 기계 한 대의 작업 수 상한
    int d[AN], c[AN][AM];                  // 전체 입력: 감춰진 정보(아직 도착하지 않은 작업)
    int next;                              // 다음에 도착할 작업 번호
    int load[AM], cnt[AM];                 // 기계별 부하와 작업 수
    long long cs;                          // 맡긴 작업의 추가 비용 합

    void start() { next = 0; cs = 0; for (int q = 0; q < m; ++q) load[q] = cnt[q] = 0; }
    bool arrive(int& len, int row[]) {     // 다음 작업이 도착한다: 이 작업의 길이와 기계별 추가 비용만 보인다. 더 없으면 false
        if (next >= n) return false;
        len = d[next];
        for (int q = 0; q < m; ++q) row[q] = c[next][q];
        return true;
    }
    bool assign(int q) {                   // 방금 도착한 작업을 기계 q에 맡긴다(되돌릴 수 없다). 상한을 넘으면 false(무효)
        if (q < 0 || q >= m || cnt[q] >= k) return false;
        load[q] += d[next]; ++cnt[q]; cs += c[next][q]; ++next;
        return true;
    }
    long long score() const {              // 모든 작업을 맡긴 뒤의 비용(작을수록 좋음)
        long long sq = 0;
        for (int q = 0; q < m; ++q) sq += (long long)load[q] * load[q];
        return sq / 100 + cs;
    }
};

struct OnlineMirror {                      // 내 쪽의 거울: 규칙(아는 것), 도착한 작업과 내 배정(기억한 것), 앞으로 올 작업(모르는 것)
    int n, m, k;                           // 아는 것: 규칙
    int load[AM], cnt[AM];                 // 내가 센 기계별 부하와 작업 수
    int seen;                              // 도착한 작업 수(지금 것 포함)
    long long dSum, cSum;                  // 도착한 작업 길이의 합, 맡긴 추가 비용의 합
    int len, row[AM];                      // 지금 도착한 작업

    void begin(const OnlineJudge& j) {
        n = j.n; m = j.m; k = j.k; seen = 0; dSum = cSum = 0;
        for (int q = 0; q < m; ++q) load[q] = cnt[q] = 0;
    }
    void observe(int l, const int r[]) {   // 도착을 기록한다
        len = l; for (int q = 0; q < m; ++q) row[q] = r[q];
        ++seen; dSum += l;
    }
    void commit(int q) {                   // 내 배정을 적는다. 채점기에 묻지 않고 기억한 값으로 센다
        load[q] += len; ++cnt[q]; cSum += row[q];
    }
};

const int FUT_OFF = -2, FUT_MEAN = -1;
// 기계 q에 맡길 때의 점수(x100) = 100 x 추가 비용 + (부하 제곱의 증가). 부하는 lam 아래를 "앞으로 채워진다"고 보고 lam으로 올려 센다.
// lam = 0이면 앞일을 고려하지 않는 평범한 탐욕이다. 상한이 찬 기계는 고르지 않는다.
int chooseMachine(const int load[], const int cnt[], int m, int k, int len, const int row[], long long lam) {
    int best = -1; long long bs = 0;
    for (int q = 0; q < m; ++q) {
        if (cnt[q] >= k) continue;
        const long long before = load[q] > lam ? load[q] : lam, after = load[q] + len > lam ? load[q] + len : lam;
        const long long s = 100LL * row[q] + after * after - before * before;
        if (best < 0 || s < bs) { best = q; bs = s; }
    }
    return best;
}

struct OnlinePolicy {
    int fut;                               // 앞으로 올 작업 하나의 길이 가정: 0 이상이면 그 값, FUT_MEAN이면 도착한 작업의 평균, FUT_OFF면 앞일을 보지 않는다
    long long lambda(const OnlineMirror& m) const {    // 마지막에 기계 하나가 맡을 부하의 예상(= 도착한 것 + 가정한 앞으로의 것을 기계 수로 나눈 값)
        if (fut == FUT_OFF) return 0;
        const long long each = fut == FUT_MEAN ? m.dSum / m.seen : fut;
        return (m.dSum + (long long)(m.n - m.seen) * each) / m.m;
    }
    int act(const OnlineMirror& m) const { return chooseMachine(m.load, m.cnt, m.m, m.k, m.len, m.row, lambda(m)); }
};

bool onlineMirrorOk(const OnlineJudge& j, const OnlineMirror& m) {    // 검사용: 부하·작업 수·길이 합·추가 비용 합을 채점기와 대조한다
    long long ds = 0;
    for (int i = 0; i < j.next; ++i) ds += j.d[i];
    for (int q = 0; q < j.m; ++q) if (m.load[q] != j.load[q] || m.cnt[q] != j.cnt[q]) return false;
    return m.seen == j.next && m.dSum == ds && m.cSum == j.cs;
}

// 한 판: 도착한 작업을 기록하고(observe), 거울과 추정만으로 기계를 정하고(act), 맡기고, 거울에 적는다.
// firstBad가 있으면 거울이 채점기와 처음 어긋난 작업 번호(1부터)를 적는다(-1은 어긋남 없음). 반환값은 비용, 규칙 위반이면 -1.
long long playOnline(OnlineJudge& j, OnlineMirror& m, OnlinePolicy& p, int to[], int* firstBad) {
    j.start(); m.begin(j);
    if (firstBad) *firstBad = -1;
    int len, row[AM];
    while (j.arrive(len, row)) {
        m.observe(len, row);
        const int q = p.act(m);
        if (to) to[m.seen - 1] = q;
        if (!j.assign(q)) return -1;
        m.commit(q);
        if (firstBad && *firstBad < 0 && !onlineMirrorOk(j, m)) *firstBad = m.seen;
    }
    return j.score();
}

// 감춰진 정보를 쓰지 않는지: 작업 from번부터 뒤를 전부 다른 값으로 바꿔도 앞의 배정은 같아야 한다. 같으면 true.
bool onlineNoPeek(const OnlineJudge& base, OnlineMirror& m, OnlinePolicy& p, int from) {
    static OnlineJudge a, b;
    static int toA[AN], toB[AN];
    a = base; b = base;
    for (int i = from; i < b.n; ++i) b.d[i] = 1;           // 아직 도착하지 않은 작업을 전부 가장 짧은 작업으로 바꾼다
    hc::fill(toA, AN, -1); hc::fill(toB, AN, -1);
    playOnline(a, m, p, toA, 0); playOnline(b, m, p, toB, 0);   // 규칙을 어긴 배정이 나오면 거기서 멈춘다. 멈추기 전의 결정만 비교한다
    for (int i = 0; i < from; ++i) if (toA[i] != toB[i]) return false;
    return true;
}

// 전체 정보 기준선 1: 모든 작업을 안다. 총 길이로 lam을 정하고 같은 규칙으로 맡긴다. byLength이면 긴 작업부터(도착 순서를 무시).
long long offlineGreedy(const OnlineJudge& j, bool byLength) {
    int ord[AN], tmp[AN], load[AM], cnt[AM];
    long long key[AN], total = 0, cs = 0;
    for (int i = 0; i < j.n; ++i) { ord[i] = i; key[i] = byLength ? -j.d[i] : 0; total += j.d[i]; }
    hc::sortIds(ord, tmp, j.n, key);                       // key가 같으면 번호 순서 = 도착 순서
    for (int q = 0; q < j.m; ++q) load[q] = cnt[q] = 0;
    for (int r = 0; r < j.n; ++r) {
        const int i = ord[r];
        const int q = chooseMachine(load, cnt, j.m, j.k, j.d[i], j.c[i], total / j.m);
        load[q] += j.d[i]; ++cnt[q]; cs += j.c[i][q];
    }
    long long sq = 0;
    for (int q = 0; q < j.m; ++q) sq += (long long)load[q] * load[q];
    return sq / 100 + cs;
}

// 전체 정보 기준선 2: 아무 배정도 이 값보다 낮을 수 없다(부하 항은 모든 기계가 똑같을 때, 추가 비용 항은 작업마다 가장 싼 기계일 때가 최소. 둘은 따로 낮출 수 있어 합은 하한일 뿐이다).
long long lowerBound(const OnlineJudge& j) {
    long long total = 0, cmin = 0;
    for (int i = 0; i < j.n; ++i) {
        total += j.d[i];
        int lo = j.c[i][0];
        for (int q = 1; q < j.m; ++q) if (j.c[i][q] < lo) lo = j.c[i][q];
        cmin += lo;
    }
    return (total * total + j.m - 1) / j.m / 100 + cmin;
}

long long roundRobin(const OnlineJudge& j) {              // 아무것도 보지 않는 기준선: 작업 i를 기계 i % m에
    int load[AM];
    long long cs = 0, sq = 0;
    for (int q = 0; q < j.m; ++q) load[q] = 0;
    for (int i = 0; i < j.n; ++i) { load[i % j.m] += j.d[i]; cs += j.c[i][i % j.m]; }
    for (int q = 0; q < j.m; ++q) sq += (long long)load[q] * load[q];
    return sq / 100 + cs;
}
```

## 입력 생성과 실행

입력은 [연습용 문제 틀](idea.md)의 규칙대로 시드 하나에서 만듭니다. 생성용 난수 `Gen`은 64비트 선형 합동 생성기입니다. 두 정책은 난수를 쓰지 않으므로 탐색용 난수는 없습니다.

```cpp snippet=pi-gen
struct Gen {                               // 입력 생성용 64비트 난수
    unsigned long long x;
    void reset(unsigned long long seed) { x = seed; }
    int next(int range) {                  // [0, range)
        x = x * 6364136223846793005ULL + 1442695040888963407ULL;
        return (int)((x >> 33) % (unsigned long long)range);
    }
};

// 격자: 칸마다 행 순서로 u = next(10)을 읽어 u < zeros10이면 값 0(기본 6 = 60%), 아니면 한 번 더 읽어 1 + next(9). 칸 0에서 시작한다.
void genGrid(GridJudge& g, unsigned long long seed, int h, int w, int T, int rad, int zeros10) {
    Gen r; r.reset(seed);
    g.h = h; g.w = w; g.T = T; g.rad = rad;
    for (int c = 0; c < h * w; ++c) {
        const int u = r.next(10);
        g.v[c] = u < zeros10 ? 0 : 1 + r.next(9);
    }
}

// 온라인 배정: 작업 i = 0, 1, ...의 순서로 길이 1 + next(dmax), 이어서 기계 0..m-1의 추가 비용 next(51)을 읽는다. 작업은 번호 순서로 도착한다.
void genOnline(OnlineJudge& g, unsigned long long seed, int n, int m, int k, int dmax) {
    Gen r; r.reset(seed);
    g.n = n; g.m = m; g.k = k;
    for (int i = 0; i < n; ++i) {
        g.d[i] = 1 + r.next(dmax);
        for (int q = 0; q < m; ++q) g.c[i][q] = r.next(51);
    }
}
```

```cpp snippet=pi-run
static GridJudge gridJ;
static GridMirror gridM;
static GridPolicy gridP;
static OnlineJudge onJ;
static OnlineMirror onM;
static OnlinePolicy onP;

// 격자 수집(20 x 20, 60걸음): 보이는 거리 rad, 모르는 칸의 값 가정 est100, 계획 깊이 horizon, 재계획 주기 period, 빔 폭 width.
// 반환값은 얻은 값의 합(클수록 좋음).
long long runGrid(unsigned long long seed, int rad, int est100, int horizon, int period, int width, int zeros10) {
    genGrid(gridJ, seed, 20, 20, 60, rad, zeros10);
    gridP.est100 = est100; gridP.horizon = horizon; gridP.period = period; gridP.width = width;
    return playGrid(gridJ, gridM, gridP, 0, 0);
}

// 온라인 배정(작업 120개, 기계 8대, 기계당 18개): 앞으로 올 작업의 길이 가정 fut. 반환값은 비용(작을수록 좋음).
long long runOnline(unsigned long long seed, int fut, int dmax) {
    genOnline(onJ, seed, 120, 8, 18, dmax);
    onP.fut = fut;
    return playOnline(onJ, onM, onP, 0, 0);
}
```

[실험과 점검](practice.md)의 표는 모두 이 두 실행 함수(와 `planFull`, `offlineGreedy`)로 시드 1~20을 돌린 값입니다.

## 검사 틀을 쓰는 법

정보가 가려진 문제의 오류는 대개 조용히 나쁜 점수를 냅니다. 컴파일도 되고 실행도 되고 유효한 행동도 냅니다. 아래 검사를 문제와 별도로 둡니다.

1. **거울 대조.** `firstBad`를 주고 `playGrid`, `playOnline`을 돌려 거울이 채점기와 처음 어긋나는 걸음을 찾습니다. 어긋남이 없으면 `-1`입니다. 이 검사는 "내가 센 점수·부하가 채점기와 같은가"와 "아는 것으로 적은 칸이 정말 보여 준 칸인가"를 매 걸음 확인합니다.
2. **추정 지도 대조.** 격자에서는 거울에서 만든 지도가 "아는 칸 = 진짜 값, 모르는 칸 = 같은 추정값"인지 `gridMapOk`로 봅니다. 거울이 맞아도 지도를 만들다 모름을 `0`으로 읽으면 여기서 걸립니다.
3. **엿보기 검사.** `gridNoPeek`, `onlineNoPeek`입니다. 한 번도 보여 주지 않은 칸(온라인에서는 정해진 번호 뒤의 작업)을 다른 값으로 바꿔도 같은 결정이 나와야 합니다. 로컬 채점기는 전체 입력을 가지고 있어서 정책이 실수로 감춰진 값을 읽어도 컴파일과 실행이 됩니다. 대회의 채점기에서는 그 값이 없어서 다른 점수가 나옵니다.
4. **전체 정보 기준선과의 비교.** `planFull`과 `offlineGreedy`를 같은 입력에서 돌려 점수의 차이를 봅니다. 부분 정보의 결과가 기준선보다 좋으면 기준선이 약하거나 정책이 엿본 것입니다.

## 코드를 다른 문제에 옮길 때 바뀌는 곳

| 부분 | 격자 수집 | 온라인 배정 | 새 문제에서 |
| --- | --- | --- | --- |
| 채점기가 보여 주는 것 | 거리 2 이내 칸의 값 | 도착한 작업의 길이·비용 | 문제의 관측 호출의 결과 |
| 거울 | `val`, `seenAt`, `stepped`, 위치, 얻은 값, 평균 재료 | 부하, 작업 수, 길이 합, 추가 비용 합 | 채점기의 상태를 따라 그릴 필드(맞춘 것을 대조할 수 있게) |
| 모르는 것의 추정 | 못 본 칸의 값 | 앞으로 올 작업의 길이 | 관측한 것의 평균, 가능한 최대·최소 |
| 결정 | 추정 지도 위 빔 서치 | 부하를 `lam`으로 올려 센 점수 | 거울과 추정만으로 계산하는 규칙 |
| 다시 계획 | `period` | 없음(결정을 되돌릴 수 없다) | 새 관측이 계획을 바꾸는지로 정한다 |
| 검사 | `gridMirrorOk`, `gridMapOk`, `gridNoPeek` | `onlineMirrorOk`, `onlineNoPeek` | 거울 대조 + 엿보기 검사 + 전체 정보 기준선 |
