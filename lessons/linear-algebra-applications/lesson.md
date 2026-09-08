# Linear Algebra Applications

Linear Algebra Applications는 rank, determinant, basis, recurrence, graph counting을 각각 따로 외우는 대신 "무엇을 vector space로 볼 수 있는가"를 기준으로 문제를 번역하는 decision map입니다.

## 선택 표

| 먼저 보이는 조건 | 우선 선택 | 대표 하위 주제 |
| --- | --- | --- |
| 값이 xor로 합쳐지고 carry가 없다 | GF(2) basis | XOR Linear Basis, Linear Basis Applications |
| 식 수와 변수 수가 작고 matrix가 dense하다 | Gaussian elimination | augmented rank, determinant |
| matrix가 크지만 matvec oracle이 빠르다 | black-box/sparse solver | Black-Box Linear Algebra, Sparse Linear Systems |
| 존재성이나 counting이 determinant로 압축된다 | modular determinant | Randomized Determinant, Matrix-Tree Theorem |
| graph 구조의 tree/counting을 묻는다 | Laplacian/cofactor | Matrix-Tree Theorem Applications |
| DP transition이 선형 반복이다 | matrix power 또는 minimal polynomial | Matrix Exponentiation, Polynomial and Recurrence Algorithms |

이 표는 "어떤 선형대수 레슨을 먼저 볼지"를 고르는 용도입니다. 실제 구현 레슨은 각 하위 문서에서 보고, 이 문서에서는 모델 번역과 선택 이유를 검증합니다.

## 작은 예시: Parity Constraints

아래 조건이 있다고 하겠습니다.

```text
x0 xor x1 = 1
x1 xor x2 = 0
x0 xor x2 = 1
```

GF(2)에서는 xor가 덧셈입니다. 각 식은 row가 되고, 오른쪽 값은 augmented column이 됩니다.

```text
1 1 0 | 1
0 1 1 | 0
1 0 1 | 1
```

rank를 구하면 일관성 여부와 자유 변수 수를 알 수 있습니다. 해 개수는 `2^(variables - rank)`입니다. 단, augmented rank가 더 크면 해가 없습니다.

## Rank로 세는 것

Rank는 독립인 정보의 수입니다.

| 상황 | rank 해석 |
| --- | --- |
| xor basis | 표현 가능한 xor 공간의 차원 |
| linear equations | 독립 제약식 수 |
| graph incidence over GF(2) | component/cycle space |
| vector matroid | 선택 가능한 독립 벡터 수 |

문제에서 "몇 가지가 독립인가", "몇 개를 자유롭게 정할 수 있는가", "표현 가능한 값이 몇 개인가"가 보이면 rank를 먼저 떠올립니다.

## Determinant로 세는 것

Determinant는 단순한 행렬 값이 아니라 여러 조합적 구조의 압축입니다.

| 정리/기법 | 쓰임 |
| --- | --- |
| Matrix-Tree Theorem | spanning tree 개수 |
| Tutte matrix | perfect matching 존재성 |
| determinant polynomial identity | randomized zero test |
| Vandermonde determinant | interpolation 조건 |

랜덤 값을 대입해 determinant가 0이 아닌지 보는 방식은 확률적입니다. 여러 prime이나 여러 random seed로 반복하고, 작은 입력에서는 brute force와 비교해야 합니다.

## Recurrence와 Matrix

DP transition이 선형이면 matrix power나 minimal polynomial로 바꿀 수 있습니다.

```text
state_{t+1} = A * state_t
answer_t = c^T * state_t
```

`t`가 매우 크면 `A^t`를 직접 거듭제곱합니다. `A`가 너무 크지만 matvec이 빠르면 Krylov sequence와 Berlekamp-Massey로 `answer_t`의 recurrence를 찾는 선택지도 있습니다.

64비트 이하 GF(2) rank는 [XOR Linear Basis](https://h.readiz.com/learn/linear-basis-xor)의 rank를 사용합니다. 더 큰 행렬은 bitset 또는 word-block 소거가 필요합니다.

## 연습 문제

[Decision Map Practice](pages/decision-map-practice.md)에서 parity 제약과 Matrix-Tree를 풀어 봅니다.
