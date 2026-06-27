# Dynamic MST

Dynamic MST는 그래프의 간선 가중치나 활성 상태가 바뀔 때 minimum spanning tree를 유지하는 주제입니다. 완전한 online dynamic MST는 매우 어렵지만, 대회에서는 "작은 변경은 MST 성질로 갱신"하거나 "질의를 모아서 오프라인으로 처리"하는 형태가 더 자주 등장합니다.

이 레슨은 MST, Dynamic Connectivity, Gomory-Hu Tree 이후에 보는 그래프 심화입니다.

1. 간선 추가는 새 간선을 넣고 cycle에서 가장 무거운 간선을 제거한다.
2. MST 간선 삭제는 replacement edge를 찾아야 하므로 훨씬 어렵다.
3. 질의를 모두 알 수 있으면 구간 분할, rollback, rebuild를 먼저 검토한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Kruskal, cut/cycle property, Union-Find, dynamic connectivity
- 함께 보면 좋은 레슨: Graph와 Tree 기본, Dynamic Connectivity, Euler Tour Tree
- 다음에 볼 레슨: fully dynamic MST, top tree, replacement edge data structure

## 1. 문제 신호

| 문제 표현 | Dynamic MST 관점 |
| --- | --- |
| 간선이 추가되고 MST 비용을 묻는다 | cycle property 갱신 |
| 간선 삭제가 섞인다 | replacement edge 탐색 |
| 가중치 업데이트가 있다 | 삭제 후 추가로 분해 |
| 질의를 모두 미리 읽을 수 있다 | offline divide and conquer 후보 |
| 정점 수는 크지만 변경 수가 작다 | periodic rebuild 후보 |

MST는 cut property와 cycle property가 강력합니다. 하지만 삭제된 간선이 MST에 들어 있었는지, 들어 있었다면 어떤 non-tree edge가 대체할 수 있는지를 빠르게 찾는 것이 핵심 난점입니다.

## 2. 간선 추가

현재 MST가 있고 새 간선 `(u, v, w)`가 추가되면, MST 경로 `u..v`에 새 간선을 더해 cycle이 생깁니다.

```text
cycle에서 가장 무거운 간선이 새 간선보다 무거우면 교체
그렇지 않으면 새 간선은 MST에 들어가지 않음
```

따라서 online 추가만 있다면 MST 위 path maximum query가 필요합니다. Link-Cut Tree, Heavy-Light Decomposition, binary lifting rebuild 중 제약에 맞는 것을 고릅니다.

## 3. 간선 삭제

삭제된 간선이 MST 밖이면 MST는 변하지 않습니다. 삭제된 간선이 MST 안이면 MST가 두 component로 갈라지고, 두 component를 잇는 non-tree edge 중 가장 싼 edge를 찾아야 합니다.

```text
MST edge e 삭제
component A, B로 분리
min weight non-tree edge crossing (A, B)를 replacement로 선택
```

이 replacement edge query가 동적 MST의 어려운 부분입니다. 문제 조건이 약하면 삭제마다 전체 Kruskal을 다시 돌리는 rebuild가 더 안전합니다.

## 4. Rebuild Baseline

아래 코드는 활성 간선 집합에서 MST 비용을 다시 계산하는 기준 구현입니다. 복잡도는 무겁지만, 작은 입력이나 sqrt decomposition rebuild의 내부 루틴으로 유용합니다.

```cpp compile-check
#include <algorithm>
#include <numeric>
#include <vector>
using namespace std;

struct DynamicMstBaseline {
    struct Edge {
        int u;
        int v;
        long long weight;
        bool active;
    };

    struct DSU {
        vector<int> parent;
        vector<int> size;

        explicit DSU(int n) : parent(n + 1), size(n + 1, 1) {
            iota(parent.begin(), parent.end(), 0);
        }

        int find(int x) {
            while (parent[x] != x) {
                parent[x] = parent[parent[x]];
                x = parent[x];
            }
            return x;
        }

        bool unite(int a, int b) {
            a = find(a);
            b = find(b);
            if (a == b) {
                return false;
            }
            if (size[a] < size[b]) {
                swap(a, b);
            }
            parent[b] = a;
            size[a] += size[b];
            return true;
        }
    };

    int vertexCount;
    vector<Edge> edges;

    explicit DynamicMstBaseline(int n) : vertexCount(n) {}

    int addEdge(int u, int v, long long weight) {
        edges.push_back({u, v, weight, true});
        return (int)edges.size() - 1;
    }

    void setActive(int edgeId, bool active) {
        if (0 <= edgeId && edgeId < (int)edges.size()) {
            edges[edgeId].active = active;
        }
    }

    pair<bool, long long> rebuildMstCost() const {
        vector<Edge> usable;
        for (const Edge& edge : edges) {
            if (edge.active) {
                usable.push_back(edge);
            }
        }
        sort(usable.begin(), usable.end(), [](const Edge& a, const Edge& b) {
            return a.weight < b.weight;
        });

        DSU dsu(vertexCount);
        long long cost = 0;
        int used = 0;
        for (const Edge& edge : usable) {
            if (dsu.unite(edge.u, edge.v)) {
                cost += edge.weight;
                ++used;
            }
        }
        return {used == vertexCount - 1, cost};
    }
};
```

이 baseline은 update마다 `O(M log M)`입니다. 하지만 정답 확인용, stress test용, block rebuild용으로는 여전히 가치가 큽니다.

## 5. 오프라인 접근

질의를 모두 읽을 수 있으면 간선의 활성 구간을 만들고 시간 구간별로 안정적인 간선을 분류합니다.

```text
edge e active on [l, r)
divide query time interval
항상 존재하는 edge는 contraction 후보
절대 MST에 못 들어가는 edge는 filtering 후보
```

Dynamic Connectivity에서 쓰는 segment tree over time과 비슷해 보이지만, MST는 가중치 최적화가 끼기 때문에 단순 rollback DSU만으로 끝나지 않습니다. 그래도 "각 구간에서 필요한 edge 후보를 줄인 뒤 재귀"하는 방향은 자주 쓰입니다.

## 6. 작은 변경 처리

변경 수가 작으면 block 단위 전략이 실용적입니다.

1. block 시작 시점에 고정 간선으로 MST를 rebuild한다.
2. block 안에서 바뀐 간선만 별도 후보로 모은다.
3. query마다 고정 MST edge와 변경 후보를 합쳐 작은 Kruskal을 돌린다.

이 방식은 구현 난도가 낮고, `Q sqrt Q` 계열 제한에서 잘 맞습니다.

## 7. 시간 복잡도 감각

| 접근 | 대략적인 비용 | 특징 |
| --- | ---: | --- |
| 매 query rebuild | `O(M log M)` | 단순하고 안전 |
| 추가만 처리 | `O(log^2 N)` path max query | 삭제 없음 |
| block rebuild | `O((M log M) * blocks + small Kruskal)` | 변경 수가 작을 때 |
| full online dynamic MST | 고급 자료구조 필요 | 구현 위험 큼 |

문제 제한이 아주 크지 않다면 먼저 baseline으로 correctness를 잡고, 병목이 확인되면 block/offline으로 줄입니다.

## 8. 자주 하는 실수

1. MST 밖 간선 삭제도 MST를 바꾼다고 처리한다.
2. 새 간선 추가 때 cycle의 최대 간선이 아니라 전체 MST의 최대 간선을 본다.
3. 같은 weight edge가 있을 때 tie가 바뀌어도 MST cost만 유지하면 되는 문제인지 확인하지 않는다.
4. disconnected 상태를 MST cost 0처럼 출력한다.
5. 완전한 online dynamic MST가 필요한 문제를 단순 rollback DSU로 풀려고 한다.

## 9. 문제를 볼 때 체크할 조건

- update가 추가만 있는가, 삭제도 있는가?
- 모든 질의를 미리 읽을 수 있는가?
- 필요한 답이 MST cost인가, 실제 edge set인가?
- 그래프가 disconnected일 수 있는가?
- 변경 간선 수가 작아서 rebuild가 가능한가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: dynamic MST rebuild `/practice/...` 문제 필요 | Kruskal baseline 유지 | active edges |
| 표준 | TODO: edge insertion MST `/practice/...` 문제 필요 | cycle maximum 교체 | path max |
| 응용 | TODO: block rebuild MST `/practice/...` 문제 필요 | 변경 후보 축소 | sqrt decomposition |
| 함정 | TODO: deleted tree edge replacement `/practice/...` 문제 필요 | crossing edge 탐색 | replacement edge |
