# Suffix Tree와 Ukkonen

Suffix Tree는 한 문자열의 모든 suffix를 압축 trie로 저장한 구조입니다. Suffix Array나 Suffix Automaton보다 구현 난도는 높지만, substring 위치, LCP, 반복 구간, 여러 문자열 공통 부분을 "간선 구간"으로 직접 다룰 수 있습니다.

## 문제 신호

| 문제 표현 | Suffix Tree 관점 |
| --- | --- |
| substring의 모든 등장 위치를 찾아야 한다 | 해당 pattern 경로 아래 leaf들 |
| 여러 문자열의 longest common substring | generalized suffix tree |
| 반복 substring의 구조를 직접 봐야 한다 | internal node의 string depth |
| suffix 간 LCP 관계를 tree ancestor로 다룬다 | path depth와 LCA |
| 온라인으로 문자열을 붙이며 suffix 구조를 유지한다 | Ukkonen |

Suffix Tree는 매우 강하지만, 대회에서는 구현 비용이 큽니다. 대부분의 substring counting은 Suffix Array나 Suffix Automaton이 더 짧습니다. Tree가 필요한지는 "substring 집합"뿐 아니라 "경로와 subtree를 직접 질의하는가"로 판단합니다.

## 압축 간선

Suffix trie에서는 한 간선이 글자 하나를 나타냅니다. Suffix Tree에서는 같은 방향으로만 이어지는 chain을 한 간선으로 압축합니다.

```text
edge label = s[l..r)
node stores outgoing edges by first character
```

따라서 간선을 복사해서 문자열로 저장하지 않고, 원문 index 구간만 저장합니다. 이 방식은 memory와 substring 비교 모두에서 중요합니다.

## Sentinel이 먼저 필요한 이유

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

## Ukkonen의 상태

Ukkonen 알고리즘은 현재까지 만든 implicit suffix tree 위에서 active point를 유지합니다.

| 상태 | 의미 |
| --- | --- |
| `activeNode` | 현재 탐색이 시작되는 노드 |
| `activeEdge` | active edge의 첫 글자 위치 |
| `activeLength` | active edge 위에서 내려간 길이 |
| `suffixLink` | 다음 suffix로 건너뛸 internal node 링크 |
| `remaining` | 이번 phase에서 아직 추가해야 하는 suffix 수 |

아래 구현은 같은 아이디어를 `state(node, positionOnEdge)` 형태로 둔 버전입니다. 간선 label은 원문 구간으로 저장합니다.

## abab$에서 상태 변화 따라가기

### 표기

아래 표에서는 active point를 `(node, edge, length)`로 적습니다.

| 표기 | 의미 |
| --- | --- |
| `root` | suffix tree root |
| `edge=a` | root 또는 현재 node에서 `a`로 시작하는 edge 위에 있음 |
| `length=2` | active edge를 2글자 내려간 위치 |
| Rule 3 | 다음 문자가 이미 있어서 이번 phase가 implicit하게 끝남 |

Sentinel `$`는 입력 alphabet에 없는 문자라고 가정합니다.

### Phase 0: `a`

처음에는 root에 아무 edge도 없습니다. 새 문자 `a`를 넣으면 suffix `a`를 나타내는 leaf를 만듭니다.

```text
root
└── a...
```

| 항목 | 값 |
| --- | --- |
| active point | `(root, -, 0)` |
| 처리 suffix | `a` |
| 동작 | root에 `a` edge leaf 생성 |
| phase 후 active | `(root, -, 0)` |

### Phase 1: `ab`

새 문자 `b`를 붙입니다. root에 `b` edge가 없으므로 suffix `b` leaf를 만듭니다.

```text
root
├── ab...
└── b...
```

| 항목 | 값 |
| --- | --- |
| active point | `(root, -, 0)` |
| 처리 suffix | `b` |
| 동작 | root에 `b` edge leaf 생성 |
| phase 후 active | `(root, -, 0)` |

### Phase 2: `aba`

새 문자 `a`를 붙입니다. root에는 이미 `a`로 시작하는 edge가 있고, 다음 문자가 일치합니다. 그래서 새 leaf를 만들지 않고 implicit tree 상태로 멈춥니다.

```text
root
├── aba...
└── ba...
```

| 항목 | 값 |
| --- | --- |
| active point | `(root, edge=a, length=0)` |
| 본 문자 | `a` |
| 동작 | 기존 `a` edge를 따라감, Rule 3 |
| phase 후 active | `(root, edge=a, length=1)` |

이 시점의 suffix `a`는 root의 `a...` edge 중간에서 끝납니다. sentinel이 없으면 이런 implicit suffix가 끝까지 남을 수 있습니다.

### Phase 3: `abab`

새 문자 `b`를 붙입니다. active edge `a...`에서 한 글자 내려간 위치 다음 문자가 `b`이고, 새 문자와 일치합니다. 다시 Rule 3으로 멈춥니다.

| 항목 | 값 |
| --- | --- |
| active point | `(root, edge=a, length=1)` |
| 본 문자 | `b` |
| 동작 | 기존 edge 위에서 `ab`까지 진행, Rule 3 |
| phase 후 active | `(root, edge=a, length=2)` |

아직 `ab`와 `b` suffix는 명시 leaf로 분리되지 않았습니다. 반복 문자열에서 Ukkonen이 빠른 이유가 여기에 있습니다. 매 suffix를 강제로 leaf로 만들지 않고, 이미 있는 경로와 맞으면 phase를 멈춥니다.

### Phase 4: `abab$`

Sentinel `$`를 붙이면 더 이상 기존 edge와 맞지 않으므로 밀린 implicit suffix들이 한꺼번에 명시됩니다.

먼저 active point는 root의 `a...` edge를 `ab`만큼 내려간 위치입니다. 다음 글자는 원래 `a`인데 새 문자는 `$`라서 mismatch입니다.

```text
root
└── ab
    ├── ab$
    └── $
```

| 처리 suffix | active 위치 | 동작 |
| --- | --- | --- |
| `ab$` | `a...` edge의 `ab` 뒤 | edge를 `ab`에서 split하고 `$` leaf 생성 |
| `b$` | suffix link/root 규칙으로 `b...` edge 위 | `b` 뒤에서 split하고 `$` leaf 생성 |
| `$` | root | root에 `$` leaf 생성 |

완성된 구조를 개념적으로 그리면 아래와 같습니다.

```text
root
├── ab
│   ├── ab$
│   └── $
├── b
│   ├── ab$
│   └── $
└── $
```

여기서 root 아래 `ab` node와 `b` node가 internal node입니다. 첫 split으로 생긴 internal node의 suffix link는 다음 suffix인 `b` node로 이어지고, 마지막에는 root로 돌아갑니다.

### 코드와 연결하기

위 trace를 구현 함수에 대응시키면 아래처럼 읽을 수 있습니다.

| trace 사건 | 코드에서 보는 함수 |
| --- | --- |
| 기존 edge를 따라가며 Rule 3으로 멈춤 | `go(active, position, position + 1)` 성공 |
| edge 중간 mismatch | `split(active)`로 internal node 생성 |
| 새 suffix leaf 생성 | `tree.push_back(Node(position, s.size(), middle))` |
| 다음 suffix 처리 위치로 이동 | `active.v = getLink(middle)` |
| root에서 첫 글자 skip | `skipRootCharacter` 처리 |

디버깅할 때는 phase마다 active point와 생성된 internal node의 edge label을 출력하는 것이 좋습니다. `abab$`, `banana$`, `aaaa$`에서 split과 suffix link를 추적한 뒤, 작은 무작위 문자열의 모든 suffix·substring을 직접 비교합니다. 큰 입력의 시간·메모리는 별도로 측정합니다.

## 구현

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

        int oldLeft = tree[state.v].l;
        int oldParent = tree[state.v].parent;
        int id = (int)tree.size();
        tree.push_back(Node(oldLeft, oldLeft + state.pos, oldParent));
        tree[oldParent].child(s[oldLeft]) = id;
        tree[id].child(s[oldLeft + state.pos]) = state.v;
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

위 코드는 최종 문자열을 한 번에 받아 leaf 끝을 `s.size()`로 고정합니다. 생성 후 문자열을 append하는 API가 아닙니다. 실전 구현에서는 생성자에 들어가기 전에 문자열 끝에 sentinel을 붙여 둡니다. Sentinel이 없으면 마지막 suffix들이 implicit 상태로 남을 수 있고, leaf 기반 질의가 한 칸씩 비게 됩니다.

## Suffix Array와 비교

| 구조 | 강점 | 약점 |
| --- | --- | --- |
| Suffix Array | 구현이 상대적으로 짧고 정렬 기반 | subtree 탐색은 별도 RMQ/범위 관리 필요 |
| Suffix Automaton | substring 개수와 occurrence DP가 짧음 | suffix 위치 tree를 직접 보기는 어려움 |
| Suffix Tree | pattern subtree, generalized tree, path 질의가 직접적 | 구현 난도와 디버깅 비용이 큼 |

문제에서 "모든 suffix를 사전순으로 정렬"하면 suffix array를 먼저 생각하고, "substring 상태 수"가 나오면 suffix automaton을 먼저 생각합니다. Suffix Tree는 path와 subtree가 모두 필요한 경우에 꺼냅니다.

## Generalized Suffix Tree

여러 문자열을 하나의 suffix tree에 넣을 때는 각 문자열마다 서로 다른 sentinel을 붙입니다.

```text
A + # + B + $ + C + %
```

Internal node의 subtree leaf가 어떤 문자열들에서 왔는지 bitmask로 모으면 longest common substring이나 k개 문자열 공통 substring을 처리할 수 있습니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| Ukkonen build with map | `O(N log alphabet)` |
| Ukkonen build with fixed array/hash | 평균 또는 상수 alphabet에서 `O(N)` |
| pattern 탐색 | `O(|pattern| log alphabet)` |
| subtree leaf 순회 | 출력 크기에 비례 |
