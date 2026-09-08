# Practice Set

Online Convex Optimization 허브의 연습은 먼저 feedback 모델을 판독하고, 그다음 feasible set에 맞는 update를 고르는 순서로 진행합니다.

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
