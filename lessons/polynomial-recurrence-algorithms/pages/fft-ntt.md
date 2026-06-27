# FFT와 NTT

FFT와 NTT는 다항식 곱셈, 즉 convolution을 빠르게 계산하는 기법입니다. 두 배열 `a`, `b`에 대해 `c[k] = sum a[i] * b[k - i]`를 직접 계산하면 `O(NM)`이지만, FFT/NTT를 쓰면 대략 `O(N log N)`에 처리할 수 있습니다.

이 레슨은 "계수 표현의 다항식을 값 표현으로 바꿔 곱한 뒤 되돌린다"는 관점으로 FFT와 NTT를 봅니다.

1. convolution이 필요한 문제 신호를 찾는다.
2. NTT friendly modulus에서 정수 convolution을 구현한다.
3. FFT/NTT 선택 기준과 실수 포인트를 점검한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 모듈러 연산, 빠른 거듭제곱, 조합론, 복소수 또는 원시근 개념
- 함께 보면 좋은 레슨: 모듈러 연산과 빠른 거듭제곱, 조합론, Matrix Exponentiation
- 다음에 볼 레슨: polynomial inverse, formal power series, divide-and-conquer convolution DP

## 1. Convolution 신호

다음 형태가 보이면 convolution을 의심합니다.

```text
c[k] = sum a[i] * b[k - i]
```

| 문제 표현 | convolution 해석 |
| --- | --- |
| 두 집합에서 합이 k가 되는 쌍의 수 | 빈도 배열 convolution |
| 다항식 두 개의 곱 | 계수 convolution |
| 가능한 무게 합의 조합 | generating function |
| 거리/값 차이별 pair count | index를 뒤집은 convolution |
| 여러 DP 전이의 합성 | polynomial multiplication |

모든 "이중 합"이 convolution은 아닙니다. 두 index가 `i + j = k`처럼 하나의 합으로 묶일 때 convolution 구조가 됩니다.

## 2. FFT와 NTT 차이

| 방식 | 값 타입 | 장점 | 주의점 |
| --- | --- | --- | --- |
| FFT | 복소수 | 임의 정수/실수 계수에 넓게 사용 | 반올림 오차 |
| NTT | 모듈러 정수 | 정확한 정수 계산 | 특정 mod와 원시근 필요 |

대회에서 결과를 `998244353`으로 나누는 문제가 많으면 NTT가 가장 편합니다. `998244353 = 119 * 2^23 + 1`이고 원시근 `3`을 쓸 수 있어 길이 `2^23`까지 NTT가 가능합니다.

## 3. NTT 구현

아래 구현은 `998244353` 모듈러에서 convolution을 계산합니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

const long long MOD = 998244353;
const long long PRIMITIVE_ROOT = 3;

long long modPow(long long base, long long exp) {
    long long result = 1;
    while (exp > 0) {
        if (exp & 1LL) {
            result = result * base % MOD;
        }
        base = base * base % MOD;
        exp >>= 1LL;
    }
    return result;
}

void ntt(vector<long long>& a, bool invert) {
    int n = (int)a.size();
    for (int i = 1, j = 0; i < n; ++i) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) {
            j ^= bit;
        }
        j ^= bit;
        if (i < j) {
            swap(a[i], a[j]);
        }
    }

    for (int len = 2; len <= n; len <<= 1) {
        long long root = modPow(PRIMITIVE_ROOT, (MOD - 1) / len);
        if (invert) {
            root = modPow(root, MOD - 2);
        }
        for (int i = 0; i < n; i += len) {
            long long w = 1;
            for (int j = 0; j < len / 2; ++j) {
                long long u = a[i + j];
                long long v = a[i + j + len / 2] * w % MOD;
                a[i + j] = (u + v) % MOD;
                a[i + j + len / 2] = (u - v + MOD) % MOD;
                w = w * root % MOD;
            }
        }
    }

    if (invert) {
        long long invN = modPow(n, MOD - 2);
        for (long long& x : a) {
            x = x * invN % MOD;
        }
    }
}

vector<long long> convolution(vector<long long> a, vector<long long> b) {
    if (a.empty() || b.empty()) {
        return {};
    }

    int need = (int)a.size() + (int)b.size() - 1;
    int n = 1;
    while (n < need) {
        n <<= 1;
    }
    a.resize(n);
    b.resize(n);

    ntt(a, false);
    ntt(b, false);
    for (int i = 0; i < n; ++i) {
        a[i] = a[i] * b[i] % MOD;
    }
    ntt(a, true);

    a.resize(need);
    return a;
}
```

`n`은 반드시 2의 거듭제곱이어야 합니다. 결과 길이는 `a.size() + b.size() - 1`이고, padding된 뒤쪽 값은 잘라냅니다.

## 4. 왜 빨라지는가

계수 표현에서 다항식 곱셈은 convolution입니다.

```text
A(x) = a0 + a1*x + a2*x^2
B(x) = b0 + b1*x + b2*x^2
```

계수로 직접 곱하면 모든 쌍을 더해야 합니다. 하지만 여러 점 `x`에서의 값 표현으로 바꾸면 같은 점에서의 값끼리 곱하면 됩니다.

```text
C(x_i) = A(x_i) * B(x_i)
```

FFT/NTT는 이 값 표현으로 빠르게 변환하고 다시 계수로 되돌리는 알고리즘입니다.

## 5. 문제 모델링 예시

두 배열에서 합이 `k`가 되는 쌍의 수를 세고 싶다면 값 빈도 배열을 만듭니다.

```text
freqA[x] = A에서 값 x의 개수
freqB[y] = B에서 값 y의 개수
conv[k] = sum freqA[x] * freqB[k - x]
```

음수 값이 있으면 offset을 더해 index를 양수로 바꿉니다. 차이를 세고 싶으면 한쪽 배열을 뒤집거나 offset을 조정해 `x - y`를 `x + shifted(-y)` 형태로 만듭니다.

## 6. 임의 모듈러와 큰 정수

NTT는 특정 모듈러에서만 바로 됩니다. 결과를 `1,000,000,007` 같은 다른 mod로 내야 한다면 선택지가 있습니다.

| 상황 | 선택 |
| --- | --- |
| 정답 mod가 NTT friendly | 그 mod로 NTT |
| 정답 mod가 다르지만 계수가 작다 | 복소수 FFT 후 반올림 |
| 정확한 큰 정수 convolution 필요 | 여러 NTT mod + CRT |
| 길이가 작다 | 단순 `O(NM)`이 더 간단 |

대회에서는 제한과 오차 허용 여부를 보고 FFT와 NTT 중 하나를 고릅니다. 정수 정답이 정확히 필요하고 friendly mod가 주어지면 NTT가 안전합니다.

## 7. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| 단순 convolution | `O(NM)` | 결과 배열 |
| NTT 변환 1회 | `O(L log L)` | `O(L)` |
| convolution 전체 | `O(L log L)` | `O(L)` |

여기서 `L`은 결과 길이 이상인 가장 작은 2의 거듭제곱입니다. `N`, `M`이 몇 천 이하라면 단순 곱셈이 더 빠를 수도 있습니다. FFT/NTT는 구현 상수가 큽니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 길이를 2의 거듭제곱으로 맞추지 않음 | bit reversal/근 계산 오류 | `while (n < need) n <<= 1` |
| inverse transform에서 `n^{-1}` 곱 누락 | 결과가 n배 | invert 마지막 단계 확인 |
| 원시근이 mod와 맞지 않음 | 전부 오답 | mod와 primitive root 세트 확인 |
| 음수 계수 정규화 누락 | 모듈러 값 깨짐 | 입력을 `[0, MOD)`로 변환 |
| 결과 길이를 자르지 않음 | padding 값 출력 | `resize(need)` |
| 작은 입력에 무조건 NTT 사용 | 구현 복잡도/상수 손해 | 단순 곱셈과 비교 |

## 9. 문제를 볼 때 체크할 조건

1. 식이 `sum a[i] * b[k - i]` 형태인가?
2. index 합, 차이, pair count를 빈도 배열로 바꿀 수 있는가?
3. 결과 mod가 NTT friendly인가?
4. 입력 길이가 FFT/NTT를 쓸 만큼 큰가?
5. 음수 값이나 offset 처리가 필요한가?
6. 정확한 정수 결과가 필요한가, 반올림 오차가 허용되는가?

FFT와 NTT는 "곱셈을 빠르게 한다"보다 "이중 합을 convolution으로 모델링한다"가 더 중요합니다. 모델링이 convolution으로 떨어지면, 구현은 mod와 오차 조건에 맞춰 FFT 또는 NTT를 선택하면 됩니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 다항식 곱셈 `/practice/...` 문제 필요 | NTT 입출력과 결과 길이 처리 | polynomial multiplication |
| 표준 | TODO: 합이 k인 쌍 개수 `/practice/...` 문제 필요 | 빈도 배열 convolution | pair sum |
| 응용 | TODO: 차이별 pair count `/practice/...` 문제 필요 | 한쪽 배열 뒤집기와 offset | reversed convolution |
| 함정 | TODO: 다른 mod의 convolution `/practice/...` 문제 필요 | FFT 또는 여러 NTT mod 선택 | arbitrary modulus |
