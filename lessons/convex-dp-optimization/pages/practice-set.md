# Practice Set

Convex DP Optimization 계열은 "이 기법을 쓸 수 있는 식인가"를 먼저 연습해야 합니다. 적절한 h-contest 문제가 없는 항목은 임의 ID를 만들지 않고 `TODO`로 둡니다.

## 1. 로컬 완결형 연습

### Line Query DP

아래 DP를 계산합니다.

```text
dp[i] = x[i]^2 + C + min_{0 <= j < i}(dp[j] + a[j]^2 - 2*a[j]*x[i])
```

`j`별 후보를 직선 `y = m*x + b`로 보면 `m = -2*a[j]`, `b = dp[j] + a[j]^2`입니다. `x[i]`가 단조 증가하면 deque CHT를 먼저 구현하고, 단조가 깨지는 입력으로 바꿔 Li Chao Tree가 필요한 이유를 확인합니다.

검증은 `N <= 2000` naive `O(N^2)` DP와 random stress로 비교합니다. 이 연습을 통과하면 "전이를 직선과 query x로 분리한다"는 조건을 실제 코드까지 이어갈 수 있습니다.

### Slope Trick Trace

절댓값 비용 `sum |x_i - t_i|`에 이동 제약이 붙는 작은 예시를 잡고, 왼쪽 heap과 오른쪽 heap의 top이 어떻게 breakpoint를 나타내는지 손으로 추적합니다. 구현보다 먼저 함수가 convex piecewise-linear로 유지되는지 확인하는 연습입니다.

## 2. 권장 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: line query DP `/practice/...` 문제 필요 | 전이를 직선과 x query로 분리 | CHT |
| 표준 | TODO: arbitrary x Li Chao `/practice/...` 문제 필요 | 일반 삽입/질의 구현 | Li Chao Tree |
| 표준 | TODO: monotone opt DP `/practice/...` 문제 필요 | argmin 단조성 확인 | D&C DP |
| 응용 | TODO: absolute value convex cost `/practice/...` 문제 필요 | breakpoints 관리 | Slope Trick |
| 응용 | TODO: min-plus merge `/practice/...` 문제 필요 | convolution 모델링 | convex sequence |
| 심화 | TODO: dynamic line set `/practice/...` 문제 필요 | offline deletion 또는 dynamic hull | fully dynamic CHT |

## 3. 완료 기준

- 전이식에서 후보와 query 변수를 분리합니다.
- 기법 적용 조건을 한 문장으로 씁니다.
- 작은 입력 naive DP와 비교하는 stress test를 준비합니다.
- overflow 범위와 `INF` 정책을 명시합니다.
- precision이 필요한 경우 정수 비교식으로 바꿀 수 있는지 먼저 봅니다.
