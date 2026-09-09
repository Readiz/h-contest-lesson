# Dual Averaging

Dual Averaging은 online convex optimization에서 매 라운드 gradient를 바로 현재 점에만 반영하지 않고, 누적 gradient와 regularizer를 이용해 다음 결정을 고르는 방식입니다. Mirror Descent와 가까운 관점이지만, "지금까지 본 gradient 전체를 평균적으로 반영한다"는 해석이 특히 중요합니다.

이 페이지는 Online Convex Optimization, Convex DP Modeling, Bayesian Bandits 이후에 보는 온라인 최적화 심화입니다.

1. gradient 또는 subgradient를 누적한다.
2. 누적 gradient에 regularizer를 더한 surrogate를 최소화한다.
3. simplex, box, ball 같은 feasible set에 맞는 closed form update를 고른다.


actionCount>0, loss 벡터 길이 일치, eta>=0과 누적 손실과 `eta * cumulativeLoss`가 모두 유한함을 전제로 합니다. 반환값은 모든 관측 뒤 다음 라운드의 분포입니다. 실수 exp는 underflow로 0이 될 수 있으므로 수학적으로 양수라는 사실과 구분합니다.

## 문제 신호

| 문제 표현 | Dual Averaging 관점 |
| --- | --- |
| 매 라운드 loss gradient가 공개된다 | cumulative gradient |
| simplex 위 확률분포를 갱신한다 | entropy regularizer |
| sparse한 decision을 선호한다 | L1/proximal regularizer 후보 |
| projection step이 비싸다 | regularized closed form update |
| regret bound가 필요하다 | online learning 분석 |

Online Gradient Descent가 현재 점에서 한 걸음 이동한다면, Dual Averaging은 지금까지의 gradient 합이 가리키는 방향을 regularizer로 누그러뜨려 새 점을 고릅니다.

### Feedback 모델 경계

대회 문맥에서 가장 흔한 오독은 bandit feedback을 full-information 문제처럼 푸는 것입니다. 선택하지 않은 action의 loss까지 매 라운드 모두 주어지면 이 레슨의 simplex update를 바로 쓸 수 있습니다. 반대로 선택한 action의 결과만 보이면 관측되지 않은 loss를 추정하거나 탐색을 섞어야 하므로 Bayesian Bandits, Thompson Sampling, UCB 계열을 먼저 의심합니다.

## 기본 식

라운드 `t`까지의 gradient 합을 `G_t`라고 합시다.

```text
G_t = g_1 + g_2 + ... + g_t
```

Dual Averaging의 다음 선택은 대략 아래 문제의 해입니다.

```text
x_{t+1} = argmin_x <G_t, x> + (1 / eta_t) * R(x)
```

`R(x)`는 regularizer입니다. Euclidean regularizer를 쓰면 평균 gradient 방향으로 이동하고, entropy regularizer를 쓰면 multiplicative weights 형태가 됩니다.

## Simplex에서의 Exponential Update

확률분포 simplex에서 entropy regularizer를 쓰면 누적 loss에 대한 softmax가 됩니다.

```text
weight_i = exp(-eta * cumulativeLoss_i)
x_i = weight_i / sum weight
```

아래 코드는 loss vector가 매 라운드 전체 공개되는 full-information setting의 기본 update입니다.

```cpp compile-check
#include <cmath>
#include <vector>
using namespace std;

vector<double> dualAveragingSimplex(
    int actionCount,
    const vector<vector<double>>& losses,
    double eta
) {
    vector<double> cumulative(actionCount, 0.0);
    vector<double> probability(actionCount, 1.0 / actionCount);

    for (const vector<double>& loss : losses) {
        for (int i = 0; i < actionCount; ++i) {
            cumulative[i] += loss[i];
        }

        double maxLogWeight = -eta * cumulative[0];
        vector<double> logWeight(actionCount);
        for (int i = 0; i < actionCount; ++i) {
            logWeight[i] = -eta * cumulative[i];
            if (logWeight[i] > maxLogWeight) {
                maxLogWeight = logWeight[i];
            }
        }

        double normalizer = 0.0;
        for (int i = 0; i < actionCount; ++i) {
            probability[i] = exp(logWeight[i] - maxLogWeight);
            normalizer += probability[i];
        }
        for (double& value : probability) {
            value /= normalizer;
        }
    }

    return probability;
}
```

`maxLogWeight`를 빼는 이유는 exponential overflow를 막기 위해서입니다.

## 작은 예시

세 action의 누적 loss가 아래라고 하겠습니다.

```text
cumulativeLoss = [3, 5, 1]
eta = 0.5
```

log weight는 아래가 됩니다.

```text
[-1.5, -2.5, -0.5]
```

세 번째 action의 loss가 가장 작으므로 가장 큰 확률을 받습니다. 하지만 entropy regularizer 때문에 다른 action도 0이 아닌 확률을 유지합니다.

## OGD와의 차이

| 기준 | Online Gradient Descent | Dual Averaging |
| --- | --- | --- |
| 기준점 | 현재 점 `x_t` | 누적 gradient `G_t` |
| update | 한 걸음 이동 후 projection | regularized surrogate 최소화 |
| simplex update | projection이 필요할 수 있음 | entropy면 softmax |
| sparse regularizer | proximal step 필요 | regularizer 선택으로 직접 반영 |

두 방식은 비슷한 regret 보장을 갖지만, feasible set과 regularizer에 따라 구현 난도가 달라집니다.

## Learning Rate 감각

일반적인 convex Lipschitz setting에서는 `eta`를 `1 / sqrt(T)` 계열로 둡니다. horizon을 모르면 time-varying schedule을 씁니다.

```text
eta_t = c / sqrt(t)
```

loss scale이 크면 gradient norm도 커지므로 `eta`를 줄여야 합니다. 입력 값 범위를 보지 않고 고정 상수를 쓰면 확률분포가 한 action으로 너무 빨리 붕괴합니다.

## Lagrangian과의 연결

여러 제약의 multiplier를 동시에 조정해야 할 때, violation vector를 subgradient처럼 누적할 수 있습니다.

```text
constraint violation -> gradient for dual variable
dual variable update -> new penalty
relaxed oracle solve -> new primal decision
```

이 관점은 Lagrangian relaxation에서 단일 `lambda` 이분 탐색이 어려울 때 유용합니다.
