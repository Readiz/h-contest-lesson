# Runs와 문자열 주기

Runs와 Periodicity는 문자열 안에서 반복되는 구간을 구조적으로 다루는 주제입니다. KMP의 border, Z algorithm의 일치 길이, Suffix 구조를 배운 뒤 "반복이 어디에 얼마나 조밀하게 있는가"를 보는 단계입니다.

이 레슨은 Suffix Tree와 Ukkonen 이후에 보는 문자열 심화입니다.

1. 주기 `p`는 `s[i] == s[i + p]`가 반복되는 간격이다.
2. border는 문자열 전체의 prefix이면서 suffix인 길이다.
3. run은 같은 minimal period가 두 번 이상 반복되는 maximal substring이다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: prefix function, Z algorithm, suffix array/tree, gcd 성질
- 함께 보면 좋은 레슨: KMP/Z, Suffix Array와 LCP, Suffix Tree와 Ukkonen
- 다음에 볼 레슨: suffix array applications, Lyndon 기반 run enumeration, periodicity 응용

## 1. 문제 신호

| 문제 표현 | Periodicity 관점 |
| --- | --- |
| 문자열이 어떤 패턴의 반복인지 판정 | minimal period |
| prefix와 suffix가 겹친다 | border chain |
| 같은 substring이 촘촘하게 반복된다 | period와 run |
| 반복 구간을 모두 세거나 압축한다 | runs theorem |
| cyclic shift나 최소 회전이 등장한다 | period, Lyndon factorization |

반복을 단순히 `O(N^2)`로 비교하면 금방 터집니다. 먼저 "전체 문자열의 주기"인지, "구간별 반복"인지, "모든 maximal 반복"인지 범위를 분리해야 합니다.

## 2. Period와 Border

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

## 3. Prefix Function으로 전체 주기 찾기

아래 함수는 문자열 전체의 최소 반복 단위를 찾습니다. 완전히 반복되지 않으면 원래 길이를 반환합니다.

```cpp compile-check
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

int minimalPeriodLength(const string& s) {
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
    int period = minimalPeriodLength(s);
    return period > 0 && period < (int)s.size();
}
```

이 판정은 "전체 문자열" 기준입니다. 부분 문자열의 반복까지 모두 찾으려면 suffix/LCP나 run enumeration이 필요합니다.

## 4. Border Chain

가장 긴 border만 보는 것으로 부족할 때는 border chain을 따라 내려갑니다.

```cpp compile-check
#include <algorithm>
#include <string>
#include <vector>
using namespace std;

vector<int> prefixFunctionBorder(const string& s) {
    vector<int> pi(s.size(), 0);
    for (int i = 1; i < (int)s.size(); ++i) {
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

vector<int> allBorderLengths(const string& s) {
    vector<int> pi = prefixFunctionBorder(s);
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

Border chain은 "이 prefix가 몇 번 등장하는가", "접두사와 접미사가 동시에 되는 길이" 같은 문제에서 자주 쓰입니다.

## 5. Fine-Wilf 관점

문자열이 period `p`와 `q`를 동시에 갖고 길이가 충분히 길면 `gcd(p, q)`도 period가 됩니다.

```text
length >= p + q - gcd(p, q)
```

이 성질은 반복 구간이 겹칠 때 period가 더 작은 값으로 합쳐지는 이유를 설명합니다. Runs theorem의 핵심 직관도 "서로 너무 많이 겹치는 반복은 독립적으로 많아질 수 없다"입니다.

## 6. Run의 정의

Run은 아래 조건을 만족하는 substring `[l, r)`입니다.

1. 길이 `r - l`이 최소 period `p`의 두 배 이상이다.
2. 왼쪽이나 오른쪽으로 한 글자 더 확장해도 같은 period `p`를 유지할 수 없다.
3. `p`가 그 구간의 최소 period다.

```text
aaaaa 에는 period 1 run이 하나 있다.
abcabcabcx 에는 abc 반복 구간이 run 후보가 된다.
```

모든 run의 개수는 `O(N)`개입니다. 이 사실이 없으면 "모든 maximal 반복"을 출력하는 문제는 감당하기 어렵습니다.

## 7. 구현 전략 선택

| 목표 | 보통 쓰는 도구 |
| --- | --- |
| 전체 문자열 반복 판정 | prefix function |
| 모든 prefix의 border 통계 | prefix function tree |
| 두 substring의 LCP/LCS | suffix array + RMQ 또는 suffix tree |
| 모든 run enumeration | Lyndon factorization 기반 알고리즘 |
| cyclic shift와 최소 회전 | Duval algorithm |

대회에서는 run enumeration 전체 구현보다, prefix/Z/suffix 구조로 필요한 반복만 좁히는 문제가 더 흔합니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| prefix function | `O(N)` |
| 전체 minimal period | `O(N)` |
| border chain 출력 | border 개수에 비례 |
| 모든 run enumeration | 알려진 알고리즘으로 `O(N)` 또는 `O(N log N)` 구현 가능 |

## 9. 자주 하는 실수

1. `n - longestBorder`가 period 후보라는 것과 `n % p == 0` 조건을 섞는다.
2. 전체 문자열 반복 판정을 부분 문자열 반복 판정으로 착각한다.
3. 같은 period를 유지하며 더 확장 가능한 구간을 run으로 세어 중복을 만든다.
4. `abababa`처럼 마지막 반복이 덜 끝나는 문자열을 완전 반복으로 처리한다.
5. border 길이와 period 길이를 같은 의미로 쓴다.

## 10. 문제를 볼 때 체크할 조건

- 전체 문자열만 보면 되는가, 임의 substring을 봐야 하는가?
- 반복 단위가 정확히 몇 번 반복되어야 하는가?
- maximal 반복 구간이 필요한가, 존재 여부만 필요한가?
- 주기 후보가 여러 개일 때 최소 period가 필요한가?
- cyclic shift나 reverse가 섞여 period가 깨지는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 문자열 전체 반복 판정 `/practice/...` 문제 필요 | longest border로 minimal period 계산 | prefix function |
| 표준 | TODO: 모든 border 길이 `/practice/...` 문제 필요 | failure link chain 순회 | border tree |
| 응용 | TODO: 반복 substring 개수 `/practice/...` 문제 필요 | LCP와 period 후보 결합 | periodic substring |
| 함정 | TODO: maximal run 판정 `/practice/...` 문제 필요 | 좌우 확장 가능성과 minimal period 구분 | runs theorem |
