# Max Flow, Min Cut, Bipartite Matching

Max Flow는 방향 그래프에서 source에서 sink로 보낼 수 있는 최대 유량을 구하는 문제입니다. 각 간선에는 용량(capacity)이 있고, 한 간선으로 보낼 수 있는 유량은 그 용량을 넘을 수 없습니다.

이 레슨은 Max Flow를 하나의 독립 알고리즘으로만 보지 않고, 아래 세 가지 관점으로 연결합니다.

1. source에서 sink까지 최대한 많이 보낸다.
2. 더 이상 보낼 수 없을 때 source 쪽과 sink 쪽을 가르는 최소 cut을 찾는다.
3. 이분 매칭을 source-left-right-sink flow 모델로 바꾼다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: BFS, 그래프 표현, residual graph, SCC와 2-SAT 수준의 방향 그래프 감각
- 함께 보면 좋은 레슨: 그래프와 트리 기본 성질, 우선순위 큐와 힙
- 다음에 볼 레슨: Min-Cost Flow, Hopcroft-Karp, matching/cover duality

## 1. Flow 모델

Flow 문제의 입력은 보통 아래처럼 해석합니다.

| 구성 | 의미 |
| --- | --- |
| source `S` | 유량이 시작되는 정점 |
| sink `T` | 유량이 도착해야 하는 정점 |
| capacity `c(u, v)` | 간선 `u -> v`로 보낼 수 있는 최대 유량 |
| flow `f(u, v)` | 실제로 보내는 유량 |

유량은 두 조건을 만족해야 합니다.

1. capacity 제한: `0 <= f(u, v) <= c(u, v)`
2. flow conservation: `S`, `T`를 제외한 정점에서는 들어온 유량과 나간 유량이 같다.

Max Flow는 이 조건을 만족하면서 `S`에서 `T`로 들어가는 총 유량을 최대화합니다.

## 2. Residual graph

유량을 보낸 뒤에도 "얼마나 더 보낼 수 있는가"를 나타내는 그래프가 residual graph입니다.

간선 `u -> v`에 용량 5가 있고 현재 3을 보냈다면, 앞으로 `u -> v`로 2를 더 보낼 수 있습니다. 동시에 보낸 유량을 취소하는 의미로 `v -> u` 방향에 3의 residual capacity가 생깁니다.

```text
capacity u -> v = 5
current flow u -> v = 3

residual u -> v = 2
residual v -> u = 3
```

역방향 간선은 실수처럼 보이지만 핵심입니다. 나중에 더 좋은 경로를 찾으면 이전 선택을 일부 되돌리고 다른 방향으로 유량을 재배치할 수 있습니다.

## 3. Dinic 알고리즘

Dinic은 Max Flow의 대표적인 구현입니다.

1. BFS로 residual graph의 level graph를 만든다.
2. DFS로 level이 1씩 증가하는 간선만 따라 blocking flow를 보낸다.
3. 더 이상 `S`에서 `T`로 갈 수 없을 때 종료한다.

BFS level은 "현재 residual graph에서 sink까지 가는 shortest edge count 구조"를 만듭니다. DFS는 그 구조 위에서 더 보낼 수 있는 유량을 여러 번 흘립니다.

```cpp compile-check
#include <algorithm>
#include <limits>
#include <queue>
#include <vector>
using namespace std;

struct Dinic {
    struct Edge {
        int to;
        int rev;
        long long cap;
    };

    int n;
    vector<vector<Edge>> graph;
    vector<int> level;
    vector<int> work;

    explicit Dinic(int n) : n(n), graph(n), level(n), work(n) {}

    void addEdge(int from, int to, long long cap) {
        Edge forward{to, (int)graph[to].size(), cap};
        Edge backward{from, (int)graph[from].size(), 0};
        graph[from].push_back(forward);
        graph[to].push_back(backward);
    }

    bool buildLevelGraph(int source, int sink) {
        fill(level.begin(), level.end(), -1);
        queue<int> q;
        level[source] = 0;
        q.push(source);

        while (!q.empty()) {
            int u = q.front();
            q.pop();
            for (const Edge& edge : graph[u]) {
                if (edge.cap <= 0 || level[edge.to] != -1) {
                    continue;
                }
                level[edge.to] = level[u] + 1;
                q.push(edge.to);
            }
        }
        return level[sink] != -1;
    }

    long long dfs(int u, int sink, long long pushed) {
        if (u == sink) {
            return pushed;
        }
        for (int& i = work[u]; i < (int)graph[u].size(); ++i) {
            Edge& edge = graph[u][i];
            if (edge.cap <= 0 || level[edge.to] != level[u] + 1) {
                continue;
            }
            long long sent = dfs(edge.to, sink, min(pushed, edge.cap));
            if (sent == 0) {
                continue;
            }
            edge.cap -= sent;
            graph[edge.to][edge.rev].cap += sent;
            return sent;
        }
        return 0;
    }

    long long maxFlow(int source, int sink) {
        const long long INF = numeric_limits<long long>::max() / 4;
        long long flow = 0;
        while (buildLevelGraph(source, sink)) {
            fill(work.begin(), work.end(), 0);
            while (true) {
                long long pushed = dfs(source, sink, INF);
                if (pushed == 0) {
                    break;
                }
                flow += pushed;
            }
        }
        return flow;
    }
};
```

`work[u]`는 DFS가 이미 막힌 간선을 다시 보지 않도록 하는 포인터입니다. 이 최적화가 없으면 같은 level graph 안에서 불필요한 재탐색이 많이 생깁니다.

## 4. Min Cut

Cut은 정점 집합을 source 쪽 `A`와 sink 쪽 `B`로 나누는 것입니다. `S`는 `A`, `T`는 `B`에 있어야 합니다. Cut의 용량은 `A`에서 `B`로 나가는 간선 용량의 합입니다.

Max-flow min-cut theorem은 아래를 말합니다.

```text
maximum flow value = minimum cut capacity
```

Dinic이 끝난 뒤 residual graph에서 source로부터 아직 도달 가능한 정점들을 표시하면, 그 집합이 min cut의 source 쪽입니다. 원래 그래프에서 `reachable[u] == true`, `reachable[v] == false`인 간선 `u -> v`들이 cut 경계가 됩니다.

```cpp compile-check
#include <queue>
#include <vector>
using namespace std;

struct ResidualEdge {
    int to;
    long long cap;
};

vector<int> reachableInResidual(const vector<vector<ResidualEdge>>& graph, int source) {
    vector<int> reachable(graph.size(), 0);
    queue<int> q;
    reachable[source] = 1;
    q.push(source);

    while (!q.empty()) {
        int u = q.front();
        q.pop();
        for (const ResidualEdge& edge : graph[u]) {
            if (edge.cap <= 0 || reachable[edge.to]) {
                continue;
            }
            reachable[edge.to] = 1;
            q.push(edge.to);
        }
    }
    return reachable;
}
```

실제 구현에서는 Dinic의 residual graph를 그대로 탐색하면 됩니다. 단, cut 용량을 다시 계산하려면 원래 간선 용량도 따로 보관해야 합니다.

## 5. Bipartite Matching으로 바꾸기

이분 그래프에서 왼쪽 정점과 오른쪽 정점을 겹치지 않게 최대한 많이 짝짓는 문제가 bipartite matching입니다. 이것은 Max Flow로 바꿀 수 있습니다.

```text
source -> left nodes      capacity 1
left -> right edges       capacity 1
right nodes -> sink       capacity 1
```

모든 간선 용량을 1로 두면, 한 왼쪽 정점은 최대 한 번만 선택되고 한 오른쪽 정점도 최대 한 번만 선택됩니다. 최대 유량 값이 최대 매칭 크기입니다.

이 모델은 이해하기 쉽고 다른 capacity 제약을 섞기 좋습니다. 다만 순수 이분 매칭만 매우 크게 풀 때는 Hopcroft-Karp가 더 직접적일 수 있습니다.

## 6. 모델링 신호

아래 문장이 보이면 flow 모델을 의심합니다.

| 문제 표현 | Flow 해석 |
| --- | --- |
| 여러 경로로 자원을 보내야 한다 | Max Flow |
| 간선/정점마다 처리 가능량이 있다 | capacity |
| 최소로 끊어서 source와 sink를 분리한다 | Min Cut |
| 왼쪽 그룹과 오른쪽 그룹을 최대한 매칭한다 | Bipartite Matching |
| 정점 자체에 용량이 있다 | 정점을 in/out으로 쪼개기 |
| 각 선택을 한 번만 사용할 수 있다 | capacity 1 |

정점 용량은 `v_in -> v_out` 간선을 만들고 그 간선에 capacity를 걸어 처리합니다. 원래 들어오는 간선은 `v_in`으로, 나가는 간선은 `v_out`에서 시작하게 바꿉니다.

## 7. 시간 복잡도와 선택 기준

Dinic의 일반적인 최악 시간 복잡도는 그래프 형태에 따라 다르게 설명됩니다. 대회 입문 단계에서는 아래처럼 판단하면 충분합니다.

| 상황 | 감각 |
| --- | --- |
| 정점/간선이 수천~수만 규모 | Dinic 우선 검토 |
| 모든 용량이 1인 이분 매칭 | Dinic 또는 Hopcroft-Karp |
| 비용까지 최소화해야 함 | Min-Cost Flow 필요 |
| source/sink 분리 최소 비용 | Max Flow 후 Min Cut 해석 |

Flow는 상수가 큰 편입니다. 입력 제한이 크고 문제 구조가 순수 이분 매칭이면 전용 알고리즘을 고려합니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 역방향 간선을 만들지 않음 | 이전 선택을 취소하지 못함 | forward/reverse edge pair 유지 |
| reverse index를 잘못 저장 | residual graph 손상 | `rev`가 상대 adjacency 위치를 가리키는지 확인 |
| 정점 용량을 간선 용량처럼 처리 | 같은 정점이 여러 번 사용됨 | `in/out` split 사용 |
| 무방향 간선을 한 방향만 추가 | 가능한 경로 누락 | 문제의 간선 방향 확인 |
| `int` capacity 사용 | 큰 유량 overflow | capacity와 flow는 `long long` 검토 |
| min cut을 원래 그래프가 아니라 residual capacity로 계산 | cut 간선 누락 | reachable은 residual, cut 용량은 원래 capacity 기준 |
| 매칭에서 capacity를 1로 두지 않음 | 한 정점이 여러 번 매칭 | source/left/right/sink capacity 확인 |

## 9. 문제를 볼 때 체크할 조건

1. source와 sink가 자연스럽게 보이는가?
2. 간선 또는 정점마다 최대 사용량이 있는가?
3. 최대 개수/최대 양을 보내는 문제인가?
4. source와 sink를 분리하는 최소 비용 문제인가?
5. 이분 그래프의 최대 매칭으로 해석할 수 있는가?
6. 비용 최적화가 함께 있으면 Min-Cost Flow가 필요한가?

정리하면, Max Flow는 "용량이 있는 이동"을 모델링하는 도구입니다. Min Cut은 max flow가 끝난 뒤 residual graph에서 읽어 내는 dual 해석이고, Bipartite Matching은 capacity 1 flow의 대표 응용입니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: source에서 sink까지 최대 유량을 구하는 문제 추가 | Dinic level graph와 residual edge 구현 | max flow, residual graph |
| 표준 | TODO: 이분 그래프 최대 매칭 문제 추가 | source-left-right-sink 모델링 | bipartite matching |
| 응용 | TODO: 정점 용량이 있는 경로 선택 문제 추가 | vertex split으로 capacity 표현 | node capacity |
| 함정 | TODO: min cut 간선을 출력하는 문제 추가 | residual reachable과 원래 capacity 구분 | min cut |
