# Minimax와 Alpha-Beta Pruning

Minimax는 두 플레이어가 번갈아 최선의 수를 둔다고 가정하고 게임 트리의 값을 계산하는 알고리즘입니다. Alpha-Beta Pruning은 이미 더 좋은 선택이 보장된 가지를 잘라 탐색량을 줄입니다.

이 레슨은 Grundy number처럼 수학적으로 닫히는 impartial game이 아니라, 실제 game tree를 탐색해야 하는 상황을 다룹니다.

1. 현재 플레이어가 최대화/최소화 중 무엇을 하는지 구분한다.
2. terminal state와 evaluation function을 정의한다.
3. alpha와 beta로 불필요한 가지를 자른다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: DFS, 재귀, 게임 상태 표현, Game Theory와 Grundy Number
- 함께 보면 좋은 레슨: Game Theory와 Grundy Number, Testing과 Stress Test
- 다음에 볼 레슨: iterative deepening, transposition table, Monte Carlo tree search

## 1. 언제 Minimax인가

| 문제 신호 | 접근 |
| --- | --- |
| 두 플레이어가 번갈아 수를 둔다 | game tree |
| 한쪽은 점수를 최대화, 다른 쪽은 최소화 | minimax |
| 완전 탐색 가능한 깊이가 작다 | exact minimax |
| 깊이가 크지만 평가 함수가 있다 | depth-limited search |
| 같은 상태가 여러 경로로 나온다 | memoization/transposition |

Nim처럼 impartial game의 합으로 분해되면 Grundy가 더 낫습니다. 체스류 게임처럼 상태 평가와 탐색이 필요하면 minimax 계열을 봅니다.

## 2. Minimax 정의

현재 플레이어가 최대화한다고 보면:

```text
value(state) = max value(next)  if current is maximizing
value(state) = min value(next)  if current is minimizing
```

terminal state에서는 승패나 점수를 바로 반환합니다.

```text
win = +1
draw = 0
lose = -1
```

점수 크기는 문제에 맞게 바꿀 수 있습니다.

## 3. Alpha-Beta Pruning

`alpha`는 maximizing player가 현재까지 보장한 최선 값입니다. `beta`는 minimizing player가 현재까지 보장한 최선 값입니다.

탐색 중 `alpha >= beta`가 되면 더 봐도 부모가 선택하지 않을 가지이므로 잘라낼 수 있습니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct GameState {
    int value = 0;
    bool terminal = false;
    vector<GameState> nextStates;
};

int evaluateTerminal(const GameState& state) {
    return state.value;
}

int alphaBeta(const GameState& state, int depth, int alpha, int beta, bool maximizing) {
    if (depth == 0 || state.terminal) {
        return evaluateTerminal(state);
    }

    if (maximizing) {
        int best = -1000000000;
        for (const GameState& next : state.nextStates) {
            best = max(best, alphaBeta(next, depth - 1, alpha, beta, false));
            alpha = max(alpha, best);
            if (alpha >= beta) {
                break;
            }
        }
        return best;
    }

    int best = 1000000000;
    for (const GameState& next : state.nextStates) {
        best = min(best, alphaBeta(next, depth - 1, alpha, beta, true));
        beta = min(beta, best);
        if (alpha >= beta) {
            break;
        }
    }
    return best;
}
```

실전에서는 `nextStates`를 미리 모두 저장하기보다 move를 생성하고 적용/되돌리기 하는 방식이 많습니다.

## 4. Move ordering

Alpha-beta는 좋은 수를 먼저 보면 가지치기가 강해집니다.

| ordering 기준 | 이유 |
| --- | --- |
| 즉시 이기는 수 먼저 | 빠른 beta cutoff |
| capture/큰 점수 변화 먼저 | 평가가 크게 갈림 |
| 이전 iteration의 best move 먼저 | iterative deepening과 궁합 |
| heuristic score 정렬 | pruning 효율 증가 |

순서가 나쁘면 alpha-beta도 거의 minimax와 비슷하게 많은 노드를 봅니다.

## 5. Depth-limited Search

전체 게임 트리가 너무 크면 깊이를 제한하고 evaluation function을 사용합니다.

```text
if depth == 0:
    return heuristicScore(state)
```

평가 함수는 현재 상태가 얼마나 유리한지를 숫자로 반환합니다. 이 값이 부정확하면 더 깊게 봐도 잘못된 결론을 낼 수 있습니다.

## 6. Memoization과 Transposition

같은 상태가 여러 move order로 다시 나타날 수 있습니다. 이때 state hash를 key로 memoization하면 탐색량을 줄일 수 있습니다.

```text
memo[(stateHash, depth, maximizing)] = value
```

alpha-beta와 transposition table을 함께 쓸 때는 bound type(exact/lower/upper)을 구분해야 정확합니다. 입문에서는 alpha-beta 없이 순수 minimax memoization부터 적용하는 것이 안전합니다.

## 7. 시간 복잡도

| 방식 | 시간 |
| --- | ---: |
| minimax | `O(b^d)` |
| alpha-beta 최선 ordering | 대략 `O(b^(d/2))` |
| alpha-beta 최악 ordering | `O(b^d)` |

`b`는 branching factor, `d`는 depth입니다. alpha-beta는 정답을 바꾸지 않고 탐색량만 줄입니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| maximizing/minimizing 턴을 반대로 넘김 | 승패 반전 | depth마다 player 전환 확인 |
| terminal 평가를 현재 플레이어 기준으로 섞음 | score 부호 오류 | 평가 기준을 한 플레이어로 고정 |
| alpha/beta 업데이트 위치 오류 | 잘못된 pruning | max는 alpha, min은 beta |
| move undo 누락 | 상태 오염 | apply/rollback 쌍 검증 |
| depth 0 평가와 terminal 평가 혼동 | 종료 상태 오평가 | terminal을 먼저 확인 |
| move ordering 없이 깊이만 늘림 | 시간 초과 | 좋은 후보 우선 정렬 |

## 9. 문제를 볼 때 체크할 조건

1. 게임이 Grundy처럼 수학적으로 분해되지 않는가?
2. 상태 수와 branching factor가 탐색 가능한가?
3. terminal score 기준을 한 플레이어 관점으로 고정했는가?
4. depth limit가 필요한가?
5. move ordering으로 pruning 효과를 낼 수 있는가?
6. 같은 상태가 반복되어 memoization이 필요한가?

Minimax는 "상대도 최선을 둔다"는 가정을 코드로 옮긴 것입니다. Alpha-beta는 그 결론을 바꾸지 않고, 볼 필요 없는 가지를 줄이는 탐색 최적화입니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 작은 게임 minimax `/practice/...` 문제 필요 | terminal score와 턴 전환 구현 | minimax |
| 표준 | TODO: alpha-beta pruning `/practice/...` 문제 필요 | alpha/beta cutoff 확인 | pruning |
| 응용 | TODO: depth-limited game search `/practice/...` 문제 필요 | evaluation function 설계 | heuristic evaluation |
| 함정 | TODO: 반복 상태 게임 `/practice/...` 문제 필요 | state hash와 memoization | transposition |
