# Versioned Data Structures

Versioned Data Structures는 update 이후에도 과거 상태를 보존하거나 조회해야 하는 자료구조를 묶는 허브입니다. Persistent Segment Tree, Persistent Lazy Segment Tree, Persistent Union-Find, Persistent Queue/Stack, Persistent Sequence Queries는 모두 "상태를 통째로 복사하지 않고 버전 이름표만 바꾸는" 같은 문제군에 속합니다.

이 허브는 persistence, rollback, retroactivity를 먼저 구분하고, 필요한 구조로 내려가게 합니다. 과거 상태를 임의로 조회하는 문제와 DFS 중 되돌리기만 필요한 문제는 구현이 다릅니다.

## 선수 지식과 이어지는 레슨

- 선수 지식: Segment Tree, Union-Find, Coordinate Compression, Offline Queries
- 함께 보면 좋은 레슨: Rollback Techniques, Retroactive Data Structures, Offline Range Query Techniques
- 다음에 볼 레슨: Offline and Time-Axis Techniques, Wavelet Tree, Dynamic Connectivity

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| point update 뒤 과거 배열 버전을 질의한다 | [Persistent Segment Tree](pages/persistent-segment-tree.md) |
| range update와 range query가 모두 version별로 필요하다 | [Persistent Lazy Segment Tree](pages/persistent-lazy-segment-tree.md) |
| union-only history에서 과거 연결성을 묻는다 | [Persistent Union-Find](pages/persistent-union-find.md) |
| version별 stack/queue top이나 front가 필요하다 | [Persistent Queue and Stack](pages/persistent-queue-stack.md) |
| version별 배열/sequence에서 kth, count, range query가 필요하다 | [Persistent Sequence Queries](pages/persistent-sequence-queries.md) |

## Persistence, Rollback, Retroactivity

| 방식 | 핵심 | 잘 맞는 문제 |
| --- | --- | --- |
| Persistence | 과거 version root를 보존하고 새 branch를 만든다 | version id가 query에 직접 등장 |
| Rollback | 현재 상태를 snapshot으로 되돌린다 | DFS, divide and conquer over time |
| Partial persistence | 시간은 선형이고 과거 조회만 한다 | union-only DSU history |
| Retroactivity | 과거 operation 자체를 삽입/삭제한다 | timeline 편집 문제 |

단순히 "되돌린다"는 표현만 보고 persistent structure를 만들면 과할 수 있습니다. query가 임의 version을 직접 지정하면 persistence, 재귀를 빠져나오며 undo하면 rollback이 보통 더 맞습니다.

## 버전과 메모리

버전이 분기하지 않고 질의를 시간 순서로 처리할 수 있으면 Fenwick/Segment Tree sweep으로 충분할 수 있습니다. 분기하는 버전에서 과거 상태를 다시 조회해야 하면 root를 보존합니다. 정적 구간의 kth 질의는 prefix별 root 두 개의 차이로 표현할 수 있습니다.

노드 수는 초기 build에 `update 수 × 갱신당 생성 노드 수`를 더해 계산합니다. 점 갱신은 보통 `O(log N)`개를 복사하지만 lazy propagation과 binary lifting을 붙이면 메모리 상수가 커집니다. 질의 중 lazy push도 과거 노드를 바꾸는지 확인해야 합니다. 과거 DSU 상태를 보존할 때 일반적인 path compression을 그대로 적용하면 안 됩니다.

## 연습 문제

이 허브의 연습 흐름은 [Practice Set](pages/practice-set.md)에 모읍니다.
