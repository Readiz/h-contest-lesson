# Game Theory Applications

Game Theory Applications는 Grundy, minimax, MDP, imperfect information 모델을 문제 신호별로 고르는 레슨입니다. 개별 알고리즘을 외우는 것보다 게임의 정보 구조, 확률, 독립 합성 여부를 먼저 분류하는 것이 핵심입니다.

이 레슨은 Game Theory와 Grundy Number, Minimax, Markov Decision Process 이후에 보는 응용 레슨입니다.

1. 게임이 impartial인지, 두 플레이어 zero-sum인지, 확률적 의사결정인지 분류한다.
2. 독립 subgame 합성이 있으면 Grundy/xor를 검토한다.
3. hidden information이나 stochastic transition이 있으면 search/MDP 계열로 옮긴다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Game Theory와 Grundy Number, Minimax와 Alpha-Beta Pruning, Markov Decision Process
- 함께 보면 좋은 레슨: Monte Carlo Tree Search, Imperfect Information Search, POMDP
- 다음에 볼 레슨: Point-Based Value Iteration, reinforcement learning basics, stochastic games

## 1. 분류표

| 문제 신호 | 우선 모델 |
| --- | --- |
| 양쪽 선택지가 같고 마지막 행동자가 승리 | impartial game, Grundy |
| 여러 독립 더미/구간이 합쳐짐 | xor sum |
| MAX/MIN이 번갈아 최적 선택 | minimax |
| 확률 전이가 있고 보상 기대값 최대화 | MDP |
| 숨은 정보가 있고 관측만 가능 | imperfect information 또는 POMDP |
| 정확 최적보다 좋은 move가 필요 | MCTS/heuristic search |

처음부터 구현을 고르면 위험합니다. state, turn, information, randomness 네 가지를 먼저 분리합니다.

## 2. Impartial Game인지 확인

Grundy를 쓰려면 보통 아래 조건이 필요합니다.

1. 두 플레이어가 같은 move set을 가진다.
2. 확률이 없다.
3. 각 state의 승패가 이후 state들로만 결정된다.
4. 여러 subgame이 독립이면 xor로 합성된다.

move set이 플레이어마다 다르거나 점수가 누적되는 게임이면 Grundy가 아닐 가능성이 큽니다.

## 3. Grundy Skeleton

아래 코드는 DAG game에서 Grundy number를 계산합니다.

```cpp compile-check
#include <vector>
using namespace std;

int mexValue(const vector<int>& values) {
    vector<int> seen(values.size() + 2, 0);
    for (int value : values) {
        if (0 <= value && value < (int)seen.size()) {
            seen[value] = 1;
        }
    }
    int result = 0;
    while (seen[result]) {
        ++result;
    }
    return result;
}

int grundyDfs(int node, const vector<vector<int>>& graph, vector<int>& memo) {
    if (memo[node] != -1) {
        return memo[node];
    }
    vector<int> childValues;
    for (int next : graph[node]) {
        childValues.push_back(grundyDfs(next, graph, memo));
    }
    memo[node] = mexValue(childValues);
    return memo[node];
}
```

순환 게임이면 이 skeleton은 바로 쓸 수 없습니다. 반복 상태는 draw, discount, horizon 중 무엇으로 처리하는지 문제 조건을 먼저 봐야 합니다.

## 4. Minimax로 넘어가는 조건

아래 중 하나라도 있으면 Grundy 대신 minimax를 봅니다.

| 조건 | 이유 |
| --- | --- |
| 플레이어별 move가 다름 | impartial이 아님 |
| 점수 차이를 최대화 | win/lose만으로 부족 |
| depth limit과 평가 함수가 있음 | game tree search |
| move ordering/pruning이 중요 | alpha-beta 후보 |

minimax는 state 수가 작거나 depth가 제한될 때 정확합니다. branching이 크면 pruning, memoization, heuristic evaluation이 필수입니다.

## 5. 확률이 있으면 MDP

상대가 아니라 확률 전이가 결과를 바꾸고, action을 골라 기대 보상을 최대화하면 MDP입니다.

```text
V(s) = max_a reward(s,a) + sum_t P(t|s,a) V(t)
```

상대와 확률이 모두 있으면 stochastic game이지만, 대회 문제에서는 한쪽을 고정 정책이나 chance node로 단순화하는 경우가 많습니다.

## 6. 숨은 정보가 있으면 정보 구조 확인

카드, 안개, 비공개 상태가 있으면 실제 state를 기준으로 행동하면 정보 누출입니다.

| 상황 | 접근 |
| --- | --- |
| 가능한 상태 집합만 관리 | information set search |
| 상태별 확률이 중요 | belief state |
| observation model이 명확 | POMDP |
| 정확 계산이 너무 큼 | sampling/MCTS |

숨은 정보를 무작위로 하나 뽑아 perfect-information game처럼 푸는 determinization은 baseline일 뿐입니다. 서로 다른 숨은 상태에서 같은 행동을 해야 한다는 제약을 깨기 쉽습니다.

## 7. 작은 예시

```text
문제 A: 돌더미에서 1,2,3개를 가져가고 마지막에 가져간 사람이 승리
-> impartial game, Grundy 또는 win/lose DP

문제 B: 체스처럼 MAX/MIN이 서로 다른 기물 배치를 평가
-> minimax, alpha-beta

문제 C: 행동 후 70%/30%로 다음 상태가 달라지고 보상이 있음
-> MDP

문제 D: 상대 카드가 보이지 않고 관측 history만 있음
-> imperfect information/POMDP
```

같은 "게임" 단어가 있어도 네 문제는 완전히 다른 도구를 요구합니다.

## 8. 독립 합성의 함정

Grundy xor는 subgame이 독립일 때만 됩니다.

```text
전체 행동이 한 subgame에만 영향을 준다 -> xor 가능
한 행동이 여러 subgame 조건을 동시에 바꾼다 -> xor 위험
공유 resource가 있다 -> 독립 아님
```

구간 게임에서 한 수가 구간을 둘로 쪼개면 독립 subgame이 생길 수 있습니다. 반대로 남은 횟수 제한처럼 전체 공유 제약이 있으면 독립이 깨집니다.

## 9. 구현 선택 기준

| state 수/구조 | 추천 |
| --- | --- |
| DAG, win/lose | Grundy or boolean DP |
| 작은 game tree | minimax + memo |
| 깊고 branching 큼 | alpha-beta + move ordering |
| 확률 transition | expected value DP |
| hidden state | belief/information set |
| 실시간 AI | MCTS/heuristic |

정확한 정답을 요구하는 문제에서 MCTS 같은 근사를 쓰면 보통 틀립니다. 근사가 허용되는 문제인지부터 확인합니다.

## 10. 자주 하는 실수

1. partisan game에 Grundy xor를 적용한다.
2. 반복 상태를 무조건 losing으로 처리한다.
3. hidden state를 알고 있는 것처럼 minimax를 돌린다.
4. 확률 node와 opponent choice node를 같은 `min`/`max`로 처리한다.
5. score game인데 win/lose DP만 저장한다.

## 11. 문제를 볼 때 체크할 조건

- 두 플레이어의 move set이 같은가?
- subgame이 독립인가?
- 확률 전이가 있는가?
- hidden information이 있는가?
- 정확 최적값이 필요한가, 좋은 정책이면 되는가?

## 12. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: game theory applications `/practice/...` 문제 필요 | Grundy와 minimax 분류 | impartial |
| 표준 | TODO: split game xor `/practice/...` 문제 필요 | 독립 subgame 판정 | Sprague-Grundy |
| 응용 | TODO: stochastic game modeling `/practice/...` 문제 필요 | chance node와 max node 분리 | MDP |
| 함정 | TODO: hidden information game `/practice/...` 문제 필요 | 정보 누출 방지 | belief state |
