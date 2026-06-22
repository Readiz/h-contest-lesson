# Dirichlet Convolution

Dirichlet Convolution은 약수 관계 위에서 두 산술 함수 `f`, `g`를 합성하는 연산입니다. `h(n) = sum_{d|n} f(d)g(n/d)` 형태가 보이면 Mobius Inversion, multiplicative function, divisor transform을 하나의 언어로 정리할 수 있습니다.

이 레슨은 Mobius Inversion, 정수론 심화, 조합론 이후에 보는 수학 심화입니다.

1. 약수 합 관계를 Dirichlet convolution으로 쓴다.
2. `1`, `mu`, `id`, `phi` 같은 기본 함수를 convolution 관계로 이해한다.
3. divisor zeta/Mobius transform으로 여러 값을 한 번에 계산한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: gcd, divisor enumeration, Mobius function, sieve
- 함께 보면 좋은 레슨: Mobius Inversion, Extended Euclid와 CRT, Combinatorics
- 다음에 볼 레슨: multiplicative function DP, divisor transform, number theoretic summatory functions

## 1. 문제 신호

| 문제 표현 | Dirichlet Convolution 관점 |
| --- | --- |
| `n`의 모든 약수 `d`에 대해 합산 | divisor convolution |
| 약수 합으로 정의된 함수를 역변환 | Mobius inverse |
| multiplicative function 두 개를 합성 | convolution preserves multiplicativity |
| gcd나 lcm 관련 합 | divisor grouping |
| 모든 `n <= N`에 대해 약수 합 필요 | sieve over multiples |

Mobius Inversion은 Dirichlet convolution에서 `1` 함수의 역원이 `mu`라는 특수한 경우입니다.

## 2. 정의

두 함수 `f`, `g`의 Dirichlet convolution은 아래와 같습니다.

```text
(f * g)(n) = sum_{d | n} f(d) * g(n / d)
```

항등원은 `epsilon(1)=1`, `epsilon(n>1)=0`인 함수입니다. 모든 `n`에서 1인 함수는 보통 `1(n)`으로 쓰고, `mu * 1 = epsilon`입니다.

## 3. 대표 관계

| 관계 | 의미 |
| --- | --- |
| `F = f * 1` | `F(n)`은 `f`의 약수 합 |
| `f = F * mu` | Mobius inversion |
| `phi * 1 = id` | `sum_{d|n} phi(d) = n` |
| `sigma = id * 1` | 약수 합 함수 |
| `tau = 1 * 1` | 약수 개수 함수 |

공식을 외우기보다 "어떤 함수의 약수 합인가"를 먼저 찾으면 역변환 방향이 자연스럽습니다.

## 4. 기본 구현

아래 코드는 `1..N` 범위에서 convolution과 divisor zeta transform을 계산합니다.

```cpp compile-check
#include <vector>
using namespace std;

struct DirichletConvolutionTools {
    static vector<long long> convolution(
        const vector<long long>& f,
        const vector<long long>& g,
        int limit
    ) {
        vector<long long> h(limit + 1, 0);
        for (int d = 1; d <= limit; ++d) {
            if (f[d] == 0) {
                continue;
            }
            for (int multiple = d; multiple <= limit; multiple += d) {
                h[multiple] += f[d] * g[multiple / d];
            }
        }
        return h;
    }

    static vector<long long> divisorZeta(const vector<long long>& f, int limit) {
        vector<long long> result(limit + 1, 0);
        for (int d = 1; d <= limit; ++d) {
            for (int multiple = d; multiple <= limit; multiple += d) {
                result[multiple] += f[d];
            }
        }
        return result;
    }

    static vector<long long> mobiusInvert(
        const vector<long long>& divisorSum,
        const vector<int>& mu,
        int limit
    ) {
        vector<long long> result(limit + 1, 0);
        for (int d = 1; d <= limit; ++d) {
            if (mu[d] == 0) {
                continue;
            }
            for (int multiple = d; multiple <= limit; multiple += d) {
                result[multiple] += 1LL * mu[d] * divisorSum[multiple / d];
            }
        }
        return result;
    }
};
```

값이 커지는 문제에서는 모듈러 연산을 넣습니다. `long long`으로 충분한지 먼저 범위를 계산합니다.

## 5. Multiplicative Function

함수 `f`가 `gcd(a, b)=1`일 때 `f(ab)=f(a)f(b)`를 만족하면 multiplicative function입니다. 두 multiplicative function의 Dirichlet convolution도 multiplicative입니다.

그래서 많은 공식은 prime power에서만 확인하면 됩니다.

```text
tau(p^k) = k + 1
sigma(p^k) = 1 + p + ... + p^k
phi(p^k) = p^k - p^{k-1}
```

입력 범위가 크고 query가 많으면 linear sieve로 multiplicative function 값을 한 번에 계산합니다.

## 6. gcd 합으로 바꾸기

`gcd(a, b)`가 들어간 합은 `g = gcd(a, b)`로 묶습니다.

```text
sum F(gcd(a,b))
= sum_g F(g) * count pairs with gcd exactly g
```

`gcd exactly g`는 Mobius inversion으로 계산하거나, `g`의 배수들끼리 만든 pair에서 더 큰 gcd의 기여를 빼는 방식으로 구합니다.

## 7. Subset Transform과의 유사성

Dirichlet convolution은 divisor lattice 위 convolution입니다. subset zeta transform에서 `A subset B` 관계를 쓰듯, 여기서는 `d | n` 관계를 씁니다.

| 구조 | 포함 관계 | 역원 |
| --- | --- | --- |
| subset lattice | `S subset T` | inclusion-exclusion |
| divisor lattice | `d | n` | Mobius function |

이 유사성을 알면 약수 DP를 더 체계적으로 설계할 수 있습니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| 모든 약수 합 zeta | `O(N log N)` |
| 직접 convolution | `O(N log N)` |
| Mobius inversion | `O(N log N)` |
| linear sieve로 기본 함수 계산 | `O(N)` |

`N`이 크고 실제 값 개수가 적으면 모든 범위를 훑는 대신 각 수의 약수만 열거하는 sparse 접근이 낫습니다.

## 9. 자주 하는 실수

1. convolution의 `g(n/d)`를 `g(d)`로 잘못 쓴다.
2. `mu * 1 = epsilon` 관계에서 `epsilon`과 상수 1 함수를 혼동한다.
3. multiplicative와 completely multiplicative를 섞는다.
4. ordered pair와 unordered pair 보정을 빠뜨린다.
5. 값 범위가 큰데 `O(maxA log maxA)` 배열을 무리하게 잡는다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: Dirichlet convolution `/practice/...` 문제 필요 | 약수 합 함수 계산 | divisor zeta |
| 표준 | TODO: multiplicative function `/practice/...` 문제 필요 | prime power 공식 | linear sieve |
| 응용 | TODO: gcd summatory function `/practice/...` 문제 필요 | gcd별 pair count | Mobius inverse |
| 함정 | TODO: sparse divisor transform `/practice/...` 문제 필요 | 값 범위와 개수 구분 | coordinate values |
