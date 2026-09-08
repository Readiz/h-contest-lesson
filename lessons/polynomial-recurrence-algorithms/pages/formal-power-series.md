# Formal Power Series

Formal Power Series는 다항식을 무한히 긴 계수열처럼 다루며, 미분, 적분, 역원, 로그, 지수 같은 연산을 계수 관점에서 정의하는 도구입니다. 대회에서는 NTT 기반 다항식 곱셈을 익힌 뒤, 조합론 생성함수와 polynomial DP를 빠르게 처리할 때 등장합니다.


계수는 `[0,MOD)`로 정규화합니다. n과 truncate 길이는 비음수, 역원은 n>0이면 a가 비어 있지 않고 a[0]!=0이어야 합니다. 적분은 분모가 MOD 배수가 되지 않는 길이에서만 사용합니다. 현재 적분은 `O(N log MOD)`, 단순 곱셈 기반 역원은 `O(N²)`입니다.

## Formal의 의미

Formal Power Series에서는 `x`에 실제 값을 대입하기보다 계수들의 규칙을 다룹니다.

```text
A(x) = a0 + a1*x + a2*x^2 + ...
```

대회에서는 보통 앞 `N`개 계수만 필요합니다. 모든 연산 뒤에도 degree를 `N` 미만으로 잘라서 관리합니다.

| 연산 | 계수 관점 |
| --- | --- |
| 덧셈/뺄셈 | 같은 차수끼리 |
| 곱셈 | convolution |
| 미분 | `i*a[i]`가 `x^(i-1)` 계수 |
| 적분 | `a[i] / (i+1)`이 `x^(i+1)` 계수 |
| 역원 | `A(x) * B(x) = 1 mod x^n` |

## 기본 다항식 연산

아래 코드는 미분과 적분입니다. 모듈러는 소수라고 가정합니다.

```cpp compile-check
#include <vector>
using namespace std;

const long long MOD = 998244353;

long long modPow(long long base, long long exp) {
    long long result = 1;
    while (exp > 0) {
        if (exp & 1LL) {
            result = result * base % MOD;
        }
        base = base * base % MOD;
        exp >>= 1LL;
    }
    return result;
}

vector<long long> derivative(const vector<long long>& a) {
    if (a.size() <= 1) {
        return {0};
    }
    vector<long long> result(a.size() - 1);
    for (int i = 1; i < (int)a.size(); ++i) {
        result[i - 1] = a[i] * i % MOD;
    }
    return result;
}

vector<long long> integral(const vector<long long>& a) {
    vector<long long> result(a.size() + 1, 0);
    for (int i = 0; i < (int)a.size(); ++i) {
        result[i + 1] = a[i] * modPow(i + 1, MOD - 2) % MOD;
    }
    return result;
}
#include <algorithm>
#include <vector>
using namespace std;




vector<long long> multiplyTruncated(
    const vector<long long>& a,
    const vector<long long>& b,
    int limit
) {
    vector<long long> result(limit, 0);
    for (int i = 0; i < (int)a.size(); ++i) {
        for (int j = 0; j < (int)b.size() && i + j < limit; ++j) {
            result[i + j] = (result[i + j] + a[i] * b[j]) % MOD;
        }
    }
    return result;
}

vector<long long> inversePolynomial(const vector<long long>& a, int n) {
    if (n == 0) return {};
    vector<long long> result(1, modPow(a[0], MOD - 2));

    while ((int)result.size() < n) {
        int nextSize = min(2 * (int)result.size(), n);
        vector<long long> prefix(min((int)a.size(), nextSize));
        for (int i = 0; i < (int)prefix.size(); ++i) {
            prefix[i] = a[i];
        }

        vector<long long> product = multiplyTruncated(prefix, result, nextSize);
        for (long long& value : product) {
            value = (MOD - value) % MOD;
        }
        product[0] = (product[0] + 2) % MOD;
        result = multiplyTruncated(result, product, nextSize);
    }

    result.resize(n);
    return result;
}
```

실전에서는 inverse number를 미리 전처리해 적분을 `O(N)`으로 처리합니다. 위 구현은 개념을 보여 주기 위해 `modPow`를 직접 호출했습니다.

## 곱셈과 truncate

FPS 연산은 필요한 차수까지만 유지합니다.

```text
A(x) * B(x) mod x^n
```

이는 `x^n` 이상의 항을 버린다는 뜻입니다. NTT convolution 결과를 얻은 뒤 `resize(n)`으로 자르면 됩니다.

작은 차수에서는 단순 `O(N^2)` 곱셈이 NTT보다 빠를 수 있습니다. 큰 입력에서만 NTT가 이득입니다.

## 다항식 역원

`A(0) != 0`이면 `A(x)`의 곱셈 역원 `B(x)`가 존재합니다.

```text
A(x) * B(x) = 1 mod x^n
```

Newton iteration은 현재 `k`차까지 맞는 역원 `B`를 `2k`차까지 맞게 확장합니다.

```text
B_new = B * (2 - A * B) mod x^(2k)
```

이 식은 수의 Newton iteration과 비슷하게 오차 차수를 두 배로 늘립니다.

## 단순 곱셈 기반 역원 예시

아래 코드는 구조를 보여 주기 위해 단순 곱셈을 사용합니다. 큰 입력에서는 `multiplyTruncated`를 NTT 기반으로 바꿉니다.

위 `inversePolynomial`은 Newton 갱신에 단순 곱셈을 사용하는 검산용 구현입니다.

`a[0]`이 0이면 역원이 없습니다. 이 조건을 빼먹으면 첫 상수항 inverse부터 실패합니다.

형식적 거듭제곱급수에서 log와 exp는 계수 연산입니다. 소수 MOD 위에서 필요한 차수가 MOD보다 작아 1..N의 역원이 존재한다고 가정합니다.

## Log

F(0)=1일 때 `log F = integral(F'/F)`입니다. 위 구현의 derivative, inversePolynomial, multiplyTruncated, integral을 순서대로 사용하고 원하는 길이로 자릅니다. 적분 상수는 0입니다.

`log(1+x) = x-x²/2+x³/3-...`가 작은 검산 예시입니다. 나눗셈은 field 역원입니다.

## Exp

G(0)=0일 때 F=exp(G)는 F(0)=1이고 `F'=G'F`를 만족합니다. 따라서 작은 입력은 다음 계수 점화식으로 검산할 수 있습니다.

```text
f[0] = 1
f[n] = inverse(n) * sum(i*g[i]*f[n-i], i=1..n)
```

이 방법은 O(N²)입니다. `exp(x)=1+x+x²/2+x³/6+...`를 확인합니다. 빠른 구현은 `F <- F*(1+G-log F)`로 맞는 계수 길이를 두 배씩 늘리고 NTT 곱셈을 사용합니다. 수학식만 같다고 단순 곱셈이 O(N log N)이 되지는 않습니다.

## 생성함수에서의 의미

라벨이 붙은 조합 대상이 연결 성분들의 집합으로 유일하게 분해될 때 지수 생성함수는 `A(x)=exp(C(x))` 관계를 가질 수 있습니다. 이때 C(0)=0이며 계수의 n! 정규화를 포함해야 합니다. 임의의 일반 생성함수에 같은 관계를 적용하지 않습니다.

## 시간 복잡도

| 작업 | 단순 구현 | NTT 기반 |
| --- | ---: | ---: |
| 곱셈 | `O(N^2)` | `O(N log N)` |
| 미분 / 현재 적분 | `O(N)` / `O(N log MOD)` | 역원 전처리 시 적분 `O(N)` |
| 역원 | `O(N^2)` 또는 그 이상 | `O(N log N)` 수준 |
| log | 곱셈/역원 비용 포함 | NTT 필요 |

실제 FPS 라이브러리는 상수와 메모리 사용량도 큽니다. 문제 제한이 작으면 단순 polynomial DP가 더 낫습니다.
