# Face 순회와 Dual Graph 구성

좌표와 간선만 주어진 planar graph에서 dual graph를 만들려면 먼저 face를 찾아야 합니다. 가장 안정적인 방법은 무향 간선을 양방향 half-edge로 쪼개고, 각 정점의 outgoing half-edge를 polar angle 순서로 정렬한 뒤, 아직 방문하지 않은 half-edge를 따라 face를 순회하는 것입니다.


이 구현은 연결된 straight-line planar embedding, 서로 다른 정점 좌표, self-loop·중첩 간선·간선 내부의 다른 정점 없음, 좌표 절댓값<=10^9를 전제로 합니다. 비연결 입력에서는 순회 하나가 face가 아니라 boundary component일 수 있어 포함 관계로 합쳐야 합니다. 연결된 단일 정점은 outer face 하나로 처리합니다. 정렬은 정수 반평면과 외적을 사용하고 면적 합은 __int128입니다.

## Half-edge 구조

무향 edge `(u, v)` 하나는 두 directed half-edge `u -> v`, `v -> u`가 됩니다. 각 half-edge는 반대 방향 half-edge와 같은 primal edge id를 공유합니다.

```text
half h:     u -> v
opposite:  v -> u
left face: h를 따라갈 때 왼쪽에 있는 face
```

face traversal은 각 half-edge의 left face를 한 번씩 채우는 과정입니다.

## 다음 half-edge 고르기

각 정점의 outgoing half-edge를 angle 오름차순으로 정렬합니다. 현재 half-edge가 `u -> v`라면, `v`에 도착한 뒤 `v -> u`의 정렬 위치를 찾고 그 바로 이전 half-edge를 다음으로 택합니다. 이 규칙은 현재 방향의 왼쪽 face를 따라가게 합니다.

```text
next(u -> v) = outgoing[v][position(v -> u) - 1]
```

인덱스는 cyclic하게 돌립니다.

## 구현

아래 코드는 straight-line planar embedding을 가정합니다. 간선 교차가 없고, 같은 두 정점을 잇는 여러 edge가 같은 선분 위에 완전히 겹치지 않는다는 조건이 필요합니다. 겹치는 multi-edge나 곡선 embedding이 필요한 입력은 좌표만으로 rotation order를 복원할 수 없으므로, 문제에서 half-edge 순서나 face 정보를 따로 줘야 합니다.

```cpp compile-check
#include <algorithm>
#include <cmath>
#include <vector>
using namespace std;

struct Point {
    long long x = 0;
    long long y = 0;
};

struct InputEdge {
    int u = 0;
    int v = 0;
    int weight = 0;
};

struct HalfEdge {
    int from = 0;
    int to = 0;
    int edgeId = 0;
    int opposite = 0;

};

struct FaceEmbedding {
    vector<HalfEdge> halfEdges;
    vector<vector<int>> faceHalfEdges;
    vector<int> faceOfHalfEdge;
    vector<__int128> signedDoubleArea;
    int outerFace = -1;
};

__int128 cross(const Point& a, const Point& b) {
    return (__int128)a.x * b.y - (__int128)a.y * b.x;
}

FaceEmbedding buildFaceEmbedding(
    const vector<Point>& points,
    const vector<InputEdge>& edges
) {
    int n = (int)points.size();
    if (n==1 && edges.empty()) {
        FaceEmbedding result; result.outerFace=0;
        result.faceHalfEdges.push_back({}); result.signedDoubleArea.push_back(0);
        return result;
    }
    vector<HalfEdge> halfEdges;
    vector<vector<int>> outgoing(n);

    for (int edgeId = 0; edgeId < (int)edges.size(); ++edgeId) {
        int u = edges[edgeId].u;
        int v = edges[edgeId].v;
        int first = (int)halfEdges.size();
        int second = first + 1;

        halfEdges.push_back({u, v, edgeId, second});
        halfEdges.push_back({v, u, edgeId, first});
        outgoing[u].push_back(first);
        outgoing[v].push_back(second);
    }

    vector<int> position(halfEdges.size(), -1);
    for (int v = 0; v < n; ++v) {
        sort(outgoing[v].begin(), outgoing[v].end(), [&](int a, int b) {
            Point da{points[halfEdges[a].to].x-points[v].x,points[halfEdges[a].to].y-points[v].y};
            Point db{points[halfEdges[b].to].x-points[v].x,points[halfEdges[b].to].y-points[v].y};
            auto half=[](Point d){return d.y<0 || (d.y==0 && d.x<0);};
            if (half(da)!=half(db)) return half(da)<half(db);
            auto turn=cross(da,db);
            if (turn!=0) return turn>0;
            return a<b;
        });
        for (int i = 0; i < (int)outgoing[v].size(); ++i) {
            position[outgoing[v][i]] = i;
        }
    }

    vector<int> nextHalfEdge(halfEdges.size(), -1);
    for (int h = 0; h < (int)halfEdges.size(); ++h) {
        int at = halfEdges[h].to;
        int reverse = halfEdges[h].opposite;
        int degree = (int)outgoing[at].size();
        int pos = position[reverse];
        int nextPos = (pos - 1 + degree) % degree;
        nextHalfEdge[h] = outgoing[at][nextPos];
    }

    FaceEmbedding result;
    result.halfEdges = halfEdges;
    result.faceOfHalfEdge.assign(halfEdges.size(), -1);

    vector<char> visited(halfEdges.size(), 0);
    for (int start = 0; start < (int)halfEdges.size(); ++start) {
        if (visited[start]) {
            continue;
        }

        int faceId = (int)result.faceHalfEdges.size();
        vector<int> boundary;
        __int128 area = 0;
        int h = start;
        do {
            visited[h] = 1;
            result.faceOfHalfEdge[h] = faceId;
            boundary.push_back(h);
            const HalfEdge& edge = halfEdges[h];
            area += cross(points[edge.from], points[edge.to]);
            h = nextHalfEdge[h];
        } while (h != start);

        result.faceHalfEdges.push_back(boundary);
        result.signedDoubleArea.push_back(area);
    }

    for (int face = 0; face < (int)result.signedDoubleArea.size(); ++face) {
        if (
            result.outerFace == -1
            || result.signedDoubleArea[face] < result.signedDoubleArea[result.outerFace]
        ) {
            result.outerFace = face;
        }
    }

    return result;
}
```

## Outer Face 식별

위 순회 규칙에서는 내부 face가 보통 양의 signed area를 가지고, outer face는 음의 signed area를 갖습니다. 따라서 signed area가 가장 작은 face를 outer face로 잡을 수 있습니다.

```text
outerFace = argmin signedDoubleArea[face]
```

bridge만 있는 tree처럼 면적이 정확히 0인 입력은 dual shortest path 문제로 바로 쓰기 어렵습니다. 이 경우 face가 사실상 outer 하나이고, bridge edge 양쪽 face가 같아지는 self-loop 상황을 별도로 처리해야 합니다.

## Euler 검증

연결 성분 수가 `C`인 planar embedding에서는 아래가 성립합니다.

```text
V - E + F = 1 + C
```

이 식이 맞지 않으면 보통 다음 중 하나입니다.

- 간선이 실제로 교차한다.
- 정점별 angle 정렬 tie가 embedding과 다르다.
- half-edge를 양방향으로 만들지 않았다.
- 비연결 성분의 boundary walk를 서로 다른 face로 잘못 셌다.
- 입력이 겹치는 multi-edge를 포함해 좌표만으로 rotation order를 알 수 없다.

## Bridge와 Multi-edge 정책

Bridge는 양쪽 half-edge가 같은 face를 가리킬 수 있습니다. dual graph에서는 self-loop가 되며, shortest path나 cut 변환에서는 보통 유용하지 않아 무시할 수 있지만, 문제 조건에 따라 비용 있는 loop를 보존해야 할 수도 있습니다.

Multi-edge는 두 종류로 나눕니다.

- 서로 다른 곡선이나 embedding 순서가 주어진 multi-edge: rotation order를 입력으로 받아 처리합니다.
- 같은 두 좌표를 잇는 겹친 straight segment: 좌표만으로 face를 복원할 수 없으므로 이 구현의 전제 밖입니다.

## Dual Graph 만들기

primal graph의 face 하나를 dual graph의 정점 하나로 둡니다. primal edge `e`가 face `a`와 face `b` 사이의 경계라면 dual edge `(a, b)`를 만듭니다.

```text
primal edge e separates face left(e), right(e)
dual edge e* connects left(e) and right(e)
```

outer face도 하나의 face입니다. 외부와 내부를 구분해야 하는 문제에서는 outer face의 번호를 특별히 관리합니다.

## Cut-Cycle 대응

단순 cycle과 bond의 대응 및 s-t를 공통 face 안에서 분리하는 구성은 [Cut-Cycle Duality](https://h.readiz.com/learn/planar-graph-duality/cut-cycle-duality)에 둡니다. 일반 cut을 항상 dual 경로 하나로 보지 않습니다.

## 작은 예시

사각형에 대각선 하나가 있는 planar graph를 봅니다.

```text
1 ---- 2
|    / |
|  /   |
4 ---- 3
```

대각선 `2-4`가 내부 사각형을 두 삼각형 face로 나눕니다. dual graph에는 아래 face들이 생깁니다.

```text
F0 = outer face
F1 = triangle 1-2-4
F2 = triangle 2-3-4
```

edge `2-4`는 `F1`과 `F2` 사이의 dual edge가 됩니다. 바깥 경계 edge들은 outer face `F0`와 내부 face 하나를 잇는 dual edge가 됩니다.

## Face 순회 결과로 dual 간선 만들기

위 `buildFaceEmbedding`의 결과에서 원본 간선 `i` 양쪽 face는 `faceOfHalfEdge[2*i]`와 `faceOfHalfEdge[2*i+1]`입니다. 이를 아래 `leftFaceUV`, `leftFaceVU`에 넣고, face 수는 `faceHalfEdges.size()`를 사용합니다. 문제에서 face 번호를 직접 주면 순회를 생략하고 같은 구성 함수를 사용합니다.

```cpp
struct EdgeFace {
    int u = 0;
    int v = 0;
    int leftFaceUV = 0;
    int leftFaceVU = 0;
    long long weight = 0;
};

vector<vector<pair<int, long long>>> buildDualGraph(
    int faceCount,
    const vector<EdgeFace>& edges
) {
    vector<vector<pair<int, long long>>> dual(faceCount);
    for (const EdgeFace& edge : edges) {
        int a = edge.leftFaceUV;
        int b = edge.leftFaceVU;
        dual[a].push_back({b, edge.weight});
        dual[b].push_back({a, edge.weight});
    }
    return dual;
}
```

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
