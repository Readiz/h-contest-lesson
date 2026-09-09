# MDP: 유한 지평, 할인과 정책 반복

Finite Horizon MDP는 남은 턴 수가 정해져 있을 때의 확률적 의사결정 문제입니다. 수렴 반복이 아니라 시간 축이 줄어드는 DP이므로, 가능한 경우 가장 먼저 의심해야 하는 모델입니다.


코드는 종료 보상 0인 유한 지평 모델입니다. turns>=0, 유효한 nextState, 각 action의 비음수 확률 합 1, 유한 보상을 전제로 합니다. 행동이 없는 상태는 이후 보상 0으로 처리합니다. 일반 terminal reward가 있으면 초기 value와 terminal 갱신을 함께 바꿉니다.

## 기본 식

남은 턴이 `t`이고 현재 상태가 `s`일 때의 최적 기대 보상을 `dp[t][s]`라고 둡니다.

```text
dp[0][s] = terminal reward or 0
dp[t][s] = max_a sum P(s' | s, a) * (reward(s,a,s') + dp[t-1][s'])
```

최소 비용 문제라면 `max`를 `min`으로 바꿉니다.

## 구현 골격

```cpp compile-check
#include <algorithm>
#include <limits>
#include <vector>
using namespace std;

struct Transition {
    int nextState = 0;
    double probability = 0.0;
    double reward = 0.0;
};

using Action = vector<Transition>;

vector<double> finiteHorizonValue(
    const vector<vector<Action>>& actions,
    int turns
) {
    int n = (int)actions.size();
    vector<double> value(n, 0.0);
    vector<double> nextValue(n, 0.0);

    for (int left = 1; left <= turns; ++left) {
        for (int state = 0; state < n; ++state) {
            if (actions[state].empty()) {
                nextValue[state] = 0.0;
                continue;
            }
            double best = -numeric_limits<double>::infinity();
            for (const Action& action : actions[state]) {
                double candidate = 0.0;
                for (const Transition& transition : action) {
                    candidate += transition.probability *
                        (transition.reward + value[transition.nextState]);
                }
                best = max(best, candidate);
            }
            nextValue[state] = best;
        }
        value.swap(nextValue);
    }

    return value;
}
```

## Discounted MDP와 다른 점

| 기준 | Finite horizon | Discounted infinite horizon |
| --- | --- | --- |
| 종료 | 턴 수가 0이 됨 | `gamma < 1` 수렴 |
| 정확도 | layer 수만큼 정확 계산 | 오차 기준 필요 |
| 상태 | 보통 `turn`을 포함 | stationary value |
| 구현 | 뒤에서 앞으로 DP | 반복 수렴 또는 contraction |

## 할인 무한 지평과 Value Iteration

Markov Decision Process(MDP)는 상태, 행동, 확률 전이, 보상으로 이루어진 의사결정 모델입니다. 단순 확률 DP가 "정해진 전이의 기대값"을 계산한다면, MDP는 각 상태에서 어떤 행동을 고를지까지 함께 최적화합니다.


유한 상태·행동, 유계 보상, 행동별 확률 합 1과 0<=gamma<1을 전제로 합니다. Bellman 연산자는 gamma 수축입니다. delta=||V_new-V_old||∞라면 반환 V_new의 오차는 gamma*delta/(1-gamma) 이하입니다. gamma=0이면 한 번 갱신으로 충분합니다. 반복 횟수만 정해 반환한 값은 정확해가 아닙니다.

### 문제 신호

| 문제 표현 | MDP 관점 |
| --- | --- |
| 상태마다 여러 행동 중 하나를 선택 | action optimization |
| 행동 결과가 확률적으로 갈림 | stochastic transition |
| 장기 기대 보상을 최대화 | value function |
| 현재 상태만 알면 미래 분포가 결정 | Markov property |
| simulation이 아니라 정확/근사 기대값 필요 | value iteration |

선택이 없으면 Markov chain 또는 기대값 DP입니다. 상대 플레이어가 있으면 game tree나 stochastic game으로 확장됩니다.

### Bellman Optimality Equation

discount factor `gamma`가 있는 무한 horizon MDP에서는 각 상태 가치가 아래 식을 만족합니다.

```text
V[s] = max over action a:
    reward(s, a) + gamma * sum P(s -> t | a) * V[t]
```

최소 비용 문제라면 `max`를 `min`으로 바꾸고 보상 대신 비용을 씁니다.

### Value Iteration

Value iteration은 모든 상태 값을 반복해서 갱신합니다. `gamma < 1`이면 수렴성이 좋아집니다.

```cpp compile-check
#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>
using namespace std;

struct TransitionMdp {
    int to = 0;
    double probability = 0.0;
};

struct ActionMdp {
    double reward = 0.0;
    vector<TransitionMdp> transitions;
};

vector<double> valueIteration(
    const vector<vector<ActionMdp>>& actions,
    double gamma,
    int iterations
) {
    int n = (int)actions.size();
    vector<double> value(n, 0.0);

    for (int iter = 0; iter < iterations; ++iter) {
        vector<double> nextValue = value;
        for (int state = 0; state < n; ++state) {
            if (actions[state].empty()) {
                continue;
            }

            double best = -numeric_limits<double>::infinity();
            for (const ActionMdp& action : actions[state]) {
                double candidate = action.reward;
                for (const TransitionMdp& transition : action.transitions) {
                    candidate += gamma * transition.probability * value[transition.to];
                }
                best = max(best, candidate);
            }
            nextValue[state] = best;
        }
        value.swap(nextValue);
    }

    return value;
}
```

반복 횟수는 오차 허용 기준으로 정합니다. 실전에서는 `max |newV - oldV|`가 충분히 작아질 때 멈추기도 합니다.

### Policy

Policy는 각 상태에서 고를 행동을 정한 함수입니다.

```text
policy[state] = action
```

가치만 구하고 끝나는 문제가 아니라 실제 행동 sequence를 출력해야 하면, value update에서 best action도 같이 저장합니다.

### Discount와 종료 상태

MDP에서 무한히 보상을 받을 수 있으면 값이 발산할 수 있습니다.

| 모델 | 처리 |
| --- | --- |
| finite horizon | 남은 step 수로 제한 |
| absorbing terminal | terminal state value를 고정 |
| discounted infinite horizon | `0 <= gamma < 1` 사용 |
| average reward | 더 전문적인 알고리즘 필요 |

대회 문제에서는 finite horizon이나 absorbing state가 가장 흔합니다.

### 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| value iteration 1회 | `O(total transitions over actions)` |
| `K`번 반복 | `O(K * transitions)` |
| finite horizon `T` | `O(T * transitions)` |
| policy 저장 | `O(states)` |

transition list가 dense하면 상태 수의 제곱이 됩니다. sparse representation을 유지하는 편이 좋습니다.

## 고정 정책 평가와 개선

Policy Evaluation은 각 상태에서 행동이 이미 정해졌을 때 그 policy의 기대값을 계산하는 과정입니다. 최적 action을 고르는 Bellman optimality와 달리, max/min이 사라져 선형 방정식이나 반복 평가로 다룰 수 있습니다.


할인 정책 반복은 0<=gamma<1과 유계 보상에서 다룹니다. 선형 해법도 실수 연산이면 반올림 오차가 있습니다. 동률에는 기존 행동을 유지하면 의미 없는 정책 교체를 피할 수 있습니다.

### 고정 Policy의 Bellman 식

policy `pi(s)`가 고정되어 있으면 아래 식이 됩니다.

```text
V_pi(s) = sum P(s' | s, pi(s)) * (reward(s,pi(s),s') + gamma * V_pi(s'))
```

SSP 비용 모델에서는 reward 대신 cost를 쓰고, terminal value를 0으로 고정합니다.

### 선형 방정식 관점

discounted setting에서 식을 왼쪽으로 옮기면 아래 형태입니다.

```text
V(s) - gamma * sum P(s'|s,pi(s)) * V(s') = expectedReward(s,pi(s))
```

상태 수가 작으면 Gaussian elimination으로 수치적으로 풀 수 있습니다. 상태 수가 크고 sparse하면 반복 평가가 더 현실적입니다.

### Policy Improvement

현재 policy의 value를 구한 뒤, 각 상태에서 더 좋은 action이 있는지 확인합니다.

```text
newPi(s) = argmax_a sum P(s'|s,a) * (reward + gamma * V_pi(s'))
```

policy가 바뀌지 않으면 policy iteration이 종료됩니다.

### Value Iteration과의 차이

| 기준 | Value Iteration | Policy Iteration |
| --- | --- | --- |
| 한 step | Bellman optimality로 value 직접 갱신 | policy 평가 후 개선 |
| policy | 결과로 복원 가능 | 중간에 명시적으로 유지 |
| 작은 상태 수 | 간단함 | 빠르게 안정될 수 있음 |
| linear solve | 필요 없음 | policy evaluation에 쓸 수 있음 |

## 로컬 완결형 연습

### Finite-Horizon MDP Value DP

전이 확률과 보상이 모두 주어진 finite-horizon MDP에서 시작 상태의 최대 기대 보상을 구합니다. 이 연습은 sampling이나 MCTS가 아니라 정확한 Bellman DP입니다.

#### 입력

```text
S A H start
각 state s, action a마다:
M next_1 prob_1 reward_1 ... next_M prob_M reward_M
```

- `1 <= S <= 200`
- `1 <= A <= 20`
- `0 <= H <= 1000`
- 각 action의 transition 확률합은 `1`입니다.
- reward와 출력은 double로 계산합니다.

#### 출력

```text
start 상태에서 H턴 동안 얻을 수 있는 최대 기대 보상
```

#### 예시

```text
2 2 2 0
1 0 1.0 0
2 0 0.5 0 1 0.5 10
1 1 1.0 0
1 1 1.0 0
```

```text
7.5000000000
```

state `0`에서 action `1`을 고르면 절반 확률로 state `1`에 가며 보상 `10`을 받습니다. state `1`은 이후 추가 보상이 없는 absorbing state입니다.

#### 손으로 따라가는 Trace

`V[t][s]`를 남은 턴이 `t`일 때 state `s`의 최적 기대 보상이라고 둡니다.

| 남은 턴 | `V[t][1]` | `V[t][0]` 계산 | `V[t][0]` |
| ---: | ---: | --- | ---: |
| 0 | 0 | terminal value | 0 |
| 1 | 0 | `max(stay=0, try=0.5*0 + 0.5*10)` | 5 |
| 2 | 0 | `max(stay=5, try=0.5*(0+5) + 0.5*(10+0))` | 7.5 |

`H = 2`에서는 첫 턴에 try를 고르는 것이 최적이고, 실패해 state `0`에 남으면 다음 턴에 다시 시도할 수 있습니다.

#### 구현 기준

```cpp
#include <iomanip>
#include <iostream>

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int states;
    int actionsPerState;
    int horizon;
    int start;
    cin >> states >> actionsPerState >> horizon >> start;

    vector<vector<Action>> actions(states, vector<Action>(actionsPerState));
    for (int state = 0; state < states; ++state) {
        for (int action = 0; action < actionsPerState; ++action) {
            int transitionCount;
            cin >> transitionCount;
            actions[state][action].resize(transitionCount);
            for (Transition& transition : actions[state][action]) {
                cin >> transition.nextState >> transition.probability >> transition.reward;
            }
        }
    }

    vector<double> value = finiteHorizonValue(actions, horizon);

    cout << fixed << setprecision(10) << value[start] << '\n';
}
```

#### Stress 기준

1. 모든 action의 확률합이 `1 +/- 1e-9`인지 먼저 검사합니다.
2. `H <= 6`, `S <= 5`에서는 모든 deterministic policy sequence를 brute force로 열거하거나 recursion memo로 비교합니다.
3. `H = 0`, absorbing state, reward가 모두 음수인 경우를 deterministic case로 둡니다.
4. simulator sample 평균과 비교하지 않습니다. 이 문제는 전이표가 주어진 exact DP입니다.
