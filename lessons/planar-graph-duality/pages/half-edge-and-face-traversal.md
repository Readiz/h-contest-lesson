# Half-edge and Face Traversal

좌표와 간선만 주어진 planar graph에서 dual graph를 만들려면 먼저 face를 찾아야 합니다. 가장 안정적인 방법은 무향 간선을 양방향 half-edge로 쪼개고, 각 정점의 outgoing half-edge를 polar angle 순서로 정렬한 뒤, 아직 방문하지 않은 half-edge를 따라 face를 순회하는 것입니다.

## 1. Half-edge 구조

무향 edge `(u, v)` 하나는 두 directed half-edge `u -> v`, `v -> u`가 됩니다. 각 half-edge는 반대 방향 half-edge와 같은 primal edge id를 공유합니다.

```text
half h:     u -> v
opposite:  v -> u
left face: h를 따라갈 때 왼쪽에 있는 face
```

face traversal은 각 half-edge의 left face를 한 번씩 채우는 과정입니다.

## 2. 다음 half-edge 고르기

각 정점의 outgoing half-edge를 angle 오름차순으로 정렬합니다. 현재 half-edge가 `u -> v`라면, `v`에 도착한 뒤 `v -> u`의 정렬 위치를 찾고 그 바로 이전 half-edge를 다음으로 택합니다. 이 규칙은 현재 방향의 왼쪽 face를 따라가게 합니다.

```text
next(u -> v) = outgoing[v][position(v -> u) - 1]
```

인덱스는 cyclic하게 돌립니다.

## 3. 구현

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
    double angle = 0.0;
};

struct FaceEmbedding {
    vector<HalfEdge> halfEdges;
    vector<vector<int>> faceHalfEdges;
    vector<int> faceOfHalfEdge;
    vector<long long> signedDoubleArea;
    int outerFace = -1;
};

long long cross(const Point& a, const Point& b) {
    return a.x * b.y - a.y * b.x;
}

FaceEmbedding buildFaceEmbedding(
    const vector<Point>& points,
    const vector<InputEdge>& edges
) {
    int n = (int)points.size();
    vector<HalfEdge> halfEdges;
    vector<vector<int>> outgoing(n);

    for (int edgeId = 0; edgeId < (int)edges.size(); ++edgeId) {
        int u = edges[edgeId].u;
        int v = edges[edgeId].v;
        int first = (int)halfEdges.size();
        int second = first + 1;

        double angleUV = atan2(
            (double)(points[v].y - points[u].y),
            (double)(points[v].x - points[u].x)
        );
        double angleVU = atan2(
            (double)(points[u].y - points[v].y),
            (double)(points[u].x - points[v].x)
        );

        halfEdges.push_back({u, v, edgeId, second, angleUV});
        halfEdges.push_back({v, u, edgeId, first, angleVU});
        outgoing[u].push_back(first);
        outgoing[v].push_back(second);
    }

    vector<int> position(halfEdges.size(), -1);
    for (int v = 0; v < n; ++v) {
        sort(outgoing[v].begin(), outgoing[v].end(), [&](int a, int b) {
            if (halfEdges[a].angle != halfEdges[b].angle) {
                return halfEdges[a].angle < halfEdges[b].angle;
            }
            return halfEdges[a].to < halfEdges[b].to;
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
        long long area = 0;
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

## 4. Outer Face 식별

위 순회 규칙에서는 내부 face가 보통 양의 signed area를 가지고, outer face는 음의 signed area를 갖습니다. 따라서 signed area가 가장 작은 face를 outer face로 잡을 수 있습니다.

```text
outerFace = argmin signedDoubleArea[face]
```

bridge만 있는 tree처럼 면적이 모두 0에 가까운 입력은 dual shortest path 문제로 바로 쓰기 어렵습니다. 이 경우 face가 사실상 outer 하나이고, bridge edge 양쪽 face가 같아지는 self-loop 상황을 별도로 처리해야 합니다.

## 5. Euler 검증

연결 성분 수가 `C`인 planar embedding에서는 아래가 성립합니다.

```text
V - E + F = 1 + C
```

이 식이 맞지 않으면 보통 다음 중 하나입니다.

- 간선이 실제로 교차한다.
- 정점별 angle 정렬 tie가 embedding과 다르다.
- half-edge를 양방향으로 만들지 않았다.
- next half-edge를 이전이 아니라 다음으로 잡아 좌우 face가 뒤집혔다.
- 입력이 겹치는 multi-edge를 포함해 좌표만으로 rotation order를 알 수 없다.

## 6. Bridge와 Multi-edge 정책

Bridge는 양쪽 half-edge가 같은 face를 가리킬 수 있습니다. dual graph에서는 self-loop가 되며, shortest path나 cut 변환에서는 보통 유용하지 않아 무시할 수 있지만, 문제 조건에 따라 비용 있는 loop를 보존해야 할 수도 있습니다.

Multi-edge는 두 종류로 나눕니다.

- 서로 다른 곡선이나 embedding 순서가 주어진 multi-edge: rotation order를 입력으로 받아 처리합니다.
- 같은 두 좌표를 잇는 겹친 straight segment: 좌표만으로 face를 복원할 수 없으므로 이 구현의 전제 밖입니다.
