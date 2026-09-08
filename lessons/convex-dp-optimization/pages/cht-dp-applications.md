# CHT DP Applications

CHT DP Applications는 Convex Hull Trick을 실제 DP 식으로 바꾸는 과정을 다룹니다. CHT 구현을 알고 있어도, `j`가 만드는 직선과 `i`가 던지는 query를 정확히 분리하지 못하면 최적화가 아니라 다른 문제를 풀게 됩니다.


아래 함수는 [Convex Hull Trick Variants](https://h.readiz.com/learn/convex-dp-optimization/convex-hull-trick-variants)의 MonotoneMinCht 뒤에 붙입니다. prefix는 비감소하고 비어 있지 않아야 하며, 이때 slope=-2*prefix는 비증가합니다. 모든 DP/곱셈 결과가 long long 범위여야 합니다.

## 문제 신호

| DP 전이 형태 | CHT 관점 |
| --- | --- |
| `dp[i] = min_j(dp[j] + A[j] * X[i] + B[j])` | `j`가 직선, `i`가 query |
| `cost(j, i)`에 곱셈 항이 있음 | 식 전개 후 직선 분리 |
| `j < i` 조건 | add/query 순서가 온라인 |
| `A[j]`가 단조 | deque 또는 breakpoint hull 후보 |
| `X[i]`가 임의 | Li Chao 또는 binary search hull |

식이 직선과 점 질의로 분리되지 않으면 CHT를 억지로 적용하면 안 됩니다.

## 식 분리 예시

아래 전이가 있다고 합시다.

```text
dp[i] = min over j < i:
  dp[j] + (prefix[i] - prefix[j])^2 + C
```

전개하면 다음과 같습니다.

```text
dp[i] = prefix[i]^2 + C + min_j(
  dp[j] + prefix[j]^2 - 2*prefix[j]*prefix[i]
)
```

따라서 `x = prefix[i]`, `m = -2*prefix[j]`, `b = dp[j] + prefix[j]^2`인 직선 최솟값 질의가 됩니다.

## 구현 골격

아래 코드는 `x`가 증가하고 slope도 증가하는 최솟값 문제를 처리하는 monotone CHT skeleton입니다.

```cpp
#include <vector>
using namespace std;

vector<long long> optimizeQuadraticPartition(const vector<long long>& prefix, long long cost) {
    int n = (int)prefix.size() - 1;
    vector<long long> dp(n + 1, 0);
    MonotoneMinCht cht;
    cht.addLine(-2 * prefix[0], dp[0] + prefix[0] * prefix[0]);

    for (int i = 1; i <= n; ++i) {
        long long x = prefix[i];
        dp[i] = x * x + cost + cht.queryIncreasingX(x);
        cht.addLine(-2 * prefix[i], dp[i] + prefix[i] * prefix[i]);
    }
    return dp;
}
```

이 skeleton은 `prefix[i]`가 증가한다는 전제를 둡니다. 값이 감소할 수 있으면 `queryIncreasingX`가 틀립니다.

## 선택 순서 체크

CHT DP에서는 아래 순서를 먼저 표로 씁니다.

| 질문 | 답이 필요한 이유 |
| --- | --- |
| `j`는 언제 line으로 추가되는가 | `j < i` 온라인 조건 |
| slope가 정렬되어 들어오는가 | deque 가능 여부 |
| query x가 정렬되어 들어오는가 | front pop 가능 여부 |
| 같은 slope가 생기는가 | intercept tie 처리 |
| min인가 max인가 | 부호 변환 |

이 다섯 가지가 정해지면 구현 선택은 대부분 결정됩니다.

## 작은 예시

```text
prefix = 0, 2, 5
C = 3

i=1, x=2
line j=0: m=0, b=0
dp[1] = 4 + 3 + 0 = 7
add j=1: m=-4, b=11

i=2, x=5
line j=0 => 0
line j=1 => -20 + 11 = -9
dp[2] = 25 + 3 - 9 = 19
```

손으로 한두 단계 따라가면 직선의 `m`, `b`가 DP 전이와 맞는지 빠르게 확인할 수 있습니다.

## Li Chao로 가야 하는 경우

삽입 slope가 비증가하거나 query x가 비감소한다는 조건이 깨지면 Li Chao를 사용합니다. 정수 x의 범위를 알거나 query 좌표를 미리 압축해야 합니다. 일반 Li Chao와 multiset line container는 임의 삭제를 지원하지 않으므로, 삭제에는 시간 구간 분해/rollback 등 별도 설계가 필요합니다.

## D&C DP와 구분

`cost(j, i)`가 Monge이고 argmin이 단조라면 Divide and Conquer Optimization이 더 간단할 수 있습니다. CHT는 보통 곱셈 항을 직선 질의로 분리할 수 있을 때 유리합니다.

| 구조 | 우선 후보 |
| --- | --- |
| `A[j] * X[i] + B[j]` | CHT/Li Chao |
| `cost(j, i)`가 Monge | D&C DP |
| convex function에 point update | Slope Trick |
| 선택 개수 penalty | Parametric DP |
