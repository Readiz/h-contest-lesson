# 관측과 행동을 나누는 문제

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
