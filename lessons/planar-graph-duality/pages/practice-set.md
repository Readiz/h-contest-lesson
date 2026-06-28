# Practice Set

Planar Graph Duality 허브의 연습은 face traversal, dual graph 구성, cut-cycle 변환을 순서대로 확인하는 흐름이 좋습니다. 실제 h-contest 문제가 아직 부족한 주제는 임의 ID를 만들지 않고 `TODO`로 남기며, face incidence가 주어진 경우의 dual shortest path를 로컬 완결형으로 먼저 둡니다.

## 1. 로컬 완결형 연습: Face Incidence Dual Shortest Path

평면 그래프의 각 primal edge가 양쪽 face 번호와 비용을 알고 있다고 합시다. 각 face를 dual graph의 정점으로 만들고, primal edge 하나를 양쪽 face 사이의 dual edge로 바꾼 뒤 `startFace`에서 `targetFace`까지의 최단거리를 구합니다.

### 입력

```text
F E startFace targetFace
leftFace_0 rightFace_0 cost_0
...
leftFace_{E-1} rightFace_{E-1} cost_{E-1}
```

- `1 <= F <= 200000`
- `0 <= leftFace_i, rightFace_i < F`
- `0 <= cost_i <= 10^12`
- `leftFace_i == rightFace_i`인 bridge/self-loop dual edge도 입력될 수 있습니다.

### 출력

```text
dual graph에서 startFace부터 targetFace까지의 최단거리
```

도달할 수 없으면 `-1`을 출력합니다.

### 예시

사각형에 대각선 하나가 있는 그림을 생각합니다. face `0`은 outer face, face `1`, `2`는 두 내부 삼각형입니다.

```text
3 5 1 2
0 1 4
0 1 2
0 2 3
0 2 5
1 2 1
```

```text
1
```

### 손으로 따라가는 Trace

primal edge를 dual edge로 바꾸면 아래와 같습니다.

| primal edge 의미 | 양쪽 face | dual edge cost |
| --- | --- | ---: |
| outer와 triangle 1의 경계 | `0-1` | 4 |
| outer와 triangle 1의 다른 경계 | `0-1` | 2 |
| outer와 triangle 2의 경계 | `0-2` | 3 |
| outer와 triangle 2의 다른 경계 | `0-2` | 5 |
| diagonal | `1-2` | 1 |

`1 -> 2` 최단거리는 diagonal에 대응하는 dual edge 하나라서 `1`입니다. 같은 face 쌍 사이에 edge가 여러 개 있어도 Dijkstra는 multi-edge를 그대로 허용하면 됩니다.

### 구현 기준

```cpp compile-check
#include <functional>
#include <iostream>
#include <queue>
#include <utility>
#include <vector>
using namespace std;

const long long INF = (1LL << 62);

struct Edge {
    int to = 0;
    long long cost = 0;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int faceCount;
    int edgeCount;
    int startFace;
    int targetFace;
    cin >> faceCount >> edgeCount >> startFace >> targetFace;

    vector<vector<Edge>> graph(faceCount);
    for (int i = 0; i < edgeCount; ++i) {
        int leftFace;
        int rightFace;
        long long cost;
        cin >> leftFace >> rightFace >> cost;

        graph[leftFace].push_back({rightFace, cost});
        if (leftFace != rightFace) {
            graph[rightFace].push_back({leftFace, cost});
        }
    }

    vector<long long> dist(faceCount, INF);
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<pair<long long, int>>> pq;
    dist[startFace] = 0;
    pq.push({0, startFace});

    while (!pq.empty()) {
        auto [cost, face] = pq.top();
        pq.pop();
        if (cost != dist[face]) {
            continue;
        }
        for (const Edge& edge : graph[face]) {
            long long nextCost = cost + edge.cost;
            if (nextCost < dist[edge.to]) {
                dist[edge.to] = nextCost;
                pq.push({nextCost, edge.to});
            }
        }
    }

    if (dist[targetFace] == INF) {
        cout << -1 << '\n';
    } else {
        cout << dist[targetFace] << '\n';
    }
}
```

### Stress 기준

1. `F <= 8`에서는 Floyd-Warshall로 모든 face pair 최단거리를 구해 Dijkstra 결과와 비교합니다.
2. multi-edge, self-loop, disconnected dual graph를 deterministic case로 둡니다.
3. half-edge traversal에서 face incidence를 직접 만든 경우에는 먼저 `V - E + F = 1 + C`를 통과해야 이 연습으로 내려옵니다.
4. directed primal edge를 무향 dual edge로 바꾸면 안 되는 문제인지 별도로 확인합니다.

## 2. 연습 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | 로컬: face incidence dual shortest path | face adjacency로 dual 만들기 | outer face |
| 표준 | TODO: half-edge face traversal `/practice/...` 문제 필요 | 좌표에서 face 번호 찾기 | angle sort |
| 응용 | TODO: planar cut shortest path `/practice/...` 문제 필요 | cut을 dual path로 변환 | cut-cycle duality |
| 함정 | TODO: bridge in dual graph `/practice/...` 문제 필요 | self-loop와 bridge 처리 | Euler formula |

## 3. 추가 로컬 연습 후보

### Square with a Diagonal

정점 네 개로 사각형을 만들고 대각선 하나를 추가합니다. half-edge traversal로 outer face와 두 내부 삼각형 face를 찾은 뒤, 대각선 edge의 양쪽 face가 서로 다른지 확인합니다.

### Tree as a Planar Graph

간선이 모두 bridge인 tree를 입력으로 넣고 face traversal 결과를 확인합니다. 이 경우 dual graph에 self-loop가 생기거나 모든 edge가 같은 face 양쪽을 가질 수 있음을 관찰합니다.

### Boundary Cut to Dual Path

작은 격자 그래프에서 위쪽 boundary와 아래쪽 boundary를 분리하는 최소 edge cut을 만들고, dual graph에서 좌우 또는 boundary arc 사이 shortest path와 비용이 같은지 비교합니다.

## 4. 제출 전 체크리스트

- `V - E + F = 1 + C`를 출력해 확인했는가?
- outer face 번호를 signed area로 찾았는가?
- dual graph가 multi-edge와 self-loop를 허용하는가?
- directed 문제를 무향 dual shortest path로 바꾸지 않았는가?
- 작은 그림에서 primal edge id와 dual edge id가 같은 비용으로 대응하는가?
