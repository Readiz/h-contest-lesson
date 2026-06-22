# Polynomial Interpolation

Polynomial Interpolation은 몇 개의 점을 지나는 다항식을 복원하거나, 복원하지 않고 특정 위치의 값을 계산하는 기법입니다. Multipoint Evaluation이 "하나의 다항식을 여러 점에서 평가"하는 방향이라면, Interpolation은 "여러 점에서 다항식을 되찾는" 반대 방향입니다.

이 레슨은 조합론, FFT/NTT, Formal Power Series, Multipoint Evaluation 이후에 보는 polynomial 심화입니다.

1. 차수 `< N`인 다항식은 서로 다른 `N`개의 점으로 결정된다.
2. 연속된 x좌표 `0, 1, ..., N-1`에서는 Lagrange 보간을 `O(N)`에 한 점 평가할 수 있다.
3. 임의 x좌표의 전체 계수 복원은 나이브 `O(N^2)`, product tree를 쓰면 더 빠르게 가능하다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 모듈러 역원, factorial, polynomial multiplication, prefix/suffix product
- 함께 보면 좋은 레슨: 조합론, Multipoint Evaluation, Formal Power Series
- 다음에 볼 레슨: linear basis, NTT 기반 interpolation, combinatorial polynomial trick

## 1. 문제 신호

| 문제 표현 | Interpolation 관점 |
| --- | --- |
| `f(0)..f(k)`를 알고 `f(n)`을 구한다 | consecutive Lagrange |
| 답이 k차 다항식임을 증명할 수 있다 | k+1개 값으로 결정 |
| 조합 합이 n에 대한 다항식이다 | finite differences 또는 interpolation |
| 여러 점에서 값을 알고 계수를 복원한다 | polynomial interpolation |
| evaluation과 interpolation을 반복한다 | product tree/NTT 고려 |

핵심은 "답 함수가 다항식인가"입니다. 단순히 몇 개 값을 안다고 항상 보간해도 되는 것은 아닙니다.

## 2. Lagrange 공식

서로 다른 점 `(x_i, y_i)`가 있을 때 차수 `< N`인 다항식 `f(x)`는:

```text
f(x) = sum_i y_i * product_{j != i} (x - x_j) / (x_i - x_j)
```

모듈러에서 나눗셈은 역원입니다. 따라서 mod가 prime이고 `x_i - x_j`가 0이 아니어야 합니다.

## 3. 연속 x좌표 최적화

`x_i = i`인 경우 분모가 factorial로 정리됩니다.

```text
denominator_i = i! * (-1)^(n-1-i) * (n-1-i)!
```

분자 `product (x - j)`는 prefix/suffix product로 각 i에 대해 `O(1)`에 얻습니다.

## 4. 구현

아래 함수는 `f(0), f(1), ..., f(n-1)`이 주어졌을 때 `f(x)`를 계산합니다. `x < n`이면 저장된 값을 바로 반환합니다.

```cpp compile-check
#include <vector>
using namespace std;

const long long MOD_INTERPOLATION = 998244353;

long long normalizeInterpolation(long long value) {
    value %= MOD_INTERPOLATION;
    if (value < 0) {
        value += MOD_INTERPOLATION;
    }
    return value;
}

long long modPowInterpolation(long long base, long long exp) {
    long long result = 1;
    base = normalizeInterpolation(base);
    while (exp > 0) {
        if (exp & 1LL) {
            result = result * base % MOD_INTERPOLATION;
        }
        base = base * base % MOD_INTERPOLATION;
        exp >>= 1LL;
    }
    return result;
}

long long inverseInterpolation(long long value) {
    return modPowInterpolation(value, MOD_INTERPOLATION - 2);
}

long long lagrangeConsecutive(const vector<long long>& y, long long x) {
    int n = (int)y.size();
    if (0 <= x && x < n) {
        return normalizeInterpolation(y[(int)x]);
    }

    vector<long long> prefix(n + 1, 1);
    vector<long long> suffix(n + 1, 1);
    for (int i = 0; i < n; ++i) {
        prefix[i + 1] = prefix[i] * normalizeInterpolation(x - i) % MOD_INTERPOLATION;
    }
    for (int i = n - 1; i >= 0; --i) {
        suffix[i] = suffix[i + 1] * normalizeInterpolation(x - i) % MOD_INTERPOLATION;
    }

    vector<long long> factorial(n, 1);
    vector<long long> invFactorial(n, 1);
    for (int i = 1; i < n; ++i) {
        factorial[i] = factorial[i - 1] * i % MOD_INTERPOLATION;
    }
    invFactorial[n - 1] = inverseInterpolation(factorial[n - 1]);
    for (int i = n - 1; i >= 1; --i) {
        invFactorial[i - 1] = invFactorial[i] * i % MOD_INTERPOLATION;
    }

    long long answer = 0;
    for (int i = 0; i < n; ++i) {
        long long numerator = prefix[i] * suffix[i + 1] % MOD_INTERPOLATION;
        long long denominatorInverse = invFactorial[i] * invFactorial[n - 1 - i] % MOD_INTERPOLATION;
        if ((n - 1 - i) & 1) {
            denominatorInverse = MOD_INTERPOLATION - denominatorInverse;
        }
        long long term = normalizeInterpolation(y[i]) * numerator % MOD_INTERPOLATION * denominatorInverse % MOD_INTERPOLATION;
        answer += term;
        if (answer >= MOD_INTERPOLATION) {
            answer -= MOD_INTERPOLATION;
        }
    }
    return answer;
}
```

## 5. Finite Difference와 관계

연속된 정수점에서 다항식 값을 보면 차분도 유용합니다.

```text
degree 0 polynomial -> first difference is 0
degree 1 polynomial -> second difference is 0
degree k polynomial -> (k+1)-th difference is 0
```

문제에서 "몇 개 값을 직접 구해보면 차분이 일정해진다"는 신호가 있으면 다항식 차수를 추측하고 interpolation으로 큰 n을 처리할 수 있습니다. 단, 추측만으로 제출하면 위험하므로 조합론적 증명이나 recurrence를 같이 확인해야 합니다.

## 6. 전체 계수 복원

모든 계수가 필요하면 Lagrange basis polynomial을 직접 더할 수 있습니다.

```text
L_i(x) = product_{j != i} (x - x_j) / (x_i - x_j)
f(x) = sum y_i L_i(x)
```

나이브로는 각 basis를 만드는 데 `O(N^2)`입니다. N이 크면 subproduct tree, multipoint evaluation, polynomial inverse를 조합해야 합니다.

## 7. 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| 연속 x좌표 한 점 평가 | `O(N)` |
| 임의 x좌표 나이브 한 점 평가 | `O(N^2)` 또는 전처리 후 `O(N)` 형태 |
| 전체 계수 나이브 복원 | `O(N^2)` |
| product tree 기반 계수 복원 | `O(M(N) log N)` 계열 |

## 8. 자주 하는 실수

1. 점의 개수가 차수보다 하나 더 필요하다는 조건을 잊는다.
2. `x`가 이미 주어진 점이면 분모가 0이 되는데도 공식을 그대로 적용한다.
3. mod가 prime이 아닌데 페르마 역원을 쓴다.
4. `(-1)^(n-1-i)` 부호를 빠뜨린다.
5. 값 몇 개가 맞는다는 이유만으로 다항식임을 증명하지 않는다.

## 9. 문제를 볼 때 체크할 조건

- 답이 어떤 변수에 대한 다항식이라는 근거가 있는가?
- 차수 상한을 알고 있는가?
- x좌표가 연속 정수인가, 임의 점인가?
- 여러 query를 처리해야 하는가?
- 전체 계수가 필요한가, 특정 값 하나만 필요한가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: consecutive Lagrange `/practice/...` 문제 필요 | `f(0..k)`로 `f(n)` 계산 | Lagrange |
| 표준 | TODO: finite difference polynomial `/practice/...` 문제 필요 | 차수 추정과 증명 | finite difference |
| 응용 | TODO: arbitrary point interpolation `/practice/...` 문제 필요 | 전체 계수 복원 | basis polynomial |
| 함정 | TODO: non-prime modulus interpolation `/practice/...` 문제 필요 | 역원 조건 확인 | modular inverse |
