# Matching과 Cover Duality

이분 그래프에서는 maximum matching과 minimum vertex cover가 같은 크기를 가집니다. 이 성질을 Konig theorem이라고 부르며, "서로 겹치지 않는 선택을 최대화"하는 문제와 "모든 간선을 덮는 최소 정점 집합" 문제를 서로 바꿔 생각하게 해 줍니다.

이 레슨은 Max Flow 이후에 보는 이분 매칭의 해석 확장입니다.

1. 이분 매칭을 flow 없이 직접 구현한다.
2. maximum matching에서 minimum vertex cover를 복원한다.
3. vertex cover, minimum path cover, maximum independent set으로 모델링을 넓힌다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Max Flow, Bipartite Matching, BFS/DFS
- 함께 보면 좋은 레슨: Max Flow, Min Cut, Bipartite Matching, SCC와 2-SAT
- 다음에 볼 레슨: Dilworth theorem, min-cost matching, general graph matching

## 1. 문제 신호

Matching은 "한 정점이 최대 하나만 선택된다"는 제약이 양쪽에 있을 때 나옵니다.

| 문제 표현 | 그래프 모델 |
| --- | --- |
| 일과 사람을 겹치지 않게 배정 | 사람-일 이분 매칭 |
| 행/열에서 충돌하지 않게 선택 | 행-열 간선 매칭 |
| 모든 충돌을 최소 정점으로 막기 | minimum vertex cover |
| 최대한 많은 독립 정점 선택 | 전체 정점 - minimum vertex cover |
| DAG에서 최소 경로 덮개 | split graph matching |

이분 그래프인지 먼저 확인해야 합니다. 일반 그래프 matching은 blossom 같은 다른 알고리즘이 필요합니다.

## 2. Matching과 Vertex Cover

이분 그래프 `L - R`에서 matching은 공통 정점을 공유하지 않는 간선 집합입니다. Vertex cover는 모든 간선의 양끝 중 적어도 하나를 포함하는 정점 집합입니다.

Konig theorem은 아래를 말합니다.

```text
maximum matching size = minimum vertex cover size
```

증명 자체보다 대회에서 중요한 것은 maximum matching을 구한 뒤 minimum vertex cover를 실제로 복원할 수 있다는 점입니다.

## 3. Alternating path로 cover 복원

maximum matching을 구한 뒤, 매칭되지 않은 왼쪽 정점에서 alternating path를 따라갑니다.

1. 왼쪽에서는 matching에 없는 간선을 따라 오른쪽으로 간다.
2. 오른쪽에서는 matching에 있는 간선을 따라 왼쪽으로 간다.
3. 도달한 왼쪽 정점 집합을 `Z_L`, 도달한 오른쪽 정점 집합을 `Z_R`이라고 한다.

그러면 minimum vertex cover는 아래입니다.

```text
(L - Z_L) union (R intersect Z_R)
```

이 공식은 min cut의 reachable side와 같은 의미로 볼 수 있습니다.

## 4. DFS 기반 매칭과 Cover 복원

아래 구현은 작은 입력에서 쓰기 쉬운 DFS augmenting path 매칭입니다. 매칭을 구한 뒤 alternating BFS로 minimum vertex cover를 복원합니다.

```cpp compile-check
#include <queue>
#include <utility>
#include <vector>
using namespace std;

struct BipartiteMatchingCover {
    int nLeft;
    int nRight;
    vector<vector<int>> adj;
    vector<int> matchLeft;
    vector<int> matchRight;
    vector<int> seen;

    BipartiteMatchingCover(int nLeft, int nRight)
        : nLeft(nLeft),
          nRight(nRight),
          adj(nLeft),
          matchLeft(nLeft, -1),
          matchRight(nRight, -1),
          seen(nRight, 0) {}

    void addEdge(int left, int right) {
        adj[left].push_back(right);
    }

    bool dfs(int left, int stamp) {
        for (int right : adj[left]) {
            if (seen[right] == stamp) {
                continue;
            }
            seen[right] = stamp;
            if (matchRight[right] == -1 || dfs(matchRight[right], stamp)) {
                matchLeft[left] = right;
                matchRight[right] = left;
                return true;
            }
        }
        return false;
    }

    int maximumMatching() {
        int result = 0;
        for (int left = 0; left < nLeft; ++left) {
            if (dfs(left, left + 1)) {
                ++result;
            }
        }
        return result;
    }

    pair<vector<int>, vector<int>> minimumVertexCover() {
        vector<int> visitedLeft(nLeft, 0);
        vector<int> visitedRight(nRight, 0);
        queue<int> q;

        for (int left = 0; left < nLeft; ++left) {
            if (matchLeft[left] == -1) {
                visitedLeft[left] = 1;
                q.push(left);
            }
        }

        while (!q.empty()) {
            int left = q.front();
            q.pop();
            for (int right : adj[left]) {
                if (matchLeft[left] == right || visitedRight[right]) {
                    continue;
                }
                visitedRight[right] = 1;
                int nextLeft = matchRight[right];
                if (nextLeft != -1 && !visitedLeft[nextLeft]) {
                    visitedLeft[nextLeft] = 1;
                    q.push(nextLeft);
                }
            }
        }

        vector<int> coverLeft;
        vector<int> coverRight;
        for (int left = 0; left < nLeft; ++left) {
            if (!visitedLeft[left]) {
                coverLeft.push_back(left);
            }
        }
        for (int right = 0; right < nRight; ++right) {
            if (visitedRight[right]) {
                coverRight.push_back(right);
            }
        }
        return {coverLeft, coverRight};
    }
};
```

DFS 매칭은 `O(VE)` 정도로 생각하면 됩니다. 정점과 간선이 크면 Hopcroft-Karp의 `O(E sqrt(V))` 구현을 검토합니다.

## 5. Maximum Independent Set

이분 그래프에서 minimum vertex cover를 알면 maximum independent set도 바로 얻습니다.

```text
maximum independent set size = |V| - minimum vertex cover size
```

Independent set은 서로 간선으로 연결되지 않은 정점 집합입니다. "서로 충돌하는 쌍을 간선으로 만들고, 충돌 없이 최대한 많이 고르기" 같은 문제에서 사용합니다.

주의할 점은 이 공식이 이분 그래프에서 vertex cover를 정확히 구할 수 있기 때문에 실용적이라는 것입니다. 일반 그래프의 maximum independent set은 훨씬 어렵습니다.

## 6. DAG Minimum Path Cover

DAG의 모든 정점을 몇 개의 vertex-disjoint path로 덮고 싶다면, 각 정점을 왼쪽/오른쪽으로 복제한 이분 그래프를 만듭니다.

```text
원래 DAG 간선 u -> v
복제 그래프 간선 u_left -> v_right
```

그러면 최소 path cover 수는 아래입니다.

```text
N - maximum matching size
```

매칭된 간선은 두 정점을 같은 path에서 이어 붙인다는 뜻입니다. DAG가 아니면 이 해석이 깨질 수 있으니 위상 구조를 먼저 확인합니다.

## 7. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| DFS augmenting matching | `O(VE)` | `O(V + E)` |
| Hopcroft-Karp | `O(E sqrt(V))` | `O(V + E)` |
| minimum vertex cover 복원 | `O(V + E)` | `O(V)` |
| DAG path cover 변환 | `O(V + E)` + matching | split graph |

입력이 작다면 DFS 매칭이 구현 실수도 적고 충분합니다. 제한이 커지면 Hopcroft-Karp로 넘어갑니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 일반 그래프에 이분 매칭 공식 적용 | 오답 | 그래프가 좌/우로 나뉘는지 확인 |
| cover 복원에서 시작점을 모든 unmatched 정점으로 잡지 않음 | cover 누락 | unmatched left 전체에서 시작 |
| alternating edge 방향을 반대로 탐색 | cover 공식 깨짐 | 왼쪽은 unmatched edge, 오른쪽은 matched edge |
| maximum independent set을 cover 자체로 출력 | 보수 집합 필요 | `V - cover` 확인 |
| DAG path cover에 cycle 있는 그래프 사용 | 해석 오류 | DAG 여부 먼저 검사 |
| 1-index/0-index 혼동 | 매칭 배열 범위 오류 | 좌/우 크기 분리 |

## 9. 문제를 볼 때 체크할 조건

1. 선택 대상이 좌/우 두 부류로 나뉘는가?
2. 각 대상은 최대 하나의 짝만 가질 수 있는가?
3. "모든 충돌을 덮기"가 vertex cover로 바뀌는가?
4. "충돌 없이 최대 선택"이 independent set으로 바뀌는가?
5. DAG path cover로 정점들을 경로에 이어 붙일 수 있는가?
6. 입력 크기가 DFS 매칭으로 충분한가?

Matching과 cover duality는 같은 구조를 최대화와 최소화 양쪽에서 보게 해 줍니다. 문제의 문장이 "최대 배정"인지 "최소 차단"인지 달라도, 이분 그래프 위에서는 같은 matching 결과에서 답이 나올 수 있습니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 기본 이분 매칭 `/practice/...` 문제 필요 | augmenting path 매칭 구현 | bipartite matching |
| 표준 | TODO: minimum vertex cover `/practice/...` 문제 필요 | alternating path로 cover 복원 | Konig theorem |
| 응용 | TODO: DAG path cover `/practice/...` 문제 필요 | split graph와 `N - matching` | path cover |
| 함정 | TODO: maximum independent set 변환 `/practice/...` 문제 필요 | vertex cover의 보수 출력 | independent set |
