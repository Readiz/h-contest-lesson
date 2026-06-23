# Stochastic Shortest Path

Stochastic Shortest Path는 상태와 행동이 있고, 행동 결과가 확률적으로 다음 상태를 정하는 문제에서 terminal state까지의 기대 비용을 최소화하는 모델입니다. Markov Decision Process의 특수한 형태이지만, absorbing state와 hitting time이 중심이라 shortest path, Bellman equation, linear equation 관점이 함께 등장합니다.

이 레슨은 Markov Decision Process, Reinforcement Learning Basics, Probability 이후에 보는 확률적 의사결정 심화입니다.

1. terminal 또는 absorbing state를 명확히 둔다.
2. 각 행동의 기대 비용과 다음 상태 분포를 Bellman 식으로 쓴다.
3. proper policy가 존재하는지, 무한 기대 비용이 가능한지 확인한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Markov Decision Process, Probability Expected Value, Dijkstra
- 함께 보면 좋은 레슨: Reinforcement Learning Basics, Sparse Linear Systems, Bayesian Bandits
- 다음에 볼 레슨: risk-sensitive planning, constrained MDP, policy gradient basics

## 1. 문제 신호

| 문제 표현 | Stochastic Shortest Path 관점 |
| --- | --- |
| 목표 상태에 도달할 때까지 비용이 누적된다 | hitting cost |
| 행동마다 여러 다음 상태가 확률로 주어진다 | stochastic transition |
| 실패하면 같은 상태로 돌아온다 | geometric expected cost |
| terminal state의 value는 0이다 | absorbing boundary |
| 기대 이동 횟수나 기대 비용을 묻는다 | Bellman equation |

일반 shortest path와 다른 점은 edge 하나를 선택해도 다음 정점이 확정되지 않는다는 것입니다.

## 2. Bellman 식

상태 `s`에서 행동 `a`를 고르면 비용 `c(s,a)`를 내고 확률 `P(s'|s,a)`로 다음 상태가 됩니다.

```text
V(goal) = 0
V(s) = min_a c(s,a) + sum P(s'|s,a) * V(s')
```

terminal에 도달하지 못하고 영원히 도는 policy가 있으면 기대 비용이 무한대가 될 수 있습니다. 문제에서 모든 policy가 proper인지, 또는 최소 정책만 proper이면 되는지 확인해야 합니다.

## 3. 작은 예시

상태 `A`에서 목표 `G`로 가는 행동이 하나 있다고 하겠습니다.

```text
성공 확률 0.7: G로 이동, 비용 1
실패 확률 0.3: A로 돌아옴, 비용 1
```

Bellman 식은 아래와 같습니다.

```text
V(A) = 1 + 0.7 * V(G) + 0.3 * V(A)
V(G) = 0
0.7 * V(A) = 1
V(A) = 1 / 0.7
```

확률적으로 실패해도 반복할 수 있기 때문에 기대 비용은 단순 1이 아니라 성공까지의 geometric 기대 횟수입니다.

## 4. Value Iteration 골격

아래 코드는 모든 비용이 비음수이고 proper policy가 있다고 가정한 value iteration 예시입니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct Transition {
    int nextState = 0;
    double probability = 0.0;
};

struct Action {
    double cost = 0.0;
    vector<Transition> transitions;
};

vector<double> stochasticShortestPathValueIteration(
    const vector<vector<Action>>& actions,
    int goal,
    int iterations
) {
    int n = (int)actions.size();
    vector<double> value(n, 0.0);
    vector<double> nextValue(n, 0.0);

    for (int iter = 0; iter < iterations; ++iter) {
        for (int state = 0; state < n; ++state) {
            if (state == goal) {
                nextValue[state] = 0.0;
                continue;
            }
            double best = 1e100;
            for (const Action& action : actions[state]) {
                double candidate = action.cost;
                for (const Transition& transition : action.transitions) {
                    candidate += transition.probability * value[transition.nextState];
                }
                best = min(best, candidate);
            }
            nextValue[state] = best;
        }
        value.swap(nextValue);
    }

    return value;
}
```

정확한 오차가 필요한 문제에서는 단순 반복 횟수를 감으로 정하면 안 됩니다. 수렴성 조건이나 linear equation 풀이를 검토해야 합니다.

## 5. Linear Equation으로 푸는 경우

policy가 고정되어 있으면 min이 사라지고 선형 방정식이 됩니다.

```text
V(s) - sum P(s'|s,pi(s)) * V(s') = c(s,pi(s))
```

상태 수가 작고 policy가 고정되어 있거나, 가능한 policy를 따로 고를 수 있다면 Gaussian elimination이나 sparse linear solver로 기대 비용을 정확히 계산할 수 있습니다.

## 6. Deterministic Shortest Path와의 관계

전이가 항상 한 상태로만 간다면 식은 일반 shortest path와 비슷해집니다.

```text
V(s) = min_a cost(s,a) + V(next(s,a))
```

비음수 edge면 Dijkstra, DAG면 topological DP를 쓸 수 있습니다. stochastic case에서는 자기 자신으로 돌아오는 확률 때문에 단순한 정점 순서가 없어질 수 있습니다.

## 7. Proper Policy 체크

| 상황 | 해석 |
| --- | --- |
| 목표에 도달할 확률이 1인 정책 존재 | finite optimum 후보 |
| 어떤 상태에서 목표로 갈 방법이 없음 | value는 무한대 |
| 음수 비용 cycle 가능 | 기대 비용이 아래로 발산할 수 있음 |
| 실패 시 제자리 확률이 큼 | 수렴이 느려질 수 있음 |

문제에서 "항상 언젠가 도착한다"는 조건이 없다면, 무한 기대 비용 상태를 어떻게 출력해야 하는지도 확인해야 합니다.

## 8. 자주 하는 실수

1. terminal state에서도 future value를 더한다.
2. 실패해서 같은 상태로 돌아오는 항을 빼지 않고 단순 기대값만 계산한다.
3. 확률 합이 1인지 검증하지 않는다.
4. 모든 정책이 proper하다고 가정한다.
5. discounted MDP와 undiscounted hitting cost를 섞는다.
6. value iteration 수렴 오차를 출력 오차보다 크게 둔다.

## 9. 문제를 볼 때 체크할 조건

- terminal state가 absorbing인가?
- 모든 action의 transition probability 합이 1인가?
- 비용이 비음수인가, 음수 cycle이 가능한가?
- fixed policy 평가인가, optimal policy 선택인가?
- linear equation으로 풀 수 있는 상태 수인가?
- 무한 기대 비용을 어떻게 다뤄야 하는가?

## 10. 대표 문제로 연결하기

### 문제에서 보이는 신호

- 입력 크기: 상태 수가 작거나 transition이 sparse함
- 필요한 복잡도: value iteration, policy iteration, 또는 sparse linear solve
- 이 레슨의 핵심 개념: terminal까지의 기대 비용 Bellman 식

### 풀이 흐름

1. 목표 상태의 value를 0으로 고정한다.
2. 각 action의 cost와 transition distribution을 정규화한다.
3. Bellman optimality equation을 쓴다.
4. proper policy와 무한 value 가능성을 먼저 제거한다.
5. 상태 수와 오차 요구에 맞춰 iteration 또는 linear solve를 선택한다.

### 자주 틀리는 지점

- "확률적으로 이동"이 있어도 goal 도달 전까지 비용이 계속 누적되면 discounted MDP가 아닙니다.
- 자기 자신으로 돌아오는 확률이 있으면 식을 정리하거나 반복 수렴을 충분히 검증해야 합니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: expected hitting time `/practice/...` 문제 필요 | 자기 상태로 돌아오는 기대 비용 계산 | geometric |
| 표준 | TODO: stochastic shortest path `/practice/...` 문제 필요 | Bellman optimality equation 작성 | absorbing state |
| 응용 | TODO: policy evaluation linear system `/practice/...` 문제 필요 | 고정 policy의 value 계산 | Gaussian elimination |
| 함정 | TODO: improper policy `/practice/...` 문제 필요 | 무한 기대 비용 상태 구분 | proper policy |
