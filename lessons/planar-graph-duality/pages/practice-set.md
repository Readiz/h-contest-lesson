# Practice Set

Planar Graph Duality 허브의 연습은 face traversal, dual graph 구성, cut-cycle 변환을 순서대로 확인하는 흐름이 좋습니다.


0<=E<=400000, 0<=startFace,targetFace<F를 추가 입력 제한으로 둡니다. F<=200000과 간선 비용<=10^12이므로 단순 최단 경로 비용은 INF보다 작습니다.


입출력 코드는 [Dijkstra 최단거리](https://h.readiz.com/learn/dijkstra)의 Edge, INF, dijkstra 뒤에 붙입니다.

## 로컬 완결형 연습: Face Incidence Dual Shortest Path

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

```cpp
#include <iostream>

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

    vector<long long> dist = dijkstra(graph, startFace);

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

## 추가 로컬 연습 후보

### Square with a Diagonal

정점 네 개로 사각형을 만들고 대각선 하나를 추가합니다. half-edge traversal로 outer face와 두 내부 삼각형 face를 찾은 뒤, 대각선 edge의 양쪽 face가 서로 다른지 확인합니다.

### Tree as a Planar Graph

간선이 모두 bridge인 tree를 입력으로 넣고 face traversal 결과를 확인합니다. 이 경우 dual graph에 self-loop가 생기거나 모든 edge가 같은 face 양쪽을 가질 수 있음을 관찰합니다.

경계 cut 변환의 정확한 조건은 [Cut-Cycle Duality](https://h.readiz.com/learn/planar-graph-duality/cut-cycle-duality)에서 확인합니다.
