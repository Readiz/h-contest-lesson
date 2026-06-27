# Suffix Tree와 Ukkonen

Suffix Tree는 한 문자열의 모든 suffix를 압축 trie로 저장한 구조입니다. Suffix Array나 Suffix Automaton보다 구현 난도는 높지만, substring 위치, LCP, 반복 구간, 여러 문자열 공통 부분을 "간선 구간"으로 직접 다룰 수 있습니다.

이 레슨은 Suffix Array, Suffix Automaton, Lyndon Factorization 이후에 보는 문자열 구조 심화입니다.

1. 모든 suffix를 trie에 넣으면 `O(N^2)` 노드가 될 수 있다.
2. 경로를 한 글자씩 저장하지 않고 원문 구간 `[l, r)`로 압축한다.
3. Ukkonen 알고리즘은 active point와 suffix link로 suffix tree를 온라인 `O(N log alphabet)`에 만든다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Trie, suffix array, suffix automaton, 문자열 index 구간
- 함께 보면 좋은 레슨: Suffix Array와 LCP, Suffix Automaton, Lyndon Factorization
- 다음에 볼 레슨: runs/periodicity, generalized suffix tree, suffix tree 기반 LCP 응용

## 1. 문제 신호

| 문제 표현 | Suffix Tree 관점 |
| --- | --- |
| substring의 모든 등장 위치를 찾아야 한다 | 해당 pattern 경로 아래 leaf들 |
| 여러 문자열의 longest common substring | generalized suffix tree |
| 반복 substring의 구조를 직접 봐야 한다 | internal node의 string depth |
| suffix 간 LCP 관계를 tree ancestor로 다룬다 | path depth와 LCA |
| 온라인으로 문자열을 붙이며 suffix 구조를 유지한다 | Ukkonen |

Suffix Tree는 매우 강하지만, 대회에서는 구현 비용이 큽니다. 대부분의 substring counting은 Suffix Array나 Suffix Automaton이 더 짧습니다. Tree가 필요한지는 "substring 집합"뿐 아니라 "경로와 subtree를 직접 질의하는가"로 판단합니다.

## 2. 압축 간선

Suffix trie에서는 한 간선이 글자 하나를 나타냅니다. Suffix Tree에서는 같은 방향으로만 이어지는 chain을 한 간선으로 압축합니다.

```text
edge label = s[l..r)
node stores outgoing edges by first character
```

따라서 간선을 복사해서 문자열로 저장하지 않고, 원문 index 구간만 저장합니다. 이 방식은 memory와 substring 비교 모두에서 중요합니다.

## 3. Sentinel이 먼저 필요한 이유

Suffix Tree 구현에서는 문자열 끝에 입력 alphabet에 없는 sentinel을 붙이는 것이 사실상 전제입니다. 예를 들어 `abab`만 넣으면 suffix `ab`가 suffix `abab`의 prefix라서 별도 leaf로 명시되지 않고 implicit 상태로 남을 수 있습니다.

```text
suffixes of abab:
abab
bab
ab
b
```

여기에 `$`를 붙이면 모든 suffix가 서로 prefix 관계로 끝나지 않습니다.

```text
suffixes of abab$:
abab$
bab$
ab$
b$
$
```

그래서 `ab$`, `b$`, `$`가 각각 명시 leaf로 드러납니다. pattern occurrence, suffix 시작 위치 복구, generalized suffix tree를 다룰 때는 이 leaf 명시성이 중요합니다.

여러 문자열을 합칠 때도 같은 sentinel을 재사용하면 안 됩니다. `A#B#`처럼 같은 끝 문자를 쓰면 서로 다른 문자열의 suffix가 잘못 이어질 수 있으므로 `A#B$C%`처럼 문자열마다 고유 sentinel을 둡니다.

## 4. Ukkonen의 상태

Ukkonen 알고리즘은 현재까지 만든 implicit suffix tree 위에서 active point를 유지합니다.

| 상태 | 의미 |
| --- | --- |
| `activeNode` | 현재 탐색이 시작되는 노드 |
| `activeEdge` | active edge의 첫 글자 위치 |
| `activeLength` | active edge 위에서 내려간 길이 |
| `suffixLink` | 다음 suffix로 건너뛸 internal node 링크 |
| `remaining` | 이번 phase에서 아직 추가해야 하는 suffix 수 |

아래 구현은 같은 아이디어를 `state(node, positionOnEdge)` 형태로 둔 버전입니다. 간선 label은 원문 구간으로 저장합니다.

작은 문자열에서 active point와 split이 어떻게 움직이는지는 [abab$ phase trace](suffix-tree-phase-trace.md)에서 먼저 확인할 수 있습니다. 코드를 읽기 전에 phase trace를 보면 `go`, `split`, `getLink`, `extend`가 왜 서로 맞물리는지 훨씬 덜 추상적으로 보입니다.

## 5. 구현 골격

```cpp compile-check
#include <map>
#include <string>
#include <vector>
using namespace std;

struct SuffixTree {
    struct Node {
        int l = 0;
        int r = 0;
        int parent = -1;
        int link = -1;
        map<char, int> next;

        Node() = default;
        Node(int left, int right, int parentNode)
            : l(left), r(right), parent(parentNode), link(-1) {}

        int length() const {
            return r - l;
        }

        int& child(char c) {
            if (!next.count(c)) {
                next[c] = -1;
            }
            return next[c];
        }
    };

    struct State {
        int v = 0;
        int pos = 0;
        State() = default;
        State(int node, int position) : v(node), pos(position) {}
    };

    string s;
    vector<Node> tree;
    State active;

    explicit SuffixTree(string text) : s(std::move(text)) {
        tree.reserve(2 * s.size() + 2);
        tree.push_back(Node(0, 0, -1));
        active = State(0, 0);
        for (int i = 0; i < (int)s.size(); ++i) {
            extend(i);
        }
    }

    State go(State state, int l, int r) {
        while (l < r) {
            if (state.pos == tree[state.v].length()) {
                state = State(tree[state.v].child(s[l]), 0);
                if (state.v == -1) {
                    return state;
                }
            } else {
                char edgeChar = s[tree[state.v].l + state.pos];
                if (edgeChar != s[l]) {
                    return State(-1, -1);
                }
                int edgeLeft = tree[state.v].length() - state.pos;
                if (r - l < edgeLeft) {
                    return State(state.v, state.pos + r - l);
                }
                l += edgeLeft;
                state.pos = tree[state.v].length();
            }
        }
        return state;
    }

    int split(State state) {
        if (state.pos == tree[state.v].length()) {
            return state.v;
        }
        if (state.pos == 0) {
            return tree[state.v].parent;
        }

        Node old = tree[state.v];
        int id = (int)tree.size();
        tree.push_back(Node(old.l, old.l + state.pos, old.parent));
        tree[old.parent].child(s[old.l]) = id;
        tree[id].child(s[old.l + state.pos]) = state.v;
        tree[state.v].parent = id;
        tree[state.v].l += state.pos;
        return id;
    }

    int getLink(int v) {
        if (tree[v].link != -1) {
            return tree[v].link;
        }
        if (tree[v].parent == -1) {
            return 0;
        }
        int parentLink = getLink(tree[v].parent);
        int skipRootCharacter = tree[v].parent == 0 ? 1 : 0;
        return tree[v].link = split(go(State(parentLink, tree[parentLink].length()),
                                      tree[v].l + skipRootCharacter, tree[v].r));
    }

    void extend(int position) {
        while (true) {
            State nextState = go(active, position, position + 1);
            if (nextState.v != -1) {
                active = nextState;
                return;
            }

            int middle = split(active);
            int leaf = (int)tree.size();
            tree.push_back(Node(position, (int)s.size(), middle));
            tree[middle].child(s[position]) = leaf;

            active.v = getLink(middle);
            active.pos = tree[active.v].length();
            if (middle == 0) {
                break;
            }
        }
    }
};
```

실전 구현에서는 생성자에 들어가기 전에 문자열 끝에 sentinel을 붙여 둡니다. Sentinel이 없으면 마지막 suffix들이 implicit 상태로 남을 수 있고, leaf 기반 질의가 한 칸씩 비게 됩니다.

## 6. Suffix Array와 비교

| 구조 | 강점 | 약점 |
| --- | --- | --- |
| Suffix Array | 구현이 상대적으로 짧고 정렬 기반 | subtree 탐색은 별도 RMQ/범위 관리 필요 |
| Suffix Automaton | substring 개수와 occurrence DP가 짧음 | suffix 위치 tree를 직접 보기는 어려움 |
| Suffix Tree | pattern subtree, generalized tree, path 질의가 직접적 | 구현 난도와 디버깅 비용이 큼 |

문제에서 "모든 suffix를 사전순으로 정렬"하면 suffix array를 먼저 생각하고, "substring 상태 수"가 나오면 suffix automaton을 먼저 생각합니다. Suffix Tree는 path와 subtree가 모두 필요한 경우에 꺼냅니다.

## 7. Generalized Suffix Tree

여러 문자열을 하나의 suffix tree에 넣을 때는 각 문자열마다 서로 다른 sentinel을 붙입니다.

```text
A + # + B + $ + C + %
```

Internal node의 subtree leaf가 어떤 문자열들에서 왔는지 bitmask로 모으면 longest common substring이나 k개 문자열 공통 substring을 처리할 수 있습니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| Ukkonen build with map | `O(N log alphabet)` |
| Ukkonen build with fixed array/hash | 평균 또는 상수 alphabet에서 `O(N)` |
| pattern 탐색 | `O(|pattern| log alphabet)` |
| subtree leaf 순회 | 출력 크기에 비례 |

## 9. 자주 하는 실수

1. Sentinel을 붙이지 않아 leaf가 명시적으로 끝나지 않는다.
2. 간선 구간을 inclusive/exclusive로 섞어 off-by-one을 만든다.
3. split 후 parent와 child map을 한쪽만 갱신한다.
4. root에서 suffix link를 따라갈 때 첫 글자 skip 규칙을 빠뜨린다.
5. 여러 문자열 sentinel을 같은 문자로 둔다.

## 10. 문제를 볼 때 체크할 조건

- suffix tree가 꼭 필요한가, suffix array나 suffix automaton으로 충분한가?
- alphabet 크기가 작아 fixed array를 쓸 수 있는가?
- leaf마다 suffix 시작 위치를 복구해야 하는가?
- 여러 문자열을 합칠 때 sentinel 충돌이 없는가?
- path depth와 edge length를 분리해서 계산하고 있는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: suffix tree construction `/practice/...` 문제 필요 | 압축 간선과 sentinel 이해 | suffix tree |
| 표준 | TODO: pattern occurrence subtree `/practice/...` 문제 필요 | pattern 경로 아래 leaf 수 세기 | subtree leaves |
| 응용 | TODO: generalized suffix tree LCS `/practice/...` 문제 필요 | 여러 문자열 공통 substring | unique sentinel |
| 함정 | TODO: repeated string implicit tree `/practice/...` 문제 필요 | sentinel 없는 경우 비교 | implicit suffix tree |
