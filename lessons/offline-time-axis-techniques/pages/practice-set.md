# Practice Set

Offline and Time-Axis Techniques 계열은 같은 입력을 여러 모델로 바꿔 보는 연습이 중요합니다. 아직 적절한 h-contest 문제 링크가 없는 항목은 임의 ID를 만들지 않고 `TODO`로 둡니다.

## 1. 권장 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: static range query `/practice/...` 문제 필요 | Mo ordering과 answer index 복구 | sqrt block, add/remove |
| 표준 | TODO: value threshold range query `/practice/...` 문제 필요 | offline sorting + Fenwick | sweep by value |
| 표준 | TODO: dynamic connectivity `/practice/...` 문제 필요 | edge active interval + rollback DSU | segment tree over time |
| 심화 | TODO: parallel binary search `/practice/...` 문제 필요 | 여러 질의의 답 후보 동시 축소 | monotone predicate |
| 심화 | TODO: retroactive operation `/practice/...` 문제 필요 | operation interval 모델링 | offline retroactivity |

## 2. 로컬 완결형 연습 아이디어

| 연습 | 제한 | 확인할 것 |
| --- | --- | --- |
| 배열 distinct query | `N,Q <= 200000` | Mo의 block size와 value compression |
| 간선 add/remove/query | `N,Q <= 200000` | remove되지 않은 간선을 `[start, Q)`로 닫기 |
| kth active update | `Q <= 200000` | PBS에서 Fenwick 초기화/복구 비용 |
| 과거 operation 삭제 | `Q <= 100000` | operation id별 active interval |

## 3. 완료 기준

- query를 원래 순서로 출력하는지 확인합니다.
- active interval을 `[l, r)`로 통일합니다.
- rollback snapshot 크기를 재귀 진입 직후에 저장합니다.
- 현재 상태만으로 leaf query를 답할 수 있는지 확인합니다.
- online 요구를 offline으로 바꿔도 되는지 문제 조건에서 확인합니다.
