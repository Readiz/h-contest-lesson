// dynamic-programming 하네스: 제출 코드 바깥의 로컬 검사.
static Item gItems[100];
static int gA[MAX_SEQ];
static int gCoins[8];

// 로컬 연습: 각 물건을 한 번만 고르는 배낭.
static int sample() {
    int n, w;
    std::cin >> n >> w;
    for (int i = 0; i < n; ++i) std::cin >> gItems[i].weight >> gItems[i].value;
    std::printf("%lld\n", knapsack(gItems, n, w));
    return 0;
}

// ---- 격자 경로: 독립 기준은 깊이 우선 전수 열거(작은 격자)와 열 단위 DP ----
static long long enumerate(int h, int w, int r, int c) {
    if (r >= h || c >= w || blocked[r][c]) return 0;
    if (r == h - 1 && c == w - 1) return 1;
    return enumerate(h, w, r + 1, c) + enumerate(h, w, r, c + 1);
}

static long long columnDp(int h, int w) {
    std::vector<long long> column(h, 0);
    for (int c = 0; c < w; ++c) {
        for (int r = 0; r < h; ++r) {
            long long value = 0;
            if (!blocked[r][c]) {
                if (r == 0 && c == 0) value = 1;
                else value = (r > 0 ? column[r - 1] : 0) + (c > 0 ? column[r] : 0);
            }
            column[r] = value; // 갱신 전의 column[r]은 왼쪽 칸의 값이었다
        }
    }
    return column[h - 1];
}

static void gridCase(int h, int w, int blockedPercent) {
    for (int r = 0; r < 40; ++r) // 사용할 구간(최대 30 x 30)과 그 둘레를 채운다
        for (int c = 0; c < 40; ++c) { blocked[r][c] = rnd(100) < blockedPercent; gridDp[r][c] = -777; }
    long long got = countPaths(h, w);
    if (h * w <= 64) CHECK(got == enumerate(h, w, 0, 0));
    CHECK(got == columnDp(h, w));
}

// ---- 최소 동전: 독립 기준은 금액을 정점으로 보는 BFS ----
static int bfsCoins(const int* coins, int count, int target) {
    std::vector<int> dist(target + 1, -1);
    std::vector<int> queue = {0};
    dist[0] = 0;
    for (size_t head = 0; head < queue.size(); ++head) {
        int x = queue[head];
        for (int i = 0; i < count; ++i) {
            int y = x + coins[i];
            if (y <= target && dist[y] < 0) { dist[y] = dist[x] + 1; queue.push_back(y); }
        }
    }
    return dist[target] < 0 ? COIN_INF : dist[target];
}

static void coinCase(int count, int maxCoin, int target) {
    for (int i = 0; i <= 100; ++i) coinDp[i] = -5; // 이전 호출이 남긴 값
    for (int i = 0; i < count; ++i) gCoins[i] = 1 + rnd(maxCoin);
    CHECK(minCoins(gCoins, count, target) == bfsCoins(gCoins, count, target));
}

// ---- 배낭: 독립 기준은 부분집합 전수 조사와 2차원 표 ----
static long long bruteKnapsack(int n, int capacity) {
    long long best = 0;
    for (int mask = 0; mask < (1 << n); ++mask) {
        long long weightSum = 0, value = 0;
        for (int i = 0; i < n; ++i) if (mask >> i & 1) { weightSum += gItems[i].weight; value += gItems[i].value; }
        if (weightSum <= capacity) best = std::max(best, value);
    }
    return best;
}

static long long tableKnapsack(int n, int capacity) {
    std::vector<std::vector<long long>> table(n + 1, std::vector<long long>(capacity + 1, 0));
    for (int i = 1; i <= n; ++i)
        for (int w = 0; w <= capacity; ++w) {
            table[i][w] = table[i - 1][w];
            if (w >= gItems[i - 1].weight)
                table[i][w] = std::max(table[i][w], table[i - 1][w - gItems[i - 1].weight] + gItems[i - 1].value);
        }
    return table[n][capacity];
}

static void knapsackCase(int n, int capacity, int maxWeight, long long maxValue) {
    for (int i = 0; i < n; ++i) {
        gItems[i].weight = 1 + rnd(maxWeight);
        gItems[i].value = (long long)(harnessRng() % (unsigned long long)(maxValue + 1));
    }
    for (int w = 0; w <= MAX_CAPACITY; ++w) knapsackDp[w] = -9; // 이전 TC가 남긴 값
    long long got = knapsack(gItems, n, capacity);
    CHECK(got == tableKnapsack(n, capacity));
    if (n <= 14) CHECK(got == bruteKnapsack(n, capacity));
}

// ---- LIS: 독립 기준은 부분집합 전수 조사와 std::lower_bound ----
static int bruteLis(const int* a, int n) {
    int best = 0;
    for (int mask = 0; mask < (1 << n); ++mask) {
        int last = 0, length = 0;
        bool increasing = true;
        for (int i = 0; i < n && increasing; ++i) if (mask >> i & 1) {
            if (length > 0 && a[i] <= last) increasing = false;
            last = a[i];
            ++length;
        }
        if (increasing) best = std::max(best, length);
    }
    return best;
}

static int patienceLis(const int* a, int n) {
    std::vector<int> t;
    for (int i = 0; i < n; ++i) {
        auto it = std::lower_bound(t.begin(), t.end(), a[i]);
        if (it == t.end()) t.push_back(a[i]); else *it = a[i];
    }
    return (int)t.size();
}

static void lisCase(int n, int range) {
    for (int i = 0; i < n; ++i) gA[i] = rnd(range) - range / 2;
    for (int i = 0; i < 3000; ++i) { lisDp[i] = -3; tails[i] = -3; }
    int fast = lisFast(gA, n);
    CHECK(fast == patienceLis(gA, n));
    if (n <= 3000) CHECK(lisQuadratic(gA, n) == fast);
    if (n <= 14) CHECK(fast == bruteLis(gA, n));
    std::vector<int> sorted(gA, gA + n);
    std::sort(sorted.begin(), sorted.end());
    for (int step = 0; step < 40; ++step) {
        int target = rnd(range + 4) - range / 2 - 2;
        CHECK(lowerBound(sorted.data(), n, target) ==
              (int)(std::lower_bound(sorted.begin(), sorted.end(), target) - sorted.begin()));
    }
}

// ---- 트리 DP: 독립 기준은 부분집합 전수 조사와 반복 DP ----
static int gParent[MAX_TREE_V];

static long long bruteTree(int n) {
    long long best = 0;
    for (int mask = 0; mask < (1 << n); ++mask) {
        bool ok = true;
        long long total = 0;
        for (int v = 0; v < n && ok; ++v) if (mask >> v & 1) {
            total += weight[v];
            if (v > 0 && (mask >> gParent[v] & 1)) ok = false;
        }
        if (ok) best = std::max(best, total);
    }
    return best;
}

// parent[v] < v인 트리를 뒤에서부터 접어 올린다.
static long long iterativeTree(int n) {
    std::vector<long long> skip(n, 0), take(n);
    for (int v = 0; v < n; ++v) take[v] = weight[v];
    for (int v = n - 1; v > 0; --v) {
        skip[gParent[v]] += std::max(skip[v], take[v]);
        take[gParent[v]] += skip[v];
    }
    return std::max(skip[0], take[0]);
}

// shape: 0 무작위, 1 일자(깊은 재귀), 2 별 모양
static void treeCase(int n, int shape, long long maxWeight) {
    tree.init(n);
    for (int v = 1; v < n; ++v) {
        gParent[v] = shape == 1 ? v - 1 : shape == 2 ? 0 : rnd(v);
        CHECK(tree.addEdge(gParent[v], v));
    }
    for (int v = 0; v < n; ++v) weight[v] = (long long)(harnessRng() % (unsigned long long)(maxWeight + 1));
    for (int v = 0; v < MAX_TREE_V; ++v) treeDp[v][0] = treeDp[v][1] = -11;
    dfs(0, -1);
    long long got = std::max(treeDp[0][0], treeDp[0][1]);
    CHECK(got == iterativeTree(n));
    if (n <= 16) CHECK(got == bruteTree(n));
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();

    // 격자: 크기가 다른 케이스를 이어서 실행(이전 gridDp 값이 남아 있다).
    for (int trial = 0; trial < 400; ++trial) gridCase(1 + rnd(8), 1 + rnd(8), rnd(5) * 10);
    for (int trial = 0; trial < 30; ++trial) gridCase(1 + rnd(30), 1 + rnd(30), rnd(4) * 8);
    // 용량 경계: 1000 x 1000에서 첫 행과 마지막 열만 열려 있으면 경로는 정확히 하나다.
    for (int r = 0; r < MAX_H; ++r)
        for (int c = 0; c < MAX_W; ++c) blocked[r][c] = r != 0 && c != MAX_W - 1;
    CHECK(countPaths(MAX_H, MAX_W) == 1);
    CHECK(countPaths(1, MAX_W) == 1);
    CHECK(countPaths(1, 1) == 1);
    blocked[0][0] = true;
    CHECK(countPaths(MAX_H, MAX_W) == 0);
    blocked[0][0] = false;
    blocked[MAX_H - 1][MAX_W - 1] = true;
    CHECK(countPaths(MAX_H, MAX_W) == 0);
    for (int r = 0; r < MAX_H; ++r) for (int c = 0; c < MAX_W; ++c) blocked[r][c] = false;
    CHECK(countPaths(3, 3) == 6 && countPaths(2, 5) == 5 && countPaths(1, 7) == 1); // 장애물 없음: C(h+w-2, h-1)

    // 동전: 본문 예 {1, 3, 4}, 6원은 2개이고 그리디는 3개.
    {
        int coins[3] = {1, 3, 4};
        CHECK(minCoins(coins, 3, 6) == 2 && minCoins(coins, 3, 0) == 0 && minCoins(coins, 3, 1) == 1);
        int two[2] = {5, 7};
        CHECK(minCoins(two, 2, 3) == COIN_INF && minCoins(two, 2, 12) == 2 && minCoins(two, 2, 0) == 0);
        CHECK(minCoins(coins, 0, 0) == 0 && minCoins(coins, 0, 5) == COIN_INF);
    }
    for (int trial = 0; trial < 300; ++trial) coinCase(1 + rnd(4), 1 + rnd(9), rnd(60));
    coinCase(3, 50, 100000);
    coinCase(2, 3, 5);
    coinCase(4, 20, MAX_TARGET);
    gCoins[0] = 1; gCoins[1] = 3; gCoins[2] = 4;
    CHECK(minCoins(gCoins, 3, MAX_TARGET) == bfsCoins(gCoins, 3, MAX_TARGET));
    gCoins[0] = 2;
    CHECK(minCoins(gCoins, 1, MAX_TARGET) == MAX_TARGET / 2 && minCoins(gCoins, 1, MAX_TARGET - 1) == COIN_INF);

    // 배낭: 작은 입력은 전수 조사, 큰 입력은 표와 비교한다. 같은 프로세스에서 크기를 바꿔 이어서 실행한다.
    for (int trial = 0; trial < 400; ++trial) knapsackCase(rnd(10), rnd(25), 1 + rnd(9), 20);
    for (int n : {100, 3, 0, 14, 60}) knapsackCase(n, 1 + rnd(200), 1 + rnd(40), 1000000000LL);
    CHECK(knapsack(gItems, 0, 0) == 0 && knapsack(gItems, 0, MAX_CAPACITY) == 0);
    CHECK(knapsack(gItems, 5, -1) == -1 && knapsack(gItems, 5, MAX_CAPACITY + 1) == -1);
    // 용량 경계: W = 10000, 100개 모두 가치 10^9이면 합은 int를 넘는 10^11이다.
    for (int i = 0; i < 100; ++i) { gItems[i].weight = 100; gItems[i].value = 1000000000LL; }
    CHECK(knapsack(gItems, 100, MAX_CAPACITY) == 100000000000LL);
    CHECK(knapsack(gItems, 100, 99) == 0 && knapsack(gItems, 100, 100) == 1000000000LL);
    for (int i = 0; i < 100; ++i) { gItems[i].weight = 1 + rnd(10000); gItems[i].value = 1 + rnd(1000); }
    CHECK(knapsack(gItems, 100, MAX_CAPACITY) == tableKnapsack(100, MAX_CAPACITY));
    // 본문 반례: 무게 2, 가치 3 하나와 용량 4는 3이다(정방향 갱신이면 6).
    gItems[0].weight = 2; gItems[0].value = 3;
    CHECK(knapsack(gItems, 1, 4) == 3);
    // 연습 예시: 무게 2와 5를 고르면 10.
    gItems[0] = {3, 4}; gItems[1] = {4, 5}; gItems[2] = {2, 3}; gItems[3] = {5, 7};
    CHECK(knapsack(gItems, 4, 7) == 10);

    // LIS: 값 범위가 좁으면 같은 값이 많고, 넓으면 거의 서로 다르다.
    for (int trial = 0; trial < 500; ++trial) lisCase(rnd(13), 1 + rnd(12));
    for (int n : {2000, 0, 7, 3000, 50, 1}) lisCase(n, 1 + rnd(5000));
    lisCase(50000, 1000000000);
    lisCase(MAX_SEQ, 100);
    // 용량 경계: n = MAX_SEQ에서 정렬·역순·모두 같은 값.
    for (int i = 0; i < MAX_SEQ; ++i) gA[i] = i - 100000;
    CHECK(lisFast(gA, MAX_SEQ) == MAX_SEQ);
    for (int i = 0; i < MAX_SEQ; ++i) gA[i] = 100000 - i;
    CHECK(lisFast(gA, MAX_SEQ) == 1);
    for (int i = 0; i < MAX_SEQ; ++i) gA[i] = 7;
    CHECK(lisFast(gA, MAX_SEQ) == 1 && lisFast(gA, 0) == 0);
    gA[0] = 2147483647; gA[1] = -2147483647 - 1;
    CHECK(lisFast(gA, 2) == 1 && lisQuadratic(gA, 2) == 1);

    // 트리 DP: 무작위 트리 → 일자·별 모양 → 다시 작은 트리.
    for (int trial = 0; trial < 500; ++trial) treeCase(1 + rnd(14), 0, 1 + rnd(20));
    for (int n : {1000, 1, 2, 300}) treeCase(n, 0, 1000000000LL);
    for (int n : {16, 15}) { treeCase(n, 1, 9); treeCase(n, 2, 9); }
    treeCase(MAX_TREE_V, 0, 1000000000LL);
    treeCase(MAX_TREE_V, 2, 1000000000LL);
    treeCase(5, 0, 5);
    // 용량 경계: 일자 트리 MAX_TREE_V개(재귀 깊이 MAX_TREE_V), 가중치 10^9. 간선 배열도 가득 찬다.
    treeCase(MAX_TREE_V, 1, 0);
    tree.init(MAX_TREE_V);
    for (int v = 1; v < MAX_TREE_V; ++v) CHECK(tree.addEdge(v - 1, v));
    CHECK(tree.edgeCount == MAX_TREE_E && !tree.addEdge(0, 1));
    for (int v = 0; v < MAX_TREE_V; ++v) weight[v] = 1000000000LL;
    dfs(0, -1);
    CHECK(std::max(treeDp[0][0], treeDp[0][1]) == (long long)((MAX_TREE_V + 1) / 2) * 1000000000LL);
    // 본문 규칙: 정점 하나(가중치 5), 간선 하나(가중치 3, 4).
    tree.init(1); weight[0] = 5; dfs(0, -1);
    CHECK(treeDp[0][0] == 0 && treeDp[0][1] == 5);
    tree.init(2); CHECK(tree.addEdge(0, 1)); weight[0] = 3; weight[1] = 4; dfs(0, -1);
    CHECK(treeDp[0][0] == 4 && treeDp[0][1] == 3);

    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
