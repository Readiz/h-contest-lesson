# Online Convex Optimization

Online Convex Optimization은 입력이 순차적으로 공개되는 상황에서 매 라운드 결정을 먼저 내리고, 이후 관측한 loss나 gradient로 다음 결정을 갱신하는 온라인 최적화 허브입니다. 기존 Online Convex Optimization과 Dual Averaging은 같은 regret minimization 흐름 안에 있으므로, 이 허브에서 문제 모델을 먼저 구분한 뒤 필요한 update 방식으로 내려갑니다.

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 선택 후 전체 loss 함수나 gradient가 공개된다 | [Online Decision and Regret](pages/online-decision-and-regret.md) |
| feasible set이 ball, box, simplex 같은 convex set이다 | [Online Decision and Regret](pages/online-decision-and-regret.md) |
| simplex 위 확률분포를 multiplicative하게 갱신한다 | [Mirror Descent and Multiplicative Weights](pages/mirror-descent-and-multiplicative-weights.md) |
| 누적 gradient와 regularizer로 decision을 고른다 | [Dual Averaging](pages/dual-averaging.md) |

핵심 질문은 아래 순서로 묻는 것이 좋습니다.

```text
1. 매 라운드 decision을 먼저 해야 하는가?
2. 관측되는 정보가 전체 loss/gradient인가, 선택한 action의 결과뿐인가?
3. feasible set에 맞는 projection 또는 regularizer update가 있는가?
4. 출력은 최종 decision, 평균 policy, 또는 regret bound 중 무엇인가?
```

## 라운드 뒤에 관측하는 정보

| 관측 | 사용할 수 있는 갱신 |
| --- | --- |
| 모든 expert의 loss | Multiplicative Weights, Dual Averaging |
| 선택점의 gradient/subgradient | OGD, Mirror Descent |
| 선택한 action의 결과만 | Bandit의 탐색·추정 방법 필요 |
| Simulator trajectory | Planning 또는 RL 모델 확인 |

예를 들어 loss vector `[3, 5, 1, 4]`가 공개되면 모든 expert를 갱신할 수 있습니다. Action 2의 loss가 5라는 정보만 받았다면 나머지 loss는 미관측입니다. 이를 0으로 채우면 올바른 full-information 갱신이 되지 않습니다. Regret의 비교 대상도 고정 action인지, 고정 convex decision인지 명시합니다.

## 연습

[로컬 연습](pages/practice-set.md)에서 입력과 검증 기준을 확인합니다.
