# Palindromic Tree

Palindromic Tree는 문자열의 모든 서로 다른 palindrome substring을 노드로 압축해 저장하는 자료구조입니다. Eertree라고도 부르며, 문자열을 왼쪽에서 오른쪽으로 읽으면서 새로 생기는 palindrome을 `O(1)` amortized에 가까운 방식으로 추가합니다.

이 레슨은 Suffix Automaton 이후에 보는 "부분 문자열 구조 압축"의 palindrome 버전입니다.

1. 두 개의 root로 홀수/짝수 palindrome을 동시에 관리한다.
2. suffix link를 따라가며 새 문자를 양끝에 붙일 수 있는 palindrome을 찾는다.
3. 각 palindrome의 개수, 길이, suffix 관계를 DP로 활용한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 문자열, palindrome, suffix link 감각, Suffix Automaton
- 함께 보면 좋은 레슨: Suffix Automaton, 문자열 매칭, Trie와 Aho-Corasick
- 다음에 볼 레슨: palindromic DP, Manacher, palindromic automaton 응용

## 1. 문제 신호

Palindromic Tree는 palindrome substring을 "모두" 다뤄야 할 때 강합니다.

| 문제 표현 | Palindromic Tree 관점 |
| --- | --- |
| 서로 다른 palindrome substring 개수 | 노드 개수 |
| 각 palindrome의 등장 횟수 | 생성 count를 suffix link 역순 누적 |
| prefix마다 새 palindrome 개수 | 문자 추가 시 새 노드 여부 |
| palindrome suffix를 따라 DP | suffix link tree |
| 온라인으로 문자를 하나씩 추가 | Eertree construction |

단순히 가장 긴 palindrome만 필요하면 Manacher가 더 간단합니다. 서로 다른 palindrome들을 노드로 보존해야 할 때 Palindromic Tree가 빛납니다.

## 2. 두 root

Palindromic Tree에는 특수 root가 두 개 있습니다.

| root | 길이 | 의미 |
| --- | ---: | --- |
| odd root | `-1` | 모든 홀수 palindrome 확장의 시작점 |
| even root | `0` | 빈 문자열 palindrome |

길이 `-1` root는 경계 처리를 쉽게 해 줍니다. 새 문자를 붙일 때 "현재 palindrome 양끝 바깥 문자가 같은가"를 검사하는데, 길이 `-1` root는 항상 다음 확장 후보가 되도록 작동합니다.

## 3. Construction

문자열의 새 위치 `pos`에 문자 `s[pos]`를 추가한다고 합시다. 현재 longest palindromic suffix를 가리키는 `last`에서 suffix link를 따라가며, 양끝에 새 문자를 붙여도 palindrome이 되는 가장 긴 노드를 찾습니다.

이미 그 문자 transition이 있으면 `last`만 이동합니다. 없으면 새 palindrome 노드를 만들고 suffix link를 정합니다.

```cpp compile-check
#include <array>
#include <string>
#include <vector>
using namespace std;

struct PalindromicTree {
    struct Node {
        int len = 0;
        int link = 0;
        int count = 0;
        array<int, 26> next{};

        Node() {
            next.fill(0);
        }
    };

    vector<Node> tree;
    string s;
    int last = 1;

    PalindromicTree() {
        tree.push_back(Node{});
        tree.push_back(Node{});
        tree[0].len = -1;
        tree[0].link = 0;
        tree[1].len = 0;
        tree[1].link = 0;
    }

    int getSuffixCandidate(int node, int pos) const {
        while (true) {
            int mirrored = pos - 1 - tree[node].len;
            if (mirrored >= 0 && s[mirrored] == s[pos]) {
                return node;
            }
            node = tree[node].link;
        }
    }

    bool addChar(char ch) {
        s.push_back(ch);
        int pos = (int)s.size() - 1;
        int c = ch - 'a';

        int current = getSuffixCandidate(last, pos);
        if (tree[current].next[c] != 0) {
            last = tree[current].next[c];
            tree[last].count += 1;
            return false;
        }

        int created = (int)tree.size();
        tree.push_back(Node{});
        tree[created].len = tree[current].len + 2;
        tree[created].count = 1;
        tree[current].next[c] = created;

        if (tree[created].len == 1) {
            tree[created].link = 1;
        } else {
            int linkCandidate = getSuffixCandidate(tree[current].link, pos);
            tree[created].link = tree[linkCandidate].next[c];
        }

        last = created;
        return true;
    }

    void build(const string& text) {
        for (char ch : text) {
            addChar(ch);
        }
    }
};
```

위 구현은 소문자 알파벳을 가정합니다. 문자 종류가 넓다면 `array<int, 26>` 대신 map 또는 압축된 transition 구조를 사용합니다.

## 4. 서로 다른 palindrome 개수

두 root를 제외한 노드 하나가 서로 다른 palindrome substring 하나입니다.

```text
distinct palindrome count = number of nodes - 2
```

문자를 추가할 때 새 노드가 생기면 그 prefix에서 처음 등장한 palindrome이 하나 늘어난 것입니다. 그래서 prefix별 distinct count도 온라인으로 계산할 수 있습니다.

## 5. 등장 횟수 누적

`count[v]`를 노드 `v`가 longest palindromic suffix로 선택된 횟수로 두면, suffix link 역순으로 더해 각 palindrome의 총 등장 횟수를 얻습니다.

```cpp compile-check
#include <vector>
using namespace std;

struct PalNodeCount {
    int link;
    int count;
};

void accumulatePalindromeCounts(vector<PalNodeCount>& nodes) {
    for (int v = (int)nodes.size() - 1; v >= 2; --v) {
        nodes[nodes[v].link].count += nodes[v].count;
    }
}
```

construction 중 노드는 길이가 대체로 증가하는 순서로 만들어지므로, 뒤에서 앞으로 처리하면 자식 palindrome의 등장 횟수가 suffix link 부모로 모입니다.

## 6. Manacher와 비교

| 도구 | 강점 | 한계 |
| --- | --- | --- |
| Manacher | 각 중심의 최대 반지름을 `O(N)`에 계산 | distinct palindrome 노드 관리가 없음 |
| Palindromic Tree | 서로 다른 palindrome과 suffix 관계 저장 | 구현이 더 복잡 |
| DP 직접 검사 | 구현 단순 | `O(N^2)` 이상 |

가장 긴 palindrome substring만 묻는다면 Manacher가 더 좋습니다. 각 palindrome을 세거나, palindrome suffix를 타고 DP를 해야 하면 Palindromic Tree를 고려합니다.

## 7. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| 문자 하나 추가 | amortized `O(alphabet transition cost)` | 새 노드 최대 1개 |
| 전체 build | `O(N)` for fixed alphabet | 최대 `N + 2` 노드 |
| distinct count | `O(1)` | 노드 수 사용 |
| occurrence 누적 | `O(number of nodes)` | count 배열 |

각 위치에서 새 palindrome은 최대 하나만 생깁니다. 그래서 전체 노드 수도 `N + 2`를 넘지 않습니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 길이 `-1` root를 생략 | 경계 처리 복잡/오류 | odd root와 even root 둘 다 유지 |
| 새 노드 suffix link를 current에서 바로 찾음 | link가 자기 자신으로 꼬임 | `tree[current].link`부터 후보 탐색 |
| transition 기본값과 node index 충돌 | root transition 오해 | 0번 root를 특수값으로 쓸 때 설계 고정 |
| occurrence를 생성 횟수로만 사용 | 짧은 palindrome 등장 누락 | suffix link 역순 누적 |
| alphabet 범위 가정 오류 | 범위 밖 접근 | 입력 문자 set 확인 |
| Manacher로 충분한 문제에 과한 구현 | 시간 낭비 | 필요한 정보가 distinct인지 확인 |

## 9. 문제를 볼 때 체크할 조건

1. 서로 다른 palindrome substring을 모두 다뤄야 하는가?
2. 각 palindrome의 등장 횟수나 길이별 통계가 필요한가?
3. prefix를 읽으며 온라인으로 답을 내야 하는가?
4. 가장 긴 palindrome만 필요해서 Manacher가 충분하지 않은가?
5. alphabet 크기에 맞는 transition 구조를 골랐는가?
6. occurrence 누적 순서가 suffix link 방향과 맞는가?

Palindromic Tree는 palindrome substring을 노드로 만든다는 점에서 Suffix Automaton과 비슷한 감각을 줍니다. 다만 suffix link가 "가장 긴 proper palindromic suffix"로 이어진다는 차이를 정확히 잡아야 합니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 서로 다른 palindrome 개수 `/practice/...` 문제 필요 | 새 노드 개수 세기 | eertree |
| 표준 | TODO: palindrome 등장 횟수 `/practice/...` 문제 필요 | suffix link 역순 count 누적 | occurrence |
| 응용 | TODO: prefix별 palindrome 통계 `/practice/...` 문제 필요 | 온라인 추가와 last 관리 | palindromic suffix |
| 함정 | TODO: 큰 alphabet palindrome `/practice/...` 문제 필요 | transition 구조 변경 | alphabet mapping |
