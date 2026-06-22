# Weighted Matching

Weighted Matching은 matching의 크기뿐 아니라 선택한 간선의 가중치 합을 최적화하는 문제입니다. 이분 그래프에서는 Hungarian algorithm이나 Min-Cost Flow로 접근할 수 있지만, 일반 그래프에서는 weighted blossom이 필요합니다.

이 레슨은 General Matching 이후에 보는 "matching에 가중치가 붙을 때 무엇이 달라지는가"를 정리합니다.

이 레슨은 weighted blossom을 직접 구현하는 레슨이 아닙니다. 문제를 보고 bitmask DP, Hungarian, Min-Cost Flow, weighted blossom 중 무엇을 골라야 하는지 판단하는 선택 가이드에 가깝습니다. 일반 그래프 weighted blossom은 구현량과 디버깅 비용이 크므로, 대회에서는 검증된 라이브러리 영역으로 보는 편이 안전합니다.

1. cardinality matching과 weight matching을 구분한다.
2. 이분 그래프 weighted matching은 dual slack 관점으로 이해한다.
3. 일반 그래프 weighted matching은 blossom 수축에 dual variable이 추가된다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 이분 matching, General Matching, Min-Cost Flow
- 함께 보면 좋은 레슨: Matching과 Cover Duality, General Matching, Min-Cost Flow
- 다음에 볼 레슨: weighted blossom, assignment problem, matroid intersection

## 1. 문제 신호

| 문제 표현 | 접근 |
| --- | --- |
| 최대 가중치 matching | weighted matching |
| 이분 그래프 assignment | Hungarian 또는 Min-Cost Flow |
| 일반 무향 그래프 weighted matching | weighted blossom |
| 정점 수가 작다 | bitmask DP 가능 |
| perfect matching 요구 | 모든 정점 matching 여부 확인 |

가중치가 있어도 그래프가 이분이면 일반 weighted blossom을 꺼낼 필요가 없습니다. 모델이 이분인지 먼저 확인합니다.

## 2. Cardinality와 Weight의 차이

Maximum cardinality matching은 간선 개수를 최대화합니다. Maximum weight matching은 간선 수보다 weight 합을 우선합니다.

```text
cardinality: maximize number of selected edges
weighted:    maximize sum of selected edge weights
```

문제에 따라 "가중치 합 최대, 그중 간선 수 최대" 같은 tie-break가 있을 수 있습니다. 목적식 우선순위를 먼저 고정해야 합니다.

## 3. Small-N Bitmask DP

정점 수가 작다면 일반 그래프 weighted perfect matching을 bitmask DP로 풀 수 있습니다. 아래 코드는 모든 정점을 짝지어야 하는 maximum weight perfect matching입니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

long long maxWeightPerfectMatchingSmall(const vector<vector<long long>>& weight) {
    int n = (int)weight.size();
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
            int nextMask = mask | (1 << first) | (1 << j);
            dp[nextMask] = max(dp[nextMask], dp[mask] + weight[first][j]);
        }
    }

    return dp[totalMask - 1];
}
```

이 방식은 `O(2^N * N^2)`라서 `N`이 20대만 되어도 부담됩니다. 하지만 weighted blossom이 과한 small constraint 문제에서는 매우 실용적입니다.

## 4. 이분 Weighted Matching

이분 그래프라면 assignment problem으로 볼 수 있습니다.

| 방법 | 특징 |
| --- | --- |
| Hungarian | dense complete bipartite assignment에 강함 |
| Min-Cost Flow | capacity, forbidden edge, unmatched 허용 같은 변형에 유연 |
| DP/bitmask | 한쪽 크기가 작을 때 간단 |

Hungarian은 potential 또는 dual variable을 관리하며 reduced cost가 0인 tight edge를 늘려 갑니다. Min-Cost Flow는 같은 문제를 shortest augmenting path로 표현합니다.

## 5. 일반 그래프 Weighted Blossom 개요

일반 그래프 weighted matching은 cardinality blossom에 가중치 dual 조건이 추가됩니다.

```text
edge slack = dual[u] + dual[v] + blossomDuals - weight[u][v]
```

slack이 0인 tight edge만 alternating forest 확장에 사용하고, 더 이상 확장할 수 없으면 dual variable을 조정해 새로운 tight edge를 만듭니다. odd cycle blossom을 수축하는 흐름은 유지되지만, 각 blossom의 dual 값과 slack 갱신이 추가되어 구현 난도가 크게 올라갑니다.

### 왜 일반 그래프가 이분 그래프보다 어려운가

이분 matching에서는 alternating path가 layer를 왼쪽, 오른쪽으로 번갈아 움직입니다. 홀수 cycle이 없으므로 BFS/DFS layer 구조가 깨지지 않습니다.

일반 그래프에는 삼각형이나 오각형 같은 홀수 cycle이 있습니다.

```text
0 -- 1
 \  /
  2
```

삼각형에서 cardinality matching은 간선 하나만 고르면 끝이라 쉬워 보이지만, 더 큰 그래프에서는 홀수 cycle 안의 어떤 정점을 밖으로 노출해야 augmenting path가 이어지는지 추적해야 합니다. Cardinality blossom은 이 odd cycle을 하나의 super node처럼 수축해서 "cycle 내부 선택은 나중에 복원"합니다.

Weighted blossom은 여기에 weight까지 붙습니다. 단순히 cycle을 수축하는 것만으로는 부족하고, 어떤 edge가 현재 dual 기준으로 tight한지, blossom 내부 dual 값이 slack 계산에 어떻게 들어가는지 계속 유지해야 합니다.

예를 들어 오각형 cycle 바깥에서 들어오는 간선이 여러 개 있으면 cardinality 관점에서는 "어느 한 정점이 노출된다" 정도면 충분하지만, weighted 관점에서는 그 노출 선택이 내부 matching weight와 외부 edge weight를 동시에 바꿉니다. 그래서 slack과 dual 조정이 핵심이 됩니다.

이 레슨에서는 이 복잡한 구현을 전개하지 않습니다. 대신 아래 판단을 먼저 합니다.

| 그래프/제약 | 먼저 볼 선택지 |
| --- | --- |
| 이분 그래프 assignment | Hungarian |
| 이분 그래프에 capacity/forbidden edge/penalty | Min-Cost Flow |
| 일반 그래프이지만 `N <= 24` 정도 | bitmask DP |
| 일반 그래프이고 큰 weighted matching | 검증된 weighted blossom |

## 6. 목적식 모델링

| 요구 | 모델링 |
| --- | --- |
| 최대 weight matching | 그대로 maximum weight |
| 최소 cost matching | weight를 `-cost`로 변환하거나 min-cost 알고리즘 사용 |
| perfect matching | unmatched 금지 |
| maximum cardinality 후 maximum weight | 큰 상수 `B`로 `B + weight`를 간선 가중치에 추가 |
| unmatched 허용 penalty | dummy vertex 또는 penalty edge |

큰 상수 trick을 쓸 때는 overflow와 weight 범위를 반드시 확인합니다.

## 7. 음수 가중치

음수 가중치가 있으면 "선택하지 않는 것"이 더 나을 수 있습니다. perfect matching이면 어쩔 수 없이 선택해야 하지만, 일반 matching이면 빈 matching도 후보입니다.

| 조건 | 처리 |
| --- | --- |
| perfect matching | 음수도 선택 가능 |
| cardinality 제한 없음 | 음수 간선은 보통 선택하지 않음 |
| 정확히 K개 선택 | count 제한과 weight 최적화를 함께 처리 |

문제에서 반드시 몇 개를 선택해야 하는지 확인합니다.

## 8. 시간 복잡도

| 알고리즘 | 대상 | 시간 |
| --- | --- | ---: |
| bitmask DP | small general graph perfect matching | `O(2^N N^2)` |
| Hungarian | bipartite assignment | `O(N^3)` |
| Min-Cost Flow | sparse/constraint bipartite | flow량에 의존 |
| weighted blossom | general graph | polynomial 구현이 알려져 있지만 직접 구현 비권장 |

일반 weighted blossom은 검증된 라이브러리를 쓰는 편이 안전합니다. 이분 그래프라면 weighted blossom부터 생각하지 말고 Hungarian이나 Min-Cost Flow로 모델을 낮추는 것이 좋습니다. 직접 구현해야 한다면 cardinality blossom을 완전히 이해한 뒤 dual/slack을 추가합니다.

## 9. 자주 하는 실수

1. 이분 그래프인지 확인하지 않고 weighted blossom을 고민한다.
2. maximum cardinality와 maximum weight의 우선순위를 섞는다.
3. perfect matching 요구에서 홀수 정점 수를 처리하지 않는다.
4. 음수 가중치가 있는데 빈 matching 허용 여부를 확인하지 않는다.
5. 큰 상수 tie-break에서 overflow를 낸다.

## 10. 문제를 볼 때 체크할 조건

- 그래프가 이분인가 일반 그래프인가?
- matching 크기와 weight 중 무엇이 우선인가?
- perfect matching이 필요한가, unmatched 정점이 허용되는가?
- 정점 수가 bitmask DP 범위인가?
- 음수 weight와 dummy edge가 필요한가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: small weighted perfect matching `/practice/...` 문제 필요 | bitmask DP로 일반 그래프 처리 | weighted matching |
| 표준 | TODO: assignment problem `/practice/...` 문제 필요 | Hungarian 또는 Min-Cost Flow 모델링 | bipartite matching |
| 응용 | TODO: maximum cardinality 후 weight `/practice/...` 문제 필요 | 큰 상수 tie-break | lexicographic objective |
| 함정 | TODO: 음수 weight matching `/practice/...` 문제 필요 | unmatched 허용 여부 확인 | negative weight |
