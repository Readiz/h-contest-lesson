# Weighted Matching

Weighted Matching은 matching의 크기뿐 아니라 선택한 간선의 가중치 합을 최적화하는 문제입니다. 이분 그래프에서는 Hungarian algorithm이나 Min-Cost Flow로 접근할 수 있지만, 일반 그래프에서는 weighted blossom이 필요합니다.

이 레슨은 General Matching 이후에 보는 "matching에 가중치가 붙을 때 무엇이 달라지는가"를 정리합니다.

## 문제 신호

| 문제 표현 | 접근 |
| --- | --- |
| 최대 가중치 matching | weighted matching |
| 이분 그래프 assignment | Hungarian 또는 Min-Cost Flow |
| 일반 무향 그래프 weighted matching | weighted blossom |
| 정점 수가 작다 | bitmask DP 가능 |
| perfect matching 요구 | 모든 정점 matching 여부 확인 |

가중치가 있어도 그래프가 이분이면 일반 weighted blossom을 꺼낼 필요가 없습니다. 모델이 이분인지 먼저 확인합니다.

## Cardinality와 Weight의 차이

Maximum cardinality matching은 간선 개수를 최대화합니다. Maximum weight matching은 간선 수보다 weight 합을 우선합니다.

```text
cardinality: maximize number of selected edges
weighted:    maximize sum of selected edge weights
```

문제에 따라 "가중치 합 최대, 그중 간선 수 최대" 같은 tie-break가 있을 수 있습니다. 목적식 우선순위를 먼저 고정해야 합니다.

## Small-N Bitmask DP

정점 수가 작다면 일반 그래프 weighted perfect matching을 bitmask DP로 풀 수 있습니다. 아래 코드는 모든 정점을 짝지어야 하는 maximum weight perfect matching입니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

long long maxWeightPerfectMatchingSmall(const vector<vector<long long>>& weight) {
    int n = (int)weight.size(); // n <= 22, 정사각 대칭 행렬
    int totalMask = 1 << n;
    const long long NEG = -(1LL << 60);
    vector<long long> dp(totalMask, NEG);
    dp[0] = 0;

    for (int mask = 0; mask < totalMask; ++mask) {
        if (dp[mask] == NEG) {
            continue;
        }

        int first = -1;
        for (int i = 0; i < n; ++i) {
            if (((mask >> i) & 1) == 0) {
                first = i;
                break;
            }
        }
        if (first == -1) {
            continue;
        }

        for (int j = first + 1; j < n; ++j) {
            if ((mask >> j) & 1) {
                continue;
            }
            if (weight[first][j] == NEG) continue; // 없는 간선
            int nextMask = mask | (1 << first) | (1 << j);
            dp[nextMask] = max(dp[nextMask], dp[mask] + weight[first][j]);
        }
    }

    return dp[totalMask - 1];
}
```

`NEG`는 없는 간선과 불가능한 결과를 나타냅니다. 유효한 비용 합은 `NEG`보다 크고 `long long` 범위 안이어야 합니다. 홀수 정점 수는 perfect matching이 불가능하여 `NEG`를 반환합니다.

이 방식은 `O(2^N * N)`라서 `N`이 20대만 되어도 부담됩니다. 하지만 weighted blossom이 과한 small constraint 문제에서는 매우 실용적입니다.

## 이분 Weighted Matching

이분 그래프라면 assignment problem으로 볼 수 있습니다.

| 방법 | 특징 |
| --- | --- |
| Hungarian | dense complete bipartite assignment에 강함 |
| Min-Cost Flow | capacity, forbidden edge, unmatched 허용 같은 변형에 유연 |
| DP/bitmask | 한쪽 크기가 작을 때 간단 |

Hungarian은 potential 또는 dual variable을 관리하며 reduced cost가 0인 tight edge를 늘려 갑니다. Min-Cost Flow는 같은 문제를 shortest augmenting path로 표현합니다. Hungarian의 potential/tight edge 구현은 별도 Hungarian Algorithm 레슨에서 따로 다룹니다.

## 일반 그래프 Weighted Blossom 개요

일반 그래프 weighted matching은 cardinality blossom에 가중치 dual 조건이 추가됩니다.

Weighted blossom은 홀수 사이클의 수축과 dual/slack 조건을 함께 관리합니다. 이 문서의 코드는 작은 그래프용 DP이며 weighted blossom 구현을 대신하지 않습니다. 큰 일반 그래프는 가중 매칭 전용 구현이 필요합니다.

## 목적식 모델링

| 요구 | 모델링 |
| --- | --- |
| 최대 weight matching | 그대로 maximum weight |
| 최소 cost matching | weight를 `-cost`로 변환하거나 min-cost 알고리즘 사용 |
| perfect matching | unmatched 금지 |
| maximum cardinality 후 maximum weight | 큰 상수 `B`로 `B + weight`를 간선 가중치에 추가 |
| unmatched 허용 penalty | dummy vertex 또는 penalty edge |

큰 상수 trick을 쓸 때는 overflow와 weight 범위를 반드시 확인합니다.

## 음수 가중치

음수 가중치가 있으면 "선택하지 않는 것"이 더 나을 수 있습니다. perfect matching이면 어쩔 수 없이 선택해야 하지만, 일반 matching이면 빈 matching도 후보입니다.

| 조건 | 처리 |
| --- | --- |
| perfect matching | 음수도 선택 가능 |
| cardinality 제한 없음 | 음수 간선은 보통 선택하지 않음 |
| 정확히 K개 선택 | count 제한과 weight 최적화를 함께 처리 |

문제에서 반드시 몇 개를 선택해야 하는지 확인합니다.

## 시간 복잡도

| 알고리즘 | 대상 | 시간 |
| --- | --- | ---: |
| bitmask DP | small general graph perfect matching | `O(2^N N)` |
| Hungarian | bipartite assignment | `O(N^3)` |
| Min-Cost Flow | sparse/constraint bipartite | flow량에 의존 |
| weighted blossom | general graph | polynomial 구현이 알려져 있지만 직접 구현 비권장 |

일반 weighted blossom은 검증된 라이브러리를 쓰는 편이 안전합니다. 이분 그래프라면 weighted blossom부터 생각하지 말고 Hungarian이나 Min-Cost Flow로 모델을 낮추는 것이 좋습니다. 직접 구현해야 한다면 cardinality blossom을 완전히 이해한 뒤 dual/slack을 추가합니다.
