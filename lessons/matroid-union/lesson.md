# Matroid Union

Matroid Union은 여러 개의 matroid 독립 집합을 합쳐 얼마나 많은 원소를 덮을 수 있는지, 또는 한 ground set을 몇 개의 독립 집합으로 나눌 수 있는지를 다루는 조합 최적화 모델입니다. Matroid Intersection과 Parity가 "동시에 만족"과 "pair 단위 선택"을 본다면, Union은 "여러 독립 집합의 합"을 봅니다.

이 레슨은 Matroid Intersection, Matroid Parity, Proof and Invariants 이후에 보는 그래프/조합 최적화 심화입니다.

1. 같은 ground set 위에 독립 집합을 여러 layer로 둔다.
2. 각 원소를 어떤 layer에 배치할 수 있는지 확인한다.
3. union rank와 covering 조건을 matroid 성질로 해석한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Matroid Intersection, Matroid Parity, Proof and Invariants
- 함께 보면 좋은 레슨: General Matching, Linear Algebra Applications, Randomized Determinant
- 다음에 볼 레슨: matroid covering, arboricity, algebraic matching

## 1. 문제 신호

| 문제 표현 | Matroid Union 관점 |
| --- | --- |
| 원소를 여러 그룹에 나눠 각 그룹이 독립이어야 한다 | independent set union |
| 그래프 간선을 `k`개의 forest로 분해한다 | graphic matroid union |
| 색깔별 capacity가 있는 선택을 여러 번 할 수 있다 | partition matroid union |
| 전체 집합을 몇 개의 독립 집합으로 덮는지 묻는다 | matroid covering |
| rank formula나 exchange argument가 등장한다 | matroid union theorem 후보 |

대회에서는 일반 matroid oracle보다 graphic, partition, linear matroid처럼 구현 가능한 특수 형태로 나타나는 경우가 많습니다.

## 2. 핵심 모델

matroid `M1, M2, ..., Mk`가 같은 원소 집합 `E` 위에 있다고 하겠습니다. 선택한 집합 `S`가 union matroid에서 독립이라는 뜻은 아래처럼 분해할 수 있다는 뜻입니다.

```text
S = S1 union S2 union ... union Sk
Si is independent in Mi
```

모든 `Mi`가 같은 matroid라면 "원소를 k개의 독립 집합으로 칠할 수 있는가"가 됩니다.

## 3. Graphic Matroid 예시

그래프에서 forest는 graphic matroid의 독립 집합입니다. 간선 집합을 `k`개의 forest로 나눌 수 있다면 그 그래프의 arboricity가 `k` 이하라는 뜻입니다.

```text
간선 색 1: forest
간선 색 2: forest
...
간선 색 k: forest
```

cycle이 생긴 간선을 같은 색에 넣을 수 없으므로, 각 색마다 DSU를 하나씩 두는 greedy 검증을 떠올릴 수 있습니다. 하지만 임의 순서 greedy는 일반적으로 틀릴 수 있고, 막힌 간선을 넣기 위해 다른 색의 간선을 교환해야 할 수 있습니다.

## 4. Partition Matroid의 쉬운 경우

원소마다 class가 있고, 한 독립 집합은 class별로 capacity만큼만 고를 수 있다고 합시다. 같은 matroid를 `k`번 union하면 class별 capacity가 `k`배가 됩니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

int partitionMatroidUnionRank(
    const vector<int>& itemClass,
    const vector<int>& capacityPerClass,
    int copies
) {
    vector<int> count(capacityPerClass.size(), 0);
    for (int cls : itemClass) {
        ++count[cls];
    }

    int rank = 0;
    for (int cls = 0; cls < (int)capacityPerClass.size(); ++cls) {
        rank += min(count[cls], copies * capacityPerClass[cls]);
    }
    return rank;
}
```

이 코드는 partition matroid처럼 독립성 조건이 완전히 분리될 때만 맞습니다. Graphic matroid나 linear matroid에서는 교환 구조가 필요합니다.

## 5. Union Rank 직관

Matroid Union Theorem은 union rank를 아래 형태의 min formula로 설명합니다.

```text
r_union(X) = min over A subset X of |X - A| + r1(A) + r2(A) + ... + rk(A)
```

직관적으로 `A` 안의 원소들은 각 matroid rank로 감당해야 하고, `X - A`는 그냥 버리거나 직접 세는 부분입니다. 이 식을 그대로 구현하는 경우는 드물지만, 왜 단순 greedy가 부족한지 보여 줍니다.

## 6. Exchange가 필요한 이유

새 원소 `e`가 어떤 layer에도 바로 들어가지 않는다고 해서 실패는 아닙니다. 한 layer에서 cycle이나 rank conflict가 생기면, 그 layer의 기존 원소 하나를 다른 layer로 보내고 `e`를 넣는 연쇄 교환이 가능할 수 있습니다.

```text
e enters layer 1
old edge a moves from layer 1 to layer 2
old edge b moves from layer 2 to layer 3
...
```

이 관점은 Matroid Intersection의 exchange graph와 닮았지만, "layer 사이 이동"이 중심이라는 점이 다릅니다.

## 7. 문제별 구현 선택

| 구조 | 가능한 접근 |
| --- | --- |
| partition matroid | class별 count/capacity |
| graphic matroid 작은 입력 | 색별 DSU + backtracking/augmenting |
| linear matroid 작은 rank | basis rollback과 augmenting search |
| arboricity 판정 | Nash-Williams 조건, flow/modeling 후보 |
| 일반 oracle matroid | 대회 구현 범위를 넘기 쉬움 |

문제가 일반 matroid union을 요구하는 것처럼 보여도, 실제로는 그래프 density 조건이나 partition capacity로 단순화되는 경우가 많습니다.

## 8. 자주 하는 실수

1. 각 layer에 greedy로 넣다 막히면 불가능하다고 판단한다.
2. union을 intersection처럼 "모든 matroid에서 독립"이라고 해석한다.
3. 같은 원소를 여러 layer에 중복 배치해 버린다.
4. graphic matroid union에서 cycle 교환을 고려하지 않는다.
5. rank formula를 알고도 실제 입력 구조에 맞는 더 쉬운 풀이를 찾지 않는다.

## 9. 문제를 볼 때 체크할 조건

- 원소가 여러 독립 집합 중 정확히 하나에 들어가는가?
- 각 layer의 matroid가 같은가, 서로 다른가?
- 독립성 oracle을 효율적으로 구현할 수 있는가?
- greedy가 실패하는 교환 반례가 있는가?
- rank만 필요한가, 실제 분해까지 출력해야 하는가?
- 그래프 문제라면 forest decomposition이나 arboricity로 바뀌는가?

## 10. 대표 문제로 연결하기

### 문제에서 보이는 신호

- 입력 크기: layer 수가 작거나 독립성 구조가 partition/graphic으로 명확함
- 필요한 복잡도: 단순 subset DP보다 빠른 exchange 또는 rank 계산
- 이 레슨의 핵심 개념: 여러 독립 집합의 합과 layer 교환

### 풀이 흐름

1. 독립 집합 하나가 무엇인지 먼저 정의한다.
2. 원소를 몇 개의 독립 집합으로 나누는 문제인지 확인한다.
3. 쉬운 partition case인지, exchange가 필요한 case인지 나눈다.
4. 작은 반례로 naive greedy를 검증한다.
5. rank만 묻는지 실제 coloring/decomposition을 요구하는지 확인한다.

### 자주 틀리는 지점

- "두 조건을 동시에 만족"은 union이 아니라 intersection일 수 있습니다.
- "pair를 통째로 선택"은 union보다 matroid parity 쪽 신호입니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: partition matroid union `/practice/...` 문제 필요 | class capacity가 여러 copy로 늘어나는 경우 | capacity |
| 표준 | TODO: forest decomposition `/practice/...` 문제 필요 | 간선을 여러 forest로 색칠 | graphic matroid |
| 응용 | TODO: matroid union augmenting `/practice/...` 문제 필요 | layer 사이 교환 경로 구성 | exchange |
| 함정 | TODO: greedy failure `/practice/...` 문제 필요 | 바로 넣기 greedy 반례 확인 | augmenting path |
