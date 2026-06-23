# CHT DP Applications

CHT DP Applications는 Convex Hull Trick을 실제 DP 식으로 바꾸는 과정을 다룹니다. CHT 구현을 알고 있어도, `j`가 만드는 직선과 `i`가 던지는 query를 정확히 분리하지 못하면 최적화가 아니라 다른 문제를 풀게 됩니다.

이 레슨은 Convex DP Modeling, Convex Hull Trick Variants 이후에 보는 DP 최적화 응용 레슨입니다.

1. 전이식을 `line_j(x_i)` 형태로 분해한다.
2. slope 추가 순서와 query 순서를 확인한다.
3. 구현 선택과 tie-breaking을 문제 조건에 맞춘다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: DP transition, CHT/Li Chao Tree, convex DP modeling
- 함께 보면 좋은 레슨: Convex Hull Trick Variants, Convex DP Modeling, Divide and Conquer DP Optimization
- 다음에 볼 레슨: parametric DP, slope trick, kinetic hull

## 1. 문제 신호

| DP 전이 형태 | CHT 관점 |
| --- | --- |
| `dp[i] = min_j(dp[j] + A[j] * X[i] + B[j])` | `j`가 직선, `i`가 query |
| `cost(j, i)`에 곱셈 항이 있음 | 식 전개 후 직선 분리 |
| `j < i` 조건 | add/query 순서가 온라인 |
| `A[j]`가 단조 | deque 또는 breakpoint hull 후보 |
| `X[i]`가 임의 | Li Chao 또는 binary search hull |

식이 직선과 점 질의로 분리되지 않으면 CHT를 억지로 적용하면 안 됩니다.

## 2. 식 분리 예시

아래 전이가 있다고 합시다.

```text
dp[i] = min over j < i:
  dp[j] + (prefix[i] - prefix[j])^2 + C
```

전개하면 다음과 같습니다.

```text
dp[i] = prefix[i]^2 + C + min_j(
  dp[j] + prefix[j]^2 - 2*prefix[j]*prefix[i]
)
```

따라서 `x = prefix[i]`, `m = -2*prefix[j]`, `b = dp[j] + prefix[j]^2`인 직선 최솟값 질의가 됩니다.

## 3. 구현 골격

아래 코드는 `x`가 증가하고 slope도 증가하는 최솟값 문제를 처리하는 monotone CHT skeleton입니다.

```cpp compile-check
#include <deque>
#include <vector>
using namespace std;

struct ChtDpLine {
    long long m = 0;
    long long b = 0;

    long long value(long long x) const {
        return m * x + b;
    }
};

struct MonotoneChtDp {
    deque<ChtDpLine> hull;

    static bool bad(const ChtDpLine& a, const ChtDpLine& b, const ChtDpLine& c) {
        __int128 left = (__int128)(b.b - a.b) * (a.m - c.m);
        __int128 right = (__int128)(c.b - a.b) * (a.m - b.m);
        return left >= right;
    }

    void add(long long m, long long b) {
        ChtDpLine line{m, b};
        if (!hull.empty() && hull.back().m == m) {
            if (hull.back().b <= b) {
                return;
            }
            hull.pop_back();
        }
        while (hull.size() >= 2 && bad(hull[hull.size() - 2], hull[hull.size() - 1], line)) {
            hull.pop_back();
        }
        hull.push_back(line);
    }

    long long queryIncreasingX(long long x) {
        while (hull.size() >= 2 && hull[0].value(x) >= hull[1].value(x)) {
            hull.pop_front();
        }
        return hull.front().value(x);
    }
};

vector<long long> optimizeQuadraticPartition(const vector<long long>& prefix, long long cost) {
    int n = (int)prefix.size() - 1;
    vector<long long> dp(n + 1, 0);
    MonotoneChtDp cht;
    cht.add(-2 * prefix[0], dp[0] + prefix[0] * prefix[0]);

    for (int i = 1; i <= n; ++i) {
        long long x = prefix[i];
        dp[i] = x * x + cost + cht.queryIncreasingX(x);
        cht.add(-2 * prefix[i], dp[i] + prefix[i] * prefix[i]);
    }
    return dp;
}
```

이 skeleton은 `prefix[i]`가 증가한다는 전제를 둡니다. 값이 감소할 수 있으면 `queryIncreasingX`가 틀립니다.

## 4. 선택 순서 체크

CHT DP에서는 아래 순서를 먼저 표로 씁니다.

| 질문 | 답이 필요한 이유 |
| --- | --- |
| `j`는 언제 line으로 추가되는가 | `j < i` 온라인 조건 |
| slope가 정렬되어 들어오는가 | deque 가능 여부 |
| query x가 정렬되어 들어오는가 | front pop 가능 여부 |
| 같은 slope가 생기는가 | intercept tie 처리 |
| min인가 max인가 | 부호 변환 |

이 다섯 가지가 정해지면 구현 선택은 대부분 결정됩니다.

## 5. 작은 예시

```text
prefix = 0, 2, 5
C = 3

i=1, x=2
line j=0: m=0, b=0
dp[1] = 4 + 3 + 0 = 7
add j=1: m=-4, b=11

i=2, x=5
line j=0 => 0
line j=1 => -20 + 11 = -9
dp[2] = 25 + 3 - 9 = 19
```

손으로 한두 단계 따라가면 직선의 `m`, `b`가 DP 전이와 맞는지 빠르게 확인할 수 있습니다.

## 6. Li Chao로 가야 하는 경우

아래 조건 중 하나라도 깨지면 monotone deque 대신 Li Chao를 먼저 고려합니다.

1. slope가 입력 순서대로 단조가 아니다.
2. query x가 되돌아갈 수 있다.
3. 중간에 과거 line 삭제가 필요하지는 않다.
4. x 좌표 범위를 알고 있거나 모든 query 좌표를 미리 압축할 수 있다.

삭제가 필요한 경우는 rollback/offline 또는 multiset line container까지 봐야 합니다.

## 7. D&C DP와 구분

`cost(j, i)`가 Monge이고 argmin이 단조라면 Divide and Conquer Optimization이 더 간단할 수 있습니다. CHT는 보통 곱셈 항을 직선 질의로 분리할 수 있을 때 유리합니다.

| 구조 | 우선 후보 |
| --- | --- |
| `A[j] * X[i] + B[j]` | CHT/Li Chao |
| `cost(j, i)`가 Monge | D&C DP |
| convex function에 point update | Slope Trick |
| 선택 개수 penalty | Parametric DP |

## 8. 자주 하는 실수

1. `prefix[i]^2`처럼 query에만 의존하는 항을 line intercept에 넣는다.
2. slope가 감소하는데 증가용 hull 조건을 그대로 쓴다.
3. `x`가 단조가 아닌데 deque query를 쓴다.
4. 같은 slope에서 더 나쁜 line을 제거하지 않는다.
5. `m*x+b` overflow를 `long long`으로 방치한다.

## 9. 문제를 볼 때 체크할 조건

- 전이식을 line과 query x로 분리했는가?
- line 추가 시점이 `j < i` 제약과 맞는가?
- slope/query 단조성이 입력에서 보장되는가?
- min/max convention을 통일했는가?
- naive DP와 작은 입력에서 비교했는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: quadratic partition CHT `/practice/...` 문제 필요 | 식 전개와 line 분리 | prefix square |
| 표준 | TODO: Li Chao DP `/practice/...` 문제 필요 | 임의 query 처리 | dynamic hull |
| 응용 | TODO: online CHT DP `/practice/...` 문제 필요 | add/query 순서 설계 | transition ordering |
| 함정 | TODO: non-monotone CHT `/practice/...` 문제 필요 | deque 전제 검증 | counterexample |
