# Imperfect Information Search

Imperfect Information Search는 상대의 패, 숨겨진 상태, 랜덤 seed처럼 모든 정보를 볼 수 없는 게임/탐색 문제를 다룹니다. 완전 정보 Minimax나 기본 MCTS와 달리, 실제 상태 하나가 아니라 가능한 상태들의 집합과 믿음 분포를 함께 관리해야 합니다.

## 문제 신호

| 문제 표현 | Imperfect Information 관점 |
| --- | --- |
| 상대의 카드를 모른다 | information set |
| 같은 관측에서 실제 상태가 여러 개 가능 | belief state |
| hidden state가 action 결과로 일부 드러남 | belief update |
| 랜덤 event와 관측이 섞임 | POMDP 모델 |
| 완전 정보로 가정하면 전략이 과하게 낙관적 | strategy fusion 위험 |

숨은 정보를 임의로 하나 정하고 완전 정보 게임처럼 풀면 빠르지만, 잘못된 확신을 만들 수 있습니다.

## Information Set

Information set은 현재 플레이어가 구분할 수 없는 실제 상태들의 묶음입니다.

```text
관측: 내 패, 공개 보드, 지나간 행동
숨은 정보: 상대 패, 덱 순서
information set = 관측과 일치하는 모든 실제 상태
```

탐색 node를 실제 상태가 아니라 information set으로 잡으면 같은 관측에서 같은 전략을 선택하도록 만들 수 있습니다.

## Belief Update

행동과 관측이 들어오면 가능한 상태를 걸러내고 확률을 다시 정규화합니다.

임의 상태 ID의 나머지 연산으로 관측 모델을 대신하지 않습니다. 실제 전이 확률과 관측 likelihood를 사용하는 [POMDP belief 갱신](https://h.readiz.com/learn/probabilistic-decision-ai/pomdp)을 재사용합니다. 정적인 숨은 상태의 결정적 관측인 경우에만 후보 제거 후 정규화로 줄어듭니다.

예시의 `isConsistentWithObservation`은 문제별 규칙으로 바꿔야 합니다. 핵심은 불가능한 상태를 제거하고 남은 확률을 다시 합 1로 만드는 것입니다.

## Determinization

가장 단순한 접근은 숨은 정보를 여러 번 샘플링해 완전 정보 상태로 만든 뒤 각각 탐색하는 것입니다.

```text
for sampled hidden state:
    run minimax or MCTS as if fully known
aggregate action scores
```

구현이 쉽고 빠르지만 한계가 있습니다. 각 샘플에서는 원래 알 수 없는 정보를 알고 있는 것처럼 행동하므로, 실제 게임에서는 불가능한 전략을 평균낼 수 있습니다.

## Strategy Fusion과 Information Leakage

대표적인 함정은 strategy fusion입니다. 서로 다른 hidden state에서 같은 관측을 가진 플레이어가 서로 다른 행동을 고르는 것처럼 계산하는 문제입니다.

```text
실제로는 두 상태를 구분할 수 없음
하지만 determinization별 탐색은 구분해서 최적 행동을 고름
=> 평균 점수가 과대평가됨
```

그래서 중요한 문제에서는 action을 information set 단위로 묶거나, information set MCTS처럼 관측 기준 node를 만들어야 합니다.

## Information Set MCTS

Information Set MCTS는 node 통계를 실제 상태가 아니라 관측 가능한 history나 information set에 저장합니다.

| 단계 | 차이점 |
| --- | --- |
| selection | information set node의 UCB를 사용 |
| expansion | 관측 가능한 action을 확장 |
| simulation | hidden state를 샘플링해 rollout |
| backpropagation | 같은 information set 통계로 누적 |

완전한 구현은 도메인 의존적입니다. 그래도 "통계 저장 단위가 실제 hidden state가 아니다"라는 점을 지키면 정보 누출을 줄일 수 있습니다.

## Belief State Search

상태 수가 작으면 belief distribution 자체를 state로 보고 MDP처럼 풀 수 있습니다.

```text
belief --action--> observation distribution --updated belief
```

이 모델은 POMDP에 가깝습니다. 정확 풀이는 비싸지만, 상태 수가 작거나 horizon이 짧으면 가능한 belief를 map으로 memoization할 수 있습니다.

## 어떤 접근을 고를까

| 상황 | 접근 |
| --- | --- |
| 숨은 경우의 수가 작음 | belief state DP/search |
| 상태가 크고 rollout이 쉬움 | information set MCTS |
| 빠른 heuristic이 필요 | 여러 determinization 평균 |
| 상대 모델이 중요 | opponent modeling 추가 |
| 정확한 증명이 필요한 문제 | 숨은 정보를 상태에 포함한 DP 가능성부터 확인 |

대회 문제에서는 완전한 게임 AI보다 "숨은 정보 때문에 상태를 어떻게 표현할 것인가"가 핵심인 경우가 많습니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| belief filtering | `O(number of candidates)` |
| determinization `K`개 | `K * search cost` |
| information set MCTS | `iterations * rollout cost` |
| exact belief DP | belief state 수에 따라 지수적으로 증가 가능 |

숨은 상태 후보가 너무 많으면 sampling이나 compressed belief가 필요합니다.
