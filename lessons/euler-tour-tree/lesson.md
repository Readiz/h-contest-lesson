# Euler Tour Tree

Euler Tour Tree는 dynamic forest를 Euler tour sequence로 표현하고, balanced binary tree로 sequence를 split/merge해서 `link`, `cut`, connectivity query를 처리하는 자료구조입니다. Link-Cut Tree가 path 중심이라면 Euler Tour Tree는 tree 전체의 Euler sequence 중심입니다.

이 레슨은 Link-Cut Tree와 Dynamic Connectivity 이후에 보는 자료구조/그래프 심화입니다.

1. 각 tree를 Euler tour sequence 하나로 표현한다.
2. sequence node가 속한 balanced tree root가 connectivity component를 뜻한다.
3. edge 추가/삭제는 sequence split과 merge로 처리한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Euler tour, randomized treap, split/merge, dynamic forest
- 함께 보면 좋은 레슨: Link-Cut Tree, Dynamic Connectivity, Tree Advanced
- 다음에 볼 레슨: fully dynamic connectivity, dynamic MST, top tree

## 1. 문제 신호

| 문제 표현 | Euler Tour Tree 관점 |
| --- | --- |
| forest에서 edge link/cut이 온라인으로 들어온다 | dynamic forest |
| 두 정점이 같은 tree인지 묻는다 | treap root 비교 |
| subtree나 component aggregate가 필요하다 | Euler sequence aggregate |
| 일반 그래프가 아니라 forest이다 | ETT 단독 적용 가능 |
| 일반 그래프 connectivity | replacement edge 관리가 추가 필요 |

Euler Tour Tree 단독으로는 forest를 관리합니다. 일반 그래프의 fully dynamic connectivity는 spanning forest level과 replacement edge 탐색이 추가로 필요합니다.

## 2. Euler Tour 표현

무향 tree의 각 edge를 양방향 arc 두 개로 보고 Euler tour sequence를 만듭니다.

```text
u -> v arc
v -> u arc
vertex occurrence
```

sequence 전체가 하나의 connected component입니다. 어떤 정점 occurrence가 들어 있는 treap root를 비교하면 같은 tree인지 알 수 있습니다.

## 3. Treap Split/Merge

실전 구현은 treap, splay, rope 등으로 sequence를 표현할 수 있습니다. 핵심 연산은 아래와 같습니다.

| 연산 | 의미 |
| --- | --- |
| `split(root, k)` | 앞 `k`개와 나머지 sequence로 분리 |
| `merge(a, b)` | 두 sequence를 이어 붙임 |
| `index(node)` | node가 sequence에서 몇 번째인지 계산 |
| `root(node)` | node가 속한 treap root |

아래는 Euler Tour Tree에 필요한 implicit treap 골격입니다.

```cpp compile-check
#include <utility>
using namespace std;

struct ETTNode {
    int vertex = 0;
    unsigned priority = 0;
    int size = 1;
    ETTNode* left = nullptr;
    ETTNode* right = nullptr;
    ETTNode* parent = nullptr;
};

int nodeSize(ETTNode* node) {
    return node == nullptr ? 0 : node->size;
}

void attachLeft(ETTNode* root, ETTNode* child) {
    if (root != nullptr) {
        root->left = child;
    }
    if (child != nullptr) {
        child->parent = root;
    }
}

void attachRight(ETTNode* root, ETTNode* child) {
    if (root != nullptr) {
        root->right = child;
    }
    if (child != nullptr) {
        child->parent = root;
    }
}

void pull(ETTNode* node) {
    if (node != nullptr) {
        node->size = 1 + nodeSize(node->left) + nodeSize(node->right);
    }
}

ETTNode* mergeTreap(ETTNode* left, ETTNode* right) {
    if (left == nullptr) {
        if (right != nullptr) {
            right->parent = nullptr;
        }
        return right;
    }
    if (right == nullptr) {
        left->parent = nullptr;
        return left;
    }
    if (left->priority < right->priority) {
        ETTNode* merged = mergeTreap(left->right, right);
        attachRight(left, merged);
        left->parent = nullptr;
        pull(left);
        return left;
    }
    ETTNode* merged = mergeTreap(left, right->left);
    attachLeft(right, merged);
    right->parent = nullptr;
    pull(right);
    return right;
}

pair<ETTNode*, ETTNode*> splitTreap(ETTNode* root, int leftSize) {
    if (root == nullptr) {
        return {nullptr, nullptr};
    }
    root->parent = nullptr;
    if (nodeSize(root->left) >= leftSize) {
        auto parts = splitTreap(root->left, leftSize);
        attachLeft(root, parts.second);
        pull(root);
        if (parts.first != nullptr) {
            parts.first->parent = nullptr;
        }
        root->parent = nullptr;
        return {parts.first, root};
    }

    int used = nodeSize(root->left) + 1;
    auto parts = splitTreap(root->right, leftSize - used);
    attachRight(root, parts.first);
    pull(root);
    if (parts.second != nullptr) {
        parts.second->parent = nullptr;
    }
    root->parent = nullptr;
    return {root, parts.second};
}

ETTNode* treapRoot(ETTNode* node) {
    while (node != nullptr && node->parent != nullptr) {
        node = node->parent;
    }
    return node;
}
```

이 골격에 aggregate 값, lazy flag, vertex occurrence 관리가 붙으면 component sum 같은 질의도 처리할 수 있습니다.

## 4. `reroot` 관점

`link(u, v)`를 편하게 하려면 두 tree의 sequence를 각각 `u`, `v`가 앞에 오도록 회전합니다.

```text
reroot(u):
  sequence = A + occurrence(u) + B
  rotate to occurrence(u) + B + A
```

그 뒤 새 edge arc `(u, v)`, `(v, u)`를 사이에 끼우며 두 sequence를 merge합니다.

## 5. Sequence trace

아래 tree를 Euler Tour Tree sequence로 펼쳐 보겠습니다.

```text
1 -- 2 -- 3
```

무향 edge를 양방향 arc로 보면 한 가지 가능한 sequence는 아래와 같습니다.

```text
1, (1,2), 2, (2,3), 3, (3,2), 2, (2,1), 1
```

정점 occurrence가 여러 번 나오기 때문에, 구현에서는 정점별 대표 occurrence와 edge별 양방향 arc pointer를 따로 들고 있어야 합니다.

### 5.1 `link(3, 4)`

먼저 `3`이 sequence 앞에 오도록 기존 tree를 reroot합니다.

```text
3, (3,2), 2, (2,1), 1, (1,2), 2, (2,3), 3
```

정점 `4`의 singleton sequence는 단순히 아래와 같습니다.

```text
4
```

새 edge `3-4`를 추가하려면 arc `(3,4)`, `(4,3)`를 만들어 두 sequence 사이에 넣습니다.

```text
3, (3,2), 2, (2,1), 1, (1,2), 2, (2,3), 3,
(3,4), 4, (4,3)
```

실제 treap에서는 이 전체 문자열을 복사하지 않습니다. `split`과 `merge`로 root pointer 몇 개를 재조합할 뿐입니다. 그래도 논리적으로는 위 sequence 하나가 같은 component를 뜻합니다.

### 5.2 `cut(2, 3)`

다시 원래 tree `1-2-3`의 sequence를 보겠습니다.

```text
1, (1,2), 2, (2,3), 3, (3,2), 2, (2,1), 1
```

edge `2-3`을 지우려면 arc `(2,3)`와 `(3,2)`의 위치를 찾습니다.

```text
prefix = 1, (1,2), 2
middle = 3
suffix = 2, (2,1), 1
```

`middle`은 정점 `3`만 있는 component가 되고, `suffix + prefix`를 다시 붙이면 `1-2` component가 됩니다.

```text
component A: 3
component B: 2, (2,1), 1, 1, (1,2), 2
```

위 표기는 개념 trace라서 vertex occurrence가 연속으로 보일 수 있습니다. 실제 구현에서는 chosen occurrence와 arc 제거 위치를 기준으로 treap을 잘라, 각 component가 유효한 Euler tour cycle이 되도록 회전합니다. 중요한 점은 `cut`이 edge endpoint 값만으로는 부족하고, `(u,v)`, `(v,u)` arc node pointer가 있어야 정확한 두 split 지점을 잡을 수 있다는 것입니다.

## 6. `cut` 관점

edge `(u, v)`를 삭제하려면 Euler sequence 안의 arc `(u, v)`와 `(v, u)` 위치를 찾아 그 사이를 잘라 두 component sequence로 나눕니다.

```text
... (u,v) ... (v,u) ...
```

두 arc의 순서에 따라 split 구간이 달라집니다. 그래서 edge id로 양방향 arc node pointer를 모두 저장해 두는 것이 중요합니다.

## 7. Link-Cut Tree와 비교

| 구조 | 강점 |
| --- | --- |
| Link-Cut Tree | path query, represented tree root 변경 |
| Euler Tour Tree | component aggregate, connectivity, subtree-like aggregate |
| Rollback DSU | offline dynamic connectivity |

경로 max/min이 핵심이면 Link-Cut Tree가 자연스럽고, component 전체 합이나 dynamic forest connectivity가 핵심이면 Euler Tour Tree가 더 직접적입니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| connectivity check | `O(log N)` 또는 root pointer amortized |
| reroot | `O(log N)` |
| link | `O(log N)` |
| cut | `O(log N)` |
| component aggregate | `O(1)` after root access |

treap priority가 편향되면 성능이 무너질 수 있습니다. deterministic judge에서는 난수 seed와 priority 충돌 처리도 신경 씁니다.

## 9. 자주 하는 실수

1. 일반 그래프 connectivity를 ETT 하나만으로 처리하려고 한다.
2. edge의 양방향 arc pointer를 저장하지 않아 cut 위치를 못 찾는다.
3. reroot 후 parent pointer를 갱신하지 않아 root 비교가 틀린다.
4. vertex occurrence가 여러 개인데 대표 occurrence 관리를 잃는다.
5. treap split/merge에서 aggregate pull 순서를 빠뜨린다.

## 10. 문제를 볼 때 체크할 조건

- 유지되는 그래프가 항상 forest인가?
- edge 삭제가 온라인으로 들어오는가?
- connectivity만 필요한가, component aggregate도 필요한가?
- path aggregate가 핵심이라 Link-Cut Tree가 더 나은 문제는 아닌가?
- edge id로 arc node를 안정적으로 찾을 수 있는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: dynamic forest connectivity `/practice/...` 문제 필요 | root 비교로 연결성 확인 | Euler tour sequence |
| 표준 | TODO: online link cut `/practice/...` 문제 필요 | reroot, split, merge 구현 | implicit treap |
| 응용 | TODO: component sum `/practice/...` 문제 필요 | treap aggregate 유지 | component aggregate |
| 함정 | TODO: non-forest dynamic graph `/practice/...` 문제 필요 | ETT 단독 적용 한계 판정 | replacement edge |
