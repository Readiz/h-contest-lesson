# Shape Distance Modeling

Shape Distance Modeling은 점, 선분, 원, 볼록 다각형 사이의 거리와 충돌 문제를 어떤 수학 모델로 바꿀지 정리하는 기하 심화 레슨입니다. Minkowski Sum이나 Rotating Calipers를 바로 구현하기 전에, 어떤 도형을 점으로 줄이고 어떤 도형을 확장할지 결정하는 단계입니다.

이 레슨은 Minkowski Sum, Rotating Calipers Applications 이후에 보는 계산기하 심화입니다.

1. 두 도형 사이 거리를 원점과 Minkowski difference의 거리로 바꾼다.
2. 볼록 도형은 support function과 tangent 방향으로 본다.
3. 일반 polygon은 segment distance baseline으로 검증한 뒤 최적화를 붙인다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: CCW, dot product, segment intersection, convex hull, Minkowski Sum
- 함께 보면 좋은 레슨: Minkowski Sum, Rotating Calipers Applications, Sweep Line Geometry
- 다음에 볼 레슨: circle geometry, configuration space, separating axis theorem

## 1. 문제 신호

| 문제 표현 | 모델링 후보 |
| --- | --- |
| 움직이는 물체와 장애물의 충돌 | obstacle + reflected shape |
| 두 convex polygon 사이 최소 거리 | Minkowski difference와 원점 거리 |
| 한 방향으로 가장 먼 점 | support function |
| 선분과 polygon의 최단 거리 | segment distance + intersection |
| 원과 polygon 충돌 | edge distance와 inside 판정 |

거리 문제는 "두 도형의 모든 점쌍"을 직접 보지 않도록 바꾸는 것이 핵심입니다.

## 2. 점, 선분, 다각형의 기본 거리

복잡한 모델을 쓰기 전에는 작은 baseline을 갖고 있어야 합니다. 아래 코드는 점과 선분 거리, polygon 간 segment distance baseline을 계산합니다.

```cpp compile-check
#include <algorithm>
#include <cmath>
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
        return sign(crossDistance(q - p, r - p));
    };
    int abC = orient(a, b, c);
    int abD = orient(a, b, d);
    int cdA = orient(c, d, a);
    int cdB = orient(c, d, b);
    if (abC == 0 && abD == 0) {
        auto overlap = [](double l1, double r1, double l2, double r2) {
            if (l1 > r1) {
                swap(l1, r1);
            }
            if (l2 > r2) {
                swap(l2, r2);
            }
            return max(l1, l2) <= min(r1, r2) + 1e-10;
        };
        return overlap(a.x, b.x, c.x, d.x) && overlap(a.y, b.y, c.y, d.y);
    }
    return abC * abD <= 0 && cdA * cdB <= 0;
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

double polygonDistance2(const vector<PointDistance>& left, const vector<PointDistance>& right) {
    double best = 1e100;
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

## 3. Minkowski Difference

두 도형 `A`, `B` 사이의 충돌은 아래처럼 볼 수 있습니다.

```text
A intersects B
<=> 0 in A + (-B)
```

거리도 비슷하게 봅니다. `A + (-B)`가 원점을 포함하면 거리는 0이고, 포함하지 않으면 원점에서 이 도형까지의 최단 거리입니다. 두 도형이 convex라면 `A + (-B)`도 convex라서 rotating calipers나 support function으로 빠르게 다룰 수 있습니다.

## 4. Support Function 관점

도형 `P`의 support function은 방향 `dir`에서 가장 큰 dot product입니다.

```text
support(P, dir) = max dot(p, dir)
```

두 도형을 합치면 support가 더해집니다.

```text
support(A + B, dir) = support(A, dir) + support(B, dir)
```

이 식은 collision, separating axis, tangent, width 계산으로 이어집니다. "어떤 방향으로 가장 멀리 있는 점"을 빠르게 찾을 수 있으면 거리 모델링이 쉬워집니다.

## 5. Separating Axis

두 convex polygon이 겹치지 않으면 두 도형을 분리하는 축이 있습니다. 후보 축은 보통 각 polygon edge의 normal입니다.

```text
for each edge normal axis:
  project A onto axis -> [minA, maxA]
  project B onto axis -> [minB, maxB]
  intervals disjoint이면 충돌하지 않음
```

최소 이동 거리나 penetration depth가 필요한 문제에서는 가장 작은 overlap 축을 기록합니다. 정수 좌표라면 projection 비교를 dot product로 하고, 실제 거리에는 axis length 정규화가 필요합니다.

## 6. 어떤 모델을 고를까

| 상황 | 우선 모델 |
| --- | --- |
| 입력이 작은 일반 polygon | segment distance baseline |
| convex polygon 충돌만 필요 | separating axis 또는 Minkowski containment |
| convex polygon 거리 | Minkowski difference + point to convex distance |
| 원이 섞임 | radius만큼 polygon 확장 또는 edge distance |
| 움직이는 rigid shape | reflected shape로 obstacle 확장 |

모델을 고른 뒤에 최적화를 붙입니다. 처음부터 calipers를 쓰면 inside/intersection case를 놓치기 쉽습니다.

## 7. 작은 예시

```text
A: unit square at [0,1] x [0,1]
B: unit square at [3,4] x [0,1]

B를 -B로 반사해 A + (-B)를 만들면
원점은 포함되지 않는다.
원점까지의 최단 거리는 x 방향 2이다.
따라서 두 square 사이 거리는 2이다.
```

도형 하나를 움직이는 문제라면, 움직이는 도형을 반사해 장애물에 더하고 움직이는 점의 경로와 충돌하는지 보면 됩니다.

## 8. 시간 복잡도

| 방식 | 복잡도 |
| --- | ---: |
| 모든 segment pair baseline | `O(nm)` |
| convex polygon Minkowski sum | `O(n + m)` |
| separating axis naive projection | `O((n + m)^2)` |
| rotating calipers 기반 distance | `O(n + m)` |
| point to convex polygon query | 전처리에 따라 `O(log n)` 가능 |

대회에서는 입력 크기가 작으면 baseline이 더 안전합니다. 큰 convex 입력에서만 calipers와 support 최적화가 필요합니다.

## 9. 자주 하는 실수

1. polygon이 convex인지 확인하지 않고 convex 전용 모델을 쓴다.
2. 충돌하면 거리 0이라는 case를 baseline보다 뒤에 처리한다.
3. edge normal projection에서 axis 길이 정규화를 빼고 실제 거리로 출력한다.
4. Minkowski difference에서 `A + B`를 만들고 `-B` 반사를 빼먹는다.
5. 접하는 경우를 겹침으로 볼지 분리로 볼지 문제 조건을 확인하지 않는다.
6. 실수 EPS를 너무 크게 잡아 작은 간격을 0으로 만든다.

## 10. 문제를 볼 때 체크할 조건

- 도형이 convex인지 일반 polygon인지 명확한가?
- 충돌 판정인지 실제 거리 출력인지 구분했는가?
- 움직이는 도형을 반사해서 장애물을 확장할 수 있는가?
- support function이나 separating axis가 필요한가?
- 작은 입력 baseline으로 최적화 구현을 검증할 수 있는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: point segment distance `/practice/...` 문제 필요 | projection과 clamp 구현 | dot product |
| 표준 | TODO: convex collision `/practice/...` 문제 필요 | separating axis 판정 | projection interval |
| 응용 | TODO: moving shape distance `/practice/...` 문제 필요 | reflected shape 모델링 | Minkowski difference |
| 함정 | TODO: touching polygons `/practice/...` 문제 필요 | 접점과 EPS 정책 확인 | zero distance |
