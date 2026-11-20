// floyd-warshall 하네스: 제출 코드 바깥의 로컬 검사.
#include <queue>
#include <utility>

static long long gDist[MAX_N][MAX_N];
static int gNext[MAX_N][MAX_N];
static bool gAffected[MAX_N][MAX_N];
static int gPath[MAX_N];

static int sample() {
    int n, m, q;
    std::cin >> n >> m >> q;
    CHECK(initDist(n, gDist));
    for (int i = 0; i < m; ++i) {
        int u, v;
        long long w;
        std::cin >> u >> v >> w;
        CHECK(addEdge(n, gDist, u, v, w));
    }
    floydWarshall(n, gDist);
    for (int i = 0; i < q; ++i) {
        int s, t;
        std::cin >> s >> t;
        if (gDist[s][t] == INF) std::printf("UNREACHABLE\n");
        else std::printf("%lld\n", gDist[s][t]);
    }
    return 0;
}

typedef std::vector<std::vector<long long>> Matrix;

static void dirty() { // 이전 TC가 남긴 값을 흉내 내려고 전체를 쓰레기 값으로 채운다.
    for (int i = 0; i < MAX_N; ++i) for (int j = 0; j < MAX_N; ++j) {
        gDist[i][j] = 777; gNext[i][j] = 888; gAffected[i][j] = (i + j) % 2 == 0;
    }
}

// 입력 행렬(대각 0, 간선 없으면 INF)을 전역 배열에 직접 적는다.
static void load(const Matrix& input) {
    int n = (int)input.size();
    dirty();
    for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) gDist[i][j] = input[i][j];
}

// 독립 기준: 간선 수 단계 DP. 한 회차는 이전 회차 값만 읽는다.
static std::vector<long long> edgeDp(const Matrix& input, int s) {
    int n = (int)input.size();
    std::vector<long long> best(n, INF);
    best[s] = 0;
    for (int step = 0; step < n - 1; ++step) {
        auto after = best;
        for (int u = 0; u < n; ++u) for (int v = 0; v < n; ++v)
            if (best[u] != INF && input[u][v] != INF) after[v] = std::min(after[v], best[u] + input[u][v]);
        best = after;
    }
    return best;
}

static void verify(const Matrix& input) {
    int n = (int)input.size();
    load(input);
    floydWarshall(n, gDist);
    negativeCyclePairs(n, gDist, gAffected);
    // 사용 구간 밖은 건드리지 않는다.
    for (int i = 0; i < MAX_N; ++i) for (int j = 0; j < MAX_N; ++j)
        if (i >= n || j >= n) CHECK(gDist[i][j] == 777 && gAffected[i][j] == ((i + j) % 2 == 0));
    // 경로 복원용 계산: 같은 k, i, j 순서의 relaxPath가 floydWarshall과 같은 행렬을 만든다.
    static long long solved[MAX_N][MAX_N], restored[MAX_N][MAX_N];
    for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) solved[i][j] = gDist[i][j];
    load(input);
    initNext(n, gDist, gNext);
    for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) restored[i][j] = gDist[i][j];
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j)
        relaxPath(i, j, k, restored, gNext);
    for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) CHECK(restored[i][j] == solved[i][j]);
    negativeCyclePairs(n, solved, gAffected); // load()가 지운 영향 행렬을 다시 계산한다.
    for (int s = 0; s < n; ++s) {
        auto best = edgeDp(input, s);
        // 단계 DP로 n회 더 완화할 수 있는 정점과 거기서 도달 가능한 정점이 영향을 받는다.
        std::vector<bool> bad(n, false);
        for (int u = 0; u < n; ++u) for (int v = 0; v < n; ++v)
            if (best[u] != INF && input[u][v] != INF && best[u] + input[u][v] < best[v]) bad[v] = true;
        for (int pass = 0; pass < n; ++pass)
            for (int u = 0; u < n; ++u) for (int v = 0; v < n; ++v)
                if (bad[u] && input[u][v] != INF) bad[v] = true;
        for (int t = 0; t < n; ++t) {
            CHECK(solved[s][t] >= -INF && solved[s][t] <= INF);
            CHECK(gAffected[s][t] == bad[t]);
            if (bad[t]) { CHECK(restorePath(s, t, gNext, gPath) >= 0); continue; }
            CHECK(solved[s][t] == best[t]);
            int length = restorePath(s, t, gNext, gPath);
            if (best[t] == INF) { CHECK(length == 0); continue; }
            CHECK(length >= 1 && length <= n && gPath[0] == s && gPath[length - 1] == t);
            long long cost = 0;
            for (int i = 1; i < length; ++i) {
                CHECK(input[gPath[i - 1]][gPath[i]] != INF);
                cost += input[gPath[i - 1]][gPath[i]];
            }
            CHECK(cost == best[t]);
        }
    }
}

static Matrix emptyMatrix(int n) {
    Matrix d(n, std::vector<long long>(n, INF));
    for (int i = 0; i < n; ++i) d[i][i] = 0;
    return d;
}

// initDist/addEdge로 만든 행렬이 직접 만든 행렬과 같고 floydWarshall 결과가 같다.
static void builderCase(int n, int edgeCount, long long maxWeight) {
    Matrix d = emptyMatrix(n);
    dirty();
    CHECK(initDist(n, gDist));
    for (int e = 0; e < edgeCount && n > 0; ++e) {
        int u = rnd(n), v = rnd(n);
        long long w = (long long)(harnessRng() % (unsigned long long)(maxWeight + 1));
        CHECK(addEdge(n, gDist, u, v, w));
        d[u][v] = std::min(d[u][v], w);
    }
    for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) CHECK(gDist[i][j] == d[i][j]);
    floydWarshall(n, gDist);
    // 독립 기준: 시작점마다 Dijkstra.
    for (int s = 0; s < n; ++s) {
        std::vector<long long> best(n, INF);
        std::priority_queue<std::pair<long long, int>, std::vector<std::pair<long long, int>>,
                            std::greater<std::pair<long long, int>>> heap;
        best[s] = 0;
        heap.push({0, s});
        while (!heap.empty()) {
            auto top = heap.top(); heap.pop();
            if (top.first != best[top.second]) continue;
            for (int v = 0; v < n; ++v)
                if (d[top.second][v] != INF && top.first + d[top.second][v] < best[v]) {
                    best[v] = top.first + d[top.second][v];
                    heap.push({best[v], v});
                }
        }
        for (int t = 0; t < n; ++t) CHECK(gDist[s][t] == best[t]);
    }
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 작은 그래프 무작위: 음수 비용과 음수 사이클 포함. 크기를 바꿔 가며 한 프로세스에서 이어 실행한다.
    for (int trial = 0; trial < 500; ++trial) {
        int n = 1 + rnd(7);
        Matrix d = emptyMatrix(n);
        for (int e = 0; e < n * n; ++e) {
            int u = rnd(n), v = rnd(n);
            if (rnd(3)) d[u][v] = std::min(d[u][v], (long long)(rnd(21) - 10));
        }
        verify(d);
    }
    // 빈 입력, 자기 음수 간선, 본문 예시.
    verify({});
    verify({{0}});
    verify({{-1}});
    {
        Matrix example = emptyMatrix(5);
        example[0][1] = 3; example[1][2] = -2; example[2][1] = 1; example[2][3] = 4; example[0][4] = 9;
        verify(example);
        floydWarshall(5, gDist);
        load(example);
        floydWarshall(5, gDist);
        negativeCyclePairs(5, gDist, gAffected);
        CHECK(gAffected[0][3] && !gAffected[0][4] && gDist[0][4] == 9 && gDist[4][0] == INF);
    }
    // 서로 다른 모든 정점 사이 비용 -1인 30정점: 하한 -INF로 막지 않으면 long long을 넘친다.
    {
        Matrix dense(30, std::vector<long long>(30, -1));
        for (int i = 0; i < 30; ++i) dense[i][i] = 0;
        verify(dense);
        load(dense);
        floydWarshall(30, gDist);
        CHECK(gDist[29][29] == -INF);
    }
    // 큰 비용 w = INF / 4 가 경유해 INF 범위 안에 머무는 경우.
    {
        long long w = INF / 4;
        verify({{0, w, INF}, {INF, 0, w}, {INF, INF, 0}});
        verify({{0, -w, INF}, {INF, 0, -w}, {INF, INF, 0}});
    }
    // 음수 간선과 INF: 도달 불가 정점에서 나오는 음수 간선이 INF를 깨지 않는다.
    {
        Matrix d = emptyMatrix(3);
        d[2][1] = -5; // 0에서는 2에 갈 수 없다
        d[0][1] = 4;
        verify(d);
        load(d);
        floydWarshall(3, gDist);
        CHECK(gDist[0][2] == INF && gDist[0][1] == 4 && gDist[2][1] == -5 && gDist[1][2] == INF);
    }
    // 계약 위반 입력.
    CHECK(!initDist(-1, gDist) && !initDist(MAX_N + 1, gDist));
    CHECK(initDist(2, gDist));
    CHECK(!addEdge(2, gDist, 2, 0, 1) && !addEdge(2, gDist, 0, -1, 1) && !addEdge(2, gDist, 0, 2, 1));
    CHECK(addEdge(2, gDist, 0, 1, 5) && addEdge(2, gDist, 0, 1, 7) && addEdge(2, gDist, 0, 1, 3));
    CHECK(gDist[0][1] == 3); // 평행 간선은 최소 비용만 남는다
    CHECK(initDist(0, gDist));
    floydWarshall(0, gDist);

    // 생성기 경로(비음수): 작은 n에서 큰 n으로, 다시 작은 n으로.
    for (int n : {40, 2, 1, 0, 25}) builderCase(n, n * 4, 1000000000LL);
    // 용량 경계: 정점 MAX_N개. 조밀한 비음수 그래프와 일자 경로, 10^9 비용의 합은 3 * 10^11.
    builderCase(MAX_N, MAX_N * 6, 1000000000LL);
    {
        CHECK(initDist(MAX_N, gDist));
        for (int i = 0; i + 1 < MAX_N; ++i) CHECK(addEdge(MAX_N, gDist, i, i + 1, 1000000000LL));
        initNext(MAX_N, gDist, gNext);
        for (int k = 0; k < MAX_N; ++k) for (int i = 0; i < MAX_N; ++i) for (int j = 0; j < MAX_N; ++j)
            relaxPath(i, j, k, gDist, gNext);
        for (int j = 0; j < MAX_N; ++j) CHECK(gDist[0][j] == 1000000000LL * j && gDist[j][0] == (j == 0 ? 0 : INF));
        CHECK(restorePath(0, MAX_N - 1, gNext, gPath) == MAX_N); // 경로 버퍼가 가득 차는 가장 긴 경우
        for (int i = 0; i < MAX_N; ++i) CHECK(gPath[i] == i);
        CHECK(restorePath(MAX_N - 1, 0, gNext, gPath) == 0);
        CHECK(restorePath(5, 5, gNext, gPath) == 1 && gPath[0] == 5);
    }
    // 용량 경계: 정점 MAX_N개 전체에 음수 사이클(모든 비용 -1). 값이 하한 -INF에서 멈추고 모든 쌍이 영향을 받는다.
    {
        CHECK(initDist(MAX_N, gDist));
        for (int i = 0; i < MAX_N; ++i) CHECK(addEdge(MAX_N, gDist, i, (i + 1) % MAX_N, -1));
        initNext(MAX_N, gDist, gNext);
        for (int k = 0; k < MAX_N; ++k) for (int i = 0; i < MAX_N; ++i) for (int j = 0; j < MAX_N; ++j)
            relaxPath(i, j, k, gDist, gNext); // floydWarshall과 같은 결과를 내면서 next도 갱신
        negativeCyclePairs(MAX_N, gDist, gAffected);
        for (int i = 0; i < MAX_N; ++i) for (int j = 0; j < MAX_N; ++j)
            CHECK(gDist[i][j] >= -INF && gAffected[i][j]);
        // 영향을 받는 쌍을 복원해도 next 사슬이 돌더라도 길이 상한에서 끝나 무한 반복하지 않는다.
        for (int t = 0; t < 20; ++t) CHECK(restorePath(rnd(MAX_N), rnd(MAX_N), gNext, gPath) >= 0);
    }
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
