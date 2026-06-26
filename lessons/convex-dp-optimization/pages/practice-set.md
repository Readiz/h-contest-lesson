# Practice Set

Convex DP Optimization 계열은 "이 기법을 쓸 수 있는 식인가"를 먼저 연습해야 합니다. 적절한 h-contest 문제가 없는 항목은 임의 ID를 만들지 않고 `TODO`로 둡니다.

## 1. 권장 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: line query DP `/practice/...` 문제 필요 | 전이를 직선과 x query로 분리 | CHT |
| 표준 | TODO: arbitrary x Li Chao `/practice/...` 문제 필요 | 일반 삽입/질의 구현 | Li Chao Tree |
| 표준 | TODO: monotone opt DP `/practice/...` 문제 필요 | argmin 단조성 확인 | D&C DP |
| 응용 | TODO: absolute value convex cost `/practice/...` 문제 필요 | breakpoints 관리 | Slope Trick |
| 응용 | TODO: min-plus merge `/practice/...` 문제 필요 | convolution 모델링 | convex sequence |
| 심화 | TODO: dynamic line set `/practice/...` 문제 필요 | offline deletion 또는 dynamic hull | fully dynamic CHT |

## 2. 완료 기준

- 전이식에서 후보와 query 변수를 분리합니다.
- 기법 적용 조건을 한 문장으로 씁니다.
- 작은 입력 naive DP와 비교하는 stress test를 준비합니다.
- overflow 범위와 `INF` 정책을 명시합니다.
- precision이 필요한 경우 정수 비교식으로 바꿀 수 있는지 먼저 봅니다.
