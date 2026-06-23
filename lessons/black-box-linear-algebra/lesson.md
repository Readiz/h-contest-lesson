# Black-Box Linear Algebra

Black-Box Linear Algebra는 큰 행렬을 직접 저장하거나 `O(N^3)`으로 다루지 않고, sparse matrix-vector product만으로 rank, determinant, linear recurrence 정보를 얻는 관점입니다. 구현 대회에서 자주 쓰는 완성 템플릿은 아니지만, 큰 선형 시스템과 recurrence를 연결하는 중요한 모델입니다.

이 레슨은 Linear Recurrence Applications, Berlekamp-Massey, Modular Arithmetic 이후에 보는 수학 심화입니다.

1. 행렬을 원소 배열이 아니라 곱셈 oracle로 본다.
2. Krylov sequence `u^T A^k v`를 만들어 선형 점화식을 찾는다.
3. field 조건, randomized projection, 검증 단계를 분리한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Linear Recurrence Applications, Berlekamp-Massey, modular inverse
- 함께 보면 좋은 레슨: Matrix Exponentiation, Bostan-Mori, Recurrence Guessing
- 다음에 볼 레슨: sparse linear system, randomized verification, determinant algorithms

## 1. 문제 신호

| 문제 표현 | Black-box 관점 |
| --- | --- |
| 행렬 크기가 크지만 nonzero가 적다 | sparse matvec |
| `A^k v` 형태가 반복된다 | Krylov sequence |
| determinant/rank를 큰 prime mod에서 구한다 | randomized projection 후보 |
| recurrence 차수가 행렬 차수보다 작을 수 있다 | minimal polynomial |
| 행렬 원소를 직접 만들기 어렵고 곱만 쉽다 | matrix oracle |

핵심 입력은 `multiply(vector)`입니다. 행렬 전체를 노출하지 않아도 이 함수만 빠르면 알고리즘을 설계할 수 있습니다.

## 2. Krylov Sequence

임의 vector `u`, `v`를 잡고 아래 수열을 만듭니다.

```text
s_k = u^T A^k v
```

Cayley-Hamilton 정리에 의해 이 수열은 선형 점화식을 가집니다. Berlekamp-Massey로 점화식을 찾으면 `A`의 minimal polynomial 정보를 얻을 수 있습니다.

무작위 `u`, `v`를 쓰는 이유는 특정 방향이 중요한 eigenspace를 놓치는 일을 줄이기 위해서입니다. 그래서 이 계열은 보통 randomized algorithm입니다.

## 3. Sparse Matrix-Vector Product

아래는 edge list 형태의 sparse matrix를 vector에 곱하는 기본 skeleton입니다.

```cpp compile-check
#include <vector>
using namespace std;

const long long MOD_BLACK_BOX = 998244353;

struct SparseEntry {
    int row = 0;
    int col = 0;
    long long value = 0;
};

vector<long long> multiplySparseMatrix(
    int size,
    const vector<SparseEntry>& entries,
    const vector<long long>& vectorValue
) {
    vector<long long> result(size, 0);
    for (const SparseEntry& entry : entries) {
        long long add = entry.value * vectorValue[entry.col] % MOD_BLACK_BOX;
        result[entry.row] += add;
        if (result[entry.row] >= MOD_BLACK_BOX) {
            result[entry.row] -= MOD_BLACK_BOX;
        }
    }
    return result;
}

long long dotProductMod(const vector<long long>& left, const vector<long long>& right) {
    long long result = 0;
    for (int i = 0; i < (int)left.size(); ++i) {
        result = (result + left[i] * right[i]) % MOD_BLACK_BOX;
    }
    return result;
}

vector<long long> krylovSequence(
    int size,
    const vector<SparseEntry>& entries,
    vector<long long> state,
    const vector<long long>& probe,
    int terms
) {
    vector<long long> sequence;
    sequence.reserve(terms);
    for (int step = 0; step < terms; ++step) {
        sequence.push_back(dotProductMod(probe, state));
        state = multiplySparseMatrix(size, entries, state);
    }
    return sequence;
}
```

실전에서는 `entry.value`를 미리 `[0, MOD)`로 정규화하고, 여러 번 곱할 때 cache locality를 위해 row별로 묶습니다.

## 4. Wiedemann 관점

Wiedemann 알고리즘의 큰 흐름은 아래와 같습니다.

```text
random u, v
generate s_k = u^T A^k v for enough k
Berlekamp-Massey(s)
minimal polynomial candidate 확인
```

determinant나 rank를 얻으려면 추가 변환과 확률적 보정이 필요합니다. 이 레슨의 목표는 전체 이론을 외우는 것이 아니라, "행렬을 직접 보지 않고 수열로 낮추는" 감각을 갖는 것입니다.

## 5. 작은 예시

```text
A = [[1, 1],
     [1, 0]]
v = [1, 0]
u = [1, 0]

s_k = u^T A^k v
    = 1, 1, 2, 3, 5, ...
```

행렬 거듭제곱이 Fibonacci 수열을 만들고, 수열은 `s_n = s_{n-1} + s_{n-2}` 점화식을 가집니다. Black-box 관점에서는 행렬의 구조를 수열의 recurrence로 압축한 셈입니다.

## 6. Rank와 Determinant에서의 역할

큰 sparse matrix의 determinant를 바로 전개하지 않고, diagonal random preconditioner를 곱한 뒤 minimal polynomial의 상수항을 보는 기법들이 있습니다.

대회에서 이 수준이 직접 요구되는 경우는 드뭅니다. 다만 아래 문제 신호가 보이면 black-box linear algebra를 떠올릴 만합니다.

| 요구 | 힌트 |
| --- | --- |
| sparse matrix rank | random projection + Wiedemann |
| huge transition nth term | Krylov + BM |
| determinant modulo prime | randomized preconditioning |
| linear system consistency | rank 비교 또는 iterative method |

## 7. Field 조건

Berlekamp-Massey와 많은 black-box 선형대수 기법은 field가 필요합니다. 즉 modulo가 prime이어야 나눗셈이 안전합니다.

합성수 modulo에서 그대로 inverse를 쓰면 깨집니다. 필요하면 여러 prime에서 계산한 뒤 CRT로 합치거나, 문제 조건을 다시 확인해야 합니다.

## 8. 검증 전략

Randomized algorithm은 한 번 맞아 보이는 것으로 충분하지 않습니다.

1. 다른 random `u`, `v`로 반복한다.
2. 찾은 recurrence가 holdout 항에도 맞는지 확인한다.
3. 작은 입력은 dense Gaussian elimination과 비교한다.
4. zero matrix, identity matrix, singular matrix를 따로 테스트한다.

특히 rank/determinant는 실패 시 틀린 값을 조용히 낼 수 있으므로 stress test가 중요합니다.

## 9. 시간 복잡도

| 단계 | 시간 |
| --- | ---: |
| sparse matvec 1회 | `O(nnz)` |
| `T`개 Krylov 항 생성 | `O(T * nnz)` |
| 기본 Berlekamp-Massey | `O(T^2)` |
| dense elimination baseline | `O(N^3)` |

`nnz`가 `N^2`에 가깝다면 black-box 접근의 장점이 줄어듭니다. sparse일 때만 의미가 큽니다.

## 10. 자주 하는 실수

1. modulo가 prime인지 확인하지 않고 inverse를 쓴다.
2. projection vector가 나쁜 경우를 고려하지 않고 한 번만 시도한다.
3. 필요한 항 개수보다 짧은 수열로 recurrence를 확정한다.
4. sparse entry의 row/col 방향을 뒤집어 `A` 대신 `A^T`를 곱한다.
5. dense matrix를 만들 수 있는데도 과한 randomized 기법을 써서 구현 위험을 키운다.

## 11. 문제를 볼 때 체크할 조건

- 행렬 전체가 필요한가, matvec만 있으면 되는가?
- nonzero 수가 충분히 작은가?
- modulo가 field인가?
- 결과가 deterministic이어야 하는가, randomized 허용인가?
- 작은 입력으로 dense baseline을 만들 수 있는가?

## 12. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: sparse matrix-vector `/practice/...` 문제 필요 | row/col 방향과 modulo 처리 | matvec |
| 표준 | TODO: Krylov recurrence `/practice/...` 문제 필요 | `u^T A^k v` 수열 생성 | Berlekamp-Massey |
| 응용 | TODO: black-box determinant `/practice/...` 문제 필요 | randomized projection 검증 | Wiedemann |
| 함정 | TODO: composite modulo linear algebra `/practice/...` 문제 필요 | field 조건 판별 | modular inverse |
