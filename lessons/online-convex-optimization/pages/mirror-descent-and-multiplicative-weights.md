# Mirror Descent and Multiplicative Weights

Mirror Descent는 Euclidean distance가 문제의 decision space와 잘 맞지 않을 때, 다른 regularizer가 만드는 geometry에서 한 걸음 이동하는 관점입니다. Online Convex Optimization에서 가장 자주 쓰는 예시는 simplex 위의 entropy regularizer이고, 이는 Multiplicative Weights update로 나타납니다.

## 1. 왜 projection만으로 부족한가

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

## 2. Entropy Regularizer와 Simplex

확률분포 `p`에 entropy 계열 regularizer를 쓰면 update가 softmax 또는 weight 곱셈 형태가 됩니다.

```text
weight_i <- weight_i * exp(-eta * loss_i)
p_i <- weight_i / sum_j weight_j
```

loss가 큰 action은 weight가 감소하고, loss가 작은 action은 상대적으로 커집니다. 모든 action의 weight가 양수로 유지되므로 탐색이 완전히 사라지지는 않지만, 이 자체가 bandit exploration을 해결한다는 뜻은 아닙니다.

## 3. 작은 추적 예시

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

## 4. Dual Averaging과의 관계

Multiplicative Weights를 매 라운드 loss에 대해 곱한다고 써도 되고, 지금까지의 누적 loss `L_i`로 아래처럼 써도 됩니다.

```text
p_i ∝ exp(-eta * L_i)
```

이 두 표현은 고정 `eta`에서는 같은 update를 다른 방식으로 본 것입니다. [Dual Averaging](dual-averaging.md)은 이 누적 gradient 표현을 regularized surrogate minimization으로 일반화합니다.

## 5. 실수 포인트

1. reward를 loss처럼 넣어 부호를 반대로 갱신한다.
2. exponential overflow를 막기 위한 max-shift를 하지 않는다.
3. bandit 문제에서 관측하지 않은 action loss까지 안다고 가정한다.
4. simplex가 아닌 feasible set에 softmax update를 억지로 적용한다.
5. `eta`가 너무 커서 초반 몇 라운드만에 한 action으로 확률이 붕괴한다.
