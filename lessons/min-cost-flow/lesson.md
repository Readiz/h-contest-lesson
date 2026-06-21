# Min-Cost Flow

Min-Cost Flow는 source에서 sink로 유량을 보내되, 보낸 유량의 총 비용을 최소화하는 문제입니다. Max Flow가 "얼마나 많이 보낼 수 있는가"를 묻는다면, Min-Cost Flow는 "정해진 양을 가장 싸게 보낼 수 있는가" 또는 "보낼 수 있는 만큼 보내면서 비용을 최소화할 수 있는가"를 함께 봅니다.

이 레슨은 Max Flow 위에 비용을 붙이는 관점으로 정리합니다.

1. residual graph에 capacity와 cost를 함께 둔다.
2. residual graph에서 가장 싼 augmenting path를 찾는다.
3. assignment, transportation, weighted matching 계열 모델링으로 연결한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Max Flow, residual graph, 최단거리 알고리즘
- 함께 보면 좋은 레슨: Max Flow, Min Cut, Bipartite Matching, Bellman-Ford와 음수 사이클
- 다음에 볼 레슨: matching/cover duality, linear programming duality

## 1. 비용이 붙은 Flow 모델

각 간선 `u -> v`에 capacity와 cost가 함께 있습니다.

| 값 | 의미 |
| --- | --- |
| `cap(u, v)` | 이 간선으로 보낼 수 있는 최대 유량 |
| `cost(u, v)` | 유량 1을 보낼 때 드는 비용 |
| `flow(u, v)` | 실제로 보낸 유량 |

전체 비용은 `sum(flow(u, v) * cost(u, v))`입니다. 보통 아래 중 하나를 묻습니다.

| 요구 | 해석 |
| --- | --- |
| 정확히 `K`만큼 보내는 최소 비용 | `K`번 또는 병목 용량만큼 augment |
| 보낼 수 있는 최대 유량의 최소 비용 | sink가 도달 가능할 때까지 augment |
| 이익을 최대화 | cost를 음수로 두거나 이익을 비용으로 변환 |
| 선택을 서로 겹치지 않게 최소 비용으로 매칭 | assignment flow 모델 |

비용이 음수인 간선이 있을 수 있으므로 단순 Dijkstra를 그대로 쓰기 어렵습니다. 입문 구현에서는 SPFA로 shortest augmenting path를 찾는 방식이 이해하기 쉽습니다.

## 2. Residual cost

Max Flow처럼 유량을 보낸 뒤에는 되돌릴 수 있는 역방향 residual edge가 생깁니다. 비용도 반대로 붙습니다.

```text
forward:  u -> v, cap = 5, cost = 7
reverse:  v -> u, cap = 0, cost = -7
```

`u -> v`로 3을 보냈다면 forward residual capacity는 2가 되고, reverse residual capacity는 3이 됩니다. 나중에 `v -> u` 역방향으로 1을 보내는 것은 이전 선택 1만큼을 취소하는 의미이고, 비용도 `-7`만큼 줄어듭니다.

## 3. Shortest augmenting path 구현

아래 구현은 residual graph에서 비용이 가장 작은 경로를 SPFA로 찾고, 그 경로에 가능한 만큼 유량을 보냅니다. 목표 유량 `requiredFlow`를 넘기 전까지 반복합니다.

```cpp compile-check
#include <algorithm>
#include <limits>
#include <queue>
#include <utility>
#include <vector>
using namespace std;

struct MinCostFlow {
    struct Edge {
        int to;
        int rev;
        long long cap;
        long long cost;
    };

    int n;
    vector<vector<Edge>> graph;

    explicit MinCostFlow(int n) : n(n), graph(n) {}

    void addEdge(int from, int to, long long cap, long long cost) {
        Edge forward{to, (int)graph[to].size(), cap, cost};
        Edge backward{from, (int)graph[from].size(), 0, -cost};
        graph[from].push_back(forward);
        graph[to].push_back(backward);
    }

    pair<long long, long long> minCostFlow(int source, int sink, long long requiredFlow) {
        const long long INF = numeric_limits<long long>::max() / 4;
        long long totalFlow = 0;
        long long totalCost = 0;

        while (totalFlow < requiredFlow) {
            vector<long long> dist(n, INF);
            vector<int> parentNode(n, -1);
            vector<int> parentEdge(n, -1);
            vector<int> inQueue(n, 0);
            queue<int> q;

            dist[source] = 0;
            q.push(source);
            inQueue[source] = 1;

            while (!q.empty()) {
                int u = q.front();
                q.pop();
                inQueue[u] = 0;

                for (int i = 0; i < (int)graph[u].size(); ++i) {
                    const Edge& edge = graph[u][i];
                    if (edge.cap <= 0) {
                        continue;
                    }
                    long long nextDist = dist[u] + edge.cost;
                    if (dist[u] != INF && nextDist < dist[edge.to]) {
                        dist[edge.to] = nextDist;
                        parentNode[edge.to] = u;
                        parentEdge[edge.to] = i;
                        if (!inQueue[edge.to]) {
                            q.push(edge.to);
                            inQueue[edge.to] = 1;
                        }
                    }
                }
            }

            if (dist[sink] == INF) {
                break;
            }

            long long pushed = requiredFlow - totalFlow;
            for (int v = sink; v != source; v = parentNode[v]) {
                int u = parentNode[v];
                int edgeIndex = parentEdge[v];
                pushed = min(pushed, graph[u][edgeIndex].cap);
            }

            for (int v = sink; v != source; v = parentNode[v]) {
                int u = parentNode[v];
                int edgeIndex = parentEdge[v];
                Edge& edge = graph[u][edgeIndex];
                edge.cap -= pushed;
                graph[edge.to][edge.rev].cap += pushed;
            }

            totalFlow += pushed;
            totalCost += pushed * dist[sink];
        }

        return {totalFlow, totalCost};
    }
};
```

반환된 `totalFlow`가 `requiredFlow`보다 작으면 필요한 양을 모두 보낼 수 없다는 뜻입니다. 문제에서 "가능하지 않으면 -1" 같은 처리가 필요할 수 있습니다.

## 4. 모델링 예시: Assignment

작업자 `N`명과 일 `M`개가 있고, 한 작업자는 최대 하나의 일을 맡고 각 일도 최대 한 명에게 배정된다고 합시다. 작업자 `i`가 일 `j`를 하면 비용 `c[i][j]`가 듭니다.

```text
source -> worker i      capacity 1, cost 0
worker i -> job j       capacity 1, cost c[i][j]
job j -> sink           capacity 1, cost 0
```

정확히 `K`개의 일을 배정하고 싶으면 `requiredFlow = K`로 둡니다. 모든 작업자와 모든 일이 반드시 매칭되어야 하면 `K = N = M`이어야 하고, `totalFlow`가 `K`에 못 미치면 불가능입니다.

이익 최대화 문제는 비용을 `-profit`으로 두고 최소 비용을 구하면 됩니다. 다만 음수 비용이 커질 수 있으므로 `long long`을 쓰는 편이 안전합니다.

## 5. Potential을 쓰는 최적화

SPFA 기반 구현은 이해하기 쉽지만 큰 입력에서는 느릴 수 있습니다. 비용 간선이 많고 augment 횟수가 크면 Johnson potential을 써서 reduced cost를 음수가 아니게 만들고 Dijkstra로 최단 경로를 찾는 구현을 씁니다.

| 방식 | 장점 | 주의점 |
| --- | --- | --- |
| SPFA shortest augmenting path | 구현이 짧고 음수 비용을 직접 처리 | 최악 성능이 나쁠 수 있음 |
| Potential + Dijkstra | 큰 그래프에서 안정적 | 초기 potential, reduced cost 갱신 필요 |
| Cycle canceling | 이론적으로 직관적 | 대회 구현으로는 드묾 |

문제 제한이 작거나 유량이 작으면 SPFA로 충분한 경우가 많습니다. 제한이 수만 간선 이상이고 많은 유량을 보내야 하면 potential 구현을 검토합니다.

## 6. 시간 복잡도

SPFA shortest augmenting path 구현은 augment 횟수를 `F`, 정점 수를 `V`, 간선 수를 `E`라고 할 때 대략 `O(F * V * E)`로 생각하면 됩니다. 실제로는 더 빠르게 도는 경우도 많지만, 최악을 믿고 큰 입력에 쓰면 위험합니다.

| 작업 | 시간 |
| --- | ---: |
| 간선 추가 | `O(1)` |
| SPFA 한 번 | 최악 `O(VE)` |
| `F`번 augment | 최악 `O(FVE)` |
| Potential + Dijkstra 한 번 | `O(E log V)` 수준 |

capacity가 크더라도 한 번에 경로의 병목만큼 보내므로 augment 횟수는 보낸 유량 값보다 작을 수 있습니다. 하지만 모든 간선 capacity가 1이면 보낸 유량 횟수만큼 반복합니다.

## 7. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 역방향 간선 cost를 `-cost`로 두지 않음 | 이전 선택을 취소할 때 비용이 깨짐 | forward/reverse pair 확인 |
| 필요한 유량을 다 못 보냈는데 비용만 출력 | 불가능 케이스 오답 | `totalFlow == requiredFlow` 확인 |
| 이익 최대화에서 부호를 반대로 둠 | 최소 이익 선택 | `cost = -profit`인지 확인 |
| capacity 1 모델링을 빠뜨림 | 한 작업자나 일이 여러 번 선택됨 | source/job/sink capacity 확인 |
| `int` 비용 사용 | 비용 합 overflow | `flow * dist`는 `long long` |
| 큰 입력에 SPFA만 사용 | 시간 초과 | potential + Dijkstra 검토 |

## 8. 문제를 볼 때 체크할 조건

1. 최대 유량뿐 아니라 비용/이익 최적화가 필요한가?
2. 정확히 몇 단위의 유량을 보내야 하는가?
3. 각 선택이 한 번만 가능한가, capacity가 여러 개인가?
4. 음수 비용이나 이익 최대화가 섞여 있는가?
5. 입력 크기가 SPFA 구현으로 감당 가능한가?
6. 불가능할 때 어떤 출력을 해야 하는가?

Min-Cost Flow는 "선택의 개수 제한"과 "선택 비용"이 동시에 있는 문제를 그래프로 바꾸는 도구입니다. 먼저 Max Flow 모델을 만들고, 선택 간선에 비용을 붙인 뒤 필요한 유량을 명시하면 모델링이 단순해집니다.

## 9. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 정해진 유량의 최소 비용 `/practice/...` 문제 필요 | residual cost와 역방향 비용 구현 | shortest augmenting path |
| 표준 | TODO: assignment 모델링 `/practice/...` 문제 필요 | worker-job-sink capacity 1 모델 | assignment |
| 응용 | TODO: 이익 최대화 매칭 `/practice/...` 문제 필요 | profit을 음수 cost로 변환 | negative cost |
| 함정 | TODO: 불가능한 요구 유량 `/practice/...` 문제 필요 | `totalFlow == requiredFlow` 확인 | infeasible flow |
