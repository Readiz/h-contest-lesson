# Runs와 문자열 주기

Runs와 Periodicity는 문자열 안에서 반복되는 구간을 구조적으로 다루는 주제입니다. KMP의 border, Z algorithm의 일치 길이, Suffix 구조를 배운 뒤 "반복이 어디에 얼마나 조밀하게 있는가"를 보는 단계입니다.


일반 주기는 나누어떨어질 필요가 없습니다. 비어 있지 않은 문자열의 최소 주기는 `N-pi[N-1]`입니다. 아래 `smallestRepeatingBlockLength`는 문자열 전체를 같은 블록으로 정확히 분할하는 최소 블록 길이를 구하므로 추가로 나눗셈 조건을 검사합니다.

## 문제 신호

| 문제 표현 | Periodicity 관점 |
| --- | --- |
| 문자열이 어떤 패턴의 반복인지 판정 | minimal period |
| prefix와 suffix가 겹친다 | border chain |
| 같은 substring이 촘촘하게 반복된다 | period와 run |
| 반복 구간을 모두 세거나 압축한다 | runs theorem |
| cyclic shift나 최소 회전이 등장한다 | period, Lyndon factorization |

반복을 단순히 `O(N^2)`로 비교하면 금방 터집니다. 먼저 "전체 문자열의 주기"인지, "구간별 반복"인지, "모든 maximal 반복"인지 범위를 분리해야 합니다.

## Period와 Border

길이 `n` 문자열의 period가 `p`라는 뜻은 아래 조건입니다.

```text
0 <= i < n - p 에 대해 s[i] == s[i + p]
```

전체 문자열에서 길이 `b` border가 있으면 `p = n - b`가 period 후보입니다. `n % p == 0`이면 문자열 전체가 길이 `p` 패턴의 반복입니다.

```text
s = abcabcabc
longest border = abcabc, length 6
period candidate = 9 - 6 = 3
```

## Prefix Function으로 전체 주기 찾기

아래 함수는 문자열 전체의 최소 반복 단위를 찾습니다. 완전히 반복되지 않으면 원래 길이를 반환합니다.

```cpp compile-check
#include <algorithm>
#include <string>
#include <vector>
using namespace std;

vector<int> prefixFunctionPeriod(const string& s) {
    int n = (int)s.size();
    vector<int> pi(n, 0);
    for (int i = 1; i < n; ++i) {
        int j = pi[i - 1];
        while (j > 0 && s[i] != s[j]) {
            j = pi[j - 1];
        }
        if (s[i] == s[j]) {
            ++j;
        }
        pi[i] = j;
    }
    return pi;
}

int smallestRepeatingBlockLength(const string& s) {
    if (s.empty()) {
        return 0;
    }
    vector<int> pi = prefixFunctionPeriod(s);
    int n = (int)s.size();
    int candidate = n - pi[n - 1];
    if (candidate != n && n % candidate == 0) {
        return candidate;
    }
    return n;
}

bool isWholeStringRepetition(const string& s) {
    int period = smallestRepeatingBlockLength(s);
    return period > 0 && period < (int)s.size();
}

vector<int> allBorderLengths(const string& s) {
    vector<int> pi = prefixFunctionPeriod(s);
    vector<int> borders;
    int current = s.empty() ? 0 : pi.back();
    while (current > 0) {
        borders.push_back(current);
        current = pi[current - 1];
    }
    reverse(borders.begin(), borders.end());
    return borders;
}
```

이 판정은 "전체 문자열" 기준입니다. 부분 문자열의 반복까지 모두 찾으려면 suffix/LCP나 run enumeration이 필요합니다.

## Border Chain

가장 긴 border만 보는 것으로 부족할 때는 border chain을 따라 내려갑니다.

`allBorderLengths`는 위 구현의 실패 링크를 따라갑니다.

Border chain은 "이 prefix가 몇 번 등장하는가", "접두사와 접미사가 동시에 되는 길이" 같은 문제에서 자주 쓰입니다.

## Fine-Wilf 관점

문자열이 period `p`와 `q`를 동시에 갖고 길이가 충분히 길면 `gcd(p, q)`도 period가 됩니다.

```text
length >= p + q - gcd(p, q)
```

이 성질은 반복 구간이 겹칠 때 period가 더 작은 값으로 합쳐지는 이유를 설명합니다. Runs theorem의 핵심 직관도 "서로 너무 많이 겹치는 반복은 독립적으로 많아질 수 없다"입니다.

## Run의 정의

Run은 아래 조건을 만족하는 substring `[l, r)`입니다.

1. 길이 `r - l`이 최소 period `p`의 두 배 이상이다.
2. 왼쪽이나 오른쪽으로 한 글자 더 확장해도 같은 period `p`를 유지할 수 없다.
3. `p`가 그 구간의 최소 period다.

```text
aaaaa 에는 period 1 run이 하나 있다.
abcabcabcx 에는 abc 반복 구간이 run 후보가 된다.
```

모든 run의 개수는 `O(N)`개입니다. 이 사실이 없으면 "모든 maximal 반복"을 출력하는 문제는 감당하기 어렵습니다.

## 구현 전략 선택

| 목표 | 보통 쓰는 도구 |
| --- | --- |
| 전체 문자열 반복 판정 | prefix function |
| 모든 prefix의 border 통계 | prefix function tree |
| 두 substring의 LCP/LCS | suffix array + RMQ 또는 suffix tree |
| 모든 run enumeration | Lyndon factorization 기반 알고리즘 |
| cyclic shift와 최소 회전 | Duval algorithm |

대회에서는 run enumeration 전체 구현보다, prefix/Z/suffix 구조로 필요한 반복만 좁히는 문제가 더 흔합니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| prefix function | `O(N)` |
| 전체 minimal period | `O(N)` |
| border chain 출력 | border 개수에 비례 |
| 모든 run enumeration | 알려진 알고리즘으로 `O(N)` 또는 `O(N log N)` 구현 가능 |

## 전체 문자열과 구간 문자열

전체 문자열의 최소 period는 prefix function 하나로 충분합니다. 하지만 구간 `[l, r)`의 period는 그 구간을 따로 떼어낸 문자열 기준입니다.

```text
s = abababxababab
전체 문자열은 period 6도 완전 반복이 아니다.
구간 [0, 6) = ababab 은 period 2다.
구간 [7, 13) = ababab 도 period 2다.
```

query가 많으면 구간마다 prefix function을 새로 만들 수 없습니다. 구간 equality를 빠르게 확인하는 구조가 필요합니다.

## 후보 Period 검증

구간 `[l, r)` 길이를 `len`, 후보 period를 `p`라고 합시다. `p`가 period라는 조건은 아래와 같습니다.

```text
s[l + i] == s[l + i + p] for 0 <= i < len - p
```

즉 두 substring이 같으면 됩니다.

```text
s[l, r-p) == s[l+p, r)
```

이 equality는 rolling hash, suffix array LCP, suffix automaton 기반 query 구조로 확인할 수 있습니다. 대회에서는 static string이면 rolling hash나 suffix array RMQ가 가장 실용적입니다.

## Rolling Hash 기반 Equality

[KMP·Z와 문자열 해시 자료](https://h.readiz.com/learn/string-matching-kmp-z)와 기존 Rolling Hash의 구간 비교를 재사용합니다. 길이 `L`인 구간에서 `0 < p <= L`일 때 앞 `L-p`자와 뒤 `L-p`자가 같은지 비교하면 됩니다. 해시 일치는 충돌 가능성이 있습니다.

후보 `p`가 구간 길이를 나누어야 하는지는 문제 표현에 따라 다릅니다. "완전히 반복되는 문자열"이면 `len % p == 0`이 필요하고, "period" 자체만 묻는다면 나누어떨어지지 않아도 됩니다.

## Minimal Period Query

구간의 최소 period를 바로 찾는 것은 어렵습니다. 보통은 후보를 좁힙니다.

| 후보 생성 방식 | 쓸 수 있는 경우 |
| --- | --- |
| 길이의 약수 나열 | 완전 반복 판정 |
| prefix/border 후보 | 한쪽 끝이 고정된 query |
| runs 또는 maximal repeat | 반복 구간을 offline으로 모을 때 |
| binary search | monotone 조건이 있을 때만 가능 |

`p`가 period라고 해서 `p+1`도 period인 것은 아닙니다. 따라서 최소 period는 일반적인 binary search 대상이 아닙니다.

## LCP/LCS로 반복 확장

거리 `p`인 두 위치의 일치 구간을 왼쪽으로 `left`, 오른쪽으로 `right`만큼 확장하면 주기 구간의 길이는 `left+right+p`입니다. `left+right >= p`이면 길이가 최소 `2p`인 반복을 얻습니다. 경계를 넘지 않도록 확장 길이를 제한합니다.

## 작은 예시

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

## Query 구조 선택

| 상황 | 추천 도구 |
| --- | --- |
| static string, equality query만 많음 | rolling hash |
| LCP/LCS query가 많음 | suffix array + RMQ, reverse string RMQ |
| pattern 금지 DP와 연결 | border automaton |
| 모든 반복 구간을 나열 | runs enumeration |
| update가 있음 | rope/hash segment tree 같은 별도 구조 |

Rolling hash는 빠르지만 확률적입니다. 엄밀성이 필요한 환경이면 suffix array와 RMQ를 선택합니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| rolling hash 전처리 | `O(N)` |
| substring equality | `O(1)` |
| 후보 약수 나열 | 보통 `O(sqrt N)` |
| suffix array + LCP RMQ 전처리 | `O(N log N)` 또는 구현에 따라 `O(N)` |
| LCP/LCS query | `O(1)` RMQ 이후 |

구간마다 모든 period 후보를 보는 방식은 최악에서 느립니다. query 수와 문자열 길이에 맞춰 후보 생성 방식을 제한해야 합니다.
