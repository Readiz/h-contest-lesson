# Linear Recurrence와 Kitamasa

Linear Recurrence는 앞의 몇 항으로 다음 항이 결정되는 수열입니다. Matrix Exponentiation으로도 풀 수 있지만, 차수 `K`가 크고 `N`이 매우 클 때는 characteristic polynomial을 이용하는 Kitamasa 방식이 더 직접적입니다.

이 레슨은 Matrix Exponentiation 이후에 보는 선형 점화식 고속 계산을 정리합니다.

1. 점화식을 characteristic polynomial로 표현한다.
2. `x^n mod P(x)`의 계수를 구한다.
3. 그 계수로 초기항의 선형 결합을 계산한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 모듈러 연산, 행렬 거듭제곱, polynomial 나머지
- 함께 보면 좋은 레슨: Matrix Exponentiation, Formal Power Series, FFT와 NTT
- 다음에 볼 레슨: Bostan-Mori, linear recurrence guessing, multipoint evaluation

## 1. 문제 신호

| 문제 표현 | 접근 |
| --- | --- |
| `a_n = c1*a_{n-1} + ... + ck*a_{n-k}` | linear recurrence |
| `n`이 `10^18`처럼 크다 | fast exponentiation of polynomial |
| `K`가 수십~수천 | Kitamasa 후보 |
| 여러 n번째 항을 물어본다 | precompute/fast doubling 변형 고려 |
| 생성함수 분모가 주어진다 | Bostan-Mori 후보 |

`K`가 작으면 matrix exponentiation도 충분합니다. `K`가 커질수록 `K x K` 행렬 곱보다 polynomial reduction 관점이 유리해집니다.

## 2. Characteristic Polynomial

점화식이 아래와 같다고 합시다.

```text
a_n = c0*a_{n-1} + c1*a_{n-2} + ... + c_{K-1}*a_{n-K}
```

그러면 companion relation은 아래입니다.

```text
x^K = c0*x^{K-1} + c1*x^{K-2} + ... + c_{K-1}
```

`x^n`을 이 관계로 계속 줄이면 `degree < K`인 polynomial이 됩니다.

```text
x^n mod P(x) = p0 + p1*x + ... + p_{K-1}*x^{K-1}
```

그럼 답은 아래처럼 계산됩니다.

```text
a_n = p0*a_0 + p1*a_1 + ... + p_{K-1}*a_{K-1}
```

## 3. Kitamasa 구현

아래 구현은 `coeff[i]`가 `a_n`에서 `a_{n-i-1}`에 곱해지는 계수라는 convention을 사용합니다.

```cpp compile-check
#include <vector>
using namespace std;

const long long MOD_RECURRENCE = 998244353;

long long normalizeMod(long long value) {
    value %= MOD_RECURRENCE;
    if (value < 0) {
        value += MOD_RECURRENCE;
    }
    return value;
}

vector<long long> combinePolynomial(
    const vector<long long>& left,
    const vector<long long>& right,
    const vector<long long>& coeff
) {
    int k = (int)coeff.size();
    vector<long long> temp(2 * k - 1, 0);

    for (int i = 0; i < k; ++i) {
        for (int j = 0; j < k; ++j) {
            temp[i + j] = (temp[i + j] + left[i] * right[j]) % MOD_RECURRENCE;
        }
    }

    for (int degree = 2 * k - 2; degree >= k; --degree) {
        long long value = temp[degree];
        if (value == 0) {
            continue;
        }
        for (int j = 1; j <= k; ++j) {
            temp[degree - j] = (temp[degree - j] + value * coeff[j - 1]) % MOD_RECURRENCE;
        }
    }

    temp.resize(k);
    return temp;
}

vector<long long> coefficientOfNthPower(long long n, const vector<long long>& coeff) {
    int k = (int)coeff.size();
    vector<long long> result(k, 0);
    vector<long long> base(k, 0);

    result[0] = 1;
    if (k == 1) {
        base[0] = coeff[0];
    } else {
        base[1] = 1;
    }

    while (n > 0) {
        if (n & 1LL) {
            result = combinePolynomial(result, base, coeff);
        }
        base = combinePolynomial(base, base, coeff);
        n >>= 1LL;
    }

    return result;
}

long long nthLinearRecurrence(
    const vector<long long>& initial,
    const vector<long long>& coeff,
    long long n
) {
    int k = (int)coeff.size();
    if (n < (long long)initial.size()) {
        return normalizeMod(initial[(int)n]);
    }

    vector<long long> weight = coefficientOfNthPower(n, coeff);
    long long answer = 0;
    for (int i = 0; i < k; ++i) {
        answer = (answer + weight[i] * normalizeMod(initial[i])) % MOD_RECURRENCE;
    }
    return answer;
}
```

`coeff`와 `initial`의 길이는 같아야 합니다. 초기항은 `a_0..a_{K-1}` 순서입니다.

## 4. 작은 예시

Fibonacci는 아래 점화식입니다.

```text
F_n = F_{n-1} + F_{n-2}
F_0 = 0, F_1 = 1
```

그러면 입력은 아래처럼 됩니다.

```text
initial = [0, 1]
coeff = [1, 1]
```

`x^n mod (x^2 - x - 1)`의 계수를 구한 뒤 `F_0`, `F_1`에 곱하면 `F_n`이 됩니다.

## 5. Matrix Exponentiation과 비교

| 방식 | 시간 | 특징 |
| --- | ---: | --- |
| Matrix exponentiation | `O(K^3 log N)` | 구현 직관적, 전이 일반화 쉬움 |
| Kitamasa 기본형 | `O(K^2 log N)` | 선형 점화식 특화 |
| NTT 최적화 | `O(K log K log N)` 근처 | 구현 복잡 |
| Bostan-Mori | `O(K log K log N)` | 생성함수 분수 형태에 강함 |

문제가 단순 선형 점화식이면 Kitamasa가 깔끔합니다. 상태 전이가 sparse하거나 다른 구조가 있으면 행렬 방식이 더 읽기 쉬울 수 있습니다.

## 6. Berlekamp-Massey와의 연결

처음 몇 항만 주어지고 점화식을 모르면 Berlekamp-Massey로 최소 선형 점화식을 추정할 수 있습니다.

```text
sequence prefix -> Berlekamp-Massey -> coeff -> Kitamasa nth term
```

다만 이 조합은 모듈러 field 위에서 동작합니다. 합성수 mod나 실수 근사 수열에는 그대로 적용하면 안 됩니다.

## 7. 시간 복잡도

기본 구현은 polynomial 곱셈과 reduction에 `O(K^2)`가 들고, 거듭제곱에 `O(log N)`번 사용합니다.

```text
O(K^2 log N)
```

`K`가 5000 이상이면 이 구현도 부담될 수 있습니다. 그때는 NTT 기반 polynomial reduction이나 Bostan-Mori를 고려합니다.

## 8. 자주 하는 실수

1. `coeff` 순서를 거꾸로 넣는다.
2. `a_0` 기반인지 `a_1` 기반인지 섞는다.
3. `n < K`일 때 초기항을 바로 반환하지 않는다.
4. 음수 계수를 모듈러 정규화하지 않는다.
5. characteristic relation의 degree reduction 방향을 잘못 잡는다.

## 9. 문제를 볼 때 체크할 조건

- 점화식 차수 `K`와 질의 `N`의 범위는?
- 초기항 index가 0부터인가 1부터인가?
- 계수와 답의 mod가 prime인가?
- 점화식이 고정인가, query마다 바뀌는가?
- 여러 항을 한꺼번에 구해야 하는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: Fibonacci 큰 n `/practice/...` 문제 필요 | `x^n mod P(x)` 계수 계산 | Kitamasa |
| 표준 | TODO: K차 선형 점화식 `/practice/...` 문제 필요 | `O(K^2 log N)` 구현 | linear recurrence |
| 응용 | TODO: 점화식 추정 후 nth `/practice/...` 문제 필요 | Berlekamp-Massey와 연결 | recurrence guessing |
| 함정 | TODO: 음수 계수 점화식 `/practice/...` 문제 필요 | 모듈러 정규화 | characteristic polynomial |
