# 임시

```cpp snippet=land-state
#define MAP_SIZE (1000)
#define SPACESHIP_SIZE (10000)

struct Spaceship {
    int height;
    int width;
};

namespace land {
const int MAX_CAND = 16384;  // 가능한 직사각형 위치(후보)의 상한
const int KINDS = 16;        // 종류 번호 = (짧은 변 - 2) * 4 + (긴 변 - 2)
const int MAX_OWNERS = 32;

const int (*heightMap)[MAP_SIZE];
int candCount;
short candRow[MAX_CAND], candCol[MAX_CAND];
unsigned char candH[MAX_CAND], candW[MAX_CAND];  // 놓았을 때의 세로·가로(회전 반영)
int candWeight[MAX_CAND], candKind[MAX_CAND];
int kindBegin[KINDS], kindEnd[KINDS];            // 종류별 후보 구간 [begin, end)
int kindLimit[KINDS];                            // 종류별 우주선 수

int kindOf(int a, int b) { return ((a < b ? a : b) - 2) * 4 + ((a < b ? b : a) - 2); }
int weightOf(int a, int b) { return a * b * (a < b ? a : b); }

// 점유 격자와 선택 목록. 제출할 답은 picked[]이고 나머지는 계산을 빠르게 하는 보조 값이다.
struct Board {
    int owner[MAP_SIZE][MAP_SIZE];  // 칸을 덮는 선택된 후보 번호, 비었으면 -1
    int have[KINDS];                // 종류별 선택 수
    int picked[MAX_CAND];           // 선택된 후보 번호들
    int slot[MAX_CAND];             // 후보 -> picked 안의 위치, 선택 안 했으면 -1
    int count;
    long long score;
};

void clear(Board& bd) {
    for (int y = 0; y < MAP_SIZE; ++y)
        for (int x = 0; x < MAP_SIZE; ++x) bd.owner[y][x] = -1;
    for (int k = 0; k < KINDS; ++k) bd.have[k] = 0;
    for (int c = 0; c < MAX_CAND; ++c) bd.slot[c] = -1;
    bd.count = 0;
    bd.score = 0;
}

// 직사각형 한 개의 유효성을 한 곳에서 판정한다. 0: 가능, 1: 지도 밖, 2: 고도 차, 3: 겹침
int reason(const Board& bd, int r, int c, int a, int b) {
    if (r < 0 || c < 0 || r + a > MAP_SIZE || c + b > MAP_SIZE) return 1;
    int v[4] = {heightMap[r][c], heightMap[r][c + b - 1], heightMap[r + a - 1][c], heightMap[r + a - 1][c + b - 1]};
    int lo = v[0], hi = v[0];
    for (int i = 1; i < 4; ++i) {
        if (v[i] < lo) lo = v[i];
        if (v[i] > hi) hi = v[i];
    }
    if (hi - lo > 6) return 2;
    for (int y = r; y < r + a; ++y)
        for (int x = c; x < c + b; ++x)
            if (bd.owner[y][x] >= 0) return 3;
    return 0;
}

// 후보 c와 겹치는 선택 후보의 서로 다른 번호를 out에 담고 개수를 돌려준다.
int owners(const Board& bd, int c, int out[]) {
    int n = 0;
    for (int y = candRow[c]; y < candRow[c] + candH[c]; ++y)
        for (int x = candCol[c]; x < candCol[c] + candW[c]; ++x) {
            int o = bd.owner[y][x];
            if (o < 0) continue;
            int i = 0;
            while (i < n && out[i] != o) ++i;
            if (i == n) out[n++] = o;
        }
    return n;
}

// 제안 단계의 검사: 종류별 우주선이 남아 있고 선택된 후보와 겹치지 않는가
bool canAdd(const Board& bd, int c) {
    if (bd.have[candKind[c]] >= kindLimit[candKind[c]]) return false;
    for (int y = candRow[c]; y < candRow[c] + candH[c]; ++y)
        for (int x = candCol[c]; x < candCol[c] + candW[c]; ++x)
            if (bd.owner[y][x] >= 0) return false;
    return true;
}

void paint(Board& bd, int c, int value) {
    for (int y = candRow[c]; y < candRow[c] + candH[c]; ++y)
        for (int x = candCol[c]; x < candCol[c] + candW[c]; ++x) bd.owner[y][x] = value;
}

// 전제: canAdd(bd, c)
void put(Board& bd, int c) {
    paint(bd, c, c);
    ++bd.have[candKind[c]];
    bd.slot[c] = bd.count;
    bd.picked[bd.count++] = c;
    bd.score += candWeight[c];
}

// 전제: 후보 c가 선택돼 있다.
void take(Board& bd, int c) {
    paint(bd, c, -1);
    --bd.have[candKind[c]];
    int last = bd.picked[--bd.count];
    bd.picked[bd.slot[c]] = last;
    bd.slot[last] = bd.slot[c];
    bd.slot[c] = -1;
    bd.score -= candWeight[c];
}

// 점유 격자를 picked[]와 대조한다. 선택 후보의 칸은 모두 자기 번호이고 그 밖의 칸은 비어 있어야 한다.
bool consistent(const Board& bd) {
    long long cells = 0, score = 0;
    int have[KINDS] = {0};
    for (int i = 0; i < bd.count; ++i) {
        int c = bd.picked[i];
        if (bd.slot[c] != i) return false;
        for (int y = candRow[c]; y < candRow[c] + candH[c]; ++y)
            for (int x = candCol[c]; x < candCol[c] + candW[c]; ++x)
                if (bd.owner[y][x] != c) return false;
        cells += candH[c] * candW[c];
        score += candWeight[c];
        ++have[candKind[c]];
    }
    long long taken = 0;
    for (int y = 0; y < MAP_SIZE; ++y)
        for (int x = 0; x < MAP_SIZE; ++x)
            if (bd.owner[y][x] >= 0) ++taken;
    for (int k = 0; k < KINDS; ++k)
        if (have[k] != bd.have[k] || have[k] > kindLimit[k]) return false;
    return taken == cells && score == bd.score;
}
}
```

```cpp snippet=land-build
namespace land {
const Spaceship* shipList;
int shipCount;
int kindStart[KINDS + 1], kindShips[SPACESHIP_SIZE];  // 종류별 우주선 번호 목록(제출 때 배정)
int candBlocked[MAX_CAND];                           // 후보가 지나는 칸의 겹침 수 합(혼잡도)

// 지도와 우주선 목록에서 후보를 모두 만든다. empty는 clear()한 빈 보드이다.
void build(int map[][MAP_SIZE], const Spaceship ships[], int n, const Board& empty) {
    static unsigned short cover[MAP_SIZE][MAP_SIZE];
    heightMap = map;
    shipList = ships;
    shipCount = n;
    for (int k = 0; k < KINDS; ++k) kindLimit[k] = 0;
    for (int i = 0; i < shipCount; ++i) ++kindLimit[kindOf(ships[i].height, ships[i].width)];
    candCount = 0;
    for (int lo = 2; lo <= 5; ++lo) {
        for (int hi = lo; hi <= 5; ++hi) {
            int k = kindOf(lo, hi);
            kindBegin[k] = candCount;
            int turns = kindLimit[k] == 0 ? 0 : (lo == hi ? 1 : 2);  // 우주선이 없는 종류는 후보를 만들지 않는다.
            for (int turn = 0; turn < turns; ++turn) {
                int a = turn == 0 ? lo : hi, b = turn == 0 ? hi : lo;
                for (int r = 0; r + a <= MAP_SIZE; ++r)
                    for (int c = 0; c + b <= MAP_SIZE; ++c) {
                        if (reason(empty, r, c, a, b) != 0 || candCount == MAX_CAND) continue;
                        int id = candCount++;
                        candRow[id] = (short)r; candCol[id] = (short)c;
                        candH[id] = (unsigned char)a; candW[id] = (unsigned char)b;
                        candWeight[id] = weightOf(a, b);
                        candKind[id] = k;
                    }
            }
            kindEnd[k] = candCount;
        }
    }
    for (int y = 0; y < MAP_SIZE; ++y)
        for (int x = 0; x < MAP_SIZE; ++x) cover[y][x] = 0;
    for (int c = 0; c < candCount; ++c)
        for (int y = candRow[c]; y < candRow[c] + candH[c]; ++y)
            for (int x = candCol[c]; x < candCol[c] + candW[c]; ++x) ++cover[y][x];
    for (int c = 0; c < candCount; ++c) {
        candBlocked[c] = 0;
        for (int y = candRow[c]; y < candRow[c] + candH[c]; ++y)
            for (int x = candCol[c]; x < candCol[c] + candW[c]; ++x) candBlocked[c] += cover[y][x] - 1;
    }
    for (int k = 0; k <= KINDS; ++k) kindStart[k] = 0;
    for (int i = 0; i < shipCount; ++i) ++kindStart[kindOf(ships[i].height, ships[i].width) + 1];
    for (int k = 0; k < KINDS; ++k) kindStart[k + 1] += kindStart[k];
    int fill[KINDS] = {0};
    for (int i = 0; i < shipCount; ++i) {
        int k = kindOf(ships[i].height, ships[i].width);
        kindShips[kindStart[k] + fill[k]++] = i;
    }
}

// 선택된 후보를 우주선 번호에 배정해 row/col/dir로 옮긴다.
void submit(const Board& bd, int row[], int col[], int dir[]) {
    int used[KINDS] = {0};
    for (int i = 0; i < shipCount; ++i) row[i] = col[i] = dir[i] = -1;
    for (int p = 0; p < bd.count; ++p) {
        int c = bd.picked[p], k = candKind[c];
        int ship = kindShips[kindStart[k] + used[k]++];  // canAdd가 개수를 보장한다.
        row[ship] = candRow[c];
        col[ship] = candCol[c];
        dir[ship] = (candH[c] == shipList[ship].height && candW[c] == shipList[ship].width) ? 0 : 1;
    }
}
}
```

```cpp snippet=land-greedy
namespace land {
long long evaluations;  // 후보 검사 횟수. 모든 방법의 예산 단위이다.

bool tryPut(Board& bd, int c) {
    ++evaluations;
    if (!canAdd(bd, c)) return false;
    put(bd, c);
    return true;
}

// 기준선: 우주선을 입력 순서대로 보고, 자기 종류의 후보 중 지도 순서로 처음 들어가는 곳에 놓는다.
void firstFit(Board& bd) {
    for (int i = 0; i < shipCount; ++i) {
        int k = kindOf(shipList[i].height, shipList[i].width);
        for (int c = kindBegin[k]; c < kindEnd[k]; ++c)
            if (tryPut(bd, c)) break;
    }
}

// 후보를 key 오름차순으로 한 번 훑으며 들어가는 대로 놓는다. order/temp는 candCount칸 이상.
void sweep(Board& bd, const long long key[], int order[], int temp[]) {
    for (int c = 0; c < candCount; ++c) order[c] = c;
    hc::sortIds(order, temp, candCount, key);
    for (int i = 0; i < candCount; ++i) tryPut(bd, order[i]);
}
}
```

```cpp snippet=land-local
namespace land {
struct Move {
    int add;          // 새로 선택할 후보
    int drop;         // 대신 뺄 후보, 없으면 -1
    long long delta;  // 점수 변화
};

// 후보 x를 넣는 이동을 평가한다. board는 바꾸지 않는다.
// 겹치는 선택 후보가 0개면 추가, 1개면 교체이고 2개 이상이면 이 이웃에서는 제안하지 않는다.
bool evaluate(const Board& bd, int x, Move& mv) {
    ++evaluations;
    int own[MAX_OWNERS];
    int n = owners(bd, x, own);
    if (n > 1) return false;
    int kind = candKind[x];
    int drop = n == 1 ? own[0] : -1;
    int have = bd.have[kind] - ((drop >= 0 && candKind[drop] == kind) ? 1 : 0);
    if (have >= kindLimit[kind]) return false;  // 종류별 우주선 수를 넘을 수 없다.
    mv.add = x;
    mv.drop = drop;
    mv.delta = candWeight[x] - (drop >= 0 ? candWeight[drop] : 0);
    return true;
}

void apply(Board& bd, const Move& mv) {
    if (mv.drop >= 0) take(bd, mv.drop);
    put(bd, mv.add);
}

// 점수가 줄지 않는 이동만 받는다. budget만큼 후보를 평가한다.
void hillClimb(Board& bd, hc::Random& rng, long long budget) {
    long long stop = evaluations + budget;
    while (evaluations < stop && candCount > 0) {
        int x = (int)rng.below((unsigned)candCount);
        if (bd.slot[x] >= 0) { ++evaluations; continue; }  // 이미 선택한 후보
        Move mv;
        if (evaluate(bd, x, mv) && mv.delta >= 0) apply(bd, mv);
    }
}
}
```

```cpp snippet=land-destroy
namespace land {
const int BUCKET = 16;
const int BUCKETS = (MAP_SIZE + BUCKET - 1) / BUCKET;
const int POOL_MAX = 2048;
int bucketHead[BUCKETS][BUCKETS];  // 후보 시작 칸 기준의 구역 목록
int bucketNext[MAX_CAND];
int stampOf[MAX_CAND], stampNow;

void buildBuckets() {
    for (int i = 0; i < BUCKETS; ++i)
        for (int j = 0; j < BUCKETS; ++j) bucketHead[i][j] = -1;
    for (int c = 0; c < candCount; ++c) {
        int& head = bucketHead[candRow[c] / BUCKET][candCol[c] / BUCKET];
        bucketNext[c] = head;
        head = c;
    }
    for (int c = 0; c < MAX_CAND; ++c) stampOf[c] = 0;
}

// 칸 범위 [r0,r1] x [c0,c1]와 겹치는 후보를 pool[n..]에 덧붙인다. 같은 stampNow에서는 한 번씩만 넣는다.
int collect(int r0, int c0, int r1, int c1, int pool[], int n) {
    int br0 = (r0 > 4 ? r0 - 4 : 0) / BUCKET, br1 = (r1 < MAP_SIZE - 1 ? r1 : MAP_SIZE - 1) / BUCKET;
    int bc0 = (c0 > 4 ? c0 - 4 : 0) / BUCKET, bc1 = (c1 < MAP_SIZE - 1 ? c1 : MAP_SIZE - 1) / BUCKET;
    for (int br = br0; br <= br1; ++br)
        for (int bc = bc0; bc <= bc1; ++bc)
            for (int c = bucketHead[br][bc]; c >= 0; c = bucketNext[c]) {
                if (stampOf[c] == stampNow || n == POOL_MAX) continue;
                if (candRow[c] + candH[c] - 1 < r0 || candRow[c] > r1) continue;
                if (candCol[c] + candW[c] - 1 < c0 || candCol[c] > c1) continue;
                stampOf[c] = stampNow;
                pool[n++] = c;
            }
    return n;
}

// 되돌리기 기록: 마지막 작업부터 거꾸로 뒤집으면 직전 상태가 된다.
// 한 번의 destroy/repair가 만드는 작업은 빼기 최대 POOL_MAX개와 넣기 최대 POOL_MAX개이다.
const int LOG_MAX = 2 * POOL_MAX;
struct Op { int cand; bool added; };
Op opLog[LOG_MAX];
int opCount;

void logPut(Board& bd, int c) {
    put(bd, c);
    opLog[opCount].cand = c;
    opLog[opCount++].added = true;
}
void logTake(Board& bd, int c) {
    take(bd, c);
    opLog[opCount].cand = c;
    opLog[opCount++].added = false;
}
void undo(Board& bd) {
    while (opCount > 0) {
        const Op& op = opLog[--opCount];
        if (op.added) take(bd, op.cand);
        else put(bd, op.cand);
    }
}

enum DestroyMode { REGION = 0, RANDOM_K = 1, LOWEST_K = 2 };

struct DestroyParams {
    int mode;
    int size;      // REGION: 선택한 후보 주위 여백 칸 수, 나머지: 뺄 후보 수 k
    int noise;     // 다시 채울 때 점수에 곱하는 무작위 배율의 폭(백분율). 0이면 점수 순서 그대로
};

// 후보 한 번의 destroy/repair. 나빠지면 되돌린다. 뺀 후보 수를 돌려준다.
int destroyRepair(Board& bd, hc::Random& rng, const DestroyParams& prm) {
    static int pool[POOL_MAX], temp[POOL_MAX];
    static long long key[MAX_CAND];
    if (bd.count == 0) { ++evaluations; return 0; }
    long long before = bd.score;
    int removed = 0, n = 0;
    opCount = 0;
    ++stampNow;
    if (prm.mode == REGION) {
        int y = bd.picked[rng.below((unsigned)bd.count)];
        n = collect(candRow[y] - prm.size, candCol[y] - prm.size, candRow[y] + candH[y] + prm.size - 1,
                    candCol[y] + candW[y] + prm.size - 1, pool, 0);
        for (int i = 0; i < n; ++i)
            if (bd.slot[pool[i]] >= 0) { logTake(bd, pool[i]); ++removed; }
    } else {
        for (int t = 0; t < prm.size && t < POOL_MAX && bd.count > 0; ++t) {
            int y = bd.picked[rng.below((unsigned)bd.count)];
            if (prm.mode == LOWEST_K) {  // 세 개를 뽑아 점수가 가장 낮은 것
                for (int s = 0; s < 2; ++s) {
                    int z = bd.picked[rng.below((unsigned)bd.count)];
                    if (candWeight[z] < candWeight[y]) y = z;
                }
            }
            logTake(bd, y);
            ++removed;
            n = collect(candRow[y], candCol[y], candRow[y] + candH[y] - 1, candCol[y] + candW[y] - 1, pool, n);
        }
    }
    for (int i = 0; i < n; ++i) {
        int c = pool[i];
        long long noise = prm.noise == 0 ? 0 : (long long)rng.below((unsigned)prm.noise + 1u);
        key[c] = -(long long)candWeight[c] * (100 + noise);
    }
    hc::sortIds(pool, temp, n, key);
    for (int i = 0; i < n; ++i) {
        int c = pool[i];
        ++evaluations;
        if (canAdd(bd, c)) logPut(bd, c);
    }
    if (bd.score < before) undo(bd);
    opCount = 0;
    return removed;
}

void destroyRepairRun(Board& bd, hc::Random& rng, const DestroyParams& prm, long long budget) {
    long long stop = evaluations + budget;
    while (evaluations < stop) destroyRepair(bd, rng, prm);
}
}
```

```cpp snippet=land-entry
static land::Board layout;
static int sortOrder[land::MAX_CAND], sortTemp[land::MAX_CAND];
static long long sortKey[land::MAX_CAND];

void init(int map[MAP_SIZE][MAP_SIZE], Spaceship spaceships[]) {
    land::clear(layout);
    land::build(map, spaceships, SPACESHIP_SIZE, layout);
    land::buildBuckets();
}

void process(int row[], int col[], int dir[]) {
    land::evaluations = 0;
    for (int c = 0; c < land::candCount; ++c) sortKey[c] = -(long long)land::candWeight[c];
    land::sweep(layout, sortKey, sortOrder, sortTemp);  // 점수가 큰 후보부터 훑는 탐욕

    hc::Random rng;
    rng.reset(20261118u);
    land::DestroyParams prm = {land::REGION, 8, 200};
    land::destroyRepairRun(layout, rng, prm, 1000000);
    land::submit(layout, row, col, dir);
}
```


        else {  // 격자 칠하기를 빠뜨린 되돌리기
            ++bd.have[candKind[op.cand]];
            bd.slot[op.cand] = bd.count;
            bd.picked[bd.count++] = op.cand;
            bd.score += candWeight[op.cand];
        }
    if (bd.have[candKind[c]] >= kindLimit[candKind[c]]) return false;
