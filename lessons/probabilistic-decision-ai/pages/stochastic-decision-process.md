# Stochastic Decision Process

Stochastic Decision Process는 상태, 행동, 확률 전이, 보상 또는 비용이 있는 문제를 Bellman 식으로 모델링하는 확률적 의사결정 허브입니다. Markov Decision Process, Reinforcement Learning Basics, Stochastic Shortest Path는 서로 다른 독립 알고리즘이라기보다 같은 Bellman 모델의 다른 조건입니다.

이 허브는 먼저 종료 조건과 전이 정보가 무엇인지 구분하고, 그에 맞는 계산 방법을 고르게 합니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 확률과 기대값, 동적 계획법, 그래프 상태 모델링
- 함께 보면 좋은 레슨: Monte Carlo Tree Search, Minimax와 Alpha-Beta, Sparse Linear Systems
- 다음에 볼 레슨: POMDP, Bayesian Bandits, POMCP, online planning evaluation

## 1. 모델 선택 표

| 모델 | 종료 조건 | 전이 정보 | 대표 풀이 |
| --- | --- | --- | --- |
| Finite horizon MDP | 남은 턴 수 | 전이표 있음 | 뒤에서 앞으로 layer DP |
| Discounted MDP | `0 <= gamma < 1` | 전이표 있음 | 오차 기준이 있는 value iteration |
| Fixed policy evaluation | 행동 고정 | 전이표 있음 | 선형 방정식 또는 반복 평가 |
| Stochastic Shortest Path | absorbing goal | 전이표 있음 | proper policy 검사 + Bellman/linear solve |
| Model-free RL | 종료/discount 다양 | sample만 관측 | 대회 정답형보다 simulator/학습 문제에 가까움 |

모두 Bellman 식을 쓰지만, 수렴 조건과 출력의 의미가 다릅니다. 같은 value iteration 코드처럼 보여도 finite horizon, discounted infinite horizon, absorbing hitting cost를 섞으면 오답이 됩니다.

## 2. 읽는 순서

1. [Finite Horizon MDP](finite-horizon-mdp.md)에서 정확한 layer DP를 먼저 봅니다.
2. [Discounted Value Iteration](discounted-value-iteration.md)에서 `gamma < 1`일 때의 반복 갱신과 오차를 다룹니다.
3. [Policy Evaluation and Improvement](policy-evaluation-and-improvement.md)에서 고정 policy와 policy iteration을 분리합니다.
4. [Stochastic Shortest Path](stochastic-shortest-path.md)은 absorbing goal과 무한 기대 비용 가능성이 있을 때 읽습니다.
5. [Exact Model vs Sampling](exact-model-vs-sampling.md)에서 MDP DP와 model-free RL을 구분합니다.

## 3. 쓰지 말아야 할 경우

- 상태가 완전히 관측되지 않으면 POMDP나 belief state가 먼저입니다.
- 전이표가 없고 simulator sample만 있으면 exact value iteration 문제로 취급하면 안 됩니다.
- `gamma = 1`이고 terminal도 없는데 임의 반복 횟수만으로 수렴을 기대하면 안 됩니다.
- 출력이 policy인지 value인지, 시작 상태 하나의 답인지 전체 상태의 답인지 정하지 않았습니다.
- 확률 합, terminal 처리, reward/cost 부호를 검증하지 않았습니다.

## 4. 구현 전 체크리스트

- horizon, discount, absorbing terminal 중 어느 조건이 수렴을 보장하는가?
- 각 action의 transition probability 합이 1인가?
- reward가 state, action, transition 중 어디에 붙는가?
- terminal state에서 future value를 더하지 않는가?
- 오차 허용이 있으면 반복 종료 기준이나 반복 횟수를 설명할 수 있는가?
- fixed policy라면 max/min을 제거하고 선형 방정식으로 평가할 수 있는가?

## 5. 연습 문제

이 허브의 연습 흐름은 [Stochastic Decision Practice Set](stochastic-decision-practice-set.md)에 모읍니다. 실제 h-contest 문제가 없는 칸은 임의 ID를 넣지 않고 `TODO`로 둡니다.
