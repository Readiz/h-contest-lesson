// zero-one-bfs 하네스: 제출 코드 바깥의 로컬 검사.
static Graph gGraph;
static int gDist[MAX_V];

// 로컬 연습: 비용 0 또는 1인 방향 그래프의 최소 비용, 도달 불가는 -1.
static int sample() {
    int n, m, s;
    std::cin >> n >> m >> s;
    gGraph.init(n);
    for (int i = 0; i < m; ++i) {
        int u, v, w;
        std::cin >> u >> v >> w;
        CHECK(gGraph.addEdge(u, v, w));
    }
    CHECK(zeroOneBfs(gGraph, n, s, gDist));
    for (int i = 0; i < n; ++i) std::printf("%d%c", gDist[i] == INF ? -1 : gDist[i], i + 1 < n ? ' ' : '\n');
    return 0;
}

struct E { int u, v, w; };

// 독립 기준: 간선 수 단계 DP(Bellman-Ford).
static std::vector<int> oracle(int n, const std::vector<E>& edges, int s) {
    std::vector<int> best(n, INF);
    best[s] = 0;
    for (int step = 0; step < n; ++step) {
        auto after = best;
        for (const E& e : edges)
            if (best[e.u] != INF && best[e.u] + e.w < after[e.v]) after[e.v] = best[e.u] + e.w;
        best = after;
    }
    return best;
}

static void randomCase(int n, int edgeCount, int zeroPercent) {
    gGraph.init(n);
    std::vector<E> edges;
    for (int i = 0; i < edgeCount; ++i) {
        E e = {rnd(n), rnd(n), rnd(100) < zeroPercent ? 0 : 1}; // 자기 간선·평행 간선·0비용 사이클 포함
        edges.push_back(e);
        CHECK(gGraph.addEdge(e.u, e.v, e.w));
    }
    int s = rnd(n);
    for (int i = 0; i < MAX_V; ++i) gDist[i] = -4242; // 이전 TC의 값
    CHECK(zeroOneBfs(gGraph, n, s, gDist));
    auto want = oracle(n, edges, s);
    for (int i = 0; i < n; ++i) CHECK(gDist[i] == want[i]);
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    const int zeros[4] = {0, 30, 70, 100};
    for (int trial = 0; trial < 800; ++trial) {
        int n = 1 + rnd(10);
        randomCase(n, rnd(n * n + 1), zeros[rnd(4)]);
    }
    for (int n : {300, 2, 1, 120, 1}) randomCase(n, 3 * n, 50);
    // 계약 위반 입력.
    gGraph.init(3);
    CHECK(!zeroOneBfs(gGraph, 0, 0, gDist) && !zeroOneBfs(gGraph, 3, 3, gDist));
    CHECK(!zeroOneBfs(gGraph, 3, -1, gDist) && !zeroOneBfs(gGraph, MAX_V + 1, 0, gDist));
    // 본문 그림의 예: 2를 꺼낸 뒤 1의 거리가 1에서 0으로 줄고 낡은 후보 1(1)은 건너뛴다.
    gGraph.init(5);
    CHECK(gGraph.addEdge(0, 1, 1) && gGraph.addEdge(0, 2, 0) && gGraph.addEdge(2, 1, 0));
    CHECK(gGraph.addEdge(1, 3, 1) && gGraph.addEdge(2, 3, 1) && gGraph.addEdge(3, 2, 0));
    CHECK(zeroOneBfs(gGraph, 5, 0, gDist));
    CHECK(gDist[0] == 0 && gDist[1] == 0 && gDist[2] == 0 && gDist[3] == 1 && gDist[4] == INF);
    // 용량 경계 1: 모든 정점이 먼저 비용 1로 뒤에 들어갔다가 비용 0으로 앞에 다시 들어간다.
    // deque에 정점당 두 번, 모두 2 * (MAX_V - 2)개 이상이 동시에 쌓인다.
    gGraph.init(MAX_V);
    for (int v = 2; v < MAX_V; ++v) CHECK(gGraph.addEdge(0, v, 1));
    CHECK(gGraph.addEdge(0, 1, 0)); // 목록에서는 가장 먼저 나와 1이 먼저 앞에 들어간다
    for (int v = 2; v < MAX_V; ++v) CHECK(gGraph.addEdge(1, v, 0));
    CHECK(zeroOneBfs(gGraph, MAX_V, 0, gDist));
    for (int v = 0; v < MAX_V; ++v) CHECK(gDist[v] == 0);
    // 용량 경계 2: 정점 MAX_V개의 긴 경로, 비용이 1과 0으로 번갈아 나온다.
    gGraph.init(MAX_V);
    for (int i = 0; i + 1 < MAX_V; ++i) CHECK(gGraph.addEdge(i, i + 1, i % 2 == 0 ? 1 : 0));
    CHECK(zeroOneBfs(gGraph, MAX_V, 0, gDist));
    for (int i = 0; i < MAX_V; ++i) CHECK(gDist[i] == (i + 1) / 2);
    // 간선 수 상한과 빈 정점 하나.
    gGraph.init(1);
    for (int i = 0; i < MAX_E; ++i) CHECK(gGraph.addEdge(0, 0, i % 2));
    CHECK(!gGraph.addEdge(0, 0, 0));
    CHECK(zeroOneBfs(gGraph, 1, 0, gDist) && gDist[0] == 0);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
