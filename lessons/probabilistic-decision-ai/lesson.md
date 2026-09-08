# Probabilistic Decision AI

Probabilistic Decision AI는 확률 전이, 숨은 상태, simulation 기반 탐색, bandit, online planning 평가를 하나의 reference 트랙으로 묶는 허브입니다. 이 계열은 대회 정답형 알고리즘과 heuristic/simulator planning이 섞이기 쉬우므로, 먼저 "정확 계산 문제인지, 근사 planning 문제인지"를 구분해야 합니다.

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 선택 뒤 무엇을 관측하는지부터 헷갈린다 | [Feedback Model Boundary](pages/feedback-model-boundary.md) |
| 큰 game tree에서 좋은 수를 시간 내에 고른다 | [Monte Carlo Tree Search](pages/monte-carlo-tree-search.md) |
| 상대 패나 hidden state처럼 관측 불가능한 정보가 있다 | [Imperfect Information Search](pages/imperfect-information-search.md) |
| action 뒤 observation만 받는 확률 모델이다 | [Partially Observable MDP](pages/pomdp.md) |
| POMDP policy를 belief point에서 근사한다 | [Point-Based Value Iteration](pages/point-based-value-iteration.md) |
| simulator와 particle belief로 online action을 고른다 | [POMCP](pages/pomcp.md) |
| arm reward 확률을 모른 채 탐색/활용을 조절한다 | [Bayesian Bandits](pages/bayesian-bandits.md) |
| planning algorithm의 시간/점수 tradeoff를 평가한다 | [Online Planning Evaluation](pages/online-planning-evaluation.md) |

## 전이표가 주어진 경우

| 종료·평가 조건 | 계산 방법 |
| --- | --- |
| 남은 턴 수가 고정됨 | [Finite Horizon MDP](pages/finite-horizon-mdp.md) |
| `0 <= gamma < 1`인 할인 보상 | [Discounted Value Iteration](pages/discounted-value-iteration.md) |
| 상태별 행동이 고정됨 | [Policy Evaluation and Improvement](pages/policy-evaluation-and-improvement.md) |
| absorbing goal까지 기대 비용 | [Stochastic Shortest Path](pages/stochastic-shortest-path.md) |
| 전이표 없이 sample만 관측함 | [Exact Model vs Sampling](pages/exact-model-vs-sampling.md) |

Finite horizon, 할인 무한 horizon, 목표 도달 비용은 종료·수렴 조건이 다릅니다. `gamma = 1`이라는 이유만으로 할인 모델의 반복 계산을 그대로 적용할 수 없습니다. 상태가 숨겨져 있으면 관측값만 상태로 쓰지 말고 belief 갱신을 먼저 정합니다.

## 연습

[로컬 연습](pages/practice-set.md)에서 입력과 검증 기준을 확인합니다.
