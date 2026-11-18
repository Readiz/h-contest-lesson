# skeleton

```cpp snippet=coupang-contract
#define ABS(x) ((x) > 0 ? (x) : -(x))

struct Coordinates {
    int y, x;
    Coordinates() { y = x = 0; }
    Coordinates(int _y, int _x) { y = _y; x = _x; }
    int operator-(Coordinates& param) { return ABS(y - param.y) + ABS(x - param.x); }
};

struct Product {
    int id, count;
    Product() { id = count = 0; }
    Product(int _id, int _count) { id = _id; count = _count; }
};

extern int truckMove(int);
extern int truckLoading(int, int[], int);
```

```cpp snippet=coupang-state
namespace ship {
const int N = 1000, M = 10000, K = 1000000;  // 센터, 상품 종류, 배송 요청의 상한
const int CAP = 50;                          // 트럭 적재 상한
const int SIDE = 1000, CELL = 16;            // 좌표 범위, 칸의 한 변
const int G = (SIDE + CELL - 1) / CELL;      // 한 변의 칸 수

struct Item {                // 칸 안에 붙어 있는 후보 하나: 12바이트
    short y, x, prod;
    int id;
};

static int cy[N], cx[N];                          // 센터 좌표
static unsigned short stock[N][M];                // stock[c][p]: 센터 c에 남은 상품 p. 같은 상품이 두 줄이면 합친다.
static int listStart[M + 1], listCenter[N * 100]; // 상품 p를 가진 센터 번호 목록(CSR)
static int demand[M];                             // 상품 p의 남은 배송 수
static int mass[N];                               // sum of min(stock[c][p], demand[p]): 센터 c가 지금 더 실을 수 있는 배송 수의 상한
static Item slot[K];                              // 칸별로 이어 붙인 후보. 칸 안에서는 앞쪽 cellLive개만 남아 있다.
static int where[K];                              // where[id]: slot에서 배송 id의 위치
static int cellStart[G * G + 1], cellLive[G * G]; // 칸의 시작 위치, 남은 후보 수
static int centerCount, typeCount, deliveryCount;

inline int absInt(int v) { return v < 0 ? -v : v; }
inline int minInt(int a, int b) { return a < b ? a : b; }
inline int cellOf(int y, int x) { return (y / CELL) * G + x / CELL; }

void loadCenters(int n, int m, const Coordinates pos[], Product list[][100], const int size[]) {
    centerCount = n; typeCount = m;
    for (int c = 0; c < n; ++c) {
        cy[c] = pos[c].y; cx[c] = pos[c].x;
        for (int p = 0; p < m; ++p) stock[c][p] = 0;
        for (int j = 0; j < size[c]; ++j) stock[c][list[c][j].id] += list[c][j].count;
    }
}

// 칸마다 개수를 세어 시작 위치를 정하고(counting sort) 후보를 칸별로 이어 붙인다.
void loadDeliveries(int cnt, const Coordinates pos[], const int prod[]) {
    deliveryCount = cnt;
    for (int g = 0; g <= G * G; ++g) cellStart[g] = 0;
    for (int g = 0; g < G * G; ++g) cellLive[g] = 0;
    for (int i = 0; i < cnt; ++i) ++cellStart[cellOf(pos[i].y, pos[i].x) + 1];
    for (int g = 0; g < G * G; ++g) cellStart[g + 1] += cellStart[g];
    for (int i = 0; i < cnt; ++i) {
        int g = cellOf(pos[i].y, pos[i].x), w = cellStart[g] + cellLive[g]++;
        slot[w].y = (short)pos[i].y; slot[w].x = (short)pos[i].x; slot[w].prod = (short)prod[i]; slot[w].id = i;
        where[i] = w;
    }
}

// 두 목록을 모두 받은 뒤 한 번 부른다: 상품별 센터 목록, 남은 배송 수, 센터별 mass.
void prepare() {
    for (int p = 0; p <= typeCount; ++p) listStart[p] = 0;
    for (int p = 0; p < typeCount; ++p) demand[p] = 0;
    for (int c = 0; c < centerCount; ++c) mass[c] = 0;
    for (int c = 0; c < centerCount; ++c) for (int p = 0; p < typeCount; ++p) if (stock[c][p]) ++listStart[p + 1];
    for (int p = 0; p < typeCount; ++p) listStart[p + 1] += listStart[p];
    static int filled[M];
    for (int p = 0; p < typeCount; ++p) filled[p] = 0;
    for (int c = 0; c < centerCount; ++c) for (int p = 0; p < typeCount; ++p) if (stock[c][p]) listCenter[listStart[p] + filled[p]++] = c;
    for (int i = 0; i < deliveryCount; ++i) ++demand[slot[where[i]].prod];
    for (int p = 0; p < typeCount; ++p)
        for (int t = listStart[p]; t < listStart[p + 1]; ++t) mass[listCenter[t]] += minInt(stock[listCenter[t]][p], demand[p]);
}

// 센터 c가 배송 id를 맡는다. 칸에서 지우고(마지막 살아 있는 후보와 자리를 바꾼다) 재고, 남은 배송 수, mass를 고친다.
// 전제: 배송 id가 남아 있고 stock[c][상품] > 0
void take(int id, int c) {
    const int w = where[id], g = cellOf(slot[w].y, slot[w].x), last = cellStart[g] + --cellLive[g], p = slot[w].prod;
    Item moved = slot[last]; slot[last] = slot[w]; slot[w] = moved;
    where[slot[w].id] = w; where[slot[last].id] = last;
    for (int t = listStart[p]; t < listStart[p + 1]; ++t) {
        const int e = listCenter[t], s = stock[e][p];
        mass[e] += minInt(s - (e == c), demand[p] - 1) - minInt(s, demand[p]);
    }
    --stock[c][p]; --demand[p];
}
}
```

```cpp snippet=coupang-send
void sendCenterList(int N, int M, Coordinates centerCoordinatesList[], Product centerProductList[][100], int centerProductSize[]) {
    ship::loadCenters(N, M, centerCoordinatesList, centerProductList, centerProductSize);
}

void sendDeliveryList(int K, Coordinates deliveryCoordinatesList[], int deliveryProductList[]) {
    ship::loadDeliveries(K, deliveryCoordinatesList, deliveryProductList);
}
```

```cpp snippet=coupang-baseline
void solve(Coordinates truckCoordinates) {
    ship::prepare();
    int ty = truckCoordinates.y, tx = truckCoordinates.x;
    for (int id = 0; id < ship::deliveryCount; ++id) {
        const ship::Item it = ship::slot[ship::where[id]];  // take()가 칸 안의 자리를 바꾸므로 먼저 복사한다.
        int c = -1, bestDist = 1 << 30;
        for (int t = ship::listStart[it.prod]; t < ship::listStart[it.prod + 1]; ++t) {  // 이 상품을 가진 센터 중 트럭에서 가장 가까운 곳
            const int e = ship::listCenter[t];
            const int d = ship::absInt(ship::cy[e] - ty) + ship::absInt(ship::cx[e] - tx);
            if (ship::stock[e][it.prod] > 0 && d < bestDist) { bestDist = d; c = e; }
        }
        ship::take(id, c);
        int product = it.prod;
        truckLoading(c, &product, 1);
        truckMove(id);
        ty = it.y; tx = it.x;
    }
}
```

```cpp snippet=coupang-search
namespace ship {
// (y, x)에서 가장 가까운, 센터 c가 지금 실을 수 있는 배송의 번호. 없으면 -1.
// 칸을 가운데부터 한 겹(링)씩 넓혀 본다. 링 r을 보기 전에 남은 후보는 모두 (r-1)*CELL+1 이상 떨어져 있으므로
// 지금까지의 최선이 (r-1)*CELL 이하이면 더 볼 필요가 없다. extra >= 0이면 첫 후보가 나온 링에서 extra겹만 더 보고 멈춘다(근사).
int nearest(int y, int x, int c, int extra) {
    const int gy0 = y / CELL, gx0 = x / CELL;
    int best = -1, bestDist = 1 << 30, lastRing = G;
    for (int r = 0; r <= lastRing && r < G; ++r) {
        if (bestDist <= (r - 1) * CELL) break;
        for (int gy = gy0 - r; gy <= gy0 + r; ++gy) {
            if (gy < 0 || gy >= G) continue;
            const int step = (gy == gy0 - r || gy == gy0 + r || r == 0) ? 1 : 2 * r;  // 가운데 행은 양 끝 칸만
            for (int gx = gx0 - r; gx <= gx0 + r; gx += step) {
                if (gx < 0 || gx >= G) continue;
                const int g = gy * G + gx;
                const Item* it = slot + cellStart[g];
                for (int j = 0, n = cellLive[g]; j < n; ++j) {
                    if (stock[c][it[j].prod] == 0) continue;
                    const int d = absInt(it[j].y - y) + absInt(it[j].x - x);
                    if (d < bestDist) { bestDist = d; best = it[j].id; }
                }
            }
        }
        if (best >= 0 && extra >= 0 && lastRing == G) lastRing = r + extra;
    }
    return best;
}
}
```

```cpp snippet=coupang-trip
namespace ship {
// 센터 한 곳에서 싣고 나가는 한 번의 운행. s[0]은 센터, s[1..n]은 배달 순서다.
struct Stop { int id, prod, y, x; };
struct Trip { int n; Stop s[CAP + 1]; };

// 센터 c에서 출발해 가장 가까운 후보를 이어 붙인다. 고른 후보는 바로 take()로 지우므로 같은 후보를 두 번 고르지 않는다.
void build(Trip& t, int c, int load, int extra) {
    t.n = 0;
    t.s[0].id = -1; t.s[0].prod = -1; t.s[0].y = cy[c]; t.s[0].x = cx[c];
    while (t.n < load) {
        const Stop& from = t.s[t.n];
        const int id = nearest(from.y, from.x, c, extra);
        if (id < 0) break;
        const Item& it = slot[where[id]];
        Stop next = {id, it.prod, it.y, it.x};
        take(id, c);
        t.s[++t.n] = next;
    }
}

// i번째 구간(s[i-1] -> s[i])의 비용: 이 구간을 달릴 때 아직 싣고 있는 상품은 n-i+1개다.
inline int legCost(const Trip& t, int i) {
    return (100 + 10 * (t.n - i + 1)) * (absInt(t.s[i].y - t.s[i - 1].y) + absInt(t.s[i].x - t.s[i - 1].x));
}
inline int spanCost(const Trip& t, int lo, int hi) {  // 구간 lo..hi(끝은 n까지)
    int sum = 0;
    for (int i = lo; i <= hi && i <= t.n; ++i) sum += legCost(t, i);
    return sum;
}

// 배달 순서를 개선한다. 구간 뒤집기(2-opt)와 한 곳 옮기기(or-opt)를 줄어들 때만 적용하고 passes번까지 되풀이한다.
// 모든 이동은 영향을 받는 구간만 다시 계산한다.
void improve(Trip& t, int passes) {
    for (int pass = 0; pass < passes; ++pass) {
        bool better = false;
        for (int i = 1; i <= t.n; ++i) {
            for (int j = i + 1; j <= t.n; ++j) {
                const int before = spanCost(t, i, j + 1);
                for (int a = i, b = j; a < b; ++a, --b) { Stop tmp = t.s[a]; t.s[a] = t.s[b]; t.s[b] = tmp; }
                if (spanCost(t, i, j + 1) < before) { better = true; continue; }
                for (int a = i, b = j; a < b; ++a, --b) { Stop tmp = t.s[a]; t.s[a] = t.s[b]; t.s[b] = tmp; }
            }
        }
        for (int i = 1; i <= t.n; ++i) {
            for (int j = 1; j <= t.n; ++j) {
                if (i == j) continue;
                const int lo = i < j ? i : j, hi = (i < j ? j : i) + 1;
                const int before = spanCost(t, lo, hi);
                const Stop moved = t.s[i];
                if (i < j) for (int k = i; k < j; ++k) t.s[k] = t.s[k + 1];
                else for (int k = i; k > j; --k) t.s[k] = t.s[k - 1];
                t.s[j] = moved;
                if (spanCost(t, lo, hi) < before) { better = true; continue; }
                if (i < j) { for (int k = j; k > i; --k) t.s[k] = t.s[k - 1]; }
                else { for (int k = j; k < i; ++k) t.s[k] = t.s[k + 1]; }
                t.s[i] = moved;
            }
        }
        if (!better) break;
    }
}

// 센터를 고르는 비용 = 트럭에서 센터까지의 거리 + beta * sqrt(1e6 / mass[c]). 뒤의 항은 이 센터의 후보 밀도로 어림한 배송 간격이다.
// sqrt를 헤더 없이 쓰기 위해 16 * sqrt(1e6 / e)를 정수로 한 번 만들어 둔다.
static int spacing[20001];
int isqrt(long long v) {  // floor(sqrt(v)), v <= 2^40
    int lo = 0, hi = 1 << 20;
    while (lo < hi) {
        const int mid = (lo + hi + 1) / 2;
        if ((long long)mid * mid <= v) lo = mid; else hi = mid - 1;
    }
    return lo;
}
void makeSpacing() {
    spacing[0] = 1 << 28;
    for (int e = 1; e <= 20000; ++e) spacing[e] = isqrt(256LL * 1000000 / e);
}

int chooseCenter(int ty, int tx, int beta) {
    int best = -1;
    long long bestKey = 0;
    for (int c = 0; c < centerCount; ++c) {
        if (mass[c] <= 0) continue;
        const long long key = 16LL * (absInt(cy[c] - ty) + absInt(cx[c] - tx)) + (long long)beta * spacing[minInt(mass[c], 20000)];
        if (best < 0 || key < bestKey) { best = c; bestKey = key; }
    }
    return best;
}
}
```

```cpp snippet=coupang-entry
void solve(Coordinates truckCoordinates) {
    ship::prepare();
    ship::makeSpacing();
    int ty = truckCoordinates.y, tx = truckCoordinates.x;
    for (int left = ship::deliveryCount; left > 0;) {
        const int c = ship::chooseCenter(ty, tx, 25);
        if (c < 0) break;                       // 입력이 올바르면 오지 않는다.
        static ship::Trip trip;
        ship::build(trip, c, 20, -1);
        ship::improve(trip, 3);
        int prods[ship::CAP];
        for (int i = 0; i < trip.n; ++i) prods[i] = trip.s[i + 1].prod;
        truckLoading(c, prods, trip.n);
        for (int i = 1; i <= trip.n; ++i) truckMove(trip.s[i].id);
        ty = trip.s[trip.n].y; tx = trip.s[trip.n].x;
        left -= trip.n;
    }
}
```
