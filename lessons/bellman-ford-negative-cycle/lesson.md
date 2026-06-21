# Bellman-Ford와 음수 사이클

Bellman-Ford 알고리즘은 **음수 간선이 있을 수 있는 그래프**에서 한 시작점으로부터 각 정점까지의 최단거리를 구하는 방법입니다. Dijkstra가 "가장 가까운 후보를 확정한다"는 성질에 기대는 반면, Bellman-Ford는 모든 간선을 여러 번 확인하면서 더 짧은 경로를 천천히 전파합니다.

이 레슨의 핵심은 두 가지입니다.

1. 음수 간선이 있어도 최단거리를 계산할 수 있다.
2. 시작점에서 도달 가능한 음수 사이클이 있으면 최단거리가 정의되지 않는 정점이 생긴다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 그래프 표현, 최단거리 배열, Dijkstra 최단거리
- 함께 보면 좋은 레슨: BFS/DFS와 격자 탐색, 위상 정렬과 DAG DP
- 다음에 볼 레슨: SCC와 2-SAT, Flow와 Bipartite Matching

## 1. 언제 Bellman-Ford를 떠올릴까

가중치 그래프 최단거리 문제에서 아래 조건이 보이면 Dijkstra를 바로 쓰면 안 됩니다.

| 조건 | 판단 |
| --- | --- |
| 모든 간선 비용이 0 이상 | Dijkstra 우선 검토 |
| 간선 비용이 0 또는 1뿐 | 0-1 BFS 검토 |
| 음수 간선이 있지만 음수 사이클은 없음 | Bellman-Ford 검토 |
| 음수 사이클 존재 여부를 물음 | Bellman-Ford 검토 |
| 그래프가 DAG | 위상 순서 DP로 음수 간선도 처리 가능 |

음수 간선이 있다는 사실만으로 답이 없는 것은 아닙니다. 문제는 음수 사이클입니다. 사이클을 한 바퀴 돌 때마다 비용이 계속 줄어든다면 최단거리는 더 이상 하나의 값으로 정해지지 않습니다.

## 2. 왜 `V - 1`번 반복할까

음수 사이클이 없는 최단 경로는 같은 정점을 두 번 지날 필요가 없습니다. 같은 정점을 두 번 지난다면 그 사이에는 사이클이 있고, 음수 사이클이 아니라면 제거해도 더 나빠지지 않기 때문입니다.

정점 수가 `V`개이면 단순 경로의 간선 수는 최대 `V - 1`개입니다. 그래서 모든 간선을 한 번 훑는 relax를 최대 `V - 1`번 반복하면, 시작점에서 도달 가능한 최단거리가 모두 전파됩니다.

```text
repeat V - 1 times:
    for each edge u -> v with cost w:
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
```

중간에 아무 거리도 갱신되지 않으면 더 반복해도 달라지지 않으므로 멈출 수 있습니다.

## 3. 작은 예시

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

## 4. 기본 구현

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

`dist[edge.from] == INF`인 간선은 시작점에서 아직 도달할 수 없는 정점에서 출발합니다. 이 간선을 relax하면 안 됩니다. 도달 불가능한 정점의 `INF + cost`를 계산하면 의미 없는 값이 생길 수 있습니다.

## 5. 음수 사이클 판정

`V - 1`번 반복한 뒤에도 어떤 간선을 더 relax할 수 있다면, 시작점에서 도달 가능한 음수 사이클이 있다는 뜻입니다.

```text
after V - 1 relax rounds:
    if any edge can still reduce dist:
        reachable negative cycle exists
```

왜냐하면 음수 사이클이 없다면 최단 경로는 최대 `V - 1`개의 간선만 사용합니다. 그런데 그 이후에도 더 줄어든다면, 같은 정점을 다시 지나는 경로가 더 좋아졌다는 뜻이고, 그 사이클의 총 비용은 음수입니다.

주의할 점은 "그래프 어딘가의 음수 사이클"과 "시작점에서 도달 가능한 음수 사이클"이 다르다는 것입니다. 시작점에서 갈 수 없는 컴포넌트의 음수 사이클은 시작점 기준 최단거리에 영향을 주지 않습니다.

## 6. 음수 사이클의 영향 범위

문제에 따라 음수 사이클이 하나라도 있으면 `YES`를 출력하면 되는 경우가 있고, 특정 정점까지의 최단거리가 영향을 받는지 물을 수도 있습니다.

특정 정점까지의 답이 영향을 받는지 보려면 아래처럼 생각합니다.

1. `V - 1`번 relax 뒤에도 줄어드는 정점을 찾는다.
2. 그 정점들에서 도달 가능한 정점들을 모두 표시한다.
3. 목표 정점이 표시되면 그 목표까지의 최단거리는 정의되지 않는다.

즉, 음수 사이클 자체가 아니라 **음수 사이클에서 목표로 갈 수 있는가**가 중요합니다.

## 7. 시간 복잡도와 한계

Bellman-Ford의 시간 복잡도는 아래와 같습니다.

```text
O(VE)
```

정점과 간선이 모두 크면 매우 느립니다. 예를 들어 `V = 100,000`, `E = 200,000`이면 사용할 수 없습니다. 그래서 음수 간선이 없다는 조건이 보이면 Dijkstra를 써야 하고, 그래프가 DAG라면 위상 순서 DP를 써야 합니다.

SPFA는 큐를 써서 실제로 갱신된 정점 주변만 보는 Bellman-Ford 변형입니다. 평균적으로 빠른 경우도 있지만 최악 시간 복잡도는 여전히 나쁩니다. 문제에서 명시적으로 허용될 만한 제한이 아니라면, SPFA를 만능 대체재처럼 쓰면 위험합니다.

## 8. Dijkstra, DAG 최단거리와 비교

| 상황 | 우선 후보 |
| --- | --- |
| 모든 간선 비용이 1 | BFS |
| 간선 비용이 0 또는 1 | 0-1 BFS |
| 음수 없는 일반 가중치 | Dijkstra |
| DAG | 위상 순서 기반 최단거리 |
| 음수 간선 또는 음수 사이클 판정 | Bellman-Ford |

Bellman-Ford는 "음수 간선 때문에 Dijkstra의 확정 성질이 깨지는 경우"를 받쳐 주는 레슨입니다. 반대로 음수 간선이 없고 입력이 크다면 Bellman-Ford보다 Dijkstra가 자연스럽습니다.

## 9. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 도달 불가능한 정점에서 relax | 가짜 거리 갱신 | `dist[from] == INF`면 건너뛰기 |
| `V`번 본 반복 값을 그대로 답으로 사용 | 음수 사이클 영향을 답으로 착각 | `V - 1`번 뒤 추가 relax는 판정용으로만 사용 |
| 그래프 전체 음수 사이클과 시작점 도달 가능성을 혼동 | 불필요하게 `-INF` 처리 | 시작점에서 도달 가능한지 확인 |
| `int` 거리 사용 | overflow | 거리 합은 `long long` |
| 무방향 음수 간선을 그대로 추가 | 즉시 음수 사이클 생성 | 무방향 간선의 의미와 비용 조건 확인 |
| SPFA를 항상 빠르다고 가정 | 최악 케이스 시간 초과 | 제한을 보고 Bellman-Ford/Dijkstra/DAG를 구분 |

## 10. 문제를 볼 때 체크할 조건

1. 간선 비용에 음수가 있을 수 있는가?
2. 음수 사이클 존재 여부를 묻는가, 최단거리 값을 묻는가?
3. 시작점에서 도달 가능한 음수 사이클만 중요한가?
4. 음수 사이클에서 목표 정점으로 갈 수 있는지까지 확인해야 하는가?
5. `O(VE)`가 입력 제한 안에 들어오는가?
6. 그래프가 DAG라서 더 빠른 위상 순서 풀이가 가능한가?

정리하면, Bellman-Ford는 느리지만 조건이 분명한 알고리즘입니다. 음수 간선과 음수 사이클이 핵심 신호이고, 입력 크기가 작거나 음수 사이클 판정이 필요한 문제에서 우선 검토합니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 음수 간선이 있지만 음수 사이클은 없는 최단거리 문제 추가 | `V - 1`번 relax와 도달 불가능 정점 처리 | relax, INF guard |
| 표준 | TODO: 음수 사이클 존재 판정 문제 추가 | 마지막 추가 relax로 사이클 신호 찾기 | negative cycle |
| 응용 | TODO: 특정 목표가 음수 사이클 영향을 받는지 판정하는 문제 추가 | 사이클 영향 범위 전파 | cycle reachability |
| 함정 | TODO: 음수 간선이 있는 DAG 최단거리 문제 추가 | Bellman-Ford와 위상 순서 DP 선택 비교 | DAG shortest path |
