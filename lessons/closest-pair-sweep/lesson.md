# Closest Pair Sweep

Closest Pair는 평면 위 점들 중 가장 가까운 두 점의 거리를 찾는 문제입니다. 모든 쌍을 비교하면 `O(N^2)`이지만, 점을 x좌표 순서로 훑으며 y좌표 active set을 유지하면 `O(N log N)`에 처리할 수 있습니다.

이 레슨은 Sweep Line Geometry 이후에 보는 거리 기반 sweep 패턴입니다.

1. 점을 x좌표 기준으로 정렬한다.
2. 현재 최단거리보다 x 차이가 큰 점을 active set에서 제거한다.
3. y좌표가 가까운 후보만 검사한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 정렬, set, 기하 거리, Sweep Line
- 함께 보면 좋은 레슨: Sweep Line Geometry, 기하 기본, Rotating Calipers
- 다음에 볼 레슨: divide-and-conquer closest pair, Delaunay/Voronoi intuition

## 1. 문제 신호

| 문제 표현 | 접근 |
| --- | --- |
| 가장 가까운 두 점 | closest pair |
| 모든 쌍 비교가 너무 크다 | sweep 또는 divide-and-conquer |
| 좌표가 정수이고 거리 제곱으로 비교 가능 | overflow 주의 |
| 동점 쌍이나 점 index 필요 | pair 복원 |

거리 비교는 제곱 거리로 해도 됩니다. 제곱근을 매번 계산할 필요가 없습니다.

## 2. Sweep 아이디어

점을 x좌표 오름차순으로 처리합니다. 현재까지의 최단 제곱거리 `best`가 있을 때, 현재 점과 x 차이의 제곱이 `best` 이상인 오래된 점은 더 이상 후보가 될 수 없습니다.

남은 active set에서는 y좌표 차이의 제곱도 `best`보다 작은 점만 보면 됩니다.

```text
|x_i - x_j|^2 < best
|y_i - y_j|^2 < best
```

이 조건 덕분에 active set 전체가 아니라 현재 점 주변의 좁은 y 범위만 검사합니다.

## 3. 구현

아래 구현은 가장 가까운 두 점의 제곱거리를 반환합니다.

```cpp compile-check
#include <algorithm>
#include <limits>
#include <set>
#include <vector>
using namespace std;

struct Point {
    long long x;
    long long y;
    int id;
};

long long squaredDistance(const Point& a, const Point& b) {
    long long dx = a.x - b.x;
    long long dy = a.y - b.y;
    return dx * dx + dy * dy;
}

long long closestPairSquared(vector<Point> points) {
    sort(points.begin(), points.end(), [](const Point& a, const Point& b) {
        if (a.x != b.x) {
            return a.x < b.x;
        }
        return a.y < b.y;
    });

    const long long INF = numeric_limits<long long>::max() / 4;
    long long best = INF;
    set<pair<long long, int>> activeByY;
    int left = 0;

    for (int i = 0; i < (int)points.size(); ++i) {
        while (left < i) {
            long long dx = points[i].x - points[left].x;
            if (dx * dx < best) {
                break;
            }
            activeByY.erase({points[left].y, left});
            ++left;
        }

        long long limit = 1;
        while (limit * limit < best) {
            limit <<= 1;
        }

        auto it = activeByY.lower_bound({points[i].y - limit, -1});
        while (it != activeByY.end() && it->first <= points[i].y + limit) {
            best = min(best, squaredDistance(points[i], points[it->second]));
            ++it;
        }

        activeByY.insert({points[i].y, i});
    }

    return best;
}
```

`limit` 계산은 단순화를 위해 2의 거듭제곱 상한을 잡았습니다. 정확한 integer sqrt를 써도 되고, `dy * dy < best`를 loop 안에서 직접 검사해도 됩니다.

## 4. 중복 점

같은 좌표의 점이 두 개 이상 있으면 답은 0입니다. 정렬 후 인접한 같은 점을 먼저 검사하면 빠르게 처리할 수 있습니다.

```text
if points[i].x == points[i-1].x and points[i].y == points[i-1].y:
    answer = 0
```

답이 0이면 더 줄어들 수 없으므로 즉시 종료할 수 있습니다.

## 5. Divide-and-Conquer와 비교

Closest Pair의 표준 풀이에는 divide-and-conquer도 있습니다.

| 방식 | 장점 | 주의점 |
| --- | --- | --- |
| Sweep set | 구현이 직관적, 온라인 느낌 | set 후보 탐색과 limit 처리 |
| Divide-and-conquer | 이론적 후보 수가 명확 | y정렬 병합 구현 필요 |

둘 다 `O(N log N)`입니다. 대회에서는 구현에 익숙한 쪽을 선택하면 됩니다.

## 6. 거리와 overflow

좌표가 `10^9`이면 차이는 `2*10^9`, 제곱은 `4*10^18`까지 갈 수 있습니다. `long long` 한계에 가까우므로 더 큰 범위에서는 `__int128`이 필요합니다.

| 좌표 범위 | 권장 |
| --- | --- |
| `|coord| <= 10^6` | `long long` 충분 |
| `|coord| <= 10^9` | `long long` 가능하지만 주의 |
| 그 이상 | `__int128` 고려 |

문제가 실제 거리 출력이면 마지막에만 `sqrt`를 적용합니다.

## 7. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| 정렬 | `O(N log N)` | `O(N)` |
| sweep set update | `O(N log N)` | active set |
| 후보 거리 검사 | 평균/기하적으로 제한 | active range |

랜덤 데이터에서는 빠르지만, 구현이 y 후보를 지나치게 넓게 보면 최악에 가까워질 수 있습니다. `dy` 범위를 반드시 제한해야 합니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 전체 active set을 모두 검사 | 시간 초과 | y 범위 lower_bound 사용 |
| x 차이 제거 조건에서 제곱 비교 누락 | 후보 누락/과다 | `dx*dx < best` 유지 |
| set key에 index를 안 넣음 | 같은 y 점 삭제 오류 | `{y, index}` 사용 |
| 중복 점 처리 누락 | 답 0 늦게 발견 | 정렬 후 adjacent 검사 |
| int로 거리 제곱 계산 | overflow | `long long` 또는 `__int128` |
| 실제 거리와 제곱 거리 혼용 | 비교 오류 | 내부는 제곱 거리로 통일 |

## 9. 문제를 볼 때 체크할 조건

1. 모든 점 쌍 비교가 불가능한 크기인가?
2. 거리 비교만 필요해서 제곱 거리로 충분한가?
3. 좌표 범위가 overflow 없이 처리되는가?
4. 같은 좌표 점이 있을 수 있는가?
5. 가장 가까운 거리만 필요한가, 점 쌍도 출력해야 하는가?
6. sweep과 divide-and-conquer 중 구현하기 쉬운 쪽이 무엇인가?

Closest Pair Sweep은 "현재 최단거리보다 멀리 떨어진 점은 버린다"는 간단한 원리로 동작합니다. x와 y 두 축에서 후보를 동시에 줄이는 것이 핵심입니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: closest pair 기본 `/practice/...` 문제 필요 | 정렬과 active set 유지 | closest pair |
| 표준 | TODO: 중복 점 포함 closest pair `/practice/...` 문제 필요 | 답 0 처리와 index key | duplicate points |
| 응용 | TODO: 가장 가까운 점 쌍 복원 `/practice/...` 문제 필요 | best pair 저장 | pair restore |
| 함정 | TODO: 큰 좌표 closest pair `/practice/...` 문제 필요 | 거리 제곱 overflow 점검 | squared distance |
