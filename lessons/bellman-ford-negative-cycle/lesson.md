# Bellman-Ford와 음수 사이클

Bellman-Ford 알고리즘은 **음수 간선이 있을 수 있는 그래프**에서 한 시작점으로부터 각 정점까지의 최단거리를 구하는 방법입니다. Dijkstra가 "가장 가까운 후보를 확정한다"는 성질에 기대는 반면, Bellman-Ford는 모든 간선을 여러 번 확인하면서 더 짧은 경로를 천천히 전파합니다.

## 언제 Bellman-Ford를 떠올릴까

가중치 그래프 최단거리 문제에서 아래 조건이 보이면 Dijkstra를 바로 쓰면 안 됩니다.

| 조건 | 판단 |
| --- | --- |
| 모든 간선 비용이 0 이상 | Dijkstra 우선 검토 |
| 간선 비용이 0 또는 1뿐 | 0-1 BFS 검토 |
| 음수 간선이 있지만 음수 사이클은 없음 | Bellman-Ford 검토 |
| 음수 사이클 존재 여부를 물음 | Bellman-Ford 검토 |
| 그래프가 DAG | 위상 순서 DP로 음수 간선도 처리 가능 |

음수 간선이 있다는 사실만으로 답이 없는 것은 아닙니다. 문제는 음수 사이클입니다. 사이클을 한 바퀴 돌 때마다 비용이 계속 줄어든다면 최단거리는 더 이상 하나의 값으로 정해지지 않습니다.

## 왜 `V - 1`번 반복할까

음수 사이클이 없는 최단 경로는 같은 정점을 두 번 지날 필요가 없습니다. 같은 정점을 두 번 지난다면 그 사이에는 사이클이 있고, 음수 사이클이 아니라면 제거해도 더 나빠지지 않기 때문입니다.

정점 수가 `V`개이면 단순 경로의 간선 수는 최대 `V - 1`개입니다. 그래서 모든 간선을 한 번 훑는 relax를 최대 `V - 1`번 반복하면, 시작점에서 도달 가능한 최단거리가 모두 전파됩니다.

```text
repeat V - 1 times:
    for each edge u -> v with cost w:
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
```

중간에 아무 거리도 갱신되지 않으면 더 반복해도 달라지지 않으므로 멈출 수 있습니다.

## 작은 예시

아래 그래프에서 시작점이 `0`이라고 해 봅시다.

```text
0 -> 1 비용 4
0 -> 2 비용 5
1 -> 2 비용 -3
2 -> 3 비용 2
```

처음에는 `dist = [0, INF, INF, INF]`입니다.

| 반복 | 갱신 결과 |
| --- | --- |
| 1회차 | `0 -> 1`, `0 -> 2`, `1 -> 2`, `2 -> 3`이 차례로 반영되어 `[0, 4, 1, 3]` |
| 2회차 | 더 짧은 경로 없음 |

음수 간선 `1 -> 2`가 있어도 문제는 없습니다. 사이클을 돌며 계속 줄어드는 구조가 없기 때문입니다.

## 기본 구현

Bellman-Ford는 인접 리스트보다 간선 목록으로 구현하면 가장 단순합니다. 매 반복마다 모든 간선을 확인하기 때문입니다.

```cpp compile-check
#include <limits>
#include <vector>
using namespace std;

const long long INF = numeric_limits<long long>::max() / 4;

struct Edge {
    int from;
    int to;
    long long cost;
};

struct BellmanFordResult {
    vector<long long> dist;
    vector<int> parent;
    bool hasReachableNegativeCycle;
};

BellmanFordResult bellmanFord(int n, const vector<Edge>& edges, int start) {
    vector<long long> dist(n, INF);
    vector<int> parent(n, -1);
    dist[start] = 0;

    for (int iter = 0; iter < n - 1; ++iter) {
        bool changed = false;
        for (const Edge& edge : edges) {
            if (dist[edge.from] == INF) {
                continue;
            }
            long long nextDist = dist[edge.from] + edge.cost;
            if (nextDist < dist[edge.to]) {
                dist[edge.to] = nextDist;
                parent[edge.to] = edge.from;
                changed = true;
            }
        }
        if (!changed) {
            break;
        }
    }

    bool hasReachableNegativeCycle = false;
    for (const Edge& edge : edges) {
        if (dist[edge.from] == INF) {
            continue;
        }
        if (dist[edge.from] + edge.cost < dist[edge.to]) {
            hasReachableNegativeCycle = true;
            break;
        }
    }

    return {dist, parent, hasReachableNegativeCycle};
}
```

`dist[edge.from] == INF`인 간선은 시작점에서 아직 도달할 수 없는 정점에서 출발합니다. 이 간선을 relax하면 안 됩니다. 도달 불가능한 정점의 `INF + cost`를 계산하면 의미 없는 값이 생길 수 있습니다. 도달 가능한 거리의 합도 `long long` 범위 안인지 입력 상한으로 계산합니다.

## 음수 사이클 판정

`V - 1`번 반복한 뒤에도 어떤 간선을 더 relax할 수 있다면, 시작점에서 도달 가능한 음수 사이클이 있다는 뜻입니다.

```text
after V - 1 relax rounds:
    if any edge can still reduce dist:
        reachable negative cycle exists
```

왜냐하면 음수 사이클이 없다면 최단 경로는 최대 `V - 1`개의 간선만 사용합니다. 그런데 그 이후에도 더 줄어든다면, 같은 정점을 다시 지나는 경로가 더 좋아졌다는 뜻이고, 그 사이클의 총 비용은 음수입니다.

주의할 점은 "그래프 어딘가의 음수 사이클"과 "시작점에서 도달 가능한 음수 사이클"이 다르다는 것입니다. 시작점에서 갈 수 없는 컴포넌트의 음수 사이클은 시작점 기준 최단거리에 영향을 주지 않습니다. 추가 relax는 사이클 판정용이며, 그때 얻은 값을 최단거리 답으로 쓰지 않습니다.

무방향 음수 간선을 양방향으로 넣으면 왕복만으로 음수 사이클이 됩니다.

## 음수 사이클의 영향 범위

문제에 따라 음수 사이클이 하나라도 있으면 `YES`를 출력하면 되는 경우가 있고, 특정 정점까지의 최단거리가 영향을 받는지 물을 수도 있습니다.

특정 정점까지의 답이 영향을 받는지 보려면 아래처럼 생각합니다.

1. `V - 1`번 relax 뒤에도 줄어드는 정점을 찾는다.
2. 그 정점들에서 도달 가능한 정점들을 모두 표시한다.
3. 목표 정점이 표시되면 그 목표까지의 최단거리는 정의되지 않는다.

즉, 음수 사이클 자체가 아니라 **음수 사이클에서 목표로 갈 수 있는가**가 중요합니다.

## 시간 복잡도와 한계

Bellman-Ford의 시간 복잡도는 아래와 같습니다.

```text
O(VE)
```

정점과 간선이 모두 크면 매우 느립니다. 예를 들어 `V = 100,000`, `E = 200,000`이면 사용할 수 없습니다. 그래서 음수 간선이 없다는 조건이 보이면 Dijkstra를 써야 하고, 그래프가 DAG라면 위상 순서 DP를 써야 합니다.

SPFA는 큐를 써서 실제로 갱신된 정점 주변만 보는 Bellman-Ford 변형입니다. 평균적으로 빠른 경우도 있지만 최악 시간 복잡도는 여전히 나쁩니다. 문제에서 명시적으로 허용될 만한 제한이 아니라면, SPFA를 만능 대체재처럼 쓰면 위험합니다.
