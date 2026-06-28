# Parametric Optimization Practice Set

이 페이지는 Parametric Optimization 계열을 하나의 학습 단위로 연습하기 위한 문제 목록입니다. 아직 적절한 h-contest 문제가 없는 칸은 임의 ID를 넣지 않고, 로컬 완결형 연습과 검증 기준을 먼저 둡니다.

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

```cpp compile-check
#include <algorithm>
#include <iomanip>
#include <iostream>
#include <vector>
using namespace std;

bool feasibleAverage(const vector<double>& values, int minLength, double target) {
    int n = (int)values.size();
    vector<double> prefix(n + 1, 0.0);
    for (int i = 0; i < n; ++i) {
        prefix[i + 1] = prefix[i] + values[i] - target;
    }

    double minPrefix = 0.0;
    for (int right = minLength; right <= n; ++right) {
        minPrefix = min(minPrefix, prefix[right - minLength]);
        if (prefix[right] - minPrefix >= 0.0) {
            return true;
        }
    }
    return false;
}

double maximumAverage(const vector<double>& values, int minLength) {
    double low = *min_element(values.begin(), values.end());
    double high = *max_element(values.begin(), values.end());

    for (int iter = 0; iter < 80; ++iter) {
        double mid = (low + high) * 0.5;
        if (feasibleAverage(values, minLength, mid)) {
            low = mid;
        } else {
            high = mid;
        }
    }
    return low;
}

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

    cout << fixed << setprecision(10) << maximumAverage(values, minLength) << '\n';
}
```

#### Stress 기준

작은 입력에서는 `O(n^2)` brute force와 비교합니다.

1. `n <= 30`에서 모든 `l, r`을 열거하고 `r-l+1 >= L`인 구간 평균의 최댓값을 구합니다.
2. 위 binary search 구현의 답과 절대 오차 `1e-7` 이하인지 비교합니다.
3. 전부 음수인 배열, `L=1`, `L=n`, 최적 구간이 여러 개인 배열을 deterministic case로 둡니다.

### 정확히 K개 Segment 고르기

배열을 몇 개의 segment로 나누어 segment 비용 합을 최소화하되, 정확히 `K`개 segment를 골라야 합니다. `K` 차원을 직접 넣으면 너무 크다고 가정합니다.

```text
입력
n K
segment cost oracle

목표
고정 penalty에서 count를 함께 반환하는 DP를 만들고,
lambda 탐색 후 원래 비용을 복원합니다.
```

이 연습은 실제 문제마다 cost oracle이 다르므로, 먼저 작은 `O(n^2)` oracle로 count와 tie-break를 검증한 뒤 최적화 기법을 붙이는 순서가 안전합니다.

## h-contest 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | 로컬: maximum average subarray | `value - x * weight` 판정 구현 | binary search |
| 표준 | TODO: exact K DP `/practice/...` 문제 필요 | penalty와 count tie-break | Alien trick |
| 응용 | TODO: fractional graph path `/practice/...` 문제 필요 | 비율 목적식과 shortest path 결합 | transformed weight |
| 함정 | TODO: breakpoint counterexample `/practice/...` 문제 필요 | 동점 처리와 답 복원 검증 | breakpoint |
