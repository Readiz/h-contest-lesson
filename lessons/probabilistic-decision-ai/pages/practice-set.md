# Practice Set

Probabilistic Decision AI 계열은 정확 알고리즘과 근사 planning의 평가 기준이 다릅니다. 아직 적절한 h-contest 문제 링크가 없는 항목은 임의 ID를 만들지 않고 `TODO`로 둡니다.

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
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
