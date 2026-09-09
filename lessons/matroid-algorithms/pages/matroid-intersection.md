# Matroid Intersection

Matroid Intersection은 두 개의 독립성 조건을 동시에 만족하는 가장 큰 집합을 찾는 reference 모델입니다. 그래프 matching처럼 augmenting path를 찾지만, "간선을 하나 더 넣어도 되는가" 대신 "현재 집합에서 무엇을 빼면 새 원소를 넣을 수 있는가"를 두 matroid 각각에 대해 묻습니다.

이 페이지는 Matroid Algorithms 허브 아래에서 General Matching, Weighted Matching, Linear Basis Applications 이후에 보는 그래프/조합 최적화 심화입니다.

1. 독립 집합을 하나씩 키우는 문제인지 본다.
2. 두 독립성 조건이 모두 matroid 교환 성질을 가지는지 확인한다.
3. exchange graph에서 augmenting path를 찾아 선택 집합을 뒤집는다.


예시의 색상 제한은 red 1개·blue 1개라 현재 크기 2가 이미 최대입니다. 나열한 교환 가능성이 곧 증가 경로의 존재를 뜻하지 않습니다. 임의 DFS 경로를 뒤집는 대신 최단 증가 경로 조건을 사용합니다.

## 문제 신호

| 문제 표현 | Matroid Intersection 관점 |
| --- | --- |
| 두 종류의 "동시에 가능" 조건이 있다 | 두 matroid의 공통 독립 집합 |
| 하나는 cycle 금지, 하나는 색상별 개수 제한 | graphic matroid + partition matroid |
| 벡터들이 독립이어야 하고 그룹별 제한도 있다 | linear matroid + partition matroid |
| 단순 greedy가 앞 선택 때문에 막힌다 | exchange path 필요 |
| 최대 크기뿐 아니라 가중치 확장이 보인다 | weighted matroid intersection 후보 |

Matroid는 독립 집합의 모든 부분집합도 독립이고, 작은 독립 집합은 큰 독립 집합의 어떤 원소를 받아 더 커질 수 있다는 교환 성질을 가집니다. 이 성질 덕분에 augmenting path 기반 알고리즘이 맞습니다.

## 핵심 모델

원소 전체 집합을 `E`, 현재 선택 집합을 `S`라고 하겠습니다. 목표는 `S`가 두 matroid `M1`, `M2`에서 모두 독립이 되도록 하면서 크기를 최대화하는 것입니다.

한 번의 증가 단계는 아래 질문으로 구성됩니다.

```text
어떤 원소 x not in S를 넣고 싶다.
M1에서 x를 넣으려면 어떤 y in S를 빼야 하는가?
M2에서 x를 넣으려면 어떤 y in S를 빼야 하는가?
```

이 질문들의 답을 방향 그래프로 만들면 exchange graph가 됩니다. 시작점은 `S + x`가 `M1`에서 바로 독립인 원소이고, 도착점은 `S + x`가 `M2`에서 바로 독립인 원소입니다. 시작점에서 도착점까지 BFS로 간선 수가 가장 적은 증가 경로를 찾으면, 그 경로의 원소 선택 여부를 뒤집어 `|S|`를 1 늘립니다.

## 작은 예시

간선 4개가 있고, forest 조건과 색상별 최대 1개 조건을 동시에 만족해야 한다고 하겠습니다.

```text
e1: 1-2, red
e2: 2-3, red
e3: 1-3, blue
e4: 3-4, blue
```

현재 `S = {e1, e3}`이라면 forest 조건은 이미 `1-2-3` path라서 독립이고, 색상도 red 1개, blue 1개라서 독립입니다. `e2`를 넣으면 색상 red가 2개라서 partition matroid가 깨집니다. 대신 `e1`을 빼면 색상 조건은 복구됩니다.

`e4`를 넣으면 색상 blue가 2개라서 `e3`을 빼야 합니다. 하지만 forest 쪽에서는 `e4`를 넣어도 cycle이 생기지 않습니다. 이런 교환 가능성을 양쪽에서 연결해 증가 경로를 탐색합니다. 이 예시는 색상별 capacity가 합계 2이므로 sink에 도달할 증가 경로가 없습니다.

## Exchange Graph

현재 선택되지 않은 원소를 `outside`, 선택된 원소를 `inside`라고 부릅니다.

| 간선 종류 | 의미 |
| --- | --- |
| source -> `x` | `S + x`가 `M1`에서 독립 |
| `x` -> sink | `S + x`가 `M2`에서 독립 |
| `y` -> `x` | `S - y + x`가 `M1`에서 독립 |
| `x` -> `y` | `S - y + x`가 `M2`에서 독립 |

방향이 다른 이유가 중요합니다. 하나의 path를 따라 선택 여부를 뒤집었을 때, `M1`과 `M2`의 조건이 번갈아 복구되도록 방향을 맞춥니다.

## 독립성 판정 구현

`canAdd(S, x)`는 `S + x`, `canExchange(S, y, x)`는 `S - y + x`가 독립인지 판정합니다. 이 판정을 항상 참으로 두면 제약을 검사하지 않으므로 교환 그래프를 올바르게 만들 수 없습니다.

그래프 matroid는 선택 간선으로 DSU를 구성해 cycle을 검사하고, partition matroid는 그룹별 개수를 제한과 비교합니다. Linear matroid는 선택 벡터의 basis를 다시 구성해 독립성을 판정합니다. 먼저 작은 입력에서 이 판정과 선택 집합을 검증하고, 시간이 많이 드는 판정부터 최적화합니다.

## 시간 복잡도

| 단계 | 시간 |
| --- | ---: |
| exchange graph 후보 쌍 | `O(|E| * |S|)` |
| 독립성 oracle 1회 | matroid 종류에 따라 다름 |
| augmenting path 1회 | 최단 증가 경로 BFS |
| 총 증가 횟수 | 최대 rank |

순진하게 매번 oracle을 rebuild하면 `O(r * |E| * r * oracle)`이 됩니다. 대회에서는 partition/graphic/linear처럼 oracle을 빠르게 만들 수 있는 구조가 있는지 먼저 봐야 합니다.
