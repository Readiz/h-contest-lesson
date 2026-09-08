# Minkowski Sum

Minkowski Sum은 두 점 집합 `A`, `B`의 모든 합 `a + b`로 새 집합을 만드는 연산입니다. 볼록 다각형끼리의 합은 다시 볼록 다각형이 되므로, 장애물 확장, 두 물체의 충돌 판정, 볼록 다각형 사이 거리 같은 문제를 기하 문제 하나로 정리할 수 있습니다.


이 edge-merge 구현은 빈 집합 또는 꼭짓점 3개 이상의 엄격한 CCW 볼록 다각형을 입력받습니다. 중복·연속 collinear 꼭짓점은 사전에 제거하고 좌표 절댓값은 10^8 이하로 둡니다. 점·선분 입력은 평행이동 또는 별도 퇴화 처리가 필요합니다.

## 문제 신호

| 문제 표현 | Minkowski Sum 관점 |
| --- | --- |
| 두 도형을 더하거나 한 도형을 다른 도형만큼 확장 | polygon sum |
| 이동하는 물체가 장애물과 부딪히는지 확인 | obstacle + reflected shape |
| 두 convex polygon 사이 거리를 구함 | `A + (-B)`가 원점을 포함하는지/얼마나 떨어졌는지 |
| 모든 `a + b` 후보의 convex hull 필요 | hull of pairwise sums |
| 점 집합에 벡터 집합을 더함 | translation closure |

모든 점쌍을 더하면 `O(nm)`입니다. 두 입력이 convex polygon이면 edge vector를 한 바퀴 merge해서 `O(n + m)`에 합 다각형을 만들 수 있습니다.

## 정의

두 집합의 Minkowski sum은 아래와 같습니다.

```text
A + B = { a + b | a in A, b in B }
```

두 convex polygon의 합은 convex입니다. 각 polygon의 boundary를 따라가며 edge direction을 angle 순서로 합치면 합 polygon의 boundary가 됩니다.

## 준비 조건

구현 전에 polygon 형식을 통일합니다.

1. 꼭짓점은 반시계 방향이다.
2. 첫 점을 마지막에 다시 넣지 않는다.
3. 중복 점을 제거한다.
4. 연속한 collinear 점은 필요하면 제거한다.
5. 시작점은 `y`가 가장 작고, tie는 `x`가 가장 작은 점으로 회전한다.

시작점을 맞추지 않으면 edge vector merge 순서가 중간에서 끊겨 잘못된 polygon이 나옵니다.

## 구현

아래 코드는 convex polygon 두 개의 Minkowski sum을 계산합니다. 입력 polygon은 반시계 방향이라고 가정합니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct PointMinkowski {
    long long x = 0;
    long long y = 0;

    bool operator<(const PointMinkowski& other) const {
        if (y != other.y) {
            return y < other.y;
        }
        return x < other.x;
    }

    bool operator==(const PointMinkowski& other) const {
        return x == other.x && y == other.y;
    }
};

PointMinkowski operator+(PointMinkowski a, PointMinkowski b) {
    return {a.x + b.x, a.y + b.y};
}

PointMinkowski operator-(PointMinkowski a, PointMinkowski b) {
    return {a.x - b.x, a.y - b.y};
}

long long crossMinkowski(PointMinkowski a, PointMinkowski b) {
    return a.x * b.y - a.y * b.x;
}

vector<PointMinkowski> normalizeConvexPolygon(vector<PointMinkowski> polygon) {
    if (polygon.empty()) {
        return polygon;
    }

    int start = min_element(polygon.begin(), polygon.end()) - polygon.begin();
    rotate(polygon.begin(), polygon.begin() + start, polygon.end());

    vector<PointMinkowski> cleaned;
    for (PointMinkowski point : polygon) {
        if (cleaned.empty() || !(cleaned.back() == point)) {
            cleaned.push_back(point);
        }
    }
    if (cleaned.size() > 1 && cleaned.front() == cleaned.back()) {
        cleaned.pop_back();
    }
    return cleaned;
}

vector<PointMinkowski> removeCollinear(vector<PointMinkowski> polygon) {
    vector<PointMinkowski> result;
    for (PointMinkowski point : polygon) {
        while (result.size() >= 2) {
            PointMinkowski a = result[result.size() - 2];
            PointMinkowski b = result[result.size() - 1];
            if (crossMinkowski(b - a, point - b) == 0) {
                result.pop_back();
            } else {
                break;
            }
        }
        result.push_back(point);
    }

    while (result.size() >= 3 && crossMinkowski(
        result.back() - result[result.size() - 2],
        result.front() - result.back()
    ) == 0) {
        result.pop_back();
    }
    return result;
}

vector<PointMinkowski> minkowskiSum(
    vector<PointMinkowski> left,
    vector<PointMinkowski> right
) {
    left = normalizeConvexPolygon(left);
    right = normalizeConvexPolygon(right);
    if (left.empty() || right.empty()) return {};

    int n = (int)left.size();
    int m = (int)right.size();
    vector<PointMinkowski> edgeLeft(n);
    vector<PointMinkowski> edgeRight(m);

    for (int i = 0; i < n; ++i) {
        edgeLeft[i] = left[(i + 1) % n] - left[i];
    }
    for (int i = 0; i < m; ++i) {
        edgeRight[i] = right[(i + 1) % m] - right[i];
    }

    vector<PointMinkowski> result;
    result.push_back(left[0] + right[0]);

    int i = 0;
    int j = 0;
    while (i < n || j < m) {
        long long crossValue = 0;
        if (i < n && j < m) {
            crossValue = crossMinkowski(edgeLeft[i], edgeRight[j]);
        }

        PointMinkowski step{0, 0};
        if (j == m || (i < n && crossValue > 0)) {
            step = edgeLeft[i++];
        } else if (i == n || crossValue < 0) {
            step = edgeRight[j++];
        } else {
            step = edgeLeft[i++] + edgeRight[j++];
        }
        result.push_back(result.back() + step);
    }

    if (!result.empty()) {
        result.pop_back();
    }
    return removeCollinear(result);
}
```

좌표 곱이 `long long`을 넘을 수 있으면 외적 계산을 `__int128`로 바꿉니다.

## 충돌 판정으로 보기

두 convex polygon `A`, `B`가 교차하는지는 `A + (-B)`가 원점을 포함하는지로 볼 수 있습니다. 여기서 `-B`는 모든 점에 `-1`을 곱한 polygon입니다.

```text
0 in A + (-B)  <=>  A와 B가 만난다
```

이 관점은 로봇이 움직일 수 있는 공간을 계산할 때 자주 쓰입니다. 움직이는 물체의 모양을 장애물에 더해 두면, 물체를 점 하나로 보고 경로를 찾을 수 있습니다.

## 거리와 Support Function

Minkowski sum은 support function으로도 해석할 수 있습니다.

```text
support(A + B, dir) = support(A, dir) + support(B, dir)
```

즉 어떤 방향으로 가장 멀리 있는 점을 찾는 연산이 두 polygon에서 분리됩니다. 이 성질 때문에 rotating calipers, tangent, width 계산과 잘 이어집니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| 시작점 회전 | `O(n + m)` |
| edge merge | `O(n + m)` |
| collinear 정리 | `O(n + m)` |
| naive pairwise sum 후 hull | `O(nm log(nm))` |

일반 점 집합에서 먼저 hull을 취하면 원래 이산 Minkowski sum이 아니라 그 convex hull을 계산하게 됩니다. 목적이 모든 합점의 hull일 때만 이 변환을 사용합니다.
