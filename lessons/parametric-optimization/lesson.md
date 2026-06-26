# Parametric Optimization

Parametric Optimization은 제약이나 답을 직접 상태에 넣기 어려울 때, 하나의 parameter를 고정한 더 쉬운 문제를 반복해서 풀어 원래 답을 복원하는 최적화 트랙입니다. Alien Optimization, Parametric DP, Fractional Programming DP, Lagrangian Relaxation은 별개의 카드라기보다 같은 도구 상자의 다른 장입니다.

이 허브는 문제를 보고 어떤 변환을 골라야 하는지 먼저 정리한 뒤, 필요한 세부 페이지로 내려갑니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 이분 탐색, 동적 계획법, Convex DP Modeling, Monge와 SMAWK
- 함께 보면 좋은 레슨: Convex Hull Trick, Min-Plus Convolution, Flow with Lower Bound
- 다음에 볼 레슨: Online Convex Optimization, Convex Cost Flow, primal-dual methods

## 1. 문제 신호와 선택 기준

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 답 `x`를 고정하면 가능 여부가 단조적이다 | [Feasibility and Answer Search](pages/feasibility-and-answer-search.md) |
| 정확히 `K`개를 골라야 하는데 `K` 차원이 너무 크다 | [Exact-K Alien Optimization](pages/exact-k-alien-optimization.md) |
| 평균, 밀도, 비용 대비 효율 같은 비율 목적식이다 | [Fractional Objectives](pages/fractional-objectives.md) |
| 여러 제약을 penalty와 dual variable로 분리해야 한다 | [General Lagrangian Relaxation](pages/general-lagrangian-relaxation.md) |
| count가 흔들리거나 breakpoint 보정이 필요하다 | [Tie-breaking and Breakpoints](pages/tie-breaking-and-breakpoints.md) |

핵심 질문은 하나입니다.

```text
parameter를 고정했을 때 원래보다 쉬운 DP, greedy, shortest path, flow oracle이 되는가?
```

답이 아니면 parametric trick을 붙여도 풀이가 쉬워지지 않습니다.

## 2. 공통 변환 흐름

1. 원래 objective와 어려운 제약을 분리합니다.
2. 제약 또는 답 후보를 `lambda`, `x`, `penalty` 같은 parameter로 둡니다.
3. parameter가 고정된 subproblem을 풉니다.
4. subproblem의 response가 parameter에 대해 단조인지 확인합니다.
5. 이분 탐색, breakpoint 탐색, 또는 dual update로 parameter를 조정합니다.
6. relaxed score에서 penalty를 되돌려 원래 objective를 복원합니다.

## 3. 쓰지 말아야 할 경우

- parameter를 고정해도 상태 수나 제약 수가 줄지 않습니다.
- response가 단조가 아니고, breakpoint를 직접 다룰 방법도 없습니다.
- 동점 처리에 따라 count가 불안정하게 바뀌는데 tie-break 규칙을 세울 수 없습니다.
- 실수 이분 탐색 오차가 정답 판정 기준보다 커질 위험이 있습니다.
- 문제는 단순 feasibility인데 불필요하게 Lagrangian dual을 도입하고 있습니다.

## 4. 학습 순서

1. [Feasibility and Answer Search](pages/feasibility-and-answer-search.md)에서 answer binary search와 penalty DP의 공통 구조를 봅니다.
2. [Exact-K Alien Optimization](pages/exact-k-alien-optimization.md)에서 `count`를 함께 들고 다니는 이유를 확인합니다.
3. [Fractional Objectives](pages/fractional-objectives.md)에서 `value - x * weight` 변환과 수치 오차를 다룹니다.
4. [Tie-breaking and Breakpoints](pages/tie-breaking-and-breakpoints.md)에서 같은 relaxed score가 여러 count를 만들 때의 처리 기준을 봅니다.
5. [General Lagrangian Relaxation](pages/general-lagrangian-relaxation.md)은 여러 제약이나 flow/greedy oracle로 확장할 때 읽습니다.

## 5. 구현 전 체크리스트

- 고정 parameter에서 어떤 차원이 사라지는가?
- response는 증가, 감소, 유지 중 어느 방향으로 움직이는가?
- 동점일 때 count를 큰 쪽으로 고를지 작은 쪽으로 고를지 정했는가?
- 최종 답에서 `lambda * K` 또는 `x * weight` 보정을 반대로 하지 않았는가?
- 정수 parameter인지 실수 parameter인지, 필요한 반복 횟수와 오차가 무엇인지 정했는가?

## 6. 연습 문제

이 허브의 실제 연습 흐름은 [Practice Set](pages/practice-set.md)에 모읍니다. 적절한 h-contest 문제가 아직 없는 칸은 임의 ID를 넣지 않고 `TODO`로 둡니다.
