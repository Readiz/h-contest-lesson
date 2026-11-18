// dijkstra 하네스: 제출 코드 바깥의 로컬 검사.
static Graph gGraph;
static long long gDist[MAX_V];

static int sample() {
    int n, m, s;
    std::cin >> n >> m >> s;
    gGraph.init(n);
    for (int i = 0; i < m; ++i) {
        int u, v;
        long long w;
        std::cin >> u >> v >> w;
        CHECK(gGraph.addEdge(u, v, w));
    }
    CHECK(dijkstra(gGraph, n, s, gDist));
    for (int i = 0; i < n; ++i) std::printf("%lld%c", gDist[i] == INF ? -1 : gDist[i], i + 1 < n ? ' ' : '\n');
    return 0;
}

struct E { int u, v; long long w; };

// 독립 기준: 간선 수 단계 DP(Bellman-Ford). 음수 없는 가중치에서 n-1번이면 충분하다.
static std::vector<long long> oracle(int n, const std::vector<E>& edges, int s) {
    std::vector<long long> best(n, INF);
    best[s] = 0;
    for (int step = 0; step < n; ++step) {
        auto after = best;
        for (const E& e : edges)
            if (best[e.u] != INF && best[e.u] + e.w < after[e.v]) after[e.v] = best[e.u] + e.w;
        best = after;
    }
    return best;
}

static void randomCase(int n, int edgeCount, long long maxWeight) {
    gGraph.init(n);
    std::vector<E> edges;
    for (int i = 0; i < edgeCount; ++i) {
        E e = {rnd(n), rnd(n), (long long)(harnessRng() % (unsigned long long)(maxWeight + 1))};
        edges.push_back(e);
        CHECK(gGraph.addEdge(e.u, e.v, e.w));
    }
    int s = rnd(n);
    for (int i = 0; i < MAX_V; ++i) gDist[i] = -12345; // 이전 TC의 값
    CHECK(dijkstra(gGraph, n, s, gDist));
    auto want = oracle(n, edges, s);
    for (int i = 0; i < n; ++i) CHECK(gDist[i] == want[i]);
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 작은 그래프 무작위 비교. 크기를 바꾸며 한 프로세스에서 이어 실행한다.
    const long long weights[4] = {0, 3, 1000000000LL, 20};
    for (int trial = 0; trial < 600; ++trial) {
        int n = 1 + rnd(10);
        randomCase(n, rnd(n * n + 1), weights[rnd(4)]);
    }
    for (int n : {300, 2, 1, 150, 1}) randomCase(n, n * 3, 1000000000LL);

    // 계약 위반 입력.
    gGraph.init(3);
    CHECK(!dijkstra(gGraph, 0, 0, gDist));
    CHECK(!dijkstra(gGraph, 3, 3, gDist));
    CHECK(!dijkstra(gGraph, 3, -1, gDist));
    CHECK(!dijkstra(gGraph, -1, 0, gDist));
    CHECK(!dijkstra(gGraph, MAX_V + 1, 0, gDist));
    // 본문의 음수 간선 반례: 위 코드는 dist[1] = -5를 남긴다.
    gGraph.init(3);
    CHECK(gGraph.addEdge(0, 1, 2) && gGraph.addEdge(0, 2, 5) && gGraph.addEdge(2, 1, -10));
    CHECK(dijkstra(gGraph, 3, 0, gDist));
    CHECK(gDist[0] == 0 && gDist[1] == -5 && gDist[2] == 5);
    // 평행 간선·비용 0 간선·자기 간선.
    gGraph.init(4);
    CHECK(gGraph.addEdge(0, 1, 7) && gGraph.addEdge(0, 1, 0) && gGraph.addEdge(0, 2, 9));
    CHECK(gGraph.addEdge(1, 2, 0) && gGraph.addEdge(2, 2, 0));
    CHECK(dijkstra(gGraph, 4, 0, gDist));
    CHECK(gDist[0] == 0 && gDist[1] == 0 && gDist[2] == 0 && gDist[3] == INF);

    // 용량 경계 1: 정점 MAX_V개의 긴 경로, 가중치 10^9 -> 거리는 2 * 10^14까지.
    gGraph.init(MAX_V);
    for (int i = 0; i + 1 < MAX_V; ++i) CHECK(gGraph.addEdge(i, i + 1, 1000000000LL));
    CHECK(dijkstra(gGraph, MAX_V, 0, gDist));
    for (int i = 0; i < MAX_V; ++i) CHECK(gDist[i] == 1000000000LL * i);
    // 용량 경계 2: 같은 정점으로 가는 평행 간선 MAX_E개가 모두 성공한 완화가 된다.
    // 목록은 나중에 넣은 간선부터 읽으므로 비용이 커지는 순서로 넣으면 매번 거리가 줄어
    // 힙에 낡은 후보가 MAX_E개까지 동시에 쌓인다.
    gGraph.init(2);
    for (int j = 0; j < MAX_E; ++j) CHECK(gGraph.addEdge(0, 1, 1000000LL + j));
    CHECK(gGraph.edgeCount == MAX_E && !gGraph.addEdge(0, 1, 0));
    CHECK(dijkstra(gGraph, 2, 0, gDist));
    CHECK(gDist[0] == 0 && gDist[1] == 1000000LL);
    // 용량 경계 3: 정점 133334개가 서로 다른 시점에 t의 거리를 줄이는 큰 입력 (낡은 후보가 오래 남는다).
    const int K = (MAX_E - 1) / 3;
    const int t = K + 1, z = K + 2;
    gGraph.init(z + 1);
    for (int i = 1; i <= K; ++i) {
        CHECK(gGraph.addEdge(0, i, i));
        CHECK(gGraph.addEdge(i, t, 4LL * K - 4LL * i + 9));
        CHECK(gGraph.addEdge(i, t, 4LL * K - 4LL * i + 10));
    }
    CHECK(gGraph.addEdge(t, z, 1));
    CHECK(gGraph.edgeCount == MAX_E);
    CHECK(dijkstra(gGraph, z + 1, 0, gDist));
    CHECK(gDist[t] == K + 9 && gDist[z] == K + 10);

    // 경로 복원: parent 사슬을 따라 거꾸로 올라간 뒤 뒤집는다.
    int parent[5] = {-1, 0, 1, 1, 3};
    int path[5];
    CHECK(restorePath(4, parent, path) == 4);
    CHECK(path[0] == 0 && path[1] == 1 && path[2] == 3 && path[3] == 4);
    CHECK(restorePath(0, parent, path) == 1 && path[0] == 0);
    static int line[MAX_V], linePath[MAX_V];
    line[0] = -1;
    for (int i = 1; i < MAX_V; ++i) line[i] = i - 1;
    CHECK(restorePath(MAX_V - 1, line, linePath) == MAX_V);
    for (int i = 0; i < MAX_V; ++i) CHECK(linePath[i] == i);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
