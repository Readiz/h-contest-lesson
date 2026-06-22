# Global Min Cut Applications

Global Min Cut Applications는 Stoer-Wagner로 값을 구하는 단계를 넘어, cut 후보를 모델링하고 여러 min cut 정보를 해석하는 응용 레슨입니다. 무향 그래프의 최약 연결부를 찾는 문제는 단순 계산뿐 아니라 cactus representation, Gomory-Hu Tree, edge criticality 같은 관점으로 확장됩니다.

이 레슨은 Global Min Cut과 Cut Sparsification 이후에 보는 그래프 심화입니다.

1. global min cut 값과 실제 cut partition이 각각 언제 필요한지 구분한다.
2. 여러 minimum cut을 다루는 문제에서 cactus/cut tree 관점을 이해한다.
3. edge 중요도, network vulnerability, repeated cut query를 적절한 구조로 모델링한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Global Min Cut, Stoer-Wagner, Gomory-Hu Tree, cut value
- 함께 보면 좋은 레슨: Cut Sparsification, Max Flow와 Min Cut, Gomory-Hu Tree
- 다음에 볼 레슨: cactus representation, cut sensitivity, randomized min cut

## 1. 문제 신호

| 문제 표현 | 응용 관점 |
| --- | --- |
| 네트워크의 가장 취약한 분리와 그 구성 | min cut value + partition 복원 |
| 최소 cut이 여러 개인지 판단 | min cut family |
| 모든 pair의 병목 cut 질의 | Gomory-Hu Tree |
| edge를 하나 제거/강화했을 때 영향 | cut sensitivity |
| dense graph에서 반복 min cut | sparsification 또는 contraction 후보 |

값만 묻는 문제와 cut 자체를 묻는 문제는 구현이 다릅니다. Stoer-Wagner 기본 구현은 값만 반환하기 쉽기 때문에 partition이 필요하면 phase의 마지막 집합을 함께 저장해야 합니다.

## 2. Partition 복원

Stoer-Wagner phase에서 마지막으로 추가된 정점 `t`와 phase의 selected set은 하나의 `s-t` cut 후보를 이룹니다. contraction된 super node가 어떤 원래 정점을 포함하는지 추적하면 실제 partition도 복원할 수 있습니다.

```text
각 active vertex마다 원래 정점 목록 group[v]를 둔다
phase 마지막 selected = t
candidate side = group[t]
best가 갱신되면 candidate side 저장
contract s += t 할 때 group[s]에 group[t]를 합친다
```

이 방식은 global min cut 중 하나를 복원합니다. 모든 minimum cut을 나열하는 것은 별도 구조가 필요합니다.

## 3. 여러 Minimum Cut

minimum cut이 하나가 아닐 수 있습니다. 예를 들어 cycle graph에서는 같은 값의 cut이 여러 개 생깁니다.

| 필요한 정보 | 후보 구조 |
| --- | --- |
| min cut 값 하나 | Stoer-Wagner |
| min cut partition 하나 | Stoer-Wagner + group tracking |
| 모든 pair min cut 값 | Gomory-Hu Tree |
| 모든 global min cut의 family | cactus representation |
| edge가 어떤 min cut에 속하는지 | cactus/cut sensitivity |

Cactus representation은 모든 global minimum cut을 cycle-like 구조로 압축하는 관점입니다. 구현 난도가 높으므로 대부분의 대회 문제는 직접 요구하지 않지만, "minimum cut이 여러 개"라는 해석에는 도움이 됩니다.

## 4. Edge Criticality

edge가 global min cut에 포함되는지, capacity를 올리면 min cut 값이 변하는지 묻는 문제는 "그 edge를 가로지르는 minimum cut이 존재하는가"로 바뀝니다.

```text
edge e = (u, v)
어떤 minimum cut partition에서 u와 v가 갈라지는가?
  yes -> e는 최소 절단 후보에 직접 관여
  no  -> e 하나를 바꿔도 현재 min cut 값은 그대로일 수 있음
```

모든 edge에 대해 이 판정을 빠르게 하려면 단일 Stoer-Wagner 값만으로는 부족합니다. pair cut 정보나 cactus 구조가 필요할 수 있습니다.

## 5. Gomory-Hu Tree로 보는 응용

무향 그래프에서 Gomory-Hu Tree는 모든 두 정점 `u, v`의 min cut 값을 tree path의 최소 edge weight로 표현합니다.

| 질의 | Tree 위 해석 |
| --- | --- |
| 전체 global min cut | tree edge weight 최솟값 |
| `u-v` min cut value | path minimum |
| 가장 약한 pair 그룹 | 작은 weight edge가 나누는 component |
| 여러 pair query | LCA/RMQ 또는 tree path min |

global min cut 하나만 필요하면 과합니다. 하지만 pair 질의가 많으면 Gomory-Hu Tree가 응용의 중심이 됩니다.

## 6. Cut Modeling 예시

문제에서 "서버를 두 그룹으로 나눌 때 끊기는 회선 비용의 최솟값"이라고 하면 global min cut입니다. 하지만 "A 데이터센터와 B 데이터센터를 분리"라고 하면 `s-t min cut`입니다.

| 표현 | 모델 |
| --- | --- |
| 아무 두 그룹으로 나누어도 됨 | global min cut |
| 특정 두 정점을 반드시 분리 | `s-t` min cut |
| 모든 pair의 취약도 | Gomory-Hu Tree |
| k 이하 취약 cut 존재 여부 | cut certificate + min cut |

source/sink가 숨어 있는지 먼저 찾아야 합니다.

## 7. 시간 복잡도 선택

| 접근 | 복잡도 감각 | 쓰는 경우 |
| --- | ---: | --- |
| Stoer-Wagner matrix | `O(N^3)` | `N` 중간, global 값/partition 하나 |
| 여러 max-flow | flow 비용 곱 | 특정 pair가 적거나 구현 단순성 우선 |
| Gomory-Hu Tree | `N-1`번 max-flow | 모든 pair min cut |
| certificate + min cut | 전처리 후 축소 | dense graph, 작은 cut threshold |

문제 제한에서 `N`, `M`, capacity 범위, pair query 수를 함께 봅니다.

## 8. 자주 하는 실수

1. partition이 필요한데 값만 반환하는 구현을 사용한다.
2. 모든 minimum cut을 단일 partition으로 대표할 수 있다고 생각한다.
3. 방향 그래프 min cut과 무향 global min cut 구조를 섞는다.
4. Gomory-Hu Tree의 path sum과 path minimum을 혼동한다.
5. edge capacity가 음수일 수 있는 모델을 cut 알고리즘에 그대로 넣는다.

## 9. 문제를 볼 때 체크할 조건

- 특정 source/sink가 있는가?
- 답이 cut value인지, partition인지, 모든 cut family인지 확인했는가?
- pair query가 많은가?
- 그래프가 무향이고 capacity가 nonnegative인가?
- dense graph에서 certificate로 줄일 여지가 있는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: global min cut partition `/practice/...` 문제 필요 | partition 복원 | Stoer-Wagner group tracking |
| 표준 | TODO: all pair cut query `/practice/...` 문제 필요 | pair min cut 질의 | Gomory-Hu Tree |
| 응용 | TODO: critical cut edge `/practice/...` 문제 필요 | edge sensitivity | min cut family |
| 함정 | TODO: source sink vs global `/practice/...` 문제 필요 | 모델 구분 | global vs s-t |
