# Formal Power Series

Formal Power Series는 다항식을 무한히 긴 계수열처럼 다루며, 미분, 적분, 역원, 로그, 지수 같은 연산을 계수 관점에서 정의하는 도구입니다. 대회에서는 NTT 기반 다항식 곱셈을 익힌 뒤, 조합론 생성함수와 polynomial DP를 빠르게 처리할 때 등장합니다.

이 레슨은 FFT/NTT 다음 단계의 polynomial 기본 연산을 정리합니다.

1. 계수 배열로 다항식을 표현한다.
2. 미분과 적분을 계수 연산으로 처리한다.
3. Newton iteration으로 다항식 역원을 구한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 모듈러 연산, NTT, 조합론, 다항식 곱셈
- 함께 보면 좋은 레슨: FFT와 NTT, 조합론, 모듈러 연산
- 다음에 볼 레슨: FPS log/exp, generating function, divide-and-conquer convolution DP

## 1. Formal의 의미

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

## 2. 기본 다항식 연산

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
```

실전에서는 inverse number를 미리 전처리해 적분을 `O(N)`으로 처리합니다. 위 구현은 개념을 보여 주기 위해 `modPow`를 직접 호출했습니다.

## 3. 곱셈과 truncate

FPS 연산은 필요한 차수까지만 유지합니다.

```text
A(x) * B(x) mod x^n
```

이는 `x^n` 이상의 항을 버린다는 뜻입니다. NTT convolution 결과를 얻은 뒤 `resize(n)`으로 자르면 됩니다.

작은 차수에서는 단순 `O(N^2)` 곱셈이 NTT보다 빠를 수 있습니다. 큰 입력에서만 NTT가 이득입니다.

## 4. 다항식 역원

`A(0) != 0`이면 `A(x)`의 곱셈 역원 `B(x)`가 존재합니다.

```text
A(x) * B(x) = 1 mod x^n
```

Newton iteration은 현재 `k`차까지 맞는 역원 `B`를 `2k`차까지 맞게 확장합니다.

```text
B_new = B * (2 - A * B) mod x^(2k)
```

이 식은 수의 Newton iteration과 비슷하게 오차 차수를 두 배로 늘립니다.

## 5. 단순 곱셈 기반 역원 예시

아래 코드는 구조를 보여 주기 위해 단순 곱셈을 사용합니다. 큰 입력에서는 `multiplyTruncated`를 NTT 기반으로 바꿉니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

const long long MOD_FPS = 998244353;

long long modPowFps(long long base, long long exp) {
    long long result = 1;
    while (exp > 0) {
        if (exp & 1LL) result = result * base % MOD_FPS;
        base = base * base % MOD_FPS;
        exp >>= 1LL;
    }
    return result;
}

vector<long long> multiplyTruncated(
    const vector<long long>& a,
    const vector<long long>& b,
    int limit
) {
    vector<long long> result(limit, 0);
    for (int i = 0; i < (int)a.size(); ++i) {
        for (int j = 0; j < (int)b.size() && i + j < limit; ++j) {
            result[i + j] = (result[i + j] + a[i] * b[j]) % MOD_FPS;
        }
    }
    return result;
}

vector<long long> inversePolynomial(const vector<long long>& a, int n) {
    vector<long long> result(1, modPowFps(a[0], MOD_FPS - 2));

    while ((int)result.size() < n) {
        int nextSize = min(2 * (int)result.size(), n);
        vector<long long> prefix(min((int)a.size(), nextSize));
        for (int i = 0; i < (int)prefix.size(); ++i) {
            prefix[i] = a[i];
        }

        vector<long long> product = multiplyTruncated(prefix, result, nextSize);
        for (long long& value : product) {
            value = (MOD_FPS - value) % MOD_FPS;
        }
        product[0] = (product[0] + 2) % MOD_FPS;
        result = multiplyTruncated(result, product, nextSize);
    }

    result.resize(n);
    return result;
}
```

`a[0]`이 0이면 역원이 없습니다. 이 조건을 빼먹으면 첫 상수항 inverse부터 실패합니다.

## 6. Log와 Exp로 이어지는 흐름

FPS log와 exp는 미분, 적분, 역원을 조합합니다.

```text
log A = integral(A' / A)
exp B는 log의 역연산
```

대회에서 generating function을 다루면 이 연산들이 등장합니다. 다만 구현량이 크므로, 먼저 inverse와 derivative/integral을 안정적으로 익히는 편이 좋습니다.

## 7. 생성함수 관점

조합론에서 경우의 수를 계수로 담으면 다항식이 됩니다.

```text
F(x) = sum ways[n] * x^n
```

두 독립 선택을 합치는 것은 다항식 곱셈입니다. 여러 조건을 빠르게 합치려면 convolution과 FPS 연산이 자연스럽게 연결됩니다.

## 8. 시간 복잡도

| 작업 | 단순 구현 | NTT 기반 |
| --- | ---: | ---: |
| 곱셈 | `O(N^2)` | `O(N log N)` |
| 미분/적분 | `O(N)` | `O(N)` |
| 역원 | `O(N^2)` 또는 그 이상 | `O(N log N)` 수준 |
| log | 곱셈/역원 비용 포함 | NTT 필요 |

실제 FPS 라이브러리는 상수와 메모리 사용량도 큽니다. 문제 제한이 작으면 단순 polynomial DP가 더 낫습니다.

## 9. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| `a[0] == 0`인데 역원 계산 | inverse 불가능 | 상수항 확인 |
| truncate를 안 함 | 시간/메모리 폭증 | 모든 연산 뒤 `resize(n)` |
| 적분에서 modular inverse 누락 | 계수 오답 | `(i+1)^{-1}` 곱 |
| mod가 NTT friendly가 아님 | NTT 오답 | mod/root 세트 확인 |
| 작은 입력에 과한 FPS 구현 | 복잡도 손해 | 단순 DP와 비교 |
| 계수 차수와 배열 index 혼동 | 한 칸 밀림 | `a[i]`는 `x^i` 계수 |

## 10. 문제를 볼 때 체크할 조건

1. 경우의 수가 계수열로 표현되는가?
2. 선택 결합이 convolution으로 바뀌는가?
3. 앞 `N`개 계수만 필요해 truncate할 수 있는가?
4. 역원, log, exp가 필요한 식인지 확인했는가?
5. mod와 원시근이 NTT에 맞는가?
6. 단순 `O(N^2)` 다항식으로 충분하지 않은가?

Formal Power Series는 구현보다 수식 변환이 더 중요합니다. 식이 계수 연산으로 정리되면, NTT와 inverse 같은 기본 블록을 조합해 큰 경우의 수 문제를 빠르게 처리할 수 있습니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: polynomial derivative/integral `/practice/...` 문제 필요 | 계수 index와 modular inverse 처리 | FPS basics |
| 표준 | TODO: polynomial inverse `/practice/...` 문제 필요 | Newton iteration 구현 | inverse FPS |
| 응용 | TODO: generating function convolution `/practice/...` 문제 필요 | 경우의 수 계수 결합 | generating function |
| 함정 | TODO: truncate가 필요한 FPS `/practice/...` 문제 필요 | `mod x^n` 유지 | truncation |
