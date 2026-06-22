# Knuth Optimization

Knuth Optimization은 interval DP에서 최적 분할점의 범위가 좁아지는 성질을 이용해 `O(N^3)` DP를 `O(N^2)`로 줄이는 기법입니다. 파일 합치기, optimal binary search tree처럼 구간을 둘로 나누는 DP에서 자주 등장합니다.

이 레슨은 divide-and-conquer DP optimization과 구분되는 interval DP 최적화를 정리합니다.

1. `dp[l][r] = min_k(dp[l][k] + dp[k+1][r] + cost(l, r))` 형태를 찾는다.
2. 최적 분할점 `opt[l][r]`의 monotone 범위를 확인한다.
3. `k` 후보를 `opt[l][r-1]..opt[l+1][r]`로 줄인다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 구간 DP, prefix sum, Proof와 Invariant
- 함께 보면 좋은 레슨: 동적 계획법, Divide and Conquer DP Optimization
- 다음에 볼 레슨: quadrangle inequality, Monge array, optimal BST

## 1. 문제 신호

Knuth Optimization은 interval DP에서 나옵니다.

| 문제 표현 | DP 관점 |
| --- | --- |
| 인접한 구간들을 반복해서 합친다 | `dp[l][r]` |
| 구간을 어느 위치에서 나눌지 고른다 | split point `k` |
| 구간 전체 비용이 추가된다 | `cost(l, r)` |
| 단순 구현이 `O(N^3)`이다 | `N^2` states * `N` candidates |

layer DP는 divide-and-conquer DP optimization 쪽이고, interval `[l, r]`을 나누는 구조는 Knuth 쪽을 먼저 봅니다.

## 2. 전이 형태

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

## 3. 기본 구현

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

## 4. 적용 조건

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

## 5. Divide-and-Conquer DP와 차이

| 기법 | DP 형태 | 후보 범위 |
| --- | --- | --- |
| Knuth Optimization | `dp[l][r]` interval | `opt[l][r-1]..opt[l+1][r]` |
| Divide-and-Conquer DP | `dp[layer][i]` | 재귀 구간의 `optLeft..optRight` |
| Convex Hull Trick | `m_j*x_i+b_j` | 직선 query |

형태가 비슷해 보여도 적용 조건이 다릅니다. interval DP라는 이유만으로 divide-and-conquer DP를 쓰거나, layer DP라는 이유로 Knuth를 쓰면 안 됩니다.

## 6. Tie-breaking

같은 값이 여러 split에서 나올 수 있습니다. 이때 opt monotonicity를 안정적으로 유지하려면 tie-breaking을 일관되게 해야 합니다.

```text
candidate < best 일 때만 갱신: 가장 작은 split 유지
candidate <= best 일 때 갱신: 가장 큰 split 유지
```

둘 중 하나로 고정하고, 단조성 증명 또는 구현 관례와 맞춥니다. 보통 가장 작은 split을 유지하는 방식이 무난합니다.

## 7. 시간 복잡도

| 구현 | 시간 | 메모리 |
| --- | ---: | ---: |
| 단순 interval DP | `O(N^3)` | `O(N^2)` |
| Knuth Optimization | `O(N^2)` | `O(N^2)` |
| cost prefix sum | `O(1)` per query | `O(N)` |

`N`이 수천이면 `O(N^2)`도 메모리와 시간이 부담될 수 있습니다. `dp`와 `opt`가 각각 `N^2`이므로 메모리 제한을 먼저 계산해야 합니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 적용 조건 없이 Knuth 사용 | 숨은 케이스 오답 | opt 단조성 증명 확인 |
| `end`를 `right - 1`로 제한하지 않음 | 빈 오른쪽 구간 접근 | split 범위는 `l..r-1` |
| base opt 초기화 누락 | 길이 2부터 범위 오류 | `opt[i][i] = i` |
| cost가 split에 의존 | 전이 형태 불일치 | `cost(l,r)`만 추가되는지 확인 |
| tie-breaking 불일치 | opt 범위 흔들림 | `<` 또는 `<=` 고정 |
| prefix sum off-by-one | 비용 오답 | `prefix[r+1]-prefix[l]` |

## 9. 문제를 볼 때 체크할 조건

1. DP가 구간 `[l, r]` 형태인가?
2. 구간을 split `k`로 나누는 전이인가?
3. 추가 비용이 `cost(l, r)`로 split과 독립인가?
4. opt 범위 단조성이 증명되거나 알려진 구조인가?
5. cost를 `O(1)`에 계산할 수 있는가?
6. `O(N^2)` 메모리를 감당할 수 있는가?

Knuth Optimization은 interval DP의 대표적인 고급 최적화입니다. 조건이 맞으면 성능이 크게 좋아지지만, 조건 확인 없이 적용하면 가장 위험한 종류의 최적화이기도 합니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 파일 합치기 `/practice/...` 문제 필요 | interval DP와 prefix sum cost | file merging |
| 표준 | TODO: Knuth 최적화 DP `/practice/...` 문제 필요 | opt 범위 축소 구현 | Knuth optimization |
| 응용 | TODO: optimal BST `/practice/...` 문제 필요 | 구간 확률 비용과 opt 단조성 | optimal BST |
| 함정 | TODO: Knuth 조건이 없는 interval DP `/practice/...` 문제 필요 | 적용 가능성 판정 | quadrangle inequality |
