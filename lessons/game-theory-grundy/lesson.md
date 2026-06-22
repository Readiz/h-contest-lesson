# Game Theory와 Grundy Number

Game Theory 문제 중 impartial game은 두 플레이어가 같은 선택지를 가지고, 마지막 수를 둔 사람이 이기는 형태가 많습니다. 이런 게임은 각 상태의 Grundy number를 계산해 여러 게임의 합까지 판정할 수 있습니다.

이 레슨은 mex와 Sprague-Grundy theorem을 대회 문제 풀이 관점에서 정리합니다.

1. 상태를 winning/losing으로 분류한다.
2. 각 상태의 Grundy number를 mex로 계산한다.
3. 독립 게임 여러 개의 xor로 전체 승패를 판정한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 동적 계획법, DFS, DAG 상태 그래프, xor
- 함께 보면 좋은 레슨: 동적 계획법, Proof와 Invariant, 확률과 기대값
- 다음에 볼 레슨: minimax, alpha-beta pruning, partisan game

## 1. Impartial Game

Impartial game은 현재 가능한 움직임이 플레이어에 따라 달라지지 않는 게임입니다.

| 조건 | 의미 |
| --- | --- |
| 두 플레이어의 행동 규칙이 같다 | impartial |
| 더 움직일 수 없으면 진다 | normal play |
| 상태가 되돌아오지 않는다 | DAG DP 가능 |
| 여러 독립 pile이 있다 | xor 합성 가능 |

Nim, 돌 더미 게임, DAG 위 token 이동이 대표 예시입니다.

## 2. Winning과 Losing

가장 기본 분류는 아래입니다.

```text
losing state: 갈 수 있는 모든 상태가 winning
winning state: 갈 수 있는 상태 중 losing이 하나라도 있음
```

움직일 수 없는 terminal state는 losing입니다. 상대에게 losing state를 넘길 수 있으면 현재는 winning입니다.

```cpp compile-check
#include <vector>
using namespace std;

vector<int> computeWinLose(const vector<vector<int>>& graph) {
    int n = (int)graph.size();
    vector<int> winning(n, 0);

    for (int state = n - 1; state >= 0; --state) {
        for (int next : graph[state]) {
            if (!winning[next]) {
                winning[state] = 1;
                break;
            }
        }
    }

    return winning;
}
```

위 코드는 간선이 항상 더 큰 번호로 간다는 DAG 순서를 가정합니다. 일반 DAG라면 위상 정렬이나 DFS memoization이 필요합니다.

## 3. Grundy Number와 mex

Grundy number는 상태를 Nim pile 크기처럼 바꿔 주는 값입니다.

```text
grundy[state] = mex({ grundy[next] | next is reachable in one move })
```

`mex`는 집합에 없는 가장 작은 0 이상의 정수입니다.

```text
mex({0, 1, 3}) = 2
mex({1, 2}) = 0
```

Grundy number가 0이면 losing state입니다. 0이 아니면 winning state입니다.

## 4. Grundy 계산

```cpp compile-check
#include <vector>
using namespace std;

int mexOf(const vector<int>& values) {
    vector<int> seen(values.size() + 2, 0);
    for (int value : values) {
        if (0 <= value && value < (int)seen.size()) {
            seen[value] = 1;
        }
    }
    for (int i = 0; i < (int)seen.size(); ++i) {
        if (!seen[i]) {
            return i;
        }
    }
    return (int)seen.size();
}

int grundyDfs(int state, const vector<vector<int>>& graph, vector<int>& memo) {
    if (memo[state] != -1) {
        return memo[state];
    }

    vector<int> nextValues;
    for (int next : graph[state]) {
        nextValues.push_back(grundyDfs(next, graph, memo));
    }
    memo[state] = mexOf(nextValues);
    return memo[state];
}
```

상태 그래프에 cycle이 있으면 이 DFS는 끝나지 않습니다. Sprague-Grundy 기본형은 보통 finite DAG game에서 사용합니다.

## 5. 게임의 합

독립적인 게임 여러 개를 동시에 하고, 한 턴에 그중 하나에서만 움직인다고 합시다. 전체 Grundy number는 각 게임 Grundy의 xor입니다.

```text
G(total) = G(game1) xor G(game2) xor ... xor G(gameK)
```

전체 xor가 0이면 losing, 0이 아니면 winning입니다.

```cpp compile-check
#include <vector>
using namespace std;

bool firstPlayerWins(const vector<int>& grundyValues) {
    int xorSum = 0;
    for (int value : grundyValues) {
        xorSum ^= value;
    }
    return xorSum != 0;
}
```

이 성질이 Nim의 핵심이고, 여러 독립 subgame으로 분해되는 문제에서 강력합니다.

## 6. 패턴 찾기

상태 수가 매우 크면 직접 DP가 어렵습니다. 작은 값의 Grundy number를 계산해 주기를 찾는 경우가 있습니다.

```text
0 1 0 1 2 0 1 0 1 2 ...
```

하지만 주기 추정은 위험합니다. 문제에서 주기를 증명할 수 있거나, 제한이 주기 탐색을 의도한 형태일 때만 사용합니다.

## 7. Misere 조건

마지막 수를 둔 사람이 지는 misere play는 일반 Grundy 규칙과 달라질 수 있습니다. 특히 Nim에서는 모든 pile 크기가 1 이하일 때 별도 처리가 필요합니다.

문제 statement에서 "더 이상 움직일 수 없는 사람이 패배"인지 "승리"인지 반드시 확인합니다. 대부분은 normal play지만, 함정으로 바뀌는 경우가 있습니다.

## 8. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| win/lose DAG DP | `O(V + E)` | `O(V)` |
| Grundy DFS | `O(V + E + mex cost)` | `O(V)` |
| 여러 게임 xor | `O(K)` | `O(1)` |
| 주기 탐색 | 문제별 | 값 배열 |

mex 계산은 outdegree 크기만큼의 seen 배열이면 충분합니다. 전역 큰 배열을 매번 초기화하면 느릴 수 있으니 timestamp trick을 쓰기도 합니다.

## 9. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| terminal state를 winning으로 둠 | 전체 승패 반전 | 움직임 없음 = losing |
| cycle 있는 게임에 DFS memo만 사용 | 무한 재귀 | 상태 그래프 DAG 확인 |
| 여러 게임을 합산으로 더함 | 오답 | Grundy는 xor |
| Grundy 0과 losing의 관계를 반대로 봄 | 승패 반전 | `G=0`이면 losing |
| misere play를 normal로 처리 | 마지막 수 조건 오답 | statement 문장 확인 |
| 주기를 근거 없이 사용 | 숨은 케이스 오답 | 주기 증명 또는 충분한 조건 |

## 10. 문제를 볼 때 체크할 조건

1. 두 플레이어가 같은 move set을 갖는 impartial game인가?
2. 움직일 수 없는 상태의 승패가 normal play인가?
3. 상태 그래프가 DAG인가?
4. 독립 subgame의 합으로 분해되는가?
5. Grundy number가 필요한가, 단순 win/lose DP로 충분한가?
6. 상태 수가 크다면 주기나 수식 패턴을 증명할 수 있는가?

Game Theory 문제는 구현보다 상태 정의가 중요합니다. "상대에게 losing state를 넘기는가"로 시작하고, 여러 독립 게임이 보이면 Grundy xor로 확장합니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 돌 가져가기 게임 `/practice/...` 문제 필요 | terminal losing과 win/lose DP | impartial game |
| 표준 | TODO: Grundy number 계산 `/practice/...` 문제 필요 | mex와 DFS memoization | Sprague-Grundy |
| 응용 | TODO: 여러 pile 게임 `/practice/...` 문제 필요 | Grundy xor 합성 | nim xor |
| 함정 | TODO: misere play `/practice/...` 문제 필요 | 마지막 수 조건 별도 처리 | misere |
