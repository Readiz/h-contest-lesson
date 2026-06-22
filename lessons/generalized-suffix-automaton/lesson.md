# Generalized Suffix Automaton

Generalized Suffix Automaton은 여러 문자열의 substring 집합을 하나의 automaton에 합치고, 문자열별 등장 여부나 occurrence를 상태 단위로 집계하는 문자열 심화 기법입니다. 단일 문자열 SAM이 "한 문자열의 모든 substring"을 압축한다면, generalized SAM은 여러 문자열에서 공통으로 등장하는 substring, 특정 그룹에만 등장하는 substring, dictionary 전체의 substring 통계를 다룹니다.

이 레슨은 Suffix Automaton과 Suffix Automaton Applications 이후에 보는 문자열 심화입니다.

1. 여러 문자열을 단순히 separator로 이어 붙이는 방식과 trie 기반 generalized construction을 구분한다.
2. 상태별로 "어떤 문자열에서 얼마 길이까지 match되었는지"를 누적한다.
3. longest common substring, group coverage, occurrence aggregation 문제를 automaton DP로 바꾼다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Suffix Automaton, suffix link, transition DAG, occurrence 누적
- 함께 보면 좋은 레슨: Suffix Automaton Applications, Trie와 Aho-Corasick, Suffix Array 응용 패턴
- 다음에 볼 레슨: multi-string substring query, dictionary substring analytics

## 1. 문제 신호

| 문제 표현 | Generalized SAM 관점 |
| --- | --- |
| 여러 문자열에 모두 등장하는 가장 긴 substring | 문자열별 maximum match length의 최솟값 |
| 적어도 K개 문자열에 등장하는 substring | state coverage count |
| forbidden 문자열 집합을 피하는 substring | dictionary automaton + DP |
| 문자열 그룹 A에는 있고 B에는 없는 substring | state별 bitset/group mask |
| 많은 pattern 대신 많은 text를 합친다 | trie 기반 generalized SAM 후보 |

단일 문자열 두 개 정도면 한 문자열로 SAM을 만들고 다른 문자열을 scan하면 충분합니다. 문자열이 많고 전체 substring 집합을 계속 재사용해야 할 때 generalized SAM을 고려합니다.

## 2. 두 가지 구성 방식

| 방식 | 장점 | 주의점 |
| --- | --- | --- |
| separator로 문자열을 이어 붙인 뒤 SAM 구성 | 구현이 쉽다 | separator가 문자열마다 달라야 하고, separator를 가로지르는 substring을 걸러야 한다 |
| Trie를 만든 뒤 BFS/DFS 순서로 SAM 확장 | dictionary 전체를 자연스럽게 합친다 | construction 순서와 clone 처리 이해가 필요하다 |

대회에서는 separator 방식이 가장 빠르게 쓸 수 있습니다. 다만 문자열 수가 많고 alphabet이 넓으면 고유 separator를 만들기 어렵고, 이때 trie 기반 접근이 깔끔합니다.

## 3. 문자열별 Match Length 누적

기준 automaton을 만든 뒤 각 문자열 `T`를 transition으로 훑으면 각 위치에서 현재 state `v`와 match length `len`을 얻습니다.

```text
for each string T:
  v = root, matched = 0
  for ch in T:
    while v has no transition ch:
      v = link[v]
      matched = len[v]
    move ch
    matched += 1
    bestForThisString[v] = max(bestForThisString[v], matched)
  suffix link 역순으로 best를 부모 쪽에 min(best[child], len[parent])로 전파
```

모든 문자열에 대해 state별 match 값을 얻으면, common substring 길이는 state별 값들의 최솟값으로 계산할 수 있습니다.

## 4. Longest Common Substring of Many Strings

첫 번째 문자열로 SAM을 만들고 나머지 문자열을 하나씩 scan하는 방식입니다. state마다 "지금까지 처리한 모든 문자열에서 가능한 최대 길이"를 유지합니다.

```cpp compile-check
#include <algorithm>
#include <array>
#include <string>
#include <vector>
using namespace std;

struct GeneralizedSamLcs {
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

    GeneralizedSamLcs() {
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

    vector<int> orderByLengthDesc() const {
        vector<int> order(st.size());
        for (int i = 0; i < (int)st.size(); ++i) {
            order[i] = i;
        }
        sort(order.begin(), order.end(), [&](int a, int b) {
            return st[a].len > st[b].len;
        });
        return order;
    }

    int longestCommonSubstring(const vector<string>& others) {
        const int INF = 1 << 30;
        vector<int> common(st.size(), INF);
        vector<int> order = orderByLengthDesc();

        for (const string& t : others) {
            vector<int> best(st.size(), 0);
            int v = 0;
            int matched = 0;

            for (char ch : t) {
                int c = ch - 'a';
                while (v != -1 && st[v].next[c] == -1) {
                    v = st[v].link;
                    matched = (v == -1 ? 0 : st[v].len);
                }
                if (v == -1) {
                    v = 0;
                    matched = 0;
                    continue;
                }
                v = st[v].next[c];
                ++matched;
                best[v] = max(best[v], matched);
            }

            for (int state : order) {
                int parent = st[state].link;
                if (parent != -1) {
                    best[parent] = max(best[parent], min(best[state], st[parent].len));
                }
            }

            for (int i = 0; i < (int)st.size(); ++i) {
                common[i] = min(common[i], best[i]);
            }
        }

        int answer = 0;
        for (int value : common) {
            if (value != INF) {
                answer = max(answer, value);
            }
        }
        return answer;
    }
};
```

`common[v]`는 state `v`가 대표하는 길이 구간 중 모든 문자열에서 보장되는 최대 길이입니다. 답은 모든 state의 `common[v]` 최댓값입니다.

## 5. Coverage Count

적어도 K개 문자열에 등장하는 substring을 찾을 때는 문자열별 best length를 모두 저장하지 않고, state별 coverage count만 세는 방식도 가능합니다.

```text
for each string:
  best[v] 계산
  for v:
    if best[v] > len[link[v]]:
      covered[v] += 1
```

state `v`가 대표하는 길이 구간은 `(len[link[v]], len[v]]`입니다. 어떤 문자열의 `best[v]`가 이 구간 일부 이상이면 그 길이까지만 coverage 후보가 됩니다. 길이별 정답이 필요하면 difference array나 event를 함께 둡니다.

## 6. Separator 방식의 함정

문자열들을 `S1#S2$S3%...`처럼 이어 붙이면 SAM 자체는 간단합니다. 하지만 separator를 포함하는 path도 automaton 안에 생깁니다.

| 함정 | 방지 방법 |
| --- | --- |
| separator를 가로지르는 substring을 답에 포함 | scan 단계에서 원본 문자열별 match만 기록 |
| separator가 alphabet과 충돌 | 입력에 없는 고유 문자 사용 |
| 문자열 수가 alphabet보다 많음 | trie 기반 generalized construction 또는 정수 alphabet |
| occurrence가 문자열별 등장인지 전체 등장인지 혼동 | count 목적을 먼저 정의 |

공통 substring 길이만 필요하면 separator SAM보다 "첫 문자열 SAM + 나머지 scan"이 단순합니다.

## 7. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| 기준 SAM 구성 | `O(|S| * transition cost)` |
| 각 문자열 scan | `O(|T| * suffix fallback cost)` |
| state별 역순 전파 | 문자열마다 `O(number of states)` |
| 전체 LCS | `O(total length + number of strings * states)` |
| 메모리 | `O(states * alphabet)` 또는 map 기반 |

문자열 개수가 매우 많으면 `number of strings * states`가 병목이 됩니다. 이때는 bitset, sparse visited list, group별 aggregation을 고려합니다.

## 8. 자주 하는 실수

1. state 하나가 정확히 하나의 substring이라고 가정한다.
2. best length를 suffix link 부모에게 전파할 때 `len[parent]`로 clamp하지 않는다.
3. separator를 포함한 substring을 제거하지 않는다.
4. clone state의 occurrence와 coverage를 construction 시점에 확정하려고 한다.
5. 문자열별 occurrence와 전체 occurrence를 같은 값으로 취급한다.

## 9. 문제를 볼 때 체크할 조건

- 문자열이 몇 개인가?
- 필요한 값이 longest common substring인지, 모든 substring count인지 확인했는가?
- 각 문자열별 등장 여부만 필요한가, 등장 횟수까지 필요한가?
- alphabet이 작아서 array transition을 쓸 수 있는가?
- separator 방식으로 풀 때 가로지르는 substring을 확실히 배제할 수 있는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: generalized suffix automaton `/practice/...` 문제 필요 | 여러 문자열 LCS | state별 match length |
| 표준 | TODO: at least K strings substring `/practice/...` 문제 필요 | coverage count | suffix link propagation |
| 응용 | TODO: group substring difference `/practice/...` 문제 필요 | 그룹별 mask 집계 | bitset aggregation |
| 함정 | TODO: separator crossing substring `/practice/...` 문제 필요 | separator 제거 | per-string scan |
