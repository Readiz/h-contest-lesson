# Linear Recurrence Applications

Linear Recurrence Applications는 점화식이 주어진 상황을 넘어, 문제에서 recurrence를 찾아내고 Matrix Exponentiation, Kitamasa, Bostan-Mori, Berlekamp-Massey 중 무엇을 쓸지 고르는 레슨입니다. 핵심은 알고리즘 이름보다 "상태 전이가 선형인가"와 "계수가 고정인가"를 먼저 확인하는 것입니다.

이 레슨은 Matrix Exponentiation, Linear Recurrence와 Kitamasa, Bostan-Mori 이후에 보는 수학 응용입니다.

1. 수열, DP, graph walk에서 선형 전이를 찾는다.
2. 차수와 질의 수에 따라 계산 방식을 고른다.
3. 처음 몇 항만 있을 때는 recurrence 추정 가능성을 검토한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Matrix Exponentiation, Kitamasa, Bostan-Mori, modular arithmetic
- 함께 보면 좋은 레슨: Formal Power Series, Polynomial Interpolation, Multipoint Evaluation
- 다음에 볼 레슨: recurrence guessing, generating function modeling, polynomial power

## 1. 문제 신호

| 문제 표현 | Recurrence 관점 |
| --- | --- |
| 이전 K개 항으로 다음 항 결정 | 직접 linear recurrence |
| 격자/그래프 walk 수 `n`번째 | matrix power 또는 characteristic polynomial |
| 동일 전이를 매우 많이 반복 | transition exponentiation |
| 처음 항만 많이 주어짐 | Berlekamp-Massey 후보 |
| 생성함수 분모가 낮은 차수 | Bostan-Mori 후보 |

점화식이 선형이려면 다음 항이 이전 항들의 상수 계수 합이어야 합니다. `min`, `max`, `xor`가 섞이면 다른 구조일 수 있습니다.

## 2. 방법 선택표

| 조건 | 우선 방법 |
| --- | --- |
| 상태 수가 작고 전이가 일반적 | Matrix Exponentiation |
| 단일 K차 recurrence, K가 중간 | Kitamasa |
| 생성함수 `P/Q`가 주어짐 | Bostan-Mori |
| 앞 항만 있고 recurrence를 모름 | Berlekamp-Massey + Kitamasa |
| 같은 recurrence에 많은 n 질의 | polynomial power 전처리 또는 multipoint |

구현 안정성까지 보면, K가 작으면 행렬이 가장 읽기 쉽습니다. K가 커지고 전이가 companion 형태면 Kitamasa가 유리합니다.

## 3. 그래프 Walk를 Recurrence로 보기

정점 수가 `S`인 graph에서 길이 `n` walk 수는 adjacency matrix `A^n`으로 계산합니다. Cayley-Hamilton 정리에 의해 각 entry도 차수 `S` 이하의 선형 recurrence를 가집니다.

```text
walk_n = (A^n)[start][target]
```

`S`가 작으면 matrix exponentiation이 충분합니다. `S`가 크지만 처음 항을 빠르게 만들 수 있으면 Berlekamp-Massey로 recurrence를 추정하는 전략도 후보가 됩니다.

## 4. Berlekamp-Massey 연결

모듈러 prime field에서 수열의 앞 항을 충분히 알고 있으면 최소 선형 점화식을 찾을 수 있습니다.

```text
first terms -> Berlekamp-Massey -> coeff -> Kitamasa nth term
```

주의할 점은 "충분한 앞 항"입니다. 차수 `K` recurrence라면 보통 `2K`개 이상이 필요합니다. 항 생성 자체가 비싸면 이 전략이 이득이 아닐 수 있습니다.

## 5. Companion Matrix와 Kitamasa

K차 recurrence는 companion matrix로도 볼 수 있습니다.

```text
[a_n, a_{n-1}, ..., a_{n-K+1}]^T
  = M * [a_{n-1}, ..., a_{n-K}]^T
```

Kitamasa는 이 companion matrix의 거듭제곱을 polynomial 나머지로 계산하는 관점입니다. 그래서 recurrence가 정확히 K개 이전 항의 선형 결합일 때 잘 맞습니다.

## 6. Bostan-Mori가 좋은 경우

생성함수가 아래처럼 rational form이면 Bostan-Mori가 직접적입니다.

```text
F(x) = P(x) / Q(x)
answer = [x^n] F(x)
```

조합 문제에서 "길이 n 구조의 개수"가 polynomial equation이나 transfer로 나오면 생성함수 분모를 만들 수 있습니다. 이때 nth coefficient extraction이 recurrence 계산과 같은 역할을 합니다.

## 7. 작은 예시

```text
문제: 길이 n 문자열에서 11이 나오지 않는 binary string 개수

dp0[n] = n번째가 0으로 끝남
dp1[n] = n번째가 1로 끝남

dp0[n] = dp0[n-1] + dp1[n-1]
dp1[n] = dp0[n-1]

total[n] = total[n-1] + total[n-2]
```

상태 DP로 보면 2x2 matrix이고, 수열로 보면 Fibonacci 형태의 2차 recurrence입니다. 필요한 질의와 N 범위에 따라 둘 중 하나를 고르면 됩니다.

## 8. 구현 Skeleton

아래 코드는 recurrence가 주어졌다고 가정하고, 작은 K는 행렬 대신 Kitamasa 함수로 보내는 wrapper 형태입니다.

```cpp compile-check
#include <vector>
using namespace std;

const long long MOD_LINEAR_APP = 998244353;

long long modNormalizeLinearApp(long long value) {
    value %= MOD_LINEAR_APP;
    if (value < 0) {
        value += MOD_LINEAR_APP;
    }
    return value;
}

vector<long long> combineLinearApp(
    const vector<long long>& a,
    const vector<long long>& b,
    const vector<long long>& coeff
) {
    int k = (int)coeff.size();
    vector<long long> temp(2 * k - 1, 0);
    for (int i = 0; i < k; ++i) {
        for (int j = 0; j < k; ++j) {
            temp[i + j] = (temp[i + j] + a[i] * b[j]) % MOD_LINEAR_APP;
        }
    }
    for (int degree = 2 * k - 2; degree >= k; --degree) {
        long long value = temp[degree];
        for (int j = 1; j <= k; ++j) {
            temp[degree - j] = (temp[degree - j] + value * coeff[j - 1]) % MOD_LINEAR_APP;
        }
    }
    temp.resize(k);
    return temp;
}

long long nthByRecurrence(
    const vector<long long>& initial,
    const vector<long long>& coeff,
    long long n
) {
    int k = (int)coeff.size();
    if (n < (long long)initial.size()) {
        return modNormalizeLinearApp(initial[(int)n]);
    }

    vector<long long> result(k, 0);
    vector<long long> base(k, 0);
    result[0] = 1;
    if (k == 1) {
        base[0] = coeff[0];
    } else {
        base[1] = 1;
    }

    while (n > 0) {
        if (n & 1LL) {
            result = combineLinearApp(result, base, coeff);
        }
        base = combineLinearApp(base, base, coeff);
        n >>= 1LL;
    }

    long long answer = 0;
    for (int i = 0; i < k; ++i) {
        answer = (answer + result[i] * modNormalizeLinearApp(initial[i])) % MOD_LINEAR_APP;
    }
    return answer;
}
```

실전에서는 coeff 순서와 초기항 index를 문제 statement 기준으로 먼저 고정해야 합니다.

## 9. 시간 복잡도

| 방법 | 시간 |
| --- | ---: |
| Matrix exponentiation | `O(S^3 log N)` |
| Kitamasa 기본형 | `O(K^2 log N)` |
| Berlekamp-Massey | `O(T^2)` 또는 최적화 가능 |
| Bostan-Mori with NTT | `O(K log K log N)` 근처 |

`S`는 상태 수, `K`는 recurrence 차수입니다. 둘이 같을 수도 있지만 항상 같지는 않습니다.

## 10. 자주 하는 실수

1. recurrence가 선형이 아닌데 BM으로 추정하려 한다.
2. 합성수 mod에서 field inverse가 필요한 알고리즘을 그대로 쓴다.
3. 초기항이 `a_1`부터 주어졌는데 `a_0` 기반 함수에 그대로 넣는다.
4. 여러 질의에서 매번 앞 항을 새로 생성한다.
5. matrix 상태 순서와 recurrence coeff 순서를 섞는다.

## 11. 문제를 볼 때 체크할 조건

- 전이가 정말 선형인가?
- 계수가 시간에 따라 바뀌는가?
- mod가 prime인가?
- K, N, query 수 중 병목은 무엇인가?
- 점화식이 직접 주어졌는가, 앞 항에서 추정해야 하는가?

## 12. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: recurrence modeling `/practice/...` 문제 필요 | DP에서 recurrence 추출 | state compression |
| 표준 | TODO: many nth recurrence `/practice/...` 문제 필요 | Kitamasa 선택 | characteristic polynomial |
| 응용 | TODO: Berlekamp-Massey application `/practice/...` 문제 필요 | 앞 항에서 점화식 추정 | minimal recurrence |
| 함정 | TODO: non-linear sequence `/practice/...` 문제 필요 | 선형성 검증 | counterexample |
