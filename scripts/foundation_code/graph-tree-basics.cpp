// graph-tree-basics 하네스: 제출 코드 바깥의 로컬 검사. 이 강의에는 표준 입력 연습이 없다.
// lesson.md(그래프·트리 함수)와 pages/mst-kruskal-prim.md(Kruskal)의 코드를 함께 검사한다.
#include <queue>
#include <utility>
static int sample() { return 0; }

static Graph gTree;
static int gDepth[MAX_V], gSub[MAX_V], gDist[MAX_V];

struct RandomTree {
    int n;
    std::vector<std::pair<int, int>> edges; // 무작위 정점 번호, 무작위 순서
};

// 정점 i는 앞선 정점 하나에 붙는다. mode 0: 무작위, 1: 일자, 2: 별, 3: 폭 3 이내의 얕은 일자.
static RandomTree makeTree(int n, int mode) {
    RandomTree tree;
    tree.n = n;
    std::vector<int> label(n);
    std::iota(label.begin(), label.end(), 0);
    for (int i = n - 1; i > 0; --i) std::swap(label[i], label[rnd(i + 1)]);
    for (int i = 1; i < n; ++i) {
        int parent = mode == 0 ? rnd(i) : mode == 1 ? i - 1 : mode == 2 ? 0 : i - 1 - rnd(std::min(i, 3));
        int a = label[i], b = label[parent];
        if (rnd(2)) std::swap(a, b);
        tree.edges.push_back({a, b});
    }
    for (int i = (int)tree.edges.size() - 1; i > 0; --i) std::swap(tree.edges[i], tree.edges[rnd(i + 1)]);
    return tree;
}

static void load(const RandomTree& tree) {
    gTree.init(tree.n);
    for (auto& e : tree.edges) {
        CHECK(gTree.addEdge(e.first, e.second));
        CHECK(gTree.addEdge(e.second, e.first));
    }
}

static std::vector<std::vector<int>> adjacency(const RandomTree& tree) {
    std::vector<std::vector<int>> adj(tree.n);
    for (auto& e : tree.edges) { adj[e.first].push_back(e.second); adj[e.second].push_back(e.first); }
    return adj;
}

// 독립 기준 1: 루트 기준 BFS 순서로 부모·깊이·부분트리 크기를 구한다(재귀 없음).
struct Rooted { std::vector<int> depth, sub, parent, order; };
static Rooted rootAt(const std::vector<std::vector<int>>& adj, int root) {
    int n = (int)adj.size();
    Rooted r{std::vector<int>(n, -1), std::vector<int>(n, 1), std::vector<int>(n, -1), {}};
    r.depth[root] = 0;
    r.order.push_back(root);
    for (size_t head = 0; head < r.order.size(); ++head) {
        int u = r.order[head];
        for (int v : adj[u]) if (r.depth[v] == -1) { r.depth[v] = r.depth[u] + 1; r.parent[v] = u; r.order.push_back(v); }
    }
    for (int i = n - 1; i > 0; --i) r.sub[r.parent[r.order[i]]] += r.sub[r.order[i]];
    return r;
}

// 독립 기준 2: 지름은 부분트리 높이 DP(가장 깊은 두 자식 높이의 합)로 구한다.
static int diameterOracle(const std::vector<std::vector<int>>& adj) {
    int n = (int)adj.size();
    if (n == 0) return 0;
    Rooted r = rootAt(adj, 0);
    std::vector<int> best1(n, 0), best2(n, 0);
    int answer = 0;
    for (int i = n - 1; i >= 0; --i) {
        int u = r.order[i];
        answer = std::max(answer, best1[u] + best2[u]);
        int p = r.parent[u];
        if (p == -1) continue;
        int h = best1[u] + 1;
        if (h > best1[p]) { best2[p] = best1[p]; best1[p] = h; }
        else if (h > best2[p]) best2[p] = h;
    }
    return answer;
}

// 독립 기준 3: 센트로이드는 "정점을 지웠을 때 가장 큰 조각이 최소"인 정점이다(정의 그대로).
static std::vector<int> centroidOracle(const std::vector<std::vector<int>>& adj) {
    int n = (int)adj.size();
    std::vector<int> largest(n, 0);
    for (int removed = 0; removed < n; ++removed) {
        std::vector<int> seen(n, 0);
        seen[removed] = 1;
        for (int s = 0; s < n; ++s) {
            if (seen[s]) continue;
            int size = 0;
            std::vector<int> stack = {s};
            seen[s] = 1;
            while (!stack.empty()) {
                int u = stack.back(); stack.pop_back(); ++size;
                for (int v : adj[u]) if (!seen[v]) { seen[v] = 1; stack.push_back(v); }
            }
            largest[removed] = std::max(largest[removed], size);
        }
    }
    int smallest = *std::min_element(largest.begin(), largest.end());
    std::vector<int> result;
    for (int v = 0; v < n; ++v) if (largest[v] == smallest) result.push_back(v);
    return result;
}

static void checkTree(const RandomTree& tree, int root, bool full) {
    int n = tree.n;
    load(tree);
    auto adj = adjacency(tree);
    Rooted want = rootAt(adj, root);
    for (int i = 0; i < MAX_V; ++i) { gDepth[i] = -777; gSub[i] = -777; } // 이전 TC의 값
    gDepth[root] = 0;
    buildTree(root, -1, gTree, gDepth, gSub);
    for (int u = 0; u < n; ++u) CHECK(gDepth[u] == want.depth[u] && gSub[u] == want.sub[u]);
    CHECK(gSub[root] == n);

    for (int i = 0; i < MAX_V; ++i) gDist[i] = -777;
    int far = farthest(root, gTree, n, gDist);
    int maxDist = 0;
    for (int u = 0; u < n; ++u) { CHECK(gDist[u] == want.depth[u]); maxDist = std::max(maxDist, gDist[u]); }
    CHECK(gDist[far] == maxDist);
    CHECK(treeDiameter(gTree, n) == diameterOracle(adj));

    int centroids[2], count = 0;
    findCentroids(root, -1, gTree, gSub, n, centroids, count);
    CHECK(count == 1 || count == 2);
    std::vector<int> got(centroids, centroids + count);
    std::sort(got.begin(), got.end());
    if (full) CHECK(got == centroidOracle(adj));
    else { // 큰 트리: 정의의 O(n^2) 검사 대신 "남는 조각이 n/2 이하인 정점" 집합과 비교한다.
        std::vector<int> expected;
        for (int v = 0; v < n; ++v) {
            int largest = n - want.sub[v];
            for (int w : adj[v]) if (want.parent[w] == v) largest = std::max(largest, want.sub[w]);
            if (largest <= n / 2) expected.push_back(v);
        }
        CHECK(got == expected);
    }
}

// ---- Kruskal ----
static Edge gEdges[MAX_EDGES];

// 독립 기준: 우선순위 큐 Prim. 연결이 안 되면 connected = false.
static long long primOracle(int n, const Edge* edges, int m, bool& connected) {
    std::vector<std::vector<std::pair<long long, int>>> adj(n);
    for (int i = 0; i < m; ++i) {
        adj[edges[i].u].push_back({edges[i].cost, edges[i].v});
        adj[edges[i].v].push_back({edges[i].cost, edges[i].u});
    }
    std::vector<char> in(n, 0);
    std::priority_queue<std::pair<long long, int>, std::vector<std::pair<long long, int>>,
                        std::greater<std::pair<long long, int>>> heap;
    heap.push({0, 0});
    long long total = 0;
    int taken = 0;
    while (!heap.empty()) {
        auto top = heap.top(); heap.pop();
        if (in[top.second]) continue;
        in[top.second] = 1;
        total += top.first;
        ++taken;
        for (auto& next : adj[top.second]) if (!in[next.second]) heap.push(next);
    }
    connected = taken == n;
    return total;
}

static void kruskalCase(int n, int m, long long maxCost, bool forceConnected) {
    for (int i = 0; i < m; ++i) {
        int u, v;
        if (forceConnected && i < n - 1) { u = i + 1; v = rnd(i + 1); } // 앞 n-1개는 신장 트리
        else { u = rnd(n); v = rnd(n); } // 자기 간선·평행 간선 포함
        gEdges[i] = {u, v, (long long)(harnessRng() % (unsigned long long)(maxCost + 1))};
    }
    for (int i = m - 1; i > 0; --i) std::swap(gEdges[i], gEdges[rnd(i + 1)]);
    std::vector<Edge> copy(gEdges, gEdges + m);
    for (int i = 0; i < MAX_N; ++i) { dsu.parent[i] = -5; dsu.size[i] = 99; } // 이전 TC의 값
    for (int i = 0; i < MAX_EDGES; ++i) edgeTemp[i] = {-1, -1, -1};
    long long total = -42;
    bool ok = kruskal(n, gEdges, m, total);
    bool connected;
    long long want = primOracle(n, copy.data(), m, connected);
    CHECK(ok == connected);
    if (ok) CHECK(total == want);
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 작은 트리 무작위 비교: 모양과 크기를 바꿔 가며 한 프로세스에서 이어 실행한다.
    for (int trial = 0; trial < 400; ++trial) {
        int n = 1 + rnd(11);
        RandomTree tree = makeTree(n, trial % 4);
        checkTree(tree, rnd(n), true);
    }
    // 큰 TC -> 작은 TC -> 큰 TC.
    for (int n : {3000, 2, 1, 700, 1, 2}) checkTree(makeTree(n, 0), 0, false);
    // 재귀 깊이: 일자 트리를 끝점과 중간 정점에서 시작한다(스택 한도 안의 깊이).
    {
        RandomTree path = makeTree(10000, 1);
        auto adj = adjacency(path);
        int end = 0;
        for (int v = 0; v < 10000; ++v) if (adj[v].size() == 1) { end = v; break; }
        checkTree(path, end, false);
        checkTree(path, rnd(10000), false);
    }
    // 용량 경계: 정점 MAX_V개. 무작위 트리(깊이 얕음)와 별은 간선 399998칸을 쓰고, 일자 트리는 지름만 검사한다.
    checkTree(makeTree(MAX_V, 0), rnd(MAX_V), false);
    checkTree(makeTree(MAX_V, 2), rnd(MAX_V), false);
    {
        RandomTree path = makeTree(MAX_V, 1);
        load(path);
        CHECK(gTree.edgeCount == 2 * (MAX_V - 1) && gTree.edgeCount <= MAX_E);
        CHECK(treeDiameter(gTree, MAX_V) == MAX_V - 1);
    }
    // 빈 트리와 범위 밖.
    gTree.init(0);
    CHECK(treeDiameter(gTree, 0) == 0);
    CHECK(treeDiameter(gTree, -1) == -1 && treeDiameter(gTree, MAX_V + 1) == -1);
    gTree.init(1);
    CHECK(treeDiameter(gTree, 1) == 0);

    // Kruskal: 무작위 비교(연결/비연결, 비용 동률·0·큰 값 포함).
    const long long costs[3] = {3, 1000000, 1000000000000LL};
    for (int trial = 0; trial < 800; ++trial) {
        int n = 1 + rnd(10);
        int m = rnd(2 * n + 6);
        bool force = trial % 2 == 0 && m >= n - 1;
        kruskalCase(n, m, costs[rnd(3)], force);
    }
    for (int n : {2000, 2, 1, 500, 1}) kruskalCase(n, n * 3, 1000000000LL, true);
    // 용량 경계: 정점 MAX_N, 간선 MAX_EDGES. 합이 int 범위를 넘고 long long으로 계산된다.
    kruskalCase(MAX_N, MAX_EDGES, 1000000000000LL, true);
    kruskalCase(MAX_N, MAX_EDGES, 1000000000000LL, false); // 무작위라 거의 확실히 비연결
    {
        long long total = 0;
        for (int i = 0; i < MAX_EDGES; ++i) gEdges[i] = {0, 0, 5}; // 자기 간선만
        CHECK(!kruskal(MAX_N, gEdges, MAX_EDGES, total)); // 연결되지 않음
        CHECK(kruskal(1, gEdges, MAX_EDGES, total) && total == 0); // 정점 1개: 간선 없이 연결
        CHECK(!kruskal(MAX_N, gEdges, MAX_EDGES + 1, total));
        CHECK(!kruskal(MAX_N + 1, gEdges, 0, total) && !kruskal(0, gEdges, 0, total));
        CHECK(!kruskal(1, gEdges, -1, total));
        CHECK(!kruskal(2, gEdges, 0, total)); // 간선 없는 두 정점
        // 정점 MAX_N개 일자 + 비용 10^12: 합 (MAX_N - 1) * 10^12 = 약 2 * 10^17.
        for (int i = 0; i + 1 < MAX_N; ++i) gEdges[i] = {i, i + 1, 1000000000000LL};
        CHECK(kruskal(MAX_N, gEdges, MAX_N - 1, total) && total == (long long)(MAX_N - 1) * 1000000000000LL);
    }
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
