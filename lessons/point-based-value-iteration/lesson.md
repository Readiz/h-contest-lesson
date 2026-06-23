# Point-Based Value Iteration

Point-Based Value Iteration(PBVI)은 POMDP의 연속적인 belief space 전체를 다루지 않고, 대표 belief point 집합에서 value function을 근사하는 planning 기법입니다. 정확한 대회 정답용 알고리즘이라기보다, POMDP가 왜 어려운지와 belief 기반 근사가 어떻게 구성되는지 이해하는 레슨입니다.

이 레슨은 Partially Observable MDP 이후에 보는 확률적 planning 심화입니다.

1. belief 전체가 아니라 자주 도달하는 belief point를 모은다.
2. alpha vector로 piecewise-linear value function을 근사한다.
3. backup을 대표 belief들에 반복 적용해 정책을 개선한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Partially Observable MDP, Markov Decision Process, Probability Expected Value
- 함께 보면 좋은 레슨: Imperfect Information Search, Monte Carlo Tree Search, Heuristic Search
- 다음에 볼 레슨: POMCP, reinforcement learning basics, approximate dynamic programming

## 1. 문제 신호

| 문제 표현 | PBVI 관점 |
| --- | --- |
| hidden state가 작지만 belief가 연속 | 대표 belief 근사 |
| observation branching이 커서 exact tree가 폭발 | point-based backup |
| 정확 최적보다 policy 품질이 중요 | approximate planning |
| reward와 transition/observation model이 있음 | POMDP model |
| belief가 특정 영역에 자주 모임 | reachable belief set |

정확한 값을 요구하는 알고리즘 문제라면 PBVI는 보통 맞지 않습니다. heuristic AI, planning, simulator 계열 문제에서 의미가 있습니다.

## 2. Alpha Vector 직관

유한 horizon POMDP의 value function은 belief에 대해 piecewise-linear convex 형태로 표현할 수 있습니다.

```text
V(b) = max_alpha sum_s b[s] * alpha[s]
```

각 alpha vector는 어떤 조건부 계획을 따랐을 때 state별 기대 보상을 담습니다. belief가 달라지면 가장 좋은 alpha도 달라집니다.

## 3. 대표 Belief Point

PBVI는 모든 belief를 보지 않고 집합 `B`만 봅니다.

```text
B = {b_1, b_2, ..., b_m}
```

이 point들은 보통 초기 belief에서 action/observation을 sampling하거나, 문제에서 중요한 상황을 직접 넣어 만듭니다. 품질은 `B`가 실제 reachable belief를 얼마나 잘 덮는지에 크게 좌우됩니다.

## 4. Alpha 선택 구현

아래 코드는 belief 하나에서 가장 큰 값을 주는 alpha vector를 고릅니다.

```cpp compile-check
#include <limits>
#include <vector>
using namespace std;

double dotBeliefAlpha(const vector<double>& belief, const vector<double>& alpha) {
    double value = 0.0;
    for (int i = 0; i < (int)belief.size(); ++i) {
        value += belief[i] * alpha[i];
    }
    return value;
}

int bestAlphaIndex(
    const vector<double>& belief,
    const vector<vector<double>>& alphaVectors
) {
    int best = -1;
    double bestValue = -numeric_limits<double>::infinity();
    for (int index = 0; index < (int)alphaVectors.size(); ++index) {
        double value = dotBeliefAlpha(belief, alphaVectors[index]);
        if (value > bestValue) {
            bestValue = value;
            best = index;
        }
    }
    return best;
}
```

실제 PBVI backup은 action과 observation별 alpha 조합을 만들지만, 최종적으로는 각 belief에서 가장 좋은 alpha를 고르는 이 구조가 반복됩니다.

## 5. Backup의 큰 흐름

대표 belief `b`에 대해 action `a`를 하나 고르면, observation마다 다음 belief가 생깁니다.

```text
b --action a, observation o--> b'
```

각 `b'`에서 기존 alpha set 중 best alpha를 고르고, 이를 이용해 현재 action의 alpha를 만듭니다.

```text
alpha_a[s] =
  reward(s,a)
  + gamma * sum_o sum_t P(t,o | s,a) * alpha_best(o)[t]
```

모든 action에 대해 `alpha_a`를 만들고, 현재 belief에서 가장 값이 큰 alpha를 새 set에 넣습니다.

## 6. 작은 예시

```text
hidden state: safe / risky
actions: observe / take
observations: good / bad
```

초기 belief가 `[0.5, 0.5]`이고 `observe`를 하면 observation에 따라 `[0.8,0.2]` 또는 `[0.2,0.8]` 근처로 이동한다고 합시다. PBVI는 이 세 belief를 point set에 넣고, 각 지점에서 좋은 action을 대표하도록 alpha vector를 갱신합니다.

전체 belief space를 격자로 모두 나누지 않아도 reachable한 영역 중심으로 policy를 만들 수 있습니다.

## 7. Belief Point 확장

대표 belief는 고정해도 되지만, 보통 반복적으로 확장합니다.

1. 현재 point에서 가능한 action/observation으로 다음 belief를 만든다.
2. 기존 point와 너무 가까우면 버린다.
3. 멀리 떨어진 belief를 추가한다.
4. point 수가 너무 커지면 pruning한다.

거리 척도는 L1 distance나 KL divergence를 쓸 수 있지만, 구현 단순성은 L1이 좋습니다.

## 8. 정확 POMDP와의 차이

| 기준 | Exact belief DP | PBVI |
| --- | --- | --- |
| belief 처리 | 가능한 모든 branch | 대표 point |
| 보장 | 작은 horizon에서 정확 가능 | 근사 |
| 병목 | observation tree 폭발 | point 품질 |
| 출력 | optimal value/policy | approximate policy |

문제가 "정답과 오차 허용" 형태인지, 아니면 judge가 정확한 값만 받는지에 따라 선택이 갈립니다.

## 9. MCTS와의 비교

PBVI는 model을 알고 있고 반복 planning을 할 때 유리합니다. POMCP 같은 MCTS 계열은 큰 상태 공간에서 simulation으로 action을 고를 때 더 자연스럽습니다.

| 상황 | 우선 후보 |
| --- | --- |
| state/observation model이 명확하고 작음 | PBVI |
| simulator만 있고 model table이 큼 | POMCP/MCTS |
| horizon이 매우 작음 | exact belief tree |
| policy를 미리 계산 | PBVI |

## 10. 자주 하는 실수

1. 대표 belief를 초기 근처에만 두어 실제 도달 영역을 놓친다.
2. observation probability로 belief를 정규화하지 않는다.
3. alpha vector가 state별 값이라는 점을 잊고 belief별 scalar만 저장한다.
4. 근사 알고리즘인데 정확 judge 문제에 사용한다.
5. discount `gamma`와 horizon 종료 조건을 섞는다.

## 11. 문제를 볼 때 체크할 조건

- POMDP model table을 만들 수 있는가?
- exact belief tree가 너무 큰가?
- 근사 policy가 허용되는가?
- reachable belief point를 어떻게 만들 것인가?
- alpha vector와 action을 함께 저장해야 하는가?

## 12. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: point-based value iteration `/practice/...` 문제 필요 | belief point와 alpha value 계산 | alpha vector |
| 표준 | TODO: small PBVI planning `/practice/...` 문제 필요 | action/observation backup | belief update |
| 응용 | TODO: reachable belief sampling `/practice/...` 문제 필요 | point set 확장 | L1 distance |
| 함정 | TODO: exact vs approximate POMDP `/practice/...` 문제 필요 | 근사 허용 조건 판별 | planning |
