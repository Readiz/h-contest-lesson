# 조합론: nCr, 포함-배제, Lucas

조합론 문제는 "몇 가지 방법이 있는가"를 세는 문제입니다. 가장 자주 나오는 도구는 `nCr`이고, 조건을 만족하지 않는 경우를 빼는 포함-배제, 큰 `n`을 작은 자리로 쪼개는 Lucas 정리까지 이어집니다.


factorial 방식은 소수 p에 대해 `0<=maxN<p`이며 질의 n은 전처리 범위 안이어야 합니다. Lucas는 자릿수 조합을 위해 p보다 작은 범위를 준비하므로 큰 p 전체를 전처리할 수는 없습니다. 포함·배제의 상자는 서로 구분되는 상자입니다.

## `nCr`의 의미

`nCr`은 서로 다른 `n`개 중에서 순서 없이 `r`개를 고르는 경우의 수입니다.

```text
nCr = n! / (r! * (n-r)!)
```

순서가 중요하면 permutation이고, 순서가 중요하지 않으면 combination입니다. 문제에서 "고른다", "집합", "순서는 상관없다" 같은 표현이 나오면 조합을 의심합니다.

## Factorial 전처리

`MOD`가 소수이고 `n`의 최대값이 적당히 작으면 factorial과 inverse factorial을 미리 만들면 됩니다.

```cpp compile-check
#include <vector>
using namespace std;

long long modPow(long long base, long long exp, long long mod) {
    long long result = 1 % mod;
    base %= mod;
    while (exp > 0) {
        if (exp & 1LL) {
            result = result * base % mod;
        }
        base = base * base % mod;
        exp >>= 1LL;
    }
    return result;
}

struct Combination {
    long long mod;
    vector<long long> fact;
    vector<long long> invFact;

    Combination(int maxN, long long mod) : mod(mod), fact(maxN + 1), invFact(maxN + 1) {
        fact[0] = 1;
        for (int i = 1; i <= maxN; ++i) {
            fact[i] = fact[i - 1] * i % mod;
        }

        invFact[maxN] = modPow(fact[maxN], mod - 2, mod);
        for (int i = maxN; i >= 1; --i) {
            invFact[i - 1] = invFact[i] * i % mod;
        }
    }

    long long nCr(int n, int r) const {
        if (r < 0 || r > n) {
            return 0;
        }
        return fact[n] * invFact[r] % mod * invFact[n - r] % mod;
    }
};

long long lucas(long long n, long long r, const Combination& small) {
    if (n < 0 || r < 0 || r > n) return 0;
    long long answer = 1, p = small.mod;
    while (n || r) {
        answer = answer * small.nCr(n % p, r % p) % p;
        n /= p; r /= p;
    }
    return answer;
}
```

전처리는 `O(N + log MOD)`, 각 질의는 `O(1)`입니다. `MOD`가 소수일 때 Fermat 역원을 쓴다는 조건을 잊으면 안 됩니다.

## 언제 factorial 방식이 안 되는가

factorial 방식은 강력하지만 항상 쓸 수는 없습니다.

| 상황 | 문제점 | 대안 |
| --- | --- | --- |
| `MOD`가 소수가 아니다 | Fermat 역원이 틀릴 수 있음 | extended gcd, prime factor 분해 |
| `n >= MOD`이고 `MOD`가 소수 | `fact[n]`에 `MOD`가 곱해져 0 | Lucas 정리 |
| `n`이 `10^18`처럼 매우 큼 | factorial 배열 불가 | Lucas, 수식 변형 |
| 질의가 매우 적고 `r`이 작다 | 전처리가 과함 | 곱셈 `r`번 + 역원 |

문제에서 `MOD = 1,000,000,007`처럼 큰 소수가 주어지고 `n <= 1,000,000` 정도라면 factorial 방식이 표준입니다. `MOD`가 작거나 합성수이면 조건을 다시 봐야 합니다.

## 포함-배제

포함-배제는 "전체에서 나쁜 경우를 빼고, 두 번 빠진 경우를 다시 더하는" 방식입니다.

두 조건 `A`, `B` 중 하나라도 만족하는 경우의 수는 아래와 같습니다.

```text
|A union B| = |A| + |B| - |A intersection B|
```

조건이 여러 개면 부호가 번갈아 나옵니다.

```text
좋은 경우 = 전체
          - 조건 1개를 위반하는 경우
          + 조건 2개를 동시에 위반하는 경우
          - 조건 3개를 동시에 위반하는 경우
          + ...
```

대표 예시는 "각 상자에 최소 1개씩 넣기"입니다. `n`개의 서로 다른 공을 `k`개의 상자에 넣는데 빈 상자가 없게 하려면, 전체 `k^n`에서 빈 상자가 있는 경우를 포함-배제로 뺍니다.

```text
answer = sum_{i=0..k} (-1)^i * C(k, i) * (k - i)^n
```

## 포함-배제 구현 습관

모듈러에서 빼기가 반복되므로 음수 정규화가 중요합니다.

각 항을 `[0,mod)`로 정규화한 뒤 더하거나 빼고 다시 정규화합니다. 위 구현의 곱셈은 `p<=2*10^9`를 전제로 합니다.

포함-배제 문제는 부호보다 "무엇을 위반한 것으로 고를지"가 더 중요합니다. 조건 집합을 고르고, 그 조건들이 동시에 위반될 때 남는 자유도를 계산하는 식으로 접근합니다.

## Lucas 정리

`MOD = p`가 소수이고 `n`, `r`이 매우 크며 `p`가 상대적으로 작을 때 Lucas 정리를 씁니다.

`n`과 `r`을 `p`진법으로 쪼갭니다.

```text
n = n0 + n1*p + n2*p^2 + ...
r = r0 + r1*p + r2*p^2 + ...

C(n, r) mod p = product C(ni, ri) mod p
```

각 자리의 `ri > ni`이면 그 자리 조합이 0이므로 전체도 0입니다.

위 `lucas(n,r,small)`에 `Combination small(p-1,p)`를 전달합니다.

이 구현은 `p` 크기만큼 배열을 만듭니다. `p`가 너무 크면 Lucas용 factorial 전처리 자체가 부담이므로 문제 제한을 먼저 봐야 합니다.

## 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| factorial/invFact 전처리 | `O(N + log MOD)` | `O(N)` |
| `nCr` 질의 | `O(1)` | 전처리 사용 |
| 포함-배제 `k`조건 전체 순회 | 보통 `O(2^k)` 또는 `O(k)` 공식화 | 문제별 |
| Lucas 전처리 | `O(p + log p)` | `O(p)` |
| Lucas 질의 | `O(log_p n)` | 전처리 사용 |

포함-배제는 조건 수가 크면 그대로 `2^k`를 돌 수 없습니다. 대칭성이 있으면 `C(k, i)`로 묶어 `O(k)` 공식으로 줄이는 것이 핵심입니다.
