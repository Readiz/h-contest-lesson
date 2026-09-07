# Minimax와 Alpha-Beta Pruning

Minimax는 두 플레이어가 번갈아 최선의 수를 둔다고 가정하고 게임 트리의 값을 계산하는 알고리즘입니다. Alpha-Beta Pruning은 이미 더 좋은 선택이 보장된 가지를 잘라 탐색량을 줄입니다.

## 언제 Minimax인가

| 문제 신호 | 접근 |
| --- | --- |
| 두 플레이어가 번갈아 수를 둔다 | game tree |
| 한쪽은 점수를 최대화, 다른 쪽은 최소화 | minimax |
| 완전 탐색 가능한 깊이가 작다 | exact minimax |
| 깊이가 크지만 평가 함수가 있다 | depth-limited search |
| 같은 상태가 여러 경로로 나온다 | memoization/transposition |

Nim처럼 impartial game의 합으로 분해되면 Grundy가 더 낫습니다. 체스류 게임처럼 상태 평가와 탐색이 필요하면 minimax 계열을 봅니다.

## Minimax 정의

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

점수는 항상 최대화하는 플레이어 관점으로 계산합니다. 턴이 바뀌어도 승패 점수의 기준은 뒤집지 않습니다.

## Alpha-Beta Pruning

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

위 코드는 미리 만든 트리의 `value`를 읽는 형태입니다. 상태를 직접 변경하며 탐색한다면 자식 탐색 직후 move를 되돌려야 다음 형제도 같은 부모 상태에서 시작합니다.

## Move ordering

Alpha-beta는 좋은 수를 먼저 보면 가지치기가 강해집니다.

| ordering 기준 | 이유 |
| --- | --- |
| 즉시 이기는 수 먼저 | 빠른 beta cutoff |
| capture/큰 점수 변화 먼저 | 평가가 크게 갈림 |
| 이전 iteration의 best move 먼저 | iterative deepening과 궁합 |
| heuristic score 정렬 | pruning 효율 증가 |

순서가 나쁘면 alpha-beta도 거의 minimax와 비슷하게 많은 노드를 봅니다.

## Depth-limited Search

전체 게임 트리가 너무 크면 깊이를 제한하고 evaluation function을 사용합니다.

```text
if depth == 0:
    return heuristicScore(state)
```

종료된 게임은 깊이 제한에 도달했더라도 실제 승패를 반환합니다. 아직 끝나지 않은 상태에만 평가 함수를 적용하며, 이 함수도 최대화하는 플레이어 관점을 사용합니다. 이 값이 부정확하면 더 깊게 봐도 잘못된 결론을 낼 수 있습니다.

## Memoization과 Transposition

같은 상태가 여러 move order로 다시 나타날 수 있습니다. 이때 state hash를 key로 memoization하면 탐색량을 줄일 수 있습니다.

```text
memo[(stateHash, depth, maximizing)] = value
```

alpha-beta와 transposition table을 함께 쓸 때는 bound type(exact/lower/upper)을 구분해야 정확합니다. cutoff로 얻은 하한·상한을 정확한 점수로 재사용하면 잘못된 가지치기가 생깁니다.

## 시간 복잡도

| 방식 | 시간 |
| --- | ---: |
| minimax | `O(b^d)` |
| alpha-beta 최선 ordering | 대략 `O(b^(d/2))` |
| alpha-beta 최악 ordering | `O(b^d)` |

`b`는 branching factor, `d`는 depth입니다. alpha-beta는 정답을 바꾸지 않고 탐색량만 줄입니다.
