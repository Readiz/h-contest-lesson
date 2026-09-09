# Mirror Descent and Multiplicative Weights

Mirror Descent는 Euclidean distance가 문제의 decision space와 잘 맞지 않을 때, 다른 regularizer가 만드는 geometry에서 한 걸음 이동하는 관점입니다. Online Convex Optimization에서 가장 자주 쓰는 예시는 simplex 위의 entropy regularizer이고, 이는 Multiplicative Weights update로 나타납니다.


제약 집합 C에서 Mirror Descent는 x_{t+1}=argmin_{x∈C}{η〈g_t,x〉+D_ψ(x,x_t)}입니다. D_ψ(x,y)=ψ(x)-ψ(y)-〈∇ψ(y),x-y〉이며 일반적으로 단순 mirror-map 역변환만으로 제약이 만족되지는 않습니다. Simplex의 음의 entropy는 KL divergence와 정규화된 지수 갱신으로 이어집니다.

## 왜 projection만으로 부족한가

Projected Gradient Descent는 아래 형태입니다.

```text
x_{t+1} = projection_C(x_t - eta * g_t)
```

`C`가 Euclidean ball이나 box라면 이 식이 자연스럽습니다. 하지만 `x`가 확률분포이면 단순히 좌표를 빼고 simplex projection을 하는 방식은 구현도 무겁고, "loss가 큰 action의 weight를 곱셈적으로 줄인다"는 직관도 잘 드러나지 않습니다.

Mirror Descent는 `x` 자체의 좌표보다 regularizer가 정의하는 dual space에서 update를 해석합니다.

```text
dual coordinate <- dual coordinate - eta * gradient
primal coordinate <- mirror map inverse
```

## Entropy Regularizer와 Simplex

확률분포 `p`에 entropy 계열 regularizer를 쓰면 update가 softmax 또는 weight 곱셈 형태가 됩니다.

```text
weight_i <- weight_i * exp(-eta * loss_i)
p_i <- weight_i / sum_j weight_j
```

loss가 큰 action은 weight가 감소하고, loss가 작은 action은 상대적으로 커집니다. 정확한 실수 연산에서는 양수 weight가 유지되지만 부동소수점에서는 underflow로 0이 될 수 있습니다. log-weight에서 최대값을 뺀 뒤 exp하는 방식으로 완화하며, 이 자체가 bandit exploration을 해결한다는 뜻은 아닙니다.

## 작은 추적 예시

```text
초기 weight = [1, 1, 1]
eta = 0.5
round loss = [0, 2, 1]
```

업데이트 후 weight는 아래처럼 됩니다.

```text
[1, exp(-1), exp(-0.5)] ~= [1.000, 0.368, 0.607]
```

정규화하면 첫 번째 action의 확률이 가장 큽니다. 다음 라운드에서 두 번째 action의 loss가 계속 크다면 weight는 곱셈적으로 더 빨리 줄어듭니다.

## Dual Averaging과의 관계

Multiplicative Weights를 매 라운드 loss에 대해 곱한다고 써도 되고, 지금까지의 누적 loss `L_i`로 아래처럼 써도 됩니다.

```text
p_i ∝ exp(-eta * L_i)
```

이 두 표현은 고정 `eta`에서는 같은 update를 다른 방식으로 본 것입니다. [Dual Averaging](dual-averaging.md)은 이 누적 gradient 표현을 regularized surrogate minimization으로 일반화합니다.

## 로컬 완결형 연습: Expert Advice with Full Loss Vectors

`N`개의 expert와 `T`라운드가 있습니다. 매 라운드가 끝나면 모든 expert의 loss가 공개됩니다. Multiplicative Weights로 확률분포를 갱신하고, 누적 expected loss와 가장 좋은 고정 expert의 loss 차이를 출력합니다.

### 입력

```text
N T eta
loss_{1,0} loss_{1,1} ... loss_{1,N-1}
...
loss_{T,0} loss_{T,1} ... loss_{T,N-1}
```

- `1 <= N <= 2000`
- `1 <= T <= 2000`
- `0 < eta <= 10`
- `0 <= loss_{t,i} <= 1`
- 모든 expert의 loss vector가 매 라운드 공개되는 full-information 모델입니다.

### 출력

```text
cumulative_expected_loss best_fixed_expert_loss regret
```

### 예시

```text
2 3 0.5
0 1
1 0
0 1
```

```text
1.6224593312 1.0000000000 0.6224593312
```

### 손으로 따라가는 Trace

초기 확률은 `(0.5, 0.5)`입니다.

| round | loss vector | round expected loss | update 뒤 확률 |
| ---: | --- | ---: | --- |
| 1 | `(0, 1)` | `0.5` | `(0.622459, 0.377541)` |
| 2 | `(1, 0)` | `0.622459` | `(0.5, 0.5)` |
| 3 | `(0, 1)` | `0.5` | `(0.622459, 0.377541)` |

누적 expected loss는 `1.622459...`이고, 가장 좋은 고정 expert는 expert 0으로 loss `1`입니다.

### 구현 기준

```cpp compile-check
#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <vector>
using namespace std;

vector<double> softmaxFromLogWeights(const vector<double>& logWeight) {
    double maxLog = *max_element(logWeight.begin(), logWeight.end());
    vector<double> probability(logWeight.size());
    double sum = 0.0;
    for (int i = 0; i < (int)logWeight.size(); ++i) {
        probability[i] = exp(logWeight[i] - maxLog);
        sum += probability[i];
    }
    for (double& value : probability) {
        value /= sum;
    }
    return probability;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int experts;
    int rounds;
    double eta;
    cin >> experts >> rounds >> eta;

    vector<double> logWeight(experts, 0.0);
    vector<double> expertLoss(experts, 0.0);
    double expectedLoss = 0.0;

    for (int round = 0; round < rounds; ++round) {
        vector<double> probability = softmaxFromLogWeights(logWeight);
        vector<double> loss(experts);
        for (double& value : loss) {
            cin >> value;
        }

        for (int expert = 0; expert < experts; ++expert) {
            expectedLoss += probability[expert] * loss[expert];
            expertLoss[expert] += loss[expert];
            logWeight[expert] -= eta * loss[expert];
        }
    }

    double bestExpert = *min_element(expertLoss.begin(), expertLoss.end());
    cout << fixed << setprecision(10)
         << expectedLoss << ' '
         << bestExpert << ' '
         << expectedLoss - bestExpert << '\n';
}
```

### Stress 기준

1. 매 round의 probability 합이 `1 +/- 1e-12`인지 확인합니다.
2. `eta = 0`에 가까운 작은 값에서는 거의 uniform 평균과 같아지는지 확인합니다.
3. 한 expert가 모든 round에서 loss 0인 입력, 모든 expert loss가 같은 입력을 deterministic case로 둡니다.
4. 선택한 expert의 loss만 주어지는 bandit 입력으로 바꾸면 이 구현을 쓰면 안 됩니다.
