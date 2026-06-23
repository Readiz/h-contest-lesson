# Cut Cactus Applications

Cut Cactus Applications는 global min cut이 여러 개 존재할 때, 그 cut family를 cactus representation으로 모델링하는 응용 레슨입니다. Global Min Cut 값 하나를 구하는 것에서 더 나아가 "어떤 간선이나 정점 분리가 최소 cut에 참여하는가"를 물을 때 cactus 구조가 등장합니다.

이 레슨은 Cactus Representation, Global Min Cut, Gomory-Hu Tree 이후에 보는 그래프 cut 심화입니다.

1. 필요한 cut이 global min cut family인지 pair min cut인지 구분한다.
2. cactus의 cycle block이 여러 최소 cut 선택지를 압축한다는 점을 이해한다.
3. edge criticality, component partition, query를 cactus 위 문제로 바꾼다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Global Min Cut, Cactus Representation, Gomory-Hu Tree
- 함께 보면 좋은 레슨: Cut Sparsification, Randomized Min Cut, Global Min Cut Applications
- 다음에 볼 레슨: randomized contraction variants, cut family queries, connectivity certificates

## 1. 문제 신호

| 문제 표현 | Cactus 응용 관점 |
| --- | --- |
| minimum cut이 여러 개 있음 | cut family compression |
| 어떤 두 정점이 모든 min cut에서 같이 남는가 | cactus path/cycle query |
| 간선 하나가 min cut에 얼마나 중요한가 | edge criticality |
| min cut partition을 모두 나열하기 어려움 | cactus block representation |
| global min cut 값은 이미 알고 있음 | family representation stage |

Gomory-Hu Tree는 모든 쌍 min cut 값을 압축하고, cut cactus는 global min cut family를 압축합니다. 두 구조의 목적을 섞지 않는 것이 중요합니다.

## 2. Cactus가 표현하는 것

Cactus graph는 각 edge가 최대 하나의 simple cycle에만 속하는 그래프입니다. Global min cut family에서는 cactus의 edge나 cycle 선택이 원래 그래프의 minimum cut partition에 대응합니다.

```text
tree edge cut: 그 edge 하나를 제거
cycle block cut: cycle에서 두 edge를 골라 분리
```

cycle은 "여러 minimum cut이 같은 값으로 공존하는 영역"을 압축합니다.

## 3. 작은 예시

```text
cactus cycle: A - B - C - D - A
```

cycle에서 두 edge를 끊으면 cycle이 두 path로 나뉩니다. 이 선택이 원래 그래프의 서로 다른 minimum cut partition을 나타낼 수 있습니다.

```text
remove (A-B), (C-D)
=> {B,C} side와 {D,A} side
```

따라서 cycle 길이가 길수록 가능한 minimum cut partition이 많이 생깁니다.

## 4. Query로 바꾸기

원래 그래프 정점은 cactus node나 cactus component에 매핑됩니다. 그러면 질의는 cactus 위 경로/사이클 질의가 됩니다.

| 원래 질문 | Cactus 질문 |
| --- | --- |
| `u`, `v`를 분리하는 min cut이 있는가 | mapped nodes 사이를 끊는 선택이 가능한가 |
| 모든 min cut에서 같이 남는가 | 어떤 cactus cut도 둘을 분리하지 못하는가 |
| 특정 component가 분리 가능한가 | cactus edge/cycle 선택으로 isolate 가능한가 |
| min cut family 수를 세는가 | tree edge와 cycle pair 선택 count |

실제 문제에서는 cactus를 직접 만들기보다 이미 주어진 cactus에서 query를 처리하는 형태가 더 자주 나옵니다.

## 5. Cactus Tree DP Skeleton

아래 코드는 cactus를 block tree처럼 보고, tree edge contribution을 DFS로 누적하는 단순 skeleton입니다.

```cpp compile-check
#include <vector>
using namespace std;

struct CactusQueryGraph {
    vector<vector<int>> graph;
    vector<int> subtreeSize;

    explicit CactusQueryGraph(int n) : graph(n), subtreeSize(n, 0) {}

    void addEdge(int a, int b) {
        graph[a].push_back(b);
        graph[b].push_back(a);
    }

    int dfsSize(int node, int parent) {
        subtreeSize[node] = 1;
        for (int next : graph[node]) {
            if (next == parent) {
                continue;
            }
            subtreeSize[node] += dfsSize(next, node);
        }
        return subtreeSize[node];
    }
};
```

cycle block이 있으면 단순 tree DFS만으로는 부족합니다. cycle을 block node로 압축하거나, cycle 내부 query를 별도 prefix로 처리합니다.

## 6. Edge Criticality

간선 `e`가 모든 global min cut에 포함되는지, 어떤 min cut에는 포함되는지 묻는 경우가 있습니다.

```text
always critical: cactus에서 대체 cycle 선택이 없음
sometimes critical: 어떤 edge/cycle 선택에 대응됨
never critical: min cut family 표현에 나타나지 않음
```

원래 그래프 edge와 cactus cut element의 매핑이 필요하므로, cut construction 단계에서 witness 정보를 보존해야 합니다.

## 7. Gomory-Hu Tree와 비교

| 구조 | 압축 대상 |
| --- | --- |
| Gomory-Hu Tree | 모든 정점 쌍의 min cut value |
| Cut Cactus | global min cut partition family |
| Cut Sparsifier | cut value를 보존하는 작은 edge set |
| Stoer-Wagner | global min cut 값 하나 |

질문이 pair-specific이면 Gomory-Hu Tree를 먼저 떠올리고, 질문이 global min cut의 모든 형태라면 cactus를 떠올립니다.

## 8. 구현 현실성

cut cactus를 처음부터 구성하는 알고리즘은 상당히 복잡합니다. 대회에서는 다음 중 하나인 경우가 많습니다.

1. cactus가 입력으로 주어진다.
2. global min cut 후보들이 주어지고 family query만 한다.
3. 작은 그래프에서 all min cut을 brute force한 뒤 cactus 성질을 활용한다.
4. 이론 설명이나 모델링이 목적이다.

직접 construction이 요구되면 논문 수준 구현인지, 더 단순한 min cut 반복 풀이가 통하는 크기인지 먼저 확인합니다.

## 9. 자주 하는 실수

1. Gomory-Hu Tree를 global min cut family 표현으로 착각한다.
2. cactus cycle에서 edge 하나만 끊는다고 생각한다.
3. 원래 정점과 cactus node mapping을 잃어 query를 못 푼다.
4. global min cut 값이 아닌 pair min cut까지 cactus 하나로 처리하려 한다.
5. cycle block을 tree edge처럼 DFS해 가능한 cut 수를 틀린다.
6. construction 난도를 무시하고 전체 cactus build부터 구현한다.

## 10. 문제를 볼 때 체크할 조건

- 질문이 global min cut family에 대한 것인가?
- cactus가 입력으로 주어지는가, 직접 구성해야 하는가?
- 원래 정점이 cactus의 어느 component에 매핑되는가?
- cycle block의 두 edge 선택을 query에 반영했는가?
- pair min cut value가 필요하면 Gomory-Hu Tree가 더 맞지 않은가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: cactus cut query `/practice/...` 문제 필요 | tree edge와 cycle cut 구분 | cactus |
| 표준 | TODO: min cut family count `/practice/...` 문제 필요 | cycle pair 선택 세기 | global min cut |
| 응용 | TODO: edge criticality `/practice/...` 문제 필요 | 원래 edge와 cactus cut 매핑 | witness |
| 함정 | TODO: gomory-hu vs cactus `/practice/...` 문제 필요 | pair cut과 global cut 구분 | cut family |
