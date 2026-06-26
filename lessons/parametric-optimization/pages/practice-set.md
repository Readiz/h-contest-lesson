# Parametric Optimization Practice Set

이 페이지는 Parametric Optimization 계열을 하나의 학습 단위로 연습하기 위한 문제 목록입니다. 아직 적절한 h-contest 문제가 없는 칸은 임의 ID를 넣지 않고 `TODO`로 둡니다.

## 로컬 완결형 연습

### 최대 평균 부분 배열

길이 `L` 이상인 연속 부분 배열의 평균 최댓값을 구합니다.

```text
입력
n L
a1 a2 ... an

제한
1 <= L <= n <= 200000
-10000 <= ai <= 10000

출력
최대 평균을 절대/상대 오차 1e-6 이하로 출력
```

풀이 신호는 `average >= x`를 `sum(ai - x) >= 0`인 길이 `L` 이상 구간 존재 여부로 바꾸는 것입니다. [Fractional Objectives](fractional-objectives.md)의 prefix minimum 판정을 그대로 끝까지 구현할 수 있어야 합니다.

### 정확히 K개 Segment 고르기

배열을 몇 개의 segment로 나누어 segment 비용 합을 최소화하되, 정확히 `K`개 segment를 골라야 합니다. `K` 차원을 직접 넣으면 너무 크다고 가정합니다.

```text
입력
n K
segment cost oracle

목표
고정 penalty에서 count를 함께 반환하는 DP를 만들고,
lambda 탐색 후 원래 비용을 복원합니다.
```

이 연습은 실제 문제마다 cost oracle이 다르므로, 먼저 작은 `O(n^2)` oracle로 count와 tie-break를 검증한 뒤 최적화 기법을 붙이는 순서가 안전합니다.

## h-contest 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: maximum average `/practice/...` 문제 필요 | `value - x * weight` 판정 구현 | binary search |
| 표준 | TODO: exact K DP `/practice/...` 문제 필요 | penalty와 count tie-break | Alien trick |
| 응용 | TODO: fractional graph path `/practice/...` 문제 필요 | 비율 목적식과 shortest path 결합 | transformed weight |
| 함정 | TODO: breakpoint counterexample `/practice/...` 문제 필요 | 동점 처리와 답 복원 검증 | breakpoint |
