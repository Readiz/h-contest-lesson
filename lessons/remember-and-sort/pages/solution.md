# 열어 본 상자를 기억해 쌓고 정렬하기: 풀이

높이 재기, 비우기, 정렬의 세 구간과 거울(`drone-mirror`)로 풀이를 나누고, 네 블록의 제출 코드를 완성합니다. 앞 단계는 [문제 계약과 점수 하한](contract-and-baseline.md)입니다.

## 세 구간으로 나눈 풀이

풀이는 한 TC를 세 구간으로 나눕니다. 구간 사이에서 거울만 믿습니다.

1. **높이 재기** (`measureHeights`): 칸을 뱀 모양으로 한 번 돌며 아래로 내려가 `move(5)`가 거절될 때의 `z`를 높이로 기록합니다. 막힌 칸은 한 칸 올라가 다시 시도합니다.
2. **비우기** (`clearCell`): 칸을 하나씩 비웁니다. 꺼낸 상자는 목적지 칸의 맨 위에 올립니다. 목적지 칸이 아직 열지 않은 칸이어도 상관없습니다. 올린 상자의 값은 거울에 남고, 그 칸을 비울 때 맨 위 `H - orig`개로 다시 나옵니다.
3. **정렬** (`sortCell`): 비우기가 끝나면 모든 칸에는 자기 목적지 상자만 순서 없이 쌓여 있습니다. 이제 칸마다 무게순으로 정렬합니다. 상자의 값은 전부 거울에 있어서 정렬 계획은 행동 없이 세울 수 있습니다.

비우기의 한 가지가 까다롭습니다. 칸 `c`를 비우려면 맨 위의 `H - orig`개(목적지가 `c`인 상자)부터 꺼내야 하는데, 꺼낸 상자를 `c`에 도로 놓을 수 없습니다. 그래서 옆 칸 `q`에 맡겼다가 `c`가 빈 뒤 돌려놓습니다. 맡기는 동안 `c`의 원래 상자 중 목적지가 `q`인 상자가 `q` 위에 도착하면 `q`의 맡긴 높이 `hb` 위가 섞입니다. 돌려놓을 때는 `hb` 위를 모두 꺼내 목적지가 `c`인 것만 `c`로 보내고, 나머지는 칸 `r`에 잠깐 두었다가 `q`로 되돌립니다. 이 경로는 상자 10개 중 하나가 특정 칸이 목적지일 확률이 약 0.1%라 공개 TC 10개에서 83번만 실행됩니다. 드물어서 큰 입력에서는 놓치기 쉽고, 아래 검사는 작은 창고에서 이 경로를 일부러 자주 만듭니다.

> **코드 환경: h-contest 제출용.** 아래 네 블록을 이 순서로 `user.cpp`에 붙입니다. 블록 이름 `drone-mirror`, `drone-clear`, `drone-sort`, `drone-entry`. 배열 상한은 `N = 100`이고, 칸 높이 98 이하·정렬할 상자 수 `k ≤ 98`이 인덱스 범위입니다. TC 초기화는 `process` 시작과 `measureHeights` 시작에 있습니다.

`drone-mirror`는 채점기 호출을 한 곳으로 모읍니다. `go`·`popTop`·`pushTop`이 거울을 갱신하는 유일한 통로이고, `goTo`가 거울의 높이로 날 높이를 정합니다. `TERRAIN`과 `CHOOSE_PATH`는 아래 [단계별 비교](experiments-and-failures.md)를 위해 바꾸는 상수입니다.

```cpp snippet=drone-mirror
extern bool move(int dir);
extern bool pick(int& destX, int& destY, int& weight);
extern bool drop();

namespace dr {
const int N = 100;               // 창고 한 변 (x, y, z 모두)
const bool TERRAIN = true;       // false면 항상 z = N - 1 로만 날아다닌다
const bool CHOOSE_PATH = true;   // false면 항상 x 방향부터 이동한다
const int DX[6] = {1, -1, 0, 0, 0, 0};
const int DY[6] = {0, 0, 1, -1, 0, 0};

int px, py, pz;          // 거울: 드론 위치
bool hold;               // 거울: 상자를 들고 있는가
int H[N][N];             // 거울: 칸의 상자 높이
int orig[N][N];          // 바닥부터 아직 열어 보지 않은 상자 수
short bd[N][N][N];       // 열어 본 상자의 목적지 칸 번호 dy * N + dx
short bw[N][N][N];       // 열어 본 상자의 무게
int stage;               // 0 높이 재기, 1 비우기, 2 정렬 (로컬 검사가 읽는다)
int refused, mismatch;   // 거절된 호출 수, 거울과 다른 pick 결과 수
int deferred, fallbacks; // 비켜 둔 상자 수, 삽입 정렬로 물러난 칸 수 (로컬 검사용 계수)
int ox[N * N], oy[N * N];   // 칸을 도는 순서 (뱀 모양)

bool go(int dir) {       // 채점기 move 호출은 모두 여기를 지난다
    if (!move(dir)) return false;
    px += DX[dir]; py += DY[dir];
    if (dir == 4) ++pz; else if (dir == 5) --pz;
    return true;
}
void must(int dir) { if (!go(dir)) ++refused; }

int req(int x, int y) { return H[y][x] + (hold ? 1 : 0); }   // 이 칸에 들어갈 때 필요한 최소 z

void vz(int z) { while (pz < z) must(4); while (pz > z) must(5); }

// (tx, ty) 위 높이 tz로 간다. 지나는 칸의 높이는 거울로 안다.
void goTo(int tx, int ty, int tz) {
    if (px == tx && py == ty) { vz(tz); return; }
    int a = req(px, py), b = a;                                       // a: x 먼저, b: y 먼저
    for (int x = px; x != tx; ) { x += tx > px ? 1 : -1; if (req(x, py) > a) a = req(x, py); }
    for (int y = py; y != ty; ) { y += ty > py ? 1 : -1; if (req(tx, y) > a) a = req(tx, y); }
    for (int y = py; y != ty; ) { y += ty > py ? 1 : -1; if (req(px, y) > b) b = req(px, y); }
    for (int x = px; x != tx; ) { x += tx > px ? 1 : -1; if (req(x, ty) > b) b = req(x, ty); }
    bool xFirst = !CHOOSE_PATH || a <= b;
    vz(TERRAIN ? (xFirst ? a : b) : N - 1);
    if (xFirst) {
        while (px < tx) must(0); while (px > tx) must(1);
        while (py < ty) must(2); while (py > ty) must(3);
    } else {
        while (py < ty) must(2); while (py > ty) must(3);
        while (px < tx) must(0); while (px > tx) must(1);
    }
    vz(tz);
}

// 전제: 상자를 들지 않았고 pz == H[py][px] > 0. 열어 본 값을 거울에 남긴다.
void popTop(int& dx, int& dy, int& w) {
    if (!pick(dx, dy, w)) { ++refused; return; }
    hold = true;
    int h = --H[py][px];
    if (h < orig[py][px]) orig[py][px] = h;                           // 원래 상자를 처음 열었다
    else if (bd[py][px][h] != dy * N + dx || bw[py][px][h] != w) ++mismatch;   // 기억과 달랐다
}

// 전제: 상자를 들었고 pz == H[py][px] + 1
void pushTop(int dx, int dy, int w) {
    if (!drop()) { ++refused; return; }
    int h = H[py][px]++;
    bd[py][px][h] = dy * N + dx; bw[py][px][h] = w;
    hold = false;
}

// (sx, sy)의 맨 위 상자를 (tx, ty)의 맨 위로 옮긴다. 상자 내용은 pick 결과를 그대로 쓴다.
void shift(int sx, int sy, int tx, int ty) {
    goTo(sx, sy, H[sy][sx]);
    int dx, dy, w; popTop(dx, dy, w);
    goTo(tx, ty, H[ty][tx] + 1);
    pushTop(dx, dy, w);
}
}
```

`popTop`은 `pick`이 돌려준 값을 거울과 대조해 `mismatch`를 셉니다. 이 값은 정상이면 항상 0이고, 기억이 어긋난 코드는 첫 `pick`에서 0이 아니게 됩니다. `drone-clear`에는 높이 재기와 비우기가 있습니다.

```cpp snippet=drone-clear
namespace dr {
// 0단계: 모든 칸의 높이를 잰다. 내려가다 막히면 그 z가 높이다.
void measureHeights() {
    stage = 0;
    px = py = pz = N - 1; hold = false;                              // TC 시작 위치
    for (int i = 0; i < N * N; ++i) {
        if (i > 0) {
            int dir = ox[i] != ox[i - 1] ? (ox[i] > ox[i - 1] ? 0 : 1) : 3;
            while (!go(dir)) go(4);                                  // 높이를 모르니 막히면 한 칸 올라가 다시
        }
        while (go(5)) {}
        H[oy[i]][ox[i]] = pz; orig[oy[i]][ox[i]] = pz;
    }
}

// 칸 (cx, cy)의 상자를 모두 꺼내 각자의 목적지 맨 위로 보낸다.
// 목적지가 이 칸인 상자는 옆 칸 q에 맡겼다가 칸이 빈 뒤 돌려놓는다.
void clearCell(int cx, int cy) {
    if (H[cy][cx] == 0) return;
    int qx = cx > 0 ? cx - 1 : cx + 1, qy = cy;                      // 맡기는 칸
    int rx = qx, ry = qy > 0 ? qy - 1 : qy + 1;                      // 잠깐 비켜 둘 칸
    int hb = H[qy][qx];                                              // 맡기기 전 q의 높이
    while (H[cy][cx] > 0) {
        goTo(cx, cy, H[cy][cx]);
        int dx, dy, w; popTop(dx, dy, w);
        if (dx == cx && dy == cy) goTo(qx, qy, H[qy][qx] + 1);
        else goTo(dx, dy, H[dy][dx] + 1);
        pushTop(dx, dy, w);
    }
    int moved = 0;
    while (H[qy][qx] > hb) {                                         // q의 hb 위는 전부 거울이 아는 상자
        goTo(qx, qy, H[qy][qx]);
        int dx, dy, w; popTop(dx, dy, w);
        if (dx == cx && dy == cy) goTo(cx, cy, H[cy][cx] + 1);
        else { goTo(rx, ry, H[ry][rx] + 1); ++moved; }               // 맡기는 동안 q로 온 q의 상자
        pushTop(dx, dy, w);
    }
    deferred += moved;
    for (; moved > 0; --moved) shift(rx, ry, qx, qy);
}
}
```

`drone-sort`는 정렬 두 가지를 모두 담습니다. `PATIENCE`를 `false`로 두면 삽입 정렬만 씁니다.

```cpp snippet=drone-sort
namespace dr {
const bool PATIENCE = true;      // false면 삽입 정렬만 쓴다
const bool DIAGONAL = true;      // false면 위아래좌우 4칸만 임시 칸으로 쓴다

// 바닥에서 위로 무게가 줄어들지 않으면(같으면 허용) 이미 끝난 칸이다.
bool sorted(int cx, int cy) {
    for (int i = 1; i < H[cy][cx]; ++i) if (bw[cy][cx][i] > bw[cy][cx][i - 1]) return false;
    return true;
}

// 삽입 정렬: 위쪽을 s로 옮긴 뒤 하나씩 제자리에 끼운다. 옮기는 횟수는 역전 수에 비례한다.
void insertionSort(int cx, int cy) {
    int k = H[cy][cx], keep = 1;
    while (keep < k && bw[cy][cx][keep] <= bw[cy][cx][keep - 1]) ++keep;   // 바닥에서 이미 정렬된 부분
    int sx = cx > 0 ? cx - 1 : cx + 1, sy = cy;
    int tx = cx, ty = cy > 0 ? cy - 1 : cy + 1;
    for (int i = k - keep; i > 0; --i) shift(cx, cy, sx, sy);
    for (int i = k - keep; i > 0; --i) {
        int w = bw[sy][sx][H[sy][sx] - 1], j = 0;
        while (j < H[cy][cx] && bw[cy][cx][H[cy][cx] - 1 - j] < w) ++j;    // w보다 가벼워 비켜야 할 상자 수
        for (int t = 0; t < j; ++t) shift(cx, cy, tx, ty);
        shift(sx, sy, cx, cy);
        for (int t = 0; t < j; ++t) shift(tx, ty, cx, cy);
    }
}

// 인내 정렬 후 병합: 무게를 다 아니, 임시 칸마다 "위로 갈수록 무거운" 더미를 만들고
// 가장 무거운 윗면부터 골라 빈 칸에 쌓는다. 상자는 두 번만 움직인다.
bool patienceSort(int cx, int cy) {
    int k = H[cy][cx];
    int scx[8], scy[8], ns = 0;
    for (int dy = -1; dy <= 1; ++dy) for (int dx = -1; dx <= 1; ++dx) {
        int x = cx + dx, y = cy + dy;
        if ((dx || dy) && (DIAGONAL || !dx || !dy) && x >= 0 && x < N && y >= 0 && y < N) {
            scx[ns] = x; scy[ns] = y; ++ns;
        }
    }
    int top[8], onS[8], to[N];
    for (int j = 0; j < ns; ++j) top[j] = onS[j] = 0;
    for (int i = k - 1; i >= 0; --i) {                               // 계획만 세운다: 행동은 아직 없다
        int w = bw[cy][cx][i], best = -1;
        for (int j = 0; j < ns; ++j) if (top[j] <= w && (best < 0 || top[j] > top[best])) best = j;
        if (best < 0) return false;                                  // 임시 칸이 모자란다
        to[i] = best; top[best] = w; ++onS[best];
    }
    for (int i = k - 1; i >= 0; --i) shift(cx, cy, scx[to[i]], scy[to[i]]);
    for (int t = 0; t < k; ++t) {                                    // 가장 무거운 윗면부터 빈 칸에 쌓는다
        int best = -1, bt = -1;
        for (int j = 0; j < ns; ++j) {
            if (onS[j] == 0) continue;
            int w = bw[scy[j]][scx[j]][H[scy[j]][scx[j]] - 1];
            if (w > bt) { bt = w; best = j; }
        }
        shift(scx[best], scy[best], cx, cy); --onS[best];
    }
    return true;
}

void sortCell(int cx, int cy) {
    if (H[cy][cx] <= 1 || sorted(cx, cy)) return;
    if (PATIENCE && patienceSort(cx, cy)) return;
    if (PATIENCE) ++fallbacks;
    insertionSort(cx, cy);
}
}
```

`drone-entry`가 구간을 잇습니다.

```cpp snippet=drone-entry
void process() {
    using namespace dr;
    refused = mismatch = deferred = fallbacks = 0;
    for (int y = 0; y < N; ++y) for (int x = 0; x < N; ++x) H[y][x] = orig[y][x] = 0;
    for (int r = 0; r < N; ++r) for (int i = 0; i < N; ++i) {
        ox[r * N + i] = r % 2 == 0 ? N - 1 - i : i;                  // 드론이 있는 (99, 99)에서 시작
        oy[r * N + i] = N - 1 - r;
    }
    measureHeights();
    stage = 1;
    for (int i = 0; i < N * N; ++i) clearCell(ox[i], oy[i]);
    stage = 2;
    for (int i = 0; i < N * N; ++i) sortCell(ox[i], oy[i]);
}
```
