# FPS Log와 Exp

FPS Log와 Exp는 Formal Power Series의 고급 기본 연산입니다. polynomial inverse, derivative, integral을 조합해 `log F(x)`를 계산하고, Newton iteration으로 `exp F(x)`를 구합니다. 생성함수 문제에서 곱셈 이상의 변환이 필요할 때 등장합니다.

이 레슨은 Formal Power Series의 다음 단계로 log, exp, power의 의미와 구현 흐름을 정리합니다.

1. `log F = integral(F' / F)` 공식을 사용한다.
2. `exp G`는 `log H = G`를 만족하는 `H`를 Newton iteration으로 찾는다.
3. 생성함수 문제에서 log/exp가 어떤 조합 의미를 갖는지 이해한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Formal Power Series, NTT, polynomial inverse, derivative/integral
- 함께 보면 좋은 레슨: Formal Power Series, FFT와 NTT, 조합론
- 다음에 볼 레슨: polynomial power, exponential generating function, combinatorial species

## 1. 언제 필요한가

| 문제 신호 | FPS 연산 |
| --- | --- |
| 생성함수의 로그가 필요하다 | FPS log |
| 어떤 계수열의 exponential composition | FPS exp |
| 다항식을 큰 지수로 거듭제곱 | log 후 scalar multiply 후 exp |
| connected object와 all object 관계 | log/exp 조합 |

대부분의 일반 대회에서는 드물지만, polynomial 라이브러리를 요구하는 문제에서는 핵심 연산입니다.

## 2. FPS Log

상수항이 `1`인 FPS `F`에 대해 log는 아래로 정의됩니다.

```text
log F = integral(F' * inverse(F))
```

`F(0) = 1`이어야 log의 상수항이 0으로 자연스럽게 정의됩니다.

```cpp compile-check
#include <vector>
using namespace std;

const long long MOD_LOG = 998244353;

long long modPowLog(long long base, long long exp) {
    long long result = 1;
    while (exp > 0) {
        if (exp & 1LL) result = result * base % MOD_LOG;
        base = base * base % MOD_LOG;
        exp >>= 1LL;
    }
    return result;
}

vector<long long> derivativeLog(const vector<long long>& a) {
    if (a.size() <= 1) {
        return {0};
    }
    vector<long long> result(a.size() - 1);
    for (int i = 1; i < (int)a.size(); ++i) {
        result[i - 1] = a[i] * i % MOD_LOG;
    }
    return result;
}

vector<long long> integralLog(const vector<long long>& a) {
    vector<long long> result(a.size() + 1, 0);
    for (int i = 0; i < (int)a.size(); ++i) {
        result[i + 1] = a[i] * modPowLog(i + 1, MOD_LOG - 2) % MOD_LOG;
    }
    return result;
}
```

실제 `log` 구현에는 polynomial inverse와 convolution이 필요합니다. 위 코드는 log의 구성 요소인 미분/적분을 보여 주는 최소 조각입니다.

## 3. FPS Exp

`G(0) = 0`인 FPS `G`에 대해 `exp G`는 아래를 만족하는 FPS `F`입니다.

```text
log F = G
F(0) = 1
```

Newton iteration은 현재 근사 `F`를 더 긴 차수로 확장합니다.

```text
F_new = F * (1 - log F + G) mod x^n
```

이 식은 `log F`가 목표 `G`에 가까워지도록 보정합니다.

## 4. Power로 이어지는 공식

다항식 거듭제곱도 log/exp로 처리할 수 있습니다.

```text
F(x)^k = exp(k * log F(x))
```

단, `F(0) = 1`이 아닐 때는 앞쪽의 0이 아닌 최소 차수와 상수 계수를 분리해야 합니다. 이 처리가 까다로워서 power 구현은 log/exp보다 더 많은 예외 처리가 필요합니다.

## 5. 단순 convolution 도우미

큰 입력에서는 NTT를 써야 하지만, 연산 관계를 확인하는 작은 테스트에는 단순 convolution이 유용합니다.

```cpp compile-check
#include <vector>
using namespace std;

const long long MOD_FPS_LOG = 998244353;

vector<long long> multiplySmall(
    const vector<long long>& a,
    const vector<long long>& b,
    int limit
) {
    vector<long long> result(limit, 0);
    for (int i = 0; i < (int)a.size(); ++i) {
        for (int j = 0; j < (int)b.size() && i + j < limit; ++j) {
            result[i + j] = (result[i + j] + a[i] * b[j]) % MOD_FPS_LOG;
        }
    }
    return result;
}

void truncate(vector<long long>& a, int limit) {
    if ((int)a.size() > limit) {
        a.resize(limit);
    }
}
```

FPS 코드는 작은 차수에서 단순 곱셈으로 검증한 뒤 NTT로 바꾸는 방식이 안전합니다.

## 6. 조합론적 의미

생성함수에서 log와 exp는 "connected object"와 "set of objects" 관계를 표현할 때 자주 등장합니다.

```text
All structures = exp(Connected structures)
Connected structures = log(All structures)
```

정확한 의미는 ordinary generating function인지 exponential generating function인지에 따라 달라집니다. 문제에서 factorial이 섞인 EGF인지, 일반 OGF인지 먼저 확인해야 합니다.

## 7. 구현 전제 조건

| 연산 | 조건 |
| --- | --- |
| `log F` | `F[0] = 1` |
| `exp G` | `G[0] = 0` |
| `inverse F` | `F[0] != 0` |
| `F^k` 간단 공식 | 보통 `F[0] = 1` |

조건이 다르면 shift와 scale 처리가 들어갑니다. 라이브러리로 숨기더라도 수학적 전제는 알고 있어야 합니다.

## 8. 시간 복잡도

| 연산 | NTT 기반 시간 |
| --- | ---: |
| inverse | `O(N log N)` |
| log | inverse + derivative/integral + multiply |
| exp | Newton iteration으로 `O(N log N)` 수준 |
| power | log + scalar multiply + exp |

상수는 큽니다. `N`이 작으면 단순 DP나 `O(N^2)` polynomial이 더 빠를 수 있습니다.

## 9. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| `log`에서 `F[0] != 1` | 정의 조건 위반 | 상수항 확인 |
| `exp`에서 `G[0] != 0` | 결과 상수항 불일치 | 목표 FPS 상수항 확인 |
| truncation 누락 | 시간/메모리 폭증 | 매 단계 `mod x^n` |
| OGF/EGF 구분 실패 | 계수 전체 오답 | factorial 포함 여부 확인 |
| NTT mod/root 불일치 | 곱셈 오답 | `998244353`, root 3 세트 확인 |
| 작은 테스트 없이 라이브러리 사용 | 디버깅 어려움 | 낮은 차수 직접 검산 |

## 10. 문제를 볼 때 체크할 조건

1. 다항식의 log/exp/power가 실제로 필요한가?
2. 상수항 조건이 맞는가?
3. 원하는 계수 개수 `N`으로 truncate할 수 있는가?
4. convolution은 NTT가 필요한 크기인가?
5. 생성함수가 OGF인지 EGF인지 구분했는가?
6. 작은 차수에서 직접 곱해 검증할 수 있는가?

FPS Log와 Exp는 공식 자체는 짧지만 구현은 복잡합니다. 조건을 맞춘 뒤 inverse, multiply, derivative, integral이 각각 검증되어 있어야 안정적으로 사용할 수 있습니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: FPS log `/practice/...` 문제 필요 | `integral(F'/F)` 구현 | FPS logarithm |
| 표준 | TODO: FPS exp `/practice/...` 문제 필요 | Newton iteration 보정 | FPS exponential |
| 응용 | TODO: polynomial power `/practice/...` 문제 필요 | `exp(k log F)`와 shift 처리 | polynomial power |
| 함정 | TODO: OGF/EGF 구분 `/practice/...` 문제 필요 | factorial 계수 해석 | generating function |
