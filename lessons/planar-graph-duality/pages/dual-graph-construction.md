# Dual Graph Construction

Dual Graph Construction은 평면에 교차 없이 그린 그래프에서 face를 정점으로 바꿔 dual graph를 만드는 단계입니다. 기하처럼 보이는 planar embedding 문제와 그래프 min-cut, shortest path 문제가 서로 바뀔 수 있습니다.

이 페이지는 Matrix-Tree Theorem Applications, Geometry CCW, Max Flow Min Cut 이후에 보는 그래프/기하 연결 심화입니다.

1. planar embedding에서 edge 양쪽의 face를 알아낸다.
2. primal edge마다 dual edge를 만든다.
3. primal cut, cycle, path 조건이 dual에서 무엇이 되는지 바꿔 본다.

## 문제 신호

| 문제 표현 | Duality 관점 |
| --- | --- |
| planar graph와 face 정보가 주어진다 | dual graph 구성 |
| 영역을 가르는 최소 비용 선을 찾는다 | primal cut 또는 dual shortest path |
| cycle로 두 점/face를 분리한다 | dual path |
| planar embedding이 고정되어 있다 | edge 양쪽 face가 의미 있음 |
| `V - E + F = 2` 검증이 가능하다 | Euler formula sanity check |

단순히 정점 좌표가 있다고 planar dual을 만들 수 있는 것은 아닙니다. 어떤 edge가 어떤 face를 경계로 가지는지 알아야 합니다.

## Dual Graph 만들기

primal graph의 face 하나를 dual graph의 정점 하나로 둡니다. primal edge `e`가 face `a`와 face `b` 사이의 경계라면 dual edge `(a, b)`를 만듭니다.

```text
primal edge e separates face left(e), right(e)
dual edge e* connects left(e) and right(e)
```

outer face도 하나의 face입니다. 외부와 내부를 구분해야 하는 문제에서는 outer face의 번호를 특별히 관리합니다.

## Cut-Cycle 대응

평면 그래프에서 중요한 대응은 아래와 같습니다.

| Primal | Dual |
| --- | --- |
| cycle | cut |
| cut | cycle |
| s-t cut | s와 t가 있는 face를 분리하는 dual cycle/path |
| face adjacency | dual edge |

예를 들어 어떤 장애물을 피해 boundary를 자르는 최소 비용을 묻는 문제가 dual shortest path로 바뀌는 경우가 있습니다. primal에서 "막아야 하는 edge 집합"이 dual에서는 "연결해야 하는 path"가 됩니다.

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

## Embedding이 주어졌을 때의 구성 골격

대회 문제에서 이미 각 directed half-edge의 왼쪽 face가 주어졌다면 dual graph는 단순히 edge 양쪽 face를 연결하면 됩니다.

```cpp
struct EdgeFace {
    int u = 0;
    int v = 0;
    int leftFaceUV = 0;
    int leftFaceVU = 0;
    int weight = 0;
};

vector<vector<pair<int, int>>> buildDualGraph(
    int faceCount,
    const vector<EdgeFace>& edges
) {
    vector<vector<pair<int, int>>> dual(faceCount);
    for (const EdgeFace& edge : edges) {
        int a = edge.leftFaceUV;
        int b = edge.leftFaceVU;
        dual[a].push_back({b, edge.weight});
        dual[b].push_back({a, edge.weight});
    }
    return dual;
}
```

문제에서 face 정보가 없고 좌표만 있다면, 각 정점의 incident edge를 polar angle로 정렬하고 half-edge traversal로 face를 찾아야 합니다. 이 단계가 구현의 대부분입니다.

좌표만 있는 입력의 최소 구현 순서는 아래처럼 분리해 두는 편이 안전합니다.

1. 무향 간선 하나를 양방향 half-edge 두 개로 만든다.
2. 각 정점의 outgoing half-edge를 polar angle 순서로 정렬한다.
3. 아직 방문하지 않은 half-edge에서 시작해, 반대 방향으로 건너간 뒤 정렬 순서에서 다음 왼쪽 회전 edge를 고른다.
4. 시작 half-edge로 돌아올 때까지 반복해 face 하나를 기록한다.
5. 모든 half-edge를 한 번씩 방문했는지, `V - E + F` 검증이 맞는지 확인한 뒤 dual graph를 만든다.

## Euler Formula로 검증

연결 planar graph라면 아래가 성립합니다.

```text
V - E + F = 2
```

연결 성분이 여러 개면 식이 바뀝니다. face traversal을 직접 구현했다면, face count가 이 식과 맞는지 먼저 확인해야 합니다.

```text
connected components = C
V - E + F = 1 + C
```

outer face를 빼먹거나 edge 방향을 한 번만 방문하면 이 검증에서 바로 드러납니다.

## Min-Cut과 Shortest Path

planar graph의 특정 형태에서는 min cut이 dual shortest path로 바뀝니다. 예를 들어 source와 sink가 outer boundary 위에 있고, 이 둘을 분리하는 cut을 찾는 문제는 dual에서 두 boundary arc 사이를 잇는 최단 경로로 해석할 수 있습니다.

```text
primal edge cost = cut cost
dual edge cost = same cost
minimum separating cut = shortest dual path
```

모든 max-flow가 이렇게 단순히 바뀌지는 않습니다. source/sink 위치, directed edge, capacity 방향, embedding 조건을 확인해야 합니다.

## 자주 하는 실수

1. 좌표가 있다는 이유만으로 embedding을 고정됐다고 가정한다.
2. outer face를 dual 정점에서 빼 버린다.
3. primal edge의 양쪽 face가 같은 bridge edge를 일반 edge처럼 처리한다.
4. directed graph에서 dual edge 방향을 무시한다.
5. cut과 cycle 대응을 반대로 적용한다.
6. face traversal 후 Euler formula 검증을 하지 않는다.
