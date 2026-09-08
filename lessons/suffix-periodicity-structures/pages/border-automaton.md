# Border Automaton

Border Automaton은 KMP의 prefix function을 상태 전이표로 바꿔, 문자열을 한 글자씩 읽으면서 현재 matched prefix 길이를 즉시 갱신하는 기법입니다. 패턴 하나를 여러 텍스트, 여러 DP 상태, 혹은 online stream에 반복 적용할 때 KMP fallback을 매번 따라가지 않고 automaton 전이로 처리합니다.


패턴은 소문자로 구성합니다. 빈 패턴의 검색 결과는 빈 목록으로 정합니다. 텍스트의 소문자 이외 문자는 매칭을 끊습니다.

## 문제 신호

| 문제 표현 | Border Automaton 관점 |
| --- | --- |
| 같은 패턴으로 많은 문자열을 검사 | KMP transition table 재사용 |
| 문자열 DP에서 forbidden pattern을 피함 | matched prefix length를 DP 상태로 사용 |
| 문자를 하나씩 추가하며 현재 매칭 길이를 유지 | online automaton transition |
| prefix/suffix 일치 조건이 반복됨 | border state 이동 |
| 패턴 등장 횟수와 상태 전이가 함께 필요 | accepting state 이후 fallback 처리 |

KMP는 text를 왼쪽에서 오른쪽으로 읽으며 `while` fallback을 할 수 있습니다. Border Automaton은 그 fallback 결과를 `go[state][char]`에 캐시해 두는 형태입니다.

## 상태 의미

패턴 `p`의 길이가 `m`이면 상태는 `0..m`입니다.

```text
state = k
현재까지 읽은 문자열의 suffix가 p[0..k-1]와 같음
```

상태 `m`은 패턴 전체가 방금 매칭된 상태입니다. 겹치는 등장도 세려면 매칭을 기록한 뒤 `pi[m-1]` 상태로 돌아가 다음 문자를 계속 처리합니다.

## 전이 만들기

상태 `s`에서 문자 `c`를 붙였을 때 다음 상태는 아래 규칙입니다.

```text
if s < m and p[s] == c:
    next = s + 1
else:
    next = go[pi[s - 1]][c]  (s > 0)
```

`s = 0`이면 더 돌아갈 border가 없으므로 일치하지 않는 문자는 0으로 갑니다.

## 구현

아래 코드는 lowercase alphabet을 가정한 border automaton입니다. alphabet이 다르면 문자 압축이나 `map` 기반 전이를 사용합니다.

```cpp compile-check
#include <string>
#include <vector>
using namespace std;

struct BorderAutomaton {
    string pattern;
    vector<int> pi;
    vector<vector<int>> go;

    static vector<int> prefixFunction(const string& s) {
        int n = (int)s.size();
        vector<int> result(n, 0);
        for (int i = 1; i < n; ++i) {
            int j = result[i - 1];
            while (j > 0 && s[i] != s[j]) {
                j = result[j - 1];
            }
            if (s[i] == s[j]) {
                ++j;
            }
            result[i] = j;
        }
        return result;
    }

    explicit BorderAutomaton(string p) : pattern(p), pi(prefixFunction(pattern)) {
        int m = (int)pattern.size();
        go.assign(m + 1, vector<int>(26, 0));
        for (int state = 0; state <= m; ++state) {
            for (int ch = 0; ch < 26; ++ch) {
                char c = char('a' + ch);
                if (state < m && pattern[state] == c) {
                    go[state][ch] = state + 1;
                } else if (state == 0) {
                    go[state][ch] = 0;
                } else {
                    go[state][ch] = go[pi[state - 1]][ch];
                }
            }
        }
    }

    vector<int> matchPositions(const string& text) const {
        vector<int> positions;
        if (pattern.empty()) return positions;
        int state = 0;
        int m = (int)pattern.size();
        for (int i = 0; i < (int)text.size(); ++i) {
            int ch = text[i] - 'a';
            if (0 <= ch && ch < 26) {
                state = go[state][ch];
            } else {
                state = 0;
            }
            if (state == m) {
                positions.push_back(i - m + 1);
                // go[m]이 실패 링크 전이를 포함하므로 다음 문자에 그대로 사용한다.
            }
        }
        return positions;
    }
};
```

전이표 크기는 `O(m * alphabet)`입니다. alphabet이 크고 sparse하면 필요한 문자만 계산하는 lazy transition이 더 낫습니다.

## Forbidden Pattern DP

"길이 N 문자열 중 패턴 P를 포함하지 않는 개수" 같은 문제에서는 DP 상태를 matched prefix 길이로 둡니다.

```text
dp[pos][state] = pos글자를 만들었고, 현재 matched prefix length가 state인 경우
next = go[state][c]
if next != m:
    dp[pos + 1][next] += dp[pos][state]
```

상태 `m`으로 가는 전이를 버리면 패턴이 등장하는 문자열을 제외할 수 있습니다. 여러 forbidden pattern이면 Aho-Corasick이 더 자연스럽습니다.

## Border Transition 응용

Prefix function의 failure link는 "현재 matched prefix의 가장 긴 proper border"로 이동합니다.

```text
state k
fallback pi[k - 1]
fallback pi[pi[k - 1] - 1]
...
```

이 chain을 따라가면 현재 suffix가 동시에 만족하는 모든 border 길이를 열거할 수 있습니다. prefix 등장 횟수, border별 누적 count, period 조건을 처리할 때 이 관점이 필요합니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| prefix function | `O(M)` |
| automaton build | `O(M * sigma)` |
| text scan | `O(N)` |
| forbidden pattern DP | `O(N * M * sigma)` |

`sigma`는 alphabet 크기입니다. lowercase만 보면 26이지만, 전체 ASCII나 압축되지 않은 정수 alphabet이면 전이표 크기를 먼저 확인합니다.
