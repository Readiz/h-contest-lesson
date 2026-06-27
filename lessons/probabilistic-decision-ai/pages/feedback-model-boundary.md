# Feedback Model Boundary

Feedback Model Boundary는 Online Convex Optimization, Bayesian Bandits, MCTS, POMDP를 섞어 읽지 않기 위한 판독 페이지입니다. 같은 "매 턴 하나를 선택한다"는 문장이라도, 선택 뒤 무엇을 관측하는지에 따라 쓸 수 있는 알고리즘이 달라집니다.

## 1. 네 가지 관측 모델

| 모델 | 선택 뒤 보이는 것 | 대표 접근 | 착각하면 생기는 문제 |
| --- | --- | --- | --- |
| Full-information | 모든 action의 loss/reward 또는 gradient | OCO, multiplicative weights | bandit 문제를 너무 쉽게 품 |
| Bandit feedback | 선택한 action의 결과만 | UCB, Thompson Sampling, EXP3 | 관측하지 않은 loss를 안다고 가정 |
| Simulator feedback | 선택 sequence의 sampled trajectory | MCTS, rollout evaluation | single seed score로 정책을 고름 |
| Hidden-state observation | 실제 state가 아니라 observation | POMDP, belief update, POMCP | hidden state를 직접 알고 행동함 |

첫 질문은 "정답을 계산할 model table이 있는가, 아니면 선택한 결과만 관측하는가"입니다. 전이확률과 보상표가 모두 주어지면 MDP DP가 후보이고, 선택한 arm의 결과만 보이면 bandit입니다. simulator만 있으면 exact Bellman update보다 rollout 평가와 sampling budget을 먼저 봅니다.

## 2. 판독 순서

1. 매 라운드 이후 모든 후보의 cost가 공개되는지 확인합니다.
2. 공개되지 않는다면 선택한 action의 reward만 관측하는지, trajectory sample을 받는지 구분합니다.
3. state가 완전히 보이는지, observation만 보이는지 확인합니다.
4. model table이 주어지는지, generative simulator만 호출 가능한지 확인합니다.
5. judge가 exact answer를 요구하는지, policy 성능을 평가하는지 확인합니다.

이 다섯 질문에 답하지 못한 상태에서 OCO update, bandit posterior, MCTS rollout, POMDP belief를 고르면 대부분 모델을 잘못 읽은 것입니다.

## 3. 작은 예시

### Full-information experts

```text
매일 하나의 expert를 선택한다.
하루가 끝나면 모든 expert의 loss vector가 공개된다.
목표는 내 누적 loss와 best expert 누적 loss의 차이를 줄이는 것이다.
```

이 경우에는 선택하지 않은 expert의 loss도 알 수 있으므로 multiplicative weights 같은 full-information update를 쓸 수 있습니다. exploration을 별도로 넣지 않아도 update에 필요한 loss vector가 있습니다.

### Bandit arms

```text
매일 하나의 광고를 선택한다.
클릭 여부는 선택한 광고에 대해서만 관측된다.
목표는 총 클릭 수를 늘리는 것이다.
```

선택하지 않은 광고의 reward는 없습니다. full-information loss vector를 0으로 채우면 모델을 바꾼 것이 아니라 잘못된 estimator를 만든 것입니다. posterior나 confidence bound처럼 불확실성을 다루는 장치가 필요합니다.

### Simulator planning

```text
현재 state에서 action을 고르면 simulator가 다음 state와 reward를 sample한다.
시간 제한 안에서 action 하나를 출력해야 한다.
```

전이표 전체를 알 수 없다면 exact value iteration이 아니라 rollout 기반 planning입니다. MCTS를 쓰더라도 seed, iteration budget, deadline miss를 같이 관리해야 합니다.

### Hidden-state observation

```text
상대의 손패는 숨겨져 있고, 공개 action과 observation만 볼 수 있다.
```

node를 실제 hidden state로 만들면 정보 누출이 생깁니다. 통계와 policy는 observation history 또는 belief 단위로 관리해야 합니다.

## 4. 경계 반례

| 잘못 읽은 문장 | 왜 틀렸는가 | 바른 분류 |
| --- | --- | --- |
| "선택하지 않은 arm은 reward 0으로 둔다" | 관측되지 않은 값을 만든 것 | bandit feedback |
| "simulator를 많이 돌려 평균을 내면 exact DP다" | sample 평균은 근사이며 variance가 남음 | simulator feedback |
| "관측값을 state로 두면 POMDP가 MDP가 된다" | 같은 observation 뒤에 여러 hidden state가 가능 | hidden-state observation |
| "loss vector가 공개되지만 선택한 loss만 update한다" | 사용할 수 있는 정보를 버림 | full-information |

## 5. 로컬 완결형 연습

아래 네 문제 설명을 읽고 모델을 분류합니다. 답안에는 `full-information`, `bandit`, `simulator`, `hidden-state` 중 하나 이상을 쓰고, 쓰면 안 되는 대표 알고리즘도 함께 적습니다.

```text
A. 각 round가 끝나면 모든 서버의 latency가 공개된다.
B. 선택한 슬롯머신의 성공/실패만 관측된다.
C. 게임 state를 넣으면 simulator가 random rollout 하나를 반환한다.
D. 관측은 센서 값뿐이고 실제 위치는 확률적으로만 추정된다.
```

기대 답:

| 항목 | 분류 | 피해야 할 해석 |
| --- | --- | --- |
| A | full-information | bandit exploration이 필수라고 가정 |
| B | bandit feedback | 선택하지 않은 arm reward를 알고 있다고 가정 |
| C | simulator feedback | exact transition table이 있다고 가정 |
| D | hidden-state observation | 실제 state 기준으로 policy를 학습 |

## 6. 문제를 볼 때 체크할 조건

- 선택하지 않은 action의 결과가 공개되는가?
- transition/reward table이 입력으로 주어지는가?
- simulator call budget과 wall-clock deadline이 있는가?
- state가 완전 관측인가, observation만 주어지는가?
- 제출물이 exact value인지, policy/agent인지 구분했는가?

## 7. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: feedback classification `/practice/...` 문제 필요 | full-information과 bandit 구분 | observed loss |
| 표준 | TODO: simulator planning boundary `/practice/...` 문제 필요 | exact DP와 rollout 근사 구분 | generative model |
| 응용 | TODO: hidden-state feedback `/practice/...` 문제 필요 | belief 기준 policy 확인 | observation history |
| 함정 | TODO: leakage counterexample `/practice/...` 문제 필요 | 관측하지 않은 값 사용 금지 | information leak |
