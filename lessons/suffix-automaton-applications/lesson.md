# Suffix Automaton Applications

Suffix Automaton Applications는 Suffix Automaton을 만든 뒤 그 위에서 DP, occurrence 누적, 사전순 탐색, 여러 문자열 비교를 수행하는 응용 레슨입니다. 기본 construction을 안다면 다음 단계는 "상태가 대표하는 부분 문자열 집합"을 어떤 값으로 세고 정렬하고 제한할지 정하는 것입니다.

이 레슨은 Suffix Automaton, Suffix Array 응용, Palindromic Tree 이후에 보는 문자열 심화입니다.

1. suffix link tree와 transition DAG를 구분한다.
2. 상태별 occurrence, path count, terminal 여부를 목적에 맞게 누적한다.
3. k번째 substring, 반복 substring, 여러 문자열 공통 substring을 automaton DP로 바꾼다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Suffix Automaton construction, suffix link, topological order by length
- 함께 보면 좋은 레슨: Suffix Automaton, Suffix Array 응용 패턴, Suffix와 Palindrome 응용
- 다음에 볼 레슨: generalized suffix automaton, automaton DP, substring query structures

## 1. 문제 신호

| 문제 표현 | Suffix Automaton 응용 관점 |
| --- | --- |
| 서로 다른 substring을 사전순으로 나열 | transition DAG path count |
| k번째 substring을 출력 | state별 suffix path DP |
| 각 substring의 등장 횟수 조건 | occurrence를 suffix link 역순 누적 |
| 가장 긴 반복 substring | `occ[v] >= 2`인 상태의 `len[v]` |
| 여러 문자열의 공통 substring | 각 문자열을 automaton 위에서 훑고 state별 최대 match 갱신 |

Suffix Automaton 기본 레슨의 공식만으로 끝나는 문제는 많지 않습니다. 실전에서는 "상태 하나가 길이 구간을 대표한다"는 점 때문에 집계 범위를 조심해야 합니다.

## 2. 두 그래프를 분리해서 보기

Suffix Automaton에는 두 종류의 간선이 있습니다.

| 구조 | 쓰는 곳 |
| --- | --- |
| transition DAG | substring을 한 글자씩 확장, 사전순 DP, pattern scan |
| suffix link tree | occurrence 누적, endpos 포함 관계, terminal propagation |

서로 다른 substring 수나 k번째 substring은 transition DAG 위 path 문제입니다. 등장 횟수는 terminal count를 길이가 긴 상태부터 suffix link로 올려야 합니다.

## 3. Occurrence 누적

construction에서 새 prefix가 끝나는 상태는 한 번 등장한 end position을 가집니다. clone 상태는 직접 새 prefix가 끝난 상태가 아니므로 초기 occurrence를 0으로 둡니다.

```text
for state in decreasing len:
  occ[link[state]] += occ[state]
```

이 과정을 마치면 state가 대표하는 가장 긴 문자열의 등장 횟수를 얻습니다. 같은 state 안의 길이 구간 문자열들은 endpos 집합이 같기 때문에 같은 occurrence를 공유합니다.

## 4. k번째 Substring

사전순 k번째 서로 다른 substring은 transition을 문자 순서로 보면서, 각 transition 아래에 있는 path 수를 건너뛰는 방식으로 찾습니다.

```cpp compile-check
#include <algorithm>
#include <array>
#include <string>
#include <vector>
using namespace std;

struct SuffixAutomatonApplications {
    static const long long LIMIT = (1LL << 60);

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

    SuffixAutomatonApplications() {
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
        for (char ch : s) {
            extend(ch);
        }
    }

    void buildOccurrences() {
        vector<int> order(st.size());
        for (int i = 0; i < (int)st.size(); ++i) {
            order[i] = i;
        }
        sort(order.begin(), order.end(), [&](int a, int b) {
            return st[a].len > st[b].len;
        });
        for (int v : order) {
            if (st[v].link != -1) {
                st[st[v].link].occ += st[v].occ;
            }
        }
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

위 함수는 k를 1-indexed로 받습니다. 같은 substring을 여러 번 세지 않으려면 transition DAG의 path만 세고 occurrence는 섞지 않습니다.

## 5. 가장 긴 반복 Substring

반복 substring은 occurrence가 2 이상인 문자열입니다. state `v`가 occurrence 2 이상이면 그 state가 대표하는 길이 구간 중 최댓값 `len[v]`가 후보가 됩니다.

```text
answer = max(len[v]) over occ[v] >= 2
```

문자열 자체를 복원하려면 각 state의 대표 end position을 함께 저장해 두고 `end - len[v] + 1` 구간을 잘라냅니다.

## 6. 여러 문자열 공통 Substring

문자열 `S`로 automaton을 만들고 다른 문자열 `T`를 훑으면 각 위치에서 현재 matched length를 알 수 있습니다. 이 값을 state별로 최대로 기록한 뒤 suffix link 역순으로 `min(len[link child], matched)` 형태로 올립니다.

여러 문자열의 최장 공통 substring은 각 문자열마다 얻은 state별 최대 match의 최솟값을 유지한 뒤 최댓값을 구합니다.

## 7. Suffix Array와 비교

| 문제 | Suffix Automaton | Suffix Array/LCP |
| --- | --- | --- |
| online append | 강함 | 다시 구성 필요 |
| k번째 substring | DAG DP로 직접 처리 | LCP로 중복 개수 보정 |
| 많은 pattern 포함 질의 | transition scan | binary search |
| 정렬된 suffix 구간 | 약함 | 강함 |
| 여러 문자열 LCS | scan과 state DP | generalized suffix array |

둘은 대체재라기보다 문제 신호가 다릅니다. "확장 가능한 상태"가 보이면 automaton, "정렬된 suffix 순서"가 보이면 suffix array가 자연스럽습니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| construction | `O(N * transition cost)` |
| occurrence 누적 | `O(number of states + edges)` |
| path count DP | `O(edges)` |
| k번째 substring | `O(answer length * alphabet)` |
| 한 문자열 scan | `O(length)` |

상태 수는 최대 `2N-1`입니다. alphabet이 크면 transition을 `array` 대신 map이나 압축 vector로 바꿉니다.

## 9. 자주 하는 실수

1. suffix link tree와 transition DAG를 같은 방향 그래프로 취급한다.
2. clone state의 occurrence를 1로 둔다.
3. state 하나가 정확히 한 substring만 뜻한다고 생각한다.
4. k번째 substring에서 빈 문자열을 포함할지 제외할지 정하지 않는다.
5. 여러 문자열 공통 substring에서 state별 match를 suffix link로 전파하지 않는다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: suffix automaton applications `/practice/...` 문제 필요 | occurrence 누적 | suffix link order |
| 표준 | TODO: kth substring `/practice/...` 문제 필요 | transition DAG DP | lexicographic path |
| 응용 | TODO: repeated substring query `/practice/...` 문제 필요 | occurrence threshold | endpos |
| 함정 | TODO: multiple strings LCS `/practice/...` 문제 필요 | state별 match 전파 | generalized scan |
