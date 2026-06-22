# Multiplicative Functions

Multiplicative Functions는 `gcd(a, b)=1`일 때 `f(ab)=f(a)f(b)`를 만족하는 산술 함수입니다. Euler phi, Mobius function, divisor count, divisor sum처럼 정수론 문제에서 반복되는 함수들을 linear sieve로 한 번에 계산할 수 있습니다.

이 레슨은 Mobius Inversion과 Dirichlet Convolution 이후에 보는 정수론 심화입니다.

1. 함수가 prime power에서 어떻게 정의되는지 확인한다.
2. 서로소 곱에서 값이 곱으로 분리되는지 본다.
3. linear sieve에서 `p | i`와 `p not | i` 경우를 나누어 값을 갱신한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: prime factorization, sieve, gcd, Mobius inversion
- 함께 보면 좋은 레슨: Dirichlet Convolution, Mobius Inversion, Extended Euclid와 CRT
- 다음에 볼 레슨: summatory number theory, divisor transform, multiplicative prefix sum

## 1. 문제 신호

| 문제 표현 | Multiplicative Function 관점 |
| --- | --- |
| 모든 `n <= N`에 대해 `phi(n)`, `mu(n)` 필요 | linear sieve |
| 약수 개수나 약수 합을 많이 물어봄 | prime power 상태 관리 |
| gcd가 1인 곱에서 값이 분리됨 | multiplicativity |
| `n = p^k * rest` 구조로 갱신 가능 | least prime factor DP |
| Dirichlet convolution 결과 함수 필요 | multiplicative closure |

함수가 multiplicative이면 모든 수를 직접 factorization하지 않고 sieve 순서에서 값을 채울 수 있습니다.

## 2. Multiplicative와 Completely Multiplicative

두 개념은 다릅니다.

| 종류 | 조건 | 예 |
| --- | --- | --- |
| multiplicative | `gcd(a,b)=1`일 때만 `f(ab)=f(a)f(b)` | `phi`, `mu`, `tau`, `sigma` |
| completely multiplicative | 모든 `a,b`에서 성립 | `f(n)=n^k`, 일부 character |

대부분의 산술 함수는 multiplicative일 뿐입니다. 예를 들어 `phi(p^2)`는 `phi(p)^2`가 아닙니다.

## 3. Prime Power 공식

Multiplicative function은 prime power 값만 알면 전체 값을 조립할 수 있습니다.

| 함수 | `p^k`에서 값 |
| --- | --- |
| `phi(n)` | `p^k - p^(k-1)` |
| `mu(n)` | `-1` if `k=1`, `0` if `k>=2` |
| `tau(n)` | `k + 1` |
| `sigma(n)` | `1 + p + ... + p^k` |

따라서 sieve에서는 현재 수 `i`에 새 prime `p`를 붙일 때, `p`가 이미 `i`를 나누는지 여부가 중요합니다.

## 4. Linear Sieve 구현

아래 코드는 `phi`, `mu`, 약수 개수 `tau`를 `O(N)`에 계산합니다.

```cpp compile-check
#include <vector>
using namespace std;

struct MultiplicativeSieve {
    vector<int> primes;
    vector<int> isComposite;
    vector<int> phi;
    vector<int> mu;
    vector<int> exponent;
    vector<int> coreTau;
    vector<int> tau;

    explicit MultiplicativeSieve(int limit)
        : isComposite(limit + 1, 0),
          phi(limit + 1, 0),
          mu(limit + 1, 0),
          exponent(limit + 1, 0),
          coreTau(limit + 1, 1),
          tau(limit + 1, 1) {
        phi[1] = 1;
        mu[1] = 1;
        exponent[1] = 0;
        tau[1] = 1;

        for (int i = 2; i <= limit; ++i) {
            if (!isComposite[i]) {
                primes.push_back(i);
                phi[i] = i - 1;
                mu[i] = -1;
                exponent[i] = 1;
                coreTau[i] = 1;
                tau[i] = 2;
            }

            for (int prime : primes) {
                long long value = 1LL * i * prime;
                if (value > limit) {
                    break;
                }

                int next = (int)value;
                isComposite[next] = 1;

                if (i % prime == 0) {
                    phi[next] = phi[i] * prime;
                    mu[next] = 0;
                    exponent[next] = exponent[i] + 1;
                    coreTau[next] = coreTau[i];
                    tau[next] = coreTau[next] * (exponent[next] + 1);
                    break;
                }

                phi[next] = phi[i] * (prime - 1);
                mu[next] = -mu[i];
                exponent[next] = 1;
                coreTau[next] = tau[i];
                tau[next] = tau[i] * 2;
            }
        }
    }
};
```

`tau`는 같은 prime power가 늘어날 때 기존 `(k+1)` factor를 `(k+2)`로 바꿔야 합니다. 그래서 `coreTau`처럼 해당 prime power를 제외한 나머지 부분을 따로 들고 있습니다.

## 5. Dirichlet Convolution과 닫힘

두 multiplicative function의 Dirichlet convolution도 multiplicative입니다.

```text
h = f * g
h(n) = sum_{d|n} f(d)g(n/d)
```

그래서 `phi * 1 = id`, `mu * 1 = epsilon`, `tau = 1 * 1` 같은 관계를 prime power에서 확인한 뒤 전체로 확장할 수 있습니다.

## 6. Summatory Function으로 이어지기

문제가 아래처럼 모든 값을 더하라고 하면 단순 sieve만으로 부족할 수 있습니다.

```text
sum_{i=1..N} phi(i)
sum_{i=1..N} mu(i)
sum_{i=1..N} floor(N / i) * f(i)
```

`N`이 `10^7` 정도면 prefix sum을 만들면 됩니다. `N`이 `10^11` 이상이면 같은 `floor(N/i)` 값을 묶거나 더 고급 summatory technique가 필요합니다.

## 7. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| linear sieve | `O(N)` |
| simple divisor zeta | `O(N log N)` |
| 각 수 factorization with SPF | 전체 대략 `O(N log N)` |
| prefix sum query | 전처리 후 `O(1)` |

여러 함수를 동시에 구해도 sieve loop는 하나로 묶을 수 있습니다.

## 8. 자주 하는 실수

1. multiplicative와 completely multiplicative를 혼동한다.
2. `p | i`인 경우에 break하지 않아 같은 수를 여러 번 갱신한다.
3. `mu[p^2] = 0` 처리를 빠뜨린다.
4. `tau`나 `sigma`에서 prime exponent 상태를 따로 관리하지 않는다.
5. 함수 값이 커지는데 모듈러 또는 `long long` 범위를 확인하지 않는다.

## 9. 문제를 볼 때 체크할 조건

- 함수가 서로소 곱에서 분리되는가?
- prime power 공식이 간단한가?
- 모든 `n <= N`이 필요한가, query로 일부만 필요한가?
- `N` 기준 배열 전처리가 가능한가?
- Dirichlet convolution이나 Mobius inversion으로 더 쉬운 함수로 바꿀 수 있는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: multiplicative function sieve `/practice/...` 문제 필요 | `phi`, `mu` linear sieve 구현 | prime power |
| 표준 | TODO: divisor count sum `/practice/...` 문제 필요 | `tau` exponent 상태 관리 | least prime factor |
| 응용 | TODO: multiplicative convolution `/practice/...` 문제 필요 | convolution 관계로 함수 설계 | Dirichlet convolution |
| 함정 | TODO: large summatory function `/practice/...` 문제 필요 | prefix와 floor grouping 구분 | summatory |
