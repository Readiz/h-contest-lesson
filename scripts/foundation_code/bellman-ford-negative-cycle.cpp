// bellman-ford-negative-cycle 하네스: 제출 코드 바깥의 로컬 검사.
#include <functional>
#include <utility>

static EdgeList gEdges;
static long long gDist[MAX_V];
static int gParent[MAX_V];

struct W { int u, v; long long w; };

// 본문 "음수 사이클의 영향 범위" 3단계: n-1회 뒤에도 줄어드는 정점에서 도달 가능한 정점 표시.
// 본문 코드(bellmanFord)가 dist를 주고, 표시는 하네스에서 간선 목록으로 계산한다.
static void influenced(const EdgeList& graph, int n, const long long dist[], bool marked[]) {
    for (int i = 0; i < n; ++i) marked[i] = false;
    for (int i = 0; i < graph.count; ++i) {
        const Edge& e = graph.edge[i];
        if (dist[e.from] != INF && dist[e.from] + e.cost < dist[e.to]) marked[e.to] = true;
    }
    for (int pass = 0; pass < n; ++pass)
        for (int i = 0; i < graph.count; ++i)
            if (marked[graph.edge[i].from]) marked[graph.edge[i].to] = true;
}

static int sample() {
    int n, m, s;
    std::cin >> n >> m >> s;
    gEdges.init();
    for (int i = 0; i < m; ++i) {
        int u, v;
        long long w;
        std::cin >> u >> v >> w;
        CHECK(gEdges.add(u, v, w));
    }
    bool negative;
    CHECK(bellmanFord(gEdges, n, s, gDist, gParent, negative));
    bool marked[MAX_V];
    influenced(gEdges, n, gDist, marked);
    for (int v = 0; v < n; ++v) {
        if (marked[v]) std::printf("NEGATIVE");
        else if (gDist[v] == INF) std::printf("UNREACHABLE");
        else std::printf("%lld", gDist[v]);
        std::printf("%c", v + 1 < n ? ' ' : '\n');
    }
    return 0;
}

// 독립 기준 1: 단순 경로 열거. 현재 경로 위 정점으로 돌아가는 간선의 한 바퀴 비용이 음수이면
// 도달 가능한 음수 사이클이다. (본문 알고리즘과 다른 방식)
struct Enumerated {
    std::vector<long long> best;
    bool cycle;
};
static Enumerated enumerate(int n, const std::vector<W>& edges, int start) {
    std::vector<std::vector<std::pair<int, long long>>> graph(n);
    for (const W& e : edges) graph[e.u].push_back({e.v, e.w});
    Enumerated result{std::vector<long long>(n, INF), false};
    std::vector<long long> prefix(n, 0);
    std::function<void(int, int, long long)> dfs = [&](int u, int mask, long long sum) {
        result.best[u] = std::min(result.best[u], sum);
        prefix[u] = sum;
        for (auto& e : graph[u]) {
            if (mask & (1 << e.first)) {
                if (sum + e.second - prefix[e.first] < 0) result.cycle = true;
            } else dfs(e.first, mask | (1 << e.first), sum + e.second);
        }
    };
    dfs(start, 1 << start, 0);
    return result;
}

// 독립 기준 2: Floyd-Warshall 도달성과 음수 대각 원소로 영향 범위를 구한다. n <= 8, |w| <= 7.
static std::vector<char> influenceOracle(int n, const std::vector<W>& edges, int start) {
    const long long BIG = 1000000000000LL;
    std::vector<std::vector<long long>> d(n, std::vector<long long>(n, BIG));
    for (int i = 0; i < n; ++i) d[i][i] = 0;
    for (const W& e : edges) d[e.u][e.v] = std::min(d[e.u][e.v], e.w);
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j)
        if (d[i][k] < BIG && d[k][j] < BIG && d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
    std::vector<char> bad(n, 0);
    for (int k = 0; k < n; ++k)
        if (d[start][k] < BIG && d[k][k] < 0)
            for (int v = 0; v < n; ++v) if (d[k][v] < BIG) bad[v] = 1;
    return bad;
}

static void randomCase(int n, int edgeCount, int maxAbs) {
    std::vector<W> edges;
    gEdges.init();
    for (int i = 0; i < edgeCount; ++i) {
        W e = {rnd(n), rnd(n), (long long)rnd(2 * maxAbs + 1) - maxAbs};
        edges.push_back(e);
        CHECK(gEdges.add(e.u, e.v, e.w));
    }
    int start = rnd(n);
    for (int i = 0; i < MAX_V; ++i) { gDist[i] = -123; gParent[i] = -123; } // 이전 TC의 값
    bool negative = true; // 함수가 반드시 덮어써야 한다.
    CHECK(bellmanFord(gEdges, n, start, gDist, gParent, negative));
    Enumerated want = enumerate(n, edges, start);
    CHECK(negative == want.cycle);
    bool marked[MAX_V];
    influenced(gEdges, n, gDist, marked);
    auto bad = influenceOracle(n, edges, start);
    for (int v = 0; v < n; ++v) CHECK((marked[v] != 0) == (bad[v] != 0));
    CHECK(negative == (std::count(bad.begin(), bad.end(), 1) > 0));
    if (!want.cycle) {
        for (int v = 0; v < n; ++v) CHECK(gDist[v] == want.best[v]);
        // parent 사슬은 start까지 이어지고, 각 단계는 실제 간선의 최소 비용과 맞는다.
        CHECK(gParent[start] == -1);
        for (int v = 0; v < n; ++v) {
            if (v == start) continue;
            if (gDist[v] == INF) { CHECK(gParent[v] == -1); continue; }
            int p = gParent[v];
            CHECK(p >= 0 && p < n && gDist[p] != INF);
            long long cheapest = INF;
            for (const W& e : edges) if (e.u == p && e.v == v) cheapest = std::min(cheapest, e.w);
            CHECK(gDist[v] == gDist[p] + cheapest);
            int steps = 0, cur = v;
            while (cur != start) { cur = gParent[cur]; CHECK(cur >= 0 && ++steps <= n); }
        }
    }
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 작은 그래프 무작위: 크기와 비용 범위를 바꿔 가며 한 프로세스에서 이어 실행한다.
    const int ranges[3] = {2, 7, 7};
    for (int trial = 0; trial < 1500; ++trial) {
        int n = 1 + rnd(7);
        randomCase(n, rnd(n * n + 2), ranges[rnd(3)]);
    }
    for (int n : {8, 2, 1, 6, 1, 3}) randomCase(n, n * 2, 7);

    // 본문 작은 예시: 한 번에 [0, 4, 1, 3], 사이클 없음.
    gEdges.init();
    CHECK(gEdges.add(0, 1, 4) && gEdges.add(0, 2, 5) && gEdges.add(1, 2, -3) && gEdges.add(2, 3, 2));
    bool negative = true;
    CHECK(bellmanFord(gEdges, 4, 0, gDist, gParent, negative) && !negative);
    CHECK(gDist[0] == 0 && gDist[1] == 4 && gDist[2] == 1 && gDist[3] == 3);
    // 본문 그림: 0->1(+2), 1->2(-3), 2->1(+1), 2->3(+4). 1->2->1은 한 바퀴에 -2.
    gEdges.init();
    CHECK(gEdges.add(0, 1, 2) && gEdges.add(1, 2, -3) && gEdges.add(2, 1, 1) && gEdges.add(2, 3, 4));
    CHECK(bellmanFord(gEdges, 4, 0, gDist, gParent, negative) && negative);
    // 시작점에서 갈 수 없는 음수 사이클은 판정에 영향이 없다.
    gEdges.init();
    CHECK(gEdges.add(0, 1, 5) && gEdges.add(2, 3, -1) && gEdges.add(3, 2, -1));
    CHECK(bellmanFord(gEdges, 4, 0, gDist, gParent, negative) && !negative);
    CHECK(gDist[1] == 5 && gDist[2] == INF && gDist[3] == INF);
    // 도달 불가 정점에서 나오는 음수 간선이 도달 불가 표시를 깨지 않는다(INF + cost < INF).
    gEdges.init();
    CHECK(gEdges.add(2, 1, -3) && gEdges.add(0, 3, 1));
    CHECK(bellmanFord(gEdges, 4, 0, gDist, gParent, negative) && !negative);
    CHECK(gDist[1] == INF && gDist[2] == INF && gDist[3] == 1 && gParent[1] == -1);
    // 자기 음수 간선, 비용 0 사이클, 평행 간선.
    gEdges.init();
    CHECK(gEdges.add(0, 0, -1));
    CHECK(bellmanFord(gEdges, 1, 0, gDist, gParent, negative) && negative);
    gEdges.init();
    CHECK(gEdges.add(0, 1, 0) && gEdges.add(1, 0, 0) && gEdges.add(0, 1, 7) && gEdges.add(0, 1, 2));
    CHECK(bellmanFord(gEdges, 2, 0, gDist, gParent, negative) && !negative && gDist[1] == 0);
    // 계약 위반 입력과 빈 간선.
    gEdges.init();
    CHECK(!bellmanFord(gEdges, 0, 0, gDist, gParent, negative));
    CHECK(!bellmanFord(gEdges, 3, 3, gDist, gParent, negative));
    CHECK(!bellmanFord(gEdges, 3, -1, gDist, gParent, negative));
    CHECK(!bellmanFord(gEdges, MAX_V + 1, 0, gDist, gParent, negative));
    CHECK(bellmanFord(gEdges, 3, 1, gDist, gParent, negative) && !negative);
    CHECK(gDist[1] == 0 && gDist[0] == INF && gDist[2] == INF);

    // 용량 경계 1: 정점 MAX_V개의 일자, 비용 -10^6 -> dist[i] = -i * 10^6.
    gEdges.init();
    for (int i = 0; i + 1 < MAX_V; ++i) CHECK(gEdges.add(i, i + 1, -1000000));
    CHECK(bellmanFord(gEdges, MAX_V, 0, gDist, gParent, negative) && !negative);
    for (int i = 0; i < MAX_V; ++i) CHECK(gDist[i] == -1000000LL * i);
    // 일자 간선을 거꾸로 넣으면 한 회차에 하나씩만 전파되어 n - 1회가 모두 필요하다.
    gEdges.init();
    for (int i = MAX_V - 2; i >= 0; --i) CHECK(gEdges.add(i, i + 1, 1000000));
    CHECK(bellmanFord(gEdges, MAX_V, 0, gDist, gParent, negative) && !negative);
    for (int i = 0; i < MAX_V; ++i) CHECK(gDist[i] == 1000000LL * i);
    // 용량 경계 2: 간선 MAX_E개가 모두 -10^6인 음수 사이클. 값이 크게 내려가도 INF 범위 안이다.
    gEdges.init();
    for (int i = 0; i < MAX_E; ++i) CHECK(gEdges.add(i % MAX_V, (i + 1) % MAX_V, -1000000));
    CHECK(!gEdges.add(0, 1, 0) && gEdges.count == MAX_E);
    CHECK(bellmanFord(gEdges, MAX_V, 0, gDist, gParent, negative) && negative);
    for (int i = 0; i < MAX_V; ++i) CHECK(gDist[i] > -INF && gDist[i] < INF);
    // 평행 간선 MAX_E개: 비용이 점점 작아져 마지막 간선이 최소다.
    gEdges.init();
    for (int i = 0; i < MAX_E; ++i) CHECK(gEdges.add(0, 1, 1000000 - i));
    CHECK(bellmanFord(gEdges, 2, 0, gDist, gParent, negative) && !negative && gDist[1] == 1000000 - (MAX_E - 1));
    // 용량 경계 3: 정점 MAX_V개의 무작위 큰 비음수 그래프를 단순 DP(간선 수 단계)와 비교한다.
    gEdges.init();
    std::vector<W> edges;
    for (int i = 0; i < MAX_E; ++i) {
        W e = {rnd(MAX_V), rnd(MAX_V), (long long)rnd(1000001)};
        edges.push_back(e);
        CHECK(gEdges.add(e.u, e.v, e.w));
    }
    CHECK(bellmanFord(gEdges, MAX_V, 0, gDist, gParent, negative) && !negative);
    std::vector<long long> best(MAX_V, INF);
    best[0] = 0;
    for (int step = 0; step < MAX_V; ++step) {
        auto after = best;
        for (const W& e : edges)
            if (best[e.u] != INF && best[e.u] + e.w < after[e.v]) after[e.v] = best[e.u] + e.w;
        best = after;
    }
    for (int i = 0; i < MAX_V; ++i) CHECK(gDist[i] == best[i]);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
