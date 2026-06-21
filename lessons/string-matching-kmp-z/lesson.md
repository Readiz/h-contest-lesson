# 문자열 매칭: KMP, Z, Rolling Hash

문자열 알고리즘의 첫 목표는 긴 텍스트 안에서 패턴이 어디에 등장하는지 빠르게 찾는 것입니다. 단순히 모든 시작 위치에서 패턴을 비교하면 최악의 경우 `O(NM)`이 됩니다. 텍스트 길이 `N`, 패턴 길이 `M`이 수십만 이상이면 다른 구조가 필요합니다.

이 레슨은 대표적인 세 도구를 한 번에 비교합니다.

| 도구 | 핵심 감각 | 주로 쓰는 상황 |
| --- | --- | --- |
| KMP | 패턴 내부의 접두사/접미사 정보를 이용해 되돌아가지 않는다 | 한 패턴을 텍스트에서 정확히 찾기 |
| Z algorithm | 각 위치에서 시작하는 접두사 일치 길이를 한 번에 계산한다 | 접두사 기준 매칭, 문자열 분석 |
| Rolling Hash | 부분 문자열을 숫자 해시로 비교한다 | 여러 구간 비교, 빠른 후보 판별 |

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 배열, 반복문, `string`, 복잡도 감각
- 함께 보면 좋은 레슨: 대회용 C++ 기본기, 모듈러 연산과 빠른 거듭제곱
- 다음에 볼 레슨: Trie와 Aho-Corasick, Suffix Array와 LCP

## 1. 단순 비교가 느려지는 이유

텍스트 `text`의 모든 시작 위치에서 패턴 `pattern`을 비교하면 아래처럼 됩니다.

```text
for start in 0..N-M:
    for i in 0..M-1:
        compare text[start+i] and pattern[i]
```

`text = aaaaa....a`, `pattern = aaa...ab`처럼 앞부분이 계속 일치하다가 마지막에서 틀리는 입력은 같은 문자를 여러 번 비교합니다. 이 경우 최악 시간 복잡도는 `O(NM)`입니다.

문자열 매칭 알고리즘은 이 반복 비교를 줄입니다. 핵심 질문은 "이미 비교한 정보를 다음 위치에서 재사용할 수 있는가"입니다.

## 2. KMP와 실패 함수

KMP는 패턴 내부에서 **접두사이면서 접미사인 가장 긴 길이**를 미리 계산합니다. 보통 이 배열을 `pi` 또는 failure function이라고 부릅니다.

예를 들어 `pattern = ababc`에서 앞부분 `abab`까지 봤다면, 접두사 `ab`와 접미사 `ab`가 일치합니다. 다음 문자가 틀렸을 때 패턴을 처음부터 다시 비교하지 않고, 이미 맞는 `ab` 길이만큼 상태를 유지할 수 있습니다.

```cpp compile-check
#include <string>
#include <vector>
using namespace std;

vector<int> prefixFunction(const string& pattern) {
    int n = (int)pattern.size();
    vector<int> pi(n, 0);
    for (int i = 1; i < n; ++i) {
        int j = pi[i - 1];
        while (j > 0 && pattern[i] != pattern[j]) {
            j = pi[j - 1];
        }
        if (pattern[i] == pattern[j]) {
            ++j;
        }
        pi[i] = j;
    }
    return pi;
}
```

`j`는 현재까지 맞은 패턴 길이입니다. 문자가 틀리면 `pi[j - 1]`로 되돌아가는데, 이 값은 "이미 맞은 접미사를 패턴의 접두사로 다시 쓸 수 있는 최대 길이"입니다.

## 3. KMP로 패턴 찾기

`pi`를 계산한 뒤에는 텍스트를 왼쪽에서 오른쪽으로 한 번만 훑습니다.

```cpp compile-check
#include <string>
#include <vector>
using namespace std;

vector<int> prefixFunction(const string& pattern) {
    int n = (int)pattern.size();
    vector<int> pi(n, 0);
    for (int i = 1; i < n; ++i) {
        int j = pi[i - 1];
        while (j > 0 && pattern[i] != pattern[j]) {
            j = pi[j - 1];
        }
        if (pattern[i] == pattern[j]) {
            ++j;
        }
        pi[i] = j;
    }
    return pi;
}

vector<int> kmpSearch(const string& text, const string& pattern) {
    vector<int> result;
    if (pattern.empty()) {
        return result;
    }

    vector<int> pi = prefixFunction(pattern);
    int matched = 0;
    for (int i = 0; i < (int)text.size(); ++i) {
        while (matched > 0 && text[i] != pattern[matched]) {
            matched = pi[matched - 1];
        }
        if (text[i] == pattern[matched]) {
            ++matched;
        }
        if (matched == (int)pattern.size()) {
            result.push_back(i - matched + 1);
            matched = pi[matched - 1];
        }
    }
    return result;
}
```

시간 복잡도는 `O(N + M)`입니다. `matched`가 증가하거나, 실패 함수로 감소하는 이동 전체가 선형 횟수 안에 묶이기 때문입니다.

## 4. Z algorithm

Z algorithm은 문자열 `s`의 각 위치 `i`에 대해 `s[i...]`가 `s[0...]`와 얼마나 길게 일치하는지를 계산합니다. 이 값을 `z[i]`라고 합니다.

```text
s = aabcaab
z[4] = 3  // s[4..] = aab, 접두사 aab와 3글자 일치
```

패턴을 텍스트에서 찾고 싶다면 `pattern + separator + text`를 만들고 Z 값을 계산합니다. 텍스트 영역에서 `z[i] >= pattern.size()`인 위치가 등장 위치입니다.

```cpp compile-check
#include <algorithm>
#include <string>
#include <vector>
using namespace std;

vector<int> zFunction(const string& s) {
    int n = (int)s.size();
    vector<int> z(n, 0);
    int left = 0;
    int right = 0;
    for (int i = 1; i < n; ++i) {
        if (i <= right) {
            z[i] = min(right - i + 1, z[i - left]);
        }
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) {
            ++z[i];
        }
        if (i + z[i] - 1 > right) {
            left = i;
            right = i + z[i] - 1;
        }
    }
    return z;
}
```

Z algorithm도 `O(N)`입니다. 접두사와 일치하는 구간 `[left, right]`를 유지하면서, 이미 아는 구간 안에서는 값을 재사용합니다.

## 5. Rolling Hash

Rolling Hash는 문자열을 숫자로 바꿔 부분 문자열 비교를 빠르게 하는 방법입니다. 접두사 해시를 전처리하면 임의 구간의 해시를 `O(1)`에 얻을 수 있습니다.

```cpp compile-check
#include <string>
#include <vector>
using namespace std;

const long long MOD = 1000000007LL;
const long long BASE = 911382323LL;

struct RollingHash {
    vector<long long> hash;
    vector<long long> power;

    explicit RollingHash(const string& s) {
        int n = (int)s.size();
        hash.assign(n + 1, 0);
        power.assign(n + 1, 1);
        for (int i = 0; i < n; ++i) {
            hash[i + 1] = (hash[i] * BASE + (unsigned char)s[i] + 1) % MOD;
            power[i + 1] = power[i] * BASE % MOD;
        }
    }

    long long get(int left, int right) const {
        long long value = (hash[right] - hash[left] * power[right - left]) % MOD;
        if (value < 0) {
            value += MOD;
        }
        return value;
    }
};
```

`get(left, right)`는 반열린 구간 `[left, right)`의 해시를 돌려줍니다. 같은 길이의 두 구간 해시가 같으면 문자열도 같을 가능성이 높습니다. 하지만 해시는 충돌할 수 있으므로, 정답 판정에 민감한 문제에서는 두 mod를 쓰거나 최종 후보를 직접 비교하는 방식을 고려합니다.

## 6. 무엇을 선택할까

| 문제 신호 | 우선 후보 |
| --- | --- |
| 한 패턴의 모든 등장 위치 | KMP 또는 Z |
| 접두사와 각 suffix의 일치 길이 | Z algorithm |
| 많은 부분 문자열 동등성 비교 | Rolling Hash |
| 여러 패턴을 동시에 찾기 | Trie, Aho-Corasick |
| 사전순 suffix 정렬, LCP 질의 | Suffix Array, LCP |

KMP와 Z는 정확한 선형 알고리즘입니다. Rolling Hash는 구현이 짧고 여러 구간 비교에 강하지만 충돌 가능성을 관리해야 합니다.

## 7. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| KMP 실패 함수 | `O(M)` | `O(M)` |
| KMP 검색 | `O(N + M)` | `O(M)` |
| Z function | `O(N)` | `O(N)` |
| Rolling Hash 전처리 | `O(N)` | `O(N)` |
| Rolling Hash 구간 비교 | `O(1)` | 전처리 배열 사용 |

입력 문자열이 여러 개인 경우에는 전체 길이 합을 기준으로 봐야 합니다. 테스트 케이스마다 큰 문자열을 복사하거나 `substr`를 많이 만들면 의도한 복잡도보다 느려질 수 있습니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| KMP에서 매칭 후 `matched = 0`으로 초기화 | 겹치는 등장 위치 누락 | `pi[matched - 1]`로 이동 |
| Z에서 구간 경계 `right`를 inclusive/exclusive로 혼동 | off-by-one 오답 | `[left, right]` inclusive로 통일 |
| 패턴과 텍스트 사이 구분자를 생략 | 경계 넘어 매칭 | 입력에 없는 separator 사용 |
| Rolling Hash 충돌을 무시 | 낮은 확률의 오답 | double hash 또는 후보 직접 비교 |
| `substr`를 반복 생성 | 시간/메모리 증가 | 인덱스와 해시로 비교 |
| 문자 signedness를 고려하지 않음 | 음수 문자가 해시에 섞임 | `(unsigned char)s[i]` 사용 |

## 9. 문제를 볼 때 체크할 조건

1. 패턴이 하나인가, 여러 개인가?
2. 정확한 등장 위치가 필요한가, 부분 문자열이 같은지만 확인하면 되는가?
3. 문자열 전체 길이 합이 얼마나 되는가?
4. 겹치는 매칭을 모두 세야 하는가?
5. 해시 충돌을 허용할 수 없는 판정 문제인가?
6. 사전순 정렬이나 LCP처럼 suffix 구조가 필요한가?

정리하면, 문자열 매칭 입문에서는 KMP와 Z를 정확한 선형 도구로 익히고, Rolling Hash는 많은 구간 비교를 빠르게 줄이는 후보 판별 도구로 이해하면 됩니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 한 패턴의 등장 위치를 모두 찾는 문제 추가 | KMP 실패 함수와 겹치는 매칭 처리 | prefix function |
| 표준 | TODO: 접두사 일치 길이를 이용하는 문자열 분석 문제 추가 | Z function의 `[left, right]` 구간 재사용 | Z-box |
| 응용 | TODO: 많은 부분 문자열 비교 문제 추가 | Rolling Hash 전처리와 구간 해시 비교 | double hash |
| 함정 | TODO: 해시 충돌 또는 separator 경계가 중요한 문제 추가 | 정확 알고리즘과 해시 후보 검증 구분 | collision, separator |
