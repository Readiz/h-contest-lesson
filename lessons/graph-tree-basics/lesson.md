# 그래프와 트리 기본 성질

그래프는 정점과 간선으로 관계를 표현하는 자료구조입니다. 트리는 그래프 중에서도 **연결되어 있고 사이클이 없는** 특별한 형태입니다.

문제에서 그래프나 트리가 나오면 먼저 아래 질문을 확인합니다.

```text
정점과 간선 수가 얼마인가?
방향 그래프인가, 무방향 그래프인가?
간선에 가중치가 있는가?
그래프가 연결되어 있는가?
입력이 트리라고 보장되는가?
```

이 질문에 따라 DFS/BFS, Dijkstra, Union-Find, 최소 신장 트리, 트리 DP 같은 선택지가 갈립니다.

## 1. 그래프 표현

가장 많이 쓰는 표현은 인접 리스트입니다.

```cpp
vector<vector<int>> graph(n);

for (int i = 0; i < m; ++i) {
    int u, v;
    cin >> u >> v;
    graph[u].push_back(v);
    graph[v].push_back(u); // 무방향 그래프일 때만 반대쪽도 추가
}
```

가중치가 있으면 간선을 구조체나 `pair`로 저장합니다.

```cpp
struct Edge {
    int to;
    long long cost;
};

vector<vector<Edge>> graph(n);
```

인접 행렬은 `adj[u][v]`처럼 바로 확인할 수 있어서 편하지만, 메모리가 `O(n^2)`입니다. 정점 수가 크고 간선 수가 적은 일반적인 문제에서는 인접 리스트가 기본입니다.

| 표현 | 메모리 | 좋은 경우 |
| --- | --- | --- |
| 인접 리스트 | `O(V + E)` | 정점/간선이 큰 대부분의 문제 |
| 인접 행렬 | `O(V^2)` | 정점 수가 작고 두 정점 연결 여부를 자주 볼 때 |
| 간선 리스트 | `O(E)` | Kruskal처럼 간선을 정렬하거나 전체 간선을 훑을 때 |

## 2. DFS와 BFS

DFS는 한 길을 깊게 들어갔다가 돌아오고, BFS는 시작점에서 가까운 정점부터 넓게 봅니다.

| 탐색 | 자료구조 | 대표 용도 |
| --- | --- | --- |
| DFS | 재귀 또는 스택 | 연결 요소, 사이클 판정, 트리 DP, subtree 크기 |
| BFS | 큐 | 간선 비용이 모두 1인 최단거리, 레벨 탐색 |

무방향 그래프에서 연결 요소 개수는 방문하지 않은 정점마다 DFS/BFS를 한 번 시작해 셉니다.

```cpp
void dfs(int u, const vector<vector<int>>& graph, vector<int>& visited) {
    visited[u] = 1;
    for (int v : graph[u]) {
        if (visited[v]) continue;
        dfs(v, graph, visited);
    }
}

int countComponents(const vector<vector<int>>& graph) {
    int n = (int)graph.size();
    vector<int> visited(n, 0);
    int components = 0;

    for (int i = 0; i < n; ++i) {
        if (visited[i]) continue;
        components++;
        dfs(i, graph, visited);
    }
    return components;
}
```

정점 수가 아주 크면 재귀 DFS가 스택 제한에 걸릴 수 있습니다. 그때는 반복문 스택으로 바꾸거나, 트리 DP처럼 재귀가 편한 문제에서는 실행 환경의 스택 제한을 확인해야 합니다.

## 3. 트리의 기본 성질

정점이 `n`개인 무방향 그래프가 트리라면 항상 간선은 `n - 1`개입니다. 또 임의의 두 정점 사이에는 단순 경로가 정확히 하나만 있습니다.

트리에서 자주 쓰는 성질은 아래와 같습니다.

| 성질 | 의미 |
| --- | --- |
| 연결 + 사이클 없음 | 모든 정점이 이어져 있고, 돌아오는 길이 없다 |
| 간선 수 `n - 1` | 정점이 `n`개인 트리는 간선이 정확히 `n - 1`개 |
| 두 정점 사이 경로 유일 | `u`에서 `v`로 가는 단순 경로가 하나뿐 |
| 간선 하나 제거 | 트리가 두 컴포넌트로 나뉜다 |
| 다른 컴포넌트 사이 간선 하나 추가 | 다시 트리가 된다 |

입력이 트리라고 보장되지 않는다면, `m == n - 1`만으로는 충분하지 않습니다. 연결 여부도 확인해야 합니다.

```text
트리 판정 조건:
1. 간선 수가 n - 1이다.
2. 모든 정점이 하나의 연결 요소에 있다.
```

방향이 없는 단순 그래프에서는 위 두 조건이 성립하면 사이클이 없다는 것도 따라옵니다.

## 4. 트리를 루트 기준으로 보기

트리는 원래 루트가 없을 수 있습니다. 하지만 DFS/BFS를 시작할 정점을 하나 잡으면 부모, 깊이, subtree를 정의할 수 있습니다.

```cpp
void buildTree(
    int u,
    int parent,
    const vector<vector<int>>& tree,
    vector<int>& depth,
    vector<int>& subtreeSize
) {
    subtreeSize[u] = 1;
    for (int v : tree[u]) {
        if (v == parent) continue;
        depth[v] = depth[u] + 1;
        buildTree(v, u, tree, depth, subtreeSize);
        subtreeSize[u] += subtreeSize[v];
    }
}
```

`parent`를 인자로 들고 다니면 방문 배열 없이도 부모로 되돌아가는 간선을 건너뛸 수 있습니다. 단, 입력이 트리가 아니라 일반 그래프라면 방문 배열이 필요합니다.

트리에서 subtree 크기는 많은 문제의 기본 재료입니다.

```text
subtreeSize[u] = u를 루트로 하는 부분트리의 정점 수
```

이 값으로 균형 잡힌 루트, 센트로이드, 간선을 끊었을 때 생기는 컴포넌트 크기 등을 계산합니다.

## 5. 트리 지름

트리의 지름은 트리 안에서 가장 먼 두 정점 사이의 거리입니다. 간선 개수로 세기도 하고, 가중치가 있으면 가중치 합으로 세기도 합니다.

가중치가 없는 트리에서는 BFS 두 번으로 지름을 구할 수 있습니다.

```text
1. 아무 정점 A에서 BFS를 해서 가장 먼 정점 X를 찾는다.
2. X에서 다시 BFS를 해서 가장 먼 정점 Y를 찾는다.
3. dist[X][Y]가 트리의 지름이다.
```

트리에서는 경로가 유일하므로, 아무 곳에서 가장 먼 정점은 어떤 지름의 끝점이 됩니다.

```cpp
pair<int, int> farthest(int start, const vector<vector<int>>& tree) {
    int n = (int)tree.size();
    vector<int> dist(n, -1);
    queue<int> q;

    dist[start] = 0;
    q.push(start);

    while (!q.empty()) {
        int u = q.front();
        q.pop();

        for (int v : tree[u]) {
            if (dist[v] != -1) continue;
            dist[v] = dist[u] + 1;
            q.push(v);
        }
    }

    int best = start;
    for (int i = 0; i < n; ++i) {
        if (dist[i] > dist[best]) best = i;
    }
    return {best, dist[best]};
}

int treeDiameter(const vector<vector<int>>& tree) {
    auto [x, ignored] = farthest(0, tree);
    auto [y, diameter] = farthest(x, tree);
    return diameter;
}
```

가중치가 있는 트리에서는 BFS 대신 DFS로 누적 거리를 계산하면 됩니다. 다만 두 번의 BFS/DFS로 지름 끝점을 찾는 알고리즘은 보통 간선 가중치가 비음수라는 조건에서 안전하게 사용합니다. 음수 간선까지 허용하면서 "가장 큰 경로 합"을 묻는다면 지름 공식처럼 끝점 두 번을 고르기보다 트리 DP로 최대 경로를 따로 계산하는 편이 안전합니다.

## 6. 트리 중심과 센트로이드

트리 지름을 배우면 자주 헷갈리는 개념이 두 개 있습니다.

| 개념 | 기준 |
| --- | --- |
| 중심(center) | 모든 정점까지의 최대 거리가 최소가 되는 정점 |
| 센트로이드(centroid) | 제거했을 때 남는 컴포넌트 크기의 최댓값이 최소가 되는 정점 |

중심은 거리 기준이고, 센트로이드는 크기 기준입니다. 같은 정점일 수도 있지만 항상 같지는 않습니다.

센트로이드의 대표 성질은 아래와 같습니다.

```text
정점 c를 제거했을 때 생기는 모든 컴포넌트의 크기가 n / 2 이하이면
c는 트리의 센트로이드다.
```

트리의 센트로이드는 항상 1개 또는 2개 존재합니다. subtree 크기를 한 번 구하면 모든 정점이 센트로이드인지 확인할 수 있습니다.

```cpp
void findCentroids(
    int u,
    int parent,
    const vector<vector<int>>& tree,
    const vector<int>& subtreeSize,
    int n,
    vector<int>& centroids
) {
    int largestPart = n - subtreeSize[u];

    for (int v : tree[u]) {
        if (v == parent) continue;
        largestPart = max(largestPart, subtreeSize[v]);
        findCentroids(v, u, tree, subtreeSize, n, centroids);
    }

    if (largestPart * 2 <= n) {
        centroids.push_back(u);
    }
}
```

`n - subtreeSize[u]`는 `u`의 부모 방향에 남는 컴포넌트 크기입니다. 자식 방향 컴포넌트들은 각 `subtreeSize[v]`입니다. 이 중 최댓값이 `n / 2` 이하이면 `u`를 루트로 삼아도 어느 한쪽이 절반을 넘지 않습니다.

## 7. 최소 신장 트리

최소 신장 트리(MST, Minimum Spanning Tree)는 가중치가 있는 무방향 연결 그래프에서 모든 정점을 연결하면서 간선 비용 합이 최소인 트리입니다.

MST를 생각할 때 조건을 분리하면 실수가 줄어듭니다.

```text
1. 모든 정점이 연결되어야 한다.
2. 사이클은 필요 없다. 정점 n개를 잇는 트리는 간선 n - 1개다.
3. 비용 합이 최소여야 한다.
```

대표 알고리즘은 Kruskal과 Prim입니다.

| 알고리즘 | 핵심 아이디어 | 잘 맞는 표현 |
| --- | --- | --- |
| Kruskal | 간선을 비용 오름차순으로 보며, 사이클을 만들지 않으면 선택 | 간선 리스트 + Union-Find |
| Prim | 현재 연결된 정점 집합에서 바깥으로 나가는 가장 싼 간선을 선택 | 인접 리스트 + 우선순위 큐 |

Kruskal은 Union-Find를 거의 그대로 사용합니다.

```cpp
struct DSU {
    vector<int> parent;
    vector<int> size;

    DSU(int n) : parent(n), size(n, 1) {
        for (int i = 0; i < n; ++i) parent[i] = i;
    }

    int find(int x) {
        if (parent[x] == x) return x;
        return parent[x] = find(parent[x]);
    }

    bool unite(int a, int b) {
        int rootA = find(a);
        int rootB = find(b);
        if (rootA == rootB) return false;

        if (size[rootA] < size[rootB]) swap(rootA, rootB);
        parent[rootB] = rootA;
        size[rootA] += size[rootB];
        return true;
    }
};

struct Edge {
    int u;
    int v;
    long long cost;
};

long long kruskal(int n, vector<Edge> edges) {
    sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {
        return a.cost < b.cost;
    });

    DSU dsu(n);
    long long total = 0;
    int used = 0;

    for (const Edge& edge : edges) {
        if (!dsu.unite(edge.u, edge.v)) continue;
        total += edge.cost;
        used++;
    }

    if (used != n - 1) {
        return -1; // 모든 정점을 연결할 수 없음
    }
    return total;
}
```

왜 가장 싼 간선부터 봐도 될까요? 핵심은 절단 성질입니다.

```text
어떤 정점 집합 S와 나머지를 가르는 절단을 생각한다.
그 절단을 건너는 간선 중 가장 싼 간선은 MST에 넣어도 안전하다.
```

Kruskal은 비용이 작은 간선부터 보면서, 이미 같은 컴포넌트 안의 간선은 사이클을 만들기 때문에 버립니다. 서로 다른 컴포넌트를 잇는 간선은 그 순간 두 컴포넌트를 가르는 절단의 싼 후보로 볼 수 있어 안전하게 선택합니다.

## 8. MST에서 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 방향 그래프에 MST 적용 | 정의가 맞지 않음 | MST는 보통 무방향 그래프에서 사용 |
| 연결되지 않은 그래프 처리 누락 | 간선이 `n - 1`개보다 적게 선택됨 | 마지막에 `used == n - 1` 확인 |
| 같은 컴포넌트 간선 선택 | 사이클 생성 | Union-Find의 `unite` 반환값 사용 |
| 비용 합을 `int`로 저장 | overflow | 비용 합은 `long long` 사용 |
| 최대 신장 트리와 혼동 | 반대 답 | 최소면 오름차순, 최대면 내림차순 |

MST는 "최단 경로"와 다릅니다. MST는 전체 네트워크 연결 비용을 최소화하지만, 두 정점 사이의 경로가 반드시 최단거리라는 보장은 없습니다.

## 9. 문제를 볼 때 체크할 조건

그래프나 트리 문제가 나오면 아래 순서로 정리해 봅니다.

1. 정점과 간선 수가 커서 `O(V^2)`가 가능한가, `O(V + E)`가 필요한가?
2. 입력이 트리인지, 일반 그래프인지, 연결 그래프인지 확인했는가?
3. 간선에 방향이나 가중치가 있는가?
4. 거리 문제라면 BFS, Dijkstra, Bellman-Ford 중 어느 조건인가?
5. 연결성만 필요하다면 DFS/BFS 또는 Union-Find로 충분한가?
6. 모든 정점을 싸게 연결하는 문제라면 MST 조건인가?
7. 트리에서 "가장 먼 거리"라면 지름, "균형 잡힌 제거점"이라면 센트로이드를 떠올렸는가?

정리하면, 그래프 문제의 출발점은 표현과 탐색이고, 트리 문제의 출발점은 `n - 1`개 간선과 경로 유일성입니다. 그 위에서 지름은 거리, 센트로이드는 크기, MST는 전체 연결 비용을 묻는 도구로 구분하면 됩니다.
