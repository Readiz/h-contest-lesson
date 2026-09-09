# Fractional Programming DP

Fractional Programming DP는 `benefit / cost`, 평균값, 밀도, 비율 목적식을 직접 최적화하기 어려울 때 `benefit - lambda * cost` 형태의 판정 문제로 바꾸는 기법입니다. DP나 graph feasibility가 비율 안쪽에 들어가면 parametric search, Dinkelbach iteration, binary search on answer를 함께 봅니다.


모든 feasible 해의 분모 합이 양수이고 해가 비어 있지 않아야 부등식 변환이 맞습니다. 아래 배열은 비어 있지 않고 1<=minLength<=N, 값은 유한한 실수입니다. 반복 횟수는 초기 폭/2^iterations를 줄이지만 판정의 반올림 오차는 없애지 못합니다.

## 문제 신호

| 문제 표현 | Fractional 관점 |
| --- | --- |
| 평균 점수의 최댓값을 구한다 | `sum(value) / count` |
| 비용 대비 효율이 최대인 subset | `sum(value) / sum(cost)` |
| path의 평균 weight를 최적화한다 | transformed edge weight |
| DP objective가 ratio 형태다 | fixed ratio feasibility |
| `answer`를 실수로 출력한다 | binary search on ratio |

비율을 직접 DP 상태에 넣으면 비교가 불안정해집니다. 대신 후보 비율 `x`를 고정하고 "이 비율 이상을 만들 수 있는가"를 묻습니다.

## 변환 원리

최대화하려는 값이 아래라고 합시다.

```text
R = sum value_i / sum weight_i
```

`R >= x`는 아래와 같습니다.

```text
sum value_i >= x * sum weight_i
sum (value_i - x * weight_i) >= 0
```

이제 fixed `x`에서는 각 item이나 edge의 점수가 `value - x * weight`인 일반 최댓값 문제가 됩니다.

## 평균 Subarray 예시

길이 `k` 이상인 subarray의 최대 평균을 구하려면 각 원소에서 `x`를 뺀 뒤, 길이 `k` 이상 subarray sum이 0 이상인지 확인합니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

bool hasAverageAtLeast(const vector<double>& values, int minLength, double target) {
    int n = (int)values.size();
    vector<double> prefix(n + 1, 0.0);
    for (int i = 0; i < n; ++i) {
        prefix[i + 1] = prefix[i] + values[i] - target;
    }

    double bestPrefix = 0.0;
    for (int right = minLength; right <= n; ++right) {
        if (prefix[right] - bestPrefix >= 0.0) {
            return true;
        }
        int candidateLeft = right - minLength + 1;
        if (candidateLeft <= n) {
            bestPrefix = min(bestPrefix, prefix[candidateLeft]);
        }
    }
    return false;
}

double maximumAverageSubarray(const vector<double>& values, int minLength) {
    double low = values[0];
    double high = values[0];
    for (double value : values) {
        low = min(low, value);
        high = max(high, value);
    }

    for (int iter = 0; iter < 70; ++iter) {
        double mid = (low + high) * 0.5;
        if (hasAverageAtLeast(values, minLength, mid)) {
            low = mid;
        } else {
            high = mid;
        }
    }
    return low;
}
```

`target`을 고정하면 문제는 prefix minimum을 이용하는 일반 판정으로 바뀝니다.

## DP에 붙이는 방식

선택 구조가 복잡해도 원리는 같습니다.

```text
dp[state] = max transformed score
transition adds value - x * weight
feasible if best terminal dp >= 0
```

예를 들어 path 평균 weight, tree 선택 밀도, 제한 조건이 있는 knapsack ratio는 fixed `x`에서 일반 DP나 shortest path 판정으로 바뀔 수 있습니다.

## Dinkelbach 직관

이분 탐색 대신 현재 해의 비율로 `lambda`를 갱신하는 Dinkelbach 방식도 있습니다.

```text
lambda = current ratio
solve max sum(value - lambda * weight)
new lambda = selectedValue / selectedWeight
stop when transformed score is close to 0
```

연속 최적화나 일부 discrete fractional problem에서 빠르게 수렴합니다. 다만 구현 검증은 binary search가 더 단순한 경우가 많습니다.

## 작은 예시

```text
items:
  A value=10, weight=4, ratio=2.5
  B value=8,  weight=2, ratio=4.0
  C value=7,  weight=3, ratio=2.33

target x = 3
transformed:
  A: -2
  B:  2
  C: -2
```

`x = 3` 이상인 조합을 찾으려면 transformed sum이 0 이상인 feasible set이 있는지 보면 됩니다. 단일 item이면 B만 가능하고, 여러 item 조합이면 제약에 따라 DP가 선택합니다.

## Precision 정책

| 출력 요구 | 권장 방식 |
| --- | --- |
| 소수 오차 허용 | double binary search |
| 유리수 exact 비교 | cross multiplication |
| 정수 answer 후보가 작음 | answer 후보 정렬 후 이분 |
| DP score가 매우 큼 | long double 또는 scaling |

실수 이분 탐색에서는 iteration 횟수를 고정하는 편이 안전합니다. 판정이 noisy하면 `eps`로 종료하지 말고 충분한 횟수 반복 후 출력합니다.

## 시간 복잡도 감각

| 방식 | 시간 |
| --- | ---: |
| fixed ratio 판정 | 원래 DP/graph 판정 비용 |
| binary search | `판정 비용 * iterations` |
| Dinkelbach | `판정 비용 * 갱신 횟수` |
| 후보 비율 exact search | `판정 비용 * log candidates` |

비율 최적화는 판정 함수를 수십 번 부릅니다. 판정 DP가 충분히 빠른지 먼저 계산합니다.

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
