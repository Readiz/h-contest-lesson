# Dominator Tree

Dominator Tree는 시작 정점에서 어떤 정점으로 가는 모든 경로가 반드시 지나야 하는 정점을 찾는 구조입니다. 컴파일러의 control-flow graph에서 유명하지만, 그래프 문제에서도 "이 정점을 제거하면 반드시 막히는가" 같은 질문으로 등장합니다.

이 레슨은 SCC와 그래프 심화 이후에 보는 directed graph의 지배 관계를 정리합니다.

1. 시작점 `s`에서 `v`로 가는 모든 경로가 `u`를 지나면 `u`가 `v`를 dominate한다.
2. 각 정점의 가장 가까운 strict dominator가 immediate dominator이다.
3. immediate dominator 간선을 모으면 dominator tree가 된다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: DFS order, directed graph, tree ancestor, DSU path compression
- 함께 보면 좋은 레슨: SCC와 2-SAT, 위상 정렬과 DAG DP, 그래프와 트리 기본 성질
- 다음에 볼 레슨: control-flow graph, bridge-like directed constraints, dynamic dominator

## 1. 문제 신호

| 문제 표현 | Dominator 관점 |
| --- | --- |
| 시작점에서 v로 가는 모든 경로가 u를 거치는가 | dominance |
| 어떤 정점을 제거하면 v가 도달 불가능해지는가 | strict dominator |
| 각 정점의 필수 관문을 트리로 만들기 | immediate dominator |
| directed graph의 articulation 비슷한 질문 | dominator tree |
| 도달 불가능 정점이 섞여 있다 | DFS reachable만 처리 |

무향 그래프의 articulation point와 비슷해 보이지만, dominator는 시작점이 있는 방향 그래프에서 정의됩니다.

## 2. 정의

정점 `u`가 정점 `v`를 dominate한다는 것은 시작점 `s`에서 `v`로 가는 모든 경로가 `u`를 지난다는 뜻입니다.

```text
u dominates v  <=>  every path s -> v contains u
```

모든 정점은 자기 자신을 dominate합니다. `u != v`일 때는 strict dominator라고 부릅니다.

Immediate dominator `idom[v]`는 `v`의 strict dominator 중 가장 가까운 정점입니다. 이 간선을 모으면 tree가 됩니다.

## 3. Lengauer-Tarjan 흐름

Lengauer-Tarjan 알고리즘의 핵심은 DFS order에서 semi-dominator를 계산하는 것입니다.

1. 시작점에서 DFS를 하며 각 정점에 번호를 붙인다.
2. reverse edge를 보며 `semi[v]` 후보를 갱신한다.
3. union-find의 eval/link로 ancestor 경로의 최소 semi를 빠르게 찾는다.
4. bucket을 이용해 immediate dominator 후보를 정리한다.
5. 마지막 pass에서 `idom`을 보정한다.

구현은 어렵지만, 배열의 의미를 분리하면 따라갈 수 있습니다.

## 4. 구현

아래 구현은 시작점 `root`에서 도달 가능한 정점의 immediate dominator를 반환합니다. 도달 불가능한 정점의 `idom`은 `-1`입니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct DominatorTree {
    int n;
    vector<vector<int>> graph;
    vector<vector<int>> reverseGraph;
    vector<vector<int>> bucket;
    vector<int> arr;
    vector<int> rev;
    vector<int> parent;
    vector<int> semi;
    vector<int> idom;
    vector<int> dsu;
    vector<int> label;
    int timer = 0;

    explicit DominatorTree(int n) : n(n), graph(n), reverseGraph(n) {}

    void addEdge(int u, int v) {
        graph[u].push_back(v);
    }

    void dfs(int v) {
        arr[v] = timer;
        rev[timer] = v;
        label[timer] = timer;
        semi[timer] = timer;
        dsu[timer] = timer;
        ++timer;

        for (int to : graph[v]) {
            if (arr[to] == -1) {
                dfs(to);
                parent[arr[to]] = arr[v];
            }
            reverseGraph[to].push_back(v);
        }
    }

    int find(int v, int x = 0) {
        if (dsu[v] == v) {
            return x ? -1 : v;
        }
        int p = find(dsu[v], x + 1);
        if (p < 0) {
            return v;
        }
        if (semi[label[dsu[v]]] < semi[label[v]]) {
            label[v] = label[dsu[v]];
        }
        dsu[v] = p;
        return x ? p : label[v];
    }

    void unite(int parentNode, int childNode) {
        dsu[childNode] = parentNode;
    }

    vector<int> build(int root) {
        arr.assign(n, -1);
        rev.assign(n, -1);
        parent.assign(n, -1);
        semi.assign(n, 0);
        idom.assign(n, -1);
        dsu.assign(n, 0);
        label.assign(n, 0);
        reverseGraph.assign(n, {});
        bucket.assign(n, {});
        timer = 0;

        dfs(root);
        int reachable = timer;
        vector<int> dom(reachable, -1);

        for (int i = reachable - 1; i >= 0; --i) {
            int v = rev[i];
            for (int from : reverseGraph[v]) {
                if (arr[from] == -1) {
                    continue;
                }
                int candidate = find(arr[from]);
                semi[i] = min(semi[i], semi[candidate]);
            }

            if (i > 0) {
                bucket[semi[i]].push_back(i);
            }

            for (int vertex : bucket[i]) {
                int candidate = find(vertex);
                if (semi[candidate] == semi[vertex]) {
                    dom[vertex] = semi[vertex];
                } else {
                    dom[vertex] = candidate;
                }
            }

            if (i > 0) {
                unite(parent[i], i);
            }
        }

        for (int i = 1; i < reachable; ++i) {
            if (dom[i] != semi[i]) {
                dom[i] = dom[dom[i]];
            }
            idom[rev[i]] = rev[dom[i]];
        }
        idom[root] = root;
        return idom;
    }
};
```

`idom[root]`을 `root`로 둘지 `-1`로 둘지는 문제에 맞게 선택합니다. 위 구현은 tree root 확인을 쉽게 하려고 자기 자신으로 둡니다.

## 5. Dominator Tree 사용

`idom[v]`를 구하면 아래처럼 tree를 만들 수 있습니다.

```text
for each v != root:
    tree[idom[v]].push_back(v)
```

Dominator tree에서 `u`가 `v`의 ancestor라면 `u`는 원래 graph에서 `v`를 dominate합니다. 따라서 subtree size를 이용해 특정 정점이 지배하는 정점 수를 셀 수 있습니다.

## 6. 도달 불가능 정점

Dominator는 시작점에서 도달 가능한 정점에 대해서만 의미가 있습니다.

| 상태 | 처리 |
| --- | --- |
| `arr[v] == -1` | root에서 도달 불가능 |
| `idom[v] == -1` | dominator tree에 넣지 않음 |
| 여러 시작점 | super root를 추가하거나 문제 조건을 분리 |

도달 불가능 정점을 그대로 tree에 넣으면 ancestor 판정이 깨집니다.

## 7. Articulation과 차이

| 항목 | Articulation Point | Dominator |
| --- | --- | --- |
| 그래프 | 보통 무향 | 방향 |
| 기준 | 제거 시 connected component 증가 | 시작점에서 모든 경로가 지나감 |
| 결과 | cut vertex 집합 | immediate dominator tree |
| root | DFS root 특수 처리 | 시작점 자체가 정의의 일부 |

방향 그래프의 "필수 관문" 문제에서는 articulation보다 dominator를 먼저 떠올립니다.

## 8. 시간 복잡도

Lengauer-Tarjan 구현은 거의 선형 시간으로 동작합니다.

```text
O((N + M) alpha(N))
```

구현 상수는 작은 편이 아니므로, 작은 DAG에서는 모든 predecessor idom을 LCA처럼 처리하는 단순 DP가 더 편할 수 있습니다.

## 9. 자주 하는 실수

1. reverse edge를 DFS reachable 기준으로 필터링하지 않는다.
2. DFS order index와 원래 vertex id를 섞는다.
3. root의 `idom` convention을 문제 출력과 맞추지 않는다.
4. 도달 불가능 정점을 dominator tree에 포함한다.
5. tree ancestor 판정 전 Euler tour를 만들지 않는다.

## 10. 문제를 볼 때 체크할 조건

- 시작 정점이 고정되어 있는가?
- 방향 그래프인가?
- 도달 불가능 정점 처리가 필요한가?
- 필요한 것은 `idom` 자체인가, dominate 관계 질의인가?
- 정점 제거 영향이 하나의 root 기준으로 정의되는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 필수 관문 판정 `/practice/...` 문제 필요 | dominate 정의와 tree ancestor 연결 | dominator |
| 표준 | TODO: immediate dominator tree `/practice/...` 문제 필요 | Lengauer-Tarjan 구현 | idom |
| 응용 | TODO: 지배하는 정점 수 `/practice/...` 문제 필요 | dominator tree subtree size | dominance subtree |
| 함정 | TODO: 도달 불가능 정점 포함 `/practice/...` 문제 필요 | reachable filtering | flow graph |
