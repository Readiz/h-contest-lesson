# Gomory-Hu Tree

Gomory-Hu Tree는 무향 그래프의 모든 정점 쌍 minimum cut 값을 `N-1`번의 min-cut 계산으로 압축하는 구조입니다. 완성된 tree에서는 두 정점 사이 경로의 최소 edge weight가 원래 그래프에서의 두 정점 min cut 값이 됩니다.

이 레슨은 Max Flow와 Min Cut, Flow with Lower Bound 이후에 보는 그래프 심화입니다.

1. 한 쌍 `(s, t)`의 min cut을 구하고 reachable side를 얻는다.
2. 현재 cut tree의 parent 관계를 reachable side 기준으로 재배치한다.
3. tree path minimum으로 모든 쌍 min cut 질의를 답한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: max-flow min-cut theorem, undirected capacity graph, residual graph
- 함께 보면 좋은 레슨: Max Flow, Min Cut, Flow with Lower Bound, Min-Cost Flow
- 다음에 볼 레슨: dynamic min cut, cut-equivalent tree, global min cut

## 1. 문제 신호

| 문제 표현 | Gomory-Hu Tree 관점 |
| --- | --- |
| 무향 그래프에서 모든 쌍 min cut | cut-equivalent tree |
| 많은 `s-t` cut 질의 | tree path minimum |
| edge connectivity를 여러 쌍에 대해 묻는다 | min cut value table 압축 |
| 정점 수는 작고 max-flow는 가능 | `N-1` max-flow |
| 방향 그래프이다 | Gomory-Hu Tree 기본형은 맞지 않음 |

Gomory-Hu Tree는 무향 그래프용입니다. 방향 그래프의 모든 쌍 min cut은 같은 방식으로 tree 하나에 압축되지 않습니다.

## 2. Tree가 담는 의미

Gomory-Hu Tree `T`는 원래 그래프와 같은 정점 집합을 갖고 edge가 `N-1`개입니다. 임의의 두 정점 `u`, `v`에 대해:

```text
minCut_G(u, v) = minimum edge weight on path_T(u, v)
```

즉 모든 쌍에 대해 max-flow를 다시 돌리지 않고 tree에서 LCA/RMQ 또는 단순 path traversal로 답할 수 있습니다.

## 3. Construction 개요

처음에는 모든 정점의 parent를 0으로 둡니다. 정점 `s`를 1부터 `N-1`까지 보면서 `s`와 `parent[s]` 사이 min cut을 계산합니다.

```text
for s in 1..N-1:
  t = parent[s]
  (cutValue, side) = minCut(s, t)
  parent가 t이고 side에 속한 정점들을 s 아래로 옮긴다
  필요하면 s와 t의 parent 관계를 회전한다
  weight[s] = cutValue
```

`side`는 residual graph에서 `s`로부터 도달 가능한 정점 집합입니다. 이 정보가 있어야 cut tree를 갱신할 수 있습니다.

## 4. 구현 골격

아래 코드는 max-flow 구현을 주입받아 Gomory-Hu parent tree를 만드는 골격입니다. `minCut(s, t)`는 min cut 값과 residual reachable side를 반환해야 합니다.

```cpp compile-check
#include <functional>
#include <tuple>
#include <utility>
#include <vector>
using namespace std;

struct MinCutResult {
    long long value = 0;
    vector<int> reachableFromSource;
};

struct GomoryHuTree {
    int n;
    vector<int> parent;
    vector<long long> weightToParent;
    function<MinCutResult(int, int)> minCut;

    GomoryHuTree(int vertexCount, function<MinCutResult(int, int)> oracle)
        : n(vertexCount), parent(vertexCount, 0), weightToParent(vertexCount, 0), minCut(oracle) {}

    vector<tuple<int, int, long long>> build() {
        for (int s = 1; s < n; ++s) {
            int t = parent[s];
            MinCutResult result = minCut(s, t);
            const vector<int>& side = result.reachableFromSource;

            for (int v = s + 1; v < n; ++v) {
                if (parent[v] == t && side[v]) {
                    parent[v] = s;
                }
            }

            if (side[parent[t]]) {
                parent[s] = parent[t];
                parent[t] = s;
                weightToParent[s] = weightToParent[t];
                weightToParent[t] = result.value;
            } else {
                weightToParent[s] = result.value;
            }
        }

        vector<tuple<int, int, long long>> edges;
        for (int v = 1; v < n; ++v) {
            edges.push_back({v, parent[v], weightToParent[v]});
        }
        return edges;
    }
};
```

실전에서는 매 min-cut마다 원본 capacity graph를 복사하거나 capacity를 초기화해야 합니다. 이전 flow의 residual graph를 그대로 쓰면 다음 cut이 깨집니다.

## 5. 질의 처리

완성된 Gomory-Hu Tree에서 `u-v` 경로의 edge weight 최솟값이 답입니다.

```text
answer(u, v):
  path = tree path from u to v
  return min(edge.weight for edge in path)
```

질의가 많으면 tree에 LCA binary lifting을 올리고, 각 jump마다 최소 edge weight를 함께 저장합니다. 정점 수가 작으면 DFS로 경로를 찾아도 됩니다.

## 6. 왜 `N-1`번이면 충분한가

각 단계에서 구한 cut은 현재 tree의 한 edge에 해당하는 분할을 확정합니다. reachable side에 따라 parent를 재배치하면 이전에 확정된 cut과 충돌하지 않는 형태로 cut-equivalent tree가 유지됩니다.

증명은 submodularity와 cut uncrossing에 기대지만, 구현 관점에서는 아래 두 조건을 기억하면 충분합니다.

1. 매번 `s`와 `parent[s]`의 실제 minimum cut을 구한다.
2. reachable side에 속한 같은 parent 자식들을 `s` 아래로 옮긴다.

## 7. 시간 복잡도

| 항목 | 복잡도 |
| --- | ---: |
| Gomory-Hu construction | `N-1`번 max-flow |
| tree edge 수 | `N-1` |
| 단순 질의 | `O(N)` |
| LCA 전처리 후 질의 | `O(log N)` |

전체 병목은 max-flow입니다. `N`이 크고 edge도 많은 경우에는 global min cut만 필요한지, 모든 쌍 질의가 정말 필요한지 먼저 확인합니다.

## 8. 자주 하는 실수

1. 방향 그래프에 Gomory-Hu Tree를 그대로 적용한다.
2. min-cut 값만 받고 reachable side를 저장하지 않는다.
3. 매 max-flow마다 capacity/residual graph를 초기화하지 않는다.
4. tree path의 합을 답으로 착각한다. 답은 path minimum이다.
5. parallel edge와 undirected capacity를 입력에서 합치지 않는다.

## 9. 문제를 볼 때 체크할 조건

- 그래프가 무향 capacity graph인가?
- 모든 쌍 min cut 또는 많은 쌍 cut 질의가 필요한가?
- `N-1`번 max-flow가 시간 안에 가능한가?
- min-cut 후 source side를 얻을 수 있는 max-flow 구현인가?
- 질의가 많아 LCA path minimum 전처리가 필요한가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: pair min-cut query `/practice/...` 문제 필요 | cut tree path minimum 이해 | Gomory-Hu |
| 표준 | TODO: edge connectivity all pairs `/practice/...` 문제 필요 | `N-1` max-flow construction | cut-equivalent tree |
| 응용 | TODO: many min-cut queries `/practice/...` 문제 필요 | LCA minimum edge query | tree path RMQ |
| 함정 | TODO: directed graph counterexample `/practice/...` 문제 필요 | 적용 조건 판정 | undirected cut |
