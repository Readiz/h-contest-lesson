# Markov Decision Process

Markov Decision Process(MDP)는 상태, 행동, 확률 전이, 보상으로 이루어진 의사결정 모델입니다. 단순 확률 DP가 "정해진 전이의 기대값"을 계산한다면, MDP는 각 상태에서 어떤 행동을 고를지까지 함께 최적화합니다.

이 레슨은 확률과 기대값, Minimax, Monte Carlo Tree Search 이후에 보는 확률적 전략 모델링 레슨입니다.

1. 상태와 가능한 행동을 정의한다.
2. 행동마다 다음 상태 확률과 보상을 둔다.
3. value iteration이나 finite horizon DP로 최적 기대값을 계산한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 기대값 DP, 확률 전이, 그래프 상태, 반복 완화
- 함께 보면 좋은 레슨: 확률과 기대값, Monte Carlo Tree Search, Minimax와 Alpha-Beta
- 다음에 볼 레슨: imperfect information search, policy iteration, reinforcement learning basics

## 1. 문제 신호

| 문제 표현 | MDP 관점 |
| --- | --- |
| 상태마다 여러 행동 중 하나를 선택 | action optimization |
| 행동 결과가 확률적으로 갈림 | stochastic transition |
| 장기 기대 보상을 최대화 | value function |
| 현재 상태만 알면 미래 분포가 결정 | Markov property |
| simulation이 아니라 정확/근사 기대값 필요 | value iteration |

선택이 없으면 Markov chain 또는 기대값 DP입니다. 상대 플레이어가 있으면 game tree나 stochastic game으로 확장됩니다.

## 2. Bellman Optimality Equation

discount factor `gamma`가 있는 무한 horizon MDP에서는 각 상태 가치가 아래 식을 만족합니다.

```text
V[s] = max over action a:
    reward(s, a) + gamma * sum P(s -> t | a) * V[t]
```

최소 비용 문제라면 `max`를 `min`으로 바꾸고 보상 대신 비용을 씁니다.

## 3. Value Iteration

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

## 4. Finite Horizon DP

남은 턴 수가 정해져 있으면 수렴 반복이 아니라 layer DP로 풉니다.

```text
dp[turn][state] = best expected reward from this state with turn steps left
```

이 경우 `turn`이 줄어드는 DAG가 되므로 뒤에서부터 정확히 계산할 수 있습니다.

## 5. Policy

Policy는 각 상태에서 고를 행동을 정한 함수입니다.

```text
policy[state] = action
```

가치만 구하고 끝나는 문제가 아니라 실제 행동 sequence를 출력해야 하면, value update에서 best action도 같이 저장합니다.

## 6. Discount와 종료 상태

MDP에서 무한히 보상을 받을 수 있으면 값이 발산할 수 있습니다.

| 모델 | 처리 |
| --- | --- |
| finite horizon | 남은 step 수로 제한 |
| absorbing terminal | terminal state value를 고정 |
| discounted infinite horizon | `0 <= gamma < 1` 사용 |
| average reward | 더 전문적인 알고리즘 필요 |

대회 문제에서는 finite horizon이나 absorbing state가 가장 흔합니다.

## 7. MCTS와 비교

| 기준 | MDP Value Iteration | MCTS |
| --- | --- |
| 상태 공간 | 명시적으로 열거 가능해야 함 | 큰 상태 공간도 sampling 가능 |
| 전이 확률 | 알고 있어야 함 | simulation으로 대체 가능 |
| 답 성격 | 기대값 근사/정확 DP | 행동 선택 통계 근사 |
| 시간 제어 | iteration/layer 수 | rollout 횟수 |

전이 모델을 정확히 알고 상태 수가 작으면 MDP DP가 더 명확합니다. 상태가 너무 크면 MCTS나 heuristic search가 현실적입니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| value iteration 1회 | `O(total transitions over actions)` |
| `K`번 반복 | `O(K * transitions)` |
| finite horizon `T` | `O(T * transitions)` |
| policy 저장 | `O(states)` |

transition list가 dense하면 상태 수의 제곱이 됩니다. sparse representation을 유지하는 편이 좋습니다.

## 9. 자주 하는 실수

1. 행동별 전이 확률 합이 1이 아닌데 그대로 계산한다.
2. 보상을 state 보상인지 action 보상인지 섞는다.
3. terminal state도 계속 갱신해 값이 흔들린다.
4. `gamma = 1`인 순환 MDP에서 value iteration 수렴을 기대한다.
5. 최적 행동을 출력해야 하는데 value만 저장한다.

## 10. 문제를 볼 때 체크할 조건

- 상태가 Markov property를 만족하는가?
- 행동마다 가능한 next state와 확률을 모두 알고 있는가?
- horizon이 유한한가, terminal이 있는가, discount가 있는가?
- 최대 보상 문제인가, 최소 비용 문제인가?
- 정확한 값이 필요한가, 제한 시간 안의 근사가 허용되는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: finite horizon MDP `/practice/...` 문제 필요 | 남은 턴 DP 작성 | stochastic action |
| 표준 | TODO: value iteration `/practice/...` 문제 필요 | Bellman update 구현 | policy |
| 응용 | TODO: absorbing MDP `/practice/...` 문제 필요 | terminal value와 기대 보상 | absorbing state |
| 함정 | TODO: non-convergent MDP `/practice/...` 문제 필요 | discount/종료 조건 확인 | gamma |
