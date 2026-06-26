# Cactus Representation

Cactus Representation은 여러 cut이나 biconnected 구조를 "각 edge가 하나의 cycle에만 속하는" 그래프로 압축해 보는 관점입니다. 특히 모든 global minimum cut을 compact하게 표현할 때 cactus가 등장하지만, 구현 난도 때문에 먼저 어떤 문제에서 cactus 모델이 필요한지 구분하는 것이 중요합니다.

이 레슨은 Global Min Cut Applications와 Cut Sparsification 이후에 보는 그래프 모델링 심화입니다.

1. cactus graph의 구조적 제약을 이해한다.
2. min cut family와 biconnected component 압축에서 cactus가 왜 나오는지 본다.
3. 직접 cactus를 만드는 문제와 cactus 위에서 질의하는 문제를 구분한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Global Min Cut, Gomory-Hu Tree, DFS lowlink, biconnected component
- 함께 보면 좋은 레슨: Global Min Cut Applications, Cut Sparsification, SCC와 2-SAT
- 다음에 볼 레슨: randomized min cut, bridge-block tree, cut family queries

## 1. 문제 신호

| 문제 표현 | Cactus 관점 |
| --- | --- |
| 모든 global minimum cut을 표현 | min cut cactus |
| 각 edge가 최대 하나의 cycle에 속함 | cactus graph 직접 처리 |
| 두 정점 사이 simple path 개수 제한 | cactus LCA/block 처리 |
| bridge와 cycle block이 섞임 | block tree 또는 cactus |
| minimum cut이 여러 개인지 압축 | cut family representation |

"cactus graph가 입력으로 주어지는 문제"와 "일반 그래프의 cut family를 cactus로 만드는 문제"는 난도가 크게 다릅니다.

## 2. Cactus Graph 정의

Cactus graph는 보통 아래 성질 중 하나로 정의합니다.

```text
모든 edge는 최대 하나의 simple cycle에 속한다.
```

이 성질 때문에 bridge와 cycle block을 분리하면 tree처럼 다룰 수 있습니다. cycle 내부에서는 두 방향 경로가 있고, cycle 밖으로 나가면 block tree 경로가 유일합니다.

## 3. 입력 Cactus 처리

입력 그래프가 이미 cactus라면 DFS로 cycle을 찾아 component를 만들 수 있습니다.

```cpp compile-check
#include <algorithm>
#include <utility>
#include <vector>
using namespace std;

struct CactusDfs {
    int n;
    vector<vector<pair<int, int>>> graph;
    vector<int> depth;
    vector<int> parentVertex;
    vector<int> parentEdge;
    vector<int> seen;
    vector<vector<int>> cycles;

    explicit CactusDfs(int vertexCount)
        : n(vertexCount),
          graph(vertexCount),
          depth(vertexCount, 0),
          parentVertex(vertexCount, -1),
          parentEdge(vertexCount, -1),
          seen(vertexCount, 0) {}

    void addEdge(int u, int v, int id) {
        graph[u].push_back({v, id});
        graph[v].push_back({u, id});
    }

    void recordCycle(int from, int to) {
        vector<int> cycle;
        int current = from;
        cycle.push_back(current);
        while (current != to) {
            current = parentVertex[current];
            cycle.push_back(current);
        }
        cycles.push_back(cycle);
    }

    void dfs(int u, int parentEdgeId) {
        seen[u] = 1;
        for (auto [v, edgeId] : graph[u]) {
            if (edgeId == parentEdgeId) {
                continue;
            }
            if (!seen[v]) {
                parentVertex[v] = u;
                parentEdge[v] = edgeId;
                depth[v] = depth[u] + 1;
                dfs(v, edgeId);
            } else if (depth[v] < depth[u]) {
                recordCycle(u, v);
            }
        }
    }
};
```

일반 무향 그래프에서는 같은 edge나 vertex가 여러 cycle에 엮일 수 있으므로 이 코드만으로 cactus 검증이 끝나지 않습니다. cycle edge 사용 횟수와 block 구조를 추가로 확인해야 합니다.

## 4. Min Cut Cactus 직관

무향 그래프의 모든 global minimum cut은 cactus 구조로 표현할 수 있다는 정리가 있습니다. cactus의 각 edge나 cycle 분할이 원래 그래프의 minimum cut 하나를 뜻합니다.

| 원래 그래프의 정보 | Cactus에서의 해석 |
| --- | --- |
| global min cut 값 | 모든 cactus cut의 공통 값 |
| min cut 하나 | cactus edge 또는 cycle split |
| 여러 min cut family | cactus의 cycle 구조 |
| 두 정점이 자주 함께 분리됨 | cactus 위 위치 관계 |

대회에서 이 구조를 직접 구성하는 문제는 드뭅니다. 하지만 "minimum cut이 여러 개"라는 문제 문장을 읽을 때 단일 partition만으로 부족하다는 신호가 됩니다.

## 5. Bridge Tree와의 차이

Bridge tree는 bridge를 기준으로 2-edge-connected component를 압축한 tree입니다. Cactus는 cycle block을 그대로 남길 수 있습니다.

| 구조 | 압축 기준 | 결과 |
| --- | --- | --- |
| Bridge tree | bridge가 아닌 edge로 묶음 | tree |
| Block-cut tree | articulation point와 biconnected component | bipartite tree |
| Cactus | edge-disjoint cycle 구조 | tree + cycle |
| Min cut cactus | global min cut family | cut family graph |

Cactus 입력 문제를 bridge tree로만 줄이면 cycle 내부의 두 경로 선택 정보를 잃을 수 있습니다.

## 6. Cactus 위 거리 질의

Cactus에서 두 정점 사이 최단 거리를 구할 때 cycle block 안에서는 시계/반시계 방향 중 짧은 쪽을 골라야 합니다. 전체 구조는 block tree로 올린 뒤, 같은 cycle component에 들어갈 때만 cycle distance를 계산합니다.

```text
1. bridge는 tree edge처럼 거리 1
2. cycle component는 cycle prefix length로 두 방향 거리 계산
3. block tree LCA로 지나가는 component들을 합침
```

weighted cactus라면 cycle prefix sum을 저장합니다.

## 7. 작은 예시

```text
cycle: 1-2-3-1
bridge: 3-4
cycle: 4-5-6-4

edge 3-4는 bridge라서 모든 1쪽 정점과 5쪽 정점을 분리한다.
각 triangle 내부에서는 두 방향 경로가 있다.
그래프 전체는 tree처럼 연결되지만 cycle 안에서는 선택지가 생긴다.
```

이 구조에서 단순 DFS tree path만 쓰면 triangle 내부 거리나 path count를 잘못 계산합니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| DFS로 back edge 후보 찾기 | `O(N + M)` |
| cactus 검증 | `O(N + M)` |
| block tree 구성 | `O(N + M)` |
| cactus 위 LCA 전처리 | `O(N log N)` |
| min cut cactus 구성 | 알고리즘별로 훨씬 복잡 |

입력이 cactus라고 보장되면 처리가 가벼워집니다. 일반 그래프에서 cactus representation을 만들어야 한다면 별도 이론이 필요합니다.

## 9. 자주 하는 실수

1. cactus 입력 처리와 min cut cactus 구성을 같은 문제로 생각한다.
2. vertex가 여러 cycle에 속할 수 있는 cactus 변형을 잘못 금지한다.
3. edge가 두 cycle에 속하는지 검증하지 않는다.
4. cycle 내부 거리에서 두 방향 중 하나만 본다.
5. bridge tree로 압축해 cycle 내부 정보를 잃는다.

## 10. 문제를 볼 때 체크할 조건

- cactus가 입력으로 주어지는가, 아니면 직접 구성해야 하는가?
- edge-disjoint cycle 조건인지 vertex-disjoint cycle 조건인지 문제 정의를 확인했는가?
- 질의가 거리, path count, cut family 중 무엇인가?
- cycle 내부에 prefix sum이나 order가 필요한가?
- 일반 그래프라면 biconnected component 또는 min cut 이론이 필요한가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: cactus graph validation `/practice/...` 문제 필요 | edge가 cycle에 중복 포함되는지 확인 | DFS cycle |
| 표준 | TODO: cactus distance query `/practice/...` 문제 필요 | cycle prefix와 block tree 결합 | LCA |
| 응용 | TODO: min cut cactus `/practice/...` 문제 필요 | minimum cut family 해석 | cut representation |
| 함정 | TODO: bridge tree is not enough `/practice/...` 문제 필요 | cycle 내부 정보 보존 | block compression |
