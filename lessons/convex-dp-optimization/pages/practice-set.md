# Practice Set

Convex DP Optimization 계열은 "이 기법을 쓸 수 있는 식인가"를 먼저 연습해야 합니다. 적절한 h-contest 문제가 없는 항목은 임의 ID를 만들지 않고, 로컬 완결형 연습과 검증 기준을 먼저 둡니다.

## 1. 로컬 완결형 연습

### Line Query DP

아래 DP를 계산합니다.

```text
dp[i] = x[i]^2 + C + min_{0 <= j < i}(dp[j] + a[j]^2 - 2*a[j]*x[i])
```

`j`별 후보를 직선 `y = m*x + b`로 보면 `m = -2*a[j]`, `b = dp[j] + a[j]^2`입니다. `x[i]`가 단조 증가하면 deque CHT도 가능하지만, 이 연습은 임의 순서 `x[i]`에서도 동작하는 Li Chao Tree를 대표 구현으로 둡니다.

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

```cpp compile-check
#include <algorithm>
#include <iostream>
#include <limits>
#include <vector>
using namespace std;

const long long INF = numeric_limits<long long>::max() / 4;

struct LiChaoTree {
    struct Line {
        long long m = 0;
        long long b = INF;

        long long value(long long x) const {
            return m * x + b;
        }
    };

    struct Node {
        Line line;
        Node* left = nullptr;
        Node* right = nullptr;

        explicit Node(Line line) : line(line) {}
    };

    long long xLeft;
    long long xRight;
    Node* root = nullptr;

    LiChaoTree(long long xLeft, long long xRight) : xLeft(xLeft), xRight(xRight) {}

    void addLine(Line line) {
        insert(root, xLeft, xRight, line);
    }

    long long query(long long x) const {
        return query(root, xLeft, xRight, x);
    }

    static long long midpoint(long long left, long long right) {
        return left + (right - left) / 2;
    }

    void insert(Node*& node, long long left, long long right, Line line) {
        if (node == nullptr) {
            node = new Node(line);
            return;
        }

        long long mid = midpoint(left, right);
        bool betterLeft = line.value(left) < node->line.value(left);
        bool betterMid = line.value(mid) < node->line.value(mid);

        if (betterMid) {
            swap(line, node->line);
        }
        if (left == right) {
            return;
        }

        if (betterLeft != betterMid) {
            insert(node->left, left, mid, line);
        } else {
            insert(node->right, mid + 1, right, line);
        }
    }

    long long query(Node* node, long long left, long long right, long long x) const {
        if (node == nullptr) {
            return INF;
        }

        long long result = node->line.value(x);
        if (left == right) {
            return result;
        }

        long long mid = midpoint(left, right);
        if (x <= mid) {
            result = min(result, query(node->left, left, mid, x));
        } else {
            result = min(result, query(node->right, mid + 1, right, x));
        }
        return result;
    }
};

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

### Slope Trick Trace

절댓값 비용 `sum |x_i - t_i|`에 이동 제약이 붙는 작은 예시를 잡고, 왼쪽 heap과 오른쪽 heap의 top이 어떻게 breakpoint를 나타내는지 손으로 추적합니다. 구현보다 먼저 함수가 convex piecewise-linear로 유지되는지 확인하는 연습입니다.

## 2. 권장 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | 로컬: line query DP | 전이를 직선과 x query로 분리 | CHT |
| 표준 | TODO: arbitrary x Li Chao `/practice/...` 문제 필요 | 일반 삽입/질의 구현 | Li Chao Tree |
| 표준 | TODO: monotone opt DP `/practice/...` 문제 필요 | argmin 단조성 확인 | D&C DP |
| 응용 | TODO: absolute value convex cost `/practice/...` 문제 필요 | breakpoints 관리 | Slope Trick |
| 응용 | TODO: min-plus merge `/practice/...` 문제 필요 | convolution 모델링 | convex sequence |
| 심화 | TODO: dynamic line set `/practice/...` 문제 필요 | offline deletion 또는 dynamic hull | fully dynamic CHT |

## 3. 완료 기준

- 전이식에서 후보와 query 변수를 분리합니다.
- 기법 적용 조건을 한 문장으로 씁니다.
- 작은 입력 naive DP와 비교하는 stress test를 준비합니다.
- overflow 범위와 `INF` 정책을 명시합니다.
- precision이 필요한 경우 정수 비교식으로 바꿀 수 있는지 먼저 봅니다.
