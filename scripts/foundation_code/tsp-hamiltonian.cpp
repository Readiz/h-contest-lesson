// tsp-hamiltonian 하네스: 제출 코드 바깥의 로컬 검사. 이 강의에는 표준 입력 연습이 없다.
static int sample() { return 0; }

static long long gDist[MAX_POINTS][MAX_POINTS];

static void clearTables(int n) {
    // 이전 호출이 남긴 값을 흉내 내려고 사용할 구간을 쓰레기 값으로 채운다.
    for (int mask = 0; mask < (1 << n); ++mask)
        for (int last = 0; last < n; ++last) { tspDp[mask][last] = -123; parent[mask][last] = 7777; reachable[mask][last] = 1; }
}

static void fillCost(int n, int infPercent, int maxCost) {
    for (int u = 0; u < n; ++u)
        for (int v = 0; v < n; ++v) cost[u][v] = rnd(100) < infPercent ? INF : 1 + rnd(maxCost);
}

// ---- 독립 기준 1: std::next_permutation ----
static long long oracleBrute(int n) {
    std::vector<int> order;
    for (int v = 1; v < n; ++v) order.push_back(v);
    long long best = INF;
    do {
        long long total = 0;
        int current = 0;
        bool ok = true;
        for (int next : order) {
            if (cost[current][next] == INF) { ok = false; break; }
            total += cost[current][next];
            current = next;
        }
        if (ok && cost[current][0] != INF) best = std::min(best, total + cost[current][0]);
    } while (std::next_permutation(order.begin(), order.end()));
    return best;
}

// ---- 독립 기준 2: 끝점을 기준으로 거꾸로 당겨 오는 Held-Karp(표는 std::vector) ----
static long long oracleHeldKarp(int n) {
    std::vector<std::vector<long long>> best(1 << n, std::vector<long long>(n, INF));
    best[1][0] = 0;
    for (int mask = 1; mask < (1 << n); mask += 2) { // 0번 정점을 포함한 집합만
        for (int j = 1; j < n; ++j) {
            if (!(mask >> j & 1)) continue;
            int before = mask ^ (1 << j);
            for (int i = 0; i < n; ++i) {
                if (!(before >> i & 1) || best[before][i] == INF || cost[i][j] == INF) continue;
                best[mask][j] = std::min(best[mask][j], best[before][i] + cost[i][j]);
            }
        }
    }
    long long answer = INF;
    for (int j = 1; j < n; ++j)
        if (best[(1 << n) - 1][j] != INF && cost[j][0] != INF)
            answer = std::min(answer, best[(1 << n) - 1][j] + cost[j][0]);
    return answer;
}

// ---- 독립 기준 3: 모든 순열로 해밀턴 경로 존재 확인 ----
static bool oracleHamiltonian(int n) {
    std::vector<int> order(n);
    for (int i = 0; i < n; ++i) order[i] = i;
    do {
        bool ok = true;
        for (int i = 0; i + 1 < n && ok; ++i) ok = connected[order[i]][order[i + 1]];
        if (ok) return true;
    } while (std::next_permutation(order.begin(), order.end()));
    return false;
}

static long long cycleCost(const int* route, int n) { // route[0..n]
    long long total = 0;
    for (int k = 0; k < n; ++k) total += cost[route[k]][route[k + 1]];
    return total;
}

static void checkRoute(int n, long long want) {
    int route[MAX_N + 1];
    for (int k = 0; k <= n; ++k) route[k] = -99;
    clearTables(n);
    long long got = heldKarpRoute(n, route);
    CHECK(got == want);
    if (want == INF) return;
    CHECK(route[0] == 0 && route[n] == 0);
    bool seen[MAX_N] = {};
    for (int k = 0; k < n; ++k) { CHECK(!seen[route[k]]); seen[route[k]] = true; }
    CHECK(cycleCost(route, n) == want);
}

static void tspCase(int n, int infPercent, int maxCost) {
    fillCost(n, infPercent, maxCost);
    clearTables(n);
    long long got = heldKarp(n);
    if (n <= 9) { CHECK(got == oracleBrute(n)); CHECK(tspBruteForce(n) == got); }
    if (n <= 13) CHECK(got == oracleHeldKarp(n));
    checkRoute(n, got);
}

static void pathCase(int n, int connectedPercent) {
    for (int u = 0; u < n; ++u)
        for (int v = 0; v < n; ++v) connected[u][v] = u != v && rnd(100) < connectedPercent;
    for (int mask = 0; mask < (1 << n); ++mask)
        for (int last = 0; last < n; ++last) reachable[mask][last] = 1;
    CHECK(hasHamiltonianPath(n) == oracleHamiltonian(n));
}

// ---- 2-opt ----
static long long tourLength(const int* route, int m) {
    long long total = 0;
    for (int k = 0; k + 1 < m; ++k) total += gDist[route[k]][route[k + 1]];
    return total;
}

static void twoOptCase(int n) { // n개 점, route 길이 n + 1
    std::vector<int> xs(n), ys(n);
    for (int i = 0; i < n; ++i) { xs[i] = rnd(100); ys[i] = rnd(100); }
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j) gDist[i][j] = std::abs(xs[i] - xs[j]) + std::abs(ys[i] - ys[j]);
    std::vector<int> route(n + 1);
    for (int i = 0; i < n; ++i) route[i] = i;
    std::shuffle(route.begin() + 1, route.begin() + n, harnessRng);
    route[n] = 0;
    long long before = tourLength(route.data(), n + 1);
    twoOpt(route.data(), n + 1, gDist);
    CHECK(route[0] == 0 && route[n] == 0);
    std::vector<int> sorted(route.begin(), route.begin() + n);
    std::sort(sorted.begin(), sorted.end());
    for (int i = 0; i < n; ++i) CHECK(sorted[i] == i);
    long long after = tourLength(route.data(), n + 1);
    CHECK(after <= before);
    // 독립 확인: 가운데 구간을 뒤집은 모든 경로의 전체 길이를 다시 계산해도 더 짧은 것이 없다.
    for (int i = 1; i < n; ++i)
        for (int j = i + 1; j < n; ++j) {
            std::vector<int> other = route;
            std::reverse(other.begin() + i, other.begin() + j + 1);
            CHECK(tourLength(other.data(), n + 1) >= after);
        }
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();

    // 본문 그림의 경로 비용(8+4+7+6+5=30)과 같은 형태: 5개 정점 순회.
    {
        int w[5][5] = {{0, 8, 9, 9, 5}, {8, 0, 4, 9, 9}, {9, 4, 0, 7, 9}, {9, 9, 7, 0, 6}, {5, 9, 9, 6, 0}};
        for (int u = 0; u < 5; ++u) for (int v = 0; v < 5; ++v) cost[u][v] = w[u][v];
        CHECK(tspBruteForce(5) == 30 && heldKarp(5) == 30);
    }
    // 계약 위반 입력.
    CHECK(tspBruteForce(1) == INF && heldKarp(1) == INF && heldKarp(MAX_N + 1) == INF && tspBruteForce(MAX_N + 1) == INF);
    CHECK(!hasHamiltonianPath(0) && !hasHamiltonianPath(MAX_N + 1));
    {
        int route[3];
        CHECK(heldKarpRoute(1, route) == INF);
    }

    // 무작위 비교: 크기를 바꿔 가며 한 프로세스에서 이어서 실행한다(표에 이전 값이 남아 있다).
    for (int trial = 0; trial < 300; ++trial) tspCase(2 + rnd(7), rnd(4) * 25, 1 + rnd(30));
    for (int n : {13, 3, 12, 2, 9, 6}) tspCase(n, 20, 1000000000);
    for (int trial = 0; trial < 300; ++trial) pathCase(1 + rnd(7), 20 + rnd(5) * 15);
    for (int n : {9, 1, 8, 2, 10}) pathCase(n, 15);
    // 자기 자신으로만 가는 간선은 해밀턴 경로에 쓸 수 없고, 정점 하나는 자명한 경로다.
    connected[0][0] = true;
    CHECK(hasHamiltonianPath(1));
    // 갈 수 없는 입력: 모든 비용이 INF이면 INF, 복귀 간선이 없어도 INF.
    for (int u = 0; u < 4; ++u) for (int v = 0; v < 4; ++v) cost[u][v] = INF;
    CHECK(heldKarp(4) == INF && tspBruteForce(4) == INF);
    cost[0][1] = cost[1][2] = cost[2][3] = 1;
    CHECK(heldKarp(4) == INF && tspBruteForce(4) == INF);
    checkRoute(4, INF);
    cost[3][0] = 1;
    CHECK(heldKarp(4) == 4 && tspBruteForce(4) == 4);
    checkRoute(4, 4);

    // 용량 경계 n = MAX_N = 20: 한 방향 사이클만 열려 있으면 답은 20이고 경로는 0, 1, ..., 19, 0이다.
    for (int u = 0; u < MAX_N; ++u) for (int v = 0; v < MAX_N; ++v) cost[u][v] = v == (u + 1) % MAX_N ? 1 : INF;
    CHECK(heldKarp(MAX_N) == MAX_N);
    {
        int route[MAX_N + 1];
        CHECK(heldKarpRoute(MAX_N, route) == MAX_N);
        for (int k = 0; k <= MAX_N; ++k) CHECK(route[k] == k % MAX_N);
    }
    // 같은 경계에서 해밀턴 경로: 사슬은 있고, 가운데를 끊으면 없다.
    for (int u = 0; u < MAX_N; ++u) for (int v = 0; v < MAX_N; ++v) connected[u][v] = v == u + 1;
    CHECK(hasHamiltonianPath(MAX_N));
    connected[9][10] = false;
    CHECK(!hasHamiltonianPath(MAX_N));
    // 밀집 입력 n = 20: 두 DP가 같은 비용을 내고, 복원한 경로의 비용이 그 값과 같다.
    fillCost(MAX_N, 0, 100);
    long long dense = heldKarp(MAX_N);
    CHECK(dense < INF);
    {
        int route[MAX_N + 1];
        CHECK(heldKarpRoute(MAX_N, route) == dense);
        CHECK(cycleCost(route, MAX_N) == dense);
        bool seen[MAX_N] = {};
        for (int k = 0; k < MAX_N; ++k) { CHECK(!seen[route[k]]); seen[route[k]] = true; }
    }
    // 큰 비용: 합이 정수 범위를 넘어도 long long으로 계산된다.
    for (int u = 0; u < 10; ++u) for (int v = 0; v < 10; ++v) cost[u][v] = 1000000000000LL;
    CHECK(heldKarp(10) == 10LL * 1000000000000LL);

    // 2-opt: 크기가 다른 입력을 이어서 실행한다. 작은 m에서는 루프가 돌지 않는다.
    for (int trial = 0; trial < 200; ++trial) twoOptCase(2 + rnd(30));
    for (int n : {60, 3, 2, 40}) twoOptCase(n);
    // 용량 경계 n = MAX_POINTS: 직선 위의 점을 순서대로 지나는 경로는 이미 최적이고, 안쪽 두 점을 바꾸면 고쳐진다.
    for (int i = 0; i < MAX_POINTS; ++i)
        for (int j = 0; j < MAX_POINTS; ++j) gDist[i][j] = std::abs(i - j);
    std::vector<int> line(MAX_POINTS + 1);
    for (int i = 0; i < MAX_POINTS; ++i) line[i] = i;
    line[MAX_POINTS] = 0;
    CHECK(!improve2Opt(line.data(), MAX_POINTS + 1, gDist));
    twoOpt(line.data(), MAX_POINTS + 1, gDist);
    CHECK(tourLength(line.data(), MAX_POINTS + 1) == 2 * (MAX_POINTS - 1));
    std::swap(line[300], line[700]);
    long long broken = tourLength(line.data(), MAX_POINTS + 1);
    CHECK(broken > 2 * (MAX_POINTS - 1));
    twoOpt(line.data(), MAX_POINTS + 1, gDist);
    CHECK(tourLength(line.data(), MAX_POINTS + 1) == 2 * (MAX_POINTS - 1));
    CHECK(line[0] == 0 && line[MAX_POINTS] == 0);
    // 본문 그림: a(0,0), b(4,2), c(0,2), d(4,0)에서 교차하는 a-b, c-d(합 약 9)가 a-c, b-d(합 4)로 바뀐다.
    {
        const int px[4] = {0, 4, 0, 4}, py[4] = {0, 2, 2, 0};
        for (int i = 0; i < 4; ++i)
            for (int j = 0; j < 4; ++j) gDist[i][j] = std::abs(px[i] - px[j]) + std::abs(py[i] - py[j]);
        int route[5] = {0, 1, 2, 3, 0};
        long long before = tourLength(route, 5);
        twoOpt(route, 5, gDist);
        CHECK(tourLength(route, 5) < before);
    }

    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
