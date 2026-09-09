# Convex Hull Trick과 Li Chao Tree

Convex Hull Trick은 여러 직선 중 특정 x에서 최솟값이나 최댓값을 빠르게 찾는 기법입니다. DP 전이가 `dp[i] = min_j(a_j * x_i + b_j)` 꼴로 정리되면, 각 후보 `j`를 직선으로 보고 query를 빠르게 처리할 수 있습니다.

## 식 분리 예시

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

`prefix`가 비감소하면 `x = prefix[i]`도 비감소하고 기울기 `-2 * prefix[j]`는 비증가합니다. `j < i`이므로 현재 `dp[i]`를 질의한 뒤 그 결과로 직선 `i`를 추가해야 합니다. 같은 위치를 먼저 후보에 넣지 않습니다.

## 구현 선택표

| 조건 | 추천 구현 |
| --- | --- |
| slope 추가 단조, query x 단조 | deque CHT |
| slope 추가 단조, query x 임의 | hull breakpoints + binary search |
| slope와 query 모두 임의, x 범위 고정 | Li Chao Tree |
| query x 좌표를 모두 미리 안다 | compressed Li Chao |
| 직선 삭제가 필요하다 | 임의 삭제 전용 구조 또는 rollback/offline |

## Min/Max Convention

한 구현 안에서는 최솟값 또는 최댓값 중 하나로 고정합니다. 최댓값 문제를 최솟값 구현으로 풀고 싶으면 직선과 답의 부호를 뒤집습니다.

```text
max(m*x + b)
= - min((-m)*x + (-b))
```

같은 slope에서는 min 문제라면 intercept가 작은 직선만 남기고, max 문제라면 intercept가 큰 직선만 남깁니다. 이 처리를 빼면 불필요한 직선이 쌓이거나 교점 계산에서 나눗셈이 깨집니다.

## Monotone Deque CHT

아래 구현은 기울기를 비증가 순서로 삽입하고 x를 비감소 순서로 질의합니다. 같은 기울기와 같은 x도 허용합니다. 평가값은 `long long`, 교점 비교의 곱은 `__int128` 범위 안이어야 합니다. `__int128` 변환은 뺄셈 전에 합니다.

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
        __int128 a = ((__int128)middle.intercept - left.intercept) * ((__int128)left.slope - right.slope);
        __int128 b = ((__int128)right.intercept - left.intercept) * ((__int128)left.slope - middle.slope);
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

## 앞의 전이식에 적용하기

위 `MonotoneMinCht` 바로 뒤에 아래 함수를 붙입니다. `prefix`는 비어 있지 않은 비감소 배열이며, 모든 DP 값과 곱셈 결과는 `long long` 범위 안이어야 합니다.

```cpp
#include <vector>
using namespace std;

vector<long long> optimizeQuadraticPartition(const vector<long long>& prefix, long long cost) {
    int n = (int)prefix.size() - 1;
    vector<long long> dp(n + 1, 0);
    MonotoneMinCht cht;
    cht.addLine(-2 * prefix[0], dp[0] + prefix[0] * prefix[0]);

    for (int i = 1; i <= n; ++i) {
        long long x = prefix[i];
        dp[i] = x * x + cost + cht.queryIncreasingX(x);
        cht.addLine(-2 * prefix[i], dp[i] + prefix[i] * prefix[i]);
    }
    return dp;
}
```

`prefix`가 감소하는 입력에는 이 deque를 쓰지 않습니다. 아래 Li Chao처럼 임의 순서 질의를 지원하는 구현으로 바꿔야 합니다.

## 작은 예시

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

## 중간 직선이 필요 없어지는 예

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

## Breakpoint Binary Search

slope는 단조로 추가되지만 query x가 임의이면, 각 직선이 최적이 되는 시작 x를 저장합니다.

```text
line 0: active from -inf
line 1: active from p1
line 2: active from p2
query x: 마지막 p <= x인 line 선택
```

정수 문제에서는 교점을 floor/ceil로 처리해야 합니다. min 문제와 max 문제, slope 증가와 감소에 따라 부등호가 바뀌므로 별도 함수로 테스트하는 편이 안전합니다.

## Dynamic Line Container

직선 삽입 순서가 완전히 임의이고 x query도 임의이면 Li Chao Tree가 가장 안정적입니다. 하지만 x 범위가 너무 크거나 실수 좌표이면 multiset 기반 line container를 쓰기도 합니다.

| 방식 | 장점 | 단점 |
| --- | --- | --- |
| Li Chao Tree | 구현 규칙이 명확, segment line 확장 가능 | x 범위 필요 |
| Compressed Li Chao | query 좌표만 관리해 메모리 절약 | offline 필요 |
| multiset LineContainer | x 범위가 없어도 가능 | 교점 정수 나눗셈 필요, 임의 삭제 미지원 |

대회에서는 삭제가 없다면 Li Chao가 더 실수하기 어렵습니다.

## Li Chao Tree

Li Chao Tree는 x좌표 구간을 Segment Tree처럼 나누고, 각 node에 그 구간 중앙에서 좋은 직선을 저장합니다. 새 직선을 넣을 때 기존 직선과 비교해 더 좋은 쪽을 node에 남기고, 밀려난 직선을 한쪽 child로 내려보냅니다.

아래 구현은 정수 x 범위 `[xLeft, xRight]`에서 최솟값을 구합니다. `xLeft <= xRight`이고 구간 길이와 모든 평가값은 `long long` 범위 안이어야 합니다. 실제 평가값은 sentinel인 `INF = numeric_limits<long long>::max()/4`보다 작아야 하며, 직선이 없으면 `INF`를 반환합니다.

```cpp compile-check
#include <algorithm>
#include <limits>
#include <vector>
using namespace std;

struct LiChaoTree {
    struct Line {
        long long m = 0;
        long long b = numeric_limits<long long>::max() / 4;

        long long value(long long x) const {
            return m * x + b;
        }
    };

    struct Node {
        Line line;
        int left = -1;
        int right = -1;
    };

    long long xLeft;
    long long xRight;
    vector<Node> tree;

    LiChaoTree(long long xLeft, long long xRight) : xLeft(xLeft), xRight(xRight) {
        tree.push_back(Node{});
    }

    int newNode() {
        tree.push_back(Node{});
        return (int)tree.size() - 1;
    }

    void addLine(Line line) {
        addLine(0, xLeft, xRight, line);
    }

    void addLine(int node, long long left, long long right, Line line) {
        long long mid = left + (right - left) / 2;
        bool betterLeft = line.value(left) < tree[node].line.value(left);
        bool betterMid = line.value(mid) < tree[node].line.value(mid);

        if (betterMid) {
            swap(line, tree[node].line);
        }
        if (left == right) {
            return;
        }

        if (betterLeft != betterMid) {
            if (tree[node].left == -1) {
                tree[node].left = newNode();
            }
            addLine(tree[node].left, left, mid, line);
        } else {
            if (tree[node].right == -1) {
                tree[node].right = newNode();
            }
            addLine(tree[node].right, mid + 1, right, line);
        }
    }

    long long query(long long x) const {
        return query(0, xLeft, xRight, x);
    }

    long long query(int node, long long left, long long right, long long x) const {
        long long result = tree[node].line.value(x);
        if (left == right) {
            return result;
        }
        long long mid = left + (right - left) / 2;
        if (x <= mid && tree[node].left != -1) {
            result = min(result, query(tree[node].left, left, mid, x));
        }
        if (x > mid && tree[node].right != -1) {
            result = min(result, query(tree[node].right, mid + 1, right, x));
        }
        return result;
    }
};
```

이 구현은 x 범위가 정수이고 `m * x + b`가 `long long` 범위에 들어간다는 전제가 있습니다. 값이 더 커질 수 있으면 `__int128`을 고려합니다.

## 좌표 압축 Li Chao

query가 나올 x좌표를 모두 미리 알 수 있다면, 실제 x값 전체 범위 대신 query 좌표 배열 위에서만 Li Chao Tree를 만들 수 있습니다.

| 방식 | 장점 | 주의점 |
| --- | --- | --- |
| 전체 정수 범위 Li Chao | 온라인 query 가능 | 범위와 overflow 주의 |
| 좌표 압축 Li Chao | 필요한 x만 관리 | 모든 query x를 미리 알아야 함 |
| deque CHT | 매우 빠르고 간단 | slope/query 단조 조건 필요 |

좌표 압축 방식에서도 line의 값은 압축 index가 아니라 실제 x좌표에서 계산해야 합니다.

## D&C DP와 구분

`cost(j, i)`가 Monge이고 argmin이 단조라면 Divide and Conquer Optimization이 더 간단할 수 있습니다. CHT는 보통 곱셈 항을 직선 질의로 분리할 수 있을 때 유리합니다.

| 구조 | 우선 후보 |
| --- | --- |
| `A[j] * X[i] + B[j]` | CHT/Li Chao |
| `cost(j, i)`가 Monge | D&C DP |
| convex function에 point update | Slope Trick |
| 선택 개수 penalty | Parametric DP |

## 시간 복잡도

| 구현 | 추가 | 질의 |
| --- | ---: | ---: |
| monotone deque CHT | amortized `O(1)` | amortized `O(1)` |
| breakpoint hull | amortized `O(1)` | `O(log N)` |
| Li Chao Tree | `O(log X)` | `O(log X)` |
| compressed Li Chao | `O(log Q)` | `O(log Q)` |

`X`는 정수 x 구간의 크기, `Q`는 압축한 질의 좌표 개수입니다. 위 비감소 prefix 예제는 각 직선이 deque에 한 번 들어가고 나가므로 전체 `O(N)`입니다.

## 로컬 완결형 연습

### Line Query DP

아래 DP를 계산합니다.

```text
dp[i] = x[i]^2 + C + min_{0 <= j < i}(dp[j] + a[j]^2 - 2*a[j]*x[i])
```

`j`별 후보를 직선 `y = m*x + b`로 보면 `m = -2*a[j]`, `b = dp[j] + a[j]^2`입니다. `a[j]`가 비감소하고 `x[i]`도 비감소하면 deque CHT가 가능하지만, 이 연습은 임의 순서 `x[i]`에서도 동작하는 Li Chao Tree를 대표 구현으로 둡니다.

#### 입력

```text
N C
a0 a1 ... aN-1
x0 x1 ... xN-1
```

- `1 <= N <= 200000`
- `0 <= C <= 10^12`
- `-10^6 <= a_i, x_i <= 10^6`
- `dp[0] = 0`

#### 출력

```text
dp[N-1]
```

#### 예시

```text
4 5
0 10 5 20
0 10 12 25
```

```text
335
```

#### 손으로 따라가는 Trace

`dp[0] = 0`이고, 처음에는 `j = 0` 직선 `y = 0`을 넣습니다.

| `i` | `x[i]` | query 후보 최솟값 | 선택된 `j` | `dp[i]` | 새로 넣는 직선 |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 10 | 0 | 0 | `10^2 + 5 + 0 = 105` | `y = -20x + 205` |
| 2 | 12 | -35 | 1 | `12^2 + 5 - 35 = 114` | `y = -10x + 139` |
| 3 | 25 | -295 | 1 | `25^2 + 5 - 295 = 335` | `y = -40x + 735` |

`i = 2`에서 `j = 1` 직선은 `-20*12 + 205 = -35`입니다. 이처럼 `dp[j]`가 절편에 들어가므로, `dp[i]`를 계산한 뒤에야 `i`의 직선을 추가해야 합니다.

#### 구현 기준

```cpp
#include <iostream>

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    long long c;
    cin >> n >> c;

    vector<long long> a(n), x(n);
    for (long long& value : a) {
        cin >> value;
    }
    for (long long& value : x) {
        cin >> value;
    }

    if (n == 1) {
        cout << 0 << '\n';
        return 0;
    }

    long long minX = *min_element(x.begin(), x.end());
    long long maxX = *max_element(x.begin(), x.end());

    vector<long long> dp(n, 0);
    LiChaoTree tree(minX, maxX);
    tree.addLine({-2 * a[0], dp[0] + a[0] * a[0]});

    for (int i = 1; i < n; ++i) {
        long long best = tree.query(x[i]);
        dp[i] = x[i] * x[i] + c + best;
        tree.addLine({-2 * a[i], dp[i] + a[i] * a[i]});
    }

    cout << dp[n - 1] << '\n';
}
```

검증은 `N <= 2000` naive `O(N^2)` DP와 random stress로 비교합니다. 이 연습을 통과하면 "전이를 직선과 query x로 분리한다"는 조건을 실제 코드까지 이어갈 수 있습니다.

#### Stress 기준

1. `N <= 80`, `|a_i|, |x_i| <= 20`, `C <= 100`에서 naive `O(N^2)` DP를 계산합니다.
2. 같은 입력을 Li Chao Tree 구현에 넣고 `dp[N-1]`이 같은지 비교합니다.
3. `x`가 감소하는 입력, 같은 `x`가 반복되는 입력, 같은 slope가 여러 번 들어오는 입력을 deterministic case로 둡니다.
4. 값 범위를 키울 때는 `m*x+b`, `x^2`, `dp`가 `long long` 범위 안인지 따로 계산합니다.
