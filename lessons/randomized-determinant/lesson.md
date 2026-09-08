# Randomized Determinant

Randomized Determinant는 determinant를 직접 수식 전개하지 않고, 무작위 값을 대입한 뒤 modular Gaussian elimination으로 nonzero 여부나 rank 성질을 확률적으로 판정하는 관점입니다. Polynomial Identity Testing과 Schwartz-Zippel lemma가 핵심 안전장치입니다.


정방행렬과 소수 2<=mod<=10^9+7을 전제로 하며 입력을 정규화합니다. Tutte 예시는 홀수 소수 field를 사용하고 각 간선 변수에 독립·균등 대입합니다. 0 대입도 Schwartz-Zippel의 정상 표본이며 이를 임의로 편향시키지 않습니다. 반복 실패 확률은 독립 trial에서 (degree/fieldSize)^K 이하로 평가합니다.

## 문제 신호

| 문제 표현 | Randomized Determinant 관점 |
| --- | --- |
| 어떤 구조가 존재하는지 determinant로 판정할 수 있다 | determinant polynomial |
| symbolic determinant는 너무 크다 | random substitution |
| rank가 최대인지 확인하고 싶다 | random projection 또는 random weights |
| matching 존재성, path cover, independence가 보인다 | algebraic encoding 후보 |
| 틀릴 확률을 허용하거나 반복 검증이 가능하다 | Monte Carlo algorithm |

대표 예시는 Tutte matrix입니다. 일반 그래프의 perfect matching 존재 여부를 determinant polynomial의 nonzero 여부로 바꾸고, random value를 대입해 빠르게 판정합니다.

## Schwartz-Zippel 직관

0이 아닌 다항식 `P`가 있고 각 변수에 field `F`의 값을 독립적으로 무작위 대입한다고 하겠습니다. 그러면 `P`가 우연히 0이 될 확률은 대략 `degree(P) / |F|` 이하입니다.

```text
P is nonzero polynomial
random assignment over large field
Pr[P(random values) = 0] <= degree(P) / fieldSize
```

따라서 큰 prime modulo를 쓰고 여러 번 반복하면, 존재하는 구조를 못 찾는 확률을 작게 만들 수 있습니다. 반대로 determinant가 nonzero로 나오면 구조가 있다는 증거가 됩니다.

## Modular Determinant 구현

아래는 prime modulo에서 determinant를 계산하는 기본 골격입니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;
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
    for (auto& row : matrix) for (auto& x : row) { x%=mod; if(x<0)x+=mod; }
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

## 작은 예시

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

## Matching 존재성 예시

무향 그래프의 Tutte matrix는 정점 `i < j` 사이 간선이 있으면 `A[i][j] = x_ij`, `A[j][i] = -x_ij`로 둡니다. 이 determinant polynomial이 0이 아니면 perfect matching이 존재합니다.

실전에서는 각 `x_ij`에 random modulo 값을 넣고 determinant가 nonzero인지 봅니다.

```text
edge exists -> random value r
A[i][j] = r
A[j][i] = -r
```

이 방식은 matching 자체를 복원하는 알고리즘과는 다릅니다. "존재성 판정"과 "구성 복원"을 분리해서 생각해야 합니다.

## Rank와 무작위 대입의 구분

고정 행렬에 가역인 무작위 대각 행렬을 곱해도 rank는 그대로입니다. 이를 pivot 상쇄를 없애 rank를 높이는 기법으로 설명할 수 없습니다. 여기의 확률성은 symbolic 행렬의 변수에 독립적인 값을 대입하는 데서 옵니다. 원래 field에서 다항식이 0이 아니라는 조건과 총차수/표본 집합 크기를 확인합니다.

## 반복 전략

```text
for trial in 1..K:
    fill variables with random values in prime field
    compute determinant
    if determinant != 0:
        return "nonzero polynomial"
return "probably zero"
```

`probably zero`는 증명이 아니라 확률적 결론입니다. `K`, prime 크기, polynomial degree에 따라 신뢰도를 설명할 수 있어야 합니다.

## 시간 복잡도

| 단계 | 시간 |
| --- | ---: |
| matrix 구성 | 문제 구조에 따라 다름 |
| determinant 1회 | `O(N^3)` |
| `K`회 반복 | `O(KN^3)` |
| sparse/black-box 변형 | 별도 알고리즘 필요 |

`N`이 수천 이상이면 dense determinant는 어렵습니다. 그때는 sparse elimination, black-box linear algebra, 또는 문제 특화 reduction을 봐야 합니다.

Nonzero determinant는 존재성을 판정하지만 객체 자체를 복원하지는 않습니다. 실제 matching 등이 출력에 필요하면 복원 절차를 별도로 준비합니다.
