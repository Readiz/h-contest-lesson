# Online Convex Optimization

Online Convex Optimization은 매 라운드 선택을 먼저 하고 그 뒤 손실 함수나 gradient를 관측하는 문제를 regret 관점으로 다루는 최적화 틀입니다. 대회 문제에서 순수 OCO가 그대로 나오지는 않지만, adversarial input, 반복 의사결정, projection, mirror descent 신호를 읽는 데 유용합니다.

이 레슨은 Convex DP Modeling, Convex Hull Trick Variants, Probability 이후에 보는 전략과 최적화 심화입니다.

1. 매 라운드 decision을 feasible convex set 안에서 고른다.
2. 손실을 본 뒤 gradient나 subgradient로 다음 decision을 갱신한다.
3. 최적 고정 decision과의 차이인 regret을 작게 만드는 것이 목표다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: convex function, gradient, projection, expected value
- 함께 보면 좋은 레슨: Convex DP Modeling, Parametric DP, Bayesian Bandits
- 다음에 볼 레슨: mirror descent, online learning, adaptive regret

## 1. 문제 신호

| 문제 표현 | OCO 관점 |
| --- | --- |
| 입력이 순차적으로 들어오고 즉시 선택해야 한다 | online decision |
| 선택 후 비용 함수가 공개된다 | loss feedback |
| 전체 최적을 미리 알 수 없다 | regret minimization |
| 선택 공간이 구간, simplex, ball이다 | convex feasible set |
| gradient만 알 수 있다 | online gradient descent |

OCO는 "정답 하나를 계산"하기보다 "반복 선택 규칙을 설계"하는 문제에 가깝습니다. 실전에서는 확률적 bandit, scheduling, adaptive tuning 문제를 해석하는 보조 언어로 쓰입니다.

## 2. Regret

라운드 `t`에서 선택 `x_t`를 하고 손실 `f_t(x_t)`를 냅니다. 비교 대상은 사후에 알 수 있는 가장 좋은 고정 선택 `x*`입니다.

```text
regret(T) = sum f_t(x_t) - min_x sum f_t(x)
```

regret이 `o(T)`이면 라운드 평균 손실은 최적 고정 선택과 가까워집니다. 즉 매 순간 완벽하지 않아도 장기적으로 좋은 선택 규칙입니다.

## 3. Online Gradient Descent

가장 기본적인 규칙은 gradient 반대 방향으로 조금 이동한 뒤 feasible set으로 projection하는 것입니다.

```text
x_{t+1} = projection_C(x_t - eta_t * g_t)
```

`C`가 구간이면 clamp, Euclidean ball이면 반지름으로 정규화, simplex이면 simplex projection을 사용합니다.

## 4. Projection 구현 조각

아래 코드는 Euclidean ball 제약에서 online gradient descent를 수행합니다.

```cpp compile-check
#include <cmath>
#include <vector>
using namespace std;

double squaredNorm(const vector<double>& values) {
    double total = 0.0;
    for (double value : values) {
        total += value * value;
    }
    return total;
}

void projectToBall(vector<double>& point, double radius) {
    double norm = sqrt(squaredNorm(point));
    if (norm <= radius || norm == 0.0) {
        return;
    }
    double scale = radius / norm;
    for (double& value : point) {
        value *= scale;
    }
}

vector<double> onlineGradientDescent(
    int dimension,
    const vector<vector<double>>& gradients,
    double radius,
    double learningRate
) {
    vector<double> point(dimension, 0.0);
    for (const vector<double>& gradient : gradients) {
        for (int i = 0; i < dimension; ++i) {
            point[i] -= learningRate * gradient[i];
        }
        projectToBall(point, radius);
    }
    return point;
}
```

실제 문제에서는 `learningRate`를 `1 / sqrt(t)` 계열로 줄이거나, gradient norm upper bound에 맞춥니다.

## 5. 작은 예시

```text
선택: x in [-1, 1]
라운드 손실: f_t(x) = a_t * x
gradient: a_t
```

`a_t`가 양수로 많이 나오면 손실을 줄이기 위해 `x`는 음수 쪽으로 이동합니다. 반대로 음수가 많이 나오면 양수 쪽으로 갑니다. adversarial하게 부호가 바뀌어도 projection 때문에 선택은 항상 feasible range 안에 남습니다.

## 6. Mirror Descent 직관

Euclidean projection이 어색한 공간에서는 mirror descent를 씁니다. 예를 들어 확률분포 simplex에서는 좌표를 직접 빼는 것보다 entropy regularizer로 multiplicative weights 형태가 자연스럽습니다.

```text
weight_i <- weight_i * exp(-eta * loss_i)
normalize weights
```

이 방식은 전문가 선택, online routing, 확률적 action mixing 문제에서 자주 보입니다.

## 7. Bandit과의 차이

| 기준 | OCO full-information | Bandit |
| --- | --- | --- |
| 관측 | 손실 함수나 gradient 전체 | 선택한 action의 보상만 |
| 대표 기법 | OGD, mirror descent | UCB, Thompson Sampling |
| 목표 | regret 최소화 | regret 최소화 |
| 난점 | projection, gradient bound | exploration |

문제가 선택하지 않은 action의 손실을 알려 주면 OCO에 가깝고, 선택한 것만 알려 주면 bandit 쪽입니다.

## 8. 시간 복잡도 감각

| 작업 | 시간 |
| --- | ---: |
| gradient update | `O(d)` |
| Euclidean ball projection | `O(d)` |
| box projection | `O(d)` |
| simplex projection | `O(d log d)` |
| multiplicative weights | `O(d)` |

dimension이 크면 projection이 병목이 됩니다. feasible set이 단순한지부터 확인합니다.

## 9. 자주 하는 실수

1. 손실을 본 뒤에 같은 라운드 선택을 바꾸는 offline 풀이로 착각한다.
2. projection을 하지 않아 feasible constraint를 깨뜨린다.
3. learning rate를 손실 scale과 맞추지 않는다.
4. regret 비교 대상을 매 라운드 바뀌는 최적 선택으로 잡는다.
5. bandit feedback 문제에서 full gradient를 안다고 가정한다.
6. convex가 아닌 손실에 OGD 보장을 그대로 적용한다.

## 10. 문제를 볼 때 체크할 조건

- 선택을 입력 전후 어느 시점에 해야 하는가?
- 손실 함수 전체를 관측하는가, 선택한 결과만 관측하는가?
- feasible set이 convex인가?
- gradient나 subgradient를 계산할 수 있는가?
- 필요한 것은 최적값인가, 낮은 regret의 policy인가?
- randomization이 허용되는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: online gradient descent `/practice/...` 문제 필요 | gradient step과 projection | regret |
| 표준 | TODO: multiplicative weights `/practice/...` 문제 필요 | simplex decision 갱신 | entropy |
| 응용 | TODO: online scheduling convex loss `/practice/...` 문제 필요 | sequential decision 설계 | projection |
| 함정 | TODO: bandit vs full information `/practice/...` 문제 필요 | feedback model 구분 | exploration |
