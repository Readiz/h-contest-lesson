# POMCP

POMCP(Partially Observable Monte Carlo Planning)는 POMDP를 belief table 전체로 풀지 않고, particle belief와 UCT 탐색을 결합해 online action을 고르는 방법입니다. PBVI가 대표 belief point에서 value function을 근사한다면, POMCP는 현재 belief에서 simulation tree를 키워 다음 행동을 고릅니다.


각 simulation은 현재 root belief에서 상태를 새로 뽑아 시작합니다. rollout policy도 관측 가능한 history로 행동해야 하며 숨은 상태를 직접 이용하지 않습니다. 실제 관측 뒤 particle이 소진되면 모델에 맞는 보강이 필요합니다.

## 문제 신호

| 문제 표현 | POMCP 관점 |
| --- | --- |
| hidden state가 크고 observation만 보임 | particle belief |
| transition/observation table은 크지만 simulator가 있음 | generative model |
| 매 턴 제한 시간 안에 action 선택 | online MCTS |
| 정확한 optimal value보다 좋은 정책 필요 | rollout evaluation |
| observation history가 policy state | history tree |

POMCP는 보통 interactive AI나 simulator planning에 맞습니다. 정답이 하나로 고정된 알고리즘 judge 문제에는 잘 맞지 않습니다.

## History Tree

POMCP의 node는 실제 state가 아니라 action-observation history입니다.

```text
h = o0, a0, o1, a1, o2, ...
```

같은 history에 도달한 particle state들을 node에 모으고, 그 node에서 UCT로 action을 선택합니다. state를 완전히 알 수 없기 때문에 history가 search tree의 key가 됩니다.

## Particle Belief

belief를 확률 배열로 전부 갱신하지 않고, 가능한 state sample들을 유지합니다.

```text
belief particles:
  s1, s7, s7, s3, s2, ...
```

같은 state가 여러 번 나오면 그만큼 확률 질량이 큰 것으로 봅니다. 실제 observation을 받은 뒤에는 그 observation과 일치하는 particle을 resampling합니다.

## UCT 선택 Skeleton

아래 코드는 history node에서 action을 고르는 UCT 부분만 분리한 skeleton입니다.

UCT의 보상 평균+탐색 항은 [Monte Carlo Tree Search](https://h.readiz.com/learn/probabilistic-decision-ai/monte-carlo-tree-search)을 재사용합니다. POMCP에서는 같은 history의 action 통계를 사용하며, 한 플레이어의 할인 return을 누적하므로 플레이어 교대 보상 반전은 적용하지 않습니다.

POMCP 전체 구현에서는 action 이후 simulator가 next state, observation, reward를 반환하고, observation별 child history로 내려갑니다.

## Simulation 흐름

```text
simulate(state s, history h, depth d):
  if depth limit: return 0
  if h not in tree: expand h and rollout from s
  choose action a by UCT at h
  simulator samples (s', observation o, reward r)
  R = r + gamma * simulate(s', h+a+o, d+1)
  N(h)++, N(h,a)++, valueSum(h,a) += R
  return R
```

tree policy는 방문한 history에서만 쓰고, 처음 보는 history는 rollout policy로 값을 추정합니다.

## 작은 예시

```text
hidden state: treasure is left/right
actions: check-left, check-right, open-left, open-right
observations: beep/no-beep
```

POMCP는 현재 particle belief에서 state 하나를 뽑고, `check-left` 같은 action을 simulation합니다. observation이 `beep`이면 그 history node가 자라고, 이후 `open-left`의 보상이 simulation으로 누적됩니다.

명시적으로 `P(state | history)` 전체를 계산하지 않아도, particle과 simulator로 action value를 근사합니다.

## PBVI와 비교

| 기준 | PBVI | POMCP |
| --- | --- | --- |
| belief 표현 | 대표 belief point와 alpha vector | particle belief |
| planning 방식 | offline 반복 backup | online simulation |
| model 요구 | transition/observation table이 있으면 좋음 | generative simulator가 중요 |
| 출력 | approximate policy/value | 현재 history의 action |
| 큰 상태 공간 | point 선택이 어려움 | sampling으로 완화 |

현재 한 번의 action을 잘 고르는 것이 목표라면 POMCP가 자연스럽고, policy를 미리 계산해야 하면 PBVI가 더 맞을 수 있습니다.

## Root Belief Update

실제 action을 실행하고 observation을 받으면 root history를 한 단계 내립니다.

```text
old root: h
take action a, observe o
new root: h+a+o
```

새 root의 particle이 부족하면 rejection sampling이나 particle reinvigoration으로 채웁니다. 이 단계가 약하면 belief가 빈약해져 탐색이 한쪽으로 쏠립니다.
