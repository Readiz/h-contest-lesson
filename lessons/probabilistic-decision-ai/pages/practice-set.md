# Practice Set

Probabilistic Decision AI 계열은 정확 알고리즘과 근사 planning의 평가 기준이 다릅니다. 아직 적절한 h-contest 문제 링크가 없는 항목은 임의 ID를 만들지 않고, 로컬 완결형 연습과 검증 기준을 먼저 둡니다.


입출력 코드는 [Finite Horizon MDP](https://h.readiz.com/learn/probabilistic-decision-ai/finite-horizon-mdp)의 Transition, Action, finiteHorizonValue 정의 뒤에 붙입니다.

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
