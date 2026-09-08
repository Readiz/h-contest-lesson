# Max Flow, Min Cut, Bipartite Matching

Max Flow는 방향 그래프에서 source에서 sink로 보낼 수 있는 최대 유량을 구하는 문제입니다. 각 간선에는 용량(capacity)이 있고, 한 간선으로 보낼 수 있는 유량은 그 용량을 넘을 수 없습니다.

## Flow 모델

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

## Residual graph

유량을 보낸 뒤에도 "얼마나 더 보낼 수 있는가"를 나타내는 그래프가 residual graph입니다.

간선 `u -> v`에 용량 5가 있고 현재 3을 보냈다면, 앞으로 `u -> v`로 2를 더 보낼 수 있습니다. 동시에 보낸 유량을 취소하는 의미로 `v -> u` 방향에 3의 residual capacity가 생깁니다.

```text
capacity u -> v = 5
current flow u -> v = 3

residual u -> v = 2
residual v -> u = 3
```

역방향 간선은 실수처럼 보이지만 핵심입니다. 나중에 더 좋은 경로를 찾으면 이전 선택을 일부 되돌리고 다른 방향으로 유량을 재배치할 수 있습니다.

## Dinic 알고리즘

Dinic은 Max Flow의 대표적인 구현입니다.

1. BFS로 residual graph의 level graph를 만든다.
2. DFS로 level이 1씩 증가하는 간선만 따라 blocking flow를 보낸다.
3. 더 이상 `S`에서 `T`로 갈 수 없을 때 종료한다.

BFS level은 "현재 residual graph에서 source에서 각 정점까지의 shortest edge count 구조"를 만듭니다. DFS는 그 구조 위에서 더 보낼 수 있는 유량을 여러 번 흘립니다.

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
        Edge forward{to, (int)graph[to].size() + (from == to ? 1 : 0), cap};
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

## Min Cut

Cut은 정점 집합을 source 쪽 `A`와 sink 쪽 `B`로 나누는 것입니다. `S`는 `A`, `T`는 `B`에 있어야 합니다. Cut의 용량은 `A`에서 `B`로 나가는 간선 용량의 합입니다.

Max-flow min-cut theorem은 아래를 말합니다.

```text
maximum flow value = minimum cut capacity
```

Dinic이 끝난 뒤 residual graph에서 source로부터 아직 도달 가능한 정점들을 표시하면, 그 집합이 min cut의 source 쪽입니다. 원래 그래프에서 `reachable[u] == true`, `reachable[v] == false`인 간선 `u -> v`들이 cut 경계가 됩니다.

위 `maxFlow`가 종료할 때 마지막 BFS의 `level[v] != -1`인 정점이 source 쪽 집합입니다. 별도 BFS를 복제할 필요가 없습니다. cut 용량은 이 집합에서 바깥으로 나가는 **원래 용량**을 합하므로 원본 간선 목록은 보관합니다.

## Bipartite Matching으로 바꾸기

이분 그래프에서 왼쪽 정점과 오른쪽 정점을 겹치지 않게 최대한 많이 짝짓는 문제가 bipartite matching입니다. 이것은 Max Flow로 바꿀 수 있습니다.

```text
source -> left nodes      capacity 1
left -> right edges       capacity 1
right nodes -> sink       capacity 1
```

모든 간선 용량을 1로 두면, 한 왼쪽 정점은 최대 한 번만 선택되고 한 오른쪽 정점도 최대 한 번만 선택됩니다. 최대 유량 값이 최대 매칭 크기입니다.

이 모델은 이해하기 쉽고 다른 capacity 제약을 섞기 좋습니다. 다만 순수 이분 매칭만 매우 크게 풀 때는 Hopcroft-Karp가 더 직접적일 수 있습니다.

## 모델링 신호

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

## 시간 복잡도와 선택 기준

일반 그래프에서 시간은 `O(V²E)`, 메모리는 `O(V + E)`입니다. 위의 용량 1 이분 매칭 네트워크에서는 `O(E sqrt(V))`를 얻습니다. [Dinic 시간 분석](https://cp-algorithms.com/graph/dinic.html)을 참고합니다.

`source != sink`, 용량은 음이 아닌 정수이며 총유량이 `long long` 범위 안이어야 합니다. DFS 재귀 깊이는 최대 `V`입니다. 무향 용량 간선은 필요한 두 방향을 각각 추가합니다.
