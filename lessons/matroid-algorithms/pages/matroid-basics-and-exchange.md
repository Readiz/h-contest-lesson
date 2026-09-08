# Matroid Basics and Exchange

Matroid는 greedy가 맞는 독립성 구조를 추상화한 모델입니다. 독립 집합의 모든 부분집합도 독립이고, 작은 독립 집합은 큰 독립 집합의 어떤 원소를 받아 더 커질 수 있다는 exchange 성질이 핵심입니다.


최대 가중치 독립 집합은 음수 weight 원소를 건너뜁니다. 반드시 기저를 골라야 하는 문제는 최대 rank까지 채워야 하므로 음수도 필요할 수 있습니다. 단일 matroid의 가중치 문제 자체는 greedy 적용 대상입니다.

## 독립성 공리

원소 집합 `E`와 독립 집합들의 모음 `I`가 있을 때, matroid는 보통 아래 성질을 만족합니다.

```text
1. empty set is independent
2. A is independent and B subset A -> B is independent
3. |A| < |B| and A, B independent -> exists x in B-A such that A+x independent
```

세 번째 성질이 greedy와 exchange algorithm의 근거입니다. 단순히 "제약이 있다"는 이유만으로 matroid가 되는 것은 아닙니다.

## 대표 예시

| Matroid | 독립 집합 | 구현 신호 |
| --- | --- | --- |
| Partition matroid | class별 capacity를 넘지 않는 집합 | count array |
| Graphic matroid | cycle이 없는 edge set | DSU, forest |
| Linear matroid | 선형 독립인 vector set | Gaussian elimination, XOR basis |
| Uniform matroid | 크기가 `k` 이하인 집합 | cardinality |

대회 문제에서 matroid라는 이름이 직접 나오지 않아도, 위 구조가 보이면 greedy 증명이나 exchange graph를 의심할 수 있습니다.

## Greedy가 맞는 경우

하나의 matroid에서 가중치 합이 최대인 독립 집합을 찾는 문제는 weight 내림차순 greedy가 맞습니다.

```text
sort elements by weight desc
for e in sorted order:
    if weight(e) >= 0 and S + e is independent:
        add e
```

이때 필요한 것은 `S + e` 독립성 판정입니다. Partition matroid라면 count, graphic matroid라면 DSU, linear matroid라면 basis insertion입니다.

## Greedy가 부족한 경우

아래 상황에서는 단일 matroid greedy가 아니라 별도 알고리즘이 필요할 수 있습니다.

- 두 matroid 조건을 동시에 만족해야 한다.
- pair 단위로만 선택할 수 있다.
- 여러 independent set으로 전체를 나눠야 한다.
- 이미 고른 원소를 빼고 다른 원소를 넣는 연쇄 교환이 필요하다.

이때부터 Matroid Intersection, Parity, Union 같은 reference 페이지로 내려갑니다.

## 교환 공리가 깨지는 반례

양수 크기 3,2,2인 원소 a,b,c에서 총 크기<=4인 집합을 독립이라고 둡니다. 부분집합 폐쇄성은 성립하지만 A={a}, B={b,c}에서 |A|<|B|이고 B의 어느 원소도 A에 추가할 수 없습니다. 따라서 matroid가 아닙니다. “정확히 2개” 조건은 애초에 빈 집합·부분집합 폐쇄성을 만족하지 않습니다.
