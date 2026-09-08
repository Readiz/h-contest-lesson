# 모듈러 연산과 빠른 거듭제곱

모듈러 연산은 큰 수를 어떤 수 `MOD`로 나눈 나머지만 유지하는 방식입니다. 경우의 수, DP, 조합론 문제에서 답이 매우 커질 때 거의 항상 등장합니다.

## 선수 지식과 이어지는 레슨

- 선수 지식: 사칙연산, 반복문, 정수 overflow 감각
- 함께 보면 좋은 레슨: 동적 계획법, 위상 정렬과 DAG DP
- 다음에 볼 레슨: 조합론, 소수와 체, 문자열 해싱

## 왜 나머지로 답을 출력하는가

경로의 개수나 문자열의 경우의 수는 입력이 조금만 커져도 `long long` 범위를 넘습니다. 그래서 문제는 보통 "답을 `1,000,000,007`로 나눈 나머지를 출력하라"고 합니다.

나머지만 유지해도 덧셈, 뺄셈, 곱셈 결과의 나머지는 정확히 계산할 수 있습니다.

```text
(a + b) mod M = ((a mod M) + (b mod M)) mod M
(a * b) mod M = ((a mod M) * (b mod M)) mod M
```

## 덧셈, 뺄셈, 곱셈에서 mod 처리

가장 안전한 습관은 연산 직후 바로 `MOD`를 적용하는 것입니다.

```cpp
const long long MOD = 1000000007LL;

long long addMod(long long a, long long b) {
    return (a + b) % MOD;
}

long long mulMod(long long a, long long b) {
    return (a % MOD) * (b % MOD) % MOD;
}
```

`MOD`가 `1e9` 수준이면 두 값을 곱할 때 최대 `1e18` 근처까지 갈 수 있으므로 `int`가 아니라 `long long`을 씁니다.

## 음수 나머지 처리

C++에서 음수를 `%`로 나누면 결과가 음수일 수 있습니다.

```cpp
long long normalize(long long x, long long mod) {
    x %= mod;
    if (x < 0) x += mod;
    return x;
}
```

뺄셈이 들어가는 DP나 포함-배제에서는 항상 정규화합니다.

```cpp
ways = normalize(ways - badWays, MOD);
```

## 빠른 거듭제곱

`a^b mod MOD`를 `b`번 곱하면 너무 느립니다. 지수를 이진수로 쪼개면 `O(log b)`번 곱셈으로 계산할 수 있습니다.

```cpp
long long modPow(long long base, long long exp, long long mod) {
    long long result = 1 % mod;
    base %= mod;
    while (exp > 0) {
        if (exp & 1LL) result = result * base % mod;
        base = base * base % mod;
        exp >>= 1LL;
    }
    return result;
}
```

`exp`가 매우 크면 반복 횟수는 지수의 비트 수입니다. 예를 들어 `10^18`도 약 60번만 반복합니다.

## 모듈러 역원

나머지 연산에서 나눗셈은 조심해야 합니다. `a / b mod MOD`를 단순히 `a % MOD / b % MOD`로 계산할 수 없습니다.

대신 `b * inv(b) = 1 mod MOD`를 만족하는 `inv(b)`를 곱합니다. `MOD`가 소수이고 `b`가 `MOD`의 배수가 아니면 페르마 소정리로 역원을 구할 수 있습니다.

```cpp
long long modInversePrime(long long x, long long mod) {
    return modPow(x, mod - 2, mod);
}
```

## 소수 mod와 페르마 소정리

`MOD`가 소수일 때 `x^(MOD - 1) = 1 mod MOD`입니다. 그래서 `x^(MOD - 2)`가 `x`의 역원이 됩니다.

하지만 `MOD`가 소수가 아니면 이 방식은 일반적으로 틀립니다. 그때는 확장 유클리드 알고리즘으로 역원이 존재하는지 확인해야 합니다.

## 조합론으로 연결하기

`nCr mod MOD`를 많이 계산하려면 factorial과 inverse factorial을 전처리합니다.

```cpp
vector<long long> fact, invFact;

void buildFactorials(int n, long long mod) {
    fact.assign(n + 1, 1);
    invFact.assign(n + 1, 1);
    for (int i = 1; i <= n; i++) fact[i] = fact[i - 1] * i % mod;
    invFact[n] = modInversePrime(fact[n], mod);
    for (int i = n; i >= 1; i--) invFact[i - 1] = invFact[i] * i % mod;
}

long long comb(int n, int r, long long mod) {
    if (r < 0 || r > n) return 0;
    return fact[n] * invFact[r] % mod * invFact[n - r] % mod;
}
```

## 시간 복잡도

| 작업 | 시간 |
| --- | --- |
| 덧셈/뺄셈/곱셈 mod | `O(1)` |
| 빠른 거듭제곱 | `O(log exponent)` |
| 역원 1개 | `O(log MOD)` |
| factorial 전처리 | `O(n + log MOD)` |
| nCr 질의 | `O(1)` |

## 자주 하는 실수

| 실수 | 결과 | 점검 |
| --- | --- | --- |
| 뺄셈 후 음수 방치 | 음수 출력 | `normalize` 적용 |
| 나눗셈을 `/`로 처리 | 오답 | 역원 곱셈으로 바꾸기 |
| `int`로 곱셈 | overflow | 중간 계산은 `long long` |
| 합성수 mod에서 Fermat 사용 | 역원 오답 | `MOD`가 소수인지 확인 |
| DP 전이에 mod를 늦게 적용 | overflow | 전이마다 mod 적용 |

## 문제를 볼 때 체크할 조건

1. 답이 매우 커져서 mod 출력이 요구되는가?
2. `MOD`가 소수인지 명시되어 있는가?
3. 나눗셈이나 조합 계산이 필요한가?
4. 음수 항이 생기는 포함-배제나 차분이 있는가?
5. 곱셈 중간값이 `long long` 범위를 넘지 않는가?
