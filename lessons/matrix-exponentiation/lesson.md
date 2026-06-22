# Matrix Exponentiation

Matrix Exponentiation은 선형 점화식이나 상태 전이를 행렬로 만들고, 빠른 거듭제곱으로 `K`번 적용하는 기법입니다. 피보나치 수처럼 이전 몇 항의 선형 결합으로 다음 항이 정해지거나, 그래프에서 길이 `K`인 walk 수를 세는 문제에 자주 나옵니다.

이 레슨은 "상태 벡터에 같은 선형 변환을 여러 번 적용한다"는 관점으로 행렬 거듭제곱을 봅니다.

1. 점화식을 상태 벡터와 전이 행렬로 바꾼다.
2. 행렬 곱셈과 빠른 거듭제곱을 구현한다.
3. 그래프 walk, DP transition 반복, affine transform으로 확장한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 모듈러 연산, 빠른 거듭제곱, 동적 계획법, 조합론
- 함께 보면 좋은 레슨: 모듈러 연산과 빠른 거듭제곱, 동적 계획법, 조합론
- 다음에 볼 레슨: Kitamasa, linear recurrence, FFT/NTT

## 1. 문제 신호

행렬 거듭제곱은 같은 전이를 아주 많이 반복할 때 사용합니다.

| 문제 신호 | 행렬 관점 |
| --- | --- |
| `N`번째 항을 구하는데 `N`이 `10^18` | 전이 행렬을 `N`번 거듭제곱 |
| `dp[t + 1]`이 `dp[t]`의 선형 결합 | 상태 벡터 전이 |
| 길이 `K`인 walk 수 | 인접 행렬의 `K`제곱 |
| 여러 값이 동시에 갱신된다 | 벡터와 행렬 |
| 상수항이 섞인다 | 상태에 상수 1을 추가 |

비선형 전이, `min`/`max` 전이, 조건이 시간마다 바뀌는 전이는 일반 행렬 곱셈으로 바로 처리할 수 없습니다.

## 2. 피보나치 예시

피보나치 점화식은 아래와 같습니다.

```text
F(n) = F(n - 1) + F(n - 2)
```

상태 벡터를 `[F(n), F(n - 1)]`로 두면 다음 상태는 행렬 곱으로 표현됩니다.

```text
[F(n + 1)]   [1 1] [F(n)    ]
[F(n)    ] = [1 0] [F(n - 1)]
```

따라서 전이 행렬을 `n - 1`번 적용하면 `F(n)`을 얻습니다. 빠른 거듭제곱을 쓰면 `O(log N)`번 행렬 곱으로 충분합니다.

## 3. 행렬 곱셈과 거듭제곱

아래 구현은 모듈러 행렬 곱셈과 빠른 거듭제곱입니다.

```cpp compile-check
#include <vector>
using namespace std;

using Matrix = vector<vector<long long>>;

Matrix identityMatrix(int n) {
    Matrix result(n, vector<long long>(n, 0));
    for (int i = 0; i < n; ++i) {
        result[i][i] = 1;
    }
    return result;
}

Matrix multiply(const Matrix& a, const Matrix& b, long long mod) {
    int n = (int)a.size();
    int m = (int)b[0].size();
    int inner = (int)b.size();
    Matrix result(n, vector<long long>(m, 0));

    for (int i = 0; i < n; ++i) {
        for (int k = 0; k < inner; ++k) {
            if (a[i][k] == 0) {
                continue;
            }
            for (int j = 0; j < m; ++j) {
                result[i][j] = (result[i][j] + a[i][k] * b[k][j]) % mod;
            }
        }
    }

    return result;
}

Matrix power(Matrix base, long long exp, long long mod) {
    Matrix result = identityMatrix((int)base.size());
    while (exp > 0) {
        if (exp & 1LL) {
            result = multiply(result, base, mod);
        }
        base = multiply(base, base, mod);
        exp >>= 1LL;
    }
    return result;
}
```

행렬 크기가 `D`이면 곱셈 한 번은 `O(D^3)`입니다. 거듭제곱은 곱셈을 `O(log K)`번 하므로 전체는 `O(D^3 log K)`입니다.

## 4. 선형 점화식 만들기

`a[n] = c1*a[n-1] + c2*a[n-2] + ... + cd*a[n-d]`라면 상태를 최근 `d`개 값으로 둡니다.

```text
[a[n]    ]   [c1 c2 c3 ... cd] [a[n-1]]
[a[n-1]  ] = [1  0  0  ... 0 ] [a[n-2]]
[a[n-2]  ]   [0  1  0  ... 0 ] [a[n-3]]
...
```

첫 행은 점화식 계수이고, 아래 행들은 값을 한 칸씩 밀어 내리는 역할입니다. 이 행렬을 companion matrix라고 생각하면 됩니다.

## 5. 상수항이 있는 전이

전이에 상수항이 있으면 상태 벡터에 항상 1인 값을 하나 추가합니다.

```text
x' = 2x + 3

[x']   [2 3] [x]
[1 ] = [0 1] [1]
```

이 기법은 affine transform, 누적합이 함께 필요한 점화식, 좌표 변환 반복에도 자주 쓰입니다.

## 6. 그래프 walk 수

그래프의 인접 행렬 `A`에서 `A[i][j] = i -> j 간선 수`라고 합시다. 그러면 `A^K[i][j]`는 길이 `K`인 walk가 `i`에서 `j`로 가는 경우의 수입니다.

```text
A^2[i][j] = sum A[i][mid] * A[mid][j]
```

이는 길이 1 walk 두 개를 이어 길이 2 walk를 만드는 방식입니다. 같은 이유로 `K`제곱이 길이 `K` walk 수를 나타냅니다.

## 7. 시간 복잡도와 최적화

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| `D x D` 행렬 곱 | `O(D^3)` | `O(D^2)` |
| 행렬 빠른 거듭제곱 | `O(D^3 log K)` | `O(D^2)` |
| 행렬과 벡터 곱 | `O(D^2)` | `O(D)` |

`D`가 2~50 정도면 일반 구현으로 충분할 수 있습니다. `D`가 수백이면 `O(D^3 log K)`가 부담이므로 sparse matrix, min-plus 최적화, Kitamasa 같은 다른 방법을 검토합니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 행렬을 반대로 곱함 | 상태 전이가 뒤집힘 | `next = T * current`인지 고정 |
| base case 지수 off-by-one | `F(n)` 대신 `F(n+1)` 출력 | 초기 벡터와 거듭제곱 횟수 확인 |
| 항등행렬 초기화 누락 | exp 0 처리 실패 | `result = I` |
| 상수항을 상태에 넣지 않음 | affine 전이 누락 | 마지막 상태 1 추가 |
| 곱셈 중 overflow | 모듈러 전 값 overflow | `long long`, 필요 시 `__int128` |
| `D`가 큰데 무작정 행렬 사용 | 시간 초과 | `D^3 log K` 계산 |

## 9. 문제를 볼 때 체크할 조건

1. 같은 선형 전이가 매우 많이 반복되는가?
2. 상태 수 `D`가 작고 고정되어 있는가?
3. 전이가 덧셈과 곱셈의 선형 결합인가?
4. 상수항을 상태에 추가할 수 있는가?
5. `K`가 커서 일반 DP가 불가능한가?
6. 모듈러와 overflow 조건이 명확한가?

Matrix Exponentiation은 빠른 거듭제곱의 대상을 숫자에서 행렬로 바꾼 것입니다. 점화식의 상태 벡터를 정확히 잡으면, 나머지는 곱셈 순서와 base case를 검증하는 구현 문제로 줄어듭니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 피보나치 큰 n `/practice/...` 문제 필요 | 2x2 전이 행렬과 빠른 거듭제곱 | fibonacci matrix |
| 표준 | TODO: k차 선형 점화식 `/practice/...` 문제 필요 | companion matrix 구성 | linear recurrence |
| 응용 | TODO: 길이 K walk 수 `/practice/...` 문제 필요 | 인접 행렬의 K제곱 해석 | graph walks |
| 함정 | TODO: 상수항 포함 전이 `/practice/...` 문제 필요 | 상태 벡터에 1 추가 | affine transform |
