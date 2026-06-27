# Suffix와 Palindrome 응용

Suffix와 Palindrome 응용은 Suffix Array, Suffix Automaton, Palindromic Tree를 문제 신호에 맞게 선택하는 레슨입니다. 구조를 하나씩 구현할 줄 아는 것과, 어떤 문제에서 어떤 구조를 꺼낼지 판단하는 것은 별개의 기술입니다.

이 레슨은 Suffix Automaton과 Palindromic Tree 이후에 보는 문자열 심화 응용 정리입니다.

1. 부분 문자열 전체를 다루면 suffix 계열을 먼저 본다.
2. palindrome substring을 보존해야 하면 Palindromic Tree를 본다.
3. 여러 문자열 사이의 공통성은 separator, product automaton, LCP 구간으로 모델링한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Suffix Array, LCP, Suffix Automaton, Palindromic Tree
- 함께 보면 좋은 레슨: Suffix Array와 LCP, Suffix Automaton, Palindromic Tree
- 다음에 볼 레슨: Lyndon factorization, palindromic DP, suffix tree intuition

## 1. 문제 신호별 선택

| 문제 신호 | 우선 후보 |
| --- | --- |
| 서로 다른 substring 개수 | Suffix Automaton 또는 Suffix Array + LCP |
| 각 substring의 등장 횟수 | Suffix Automaton occurrence 또는 Suffix Array interval |
| 두 문자열의 최장 공통 substring | Suffix Automaton walk 또는 combined Suffix Array |
| 모든 서로 다른 palindrome | Palindromic Tree |
| prefix마다 새 palindrome 개수 | Palindromic Tree online construction |
| suffix 기준 정렬과 range query | Suffix Array + LCP/RMQ |

가장 흔한 실수는 "문자열 심화"라는 이유만으로 구조를 과하게 고르는 것입니다. 구하려는 대상이 substring 전체인지, suffix 순서인지, palindrome인지 먼저 나눕니다.

## 2. 서로 다른 Substring 개수

Suffix Automaton에서는 각 state가 대표하는 endpos class의 substring 개수 기여가 아래처럼 계산됩니다.

```text
contribution(state) = len[state] - len[link[state]]
```

전체 서로 다른 substring 개수는 root를 제외한 모든 state의 기여 합입니다.

Suffix Array에서는 전체 substring 수 `N(N+1)/2`에서 인접 suffix의 LCP 합을 뺍니다.

```text
distinct = N(N+1)/2 - sum(LCP)
```

## 3. Suffix Automaton Occurrence 누적

아래 코드는 Suffix Automaton에서 각 state의 occurrence를 suffix link tree 방향으로 누적하는 부분입니다.

```cpp compile-check
#include <array>
#include <string>
#include <vector>
using namespace std;

struct SuffixAutomatonForCount {
    struct State {
        int link = -1;
        int len = 0;
        long long occ = 0;
        array<int, 26> next{};

        State() {
            next.fill(-1);
        }
    };

    vector<State> st;
    int last = 0;

    SuffixAutomatonForCount() {
        st.push_back(State{});
    }

    void extend(char ch) {
        int c = ch - 'a';
        int cur = (int)st.size();
        st.push_back(State{});
        st[cur].len = st[last].len + 1;
        st[cur].occ = 1;

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
                st[clone].occ = 0;
                while (p != -1 && st[p].next[c] == q) {
                    st[p].next[c] = clone;
                    p = st[p].link;
                }
                st[q].link = st[cur].link = clone;
            }
        }
        last = cur;
    }

    void build(const string& s) {
        for (char ch : s) {
            extend(ch);
        }
    }

    vector<long long> occurrenceByState() const {
        int maxLen = 0;
        for (const State& state : st) {
            if (state.len > maxLen) {
                maxLen = state.len;
            }
        }

        vector<int> bucket(maxLen + 1, 0);
        for (const State& state : st) {
            ++bucket[state.len];
        }
        for (int i = 1; i <= maxLen; ++i) {
            bucket[i] += bucket[i - 1];
        }

        vector<int> order(st.size());
        for (int i = (int)st.size() - 1; i >= 0; --i) {
            order[--bucket[st[i].len]] = i;
        }

        vector<long long> occ(st.size());
        for (int i = 0; i < (int)st.size(); ++i) {
            occ[i] = st[i].occ;
        }
        for (int i = (int)order.size() - 1; i > 0; --i) {
            int v = order[i];
            if (st[v].link != -1) {
                occ[st[v].link] += occ[v];
            }
        }
        return occ;
    }
};
```

clone state의 occurrence를 0으로 두는 점이 중요합니다. 실제 위치에서 생성된 state만 처음에 1을 갖고, suffix link를 따라 누적합니다.

## 4. 최장 공통 Substring

문자열 `A`의 Suffix Automaton을 만들고, 문자열 `B`를 왼쪽에서 오른쪽으로 걸으면 최장 공통 substring을 찾을 수 있습니다.

```text
current state와 current length를 유지한다.
다음 문자가 transition으로 가능하면 이동한다.
불가능하면 suffix link를 따라가며 가능한 상태를 찾는다.
매 위치에서 current length의 최댓값을 갱신한다.
```

Suffix Array를 쓰는 경우에는 `A + sep + B`의 suffix array를 만들고, 인접 suffix가 서로 다른 문자열에서 왔을 때 LCP 최댓값을 봅니다.

## 5. Palindrome 응용

Palindromic Tree는 서로 다른 palindrome substring을 node로 보존합니다.

| 목표 | Palindromic Tree 처리 |
| --- | --- |
| 서로 다른 palindrome 개수 | node 수 - 2 |
| 각 palindrome 등장 횟수 | count를 길이 내림차순으로 suffix link 누적 |
| 가장 긴 palindrome suffix | `last` state |
| prefix별 새 palindrome 여부 | 문자 추가 시 새 node 생성 여부 |
| palindrome partition DP | suffix link 또는 series link 응용 |

단순 longest palindrome은 Manacher가 더 간단합니다. Palindromic Tree는 "모든 서로 다른 palindrome"을 유지해야 할 때 선택합니다.

## 6. 여러 문자열 처리

여러 문자열을 한 구조에 넣을 때는 separator가 중요합니다.

```text
s1 + # + s2 + $ + s3
```

separator는 어떤 원문 문자와도 달라야 하고, 서로 다른 separator를 쓰면 substring이 문자열 경계를 넘어가는 것을 막기 쉽습니다.

Suffix Automaton에서는 각 state가 어느 문자열에 등장하는지를 bitmask나 count로 누적할 수 있습니다. Suffix Array에서는 suffix의 원본 문자열 id를 저장하고 sliding window로 모든 문자열을 포함하는 구간을 찾습니다.

## 7. 시간 복잡도

| 도구 | 대표 작업 | 시간 |
| --- | --- | ---: |
| Suffix Array + LCP | 정렬, LCP, range query | `O(N log N)` 또는 `O(N)` |
| Suffix Automaton | 온라인 construction | `O(N * alphabet)` 또는 `O(N)` |
| Palindromic Tree | 온라인 palindrome node 추가 | `O(N * alphabet)` 또는 `O(N)` |
| Manacher | longest palindrome radius | `O(N)` |

alphabet이 작으면 배열 transition이 빠릅니다. alphabet이 크면 map 또는 좌표 압축된 transition이 필요합니다.

## 8. 자주 하는 실수

1. Suffix Automaton clone state에 occurrence 1을 준다.
2. Suffix Array LCP 합을 뺄 때 `long long`을 쓰지 않는다.
3. 여러 문자열을 합칠 때 separator가 원문에 등장한다.
4. palindrome 문제인데 suffix 구조만으로 풀려고 한다.
5. substring과 subsequence를 혼동한다.

## 9. 문제를 볼 때 체크할 조건

- 대상이 substring인가 suffix인가 palindrome인가?
- 서로 다른 개수가 필요한가, 등장 횟수가 필요한가?
- 온라인 처리가 필요한가?
- 문자열이 여러 개인가, 경계가 중요한가?
- alphabet 크기가 작아 배열 transition이 가능한가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 서로 다른 substring 개수 `/practice/...` 문제 필요 | SAM 기여 또는 SA LCP 합 사용 | distinct substring |
| 표준 | TODO: 최장 공통 substring `/practice/...` 문제 필요 | SAM walk 또는 combined SA | longest common substring |
| 응용 | TODO: palindrome occurrence `/practice/...` 문제 필요 | Eertree count 누적 | palindromic tree |
| 함정 | TODO: 여러 문자열 substring `/practice/...` 문제 필요 | separator와 source id 관리 | multi-string suffix |
