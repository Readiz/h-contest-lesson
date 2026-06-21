# 그래프와 트리 기본 성질: 표현과 기본 탐색

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
