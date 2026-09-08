# Black-Box Linear Algebra

Black-Box Linear Algebra는 큰 행렬을 직접 저장하거나 `O(N^3)`으로 다루지 않고, sparse matrix-vector product만으로 rank, determinant, linear recurrence 정보를 얻는 관점입니다. 구현 대회에서 자주 쓰는 완성 템플릿은 아니지만, 큰 선형 시스템과 recurrence를 연결하는 중요한 모델입니다.


투영 수열의 최소 다항식은 행렬 최소 다항식의 약수일 수 있습니다. 한 번의 BM 결과가 곧 행렬의 최소 다항식이라는 뜻은 아닙니다. state·probe·entry는 [0,MOD)로 정규화하고 길이·인덱스 및 terms>=0을 맞춥니다. 현재 matvec는 0 초기화까지 O(N+nnz), T항은 O(T*(N+nnz))입니다. 여러 소수의 rank를 CRT로 합쳐 일반 해를 얻을 수는 없습니다.

## 문제 신호

| 문제 표현 | Black-box 관점 |
| --- | --- |
| 행렬 크기가 크지만 nonzero가 적다 | sparse matvec |
| `A^k v` 형태가 반복된다 | Krylov sequence |
| determinant/rank를 큰 prime mod에서 구한다 | randomized projection 후보 |
| recurrence 차수가 행렬 차수보다 작을 수 있다 | minimal polynomial |
| 행렬 원소를 직접 만들기 어렵고 곱만 쉽다 | matrix oracle |

핵심 입력은 `multiply(vector)`입니다. 행렬 전체를 노출하지 않아도 이 함수만 빠르면 알고리즘을 설계할 수 있습니다.

## Krylov Sequence

임의 vector `u`, `v`를 잡고 아래 수열을 만듭니다.

```text
s_k = u^T A^k v
```

Cayley-Hamilton 정리에 의해 이 수열은 선형 점화식을 가집니다. Berlekamp-Massey로 점화식을 찾으면 `A`의 minimal polynomial 정보를 얻을 수 있습니다.

무작위 `u`, `v`를 쓰는 이유는 특정 방향이 중요한 eigenspace를 놓치는 일을 줄이기 위해서입니다. 그래서 이 계열은 보통 randomized algorithm입니다.

## Sparse Matrix-Vector Product

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

## Wiedemann 관점

Wiedemann 알고리즘의 큰 흐름은 아래와 같습니다.

```text
random u, v
generate s_k = u^T A^k v for enough k
Berlekamp-Massey(s)
minimal polynomial candidate 확인
```

determinant나 rank를 얻으려면 추가 변환과 확률적 보정이 필요합니다. 이 레슨의 목표는 전체 이론을 외우는 것이 아니라, "행렬을 직접 보지 않고 수열로 낮추는" 감각을 갖는 것입니다.

## 작은 예시

```text
A = [[1, 1],
     [1, 0]]
v = [1, 0]
u = [1, 0]

s_k = u^T A^k v
    = 1, 1, 2, 3, 5, ...
```

행렬 거듭제곱이 Fibonacci 수열을 만들고, 수열은 `s_n = s_{n-1} + s_{n-2}` 점화식을 가집니다. Black-box 관점에서는 행렬의 구조를 수열의 recurrence로 압축한 셈입니다.

## Rank와 Determinant에서의 역할

큰 sparse matrix의 determinant를 바로 전개하지 않고, diagonal random preconditioner를 곱한 뒤 minimal polynomial의 상수항을 보는 기법들이 있습니다.

대회에서 이 수준이 직접 요구되는 경우는 드뭅니다. 다만 아래 문제 신호가 보이면 black-box linear algebra를 떠올릴 만합니다.

| 요구 | 힌트 |
| --- | --- |
| sparse matrix rank | random projection + Wiedemann |
| huge transition nth term | Krylov + BM |
| determinant modulo prime | randomized preconditioning |
| linear system consistency | rank 비교 또는 iterative method |

## Field 조건

Berlekamp-Massey와 많은 black-box 선형대수 기법은 field가 필요합니다. 즉 modulo가 prime이어야 나눗셈이 안전합니다.

합성수 modulo에서는 이 field 알고리즘을 그대로 적용하지 않습니다. 정수 determinant처럼 정수 값의 크기 상한과 각 소수에서의 올바른 잔여값이 있는 경우에는 CRT 복원이 가능하지만, rank나 일반 선형계의 해에 같은 조언을 적용할 수는 없습니다.

## 검증 전략

Randomized algorithm은 한 번 맞아 보이는 것으로 충분하지 않습니다.

1. 다른 random `u`, `v`로 반복한다.
2. 찾은 recurrence가 holdout 항에도 맞는지 확인한다.
3. 작은 입력은 dense Gaussian elimination과 비교한다.
4. zero matrix, identity matrix, singular matrix를 따로 테스트한다.

특히 rank/determinant는 실패 시 틀린 값을 조용히 낼 수 있으므로 stress test가 중요합니다.

## 시간 복잡도

| 단계 | 시간 |
| --- | ---: |
| sparse matvec 1회 | `O(N+nnz)` |
| `T`개 Krylov 항 생성 | `O(T * (N+nnz))` |
| 기본 Berlekamp-Massey | `O(T^2)` |
| dense elimination baseline | `O(N^3)` |

`nnz`가 `N^2`에 가깝다면 black-box 접근의 장점이 줄어듭니다. sparse일 때만 의미가 큽니다.
