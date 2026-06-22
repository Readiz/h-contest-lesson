# Suffix Automaton

Suffix Automaton은 한 문자열의 모든 부분 문자열을 압축해서 표현하는 automaton입니다. Suffix Array가 suffix를 정렬해 문제를 푼다면, Suffix Automaton은 부분 문자열들이 도달하는 상태를 만들고 transition 위에서 세거나 탐색합니다.

이 레슨은 "모든 부분 문자열의 상태 압축"이라는 관점으로 Suffix Automaton을 봅니다.

1. 문자를 하나씩 추가하며 automaton을 확장한다.
2. 각 상태가 표현하는 부분 문자열 길이 구간을 이해한다.
3. 서로 다른 부분 문자열 수, 등장 횟수, 최장 공통 부분 문자열로 연결한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 문자열 매칭, Trie, Suffix Array/LCP 감각
- 함께 보면 좋은 레슨: 문자열 매칭: KMP, Z, Rolling Hash, Trie와 Aho-Corasick, Suffix Array와 LCP
- 다음에 볼 레슨: suffix automaton DP, palindromic tree, suffix tree

## 1. 왜 automaton인가

문자열 `s`의 모든 부분 문자열은 suffix들의 prefix입니다. 이를 그대로 저장하면 부분 문자열 수가 `O(N^2)`입니다. Suffix Automaton은 같은 "앞으로 이어질 수 있는 문자열 집합"을 가진 부분 문자열들을 하나의 상태로 합쳐 `O(N)` 상태만 만듭니다.

| 질문 | Suffix Automaton 관점 |
| --- | --- |
| 서로 다른 부분 문자열 개수 | 상태별 `len[v] - len[link[v]]` 합 |
| 특정 패턴이 부분 문자열인가 | transition을 따라갈 수 있는지 확인 |
| 각 부분 문자열의 등장 횟수 | terminal count를 suffix link 역순으로 누적 |
| 두 문자열의 LCS | 두 번째 문자열을 automaton 위에서 훑기 |
| 사전순 k번째 부분 문자열 | 상태 DAG 위 DP |

입문에서는 먼저 construction과 대표 공식 두 개를 안정적으로 익히는 것이 좋습니다.

## 2. 상태가 뜻하는 것

각 상태 `v`에는 `len[v]`와 `link[v]`가 있습니다.

| 값 | 의미 |
| --- | --- |
| `len[v]` | 이 상태가 대표하는 문자열 중 가장 긴 길이 |
| `link[v]` | 가장 긴 문자열의 proper suffix가 속한 상태 |
| transition | 뒤에 문자를 하나 붙였을 때 이동하는 상태 |

상태 `v`가 새로 기여하는 서로 다른 부분 문자열 수는 아래와 같습니다.

```text
len[v] - len[link[v]]
```

`link[v]`가 이미 표현하던 suffix 길이까지는 기존 상태가 담당하고, 그보다 길고 `len[v]` 이하인 suffix들이 새로 추가된다고 보면 됩니다.

## 3. Construction

문자열을 왼쪽에서 오른쪽으로 한 글자씩 추가합니다. 새 문자를 붙인 전체 문자열을 대표하는 `cur` 상태를 만들고, 이전 마지막 상태에서 suffix link를 거슬러 올라가며 없는 transition을 채웁니다.

이미 같은 문자 transition이 있고 길이 조건이 맞지 않으면 clone 상태를 만들어 transition과 link를 나눕니다. clone은 기존 상태의 transition을 복사하지만, 길이만 필요한 값으로 줄인 상태입니다.

```cpp compile-check
#include <array>
#include <string>
#include <vector>
using namespace std;

struct SuffixAutomaton {
    struct State {
        int link = -1;
        int len = 0;
        array<int, 26> next{};

        State() {
            next.fill(-1);
        }
    };

    vector<State> st;
    int last = 0;

    SuffixAutomaton() {
        st.push_back(State{});
    }

    void extend(char ch) {
        int c = ch - 'a';
        int cur = (int)st.size();
        st.push_back(State{});
        st[cur].len = st[last].len + 1;

        int p = last;
        while (p != -1 && st[p].next[c] == -1) {
            st[p].next[c] = cur;
            p = st[p].link;
        }

        if (p == -1) {
            st[cur].link = 0;
        } else {
            int q = st[p].next[c];
            if (st[p].len + 1 == st[q].len) {
                st[cur].link = q;
            } else {
                int clone = (int)st.size();
                st.push_back(st[q]);
                st[clone].len = st[p].len + 1;
                while (p != -1 && st[p].next[c] == q) {
                    st[p].next[c] = clone;
                    p = st[p].link;
                }
                st[q].link = clone;
                st[cur].link = clone;
            }
        }

        last = cur;
    }

    void build(const string& s) {
        for (char ch : s) {
            extend(ch);
        }
    }
};
```

위 구현은 알파벳이 `a..z`라고 가정합니다. 문자 종류가 크거나 동적으로 주어진다면 `array<int, 26>` 대신 `map`, `unordered_map`, 또는 좌표 압축한 vector를 씁니다.

## 4. 서로 다른 부분 문자열 수

상태별 새 기여량을 합하면 서로 다른 부분 문자열 개수가 됩니다.

```cpp compile-check
#include <vector>
using namespace std;

struct SamCounterState {
    int link;
    int len;
};

long long countDistinctSubstrings(const vector<SamCounterState>& states) {
    long long result = 0;
    for (int v = 1; v < (int)states.size(); ++v) {
        int parent = states[v].link;
        result += states[v].len - states[parent].len;
    }
    return result;
}
```

초기 상태 0은 빈 문자열을 담당하므로 보통 부분 문자열 개수에서 제외합니다. 결과는 `N * (N + 1) / 2`까지 커질 수 있으니 `long long`을 사용합니다.

## 5. 등장 횟수 세기

각 prefix를 추가할 때 만들어지는 `cur` 상태는 그 prefix가 한 번 등장했음을 뜻합니다. 그래서 `occ[cur] = 1`로 두고, 길이가 긴 상태부터 suffix link 방향으로 occurrence를 더하면 각 상태가 대표하는 문자열들의 등장 횟수를 얻을 수 있습니다.

```text
길이가 긴 상태부터:
occ[link[v]] += occ[v]
```

clone 상태는 새 prefix가 직접 끝나는 상태가 아니므로 처음 count를 0으로 둡니다. 이후 자식 상태들의 count가 suffix link로 모이며 실제 등장 횟수가 됩니다.

## 6. 두 문자열의 최장 공통 부분 문자열

문자열 `A`로 automaton을 만든 뒤, 문자열 `B`를 왼쪽부터 훑습니다. 현재 상태에서 다음 문자가 있으면 이동하고 길이를 늘립니다. transition이 없으면 suffix link를 따라 줄이다가 가능한 상태를 찾습니다.

```cpp compile-check
#include <array>
#include <string>
#include <vector>
using namespace std;

struct SamStateForLcs {
    int link = -1;
    int len = 0;
    array<int, 26> next{};

    SamStateForLcs() {
        next.fill(-1);
    }
};

int longestCommonSubstring(const vector<SamStateForLcs>& st, const string& other) {
    int state = 0;
    int matched = 0;
    int best = 0;

    for (char ch : other) {
        int c = ch - 'a';
        while (state != 0 && st[state].next[c] == -1) {
            state = st[state].link;
            matched = st[state].len;
        }
        if (st[state].next[c] != -1) {
            state = st[state].next[c];
            ++matched;
        } else {
            state = 0;
            matched = 0;
        }
        if (matched > best) {
            best = matched;
        }
    }

    return best;
}
```

이 함수도 `next`가 `-1`로 초기화되어 있다는 전제가 있습니다. 상태 구조를 따로 쓸 때는 constructor에서 초기화하는 습관이 중요합니다.

## 7. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| automaton construction | `O(N * alphabet transition cost)` | 최대 `2N - 1` 상태 |
| 패턴 포함 여부 | `O(M)` | automaton 사용 |
| 서로 다른 부분 문자열 수 | `O(number of states)` | 없음 |
| occurrence 누적 | `O(number of states + alphabet edges)` | count 배열 |
| 두 문자열 LCS | `O(|B|)` | automaton 사용 |

고정 소문자 alphabet이면 transition cost가 `O(1)`입니다. 큰 alphabet에서 map을 쓰면 로그 또는 해시 비용이 붙습니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| clone의 transition 복사 누락 | automaton 경로가 끊김 | `clone = q` 복사 후 len만 조정 |
| clone occurrence를 1로 둠 | 등장 횟수 과대 계산 | 새 prefix 상태만 count 1 |
| suffix link 역순 누적 순서 오류 | occurrence가 덜 모임 | `len` 내림차순 처리 |
| alphabet 초기화 누락 | 임의 transition 사용 | `next.fill(-1)` 확인 |
| `int`로 부분 문자열 개수 계산 | overflow | `long long` 사용 |
| 상태가 부분 문자열 하나만 뜻한다고 오해 | 공식 적용 오류 | 상태는 길이 구간을 대표 |

## 9. 문제를 볼 때 체크할 조건

1. 한 문자열의 모든 부분 문자열을 대상으로 세거나 비교하는가?
2. 여러 패턴이 이 문자열의 부분 문자열인지 확인해야 하는가?
3. 서로 다른 부분 문자열 수나 사전순 순서가 필요한가?
4. 등장 횟수가 필요하면 clone count를 분리했는가?
5. alphabet 크기가 구현 방식과 맞는가?
6. Suffix Array/LCP로 더 단순하게 풀 수 있는지 비교했는가?

Suffix Automaton은 처음 구현이 낯설지만, construction 이후에는 상태 DAG 위 DP로 많은 문자열 문제를 처리합니다. "상태가 하나의 문자열이 아니라 길이 구간을 대표한다"는 점을 유지하면 공식과 occurrence 처리가 흔들리지 않습니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 서로 다른 부분 문자열 수 `/practice/...` 문제 필요 | `len[v] - len[link[v]]` 합 계산 | distinct substrings |
| 표준 | TODO: 패턴 포함 여부 다중 질의 `/practice/...` 문제 필요 | automaton transition 탐색 | substring query |
| 응용 | TODO: 두 문자열 LCS `/practice/...` 문제 필요 | suffix link로 matched 길이 줄이기 | lcs on sam |
| 함정 | TODO: 등장 횟수 집계 `/practice/...` 문제 필요 | clone count 0과 길이 내림차순 누적 | occurrence |
