# Fractional Programming DP

Fractional Programming DP는 `benefit / cost`, 평균값, 밀도, 비율 목적식을 직접 최적화하기 어려울 때 `benefit - lambda * cost` 형태의 판정 문제로 바꾸는 기법입니다. DP나 graph feasibility가 비율 안쪽에 들어가면 parametric search, Dinkelbach iteration, binary search on answer를 함께 봅니다.

이 레슨은 Parametric DP, Convex DP Modeling, Alien Optimization 이후에 보는 DP 최적화 심화입니다.

1. 비율 목적식을 `value - x * weight` 판정으로 바꾼다.
2. 고정된 `x`에서 DP가 최대 transformed score를 계산한다.
3. score가 0 이상인지로 가능한 비율을 이분 탐색하거나 Dinkelbach로 갱신한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: DP feasibility, binary search on answer, parametric search
- 함께 보면 좋은 레슨: Parametric DP, Alien Optimization, Convex DP Modeling
- 다음에 볼 레슨: Dinkelbach method, ratio cut, Lagrangian relaxation

## 1. 문제 신호

| 문제 표현 | Fractional 관점 |
| --- | --- |
| 평균 점수의 최댓값을 구한다 | `sum(value) / count` |
| 비용 대비 효율이 최대인 subset | `sum(value) / sum(cost)` |
| path의 평균 weight를 최적화한다 | transformed edge weight |
| DP objective가 ratio 형태다 | fixed ratio feasibility |
| `answer`를 실수로 출력한다 | binary search on ratio |

비율을 직접 DP 상태에 넣으면 비교가 불안정해집니다. 대신 후보 비율 `x`를 고정하고 "이 비율 이상을 만들 수 있는가"를 묻습니다.

## 2. 변환 원리

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

## 3. 평균 Subarray 예시

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

## 4. DP에 붙이는 방식

선택 구조가 복잡해도 원리는 같습니다.

```text
dp[state] = max transformed score
transition adds value - x * weight
feasible if best terminal dp >= 0
```

예를 들어 path 평균 weight, tree 선택 밀도, 제한 조건이 있는 knapsack ratio는 fixed `x`에서 일반 DP나 shortest path 판정으로 바뀔 수 있습니다.

## 5. Dinkelbach 직관

이분 탐색 대신 현재 해의 비율로 `lambda`를 갱신하는 Dinkelbach 방식도 있습니다.

```text
lambda = current ratio
solve max sum(value - lambda * weight)
new lambda = selectedValue / selectedWeight
stop when transformed score is close to 0
```

연속 최적화나 일부 discrete fractional problem에서 빠르게 수렴합니다. 다만 구현 검증은 binary search가 더 단순한 경우가 많습니다.

## 6. 작은 예시

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

## 7. Precision 정책

| 출력 요구 | 권장 방식 |
| --- | --- |
| 소수 오차 허용 | double binary search |
| 유리수 exact 비교 | cross multiplication |
| 정수 answer 후보가 작음 | answer 후보 정렬 후 이분 |
| DP score가 매우 큼 | long double 또는 scaling |

실수 이분 탐색에서는 iteration 횟수를 고정하는 편이 안전합니다. 판정이 noisy하면 `eps`로 종료하지 말고 충분한 횟수 반복 후 출력합니다.

## 8. 시간 복잡도 감각

| 방식 | 시간 |
| --- | ---: |
| fixed ratio 판정 | 원래 DP/graph 판정 비용 |
| binary search | `판정 비용 * iterations` |
| Dinkelbach | `판정 비용 * 갱신 횟수` |
| 후보 비율 exact search | `판정 비용 * log candidates` |

비율 최적화는 판정 함수를 수십 번 부릅니다. 판정 DP가 충분히 빠른지 먼저 계산합니다.

## 9. 자주 하는 실수

1. `sum value / sum weight`를 item별 ratio 평균으로 바꿔 버린다.
2. weight가 0일 수 있는 경우를 처리하지 않는다.
3. 최대화 문제와 최소화 문제의 부등호 방향을 뒤집는다.
4. DP 초기값의 `-inf`가 transformed score와 섞여 overflow를 만든다.
5. 실수 오차 때문에 `>= 0` 판정이 흔들리는 입력을 고려하지 않는다.
6. binary search iteration 수가 부족해 출력 오차를 넘긴다.

## 10. 문제를 볼 때 체크할 조건

- 목적식이 전체 합의 비율인가, 개별 ratio의 합인가?
- denominator가 항상 양수인가?
- fixed ratio에서 DP나 graph 판정이 쉬워지는가?
- answer가 실수인지 exact rational인지 확인했는가?
- 판정 함수가 단조성을 가지는가?
- 필요한 precision에 맞게 자료형을 정했는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: maximum average subarray `/practice/...` 문제 필요 | `a_i - x` 판정 | prefix minimum |
| 표준 | TODO: ratio knapsack DP `/practice/...` 문제 필요 | transformed score DP | binary search |
| 응용 | TODO: average path feasibility `/practice/...` 문제 필요 | graph weight 변환 | parametric search |
| 함정 | TODO: zero denominator ratio `/practice/...` 문제 필요 | 예외와 precision 처리 | denominator |
