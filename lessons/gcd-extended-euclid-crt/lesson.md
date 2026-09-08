# 정수론 심화: GCD, Extended Euclid, CRT, Sieve

정수론 문제는 나눗셈, 나머지, 약수, 소수, 합동식을 정확히 다루는 문제입니다. 모듈러 연산을 익힌 뒤에는 `gcd`, 확장 유클리드 알고리즘, CRT, 소수 전처리로 자연스럽게 확장됩니다.

## GCD와 유클리드 알고리즘

`gcd(a, b)`는 `a`와 `b`를 모두 나누는 가장 큰 양의 정수입니다. 유클리드 알고리즘은 아래 성질을 이용합니다.

```text
gcd(a, b) = gcd(b, a mod b)
```

```cpp compile-check
long long gcdLong(long long a, long long b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b != 0) {
        long long r = a % b;
        a = b;
        b = r;
    }
    return a;
}
```

두 수가 서로소라는 말은 `gcd(a, b) == 1`이라는 뜻입니다. 모듈러 역원, CRT, 분수 약분, 주기 계산에서 자주 등장합니다.

## Extended Euclid

확장 유클리드 알고리즘은 `gcd(a, b)`뿐 아니라 아래 식을 만족하는 `x`, `y`도 구합니다.

```text
a*x + b*y = gcd(a, b)
```

```cpp compile-check
struct EGResult {
    long long gcd;
    long long x;
    long long y;
};

EGResult extendedGcd(long long a, long long b) {
    if (b == 0) {
        return {a, 1, 0};
    }
    EGResult next = extendedGcd(b, a % b);
    long long x = next.y;
    long long y = next.x - (a / b) * next.y;
    return {next.gcd, x, y};
}
```

`a`와 `mod`가 서로소이면 `a*x + mod*y = 1`입니다. 따라서 `a*x = 1 mod mod`가 되어 `x`가 `a`의 모듈러 역원입니다.

## 일반 mod에서 역원 구하기

Fermat 역원은 mod가 소수일 때만 바로 쓸 수 있습니다. mod가 합성수일 수 있으면 `gcd(a, mod) == 1`인지 확인해야 합니다.

```cpp compile-check
struct EGResult {
    long long gcd;
    long long x;
    long long y;
};

EGResult extendedGcd(long long a, long long b) {
    if (b == 0) return {a, 1, 0};
    EGResult next = extendedGcd(b, a % b);
    return {next.gcd, next.y, next.x - (a / b) * next.y};
}

long long normalize(long long x, long long mod) {
    x %= mod;
    if (x < 0) x += mod;
    return x;
}

long long inverseIfExists(long long a, long long mod) {
    EGResult result = extendedGcd(a, mod);
    if (result.gcd != 1) {
        return -1;
    }
    return normalize(result.x, mod);
}
```

역원이 없을 수 있다는 점이 중요합니다. `a`와 `mod`가 서로소가 아니면 나눗셈을 역원 곱셈으로 바꿀 수 없습니다.

## CRT

CRT(Chinese Remainder Theorem)는 여러 합동식을 하나로 합치는 도구입니다.

```text
x = r1 mod m1
x = r2 mod m2
```

`m1`, `m2`가 서로소라면 항상 `m1*m2`를 mod로 하는 해가 하나 존재합니다. 서로소가 아니어도 `r1`과 `r2`가 `gcd(m1, m2)` 기준으로 모순되지 않으면 해가 존재합니다.

```cpp compile-check
struct EGResult {
    long long gcd;
    long long x;
    long long y;
};

EGResult extendedGcd(long long a, long long b) {
    if (b == 0) return {a, 1, 0};
    EGResult next = extendedGcd(b, a % b);
    return {next.gcd, next.y, next.x - (a / b) * next.y};
}

long long normalize(long long x, long long mod) {
    x %= mod;
    if (x < 0) x += mod;
    return x;
}

struct CRTResult {
    long long remainder;
    long long modulus;
    bool exists;
};

CRTResult mergeCRT(long long r1, long long m1, long long r2, long long m2) {
    EGResult eg = extendedGcd(m1, m2);
    long long g = eg.gcd;
    long long diff = r2 - r1;
    if (diff % g != 0) {
        return {0, 0, false};
    }

    long long m2Reduced = m2 / g;
    long long t = normalize((diff / g) * eg.x, m2Reduced);
    long long lcm = m1 / g * m2;
    long long remainder = normalize(r1 + m1 * t, lcm);
    return {remainder, lcm, true};
}
```

곱셈이 `long long` 범위를 넘을 수 있는 입력이면 `__int128`이나 overflow-safe multiplication이 필요합니다. 레슨의 기본 구현은 `m1 / g * m2`가 `long long` 안에 들어온다는 조건을 전제로 합니다.

## Sieve와 최소 소인수

많은 수에 대해 소수 여부나 소인수분해가 필요하면 매번 나눠 보지 않고 전처리합니다.

```cpp compile-check
#include <vector>
using namespace std;

vector<int> buildSmallestPrimeFactor(int n) {
    vector<int> spf(n + 1, 0);
    for (int i = 2; i <= n; ++i) {
        if (spf[i] != 0) {
            continue;
        }
        spf[i] = i;
        if (1LL * i * i > n) {
            continue;
        }
        for (long long j = 1LL * i * i; j <= n; j += i) {
            if (spf[(int)j] == 0) {
                spf[(int)j] = i;
            }
        }
    }
    return spf;
}

vector<pair<int, int>> factorize(int x, const vector<int>& spf) {
    vector<pair<int, int>> result;
    while (x > 1) {
        int p = spf[x];
        int count = 0;
        while (x % p == 0) {
            x /= p;
            ++count;
        }
        result.push_back({p, count});
    }
    return result;
}
```

`spf[x]`는 `x`의 가장 작은 소인수입니다. 이를 이용하면 소인수분해를 빠르게 반복할 수 있습니다.

## 조합론과 연결

정수론 심화는 조합론과 자주 연결됩니다.

| 질문 | 필요한 도구 |
| --- | --- |
| `nCr mod prime` | factorial, inverse factorial, Fermat inverse |
| `nCr mod composite` | 소인수 지수 관리, CRT |
| 나눗셈이 포함된 식 | 역원 존재 조건 |
| 반복되는 약수/배수 질의 | sieve, divisor enumeration |

mod가 소수가 아니면 "나누기"가 바로 되지 않는다는 점을 항상 먼저 확인합니다.

## 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 합성수 mod에서 Fermat 역원 사용 | 역원 오답 | mod가 소수인지 확인 |
| `gcd(a, mod) != 1`인데 역원 계산 | 존재하지 않는 나눗셈 | extended gcd로 조건 확인 |
| CRT에서 나머지 모순을 확인하지 않음 | 존재하지 않는 해 출력 | `(r2-r1) % gcd == 0` 검사 |
| lcm 계산 overflow | 음수/잘못된 mod | `m1 / g * m2` 범위 확인 |
| sieve에서 `i*i`를 int로 계산 | overflow | `1LL * i * i` |
| 음수 나머지를 방치 | 출력 형식 오답 | normalize 사용 |
