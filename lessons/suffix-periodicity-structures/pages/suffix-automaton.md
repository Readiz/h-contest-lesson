# Suffix Automaton

Suffix Automaton은 한 문자열의 모든 부분 문자열을 압축해서 표현하는 automaton입니다. Suffix Array가 suffix를 정렬해 문제를 푼다면, Suffix Automaton은 부분 문자열들이 도달하는 상태를 만들고 transition 위에서 세거나 탐색합니다.

## 왜 automaton인가

문자열 `s`의 모든 부분 문자열은 suffix들의 prefix입니다. 이를 그대로 저장하면 부분 문자열 수가 `O(N^2)`입니다. Suffix Automaton은 등장 끝 위치 집합인 `endpos`가 같은 부분 문자열들을 하나의 상태로 합쳐 `O(N)` 상태만 만듭니다.

| 질문 | Suffix Automaton 관점 |
| --- | --- |
| 서로 다른 부분 문자열 개수 | 상태별 `len[v] - len[link[v]]` 합 |
| 특정 패턴이 부분 문자열인가 | transition을 따라갈 수 있는지 확인 |
| 각 부분 문자열의 등장 횟수 | terminal count를 suffix link 역순으로 누적 |
| 두 문자열의 LCS | 두 번째 문자열을 automaton 위에서 훑기 |
| 사전순 k번째 부분 문자열 | 상태 DAG 위 DP |

입문에서는 먼저 construction과 대표 공식 두 개를 안정적으로 익히는 것이 좋습니다.

## 상태가 뜻하는 것

각 상태 `v`에는 `len[v]`와 `link[v]`가 있습니다.

| 값 | 의미 |
| --- | --- |
| `len[v]` | 이 상태가 대표하는 문자열 중 가장 긴 길이 |
| `link[v]` | 현재 상태와 다른 상태에 속하는 가장 긴 proper suffix의 상태 |
| transition | 뒤에 문자를 하나 붙였을 때 이동하는 상태 |

상태 `v`가 새로 기여하는 서로 다른 부분 문자열 수는 아래와 같습니다.

```text
len[v] - len[link[v]]
```

`link[v]`가 이미 표현하던 suffix 길이까지는 기존 상태가 담당하고, 그보다 길고 `len[v]` 이하인 suffix들이 새로 추가된다고 보면 됩니다.

## Construction

문자열을 왼쪽에서 오른쪽으로 한 글자씩 추가합니다. 새 문자를 붙인 전체 문자열을 대표하는 `cur` 상태를 만들고, 이전 마지막 상태에서 suffix link를 거슬러 올라가며 없는 transition을 채웁니다.

이미 같은 문자 transition이 있고 길이 조건이 맞지 않으면 clone 상태를 만들어 transition과 link를 나눕니다. clone은 기존 상태의 transition을 복사하지만, 길이만 필요한 값으로 줄인 상태입니다.

```cpp compile-check
#include <algorithm>
#include <array>
#include <string>
#include <vector>
using namespace std;

struct SuffixAutomaton {
    inline static constexpr long long LIMIT = (1LL << 60);

    struct State {
        int link = -1;
        int len = 0;
        array<int, 26> next{};
        long long occ = 0;
        long long paths = -1;

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
                st[q].link = clone;
                st[cur].link = clone;
            }
        }

        last = cur;
    }

    void build(const string& s) {
        st.assign(1, State{});
        last = 0;
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

    long long countPaths(int v) {
        if (st[v].paths != -1) {
            return st[v].paths;
        }
        long long total = 0;
        for (int to : st[v].next) {
            if (to == -1) {
                continue;
            }
            total = min(LIMIT, total + 1 + countPaths(to));
        }
        st[v].paths = total;
        return total;
    }

    string kthSubstring(long long k) {
        countPaths(0);
        if (k <= 0 || k > st[0].paths) {
            return "";
        }

        string result;
        int v = 0;
        while (k > 0) {
            bool moved = false;
            for (int c = 0; c < 26; ++c) {
                int to = st[v].next[c];
                if (to == -1) {
                    continue;
                }
                if (k == 1) {
                    result.push_back(char('a' + c));
                    return result;
                }
                --k;
                if (k <= st[to].paths) {
                    result.push_back(char('a' + c));
                    v = to;
                    moved = true;
                    break;
                }
                k -= st[to].paths;
            }
            if (!moved) {
                return "";
            }
        }
        return result;
    }
};
```

위 구현은 알파벳이 `a..z`라고 가정합니다. 문자 종류가 크거나 동적으로 주어진다면 `array<int, 26>` 대신 `map`, `unordered_map`, 또는 좌표 압축한 vector를 씁니다.

## 서로 다른 부분 문자열 수

상태별 새 기여량을 합하면 서로 다른 부분 문자열 개수가 됩니다.

```cpp compile-check
#include <vector>
using namespace std;

template<class State>
long long countDistinctSubstrings(const vector<State>& states) {
    long long result = 0;
    for (int v = 1; v < (int)states.size(); ++v) {
        int parent = states[v].link;
        result += states[v].len - states[parent].len;
    }
    return result;
}
```

초기 상태 0은 빈 문자열을 담당하므로 보통 부분 문자열 개수에서 제외합니다. 결과는 `N * (N + 1) / 2`까지 커질 수 있으니 `long long`을 사용합니다.

## 등장 횟수 세기

각 prefix를 추가할 때 만들어지는 `cur` 상태는 그 prefix가 한 번 등장했음을 뜻합니다. 그래서 `occ[cur] = 1`로 두고, 길이가 긴 상태부터 suffix link 방향으로 occurrence를 더하면 각 상태가 대표하는 문자열들의 등장 횟수를 얻을 수 있습니다.

```text
길이가 긴 상태부터:
occ[link[v]] += occ[v]
```

clone 상태는 새 prefix가 직접 끝나는 상태가 아니므로 처음 count를 0으로 둡니다. 이후 자식 상태들의 count가 suffix link로 모이며 실제 등장 횟수가 됩니다.

## 두 문자열의 최장 공통 부분 문자열

문자열 `A`로 automaton을 만든 뒤, 문자열 `B`를 왼쪽부터 훑습니다. 현재 상태에서 다음 문자가 있으면 이동하고 길이를 늘립니다. transition이 없으면 suffix link를 따라 줄이다가 가능한 상태를 찾습니다.

```cpp compile-check
#include <array>
#include <string>
#include <vector>
using namespace std;

template<class State>
int longestCommonSubstring(const vector<State>& st, const string& other) {
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

두 함수는 위 `sam.st`를 직접 인자로 받습니다. 이 함수도 `next`가 `-1`로 초기화되어 있다는 전제가 있습니다. 상태 구조를 따로 쓸 때는 constructor에서 초기화하는 습관이 중요합니다.

## 기본 연산의 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| automaton construction | `O(N * alphabet transition cost)` | `N >= 2`에서 최대 `2N - 1` 상태 |
| 패턴 포함 여부 | `O(M)` | automaton 사용 |
| 서로 다른 부분 문자열 수 | `O(number of states)` | 없음 |
| occurrence 누적 | `O(number of states + alphabet edges)` | count 배열 |
| 두 문자열 LCS | `O(|B|)` | automaton 사용 |

고정 소문자 alphabet이면 transition cost가 `O(1)`입니다. 큰 alphabet에서 map을 쓰면 로그 또는 해시 비용이 붙습니다.

## 두 그래프를 분리해서 보기

Suffix Automaton에는 두 종류의 간선이 있습니다.

| 구조 | 쓰는 곳 |
| --- | --- |
| transition DAG | substring을 한 글자씩 확장, 사전순 DP, pattern scan |
| suffix link tree | occurrence 누적, endpos 포함 관계, terminal propagation |

서로 다른 substring 수나 k번째 substring은 transition DAG 위 path 문제입니다. 등장 횟수는 terminal count를 길이가 긴 상태부터 suffix link로 올려야 합니다.

## k번째 Substring

사전순 k번째 서로 다른 substring은 transition을 문자 순서로 보면서, 각 transition 아래에 있는 path 수를 건너뛰는 방식으로 찾습니다.

위 `SuffixAutomaton`의 `countPaths`가 transition DAG의 경로 수를 메모하고, `kthSubstring`이 문자 순서대로 그 수를 건너뜁니다.

모든 문자 추가 후 occurrenceByState()로 등장 수 벡터를 얻습니다. 원본 occ를 바꾸지 않으므로 반복 호출해도 같습니다. path DP나 occurrence 집계 뒤에는 extend하지 말고 새 문자열로 build합니다. path DP 재귀 깊이는 문자열 길이까지 늘어납니다. 위 함수는 k를 1-indexed로 받습니다. 같은 substring을 여러 번 세지 않으려면 transition DAG의 path만 세고 occurrence는 섞지 않습니다.

## 가장 긴 반복 Substring

반복 substring은 occurrence가 2 이상인 문자열입니다. state `v`가 occurrence 2 이상이면 그 state가 대표하는 길이 구간 중 최댓값 `len[v]`가 후보가 됩니다.

```text
occ = sam.occurrenceByState()
answer = max(len[v]) over occ[v] >= 2
```

문자열 자체를 복원하려면 각 state의 대표 end position을 함께 저장해 두고 `end - len[v] + 1` 구간을 잘라냅니다.

## 여러 문자열 공통 Substring

문자열 `S`로 automaton을 만들고 다른 문자열 `T`를 훑으면 각 위치에서 현재 matched length를 알 수 있습니다. 이 값을 state별로 최대로 기록한 뒤 suffix link 역순으로 `min(len[link child], matched)` 형태로 올립니다.

여러 문자열의 최장 공통 substring은 각 문자열마다 얻은 state별 최대 match의 최솟값을 유지한 뒤 최댓값을 구합니다.

## Suffix Array와 비교

| 문제 | Suffix Automaton | Suffix Array/LCP |
| --- | --- | --- |
| online append | 강함 | 다시 구성 필요 |
| k번째 substring | DAG DP로 직접 처리 | LCP로 중복 개수 보정 |
| 많은 pattern 포함 질의 | transition scan | binary search |
| 정렬된 suffix 구간 | 약함 | 강함 |
| 여러 문자열 LCS | scan과 state DP | generalized suffix array |

둘은 대체재라기보다 문제 신호가 다릅니다. "확장 가능한 상태"가 보이면 automaton, "정렬된 suffix 순서"가 보이면 suffix array가 자연스럽습니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| construction | `O(N * transition cost)` |
| occurrence 누적 | counting sort 포함 `O(states + N)` |
| path count DP | `O(edges)` |
| k번째 substring | `O(answer length * alphabet)` |
| 한 문자열 scan | `O(length)` |

상태 수는 `N >= 2`에서 최대 `2N-1`입니다. 빈 문자열은 초기 상태 하나, 길이 1은 두 상태입니다. alphabet이 크면 transition을 `array` 대신 map이나 압축 vector로 바꿉니다.
