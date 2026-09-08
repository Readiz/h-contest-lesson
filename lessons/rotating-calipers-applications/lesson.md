# Rotating Calipers Applications

Rotating Calipers Applications는 기본 지름 계산을 넘어 width, tangent, 두 convex polygon 사이 거리, 최소 enclosing rectangle 같은 응용을 다룹니다. 공통 원리는 convex polygon 위의 support direction이 한 방향으로만 이동한다는 점입니다.

## 문제 신호

| 문제 표현 | Calipers 응용 관점 |
| --- | --- |
| convex polygon의 최소 폭 | edge와 반대쪽 support point |
| 두 convex polygon의 최단거리 | support direction 또는 Minkowski difference |
| 두 hull의 공통 접선 | 두 polygon 포인터 동시 회전 |
| 점 집합을 감싸는 최소 면적 직사각형 | 네 방향 caliper |
| 모든 방향에서 가장 먼 점 필요 | support function |

핵심은 방향이 회전할 때 최적 support point도 polygon 순서대로만 이동한다는 사실입니다.

## Width 계산

볼록 다각형의 width는 어떤 방향으로 두 평행 support line 사이의 거리입니다. 한 변을 기준선으로 잡으면 반대편에서 가장 먼 점까지의 높이가 그 방향의 폭입니다.

```text
height = abs(cross(edge, point - vertex)) / |edge|
```

모든 edge 방향을 보면 최소 width를 찾을 수 있습니다.

## 최소 폭 구현

아래 코드는 convex polygon의 최소 폭을 구합니다. 입력 hull은 반시계 방향이고 첫 점을 끝에 다시 붙이지 않습니다.

```cpp compile-check
#include <cmath>
#include <vector>
using namespace std;

struct PointCalipersApp {
    long long x = 0;
    long long y = 0;
};

PointCalipersApp operator-(PointCalipersApp a, PointCalipersApp b) {
    return {a.x - b.x, a.y - b.y};
}

long long crossCalipersApp(PointCalipersApp a, PointCalipersApp b) {
    return a.x * b.y - a.y * b.x;
}

long long norm2CalipersApp(PointCalipersApp a) {
    return a.x * a.x + a.y * a.y;
}

long long absLongLongCalipersApp(long long value) {
    return value < 0 ? -value : value;
}

double minimumWidth(const vector<PointCalipersApp>& hull) {
    int n = (int)hull.size();
    if (n <= 2) {
        return 0.0;
    }

    int j = 1;
    double best = 1e100;

    for (int i = 0; i < n; ++i) {
        int nextI = (i + 1) % n;
        PointCalipersApp edge = hull[nextI] - hull[i];

        while (true) {
            int nextJ = (j + 1) % n;
            long long current = absLongLongCalipersApp(crossCalipersApp(edge, hull[j] - hull[i]));
            long long next = absLongLongCalipersApp(crossCalipersApp(edge, hull[nextJ] - hull[i]));
            if (next > current) {
                j = nextJ;
            } else {
                break;
            }
        }

        double height = (double)absLongLongCalipersApp(
            crossCalipersApp(edge, hull[j] - hull[i])
        ) / sqrt((double)norm2CalipersApp(edge));
        if (height < best) {
            best = height;
        }
    }

    return best;
}
```

폭은 실수 값이므로 출력 오차 조건을 확인합니다. 비교만 필요하면 제곱 형태로 변형할 수 있지만 구현이 더 복잡해집니다.

## 두 Polygon 사이 거리

두 convex polygon의 거리는 다음 두 방식으로 볼 수 있습니다.

| 방식 | 설명 |
| --- | --- |
| edge-point 거리 sweep | 두 boundary의 후보 edge/point를 함께 이동 |
| Minkowski difference | `A + (-B)`와 원점 사이 거리 |

교차 여부부터 확인해야 합니다. 교차하면 거리는 `0`입니다. 교차하지 않을 때는 두 polygon의 edge direction이 만드는 후보를 훑습니다.

## Tangent와 Support Line

한 점 `p`에서 convex polygon에 그을 수 있는 tangent는 support line이 바뀌는 꼭짓점입니다. 두 convex polygon의 common tangent도 두 support point가 동시에 움직이는 문제입니다.

```text
while next point makes a better support line:
    pointer++
```

이 패턴은 convex hull trick의 "기울기 순서로 포인터 전진"과도 닮았습니다.

## 최소 면적 직사각형

최소 면적 enclosing rectangle은 한 변이 hull의 어떤 edge와 평행하다는 성질을 씁니다. 그래서 edge direction을 돌리며 네 support point를 관리합니다.

| caliper | 의미 |
| --- | --- |
| bottom | 현재 edge |
| top | edge normal 방향으로 가장 먼 점 |
| left | edge 반대 방향 support |
| right | edge 방향 support |

구현은 지름보다 훨씬 실수와 degeneracy가 많습니다. 문제에서 꼭 필요하지 않으면 width, diameter처럼 더 단순한 값부터 분리해 구현하는 편이 안전합니다.

## Monotone Pointer 조건

calipers가 성립하려면 후보 함수가 방향을 따라 unimodal이어야 합니다.

1. 입력이 convex polygon이어야 한다.
2. 방향이 한쪽으로만 회전해야 한다.
3. support point tie를 일관되게 처리해야 한다.
4. collinear edge에서 같은 방향 edge를 합치거나 tie 정책을 정해야 한다.

이 조건이 깨지면 포인터가 되돌아가야 하므로 `O(n)` sweep이 틀립니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| diameter | `O(h)` |
| width | `O(h)` |
| 두 convex polygon tangent | `O(h1 + h2)` |
| 최소 enclosing rectangle | `O(h)` |
| convex hull 생성 포함 | `O(n log n)` |

`h`는 hull 위 꼭짓점 수입니다.

## 자주 하는 실수

1. polygon 내부 점까지 포함해 calipers를 돌린다.
2. width에서 height를 edge length로 나누지 않는다.
3. 같은 방향 edge tie에서 포인터를 하나만 움직여 후보를 놓친다.
4. 두 polygon 문제에서 교차 여부를 먼저 보지 않는다.
5. 최소 면적 직사각형의 네 포인터를 같은 기준 방향으로 업데이트하지 않는다.
