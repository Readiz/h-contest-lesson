# Game Theory Applications

Game Theory Applications는 Grundy, minimax, MDP, imperfect information 모델을 문제 신호별로 고르는 레슨입니다. 개별 알고리즘을 외우는 것보다 게임의 정보 구조, 확률, 독립 합성 여부를 먼저 분류하는 것이 핵심입니다.

## 분류표

| 문제 신호 | 우선 모델 |
| --- | --- |
| 양쪽 선택지가 같고 마지막 행동자가 승리 | impartial game, Grundy |
| 여러 독립 더미/구간이 합쳐짐 | xor sum |
| MAX/MIN이 번갈아 최적 선택 | minimax |
| 확률 전이가 있고 보상 기대값 최대화 | MDP |
| 숨은 정보가 있고 관측만 가능 | imperfect information 또는 POMDP |
| 정확 최적보다 좋은 move가 필요 | MCTS/heuristic search |

처음부터 구현을 고르면 위험합니다. state, turn, information, randomness 네 가지를 먼저 분리합니다.

## Impartial Game인지 확인

Grundy를 쓰려면 보통 아래 조건이 필요합니다.

1. 두 플레이어가 같은 move set을 가진다.
2. 확률이 없다.
3. 게임이 유한하며 수를 둘 수 없는 플레이어가 지는 normal play다.
4. 여러 subgame이 독립이면 xor로 합성된다.

move set이 플레이어마다 다르거나 점수가 누적되는 게임이면 Grundy가 아닐 가능성이 큽니다.

## 독립 부분 게임

Grundy의 mex 계산과 독립 합성 구현은 [Game Theory와 Grundy 수](https://h.readiz.com/learn/game-theory-grundy)를 사용합니다. 이 페이지에서는 게임의 정보·확률·상대 선택 조건을 구분합니다.

## Minimax로 넘어가는 조건

아래 중 하나라도 있으면 Grundy 대신 minimax를 봅니다.

| 조건 | 이유 |
| --- | --- |
| 플레이어별 move가 다름 | impartial이 아님 |
| 점수 차이를 최대화 | win/lose만으로 부족 |
| depth limit과 평가 함수가 있음 | game tree search |
| move ordering/pruning이 중요 | alpha-beta 후보 |

minimax는 terminal까지 탐색하고 정확한 보상을 쓸 때 정확합니다. 깊이 제한에서 heuristic 평가로 끊으면 근사입니다. branching이 크면 pruning, memoization, heuristic evaluation이 필수입니다.

## 확률이 있으면 MDP

상대가 아니라 확률 전이가 결과를 바꾸고, action을 골라 기대 보상을 최대화하면 MDP입니다.

```text
V_h(s) = max_a [reward(s,a) + sum_t P(t|s,a) V_{h-1}(t)]
V_0(s) = terminal reward
```

위 식은 유한 지평의 기대값 DP입니다. 무한 지평이면 할인이나 적절한 종료 조건을 별도로 둡니다.

상대와 확률이 모두 있으면 stochastic game이지만, 대회 문제에서는 한쪽을 고정 정책이나 chance node로 단순화하는 경우가 많습니다.

## 숨은 정보가 있으면 정보 구조 확인

카드, 안개, 비공개 상태가 있으면 실제 state를 기준으로 행동하면 정보 누출입니다.

| 상황 | 접근 |
| --- | --- |
| 가능한 상태 집합만 관리 | information set search |
| 상태별 확률이 중요 | belief state |
| observation model이 명확 | POMDP |
| 정확 계산이 너무 큼 | sampling/MCTS |

숨은 정보를 무작위로 하나 뽑아 perfect-information game처럼 푸는 determinization은 baseline일 뿐입니다. 서로 다른 숨은 상태에서 같은 행동을 해야 한다는 제약을 깨기 쉽습니다.

## 작은 예시

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

## 독립 합성의 함정

Grundy xor는 subgame이 독립일 때만 됩니다.

```text
전체 행동이 한 subgame에만 영향을 준다 -> xor 가능
한 행동이 여러 subgame 조건을 동시에 바꾼다 -> xor 위험
공유 resource가 있다 -> 독립 아님
```

구간 게임에서 한 수가 구간을 둘로 쪼개면 독립 subgame이 생길 수 있습니다. 반대로 남은 횟수 제한처럼 전체 공유 제약이 있으면 독립이 깨집니다.

## 구현 선택 기준

| state 수/구조 | 추천 |
| --- | --- |
| DAG, win/lose | Grundy or boolean DP |
| 작은 game tree | minimax + memo |
| 깊고 branching 큼 | alpha-beta + move ordering |
| 확률 transition | expected value DP |
| hidden state | belief/information set |
| 실시간 AI | MCTS/heuristic |

정확한 정답을 요구하는 문제에서 MCTS 같은 근사를 쓰면 보통 틀립니다. 근사가 허용되는 문제인지부터 확인합니다.
