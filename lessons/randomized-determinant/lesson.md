# Randomized Determinant

Randomized Determinant는 determinant를 직접 수식 전개하지 않고, 무작위 값을 대입한 뒤 modular Gaussian elimination으로 nonzero 여부나 rank 성질을 확률적으로 판정하는 관점입니다. Polynomial Identity Testing과 Schwartz-Zippel lemma가 핵심 안전장치입니다.

이 레슨은 Black-Box Linear Algebra, Matrix Exponentiation, Modular Arithmetic 이후에 보는 선형대수/확률 심화입니다.

1. determinant가 어떤 성질을 나타내는 polynomial인지 확인한다.
2. symbolic 변수를 큰 prime field의 random value로 바꾼다.
3. false negative 가능성을 반복과 검증으로 낮춘다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Modular Arithmetic, Black-Box Linear Algebra, Probability and Expected Value
- 함께 보면 좋은 레슨: General Matching, Linear Algebra Applications, Testing and Stress
- 다음에 볼 레슨: matrix-tree theorem applications, algebraic matching, randomized verification

## 1. 문제 신호

| 문제 표현 | Randomized Determinant 관점 |
| --- | --- |
| 어떤 구조가 존재하는지 determinant로 판정할 수 있다 | determinant polynomial |
| symbolic determinant는 너무 크다 | random substitution |
| rank가 최대인지 확인하고 싶다 | random projection 또는 random weights |
| matching 존재성, path cover, independence가 보인다 | algebraic encoding 후보 |
| 틀릴 확률을 허용하거나 반복 검증이 가능하다 | Monte Carlo algorithm |

대표 예시는 Tutte matrix입니다. 일반 그래프의 perfect matching 존재 여부를 determinant polynomial의 nonzero 여부로 바꾸고, random value를 대입해 빠르게 판정합니다.

## 2. Schwartz-Zippel 직관

0이 아닌 다항식 `P`가 있고 각 변수에 field `F`의 값을 독립적으로 무작위 대입한다고 하겠습니다. 그러면 `P`가 우연히 0이 될 확률은 대략 `degree(P) / |F|` 이하입니다.

```text
P is nonzero polynomial
random assignment over large field
Pr[P(random values) = 0] <= degree(P) / fieldSize
```

따라서 큰 prime modulo를 쓰고 여러 번 반복하면, 존재하는 구조를 못 찾는 확률을 작게 만들 수 있습니다. 반대로 determinant가 nonzero로 나오면 구조가 있다는 증거가 됩니다.

## 3. Modular Determinant 구현

아래는 prime modulo에서 determinant를 계산하는 기본 골격입니다.

```cpp
long long modPow(long long base, long long exponent, long long mod) {
    long long result = 1;
    while (exponent > 0) {
        if (exponent & 1LL) {
            result = result * base % mod;
        }
        base = base * base % mod;
        exponent >>= 1LL;
    }
    return result;
}

long long determinantMod(vector<vector<long long>> matrix, long long mod) {
    int n = (int)matrix.size();
    long long det = 1;
    for (int col = 0; col < n; ++col) {
        int pivot = col;
        while (pivot < n && matrix[pivot][col] == 0) {
            ++pivot;
        }
        if (pivot == n) {
            return 0;
        }
        if (pivot != col) {
            swap(matrix[pivot], matrix[col]);
            det = (mod - det) % mod;
        }
        long long pivotValue = matrix[col][col] % mod;
        det = det * pivotValue % mod;
        long long inverse = modPow(pivotValue, mod - 2, mod);
        for (int row = col + 1; row < n; ++row) {
            long long factor = matrix[row][col] * inverse % mod;
            if (factor == 0) {
                continue;
            }
            for (int k = col; k < n; ++k) {
                matrix[row][k] = (matrix[row][k] - factor * matrix[col][k]) % mod;
                if (matrix[row][k] < 0) {
                    matrix[row][k] += mod;
                }
            }
        }
    }
    return det;
}
```

`mod`는 prime이어야 합니다. 합성수 modulo에서 `mod - 2` inverse를 쓰면 조용히 틀립니다.

## 4. 작은 예시

다항식 determinant가 아래처럼 생겼다고 하겠습니다.

```text
P(x, y) = det [[x, 1],
               [1, y]]
        = xy - 1
```

`P`는 0 다항식이 아닙니다. 하지만 `x = 1`, `y = 1`을 대입하면 값은 0입니다. 한 번의 random 대입은 우연히 실패할 수 있으므로, 다른 값을 다시 넣어 확인해야 합니다.

```text
x = 2, y = 5 -> P = 9
```

nonzero 값이 한 번이라도 나오면 `P`가 0 다항식이 아니라는 것을 알 수 있습니다.

## 5. Matching 존재성 예시

무향 그래프의 Tutte matrix는 정점 `i < j` 사이 간선이 있으면 `A[i][j] = x_ij`, `A[j][i] = -x_ij`로 둡니다. 이 determinant polynomial이 0이 아니면 perfect matching이 존재합니다.

실전에서는 각 `x_ij`에 random modulo 값을 넣고 determinant가 nonzero인지 봅니다.

```text
edge exists -> random value r
A[i][j] = r
A[j][i] = -r
```

이 방식은 matching 자체를 복원하는 알고리즘과는 다릅니다. "존재성 판정"과 "구성 복원"을 분리해서 생각해야 합니다.

## 6. Rank 판정과 Random Weight

rank를 안정적으로 드러내기 위해 행이나 열에 random diagonal scaling을 곱하는 기법도 있습니다. 특정 구조 때문에 pivot이 우연히 상쇄되는 일을 줄이려는 목적입니다.

| 목적 | 흔한 장치 |
| --- | --- |
| nonzero determinant 판정 | random substitution |
| maximum rank 추정 | random projection/scaling |
| matching existence | Tutte matrix |
| symbolic cancellation 회피 | 여러 prime과 반복 |

결과가 확률적이라는 점은 숨기면 안 됩니다. 문제에서 deterministic answer가 요구되면, 작은 입력 검증이나 여러 반복으로 실패 확률을 충분히 낮춰야 합니다.

## 7. 반복 전략

```text
for trial in 1..K:
    fill variables with random values in prime field
    compute determinant
    if determinant != 0:
        return "nonzero polynomial"
return "probably zero"
```

`probably zero`는 증명이 아니라 확률적 결론입니다. `K`, prime 크기, polynomial degree에 따라 신뢰도를 설명할 수 있어야 합니다.

## 8. 시간 복잡도

| 단계 | 시간 |
| --- | ---: |
| matrix 구성 | 문제 구조에 따라 다름 |
| determinant 1회 | `O(N^3)` |
| `K`회 반복 | `O(KN^3)` |
| sparse/black-box 변형 | 별도 알고리즘 필요 |

`N`이 수천 이상이면 dense determinant는 어렵습니다. 그때는 sparse elimination, black-box linear algebra, 또는 문제 특화 reduction을 봐야 합니다.

## 9. 자주 하는 실수

1. modulo가 prime인지 확인하지 않고 inverse를 계산한다.
2. random 값에 0을 너무 자주 넣어 구조를 스스로 지운다.
3. determinant가 0이면 "항상 불가능"이라고 단정한다.
4. existence 판정 알고리즘으로 실제 해를 복원하려고 한다.
5. signed matrix에서 `A[j][i] = -A[i][j]` 처리를 빼먹는다.

## 10. 대표 문제로 연결하기

### 문제에서 보이는 신호

- 입력 크기: dense determinant가 가능한 수백 이하이거나 sparse 변형이 있음
- 필요한 복잡도: 조합 탐색 대신 algebraic existence test
- 이 레슨의 핵심 개념: nonzero polynomial을 random evaluation으로 판정

### 풀이 흐름

1. 문제의 존재 조건을 determinant 또는 rank 조건으로 번역한다.
2. 변수가 들어가는 위치와 부호를 정확히 정한다.
3. 큰 prime modulo에서 random value를 채운다.
4. determinant를 계산하고 여러 번 반복한다.
5. 작은 입력은 brute force와 비교해 false modeling을 잡는다.

### 자주 틀리는 지점

- 확률적 실패와 구현 버그를 구분하려면 seed를 고정한 stress test가 필요합니다.
- determinant가 nonzero라는 사실은 보통 존재성만 줍니다. 실제 객체가 필요하면 별도 복원 절차가 있어야 합니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: randomized determinant `/practice/...` 문제 필요 | modular determinant와 prime field 점검 | Gaussian elimination |
| 표준 | TODO: polynomial identity `/practice/...` 문제 필요 | random substitution으로 nonzero 판정 | Schwartz-Zippel |
| 응용 | TODO: Tutte matrix `/practice/...` 문제 필요 | matching 존재성을 determinant로 바꾸기 | skew-symmetric matrix |
| 함정 | TODO: determinant false zero `/practice/...` 문제 필요 | 반복과 seed 검증 | Monte Carlo |
