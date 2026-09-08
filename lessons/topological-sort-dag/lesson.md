# 위상 정렬과 DAG DP

위상 정렬은 방향 그래프에서 모든 간선의 방향을 지키도록 정점을 나열하는 방법입니다.

```text
A를 끝내야 B를 할 수 있다.
B를 끝내야 C를 할 수 있다.
```

이런 의존 관계가 있으면 가능한 작업 순서를 찾아야 합니다. 그래프에 사이클이 있으면 모든 의존 관계를 만족하는 순서는 존재하지 않습니다.

위상 정렬은 DAG에서만 가능합니다. DAG는 Directed Acyclic Graph, 즉 사이클이 없는 방향 그래프입니다.

## 방향 그래프와 의존 관계

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

## 진입 차수

진입 차수는 어떤 정점으로 들어오는 간선의 수입니다.

```text
indegree[v] = v로 들어오는 간선 수 (중복 간선도 각각 센다)
```

진입 차수가 0인 정점은 지금 바로 처리할 수 있습니다. 위상 정렬의 가장 대표적인 알고리즘인 Kahn 알고리즘은 이 성질을 사용합니다.

```text
1. indegree가 0인 정점을 큐에 넣는다.
2. 큐에서 하나를 꺼내 결과 순서에 넣는다.
3. 그 정점에서 나가는 간선을 제거한다고 생각하며 다음 정점의 indegree를 줄인다.
4. 새로 indegree가 0이 된 정점을 큐에 넣는다.
```

## Kahn 알고리즘

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

## 사이클 판정

방향 그래프에 사이클이 있으면 모든 정점을 처리할 수 없습니다. 큐가 비었는데 아직 indegree가 남은 정점들이 생깁니다.

예를 들어 아래 그래프는 순서를 만들 수 없습니다.

```text
0 -> 1
1 -> 2
2 -> 0
```

어떤 정점을 먼저 하려고 해도 다른 정점을 먼저 해야 한다는 조건에 걸립니다.

위상 정렬 문제에서 `order.size() != n` 검사는 거의 필수입니다. 입력이 DAG라고 보장되지 않으면 반드시 확인합니다.

## 순서가 여러 개일 때

사전순으로 가장 작은 순서를 요구하면 큐를 최소 힙으로 바꾸어, 현재 진입 차수가 0인 정점 중 번호가 가장 작은 것을 꺼냅니다. 초기 정점만 정렬해서 큐에 넣는 것으로는 부족합니다. 탐색 중 새로 들어온 더 작은 번호도 다음 선택에 반영해야 하기 때문입니다.

## 작업 완료 시간

각 작업에 걸리는 시간이 있고, 모든 선행 작업이 끝나야 시작할 수 있습니다. 동시에 실행할 수 있는 작업 수에는 제한이 없다고 가정합니다. 위상 순서로 처리하면 선행 작업의 완료 시간이 모두 계산된 뒤 현재 작업을 계산할 수 있습니다. 아래 코드는 입력이 DAG임을 확인한 뒤 사용합니다.

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

앞의 `0→2`, `1→2`, `2→3`에서 작업 시간이 각각 `2, 5, 3, 4`라면 완료 시간은 `2, 5, 8, 12`입니다. 작업 2는 두 선행 작업의 시간 **합** 7이 아니라 마지막으로 끝나는 시각 5부터 시작합니다.

위상 순서를 쓰는 이유는 다른 DAG DP도 같습니다. 경로 수라면 선행 경로 수를 더하고, 최단거리라면 `dist[u] + cost`의 최솟값을 전달합니다. 최단거리에서 도달 불가 상태는 `INF`로 두고 전이하지 않습니다. 사이클이 없어 음수 간선도 처리할 수 있습니다.

## 시간 복잡도

진입 차수 계산, 큐를 쓴 위상 정렬, 위의 작업 시간 DP는 각각 `O(V + E)`입니다. 최소 힙을 쓰면 정점별 삽입·삭제 비용이 붙어 `O(E + V log V)`입니다. 인접 목록과 보조 배열의 메모리는 `O(V + E)`입니다.
