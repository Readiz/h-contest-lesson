# Slope Trick

Slope Trick은 `min |x-a|`, `max(x-a,0)` 같은 convex piecewise-linear cost를 heap 두 개로 유지하는 DP 최적화 기법입니다. 상태가 "현재 위치 x를 고를 때의 최소 비용 함수"로 표현되고, 그 함수가 볼록이면 전체 함수를 배열로 들고 있지 않고 기울기 변화점만 관리할 수 있습니다.

이 레슨은 Alien Optimization, Convex Hull Trick, Monge/SMAWK 이후에 보는 DP 최적화 심화입니다.

1. 비용 함수를 convex piecewise-linear function으로 본다.
2. 왼쪽/오른쪽 heap이 minimizer 구간 주변의 break point를 관리한다.
3. `|x-a|`, `max(x-a,0)`, shift 같은 연산으로 DP 전이를 표현한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: priority queue, convex function, DP state, greedy exchange
- 함께 보면 좋은 레슨: Convex Hull Trick, Alien Optimization, Monge와 SMAWK
- 다음에 볼 레슨: convex cost flow, min-plus convolution, DP with convex penalties

## 1. 문제 신호

| 문제 표현 | Slope Trick 관점 |
| --- | --- |
| 값을 nondecreasing하게 조정하며 절댓값 비용 최소화 | `addAbs`와 prefix 제약 |
| 위치를 선택하고 이동 비용이 `|x-a|` | convex piecewise-linear |
| DP transition이 min over previous x with interval shift | function shift |
| 비용 함수의 argmin 구간만 필요 | two heaps |
| convex penalty가 누적된다 | break point 관리 |

Slope Trick은 모든 DP에 쓰는 도구가 아닙니다. 상태 축이 1차원이고 비용 함수가 볼록으로 유지되는지 먼저 확인해야 합니다.

## 2. 함수 관점

예를 들어 지금까지의 비용 함수가 `f(x)`이고 새 조건이 `|x-a|`라면:

```text
f(x) <- f(x) + |x - a|
```

`|x-a|`는 `a`에서 기울기가 2만큼 바뀌는 convex 함수입니다. 여러 개를 더하면 break point가 쌓이고, 최소값과 minimizer 구간은 heap으로 관리할 수 있습니다.

## 3. 두 Heap 불변식

| 구조 | 의미 |
| --- | --- |
| max heap `left` | minimizer 구간 왼쪽 break point |
| min heap `right` | minimizer 구간 오른쪽 break point |
| `minimum` | 현재 함수의 최소값 |
| lazy shift | 전체 break point를 한꺼번에 이동 |

`left.top() <= right.top()` 상태가 minimizer 구간을 나타냅니다. 새 break point가 이 구간 밖에 들어오면 minimum이 증가하고 heap 사이에서 점을 옮깁니다.

## 4. 기본 구현

아래 구조는 `max(a-x,0)`, `max(x-a,0)`, `|x-a|`, 전체 shift를 제공합니다.

```cpp compile-check
#include <functional>
#include <queue>
#include <vector>
using namespace std;

struct SlopeTrick {
    priority_queue<long long> left;
    priority_queue<long long, vector<long long>, greater<long long>> right;
    long long minimum = 0;
    long long addLeft = 0;
    long long addRight = 0;

    long long topLeft() const {
        return left.top() + addLeft;
    }

    long long topRight() const {
        return right.top() + addRight;
    }

    void pushLeft(long long value) {
        left.push(value - addLeft);
    }

    void pushRight(long long value) {
        right.push(value - addRight);
    }

    long long popLeft() {
        long long value = topLeft();
        left.pop();
        return value;
    }

    long long popRight() {
        long long value = topRight();
        right.pop();
        return value;
    }

    void addMaxAMinusX(long long a) {
        if (!right.empty() && topRight() < a) {
            long long moved = popRight();
            minimum += a - moved;
            pushLeft(moved);
            pushRight(a);
        } else {
            pushLeft(a);
        }
    }

    void addMaxXMinusA(long long a) {
        if (!left.empty() && topLeft() > a) {
            long long moved = popLeft();
            minimum += moved - a;
            pushRight(moved);
            pushLeft(a);
        } else {
            pushRight(a);
        }
    }

    void addAbs(long long a) {
        addMaxAMinusX(a);
        addMaxXMinusA(a);
    }

    void shift(long long delta) {
        addLeft += delta;
        addRight += delta;
    }
};
```

`addAbs(a)`는 두 개의 hinge function을 더하는 것과 같습니다.

```text
|x-a| = max(a-x, 0) + max(x-a, 0)
```

## 5. 단조 조정 예시

배열 `a_i`를 nondecreasing 배열 `b_i`로 바꾸면서 `sum |a_i - b_i|`를 최소화하는 문제는 slope trick과 greedy heap으로 연결됩니다.

직관은 아래와 같습니다.

```text
새 값이 이전 선택보다 작아지면 안 된다.
너무 큰 break point는 현재 값으로 끌어내리고 비용을 더한다.
```

이 문제만 놓고 보면 max heap 하나로도 풀 수 있지만, slope trick 관점에서는 "argmin 구간을 제약으로 잘라내는 연산"으로 해석할 수 있습니다.

## 6. Shift가 필요한 DP

상태가 이동하면서 가능한 `x` 범위가 바뀌는 문제에서는 함수 전체를 이동합니다.

```text
f_new(x) = f_old(x - d)
```

break point도 전부 `+d` 이동하므로 모든 값을 직접 바꾸지 말고 heap별 lazy offset을 둡니다. 위 구현의 `shift(delta)`가 그 역할입니다.

## 7. Alien Optimization과 비교

| 기법 | 보는 대상 |
| --- | --- |
| Convex Hull Trick | 직선들의 min/max envelope |
| Alien Optimization | 선택 개수 제약을 penalty로 완화 |
| Slope Trick | convex piecewise-linear 비용 함수 |
| Min-Cost Flow | convex 비용을 그래프 모델로 표현 가능 |

비용이 "직선 중 최솟값"이면 CHT를, "절댓값/hinge가 누적되는 함수"면 slope trick을 먼저 의심합니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| hinge 하나 추가 | `O(log N)` |
| `addAbs` | `O(log N)` 두 번 |
| shift | `O(1)` |
| 최소값 조회 | `O(1)` |

Heap에 들어간 break point 수는 추가한 hinge 수에 비례합니다.

## 9. 자주 하는 실수

1. `max(a-x,0)`와 `max(x-a,0)`의 heap 방향을 반대로 구현한다.
2. minimum 증가분을 heap top과 `a`의 차이로 더하지 않는다.
3. lazy shift를 heap에 들어간 raw value와 실제 value에 동시에 적용한다.
4. 함수가 convex가 아닌데 slope trick으로 억지로 관리한다.
5. minimizer 하나만 필요하다고 생각하고 구간 전체 정보를 잃는다.

## 10. 문제를 볼 때 체크할 조건

- 상태 축이 1차원인가?
- 비용 함수가 끝까지 convex로 유지되는가?
- 전이가 hinge 추가, 절댓값 추가, shift, prefix min 같은 연산으로 표현되는가?
- 좌표가 정수인가 실수인가?
- 최종적으로 필요한 것이 최소 비용인가, argmin 값도 필요한가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: median absolute deviation `/practice/...` 문제 필요 | `addAbs`와 minimizer 구간 이해 | two heaps |
| 표준 | TODO: nondecreasing adjustment `/practice/...` 문제 필요 | heap으로 convex cost 관리 | isotonic regression |
| 응용 | TODO: 이동 범위가 있는 DP `/practice/...` 문제 필요 | shift와 hinge 추가 결합 | slope trick |
| 함정 | TODO: non-convex transition 반례 `/practice/...` 문제 필요 | slope trick 적용 조건 판정 | convexity |
