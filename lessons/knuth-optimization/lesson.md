# Knuth Optimization

Knuth Optimization은 interval DP에서 최적 분할점의 범위가 좁아지는 성질을 이용해 `O(N^3)` DP를 `O(N^2)`로 줄이는 기법입니다. 파일 합치기, optimal binary search tree처럼 구간을 둘로 나누는 DP에서 자주 등장합니다.


파일 크기는 비음수여야 구간 포함 단조성이 성립합니다. 비용 합과 DP 중간값은 INF 미만이어야 합니다. 빈 배열의 합병 비용은 0입니다.

## 문제 신호

Knuth Optimization은 interval DP에서 나옵니다.

| 문제 표현 | DP 관점 |
| --- | --- |
| 인접한 구간들을 반복해서 합친다 | `dp[l][r]` |
| 구간을 어느 위치에서 나눌지 고른다 | split point `k` |
| 구간 전체 비용이 추가된다 | `cost(l, r)` |
| 단순 구현이 `O(N^3)`이다 | `N^2` states * `N` candidates |

layer DP는 divide-and-conquer DP optimization 쪽이고, interval `[l, r]`을 나누는 구조는 Knuth 쪽을 먼저 봅니다.

## 전이 형태

대표 전이는 아래입니다.

```text
dp[l][r] = min_{l <= k < r} dp[l][k] + dp[k+1][r] + cost(l, r)
```

`cost(l, r)`이 `k`와 독립이어야 합니다. `k`마다 추가 비용이 달라지는 경우에는 그대로 적용하기 어렵습니다.

Knuth 조건이 성립하면 최적 분할점은 아래 범위에 있습니다.

```text
opt[l][r - 1] <= opt[l][r] <= opt[l + 1][r]
```

그래서 모든 `k`를 보지 않고 이 좁은 범위만 탐색합니다.

## 기본 구현

아래 코드는 구간 합 비용을 갖는 파일 합치기 형태입니다.

```cpp compile-check
#include <algorithm>
#include <limits>
#include <vector>
using namespace std;

long long mergeCost(const vector<long long>& prefix, int left, int right) {
    return prefix[right + 1] - prefix[left];
}

long long knuthMergeCost(const vector<int>& values) {
    int n = (int)values.size();
    if (n == 0) return 0;
    vector<long long> prefix(n + 1, 0);
    for (int i = 0; i < n; ++i) {
        prefix[i + 1] = prefix[i] + values[i];
    }

    const long long INF = numeric_limits<long long>::max() / 4;
    vector<vector<long long>> dp(n, vector<long long>(n, 0));
    vector<vector<int>> opt(n, vector<int>(n, 0));

    for (int i = 0; i < n; ++i) {
        opt[i][i] = i;
    }

    for (int length = 2; length <= n; ++length) {
        for (int left = 0; left + length <= n; ++left) {
            int right = left + length - 1;
            dp[left][right] = INF;

            int start = opt[left][right - 1];
            int end = opt[left + 1][right];
            if (end > right - 1) {
                end = right - 1;
            }

            for (int split = start; split <= end; ++split) {
                long long candidate = dp[left][split] + dp[split + 1][right]
                    + mergeCost(prefix, left, right);
                if (candidate < dp[left][right]) {
                    dp[left][right] = candidate;
                    opt[left][right] = split;
                }
            }
        }
    }

    return dp[0][n - 1];
}
```

초기 `opt[i][i] = i`가 중요합니다. 길이 2 구간에서 후보 범위가 제대로 잡히려면 base opt가 필요합니다.

## 적용 조건

Knuth Optimization은 아무 interval DP에나 적용할 수 없습니다. 보통 아래 조건을 확인합니다.

```text
opt[l][r - 1] <= opt[l][r] <= opt[l + 1][r]
```

이 단조성이 성립하려면 cost가 quadrangle inequality와 monotonicity를 만족하는 경우가 많습니다.

```text
A[a][c] + A[b][d] <= A[a][d] + A[b][c]  (a <= b <= c <= d)
A[b][c] <= A[a][d]
```

대회에서는 editorial에서 "Knuth optimization applies"라고 주어지거나, 파일 합치기 같은 표준 구조로 확인하는 경우가 많습니다.

## Divide-and-Conquer DP와 차이

| 기법 | DP 형태 | 후보 범위 |
| --- | --- | --- |
| Knuth Optimization | `dp[l][r]` interval | `opt[l][r-1]..opt[l+1][r]` |
| Divide-and-Conquer DP | `dp[layer][i]` | 재귀 구간의 `optLeft..optRight` |
| Convex Hull Trick | `m_j*x_i+b_j` | 직선 query |

형태가 비슷해 보여도 적용 조건이 다릅니다. interval DP라는 이유만으로 divide-and-conquer DP를 쓰거나, layer DP라는 이유로 Knuth를 쓰면 안 됩니다.

## Tie-breaking

같은 값이 여러 split에서 나올 수 있습니다. 이때 opt monotonicity를 안정적으로 유지하려면 tie-breaking을 일관되게 해야 합니다.

```text
candidate < best 일 때만 갱신: 가장 작은 split 유지
candidate <= best 일 때 갱신: 가장 큰 split 유지
```

둘 중 하나로 고정하고, 단조성 증명 또는 구현 관례와 맞춥니다. 보통 가장 작은 split을 유지하는 방식이 무난합니다.

## 시간 복잡도

| 구현 | 시간 | 메모리 |
| --- | ---: | ---: |
| 단순 interval DP | `O(N^3)` | `O(N^2)` |
| Knuth Optimization | `O(N^2)` | `O(N^2)` |
| cost prefix sum | `O(1)` per query | `O(N)` |

`N`이 수천이면 `O(N^2)`도 메모리와 시간이 부담될 수 있습니다. `dp`와 `opt`가 각각 `N^2`이므로 메모리 제한을 먼저 계산해야 합니다.

## 구간 합 비용의 증명

a<=b<=c<=d에서 w(a,c)+w(b,d)=w(a,d)+w(b,c)는 각 원소의 중복 횟수가 같아 성립합니다. 파일 크기가 비음수이면 w(b,c)<=w(a,d)도 성립합니다. 두 조건을 함께 확인해야 Knuth 단조성으로 이어집니다. 음수에서는 첫 등식만 남아 충분하지 않습니다.
