# 기하 기본: CCW, 선분 교차, Convex Hull

기하 문제는 공식을 많이 외우는 것보다 **좌표를 벡터로 보고 방향과 경계를 정확히 처리하는 것**이 중요합니다. 특히 정수 좌표 문제에서는 부동소수점 계산을 피하고, 외적(cross product)의 부호로 판단할 수 있는 경우가 많습니다.

이 레슨은 기하 입문의 세 축을 다룹니다.

1. CCW로 세 점의 방향을 판단한다.
2. CCW와 경계 비교로 두 선분이 교차하는지 판정한다.
3. 정렬과 CCW를 이용해 Convex Hull을 만든다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 정렬, `long long`, 좌표와 벡터 감각
- 함께 보면 좋은 레슨: 정렬 알고리즘, 대회용 C++ 기본기
- 다음에 볼 레슨: Rotating Calipers, Sweep Line Geometry

## 1. 점과 벡터

2차원 점은 보통 `(x, y)`로 표현합니다. 두 점 `a`, `b`가 있으면 `a -> b` 벡터는 `(b.x - a.x, b.y - a.y)`입니다.

```cpp compile-check
struct Point {
    long long x;
    long long y;
};
```

정수 좌표의 범위가 `10^9` 수준이면 좌표 차의 곱은 `10^18` 근처까지 갈 수 있습니다. 그래서 기하 기본 구현에서는 `int`보다 `long long`을 먼저 씁니다.

## 2. 외적과 CCW

두 벡터 `a`, `b`의 외적은 아래처럼 계산합니다.

```text
cross(a, b) = a.x * b.y - a.y * b.x
```

세 점 `a`, `b`, `c`의 방향은 `(b - a)`와 `(c - a)`의 외적 부호로 판단합니다.

| 부호 | 의미 |
| ---: | --- |
| 양수 | `a -> b -> c`가 반시계 방향 |
| 음수 | 시계 방향 |
| 0 | 세 점이 일직선 |

```cpp compile-check
struct Point {
    long long x;
    long long y;
};

long long cross(Point a, Point b, Point c) {
    long long x1 = b.x - a.x;
    long long y1 = b.y - a.y;
    long long x2 = c.x - a.x;
    long long y2 = c.y - a.y;
    return x1 * y2 - y1 * x2;
}

int ccw(Point a, Point b, Point c) {
    long long value = cross(a, b, c);
    if (value > 0) return 1;
    if (value < 0) return -1;
    return 0;
}
```

CCW는 기하 문제의 조건문입니다. "왼쪽으로 도는가", "일직선인가", "볼록 껍질에서 오른쪽으로 꺾였는가"를 모두 이 부호로 봅니다.

## 3. 선분 교차

두 선분 `ab`, `cd`가 교차하는지 보려면 서로가 서로를 가로지르는지 확인합니다.

```text
ccw(a, b, c) * ccw(a, b, d) <= 0
ccw(c, d, a) * ccw(c, d, b) <= 0
```

하지만 네 점이 일직선인 경우에는 단순 부호만으로 부족합니다. 이때는 두 선분의 bounding box가 겹치는지 확인합니다.

```cpp compile-check
#include <algorithm>
using namespace std;

struct Point {
    long long x;
    long long y;
};

long long cross(Point a, Point b, Point c) {
    long long x1 = b.x - a.x;
    long long y1 = b.y - a.y;
    long long x2 = c.x - a.x;
    long long y2 = c.y - a.y;
    return x1 * y2 - y1 * x2;
}

int ccw(Point a, Point b, Point c) {
    long long value = cross(a, b, c);
    if (value > 0) return 1;
    if (value < 0) return -1;
    return 0;
}

bool between(long long a, long long b, long long x) {
    if (a > b) swap(a, b);
    return a <= x && x <= b;
}

bool onSegment(Point a, Point b, Point p) {
    return ccw(a, b, p) == 0 &&
        between(a.x, b.x, p.x) &&
        between(a.y, b.y, p.y);
}

bool segmentsIntersect(Point a, Point b, Point c, Point d) {
    int abC = ccw(a, b, c);
    int abD = ccw(a, b, d);
    int cdA = ccw(c, d, a);
    int cdB = ccw(c, d, b);

    if (abC == 0 && onSegment(a, b, c)) return true;
    if (abD == 0 && onSegment(a, b, d)) return true;
    if (cdA == 0 && onSegment(c, d, a)) return true;
    if (cdB == 0 && onSegment(c, d, b)) return true;

    return abC * abD < 0 && cdA * cdB < 0;
}
```

끝점에서 만나는 것도 교차로 볼지, 내부에서만 만나는 것을 교차로 볼지는 문제마다 다릅니다. 위 구현은 끝점 접촉과 겹침을 모두 교차로 봅니다.

## 4. Convex Hull

Convex Hull은 모든 점을 포함하는 가장 작은 볼록 다각형입니다. 대표적인 구현은 monotonic chain입니다.

1. 점을 `(x, y)` 기준으로 정렬한다.
2. 아래쪽 hull을 왼쪽에서 오른쪽으로 만든다.
3. 위쪽 hull을 오른쪽에서 왼쪽으로 만든다.
4. 두 hull을 합친다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct Point {
    long long x;
    long long y;
};

bool operator<(const Point& a, const Point& b) {
    if (a.x != b.x) return a.x < b.x;
    return a.y < b.y;
}

bool operator==(const Point& a, const Point& b) {
    return a.x == b.x && a.y == b.y;
}

long long cross(Point a, Point b, Point c) {
    long long x1 = b.x - a.x;
    long long y1 = b.y - a.y;
    long long x2 = c.x - a.x;
    long long y2 = c.y - a.y;
    return x1 * y2 - y1 * x2;
}

vector<Point> convexHull(vector<Point> points) {
    sort(points.begin(), points.end());
    points.erase(unique(points.begin(), points.end()), points.end());
    if (points.size() <= 1) {
        return points;
    }

    vector<Point> lower;
    for (Point p : points) {
        while (lower.size() >= 2 &&
               cross(lower[lower.size() - 2], lower.back(), p) <= 0) {
            lower.pop_back();
        }
        lower.push_back(p);
    }

    vector<Point> upper;
    for (int i = (int)points.size() - 1; i >= 0; --i) {
        Point p = points[i];
        while (upper.size() >= 2 &&
               cross(upper[upper.size() - 2], upper.back(), p) <= 0) {
            upper.pop_back();
        }
        upper.push_back(p);
    }

    lower.pop_back();
    upper.pop_back();
    lower.insert(lower.end(), upper.begin(), upper.end());
    return lower;
}
```

위 구현은 한 직선 위에 있는 중간 점을 hull에서 제거합니다. 경계 위의 모든 점을 포함해야 하는 문제라면 `<= 0` 조건을 `< 0`으로 바꾸는 식으로 collinear 처리 정책을 바꿔야 합니다.

## 5. 정수 기하와 실수 기하

정수 좌표의 CCW, 선분 교차, convex hull은 대부분 `long long` 외적으로 처리할 수 있습니다. 반면 원, 각도, 거리 비교, 교점 좌표가 나오면 실수 오차를 관리해야 합니다.

입문 단계에서는 아래 원칙이 안전합니다.

| 상황 | 우선 선택 |
| --- | --- |
| 방향, 교차 여부, 볼록성 | 정수 외적 |
| 거리 비교 | 제곱 거리 비교 |
| 실제 거리 출력 | `double`과 오차 허용 |
| 각도 정렬 | 사분면 + 외적 또는 `atan2` |

거리 비교만 필요하면 `sqrt`를 쓰지 말고 제곱 거리로 비교합니다.

```cpp compile-check
struct Point {
    long long x;
    long long y;
};

long long dist2(Point a, Point b) {
    long long dx = a.x - b.x;
    long long dy = a.y - b.y;
    return dx * dx + dy * dy;
}
```

## 6. 시간 복잡도

| 작업 | 시간 |
| --- | ---: |
| CCW 한 번 | `O(1)` |
| 선분 교차 한 번 | `O(1)` |
| 모든 선분 쌍 교차 검사 | `O(n^2)` |
| Convex Hull monotonic chain | `O(n log n)` |

Convex Hull의 병목은 정렬입니다. 정렬 이후 hull을 만드는 while loop는 각 점이 들어가고 빠지는 횟수가 상수 번이라 전체 `O(n)`입니다.

## 7. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 외적을 `int`로 계산 | overflow | 좌표 범위가 크면 `long long` |
| 선분 교차에서 일직선 겹침 누락 | 끝점/겹침 케이스 오답 | `onSegment` 별도 처리 |
| 끝점 접촉을 교차로 볼지 확인하지 않음 | 판정 기준 불일치 | 문제의 교차 정의 확인 |
| Convex Hull에서 중복 점 제거 누락 | 같은 점 반복, hull 오염 | `sort + unique` |
| collinear 점 처리 정책을 무심코 선택 | 경계 점 포함 여부 오답 | `<= 0`와 `< 0` 차이 확인 |
| 실수 좌표를 정확 비교 | 오차 오답 | `eps` 또는 정수식 유지 |

## 8. 문제를 볼 때 체크할 조건

1. 좌표가 정수인가, 실수인가?
2. 좌표 범위의 곱이 `long long` 안에 들어오는가?
3. 끝점에서 만나는 것도 교차로 보는가?
4. 일직선으로 겹치는 선분을 어떻게 처리해야 하는가?
5. Convex Hull에서 경계 위의 모든 점이 필요한가?
6. 거리 자체가 필요한가, 거리 비교만 필요한가?

정리하면, 기하 기본은 외적 부호와 경계 처리입니다. CCW를 정확히 구현하고, 문제의 "포함/접촉/겹침" 정의를 먼저 확인하면 많은 기하 입문 문제를 안정적으로 풀 수 있습니다.

## 9. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 세 점의 방향을 판정하는 문제 추가 | 외적 부호와 `long long` 감각 익히기 | CCW, cross product |
| 표준 | TODO: 두 선분의 교차 여부를 판정하는 문제 추가 | 일직선과 끝점 접촉 처리 | segment intersection |
| 응용 | TODO: 점 집합의 convex hull을 구하는 문제 추가 | monotonic chain과 collinear 정책 확인 | convex hull |
| 함정 | TODO: 경계 위 모든 점 포함 여부가 갈리는 문제 추가 | `<= 0`와 `< 0` 조건 차이 체감 | collinear boundary |
