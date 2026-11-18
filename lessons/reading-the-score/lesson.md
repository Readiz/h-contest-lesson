# 특수한 점수식 읽기: 채점식을 손으로 재현하고 성질을 풀이로 옮기기

```cpp snippet=ent-state
extern int getHeight();
extern int getWidth();
extern int getParticleCount();
extern long long getMoveLimit();
extern long long getMoveCount();
extern int getCell(int y, int x);
extern int moveParticle(int y, int x, int dir);

namespace ent {
const int MAXHW = 180, MAXN = MAXHW * MAXHW;
const int DY[4] = {-1, 0, 1, 0};
const int DX[4] = {0, 1, 0, -1};

struct World {
    int H, W, n;
    bool occ[MAXHW][MAXHW];          // 내가 기록한 점유
    int py[MAXN], px[MAXN];          // i번 입자의 위치
    int preY[MAXHW], preX[MAXHW];    // preY[r] = 행이 r 이하인 입자 수, preX[c]도 같은 뜻
    long long used, limit;           // 지금까지 부른 횟수(실패 포함), 한도
    long long e0, entropy;           // 시작 엔트로피, 내가 따라가는 현재 엔트로피
    int refused, mismatch;           // 내가 막은 요청 수, 채점기 반환값이 예측과 달랐던 수
};
World G;
long long mirrorScore;
void (*hook)(long long score, long long e0, long long e, long long used, int refused, int mismatch);
}
```

```cpp snippet=ent-score
namespace ent {
// 채점기 calc_entropy를 그대로 옮긴 O(n^2). 쌍마다 한 번(i < j)이고 누적은 long long이다.
long long entropyPairs() {
    long long e = 0;
    for (int i = 0; i < G.n; ++i)
        for (int j = i + 1; j < G.n; ++j) {
            int dy = G.py[i] - G.py[j]; if (dy < 0) dy = -dy;
            int dx = G.px[i] - G.px[j]; if (dx < 0) dx = -dx;
            e += dy + dx;
        }
    return e;
}

// 채점기 verify를 그대로 옮긴 점수. 나눗셈 두 곳과 형 변환 위치까지 같게 쓴다.
long long myScore(long long e0, long long e, long long used, long long limit) {
    long long improvement = e0 - e;
    if (improvement < 0) improvement = 0;
    double ratio = (double)improvement / (double)e0;
    long long entropyScore = (long long)(1000000.0 * ratio * ratio);
    long long moveBonus = (limit - used) / 100;
    return entropyScore + moveBonus;
}
}
```

```cpp snippet=ent-axis
namespace ent {
// 행·열 개수의 누적합. 입자 하나가 한 칸 움직이면 누적합 한 칸만 바뀐다.
void buildPre() {
    for (int r = 0; r < G.H; ++r) G.preY[r] = 0;
    for (int c = 0; c < G.W; ++c) G.preX[c] = 0;
    for (int i = 0; i < G.n; ++i) { ++G.preY[G.py[i]]; ++G.preX[G.px[i]]; }
    for (int r = 1; r < G.H; ++r) G.preY[r] += G.preY[r - 1];
    for (int c = 1; c < G.W; ++c) G.preX[c] += G.preX[c - 1];
}

// 엔트로피 = 행 경계마다 (위 개수 x 아래 개수)의 합 + 열 경계마다 (왼쪽 x 오른쪽)의 합. O(H + W)
long long entropyAxis() {
    long long e = 0;
    for (int r = 0; r + 1 < G.H; ++r) e += (long long)G.preY[r] * (G.n - G.preY[r]);
    for (int c = 0; c + 1 < G.W; ++c) e += (long long)G.preX[c] * (G.n - G.preX[c]);
    return e;
}

// (y, x)의 입자를 dir로 한 칸 옮길 때 엔트로피 변화량. 음수면 좋아진다. O(1)
long long delta(int y, int x, int dir) {
    long long n = G.n;
    if (dir == 0) return n - 1 - 2LL * (y > 0 ? G.preY[y - 1] : 0);
    if (dir == 1) return 2LL * G.preX[x] - 1 - n;
    if (dir == 2) return 2LL * G.preY[y] - 1 - n;
    return n - 1 - 2LL * (x > 0 ? G.preX[x - 1] : 0);
}
}
```

```cpp snippet=ent-act
namespace ent {
void init() {
    G.H = getHeight(); G.W = getWidth(); G.n = 0;
    for (int y = 0; y < G.H; ++y)
        for (int x = 0; x < G.W; ++x) {
            G.occ[y][x] = getCell(y, x) == 1;
            if (G.occ[y][x]) { G.py[G.n] = y; G.px[G.n] = x; ++G.n; }
        }
    G.used = getMoveCount(); G.limit = getMoveLimit();
    G.refused = G.mismatch = 0;
    buildPre();
    G.entropy = G.e0 = entropyAxis();
}

bool canMove(int y, int x, int dir) {
    if (G.used >= G.limit) return false;
    int ny = y + DY[dir], nx = x + DX[dir];
    return 0 <= ny && ny < G.H && 0 <= nx && nx < G.W && !G.occ[ny][nx];
}

// 채점기를 부르는 유일한 통로. 호출 전에 내 점유 격자로 먼저 거른다.
bool act(int i, int dir) {
    int y = G.py[i], x = G.px[i];
    if (!canMove(y, x, dir)) { ++G.refused; return false; }
    int ok = moveParticle(y, x, dir);
    ++G.used;                                  // 실패해도 채점기는 횟수를 센다
    if (!ok) { ++G.mismatch; return false; }
    G.entropy += delta(y, x, dir);             // 누적합을 바꾸기 전에 계산한다
    if (dir == 0) ++G.preY[y - 1];
    else if (dir == 1) --G.preX[x];
    else if (dir == 2) --G.preY[y];
    else ++G.preX[x - 1];
    G.occ[y][x] = false;
    G.py[i] = y + DY[dir]; G.px[i] = x + DX[dir];
    G.occ[G.py[i]][G.px[i]] = true;
    return true;
}

void finish() {
    mirrorScore = myScore(G.e0, G.entropy, G.used, G.limit);
    if (hook) hook(mirrorScore, G.e0, G.entropy, G.used, G.refused, G.mismatch);
}
}
```

```cpp snippet=ent-baseline
void process() {
    ent::init();      // 아무 행동도 하지 않는다
    ent::finish();
}
```

```cpp snippet=ent-naive
// 점수식을 모르는 탐욕: 격자 중앙 쪽으로 한 칸씩 민다.
void process() {
    ent::init();
    int cy = (ent::G.H - 1) / 2, cx = (ent::G.W - 1) / 2;
    for (bool moved = true; moved && ent::G.used < ent::G.limit; ) {
        moved = false;
        for (int i = 0; i < ent::G.n; ++i) {
            int dy = cy - ent::G.py[i], dx = cx - ent::G.px[i];
            int ady = dy < 0 ? -dy : dy, adx = dx < 0 ? -dx : dx;
            if (ady == 0 && adx == 0) continue;
            int dir = ady >= adx ? (dy < 0 ? 0 : 2) : (dx > 0 ? 1 : 3);
            if (ent::act(i, dir)) moved = true;
        }
    }
    ent::finish();
}
```

```cpp snippet=ent-greedy
namespace ent {
const int ORDER = 1;           // 0 입력 순서, 1 중앙에 가까운 입자부터, 2 먼 입자부터
const long long MINGAIN = 1;   // 이만큼 이상 줄어드는 이동만 한다
int order[MAXN];

int centerDist(int i) {
    int cy = (G.H - 1) / 2, cx = (G.W - 1) / 2;
    return (G.py[i] > cy ? G.py[i] - cy : cy - G.py[i]) + (G.px[i] > cx ? G.px[i] - cx : cx - G.px[i]);
}

// 중앙까지의 거리로 계수 정렬한다. 입력 순서면 그대로 둔다.
void buildOrder() {
    static int cnt[2 * MAXHW + 2];
    int top = G.H + G.W;
    for (int i = 0; i < G.n; ++i) order[i] = i;
    if (ORDER == 0) return;
    for (int k = 0; k <= top; ++k) cnt[k] = 0;
    for (int i = 0; i < G.n; ++i) ++cnt[ORDER == 1 ? centerDist(i) : top - centerDist(i)];
    for (int k = 1; k <= top; ++k) cnt[k] += cnt[k - 1];
    for (int i = G.n - 1; i >= 0; --i) order[--cnt[ORDER == 1 ? centerDist(i) : top - centerDist(i)]] = i;
}

// i번 입자가 지금 둘 수 있는 이동 중 가장 많이 줄이는 방향. minGain만큼 못 줄이면 -1
int bestDir(int i, long long minGain) {
    int best = -1; long long bestDelta = 0;
    for (int d = 0; d < 4; ++d) {
        if (!canMove(G.py[i], G.px[i], d)) continue;
        long long dl = delta(G.py[i], G.px[i], d);
        if (dl <= -minGain && dl < bestDelta) { bestDelta = dl; best = d; }
    }
    return best;
}

// 입자를 한 번씩 훑는다. 움직인 입자 수를 돌려준다.
int sweep(long long minGain) {
    buildOrder();
    int moved = 0;
    for (int k = 0; k < G.n; ++k) {
        int i = order[k], d = bestDir(i, minGain);
        if (d >= 0 && act(i, d)) ++moved;
    }
    return moved;
}

// 문턱 t 이상 줄이는 이동만, 더 못 움직일 때까지 훑는다. t를 n에서 3/4씩 1까지 줄인다.
void thresholdSweeps() {
    long long t = G.n;
    while (t >= 1 && G.used < G.limit) {
        while (G.used < G.limit && sweep(t) > 0) {}
        t = t == 1 ? 0 : (t * 3 / 4 > 0 ? t * 3 / 4 : 1);
    }
}
}
```

```cpp snippet=ent-entry-greedy
void process() {
    ent::init();
    while (ent::G.used < ent::G.limit && ent::sweep(ent::MINGAIN) > 0) {}
    ent::finish();
}
```

```cpp snippet=ent-entry-threshold
void process() {
    ent::init();
    ent::thresholdSweeps();
    ent::finish();
}
```

```cpp snippet=ent-relocate
namespace ent {
const long long MINPER = 10;       // 이동 한 번당 이만큼 이상 줄어야 옮긴다
long long Fx[MAXHW], Fy[MAXHW];    // Fx[c] = 모든 입자와 열 c의 열 거리 합, Fy[r]은 행 버전
int dist[MAXHW][MAXHW], from[MAXHW][MAXHW], que[MAXN];

// F(c + 1) = F(c) + 2 pre[c] - n 으로 누적합에서 만든다.
void buildF() {
    long long sx = 0, sy = 0;
    for (int c = 0; c < G.W; ++c) sx += (long long)c * (G.preX[c] - (c ? G.preX[c - 1] : 0));
    for (int r = 0; r < G.H; ++r) sy += (long long)r * (G.preY[r] - (r ? G.preY[r - 1] : 0));
    Fx[0] = sx; Fy[0] = sy;
    for (int c = 0; c + 1 < G.W; ++c) Fx[c + 1] = Fx[c] + 2LL * G.preX[c] - G.n;
    for (int r = 0; r + 1 < G.H; ++r) Fy[r + 1] = Fy[r] + 2LL * G.preY[r] - G.n;
}

int absv(int v) { return v < 0 ? -v : v; }

// a에서 b로 옮겼을 때 엔트로피 변화량. b의 F에서 자기 자신과의 거리 |b - a|를 뺀다.
long long relocateDelta(int ay, int ax, int by, int bx) {
    return Fx[bx] + Fy[by] - absv(bx - ax) - absv(by - ay) - Fx[ax] - Fy[ay];
}

// i번 입자를 빈 칸만 지나 갈 수 있는 가장 좋은 칸으로 보낸다. 옮겼으면 true
bool relocate(int i) {
    int ay = G.py[i], ax = G.px[i];
    buildF();
    for (int y = 0; y < G.H; ++y) for (int x = 0; x < G.W; ++x) dist[y][x] = -1;
    int head = 0, tail = 0, by = -1, bx = -1;
    long long bestDelta = 0;
    que[tail++] = ay * G.W + ax; dist[ay][ax] = 0;
    while (head < tail) {
        int y = que[head] / G.W, x = que[head] % G.W; ++head;
        for (int d = 0; d < 4; ++d) {
            int ny = y + DY[d], nx = x + DX[d];
            if (ny < 0 || ny >= G.H || nx < 0 || nx >= G.W || G.occ[ny][nx] || dist[ny][nx] >= 0) continue;
            dist[ny][nx] = dist[y][x] + 1; from[ny][nx] = d; que[tail++] = ny * G.W + nx;
            long long dl = relocateDelta(ay, ax, ny, nx);
            if (dl <= -MINPER * dist[ny][nx] && dl < bestDelta) { bestDelta = dl; by = ny; bx = nx; }
        }
    }
    if (by < 0 || G.used + dist[by][bx] > G.limit) return false;
    int dirs[MAXN], k = 0;
    for (int y = by, x = bx; y != ay || x != ax; ) { int d = from[y][x]; dirs[k++] = d; y -= DY[d]; x -= DX[d]; }
    while (k > 0) act(i, dirs[--k]);
    return true;
}

bool hasFreeNeighbor(int i) {
    for (int d = 0; d < 4; ++d) if (canMove(G.py[i], G.px[i], d)) return true;
    return false;
}
}
```

```cpp snippet=ent-entry-final
void process() {
    ent::init();
    ent::thresholdSweeps();
    for (bool moved = true; moved && ent::G.used < ent::G.limit; ) {
        moved = false;
        for (int i = 0; i < ent::G.n; ++i)
            if (ent::hasFreeNeighbor(i) && ent::relocate(i)) moved = true;
    }
    ent::finish();
}
```

```cpp snippet=ent-hand
extern int moveParticle(int y, int x, int dir);

void process() {
    moveParticle(0, 0, 1);   // (0,0)의 입자를 오른쪽으로: 성공
    moveParticle(0, 4, 1);   // (0,4)의 입자를 오른쪽으로: 격자 밖이라 실패, 횟수는 센다
    moveParticle(3, 0, 0);   // (3,0)의 입자를 위로: 성공
}
```
