# Graph Cut Structures

Graph Cut Structures는 s-t min cut 이후의 무향 cut 구조를 하나의 학습 경로로 묶는 허브입니다. Global Min Cut, Gomory-Hu Tree, Cut Sparsification, Randomized Min Cut, Cactus Representation은 모두 "어떤 cut 정보를 얼마나 많이, 어떤 형태로 보존할 것인가"라는 같은 질문에서 출발합니다.

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 특정 `s, t`가 주어져 있다 | [Max Flow, Min Cut, Bipartite Matching](https://h.readiz.com/learn/max-flow-min-cut) |
| 아무 두 그룹으로 나누는 최약 cut 값이 필요하다 | [Global Min Cut](pages/global-min-cut.md) |
| 구현은 짧아도 randomized 반복을 허용한다 | [Randomized Min Cut](pages/randomized-min-cut.md) |
| 모든 pair min cut 질의가 많다 | [Gomory-Hu Tree](pages/gomory-hu-tree.md) |
| dense graph에서 작은 cut만 보존하면 된다 | [Cut Sparsification](pages/cut-sparsification.md) |
| minimum cut family 자체를 다뤄야 한다 | [Cactus Representation](pages/cactus-representation.md) |

## 입력과 출력의 구분

이 경로의 global cut·Gomory-Hu·cactus는 무향 cut을 대상으로 합니다. 값 하나가 필요한지, 실제 partition이 필요한지, 모든 쌍의 값인지, global minimum cut family인지 먼저 구분합니다. Gomory-Hu는 모든 쌍의 값을, cut cactus는 global minimum partition들을 압축합니다.

Weighted capacity와 무가중치 multigraph를 구분합니다. Karger의 기본형이나 forest-layer certificate의 조건을 weighted 입력에 그대로 옮기지 않습니다. Randomized 반복을 쓰는 페이지에서는 실패 확률과 반복 비용도 함께 확인합니다.

## 연습

[로컬 연습](pages/global-min-cut.md)에서 입력과 검증 기준을 확인합니다.

## 두 cut 모델의 검산



### Gomory-Hu Query Check

정점 4개 그래프에서 Gomory-Hu Tree를 만든 뒤, 모든 pair에 대해 원래 graph의 max-flow 값과 tree path minimum이 같은지 비교합니다.

### Karger Repetition Experiment

cycle graph와 complete graph에서 Karger contraction을 여러 seed로 반복하고, trial 수가 늘어날 때 best cut 값이 어떻게 안정되는지 확인합니다.
