# Palindromic Tree

Palindromic Tree는 문자열의 모든 서로 다른 palindrome substring을 노드로 압축해 저장하는 자료구조입니다. Eertree라고도 부르며, 문자열을 왼쪽에서 오른쪽으로 읽으면서 새로 생기는 palindrome을 `O(1)` amortized에 가까운 방식으로 추가합니다.


입력은 소문자입니다. 등장 횟수 누적은 모든 문자를 추가한 뒤 `accumulatePalindromeCounts(eertree.tree)`로 한 번만 호출합니다. suffix link는 항상 먼저 생성된 노드를 가리키므로 생성 번호 역순 누적이 가능합니다. 노드 길이가 생성 순서대로 증가하는 것은 아닙니다.

## 문제 신호

Palindromic Tree는 palindrome substring을 "모두" 다뤄야 할 때 강합니다.

| 문제 표현 | Palindromic Tree 관점 |
| --- | --- |
| 서로 다른 palindrome substring 개수 | 노드 개수 |
| 각 palindrome의 등장 횟수 | 생성 count를 suffix link 역순 누적 |
| prefix마다 새 palindrome 개수 | 문자 추가 시 새 노드 여부 |
| palindrome suffix를 따라 DP | suffix link tree |
| 온라인으로 문자를 하나씩 추가 | Eertree construction |

단순히 가장 긴 palindrome만 필요하면 Manacher가 더 간단합니다. 서로 다른 palindrome들을 노드로 보존해야 할 때 Palindromic Tree가 빛납니다.

## 두 root

Palindromic Tree에는 특수 root가 두 개 있습니다.

| root | 길이 | 의미 |
| --- | ---: | --- |
| odd root | `-1` | 모든 홀수 palindrome 확장의 시작점 |
| even root | `0` | 빈 문자열 palindrome |

길이 `-1` root는 경계 처리를 쉽게 해 줍니다. 새 문자를 붙일 때 "현재 palindrome 양끝 바깥 문자가 같은가"를 검사하는데, 길이 `-1` root는 항상 다음 확장 후보가 되도록 작동합니다.

## Construction

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
        *this = PalindromicTree();
        for (char ch : text) {
            addChar(ch);
        }
    }
};
```

위 구현은 소문자 알파벳을 가정합니다. 문자 종류가 넓다면 `array<int, 26>` 대신 map 또는 압축된 transition 구조를 사용합니다.

## 서로 다른 palindrome 개수

두 root를 제외한 노드 하나가 서로 다른 palindrome substring 하나입니다.

```text
distinct palindrome count = number of nodes - 2
```

문자를 추가할 때 새 노드가 생기면 그 prefix에서 처음 등장한 palindrome이 하나 늘어난 것입니다. 그래서 prefix별 distinct count도 온라인으로 계산할 수 있습니다.

## 등장 횟수 누적

`count[v]`를 노드 `v`가 longest palindromic suffix로 선택된 횟수로 두면, suffix link 역순으로 더해 각 palindrome의 총 등장 횟수를 얻습니다.

```cpp compile-check
#include <vector>
using namespace std;

template<class Node>
void accumulatePalindromeCounts(vector<Node>& nodes) {
    for (int v = (int)nodes.size() - 1; v >= 2; --v) {
        nodes[nodes[v].link].count += nodes[v].count;
    }
}
```

suffix link는 항상 먼저 만들어진 노드를 가리키므로, 뒤에서 앞으로 처리하면 자식 palindrome의 등장 횟수가 suffix link 부모로 모입니다.

## Manacher와 비교

| 도구 | 강점 | 한계 |
| --- | --- | --- |
| Manacher | 각 중심의 최대 반지름을 `O(N)`에 계산 | distinct palindrome 노드 관리가 없음 |
| Palindromic Tree | 서로 다른 palindrome과 suffix 관계 저장 | 구현이 더 복잡 |
| DP 직접 검사 | 구현 단순 | `O(N^2)` 이상 |

가장 긴 palindrome substring만 묻는다면 Manacher가 더 좋습니다. 각 palindrome을 세거나, palindrome suffix를 타고 DP를 해야 하면 Palindromic Tree를 고려합니다.

## 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| 문자 하나 추가 | amortized `O(alphabet transition cost)` | 새 노드 최대 1개 |
| 전체 build | `O(N)` for fixed alphabet | 최대 `N + 2` 노드 |
| distinct count | `O(1)` | 노드 수 사용 |
| occurrence 누적 | `O(number of nodes)` | count 배열 |

각 위치에서 새 palindrome은 최대 하나만 생깁니다. 그래서 전체 노드 수도 `N + 2`를 넘지 않습니다.

## 대표 로컬 연습: 서로 다른 Palindrome Substring 개수

문자열 `S`가 주어졌을 때, `S`에 등장하는 서로 다른 non-empty palindrome substring의 개수를 출력합니다.

### 입력

```text
S
```

- `1 <= |S| <= 200000`
- `S`는 영어 소문자로만 이루어져 있습니다.

### 출력

```text
서로 다른 palindrome substring 개수
```

### 예시

```text
ababa
```

```text
5
```

`ababa`의 서로 다른 palindrome substring은 `a`, `b`, `aba`, `bab`, `ababa`입니다.

## 손으로 따라가는 Trace

Eertree는 두 root를 먼저 둡니다.

| node | 길이 | 의미 | suffix link |
| ---: | ---: | --- | --- |
| 0 | `-1` | odd root | 0 |
| 1 | `0` | even root | 0 |

`S = ababa`를 왼쪽부터 추가하면 새로 생기는 node는 아래처럼 하나씩만 늘어납니다.

| 위치 | 문자 | 추가 뒤 longest palindromic suffix | 새 node | distinct 개수 |
| ---: | --- | --- | --- | ---: |
| 0 | `a` | `a` | `a` | 1 |
| 1 | `b` | `b` | `b` | 2 |
| 2 | `a` | `aba` | `aba` | 3 |
| 3 | `b` | `bab` | `bab` | 4 |
| 4 | `a` | `ababa` | `ababa` | 5 |

이때 suffix link는 "가장 긴 proper palindromic suffix"로 이어집니다.

| palindrome | suffix link 대상 |
| --- | --- |
| `a` | even root |
| `b` | even root |
| `aba` | `a` |
| `bab` | `b` |
| `ababa` | `aba` |

답은 항상 `node count - 2`입니다. 두 root는 실제 substring이 아니므로 빼야 합니다.

## 구현 기준

```cpp
// https://h.readiz.com/learn/palindrome-structures/palindromic-tree의 PalindromicTree를 앞에 둔다.
#include <iostream>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s;
    cin >> s;

    PalindromicTree tree;
    for (char ch : s) {
        tree.addChar(ch);
    }
    cout << (tree.tree.size() - 2) << '\n';
}
```

## 검증용 Case

| 입력 | 정답 | 확인 포인트 |
| --- | ---: | --- |
| `a` | 1 | 길이 1 node의 suffix link는 even root |
| `aa` | 2 | `a`, `aa`가 서로 다른 palindrome |
| `aaaa` | 4 | 매 prefix에서 새 palindrome 하나가 생김 |
| `abcd` | 4 | 길이 1 palindrome만 존재 |
| `ababa` | 5 | suffix link가 `ababa -> aba -> a`로 이어짐 |
| `abacaba` | 7 | `a`, `b`, `c`, `aba`, `aca`, `bacab`, `abacaba` |

## Stress 기준

짧은 문자열에서는 brute force set과 비교합니다.

1. 길이 `1..10`, alphabet `{a,b,c}`에서 모든 substring을 잘라 palindrome인지 직접 검사합니다.
2. palindrome인 substring만 `set<string>`에 넣고 크기를 구합니다.
3. Eertree의 `tree.tree.size() - 2`와 brute force set size가 항상 같은지 비교합니다.

이 stress를 통과하면 root 개수 제외, suffix link 후보 탐색, 새 node 생성 조건의 흔한 실수를 대부분 잡을 수 있습니다.
