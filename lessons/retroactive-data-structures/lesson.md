# Retroactive Data Structures

Retroactive Data Structures는 과거 시점에 update를 삽입하거나 삭제했을 때, 이후 시간의 자료구조 상태와 query 답이 어떻게 바뀌는지 다루는 관점입니다. 완전한 retroactivity는 구현 난도가 높지만, 대회에서는 시간축 segment tree, divide and conquer, rollback, persistent structure를 조합한 제한된 형태로 자주 나타납니다.

이 레슨은 Rollback Techniques, Persistent Union-Find, Offline Queries 이후에 보는 자료구조/오프라인 심화입니다.

1. partial persistence, rollback, retroactivity의 차이를 구분한다.
2. "과거 operation 변경"을 시간축 update interval로 바꾸는 모델을 익힌다.
3. offline이면 segment tree over time과 rollback으로 많은 retroactive 문제를 처리할 수 있다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: rollback, persistence, offline query, segment tree over time
- 함께 보면 좋은 레슨: Rollback Techniques, Persistent Union-Find, Dynamic Connectivity
- 다음에 볼 레슨: offline range query techniques, kinetic data structures, fully retroactive models

## 1. 문제 신호

| 문제 표현 | Retroactive 관점 |
| --- | --- |
| 과거 시점에 update를 삽입/삭제 | operation timeline 변경 |
| `t` 시점의 자료구조 상태를 묻는다 | time-indexed query |
| 삭제가 있는 동적 연결성 | edge active interval |
| query 전체를 미리 알 수 있다 | offline retroactive 가능 |
| update가 비가역적이고 online | 완전 retroactivity는 어려울 수 있음 |

문제에서 "과거"라는 말이 나오면 바로 어려운 구조를 떠올리기보다, 전체 query를 미리 알고 offline으로 바꿀 수 있는지 먼저 봅니다.

## 2. 세 개념 구분

| 개념 | 할 수 있는 일 | 대표 구현 |
| --- | --- | --- |
| Rollback | 현재 재귀 경로의 상태를 이전 snapshot으로 되돌림 | history stack |
| Persistence | 과거 version을 query하거나 새 version을 만듦 | path copying |
| Retroactivity | 과거 operation 자체를 삽입/삭제하고 이후를 바꿈 | time tree, balanced timeline |

Rollback은 stack discipline이 있어야 쉽습니다. Persistence는 version이 고정되어 있을 때 강합니다. Retroactivity는 operation timeline이 바뀌므로 가장 어렵습니다.

## 3. Offline Retroactivity

전체 operation을 미리 알 수 있다면, 과거 삽입/삭제를 "어떤 시간 구간 동안 update가 활성인가"로 바꿀 수 있습니다.

```text
operation add edge e at time a
operation remove edge e at time b
=> edge e is active on [a, b)

segment tree over query time:
  interval [a, b)를 덮는 노드에 e 추가
  DFS 중 rollback DSU로 상태 적용
```

이 패턴은 offline dynamic connectivity와 같습니다. 과거 operation 변경이 있더라도 최종 timeline을 정리할 수 있으면 rollback으로 처리됩니다.

## 4. Time Segment Tree Skeleton

아래 코드는 interval update를 시간축 segment tree에 넣고 DFS에서 rollback 가능한 구조를 호출하는 뼈대입니다.

```cpp compile-check
#include <functional>
#include <utility>
#include <vector>
using namespace std;

struct RetroactiveTimeTree {
    int queryCount = 0;
    vector<vector<pair<int, int>>> tree;

    explicit RetroactiveTimeTree(int q) : queryCount(q), tree(4 * q) {}

    void addInterval(int node, int left, int right, int ql, int qr, pair<int, int> edge) {
        if (qr <= left || right <= ql) {
            return;
        }
        if (ql <= left && right <= qr) {
            tree[node].push_back(edge);
            return;
        }
        int mid = (left + right) / 2;
        addInterval(node * 2, left, mid, ql, qr, edge);
        addInterval(node * 2 + 1, mid, right, ql, qr, edge);
    }

    template <class RollbackStructure, class AnswerLeaf>
    void dfs(int node, int left, int right, RollbackStructure& structure, AnswerLeaf answerLeaf) {
        int snap = structure.snapshot();
        for (auto edge : tree[node]) {
            structure.apply(edge.first, edge.second);
        }

        if (right - left == 1) {
            answerLeaf(left, structure);
        } else {
            int mid = (left + right) / 2;
            dfs(node * 2, left, mid, structure, answerLeaf);
            dfs(node * 2 + 1, mid, right, structure, answerLeaf);
        }

        structure.rollback(snap);
    }
};
```

`RollbackStructure`는 `snapshot`, `apply`, `rollback`을 제공해야 합니다. DSU뿐 아니라 frequency table, min/max aggregate, answer counter에도 같은 패턴을 쓸 수 있습니다.

## 5. Operation Insert/Delete 모델링

과거 operation을 삽입하거나 삭제하는 명령이 들어오면, 먼저 operation id별 active interval을 정리합니다.

| 명령 | timeline 처리 |
| --- | --- |
| insert operation X at time t | X의 적용 시작 시점 기록 |
| delete operation X at time t | X의 active interval을 닫음 |
| query at time t | leaf `t`에서 현재 상태 답변 |
| 끝까지 살아 있는 operation | `[start, Q)` interval로 닫음 |

입력 순서와 operation이 적용되는 논리 시간은 다를 수 있습니다. 좌표를 하나로 통일해야 합니다.

## 6. Online이면 왜 어려운가

online fully retroactive structure는 과거 update 하나가 현재 답 전체를 바꿀 수 있습니다. 예를 들어 priority queue에서 과거 insert/delete를 바꾸면 현재 minimum이 연쇄적으로 변합니다.

```text
time 1: insert 5
time 2: deleteMin -> 5 제거
time 3: insert 3

과거 time 1에 insert 1을 추가하면 time 2의 deleteMin 결과가 바뀌고,
그 뒤 상태도 모두 달라진다.
```

이런 문제는 일반 persistence나 rollback만으로는 부족합니다. 대회에서는 대부분 offline으로 바꾸거나 operation 종류가 제한됩니다.

## 7. 어떤 구조가 잘 맞는가

| 구조 | Retroactive 처리 가능성 |
| --- | --- |
| Union-Find connectivity | offline interval + rollback DSU에 잘 맞음 |
| 누적 frequency | add/remove가 되돌릴 수 있으면 가능 |
| Segment Tree aggregate | 방문 node old value 기록 필요 |
| Priority Queue deleteMin | fully retroactive는 어려움 |
| Shortest path | update 영향이 넓어 제한 없이는 어려움 |

operation이 commutative하거나 rollback 가능한 작은 변경으로 표현되면 offline 처리가 쉬워집니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| active interval 정리 | `O(Q log Q)` 또는 map 비용 |
| interval을 time tree에 삽입 | update마다 `O(log Q)`개 노드 |
| DFS 처리 | `O((Q + intervals log Q) * apply cost)` |
| rollback 비용 | 기록한 변경 수에 비례 |

online fully retroactive 문제는 구조마다 별도 복잡도가 필요하며, 이 레슨의 time tree skeleton으로 바로 해결되지 않습니다.

## 9. 자주 하는 실수

1. persistence가 있으면 과거 operation 삽입도 자동으로 된다고 생각한다.
2. 입력 순서와 논리 시간을 섞어 interval을 잘못 만든다.
3. rollback 구조에서 전역 answer 값을 기록하지 않는다.
4. active interval의 오른쪽 끝을 inclusive/exclusive로 섞는다.
5. online 요구 문제를 offline으로 재배열해도 되는지 확인하지 않는다.

## 10. 문제를 볼 때 체크할 조건

- 모든 query를 미리 볼 수 있는가?
- 과거 operation의 적용 구간을 interval로 표현할 수 있는가?
- 상태 변경을 rollback할 수 있는가?
- query leaf에서 필요한 답이 현재 상태만으로 계산되는가?
- fully retroactive online 구조가 필요한 문제는 아닌가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: retroactive data structure `/practice/...` 문제 필요 | operation interval 만들기 | active interval |
| 표준 | TODO: offline retroactive connectivity `/practice/...` 문제 필요 | time tree + rollback DSU | segment tree over time |
| 응용 | TODO: retroactive frequency query `/practice/...` 문제 필요 | rollback counter | old value history |
| 함정 | TODO: online retroactive priority queue `/practice/...` 문제 필요 | offline 불가 판정 | fully retroactive |
