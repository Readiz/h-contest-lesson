# Trie와 Aho-Corasick

Trie는 문자열들을 글자 단위로 공유해서 저장하는 트리입니다. 한 패턴을 찾을 때는 KMP나 Z algorithm이 충분하지만, 패턴이 수천 개 이상이고 텍스트를 한 번만 훑어야 한다면 Trie에 실패 링크를 붙인 Aho-Corasick을 씁니다.

이 레슨은 세 단계를 연결합니다.

1. 여러 문자열을 Trie에 넣고 접두사를 공유한다.
2. 실패 링크로 "현재 접두사가 깨졌을 때 돌아갈 가장 긴 접미사 상태"를 만든다.
3. 텍스트를 한 번 훑으며 여러 패턴의 등장 여부를 동시에 찾는다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 문자열 매칭, BFS, 배열 기반 그래프 표현
- 함께 보면 좋은 레슨: 문자열 매칭: KMP, Z, Rolling Hash
- 다음에 볼 레슨: Suffix Array와 LCP

## 1. Trie가 필요한 상황

단어 집합이 있고 접두사 기준으로 빠르게 탐색해야 하면 Trie를 떠올립니다.

| 문제 신호 | Trie 관점 |
| --- | --- |
| 사전에 있는 단어인지 많이 확인한다 | 루트에서 글자를 따라 내려간다 |
| 어떤 문자열이 다른 문자열의 접두사인지 본다 | 중간 노드의 종료 표시를 본다 |
| 자동완성 후보를 찾는다 | 접두사 노드의 서브트리를 훑는다 |
| 여러 패턴을 동시에 찾아야 한다 | Trie에 실패 링크를 붙여 Aho-Corasick으로 확장한다 |

Trie의 한 노드는 "지금까지 읽은 접두사"를 뜻합니다. 같은 접두사를 가진 문자열들은 같은 경로를 공유하므로, 전체 저장 공간은 문자열 길이 합에 비례합니다.

## 2. 배열 기반 Trie

알파벳 소문자만 다루는 문제라면 각 노드에 `26`개 자식 인덱스를 둘 수 있습니다. 문자가 더 다양하면 `map`이나 압축 인덱스를 쓰지만, 대회 문제에서는 배열 Trie가 빠르고 단순합니다.

```cpp compile-check
#include <array>
#include <string>
#include <vector>
using namespace std;

struct TrieNode {
    array<int, 26> next;
    int terminalCount;

    TrieNode() : terminalCount(0) {
        next.fill(-1);
    }
};

struct Trie {
    vector<TrieNode> nodes;

    Trie() {
        nodes.push_back(TrieNode());
    }

    void insert(const string& word) {
        int current = 0;
        for (char ch : word) {
            int c = ch - 'a';
            if (nodes[current].next[c] == -1) {
                nodes[current].next[c] = (int)nodes.size();
                nodes.push_back(TrieNode());
            }
            current = nodes[current].next[c];
        }
        ++nodes[current].terminalCount;
    }

    bool contains(const string& word) const {
        int current = 0;
        for (char ch : word) {
            int c = ch - 'a';
            if (nodes[current].next[c] == -1) {
                return false;
            }
            current = nodes[current].next[c];
        }
        return nodes[current].terminalCount > 0;
    }
};
```

`terminalCount`는 같은 단어가 여러 번 들어올 수 있는 경우를 처리하기 위해 개수로 둔 값입니다. 중복이 의미 없으면 `bool terminal`만 둬도 됩니다.

## 3. Aho-Corasick의 실패 링크

Aho-Corasick은 Trie 위에 KMP의 실패 함수와 비슷한 링크를 붙입니다. 현재 노드가 나타내는 문자열 뒤에 글자 `c`를 붙였는데 Trie 경로가 없다면, 가능한 가장 긴 접미사 상태로 이동해서 다시 시도합니다.

예를 들어 패턴이 `he`, `she`, `his`, `hers`라면 `she`를 읽은 상태에는 패턴 `he`도 접미사로 숨어 있습니다. 실패 링크와 출력 전파가 있어야 이런 겹친 패턴을 놓치지 않습니다.

실패 링크는 BFS 순서로 만듭니다. 부모의 실패 링크가 이미 계산되어 있어야 자식의 실패 링크를 정할 수 있기 때문입니다.

```cpp compile-check
#include <array>
#include <queue>
#include <string>
#include <vector>
using namespace std;

struct AhoNode {
    array<int, 26> next;
    int fail;
    int outputCount;

    AhoNode() : fail(0), outputCount(0) {
        next.fill(-1);
    }
};

struct AhoCorasick {
    vector<AhoNode> nodes;

    AhoCorasick() {
        nodes.push_back(AhoNode());
    }

    void insert(const string& pattern) {
        int current = 0;
        for (char ch : pattern) {
            int c = ch - 'a';
            if (nodes[current].next[c] == -1) {
                nodes[current].next[c] = (int)nodes.size();
                nodes.push_back(AhoNode());
            }
            current = nodes[current].next[c];
        }
        ++nodes[current].outputCount;
    }

    void build() {
        queue<int> q;
        for (int c = 0; c < 26; ++c) {
            int child = nodes[0].next[c];
            if (child == -1) {
                nodes[0].next[c] = 0;
            } else {
                nodes[child].fail = 0;
                q.push(child);
            }
        }

        while (!q.empty()) {
            int current = q.front();
            q.pop();

            nodes[current].outputCount += nodes[nodes[current].fail].outputCount;

            for (int c = 0; c < 26; ++c) {
                int child = nodes[current].next[c];
                if (child == -1) {
                    nodes[current].next[c] = nodes[nodes[current].fail].next[c];
                    continue;
                }
                nodes[child].fail = nodes[nodes[current].fail].next[c];
                q.push(child);
            }
        }
    }

    long long countMatches(const string& text) const {
        long long matches = 0;
        int current = 0;
        for (char ch : text) {
            int c = ch - 'a';
            current = nodes[current].next[c];
            matches += nodes[current].outputCount;
        }
        return matches;
    }
};
```

위 구현은 `build()`에서 없는 전이를 미리 채웁니다. 그래서 검색 중에는 `while`로 실패 링크를 따라가지 않고 `current = next[current][c]` 한 번으로 이동합니다.

## 4. 무엇을 세야 하는지 먼저 정하기

Aho-Corasick 문제는 구현보다 집계 방식에서 더 자주 틀립니다.

| 요구 | 필요한 정보 |
| --- | --- |
| 패턴이 하나라도 등장하는가 | `outputCount > 0` 여부 |
| 모든 등장 횟수 합 | 실패 링크 조상 출력을 더한 `outputCount` |
| 각 패턴별 등장 횟수 | terminal 노드 id와 fail tree 누적 |
| 등장 위치 출력 | 패턴 길이와 현재 텍스트 인덱스 |
| 금지 패턴을 피하는 DP | automaton 상태와 `outputCount == 0` 조건 |

각 패턴별 등장 횟수를 모두 구해야 할 때는 검색 중 방문한 상태 횟수를 세고, 실패 링크로 만든 트리에서 자식의 방문 수를 부모로 올리는 방법을 많이 씁니다. 패턴 노드에 누적된 방문 수가 그 패턴의 등장 횟수입니다.

## 5. 실패 링크와 출력 전파

실패 링크는 "다음 후보 상태"이고, 출력 전파는 "현재 상태에서 끝나는 모든 패턴"입니다. 둘을 섞어 생각하면 겹친 매칭을 놓칩니다.

```text
patterns: he, she
text: she

현재 상태는 "she"
직접 끝나는 패턴: she
fail을 따라가면 "he"
함께 끝나는 패턴: he
```

`nodes[current].outputCount += nodes[fail].outputCount`처럼 build 단계에서 전파하면 검색이 간단해집니다. 반대로 각 패턴별 id 목록이 필요하면 `vector<int> outputIds`를 합치거나, 검색 뒤 fail tree 누적을 사용합니다.

## 6. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| Trie 삽입 | 전체 패턴 길이 합 `O(S)` | `O(S * alphabet)` 또는 sparse 구조 |
| 실패 링크 생성 | `O(S * alphabet)` | Trie 노드 배열 |
| 텍스트 검색 | `O(N)` | 검색 상태 `O(1)` |
| 각 패턴별 누적 | `O(S + N)` | fail tree와 방문 수 |

알파벳이 `26`보다 훨씬 크면 모든 노드에 전체 alphabet 배열을 두는 방식이 부담됩니다. 이때는 문자 압축, `unordered_map`, 정렬된 edge list 같은 sparse 표현을 검토합니다.

## 7. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 루트의 없는 전이를 `-1`로 남김 | 검색 중 음수 인덱스 접근 | build 후 루트 전이는 루트로 채우기 |
| 실패 링크의 출력을 더하지 않음 | 접미사 패턴 누락 | `she` 안의 `he` 같은 예제로 테스트 |
| 패턴 길이를 저장하지 않음 | 등장 위치 복원 불가 | terminal 노드에 pattern id/length 보관 |
| 대문자/숫자 입력을 그대로 `ch - 'a'` 처리 | 범위 밖 접근 | 입력 alphabet 확인 후 압축 |
| 같은 패턴 중복을 무시 | 등장 횟수 차이 | 중복이 의미 있는지 문제에서 확인 |
| 텍스트가 여러 개일 때 상태를 유지 | 케이스 사이 오염 | 각 텍스트 검색은 `current = 0`에서 시작 |

## 8. 문제를 볼 때 체크할 조건

1. 패턴 개수와 전체 길이 합이 얼마나 되는가?
2. 알파벳이 고정 소문자인가, 임의 문자 집합인가?
3. 하나라도 등장하면 되는가, 모든 등장 횟수를 세야 하는가?
4. 각 패턴별 결과가 필요한가?
5. 겹치는 매칭을 포함해야 하는가?
6. 금지 문자열을 피하는 DP처럼 automaton 상태를 재사용해야 하는가?

문자열 다중 패턴 문제는 먼저 Trie로 상태를 만들고, 실패 링크로 KMP식 되돌아가기를 자동화한다고 이해하면 됩니다.

## 9. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: Trie 사전 조회 `/practice/...` 문제 필요 | 단어 삽입과 prefix 탐색 구현 | trie node |
| 표준 | TODO: 다중 패턴 등장 여부 `/practice/...` 문제 필요 | 실패 링크와 출력 전파 구현 | fail link |
| 응용 | TODO: 각 패턴별 등장 횟수 `/practice/...` 문제 필요 | fail tree 누적과 terminal id 관리 | occurrence count |
| 함정 | TODO: 금지 문자열 DP `/practice/...` 문제 필요 | automaton 상태와 DP 결합 | forbidden pattern |
