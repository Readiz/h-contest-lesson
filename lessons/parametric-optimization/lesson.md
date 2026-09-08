# Parametric Optimization

Parametric Optimization은 제약이나 답을 직접 상태에 넣기 어려울 때, 하나의 parameter를 고정한 더 쉬운 문제를 반복해서 풀어 원래 답을 복원하는 최적화 트랙입니다. Alien Optimization, Parametric DP, Fractional Programming DP, Lagrangian Relaxation은 별개의 카드라기보다 같은 도구 상자의 다른 장입니다.

이 허브는 문제를 보고 어떤 변환을 골라야 하는지 먼저 정리한 뒤, 필요한 세부 페이지로 내려갑니다.

## 문제 신호와 선택 기준

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 답 `x`를 고정하면 가능 여부가 단조적이다 | 아래 답 이분 탐색 설명 |
| 정확히 `K`개를 골라야 하는데 `K` 차원이 너무 크다 | [Exact-K Alien Optimization](pages/exact-k-alien-optimization.md) |
| 평균, 밀도, 비용 대비 효율 같은 비율 목적식이다 | [Fractional Objectives](pages/fractional-objectives.md) |
| 여러 제약을 penalty와 dual variable로 분리해야 한다 | [General Lagrangian Relaxation](pages/general-lagrangian-relaxation.md) |

핵심 질문은 하나입니다.

```text
parameter를 고정했을 때 원래보다 쉬운 DP, greedy, shortest path, flow oracle이 되는가?
```

답이 아니면 parametric trick을 붙여도 풀이가 쉬워지지 않습니다.

## 연습 문제

이 허브의 실제 연습 흐름은 [Practice Set](pages/practice-set.md)에 모읍니다. Practice Set은 maximum average subarray의 `value - x * weight` 판정 trace와 로컬 구현을 대표 흐름으로 제공합니다.

## 답 자체를 이분 탐색할 때

가능 여부가 true에서 false로 한 번만 바뀌면 answer search를 사용합니다. 비율은 분모 양수 조건에서 value-x*weight 판정으로 바꾸며 [Fractional Programming DP](https://h.readiz.com/learn/parametric-optimization/fractional-objectives)의 최대 평균 예제를 따릅니다. 볼록해 보인다는 이유만으로 삼분 탐색을 적용하지 않고 단봉성을 증명합니다.
