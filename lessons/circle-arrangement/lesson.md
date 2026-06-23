# Circle Arrangement

Circle Arrangement는 여러 원의 교점으로 arc를 나누고, union area, union perimeter, depth 같은 값을 angular sweep으로 계산하는 기하 응용 레슨입니다. Circle Geometry가 두 원과 직선의 교점 공식을 다뤘다면, 이 레슨은 많은 원이 만드는 arrangement에서 어떤 arc가 외곽 또는 특정 depth에 속하는지 판정합니다.

이 레슨은 Circle Geometry, Sweep Line Geometry, Shape Distance Modeling 이후에 보는 계산기하 심화입니다.

1. 각 원 둘레를 다른 원과의 교점 각도로 분할한다.
2. arc 중간점을 찍어 그 arc의 cover depth를 판정한다.
3. 같은 원, 포함, 접함, EPS 처리를 먼저 정리한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: circle-circle intersection, atan2, angular interval, EPS
- 함께 보면 좋은 레슨: Circle Geometry, Sweep Line Geometry, Shape Distance Modeling
- 다음에 볼 레슨: robust geometry predicates, Voronoi/Delaunay 응용

## 1. 문제 신호

| 문제 표현 | Circle Arrangement 관점 |
| --- | --- |
| 여러 원의 합집합 넓이 | arc 분할 + Green theorem |
| 원들의 외곽 둘레 | cover depth가 1인 boundary arc |
| 정확히 k개 원에 덮인 영역 | depth별 angular sweep |
| 원끼리 많이 교차 | arrangement vertices |
| 포함된 원 제거 가능 | containment preprocessing |

직사각형 union은 x sweep으로 풀지만, 원 union은 각 원의 둘레를 angular interval로 쪼개는 접근이 자주 쓰입니다.

## 2. Arc 분할 아이디어

각 원 `i`에 대해 다른 원 `j`와의 교점을 구하고, 그 교점들이 만드는 각도를 모읍니다. 인접한 두 angle 사이 arc는 다른 원들과의 포함 관계가 변하지 않습니다.

```text
angles = [0, 2pi]
for every other circle:
  if intersects current circle:
    add angle of intersection point 1
    add angle of intersection point 2
sort angles
for each neighboring angle interval:
  test midpoint
```

midpoint가 몇 개 원 안에 들어가는지 세면 그 arc의 depth를 알 수 있습니다.

## 3. 포함 관계

원 `A`가 원 `B` 안에 완전히 들어가면 `A`의 arc는 union boundary에 기여하지 않을 수 있습니다.

```text
distance(centerA, centerB) + rA <= rB
```

같은 중심, 같은 반지름 원은 중복입니다. 중복 원을 그대로 두면 depth 계산은 가능하지만 perimeter나 boundary arc를 중복 처리하기 쉽습니다.

## 4. Angle 정규화

각도는 `[0, 2pi)`로 정규화하고, wrap-around interval을 처리하기 위해 `0`과 `2pi`를 항상 넣습니다.

```cpp compile-check
#include <algorithm>
#include <cmath>
#include <vector>
using namespace std;

const double PI_CIRCLE_ARR = acos(-1.0);

double normalizeAngle(double angle) {
    double twoPi = 2.0 * PI_CIRCLE_ARR;
    while (angle < 0) {
        angle += twoPi;
    }
    while (angle >= twoPi) {
        angle -= twoPi;
    }
    return angle;
}

vector<double> uniqueAngles(vector<double> angles) {
    const double EPS = 1e-10;
    for (double& angle : angles) {
        angle = normalizeAngle(angle);
    }
    angles.push_back(0.0);
    angles.push_back(2.0 * PI_CIRCLE_ARR);
    sort(angles.begin(), angles.end());

    vector<double> result;
    for (double angle : angles) {
        if (result.empty() || fabs(result.back() - angle) > EPS) {
            result.push_back(angle);
        }
    }
    if (result.back() < 2.0 * PI_CIRCLE_ARR - EPS) {
        result.push_back(2.0 * PI_CIRCLE_ARR);
    }
    return result;
}
```

교점이 접하는 경우 같은 angle이 두 번 나올 수 있습니다. 중복 제거를 하지 않으면 길이 0 arc가 생깁니다.

## 5. Arc Midpoint 판정

원 `i`의 arc angle interval `(a, b)`를 볼 때 midpoint angle `m`을 잡고 점을 만듭니다.

```text
p = center_i + r_i * (cos m, sin m)
depth = p를 포함하는 원 개수
```

union perimeter를 구하려면 `depth == 1`인 arc 길이 `r_i * (b-a)`를 더합니다. 다른 원 안에 들어간 arc는 외곽이 아닙니다.

## 6. Area 계산 관점

원 union area는 boundary arc contribution을 더하는 방식으로 계산할 수 있습니다. arc endpoint를 `P(a)`, `P(b)`라고 할 때, Green theorem 기반으로 segment triangle area와 circular sector area를 합칩니다.

```text
arc contribution =
  cross(P(a), P(b)) / 2
  + r^2 * (theta - sin(theta)) / 2
```

부호와 방향을 일관되게 두어야 합니다. 처음 구현할 때는 perimeter나 depth counting부터 맞춘 뒤 area를 붙이는 편이 안전합니다.

## 7. 작은 예시

```text
circle A: center (0,0), r=2
circle B: center (2,0), r=2

A 위 교점 angle은 ±60도다.
A의 오른쪽 arc 일부는 B 안에 들어간다.
A의 왼쪽 큰 arc는 union boundary에 남는다.
B도 대칭적으로 boundary arc를 낸다.
```

두 원 union perimeter는 각 원의 전체 둘레에서 서로 내부에 들어간 arc를 뺀 값입니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| 모든 원 pair 교점 | `O(N^2)` |
| 각 원 angle sort | 전체 `O(N^2 log N)` |
| midpoint depth를 단순 계산 | `O(N^3)` 가능 |
| depth sweep 최적화 | 구현에 따라 `O(N^2 log N)` |

원 개수가 작으면 midpoint마다 모든 원을 검사해도 됩니다. `N`이 커지면 각도 이벤트로 depth를 갱신하는 방식이 필요합니다.

## 9. 자주 하는 실수

1. 완전히 포함된 원의 arc를 union boundary에 더한다.
2. 접점 중복 angle 때문에 0 길이 arc를 처리한다.
3. `atan2` 결과가 음수인 것을 정규화하지 않는다.
4. midpoint가 원 경계에 걸릴 때 EPS 없이 depth가 흔들린다.
5. area contribution의 방향과 sector 보정을 섞는다.

## 10. 문제를 볼 때 체크할 조건

- 구하려는 값이 union area, perimeter, depth별 area 중 무엇인가?
- 같은 원 또는 포함된 원을 어떻게 처리할 것인가?
- tangent와 거의 tangent인 경우 EPS를 정했는가?
- `O(N^3)` midpoint 검사로 충분한가?
- 각도 wrap-around와 중복 angle을 제거했는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: circle arrangement `/practice/...` 문제 필요 | 교점 angle로 arc 분할 | atan2 |
| 표준 | TODO: circle union perimeter `/practice/...` 문제 필요 | depth 1 arc 길이 합산 | angular sweep |
| 응용 | TODO: circle union area `/practice/...` 문제 필요 | arc contribution 계산 | Green theorem |
| 함정 | TODO: contained circles `/practice/...` 문제 필요 | 포함/중복 원 처리 | EPS |

