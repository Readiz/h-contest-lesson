# Offline and Time-Axis Techniques

Offline and Time-Axis Techniques는 질의를 입력 순서 그대로 처리하지 않고, 전체 query set을 본 뒤 더 쉬운 순서나 시간 구간 구조로 바꾸는 기법을 묶는 허브입니다. Mo's Algorithm, Parallel Binary Search, Rollback DSU, 시간축 Segment Tree, Offline Dynamic Connectivity, 제한된 Retroactive 구조는 모두 "시간을 다시 배치한다"는 같은 판단에서 출발합니다.

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 정적 배열의 구간 질의를 많이 처리한다 | [Offline Range Query Techniques](pages/offline-range-query-techniques.md) |
| add/remove로 현재 구간 상태를 유지할 수 있다 | [Offline Range Query Techniques](pages/offline-range-query-techniques.md) |
| 답 후보가 단조이고 여러 질의를 동시에 이분 탐색할 수 있다 | [Parallel Binary Search](pages/offline-queries.md) |
| update가 어떤 시간 구간 동안만 활성이다 | [Rollback Techniques](pages/rollback-techniques.md), [Dynamic Connectivity](pages/dynamic-connectivity.md) |
| 간선 추가/삭제 뒤 연결성을 묻는다 | [Dynamic Connectivity](pages/dynamic-connectivity.md) |
| 과거 operation 삽입/삭제를 offline으로 정리할 수 있다 | [Retroactive Data Structures](pages/retroactive-data-structures.md) |

## 시간 인덱스

질의를 재정렬하면 답은 원래 query index로 돌려놓습니다. 간선 생존 구간은 `[l, r)`로 두어 삭제 시점을 제외하고, 시간축 DFS에 들어가기 전 snapshot을 저장합니다. 입력 명령 순서와 과거 operation의 논리 시간은 서로 다를 수 있습니다.

## 연습

[로컬 연습](pages/dynamic-connectivity.md)에서 입력과 검증 기준을 확인합니다.
