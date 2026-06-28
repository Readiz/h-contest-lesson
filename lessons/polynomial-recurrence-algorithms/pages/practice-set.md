# Practice Set

Polynomial and Recurrence Algorithms 계열은 모델링 실수가 많으므로 작은 naive 구현과 비교하는 연습이 중요합니다. 아직 적절한 h-contest 문제 링크가 없는 항목은 임의 ID를 만들지 않고, 이 페이지에 로컬 완결형 연습과 검증 기준을 둡니다.

## 대표 로컬 연습: K차 선형 점화식의 N번째 항

고정된 소수 mod `998244353`에서 아래 점화식을 따르는 수열의 `a_N`을 구합니다.

```text
a_n = c0*a_{n-1} + c1*a_{n-2} + ... + c_{K-1}*a_{n-K}
```

초기항은 `a_0, a_1, ..., a_{K-1}` 순서로 주어집니다.

### 입력

```text
K N
a_0 a_1 ... a_{K-1}
c0 c1 ... c_{K-1}
```

- `1 <= K <= 2000`
- `0 <= N <= 10^18`
- 모든 항과 계수는 `0 <= value < 998244353`

### 출력

```text
a_N mod 998244353
```

### 예시

```text
2 10
0 1
1 1
```

```text
55
```

Fibonacci를 `F_0 = 0`, `F_1 = 1`, `F_n = F_{n-1} + F_{n-2}`로 둔 입력입니다.

## 손으로 따라가는 Trace

Fibonacci의 companion relation은 아래입니다.

```text
x^2 = x + 1
```

따라서 `x^N mod (x^2 - x - 1)`을 `p0 + p1*x` 꼴로 줄이면:

```text
F_N = p0*F_0 + p1*F_1
```

`N = 10`일 때 필요한 거듭제곱은 아래처럼 줄어듭니다.

| 항 | 줄이기 전 | relation 적용 후 | 계수 `[p0, p1]` |
| --- | --- | --- | --- |
| `x^1` | `x` | `x` | `[0, 1]` |
| `x^2` | `x^2` | `x + 1` | `[1, 1]` |
| `x^4` | `(x + 1)^2 = x^2 + 2x + 1` | `3x + 2` | `[2, 3]` |
| `x^8` | `(3x + 2)^2 = 9x^2 + 12x + 4` | `21x + 13` | `[13, 21]` |
| `x^10` | `x^8 * x^2 = (21x + 13)(x + 1)` | `55x + 34` | `[34, 55]` |

마지막 계수 `[34, 55]`로 `34*F_0 + 55*F_1 = 55`가 됩니다.

## 구현 기준

```cpp compile-check
#include <iostream>
#include <vector>
using namespace std;

const long long MOD = 998244353;

long long normalize(long long value) {
    value %= MOD;
    if (value < 0) {
        value += MOD;
    }
    return value;
}

vector<long long> combine(
    const vector<long long>& left,
    const vector<long long>& right,
    const vector<long long>& coeff
) {
    int k = (int)coeff.size();
    vector<long long> temp(2 * k - 1, 0);

    for (int i = 0; i < k; ++i) {
        for (int j = 0; j < k; ++j) {
            temp[i + j] = (temp[i + j] + left[i] * right[j]) % MOD;
        }
    }

    for (int degree = 2 * k - 2; degree >= k; --degree) {
        long long value = temp[degree];
        if (value == 0) {
            continue;
        }
        for (int j = 1; j <= k; ++j) {
            temp[degree - j] = (temp[degree - j] + value * coeff[j - 1]) % MOD;
        }
    }

    temp.resize(k);
    return temp;
}

vector<long long> coefficientOfPower(long long n, const vector<long long>& coeff) {
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
            result = combine(result, base, coeff);
        }
        base = combine(base, base, coeff);
        n >>= 1LL;
    }

    return result;
}

long long nthTerm(
    const vector<long long>& initial,
    const vector<long long>& coeff,
    long long n
) {
    if (n < (long long)initial.size()) {
        return normalize(initial[(int)n]);
    }

    vector<long long> weight = coefficientOfPower(n, coeff);
    long long answer = 0;
    for (int i = 0; i < (int)initial.size(); ++i) {
        answer = (answer + weight[i] * normalize(initial[i])) % MOD;
    }
    return answer;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int k;
    long long n;
    cin >> k >> n;

    vector<long long> initial(k), coeff(k);
    for (long long& value : initial) {
        cin >> value;
        value = normalize(value);
    }
    for (long long& value : coeff) {
        cin >> value;
        value = normalize(value);
    }

    cout << nthTerm(initial, coeff, n) << '\n';
}
```

## 검증용 Case

| 입력 요약 | 기대값 | 확인 포인트 |
| --- | ---: | --- |
| `K=2`, Fibonacci, `N=0` | 0 | 초기항을 바로 반환 |
| `K=2`, Fibonacci, `N=1` | 1 | 초기항 index가 0-based |
| `K=2`, Fibonacci, `N=10` | 55 | coefficient trace와 일치 |
| `K=1`, `a_n=3a_{n-1}`, `a_0=2`, `N=4` | 162 | `k=1`에서 `x mod P(x)=c0` 처리 |
| `K=3`, tribonacci `0,0,1`, coeff `1,1,1`, `N=5` | 4 | reduction 방향 검증 |

## Stress 기준

작은 입력에서는 직접 점화식을 전개하는 naive 구현과 비교합니다.

1. `K <= 6`, `N <= 80`으로 random initial/coeff를 생성합니다.
2. naive로 `a_K`부터 `a_N`까지 순서대로 계산합니다.
3. 같은 입력을 Kitamasa 구현에 넣어 결과가 같은지 비교합니다.
4. `K=1`, `N<K`, 계수가 0인 경우, 모든 초기항이 0인 경우를 별도 deterministic case로 둡니다.

Berlekamp-Massey와 연결할 때는 BM이 찾은 coeff로 이 연습의 `nthTerm`을 호출하고, BM에 쓰지 않은 holdout 항을 하나 더 비교해야 합니다.

## 다음 연습 후보

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 표준 | 로컬: K차 선형 점화식의 N번째 항 | Kitamasa `O(K^2 log N)` 구현 | linear recurrence |
| 입문 | TODO: polynomial multiplication `/practice/...` 문제 필요 | NTT 입출력과 결과 길이 처리 | convolution |
| 입문 | TODO: polynomial inverse `/practice/...` 문제 필요 | FPS inverse와 truncate | Newton iteration |
| 표준 | TODO: multipoint evaluation `/practice/...` 문제 필요 | subproduct tree | polynomial remainder |
| 표준 | TODO: interpolation `/practice/...` 문제 필요 | Lagrange basis | interpolation |
| 응용 | TODO: generating function coefficient `/practice/...` 문제 필요 | rational form 계수 추출 | Bostan-Mori |
| 심화 | TODO: Berlekamp-Massey `/practice/...` 문제 필요 | 앞 항에서 최소 점화식 찾기 | discrepancy |

## 완료 기준

- 작은 차수 naive polynomial 연산과 비교합니다.
- mod/root/primitive root 조건을 명시합니다.
- FPS 연산의 상수항 조건을 확인합니다.
- BM 결과는 holdout 항으로 검증합니다.
- n번째 항 알고리즘은 0-index/1-index를 고정합니다.
- 점화식 계수 순서를 `a_{n-1}`부터 `a_{n-K}`까지로 고정합니다.
