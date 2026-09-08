# Reinforcement Learning Basics

Reinforcement Learning Basics는 상태, 행동, 보상, 전이 확률이 있는 환경에서 policy를 평가하거나 개선하는 기본 틀입니다. contest에서는 실제 학습보다 Markov Decision Process를 반복 갱신으로 푸는 모델링, finite-horizon decision, exploration과 exploitation 구분을 위해 등장합니다.

## 문제 신호

| 문제 표현 | RL 관점 |
| --- | --- |
| 상태와 행동마다 보상과 전이가 있다 | MDP |
| 현재 정책의 기대 보상을 구한다 | policy evaluation |
| 최적 행동을 반복 갱신한다 | value iteration |
| model은 모르고 sample만 받는다 | model-free RL |
| exploration과 exploitation 균형이 필요 | bandit or RL |

대회 문제에서는 transition table이 주어지는 경우가 많습니다. 그러면 RL이라는 이름보다 MDP DP로 풀면 됩니다. sample만 주어지는 interactive나 simulator 문제에서 학습 관점이 중요해집니다.

## Bellman 식

할인율 `gamma`가 있고 보상 `r(s, a, s')`가 주어질 때 최적 value는 아래 식을 만족합니다.

```text
V(s) = max_a sum_{s'} P(s' | s, a) * (r(s,a,s') + gamma * V(s'))
```

finite horizon이면 시간 `t`를 상태에 넣거나 뒤에서 앞으로 DP를 합니다. infinite discounted case에서는 value iteration으로 수렴시킬 수 있습니다.

## 전이표가 있는 계산

할인 모델의 반복 갱신 구현과 오차 조건은 [Discounted Value Iteration](discounted-value-iteration.md)에 둡니다. Sample만 관측하는 경우에는 이 코드에 필요한 전이 확률표가 없다는 차이가 있습니다.

## Policy Evaluation과 Policy Improvement

policy가 고정되어 있으면 max를 취하지 않고 policy가 선택한 action의 기대값만 계산합니다.

```text
V_pi(s) = E[r + gamma * V_pi(s')]
```

policy iteration은 두 단계를 반복합니다.

1. 현재 policy의 value를 평가한다.
2. 각 상태에서 더 좋은 action으로 policy를 바꾼다.

상태와 행동 수가 작고 transition table이 명확하면 policy iteration이 value iteration보다 빨리 안정될 수 있습니다.

## Q-value

`Q(s, a)`는 상태 `s`에서 action `a`를 바로 선택했을 때의 기대값입니다.

```text
Q(s,a) = sum P(s'|s,a) * (r + gamma * max_b Q(s',b))
```

model-free Q-learning은 transition probability를 모를 때 sample로 이 값을 갱신합니다. 하지만 offline judge에서는 sample noise 때문에 exact answer를 내기 어려우므로 보통 model이 주어지는 MDP로 바꿔 풉니다.

## 작은 예시

```text
state 0: 안전한 행동 -> reward 1, state 0
state 0: 위험한 행동 -> 50% reward 3, 50% reward -2
gamma = 0.9
```

한 라운드 보상 평균만 보면 위험한 행동의 기대 보상은 `0.5`입니다. 장기 value까지 고려하면 안전한 행동이 계속 `1`을 주므로 더 좋아질 수 있습니다. Bellman update는 이런 장기 효과를 현재 action 선택에 반영합니다.

## Bandit, MDP, POMDP 구분

| 모델 | 상태 | 전이 | 관측 |
| --- | --- | --- | --- |
| Bandit | 거의 없음 | action별 보상만 | 선택한 보상 |
| MDP | 완전 관측 | `P(s'|s,a)` | 다음 상태 |
| POMDP | hidden state | transition + observation | observation |

상태가 없거나 독립 action만 반복하면 bandit입니다. 상태가 완전히 보이면 MDP, 숨겨져 있으면 POMDP입니다.

## 시간 복잡도 감각

| 작업 | 시간 |
| --- | ---: |
| value iteration 1회 | `O(total transitions)` |
| finite horizon DP | `O(T * total transitions)` |
| policy evaluation iterative | `O(iterations * total transitions)` |
| exact linear solve evaluation | 상태 수에 따라 cubic 가능 |

transition이 sparse하면 edge list로 저장합니다. dense matrix를 만들면 작은 상태 수를 제외하고 메모리가 먼저 커집니다.

## 자주 하는 실수

1. reward가 state에 붙는지 transition에 붙는지 섞는다.
2. terminal state에서 future value를 계속 더한다.
3. 확률 합이 1이 아닌 action을 그대로 사용한다.
4. finite horizon 문제를 infinite discounted 문제처럼 반복한다.
5. hidden state가 있는데 MDP value iteration으로 푼다.
6. model-free sample 학습을 exact judge 답안처럼 사용한다.
