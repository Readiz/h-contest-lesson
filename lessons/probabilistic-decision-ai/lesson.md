# Probabilistic Decision AI

Probabilistic Decision AI는 확률 전이, 숨은 상태, simulation 기반 탐색, bandit, online planning 평가를 하나의 reference 트랙으로 묶는 허브입니다. 이 계열은 대회 정답형 알고리즘과 heuristic/simulator planning이 섞이기 쉬우므로, 먼저 "정확 계산 문제인지, 근사 planning 문제인지"를 구분해야 합니다.

이 허브는 Stochastic Decision Process, MCTS, Imperfect Information Search, POMDP, PBVI, POMCP, Bayesian Bandits, Online Planning Evaluation을 하나의 흐름으로 연결합니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Probability and Expected Value, Dynamic Programming, Minimax and Alpha-Beta, Heuristic
- 함께 보면 좋은 레슨: Game Theory Applications, Online Convex Optimization, Testing and Stress
- 다음에 볼 레슨: Online Planning Evaluation, Black-Box Linear Algebra, Game AI evaluation

## 1. 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 선택 뒤 무엇을 관측하는지부터 헷갈린다 | [Feedback Model Boundary](pages/feedback-model-boundary.md) |
| 상태와 action, 확률 전이표가 모두 주어진다 | [Stochastic Decision Process](pages/stochastic-decision-process.md) |
| finite horizon, discounted MDP, policy evaluation, SSP를 구분해야 한다 | [Finite Horizon MDP](pages/finite-horizon-mdp.md), [Discounted Value Iteration](pages/discounted-value-iteration.md), [Stochastic Shortest Path](pages/stochastic-shortest-path.md) |
| 큰 game tree에서 좋은 수를 시간 내에 고른다 | [Monte Carlo Tree Search](pages/monte-carlo-tree-search.md) |
| 상대 패나 hidden state처럼 관측 불가능한 정보가 있다 | [Imperfect Information Search](pages/imperfect-information-search.md) |
| action 뒤 observation만 받는 확률 모델이다 | [Partially Observable MDP](pages/pomdp.md) |
| POMDP policy를 belief point에서 근사한다 | [Point-Based Value Iteration](pages/point-based-value-iteration.md) |
| simulator와 particle belief로 online action을 고른다 | [POMCP](pages/pomcp.md) |
| arm reward 확률을 모른 채 탐색/활용을 조절한다 | [Bayesian Bandits](pages/bayesian-bandits.md) |
| planning algorithm의 시간/점수 tradeoff를 평가한다 | [Online Planning Evaluation](pages/online-planning-evaluation.md) |
| 전체 경계가 헷갈린다 | [Decision AI Model Map](pages/decision-ai-model-map.md), [Feedback Model Boundary](pages/feedback-model-boundary.md) |

## 2. 정확 알고리즘과 reference/heuristic 경계

| 성격 | 대표 페이지 | 공개 의미 |
| --- | --- | --- |
| 정확 DP/선형방정식 | finite horizon MDP, policy evaluation, SSP | 대회 정답형 가능 |
| sampling 기반 탐색 | MCTS, POMCP, Bayesian Bandits | heuristic/AI reference 성격 |
| belief 근사 | POMDP, PBVI | 작은 모델 또는 근사 planning |
| 평가 방법 | Online Planning Evaluation | 알고리즘보다 실험 설계 중심 |

`published`라고 해서 모든 하위 페이지가 완전한 구현 강의라는 뜻은 아닙니다. 이 트랙은 `reference` 성격이 강하지만, [Practice Set](pages/practice-set.md)은 feedback 모델 분류와 finite-horizon MDP의 backward Bellman DP를 로컬 완결형 연습으로 제공합니다.
