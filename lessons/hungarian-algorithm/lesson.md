# Hungarian Algorithm

Hungarian Algorithm은 이분 assignment 문제를 `O(N^3)`에 푸는 표준 알고리즘입니다. `N`명의 worker와 `N`개의 job이 있고, 각 worker를 정확히 하나의 job에 배정하면서 각 job도 정확히 한 번만 쓰는 최소 비용을 찾습니다.

이 문제는 "가장 싼 간선을 하나씩 고르면 되지 않을까?"처럼 보이지만, 한 번 고른 job이 다른 worker의 유일한 좋은 선택지를 막을 수 있습니다. Hungarian은 그리디로 간선을 고르지 않고, dual potential을 조정해서 현재 비용 기준으로 공짜처럼 쓸 수 있는 `tight edge`를 만들고 그 위에서 matching을 키웁니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Matching과 Cover Duality, Weighted Matching
- 함께 보면 좋은 레슨: Min-Cost Flow, General Matching
- 다음에 볼 레슨: Matroid Algorithms, Min-Cost Flow 변형 모델링

## 1. 언제 필요한가

| 문제 신호 | Hungarian이 맞는 이유 |
| --- | --- |
| worker와 job을 1:1로 모두 매칭 | assignment problem |
| 비용 행렬이 거의 완전하다 | dense bipartite graph에 강함 |
| 한쪽 크기가 수백~수천 정도 | `O(N^3)` 구현이 실용적 |
| 제약이 "한 worker당 하나, 한 job당 하나"뿐이다 | Min-Cost Flow보다 짧고 빠름 |

직사각형 행렬도 처리할 수 있습니다. 아래 구현은 `n <= m`일 때 `n`개의 row를 서로 다른 column에 배정합니다. 정사각형 assignment는 그대로 넣으면 되고, `n > m`이면 행/열을 바꾸거나 dummy column을 추가합니다.

## 2. 쓰지 말아야 할 경우

| 상황 | 더 먼저 볼 선택지 |
| --- | --- |
| forbidden edge가 많고 그래프가 sparse | Min-Cost Flow 또는 이분 matching 변형 |
| capacity, lower bound, penalty가 있다 | Min-Cost Flow |
| 모든 worker를 배정하지 않아도 된다 | dummy job 또는 Min-Cost Flow |
| 한쪽 크기가 20 이하로 매우 작다 | bitmask DP |
| 일반 그래프 matching이다 | Weighted Blossom 또는 small-N DP |

Hungarian은 "완전한 이분 1:1 배정"에 가장 깔끔합니다. 제약이 조금만 복잡해져도 flow로 모델링하는 편이 실수를 줄입니다.

## 3. 왜 그리디가 깨지는가

아래 비용 행렬에서 각 row가 남은 column 중 가장 싼 곳을 고르는 그리디를 생각해 봅니다.

|  | X | Y | Z |
| --- | ---: | ---: | ---: |
| A | 1 | 2 | 100 |
| B | 1 | 100 | 2 |
| C | 100 | 2 | 1 |

row 순서대로 가장 싼 column을 고르면 `A-X`, `B-Z`, `C-Y`가 되어 총 비용은 `1 + 2 + 2 = 5`입니다. 하지만 최적해는 `A-Y`, `B-X`, `C-Z`이고 총 비용은 `2 + 1 + 1 = 4`입니다.

문제는 지금 싼 선택이 나중의 선택지를 막는다는 점입니다. 그래서 Hungarian은 간선을 바로 확정하지 않고, "현재 dual 기준으로 비용이 0인 간선"만 사용하면서 augmenting path를 찾습니다.

## 4. 핵심 아이디어: potential과 tight edge

최소 비용 문제에서 row potential `u[i]`, column potential `v[j]`를 둡니다.

```text
reducedCost(i, j) = cost[i][j] - u[i] - v[j]
```

`reducedCost(i, j) == 0`인 간선을 `tight edge`라고 부릅니다. Hungarian은 matching을 tight edge 위에서만 유지합니다.

1. 현재 tight edge만으로 augmenting path를 찾는다.
2. augmenting path가 없으면, 아직 닿지 않은 column으로 가는 최소 slack만큼 potential을 조정한다.
3. 그러면 새로운 tight edge가 생긴다.
4. 새 tight edge를 포함해 다시 augmenting path를 찾고 matching을 하나 키운다.

![Hungarian potential과 tight edge 시각화](lesson-assets/hungarian-potentials.svg)

이 관점은 Min-Cost Flow의 shortest augmenting path와도 이어집니다. 다만 Hungarian은 assignment 구조를 이용해 potential과 slack을 훨씬 짧게 관리합니다.

## 5. 작은 예시 trace

다음 최소 비용 assignment를 보겠습니다.

|  | X | Y | Z |
| --- | ---: | ---: | ---: |
| A | 4 | 1 | 3 |
| B | 2 | 0 | 5 |
| C | 3 | 2 | 2 |

먼저 각 row의 최솟값을 potential처럼 빼면 `u = [1, 0, 2]`입니다.

|  | X | Y | Z |
| --- | ---: | ---: | ---: |
| A | 3 | 0 | 2 |
| B | 2 | 0 | 5 |
| C | 1 | 0 | 0 |

tight edge는 `A-Y`, `B-Y`, `C-Y`, `C-Z`입니다. 여기서 `A-Y`, `C-Z`를 잡으면 `B`가 아직 배정되지 않습니다. `B`에서 출발하면 tight edge `B-Y`로 갈 수 있지만, `Y`는 이미 `A`가 쓰고 있으므로 alternating path는 `B -> Y -> A`로 이어집니다.

이 상태에서 더 갈 tight edge가 없습니다. 닿은 row는 `A, B`, 닿지 않은 column은 `X, Z`입니다. 이 둘 사이의 최소 slack은 `2`입니다. potential을 `2`만큼 조정하면 `B-X`가 새 tight edge가 됩니다. 이제 `B-X`는 비어 있는 column으로 가므로 augmenting path가 생기고, matching은 다음처럼 커집니다.

```text
B-X, A-Y, C-Z
```

총 비용은 `2 + 1 + 2 = 5`입니다. 이 행렬의 최적해입니다.

## 6. C++ 구현

아래 구현은 `n <= m`인 최소 비용 assignment를 풉니다. 반환되는 `assignment[i]`는 row `i`가 배정된 0-indexed column입니다.

```cpp compile-check
#include <algorithm>
#include <limits>
#include <utility>
#include <vector>
using namespace std;

pair<long long, vector<int>> hungarianMinCost(const vector<vector<long long>>& cost) {
    int n = (int)cost.size();
    if (n == 0) {
        return {0, {}};
    }
    int m = (int)cost[0].size();

    const long long INF = numeric_limits<long long>::max() / 4;
    vector<long long> u(n + 1), v(m + 1);
    vector<int> p(m + 1), way(m + 1);

    for (int i = 1; i <= n; i++) {
        p[0] = i;
        int j0 = 0;
        vector<long long> minv(m + 1, INF);
        vector<char> used(m + 1, false);

        do {
            used[j0] = true;
            int i0 = p[j0];
            int j1 = 0;
            long long delta = INF;

            for (int j = 1; j <= m; j++) {
                if (used[j]) {
                    continue;
                }
                long long cur = cost[i0 - 1][j - 1] - u[i0] - v[j];
                if (cur < minv[j]) {
                    minv[j] = cur;
                    way[j] = j0;
                }
                if (minv[j] < delta) {
                    delta = minv[j];
                    j1 = j;
                }
            }

            for (int j = 0; j <= m; j++) {
                if (used[j]) {
                    u[p[j]] += delta;
                    v[j] -= delta;
                } else {
                    minv[j] -= delta;
                }
            }

            j0 = j1;
        } while (p[j0] != 0);

        do {
            int j1 = way[j0];
            p[j0] = p[j1];
            j0 = j1;
        } while (j0 != 0);
    }

    vector<int> assignment(n, -1);
    for (int j = 1; j <= m; j++) {
        if (p[j] != 0) {
            assignment[p[j] - 1] = j - 1;
        }
    }

    return {-v[0], assignment};
}
```

`n > m`이면 이 구현은 완전 배정을 만들 수 없습니다. 비용 행렬을 transpose해서 "더 작은 쪽을 row"로 두거나, dummy column을 추가해 `n <= m` 조건을 맞춥니다.

## 7. 구현 변수 읽는 법

| 변수 | 의미 |
| --- | --- |
| `u[i]` | row potential |
| `v[j]` | column potential |
| `p[j]` | column `j`에 현재 매칭된 row |
| `way[j]` | augmenting path 복원용 이전 column |
| `minv[j]` | 현재 alternating tree에서 column `j`로 가는 최소 slack |
| `used[j]` | 이번 augmenting 탐색에서 tree에 들어온 column |

핵심은 `minv[j]`입니다. 매번 row 전체를 다시 훑지 않고, 현재 tree에서 각 column으로 넘어가는 가장 작은 slack을 저장합니다. `delta = min(minv[j])`를 고르면 그만큼 potential을 움직였을 때 최소 하나의 새 tight edge가 생깁니다.

## 8. 시간 복잡도

| 항목 | 복잡도 |
| --- | ---: |
| 한 row를 추가하는 augmenting 과정 | `O(M^2)` |
| 전체 `N`개 row 처리 | `O(NM^2)` |
| 정사각형 `N x N` | `O(N^3)` |
| 메모리 | `O(N + M)` plus input matrix |

대부분의 대회 구현은 이 형태를 씁니다. dense assignment에서 Min-Cost Flow보다 상수가 작고, 코드도 짧습니다.

## 9. 자주 하는 실수

1. 최대 이익 문제를 최소 비용 코드에 그대로 넣는다. `-profit`으로 바꾸거나 `maxProfit - profit` 형태로 변환합니다.
2. `n > m`인데 row를 모두 배정하려고 한다. transpose 또는 dummy column이 필요합니다.
3. forbidden edge를 너무 큰 `INF`로 넣어 overflow를 낸다. `INF / 4` 정도 여유를 두고 비용 합 범위를 계산합니다.
4. unmatched가 허용되는 문제를 perfect assignment로 풀어 버린다. dummy job과 penalty를 명시해야 합니다.
5. `assignment` 방향을 헷갈린다. 위 코드는 row에서 column으로 가는 배열입니다.
6. `p`, `way`는 1-indexed column 배열인데 input은 0-indexed라는 점을 섞는다.

## 10. 문제를 볼 때 체크할 조건

- 왼쪽과 오른쪽이 분명한 이분 구조인가?
- 모든 왼쪽 정점을 반드시 배정해야 하는가?
- 오른쪽 정점은 최대 한 번만 쓰이는가, 정확히 한 번 쓰이는가?
- 비용 행렬이 dense인가, forbidden edge가 많은 sparse graph인가?
- 목적이 최소 비용인가, 최대 이익인가?
- capacity, lower bound, penalty 같은 추가 제약이 있는가?

추가 제약이 하나라도 강하게 보이면 Hungarian보다 Min-Cost Flow가 자연스러울 수 있습니다.

## 11. 대표 문제로 연결하기

현재 lesson catalog에는 Hungarian 전용 공개 practice가 아직 없습니다. 대신 문제를 볼 때 아래 신호를 찾습니다.

| 표현 | 해석 |
| --- | --- |
| 사람 `N`명과 작업 `N`개를 각각 하나씩 배정 | assignment |
| 순열을 골라 `sum cost[i][p[i]]` 최소화 | Hungarian |
| 두 집합 사이 거리를 모두 계산한 뒤 최소 매칭 | dense bipartite matching |
| 한쪽을 더미로 채워도 되는 penalty 배정 | dummy column/row |

## 12. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 작은 assignment problem `/practice/...` 문제 필요 | row greedy가 깨지는 반례 직접 계산 | counterexample |
| 표준 | TODO: 정사각형 비용 행렬 `/practice/...` 문제 필요 | `hungarianMinCost`로 최소 비용과 배정 복원 | potential, tight edge |
| 응용 | TODO: 최대 이익 assignment `/practice/...` 문제 필요 | 최대화 문제를 최소화 입력으로 변환 | `-profit`, offset |
| 함정 | TODO: forbidden edge가 있는 sparse assignment `/practice/...` 문제 필요 | Hungarian과 Min-Cost Flow 선택 비교 | dummy, INF, sparse graph |
