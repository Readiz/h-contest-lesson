# Directed MST

Directed MST는 루트에서 모든 정점으로 도달하는 최소 비용 arborescence를 찾는 문제입니다. 무향 MST와 달리 각 정점은 루트에서 들어오는 경로가 있어야 하고, 루트를 제외한 모든 정점은 정확히 하나의 incoming edge를 선택합니다.

## 문제 신호

| 문제 표현 | Directed MST 관점 |
| --- | --- |
| 한 루트에서 모든 정점으로 방향 간선을 따라 도달 | arborescence |
| 각 정점에 부모 간선을 하나씩 골라야 한다 | incoming edge selection |
| 방향 간선 비용 합 최소 | Chu-Liu/Edmonds |
| 무향 MST를 쓸 수 없다 | edge direction matters |
| 모든 정점이 루트에서 도달 가능해야 한다 | unreachable check |

루트에서 나가는 간선만 보는 최단거리 트리와 다릅니다. Shortest path tree는 각 정점까지의 거리 합을 독립적으로 최소화하지만, directed MST는 선택한 간선들의 총합을 최소화합니다.

## 핵심 Greedy

루트가 아닌 정점 `v`는 arborescence에서 incoming edge가 정확히 하나 필요합니다. 따라서 일단 각 정점에 대해 가장 싼 incoming edge를 고릅니다.

```text
in[v] = min cost edge u -> v
```

선택 결과가 cycle이 없으면 그대로 답입니다. Cycle이 있다면 그 cycle 내부 정점들은 서로 부모를 고른 상태라 루트에서 들어오는 하나의 입구만 결정하면 됩니다. 그래서 cycle을 하나의 super node로 수축합니다.

## Cycle 수축 비용

Cycle 밖에서 cycle 안의 정점 `v`로 들어오는 간선 `u -> v`를 선택한다고 합시다. 이미 `v`에는 `in[v]`가 선택되어 있었으므로, cycle을 깨고 `u -> v`를 새 incoming edge로 바꾸는 추가 비용은:

```text
cost(u -> v) - in[v]
```

그래서 수축 후 간선 비용을 이 값으로 보정합니다. 이 과정을 cycle이 없어질 때까지 반복합니다.

## 구현

아래 구현은 `root`에서 모든 정점으로 도달하는 최소 arborescence 비용을 반환합니다. 불가능하면 `nullopt`를 반환합니다.

```cpp compile-check
#include <algorithm>
#include <limits>
#include <optional>
#include <vector>
using namespace std;

struct DirectedEdge {
    int from;
    int to;
    long long cost;
};

optional<long long> directedMST(int n, int root, vector<DirectedEdge> edges) {
    const long long INF = numeric_limits<long long>::max() / 4;
    long long answer = 0;

    while (true) {
        vector<long long> in(n, INF);
        vector<int> parent(n, -1);

        for (const auto& edge : edges) {
            if (edge.from != edge.to && edge.cost < in[edge.to]) {
                in[edge.to] = edge.cost;
                parent[edge.to] = edge.from;
            }
        }
        in[root] = 0;

        for (int v = 0; v < n; ++v) {
            if (in[v] == INF) {
                return nullopt;
            }
        }

        int cycleCount = 0;
        vector<int> id(n, -1);
        vector<int> visited(n, -1);

        for (int v = 0; v < n; ++v) {
            answer += in[v];
            int current = v;
            while (visited[current] != v && id[current] == -1 && current != root) {
                visited[current] = v;
                current = parent[current];
            }

            if (current != root && id[current] == -1) {
                for (int u = parent[current]; u != current; u = parent[u]) {
                    id[u] = cycleCount;
                }
                id[current] = cycleCount++;
            }
        }

        if (cycleCount == 0) {
            break;
        }

        for (int v = 0; v < n; ++v) {
            if (id[v] == -1) {
                id[v] = cycleCount++;
            }
        }

        vector<DirectedEdge> contracted;
        contracted.reserve(edges.size());
        for (auto edge : edges) {
            int from = id[edge.from];
            int to = id[edge.to];
            if (from != to) {
                contracted.push_back({from, to, edge.cost - in[edge.to]});
            }
        }

        root = id[root];
        n = cycleCount;
        edges.swap(contracted);
    }

    return answer;
}
```

## 최단거리 트리와 비교

| 항목 | Shortest Path Tree | Directed MST |
| --- | --- | --- |
| 목적 | 각 정점까지의 거리 최소 | 선택 간선 총합 최소 |
| 간선 선택 | 정점별 shortest predecessor | 정점별 incoming edge와 cycle 수축 |
| 음수 간선 | Bellman-Ford 필요 | 음수 cost도 가능 |
| 루트 도달성 | 거리 계산으로 확인 | incoming edge 불가능성으로 확인 |

두 구조가 같은 결과를 낼 수는 있지만, 최적화 기준이 다르기 때문에 서로 대체하면 안 됩니다.

## 모델링 포인트

1. 루트는 incoming edge를 선택하지 않는다.
2. 모든 정점이 루트에서 방향 경로로 도달 가능해야 한다.
3. 선택된 간선 수는 `N - 1`개다.
4. 여러 루트 후보가 있으면 super root를 추가하고 root edge 비용을 조절한다.
5. 최대 비용 arborescence는 cost 부호를 뒤집어 처리할 수 있다.

## 시간 복잡도

| 구현 | 복잡도 |
| --- | --- |
| 단순 Chu-Liu/Edmonds | `O(VE)` |
| heap 최적화 | `O(E log V)` 계열 |
| 작은 그래프 bitmask | `O(2^V V^2)` 가능하지만 일반적으로 비권장 |

대부분의 대회 입력에서는 `O(VE)` 구현이 가장 안정적입니다.

## 자주 하는 실수

1. 루트의 incoming edge를 고른다.
2. cycle 수축 후 간선 비용에서 `in[to]`를 빼지 않는다.
3. 도달 불가능 정점을 cycle로 오해한다.
4. self-loop를 제거하지 않아 cycle 판정이 꼬인다.
5. answer에 `in[v]`를 cycle 수축마다 더하는 이유를 잊고 중복 보정한다.
