# Border Automaton

Border Automaton은 KMP의 prefix function을 상태 전이표로 바꿔, 문자열을 한 글자씩 읽으면서 현재 matched prefix 길이를 즉시 갱신하는 기법입니다. 패턴 하나를 여러 텍스트, 여러 DP 상태, 혹은 online stream에 반복 적용할 때 KMP fallback을 매번 따라가지 않고 automaton 전이로 처리합니다.

이 레슨은 KMP/Z, Runs와 문자열 주기, Suffix Array 응용 이후에 보는 문자열 심화입니다.

1. 상태를 "현재 suffix가 pattern의 prefix 몇 글자와 일치하는가"로 둔다.
2. prefix function으로 실패했을 때 돌아갈 border 상태를 정한다.
3. 각 상태와 문자에 대해 다음 matched length를 미리 채운다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: KMP prefix function, border, finite automaton
- 함께 보면 좋은 레슨: KMP와 Z Algorithm, Runs와 문자열 주기, Suffix Array 응용 패턴
- 다음에 볼 레슨: suffix automaton applications, Aho-Corasick automaton, automaton DP

## 1. 문제 신호

| 문제 표현 | Border Automaton 관점 |
| --- | --- |
| 같은 패턴으로 많은 문자열을 검사 | KMP transition table 재사용 |
| 문자열 DP에서 forbidden pattern을 피함 | matched prefix length를 DP 상태로 사용 |
| 문자를 하나씩 추가하며 현재 매칭 길이를 유지 | online automaton transition |
| prefix/suffix 일치 조건이 반복됨 | border state 이동 |
| 패턴 등장 횟수와 상태 전이가 함께 필요 | accepting state 이후 fallback 처리 |

KMP는 text를 왼쪽에서 오른쪽으로 읽으며 `while` fallback을 할 수 있습니다. Border Automaton은 그 fallback 결과를 `go[state][char]`에 캐시해 두는 형태입니다.

## 2. 상태 의미

패턴 `p`의 길이가 `m`이면 상태는 `0..m`입니다.

```text
state = k
현재까지 읽은 문자열의 suffix가 p[0..k-1]와 같음
```

상태 `m`은 패턴 전체가 방금 매칭된 상태입니다. 겹치는 등장도 세려면 매칭을 기록한 뒤 `pi[m-1]` 상태로 돌아가 다음 문자를 계속 처리합니다.

## 3. 전이 만들기

상태 `s`에서 문자 `c`를 붙였을 때 다음 상태는 아래 규칙입니다.

```text
if s < m and p[s] == c:
    next = s + 1
else:
    next = go[pi[s - 1]][c]  (s > 0)
```

`s = 0`이면 더 돌아갈 border가 없으므로 일치하지 않는 문자는 0으로 갑니다.

## 4. 구현

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
                state = pi[m - 1];
            }
        }
        return positions;
    }
};
```

전이표 크기는 `O(m * alphabet)`입니다. alphabet이 크고 sparse하면 필요한 문자만 계산하는 lazy transition이 더 낫습니다.

## 5. Forbidden Pattern DP

"길이 N 문자열 중 패턴 P를 포함하지 않는 개수" 같은 문제에서는 DP 상태를 matched prefix 길이로 둡니다.

```text
dp[pos][state] = pos글자를 만들었고, 현재 matched prefix length가 state인 경우
next = go[state][c]
if next != m:
    dp[pos + 1][next] += dp[pos][state]
```

상태 `m`으로 가는 전이를 버리면 패턴이 등장하는 문자열을 제외할 수 있습니다. 여러 forbidden pattern이면 Aho-Corasick이 더 자연스럽습니다.

## 6. Border Transition 응용

Prefix function의 failure link는 "현재 matched prefix의 가장 긴 proper border"로 이동합니다.

```text
state k
fallback pi[k - 1]
fallback pi[pi[k - 1] - 1]
...
```

이 chain을 따라가면 현재 suffix가 동시에 만족하는 모든 border 길이를 열거할 수 있습니다. prefix 등장 횟수, border별 누적 count, period 조건을 처리할 때 이 관점이 필요합니다.

## 7. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| prefix function | `O(M)` |
| automaton build | `O(M * sigma)` |
| text scan | `O(N)` |
| forbidden pattern DP | `O(N * M * sigma)` |

`sigma`는 alphabet 크기입니다. lowercase만 보면 26이지만, 전체 ASCII나 압축되지 않은 정수 alphabet이면 전이표 크기를 먼저 확인합니다.

## 8. 자주 하는 실수

1. 매칭 상태 `m`에서 겹치는 매칭을 위해 `pi[m-1]`로 돌아가지 않는다.
2. `state == 0`일 때 `pi[state - 1]`를 참조한다.
3. alphabet에 없는 문자를 만났을 때 상태 초기화를 정의하지 않는다.
4. 여러 forbidden pattern을 하나의 border automaton으로 억지로 합친다.
5. DP에서 accepting state를 허용할지 금지할지 목적식을 혼동한다.

## 9. 문제를 볼 때 체크할 조건

- 패턴이 하나인가, 여러 개인가?
- 같은 패턴 전이를 많이 재사용하는가?
- 상태가 matched prefix length로 충분한가?
- alphabet 크기 때문에 전이표가 커지지는 않는가?
- 매칭 후 겹치는 occurrence까지 세야 하는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: border automaton `/practice/...` 문제 필요 | KMP 전이표 구성 | prefix function |
| 표준 | TODO: forbidden pattern DP `/practice/...` 문제 필요 | accepting state 제외 | automaton DP |
| 응용 | TODO: online pattern counter `/practice/...` 문제 필요 | stream transition | border state |
| 함정 | TODO: overlapping occurrence `/practice/...` 문제 필요 | match 후 fallback | pi chain |
