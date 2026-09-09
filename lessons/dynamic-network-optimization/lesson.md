# Dynamic Network Optimization

Dynamic Network Optimization은 간선 활성 시간, 용량 변화, MST 갱신, cut 재사용처럼 "그래프가 시간에 따라 바뀌는 최적화 문제"를 한곳에서 분류하는 허브입니다. Dynamic Flow와 Dynamic MST는 독립 구현 레슨처럼 보이면 과하게 어렵게 읽히기 쉽고, 실제 대회에서는 offline time-axis, rebuild, residual reuse, cut/cycle property를 먼저 고르는 편이 안전합니다.

이 허브의 목표는 완전한 online dynamic 알고리즘을 외우는 것이 아니라, 문제 조건을 보고 어떤 제한된 모델로 낮출 수 있는지 판단하는 것입니다.

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 용량 증가, 시간별 이동, residual graph 재사용이 보인다 | [Dynamic Flow](pages/dynamic-flow.md) |
| 간선 추가/삭제 뒤 MST cost를 묻는다 | [Dynamic MST](pages/dynamic-mst.md) |
| 모든 update를 미리 읽을 수 있다 | Offline and Time-Axis Techniques |
| 필요한 값이 min cut family나 all-pairs cut이다 | Graph Cut Structures |
| forest connectivity와 path aggregate가 핵심이다 | Link-Cut Tree 또는 Euler Tour Tree |

같은 "dynamic graph"라도 답이 connectivity인지, MST cost인지, max flow value인지, cut certificate인지에 따라 필요한 상태가 완전히 달라집니다. connectivity만 필요하면 rollback DSU로 끝날 수 있지만, flow와 MST는 최적화 값이 붙어서 상태 복원이 더 어렵습니다.

## 먼저 낮출 수 있는가

| 낮추는 방향 | 쓸 수 있는 조건 | 피해야 할 경우 |
| --- | --- | --- |
| rebuild baseline | 입력이 작거나 변경 수가 작음 | query마다 전체 재계산이 시간 초과 |
| block rebuild | block 안에서 바뀐 edge만 작음 | 모든 edge가 매 block 크게 흔들림 |
| segment tree over time | update가 active interval로 바뀜 | leaf 답에 강한 최적화 상태가 필요 |
| residual reuse | capacity 증가처럼 old flow가 feasible | capacity decrease, source/sink 변경 |
| time-expanded network | 시간 단계가 작고 이동 규칙이 명확 | 시간 축이 너무 길거나 online query |

완전 동적 자료구조는 마지막 선택입니다. 먼저 offline으로 바꿀 수 있는지, block으로 묶을 수 있는지, 정적 그래프를 반복해서 푸는 baseline이 제한 안에 들어오는지 확인합니다.

## 관계 정리

Dynamic Flow는 flow 구현 레슨이라기보다 모델링 reference에 가깝습니다. capacity 증가만 있으면 residual graph를 이어 쓰고, 시간 단계가 명시되면 time-expanded network로 바꿉니다. 삭제나 용량 감소가 섞이면 feasibility repair가 필요하므로 rebuild 기준을 먼저 잡습니다.

Dynamic MST는 cut/cycle property를 쓰지만 Graph Cut Structures의 prerequisite은 아닙니다. 두 주제는 서로 보완 관계입니다. MST 갱신은 tree edge replacement와 offline reduction이 중심이고, graph cut 허브는 s-t/global/all-pairs/family cut을 고르는 흐름입니다.

Offline and Time-Axis Techniques는 이 허브의 공통 바닥입니다. update 구간을 만들 수 있으면 rollback, segment tree over time, divide and conquer over time이 먼저 후보가 됩니다. 다만 flow나 MST는 leaf에서 단순 DSU 상태만으로 답하지 못할 수 있으므로 추가 최적화 구조가 필요합니다.

## 연습

[Dynamic Network Optimization Practice Set](https://h.readiz.com/learn/dynamic-network-optimization/dynamic-flow)에서 용량 증가만 있는 max-flow를 residual reuse와 매번 재계산으로 비교합니다. Block MST는 block 안에서 변하는 간선을 모두 제외한 고정 간선의 MSF를 만들고, 그 MSF와 현재 변경 간선을 합쳐 재계산합니다. 후보가 O(N+B)이므로 N이 크면 추가 축소 없이는 빠르지 않습니다.
