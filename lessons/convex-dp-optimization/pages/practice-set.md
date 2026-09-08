# Practice Set

Convex DP Optimization 계열은 "이 기법을 쓸 수 있는 식인가"를 먼저 연습해야 합니다.


아래 입출력 코드는 [Convex Hull Trick과 Li Chao Tree](https://h.readiz.com/learn/convex-dp-optimization/convex-hull-trick-li-chao)의 LiChaoTree 정의 뒤에 붙입니다.

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
