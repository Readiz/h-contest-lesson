# 위상 정렬과 DAG DP

위상 정렬은 방향 그래프에서 모든 간선의 방향을 지키도록 정점을 나열하는 방법입니다.

```text
A를 끝내야 B를 할 수 있다.
B를 끝내야 C를 할 수 있다.
```

이런 의존 관계가 있으면 가능한 작업 순서를 찾아야 합니다. 그래프에 사이클이 있으면 모든 의존 관계를 만족하는 순서는 존재하지 않습니다.

위상 정렬은 DAG에서만 가능합니다. DAG는 Directed Acyclic Graph, 즉 사이클이 없는 방향 그래프입니다.

## 1. 방향 그래프와 의존 관계

간선 `u -> v`를 "u가 먼저 와야 v를 할 수 있다"라고 해석하겠습니다.

```text
0 -> 2
1 -> 2
2 -> 3
```

가능한 위상 순서 중 하나는 아래와 같습니다.

```text
0, 1, 2, 3
```

`1, 0, 2, 3`도 가능합니다. 위상 정렬 결과는 하나로 고정되지 않을 수 있습니다. 중요한 것은 모든 간선 `u -> v`에 대해 `u`가 `v`보다 앞에 있어야 한다는 조건입니다.

## 2. 진입 차수

진입 차수는 어떤 정점으로 들어오는 간선의 수입니다.

```text
indegree[v] = v를 하기 전에 먼저 끝내야 하는 정점 수
```

진입 차수가 0인 정점은 지금 바로 처리할 수 있습니다. 위상 정렬의 가장 대표적인 알고리즘인 Kahn 알고리즘은 이 성질을 사용합니다.

```text
1. indegree가 0인 정점을 큐에 넣는다.
2. 큐에서 하나를 꺼내 결과 순서에 넣는다.
3. 그 정점에서 나가는 간선을 제거한다고 생각하며 다음 정점의 indegree를 줄인다.
4. 새로 indegree가 0이 된 정점을 큐에 넣는다.
```

## 3. Kahn 알고리즘

아래는 0-indexed 정점 `0`부터 `n - 1`까지를 다루는 구현입니다.

```cpp
#include <queue>
#include <vector>
using namespace std;

vector<int> topologicalSort(int n, const vector<vector<int>>& graph) {
    vector<int> indegree(n, 0);

    for (int u = 0; u < n; ++u) {
        for (int v : graph[u]) {
            indegree[v]++;
        }
    }

    queue<int> q;
    for (int i = 0; i < n; ++i) {
        if (indegree[i] == 0) q.push(i);
    }

    vector<int> order;
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        order.push_back(u);

        for (int v : graph[u]) {
            indegree[v]--;
            if (indegree[v] == 0) {
                q.push(v);
            }
        }
    }

    return order;
}
```

결과 `order`의 길이가 `n`이면 위상 정렬에 성공한 것입니다.

## 4. 사이클 판정

방향 그래프에 사이클이 있으면 모든 정점을 처리할 수 없습니다. 큐가 비었는데 아직 indegree가 남은 정점들이 생깁니다.

```cpp
vector<int> order = topologicalSort(n, graph);

if ((int)order.size() != n) {
    // 사이클이 있다.
}
```

예를 들어 아래 그래프는 순서를 만들 수 없습니다.

```text
0 -> 1
1 -> 2
2 -> 0
```

어떤 정점을 먼저 하려고 해도 다른 정점을 먼저 해야 한다는 조건에 걸립니다.

위상 정렬 문제에서 `order.size() != n` 검사는 거의 필수입니다. 입력이 DAG라고 보장되지 않으면 반드시 확인합니다.

## 5. 여러 답 중 하나 고르기

Kahn 알고리즘에서 큐 대신 우선순위 큐를 쓰면 가능한 정점 중 가장 번호가 작은 정점을 먼저 고를 수 있습니다.

```cpp
#include <functional>
#include <queue>
#include <vector>
using namespace std;

vector<int> lexicographicallySmallestTopo(int n, const vector<vector<int>>& graph) {
    vector<int> indegree(n, 0);
    for (int u = 0; u < n; ++u) {
        for (int v : graph[u]) indegree[v]++;
    }

    priority_queue<int, vector<int>, greater<int>> pq;
    for (int i = 0; i < n; ++i) {
        if (indegree[i] == 0) pq.push(i);
    }

    vector<int> order;
    while (!pq.empty()) {
        int u = pq.top();
        pq.pop();
        order.push_back(u);

        for (int v : graph[u]) {
            indegree[v]--;
            if (indegree[v] == 0) pq.push(v);
        }
    }
    return order;
}
```

가능한 순서 중 사전순으로 가장 작은 결과를 요구하면 이 방식이 필요할 수 있습니다.

## 6. DFS 위상 정렬

DFS로도 위상 정렬을 만들 수 있습니다. 모든 다음 정점을 먼저 방문한 뒤 현재 정점을 결과에 넣고, 마지막에 뒤집습니다.

```cpp
void dfsTopo(
    int u,
    const vector<vector<int>>& graph,
    vector<int>& visited,
    vector<int>& order
) {
    visited[u] = 1;

    for (int v : graph[u]) {
        if (visited[v]) continue;
        dfsTopo(v, graph, visited, order);
    }

    order.push_back(u);
}

vector<int> topoByDfs(int n, const vector<vector<int>>& graph) {
    vector<int> visited(n, 0);
    vector<int> order;

    for (int i = 0; i < n; ++i) {
        if (!visited[i]) dfsTopo(i, graph, visited, order);
    }

    reverse(order.begin(), order.end());
    return order;
}
```

이 구현은 입력이 DAG라고 보장될 때 간단합니다. 사이클까지 판정하려면 방문 상태를 `0, 1, 2`로 나누어야 합니다.

```text
0: 아직 방문 안 함
1: 현재 DFS 경로 안에 있음
2: 처리 완료
```

DFS 중 `state[v] == 1`인 정점을 다시 만나면 사이클입니다.

## 7. DFS로 사이클 찾기

```cpp
bool hasCycleDfs(int u, const vector<vector<int>>& graph, vector<int>& state) {
    state[u] = 1;

    for (int v : graph[u]) {
        if (state[v] == 1) return true;
        if (state[v] == 0 && hasCycleDfs(v, graph, state)) {
            return true;
        }
    }

    state[u] = 2;
    return false;
}

bool hasCycle(int n, const vector<vector<int>>& graph) {
    vector<int> state(n, 0);
    for (int i = 0; i < n; ++i) {
        if (state[i] == 0 && hasCycleDfs(i, graph, state)) {
            return true;
        }
    }
    return false;
}
```

Kahn 알고리즘은 `order.size() != n`으로 사이클을 확인하고, DFS 방식은 현재 recursion stack으로 돌아오는 간선을 확인합니다.

## 8. DAG DP

DAG에서는 위상 순서대로 정점을 처리하면 DP를 안전하게 계산할 수 있습니다. 모든 선행 정점이 먼저 계산되기 때문입니다.

예를 들어 각 간선 `u -> v`를 따라 이동할 수 있을 때, 시작점에서 각 정점까지 가는 최대 점수를 구한다고 하겠습니다.

```cpp
vector<long long> longestPathDag(
    int n,
    const vector<vector<pair<int, int>>>& graph,
    int start
) {
    vector<vector<int>> plain(n);
    for (int u = 0; u < n; ++u) {
        for (auto [v, cost] : graph[u]) {
            plain[u].push_back(v);
        }
    }

    vector<int> order = topologicalSort(n, plain);
    const long long NEG = -(1LL << 60);
    vector<long long> dp(n, NEG);
    dp[start] = 0;

    for (int u : order) {
        if (dp[u] == NEG) continue;

        for (auto [v, cost] : graph[u]) {
            dp[v] = max(dp[v], dp[u] + cost);
        }
    }
    return dp;
}
```

일반 그래프에서 최장 경로는 어렵지만, DAG에서는 위상 순서 덕분에 한 번씩만 relax하면 됩니다.

## 9. 경로 개수 세기

DAG에서 시작점에서 각 정점으로 가는 경로 수를 셀 수도 있습니다.

```cpp
vector<long long> countPathsDag(
    int n,
    const vector<vector<int>>& graph,
    int start
) {
    vector<int> order = topologicalSort(n, graph);
    vector<long long> ways(n, 0);
    ways[start] = 1;

    for (int u : order) {
        for (int v : graph[u]) {
            ways[v] += ways[u];
        }
    }
    return ways;
}
```

경로 수가 커질 수 있으면 문제에서 주어진 mod로 나눕니다.

```cpp
ways[v] = (ways[v] + ways[u]) % MOD;
```

DAG DP는 "의존 관계가 있는 상태 DP"와도 잘 맞습니다. 어떤 상태를 계산하려면 이전 상태들이 먼저 계산되어야 하는데, 그 의존 그래프가 DAG라면 위상 순서대로 처리할 수 있습니다.

## 10. 작업 완료 시간

각 작업에 걸리는 시간이 있고, 선행 작업을 모두 끝내야 다음 작업을 시작할 수 있다고 하겠습니다. 각 작업의 가장 빠른 완료 시간을 구할 수 있습니다.

```cpp
vector<long long> earliestFinish(
    int n,
    const vector<int>& duration,
    const vector<vector<int>>& graph
) {
    vector<int> order = topologicalSort(n, graph);
    vector<long long> finish(n, 0);

    for (int u : order) {
        finish[u] += duration[u];

        for (int v : graph[u]) {
            finish[v] = max(finish[v], finish[u]);
        }
    }
    return finish;
}
```

`finish[v]`는 `v`가 시작하기 전까지 끝나야 하는 선행 작업들의 완료 시간 최댓값을 먼저 모읍니다. 위상 순서대로 처리하므로 선행 작업 정보가 모두 반영된 뒤 `v`가 처리됩니다.

## 11. DAG 최단거리

DAG에서는 음수 간선이 있어도 위상 순서대로 최단거리를 구할 수 있습니다. 사이클이 없기 때문에 음수 사이클 문제가 없습니다.

```cpp
vector<long long> shortestPathDag(
    int n,
    const vector<vector<pair<int, int>>>& graph,
    int start
) {
    vector<vector<int>> plain(n);
    for (int u = 0; u < n; ++u) {
        for (auto [v, cost] : graph[u]) plain[u].push_back(v);
    }

    vector<int> order = topologicalSort(n, plain);
    const long long INF = 1LL << 60;
    vector<long long> dist(n, INF);
    dist[start] = 0;

    for (int u : order) {
        if (dist[u] == INF) continue;

        for (auto [v, cost] : graph[u]) {
            dist[v] = min(dist[v], dist[u] + cost);
        }
    }
    return dist;
}
```

일반 그래프에서 음수 간선이 있으면 Dijkstra를 쓸 수 없지만, DAG라면 위상 순서가 해결해 줍니다.

## 12. 위상 정렬이 아닌 경우

방향이 없거나, 의존 관계가 아니라 단순 연결성만 보는 문제에는 위상 정렬을 쓰지 않습니다.

```text
무방향 연결 요소 -> DFS/BFS 또는 Union-Find
최단거리 -> BFS 또는 Dijkstra
사이클이 있는 방향 그래프의 SCC -> Kosaraju, Tarjan
```

또한 "작업을 임의 순서로 해도 된다"면 위상 정렬이 필요 없습니다. 반드시 선후 관계가 있어야 합니다.

## 13. 시간 복잡도

| 작업 | 시간 |
| --- | --- |
| indegree 계산 | `O(V + E)` |
| Kahn 위상 정렬 | `O(V + E)` |
| DFS 위상 정렬 | `O(V + E)` |
| DAG DP | `O(V + E)` |
| 메모리 | `O(V + E)` |

우선순위 큐로 사전순 가장 작은 위상 순서를 만들면 각 정점 push/pop에 `O(log V)`가 붙어 `O((V + E) log V)` 정도로 보면 됩니다.

## 14. 자주 하는 실수

첫 번째 실수는 간선 방향을 반대로 저장하는 것입니다. `u`를 먼저 해야 `v`를 할 수 있으면 간선은 `u -> v`입니다. 반대로 넣으면 결과가 완전히 달라집니다.

두 번째 실수는 사이클을 확인하지 않는 것입니다. 입력이 DAG라고 보장되지 않으면 `order.size() == n`을 검사해야 합니다.

세 번째 실수는 위상 순서가 유일하다고 가정하는 것입니다. indegree 0인 정점이 여러 개면 여러 답이 가능합니다. 특정 순서를 요구하면 큐 대신 우선순위 큐 같은 tie-break가 필요합니다.

네 번째 실수는 DAG DP에서 초기값을 잘못 두는 것입니다. 도달하지 못한 정점은 `-INF` 또는 `INF`로 둬야 합니다. 0으로 두면 실제로 갈 수 없는 경로가 있는 것처럼 계산될 수 있습니다.

## 15. 문제를 볼 때 체크할 조건

1. 선행 작업, prerequisite, dependency 같은 표현이 있는가?
2. 간선 방향이 "먼저 해야 하는 것 -> 나중에 하는 것"으로 정리되는가?
3. 사이클이 생기면 불가능한 문제인가?
4. 가능한 순서 하나만 필요한가, 사전순/번호순 조건이 있는가?
5. 위상 순서 위에서 최장거리, 최단거리, 경로 수, 완료 시간 같은 DP를 계산해야 하는가?

이 조건들이 보이면 위상 정렬을 먼저 떠올립니다. 단순히 그래프를 모두 방문하는 문제라면 BFS/DFS가 더 맞고, 가중치 최단거리라면 Dijkstra나 DAG 최단거리 조건을 따로 확인합니다.

## 16. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 작업 순서 출력 문제 추가 | indegree 0 정점부터 처리하는 Kahn 알고리즘 구현 | topological order |
| 표준 | TODO: 사이클이면 불가능 판정 문제 추가 | `order.size() == n` 검사 | cycle detection |
| 응용 | TODO: DAG 최장/최단 경로 문제 추가 | 위상 순서 위에서 DP 전이 | DAG DP |
| 함정 | TODO: 사전순 위상 정렬 문제 추가 | 큐 대신 우선순위 큐로 tie-break 처리 | priority queue |
