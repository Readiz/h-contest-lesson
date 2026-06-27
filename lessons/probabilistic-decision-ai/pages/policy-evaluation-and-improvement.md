# Policy Evaluation and Improvement

Policy Evaluation은 각 상태에서 행동이 이미 정해졌을 때 그 policy의 기대값을 계산하는 과정입니다. 최적 action을 고르는 Bellman optimality와 달리, max/min이 사라져 선형 방정식이나 반복 평가로 다룰 수 있습니다.

## 1. 고정 Policy의 Bellman 식

policy `pi(s)`가 고정되어 있으면 아래 식이 됩니다.

```text
V_pi(s) = sum P(s' | s, pi(s)) * (reward(s,pi(s),s') + gamma * V_pi(s'))
```

SSP 비용 모델에서는 reward 대신 cost를 쓰고, terminal value를 0으로 고정합니다.

## 2. 선형 방정식 관점

discounted setting에서 식을 왼쪽으로 옮기면 아래 형태입니다.

```text
V(s) - gamma * sum P(s'|s,pi(s)) * V(s') = expectedReward(s,pi(s))
```

상태 수가 작으면 Gaussian elimination으로 정확하게 풀 수 있습니다. 상태 수가 크고 sparse하면 반복 평가가 더 현실적입니다.

## 3. Policy Improvement

현재 policy의 value를 구한 뒤, 각 상태에서 더 좋은 action이 있는지 확인합니다.

```text
newPi(s) = argmax_a sum P(s'|s,a) * (reward + gamma * V_pi(s'))
```

policy가 바뀌지 않으면 policy iteration이 종료됩니다.

## 4. Value Iteration과의 차이

| 기준 | Value Iteration | Policy Iteration |
| --- | --- | --- |
| 한 step | Bellman optimality로 value 직접 갱신 | policy 평가 후 개선 |
| policy | 결과로 복원 가능 | 중간에 명시적으로 유지 |
| 작은 상태 수 | 간단함 | 빠르게 안정될 수 있음 |
| linear solve | 필요 없음 | policy evaluation에 쓸 수 있음 |

## 5. 자주 하는 실수

- 고정 policy 평가인데 max/min을 계속 취합니다.
- policy improvement 후 value를 다시 평가하지 않습니다.
- 같은 expected value에서 tie-break가 흔들려 policy가 불필요하게 바뀝니다.
- terminal state의 policy를 의미 있게 설정하려고 합니다.
- `gamma = 1` 순환 문제에서 선형 시스템의 해가 항상 존재한다고 가정합니다.
