# Sparse Linear Systems

Sparse Linear Systems는 대부분의 계수가 0인 큰 연립방정식 `A x = b`를 푸는 관점입니다. 모든 원소를 dense matrix로 펼치면 `O(N^3)` Gaussian elimination이 필요하지만, nonzero 구조와 matvec oracle을 이용하면 훨씬 큰 상태를 다룰 수 있습니다.


연결된 무향 양의 가중치 실수 Laplacian은 rank N-1입니다. 비연결이면 성분 수만큼 영공간이 생기고, 유한체로 줄이면 추가 rank 감소가 가능하므로 실수 성질을 그대로 적용하지 않습니다.

## 문제 신호

| 문제 표현 | Sparse Linear System 관점 |
| --- | --- |
| 변수 수가 크지만 식 하나당 항이 적다 | sparse row elimination |
| 그래프의 vertex/edge 관계식이 나온다 | incidence/Laplacian 계열 |
| modulo prime에서 해 개수나 일관성을 묻는다 | rank 비교 |
| 전이 행렬 전체가 너무 크다 | matvec oracle |
| 실수 오차 허용 근사 최적화가 나온다 | iterative method 후보 |

대회에서는 대부분 modulo prime 위의 정확한 계산이 안전합니다. 실수 iterative method는 오차와 수렴 조건이 어려워서, 문제에서 명시적으로 허용하지 않으면 마지막 선택지로 둡니다.

## Dense와 Sparse의 차이

Dense Gaussian elimination은 pivot column마다 모든 row를 훑습니다. Sparse matrix에서는 row마다 실제 nonzero entry만 저장합니다.

```text
row 0: (0, 2), (3, 5)
row 1: (1, 7)
row 2: (0, 1), (2, 4), (3, 9)
```

이 표현은 matvec에 강합니다. 하지만 elimination을 하면 fill-in이 생겨 0이던 곳이 갑자기 nonzero가 될 수 있습니다. 그래서 sparse system은 "저장만 sparse"인지, "연산 중에도 sparse가 유지되는 구조"인지가 핵심입니다.

## 작은 예시

아래 식을 modulo 11에서 푼다고 하겠습니다.

```text
x0 + 2*x3 = 5
3*x1       = 6
4*x0 + x2 = 8
```

각 row의 항은 1개 또는 2개뿐입니다. `x1 = 2`는 바로 정해지고, `x0`, `x2`, `x3`은 자유도에 따라 여러 해가 가능합니다.

일관성만 묻는다면 rank 비교를 합니다.

```text
rank(A) == rank([A|b])이면 해가 있다.
일관성이 있고 rank(A) < number_of_variables이면 해가 여러 개다.
```

해 하나가 필요하면 자유 변수를 0으로 두고 back substitution합니다.

## Sparse Row Elimination

Sparse row를 map이나 sorted vector로 저장하면 pivot 제거 때 nonzero만 갱신할 수 있습니다.

희소 matvec는 [Black-Box Linear Algebra](https://h.readiz.com/learn/black-box-linear-algebra)의 구현을 재사용합니다. sparse elimination은 pivot row와 현재 row의 같은 열 계수를 더하고 빼며 0 항을 제거해야 하고, fill-in 때문에 희소성이 유지되지 않을 수 있습니다.

이 코드는 matvec용입니다. Elimination까지 하려면 pivot row를 더하고 빼면서 같은 column을 합쳐야 하므로 자료구조 선택이 중요합니다. column 수가 작으면 dense vector가 오히려 빠를 수 있습니다.

## Black-Box Solver 관점

행렬 전체를 직접 조작하지 않고 `multiply(A, x)`만 빠르게 할 수 있다면 Wiedemann 계열을 생각할 수 있습니다.

```text
A x = b
random projection으로 scalar Krylov sequence 생성
minimal polynomial 또는 recurrence를 찾음
해 후보를 만들고 A*x == b로 검증
```

이 방식은 구현 난도가 높습니다. 따라서 contest에서는 아래 순서로 판단합니다.

1. `N <= 500` 정도면 dense elimination이 단순하고 안전하다.
2. row당 항이 적고 pivot fill-in이 작으면 sparse elimination을 고려한다.
3. `N`이 매우 크고 matvec만 가능한 구조면 black-box linear algebra를 검토한다.

## 그래프에서 자주 나오는 형태

| 그래프 모델 | 선형 시스템 |
| --- | --- |
| flow conservation | incidence matrix |
| 전기 회로/저항 | Laplacian equation |
| Markov chain expected time | `(I - P)x = c` |
| xor constraint | GF(2) linear system |
| path parity | incidence over GF(2) |

특히 Laplacian은 각 row의 degree만큼만 nonzero가 있습니다. 하지만 Laplacian은 rank가 하나 부족한 경우가 많으므로 기준 vertex를 고정하거나 합 조건을 추가해야 합니다.

## 시간 복잡도

| 방법 | 시간 감각 | 적합한 경우 |
| --- | ---: | --- |
| dense Gaussian elimination | `O(N^3)` | `N`이 작고 구현 안전성이 중요 |
| sparse matvec | `O(nnz)` | iterative/black-box의 기본 연산 |
| sparse elimination | fill-in에 따라 달라짐 | 구조적으로 sparse가 유지됨 |
| Wiedemann 계열 | 대략 여러 번의 matvec + BM | 큰 sparse matrix, randomized 허용 |

`nnz`는 nonzero entry 수입니다. `nnz`가 `N^2`에 가까우면 sparse로 저장해도 의미가 거의 없습니다.
