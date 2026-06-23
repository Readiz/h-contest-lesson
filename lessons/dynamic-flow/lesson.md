# Dynamic Flow

Dynamic Flow는 간선 용량, 비용, 활성 상태, 시간 단계가 바뀌는 상황에서 flow 값을 매번 처음부터 계산하지 않도록 모델링하는 주제입니다. 완전한 online dynamic max flow는 매우 어렵지만, 대회에서는 residual graph 재사용, 시간 확장 네트워크, batch rebuild, offline interval 처리처럼 제한된 형태로 자주 나타납니다.

이 레슨은 Max Flow, Min-Cost Flow, Dynamic Connectivity 이후에 보는 그래프 최적화 심화입니다.

1. 어떤 변화가 flow 보존 조건을 깨는지 먼저 구분한다.
2. capacity 증가처럼 쉬운 변화는 residual graph에서 추가 augment만 한다.
3. 시간축이 명시되면 dynamic update보다 time-expanded network로 바꾸는 편이 안전하다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Max Flow, Min-Cost Flow, residual graph, cut capacity
- 함께 보면 좋은 레슨: Flow with Lower Bound, Dynamic Connectivity, Rollback Techniques
- 다음에 볼 레슨: incremental flow, parametric cut, time-expanded network modeling

## 1. 문제 신호

| 문제 표현 | Dynamic Flow 관점 |
| --- | --- |
| 간선 용량이 계속 증가한다 | residual graph에서 추가 augment |
| 간선이 삭제되거나 용량이 줄어든다 | 기존 flow를 되돌리거나 rebuild 필요 |
| 시간마다 이동 가능 간선이 다르다 | time-expanded network |
| 같은 네트워크에 source/sink query가 많다 | cut reuse 또는 batch rebuild |
| flow 값이 임계값 이상인지 반복해서 묻는다 | parametric feasibility |

flow는 단순 connectivity보다 상태가 무겁습니다. 간선 하나가 바뀌어도 모든 flow conservation 제약이 영향을 받을 수 있으므로, update 종류를 좁히지 않으면 안정적인 구현을 만들기 어렵습니다.

## 2. Static Flow와 무엇이 다른가

정적 max flow는 residual graph에서 augmenting path를 더 이상 찾을 수 없으면 끝납니다. Dynamic Flow에서는 이미 구한 residual graph가 다음 query의 출발점이 됩니다.

```text
old network + old flow
update edge capacity
repair feasibility if needed
augment or rebuild
```

capacity 증가와 source/sink가 그대로인 경우에는 기존 flow가 여전히 feasible합니다. 그래서 추가로 열린 residual capacity만 이용해 더 augment하면 됩니다. 반대로 capacity 감소나 edge deletion은 기존 flow가 그 edge를 쓰고 있었을 수 있어 feasibility repair가 먼저 필요합니다.

## 3. Update 종류별 난이도

| update | 기존 flow feasible? | 실전 접근 |
| --- | --- | --- |
| capacity increase | 유지됨 | residual에서 추가 augment |
| new edge insert | 유지됨 | 새 residual edge 추가 후 augment |
| capacity decrease | 깨질 수 있음 | 사용 flow 초과분을 되돌리거나 rebuild |
| edge delete | 깨질 수 있음 | tree/cut 관점보다 rebuild가 안전 |
| source/sink change | 대부분 재사용 어려움 | query batch나 Gomory-Hu류 검토 |

문제가 capacity 증가만 허용하는지, deletion이 섞이는지를 먼저 봅니다. 이 한 줄 조건이 풀이 난도를 크게 바꿉니다.

## 4. Time-Expanded Network

시간 단계가 작거나 이동 시간이 명시되면 update를 직접 처리하지 않고 정적인 큰 네트워크로 바꿀 수 있습니다.

```text
node(time, vertex)
wait edge: node(t, v) -> node(t+1, v)
move edge: node(t, u) -> node(t+1, v)
```

이 모델은 "시간 t에 어떤 간선이 활성인지"를 정적 edge 집합으로 펼칩니다. 최단 시간 evacuation, 시간표가 있는 이동, 라운드별 capacity 제한 문제에서 특히 자연스럽습니다.

## 5. Time Expansion 구현 조각

아래 코드는 시간 구간 `[start, end)` 동안 활성인 directed edge를 시간 확장 네트워크의 간선 목록으로 바꿉니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct DynamicArc {
    int from = 0;
    int to = 0;
    int start = 0;
    int end = 0;
    int capacity = 0;
};

struct ExpandedArc {
    int from = 0;
    int to = 0;
    int capacity = 0;
};

int timedNode(int time, int vertex, int vertexCount) {
    return time * vertexCount + vertex;
}

vector<ExpandedArc> buildTimeExpandedNetwork(
    int vertexCount,
    int timeCount,
    const vector<DynamicArc>& arcs
) {
    vector<ExpandedArc> result;

    for (int t = 0; t < timeCount; ++t) {
        for (int v = 0; v < vertexCount; ++v) {
            result.push_back({
                timedNode(t, v, vertexCount),
                timedNode(t + 1, v, vertexCount),
                1000000000
            });
        }
    }

    for (const DynamicArc& arc : arcs) {
        int left = max(0, arc.start);
        int right = min(timeCount, arc.end);
        for (int t = left; t < right; ++t) {
            result.push_back({
                timedNode(t, arc.from, vertexCount),
                timedNode(t + 1, arc.to, vertexCount),
                arc.capacity
            });
        }
    }

    return result;
}
```

이 함수는 max flow 구현 자체가 아니라 모델 변환부입니다. 변환 뒤에는 일반 Dinic이나 Min-Cost Flow를 그대로 붙이면 됩니다.

## 6. 작은 예시

```text
정점: S, A, T
시간: 0..2
활성 간선:
  t=0: S -> A capacity 2
  t=1: A -> T capacity 1
```

time-expanded network에서는 `S0 -> A1 -> T2` 경로가 됩니다. 같은 사람이나 물건이 한 단계 쉬어도 되면 wait edge가 필요합니다. wait edge를 빼면 "반드시 매 시간 이동"하는 다른 문제가 됩니다.

## 7. 어떤 접근을 고를까

| 조건 | 우선 접근 |
| --- | --- |
| capacity 증가만 있음 | residual graph 재사용 |
| deletion이 적고 query block이 큼 | block rebuild |
| 모든 update를 미리 앎 | interval over time + offline 처리 |
| 시간 단계가 작음 | time-expanded network |
| 비용이 convex하게 증가 | convex cost flow 또는 edge split |

flow update 자체보다 문제 제약을 정적 모델로 바꾸는 편이 구현 위험이 낮습니다. 특히 삭제가 섞이면 완전 동적 구조를 바로 시도하지 말고 rebuild 기준 구현부터 만듭니다.

## 8. Cut 관점

max flow 값은 min cut capacity와 같습니다. update가 cut capacity를 어떻게 바꾸는지 보면 불필요한 재계산을 줄일 수 있습니다.

```text
capacity increase on non-critical edge -> answer may stay same
capacity increase crossing every min cut -> answer may increase
capacity decrease on used critical edge -> answer may decrease
```

하지만 "critical edge인지"를 유지하는 것도 쉽지 않습니다. 이 관점은 proof와 pruning에는 좋지만, 구현은 residual augment나 rebuild로 시작하는 편이 안전합니다.

## 9. 자주 하는 실수

1. capacity 감소 후에도 기존 flow가 feasible하다고 가정한다.
2. time-expanded network에서 wait edge를 빼서 도달 가능한 경로를 없앤다.
3. 시간 node 수를 `T`개로 만들고 `T+1`번째 도착 상태를 잊는다.
4. residual graph를 재사용하면서 reverse edge의 flow를 초기화해 버린다.
5. dynamic connectivity처럼 rollback DSU만으로 flow 최적화까지 해결하려고 한다.
6. source/sink가 바뀌는데 이전 max flow 값을 그대로 이어 쓴다.

## 10. 문제를 볼 때 체크할 조건

- update가 증가만 있는가, 감소나 삭제도 있는가?
- source와 sink가 고정인가?
- 기존 flow가 다음 상태에서도 feasible한가?
- 시간 단계 수가 정적 network로 펼칠 만큼 작은가?
- 답이 정확한 flow 값인가, threshold feasibility인가?
- 비용까지 있으면 residual shortest path를 재사용할 수 있는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: incremental max flow `/practice/...` 문제 필요 | capacity 증가 후 추가 augment | residual graph |
| 표준 | TODO: time-expanded evacuation `/practice/...` 문제 필요 | 시간 node 모델링 | wait edge |
| 응용 | TODO: dynamic flow block rebuild `/practice/...` 문제 필요 | 변경 묶음 재계산 | batch rebuild |
| 함정 | TODO: capacity decrease repair `/practice/...` 문제 필요 | infeasible old flow 처리 | feasibility repair |
