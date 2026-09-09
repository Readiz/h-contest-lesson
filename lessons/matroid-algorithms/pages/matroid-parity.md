# Matroid Parity

Matroid Parity는 원소가 짝으로 묶여 있을 때, 선택한 짝들의 원소 전체가 어떤 matroid에서 독립이 되도록 최대한 많은 짝을 고르는 reference 모델입니다. Matching을 더 일반적인 독립성 구조 위로 올린 문제로 볼 수 있습니다.

이 페이지는 Matroid Algorithms 허브 아래에서 General Matching, Linear Basis Applications 이후에 보는 그래프/조합 최적화 심화입니다.

1. 선택 단위가 원소 하나인지, pair 하나인지 구분한다.
2. 선택한 pair들의 원소 전체가 어떤 독립성 조건을 만족해야 하는지 이름 붙인다.
3. 일반 matroid oracle 문제가 아니라, contest에서 다룰 수 있는 특수 구조인지 확인한다.


pair 내부 두 vector의 순서는 독립성 결과에 영향을 주지 않습니다. 둘 다 검사해야 한다는 점이 중요합니다. matching 환원에서는 간선별 endpoint occurrence를 서로 다른 원소로 두고, 같은 정점 occurrence를 capacity 1인 partition class에 넣습니다.

## 문제 신호

| 문제 표현 | Matroid Parity 관점 |
| --- | --- |
| 물건이 항상 두 개씩 묶여 선택된다 | pair가 선택 단위 |
| 고른 원소 전체가 독립이어야 한다 | underlying matroid 독립성 |
| matching보다 조건이 추상적이다 | graph matching의 일반화 후보 |
| vector pair를 골라 rank를 유지한다 | linear matroid parity |
| 단순 matroid intersection으로 자연스럽게 떨어지지 않는다 | pair 단위 parity 제약 |

Matroid Intersection은 원소를 하나씩 넣고 빼며 두 독립성 조건을 맞춥니다. Matroid Parity는 pair를 통째로 선택해야 하므로, 한 번의 선택이 독립성 구조에 두 원소를 추가합니다.

## 핵심 모델

전체 원소 집합 `E`가 pair들로 나뉘어 있다고 하겠습니다.

```text
P1 = {a1, b1}
P2 = {a2, b2}
...
Pk = {ak, bk}
```

선택한 pair 집합을 `T`라고 하면 실제로 matroid에 들어가는 원소 집합은 아래와 같습니다.

```text
U(T) = union of all elements in selected pairs
```

목표는 `U(T)`가 matroid `M`에서 독립이 되도록 하면서 `|T|`를 최대화하는 것입니다. 핵심은 "pair를 하나 더 선택해도 독립인가"뿐 아니라, 막혔을 때 어떤 pair를 교환해야 하는지도 구조에 따라 달라진다는 점입니다.

## Matroid Intersection과 다른 점

| 구분 | Matroid Intersection | Matroid Parity |
| --- | --- | --- |
| 선택 단위 | 원소 1개 | pair 1개 |
| 조건 | 두 matroid에 모두 독립 | 한 matroid에서 pair union이 독립 |
| 증가 경로 | exchange graph | 특수 구조별 augmenting 구조 |
| contest 구현 | graphic/partition/linear 조합에서 가능 | 보통 linear matroid parity 같은 제한형 |

일반 oracle matroid parity를 그대로 구현하려고 하면 대회 문제 범위를 벗어나기 쉽습니다. 문제에서 vector, rank, determinant, matching 존재성 같은 구체 구조가 같이 나오는지 먼저 확인해야 합니다.

## 작은 예시

GF(2) vector 네 쌍이 있다고 하겠습니다.

```text
P1 = (1000, 0100)
P2 = (0010, 0001)
P3 = (1100, 0011)
P4 = (1010, 0101)
```

underlying matroid를 "선택된 vector들이 선형 독립"인 linear matroid로 두면, pair 하나를 고를 때마다 vector 두 개가 basis에 들어갑니다.

`P1`, `P2`를 고르면 네 vector가 표준기저라 rank 4입니다. 여기에 어떤 pair를 더 넣으면 차원이 4인 공간에서 vector 6개가 되므로 독립일 수 없습니다. 이 경우 최대 선택 pair 수는 2입니다.

이 예시는 단순하지만, pair 단위 선택 때문에 "vector 하나만 빼고 다른 vector 하나를 넣는" 교환으로는 상태를 설명하기 어렵다는 점을 보여 줍니다.

## Linear Matroid에서의 판정 골격

작은 입력이나 검증용 baseline은 선택한 pair들의 vector를 모두 모아 rank를 계산하면 됩니다.

[XOR Linear Basis](https://h.readiz.com/learn/linear-basis-xor)의 basis를 새로 만들고 선택한 각 pair의 두 vector를 차례로 insert합니다. 어느 하나라도 종속이면 해당 선택 집합은 불가능합니다. 이것은 GF(2)의 독립성 oracle이며 최대 pair 선택 알고리즘 자체는 아닙니다.

이 판정은 GF(2) linear matroid에만 맞습니다. 일반 field vector라면 Gaussian elimination, sparse vector라면 basis representation을 따로 잡아야 합니다.

## 모델링 체크

| 질문 | 이유 |
| --- | --- |
| pair를 반드시 둘 다 선택해야 하는가? | 둘 중 하나만 고르면 matching/assignment일 수 있음 |
| 독립성 조건이 matroid인가? | 부분집합 폐쇄성과 교환 성질이 필요 |
| linear matroid처럼 구현 가능한 구조인가? | 일반 oracle는 너무 어렵기 쉬움 |
| 최대 cardinality인가, weight가 있는가? | weighted variant는 더 어렵다 |
| randomization이 허용되는가? | determinant 기반 판정으로 넘어갈 수 있음 |

특히 "pair 중 하나를 선택"하는 문제와 "pair 둘 다를 선택"하는 문제를 혼동하면 모델이 완전히 달라집니다.

## Matching과의 연결

일반 graph matching도 parity 관점으로 해석할 수 있습니다. 간선을 선택하면 양 끝점 두 개가 동시에 사용되고, 각 vertex는 한 번만 사용되어야 합니다.

다만 실제 matching 문제는 blossom, Tutte matrix, augmenting path 같은 더 직접적인 도구가 있습니다. Matroid Parity는 matching 자체를 다시 풀기 위한 도구라기보다, matching과 비슷한 pair 선택이 더 추상적인 독립성 조건과 결합될 때 떠올리는 모델입니다.

## 시간 복잡도 감각

| 접근 | 시간 |
| --- | ---: |
| 모든 pair subset brute force | `O(2^P * rankCost)` |
| greedy only | 빠르지만 일반적으로 틀림 |
| linear matroid parity 알고리즘 | 이론적으로 다항 시간, 구현 난도 높음 |
| 문제 특화 reduction | 문제 구조에 따라 다름 |

실전에서는 "이 문제가 정말 matroid parity 완성 알고리즘을 요구하는가"를 의심해야 합니다. 많은 경우 작은 rank, 특수 그래프, determinant 판정, 또는 matching reduction이 같이 주어집니다.
