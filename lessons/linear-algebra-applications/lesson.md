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


아래 조건을 봅니다.

```text
x0 xor x1 = 1
x1 xor x2 = 0
x0 xor x2 = 1
```

GF(2)에서 xor는 덧셈이므로 augmented matrix는 아래와 같습니다.

```text
1 1 0 | 1
0 1 1 | 0
1 0 1 | 1
```

row 0을 pivot으로 잡고 row 2를 xor하면 이렇게 됩니다.

```text
1 1 0 | 1
0 1 1 | 0
0 1 1 | 0
```

row 1과 row 2는 같은 제약입니다. rank는 2, 변수는 3개이므로 해 개수는 `2^(3 - 2) = 2`입니다.

같은 왼쪽 식에서 마지막 RHS만 0으로 바꾸면 반례가 됩니다.

```text
x0 xor x1 = 1
x1 xor x2 = 0
x0 xor x2 = 0
```

row 2를 pivot row와 xor하면 `0 1 1 | 1`이 되고, row 1과 다시 xor하면 `0 0 0 | 1`이 나옵니다. 이 행은 모순이므로 해가 없습니다.

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

## 로컬 연습 A: XOR Constraint Counter

### 입력

`N`개의 0/1 변수와 `M`개의 제약이 있습니다. 각 제약은 `u v b`로 주어지고, 의미는 `x_u xor x_v = b`입니다.

```text
N M
u1 v1 b1
...
uM vM bM
```

### 출력

제약이 모순이면 `0`을 출력합니다. 모순이 아니면 가능한 assignment 수를 `998244353`으로 나눈 값을 출력합니다.

### 제한

- `1 <= N <= 2000`
- `0 <= M <= 4000`
- `0 <= u, v < N`
- `b`는 0 또는 1

### 예시

```text
4 3
0 1 1
1 2 0
0 2 1
```

위 세 제약의 rank는 2입니다. `x3`은 어떤 제약에도 등장하지 않으므로 자유 변수이고, `x0, x1, x2` 묶음에서도 하나가 자유 변수입니다. 답은 `2^(4 - 2) = 4`입니다.

```text
4
```

### 풀이 기준

1. 각 제약을 GF(2) augmented row로 만든다. `u=v`이면 같은 변수 bit를 두 번 XOR해 상쇄한다. OR로 한 번 켜면 `x_u xor x_u=0`을 잘못 표현한다.
2. Gaussian elimination으로 pivot을 잡는다.
3. `0 ... 0 | 1` 행이 나오면 모순이다.
4. 모순이 없으면 `2^(N - rank)`를 출력한다.

이 문제는 parity DSU로도 풀 수 있습니다. 하지만 이 연습의 목표는 "xor 제약을 linear system으로 번역하고 rank로 해 개수를 세는 과정"입니다.

## 로컬 연습 B: Tiny Matrix-Tree

### 입력

무향 단순 그래프가 주어집니다. spanning tree 개수를 `1,000,000,007`로 나눈 값을 구합니다.

```text
N M
a1 b1
...
aM bM
```

### 제한

- `2 <= N <= 80`
- `0 <= M <= 300`
- `0 <= ai, bi < N`

### 예시

```text
4 4
0 1
1 2
2 3
3 0
```

4-cycle은 간선 하나를 빼는 네 가지 방법이 spanning tree입니다.

```text
4
```

### 풀이 기준

1. Laplacian `L`을 만든다.
2. 아무 정점 하나의 행과 열을 지운다.
3. 남은 `(N-1) x (N-1)` matrix의 determinant를 modulo prime에서 계산한다.

이 연습은 determinant가 "행렬 값"이 아니라 graph counting을 압축한 값이라는 감각을 확인합니다.
