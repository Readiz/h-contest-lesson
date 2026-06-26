# Full-information and Bandit Feedback

Online Convex Optimization 계열에서 가장 먼저 구분해야 할 것은 feedback 모델입니다. 같은 regret이라는 단어를 쓰더라도, 매 라운드 전체 loss를 보는지 선택한 action의 결과만 보는지에 따라 사용할 수 있는 update가 완전히 달라집니다.

## 1. Feedback 모델 표

| 모델 | 관측 | 대표 업데이트 | 주의점 |
| --- | --- | --- | --- |
| Full-information experts | 모든 action의 loss | Multiplicative Weights, Dual Averaging | 전체 loss vector가 실제로 주어져야 함 |
| Gradient feedback | 선택점의 gradient/subgradient | OGD, Mirror Descent | convexity와 gradient bound 필요 |
| Bandit feedback | 선택한 action의 reward/loss만 | UCB, Thompson Sampling, EXP3 | exploration 또는 loss estimator 필요 |
| Simulator feedback | sample trajectory | RL, policy search | exact Bellman DP와 구분 필요 |

문제 statement가 "선택 후 모든 후보의 비용을 알려 준다"라고 말하면 full-information에 가깝습니다. "선택한 서버의 latency만 알 수 있다"처럼 관측이 선택에 묶여 있으면 bandit입니다.

## 2. 흔한 오독

아래처럼 loss vector가 매 라운드 주어진다면 Dual Averaging simplex update를 바로 쓸 수 있습니다.

```text
round 1 losses: 3 5 1 4
round 2 losses: 2 0 6 3
```

반대로 아래처럼 선택한 action의 결과만 주어진다면, 나머지 action의 loss는 관측되지 않았습니다.

```text
choose action 2
observed loss: 5
```

이때 관측하지 않은 loss를 0으로 두거나 이전 값으로 채우면 full-information 문제로 바뀐 것이 아니라 잘못된 estimator를 만든 것입니다.

## 3. OCO와 Bandit의 경계

| 질문 | OCO 쪽 신호 | Bandit 쪽 신호 |
| --- | --- | --- |
| 선택하지 않은 action의 결과를 아는가? | 예 | 아니오 |
| gradient가 주어지는가? | 예 | 보통 아니오 |
| projection이나 regularizer가 핵심인가? | 예 | exploration이 더 중요 |
| 출력이 deterministic decision인가? | 가능 | 보통 randomized policy |

Bandit을 OCO처럼 풀 수 있는 경우도 있지만, 그때는 importance weighting 같은 loss estimator가 필요합니다. 이 허브에서는 full-information OCO를 중심으로 다루고, bandit은 Bayesian Bandits나 별도 online learning 트랙으로 넘깁니다.

## 4. 문제를 읽을 때 체크할 문장

- "After each round, the whole cost array is revealed"이면 full-information입니다.
- "You only observe the reward of the selected action"이면 bandit입니다.
- "The gradient at your chosen point is revealed"이면 OGD/Mirror Descent를 의심합니다.
- "The transition table is unknown and you can simulate episodes"이면 RL 또는 online planning입니다.

## 5. 구현 전 결정

1. 관측되지 않은 loss를 어떻게 처리할지 먼저 정합니다.
2. full-information이 아니면 OCO 코드 조각을 그대로 가져오지 않습니다.
3. regret 비교 대상이 고정 action인지, 고정 convex decision인지, adaptive policy인지 확인합니다.
4. randomization이 필요한 경우 seed, 기대값, 출력 형식을 별도로 검토합니다.
