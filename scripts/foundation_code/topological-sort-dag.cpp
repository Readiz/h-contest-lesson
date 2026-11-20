// topological-sort-dag 하네스: 제출 코드 바깥의 로컬 검사.
#include <functional>
#include <utility>

static Graph gGraph;
static int gOrder[MAX_V];
static long long gFinish[MAX_V];
static int gDuration[MAX_V];

// 연습(사전순 최소 위상 순서)의 정답: 본문 "순서가 여러 개일 때"대로 큐 대신 공통 min-heap 블록을 쓴다.
// 본문 코드 자체는 FIFO 순서를 내므로 이 함수는 하네스 안에서만 쓴다. 사이클이면 -1을 반환한다.
static hc::MinHeap<MAX_V> gHeap;
static int gLexIndegree[MAX_V];
static int lexSmallestOrder(const Graph& graph, int n, int order[]) {
    for (int i = 0; i < n; ++i) gLexIndegree[i] = 0;
    for (int u = 0; u < n; ++u)
        for (int e = graph.head[u]; e != -1; e = graph.next[e]) gLexIndegree[graph.to[e]]++;
    gHeap.clear();
    for (int i = 0; i < n; ++i) if (gLexIndegree[i] == 0) CHECK(gHeap.push(i, i));
    int count = 0;
    hc::HeapItem top;
    while (gHeap.pop(top)) {
        int u = top.id;
        order[count++] = u;
        for (int e = graph.head[u]; e != -1; e = graph.next[e])
            if (--gLexIndegree[graph.to[e]] == 0) CHECK(gHeap.push(graph.to[e], graph.to[e]));
    }
    return count == n ? n : -1;
}

static int sample() {
    int n, m;
    std::cin >> n >> m;
    gGraph.init(n);
    for (int i = 0; i < m; ++i) {
        int u, v;
        std::cin >> u >> v;
        CHECK(gGraph.addEdge(u, v));
    }
    int count = topologicalSort(gGraph, n, gOrder); // 본문 코드가 사이클 여부를 판정한다.
    if (count != n) { std::printf("CYCLE\n"); return 0; }
    CHECK(lexSmallestOrder(gGraph, n, gOrder) == n);
    for (int i = 0; i < n; ++i) std::printf("%d%c", gOrder[i], i + 1 < n ? ' ' : '\n');
    return 0;
}

struct E { int u, v; };

// 독립 기준: 전이 폐포. 어떤 사이클에서 도달 가능한(사이클 위 포함) 정점은 끝내 처리되지 못한다.
static std::vector<char> processable(int n, const std::vector<E>& edges) {
    std::vector<std::vector<char>> reach(n, std::vector<char>(n, 0));
    for (const E& e : edges) reach[e.u][e.v] = 1;
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j)
        if (reach[i][k] && reach[k][j]) reach[i][j] = 1;
    std::vector<char> ok(n, 1);
    for (int c = 0; c < n; ++c) {
        if (!reach[c][c]) continue;
        ok[c] = 0;
        for (int v = 0; v < n; ++v) if (reach[c][v]) ok[v] = 0;
    }
    return ok;
}

static void randomCase(int n, int edgeCount, bool forceDag) {
    gGraph.init(n);
    std::vector<E> edges;
    std::vector<int> label(n);
    std::iota(label.begin(), label.end(), 0);
    for (int i = n - 1; i > 0; --i) std::swap(label[i], label[rnd(i + 1)]);
    for (int i = 0; i < edgeCount && n > 0; ++i) {
        int a = rnd(n), b = rnd(n);
        if (forceDag) { // 무작위 순서에서 앞 -> 뒤 방향만, 평행 간선은 허용
            if (a == b) continue;
            if (a > b) std::swap(a, b);
            a = label[a]; b = label[b];
        }
        edges.push_back({a, b});
        CHECK(gGraph.addEdge(a, b));
    }
    for (int i = 0; i < MAX_V; ++i) gOrder[i] = -9; // 이전 TC의 값
    int count = topologicalSort(gGraph, n, gOrder);
    auto ok = processable(n, edges);
    int expected = 0;
    for (int v = 0; v < n; ++v) expected += ok[v];
    CHECK(count == expected);
    if (forceDag) CHECK(count == n);
    // 반환된 앞 count개는 서로 다른 처리 가능 정점이고, 간선의 앞뒤 순서를 지킨다.
    std::vector<int> position(n, -1);
    for (int i = 0; i < count; ++i) {
        CHECK(gOrder[i] >= 0 && gOrder[i] < n && ok[gOrder[i]] && position[gOrder[i]] == -1);
        position[gOrder[i]] = i;
    }
    for (const E& e : edges)
        if (position[e.u] != -1 && position[e.v] != -1) CHECK(position[e.u] < position[e.v]);
    if (n <= 7) { // 하네스의 사전순 계산을 모든 순열 중 유효한 첫 순서와 비교한다.
        std::vector<int> perm(n);
        std::iota(perm.begin(), perm.end(), 0);
        bool found = false;
        do {
            std::vector<int> at(n);
            for (int i = 0; i < n; ++i) at[perm[i]] = i;
            bool valid = true;
            for (const E& e : edges) if (at[e.u] >= at[e.v]) valid = false;
            if (valid) { found = true; break; }
        } while (std::next_permutation(perm.begin(), perm.end()));
        static int lexOrder[MAX_V];
        int got = lexSmallestOrder(gGraph, n, lexOrder);
        CHECK((got == n) == found);
        if (found) for (int i = 0; i < n; ++i) CHECK(lexOrder[i] == perm[i]);
    }
    // DAG 작업 완료 시간: 메모이제이션 재귀 기준.
    for (int i = 0; i < n; ++i) { gDuration[i] = rnd(10); gFinish[i] = -55; }
    bool good = earliestFinish(gGraph, n, gDuration, gFinish);
    CHECK(good == (count == n));
    if (good) {
        std::vector<long long> memo(n, -1);
        std::vector<std::vector<int>> pred(n);
        for (const E& e : edges) pred[e.v].push_back(e.u);
        std::function<long long(int)> finishOf = [&](int v) {
            if (memo[v] != -1) return memo[v];
            long long start = 0;
            for (int p : pred[v]) start = std::max(start, finishOf(p));
            return memo[v] = start + gDuration[v];
        };
        for (int v = 0; v < n; ++v) CHECK(gFinish[v] == finishOf(v));
    }
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 작은 그래프 무작위: 사이클 있는 그래프와 DAG를 섞어 크기를 바꿔 가며 이어 실행한다.
    for (int trial = 0; trial < 1500; ++trial) {
        int n = rnd(9);
        randomCase(n, rnd(2 * n + 3), trial % 3 == 0);
    }
    for (int n : {60, 3, 0, 40, 1, 7}) randomCase(n, n * 2, true);
    for (int n : {60, 3, 40, 1}) randomCase(n, n * 2, false);
    // 본문 예: 0->2, 1->2, 2->3 / 작업 시간 2 5 3 4는 완료 시간 2 5 8 12.
    gGraph.init(4);
    CHECK(gGraph.addEdge(0, 2) && gGraph.addEdge(1, 2) && gGraph.addEdge(2, 3));
    const int duration[4] = {2, 5, 3, 4};
    long long finish[4];
    CHECK(earliestFinish(gGraph, 4, duration, finish));
    CHECK(finish[0] == 2 && finish[1] == 5 && finish[2] == 8 && finish[3] == 12);
    // 본문 사이클 예 0->1->2->0에 사이클 밖 정점 3(3->0)을 붙인다. 3만 처리되고 나머지는 남는다.
    gGraph.init(4);
    CHECK(gGraph.addEdge(0, 1) && gGraph.addEdge(1, 2) && gGraph.addEdge(2, 0) && gGraph.addEdge(3, 0));
    CHECK(topologicalSort(gGraph, 4, gOrder) == 1 && gOrder[0] == 3);
    CHECK(!earliestFinish(gGraph, 4, duration, finish));
    // 자기 간선, 범위 밖 n, 빈 그래프.
    gGraph.init(2);
    CHECK(gGraph.addEdge(1, 1));
    CHECK(topologicalSort(gGraph, 2, gOrder) == 1 && gOrder[0] == 0);
    CHECK(topologicalSort(gGraph, -1, gOrder) == -1 && topologicalSort(gGraph, MAX_V + 1, gOrder) == -1);
    gGraph.init(0);
    CHECK(topologicalSort(gGraph, 0, gOrder) == 0);

    // 용량 경계 1: 정점 MAX_V개의 일자 DAG(역방향 번호), 작업 시간 10^9 -> 완료 시간은 2 * 10^14까지.
    gGraph.init(MAX_V);
    for (int i = 0; i + 1 < MAX_V; ++i) CHECK(gGraph.addEdge(MAX_V - 1 - i, MAX_V - 2 - i));
    CHECK(topologicalSort(gGraph, MAX_V, gOrder) == MAX_V);
    for (int i = 0; i < MAX_V; ++i) CHECK(gOrder[i] == MAX_V - 1 - i);
    for (int i = 0; i < MAX_V; ++i) gDuration[i] = 1000000000;
    CHECK(earliestFinish(gGraph, MAX_V, gDuration, gFinish));
    for (int i = 0; i < MAX_V; ++i) CHECK(gFinish[MAX_V - 1 - i] == 1000000000LL * (i + 1));
    // 용량 경계 2: 간선 MAX_E개 모두 평행 간선 0 -> 1, 그리고 1개 더는 거부된다.
    gGraph.init(2);
    for (int i = 0; i < MAX_E; ++i) CHECK(gGraph.addEdge(0, 1));
    CHECK(!gGraph.addEdge(0, 1));
    CHECK(topologicalSort(gGraph, 2, gOrder) == 2 && gOrder[0] == 0 && gOrder[1] == 1);
    // 용량 경계 3: 정점 MAX_V개와 간선 MAX_E개의 무작위 DAG.
    gGraph.init(MAX_V);
    std::vector<int> label(MAX_V);
    std::iota(label.begin(), label.end(), 0);
    std::shuffle(label.begin(), label.end(), harnessRng);
    std::vector<E> edges;
    for (int i = 0; i < MAX_E; ++i) {
        int a = rnd(MAX_V - 1), b = a + 1 + rnd(MAX_V - 1 - a);
        edges.push_back({label[a], label[b]});
        CHECK(gGraph.addEdge(label[a], label[b]));
    }
    CHECK(topologicalSort(gGraph, MAX_V, gOrder) == MAX_V);
    std::vector<int> position(MAX_V, -1);
    for (int i = 0; i < MAX_V; ++i) position[gOrder[i]] = i;
    for (int i = 0; i < MAX_V; ++i) CHECK(position[i] != -1);
    for (const E& e : edges) CHECK(position[e.u] < position[e.v]);
    // 같은 그래프에 사이클을 만드는 간선 하나를 넣으면 처리 수가 줄어든다(간선 용량이 가득 차 새 그래프로).
    gGraph.init(MAX_V);
    for (int i = 0; i + 1 < MAX_V; ++i) CHECK(gGraph.addEdge(i, i + 1));
    CHECK(gGraph.addEdge(MAX_V - 1, 0));
    CHECK(topologicalSort(gGraph, MAX_V, gOrder) == 0);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
