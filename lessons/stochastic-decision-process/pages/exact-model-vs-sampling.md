# Reinforcement Learning Basics

Reinforcement Learning Basics는 상태, 행동, 보상, 전이 확률이 있는 환경에서 policy를 평가하거나 개선하는 기본 틀입니다. contest에서는 실제 학습보다 Markov Decision Process를 반복 갱신으로 푸는 모델링, finite-horizon decision, exploration과 exploitation 구분을 위해 등장합니다.

이 레슨은 Markov Decision Process, Probability, Game Theory Applications 이후에 보는 확률적 의사결정 기초입니다.

1. value는 현재 policy나 최적 policy의 기대 누적 보상이다.
2. policy evaluation은 고정 policy의 value를 계산한다.
3. policy iteration과 value iteration은 Bellman update로 policy를 개선한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: expected value, Markov Decision Process, dynamic programming
- 함께 보면 좋은 레슨: Bayesian Bandits, POMDP, POMCP
- 다음에 볼 레슨: Q-learning, policy gradient, online planning evaluation

## 1. 문제 신호

| 문제 표현 | RL 관점 |
| --- | --- |
| 상태와 행동마다 보상과 전이가 있다 | MDP |
| 현재 정책의 기대 보상을 구한다 | policy evaluation |
| 최적 행동을 반복 갱신한다 | value iteration |
| model은 모르고 sample만 받는다 | model-free RL |
| exploration과 exploitation 균형이 필요 | bandit or RL |

대회 문제에서는 transition table이 주어지는 경우가 많습니다. 그러면 RL이라는 이름보다 MDP DP로 풀면 됩니다. sample만 주어지는 interactive나 simulator 문제에서 학습 관점이 중요해집니다.

## 2. Bellman 식

할인율 `gamma`가 있고 보상 `r(s, a, s')`가 주어질 때 최적 value는 아래 식을 만족합니다.

```text
V(s) = max_a sum_{s'} P(s' | s, a) * (r(s,a,s') + gamma * V(s'))
```

finite horizon이면 시간 `t`를 상태에 넣거나 뒤에서 앞으로 DP를 합니다. infinite discounted case에서는 value iteration으로 수렴시킬 수 있습니다.

## 3. Value Iteration 구현 조각

아래 코드는 작은 MDP에서 discounted value iteration을 수행합니다.

```cpp compile-check
#include <algorithm>
#include <cmath>
#include <vector>
using namespace std;

struct Transition {
    int nextState = 0;
    double probability = 0.0;
    double reward = 0.0;
};

using Action = vector<Transition>;
using StateActions = vector<Action>;

vector<double> valueIteration(
    const vector<StateActions>& mdp,
    double gamma,
    int iterations
) {
    int stateCount = (int)mdp.size();
    vector<double> value(stateCount, 0.0);
    vector<double> nextValue(stateCount, 0.0);

    for (int iter = 0; iter < iterations; ++iter) {
        for (int state = 0; state < stateCount; ++state) {
            if (mdp[state].empty()) {
                nextValue[state] = 0.0;
                continue;
            }
            double best = -1e100;
            for (const Action& action : mdp[state]) {
                double score = 0.0;
                for (const Transition& transition : action) {
                    score += transition.probability *
                        (transition.reward + gamma * value[transition.nextState]);
                }
                best = max(best, score);
            }
            nextValue[state] = best;
        }
        value.swap(nextValue);
    }

    return value;
}
```

문제에서 정확한 오차 한계를 요구하면 iteration 횟수를 `gamma`와 reward bound에 맞춰 계산해야 합니다.

## 4. Policy Evaluation과 Policy Improvement

policy가 고정되어 있으면 max를 취하지 않고 policy가 선택한 action의 기대값만 계산합니다.

```text
V_pi(s) = E[r + gamma * V_pi(s')]
```

policy iteration은 두 단계를 반복합니다.

1. 현재 policy의 value를 평가한다.
2. 각 상태에서 더 좋은 action으로 policy를 바꾼다.

상태와 행동 수가 작고 transition table이 명확하면 policy iteration이 value iteration보다 빨리 안정될 수 있습니다.

## 5. Q-value

`Q(s, a)`는 상태 `s`에서 action `a`를 바로 선택했을 때의 기대값입니다.

```text
Q(s,a) = sum P(s'|s,a) * (r + gamma * max_b Q(s',b))
```

model-free Q-learning은 transition probability를 모를 때 sample로 이 값을 갱신합니다. 하지만 offline judge에서는 sample noise 때문에 exact answer를 내기 어려우므로 보통 model이 주어지는 MDP로 바꿔 풉니다.

## 6. 작은 예시

```text
state 0: 안전한 행동 -> reward 1, state 0
state 0: 위험한 행동 -> 50% reward 3, 50% reward -2
gamma = 0.9
```

한 라운드 보상 평균만 보면 위험한 행동의 기대 보상은 `0.5`입니다. 장기 value까지 고려하면 안전한 행동이 계속 `1`을 주므로 더 좋아질 수 있습니다. Bellman update는 이런 장기 효과를 현재 action 선택에 반영합니다.

## 7. Bandit, MDP, POMDP 구분

| 모델 | 상태 | 전이 | 관측 |
| --- | --- | --- | --- |
| Bandit | 거의 없음 | action별 보상만 | 선택한 보상 |
| MDP | 완전 관측 | `P(s'|s,a)` | 다음 상태 |
| POMDP | hidden state | transition + observation | observation |

상태가 없거나 독립 action만 반복하면 bandit입니다. 상태가 완전히 보이면 MDP, 숨겨져 있으면 POMDP입니다.

## 8. 시간 복잡도 감각

| 작업 | 시간 |
| --- | ---: |
| value iteration 1회 | `O(total transitions)` |
| finite horizon DP | `O(T * total transitions)` |
| policy evaluation iterative | `O(iterations * total transitions)` |
| exact linear solve evaluation | 상태 수에 따라 cubic 가능 |

transition이 sparse하면 edge list로 저장합니다. dense matrix를 만들면 작은 상태 수를 제외하고 메모리가 먼저 커집니다.

## 9. 자주 하는 실수

1. reward가 state에 붙는지 transition에 붙는지 섞는다.
2. terminal state에서 future value를 계속 더한다.
3. 확률 합이 1이 아닌 action을 그대로 사용한다.
4. finite horizon 문제를 infinite discounted 문제처럼 반복한다.
5. hidden state가 있는데 MDP value iteration으로 푼다.
6. model-free sample 학습을 exact judge 답안처럼 사용한다.

## 10. 문제를 볼 때 체크할 조건

- 상태가 완전히 관측되는가?
- transition probability가 주어지는가, simulator sample만 가능한가?
- horizon이 finite인가 infinite discounted인가?
- terminal state와 absorbing state를 구분했는가?
- 필요한 출력이 value인지 policy인지 action 하나인지 확인했는가?
- 오차 허용과 반복 횟수를 계산했는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: finite-horizon MDP `/practice/...` 문제 필요 | 뒤에서 앞으로 기대값 DP | Bellman |
| 표준 | TODO: discounted value iteration `/practice/...` 문제 필요 | 반복 갱신과 수렴 | gamma |
| 응용 | TODO: policy iteration `/practice/...` 문제 필요 | evaluation과 improvement | policy |
| 함정 | TODO: MDP vs POMDP `/practice/...` 문제 필요 | 관측 가능한 상태 구분 | hidden state |
