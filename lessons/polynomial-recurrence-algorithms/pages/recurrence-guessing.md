# Recurrence Guessing

Recurrence Guessing은 처음 몇 항만 만들어 낼 수 있을 때 "이 수열이 낮은 차수의 선형 점화식을 따르는가"를 실험적으로 확인하는 모델링 기법입니다. Berlekamp-Massey를 쓰기 전에, 어떤 항을 만들고 어떻게 검증할지 정하지 않으면 그럴듯한 잘못된 점화식을 얻기 쉽습니다.

이 레슨은 Linear Recurrence Applications 이후, Berlekamp-Massey를 구현하기 전에 보는 수학 모델링 레슨입니다.

1. 수열 항을 충분히 만들 수 있는지 확인한다.
2. 낮은 차수 recurrence 후보를 찾고 holdout 항으로 검증한다.
3. 추정 결과를 Kitamasa, Bostan-Mori, Matrix Exponentiation 중 하나로 연결한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: linear recurrence, modular arithmetic, matrix exponentiation
- 함께 보면 좋은 레슨: Linear Recurrence Applications, Linear Recurrence와 Kitamasa, Bostan-Mori
- 다음에 볼 레슨: Berlekamp-Massey, linear recurrence applications, sequence model validation

## 1. 문제 신호

| 문제 표현 | Recurrence Guessing 관점 |
| --- | --- |
| `n`은 매우 큰데 앞 항은 만들 수 있음 | 앞 항에서 recurrence 후보 찾기 |
| 상태 전이가 크지만 첫 `T`항 생성은 가능 | black-box sequence |
| 그래프 walk나 automaton count | Cayley-Hamilton으로 recurrence 존재 가능 |
| 공식은 모르지만 수열이 규칙적으로 보임 | conjecture + verification |
| mod prime 아래 답만 필요 | Berlekamp-Massey 후보 |

추정은 증명이 아닙니다. 대회 풀이에서는 recurrence가 존재하는 이유와 충분한 검증 항을 함께 설명해야 합니다.

## 2. 기본 절차

```text
1. a[0..T-1]을 정확히 만든다.
2. 차수 K 후보를 찾는다.
3. 앞 2K개로 recurrence를 맞춘다.
4. 나머지 항으로 검증한다.
5. 통과하면 nth term 알고리즘으로 넘긴다.
```

항 생성이 확률적이거나 floating point이면 이 흐름은 위험합니다. recurrence guessing은 보통 정수 또는 모듈러 field 위에서 다룹니다.

## 3. 몇 항이 필요한가

차수 `K`의 선형 recurrence를 찾으려면 최소한 `2K`개 항이 필요합니다. 하지만 실제로는 검증용 holdout이 더 필요합니다.

| 목적 | 필요한 항 |
| --- | ---: |
| K차 후보를 맞춤 | 최소 `2K` |
| 후보 검증 | `2K + 10` 이상 권장 |
| K를 모름 | 가능한 상한보다 넉넉히 |
| noisy sequence | 이 방법 자체가 부적절 |

처음 `2K`개만 맞는 recurrence는 얼마든지 만들 수 있습니다. 뒤 항을 일부러 남겨 두고 검증해야 합니다.

## 4. 작은 예시

```text
a = 2, 5, 11, 23, 47, 95, ...

차분을 보면 3, 6, 12, 24, 48
후보: a[n] = 2*a[n-1] + 1

선형 recurrence 표준형으로 쓰면
a[n] - 2*a[n-1] = 1
상수항이 있으므로 상태에 1을 추가해야 한다.
```

이 예시는 순수 homogeneous linear recurrence가 아닙니다. `b[n] = a[n] + 1`로 바꾸면 `b[n] = 2*b[n-1]`가 됩니다. 항이 맞아 보인다고 바로 BM에 넣기 전에 상수항, affine 전이, 주기성을 분리합니다.

## 5. Holdout 검증

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

## 6. Affine 전이 처리

상수항이 있으면 상태에 `1`을 추가합니다.

```text
a[n] = 3*a[n-1] + 7

state[n] = [a[n], 1]
state[n] = [[3, 7], [0, 1]] * state[n-1]
```

BM은 homogeneous recurrence를 찾으므로 affine 구조를 그대로 넣으면 더 높은 차수로 보이거나 검증에서 흔들릴 수 있습니다.

## 7. Graph Walk와 Black-box 항 생성

정점 수 `S`인 graph walk count는 adjacency matrix의 거듭제곱 entry입니다. Cayley-Hamilton 정리에 의해 차수 `S` 이하 recurrence가 존재합니다.

```text
a[n] = number of walks of length n from s to t
```

`S`가 2000이면 matrix exponentiation은 부담스럽지만, sparse graph에서 앞 `2S`개 항을 `O(S + E)`씩 만들 수 있다면 recurrence guessing이 후보가 됩니다.

## 8. 검증해야 하는 반례

| 겉보기 패턴 | 실제 위험 |
| --- | --- |
| 앞 항이 Fibonacci처럼 보임 | 뒤에서 다른 전이로 바뀔 수 있음 |
| mod에서 맞음 | 다른 mod나 정수에서는 다를 수 있음 |
| 작은 K로 맞음 | 생성한 항 수가 너무 적을 수 있음 |
| recurrence는 맞음 | 초기 index가 `a_0`인지 `a_1`인지 틀릴 수 있음 |
| 항 생성이 빠름 | n번째 항 계산 방식 연결이 빠르지 않을 수 있음 |

특히 mod prime 하나에서 맞은 recurrence는 "그 mod에서의 답"만 보장합니다. 문제의 답도 같은 mod면 충분하지만, 정수 답 자체를 요구하면 더 조심해야 합니다.

## 9. 방법 선택

| 상황 | 다음 단계 |
| --- | --- |
| recurrence coeff를 직접 찾음 | Kitamasa |
| 앞 항만 있고 field 위 수열 | Berlekamp-Massey |
| 생성함수 분모를 알고 있음 | Bostan-Mori |
| 상태 수가 작음 | Matrix Exponentiation |
| recurrence 존재 증명이 불명확 | 더 많은 holdout 또는 다른 모델 |

실전에서는 BM으로 coeff를 찾고 Kitamasa로 `a_n`을 구하는 조합이 가장 흔합니다.

## 10. 자주 하는 실수

1. 앞 `2K`개를 모두 fitting에 쓰고 검증 항을 남기지 않는다.
2. 합성수 mod에서 field inverse가 필요한 알고리즘을 쓴다.
3. affine recurrence를 homogeneous recurrence로 착각한다.
4. 수열 index 기준을 `a_0`와 `a_1` 사이에서 섞는다.
5. recurrence가 존재하는 이유를 설명하지 않고 추정 결과만 제출한다.

## 11. 문제를 볼 때 체크할 조건

- 항을 정확히 생성할 수 있는가?
- recurrence 차수의 상한을 추정할 수 있는가?
- mod가 prime field인가?
- 검증용 holdout 항을 충분히 남겼는가?
- 찾은 recurrence로 큰 `n`을 계산하는 방법이 있는가?

## 12. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: recurrence guessing `/practice/...` 문제 필요 | 앞 항 생성과 holdout 검증 | sequence modeling |
| 표준 | TODO: graph walk recurrence `/practice/...` 문제 필요 | Cayley-Hamilton 활용 | black-box sequence |
| 응용 | TODO: affine recurrence `/practice/...` 문제 필요 | 상수항 상태 추가 | affine transition |
| 함정 | TODO: false recurrence `/practice/...` 문제 필요 | 충분한 검증 항 유지 | counterexample |
