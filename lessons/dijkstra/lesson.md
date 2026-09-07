# Dijkstra 최단거리

Dijkstra 알고리즘은 **간선 가중치가 음수가 없는 그래프**에서, 한 시작 정점으로부터 다른 모든 정점까지의 최단거리를 구하는 알고리즘입니다. 한국어로는 보통 **다익스트라 알고리즘**이라고 부릅니다.

가장 대표적인 문제는 다음 형태입니다.

```text
정점과 가중치가 있는 간선이 주어진다.
시작 정점 s에서 각 정점 v까지의 최단거리 dist[v]를 구한다.
모든 간선의 가중치는 0 이상이다.
```

모든 경로를 직접 나열하면 경우의 수가 너무 많습니다. Dijkstra는 "지금까지 알려진 거리 중 가장 작은 정점은 이제 확정해도 된다"는 성질을 이용해 필요한 후보만 확장합니다.

## 최단거리 배열

`dist[v]`는 시작점에서 정점 `v`까지 현재까지 발견한 가장 짧은 거리입니다.

처음에는 시작점만 거리가 `0`이고, 나머지는 아직 모른다는 뜻으로 충분히 큰 값 `INF`를 넣습니다.

```cpp
const long long INF = 4e18;
vector<long long> dist(n, INF);
dist[start] = 0;
```

알고리즘이 진행되면서 더 짧은 경로를 발견하면 `dist` 값을 줄입니다. 이 작업을 보통 **relax**라고 부릅니다.

```text
u까지의 거리 + 간선 (u -> v)의 비용이
현재 dist[v]보다 작으면 dist[v]를 갱신한다.
```

## 가장 가까운 후보부터 본다

Dijkstra의 핵심 선택은 단순합니다.

```text
아직 확정하지 않은 정점 중 dist 값이 가장 작은 정점을 고른다.
```

이 정점을 `u`라고 합시다. 모든 간선 가중치가 0 이상이면, 아직 확정하지 않은 다른 정점을 거쳐 다시 `u`로 오는 경로가 더 짧아질 수 없습니다. 다른 후보들의 현재 거리도 `dist[u]` 이상이고, 거기에 0 이상의 간선을 더해도 `dist[u]`보다 작아질 수 없기 때문입니다.

그래서 `u`의 거리는 최단거리로 확정할 수 있습니다. 그다음 `u`에서 나가는 간선을 보며 이웃 정점의 거리를 갱신합니다.

## 작은 예시

다음 그래프에서 `0`번 정점에서 시작한다고 해봅시다.

```text
0 --2--> 1 --1--> 2
0 --5--> 2 --2--> 3
1 --4--> 3
```

초기 상태는 아래와 같습니다.

| 단계 | 확정 정점 | dist |
| --- | --- | --- |
| 시작 | 없음 | `[0, INF, INF, INF]` |
| 0 확정 | 0 | `[0, 2, 5, INF]` |
| 1 확정 | 0, 1 | `[0, 2, 3, 6]` |
| 2 확정 | 0, 1, 2 | `[0, 2, 3, 5]` |
| 3 확정 | 0, 1, 2, 3 | `[0, 2, 3, 5]` |

`2`번 정점의 처음 거리는 `0 -> 2`로 가는 `5`였습니다. 하지만 `1`을 확정한 뒤 `0 -> 1 -> 2` 경로를 발견하면서 `3`으로 줄어듭니다.

## 우선순위 큐 구현

매번 아직 확정하지 않은 모든 정점을 훑어 최솟값을 찾으면 `O(V^2)`입니다. 간선이 많지 않은 그래프에서는 우선순위 큐를 써서 더 빠르게 구현합니다.

C++의 `priority_queue`는 기본이 max heap이므로, `greater`를 붙여 min heap처럼 사용합니다. 아래 코드는 방향 그래프이며, 무방향 간선이면 양쪽 인접 리스트에 모두 추가합니다.

```cpp
#include <functional>
#include <queue>
#include <vector>
using namespace std;

const long long INF = 4e18;

struct Edge {
    int to;
    long long cost;
};

vector<long long> dijkstra(const vector<vector<Edge>>& graph, int start) {
    int n = (int)graph.size();
    vector<long long> dist(n, INF);
    priority_queue<
        pair<long long, int>,
        vector<pair<long long, int>>,
        greater<pair<long long, int>>
    > pq;

    dist[start] = 0;
    pq.push({0, start});

    while (!pq.empty()) {
        auto [currentDist, u] = pq.top();
        pq.pop();

        if (currentDist != dist[u]) {
            continue;
        }

        for (const Edge& edge : graph[u]) {
            int v = edge.to;
            long long nextDist = currentDist + edge.cost;
            if (nextDist < dist[v]) {
                dist[v] = nextDist;
                pq.push({nextDist, v});
            }
        }
    }

    return dist;
}
```

`currentDist != dist[u]`인 항목을 건너뛰는 부분이 중요합니다. 같은 정점의 거리가 여러 번 줄어들면 우선순위 큐 안에 오래된 후보가 남을 수 있습니다. 큐에서 꺼냈을 때 현재 `dist`와 다르면 이미 더 좋은 경로가 발견된 것이므로 버립니다.

## 왜 음수 간선이 있으면 안 될까

Dijkstra는 가장 가까운 후보를 꺼내는 순간 그 거리를 확정합니다. 이 말은 "나중에 돌아오는 경로가 이 값을 더 줄일 수 없다"는 뜻입니다.

음수 간선이 있으면 이 전제가 깨집니다.

```text
0 -> 1 비용 2
0 -> 2 비용 5
2 -> 1 비용 -10
```

시작점이 `0`이면 처음에는 `dist[1] = 2`, `dist[2] = 5`입니다. Dijkstra는 `1`을 먼저 확정하려고 합니다. 하지만 실제로는 `0 -> 2 -> 1` 경로의 비용이 `-5`입니다. 나중에 더 짧아지는 길이 존재하므로, 확정 선택이 안전하지 않습니다.

음수 간선이 있는 최단거리 문제는 Bellman-Ford 같은 다른 알고리즘을 고려해야 합니다.

## 시간 복잡도

우선순위 큐 구현의 시간 복잡도는 보통 아래처럼 봅니다.

```text
O((V + E) log V)
```

- `V`: 정점 수
- `E`: 간선 수

각 relax가 성공할 때마다 우선순위 큐에 후보를 넣고, 큐 연산에 `log V` 정도가 듭니다. 입력이 아주 조밀해서 `E`가 `V^2`에 가까우면 단순 `O(V^2)` 구현이 더 편할 때도 있지만, 일반적인 문제에서는 우선순위 큐 구현을 기본으로 씁니다.

## 실전 변형

시작점이 여러 개인 최단거리 문제는 multi-source Dijkstra로 처리합니다. 모든 시작점의 거리를 0으로 두고 우선순위 큐에 함께 넣으면 됩니다.

```cpp
for (int s : starts) {
    dist[s] = 0;
    pq.push({0, s});
}
```

목표 정점 하나의 최단거리만 필요하다면, 우선순위 큐에서 그 정점을 꺼내는 순간 종료할 수 있습니다. 이 시점의 거리는 이미 확정된 최단거리입니다.

```cpp
if (u == target) break;
```

거리 계산에서는 overflow도 조심합니다. `dist[u]`가 충분히 큰 `INF`일 때 `dist[u] + cost`를 바로 계산하면 범위를 넘을 수 있습니다. `long long`을 쓰고, `INF`는 실제 가능한 최댓값보다 크되 더해도 overflow가 나지 않는 값으로 잡습니다.

```cpp
const long long INF = 4e18;
if (dist[u] != INF && dist[u] + cost < dist[v]) {
    dist[v] = dist[u] + cost;
}
```

## 경로 복원

거리뿐 아니라 실제 최단 경로도 필요하면, 거리를 갱신할 때 이전 정점을 저장합니다.

```cpp
vector<int> parent(n, -1);

if (nextDist < dist[v]) {
    dist[v] = nextDist;
    parent[v] = u;
    pq.push({nextDist, v});
}
```

목표 정점 `target`에서 `parent`를 따라 시작점까지 거슬러 올라간 뒤 뒤집으면 경로가 됩니다.

```cpp
#include <algorithm>

vector<int> restorePath(int target, const vector<int>& parent) {
    vector<int> path;
    for (int v = target; v != -1; v = parent[v]) {
        path.push_back(v);
    }
    reverse(path.begin(), path.end());
    return path;
}
```

단, `dist[target] == INF`라면 시작점에서 도달할 수 없는 정점입니다. 이 경우에는 경로 복원을 하지 않거나 빈 경로로 처리합니다.

## BFS와의 관계

모든 간선 비용이 `1`이면 최단거리는 BFS로 구할 수 있습니다. BFS는 큐에 들어가는 순서 자체가 거리 오름차순이기 때문입니다.

간선 비용이 `0` 또는 `1`뿐이면 `deque`를 사용하는 0-1 BFS가 더 빠르고 간단할 수 있습니다. 비용이 일반적인 0 이상의 값이면 Dijkstra가 자연스럽습니다.

| 간선 비용 | 대표 알고리즘 |
| --- | --- |
| 모두 1 | BFS |
| 0 또는 1 | 0-1 BFS |
| 0 이상의 일반 가중치 | Dijkstra |
| 음수 가능 | Bellman-Ford 계열 |
