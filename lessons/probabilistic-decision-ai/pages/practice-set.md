# Practice Set

Probabilistic Decision AI 계열은 정확 알고리즘과 근사 planning의 평가 기준이 다릅니다. 아직 적절한 h-contest 문제 링크가 없는 항목은 임의 ID를 만들지 않고, 로컬 완결형 연습과 검증 기준을 먼저 둡니다.

## 로컬 완결형 연습

### Feedback Model Classification

네 개의 짧은 statement를 만들고, 각 statement를 `full-information`, `bandit`, `simulator`, `hidden-state observation`으로 분류합니다. 답안에는 "왜 다른 모델이 아닌지"를 한 문장씩 붙입니다.

```text
1. 선택 후 모든 후보의 loss가 공개된다.
2. 선택한 arm의 reward만 공개된다.
3. action sequence를 넣으면 simulator가 sampled trajectory를 반환한다.
4. 실제 state는 숨겨져 있고 observation만 공개된다.
```

이 연습의 목표는 구현보다 모델 누수를 막는 것입니다. 특히 2번에서 선택하지 않은 arm의 reward를 0으로 채우거나, 4번에서 hidden state를 직접 policy state로 쓰면 실패로 처리합니다.

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

```cpp compile-check
#include <algorithm>
#include <iomanip>
#include <iostream>
#include <vector>
using namespace std;

struct Transition {
    int nextState = 0;
    double probability = 0.0;
    double reward = 0.0;
};

using Action = vector<Transition>;

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

    vector<double> value(states, 0.0);
    vector<double> nextValue(states, 0.0);

    for (int left = 1; left <= horizon; ++left) {
        for (int state = 0; state < states; ++state) {
            double best = -1e100;
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

    cout << fixed << setprecision(10) << value[start] << '\n';
}
```

#### Stress 기준

1. 모든 action의 확률합이 `1 +/- 1e-9`인지 먼저 검사합니다.
2. `H <= 6`, `S <= 5`에서는 모든 deterministic policy sequence를 brute force로 열거하거나 recursion memo로 비교합니다.
3. `H = 0`, absorbing state, reward가 모두 음수인 경우를 deterministic case로 둡니다.
4. simulator sample 평균과 비교하지 않습니다. 이 문제는 전이표가 주어진 exact DP입니다.

## h-contest 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: feedback boundary `/practice/...` 문제 필요 | 관측 모델 분류 | full-information vs bandit |
| 입문 | 로컬: finite-horizon MDP value DP | horizon DP와 Bellman 식 | MDP |
| 입문 | TODO: stochastic shortest path `/practice/...` 문제 필요 | absorbing goal과 proper policy | SSP |
| 표준 | TODO: MCTS toy game `/practice/...` 문제 필요 | selection/rollout/backprop | UCT |
| 표준 | TODO: hidden-state search `/practice/...` 문제 필요 | belief filtering | imperfect information |
| 응용 | TODO: POMDP belief update `/practice/...` 문제 필요 | Bayes update | observation model |
| 응용 | TODO: bandit simulation `/practice/...` 문제 필요 | posterior update와 regret | Thompson sampling |
| 심화 | TODO: online planning evaluation `/practice/...` 문제 필요 | paired seed benchmark | time budget |

## 완료 기준

- exact solver인지 heuristic planning인지 먼저 표시합니다.
- stochastic transition의 확률합을 검증합니다.
- sampling 기반이면 seed, budget, variance를 함께 기록합니다.
- hidden state 문제는 belief update 식을 명시합니다.
- online planning은 score뿐 아니라 deadline miss를 같이 봅니다.
