# Berlekamp–Massey: 점화식 추정과 검증

앞 항을 정확히 생성할 수 있는 수열에서 선형 점화식을 찾고 먼 항을 계산합니다. Berlekamp–Massey(BM)는 field 위의 계수를 구하는 알고리즘이며, 풀이에 쓰려면 수열 전체가 고정 선형 점화식을 따른다는 근거와 차수 상한이 필요합니다. 소수가 아닌 modulo에서는 역원이 없을 수 있어 아래 구현을 그대로 사용할 수 없습니다.

## Affine 전이 처리

상수항이 있으면 상태에 `1`을 추가합니다.

```text
a[n] = 3*a[n-1] + 7

state[n] = [a[n], 1]
state[n] = [[3, 7], [0, 1]] * state[n-1]
```

고정 affine 전이는 상수 상태를 추가하면 고정 선형 전이가 됩니다. 따라서 원 수열을 BM에 넣어도 되며 차수 상한이 하나 커질 수 있습니다.

## Graph Walk와 Black-box 항 생성

정점 수 `S`인 graph walk count는 adjacency matrix의 거듭제곱 entry입니다. Cayley-Hamilton 정리에 의해 차수 `S` 이하 recurrence가 존재합니다.

```text
a[n] = number of walks of length n from s to t
```

`S`가 2000이면 matrix exponentiation은 부담스럽지만, sparse graph에서 앞 `2S`개 항을 `O(S + E)`씩 만들 수 있다면 recurrence guessing이 후보가 됩니다.

## 몇 항이 필요한가

전체 수열이 차수 K 이하의 고정 선형 점화식을 따른다는 상한을 증명했다면 앞 2K항으로 BM 복원이 가능합니다. 상한이 없는 임의 수열에서는 항을 더 검사해도 미래를 보장하지 못합니다.

| 목적 | 필요한 항 |
| --- | ---: |
| K차 후보를 맞춤 | 최소 `2K` |
| 후보 검증 | 별도 holdout은 오류 탐지용이며 유한 개 검사만으로 무한 수열을 증명하지 못함 |
| K를 모름 | 가능한 상한보다 넉넉히 |
| noisy sequence | 이 방법 자체가 부적절 |

처음 `2K`개만 맞는 recurrence는 얼마든지 만들 수 있습니다. 뒤 항을 일부러 남겨 두고 검증해야 합니다.

## 상수항이 있는 수열부터 살펴보기

```text
a = 2, 5, 11, 23, 47, 95, ...

차분을 보면 3, 6, 12, 24, 48
후보: a[n] = 2*a[n-1] + 1

선형 recurrence 표준형으로 쓰면
a[n] - 2*a[n-1] = 1
상수항이 있으므로 상태에 1을 추가해야 한다.
```

이 수열 자체도 a[n]=3a[n-1]-2a[n-2]라는 homogeneous 점화식을 따르므로 BM에 직접 넣을 수 있습니다. b[n]=a[n]+1로 바꾸면 차수 1로 줄어듭니다.

## Discrepancy

현재 recurrence가 아래라고 합시다.

```text
s[n] = c0*s[n-1] + c1*s[n-2] + ... + cL-1*s[n-L]
```

새 항 `s[n]`에 대해 예측값이 틀리면 discrepancy가 생깁니다.

```text
d = s[n] - predicted
```

BM은 이전에 잘 작동하던 recurrence를 적절히 shift해서 이 discrepancy를 지우는 방식으로 계수를 갱신합니다.

## 구현

아래 구현은 `coeff[i]`가 `s[n-i-1]`에 곱해지는 형태로 반환합니다.

```cpp compile-check
#include <vector>
using namespace std;

const long long MOD_BM = 998244353;

long long modPowBm(long long base, long long exponent) {
    long long result = 1;
    base %= MOD_BM;
    while (exponent > 0) {
        if (exponent & 1LL) {
            result = result * base % MOD_BM;
        }
        base = base * base % MOD_BM;
        exponent >>= 1LL;
    }
    return result;
}

long long normalizeBm(long long value) {
    value %= MOD_BM;
    if (value < 0) {
        value += MOD_BM;
    }
    return value;
}

vector<long long> berlekampMassey(const vector<long long>& sequence) {
    vector<long long> current(1, 1);
    vector<long long> previous(1, 1);
    int length = 0;
    int shift = 1;
    long long lastDiscrepancy = 1;

    for (int n = 0; n < (int)sequence.size(); ++n) {
        long long discrepancy = normalizeBm(sequence[n]);
        for (int i = 1; i <= length; ++i) {
            discrepancy += current[i] * normalizeBm(sequence[n - i]);
            discrepancy %= MOD_BM;
        }

        if (discrepancy == 0) {
            ++shift;
            continue;
        }

        vector<long long> saved = current;
        long long factor = discrepancy * modPowBm(lastDiscrepancy, MOD_BM - 2) % MOD_BM;
        if ((int)current.size() < (int)previous.size() + shift) {
            current.resize(previous.size() + shift, 0);
        }

        for (int i = 0; i < (int)previous.size(); ++i) {
            current[i + shift] = normalizeBm(current[i + shift] - factor * previous[i]);
        }

        if (2 * length <= n) {
            length = n + 1 - length;
            previous = saved;
            lastDiscrepancy = discrepancy;
            shift = 1;
        } else {
            ++shift;
        }
    }

    vector<long long> coeff(length, 0);
    for (int i = 1; i <= length; ++i) {
        coeff[i - 1] = normalizeBm(-current[i]);
    }
    return coeff;
}
```

`current`는 characteristic polynomial 쪽 표현이라 부호가 반대입니다. 반환 직전에 `-current[i]`로 바꾸는 convention을 고정합니다.

## 작은 예시

Fibonacci 수열을 넣으면 BM은 차수 2 recurrence를 찾습니다.

```text
sequence = 0, 1, 1, 2, 3, 5, 8, 13
coeff = [1, 1]
F[n] = 1*F[n-1] + 1*F[n-2]
```

초기항은 `sequence[0..L-1]`입니다. `n < L`이면 초기항을 그대로 반환하고, 그 이후는 Kitamasa로 계산합니다.

## Holdout 검증

아래 코드는 이미 찾은 recurrence가 주어진 항들을 모두 설명하는지 검증합니다. `coeff[i]`는 `a[n-i-1]`에 곱해지는 계수입니다.

```cpp compile-check
#include <vector>
using namespace std;

const long long MOD_GUESS = 998244353;

long long normalizeGuess(long long value) {
    value %= MOD_GUESS;
    if (value < 0) {
        value += MOD_GUESS;
    }
    return value;
}

bool verifyRecurrenceGuess(
    const vector<long long>& terms,
    const vector<long long>& coeff
) {
    int k = (int)coeff.size();
    if ((int)terms.size() <= k) {
        return false;
    }

    for (int n = k; n < (int)terms.size(); ++n) {
        long long predicted = 0;
        for (int i = 0; i < k; ++i) {
            predicted += normalizeGuess(coeff[i]) * normalizeGuess(terms[n - i - 1]);
            predicted %= MOD_GUESS;
        }
        if (predicted != normalizeGuess(terms[n])) {
            return false;
        }
    }
    return true;
}
```

검증은 recurrence 후보를 찾는 코드와 분리하는 편이 좋습니다. 그래야 BM 구현 실수인지 모델링 실수인지 나눠 볼 수 있습니다.

## Kitamasa와 연결

BM이 반환한 coeff는 바로 nth term 계산에 넣을 수 있습니다.

```text
terms -> BM -> coeff
answer = nthByRecurrence(terms[0..L-1], coeff, n)
```

a_1부터 생성했다면 b_i=a_{i+1}로 정의하고 원래 a_N은 b의 N-1번째를 구합니다. 임의 dummy a_0을 넣으면 점화식이 깨질 수 있습니다. BM 결과가 빈 계수(L=0)이면 관측 수열은 전부 0입니다. 점화식 상한이 보장되는 경우 결과를 0으로 처리하고, K>=1을 요구하는 Kitamasa에 빈 벡터를 넘기지 않습니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| T개 항에서 BM | `O(T^2)` |
| 차수 L recurrence 검증 | `O(TL)` |
| Kitamasa nth term | `O(L^2 log N)` |

`T`는 보통 찾으려는 차수의 두 배 이상으로 잡습니다. 차수가 너무 크면 항 생성과 BM 둘 다 병목이 됩니다.
