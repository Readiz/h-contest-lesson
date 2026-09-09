# Probabilistic Decision AI

Probabilistic Decision AI는 확률 전이, 숨은 상태, simulation 기반 탐색, bandit, online planning 평가를 하나의 reference 트랙으로 묶는 허브입니다. 이 계열은 대회 정답형 알고리즘과 heuristic/simulator planning이 섞이기 쉬우므로, 먼저 "정확 계산 문제인지, 근사 planning 문제인지"를 구분해야 합니다.

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
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
| `0 <= gamma < 1`인 할인 보상 | [Discounted Value Iteration](pages/finite-horizon-mdp.md) |
| 상태별 행동이 고정됨 | [Policy Evaluation and Improvement](pages/finite-horizon-mdp.md) |
| absorbing goal까지 기대 비용 | [Stochastic Shortest Path](pages/stochastic-shortest-path.md) |
| 전이표 없이 sample만 관측함 | 아래 전이표와 표본의 차이 |

Finite horizon, 할인 무한 horizon, 목표 도달 비용은 종료·수렴 조건이 다릅니다. `gamma = 1`이라는 이유만으로 할인 모델의 반복 계산을 그대로 적용할 수 없습니다. 상태가 숨겨져 있으면 관측값만 상태로 쓰지 말고 belief 갱신을 먼저 정합니다.

## 연습

[로컬 연습](pages/finite-horizon-mdp.md)에서 입력과 검증 기준을 확인합니다.

## 전이표와 표본의 차이

전이·보상표가 있으면 Bellman 합을 직접 계산합니다. simulator만 있으면 전이와 보상을 표본으로 추정하므로 통계 오차가 남습니다. 표본에서 모델을 추정하는 model-based 접근과 Q-value를 직접 갱신하는 model-free 접근 모두 가능합니다. 표본 문제를 임의로 정확한 전이표가 주어진 문제로 바꾸지 않습니다.

## 네 가지 관측 모델

| 모델 | 선택 뒤 보이는 것 | 대표 접근 | 착각하면 생기는 문제 |
| --- | --- | --- | --- |
| Full-information | 모든 action의 loss/reward 또는 gradient | OCO, multiplicative weights | bandit 문제를 너무 쉽게 품 |
| Bandit feedback | 선택한 action의 결과만 | UCB, Thompson Sampling, EXP3 | 관측하지 않은 loss를 안다고 가정 |
| Simulator feedback | 선택 sequence의 sampled trajectory | MCTS, rollout evaluation | single seed score로 정책을 고름 |
| Hidden-state observation | 실제 state가 아니라 observation | POMDP, belief update, POMCP | hidden state를 직접 알고 행동함 |

첫 질문은 "정답을 계산할 model table이 있는가, 아니면 선택한 결과만 관측하는가"입니다. 전이확률과 보상표가 모두 주어지면 MDP DP가 후보이고, 선택한 arm의 결과만 보이면 bandit입니다. simulator만 있으면 exact Bellman update보다 rollout 평가와 sampling budget을 먼저 봅니다.

## 판독 순서

1. 매 라운드 이후 모든 후보의 cost가 공개되는지 확인합니다.
2. 공개되지 않는다면 선택한 action의 reward만 관측하는지, trajectory sample을 받는지 구분합니다.
3. state가 완전히 보이는지, observation만 보이는지 확인합니다.
4. model table이 주어지는지, generative simulator만 호출 가능한지 확인합니다.
5. judge가 exact answer를 요구하는지, policy 성능을 평가하는지 확인합니다.

이 다섯 질문에 답하지 못한 상태에서 OCO update, bandit posterior, MCTS rollout, POMDP belief를 고르면 대부분 모델을 잘못 읽은 것입니다.

## 작은 예시

### Full-information experts

```text
매일 하나의 expert를 선택한다.
하루가 끝나면 모든 expert의 loss vector가 공개된다.
목표는 내 누적 loss와 best expert 누적 loss의 차이를 줄이는 것이다.
```

이 경우에는 선택하지 않은 expert의 loss도 알 수 있으므로 multiplicative weights 같은 full-information update를 쓸 수 있습니다. exploration을 별도로 넣지 않아도 update에 필요한 loss vector가 있습니다.

### Bandit arms

```text
매일 하나의 광고를 선택한다.
클릭 여부는 선택한 광고에 대해서만 관측된다.
목표는 총 클릭 수를 늘리는 것이다.
```

선택하지 않은 광고의 reward는 없습니다. full-information loss vector를 0으로 채우면 모델을 바꾼 것이 아니라 잘못된 estimator를 만든 것입니다. posterior나 confidence bound처럼 불확실성을 다루는 장치가 필요합니다.

### Simulator planning

```text
현재 state에서 action을 고르면 simulator가 다음 state와 reward를 sample한다.
시간 제한 안에서 action 하나를 출력해야 한다.
```

전이표 전체를 알 수 없다면 exact value iteration이 아니라 rollout 기반 planning입니다. MCTS를 쓰더라도 seed, iteration budget, deadline miss를 같이 관리해야 합니다.

### Hidden-state observation

```text
상대의 손패는 숨겨져 있고, 공개 action과 observation만 볼 수 있다.
```

node를 실제 hidden state로 만들면 정보 누출이 생깁니다. 통계와 policy는 observation history 또는 belief 단위로 관리해야 합니다.

## 경계 반례

| 잘못 읽은 문장 | 왜 틀렸는가 | 바른 분류 |
| --- | --- | --- |
| "선택하지 않은 arm은 reward 0으로 둔다" | 관측되지 않은 값을 만든 것 | bandit feedback |
| "simulator를 많이 돌려 평균을 내면 exact DP다" | sample 평균은 근사이며 variance가 남음 | simulator feedback |
| "관측값을 state로 두면 POMDP가 MDP가 된다" | 같은 observation 뒤에 여러 hidden state가 가능 | hidden-state observation |
| "loss vector가 공개되지만 선택한 loss만 update한다" | 사용할 수 있는 정보를 버림 | full-information |
