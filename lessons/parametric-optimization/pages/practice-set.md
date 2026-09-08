# Parametric Optimization Practice Set

이 페이지는 Parametric Optimization 계열을 하나의 학습 단위로 연습하기 위한 문제 목록입니다. 아직 적절한 h-contest 문제가 없는 칸은 임의 ID를 넣지 않고, 로컬 완결형 연습과 검증 기준을 먼저 둡니다.


입출력 코드는 [Fractional Programming DP](https://h.readiz.com/learn/parametric-optimization/fractional-objectives)의 maximumAverageSubarray 정의 뒤에 붙입니다.

## 로컬 완결형 연습

### 최대 평균 부분 배열

길이 `L` 이상인 연속 부분 배열의 평균 최댓값을 구합니다. 후보 평균 `x`를 고정했을 때 `sum(a_i - x) >= 0`인 길이 `L` 이상 구간이 존재하는지 판정합니다.

```text
입력
n L
a1 a2 ... an

제한
1 <= L <= n <= 200000
-10000 <= ai <= 10000

출력
최대 평균을 절대/상대 오차 1e-6 이하로 출력
```

#### 예시

```text
6 4
1 12 -5 -6 50 3
```

```text
12.7500000000
```

최적 구간은 `12, -5, -6, 50`이고 평균은 `12.75`입니다.

#### 손으로 따라가는 Trace

후보 `x = 12.75`를 고정하면 변환 배열은 아래입니다.

```text
-11.75, -0.75, -17.75, -18.75, 37.25, -9.75
```

prefix sum `P`와 길이 조건을 만족하는 왼쪽 prefix 최솟값을 비교합니다.

| 오른쪽 prefix `r` | `P[r]` | 허용 왼쪽 prefix 범위 | `minPrefix` | `P[r] - minPrefix` | 판정 |
| ---: | ---: | --- | ---: | ---: | --- |
| 4 | `-49.00` | `P[0]` | `0.00` | `-49.00` | 실패 |
| 5 | `-11.75` | `P[0..1]` | `-11.75` | `0.00` | 성공 |

`r = 5`에서 성공하는 구간은 1-based `2..5`, 즉 `12, -5, -6, 50`입니다. `x`가 더 커지면 이 값이 음수가 되어 판정이 실패하므로, 이 판정은 binary search의 oracle이 됩니다.

#### 구현 기준

```cpp
#include <iomanip>
#include <iostream>

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    int minLength;
    cin >> n >> minLength;

    vector<double> values(n);
    for (double& value : values) {
        cin >> value;
    }

    cout << fixed << setprecision(10) << maximumAverageSubarray(values, minLength) << '\n';
}
```

#### Stress 기준

작은 입력에서는 `O(n^2)` brute force와 비교합니다.

1. `n <= 30`에서 모든 `l, r`을 열거하고 `r-l+1 >= L`인 구간 평균의 최댓값을 구합니다.
2. 위 binary search 구현의 답과 절대 오차 `1e-7` 이하인지 비교합니다.
3. 전부 음수인 배열, `L=1`, `L=n`, 최적 구간이 여러 개인 배열을 deterministic case로 둡니다.
