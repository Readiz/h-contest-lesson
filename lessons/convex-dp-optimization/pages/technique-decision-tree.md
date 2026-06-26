# Technique Decision Tree

Convex DP 계열은 전이식의 외형이 비슷해도 필요한 기법이 달라집니다. 아래 순서로 식을 좁히면 잘못된 최적화를 줄일 수 있습니다.

## 1. 전이식 분해

먼저 DP를 아래 꼴로 써 봅니다.

```text
dp[i] = min over j < i:
  previous[j] + cost(j, i)
```

그다음 `j`에만 의존하는 값, `i`에만 의존하는 값, 둘이 곱으로 섞이는 값을 분리합니다.

| 식 모양 | 후보 |
| --- | --- |
| `m[j] * x[i] + b[j]` | CHT / Li Chao |
| `cost(j, i)`의 argmin이 단조 | D&C DP / Knuth / SMAWK |
| `abs(x-a)` 같은 convex piecewise-linear 항 누적 | Slope Trick |
| `min_t A[t] + B[k-t]` | Min-Plus Convolution |
| constraint count가 penalty에 대해 단조 | Parametric / Alien Optimization |

## 2. CHT로 가기 전 확인

CHT는 "직선 여러 개 중 x에서 최솟값" 문제입니다. 아래 둘 중 하나라도 안 되면 CHT가 아닐 수 있습니다.

1. 후보 `j`마다 slope와 intercept를 만들 수 있다.
2. 현재 상태 `i`는 query x 하나로 표현된다.

`j`와 `i`가 비선형으로 섞이면 Li Chao Tree를 가져와도 해결되지 않습니다. 먼저 식 변형이 필요합니다.

## 3. 단조 최적화로 가기 전 확인

D&C DP나 Knuth optimization은 구현보다 조건 증명이 핵심입니다.

```text
opt[i] <= opt[i + 1]
```

이 단조성이 없으면 빠른 코드가 조용히 틀립니다. 작은 입력에서 naive DP와 비교해 `opt` 이동을 찍어 보는 stress test를 먼저 만들면 좋습니다.

## 4. Slope Trick과 Min-Plus

Slope Trick은 함수 자체를 유지하는 관점입니다. query마다 직선을 넣는 CHT와 다르게, convex function의 breakpoints를 priority queue로 관리합니다.

Min-Plus Convolution은 두 비용 배열을 합치는 관점입니다. 일반 min-plus는 무겁고, convex/Monge 같은 특수 조건이 있어야 빠른 방법을 기대할 수 있습니다.

## 5. 구현 선택 요약

| 조건 | 구현 |
| --- | --- |
| slope 추가와 x query가 모두 단조 | deque CHT |
| slope만 단조 | vector hull + binary search |
| 삽입/query 순서가 일반적 | Li Chao Tree |
| x 좌표가 sparse | coordinate-compressed Li Chao |
| line 삭제가 필요 | offline divide and conquer 또는 fully dynamic CHT |
| line이 시간에 따라 움직임 | kinetic hull |
