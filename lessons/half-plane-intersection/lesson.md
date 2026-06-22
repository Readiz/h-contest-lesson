# Half-Plane Intersection

Half-Plane Intersection은 여러 반평면의 공통 영역을 구하는 계산기하 기법입니다. Convex polygon clipping의 일반화로 볼 수 있고, Voronoi cell, 선형 제약, convex feasibility 문제에서 자주 등장합니다.

이 레슨은 CCW, 선분 교차, Line Arrangement, Voronoi/Delaunay 이후에 보는 기하 심화입니다.

1. 각 반평면을 방향 있는 직선의 왼쪽 영역으로 표현한다.
2. 직선을 각도순으로 정렬한다.
3. deque에 후보 반평면을 유지하면서 뒤/앞의 불필요한 교점을 제거한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: cross product, line intersection, convex polygon, 각도 정렬
- 함께 보면 좋은 레슨: 기하 기본, Line Arrangement, Voronoi와 Delaunay
- 다음에 볼 레슨: Minkowski sum, convex optimization, Voronoi cell clipping

## 1. 문제 신호

| 문제 표현 | Half-Plane 관점 |
| --- | --- |
| 여러 선형 부등식의 공통 영역 | half-plane intersection |
| convex polygon을 직선으로 계속 자른다 | polygon clipping |
| 한 점이 모든 왼쪽/오른쪽 조건을 만족해야 한다 | feasibility |
| Voronoi cell 하나를 구한다 | 수직이등분선 half-plane |
| convex polygon의 kernel | visibility half-planes |

공통 영역이 볼록하다는 점이 핵심입니다. 입력이 비볼록 polygon이면 먼저 어떤 반평면 집합으로 표현되는지 확인해야 합니다.

## 2. 반평면 표현

직선은 한 점 `p`와 방향 벡터 `v`로 표현합니다. 반평면은 이 방향으로 바라볼 때 왼쪽입니다.

```text
inside(line, q) <=> cross(v, q - p) >= 0
```

오른쪽 영역을 쓰고 싶으면 방향 벡터를 반대로 뒤집으면 됩니다.

## 3. Deque 알고리즘

1. 모든 반평면을 angle 기준으로 정렬한다.
2. 같은 angle의 평행 반평면은 더 안쪽 제약만 남긴다.
3. 새 반평면을 넣기 전에 뒤쪽 교점이 새 반평면 밖이면 뒤 반평면을 제거한다.
4. 앞쪽 교점도 새 반평면 밖이면 앞 반평면을 제거한다.
5. 마지막에 앞/뒤가 서로를 위반하는지 정리하고 polygon을 만든다.

## 4. 구현

아래 구현은 bounded polygon을 반환합니다. 무한 영역까지 다루려면 충분히 큰 bounding box 반평면을 함께 넣는 방식이 실전에서 자주 쓰입니다.

```cpp compile-check
#include <algorithm>
#include <cmath>
#include <deque>
#include <vector>
using namespace std;

const double EPS_HALF_PLANE = 1e-10;

struct PointHalfPlane {
    double x = 0;
    double y = 0;

    PointHalfPlane() = default;
    PointHalfPlane(double xValue, double yValue) : x(xValue), y(yValue) {}

    PointHalfPlane operator+(const PointHalfPlane& other) const {
        return {x + other.x, y + other.y};
    }

    PointHalfPlane operator-(const PointHalfPlane& other) const {
        return {x - other.x, y - other.y};
    }

    PointHalfPlane operator*(double scalar) const {
        return {x * scalar, y * scalar};
    }
};

double crossHalfPlane(PointHalfPlane a, PointHalfPlane b) {
    return a.x * b.y - a.y * b.x;
}

struct HalfPlaneLine {
    PointHalfPlane p;
    PointHalfPlane v;
    double angle = 0;

    HalfPlaneLine() = default;
    HalfPlaneLine(PointHalfPlane point, PointHalfPlane direction)
        : p(point), v(direction), angle(atan2(direction.y, direction.x)) {}
};

bool parallelHalfPlane(const HalfPlaneLine& a, const HalfPlaneLine& b) {
    return fabs(crossHalfPlane(a.v, b.v)) < EPS_HALF_PLANE;
}

bool outsideHalfPlane(const HalfPlaneLine& line, PointHalfPlane point) {
    return crossHalfPlane(line.v, point - line.p) < -EPS_HALF_PLANE;
}

PointHalfPlane intersectionHalfPlane(const HalfPlaneLine& a, const HalfPlaneLine& b) {
    PointHalfPlane diff = b.p - a.p;
    double t = crossHalfPlane(diff, b.v) / crossHalfPlane(a.v, b.v);
    return a.p + a.v * t;
}

vector<PointHalfPlane> halfPlaneIntersection(vector<HalfPlaneLine> lines) {
    sort(lines.begin(), lines.end(), [](const HalfPlaneLine& a, const HalfPlaneLine& b) {
        if (fabs(a.angle - b.angle) > EPS_HALF_PLANE) {
            return a.angle < b.angle;
        }
        return crossHalfPlane(a.v, b.p - a.p) < 0;
    });

    vector<HalfPlaneLine> uniqueLines;
    for (const auto& line : lines) {
        if (!uniqueLines.empty() && parallelHalfPlane(uniqueLines.back(), line)) {
            if (outsideHalfPlane(line, uniqueLines.back().p)) {
                uniqueLines.back() = line;
            }
        } else {
            uniqueLines.push_back(line);
        }
    }

    deque<HalfPlaneLine> dequeLines;
    deque<PointHalfPlane> intersections;

    for (const auto& line : uniqueLines) {
        while (!intersections.empty() && outsideHalfPlane(line, intersections.back())) {
            intersections.pop_back();
            dequeLines.pop_back();
        }
        while (!intersections.empty() && outsideHalfPlane(line, intersections.front())) {
            intersections.pop_front();
            dequeLines.pop_front();
        }

        if (!dequeLines.empty()) {
            if (parallelHalfPlane(dequeLines.back(), line)) {
                if (outsideHalfPlane(line, dequeLines.back().p)) {
                    dequeLines.back() = line;
                }
                continue;
            }
            intersections.push_back(intersectionHalfPlane(dequeLines.back(), line));
        }
        dequeLines.push_back(line);
    }

    while (!intersections.empty() && outsideHalfPlane(dequeLines.front(), intersections.back())) {
        intersections.pop_back();
        dequeLines.pop_back();
    }
    while (!intersections.empty() && outsideHalfPlane(dequeLines.back(), intersections.front())) {
        intersections.pop_front();
        dequeLines.pop_front();
    }

    if (dequeLines.size() < 3) {
        return {};
    }

    intersections.push_back(intersectionHalfPlane(dequeLines.back(), dequeLines.front()));
    return vector<PointHalfPlane>(intersections.begin(), intersections.end());
}
```

## 5. Bounding Box

반평면들의 교집합이 무한 영역이면 polygon 꼭짓점을 유한 개로 반환하기 어렵습니다. 실전에서는 좌표 범위가 정해져 있으면 큰 사각형을 먼저 넣습니다.

```text
-B <= x <= B
-B <= y <= B
```

그 뒤 원래 반평면을 추가하면 bounded polygon으로 계산할 수 있습니다.

## 6. Polygon Clipping과 비교

| 방법 | 특징 |
| --- | --- |
| Sutherland-Hodgman clipping | 현재 polygon을 반평면 하나로 자름, `O(NM)` |
| Half-plane intersection deque | 모든 직선을 각도순으로 처리, `O(N log N)` |
| Linear programming in 2D | 최적화 목적식이 있을 때 사용 |

제약 수가 작거나 이미 polygon이 작다면 clipping이 더 단순합니다. 일반 반평면 집합이 크면 deque 알고리즘이 낫습니다.

## 7. Voronoi Cell과 연결

점 `p_i`의 Voronoi cell은 다른 모든 점 `p_j`에 대해 아래 조건의 교집합입니다.

```text
dist(x, p_i) <= dist(x, p_j)
```

이 식은 두 점의 수직이등분선으로 만들어지는 반평면입니다. 따라서 특정 점 하나의 Voronoi cell은 half-plane intersection으로 구할 수 있습니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| angle sort | `O(N log N)` |
| deque 처리 | `O(N)` |
| bounded polygon 반환 | 꼭짓점 수에 비례 |

## 9. 자주 하는 실수

1. 반평면 방향을 오른쪽/왼쪽으로 섞는다.
2. 평행 직선 중 더 안쪽 제약을 남기지 않는다.
3. 무한 교집합인데 polygon으로 바로 반환하려 한다.
4. EPS가 너무 커서 얇은 영역을 지운다.
5. 같은 angle 정렬 tie-break를 반대로 둔다.

## 10. 문제를 볼 때 체크할 조건

- 제약이 모두 선형 반평면인가?
- 반환해야 하는 것이 존재 여부인가, 면적인가, 꼭짓점인가?
- 영역이 무한할 수 있는가?
- 좌표가 정수여도 교점은 실수가 되는가?
- convex polygon clipping으로 충분한가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: convex polygon clipping `/practice/...` 문제 필요 | 한 반평면씩 polygon 자르기 | clipping |
| 표준 | TODO: half-plane intersection `/practice/...` 문제 필요 | angle sort와 deque 구현 | HPI |
| 응용 | TODO: Voronoi cell area `/practice/...` 문제 필요 | 수직이등분선 반평면 구성 | Voronoi cell |
| 함정 | TODO: unbounded feasible region `/practice/...` 문제 필요 | bounding box 처리 | unbounded |
