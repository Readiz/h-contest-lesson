# Discounted Value Iteration

Markov Decision Process(MDP)는 상태, 행동, 확률 전이, 보상으로 이루어진 의사결정 모델입니다. 단순 확률 DP가 "정해진 전이의 기대값"을 계산한다면, MDP는 각 상태에서 어떤 행동을 고를지까지 함께 최적화합니다.


유한 상태·행동, 유계 보상, 행동별 확률 합 1과 0<=gamma<1을 전제로 합니다. Bellman 연산자는 gamma 수축입니다. delta=||V_new-V_old||∞라면 반환 V_new의 오차는 gamma*delta/(1-gamma) 이하입니다. gamma=0이면 한 번 갱신으로 충분합니다. 반복 횟수만 정해 반환한 값은 정확해가 아닙니다.

## 문제 신호

| 문제 표현 | MDP 관점 |
| --- | --- |
| 상태마다 여러 행동 중 하나를 선택 | action optimization |
| 행동 결과가 확률적으로 갈림 | stochastic transition |
| 장기 기대 보상을 최대화 | value function |
| 현재 상태만 알면 미래 분포가 결정 | Markov property |
| simulation이 아니라 정확/근사 기대값 필요 | value iteration |

선택이 없으면 Markov chain 또는 기대값 DP입니다. 상대 플레이어가 있으면 game tree나 stochastic game으로 확장됩니다.

## Bellman Optimality Equation

discount factor `gamma`가 있는 무한 horizon MDP에서는 각 상태 가치가 아래 식을 만족합니다.

```text
V[s] = max over action a:
    reward(s, a) + gamma * sum P(s -> t | a) * V[t]
```

최소 비용 문제라면 `max`를 `min`으로 바꾸고 보상 대신 비용을 씁니다.

## Value Iteration

Value iteration은 모든 상태 값을 반복해서 갱신합니다. `gamma < 1`이면 수렴성이 좋아집니다.

```cpp compile-check
#include <algorithm>
#include <cmath>
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

            double best = -1e100;
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

## Policy

Policy는 각 상태에서 고를 행동을 정한 함수입니다.

```text
policy[state] = action
```

가치만 구하고 끝나는 문제가 아니라 실제 행동 sequence를 출력해야 하면, value update에서 best action도 같이 저장합니다.

## Discount와 종료 상태

MDP에서 무한히 보상을 받을 수 있으면 값이 발산할 수 있습니다.

| 모델 | 처리 |
| --- | --- |
| finite horizon | 남은 step 수로 제한 |
| absorbing terminal | terminal state value를 고정 |
| discounted infinite horizon | `0 <= gamma < 1` 사용 |
| average reward | 더 전문적인 알고리즘 필요 |

대회 문제에서는 finite horizon이나 absorbing state가 가장 흔합니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| value iteration 1회 | `O(total transitions over actions)` |
| `K`번 반복 | `O(K * transitions)` |
| finite horizon `T` | `O(T * transitions)` |
| policy 저장 | `O(states)` |

transition list가 dense하면 상태 수의 제곱이 됩니다. sparse representation을 유지하는 편이 좋습니다.
