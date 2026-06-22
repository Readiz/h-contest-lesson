# Bostan-Mori

Bostan-Mori는 rational generating function `P(x) / Q(x)`의 `x^n` 계수를 빠르게 구하는 알고리즘입니다. 선형 점화식의 n번째 항을 characteristic polynomial이 아니라 생성함수 관점에서 계산할 수 있습니다.

이 레슨은 Linear Recurrence와 Kitamasa, Formal Power Series 이후에 보는 polynomial 계수 추출 기법입니다.

1. 짝수/홀수 계수만 남기는 변환을 반복한다.
2. 분모 `Q(x)`와 `Q(-x)`를 곱해 짝수 차수만 남긴다.
3. `n`의 parity에 따라 분자를 갱신하고 `n`을 절반으로 줄인다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 선형 점화식, 다항식 곱셈, 생성함수, modular inverse
- 함께 보면 좋은 레슨: Linear Recurrence와 Kitamasa, Formal Power Series, Multipoint Evaluation
- 다음에 볼 레슨: polynomial interpolation, linear recurrence guessing, NTT 최적화

## 1. 문제 신호

| 문제 표현 | Bostan-Mori 관점 |
| --- | --- |
| rational generating function의 n번째 계수 | Bostan-Mori |
| 선형 점화식의 큰 n번째 항 | Kitamasa 또는 Bostan-Mori |
| `P(x) / Q(x)` 형태가 직접 주어짐 | Bostan-Mori가 자연스러움 |
| n이 `10^18` 이상 | log n 반복 필요 |
| polynomial degree가 큼 | NTT 기반 곱셈 고려 |

Kitamasa는 `x^n mod characteristic`을 구하는 관점이고, Bostan-Mori는 generating function에서 계수를 뽑는 관점입니다. 둘 다 선형 점화식에 사용할 수 있습니다.

## 2. 핵심 공식

구하고 싶은 값이:

```text
[x^n] P(x) / Q(x)
```

이라고 합시다. `Q(-x)`를 곱하면 분모가 짝수 차수만 갖게 됩니다.

```text
P(x) / Q(x) = P(x)Q(-x) / (Q(x)Q(-x))
```

분모가 `x^2`의 polynomial이 되므로, n의 parity에 따라 분자의 짝수 또는 홀수 계수만 남기고 n을 절반으로 줄일 수 있습니다.

## 3. Polynomial 도우미

아래 코드는 나이브 곱셈을 사용한 Bostan-Mori 구현입니다. 큰 입력에서는 `multiply`를 NTT로 바꾸면 됩니다.

```cpp compile-check
#include <vector>
using namespace std;

const long long MOD_BOSTAN = 998244353;

long long modPowBostan(long long base, long long exp) {
    long long result = 1;
    while (exp > 0) {
        if (exp & 1LL) {
            result = result * base % MOD_BOSTAN;
        }
        base = base * base % MOD_BOSTAN;
        exp >>= 1LL;
    }
    return result;
}

long long normalizeBostan(long long value) {
    value %= MOD_BOSTAN;
    if (value < 0) {
        value += MOD_BOSTAN;
    }
    return value;
}

vector<long long> multiplyBostan(const vector<long long>& a, const vector<long long>& b) {
    vector<long long> result(a.size() + b.size() - 1, 0);
    for (int i = 0; i < (int)a.size(); ++i) {
        for (int j = 0; j < (int)b.size(); ++j) {
            result[i + j] = (result[i + j] + a[i] * b[j]) % MOD_BOSTAN;
        }
    }
    return result;
}

vector<long long> negateOddTerms(vector<long long> q) {
    for (int i = 1; i < (int)q.size(); i += 2) {
        q[i] = normalizeBostan(-q[i]);
    }
    return q;
}

vector<long long> takeParity(const vector<long long>& poly, int parity) {
    vector<long long> result;
    for (int i = parity; i < (int)poly.size(); i += 2) {
        result.push_back(poly[i]);
    }
    if (result.empty()) {
        result.push_back(0);
    }
    return result;
}

long long bostanMori(vector<long long> p, vector<long long> q, long long n) {
    while (n > 0) {
        vector<long long> qNeg = negateOddTerms(q);
        vector<long long> numerator = multiplyBostan(p, qNeg);
        vector<long long> denominator = multiplyBostan(q, qNeg);

        p = takeParity(numerator, (int)(n & 1LL));
        q = takeParity(denominator, 0);
        n >>= 1LL;
    }

    return p[0] * modPowBostan(q[0], MOD_BOSTAN - 2) % MOD_BOSTAN;
}
```

입력 `q[0]`은 0이 아니어야 합니다. 보통 생성함수 분모는 `Q(0)=1`로 정규화합니다.

## 4. 선형 점화식과 연결

점화식:

```text
a_n = c1*a_{n-1} + c2*a_{n-2} + ... + ck*a_{n-k}
```

의 생성함수 분모는 보통 아래처럼 됩니다.

```text
Q(x) = 1 - c1*x - c2*x^2 - ... - ck*x^k
```

분자 `P(x)`는 초기항과 `Q(x)`를 곱한 뒤 낮은 차수만 취해 만들 수 있습니다.

```text
A(x) = P(x) / Q(x)
P = first k terms of A(x)Q(x)
```

## 5. Kitamasa와 비교

| 방식 | 관점 | 장점 |
| --- | --- | --- |
| Kitamasa | `x^n mod characteristic` | 점화식 계수와 초기항에서 직접 출발 |
| Bostan-Mori | `[x^n] P/Q` | rational generating function이 있을 때 자연스러움 |
| Matrix exponentiation | companion matrix | 상태 전이가 명시적일 때 직관적 |

문제가 generating function을 직접 주거나 조합론적으로 분모가 먼저 보이면 Bostan-Mori가 읽기 쉽습니다.

## 6. 시간 복잡도

나이브 곱셈이면 한 단계가 `O(K^2)`이고, `log N`번 반복합니다.

```text
O(K^2 log N)
```

NTT 곱셈과 trimming을 쓰면 더 빨라집니다. 하지만 구현 복잡도가 커지므로 제약이 작으면 나이브 버전으로도 충분합니다.

## 7. 자주 하는 실수

1. `Q(-x)`를 만들 때 홀수 차수만 부호를 바꿔야 하는데 전체를 바꾼다.
2. n이 홀수일 때 분자의 홀수 계수를 골라야 하는데 짝수를 고른다.
3. denominator는 항상 짝수 계수만 취해야 한다는 점을 빼먹는다.
4. `Q(0)` inverse가 필요하다는 조건을 확인하지 않는다.
5. 점화식에서 분자 `P`를 만들 때 초기항 보정을 빼먹는다.

## 8. 문제를 볼 때 체크할 조건

- `P(x)/Q(x)`가 직접 주어졌는가?
- 구할 것은 n번째 계수 하나인가, 여러 개인가?
- modulus가 prime이라 inverse를 구할 수 있는가?
- `Q(0)`이 0이 아닌가?
- degree와 n 범위가 Kitamasa, matrix exponentiation 중 무엇에 맞는가?

## 9. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: rational generating function 계수 `/practice/...` 문제 필요 | `P/Q`에서 n번째 계수 추출 | Bostan-Mori |
| 표준 | TODO: 선형 점화식 n번째 항 `/practice/...` 문제 필요 | `Q(x)=1-cx...` 구성 | linear recurrence |
| 응용 | TODO: 조합 생성함수 계수 `/practice/...` 문제 필요 | 분모/분자 모델링 | generating function |
| 함정 | TODO: `Q(0) != 1` 보정 `/practice/...` 문제 필요 | constant inverse 처리 | normalization |
