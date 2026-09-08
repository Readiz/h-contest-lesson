# Line Arrangement

Line Arrangement는 여러 직선이 평면을 어떻게 나누는지, 교점이 어떤 순서로 생기는지, 그리고 각 직선이 arrangement에 몇 개의 새 영역을 추가하는지 분석하는 주제입니다. Segment intersection sweep보다 한 단계 더 구조적인 기하 관점입니다.

## 문제 신호

| 문제 표현 | 접근 |
| --- | --- |
| N개 직선이 평면을 몇 영역으로 나누는가 | arrangement region count |
| 중복/평행 직선이 있다 | line normalization |
| 교점 개수를 정확히 세야 한다 | rational point set |
| 선분 교차 순서가 필요하다 | sweep line |
| 면, 변, 꼭짓점 관계가 나온다 | planar subdivision |

무한 직선 arrangement는 선분 arrangement보다 단순합니다. 선분은 endpoint, overlap, active order 변화까지 처리해야 하므로 훨씬 조심해야 합니다.

## 영역 수 공식

새 직선 하나를 추가한다고 합시다. 이 직선 위에서 기존 직선들과 만나는 서로 다른 교점이 `k`개라면, 새 직선은 `k + 1`개의 조각으로 나뉘고 그만큼 새 영역을 추가합니다.

```text
regions starts at 1
for each new unique line L:
    regions += distinct_intersections_on_L + 1
```

모든 직선이 서로 평행하지 않고 세 직선이 한 점에서 만나지 않는 일반 위치라면 `N(N+1)/2 + 1`입니다. 하지만 실제 문제는 평행, 중복, concurrency가 있으므로 직접 세는 편이 안전합니다.

## 직선 정규화

직선을 아래 형태로 둡니다.

```text
a*x + b*y + c = 0
```

동일한 직선은 `(a, b, c)`를 gcd로 나누고 부호를 통일하면 같은 tuple이 됩니다.

```cpp compile-check
#include <cstdlib>
#include <numeric>
#include <tuple>
using namespace std;

struct NormalizedLine {
    long long a;
    long long b;
    long long c;
};

long long absLongLong(long long x) {
    return x < 0 ? -x : x;
}

NormalizedLine normalizeLine(long long a, long long b, long long c) {
    long long g = gcd(absLongLong(a), gcd(absLongLong(b), absLongLong(c)));
    if (g == 0) {
        return {0, 0, 0};
    }
    a /= g;
    b /= g;
    c /= g;

    if (a < 0 || (a == 0 && b < 0) || (a == 0 && b == 0 && c < 0)) {
        a = -a;
        b = -b;
        c = -c;
    }
    return {a, b, c};
}

tuple<long long, long long, long long> lineKey(const NormalizedLine& line) {
    return {line.a, line.b, line.c};
}
```

입력이 두 점으로 주어지면 `a = y1 - y2`, `b = x2 - x1`, `c = -(a*x1 + b*y1)`로 만들 수 있습니다.

## 교점 표현

두 직선

```text
a1*x + b1*y + c1 = 0
a2*x + b2*y + c2 = 0
```

의 교점은 determinant로 계산합니다.

```text
det = a1*b2 - a2*b1
x = (b1*c2 - b2*c1) / det
y = (c1*a2 - c2*a1) / det
```

`det == 0`이면 평행입니다. 중복 직선은 이미 정규화 단계에서 제거하는 편이 좋습니다.

## 영역 수 구현

아래 구현은 무한 직선 arrangement의 영역 수를 셉니다. 각 새 직선 위의 서로 다른 교점만 세기 위해 rational pair를 set에 넣습니다.

```cpp compile-check
#include <numeric>
#include <set>
#include <tuple>
#include <vector>
using namespace std;

struct Fraction {
    long long num = 0;
    long long den = 1;

    Fraction() = default;

    Fraction(long long n, long long d) {
        if (d < 0) {
            n = -n;
            d = -d;
        }
        long long g = gcd(n < 0 ? -n : n, d);
        num = n / g;
        den = d / g;
    }

    bool operator<(const Fraction& other) const {
        return (__int128)num * other.den < (__int128)other.num * den;
    }
};

struct Line {
    long long a;
    long long b;
    long long c;
};

Line normalized(long long a, long long b, long long c) {
    long long aa = a < 0 ? -a : a;
    long long bb = b < 0 ? -b : b;
    long long cc = c < 0 ? -c : c;
    long long g = gcd(aa, gcd(bb, cc));
    a /= g;
    b /= g;
    c /= g;
    if (a < 0 || (a == 0 && b < 0) || (a == 0 && b == 0 && c < 0)) {
        a = -a;
        b = -b;
        c = -c;
    }
    return {a, b, c};
}

bool parallel(const Line& x, const Line& y) {
    return x.a * y.b == y.a * x.b;
}

pair<Fraction, Fraction> intersectionPoint(const Line& x, const Line& y) {
    long long det = x.a * y.b - y.a * x.b;
    long long nx = x.b * y.c - y.b * x.c;
    long long ny = x.c * y.a - y.c * x.a;
    return {Fraction(nx, det), Fraction(ny, det)};
}

long long countLineArrangementRegions(vector<Line> input) {
    vector<Line> lines;
    set<tuple<long long, long long, long long>> seen;

    for (Line line : input) {
        line = normalized(line.a, line.b, line.c);
        auto key = make_tuple(line.a, line.b, line.c);
        if (seen.insert(key).second) {
            lines.push_back(line);
        }
    }

    long long regions = 1;
    vector<Line> added;

    for (const Line& line : lines) {
        set<pair<Fraction, Fraction>> points;
        for (const Line& prev : added) {
            if (!parallel(line, prev)) {
                points.insert(intersectionPoint(line, prev));
            }
        }
        regions += (long long)points.size() + 1;
        added.push_back(line);
    }

    return regions;
}
```

이 구현은 `long long` 범위에서 determinant 곱셈이 안전하다는 전제를 둡니다. 좌표와 계수가 크면 `__int128` 기반 fraction key가 필요합니다.

## Segment Arrangement와 Sweep

선분 arrangement는 무한 직선보다 어렵습니다.

| 추가 고려 | 이유 |
| --- | --- |
| endpoint 이벤트 | 선분은 시작/끝이 있다 |
| active order | sweep line 위 y순서가 바뀐다 |
| 교차 이벤트 | 두 선분이 만나면 active order swap |
| overlap | 같은 직선 위에서 겹치는 구간 처리 |

직선 arrangement의 region count는 교점 집합만 정확히 세면 되지만, 선분 arrangement는 event scheduling과 degeneracy 처리가 핵심입니다.

## Euler Formula 관점

planar subdivision으로 영역 수를 세는 문제는 Euler formula로도 접근합니다.

```text
V - E + F = 1 + C
```

여기서 `C`는 connected component 수입니다. 선분 arrangement에서는 교점을 vertex로 쪼개고 edge piece 개수를 세어 face 수를 구하는 방식이 자주 나옵니다.

## 시간 복잡도

| 문제 | 단순 접근 | sweep 접근 |
| --- | ---: | ---: |
| 무한 직선 영역 수 | `O(N^2 log N)` | 보통 불필요 |
| 모든 선분 교차 판정 | `O(N^2)` | `O((N+K) log N)` |
| arrangement face count | 교점 수에 따라 큼 | 구현 복잡 |

`N`이 2000 이하이면 exact pairwise가 더 안전할 때가 많습니다. `N`이 크고 교점 수가 작을 때 sweep이 효과적입니다.

## 자주 하는 실수

1. 같은 직선을 여러 번 추가해 영역 수를 늘린다.
2. 평행 직선을 교점이 있는 것처럼 처리한다.
3. 세 직선이 한 점에서 만날 때 교점 수를 중복으로 센다.
4. rational 좌표를 double로 비교한다.
5. 선분 문제를 무한 직선 공식으로 푼다.
