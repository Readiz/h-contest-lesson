# Circle Geometry

Circle Geometry는 점, 직선, 원 사이의 거리와 교점을 계산하고 tangent construction으로 이어지는 계산기하 레슨입니다. Segment intersection이나 convex polygon보다 실수 오차와 case 분기가 더 자주 등장하므로, 공식을 쓰기 전에 어떤 기하 관계를 판정하는지 분리해야 합니다.

이 레슨은 Shape Distance Modeling과 기본 CCW/거리 계산 이후에 보는 기하 심화입니다.

1. 원과 점/직선/원 사이의 거리 관계를 먼저 판정한다.
2. 교점 좌표는 projection과 수직 방향 벡터로 만든다.
3. tangent와 intersection은 EPS 정책을 명확히 한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: dot product, cross product, point-line distance, Shape Distance Modeling
- 함께 보면 좋은 레슨: Geometry CCW와 Segment Intersection, Closest Pair Sweep, Voronoi와 Delaunay
- 다음에 볼 레슨: circle arrangement, inversion geometry, robust predicates

## 1. 문제 신호

| 문제 표현 | Circle Geometry 관점 |
| --- | --- |
| 원과 직선의 교점 | projection + perpendicular offset |
| 두 원의 교점 | center line 위 base point + perpendicular |
| 한 점에서 원에 그은 접선 | right triangle |
| 두 원의 공통 접선 | radius 차이/합으로 변환 |
| 원들이 덮는 길이/넓이 | angular interval sweep |

좌표를 바로 구하기보다 먼저 교점 개수, 접함, 포함, 분리 상태를 판정합니다.

## 2. 기본 Point 연산

```cpp compile-check
#include <algorithm>
#include <cmath>
#include <vector>
using namespace std;

const double EPS_CIRCLE = 1e-10;

struct CirclePoint {
    double x = 0;
    double y = 0;
};

CirclePoint operator+(CirclePoint a, CirclePoint b) {
    return {a.x + b.x, a.y + b.y};
}

CirclePoint operator-(CirclePoint a, CirclePoint b) {
    return {a.x - b.x, a.y - b.y};
}

CirclePoint operator*(CirclePoint a, double scale) {
    return {a.x * scale, a.y * scale};
}

CirclePoint operator/(CirclePoint a, double scale) {
    return {a.x / scale, a.y / scale};
}

double dotCircle(CirclePoint a, CirclePoint b) {
    return a.x * b.x + a.y * b.y;
}

double crossCircle(CirclePoint a, CirclePoint b) {
    return a.x * b.y - a.y * b.x;
}

double norm2Circle(CirclePoint a) {
    return dotCircle(a, a);
}

double normCircle(CirclePoint a) {
    return sqrt(norm2Circle(a));
}

CirclePoint rotate90(CirclePoint a) {
    return {-a.y, a.x};
}
```

정수 좌표 입력이어도 교점은 실수가 됩니다. 출력 오차 기준을 확인하고 `double` 또는 `long double`을 고릅니다.

## 3. 원과 직선의 교점

직선 `a + t(b-a)`에 원 중심 `c`, 반지름 `r`이 있을 때, 먼저 중심을 직선에 projection합니다.

```text
foot = a + dir * dot(c - a, dir) / |dir|^2
distance = |foot - c|
```

`distance > r`이면 교점이 없습니다. 같으면 접점 하나, 작으면 수직 방향으로 두 교점입니다.

```cpp compile-check
#include <cmath>
#include <vector>
using namespace std;

struct CircleLinePoint {
    double x = 0;
    double y = 0;
};

CircleLinePoint operator+(CircleLinePoint a, CircleLinePoint b) { return {a.x + b.x, a.y + b.y}; }
CircleLinePoint operator-(CircleLinePoint a, CircleLinePoint b) { return {a.x - b.x, a.y - b.y}; }
CircleLinePoint operator*(CircleLinePoint a, double k) { return {a.x * k, a.y * k}; }

double dotLine(CircleLinePoint a, CircleLinePoint b) { return a.x * b.x + a.y * b.y; }
double norm2Line(CircleLinePoint a) { return dotLine(a, a); }
double normLine(CircleLinePoint a) { return sqrt(norm2Line(a)); }
CircleLinePoint normalLine(CircleLinePoint a) { return {-a.y, a.x}; }

vector<CircleLinePoint> circleLineIntersection(
    CircleLinePoint center,
    double radius,
    CircleLinePoint a,
    CircleLinePoint b
) {
    CircleLinePoint dir = b - a;
    double len2 = norm2Line(dir);
    CircleLinePoint foot = a + dir * (dotLine(center - a, dir) / len2);
    double d2 = norm2Line(foot - center);
    double r2 = radius * radius;
    if (d2 > r2 + 1e-10) {
        return {};
    }
    if (fabs(d2 - r2) <= 1e-10) {
        return {foot};
    }
    double offset = sqrt(max(0.0, r2 - d2)) / normLine(dir);
    CircleLinePoint unitNormal = normalLine(dir);
    return {foot + unitNormal * offset, foot - unitNormal * offset};
}
```

선분과 원의 교점이면 나온 점이 선분 bounding box 또는 parameter `t in [0,1]` 안에 있는지 추가로 봅니다.

## 4. 두 원의 교점

두 원 중심을 `c1`, `c2`, 거리 `d`라고 합시다. 중심선 위에서 첫 번째 중심으로부터 거리 `x`만큼 간 base point를 잡습니다.

```text
x = (r1^2 - r2^2 + d^2) / (2d)
h^2 = r1^2 - x^2
```

`h^2 < 0`이면 교점이 없습니다. `h = 0`이면 접하고, 양수면 두 점입니다.

## 5. Tangent Construction

외부 점 `p`에서 원 `(c, r)`에 접선을 그을 때, `pc`를 빗변으로 하는 직각삼각형을 봅니다.

```text
|p-c| < r  -> 접선 없음
|p-c| = r  -> p 자체가 접점
|p-c| > r  -> 접점 2개
```

두 원의 공통 접선은 반지름 차이 또는 합을 이용해 "점에서 축소된 원에 접선" 문제로 바꿀 수 있습니다. 외접선은 `r1 - r2`, 내접선은 `r1 + r2`가 핵심입니다.

## 6. Angular Interval Sweep

원 위에서 다른 원이 덮는 arc를 계산하는 문제는 각도 구간으로 바꿉니다.

```text
base = atan2(c2.y - c1.y, c2.x - c1.x)
delta = acos((r1^2 + d^2 - r2^2) / (2*r1*d))
covered interval = [base - delta, base + delta]
```

각도는 `[-pi, pi)` 경계에서 끊기므로 구간을 정규화하거나 `+2pi` 복사본을 같이 둡니다.

## 7. 작은 예시

```text
circle center = (0, 0), r = 5
line y = 3

projection foot = (0, 3)
distance = 3
offset = sqrt(25 - 9) = 4
intersection = (-4, 3), (4, 3)
```

이 예시는 projection이 교점의 중점이 된다는 사실을 보여 줍니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| 원-직선 교점 | `O(1)` |
| 원-원 교점 | `O(1)` |
| 한 점에서 원 접선 | `O(1)` |
| 모든 원 pair 교점 | `O(N^2)` |
| 원 arc sweep | 보통 `O(N^2 log N)` |

기하 문제는 공식보다 case 수가 병목입니다. 접함, 포함, 같은 중심, 반지름 0 같은 조건을 먼저 정리합니다.

## 9. 자주 하는 실수

1. 두 원 중심이 같은데 `d`로 나누어 NaN을 만든다.
2. 접하는 경우를 교점 2개로 중복 출력한다.
3. `acos` 인자가 오차로 `[-1,1]`을 살짝 벗어나는 것을 clamp하지 않는다.
4. 선분-원 교점에서 무한 직선 교점을 그대로 사용한다.
5. 각도 구간이 `pi` 경계를 넘는 경우를 놓친다.

## 10. 문제를 볼 때 체크할 조건

- 교점 개수를 출력해야 하는가, 좌표를 출력해야 하는가?
- 직선인지 선분인지 구분했는가?
- 같은 중심 원과 포함 관계를 처리했는가?
- EPS와 출력 오차 조건을 정했는가?
- 각도 sweep이면 구간 wrap-around를 처리했는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: circle line intersection `/practice/...` 문제 필요 | projection과 offset 계산 | point-line distance |
| 표준 | TODO: circle circle intersection `/practice/...` 문제 필요 | 교점 개수 case 분기 | center distance |
| 응용 | TODO: common tangents `/practice/...` 문제 필요 | 외접선/내접선 변환 | tangent construction |
| 함정 | TODO: angular interval sweep `/practice/...` 문제 필요 | 각도 wrap 처리 | atan2, acos |
