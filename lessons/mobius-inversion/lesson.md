# Mobius Inversion

Mobius Inversion은 divisor lattice 위에서 "약수들의 합"으로 정의된 값을 원래 함수로 되돌리는 포함-배제 도구입니다. gcd 조건, 서로소 pair count, divisor multiple count처럼 수의 약수 관계가 핵심인 문제에서 자주 등장합니다.

이 레슨은 정수론 심화와 조합론 이후에 보는 수학 심화입니다.

1. `F(n) = sum_{d|n} f(d)` 형태를 찾는다.
2. Mobius function `mu`로 `f(n) = sum_{d|n} mu(d) F(n/d)`를 복원한다.
3. gcd 조건을 divisor multiple count로 바꿔 빠르게 센다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: gcd, prime factorization, inclusion-exclusion, sieve
- 함께 보면 좋은 레슨: 정수론 심화, 조합론, XOR Linear Basis
- 다음에 볼 레슨: Dirichlet convolution, multiplicative function, divisor transform

## 1. 문제 신호

| 문제 표현 | Mobius Inversion 관점 |
| --- | --- |
| `gcd(a, b) = 1`인 pair 수 | `sum mu(d) * countMultiple(d)^2` |
| gcd가 정확히 `g` | 모든 수를 `g`로 나누고 서로소 조건 |
| 약수의 합으로 정의된 값 복원 | divisor inversion |
| multiple count가 빠르게 계산됨 | sieve over multiples |
| 포함-배제가 prime subset으로 커짐 | Mobius function으로 압축 |

Mobius inversion은 "약수 관계의 포함-배제"입니다. 상태가 divisor/multiple 축으로 정리되지 않으면 억지로 쓰기 어렵습니다.

## 2. Mobius Function

`mu(n)`은 아래처럼 정의됩니다.

| 조건 | 값 |
| --- | ---: |
| `n = 1` | `1` |
| 어떤 prime square가 `n`을 나눔 | `0` |
| 서로 다른 prime `k`개의 곱 | `(-1)^k` |

예를 들어 `12 = 2^2 * 3`은 square factor가 있으므로 `mu(12)=0`, `30 = 2 * 3 * 5`는 서로 다른 prime 3개라서 `mu(30)=-1`입니다.

## 3. Inversion 공식

약수 합 관계가 아래와 같다고 하겠습니다.

```text
F(n) = sum_{d | n} f(d)
```

그러면 원래 함수는 Mobius function으로 복원됩니다.

```text
f(n) = sum_{d | n} mu(d) * F(n / d)
```

multiple 방향으로 쓰면 아래 형태도 자주 씁니다.

```text
G(d) = sum_{d | x} f(x)
f(d) = sum_{d | x} mu(x / d) * G(x)
```

## 4. Linear Sieve 구현

아래 구현은 `mu[1..N]`을 `O(N)`에 구합니다.

```cpp compile-check
#include <vector>
using namespace std;

struct MobiusSieve {
    vector<int> primes;
    vector<int> mu;
    vector<int> isComposite;

    explicit MobiusSieve(int limit) : mu(limit + 1, 0), isComposite(limit + 1, 0) {
        mu[1] = 1;
        for (int i = 2; i <= limit; ++i) {
            if (!isComposite[i]) {
                primes.push_back(i);
                mu[i] = -1;
            }
            for (int prime : primes) {
                long long value = 1LL * i * prime;
                if (value > limit) {
                    break;
                }
                isComposite[(int)value] = 1;
                if (i % prime == 0) {
                    mu[(int)value] = 0;
                    break;
                }
                mu[(int)value] = -mu[i];
            }
        }
    }

    long long countOrderedCoprimePairs(const vector<int>& frequency) const {
        int limit = (int)frequency.size() - 1;
        vector<long long> multipleCount(limit + 1, 0);
        for (int d = 1; d <= limit; ++d) {
            for (int x = d; x <= limit; x += d) {
                multipleCount[d] += frequency[x];
            }
        }

        long long answer = 0;
        for (int d = 1; d <= limit; ++d) {
            answer += 1LL * mu[d] * multipleCount[d] * multipleCount[d];
        }
        return answer;
    }
};
```

위 `countOrderedCoprimePairs`는 순서 있는 pair `(a, b)`를 셉니다. 순서 없는 pair나 `a != b` 조건이 있으면 마지막 보정이 필요합니다.

## 5. gcd가 정확히 g인 Pair

`gcd(a, b) = g`는 `a = g*x`, `b = g*y`, `gcd(x, y)=1`로 바꿉니다.

```text
count_g = sum_{d>=1} mu(d) * countMultiple(g*d)^2
```

여러 `g`에 대해 답해야 한다면 `d`와 `g*d` 반복 순서를 잘 잡아 전체 `O(N log N)`에 처리합니다.

## 6. Divisor Transform 관점

Mobius inversion은 Dirichlet convolution으로 보면 더 간단합니다.

```text
F = f * 1
f = F * mu
```

여기서 `1(n)=1`인 함수와 `mu`는 convolution inverse 관계입니다. 이 관점은 multiplicative function, divisor zeta transform, subset zeta transform으로 이어집니다.

## 7. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| linear sieve로 `mu` 계산 | `O(N)` |
| multiple count | `O(N log N)` |
| 모든 gcd 값 pair count | `O(N log N)` |
| 단일 query after preprocessing | 문제 구조에 따라 `O(1)` 또는 `O(log N)` |

입력 값의 최댓값 `A`가 크고 원소 수 `N`이 작으면 좌표 압축이나 divisor enumeration이 더 나을 수 있습니다.

## 8. 자주 하는 실수

1. `mu[1] = 1` 초기화를 빠뜨린다.
2. square factor가 있는 수의 `mu`를 0으로 만들지 않는다.
3. ordered pair와 unordered pair를 혼동한다.
4. `gcd = g` 조건에서 `g`로 나눈 뒤의 서로소 조건을 빼먹는다.
5. 값의 최댓값이 너무 큰데 배열 sieve를 무리하게 잡는다.

## 9. 문제를 볼 때 체크할 조건

- 조건이 gcd, divisor, multiple 관계로 표현되는가?
- "약수들의 합" 또는 "배수들의 합" 형태가 보이는가?
- 필요한 pair가 ordered인지 unordered인지 명확한가?
- 모든 값의 최댓값 기준 sieve가 가능한가?
- prime subset 포함-배제를 `mu` 합으로 압축할 수 있는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: coprime pair count `/practice/...` 문제 필요 | `sum mu(d) cnt[d]^2` 적용 | gcd equals one |
| 표준 | TODO: exact gcd pair `/practice/...` 문제 필요 | `g`로 나눈 뒤 inversion | divisor multiples |
| 응용 | TODO: divisor transform `/practice/...` 문제 필요 | 약수 합 관계 복원 | Mobius inversion |
| 함정 | TODO: unordered pair 보정 `/practice/...` 문제 필요 | diagonal/order 처리 | pair counting |
