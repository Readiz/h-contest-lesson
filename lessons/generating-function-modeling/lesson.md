# Generating Function Modeling

Generating Function Modeling은 counting 문제나 DP 식을 계수열로 보고, 곱셈, 나눗셈, rational form으로 바꾸는 모델링 레슨입니다. Formal Power Series가 연산 도구를 다룬다면, 이 레슨은 문제 문장을 어떤 생성함수 식으로 번역할지에 집중합니다.

이 레슨은 조합론, Formal Power Series, Linear Recurrence Applications 이후에 보는 수학 모델링 심화입니다.

1. 선택, 합, 길이 조건을 계수의 의미로 고정한다.
2. 독립 선택은 곱, 대안 선택은 합, 반복 선택은 geometric series로 바꾼다.
3. 분모가 낮은 rational form이면 recurrence나 Bostan-Mori로 연결한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Combinatorics nCr, Formal Power Series, Linear Recurrence Applications
- 함께 보면 좋은 레슨: Bostan-Mori, FPS Log/Exp, Recurrence Guessing
- 다음에 볼 레슨: Black-Box Linear Algebra, polynomial DP, combinatorial species basics

## 1. 문제 신호

| 문제 표현 | 생성함수 관점 |
| --- | --- |
| 합이 정확히 `S`가 되게 고른다 | `x^S` 계수 |
| 각 물건을 0/1번 고른다 | `1 + x^w` |
| 같은 물건을 여러 번 고른다 | `1 + x^w + x^{2w} + ...` |
| 순서가 중요하다 | sequence construction |
| 길이 `n`의 구조 개수 | `x^n` 계수 추출 |
| 점화식이 낮은 차수로 보인다 | rational generating function 후보 |

가장 먼저 정할 것은 변수의 의미입니다. `x`가 "무게"인지, "길이"인지, "비용"인지 섞이면 식은 맞아 보여도 계수가 다른 값을 뜻합니다.

## 2. 기본 번역 규칙

| 구조 | 식 |
| --- | --- |
| 둘 중 하나 선택 | `A(x) + B(x)` |
| 독립적으로 둘 다 선택 | `A(x) * B(x)` |
| 0/1 선택 | `1 + x^w` |
| 무한 반복 선택 | `1 / (1 - x^w)` |
| 적어도 1번 선택 | `x^w / (1 - x^w)` |
| 길이 제한 `<= N` | `N`차까지만 truncate |

대회 구현에서는 무한급수를 실제로 무한히 만들지 않습니다. 필요한 차수까지만 유지합니다.

## 3. 작은 예시: Coin Change

동전 가치가 `2, 3`이고 순서를 무시해 합 `S`를 만드는 방법 수를 세어 봅시다.

```text
coin 2: 1 + x^2 + x^4 + x^6 + ...
coin 3: 1 + x^3 + x^6 + ...

F(x) = 1 / ((1 - x^2)(1 - x^3))
answer(S) = [x^S] F(x)
```

`S=6`이면 가능한 조합은 `2+2+2`, `3+3` 두 가지입니다. 실제로 `x^6` 계수는 2입니다.

## 4. 순서가 있는 경우

같은 동전이라도 순서가 중요하면 식이 달라집니다.

```text
atomic choice A(x) = x^2 + x^3
sequence of choices = 1 + A + A^2 + A^3 + ...
                   = 1 / (1 - A(x))
```

이제 `S=6`은 `2+2+2`, `3+3`뿐 아니라 순서가 다른 `2+?` 조합까지 세는 방식이 됩니다. "조합"과 "수열"을 구분하지 않으면 가장 쉽게 틀립니다.

## 5. DP와 생성함수의 연결

아래 DP는 coefficient update와 같습니다.

```text
dp[s] += dp[s - w]
```

이는 현재 다항식에 `1 + x^w + x^{2w} + ...`를 곱하는 과정입니다. 따라서 DP의 loop 순서가 생성함수 모델을 결정합니다.

| loop 순서 | 의미 |
| --- | --- |
| item 바깥, sum 증가 | 조합, 무한 반복 |
| sum 바깥, item 안쪽 | 순서 있는 sequence |
| item 바깥, sum 감소 | 0/1 선택 |

## 6. Truncated Polynomial 구현

아래 코드는 필요한 차수까지만 다항식을 곱합니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

const long long MOD_GEN_FUNC = 998244353;

vector<long long> multiplyTruncated(
    const vector<long long>& left,
    const vector<long long>& right,
    int maxDegree
) {
    vector<long long> result(maxDegree + 1, 0);
    for (int i = 0; i < (int)left.size() && i <= maxDegree; ++i) {
        if (left[i] == 0) {
            continue;
        }
        int limit = min((int)right.size() - 1, maxDegree - i);
        for (int j = 0; j <= limit; ++j) {
            result[i + j] = (result[i + j] + left[i] * right[j]) % MOD_GEN_FUNC;
        }
    }
    return result;
}

vector<long long> unboundedChoicePolynomial(int weight, int maxDegree) {
    vector<long long> poly(maxDegree + 1, 0);
    for (int degree = 0; degree <= maxDegree; degree += weight) {
        poly[degree] = 1;
    }
    return poly;
}
```

`maxDegree`가 크고 다항식이 조밀하면 NTT가 필요합니다. 하지만 모델링 단계에서는 먼저 작은 truncate 구현으로 식이 맞는지 확인하는 편이 안전합니다.

## 7. Rational Form으로 가는 신호

생성함수가 아래 꼴이면 `n`이 아주 클 때도 coefficient extraction을 할 수 있습니다.

```text
F(x) = P(x) / Q(x)
answer = [x^n] F(x)
```

`Q(x)`의 차수가 작으면 계수열은 선형 점화식을 가집니다. 이때 선택지는 세 가지입니다.

| 상황 | 방법 |
| --- | --- |
| `n`이 크고 `Q`가 직접 있음 | Bostan-Mori |
| 앞 항을 많이 만들 수 있음 | Berlekamp-Massey |
| 상태 전이가 작음 | Matrix Exponentiation |

생성함수 모델링은 이 세 도구의 입력을 만들어 주는 역할을 합니다.

## 8. 손으로 따라가는 예시

문제: `1`과 `2`를 사용해 합 `n`을 만드는 순서 있는 방법 수.

```text
A(x) = x + x^2
F(x) = 1 / (1 - A(x))
     = 1 / (1 - x - x^2)
```

따라서 계수는 Fibonacci recurrence를 따릅니다.

```text
a_n = a_{n-1} + a_{n-2}
```

DP로 풀 수도 있고, `n`이 매우 크면 recurrence로 풀 수도 있습니다. 생성함수는 왜 같은 문제가 Fibonacci로 연결되는지 설명합니다.

## 9. 시간 복잡도 선택

| 범위 | 접근 |
| --- | --- |
| `S <= 10^5`, item 수 중간 | 1차원 DP |
| 다항식 여러 개를 합친다 | divide-and-conquer convolution |
| `n`이 매우 크고 rational form | Bostan-Mori |
| 계수열 앞부분만 필요 | truncated polynomial |
| 조건이 여러 변수 | multivariate는 피하고 상태 DP로 압축 검토 |

변수가 두 개 이상이면 식은 예뻐져도 구현이 급격히 어려워집니다. 대회에서는 한 변수를 계수로 두고 나머지는 DP state로 남기는 혼합 모델이 자주 더 실용적입니다.

## 10. 자주 하는 실수

1. 순서 있는 경우와 순서 없는 경우의 생성함수를 섞는다.
2. `x`가 나타내는 값을 중간에 바꾼다.
3. `1/(1-x^w)`를 무한히 펼치려다가 필요한 차수 truncate를 잊는다.
4. rational form이 나왔는데 분모 차수와 초기항 index를 맞추지 않는다.
5. negative coefficient나 subtraction이 있는 식에서 모듈러 정규화를 빼먹는다.

## 11. 문제를 볼 때 체크할 조건

- 계수 `x^k`가 정확히 무엇을 의미하는가?
- 선택이 독립인가, 순서가 있는 sequence인가?
- 각 요소는 0/1, bounded, unbounded 중 무엇인가?
- 필요한 계수 범위가 작은가, `n`이 큰가?
- rational form이면 분모 차수와 초기항을 만들 수 있는가?

## 12. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: generating function modeling `/practice/...` 문제 필요 | 선택 구조를 다항식으로 번역 | coefficient |
| 표준 | TODO: bounded coin generating function `/practice/...` 문제 필요 | truncate와 DP loop 연결 | polynomial product |
| 응용 | TODO: rational generating function `/practice/...` 문제 필요 | Bostan-Mori 입력 구성 | coefficient extraction |
| 함정 | TODO: ordered vs unordered counting `/practice/...` 문제 필요 | sequence와 product 구분 | combinatorial model |
