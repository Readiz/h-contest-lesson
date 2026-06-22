# Floyd-Warshall

Floyd-Warshall은 모든 정점 쌍 사이의 최단거리를 구하는 `O(N^3)` 동적 계획법입니다. Dijkstra나 Bellman-Ford가 한 시작점에서의 최단거리를 구한다면, Floyd-Warshall은 정점 수가 작고 모든 쌍의 관계가 필요할 때 쓰기 좋습니다.

이 레슨은 "중간 정점으로 어디까지 허용할 것인가"라는 DP 관점으로 Floyd-Warshall을 봅니다.

1. `dist[i][j]`를 직접 거리에서 시작한다.
2. 중간 정점 `k`를 하나씩 허용하며 최단거리를 갱신한다.
3. transitive closure, negative cycle, path 복원으로 확장한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 그래프 표현, 최단거리, 동적 계획법
- 함께 보면 좋은 레슨: Dijkstra 최단거리, Bellman-Ford와 음수 사이클, 동적 계획법
- 다음에 볼 레슨: graph closure, min-plus matrix multiplication

## 1. 언제 쓰는가

Floyd-Warshall은 정점 수가 작을 때 모든 쌍 정보를 단순하게 얻는 도구입니다.

| 문제 신호 | Floyd-Warshall 관점 |
| --- | --- |
| 모든 도시 쌍 최단거리가 필요하다 | APSP |
| 정점 수가 300 이하 정도다 | `O(N^3)` 가능성 검토 |
| 경유지를 여러 개 써도 된다 | 중간 정점 DP |
| 도달 가능성만 묻는다 | boolean transitive closure |
| 음수 간선이 있지만 음수 사이클은 없다 | 최단거리 가능 |

`N`이 수만이면 Floyd-Warshall은 맞지 않습니다. 그때는 시작점마다 Dijkstra를 돌리거나, 그래프 구조를 더 활용해야 합니다.

## 2. DP 의미

반복문의 `k`는 "0..k번 정점만 중간 정점으로 사용할 수 있다"는 뜻입니다.

```text
dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

`i -> j`로 바로 가는 기존 최단거리와, `i -> k -> j`로 나눠 가는 경로를 비교합니다. `k`를 바깥 반복문에 두어야 이 DP 의미가 유지됩니다.

## 3. 기본 구현

아래 구현은 0-index 정점과 `long long` 거리를 사용합니다.

```cpp compile-check
#include <algorithm>
#include <limits>
#include <vector>
using namespace std;

vector<vector<long long>> floydWarshall(vector<vector<long long>> dist) {
    const long long INF = numeric_limits<long long>::max() / 4;
    int n = (int)dist.size();

    for (int k = 0; k < n; ++k) {
        for (int i = 0; i < n; ++i) {
            if (dist[i][k] == INF) {
                continue;
            }
            for (int j = 0; j < n; ++j) {
                if (dist[k][j] == INF) {
                    continue;
                }
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
            }
        }
    }

    return dist;
}
```

초기화는 `dist[i][i] = 0`, 간선 `u -> v`에 대해 `dist[u][v] = min(dist[u][v], w)`입니다. 무방향 그래프면 반대 방향도 같이 넣습니다.

## 4. 반복문 순서

Floyd-Warshall은 `k`가 가장 바깥에 있어야 합니다.

```text
for k:
  for i:
    for j:
      relax i -> k -> j
```

`i, j, k` 순서로 바꾸면 "허용된 중간 정점 집합"이라는 DP 단계가 깨질 수 있습니다. 일부 입력에서는 우연히 맞아도 일반적으로 보장되지 않습니다.

## 5. 경로 복원

최단거리뿐 아니라 실제 경로가 필요하면 `next[i][j]`를 저장합니다. `next[i][j]`는 `i`에서 `j`로 가는 최단 경로의 첫 다음 정점입니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

vector<int> restorePath(int start, int target, const vector<vector<int>>& nextVertex) {
    if (nextVertex[start][target] == -1) {
        return {};
    }

    vector<int> path{start};
    while (start != target) {
        start = nextVertex[start][target];
        path.push_back(start);
    }
    return path;
}

void relaxPath(
    int i,
    int j,
    int k,
    vector<vector<long long>>& dist,
    vector<vector<int>>& nextVertex
) {
    if (dist[i][k] + dist[k][j] < dist[i][j]) {
        dist[i][j] = dist[i][k] + dist[k][j];
        nextVertex[i][j] = nextVertex[i][k];
    }
}
```

초기에는 간선이 있는 `i -> j`에 대해 `next[i][j] = j`로 둡니다. 경로가 없으면 `-1`입니다.

## 6. 도달 가능성: Transitive Closure

가중치가 아니라 도달 가능 여부만 필요하면 boolean matrix로 같은 구조를 씁니다.

```cpp compile-check
#include <vector>
using namespace std;

void transitiveClosure(vector<vector<int>>& reachable) {
    int n = (int)reachable.size();
    for (int k = 0; k < n; ++k) {
        for (int i = 0; i < n; ++i) {
            if (!reachable[i][k]) {
                continue;
            }
            for (int j = 0; j < n; ++j) {
                reachable[i][j] = reachable[i][j] || reachable[k][j];
            }
        }
    }
}
```

이 방식은 "A가 B보다 먼저 와야 한다" 같은 관계를 모두 전파할 때 자주 나옵니다. bitset을 쓰면 상수 시간을 크게 줄일 수 있습니다.

## 7. 음수 사이클

Floyd-Warshall이 끝난 뒤 `dist[v][v] < 0`인 정점이 있으면 음수 사이클이 있습니다. 그 정점을 거쳐 갈 수 있는 `i, j` 쌍은 최단거리가 정의되지 않습니다.

```text
if dist[i][v] != INF and dist[v][v] < 0 and dist[v][j] != INF:
    i -> j 최단거리는 -infinity 영향을 받음
```

문제에 따라 단순히 "음수 사이클 존재 여부"만 출력할 수도 있고, 영향을 받는 쌍을 별도로 표시해야 할 수도 있습니다.

## 8. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| 거리 초기화 | `O(N^2 + M)` | `O(N^2)` |
| Floyd-Warshall | `O(N^3)` | `O(N^2)` |
| transitive closure | `O(N^3)` | `O(N^2)` |
| 경로 복원 1회 | 경로 길이 | `next` matrix |

`N = 500`이면 `125,000,000`번 갱신이라 언어와 제한에 따라 빡빡할 수 있습니다. `N = 1000`이면 보통 일반 Floyd-Warshall은 어렵습니다.

## 9. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| `k` 반복문을 안쪽에 둠 | DP 의미가 깨짐 | `for k -> for i -> for j` 확인 |
| `INF + x` overflow | 음수로 wrap | 더하기 전 `INF` 여부 확인 |
| 다중 간선에서 마지막 값만 저장 | 더 큰 간선을 선택할 수 있음 | `min`으로 초기화 |
| 무방향 간선 반대 방향 누락 | 반쪽 그래프 처리 | `dist[u][v]`, `dist[v][u]` 둘 다 |
| `dist[i][i] = 0` 누락 | 자기 자신 거리 오류 | 초기화 루프 확인 |
| 음수 사이클 영향 무시 | 정의되지 않는 최단거리 출력 | `dist[v][v] < 0` 검사 |

## 10. 문제를 볼 때 체크할 조건

1. 모든 정점 쌍의 최단거리나 도달성이 필요한가?
2. `N^3`이 제한 안에 들어오는가?
3. 음수 간선이나 음수 사이클이 있는가?
4. 경로 자체를 복원해야 하는가?
5. 그래프가 directed인지 undirected인지 확인했는가?
6. 다중 간선과 unreachable 출력을 어떻게 처리해야 하는가?

Floyd-Warshall은 구현보다 조건 판단이 중요합니다. `N`이 작고 모든 쌍 정보를 원한다면 가장 단순하고 강력한 선택이지만, 입력 크기가 커지면 바로 다른 최단거리 전략을 검토해야 합니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 모든 쌍 최단거리 `/practice/...` 문제 필요 | `dist[i][j]` 초기화와 `k` 바깥 반복문 | apsp |
| 표준 | TODO: 도달 가능성 전파 `/practice/...` 문제 필요 | boolean transitive closure | reachability |
| 응용 | TODO: 최단 경로 복원 `/practice/...` 문제 필요 | `next[i][j]` matrix 관리 | path restore |
| 함정 | TODO: 음수 사이클 영향 `/practice/...` 문제 필요 | `dist[v][v] < 0` 검사 | negative cycle |
