# Floyd-Warshall

Floyd-Warshall은 모든 정점 쌍 사이의 최단거리를 구하는 `O(N^3)` 동적 계획법입니다. Dijkstra나 Bellman-Ford가 한 시작점에서의 최단거리를 구한다면, Floyd-Warshall은 정점 수가 작고 모든 쌍의 관계가 필요할 때 쓰기 좋습니다.

## 언제 쓰는가

Floyd-Warshall은 정점 수가 작을 때 모든 쌍 정보를 단순하게 얻는 도구입니다.

| 문제 신호 | Floyd-Warshall 관점 |
| --- | --- |
| 모든 도시 쌍 최단거리가 필요하다 | APSP |
| 정점 수가 300 이하 정도다 | `O(N^3)` 가능성 검토 |
| 경유지를 여러 개 써도 된다 | 중간 정점 DP |
| 도달 가능성만 묻는다 | boolean transitive closure |
| 음수 간선이 있지만 음수 사이클은 없다 | 최단거리 가능 |

`N`이 수만이면 Floyd-Warshall은 맞지 않습니다. 그때는 시작점마다 Dijkstra를 돌리거나, 그래프 구조를 더 활용해야 합니다.

## DP 의미

반복문의 `k`는 "0..k번 정점만 중간 정점으로 사용할 수 있다"는 뜻입니다.

```text
dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

`i -> j`로 바로 가는 기존 최단거리와, `i -> k -> j`로 나눠 가는 경로를 비교합니다. `k`를 바깥 반복문에 두어야 이 DP 의미가 유지됩니다.

## 기본 구현

아래 구현은 0-index 정점과 `long long` 거리를 사용합니다. 도달 불가는 코드와 같은 `INF`로 초기화하고, 모든 덧셈 결과는 정수 범위 안이어야 합니다. 음수 사이클이 있으면 반복 중 값이 급격히 작아질 수 있으므로 단순 경로 길이만으로 범위를 잡으면 부족합니다.

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

초기화는 `dist[i][i] = 0`, 간선 `u -> v`에 대해 `dist[u][v] = min(dist[u][v], w)`입니다. 무방향 그래프면 반대 방향도 같이 넣습니다. 다중 간선은 가장 작은 비용만 남기고, 경로가 없는 `INF` 값은 덧셈에서 제외합니다.

## 경로 복원

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

`next[i][i] = i`로 두면 자기 자신으로 가는 길도 `[i]`로 복원합니다. 초기에는 간선이 있는 `i -> j`에 대해 `next[i][j] = j`로 둡니다. 경로가 없으면 `-1`입니다. `relaxPath`는 기본 구현의 두 `INF` 검사 뒤에서만 호출합니다. 음수 사이클의 영향을 받는 쌍에는 최단 경로가 없으므로 복원하지 않습니다.

## 도달 가능성만 필요할 때

거리 대신 도달 여부를 저장해도 같은 순서로 계산합니다. `reachable[i][j]`를 갱신할 식은 `reachable[i][j] || (reachable[i][k] && reachable[k][j])`입니다. 기존 경로가 있거나, `k`까지 갈 수 있고 `k`에서 목적지로 갈 수 있으면 연결된 것입니다.

## 음수 사이클

Floyd-Warshall이 끝난 뒤 `dist[v][v] < 0`인 정점이 있으면 음수 사이클이 있습니다. 그 정점을 거쳐 갈 수 있는 `i, j` 쌍은 최단거리가 정의되지 않습니다.

```text
if dist[i][v] != INF and dist[v][v] < 0 and dist[v][j] != INF:
    i -> j 최단거리는 -infinity 영향을 받음
```

문제에 따라 단순히 "음수 사이클 존재 여부"만 출력할 수도 있고, 영향을 받는 쌍을 별도로 표시해야 할 수도 있습니다.

## 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| 거리 초기화 | `O(N^2 + M)` | `O(N^2)` |
| Floyd-Warshall | `O(N^3)` | `O(N^2)` |
| transitive closure | `O(N^3)` | `O(N^2)` |
| 경로 복원 1회 | 경로 길이 | `next` matrix |

`N = 500`이면 `125,000,000`번 갱신이라 언어와 제한에 따라 빡빡할 수 있습니다. `N = 1000`이면 보통 일반 Floyd-Warshall은 어렵습니다.
