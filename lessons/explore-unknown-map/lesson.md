# tmp

```cpp snippet=rc-state
extern void scan(int floorState[3][3]);
extern int move(void);
extern void turn(int mCommand);

namespace rc {
const int S = 128, C = 64;         // 내 지도의 한 변, 시작 칸의 좌표
const int DY[4] = {-1, 0, 1, 0};
const int DX[4] = {0, -1, 0, 1};   // 0 시작 방향, 1 그 왼쪽, 2 뒤, 3 오른쪽. turn(k)은 방향에 k를 더한다
const int UNK = 0, FREE = 1, WALL = 2;

struct Robot {
    int y, x, dir;               // 내 지도에서 추정한 위치와 방향
    unsigned char cell[S][S];    // 내 지도: UNK, FREE, WALL
    bool seen[S][S];             // 밟아서 청소한 칸
};
struct Tally { long long cost; int scans, moves, bumps, turns; };

const int SCAN_MIN = 6;          // 3 x 3 안에 모르는 칸이 이만큼 이상이면 스캔한다 (0이면 매번, 9면 안 한다)

Robot R;
Tally T;                         // 이번 TC에서 내가 쓴 호출 수와 비용
int path[S * S];                 // 계획이 만든 이동 방향열

void reset() {                   // 새 실행(subtask)의 시작: 지난 지도는 좌표계가 달라 쓸 수 없다
    for (int y = 0; y < S; ++y) for (int x = 0; x < S; ++x) { R.cell[y][x] = UNK; R.seen[y][x] = false; }
    R.y = C; R.x = C; R.dir = 0;
    R.cell[C][C] = FREE; R.seen[C][C] = true;
}

void doScan() {
    int f[3][3];
    scan(f);
    T.cost += 20; ++T.scans;
    int fy = DY[R.dir], fx = DX[R.dir];                    // 앞쪽 단위 벡터
    int ry = DY[(R.dir + 3) % 4], rx = DX[(R.dir + 3) % 4]; // 오른쪽 단위 벡터
    for (int sy = 0; sy < 3; ++sy) for (int sx = 0; sx < 3; ++sx) {
        int ahead = 1 - sy, right = sx - 1;                // f[0][1]이 바로 앞 칸
        R.cell[R.y + ahead * fy + right * ry][R.x + ahead * fx + right * rx] = f[sy][sx] ? WALL : FREE;
    }
}

void face(int d) {
    int k = (d - R.dir + 4) % 4;   // 필요한 turn 명령과 같은 수
    if (k == 0) return;
    turn(k);
    T.cost += 15; ++T.turns;
    R.dir = d;
}

// d 방향으로 한 칸. 0 막힘, 1 이미 밟은 칸으로 이동, 2 새 칸으로 이동
int step(int d) {
    face(d);
    T.cost += 10;
    int ny = R.y + DY[d], nx = R.x + DX[d];
    if (!move()) { R.cell[ny][nx] = WALL; ++T.bumps; return 0; }   // 막히면 위치는 그대로
    ++T.moves;
    R.y = ny; R.x = nx; R.cell[ny][nx] = FREE;
    if (R.seen[ny][nx]) return 1;
    R.seen[ny][nx] = true;
    return 2;
}

int unknownAround() {            // 3 x 3 안에서 아직 모르는 칸 수
    int n = 0;
    for (int dy = -1; dy <= 1; ++dy) for (int dx = -1; dx <= 1; ++dx) n += R.cell[R.y + dy][R.x + dx] == UNK;
    return n;
}

// 계획한 방향열을 걷는다. 막히면 거기서 멈추고 호출한 쪽이 다시 계획한다
void walk(int n) {
    for (int i = 0; i < n; ++i) {
        int r = step(path[i]);
        if (r == 0) return;
        if (r == 2 && unknownAround() >= SCAN_MIN) doScan();
    }
}

void init() { T.cost = 0; T.scans = T.moves = T.bumps = T.turns = 0; }
}

void init() { rc::init(); }
```

```cpp snippet=rc-baseline
namespace rc {
int back[S * S];   // 지나온 길을 거꾸로 되돌아갈 방향들
}

void cleanHouse() {
    using namespace rc;
    reset();
    doScan();
    int top = 0;
    for (;;) {
        int go = -1;
        for (int d = 0; d < 4 && go < 0; ++d)       // 고정 순서: 아직 안 밟은 빈 칸
            if (R.cell[R.y + DY[d]][R.x + DX[d]] == FREE && !R.seen[R.y + DY[d]][R.x + DX[d]]) go = d;
        if (go >= 0) {
            back[top++] = (go + 2) % 4;
            step(go);
            doScan();                                  // 새 칸마다 스캔
        } else if (top > 0) {
            step(back[--top]);                         // 갈 곳이 없으면 한 칸 되돌아간다
        } else break;
    }
}
```

```cpp snippet=rc-bfs
namespace rc {
hc::Queue<S * S> Q;
int mark[S][S], markNow, enter[S][S];

// 밟은 칸 위로만 걸어 가장 가까운 "할 일 칸"까지의 방향열을 path에 담고 길이를 돌려준다. 없으면 0
int plan() {
    ++markNow; Q.clear();
    mark[R.y][R.x] = markNow; Q.push(R.y * S + R.x);
    int cur;
    while (Q.pop(cur)) {
        int y = cur / S, x = cur % S;
        for (int k = 0; k < 4; ++k) {
            int d = (R.dir + k) % 4;                  // 같은 거리면 지금 보는 방향부터
            int ny = y + DY[d], nx = x + DX[d];
            if (R.cell[ny][nx] == WALL || mark[ny][nx] == markNow) continue;
            mark[ny][nx] = markNow; enter[ny][nx] = d;
            if (!R.seen[ny][nx]) {                    // 처음 만난 안 밟은 칸이 가장 가깝다
                int n = 0, tmp[S * S];
                for (int cy = ny, cx = nx; cy != R.y || cx != R.x; ) {
                    int e = enter[cy][cx];
                    tmp[n++] = e; cy -= DY[e]; cx -= DX[e];
                }
                for (int i = 0; i < n; ++i) path[i] = tmp[n - 1 - i];
                return n;
            }
            Q.push(ny * S + nx);
        }
    }
    return 0;
}
}

void cleanHouse() {
    using namespace rc;
    reset();
    if (unknownAround() >= SCAN_MIN) doScan();
    for (int n; (n = plan()) > 0; ) walk(n);
}
```

```cpp snippet=rc-dijkstra
namespace rc {
const int TURN_W = 15;           // 계획에서 회전 한 번의 비용 (실제는 15)
const int UNK_PEN = 0;           // 모르는 칸에 들어갈 때 더하는 비용 (벽이면 헛걸음이라서)

hc::MinHeap<1 << 18> H;
int mark[S * S * 4], dist[S * S * 4], from[S * S * 4], markNow;

inline int id(int y, int x, int d) { return (y * S + x) * 4 + d; }

void relax(int a, int b, int nd) {
    if (mark[b] == markNow && dist[b] <= nd) return;
    mark[b] = markNow; dist[b] = nd; from[b] = a;
    H.push(nd, b);
}

// (칸, 방향) 상태의 최단 비용으로 가장 싼 "할 일 칸"까지의 방향열을 path에 담는다. 길이를 돌려주고, 없으면 0
int plan() {
    ++markNow; H.clear();
    int s0 = id(R.y, R.x, R.dir);
    mark[s0] = markNow; dist[s0] = 0; from[s0] = -1;
    H.push(0, s0);
    hc::HeapItem top;
    while (H.pop(top)) {
        int s = top.id;
        if (top.key > dist[s]) continue;               // 낡은 항목
        int d = s % 4, c = s / 4, y = c / S, x = c % S;
        if (!R.seen[y][x]) {                           // 처음 꺼낸 할 일 칸이 가장 싸다
            int n = 0, tmp[S * S];
            for (int t = s; from[t] >= 0; t = from[t])
                if (t / 4 != from[t] / 4) tmp[n++] = t % 4;   // 칸이 바뀐 상태만 이동
            for (int i = 0; i < n; ++i) path[i] = tmp[n - 1 - i];
            return n;
        }
        for (int k = 1; k < 4; ++k) relax(s, c * 4 + (d + k) % 4, dist[s] + TURN_W);
        int ny = y + DY[d], nx = x + DX[d];
        if (R.cell[ny][nx] != WALL) relax(s, id(ny, nx, d), dist[s] + 10 + (R.cell[ny][nx] == UNK ? UNK_PEN : 0));
    }
    return 0;
}
}

void cleanHouse() {
    using namespace rc;
    reset();
    if (unknownAround() >= SCAN_MIN) doScan();
    for (int n; (n = plan()) > 0; ) walk(n);
}
```

