# Rotating Calipers

Rotating Calipers는 Convex Hull 위에서 서로 마주 보는 점이나 변을 선형 시간에 훑는 기법입니다. 모든 점 쌍을 비교하면 `O(n^2)`이지만, 볼록 다각형 위에서는 포인터가 한 방향으로만 움직이므로 지름, 폭, antipodal pair 같은 값을 `O(n)`에 구할 수 있습니다.


입력은 중복점·연속한 일직선 점을 제거한 반시계 볼록 hull이며 좌표 절댓값은 `10^9` 이하입니다. 폭에서 외적 절댓값은 삼각형 넓이의 두 배이므로 이를 변 길이로 나눕니다.

## 언제 필요한가

Convex Hull까지 만든 뒤 아래 질문이 나오면 Rotating Calipers를 의심합니다.

| 질문 | Calipers 관점 |
| --- | --- |
| 점 집합에서 가장 먼 두 점은? | hull의 antipodal pair 중 최대 거리 |
| 볼록 다각형의 지름은? | 회전하는 두 지지선 사이의 점 쌍 |
| 볼록 다각형의 최소 폭은? | 한 변과 반대편 점 사이 거리 |
| 두 볼록 다각형의 거리나 접선은? | 두 hull의 포인터를 함께 회전 |

핵심은 모든 점이 아니라 Convex Hull 위의 점만 보면 된다는 점입니다. 가장 먼 두 점은 항상 hull 위에 있고, 내부 점은 지름 후보가 될 수 없습니다.

## Antipodal pair

볼록 다각형의 한 변 `i -> i+1`을 기준으로, 반대편 점 `j`를 움직이며 삼각형 면적이 더 커지는 동안 전진합니다.

```text
area(edge i, point j+1) > area(edge i, point j)
이면 j를 한 칸 이동
```

다각형이 반시계 방향이고 중복 없는 hull이라면 `i`가 한 바퀴 도는 동안 `j`도 한 방향으로만 움직입니다. 그래서 전체 while 반복 횟수는 `O(n)`입니다.

## 지름 구하기

아래 구현은 hull이 반시계 방향이며, 첫 점을 끝에 다시 붙이지 않은 상태라고 가정합니다. 반환값은 최대 거리의 제곱입니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct Point {
    long long x;
    long long y;
};

Point sub(Point a, Point b) {
    return {a.x - b.x, a.y - b.y};
}

long long cross(Point a, Point b) {
    return a.x * b.y - a.y * b.x;
}

long long area2(Point a, Point b, Point c) {
    return cross(sub(b, a), sub(c, a));
}

long long absll(long long x) {
    return x >= 0 ? x : -x;
}

long long dist2(Point a, Point b) {
    long long dx = a.x - b.x;
    long long dy = a.y - b.y;
    return dx * dx + dy * dy;
}

long long convexDiameter2(const vector<Point>& hull) {
    int n = (int)hull.size();
    if (n <= 1) {
        return 0;
    }
    if (n == 2) {
        return dist2(hull[0], hull[1]);
    }

    int j = 1;
    long long best = 0;
    for (int i = 0; i < n; ++i) {
        int ni = (i + 1) % n;
        while (true) {
            int nj = (j + 1) % n;
            long long currentArea = absll(area2(hull[i], hull[ni], hull[j]));
            long long nextArea = absll(area2(hull[i], hull[ni], hull[nj]));
            if (nextArea > currentArea) {
                j = nj;
            } else {
                break;
            }
        }
        best = max(best, dist2(hull[i], hull[j]));
        best = max(best, dist2(hull[ni], hull[j]));
    }
    return best;
}
```

거리 자체를 출력해야 하면 마지막에 `sqrt(best)`를 합니다. 정수 비교만 필요하면 제곱 거리로 끝까지 비교하는 것이 안전합니다.

## 왜 선형인가

겉보기에는 각 변마다 while을 돌기 때문에 `O(n^2)`처럼 보입니다. 하지만 `j`는 줄어들지 않고 한 방향으로만 움직입니다. `i`가 한 바퀴 도는 동안 `j`도 최대 한 바퀴 정도만 돕니다.

이 성질은 볼록성에서 나옵니다. 한 변에 대한 반대편 점까지의 면적은 증가하다가 감소합니다. 그래서 더 커지는 동안만 이동하면 최댓값을 놓치지 않습니다.

```text
i edge:  hull[i] -> hull[i+1]
j:       반대편 후보

while area(i, j+1) > area(i, j):
    j++
```

면적 비교는 외적의 절댓값으로 합니다. 실제 높이가 필요하면 변 길이로 나눠야 하지만, 같은 변에 대해 비교할 때는 나누지 않아도 순서가 같습니다.

## 폭과 지름의 차이

지름은 점과 점 사이의 최대 거리입니다. 폭(width)은 어떤 방향으로 두 평행 지지선 사이의 최소 거리입니다. 둘 다 calipers로 다루지만 목적이 다릅니다.

| 값 | 기준 | 대표 계산 |
| --- | --- | --- |
| 지름 | 점-점 거리 최대 | antipodal point pair의 `dist2` |
| 폭 | 변-점 거리 최소 | 각 변과 반대편 점의 높이 |
| 최소 bounding rectangle | 회전 방향의 가로/세로 | 여러 caliper를 동시에 회전 |

폭은 `area(edge, point) / edge_length`로 높이를 구합니다. 정수 비교만으로 끝나지 않고 실수 값이 필요할 수 있으므로 오차 처리까지 확인해야 합니다.

## 최소 폭 구현

위 지름 구현의 `Point`, `sub`, `cross`, `absll`, `dist2`를 그대로 사용합니다. 같은 코드 뒤에 아래 함수를 붙이면 같은 hull에서 최소 폭을 구할 수 있습니다. 입력 전제와 포인터 전진 조건도 같습니다.

```cpp
#include <cmath>

double minimumWidth(const vector<Point>& hull) {
    int n = (int)hull.size();
    if (n <= 2) {
        return 0.0;
    }

    int j = 1;
    double best = 1e100;

    for (int i = 0; i < n; ++i) {
        int nextI = (i + 1) % n;
        Point edge = sub(hull[nextI], hull[i]);

        while (true) {
            int nextJ = (j + 1) % n;
            long long current = absll(cross(edge, sub(hull[j], hull[i])));
            long long next = absll(cross(edge, sub(hull[nextJ], hull[i])));
            if (next > current) {
                j = nextJ;
            } else {
                break;
            }
        }

        double height = (double)absll(
            cross(edge, sub(hull[j], hull[i]))
        ) / sqrt((double)dist2(hull[nextI], hull[i]));
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

접선 이동 규칙은 두 다각형의 외부/내부 접선과 방향에 따라 다릅니다. 양쪽 support 조건을 먼저 정해야 합니다.

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

## Hull 준비와 동률 처리

Rotating Calipers 전에 hull의 형식을 통일해야 합니다.

1. 점이 반시계 방향으로 정렬되어 있어야 하며 방향도 한쪽으로만 회전한다.
2. 첫 점을 마지막에 중복으로 붙이지 않는다.
3. 중복 점을 제거한다.
4. collinear 점과 support point 동률 처리 정책을 고정한다. 위 지름·폭 구현은 중간 collinear 점을 제거하고 면적이 엄격히 커질 때 전진한다.
5. hull 크기 `1`, `2`를 별도로 처리한다.

Convex Hull 구현에서 collinear 경계 점을 모두 남기면 calipers가 같은 직선 위 점들을 더 많이 보게 됩니다. 대부분의 지름 문제에서는 중간 collinear 점을 제거해도 답이 유지되지만, 모든 antipodal pair를 출력해야 하는 문제라면 정책을 더 조심해야 합니다.

## 시간 복잡도

| 작업 | 시간 |
| --- | ---: |
| Convex Hull 생성 | `O(n log n)` |
| Hull 위 지름 계산 | `O(h)` |
| 모든 점 쌍 비교 | `O(n^2)` |
| 폭 계산 | `O(h)` |

`h`는 hull 위 점 개수입니다. 전체 점에서 바로 calipers를 쓰는 것이 아니라, 먼저 hull을 만들고 그 위에서만 실행합니다.
