# Polynomial Interpolation

Polynomial Interpolation은 몇 개의 점을 지나는 다항식을 복원하거나, 복원하지 않고 특정 위치의 값을 계산하는 기법입니다. Multipoint Evaluation이 "하나의 다항식을 여러 점에서 평가"하는 방향이라면, Interpolation은 "여러 점에서 다항식을 되찾는" 반대 방향입니다.


`1<=y.size()<MOD`, deg(F)<y.size()를 전제로 합니다. 이 구현은 factorial 전처리까지 포함해 한 질의 `O(N+log MOD)`입니다. 일반 보간을 O(N²)에 하려면 공통 곱 다항식을 만든 뒤 각 선형 인수로 synthetic division합니다. basis를 매번 처음부터 곱하면 O(N³)이 될 수 있습니다.

## 문제 신호

| 문제 표현 | Interpolation 관점 |
| --- | --- |
| `f(0)..f(k)`를 알고 `f(n)`을 구한다 | consecutive Lagrange |
| 답이 k차 다항식임을 증명할 수 있다 | k+1개 값으로 결정 |
| 조합 합이 n에 대한 다항식이다 | finite differences 또는 interpolation |
| 여러 점에서 값을 알고 계수를 복원한다 | polynomial interpolation |
| evaluation과 interpolation을 반복한다 | product tree/NTT 고려 |

핵심은 "답 함수가 다항식인가"입니다. 단순히 몇 개 값을 안다고 항상 보간해도 되는 것은 아닙니다.

## Lagrange 공식

서로 다른 점 `(x_i, y_i)`가 있을 때 차수 `< N`인 다항식 `f(x)`는:

```text
f(x) = sum_i y_i * product_{j != i} (x - x_j) / (x_i - x_j)
```

모듈러에서 나눗셈은 역원입니다. 따라서 mod가 prime이고 `x_i - x_j`가 0이 아니어야 합니다.

## 연속 x좌표 최적화

`x_i = i`인 경우 분모가 factorial로 정리됩니다.

```text
denominator_i = i! * (-1)^(n-1-i) * (n-1-i)!
```

분자 `product (x - j)`는 prefix/suffix product로 각 i에 대해 `O(1)`에 얻습니다.

## 구현

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
    x = normalizeInterpolation(x);
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

## Finite Difference와 관계

연속된 정수점에서 다항식 값을 보면 차분도 유용합니다.

```text
degree 0 polynomial -> first difference is 0
degree 1 polynomial -> second difference is 0
degree k polynomial -> (k+1)-th difference is 0
```

문제에서 "몇 개 값을 직접 구해보면 차분이 일정해진다"는 신호가 있으면 다항식 차수를 추측하고 interpolation으로 큰 n을 처리할 수 있습니다. 단, 추측만으로 제출하면 위험하므로 조합론적 증명이나 recurrence를 같이 확인해야 합니다.

## 전체 계수 복원

모든 계수가 필요하면 Lagrange basis polynomial을 직접 더할 수 있습니다.

```text
L_i(x) = product_{j != i} (x - x_j) / (x_i - x_j)
f(x) = sum y_i L_i(x)
```

각 basis를 처음부터 곱하면 하나에 O(N²), 전체 O(N³)입니다. 공통 곱을 한 번 만들고 선형 인수로 나누면 전체 O(N²)로 줄어듭니다. N이 크면 subproduct tree, multipoint evaluation, polynomial inverse를 조합해야 합니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| 현재 구현의 연속 x좌표 한 점 평가 | `O(N+log MOD)` |
| 임의 x좌표 나이브 한 점 평가 | `O(N^2)` 또는 전처리 후 `O(N)` 형태 |
| 전체 계수 나이브 복원 | `O(N^2)` |
| product tree 기반 계수 복원 | `O(M(N) log N)` 계열 |
