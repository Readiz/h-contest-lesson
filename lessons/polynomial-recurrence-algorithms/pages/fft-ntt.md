# FFT와 NTT

FFT와 NTT는 다항식 곱셈, 즉 convolution을 빠르게 계산하는 기법입니다. 두 배열 `a`, `b`에 대해 `c[k] = sum a[i] * b[k - i]`를 직접 계산하면 `O(NM)`이지만, FFT/NTT를 쓰면 대략 `O(N log N)`에 처리할 수 있습니다.


NTT 입력 계수는 `[0,998244353)`로 정규화하고, padding한 길이는 2의 거듭제곱이며 `2^23` 이하여야 합니다. 여러 NTT 소수의 CRT로 정수 계수를 복원하려면 modulus 곱이 계수 상한보다 커야 합니다(부호가 있으면 절댓값 상한의 두 배). 그 뒤 목표 modulus로 줄입니다.

## Convolution 신호

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

## FFT와 NTT 차이

| 방식 | 값 타입 | 장점 | 주의점 |
| --- | --- | --- | --- |
| FFT | 복소수 | 임의 정수/실수 계수에 넓게 사용 | 반올림 오차 |
| NTT | 모듈러 정수 | 정확한 정수 계산 | 특정 mod와 원시근 필요 |

대회에서 결과를 `998244353`으로 나누는 문제가 많으면 NTT가 가장 편합니다. `998244353 = 119 * 2^23 + 1`이고 원시근 `3`을 쓸 수 있어 길이 `2^23`까지 NTT가 가능합니다.

## NTT 구현

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

## 왜 빨라지는가

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

## 문제 모델링 예시

두 배열에서 합이 `k`가 되는 쌍의 수를 세고 싶다면 값 빈도 배열을 만듭니다.

```text
freqA[x] = A에서 값 x의 개수
freqB[y] = B에서 값 y의 개수
conv[k] = sum freqA[x] * freqB[k - x]
```

음수 값이 있으면 offset을 더해 index를 양수로 바꿉니다. 차이를 세고 싶으면 한쪽 배열을 뒤집거나 offset을 조정해 `x - y`를 `x + shifted(-y)` 형태로 만듭니다.

## 임의 모듈러와 큰 정수

NTT는 특정 모듈러에서만 바로 됩니다. 결과를 `1,000,000,007` 같은 다른 mod로 내야 한다면 선택지가 있습니다.

| 상황 | 선택 |
| --- | --- |
| 정답 mod가 NTT friendly | 그 mod로 NTT |
| 정답 mod가 다르지만 계수가 작다 | 복소수 FFT 후 반올림 |
| 정확한 큰 정수 convolution 필요 | 여러 NTT mod + CRT |
| 길이가 작다 | 단순 `O(NM)`이 더 간단 |

대회에서는 제한과 오차 허용 여부를 보고 FFT와 NTT 중 하나를 고릅니다. 정수 정답이 정확히 필요하고 friendly mod가 주어지면 NTT가 안전합니다.

## 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| 단순 convolution | `O(NM)` | 결과 배열 |
| NTT 변환 1회 | `O(L log L)` | `O(L)` |
| convolution 전체 | `O(L log L)` | `O(L)` |

여기서 `L`은 결과 길이 이상인 가장 작은 2의 거듭제곱입니다. `N`, `M`이 몇 천 이하라면 단순 곱셈이 더 빠를 수도 있습니다. FFT/NTT는 구현 상수가 큽니다.
