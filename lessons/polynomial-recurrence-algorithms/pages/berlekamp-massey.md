# Berlekamp-Massey

Berlekamp-Massey는 field 위 수열의 앞 항들에서 가장 짧은 선형 점화식을 찾는 알고리즘입니다. Recurrence Guessing이 "어떻게 후보를 믿을 것인가"를 다룬다면, Berlekamp-Massey는 그 후보 계수를 `O(T^2)`로 구하는 표준 도구입니다.

이 레슨은 Recurrence Guessing, Linear Recurrence와 Kitamasa 이후에 보는 선형 점화식 추정 레슨입니다.

1. discrepancy로 현재 recurrence가 깨지는 위치를 찾는다.
2. 마지막으로 크게 고친 recurrence를 이용해 보정한다.
3. 얻은 coeff를 Kitamasa나 Bostan-Mori로 연결한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: modular inverse, linear recurrence, recurrence guessing
- 함께 보면 좋은 레슨: Linear Recurrence와 Kitamasa, Bostan-Mori, Linear Recurrence Applications
- 다음에 볼 레슨: recurrence applications, black-box linear algebra, rational generating function

## 1. 문제 신호

| 문제 표현 | Berlekamp-Massey 관점 |
| --- | --- |
| 수열 앞 항만 많이 얻을 수 있음 | 최소 recurrence 추정 |
| mod prime으로 답을 요구 | field inverse 사용 가능 |
| n번째 항이 매우 큼 | BM + Kitamasa |
| recurrence 차수를 모름 | minimal linear recurrence |
| graph walk count를 sparse하게 생성 | black-box recurrence |

BM은 field 위 알고리즘입니다. `mod`가 소수가 아니면 역원이 항상 존재하지 않으므로 그대로 쓰면 안 됩니다.

## 2. Discrepancy

현재 recurrence가 아래라고 합시다.

```text
s[n] = c0*s[n-1] + c1*s[n-2] + ... + cL-1*s[n-L]
```

새 항 `s[n]`에 대해 예측값이 틀리면 discrepancy가 생깁니다.

```text
d = s[n] - predicted
```

BM은 이전에 잘 작동하던 recurrence를 적절히 shift해서 이 discrepancy를 지우는 방식으로 계수를 갱신합니다.

## 3. 구현

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

## 4. 작은 예시

Fibonacci 수열을 넣으면 BM은 차수 2 recurrence를 찾습니다.

```text
sequence = 0, 1, 1, 2, 3, 5, 8, 13
coeff = [1, 1]
F[n] = 1*F[n-1] + 1*F[n-2]
```

초기항은 `sequence[0..L-1]`입니다. `n < L`이면 초기항을 그대로 반환하고, 그 이후는 Kitamasa로 계산합니다.

## 5. 왜 `2L`개 항이 필요한가

차수 `L` recurrence는 `L`개 계수를 가집니다. 하지만 최소 차수 자체를 모르기 때문에 BM은 항을 보며 차수를 늘립니다.

```text
앞 2L개 항을 보면 L차 recurrence가 계속 맞는지 확인할 수 있다.
```

항이 부족하면 더 짧은 가짜 recurrence가 나올 수 있습니다. BM 결과도 holdout 항으로 다시 검증하는 편이 안전합니다.

## 6. Kitamasa와 연결

BM이 반환한 coeff는 바로 nth term 계산에 넣을 수 있습니다.

```text
terms -> BM -> coeff
answer = nthByRecurrence(terms[0..L-1], coeff, n)
```

이때 BM에 넣은 수열과 nth 함수의 index 기준이 같아야 합니다. `a_1`부터 생성한 수열이면 `n`도 1-based로 맞추거나 앞에 dummy `a_0`을 넣습니다.

## 7. Mod 조건

BM은 discrepancy를 이전 discrepancy로 나누어 보정합니다.

```text
factor = d / old_d
```

따라서 모든 nonzero 원소가 역원을 가져야 합니다. prime modulo에서는 Fermat inverse를 쓸 수 있지만, 합성수 modulo에서는 다른 처리가 필요합니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| T개 항에서 BM | `O(T^2)` |
| 차수 L recurrence 검증 | `O(TL)` |
| Kitamasa nth term | `O(L^2 log N)` |

`T`는 보통 찾으려는 차수의 두 배 이상으로 잡습니다. 차수가 너무 크면 항 생성과 BM 둘 다 병목이 됩니다.

## 9. 자주 하는 실수

1. 합성수 mod에서 Fermat inverse를 쓴다.
2. 반환 coeff 부호 convention을 nth 함수와 반대로 쓴다.
3. BM에 넣은 항이 부족한데 결과를 확정한다.
4. noisy sequence나 floating point sequence에 BM을 적용한다.
5. 초기항 index를 `a_0` 기준으로 맞추지 않는다.

## 10. 문제를 볼 때 체크할 조건

- mod가 prime인가?
- 앞 항을 최소 차수의 두 배 이상 만들 수 있는가?
- 수열이 homogeneous linear recurrence를 따른다는 근거가 있는가?
- BM 결과를 holdout 항으로 검증했는가?
- nth term 함수와 coeff convention이 일치하는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: Berlekamp-Massey basics `/practice/...` 문제 필요 | 최소 recurrence 찾기 | discrepancy |
| 표준 | TODO: BM + Kitamasa `/practice/...` 문제 필요 | 큰 n번째 항 계산 | nth term |
| 응용 | TODO: graph walk BM `/practice/...` 문제 필요 | sparse 항 생성 | Cayley-Hamilton |
| 함정 | TODO: composite mod recurrence `/practice/...` 문제 필요 | field 조건 확인 | modular inverse |
