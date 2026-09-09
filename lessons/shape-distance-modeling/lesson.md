# Shape Distance Modeling

Shape Distance Modeling은 점, 선분, 원, 볼록 다각형 사이의 거리와 충돌 문제를 어떤 수학 모델로 바꿀지 정리하는 기하 심화 레슨입니다. Minkowski Sum이나 Rotating Calipers를 바로 구현하기 전에, 어떤 도형을 점으로 줄이고 어떤 도형을 확장할지 결정하는 단계입니다.


polygonDistance2는 구멍 없는 단순 다각형의 내부를 포함한 거리를 구합니다. 한 도형이 다른 도형 안에 있으면 0입니다. 이 실수 baseline의 절대 오차 기준은 좌표 scale에 맞춰야 하며 exact predicate가 아닙니다. SAT의 최소 분리 이동은 포함된 투영에서도 두 끝점까지의 이동량을 비교해야 하므로 단순 교집합 길이가 아닙니다.

## 문제 신호

| 문제 표현 | 모델링 후보 |
| --- | --- |
| 움직이는 물체와 장애물의 충돌 | obstacle + reflected shape |
| 두 convex polygon 사이 최소 거리 | Minkowski difference와 원점 거리 |
| 한 방향으로 가장 먼 점 | support function |
| 선분과 polygon의 최단 거리 | segment distance + intersection |
| 원과 polygon 충돌 | edge distance와 inside 판정 |

거리 문제는 "두 도형의 모든 점쌍"을 직접 보지 않도록 바꾸는 것이 핵심입니다.

## 점, 선분, 다각형의 기본 거리

복잡한 모델을 쓰기 전에는 작은 baseline을 갖고 있어야 합니다. 아래 코드는 점과 선분 거리, polygon 간 segment distance baseline을 계산합니다.

```cpp compile-check
#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>
using namespace std;

struct PointDistance {
    double x = 0;
    double y = 0;
};

PointDistance operator+(PointDistance a, PointDistance b) {
    return {a.x + b.x, a.y + b.y};
}

PointDistance operator-(PointDistance a, PointDistance b) {
    return {a.x - b.x, a.y - b.y};
}

PointDistance operator*(PointDistance a, double scale) {
    return {a.x * scale, a.y * scale};
}

double dotDistance(PointDistance a, PointDistance b) {
    return a.x * b.x + a.y * b.y;
}

double crossDistance(PointDistance a, PointDistance b) {
    return a.x * b.y - a.y * b.x;
}

double norm2(PointDistance a) {
    return dotDistance(a, a);
}

double pointSegmentDistance2(PointDistance p, PointDistance a, PointDistance b) {
    PointDistance ab = b - a;
    double length2 = norm2(ab);
    if (length2 == 0) {
        return norm2(p - a);
    }
    double t = dotDistance(p - a, ab) / length2;
    t = max(0.0, min(1.0, t));
    PointDistance projection = a + ab * t;
    return norm2(p - projection);
}

int sign(double value) {
    const double eps = 1e-10;
    if (value > eps) {
        return 1;
    }
    if (value < -eps) {
        return -1;
    }
    return 0;
}

bool segmentsIntersect(PointDistance a, PointDistance b, PointDistance c, PointDistance d) {
    auto orient = [](PointDistance p, PointDistance q, PointDistance r) {
        return sign(crossDistance(q-p,r-p));
    };
    auto on = [&](PointDistance p, PointDistance q, PointDistance r) {
        return orient(p,q,r)==0 &&
            min(p.x,q.x)-1e-10<=r.x && r.x<=max(p.x,q.x)+1e-10 &&
            min(p.y,q.y)-1e-10<=r.y && r.y<=max(p.y,q.y)+1e-10;
    };
    int u=orient(a,b,c), v=orient(a,b,d), w=orient(c,d,a), z=orient(c,d,b);
    return (u==0 && on(a,b,c)) || (v==0 && on(a,b,d)) ||
           (w==0 && on(c,d,a)) || (z==0 && on(c,d,b)) || (u*v<0 && w*z<0);
}

double segmentDistance2(PointDistance a, PointDistance b, PointDistance c, PointDistance d) {
    if (segmentsIntersect(a, b, c, d)) {
        return 0.0;
    }
    return min(
        min(pointSegmentDistance2(a, c, d), pointSegmentDistance2(b, c, d)),
        min(pointSegmentDistance2(c, a, b), pointSegmentDistance2(d, a, b))
    );
}

bool insideOrBoundary(PointDistance p, const vector<PointDistance>& polygon) {
    bool inside=false;
    for (int i=0,j=(int)polygon.size()-1;i<(int)polygon.size();j=i++) {
        auto a=polygon[j],b=polygon[i];
        if (pointSegmentDistance2(p,a,b)<=1e-20) return true;
        if ((a.y>p.y)!=(b.y>p.y)) {
            double x=a.x+(b.x-a.x)*(p.y-a.y)/(b.y-a.y);
            if (p.x<x) inside=!inside;
        }
    }
    return inside;
}

double polygonDistance2(const vector<PointDistance>& left, const vector<PointDistance>& right) {
    if (left.empty() || right.empty()) return numeric_limits<double>::infinity();
    if (insideOrBoundary(left[0],right) || insideOrBoundary(right[0],left)) return 0;
    double best = numeric_limits<double>::infinity();
    int n = (int)left.size();
    int m = (int)right.size();
    for (int i = 0; i < n; ++i) {
        PointDistance a = left[i];
        PointDistance b = left[(i + 1) % n];
        for (int j = 0; j < m; ++j) {
            PointDistance c = right[j];
            PointDistance d = right[(j + 1) % m];
            best = min(best, segmentDistance2(a, b, c, d));
        }
    }
    return best;
}
```

이 코드는 `O(nm)` baseline입니다. 최적화 구현을 만들 때 작은 입력에서 이 baseline과 비교하면 기하 버그를 빨리 잡을 수 있습니다.

## Minkowski Difference

두 도형 `A`, `B` 사이의 충돌은 아래처럼 볼 수 있습니다.

```text
A intersects B
<=> 0 in A + (-B)
```

거리도 비슷하게 봅니다. `A + (-B)`가 원점을 포함하면 거리는 0이고, 포함하지 않으면 원점에서 이 도형까지의 최단 거리입니다. 두 도형이 convex라면 `A + (-B)`도 convex라서 rotating calipers나 support function으로 빠르게 다룰 수 있습니다.

## Support Function 관점

도형 `P`의 support function은 방향 `dir`에서 가장 큰 dot product입니다.

```text
support(P, dir) = max dot(p, dir)
```

두 도형을 합치면 support가 더해집니다.

```text
support(A + B, dir) = support(A, dir) + support(B, dir)
```

이 식은 collision, separating axis, tangent, width 계산으로 이어집니다. "어떤 방향으로 가장 멀리 있는 점"을 빠르게 찾을 수 있으면 거리 모델링이 쉬워집니다.

## Separating Axis

두 convex polygon이 겹치지 않으면 두 도형을 분리하는 축이 있습니다. 후보 축은 보통 각 polygon edge의 normal입니다.

```text
for each edge normal axis:
  project A onto axis -> [minA, maxA]
  project B onto axis -> [minB, maxB]
  intervals disjoint이면 충돌하지 않음
```

최소 이동 거리나 penetration depth가 필요한 문제에서는 각 축에서 두 투영 구간을 분리하는 최소 이동량을 비교합니다. 포함 관계에서도 `min(maxA-minB, maxB-minA)`를 사용하고, 단순 교집합 길이로 대체하지 않습니다. 정수 좌표라면 projection 비교를 dot product로 하고, 실제 거리에는 axis length 정규화가 필요합니다.

## 어떤 모델을 고를까

| 상황 | 우선 모델 |
| --- | --- |
| 입력이 작은 일반 polygon | segment distance baseline |
| convex polygon 충돌만 필요 | separating axis 또는 Minkowski containment |
| convex polygon 거리 | Minkowski difference + point to convex distance |
| 원이 섞임 | radius만큼 polygon 확장 또는 edge distance |
| 움직이는 rigid shape | reflected shape로 obstacle 확장 |

모델을 고른 뒤에 최적화를 붙입니다. 처음부터 calipers를 쓰면 inside/intersection case를 놓치기 쉽습니다.

## 작은 예시

```text
A: unit square at [0,1] x [0,1]
B: unit square at [3,4] x [0,1]

B를 -B로 반사해 A + (-B)를 만들면
원점은 포함되지 않는다.
원점까지의 최단 거리는 x 방향 2이다.
따라서 두 square 사이 거리는 2이다.
```

도형 하나를 움직이는 문제라면, 움직이는 도형을 반사해 장애물에 더하고 움직이는 점의 경로와 충돌하는지 보면 됩니다.

## 시간 복잡도

| 방식 | 복잡도 |
| --- | ---: |
| 모든 segment pair baseline | `O(nm)` |
| convex polygon Minkowski sum | `O(n + m)` |
| separating axis naive projection | `O((n + m)^2)` |
| rotating calipers 기반 distance | `O(n + m)` |
| point to convex polygon query | 전처리에 따라 `O(log n)` 가능 |

대회에서는 입력 크기가 작으면 baseline이 더 안전합니다. 큰 convex 입력에서만 calipers와 support 최적화가 필요합니다.
