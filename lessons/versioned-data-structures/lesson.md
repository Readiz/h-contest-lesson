# Versioned Data Structures

Versioned Data Structures는 update 이후에도 과거 상태를 보존하거나 조회해야 하는 자료구조를 묶는 허브입니다. Persistent Segment Tree, Persistent Lazy Segment Tree, Persistent Union-Find, Persistent Queue/Stack, Persistent Sequence Queries는 모두 "상태를 통째로 복사하지 않고 버전 이름표만 바꾸는" 같은 문제군에 속합니다.

이 허브는 persistence, rollback, retroactivity를 먼저 구분하고, 필요한 구조로 내려가게 합니다. 과거 상태를 임의로 조회하는 문제와 DFS 중 되돌리기만 필요한 문제는 구현이 다릅니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Segment Tree, Union-Find, Coordinate Compression, Offline Queries
- 함께 보면 좋은 레슨: Rollback Techniques, Retroactive Data Structures, Offline Range Query Techniques
- 다음에 볼 레슨: Offline and Time-Axis Techniques, Wavelet Tree, Dynamic Connectivity

## 1. 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| point update 뒤 과거 배열 버전을 질의한다 | [Persistent Segment Tree](pages/persistent-segment-tree.md) |
| range update와 range query가 모두 version별로 필요하다 | [Persistent Lazy Segment Tree](pages/persistent-lazy-segment-tree.md) |
| union-only history에서 과거 연결성을 묻는다 | [Persistent Union-Find](pages/persistent-union-find.md) |
| version별 stack/queue top이나 front가 필요하다 | [Persistent Queue and Stack](pages/persistent-queue-stack.md) |
| version별 배열/sequence에서 kth, count, range query가 필요하다 | [Persistent Sequence Queries](pages/persistent-sequence-queries.md) |
| rollback인지 persistence인지 헷갈린다 | [Versioning Model Map](pages/versioning-model-map.md) |

## 2. Persistence, Rollback, Retroactivity

| 방식 | 핵심 | 잘 맞는 문제 |
| --- | --- | --- |
| Persistence | 과거 version root를 보존하고 새 branch를 만든다 | version id가 query에 직접 등장 |
| Rollback | 현재 상태를 snapshot으로 되돌린다 | DFS, divide and conquer over time |
| Partial persistence | 시간은 선형이고 과거 조회만 한다 | union-only DSU history |
| Retroactivity | 과거 operation 자체를 삽입/삭제한다 | timeline 편집 문제 |

단순히 "되돌린다"는 표현만 보고 persistent structure를 만들면 과할 수 있습니다. query가 임의 version을 직접 지정하면 persistence, 재귀를 빠져나오며 undo하면 rollback이 보통 더 맞습니다.

## 3. 구현 전 체크리스트

- version이 선형 history인가, tree처럼 branch되는가?
- query가 과거 version을 임의로 지정하는가?
- update가 point, range, merge, push/pop 중 무엇인가?
- node 수가 `updates * logN` 범위로 메모리 제한에 맞는가?
- old node를 직접 수정하지 않는다는 원칙이 코드에서 지켜지는가?
- rollback이나 offline 재배치로 더 단순해지지 않는가?

## 4. 연습 문제

이 허브의 연습 흐름은 [Practice Set](pages/practice-set.md)에 모읍니다. 적절한 h-contest 문제가 아직 없는 칸은 임의 ID를 넣지 않고 `TODO`로 둡니다.
