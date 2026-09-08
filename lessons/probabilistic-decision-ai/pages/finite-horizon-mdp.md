# Finite Horizon MDP

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
