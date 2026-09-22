# Matroid Intersection

Matroid Intersection은 두 개의 독립성 조건을 동시에 만족하는 가장 큰 집합을 찾는 reference 모델입니다. 그래프 matching처럼 augmenting path를 찾지만, "간선을 하나 더 넣어도 되는가" 대신 "현재 집합에서 무엇을 빼면 새 원소를 넣을 수 있는가"를 두 matroid 각각에 대해 묻습니다.

이 페이지는 Matroid Algorithms 허브 아래에서 General Matching, Weighted Matching, Linear Basis Applications 이후에 보는 그래프/조합 최적화 심화입니다.

1. 독립 집합을 하나씩 키우는 문제인지 본다.
2. 두 독립성 조건이 모두 matroid 교환 성질을 가지는지 확인한다.
3. exchange graph에서 augmenting path를 찾아 선택 집합을 뒤집는다.

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

## 교환해야 한 개 더 고를 수 있는 예

`M1`은 forest 조건, `M2`는 **red 최대 1개·blue 최대 2개** 조건입니다.

```text
e1: 1-2, red       현재 선택
e2: 2-3, blue      현재 선택
e3: 3-4, red       미선택
e4: 1-3, blue      미선택
```

현재 `S = {e1, e2}`에 `e3`만 넣으면 red가 2개가 됩니다. `e4`만 넣으면 `1-2-3-1` cycle이 생깁니다. 하나씩 바로 추가하는 greedy는 여기서 멈춥니다.

하지만 `e1`을 빼고 `e3`, `e4`를 함께 넣으면 `S' = {e2, e3, e4}`가 됩니다. 간선은 `2-3`, `3-4`, `1-3`으로 tree이고, red 1개·blue 2개이므로 두 조건을 만족하면서 크기가 2에서 3으로 늘어납니다.

## Exchange Graph

현재 선택되지 않은 원소를 `outside`, 선택된 원소를 `inside`라고 부릅니다.

| 간선 종류 | 의미 |
| --- | --- |
| source -> `x` | `S + x`가 `M1`에서 독립 |
| `x` -> sink | `S + x`가 `M2`에서 독립 |
| `y` -> `x` | `S - y + x`가 `M1`에서 독립 |
| `x` -> `y` | `S - y + x`가 `M2`에서 독립 |

방향이 다른 이유가 중요합니다. 하나의 path를 따라 선택 여부를 뒤집었을 때, `M1`과 `M2`의 조건이 번갈아 복구되도록 방향을 맞춥니다.

위 예시의 최단 증가 경로는 다음과 같습니다.

```text
source -> e3 -> e1 -> e4 -> sink
          +     -     +
```

| 간선 | 성립하는 이유 |
| --- | --- |
| source → e3 | `S+e3`은 정점 4를 잇는 forest |
| e3 → e1 | `S-e1+e3`은 red 1개·blue 1개 |
| e1 → e4 | `S-e1+e4`는 간선 `2-3`, `1-3`의 forest |
| e4 → sink | `S+e4`는 red 1개·blue 2개 |

경로의 선택 여부를 **한 번에** 뒤집습니다. 경로 중간의 집합이 항상 두 조건을 모두 만족하는 것은 아닙니다. 올바른 증분을 보장하려면 임의 DFS 경로 대신 BFS로 찾은 최단 증가 경로를 사용합니다.

이 조건의 증명은 [MIT Matroid Intersection 강의 노트의 exchange graph 절](https://math.mit.edu/~goemans/18453S17/matroid-intersect-notes.pdf)에 나옵니다. 위 예시는 forest·색상 제한을 직접 검사해 교환을 따라가도록 구성했습니다.

종료 조건도 구분합니다. 같은 초기 집합에서 blue 제한까지 1개로 낮추면 전체 색상 capacity가 2이므로 더 늘릴 수 없습니다. 교환 간선 몇 개가 존재한다는 사실만으로 증가 경로가 있다는 뜻은 아닙니다.

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
