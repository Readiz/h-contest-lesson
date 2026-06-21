# Rotating Calipers

Rotating Calipers는 Convex Hull 위에서 서로 마주 보는 점이나 변을 선형 시간에 훑는 기법입니다. 모든 점 쌍을 비교하면 `O(n^2)`이지만, 볼록 다각형 위에서는 포인터가 한 방향으로만 움직이므로 지름, 폭, antipodal pair 같은 값을 `O(n)`에 구할 수 있습니다.

이 레슨은 Convex Hull 다음 단계로 봅니다.

1. Convex Hull을 반시계 방향으로 준비한다.
2. 한 변을 기준으로 반대편에서 면적이 커지는 동안 포인터를 움직인다.
3. 포인터가 되돌아가지 않는 성질로 전체를 선형 시간에 처리한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: CCW, 외적, Convex Hull
- 함께 보면 좋은 레슨: 기하 기본: CCW, 선분 교차, Convex Hull
- 다음에 볼 레슨: Sweep Line Geometry

## 1. 언제 필요한가

Convex Hull까지 만든 뒤 아래 질문이 나오면 Rotating Calipers를 의심합니다.

| 질문 | Calipers 관점 |
| --- | --- |
| 점 집합에서 가장 먼 두 점은? | hull의 antipodal pair 중 최대 거리 |
| 볼록 다각형의 지름은? | 회전하는 두 지지선 사이의 점 쌍 |
| 볼록 다각형의 최소 폭은? | 한 변과 반대편 점 사이 거리 |
| 두 볼록 다각형의 거리나 접선은? | 두 hull의 포인터를 함께 회전 |

핵심은 모든 점이 아니라 Convex Hull 위의 점만 보면 된다는 점입니다. 가장 먼 두 점은 항상 hull 위에 있고, 내부 점은 지름 후보가 될 수 없습니다.

## 2. Antipodal pair

볼록 다각형의 한 변 `i -> i+1`을 기준으로, 반대편 점 `j`를 움직이며 삼각형 면적이 더 커지는 동안 전진합니다.

```text
area(edge i, point j+1) > area(edge i, point j)
이면 j를 한 칸 이동
```

다각형이 반시계 방향이고 중복 없는 hull이라면 `i`가 한 바퀴 도는 동안 `j`도 한 방향으로만 움직입니다. 그래서 전체 while 반복 횟수는 `O(n)`입니다.

## 3. 지름 구하기

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

## 4. 왜 선형인가

겉보기에는 각 변마다 while을 돌기 때문에 `O(n^2)`처럼 보입니다. 하지만 `j`는 줄어들지 않고 한 방향으로만 움직입니다. `i`가 한 바퀴 도는 동안 `j`도 최대 한 바퀴 정도만 돕니다.

이 성질은 볼록성에서 나옵니다. 한 변에 대한 반대편 점까지의 면적은 증가하다가 감소합니다. 그래서 더 커지는 동안만 이동하면 최댓값을 놓치지 않습니다.

```text
i edge:  hull[i] -> hull[i+1]
j:       반대편 후보

while area(i, j+1) > area(i, j):
    j++
```

면적 비교는 외적의 절댓값으로 합니다. 실제 높이가 필요하면 변 길이로 나눠야 하지만, 같은 변에 대해 비교할 때는 나누지 않아도 순서가 같습니다.

## 5. 폭과 지름의 차이

지름은 점과 점 사이의 최대 거리입니다. 폭(width)은 어떤 방향으로 두 평행 지지선 사이의 최소 거리입니다. 둘 다 calipers로 다루지만 목적이 다릅니다.

| 값 | 기준 | 대표 계산 |
| --- | --- | --- |
| 지름 | 점-점 거리 최대 | antipodal point pair의 `dist2` |
| 폭 | 변-점 거리 최소 | 각 변과 반대편 점의 높이 |
| 최소 bounding rectangle | 회전 방향의 가로/세로 | 여러 caliper를 동시에 회전 |

폭은 `area(edge, point) / edge_length`로 높이를 구합니다. 정수 비교만으로 끝나지 않고 실수 값이 필요할 수 있으므로 오차 처리까지 확인해야 합니다.

## 6. Hull 준비 조건

Rotating Calipers 전에 hull의 형식을 통일해야 합니다.

1. 점이 반시계 방향으로 정렬되어 있어야 한다.
2. 첫 점을 마지막에 중복으로 붙이지 않는다.
3. 중복 점을 제거한다.
4. collinear 점을 포함할지 제거할지 문제 요구와 맞춘다.
5. hull 크기 `1`, `2`를 별도로 처리한다.

Convex Hull 구현에서 collinear 경계 점을 모두 남기면 calipers가 같은 직선 위 점들을 더 많이 보게 됩니다. 대부분의 지름 문제에서는 중간 collinear 점을 제거해도 답이 유지되지만, 모든 antipodal pair를 출력해야 하는 문제라면 정책을 더 조심해야 합니다.

## 7. 시간 복잡도

| 작업 | 시간 |
| --- | ---: |
| Convex Hull 생성 | `O(n log n)` |
| Hull 위 지름 계산 | `O(h)` |
| 모든 점 쌍 비교 | `O(n^2)` |
| 폭 계산 | `O(h)` |

`h`는 hull 위 점 개수입니다. 전체 점에서 바로 calipers를 쓰는 것이 아니라, 먼저 hull을 만들고 그 위에서만 실행합니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| hull이 정렬되지 않은 상태에서 실행 | 포인터 이동 의미가 깨짐 | Convex Hull 결과만 입력 |
| 첫 점을 끝에 중복으로 붙임 | 인덱스 순환 off-by-one | `hull.size()` 기준 modulo 사용 |
| `j`를 매번 `0`으로 초기화 | `O(n^2)` 또는 중복 계산 | `j`를 유지하며 전진 |
| 거리 비교에 `sqrt` 사용 | 오차와 불필요한 비용 | 제곱 거리 비교 |
| hull 크기 1, 2 처리 누락 | 런타임 에러 | 작은 hull 별도 반환 |
| collinear 정책을 확인하지 않음 | 후보 점 누락/중복 | hull 생성 조건 확인 |

## 9. 문제를 볼 때 체크할 조건

1. 전체 점이 아니라 Convex Hull 위에서 보면 되는 문제인가?
2. 최댓거리, 최소폭, bounding rectangle 중 무엇을 묻는가?
3. 답이 거리 제곱인지 실제 거리인지 확인했는가?
4. 점 개수가 1 또는 2인 입력이 가능한가?
5. hull의 collinear 경계 점 포함 여부가 답에 영향을 주는가?
6. `long long` 외적으로 좌표 곱을 감당할 수 있는가?

Rotating Calipers는 볼록 다각형 위 포인터가 뒤로 가지 않는다는 사실을 쓰는 기법입니다. 먼저 hull을 정확히 만들고, 한 변에 대한 반대편 후보가 언제 전진하는지만 고정하면 지름 문제는 안정적으로 풀 수 있습니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: Convex Hull 지름 `/practice/...` 문제 필요 | antipodal pair와 제곱 거리 계산 | diameter |
| 표준 | TODO: 가장 먼 두 점 `/practice/...` 문제 필요 | hull 생성 후 calipers 적용 | farthest pair |
| 응용 | TODO: 볼록 다각형 폭 `/practice/...` 문제 필요 | 변-점 높이와 외적 비교 | width |
| 함정 | TODO: collinear 경계 점 처리 `/practice/...` 문제 필요 | hull 정책과 작은 입력 처리 | collinear, edge case |
