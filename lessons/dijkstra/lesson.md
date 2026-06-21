# Dijkstra 최단거리

Dijkstra 알고리즘은 **간선 가중치가 음수가 없는 그래프**에서, 한 시작 정점으로부터 다른 모든 정점까지의 최단거리를 구하는 알고리즘입니다. 한국어로는 보통 **다익스트라 알고리즘**이라고 부릅니다.

가장 대표적인 문제는 다음 형태입니다.

```text
정점과 가중치가 있는 간선이 주어진다.
시작 정점 s에서 각 정점 v까지의 최단거리 dist[v]를 구한다.
모든 간선의 가중치는 0 이상이다.
```

모든 경로를 직접 나열하면 경우의 수가 너무 많습니다. Dijkstra는 "지금까지 알려진 거리 중 가장 작은 정점은 이제 확정해도 된다"는 성질을 이용해 필요한 후보만 확장합니다.

## 1. 최단거리 배열

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

## 2. 가장 가까운 후보부터 본다

Dijkstra의 핵심 선택은 단순합니다.

```text
아직 확정하지 않은 정점 중 dist 값이 가장 작은 정점을 고른다.
```

이 정점을 `u`라고 합시다. 모든 간선 가중치가 0 이상이면, 아직 확정하지 않은 다른 정점을 거쳐 다시 `u`로 오는 경로가 더 짧아질 수 없습니다. 다른 후보들의 현재 거리도 `dist[u]` 이상이고, 거기에 0 이상의 간선을 더해도 `dist[u]`보다 작아질 수 없기 때문입니다.

그래서 `u`의 거리는 최단거리로 확정할 수 있습니다. 그다음 `u`에서 나가는 간선을 보며 이웃 정점의 거리를 갱신합니다.

## 3. 작은 예시

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

## 4. 우선순위 큐 구현

매번 아직 확정하지 않은 모든 정점을 훑어 최솟값을 찾으면 `O(V^2)`입니다. 간선이 많지 않은 그래프에서는 우선순위 큐를 써서 더 빠르게 구현합니다.

C++의 `priority_queue`는 기본이 max heap이므로, `greater`를 붙여 min heap처럼 사용합니다.

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

## 5. 왜 음수 간선이 있으면 안 될까

Dijkstra는 가장 가까운 후보를 꺼내는 순간 그 거리를 확정합니다. 이 말은 "나중에 돌아오는 경로가 이 값을 더 줄일 수 없다"는 뜻입니다.

음수 간선이 있으면 이 전제가 깨집니다.

```text
0 -> 1 비용 2
0 -> 2 비용 5
2 -> 1 비용 -10
```

시작점이 `0`이면 처음에는 `dist[1] = 2`, `dist[2] = 5`입니다. Dijkstra는 `1`을 먼저 확정하려고 합니다. 하지만 실제로는 `0 -> 2 -> 1` 경로의 비용이 `-5`입니다. 나중에 더 짧아지는 길이 존재하므로, 확정 선택이 안전하지 않습니다.

음수 간선이 있는 최단거리 문제는 Bellman-Ford 같은 다른 알고리즘을 고려해야 합니다.

## 6. 시간 복잡도

우선순위 큐 구현의 시간 복잡도는 보통 아래처럼 봅니다.

```text
O((V + E) log V)
```

- `V`: 정점 수
- `E`: 간선 수

각 relax가 성공할 때마다 우선순위 큐에 후보를 넣고, 큐 연산에 `log V` 정도가 듭니다. 입력이 아주 조밀해서 `E`가 `V^2`에 가까우면 단순 `O(V^2)` 구현이 더 편할 때도 있지만, 일반적인 문제에서는 우선순위 큐 구현을 기본으로 씁니다.

## 7. 실전 변형

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

## 8. 경로 복원

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

## 9. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 음수 간선에 사용 | 잘못된 거리 확정 | 모든 간선 비용이 0 이상인지 확인 |
| `int` 거리 사용 | 큰 입력에서 overflow | 거리 합은 `long long` 사용 |
| 오래된 큐 항목 처리 | 불필요한 반복 증가 | `currentDist != dist[u]`면 건너뛰기 |
| 무방향 간선 한쪽만 추가 | 경로 누락 | `u -> v`, `v -> u`를 모두 추가 |
| 도달 불가 정점 미처리 | `INF` 출력 오류 | 출력 전 `dist[v] == INF` 확인 |
| `dist[u] + cost` overflow | 음수처럼 뒤집힌 거리 | `long long`과 안전한 `INF` 사용 |

## 10. BFS와의 관계

모든 간선 비용이 `1`이면 최단거리는 BFS로 구할 수 있습니다. BFS는 큐에 들어가는 순서 자체가 거리 오름차순이기 때문입니다.

간선 비용이 `0` 또는 `1`뿐이면 `deque`를 사용하는 0-1 BFS가 더 빠르고 간단할 수 있습니다. 비용이 일반적인 0 이상의 값이면 Dijkstra가 자연스럽습니다.

| 간선 비용 | 대표 알고리즘 |
| --- | --- |
| 모두 1 | BFS |
| 0 또는 1 | 0-1 BFS |
| 0 이상의 일반 가중치 | Dijkstra |
| 음수 가능 | Bellman-Ford 계열 |

0-1 BFS와 Bellman-Ford는 별도 레슨으로 분리해 보는 것이 좋습니다. Dijkstra 레슨에서는 "음수 없는 일반 가중치"라는 핵심 조건에 집중합니다.

## 11. 문제를 볼 때 체크할 조건

Dijkstra를 떠올렸다면 먼저 아래 조건을 확인합니다.

1. 그래프에서 한 시작점 기준 최단거리를 묻는가?
2. 간선 비용이 모두 0 이상인가?
3. 정점과 간선 수가 `O((V + E) log V)`로 처리 가능한가?
4. 도달할 수 없는 정점의 출력 규칙이 있는가?
5. 실제 경로가 필요한지, 거리만 필요한지 구분했는가?
6. 시작점이 여러 개인가, 목표 정점 하나만 필요한가?

정리하면, Dijkstra의 핵심은 "현재 가장 짧은 후보는 더 짧아질 수 없으므로 확정한다"입니다. 이 한 문장이 성립하려면 음수 간선이 없어야 하고, 구현에서는 우선순위 큐와 오래된 후보 제거가 가장 중요합니다.

## 12. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 모든 간선 비용이 1인 최단거리 문제 추가 | BFS와 Dijkstra를 비교하며 거리 배열 의미 확인 | BFS, 거리 배열 |
| 표준 | TODO: 양수 가중치 그래프 최단거리 문제 추가 | 우선순위 큐, 오래된 후보 제거, `long long` 거리 구현 | priority queue, stale entry |
| 응용 | TODO: 여러 시작점 또는 목표 정점 하나인 문제 추가 | multi-source 초기화와 조기 종료 조건 적용 | multi-source, early stop |
| 함정 | TODO: 음수 간선이 섞인 그래프 문제 추가 | Dijkstra를 쓰면 안 되는 조건과 Bellman-Ford 필요성 확인 | negative edge |
