# 채점기 상태를 따라 그리며 행동하기

[광산 탐사](/practice/MINEEXPLORE)는 지도 전체를 `process`의 인자로 줍니다. 그런데도 풀이가 틀리는 이유는 지도가 아니라 **채점기 안의 상태**에 있습니다. 어느 칸을 이미 밟았는지, 오늘 몇 번 움직였는지, 지금 날짜가 며칠인지는 어떤 API로도 물을 수 없고 `move`도 아무 값을 돌려주지 않습니다. 제출 코드가 믿을 수 있는 것은 **내가 호출한 행동의 기록**뿐입니다. 이 강의는 그 기록(관측)을 만들고, 기록을 읽기만 하는 계획 코드와 기록을 바꾸는 행동 코드를 나누어 풀이를 세 단계로 키웁니다.

![5×5 예시 지도에서 두 번 이동한 상태입니다. 채점기는 방문 3칸과 위치와 오늘 이동 2회와 점수 22를 알지만 제출 코드는 읽지 못합니다. 내 관측 기록은 seen 3칸과 위치와 남은 98회와 mirrorScore 22입니다. 추정은 목표 (0,3)까지 이동 2회와 경로 이득 71이며 주변 값은 불확실합니다.](lesson-assets/mirror-states.svg)

[그림 크게 보기](https://git.readiz.com/h-contest-lesson/lessons/observe-and-act/lesson-assets/mirror-states.svg)

위 그림의 세 층을 이 강의에서 끝까지 구분합니다. **채점기가 아는 것**은 읽을 수 없고, **내가 관측한 것**은 내 호출 결과로만 갱신하며, **내가 추정한 것**은 걸어 보기 전에는 맞는지 모릅니다. 이어지는 코드는 모두 h-contest 제출용이며 표준 헤더와 STL 없이 [공통 라이브러리](https://h.readiz.com/learn/cpp-common-library)의 `queue` 블록 하나만 씁니다.

## 문제 계약을 상태로 옮기기

| 항목 | 계약 |
| --- | --- |
| 호출 순서 | TC마다 `process(mapInfo, startY, startX)`가 한 번 호출됩니다. 이 호출이 TC 시작 콜백입니다. |
| 행동 API | `move(dir)`: `0` 위, `1` 오른쪽, `2` 아래, `3` 왼쪽으로 한 칸. `nextDay()`: 다음 날로 넘어가 오늘 이동 횟수를 0으로 만듭니다. |
| 규모 | `30 × 30` 지도, 10일, 하루 최대 10번 `move`, TC 10개. 한 TC에서 `move`는 최대 100번이고 `nextDay`는 최대 9번입니다. |
| 점수 | 처음 밟은 칸의 광물 가치 합, 클수록 좋습니다. 시작 칸의 가치는 0이고 다시 밟은 칸은 0점입니다. 10개 TC의 합이 점수이며 문제 설정의 통과 기준은 120000입니다. |
| 무효 행동 | 방향이 `0..3`이 아님, 지도 밖으로 이동, 하루 10번 초과, 10일째에 `nextDay` 호출. 무효가 되면 이후 호출은 모두 무시되고 **그 TC는 0점**입니다. |
| 피드백 | 없습니다. 무효 행동도 예외나 반환값 없이 조용히 0점이 됩니다. |

하루 10번이라는 제한은 하루 안에서만 의미가 있고, 전체로는 `10 × 10 = 100`번 이동이면 충분합니다. 날짜 경계는 어디에 두어도 점수와 무관하므로 계획 코드가 날짜를 몰라도 되게 하고, 행동 코드가 열한 번째 이동 직전에 `nextDay`를 호출하도록 만듭니다. 계획과 행동을 나누는 첫 이유입니다.

## 관측 기록을 한 곳에서만 갱신한다

세 층의 상태를 코드에 옮깁니다. `Mirror`(채점기 상태를 따라 그리는 **거울**)가 내가 관측한 것의 전부이고, `act`가 채점기를 부르는 유일한 통로입니다.

> **코드 환경: h-contest 제출용.** 아래 블록들을 이 순서대로 `user.cpp`에 붙입니다. 이 블록은 `process`를 포함하지 않는 공통 상태입니다.

```cpp snippet=mine-state
#define MAP_SIZE 30

extern void move(int dir);
extern void nextDay(void);

namespace mine {
const int N = MAP_SIZE;
const int DAYS = 10, DAILY = 10;
const int DY[4] = {-1, 0, 1, 0};
const int DX[4] = {0, 1, 0, -1};

struct Mirror {
    int y, x;            // 내가 기록한 현재 위치
    int day, dayMoves;   // 몇 일째인가, 오늘 몇 번 움직였나
    int movesLeft;       // 남은 전체 이동 횟수
    bool seen[N][N];     // 내가 밟은 칸
};

Mirror M;
int (*grid)[MAP_SIZE];   // 전달받은 지도. 읽기만 한다
long long mirrorScore;   // 거울이 계산한 점수
int refused;             // 규칙 위반이라 호출하지 않은 요청 수
void (*hook)(int dist, int gain, int around);   // 로컬 하네스만 연결하는 로그 훅

void resetCase(int mapInfo[][MAP_SIZE], int startY, int startX) {
    grid = mapInfo;
    for (int y = 0; y < N; ++y) for (int x = 0; x < N; ++x) M.seen[y][x] = false;
    M.y = startY; M.x = startX;
    M.seen[startY][startX] = true;
    M.day = 1; M.dayMoves = 0;
    M.movesLeft = DAYS * DAILY;
    mirrorScore = 0; refused = 0;
}

bool canStep(int dir) {
    if (dir < 0 || dir > 3 || M.movesLeft <= 0) return false;
    int ny = M.y + DY[dir], nx = M.x + DX[dir];
    return 0 <= ny && ny < N && 0 <= nx && nx < N;
}

// 채점기 호출은 모두 이 함수를 지난다.
bool act(int dir) {
    if (!canStep(dir)) { ++refused; return false; }
    if (M.dayMoves == DAILY) {          // 오늘 한도를 다 썼으면 먼저 날짜를 넘긴다
        nextDay();
        ++M.day; M.dayMoves = 0;
    }
    move(dir);
    ++M.dayMoves; --M.movesLeft;
    M.y += DY[dir]; M.x += DX[dir];
    if (!M.seen[M.y][M.x]) {
        M.seen[M.y][M.x] = true;
        mirrorScore += grid[M.y][M.x];
    }
    return true;
}
}
```

초기화 시점이 이 설계의 핵심입니다.

| 상태 | 언제 초기화하는가 | 이유 |
| --- | --- | --- |
| `M.seen`, 위치, 날짜, 남은 횟수, `mirrorScore`, `refused` | `process` 시작(`resetCase`)에서 한 번 | TC마다 채점기가 새로 시작합니다. 남겨 두면 이전 TC의 방문 기록이 섞입니다. |
| 위의 같은 값 | **행동마다 지우지 않음** | 행동할 때마다 지우면 방금 밟은 칸을 잊어 같은 칸을 반복 계획합니다. |
| BFS 결과(`R`)와 큐 | 목표를 고를 때마다 | 관측이 바뀌면 낡은 계획입니다. 계획은 매번 다시 계산하며 저장하지 않습니다. |
| `grid` | `resetCase`에서 새 포인터로 | 지도는 읽기 전용 입력입니다. 값을 바꿔 방문 표시로 쓰지 않습니다. |

`act`가 정상 입력에서 거절하는 일은 없어야 하므로, 거절한 요청 수 `refused`를 세어 두고 로컬에서 0인지 확인합니다. 그림의 마지막 행에서 보듯 `mirrorScore`는 내가 계산한 점수이고, 채점기의 점수와 같은지 비교하는 것이 이 강의 모든 검사의 출발점입니다.

## 0단계: 유효한 기준선

가장 단순한 규칙 준수 정책은 한 방향으로 걷다가 벽에서 시계 방향으로 꺾는 것입니다. 가치를 전혀 보지 않지만 100번을 모두 유효하게 쓰는지, 날짜 넘김이 맞는지를 먼저 확인할 수 있습니다.

```cpp snippet=mine-baseline
void process(int mapInfo[][MAP_SIZE], int startY, int startX) {
    mine::resetCase(mapInfo, startY, startX);
    int dir = 1;                                  // 오른쪽에서 시작
    while (mine::M.movesLeft > 0) {
        if (!mine::canStep(dir)) { dir = (dir + 1) % 4; continue; }   // 벽이면 시계 방향으로 꺾는다
        mine::act(dir);
    }
}
```

`mine-state` 블록 뒤에 이 블록만 붙이면 완성된 `user.cpp`입니다.

## 계획과 행동을 나눈 정책 1: 가까운 미확인 칸

정책은 두 단계를 반복합니다. 먼저 **계획**으로 현재 위치에서 모든 칸까지의 거리와 가는 길의 이득을 구하고, 목표 하나를 고릅니다. 다음에 **행동**으로 그 경로를 `act`로 걷습니다. 계획 함수는 `M`과 `grid`를 읽기만 하고 `act`를 부르지 않습니다.

BFS는 [격자 BFS](https://h.readiz.com/learn/bfs-dfs-grid)와 같지만 칸마다 `gain`을 하나 더 가집니다. 같은 거리로 오는 경로가 여럿이면 아직 밟지 않은 칸의 가치 합이 큰 경로를 남깁니다. BFS는 거리 순서로 칸을 꺼내므로, 한 칸을 꺼낼 때 그 칸으로 들어올 수 있는 이전 칸이 모두 처리되어 `gain`이 확정됩니다. 큐 용량은 칸 수 `N × N = 900`이면 됩니다. 남은 이동 횟수보다 먼 칸은 확장하지 않습니다.

> **코드 환경: h-contest 제출용.** `queue`와 `mine-state` 블록 뒤에 붙입니다. 공통 블록 이름은 `queue`, 용량은 900(누적 push 수), 초기화 시점은 `bfs()` 시작입니다.

```cpp snippet=mine-reach
namespace mine {
struct Reach {
    int dist[N][N];   // 현재 위치에서의 최단 이동 횟수, 닿을 수 없으면 -1
    int gain[N][N];   // 그 거리로 가는 경로 중 아직 안 밟은 칸의 가치 합 최댓값
    int from[N][N];   // 그 경로에서 이 칸에 들어온 방향
};

Reach R;
hc::Queue<N * N> Q;

void bfs() {
    for (int y = 0; y < N; ++y) for (int x = 0; x < N; ++x) R.dist[y][x] = -1;
    Q.clear();
    R.dist[M.y][M.x] = 0; R.gain[M.y][M.x] = 0; R.from[M.y][M.x] = -1;
    Q.push(M.y * N + M.x);
    int cur;
    while (Q.pop(cur)) {
        int y = cur / N, x = cur % N;
        if (R.dist[y][x] == M.movesLeft) continue;      // 남은 횟수 밖은 보지 않는다
        for (int d = 0; d < 4; ++d) {
            int ny = y + DY[d], nx = x + DX[d];
            if (ny < 0 || ny >= N || nx < 0 || nx >= N) continue;
            int g = R.gain[y][x] + (M.seen[ny][nx] ? 0 : grid[ny][nx]);
            if (R.dist[ny][nx] < 0) {
                R.dist[ny][nx] = R.dist[y][x] + 1;
                R.gain[ny][nx] = g; R.from[ny][nx] = d;
                Q.push(ny * N + nx);
            } else if (R.dist[ny][nx] == R.dist[y][x] + 1 && g > R.gain[ny][nx]) {
                R.gain[ny][nx] = g; R.from[ny][nx] = d;   // 같은 거리라면 더 많이 얻는 경로
            }
        }
    }
}
}
```

이제 목표를 고르는 규칙과 경로를 걷는 함수입니다. 정책 1은 값이 있는 미확인 칸 중 가장 가까운 칸을 고릅니다. 정책 2의 평가식은 다음 절에서 설명하며, 여기서는 함께 붙입니다.

```cpp snippet=mine-policy
namespace mine {
const int RADIUS = 3;       // 목표 주변을 보는 맨해튼 반경
const double WEIGHT = 0.1;  // 주변 값 합을 얼마나 믿는가
const double COST = 1.0;    // 목표를 정하는 일에 드는 고정 비용(이동 횟수 단위)

int lastAround;             // 마지막으로 고른 목표의 주변 값 합 (로그용)

// 정책 1: 가장 가까운 미확인 칸. 거리가 같으면 가는 길에 더 얻는 쪽
bool pickNearest(int& ty, int& tx) {
    bool found = false;
    for (int y = 0; y < N; ++y) for (int x = 0; x < N; ++x) {
        int d = R.dist[y][x];
        if (d <= 0 || M.seen[y][x] || grid[y][x] == 0) continue;
        if (!found || d < R.dist[ty][tx] || (d == R.dist[ty][tx] && R.gain[y][x] > R.gain[ty][tx])) {
            found = true; ty = y; tx = x;
        }
    }
    lastAround = 0;
    return found;
}

int around(int ty, int tx) {   // 목표 칸을 뺀, 반경 안의 미확인 가치 합
    int sum = 0;
    for (int y = ty - RADIUS; y <= ty + RADIUS; ++y) for (int x = tx - RADIUS; x <= tx + RADIUS; ++x) {
        int d = (y > ty ? y - ty : ty - y) + (x > tx ? x - tx : tx - x);
        if (d == 0 || d > RADIUS || y < 0 || y >= N || x < 0 || x >= N || M.seen[y][x]) continue;
        sum += grid[y][x];
    }
    return sum;
}

// 정책 2: (가는 길 이득 + WEIGHT × 주변 값) / (이동 횟수 + COST)
double key(int ty, int tx) {
    return (R.gain[ty][tx] + WEIGHT * around(ty, tx)) / (R.dist[ty][tx] + COST);
}

bool pickRatio(int& ty, int& tx) {
    bool found = false;
    double best = 0;
    for (int y = 0; y < N; ++y) for (int x = 0; x < N; ++x) {
        if (R.dist[y][x] <= 0 || M.seen[y][x] || grid[y][x] == 0) continue;
        double k = key(y, x);
        if (!found || k > best) { found = true; best = k; ty = y; tx = x; }
    }
    if (found) lastAround = around(ty, tx);
    return found;
}

void walkTo(int ty, int tx) {
    int dirs[N * N], n = 0;
    for (int y = ty, x = tx; R.dist[y][x] > 0; ) {   // 도착점에서 거꾸로 방향을 모은다
        int d = R.from[y][x];
        dirs[n++] = d;
        y -= DY[d]; x -= DX[d];
    }
    if (hook) hook(R.dist[ty][tx], R.gain[ty][tx], lastAround);
    for (int i = n - 1; i >= 0; --i) act(dirs[i]);
}
}
```

마지막으로 TC 하나를 처리하는 `process`입니다. `POLICY`를 `1`로 두면 정책 1입니다.

```cpp snippet=mine-entry
const int POLICY = 2;   // 1이면 가까운 칸 우선, 2면 평가식

void process(int mapInfo[][MAP_SIZE], int startY, int startX) {
    mine::resetCase(mapInfo, startY, startX);
    while (mine::M.movesLeft > 0) {
        mine::bfs();
        int ty, tx;
        bool found = POLICY == 1 ? mine::pickNearest(ty, tx) : mine::pickRatio(ty, tx);
        if (!found) break;          // 남은 횟수 안에 닿는 가치 있는 칸이 없다
        mine::walkTo(ty, tx);
    }
}
```

한 목표마다 BFS를 새로 하므로 한 TC의 비용은 목표 수 × 900칸이고, 목표는 많아야 100개입니다. 아래 표의 시간이 이를 보여 줍니다.

## 정책 2: 이동 비용 대비 이득을 비교하는 평가식

정책 1은 가장 가까운 칸이 1점짜리여도 그곳으로 갑니다. 정책 2는 모든 후보의 **이동당 이득**을 같은 식으로 비교합니다.

```text
key(t) = (g(t) + WEIGHT × h(t)) / (d(t) + COST)
```

| 항 | 뜻 | 확정 여부 |
| --- | --- | --- |
| `g(t)` | 거울 기준으로 `t`까지 걸으며 새로 얻는 점수 | 확정. 걸으면 정확히 이 값만큼 오릅니다. |
| `d(t)` | `t`까지 이동 횟수 | 확정. 100번이라는 예산을 쓰는 양입니다. |
| `h(t)` | `t`에서 맨해튼 거리 `RADIUS` 이내 미확인 칸의 가치 합(`t` 제외) | **추정.** 거기서 실제로 얻는다는 보장이 없고 `g`의 경로 칸과 겹칠 수도 있습니다. |
| `WEIGHT` | 추정 `h`를 얼마나 믿는가 | 0이면 `h`를 무시합니다. |
| `COST` | 목표 하나를 정하는 고정 비용 | 0이면 거리 1짜리 작은 칸의 비율이 폭주합니다. |

측정은 공개 채점기 `main.cpp`를 복사해 출력 몇 줄만 더한 로컬 사본에 위 코드를 붙여 했습니다. 측정일은 2026-11-18, 환경은 Apple M1·macOS·Apple clang 17(`-std=c++17 -O2`)이며, 점수는 같은 입력에서 항상 같고 시간(ms)은 채점기가 출력한 값입니다. 기준선·정책 1·정책 2의 시간은 9번 실행의 중앙값이고, 아래 파라미터 표의 시간은 1회 측정이라 잡음이 있습니다. 원본은 [measurements.json](lesson-assets/measurements.json)에 있습니다.

| 정책 | 점수 합 | 거울 점수 합 | 거절 요청 | 시간 ms |
| --- | --- | --- | --- | --- |
| 기준선 | 46422 | 46422 | 0 | 0 |
| 정책 1 | 105823 | 105823 | 0 | 9 |
| 정책 2 | 131259 | 131259 | 0 | 9 |

점수 합이 120000을 넘는 것은 정책 2뿐입니다. 거울 점수 합은 세 정책 모두 채점기 점수와 같고 거절 요청은 0입니다. TC별 점수는 다음과 같습니다.

| 정책 | TC 1 | TC 2 | TC 3 | TC 4 | TC 5 | TC 6 | TC 7 | TC 8 | TC 9 | TC 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 기준선 | 7359 | 4716 | 6111 | 4243 | 5364 | 3659 | 3057 | 3417 | 4053 | 4443 |
| 정책 1 | 12626 | 12380 | 6202 | 9879 | 13162 | 8461 | 13433 | 9932 | 6541 | 13207 |
| 정책 2 | 12931 | 12827 | 11792 | 12822 | 13098 | 12595 | 14517 | 13283 | 12970 | 14424 |

정책 2는 정책 1보다 10개 중 9개 TC에서 높습니다. 정책 1이 낮은 TC 3과 TC 9(6202, 6541)에서 정책 2는 11792와 12970입니다. 반대로 TC 1(12626과 12931)과 TC 5(13162와 13098)는 두 정책이 거의 같습니다. 가까운 곳에 큰 언덕이 있으면 가까운 칸 우선도 충분하다는 뜻입니다.

기본값(`RADIUS 3`, `WEIGHT 0.1`, `COST 1.0`)에서 **파라미터 하나씩만** 바꾼 결과입니다.

| 바꾼 값 | 점수 합 | 거울 점수 합 | 거절 요청 | 시간 ms |
| --- | --- | --- | --- | --- |
| RADIUS 1 | 131886 | 131886 | 0 | 1 |
| RADIUS 2 | 132049 | 132049 | 0 | 2 |
| RADIUS 3 | 131259 | 131259 | 0 | 8 |
| RADIUS 4 | 128789 | 128789 | 0 | 27 |
| RADIUS 5 | 131620 | 131620 | 0 | 50 |
| RADIUS 6 | 128691 | 128691 | 0 | 73 |
| WEIGHT 0.0 | 129734 | 129734 | 0 | 2 |
| WEIGHT 0.05 | 131740 | 131740 | 0 | 3 |
| WEIGHT 0.1 | 131259 | 131259 | 0 | 8 |
| WEIGHT 0.25 | 125514 | 125514 | 0 | 33 |
| WEIGHT 0.5 | 123507 | 123507 | 0 | 19 |
| WEIGHT 1.0 | 118013 | 118013 | 0 | 28 |
| WEIGHT 2.0 | 114557 | 114557 | 0 | 39 |
| COST 0.0 | 124190 | 124190 | 0 | 17 |
| COST 1.0 | 131259 | 131259 | 0 | 8 |
| COST 2.0 | 130971 | 130971 | 0 | 2 |
| COST 4.0 | 129383 | 129383 | 0 | 1 |
| COST 8.0 | 128253 | 128253 | 0 | 1 |
| COST 16.0 | 122967 | 122967 | 0 | 1 |

읽는 방법은 다음과 같습니다.

- `COST`는 1~2에서 가장 높고 0과 16에서 내려갑니다. 분모에 고정값이 없으면 한두 번 이동으로 닿는 작은 칸의 이동당 이득이 부풀어 오릅니다. 반대로 너무 크면 거리 차이가 비율에 덜 반영되어 멀리 있는 큰 칸을 고집합니다.
- `WEIGHT`가 0.25 이상이면 점수가 내려가 2.0에서는 114557입니다. 추정치 `h`가 실제 이득보다 크게 잡히기 때문입니다.
- `WEIGHT 0.0`(주변 값 무시)과 기본값의 TC별 차이를 입력 10개로 보면 평균 152.5, 표준오차 123.5이고 근사 구간 [-94.5, 399.5]가 0을 포함합니다. 주변 항이 도움이 되는지는 이 10개로 확정할 수 없습니다. 큰 `WEIGHT`가 해롭다는 것만 분명합니다.
- `RADIUS`는 1~3에서 점수가 비슷하고 시간만 `1 → 73` ms로 늘어납니다. 큰 반경은 이득 없이 비용만 키웁니다.

이 표는 채점에 쓰이는 같은 10개 입력에서 파라미터를 고른 결과입니다. 새 입력에서도 유지된다는 뜻이 아니므로 [실험 비교와 평가](https://h.readiz.com/learn/testing-and-stress/experiment-evaluation)의 튜닝·검증 입력 분리를 적용해, 아래 실패 검사의 하네스처럼 직접 만든 지도에서 한 번 더 확인합니다.

## 작은 손계산: 두 정책이 갈라지는 순간

`30 × 30` 지도의 왼쪽 위 일부만 다음과 같고 나머지는 모두 0이라고 하겠습니다. 시작은 `(2,3)`이고 남은 이동은 6번입니다. 좌표는 `(행, 열)`입니다.

| 행＼열 | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 2 | S | 0 | 40 | 60 |

![같은 시작 칸 (2,3)과 이동 6번에서 정책 1은 (2,2), (1,1), (0,0)을 거쳐 5번 이동해 7점을 얻습니다. 정책 2는 (2,6)을 골라 3번 이동해 100점을 얻습니다.](lesson-assets/two-policies.svg)

[그림 크게 보기](https://git.readiz.com/h-contest-lesson/lessons/observe-and-act/lesson-assets/two-policies.svg)

정책 1은 거리 1의 `(2,2)`부터 줍고, 다음에 `(2,2)`에서 가장 가까운 `(1,1)`, 그다음 `(0,0)`으로 갑니다. 5번 이동에 `2 + 3 + 2 = 7`점이며 남은 1번으로 닿는 값이 없어 끝납니다.

정책 2는 첫 위치에서 후보마다 키를 계산합니다(`WEIGHT 0.1`, `RADIUS 3`, `COST 1`).

| 후보 | 이동 d | 경로 이득 g | 주변 값 h | 키 |
| --- | --- | --- | --- | --- |
| (2,2) | 1 | 2 | 43 | 3.15 |
| (2,5) | 2 | 40 | 62 | 15.4 |
| (2,6) | 3 | 100 | 40 | 26.0 |
| (1,1) | 3 | 5 | 4 | 1.35 |
| (0,0) | 5 | 7 | 3 | 1.217 |

`(2,6)`의 키는 `(100 + 0.1 × 40) / (3 + 1) = 26.0`입니다. `(2,2)`의 `h = 43`에는 `(1,1)`의 3과 `(2,5)`의 40이 들어가지만 `g`가 2뿐이라 키는 3.15에 머뭅니다. 정책 2는 `(2,6)`으로 3번 이동해 `40 + 60 = 100`점을 얻고, 남은 3번 안에 닿는 값이 없어 끝납니다. 같은 6번 예산에서 정책 1은 7점, 정책 2는 100점입니다.

| 정책 | 목표 순서 | 이동 | 점수 |
| --- | --- | --- | --- |
| 1 | (2,2), (1,1), (0,0) | 5 | 7 |
| 2 | (2,6) | 3 | 100 |

이 표와 위 키 값은 `scripts/check_observe_and_act.py`가 위 제출 코드를 그대로 돌려 다시 계산하고, 손으로 구한 값(`g`, `h`, `d`, 키, 목표 순서, 점수)과 대조합니다. 이 예시는 `h`의 이중 계산도 보여 줍니다. `(2,5)`의 `h = 62`에는 `(2,2)`의 2처럼 다른 방향의 칸이 섞여 있고, `(2,6)`의 `g`에 들어간 40은 `(2,5)`의 `h`에도 들어갑니다. 위 파라미터 표에서 큰 `WEIGHT`가 해로운 이유와 같은 현상입니다.

## 실패 사례를 재현하고 잡는다

세 가지 실수를 정책 2 코드에서 한 줄씩 고쳐 공개 채점기로 실제 점수를 쟀습니다.

| 실수 | 채점기 점수 합 | 거울 점수 합 | 거절 요청 | 시간 ms |
| --- | --- | --- | --- | --- |
| seen 초기화 누락 | 113322 | 98848 | 0 | 4 |
| seen 갱신 누락 | 20030 | 161665 | 0 | 19 |
| nextDay 누락 | 0 | 131259 | 0 | 9 |

- **`seen 초기화 누락`**: `resetCase`가 `seen`을 지우지 않으면 TC 1은 정상이고 TC 2부터 이전 TC에서 밟은 칸이 "이미 방문"으로 남습니다. 채점기는 그 칸에서도 점수를 주므로 거울이 실제보다 낮게 계산합니다. 점수는 131259에서 113322로 떨어지고, 거울이 98848로 계산해 두 값이 어긋납니다.
- **`seen 갱신 누락`**: 밟은 칸을 기록하지 않으면 BFS가 이미 먹은 칸의 가치를 계속 `gain`에 더해, 같은 언덕을 맴돌며 이동을 낭비합니다. 채점기 점수는 20030으로 폭락하고 거울은 161665로 부풀어 어긋납니다.
- **`nextDay 누락`**: 하루 한도를 `act`가 모르면 11번째 `move`가 무효가 되어 모든 TC가 0점입니다. 거울은 131259를 계산하므로 거절 요청이 0이어도 잡힙니다. 거절 카운터만 믿으면 놓치므로 반드시 점수 대조를 함께 합니다.

세 실수 모두 **`mirrorScore ≠ 채점기 점수`**로 잡힙니다. `scripts/check_observe_and_act.py`는 공개 채점기가 없어도 같은 규칙을 구현한 참조 채점기로 같은 대조를 합니다. 참조 채점기는 TC마다 다른 지도로 `h:1, z:0, c:2, e:3, h:1`, 즉 언덕 지도, 가치가 하나도 없는 지도, 왼쪽 위 모서리 시작, 오른쪽 아래 모서리 시작, 처음과 같은 지도를 연달아 돌립니다. 올바른 코드는 처음과 마지막의 같은 지도에서 점수가 같고(참조 지도에서 12687), `seen`을 지우지 않는 코드는 처음 12687, 마지막 10273으로 달라집니다. TC마다 입력 모양이 다른 문제에서는 이처럼 입력을 바꿔 연속 실행하는 검사가 TC 시작 초기화 실수를 찾는 가장 싼 방법입니다. 이 문제에서는 지도 크기가 고정이라 "크기를 바꾼다"를 내용(빈 지도·모서리 시작)을 바꾸는 것으로 대신합니다.

BFS의 `dist`와 `gain`은 모든 칸에서 별도의 직사각형 DP와 비교하고, 세 정책은 ASan/UBSan으로 참조 채점기와 공개 채점기에서 모두 실행했습니다.

## 예측한 평가값과 실제 점수의 차이

정책 2의 `key`는 예측이고 거울 점수는 실제입니다. 두 값이 어디서 갈라지는지 알려면 행동별 로그가 필요하지만, 제출 코드가 파일이나 화면에 쓰면 안 됩니다. 그래서 제출 코드에는 **함수 포인터 `mine::hook` 하나**만 두고 기본값은 비워 둡니다. 로컬에서만 채점기 사본에 아래 내용을 더해 훅을 연결합니다(실제 검사 스크립트는 같은 자리에 `MIRROR` 줄도 출력합니다).

```text
static int gTcNow;
static void logHook(int d, int g, int a) { printf("LOG %d %d %d %d\n", gTcNow, d, g, a); }
... process(gMapInfoBak, gPosY, gPosX); 앞에  gTcNow = tc; mine::hook = logHook;
```

한 결정마다 `(d, g, h)`가 기록됩니다. `g`는 걸으면 정확히 일치하므로(거울 점수 = 채점기 점수) 틀릴 수 있는 것은 `h`뿐입니다. `h`가 "여기서 더 얻을 값"이라는 예측이라면, 실제로는 **다음 결정에서 얻은 이득** `g_next`가 그 대응값입니다. 정책 2 기본값으로 10개 TC의 결정 318개에서 `h`의 합은 718017, 다음 결정의 `g` 합은 112550이고 비율은 0.1568입니다. 주변 값 1점이 평균 0.16점으로만 실현됩니다. 기본 `WEIGHT 0.1`은 이 비율보다 낮고, 위 표에서 최고 점수가 `WEIGHT 0.05`와 `0.1`에서 나온 것과 방향이 같습니다. 반면 `0.25` 이상에서는 비율을 넘겨 평가식이 먼 목표를 과대평가합니다. 이처럼 예측과 실제의 비율을 로그로 확인하면 파라미터 표를 읽는 근거가 생기고, 결정 수가 318개뿐이라는 한계도 함께 적어 둡니다. 비교 설계는 [실험 비교와 평가](https://h.readiz.com/learn/testing-and-stress/experiment-evaluation)를 따릅니다.

## 연습: MINEEXPLORE

[광산 탐사](/practice/MINEEXPLORE)에서 다음을 순서대로 수행합니다.

1. `mine-state`와 기준선을 제출해 모든 TC가 유효한지 확인합니다. 로컬 하네스에서 `mirrorScore`와 채점기 점수가 TC마다 같은지, `refused`가 0인지 확인합니다. 제출 화면의 점수와 표의 기준선 합 46422가 같으면 상태 설계가 맞습니다.
2. `queue`와 BFS 블록을 붙여 정책 1을 만들고, 표의 105823과 맞는지 비교합니다. 일부러 `seen` 초기화를 지워 점수와 거울 점수가 어긋나는 것을 확인합니다.
3. 평가식으로 정책 2를 만들고 `RADIUS`, `WEIGHT`, `COST`를 한 번에 하나씩 바꿉니다. 바꾼 값마다 점수 합과 시간을 기록하고, 채점 입력 10개만으로 정하지 말고 직접 만든 지도에서 점수가 유지되는지도 확인합니다. 통과 기준 120000이 목표입니다.

정책 2는 한 번에 목표 하나만 평가하는 탐욕입니다. 첫 목표를 고르기 전에 그 뒤의 목표까지 몇 개 더 보고 가장 좋은 연결을 남기는 방식이 [AIRCONTECH 빔 탐색](https://h.readiz.com/learn/heuristic/aircontech-beam-search)이며, 거기서도 예측 평가값과 실제 점수를 분리해 기록합니다.
