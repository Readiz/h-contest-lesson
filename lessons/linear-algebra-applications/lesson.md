# Linear Algebra Applications

Linear Algebra Applications는 rank, determinant, basis, recurrence, graph counting을 각각 따로 외우는 대신 "무엇을 vector space로 볼 수 있는가"를 기준으로 문제를 번역하는 decision map입니다.

이 레슨은 Linear Basis Applications, Sparse Linear Systems, Black-Box Linear Algebra 이후에 보는 수학 모델링 심화입니다.

1. 상태를 vector로 표현할 수 있는지 확인한다.
2. 제약을 linear equation, span, rank, determinant 중 하나로 바꾼다.
3. field, dimension, sparsity, 필요한 답의 종류에 따라 구현 기법을 고른다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Gaussian Elimination, Linear Basis, Matrix Exponentiation
- 함께 보면 좋은 레슨: Sparse Linear Systems, Black-Box Linear Algebra, Generating Function Modeling
- 다음에 볼 레슨: algebraic graph algorithms, randomized determinant, matroid models

## 1. 문제 신호

| 문제 표현 | 선형대수 모델 |
| --- | --- |
| xor로 만들 수 있는 최댓값/개수 | GF(2) basis |
| 조건식이 모두 합과 계수로 표현된다 | linear system |
| perfect matching 존재성을 빠르게 판정 | determinant/randomized algebra |
| walk 수, recurrence, transition 반복 | matrix power/minimal polynomial |
| 독립인 object 최대 개수 | rank/matroid |

선형대수 모델은 답을 직접 주기보다 문제를 "차원", "span", "kernel", "rank"로 바꿔 줍니다. 이 번역이 맞으면 구현은 기존 알고리즘 중 하나를 선택하는 문제가 됩니다.

## 2. 선택 표

| 먼저 보이는 조건 | 우선 선택 | 대표 하위 주제 |
| --- | --- | --- |
| 값이 xor로 합쳐지고 carry가 없다 | GF(2) basis | XOR Linear Basis, Linear Basis Applications |
| 식 수와 변수 수가 작고 matrix가 dense하다 | Gaussian elimination | augmented rank, determinant |
| matrix가 크지만 matvec oracle이 빠르다 | black-box/sparse solver | Black-Box Linear Algebra, Sparse Linear Systems |
| 존재성이나 counting이 determinant로 압축된다 | modular determinant | Randomized Determinant, Matrix-Tree Theorem |
| graph 구조의 tree/counting을 묻는다 | Laplacian/cofactor | Matrix-Tree Theorem Applications |
| DP transition이 선형 반복이다 | matrix power 또는 minimal polynomial | Matrix Exponentiation, Polynomial and Recurrence Algorithms |

이 표는 "어떤 선형대수 레슨을 먼저 볼지"를 고르는 용도입니다. 실제 구현 레슨은 각 하위 문서에서 보고, 이 문서에서는 모델 번역과 선택 이유를 검증합니다.

## 3. 작은 예시: Parity Constraints

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

## 4. Rank로 세는 것

Rank는 독립인 정보의 수입니다.

| 상황 | rank 해석 |
| --- | --- |
| xor basis | 표현 가능한 xor 공간의 차원 |
| linear equations | 독립 제약식 수 |
| graph incidence over GF(2) | component/cycle space |
| vector matroid | 선택 가능한 독립 벡터 수 |

문제에서 "몇 가지가 독립인가", "몇 개를 자유롭게 정할 수 있는가", "표현 가능한 값이 몇 개인가"가 보이면 rank를 먼저 떠올립니다.

## 5. Determinant로 세는 것

Determinant는 단순한 행렬 값이 아니라 여러 조합적 구조의 압축입니다.

| 정리/기법 | 쓰임 |
| --- | --- |
| Matrix-Tree Theorem | spanning tree 개수 |
| Tutte matrix | perfect matching 존재성 |
| determinant polynomial identity | randomized zero test |
| Vandermonde determinant | interpolation 조건 |

랜덤 값을 대입해 determinant가 0이 아닌지 보는 방식은 확률적입니다. 여러 prime이나 여러 random seed로 반복하고, 작은 입력에서는 brute force와 비교해야 합니다.

## 6. Recurrence와 Matrix

DP transition이 선형이면 matrix power나 minimal polynomial로 바꿀 수 있습니다.

```text
state_{t+1} = A * state_t
answer_t = c^T * state_t
```

`t`가 매우 크면 `A^t`를 직접 거듭제곱합니다. `A`가 너무 크지만 matvec이 빠르면 Krylov sequence와 Berlekamp-Massey로 `answer_t`의 recurrence를 찾는 선택지도 있습니다.

## 7. 구현 선택표

| 조건 | 우선 선택 |
| --- | --- |
| `N <= 500`, dense | Gaussian elimination |
| GF(2), `N`이 큼 | bitset elimination |
| vector xor 최댓값 | XOR basis |
| sparse matrix, matvec 빠름 | black-box linear algebra |
| transition 차원이 작음 | matrix exponentiation |
| determinant/counting | modular determinant + randomization |

한 문제 안에서 여러 모델이 동시에 보일 수 있습니다. 예를 들어 graph cycle xor는 graph traversal로 cycle basis를 만든 뒤 XOR basis로 답을 냅니다.

## 8. C++ 구현 조각: GF(2) Rank

```cpp
int rankOverGF2(vector<unsigned long long> basisInput) {
    int rank = 0;
    for (int bit = 63; bit >= 0; --bit) {
        int pivot = -1;
        for (int row = rank; row < (int)basisInput.size(); ++row) {
            if ((basisInput[row] >> bit) & 1ULL) {
                pivot = row;
                break;
            }
        }
        if (pivot == -1) {
            continue;
        }
        swap(basisInput[rank], basisInput[pivot]);
        for (int row = 0; row < (int)basisInput.size(); ++row) {
            if (row != rank && ((basisInput[row] >> bit) & 1ULL)) {
                basisInput[row] ^= basisInput[rank];
            }
        }
        ++rank;
    }
    return rank;
}
```

`unsigned long long` 하나로는 64차원까지만 됩니다. 더 큰 GF(2) matrix는 `bitset`, `vector<unsigned long long>`, 또는 block basis로 바꿔야 합니다.

## 9. 자주 하는 실수

1. modulo가 prime이 아닌데 field처럼 나눗셈을 한다.
2. rank와 determinant를 같은 정보로 착각한다.
3. randomized determinant 판정을 한 번만 실행한다.
4. 선형이 아닌 transition에 matrix power를 억지로 적용한다.
5. 자유 변수 수를 `N - equations`로 계산하고 rank를 빼지 않는다.

## 10. 문제를 볼 때 체크할 조건

- 연산이 어떤 field 위에서 선형인가?
- 변수와 식의 수, matrix density는 어느 정도인가?
- 필요한 것이 해 하나, 해 개수, 독립성, determinant 중 무엇인가?
- randomized algorithm이 허용되는가?
- 작은 입력 brute force로 모델 번역을 확인할 수 있는가?

## 11. 대표 문제로 연결하기

### 문제에서 보이는 신호

- 입력 크기: 상태 수는 크지만 관계가 선형
- 필요한 복잡도: rank, determinant, recurrence 중 하나로 압축
- 이 레슨의 핵심 개념: vector space로 번역한 뒤 도구 선택

### 풀이 흐름

1. 값의 domain을 정한다. 예: GF(2), modulo prime, rational
2. variable vector를 정의한다.
3. 조건을 matrix row, basis vector, transition으로 바꾼다.
4. 필요한 값을 rank/determinant/recurrence로 연결한다.
5. 작은 입력에서 원래 조건과 선형 모델이 같은지 검증한다.

### 자주 틀리는 지점

- XOR 문제는 GF(2)에서는 선형이지만 modulo `1e9+7` 덧셈 문제와 완전히 다릅니다.
- determinant 기반 존재 판정은 collision 확률을 설명할 수 있어야 합니다.

## 12. 연습 문제

로컬 완결형 연습은 [Decision Map Practice](pages/decision-map-practice.md)에서 먼저 진행합니다. 실제 h-contest practice 문제와 연결되지 않은 항목은 아래 표에 TODO로 남겨 둡니다.

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | [Decision Map Practice](pages/decision-map-practice.md) | rank, determinant, recurrence 중 먼저 고르기 | model selection |
| 표준 | TODO: linear constraints `/practice/...` 문제 필요 | 해 없음/여러 해 판정 | augmented matrix |
| 응용 | TODO: determinant counting `/practice/...` 문제 필요 | determinant로 구조 세기 | Matrix-Tree |
| 함정 | TODO: randomized algebra `/practice/...` 문제 필요 | zero test 실패 확률 줄이기 | Schwartz-Zippel |
