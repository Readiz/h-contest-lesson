# Practice Set

Probabilistic Decision AI 계열은 정확 알고리즘과 근사 planning의 평가 기준이 다릅니다. 아직 적절한 h-contest 문제 링크가 없는 항목은 임의 ID를 만들지 않고 `TODO`로 둡니다.

## 로컬 완결형 연습

### Feedback Model Classification

네 개의 짧은 statement를 만들고, 각 statement를 `full-information`, `bandit`, `simulator`, `hidden-state observation`으로 분류합니다. 답안에는 "왜 다른 모델이 아닌지"를 한 문장씩 붙입니다.

```text
1. 선택 후 모든 후보의 loss가 공개된다.
2. 선택한 arm의 reward만 공개된다.
3. action sequence를 넣으면 simulator가 sampled trajectory를 반환한다.
4. 실제 state는 숨겨져 있고 observation만 공개된다.
```

이 연습의 목표는 구현보다 모델 누수를 막는 것입니다. 특히 2번에서 선택하지 않은 arm의 reward를 0으로 채우거나, 4번에서 hidden state를 직접 policy state로 쓰면 실패로 처리합니다.

## h-contest 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: feedback boundary `/practice/...` 문제 필요 | 관측 모델 분류 | full-information vs bandit |
| 입문 | TODO: finite MDP `/practice/...` 문제 필요 | horizon DP와 Bellman 식 | MDP |
| 입문 | TODO: stochastic shortest path `/practice/...` 문제 필요 | absorbing goal과 proper policy | SSP |
| 표준 | TODO: MCTS toy game `/practice/...` 문제 필요 | selection/rollout/backprop | UCT |
| 표준 | TODO: hidden-state search `/practice/...` 문제 필요 | belief filtering | imperfect information |
| 응용 | TODO: POMDP belief update `/practice/...` 문제 필요 | Bayes update | observation model |
| 응용 | TODO: bandit simulation `/practice/...` 문제 필요 | posterior update와 regret | Thompson sampling |
| 심화 | TODO: online planning evaluation `/practice/...` 문제 필요 | paired seed benchmark | time budget |

## 완료 기준

- exact solver인지 heuristic planning인지 먼저 표시합니다.
- stochastic transition의 확률합을 검증합니다.
- sampling 기반이면 seed, budget, variance를 함께 기록합니다.
- hidden state 문제는 belief update 식을 명시합니다.
- online planning은 score뿐 아니라 deadline miss를 같이 봅니다.
