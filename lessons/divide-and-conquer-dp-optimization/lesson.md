# Divide and Conquer DP Optimization

Divide and Conquer DP Optimization은 `dp[layer][mid]`의 최적 선택 위치가 오른쪽으로 갈수록 뒤로만 움직이는 단조성을 이용해, 한 층의 DP 계산을 `O(N^2)`에서 `O(N log N)` 또는 `O(KN log N)` 수준으로 줄이는 기법입니다.

이 레슨은 DP 전이의 argmin 단조성을 어떻게 쓰는지에 집중합니다.

1. 전이식을 `dp_cur[i] = min_j(dp_prev[j] + cost(j, i))` 꼴로 정리한다.
2. 최적 `j`가 단조인지 확인한다.
3. 구간의 가운데 값을 먼저 계산하고, 왼쪽/오른쪽의 후보 범위를 줄인다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 동적 계획법, 재귀 분할, prefix sum
- 함께 보면 좋은 레슨: 동적 계획법, Proof와 Invariant, Convex Hull Trick과 Li Chao Tree
- 다음에 볼 레슨: Knuth optimization, SMAWK, quadrangle inequality

## 1. 문제 신호

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

## 2. 단조성 조건

`opt[i]`를 `dp_cur[i]`를 최소로 만드는 가장 작은 `j`라고 합시다. Divide and Conquer DP Optimization은 아래가 성립할 때 씁니다.

```text
i1 < i2 이면 opt[i1] <= opt[i2]
```

이 조건이 있으면 가운데 `mid`의 최적 후보를 찾은 뒤, 왼쪽 구간은 `optLeft..best`, 오른쪽 구간은 `best..optRight`만 보면 됩니다.

## 3. 기본 구현

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

## 4. 한 층 전체 계산 흐름

`K`개 그룹으로 나누는 DP라면 아래 흐름이 됩니다.

```text
previous = dp[g - 1]
current[i] = INF
computeLayer(1, N, 0, N - 1, previous, current, cost)
```

`j < i` 조건이 있으면 후보 상한을 `mid - 1`로 제한해야 합니다. 빈 구간을 허용하는 문제라면 `j <= mid`가 될 수도 있습니다. 이 경계는 문제마다 다릅니다.

## 5. Cost 계산

최적화를 적용해도 `cost(l, r)`이 느리면 전체가 빨라지지 않습니다.

| 비용 형태 | 전처리 |
| --- | --- |
| 구간 합 | prefix sum |
| 구간 제곱합 | prefix sum 여러 개 |
| 같은 값 쌍 개수 | 투 포인터/Mo 비슷한 이동 |
| 중앙값 기준 거리 | 정렬 + prefix sum |

Divide-and-conquer로 후보 수를 줄이는 것과 cost를 빠르게 계산하는 것은 별개의 문제입니다.

## 6. Knuth Optimization과 차이

Knuth Optimization도 최적 분할점 단조성을 쓰지만 조건과 계산 순서가 다릅니다.

| 기법 | 대표 형태 | 시간 |
| --- | --- | ---: |
| Divide and Conquer DP | layer별 `dp[g][i]` | `O(KN log N)` 또는 `O(KN)` 후보 구조 |
| Knuth Optimization | interval DP `dp[l][r]` | `O(N^2)` |
| Convex Hull Trick | 직선 query DP | `O(N log X)` |

문제의 DP가 "구간을 몇 개로 나눌지" layer를 갖고 있다면 divide-and-conquer DP를 먼저 의심합니다. `dp[l][r]` 형태의 interval DP라면 Knuth 쪽을 봅니다.

## 7. 단조성 검증 습관

작은 입력에서 brute force로 `opt[i]` 배열을 출력해 보는 습관이 도움이 됩니다.

```text
layer 2 opt: 0 1 1 2 3 3 5 ...
```

계속 감소하지 않는다면 최적화 후보가 될 수 있습니다. 하지만 테스트에서 단조로 보인다고 증명이 된 것은 아닙니다. editorial에서 quadrangle inequality, Monge array, convex cost 같은 조건을 확인해야 합니다.

## 8. 시간 복잡도

한 layer에서 각 `mid`마다 후보 범위를 모두 보는 것처럼 보이지만, 재귀 깊이가 `O(log N)`이고 각 깊이에서 전체 후보 스캔이 제한되어 보통 `O(N log N)`으로 설명합니다. 문제 구조에 따라 더 조밀한 분석이 필요할 수 있습니다.

| 작업 | 시간 |
| --- | ---: |
| 단순 layer 계산 | `O(N^2)` |
| D&C 최적화 layer 계산 | 보통 `O(N log N)` |
| K layer 전체 | 보통 `O(KN log N)` |
| cost가 `O(C)`이면 | 위 시간에 `C` 곱 |

일부 표준 문제는 후보 범위 합 분석으로 `O(KN log N)`이 충분하고, 더 최적화된 구현은 `O(KN)`에 가까운 형태가 되기도 합니다.

## 9. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| opt 단조성 없이 적용 | 특정 케이스 오답 | 증명 또는 editorial 조건 확인 |
| 후보 범위에 `mid` 포함 여부 오류 | 빈 구간/자기 전이 오답 | `j < i` 조건 재확인 |
| tie-breaking이 불안정 | 단조성 깨짐 | 가장 작은 opt 또는 큰 opt로 일관 |
| current 초기화 누락 | 이전 layer 값 섞임 | layer마다 INF 초기화 |
| cost 계산이 느림 | 시간 초과 | prefix sum 등으로 `O(1)`화 |
| 재귀 범위 인자 반대로 전달 | 후보 누락 | 왼쪽 `optLeft..opt`, 오른쪽 `opt..optRight` |

## 10. 문제를 볼 때 체크할 조건

1. DP가 layer와 prefix 끝점 형태인가?
2. 전이가 이전 layer의 후보 `j` 전체를 훑는가?
3. `cost(j, i)`를 빠르게 계산할 수 있는가?
4. 최적 후보 `opt[i]`가 단조임을 보일 수 있는가?
5. 후보 경계가 `j < i`인지 `j <= i`인지 명확한가?
6. tie-breaking을 단조성에 맞게 고정했는가?

Divide and Conquer DP Optimization은 구현보다 적용 조건이 더 중요합니다. 단조성이 확인되면 재귀 구현은 짧지만, 조건이 틀리면 빠르게 틀린 답을 내는 기법입니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 구간 분할 DP `/practice/...` 문제 필요 | layer DP와 `cost(l, r)` 계산 | partition DP |
| 표준 | TODO: opt 단조성 있는 DP `/practice/...` 문제 필요 | `computeLayer` 재귀 구현 | monotone opt |
| 응용 | TODO: cost 이동이 필요한 DP `/practice/...` 문제 필요 | cost 계산과 D&C 결합 | moving cost |
| 함정 | TODO: 단조성이 깨지는 반례 `/practice/...` 문제 필요 | 최적화 적용 조건 판정 | quadrangle inequality |
