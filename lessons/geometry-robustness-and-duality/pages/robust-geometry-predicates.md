# Robust Geometry Predicates

Robust Geometry Predicates는 orientation, incircle, 교차 판정처럼 기하 알고리즘의 분기 조건을 안정적으로 계산하는 방법을 정리합니다. 좌표를 구하는 공식보다 `왼쪽인가`, `겹치는가`, `원 안인가` 같은 predicate가 틀리면 전체 알고리즘이 무너집니다.


아래 orientation은 좌표 절댓값<=10^18에서 __int128 중간값이 안전합니다. long long 전체 범위를 자동으로 지원하지는 않습니다. EPS comparator의 문제는 근사 동치가 추이적이지 않아 strict weak ordering을 깨뜨릴 수 있다는 것입니다.

## 문제 신호

| 문제 표현 | Robust Predicate 관점 |
| --- | --- |
| 세 점의 방향 판정 | orientation sign |
| 선분 교차 여부 | orientation + bounding box |
| 점이 원 안/밖인지 | incircle predicate |
| sweep line에서 순서 비교 | near-collinear 처리 |
| 입력 좌표가 큰 정수 | overflow 방지 |

좌표를 double로 바꿔서 cross product를 계산하면 큰 정수 입력에서 잘못된 부호가 나올 수 있습니다. 정수 좌표면 `__int128`부터 고려합니다.

## Orientation Predicate

세 점 `a, b, c`의 방향은 `(b-a) x (c-a)`의 부호입니다.

```text
positive: counter-clockwise
negative: clockwise
zero: collinear
```

정수 좌표 범위가 `1e9`라면 곱은 `1e18` 근처까지 갑니다. 차이까지 생각하면 `long long` 경계에 닿을 수 있으므로 `__int128`이 안전합니다.

## 정수 좌표 선분 교차

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

## EPS 정책

실수 좌표에서는 exact zero가 거의 나오지 않습니다. 대신 문제의 오차 조건에 맞춰 EPS를 정합니다.

| 상황 | 권장 |
| --- | --- |
| 입력이 정수이고 판정만 필요 | EPS 없이 exact integer |
| 좌표를 계산해 출력 | `double`/`long double` + 출력 오차 |
| 반복 회전/정규화 | 오차 누적 점검 |
| 정렬 comparator | EPS로 strict weak ordering 깨지 않게 주의 |

EPS를 크게 잡으면 가까운 두 점이 같은 점이 되어 버리고, 너무 작게 잡으면 접하는 경우를 놓칩니다.

## Incircle Predicate

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

## Construction과 Predicate 분리

Predicate는 분기 조건이고 construction은 좌표 계산입니다.

```text
predicate: 두 선분이 교차하는가?
construction: 교점 좌표는 어디인가?
```

교차 여부는 정수 exact로 판단하고, 교점 좌표만 double로 계산할 수 있습니다. 반대로 double 교점 좌표를 만든 뒤 그 값으로 다시 정렬/판정하면 오차가 퍼질 수 있습니다.

## 작은 예시

```text
a = (0, 0), b = (1000000000, 999999999)
c = (0, 0), d = (999999999, 999999998)
```

두 방향 벡터 외적은 정확히 -1입니다. 약 10^18인 두 곱의 차이를 double로 계산하면 이 부호를 잃을 수 있습니다. 선분들은 원점을 공유하므로 교차 여부 자체는 YES이고, 여기서 검사할 것은 방향 부호입니다.

## Sweep Line Comparator

Sweep line에서 active segment를 정렬할 때 `currentX`에서의 y좌표를 비교합니다. EPS를 comparator에 직접 넣으면 가까운 값 사이의 근사 동치가 추이적이지 않아 strict weak ordering을 깨뜨릴 수 있습니다.

대안은 다음과 같습니다.

1. event x 사이에서 순서가 변하는 지점을 명시적으로 처리한다.
2. exact orientation으로 두 segment의 상대 순서를 비교한다.
3. tie-breaking을 segment id로 고정한다.

## 로컬 연습: Exact Segment Intersection

정수 좌표 선분 두 개가 교차하는지 판정합니다. 교점 좌표를 만들지 말고, orientation sign과 bounding box만으로 답합니다.

#### 입력

```text
Q
ax ay bx by cx cy dx dy
...
```

- `1 <= Q <= 200000`
- 각 좌표의 절댓값은 `10^18` 이하입니다.
- 각 줄은 선분 `AB`와 `CD`를 의미합니다.

#### 출력

각 query마다 교차하면 `YES`, 아니면 `NO`를 출력합니다. 끝점에서 접하거나 collinear overlap인 경우도 교차입니다.

#### 예시

```text
3
0 0 4 4 0 4 4 0
0 0 1 0 2 0 3 0
0 0 4 0 2 0 6 0
```

```text
YES
NO
YES
```

#### 손으로 따라가는 Trace

첫 번째 query는 `A=(0,0)`, `B=(4,4)`, `C=(0,4)`, `D=(4,0)`입니다.

| predicate | cross sign | 의미 |
| --- | ---: | --- |
| `orient(A,B,C)` | `+16` | `C`는 `AB`의 왼쪽 |
| `orient(A,B,D)` | `-16` | `D`는 `AB`의 오른쪽 |
| `orient(C,D,A)` | `-16` | `A`는 `CD`의 오른쪽 |
| `orient(C,D,B)` | `+16` | `B`는 `CD`의 왼쪽 |

두 선분이 서로의 양쪽에 끝점을 하나씩 가지므로 교차합니다. 세 번째 query처럼 모든 점이 collinear이면 orientation만으로 끝내지 말고 bounding box overlap을 확인해야 합니다.

#### 구현 기준

```cpp
#include <iostream>

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int queries;
    cin >> queries;
    while (queries-- > 0) {
        RobustPoint a, b, c, d;
        cin >> a.x >> a.y >> b.x >> b.y >> c.x >> c.y >> d.x >> d.y;
        cout << (segmentsIntersect(a, b, c, d) ? "YES" : "NO") << '\n';
    }
}
```

#### Stress 기준

1. 좌표가 작은 격자 `[-5,5]`에서는 모든 선분 쌍을 열거해 endpoint permutation에 대해 결과가 같은지 확인합니다.
2. `AB`와 `BA`, `CD`와 `DC`를 바꿔도 결과가 같아야 합니다.
3. collinear disjoint, collinear overlap, endpoint touch, duplicate point segment를 deterministic case로 둡니다.
4. 좌표 범위를 키울 때는 cross product가 `__int128` 범위 안인지 계산합니다.
