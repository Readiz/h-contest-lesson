# Partially Observable MDP

Partially Observable MDP(POMDP)는 실제 상태를 직접 볼 수 없고, action 이후 관측만 받는 Markov Decision Process입니다. Imperfect Information Search가 게임/탐색 관점에서 정보 집합을 다룬다면, POMDP는 belief distribution을 상태로 올려 기대 보상을 계산합니다.

이 레슨은 Markov Decision Process와 Imperfect Information Search 이후에 보는 확률적 의사결정 심화입니다.

1. 숨은 상태와 관측 가능한 observation을 분리한다.
2. action과 observation으로 belief를 갱신한다.
3. belief state 위에서 finite horizon DP 또는 근사 탐색을 수행한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: MDP, probability distribution, belief update, expected value DP
- 함께 보면 좋은 레슨: Markov Decision Process, Imperfect Information Search, Monte Carlo Tree Search
- 다음에 볼 레슨: belief-state planning, point-based value iteration, reinforcement learning basics

## 1. 문제 신호

| 문제 표현 | POMDP 관점 |
| --- | --- |
| 실제 상태를 알 수 없고 관측만 받음 | hidden state |
| 행동이 다음 관측 확률도 바꿈 | observation model |
| 같은 관측 history에서 확률분포를 유지 | belief state |
| 장기 기대 보상을 최적화 | value over belief |
| 상태 수는 작지만 관측 branching이 있음 | finite horizon belief DP |

상태가 완전히 관측되면 MDP입니다. 상대의 전략까지 고려해야 하면 imperfect information game으로 확장됩니다.

## 2. Belief State

belief는 숨은 상태에 대한 확률분포입니다.

```text
belief[s] = P(real state is s | observations so far)
```

action `a`를 하고 observation `o`를 받으면 Bayes rule로 갱신합니다.

```text
b'(t) proportional to O(o | t, a) * sum_s P(t | s, a) * b(s)
```

정규화 상수는 observation `o`가 나올 확률입니다.

## 3. Belief Update 구현

```cpp compile-check
#include <vector>
using namespace std;

struct PomdpTransition {
    int from = 0;
    int to = 0;
    int action = 0;
    double probability = 0.0;
};

vector<double> updatePomdpBelief(
    const vector<double>& belief,
    const vector<PomdpTransition>& transitions,
    const vector<vector<vector<double>>>& observationProbability,
    int action,
    int observation
) {
    int stateCount = (int)belief.size();
    vector<double> predicted(stateCount, 0.0);

    for (const PomdpTransition& transition : transitions) {
        if (transition.action != action) {
            continue;
        }
        predicted[transition.to] += belief[transition.from] * transition.probability;
    }

    vector<double> nextBelief(stateCount, 0.0);
    double total = 0.0;
    for (int state = 0; state < stateCount; ++state) {
        double likelihood = observationProbability[action][state][observation];
        nextBelief[state] = predicted[state] * likelihood;
        total += nextBelief[state];
    }

    if (total == 0.0) {
        return vector<double>(stateCount, 0.0);
    }
    for (double& value : nextBelief) {
        value /= total;
    }
    return nextBelief;
}
```

`observationProbability[action][state][observation]`은 action 이후 실제 상태가 `state`일 때 observation이 나올 확률입니다. 문제에 따라 observation model의 index 순서를 명확히 고정해야 합니다.

## 4. 작은 예시

```text
hidden state: 비가 옴 / 맑음
action: 우산을 가져감 / 안 가져감
observation: 길이 젖음 / 마름

처음 belief = [0.5, 0.5]
길이 젖었다는 observation을 받으면
비 확률이 커진 belief로 갱신된다.
```

이후 행동은 실제 날씨가 아니라 갱신된 belief를 보고 고릅니다. belief가 충분통계량 역할을 합니다.

## 5. Finite Horizon DP

남은 턴 수가 작고 가능한 belief 수가 제한적이면 belief를 key로 memoization할 수 있습니다.

```text
value(turn, belief) =
  max_action expected immediate reward
  + sum_observation P(observation | belief, action)
      * value(turn - 1, updated_belief)
```

belief는 실수 vector라 그대로 map key로 쓰기 어렵습니다. 작은 문제에서는 rational state, discretization, canonical rounding 중 하나를 선택합니다.

## 6. MDP와의 차이

| 기준 | MDP | POMDP |
| --- | --- | --- |
| 현재 정보 | 실제 state | belief distribution |
| 전이 | `P(s -> t | a)` | transition + observation |
| DP state | state id | probability vector |
| 난점 | 상태 수 | belief 공간이 연속 |

POMDP는 MDP보다 훨씬 어렵습니다. 대회 문제에서는 정확한 일반 POMDP보다 작은 horizon, 작은 state, 또는 명확한 belief compression이 주어지는 경우가 많습니다.

## 7. Imperfect Information Search와 연결

카드 게임처럼 상대의 숨은 정보가 있으면 information set을 belief로 볼 수 있습니다.

```text
information set = 가능한 상태 집합
belief = 각 상태의 확률까지 포함한 정보 집합
```

확률이 모두 같고 관측으로 후보만 제거한다면 Imperfect Information Search의 belief filtering과 거의 같습니다. 확률 전이와 observation model이 있으면 POMDP가 더 정확한 모델입니다.

## 8. 근사 방법

| 상황 | 접근 |
| --- | --- |
| horizon이 작음 | exact belief tree search |
| belief가 sparse | 후보 상태만 유지 |
| 상태가 큼 | particle filter |
| action 선택만 필요 | POMCP/MCTS 계열 |
| value function 근사 가능 | point-based value iteration |

문제에서 정확한 최적값을 요구하면 근사 방법은 보통 부적절합니다. 반대로 heuristic AI 문제라면 sampling이 현실적입니다.

## 9. 자주 하는 실수

1. observation likelihood를 곱하지 않고 transition만 적용한다.
2. 갱신 뒤 belief를 정규화하지 않는다.
3. action 선택을 실제 hidden state 기준으로 해 정보 누출을 만든다.
4. observation이 불가능한 경우 `total=0` 처리를 하지 않는다.
5. belief vector를 부동소수 key로 쓰면서 같은 상태를 계속 새로 만든다.

## 10. 문제를 볼 때 체크할 조건

- hidden state와 observation이 무엇인가?
- action이 transition과 observation probability를 모두 바꾸는가?
- belief를 압축하거나 정확히 표현할 수 있는가?
- horizon이 유한한가, discount가 있는가?
- 정확 DP가 필요한가, sampling 근사가 허용되는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: POMDP belief update `/practice/...` 문제 필요 | observation likelihood 반영 | Bayes update |
| 표준 | TODO: finite horizon POMDP `/practice/...` 문제 필요 | belief tree DP | expected value |
| 응용 | TODO: particle belief planning `/practice/...` 문제 필요 | sampling belief 유지 | particle filter |
| 함정 | TODO: hidden-state leakage `/practice/...` 문제 필요 | 실제 상태 기준 행동 금지 | information leak |
