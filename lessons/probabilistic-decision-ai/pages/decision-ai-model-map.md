# Decision AI Model Map

확률적 의사결정/게임 AI 문제는 정확한 Bellman DP, hidden-state belief update, simulation planning, bandit 학습이 한 문장에 섞여 보일 수 있습니다. 먼저 관측 가능성과 모델 제공 방식을 나눕니다.

## 1. 네 축

| 축 | 질문 | 대표 모델 |
| --- | --- | --- |
| Full state observed | 현재 상태를 정확히 아는가? | MDP, SSP |
| Partial observation | 실제 상태 대신 observation만 받는가? | POMDP, imperfect information |
| Simulator only | 전이표 대신 rollout만 가능한가? | MCTS, POMCP |
| Unknown reward model | action reward 분포를 학습해야 하는가? | Bayesian Bandits |

## 2. 선택 기준

| 상황 | 후보 |
| --- | --- |
| 선택 뒤 무엇을 관측하는지가 핵심이다 | feedback model boundary |
| 전이표와 보상표가 있고 horizon이 작다 | finite horizon DP |
| discount가 있고 오차 허용이 있다 | value iteration |
| absorbing goal까지 기대 비용을 구한다 | stochastic shortest path |
| state는 숨겨졌지만 belief를 작게 유지할 수 있다 | POMDP belief DP |
| belief space가 크고 근사가 허용된다 | PBVI 또는 POMCP |
| 매 턴 제한 시간 안에 action 하나를 골라야 한다 | MCTS/POMCP |
| 선택하지 않은 arm의 reward를 모른다 | bandit |

관측 모델 자체가 헷갈리면 먼저 Feedback Model Boundary를 봅니다. full-information, bandit, simulator, hidden-state observation을 구분한 뒤에야 MDP, MCTS, POMDP, Bayesian Bandits 중 하나를 안전하게 고를 수 있습니다.

## 3. 쓰지 말아야 할 경우

1. 정확한 정답을 요구하는 judge 문제에 MCTS 같은 근사를 답으로 제출한다.
2. partial observation 문제를 현재 관측값만 state로 둔 MDP로 처리한다.
3. `gamma = 1`인데 terminal/proper policy 없이 value iteration을 돌린다.
4. bandit 문제를 full-information online optimization처럼 읽는다.
5. planning 성능을 single seed score만으로 비교한다.
