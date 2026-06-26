# Matroid Basics and Exchange

Matroid는 greedy가 맞는 독립성 구조를 추상화한 모델입니다. 모든 부분집합이 독립이고, 작은 독립 집합은 큰 독립 집합의 어떤 원소를 받아 더 커질 수 있다는 exchange 성질이 핵심입니다.

## 1. 독립성 공리

원소 집합 `E`와 독립 집합들의 모음 `I`가 있을 때, matroid는 보통 아래 성질을 만족합니다.

```text
1. empty set is independent
2. A is independent and B subset A -> B is independent
3. |A| < |B| and A, B independent -> exists x in B-A such that A+x independent
```

세 번째 성질이 greedy와 exchange algorithm의 근거입니다. 단순히 "제약이 있다"는 이유만으로 matroid가 되는 것은 아닙니다.

## 2. 대표 예시

| Matroid | 독립 집합 | 구현 신호 |
| --- | --- | --- |
| Partition matroid | class별 capacity를 넘지 않는 집합 | count array |
| Graphic matroid | cycle이 없는 edge set | DSU, forest |
| Linear matroid | 선형 독립인 vector set | Gaussian elimination, XOR basis |
| Uniform matroid | 크기가 `k` 이하인 집합 | cardinality |

대회 문제에서 matroid라는 이름이 직접 나오지 않아도, 위 구조가 보이면 greedy 증명이나 exchange graph를 의심할 수 있습니다.

## 3. Greedy가 맞는 경우

하나의 matroid에서 가중치 합이 최대인 독립 집합을 찾는 문제는 weight 내림차순 greedy가 맞습니다.

```text
sort elements by weight desc
for e in sorted order:
    if S + e is independent:
        add e
```

이때 필요한 것은 `S + e` 독립성 판정입니다. Partition matroid라면 count, graphic matroid라면 DSU, linear matroid라면 basis insertion입니다.

## 4. Greedy가 부족한 경우

아래 상황에서는 단일 matroid greedy가 아니라 별도 알고리즘이 필요할 수 있습니다.

- 두 matroid 조건을 동시에 만족해야 한다.
- pair 단위로만 선택할 수 있다.
- 여러 independent set으로 전체를 나눠야 한다.
- 이미 고른 원소를 빼고 다른 원소를 넣는 연쇄 교환이 필요하다.
- weight가 있고 단순 cardinality augmenting이 아니다.

이때부터 Matroid Intersection, Parity, Union 같은 reference 페이지로 내려갑니다.

## 5. 작은 반례 관점

Matroid가 아닌 제약에서는 "무거운 것부터 넣기"가 쉽게 깨집니다. 예를 들어 정확히 두 원소를 골라야 하고 두 원소의 합이 특정 값 이하이어야 하는 제약은 부분집합 폐쇄성은 있어도 exchange 성질이 깨질 수 있습니다. 큰 독립 집합의 어떤 원소를 작은 집합에 넣어도 constraint가 복구되지 않는 경우가 생기기 때문입니다.

문제를 matroid로 부르기 전에 작은 독립 집합 두 개를 만들어 exchange 성질을 손으로 확인하는 습관이 필요합니다.
