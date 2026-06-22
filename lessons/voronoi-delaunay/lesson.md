# Voronoi와 Delaunay

Voronoi Diagram과 Delaunay Triangulation은 평면의 점 집합에서 "가장 가까운 점" 구조를 다루는 쌍대 개념입니다. 구현 난도는 높지만, 문제에서 어떤 성질을 써야 하는지 알면 closest pair, nearest neighbor, Euclidean MST를 더 구조적으로 볼 수 있습니다.

이 레슨은 Line Arrangement와 Closest Pair Sweep 이후에 보는 고급 계산기하 관점입니다.

1. Voronoi cell은 한 점이 가장 가까운 영역이다.
2. Delaunay edge는 두 Voronoi cell이 이웃할 때 생긴다.
3. empty circumcircle 성질로 Delaunay triangle을 판정한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: CCW, 거리, 원, Line Arrangement, Closest Pair
- 함께 보면 좋은 레슨: 기하 기본, Closest Pair Sweep, Line Arrangement
- 다음에 볼 레슨: half-plane intersection, randomized incremental geometry, planar graph duality

## 1. 문제 신호

| 문제 표현 | 관점 |
| --- | --- |
| 각 위치에서 가장 가까운 site | Voronoi diagram |
| nearest neighbor graph의 후보를 줄이기 | Delaunay triangulation |
| Euclidean MST 후보 edge | Delaunay edge 포함 |
| 세 점의 외접원 안에 다른 점이 없는가 | Delaunay predicate |
| 평면 subdivision과 nearest region | Voronoi cell |

대부분의 대회에서는 Voronoi/Delaunay를 직접 구현하기보다, 성질을 이용해 후보를 줄이거나 특수 조건에서 우회합니다.

## 2. 쌍대 관계

Voronoi Diagram은 점마다 가장 가까운 영역을 나눕니다. Delaunay Triangulation은 Voronoi cell이 변을 공유하는 점들을 간선으로 연결합니다.

```text
Voronoi vertex  <->  Delaunay triangle
Voronoi edge    <->  Delaunay edge
Voronoi cell    <->  input point
```

이 관계 때문에 nearest 구조 문제는 Delaunay graph 위의 sparse graph 문제로 바뀔 수 있습니다.

## 3. Empty Circumcircle

세 점 `a, b, c`가 Delaunay triangle이 되려면, 그 외접원 내부에 다른 점이 없어야 합니다.

```text
no point p lies strictly inside circumcircle(a, b, c)
```

이 조건은 determinant로 판정할 수 있습니다. 아래 코드는 `a,b,c`가 반시계 방향일 때 `p`가 외접원 내부에 있으면 양수를 반환합니다.

```cpp compile-check
#include <cmath>
using namespace std;

struct Point2D {
    long double x;
    long double y;
};

long double orient(const Point2D& a, const Point2D& b, const Point2D& c) {
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

long double inCircleValue(Point2D a, Point2D b, Point2D c, Point2D p) {
    long double ax = a.x - p.x;
    long double ay = a.y - p.y;
    long double bx = b.x - p.x;
    long double by = b.y - p.y;
    long double cx = c.x - p.x;
    long double cy = c.y - p.y;

    long double det =
        (ax * ax + ay * ay) * (bx * cy - by * cx)
      - (bx * bx + by * by) * (ax * cy - ay * cx)
      + (cx * cx + cy * cy) * (ax * by - ay * bx);

    if (orient(a, b, c) < 0) {
        det = -det;
    }
    return det;
}

bool strictlyInsideCircumcircle(Point2D a, Point2D b, Point2D c, Point2D p) {
    const long double EPS = 1e-18L;
    return inCircleValue(a, b, c, p) > EPS;
}
```

정수 좌표가 작으면 `__int128` determinant로 exact predicate를 만들 수 있습니다. 실수 좌표에서는 EPS와 degeneracy가 어렵습니다.

## 4. Delaunay와 Euclidean MST

Euclidean MST의 모든 간선은 Delaunay triangulation의 간선에 포함됩니다.

```text
EMST edges ⊆ Delaunay edges
```

따라서 Delaunay graph를 만들 수 있으면, 그 위에서 Kruskal을 돌려 Euclidean MST를 구할 수 있습니다. 다만 Delaunay triangulation 구현 자체가 쉽지 않으므로, 제약이 작으면 모든 간선 또는 grid/sweep 최적화를 먼저 검토합니다.

## 5. Voronoi Cell의 반평면

한 site `p`의 Voronoi cell은 다른 모든 site `q`에 대해 `p`가 `q`보다 가까운 반평면의 교집합입니다.

```text
dist(x, p) <= dist(x, q)
```

전개하면 두 점의 수직이등분선이 만들고, `p` 쪽 반평면을 취합니다. 그래서 Voronoi cell 하나는 half-plane intersection으로도 구할 수 있습니다.

## 6. 구현 전략

| 목표 | 현실적인 접근 |
| --- | --- |
| 점 수 작음 | 모든 pair/triangle 검사 |
| closest pair만 필요 | sweep 또는 divide-and-conquer |
| EMST | 가능한 후보 edge 축소 후 Kruskal |
| 전체 Delaunay 필요 | 검증된 library 또는 randomized incremental |
| 한 cell만 필요 | half-plane intersection |

Voronoi/Delaunay 전체 구현은 degenerate case가 많습니다. 온라인 저지에서는 입력이 일반 위치인지, 같은 원 위 네 점이 가능한지 반드시 봅니다.

## 7. Degeneracy

| 상황 | 문제 |
| --- | --- |
| 같은 점 중복 | nearest region이 불명확 |
| 세 점 collinear | 외접원이 없음 |
| 네 점 cocircular | Delaunay triangulation이 유일하지 않음 |
| 매우 가까운 실수 좌표 | predicate 오차 |
| bounding box 없는 Voronoi | 무한 cell 존재 |

문제에서 "no three collinear", "no four cocircular" 같은 조건이 있으면 구현이 크게 단순해집니다.

## 8. 시간 복잡도

| 작업 | 대표 시간 |
| --- | ---: |
| 모든 pair 거리 | `O(N^2)` |
| closest pair sweep | `O(N log N)` |
| Delaunay triangulation | `O(N log N)` expected/typical |
| Voronoi cell 하나 via HPI | `O(N log N)` |
| 모든 triangle empty circle brute force | `O(N^4)` |

직접 Delaunay를 구현하는 대신 문제의 제약에 맞는 더 단순한 구조가 있는지 먼저 찾습니다.

## 9. 자주 하는 실수

1. Delaunay triangulation이 항상 유일하다고 가정한다.
2. cocircular case에서 edge 선택이 달라져도 되는지 확인하지 않는다.
3. Voronoi cell이 무한할 수 있다는 점을 잊는다.
4. in-circle predicate에서 orientation 부호를 보정하지 않는다.
5. Euclidean MST 후보를 Delaunay가 아니라 nearest neighbor 한 개로만 줄인다.

## 10. 문제를 볼 때 체크할 조건

- 전체 diagram/triangulation이 필요한가, 성질만 필요한가?
- 입력이 general position을 보장하는가?
- 좌표가 정수인가 실수인가?
- 무한 Voronoi cell 처리가 필요한가?
- 목표가 nearest query, MST, area, adjacency 중 무엇인가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: circumcircle 판정 `/practice/...` 문제 필요 | in-circle determinant 구현 | Delaunay predicate |
| 표준 | TODO: Voronoi cell 반평면 `/practice/...` 문제 필요 | 수직이등분선과 HPI 모델링 | Voronoi cell |
| 응용 | TODO: Euclidean MST 후보 축소 `/practice/...` 문제 필요 | Delaunay edge 성질 활용 | EMST |
| 함정 | TODO: cocircular points `/practice/...` 문제 필요 | triangulation non-unique 처리 | degeneracy |
