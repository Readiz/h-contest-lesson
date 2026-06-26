# Offline and Time-Axis Techniques

Offline and Time-Axis Techniques는 질의를 입력 순서 그대로 처리하지 않고, 전체 query set을 본 뒤 더 쉬운 순서나 시간 구간 구조로 바꾸는 기법을 묶는 허브입니다. Mo's Algorithm, Parallel Binary Search, Rollback DSU, 시간축 Segment Tree, Offline Dynamic Connectivity, 제한된 Retroactive 구조는 모두 "시간을 다시 배치한다"는 같은 판단에서 출발합니다.

이 허브는 개별 알고리즘을 외우기 전에 다음 질문을 먼저 하게 합니다.

1. 질의를 재정렬해도 답의 의미가 보존되는가?
2. update가 시간 구간 `[l, r)`으로 바뀌는가?
3. 상태를 snapshot으로 되돌릴 수 있는가?
4. 과거 version 조회인지, 과거 operation 변경인지 구분했는가?

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Sqrt Decomposition, Union-Find, Segment Tree, Binary Search
- 함께 보면 좋은 레슨: Versioned Data Structures, Fenwick Tree, Segment Tree, Link-Cut Tree
- 다음에 볼 레슨: Dynamic MST, Euler Tour Tree, Retroactive/Kinetic Structures

## 1. 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 정적 배열의 구간 질의를 많이 처리한다 | [Offline Queries](pages/offline-queries.md), [Offline Range Query Techniques](pages/offline-range-query-techniques.md) |
| add/remove로 현재 구간 상태를 유지할 수 있다 | [Offline Range Query Techniques](pages/offline-range-query-techniques.md) |
| 답 후보가 단조이고 여러 질의를 동시에 이분 탐색할 수 있다 | [Offline Queries](pages/offline-queries.md) |
| update가 어떤 시간 구간 동안만 활성이다 | [Rollback Techniques](pages/rollback-techniques.md), [Dynamic Connectivity](pages/dynamic-connectivity.md) |
| 간선 추가/삭제 뒤 연결성을 묻는다 | [Dynamic Connectivity](pages/dynamic-connectivity.md) |
| 과거 operation 삽입/삭제를 offline으로 정리할 수 있다 | [Retroactive Data Structures](pages/retroactive-data-structures.md) |
| rollback, persistence, retroactivity가 헷갈린다 | [Time-Axis Model Map](pages/time-axis-model-map.md) |

## 2. 시간축 문제를 읽는 순서

| 질문 | 맞으면 | 아니면 |
| --- | --- | --- |
| 모든 질의를 미리 읽을 수 있는가? | offline 재정렬 후보 | online 자료구조 필요 |
| query 순서를 바꿔도 되는가? | Mo, offline sorting, PBS | 시간축 segment tree 검토 |
| update가 활성 구간으로 표현되는가? | rollback + segment tree over time | persistence나 online 구조 검토 |
| leaf에서 현재 상태만으로 답하는가? | rollback DFS가 잘 맞음 | 더 강한 상태 요약 필요 |
| 과거 version id를 직접 질의하는가? | persistence 쪽으로 이동 | rollback이나 retroactivity 검토 |

같은 "과거"라는 단어가 나와도 구현은 크게 달라집니다. 과거 version을 읽는 문제는 persistent structure가 맞고, DFS 중 잠시 적용했다가 되돌리는 문제는 rollback이 맞습니다. 과거 operation 자체를 끼워 넣거나 삭제하면 retroactive 모델입니다.

## 3. 공개 상태

이 허브의 하위 페이지들은 대부분 구현 골격과 판단 기준을 제공하지만, 아직 실제 `/practice/...` 링크가 충분하지 않습니다. 따라서 허브는 `overview`로 공개하고, 하위 페이지의 TODO 문제는 [Practice Set](pages/practice-set.md)에 모아 추적합니다.
