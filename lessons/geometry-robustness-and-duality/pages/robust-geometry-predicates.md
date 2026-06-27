# Robust Geometry Predicates

Robust Geometry Predicates는 orientation, incircle, 교차 판정처럼 기하 알고리즘의 분기 조건을 안정적으로 계산하는 방법을 정리합니다. 좌표를 구하는 공식보다 `왼쪽인가`, `겹치는가`, `원 안인가` 같은 predicate가 틀리면 전체 알고리즘이 무너집니다.

이 레슨은 CCW/Segment Intersection, Circle Geometry, Sweep Line Geometry 이후에 보는 계산기하 안정성 레슨입니다.

1. 정수 좌표 predicate는 가능한 한 exact arithmetic으로 처리한다.
2. 실수 좌표는 EPS 정책과 출력 오차를 분리한다.
3. predicate와 construction을 같은 기준으로 섞지 않는다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: dot product, cross product, segment intersection, circle geometry
- 함께 보면 좋은 레슨: Geometry CCW와 Segment Intersection, Circle Geometry, Sweep Line Geometry
- 다음에 볼 레슨: Voronoi와 Delaunay, circle arrangement, half-plane intersection

## 1. 문제 신호

| 문제 표현 | Robust Predicate 관점 |
| --- | --- |
| 세 점의 방향 판정 | orientation sign |
| 선분 교차 여부 | orientation + bounding box |
| 점이 원 안/밖인지 | incircle predicate |
| sweep line에서 순서 비교 | near-collinear 처리 |
| 입력 좌표가 큰 정수 | overflow 방지 |

좌표를 double로 바꿔서 cross product를 계산하면 큰 정수 입력에서 잘못된 부호가 나올 수 있습니다. 정수 좌표면 `__int128`부터 고려합니다.

## 2. Orientation Predicate

세 점 `a, b, c`의 방향은 `(b-a) x (c-a)`의 부호입니다.

```text
positive: counter-clockwise
negative: clockwise
zero: collinear
```

정수 좌표 범위가 `1e9`라면 곱은 `1e18` 근처까지 갑니다. 차이까지 생각하면 `long long` 경계에 닿을 수 있으므로 `__int128`이 안전합니다.

## 3. 정수 좌표 선분 교차

```cpp compile-check
#include <algorithm>
using namespace std;

struct RobustPoint {
    long long x = 0;
    long long y = 0;
};

int sign128(__int128 value) {
    if (value < 0) {
        return -1;
    }
    if (value > 0) {
        return 1;
    }
    return 0;
}

int orientation(RobustPoint a, RobustPoint b, RobustPoint c) {
    __int128 x1 = (__int128)b.x - a.x;
    __int128 y1 = (__int128)b.y - a.y;
    __int128 x2 = (__int128)c.x - a.x;
    __int128 y2 = (__int128)c.y - a.y;
    return sign128(x1 * y2 - y1 * x2);
}

bool betweenInclusive(long long a, long long b, long long x) {
    if (a > b) {
        swap(a, b);
    }
    return a <= x && x <= b;
}

bool onSegment(RobustPoint a, RobustPoint b, RobustPoint p) {
    return orientation(a, b, p) == 0
        && betweenInclusive(a.x, b.x, p.x)
        && betweenInclusive(a.y, b.y, p.y);
}

bool segmentsIntersect(RobustPoint a, RobustPoint b, RobustPoint c, RobustPoint d) {
    int abC = orientation(a, b, c);
    int abD = orientation(a, b, d);
    int cdA = orientation(c, d, a);
    int cdB = orientation(c, d, b);

    if (abC == 0 && onSegment(a, b, c)) {
        return true;
    }
    if (abD == 0 && onSegment(a, b, d)) {
        return true;
    }
    if (cdA == 0 && onSegment(c, d, a)) {
        return true;
    }
    if (cdB == 0 && onSegment(c, d, b)) {
        return true;
    }
    return abC * abD < 0 && cdA * cdB < 0;
}
```

이 코드는 정수 좌표 predicate입니다. 교점 좌표를 출력해야 하면 별도 rational 또는 floating construction이 필요합니다.

## 4. EPS 정책

실수 좌표에서는 exact zero가 거의 나오지 않습니다. 대신 문제의 오차 조건에 맞춰 EPS를 정합니다.

| 상황 | 권장 |
| --- | --- |
| 입력이 정수이고 판정만 필요 | EPS 없이 exact integer |
| 좌표를 계산해 출력 | `double`/`long double` + 출력 오차 |
| 반복 회전/정규화 | 오차 누적 점검 |
| 정렬 comparator | EPS로 strict weak ordering 깨지 않게 주의 |

EPS를 크게 잡으면 가까운 두 점이 같은 점이 되어 버리고, 너무 작게 잡으면 접하는 경우를 놓칩니다.

## 5. Incircle Predicate

Delaunay나 circle arrangement에서는 점이 세 점의 외접원 안에 있는지 판정합니다. 정수 좌표에서는 determinant 부호로 처리할 수 있습니다.

```text
det([
  ax ay ax^2+ay^2 1
  bx by bx^2+by^2 1
  cx cy cx^2+cy^2 1
  dx dy dx^2+dy^2 1
])
```

이 determinant는 값이 매우 커질 수 있습니다. 좌표 범위가 크면 `__int128`도 부족할 수 있어 arbitrary precision이나 adaptive predicate가 필요합니다.

## 6. Construction과 Predicate 분리

Predicate는 분기 조건이고 construction은 좌표 계산입니다.

```text
predicate: 두 선분이 교차하는가?
construction: 교점 좌표는 어디인가?
```

교차 여부는 정수 exact로 판단하고, 교점 좌표만 double로 계산할 수 있습니다. 반대로 double 교점 좌표를 만든 뒤 그 값으로 다시 정렬/판정하면 오차가 퍼질 수 있습니다.

## 7. 작은 예시

```text
a = (0, 0), b = (1e9, 1e9)
c = (1e9, 1e9 - 1), d = (0, 1)
```

두 선분은 거의 평행해 보이지만 cross product의 작은 차이가 교차 여부를 결정합니다. double로 계산하면 입력 범위와 정렬 순서에 따라 부호가 흔들릴 수 있습니다.

## 8. Sweep Line Comparator

Sweep line에서 active segment를 정렬할 때 `currentX`에서의 y좌표를 비교합니다. EPS를 comparator에 직접 넣으면 `a < b`, `b < c`, `c < a` 같은 비일관성이 생길 수 있습니다.

대안은 다음과 같습니다.

1. event x 사이에서 순서가 변하는 지점을 명시적으로 처리한다.
2. exact orientation으로 두 segment의 상대 순서를 비교한다.
3. tie-breaking을 segment id로 고정한다.

## 9. 자주 하는 실수

1. 정수 좌표 판정을 double cross product로 처리한다.
2. `long long` 곱셈 overflow를 놓친다.
3. EPS comparator로 `set`의 strict weak ordering을 깨뜨린다.
4. 접하는 경우를 교차하지 않는 것으로 처리한다.
5. predicate 결과와 좌표 construction 결과를 서로 다른 기준으로 섞는다.

## 10. 문제를 볼 때 체크할 조건

- 입력 좌표가 정수인가 실수인가?
- 필요한 것은 판정인가, 좌표 출력인가?
- 좌표 범위에서 cross/determinant가 overflow하지 않는가?
- collinear, tangent, duplicate point를 어떻게 처리할 것인가?
- comparator에 tie-breaking이 있는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: robust orientation `/practice/...` 문제 필요 | `__int128` cross sign | ccw |
| 표준 | TODO: segment intersection edge cases `/practice/...` 문제 필요 | 접함/겹침 처리 | bounding box |
| 응용 | TODO: robust incircle `/practice/...` 문제 필요 | determinant sign | Delaunay |
| 함정 | TODO: sweep comparator `/practice/...` 문제 필요 | strict ordering 유지 | EPS policy |
