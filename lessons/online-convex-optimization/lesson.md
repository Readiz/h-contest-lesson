# Online Convex Optimization

Online Convex Optimization은 입력이 순차적으로 공개되는 상황에서 매 라운드 결정을 먼저 내리고, 이후 관측한 loss나 gradient로 다음 결정을 갱신하는 온라인 최적화 허브입니다. 기존 Online Convex Optimization과 Dual Averaging은 같은 regret minimization 흐름 안에 있으므로, 이 허브에서 문제 모델을 먼저 구분한 뒤 필요한 update 방식으로 내려갑니다.

이 허브는 "정답 하나를 계산하는 알고리즘"보다 "반복 선택 규칙을 설계하고 그 손실을 비교하는 모델"에 가깝습니다. 대회에서는 순수 OCO보다 scheduling, online allocation, adversarial tuning, 전문가 선택, full-information feedback 판독 문제에서 자주 신호가 보입니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: convex function, gradient, projection, expected value
- 함께 보면 좋은 레슨: Bayesian Bandits, Parametric Optimization, Slope Trick
- 다음에 볼 레슨: primal-dual methods, policy gradient basics, online planning evaluation

## 1. 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 선택 후 전체 loss 함수나 gradient가 공개된다 | [Online Decision and Regret](pages/online-decision-and-regret.md) |
| feasible set이 ball, box, simplex 같은 convex set이다 | [Online Decision and Regret](pages/online-decision-and-regret.md) |
| simplex 위 확률분포를 multiplicative하게 갱신한다 | [Mirror Descent and Multiplicative Weights](pages/mirror-descent-and-multiplicative-weights.md) |
| 누적 gradient와 regularizer로 decision을 고른다 | [Dual Averaging](pages/dual-averaging.md) |
| 선택하지 않은 action의 loss를 모른다 | [Full-information and Bandit Feedback](pages/feedback-models.md) |

핵심 질문은 아래 순서로 묻는 것이 좋습니다.

```text
1. 매 라운드 decision을 먼저 해야 하는가?
2. 관측되는 정보가 전체 loss/gradient인가, 선택한 action의 결과뿐인가?
3. feasible set에 맞는 projection 또는 regularizer update가 있는가?
4. 출력은 최종 decision, 평균 policy, 또는 regret bound 중 무엇인가?
```

## 2. 학습 순서

1. [Online Decision and Regret](pages/online-decision-and-regret.md)에서 regret의 비교 대상과 projected gradient descent를 봅니다.
2. [Mirror Descent and Multiplicative Weights](pages/mirror-descent-and-multiplicative-weights.md)에서 simplex처럼 Euclidean projection이 어색한 공간을 다룹니다.
3. [Dual Averaging](pages/dual-averaging.md)은 누적 gradient를 regularizer와 함께 최소화하는 update입니다.
4. [Full-information and Bandit Feedback](pages/feedback-models.md)에서 OCO와 bandit을 구분합니다.
5. [Practice Set](pages/practice-set.md)에서 문제 신호와 구현 체크리스트를 한 번에 점검합니다.

## 3. 쓰지 말아야 할 경우

- 모든 입력을 미리 보고 하나의 최적해를 계산할 수 있으면 offline optimization이나 DP가 먼저입니다.
- 선택하지 않은 action의 loss를 알 수 없는데 full-information update를 그대로 쓰고 있습니다.
- feasible set이 convex가 아니거나 projection이 원래 문제만큼 어렵습니다.
- regret 비교 대상을 "매 라운드마다 바뀌는 최적 선택"으로 잡고 있습니다.
- loss scale, gradient norm, horizon 없이 learning rate를 임의 상수로 둡니다.

## 4. 구현 전 체크리스트

- decision이 scalar, vector, probability distribution 중 무엇인가?
- loss를 minimize하는지 reward를 maximize하는지 부호를 정했는가?
- gradient norm 또는 loss range를 bounding할 수 있는가?
- projection, softmax, clipping 중 어느 단계가 수치적으로 위험한가?
- horizon `T`가 주어지는가, 아니면 time-varying learning rate가 필요한가?
- bandit이면 exploration이나 loss estimator가 필요한가?

## 5. 연습 문제

이 허브의 연습 흐름은 [Practice Set](pages/practice-set.md)에 모읍니다. Practice Set은 full-information expert advice에서 Multiplicative Weights를 구현하고, bandit feedback과 섞지 않는 기준을 대표 연습으로 제공합니다.
