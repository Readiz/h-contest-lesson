# Divide and Conquer DP Optimization

Divide and Conquer DP Optimization은 `dp[layer][mid]`의 최적 선택 위치가 오른쪽으로 갈수록 뒤로만 움직이는 단조성을 이용해, 한 층의 DP 계산을 `O(N^2)`에서 한 층 `O(N log N)`, K층 `O(KN log N)` 수준으로 줄이는 기법입니다.


K개 비어 있지 않은 구간 분할에서는 g층을 computeLayer(g,N,g-1,N-1,...)로 계산하고 previous[0]=0은 0층에만 둡니다. 불가능한 previous 상태는 전이에서 제외합니다. 모든 유한 비용과 합은 INF보다 작은 산술 범위여야 합니다. cost 배열의 인덱스는 cost[j+1][i]입니다.

## 문제 신호

다음 형태의 여러 layer DP에서 자주 등장합니다.

```text
dp[g][i] = min_{j < i} dp[g - 1][j] + cost(j + 1, i)
```

| 문제 표현 | DP 관점 |
| --- | --- |
| 배열을 K개 구간으로 나눈다 | layer = 구간 수 |
| 각 구간 비용을 빠르게 계산할 수 있다 | `cost(l, r)` |
| 최적 분할점이 단조로 움직인다 | divide-and-conquer optimization |
| 모든 `j`를 보면 너무 느리다 | 후보 범위 축소 |

단조성이 없으면 이 최적화는 사용할 수 없습니다. "그럴 것 같다"가 아니라 증명 또는 알려진 비용 구조가 필요합니다.

## 단조성 조건

`opt[i]`를 `dp_cur[i]`를 최소로 만드는 가장 작은 `j`라고 합시다. Divide and Conquer DP Optimization은 아래가 성립할 때 씁니다.

```text
i1 < i2 이면 opt[i1] <= opt[i2]
```

이 조건이 있으면 가운데 `mid`의 최적 후보를 찾은 뒤, 왼쪽 구간은 `optLeft..best`, 오른쪽 구간은 `best..optRight`만 보면 됩니다.

## 기본 구현

아래 함수는 한 layer를 계산합니다. `cost[j][i]`는 후보 `j`에서 끝점 `i`로 가는 비용이라고 가정합니다.

```cpp compile-check
#include <algorithm>
#include <limits>
#include <vector>
using namespace std;

const long long INF = numeric_limits<long long>::max() / 4;

void computeLayer(
    int left,
    int right,
    int optLeft,
    int optRight,
    const vector<long long>& previous,
    vector<long long>& current,
    const vector<vector<long long>>& cost
) {
    if (left > right) {
        return;
    }

    int mid = (left + right) / 2;
    pair<long long, int> best = {INF, optLeft};
    int upper = min(optRight, mid - 1);

    for (int j = optLeft; j <= upper; ++j) {
        if (previous[j] == INF) continue;
        long long candidate = previous[j] + cost[j + 1][mid];
        if (candidate < best.first) {
            best = {candidate, j};
        }
    }

    current[mid] = best.first;
    int opt = best.second;
    computeLayer(left, mid - 1, optLeft, opt, previous, current, cost);
    computeLayer(mid + 1, right, opt, optRight, previous, current, cost);
}
```

실전에서는 `cost(l, r)`을 2차원 배열로 들고 있지 않고 prefix sum으로 `O(1)`에 계산하는 경우가 많습니다. 위 코드는 최적화 구조를 보여 주기 위한 형태입니다.

## 한 층 전체 계산 흐름

`K`개 그룹으로 나누는 DP라면 아래 흐름이 됩니다.

```text
previous = dp[g - 1]
current[i] = INF
computeLayer(1, N, 0, N - 1, previous, current, cost)
```

`j < i` 조건이 있으면 후보 상한을 `mid - 1`로 제한해야 합니다. 빈 구간을 허용하는 문제라면 `j <= mid`가 될 수도 있습니다. 이 경계는 문제마다 다릅니다.

## Cost 계산

최적화를 적용해도 `cost(l, r)`이 느리면 전체가 빨라지지 않습니다.

| 비용 형태 | 전처리 |
| --- | --- |
| 구간 합 | prefix sum |
| 구간 제곱합 | prefix sum 여러 개 |
| 같은 값 쌍 개수 | 투 포인터/Mo 비슷한 이동 |
| 중앙값 기준 거리 | 정렬 + prefix sum |

Divide-and-conquer로 후보 수를 줄이는 것과 cost를 빠르게 계산하는 것은 별개의 문제입니다.

## Knuth Optimization과 차이

Knuth Optimization도 최적 분할점 단조성을 쓰지만 조건과 계산 순서가 다릅니다.

| 기법 | 대표 형태 | 시간 |
| --- | --- | ---: |
| Divide and Conquer DP | layer별 `dp[g][i]` | `O(KN log N)` |
| Knuth Optimization | interval DP `dp[l][r]` | `O(N^2)` |
| Convex Hull Trick | 직선 query DP | `O(N log X)` |

문제의 DP가 "구간을 몇 개로 나눌지" layer를 갖고 있다면 divide-and-conquer DP를 먼저 의심합니다. `dp[l][r]` 형태의 interval DP라면 Knuth 쪽을 봅니다.

## 단조성 검증 습관

작은 입력에서 brute force로 `opt[i]` 배열을 출력해 보는 습관이 도움이 됩니다.

```text
layer 2 opt: 0 1 1 2 3 3 5 ...
```

계속 감소하지 않는다면 최적화 후보가 될 수 있습니다. 하지만 테스트에서 단조로 보인다고 증명이 된 것은 아닙니다. editorial에서 quadrangle inequality, Monge array, convex cost 같은 조건을 확인해야 합니다.

## 시간 복잡도

한 layer에서 각 `mid`마다 후보 범위를 모두 보는 것처럼 보이지만, 재귀 깊이가 `O(log N)`이고 각 깊이에서 전체 후보 스캔이 제한되어 보통 `O(N log N)`으로 설명합니다. 문제 구조에 따라 더 조밀한 분석이 필요할 수 있습니다.

| 작업 | 시간 |
| --- | ---: |
| 단순 layer 계산 | `O(N^2)` |
| D&C 최적화 layer 계산 | 보통 `O(N log N)` |
| K layer 전체 | 보통 `O(KN log N)` |
| cost가 `O(C)`이면 | 위 시간에 `C` 곱 |

선형 시간의 SMAWK는 별도의 totally monotone 조건과 알고리즘이 필요합니다.
