# Convex Hull Trick Variants

Convex Hull Trick Variants는 직선 최솟값 또는 최댓값 질의를 처리할 때 어떤 구현을 골라야 하는지 정리하는 레슨입니다. 기본 Convex Hull Trick과 Li Chao Tree를 알고 있어도, slope 순서, query 순서, 같은 slope, min/max convention이 조금만 달라지면 구현 선택이 바뀝니다.

이 레슨은 Convex Hull Trick과 Li Chao Tree 이후에 보는 DP 최적화 심화입니다.

1. slope 추가 순서와 query x 순서를 먼저 분류한다.
2. min/max 문제를 하나의 convention으로 통일한다.
3. 같은 slope, overflow, tie-breaking을 구현 전에 결정한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Convex Hull Trick, Li Chao Tree, DP transition modeling
- 함께 보면 좋은 레슨: Convex Hull Trick과 Li Chao Tree, Convex DP Modeling, Divide and Conquer DP Optimization
- 다음에 볼 레슨: parametric DP, kinetic hull, fully dynamic CHT

## 1. 구현 선택표

| 조건 | 추천 구현 |
| --- | --- |
| slope 추가 단조, query x 단조 | deque CHT |
| slope 추가 단조, query x 임의 | hull breakpoints + binary search |
| slope와 query 모두 임의, x 범위 고정 | Li Chao Tree |
| query x 좌표를 모두 미리 안다 | compressed Li Chao |
| 직선 삭제가 필요하다 | multiset line container 또는 rollback/offline |

가장 빠른 구현보다 조건에 맞는 구현이 중요합니다. 단조 조건을 착각하면 deque CHT는 조용히 틀립니다.

## 2. Min/Max Convention

한 구현 안에서는 최솟값 또는 최댓값 중 하나로 고정합니다. 최댓값 문제를 최솟값 구현으로 풀고 싶으면 직선과 답의 부호를 뒤집습니다.

```text
max(m*x + b)
= - min((-m)*x + (-b))
```

같은 slope에서는 min 문제라면 intercept가 작은 직선만 남기고, max 문제라면 intercept가 큰 직선만 남깁니다. 이 처리를 빼면 불필요한 직선이 쌓이거나 교점 계산에서 나눗셈이 깨집니다.

## 3. Monotone Deque CHT

아래 구현은 slope가 증가하는 순서로 들어오고 query x도 증가하는 최솟값 문제를 처리합니다.

```cpp compile-check
#include <deque>
#include <limits>
using namespace std;

struct MonotoneMinCht {
    struct Line {
        long long slope = 0;
        long long intercept = 0;

        long long value(long long x) const {
            return slope * x + intercept;
        }
    };

    deque<Line> hull;

    static bool isBad(const Line& left, const Line& middle, const Line& right) {
        __int128 a = (__int128)(middle.intercept - left.intercept) * (left.slope - right.slope);
        __int128 b = (__int128)(right.intercept - left.intercept) * (left.slope - middle.slope);
        return a >= b;
    }

    void addLine(long long slope, long long intercept) {
        Line line{slope, intercept};
        if (!hull.empty() && hull.back().slope == slope) {
            if (hull.back().intercept <= intercept) {
                return;
            }
            hull.pop_back();
        }
        while (hull.size() >= 2 && isBad(hull[hull.size() - 2], hull[hull.size() - 1], line)) {
            hull.pop_back();
        }
        hull.push_back(line);
    }

    long long queryIncreasingX(long long x) {
        while (hull.size() >= 2 && hull[0].value(x) >= hull[1].value(x)) {
            hull.pop_front();
        }
        if (hull.empty()) {
            return numeric_limits<long long>::max() / 4;
        }
        return hull.front().value(x);
    }
};
```

이 구현은 x query가 되돌아가지 않는다는 전제가 있습니다. query x가 임의 순서라면 front pop을 하면 안 되고, breakpoints를 저장해 binary search해야 합니다.

## 4. Breakpoint Binary Search

slope는 단조로 추가되지만 query x가 임의이면, 각 직선이 최적이 되는 시작 x를 저장합니다.

```text
line 0: active from -inf
line 1: active from p1
line 2: active from p2
query x: 마지막 p <= x인 line 선택
```

정수 문제에서는 교점을 floor/ceil로 처리해야 합니다. min 문제와 max 문제, slope 증가와 감소에 따라 부등호가 바뀌므로 별도 함수로 테스트하는 편이 안전합니다.

## 5. Dynamic Line Container

직선 삽입 순서가 완전히 임의이고 x query도 임의이면 Li Chao Tree가 가장 안정적입니다. 하지만 x 범위가 너무 크거나 실수 좌표이면 multiset 기반 line container를 쓰기도 합니다.

| 방식 | 장점 | 단점 |
| --- | --- | --- |
| Li Chao Tree | 구현 규칙이 명확, segment line 확장 가능 | x 범위 필요 |
| Compressed Li Chao | query 좌표만 관리해 메모리 절약 | offline 필요 |
| multiset LineContainer | x 범위가 없어도 가능 | 교점 정수 나눗셈과 삭제가 까다로움 |

대회에서는 삭제가 없다면 Li Chao가 더 실수하기 어렵습니다.

## 6. 작은 예시

```text
lines:
  y = 3x + 0
  y = 2x + 5
  y = 1x + 9

x = 0: 3x = 0이 최소
x = 3: 2x+5 = 11, 1x+9 = 12, 3x = 9라서 3x가 여전히 최소
x = 5: 1x+9 = 14, 2x+5 = 15, 3x = 15라서 1x+9가 최소
```

손으로 교점 순서를 확인하면 "어떤 직선이 중간에서 완전히 필요 없는지"를 볼 수 있습니다.

## 7. DP 적용 체크

CHT는 자료구조보다 식 변형이 먼저입니다.

```text
dp[i] = min_j(dp[j] + A[j] * X[i] + B[j])
line_j = A[j] * x + dp[j] + B[j]
query x = X[i]
```

여기서 `A[j]`가 정렬되어 있는지, `X[i]`가 단조인지, `j < i` 조건 때문에 add/query 순서가 어떻게 되는지를 확인합니다.

## 8. 시간 복잡도

| 구현 | 추가 | 질의 |
| --- | ---: | ---: |
| monotone deque CHT | amortized `O(1)` | amortized `O(1)` |
| breakpoint hull | amortized `O(1)` | `O(log N)` |
| Li Chao Tree | `O(log X)` | `O(log X)` |
| compressed Li Chao | `O(log Q)` | `O(log Q)` |

상수까지 보면 monotone deque가 가장 빠릅니다. 하지만 조건 하나라도 부족하면 안정성을 위해 Li Chao로 가는 편이 낫습니다.

## 9. 자주 하는 실수

1. slope가 증가인지 감소인지 반대로 넣는다.
2. query x가 단조가 아닌데 front pop을 쓴다.
3. 같은 slope를 제거하지 않아 division by zero가 난다.
4. max 문제를 min 구현에 그대로 넣는다.
5. 교점 계산에서 음수 나눗셈의 floor/ceil을 틀린다.
6. `m*x+b` overflow를 확인하지 않는다.

## 10. 문제를 볼 때 체크할 조건

- 전이가 정말 직선과 점 질의로 분리되는가?
- slope 추가 순서를 보장하거나 정렬할 수 있는가?
- query x가 단조인가?
- 최솟값/최댓값 convention을 통일했는가?
- 같은 slope와 overflow 처리를 넣었는가?
- 삭제가 필요한 문제라면 offline으로 바꿀 수 있는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: monotone CHT `/practice/...` 문제 필요 | slope/query 단조 조건 사용 | deque CHT |
| 표준 | TODO: arbitrary query CHT `/practice/...` 문제 필요 | breakpoint binary search | lower hull |
| 응용 | TODO: Li Chao variant `/practice/...` 문제 필요 | x 압축과 min/max 변환 | compressed Li Chao |
| 함정 | TODO: same slope overflow `/practice/...` 문제 필요 | convention과 자료형 점검 | same slope, `__int128` |
