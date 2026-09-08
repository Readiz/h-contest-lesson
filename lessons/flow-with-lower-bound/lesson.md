# Flow with Lower Bound

Flow with Lower Bound는 각 간선에 `lower <= flow <= upper` 제약이 있는 유량 모델입니다. 일반 Max Flow는 간선마다 `0..capacity`만 생각하지만, lower bound가 있으면 반드시 흘려야 하는 최소량 때문에 feasibility를 먼저 확인해야 합니다.

## 문제 신호

아래 표현이 있으면 lower bound flow를 의심합니다.

| 문제 표현 | Flow 해석 |
| --- | --- |
| 간선마다 최소/최대 통과량이 있다 | lower/upper bound |
| 각 작업은 적어도 L개, 많아도 R개 배정 | source/job/sink bound |
| 수요를 반드시 만족해야 한다 | demand balance |
| 가능한지만 묻는다 | feasible circulation |
| 가능한 상태에서 추가 최대 유량을 묻는다 | feasibility 후 residual max flow |

lower bound가 있는 문제는 "최대 유량을 얼마 보낼 수 있나"보다 "제약을 모두 만족하는 유량이 존재하나"가 먼저입니다.

## Lower bound 제거

간선 `u -> v`에 `lower`와 `upper`가 있다고 합시다.

```text
lower <= flow(u, v) <= upper
```

먼저 `lower`만큼은 이미 보냈다고 생각합니다. 그러면 남은 residual capacity는 `upper - lower`입니다.

이때 정점 balance가 바뀝니다.

```text
u는 lower만큼 내보냈으므로 demand[u] -= lower
v는 lower만큼 받았으므로 demand[v] += lower
```

`demand[x] > 0`이면 최소 유량으로 받은 양이 내보낸 양보다 많으므로, 남은 원래 간선을 통해 그만큼 더 내보내야 합니다. `demand[x] < 0`이면 반대로 더 받아야 합니다. Super 간선은 이 불균형을 원래 간선의 추가 유량으로 해소하도록 연결합니다. 변환의 근거는 [Flows with demands](https://cp-algorithms.com/graph/flow_with_demands.html)에서 확인할 수 있습니다.

## Super source/sink 변환

모든 lower bound를 제거한 뒤, super source `SS`와 super sink `TT`를 추가합니다.

| demand | 추가 간선 |
| ---: | --- |
| `demand[v] > 0` | `SS -> v` capacity `demand[v]` |
| `demand[v] < 0` | `v -> TT` capacity `-demand[v]` |

`SS`에서 나가는 모든 간선을 포화시킬 수 있으면 feasible circulation이 존재합니다.

## Dinic 기반 feasibility 구현

아래 코드는 lower/upper 간선을 추가하고 feasibility를 검사합니다.

```cpp compile-check
#include <algorithm>
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

    bool bfs(int source, int sink) {
        fill(level.begin(), level.end(), -1);
        queue<int> q;
        level[source] = 0;
        q.push(source);
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            for (const Edge& edge : graph[u]) {
                if (edge.cap > 0 && level[edge.to] == -1) {
                    level[edge.to] = level[u] + 1;
                    q.push(edge.to);
                }
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
            long long flow = dfs(edge.to, sink, min(pushed, edge.cap));
            if (flow > 0) {
                edge.cap -= flow;
                graph[edge.to][edge.rev].cap += flow;
                return flow;
            }
        }
        return 0;
    }

    long long maxFlow(int source, int sink) {
        long long result = 0;
        const long long INF = (1LL << 60);
        while (bfs(source, sink)) {
            fill(work.begin(), work.end(), 0);
            while (true) {
                long long pushed = dfs(source, sink, INF);
                if (pushed == 0) {
                    break;
                }
                result += pushed;
            }
        }
        return result;
    }
};

struct LowerBoundFlow {
    int n;
    int superSource;
    int superSink;
    Dinic dinic;
    vector<long long> demand;

    explicit LowerBoundFlow(int n)
        : n(n), superSource(n), superSink(n + 1), dinic(n + 2), demand(n, 0) {}

    void addBoundedEdge(int from, int to, long long lower, long long upper) {
        dinic.addEdge(from, to, upper - lower);
        demand[from] -= lower;
        demand[to] += lower;
    }

    bool feasible() {
        long long required = 0;
        for (int v = 0; v < n; ++v) {
            if (demand[v] > 0) {
                dinic.addEdge(superSource, v, demand[v]);
                required += demand[v];
            } else if (demand[v] < 0) {
                dinic.addEdge(v, superSink, -demand[v]);
            }
        }
        return dinic.maxFlow(superSource, superSink) == required;
    }
};
```

이 구현은 feasibility 판정용입니다. 실제 간선별 flow 값을 복원해야 한다면, 원래 간선의 residual cap을 추적하고 `lower + used`를 계산해야 합니다.

## s-t Flow로 바꾸기

source `s`에서 sink `t`로 lower bound flow를 보내고 싶다면, circulation으로 만들기 위해 `t -> s` 간선을 무한 capacity로 추가합니다.

```text
t -> s, lower = 0, upper = INF
```

이렇게 하면 전체가 순환 구조가 되고, super source/sink 변환으로 feasible 여부를 확인할 수 있습니다. feasible flow를 만든 뒤 추가 최대 유량을 구하려면 super 간선을 제거하고 residual graph에서 `s -> t` max flow를 더 구하는 식으로 확장합니다.

## 모델링 예시

작업 `i`가 최소 `L_i`, 최대 `R_i`개의 사람에게 배정되어야 한다면 `job_i -> sink` 간선에 lower/upper를 둡니다.

```text
source -> worker       [0, 1]
worker -> job          [0, 1] if worker can do job
job -> sink            [L_i, R_i]
sink -> source         [0, INF] for circulation
```

각 job의 최소 수요가 feasibility로 강제됩니다.

## 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| lower 변환 | `O(E)` | demand 배열 |
| super source/sink 추가 | `O(V)` | 간선 `O(V)` |
| feasibility max flow | Dinic 시간 | residual graph |
| 추가 max flow | Dinic 한 번 더 | 변환 후 graph |

전체 병목은 결국 max flow입니다. lower bound 변환 자체는 선형입니다.

## 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| demand 부호를 반대로 둠 | feasibility 반전 | `from -= lower`, `to += lower` |
| capacity를 `upper`로 둠 | lower만큼 중복 허용 | residual cap은 `upper - lower` |
| `t -> s` 간선 누락 | s-t flow feasibility 실패 | circulation 변환 확인 |
| super source 간선 포화 확인 누락 | 불가능 케이스를 가능 처리 | max flow == required |
| lower > upper 입력 처리 누락 | 음수 capacity | 입력 검증 |
| 실제 flow 복원에서 lower 누락 | 출력이 최소량만큼 작음 | `flow = lower + used` |
