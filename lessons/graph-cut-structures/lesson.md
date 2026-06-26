# Graph Cut Structures

Graph Cut Structures는 s-t min cut 이후의 무향 cut 구조를 하나의 학습 경로로 묶는 허브입니다. Global Min Cut, Gomory-Hu Tree, Cut Sparsification, Randomized Min Cut, Cactus Representation은 모두 "어떤 cut 정보를 얼마나 많이, 어떤 형태로 보존할 것인가"라는 같은 질문에서 출발합니다.

기존 문서들은 각각 유용하지만 독립 카드로 나란히 놓이면 Stoer-Wagner, Karger, Gomory-Hu, cactus, sparse certificate의 선후 관계를 사용자가 직접 복원해야 합니다. 이 허브에서는 모델 선택을 먼저 하고, 필요한 세부 페이지로 내려갑니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Max Flow Min Cut, Flow with Lower Bound, Dynamic MST
- 함께 보면 좋은 레슨: Dynamic Connectivity, Planar Graph Duality, Proof and Invariants
- 다음에 볼 레슨: dynamic cut, planar min-cut, randomized graph algorithms

## 1. 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 특정 `s, t`가 주어져 있다 | Max Flow Min Cut을 먼저 본다 |
| 아무 두 그룹으로 나누는 최약 cut 값이 필요하다 | [Global Min Cut](pages/global-min-cut.md) |
| 구현은 짧아도 randomized 반복을 허용한다 | [Randomized Min Cut](pages/randomized-min-cut.md) |
| 모든 pair min cut 질의가 많다 | [Gomory-Hu Tree](pages/gomory-hu-tree.md) |
| dense graph에서 작은 cut만 보존하면 된다 | [Cut Sparsification](pages/cut-sparsification.md) |
| minimum cut family 자체를 다뤄야 한다 | [Cactus Representation](pages/cactus-representation.md), [Cut Cactus Applications](pages/cut-cactus-applications.md) |
| 문제 문장이 헷갈린다 | [Cut Model Map](pages/cut-model-map.md) |

## 2. 학습 순서

1. [Cut Model Map](pages/cut-model-map.md)에서 s-t/global/all-pairs/family/threshold cut을 구분합니다.
2. [Global Min Cut](pages/global-min-cut.md)에서 Stoer-Wagner의 deterministic baseline을 봅니다.
3. [Randomized Min Cut](pages/randomized-min-cut.md)은 Karger contraction과 확률 증폭을 비교용으로 읽습니다.
4. [Gomory-Hu Tree](pages/gomory-hu-tree.md)는 모든 pair min cut 값을 tree path minimum으로 압축합니다.
5. [Cut Sparsification](pages/cut-sparsification.md)은 작은 cut을 보존하는 certificate로 edge 수를 줄입니다.
6. [Global Min Cut Applications](pages/global-min-cut-applications.md), [Cactus Representation](pages/cactus-representation.md), [Cut Cactus Applications](pages/cut-cactus-applications.md)은 cut family와 응용 질의로 내려갑니다.

## 3. 쓰지 말아야 할 경우

- 그래프가 directed인데 무향 cut 구조를 그대로 쓰고 있습니다.
- source와 sink가 고정된 문제인데 global min cut을 돌리고 있습니다.
- global min cut 값 하나만 필요한데 Gomory-Hu Tree를 만들고 있습니다.
- pair-specific min cut 질의인데 global min cut cactus로 답하려고 합니다.
- weighted graph에서 unweighted sparse certificate나 Karger 기본형을 그대로 적용합니다.

## 4. 구현 전 체크리스트

- cut 대상이 `s-t`, global, all-pairs, family, threshold 중 무엇인가?
- 그래프가 무향이고 capacity가 nonnegative인가?
- 필요한 것이 cut value인지, partition인지, query structure인지 구분했는가?
- `O(N^3)` matrix, `N-1`번 max-flow, randomized 반복 중 무엇이 제한에 맞는가?
- multi-edge와 disconnected graph를 어떻게 처리할지 정했는가?

## 5. 연습 문제

이 허브의 연습 흐름은 [Practice Set](pages/practice-set.md)에 모읍니다. 적절한 h-contest 문제가 아직 없는 칸은 임의 ID를 넣지 않고 `TODO`로 둡니다.
