# String Period Query Applications

String Period Query Applications는 border, period, runs 정보를 단일 문자열 판정에서 range/query 문제로 확장하는 문자열 응용 레슨입니다. Runs와 Periodicity를 배운 뒤, 여러 구간에 대해 "이 구간의 최소 주기는 무엇인가", "이 반복은 어디까지 확장되는가", "prefix와 suffix가 얼마나 겹치는가"를 빠르게 답하는 관점을 정리합니다.

이 레슨은 Runs와 문자열 주기, Suffix Array Applications, Border Automaton 이후에 보는 문자열 심화입니다.

1. 전체 문자열의 period와 substring period를 구분한다.
2. query가 online인지 offline인지에 따라 prefix/Z, suffix/LCP, hash 중 도구를 고른다.
3. 반복 판정은 후보 period를 만든 뒤 LCP/LCS로 확장 가능성을 확인한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: prefix function, Z algorithm, suffix array와 LCP, rolling hash, runs
- 함께 보면 좋은 레슨: Runs와 문자열 주기, Suffix Array Applications, Border Automaton
- 다음에 볼 레슨: suffix automaton applications, palindrome range DP, Lyndon factorization 응용

## 1. 문제 신호

| 문제 표현 | Period Query 관점 |
| --- | --- |
| 여러 substring이 반복 문자열인지 묻는다 | range minimal period |
| `s[l..r]`의 border 길이 | prefix/suffix equality query |
| 두 반복 구간을 합칠 수 있는가 | LCP/LCS와 Fine-Wilf |
| 특정 period `p`가 구간에 유효한가 | shifted equality check |
| 반복 구간을 update 없이 많이 묻는다 | suffix array RMQ 또는 rolling hash |

핵심은 "후보 period를 어떻게 만들 것인가"와 "그 period가 구간 전체에서 유지되는지 어떻게 검증할 것인가"입니다.

## 2. 전체 문자열과 구간 문자열

전체 문자열의 최소 period는 prefix function 하나로 충분합니다. 하지만 구간 `[l, r)`의 period는 그 구간을 따로 떼어낸 문자열 기준입니다.

```text
s = abababxababab
전체 문자열은 period 6도 완전 반복이 아니다.
구간 [0, 6) = ababab 은 period 2다.
구간 [7, 13) = ababab 도 period 2다.
```

query가 많으면 구간마다 prefix function을 새로 만들 수 없습니다. 구간 equality를 빠르게 확인하는 구조가 필요합니다.

## 3. 후보 Period 검증

구간 `[l, r)` 길이를 `len`, 후보 period를 `p`라고 합시다. `p`가 period라는 조건은 아래와 같습니다.

```text
s[l + i] == s[l + i + p] for 0 <= i < len - p
```

즉 두 substring이 같으면 됩니다.

```text
s[l, r-p) == s[l+p, r)
```

이 equality는 rolling hash, suffix array LCP, suffix automaton 기반 query 구조로 확인할 수 있습니다. 대회에서는 static string이면 rolling hash나 suffix array RMQ가 가장 실용적입니다.

## 4. Rolling Hash 기반 Equality

아래 코드는 단일 mod hash로 substring equality를 확인하는 형태입니다. 실전에서는 충돌 위험이 있으면 double hash를 씁니다.

```cpp compile-check
#include <string>
#include <vector>
using namespace std;

struct RollingHashPeriod {
    static const long long MOD = 1000000007LL;
    static const long long BASE = 911382323LL;

    vector<long long> power;
    vector<long long> prefix;

    explicit RollingHashPeriod(const string& s) {
        int n = (int)s.size();
        power.assign(n + 1, 1);
        prefix.assign(n + 1, 0);
        for (int i = 0; i < n; ++i) {
            power[i + 1] = power[i] * BASE % MOD;
            prefix[i + 1] = (prefix[i] * BASE + (unsigned char)s[i] + 1) % MOD;
        }
    }

    long long hashRange(int left, int right) const {
        long long value = prefix[right] - prefix[left] * power[right - left] % MOD;
        if (value < 0) {
            value += MOD;
        }
        return value;
    }

    bool same(int a, int b, int length) const {
        return hashRange(a, a + length) == hashRange(b, b + length);
    }
};

bool isPeriodInRange(const RollingHashPeriod& hash, int left, int right, int period) {
    int length = right - left;
    if (period <= 0 || period > length) {
        return false;
    }
    return hash.same(left, left + period, length - period);
}
```

후보 `p`가 구간 길이를 나누어야 하는지는 문제 표현에 따라 다릅니다. "완전히 반복되는 문자열"이면 `len % p == 0`이 필요하고, "period" 자체만 묻는다면 나누어떨어지지 않아도 됩니다.

## 5. Minimal Period Query

구간의 최소 period를 바로 찾는 것은 어렵습니다. 보통은 후보를 좁힙니다.

| 후보 생성 방식 | 쓸 수 있는 경우 |
| --- | --- |
| 길이의 약수 나열 | 완전 반복 판정 |
| prefix/border 후보 | 한쪽 끝이 고정된 query |
| runs 또는 maximal repeat | 반복 구간을 offline으로 모을 때 |
| binary search | monotone 조건이 있을 때만 가능 |

`p`가 period라고 해서 `p+1`도 period인 것은 아닙니다. 따라서 최소 period는 일반적인 binary search 대상이 아닙니다.

## 6. LCP/LCS로 반복 확장

반복 후보 `s[i..i+p)`가 두 번 이상 이어지는지 보려면 오른쪽 LCP와 왼쪽 LCS를 합칩니다.

```text
right = LCP(i, i+p)
left = LCS(i-1, i+p-1)
covered length = left + right
covered length >= p 이면 두 복사본이 겹치며 반복 구간을 만든다.
```

이 관점은 run 판정과 query 응용에서 중요합니다. 반복이 한 점에서만 보이는 것이 아니라 좌우로 얼마나 확장되는지 봐야 maximality를 확인할 수 있습니다.

## 7. 작은 예시

```text
s = zzabcabcabcy
query [2, 11) = abcabcabc
candidate p = 3

s[2, 8)  = abcabc
s[5, 11) = abcabc
두 구간이 같으므로 p=3은 period다.
len = 9, len % 3 = 0 이므로 완전 반복이다.
```

같은 구간에서 `p = 6`도 period입니다. 하지만 최소 period는 `3`입니다. 답이 "가능한 period 하나"인지 "최소 period"인지 문제에서 분리해야 합니다.

## 8. Query 구조 선택

| 상황 | 추천 도구 |
| --- | --- |
| static string, equality query만 많음 | rolling hash |
| LCP/LCS query가 많음 | suffix array + RMQ, reverse string RMQ |
| pattern 금지 DP와 연결 | border automaton |
| 모든 반복 구간을 나열 | runs enumeration |
| update가 있음 | rope/hash segment tree 같은 별도 구조 |

Rolling hash는 빠르지만 확률적입니다. 엄밀성이 필요한 환경이면 suffix array와 RMQ를 선택합니다.

## 9. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| rolling hash 전처리 | `O(N)` |
| substring equality | `O(1)` |
| 후보 약수 나열 | 보통 `O(sqrt N)` |
| suffix array + LCP RMQ 전처리 | `O(N log N)` 또는 구현에 따라 `O(N)` |
| LCP/LCS query | `O(1)` RMQ 이후 |

구간마다 모든 period 후보를 보는 방식은 최악에서 느립니다. query 수와 문자열 길이에 맞춰 후보 생성 방식을 제한해야 합니다.

## 10. 자주 하는 실수

1. `len % p == 0`이 필요한 문제와 아닌 문제를 섞는다.
2. 전체 문자열 prefix function 결과를 임의 구간에 그대로 적용한다.
3. `p`가 period인지 확인하지 않고 약수라는 이유만으로 답으로 쓴다.
4. hash 충돌 가능성을 무시해야 하는 문제에서 단일 hash만 사용한다.
5. run의 maximality를 보지 않고 같은 반복을 여러 번 센다.

## 11. 문제를 볼 때 체크할 조건

- query 대상이 전체 문자열인가, 임의 substring인가?
- 완전 반복인지, period 조건만 필요한지 구분했는가?
- 후보 period를 어디서 얻는가?
- equality 검증에 hash를 써도 되는가?
- 반복 구간의 좌우 확장 또는 maximality가 필요한가?

## 12. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: string period query `/practice/...` 문제 필요 | 후보 period 검증 | substring equality |
| 표준 | TODO: range minimal period `/practice/...` 문제 필요 | 약수 후보와 hash 결합 | rolling hash |
| 응용 | TODO: repeated substring query `/practice/...` 문제 필요 | LCP/LCS로 확장 길이 계산 | suffix array RMQ |
| 함정 | TODO: maximal run query `/practice/...` 문제 필요 | maximality와 중복 제거 | runs |

