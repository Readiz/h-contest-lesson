# Stochastic Decision Process Practice Set

이 페이지는 MDP, RL, SSP 계열을 하나의 흐름으로 연습하기 위한 목록입니다. 아직 적절한 h-contest 문제가 없는 칸은 임의 ID를 넣지 않고 `TODO`로 둡니다.

## 로컬 완결형 연습

### 유한 턴 보상 최적화

```text
입력
N M T S
각 상태의 action 목록
각 action의 transition 목록: nextState probability reward

목표
시작 상태 S에서 T턴 동안 얻을 수 있는 최대 기대 보상을 출력
```

`dp[turn][state]`를 뒤에서 앞으로 계산합니다. 이 문제는 수렴 반복이 아니라 정확한 finite horizon DP로 풀어야 합니다.

### 목표까지 기대 비용

```text
입력
N goal
각 상태의 action 목록
각 action의 transition 목록: nextState probability cost

목표
goal까지의 최소 기대 비용을 구하거나, 도달할 수 없으면 INF를 출력
```

먼저 goal에 도달 가능한 proper policy가 있는지 판단하고, 작은 입력에서는 Bellman 식을 선형 방정식으로 세우는 방식까지 검증합니다.

## h-contest 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: finite horizon MDP `/practice/...` 문제 필요 | 남은 턴 DP 작성 | layer DP |
| 표준 | TODO: discounted value iteration `/practice/...` 문제 필요 | 오차 기준이 있는 Bellman 반복 | gamma |
| 응용 | TODO: policy evaluation `/practice/...` 문제 필요 | 고정 policy의 value 계산 | linear equation |
| 함정 | TODO: stochastic shortest path `/practice/...` 문제 필요 | improper policy와 INF 처리 | absorbing state |
