# BST 계열: AVL, Splay, Treap

BST는 Binary Search Tree, 즉 이진 탐색 트리입니다. 각 노드는 왼쪽 subtree에 더 작은 key를, 오른쪽 subtree에 더 큰 key를 둡니다.

```text
left subtree의 모든 key < root key < right subtree의 모든 key
```

이 조건 덕분에 탐색, 삽입, 삭제를 트리 높이에 비례해서 처리할 수 있습니다. 문제는 트리 높이입니다. 균형이 잘 잡히면 `O(log n)`이지만, 한쪽으로 기울면 `O(n)`이 됩니다.

```text
균형 잡힌 BST:       기울어진 BST:

      4                 1
    /   \                \
   2     6                2
  / \   / \                \
 1   3 5   7                3
                              \
                               4
```

AVL Tree, Splay Tree, Treap은 모두 이 문제를 해결하려는 BST 계열 자료구조입니다. 방식은 다르지만 목표는 같습니다.

```text
정렬된 key 집합을 유지하면서 삽입, 삭제, 탐색을 빠르게 한다.
```

## 1. BST 기본 연산

BST 탐색은 현재 노드와 key를 비교하면서 왼쪽 또는 오른쪽으로 내려갑니다.

```cpp
struct Node {
    int key;
    Node* left;
    Node* right;

    Node(int key) : key(key), left(nullptr), right(nullptr) {}
};

bool contains(Node* root, int key) {
    while (root) {
        if (root->key == key) return true;
        if (key < root->key) {
            root = root->left;
        } else {
            root = root->right;
        }
    }
    return false;
}
```

삽입도 같은 비교를 반복하다가 null 자리에 새 노드를 붙입니다.

```cpp
Node* insert(Node* root, int key) {
    if (!root) return new Node(key);

    if (key < root->key) {
        root->left = insert(root->left, key);
    } else if (key > root->key) {
        root->right = insert(root->right, key);
    }
    return root;
}
```

위 코드는 중복 key를 무시합니다. 중복을 허용하려면 `count`를 두거나 `(value, id)`를 key로 사용합니다.

## 2. Inorder 순회

BST를 inorder로 순회하면 key가 오름차순으로 나옵니다.

```cpp
void inorder(Node* root, vector<int>& result) {
    if (!root) return;
    inorder(root->left, result);
    result.push_back(root->key);
    inorder(root->right, result);
}
```

이 성질 때문에 BST는 정렬 집합처럼 쓸 수 있습니다.

```text
작은 값부터 출력
x보다 작은 원소 개수
k번째로 작은 원소
lower_bound / upper_bound
```

단순 BST는 이론적으로 좋지만, 입력 순서가 나쁘면 쉽게 한쪽으로 기울어집니다. 그래서 실전 자료구조는 균형을 잡는 규칙을 추가합니다.

## 3. 회전

균형 BST의 기본 도구는 회전입니다. 회전은 BST 순서를 깨지 않고 부모와 자식 관계를 바꾸는 연산입니다.

오른쪽 회전은 왼쪽 자식을 위로 올립니다.

```text
      y              x
     / \            / \
    x   C   ->     A   y
   / \                / \
  A   B              B   C
```

```cpp
Node* rotateRight(Node* y) {
    Node* x = y->left;
    Node* b = x->right;

    x->right = y;
    y->left = b;

    return x;
}
```

왼쪽 회전은 오른쪽 자식을 위로 올립니다.

```cpp
Node* rotateLeft(Node* x) {
    Node* y = x->right;
    Node* b = y->left;

    y->left = x;
    x->right = b;

    return y;
}
```

`A < x < B < y < C` 순서는 회전 전후에 유지됩니다. 그래서 회전은 BST 조건을 보존합니다.

실제 AVL이나 Treap에서는 회전 후 `height`, `size`, `sum` 같은 보조 정보를 다시 계산해야 합니다.

## 4. 균형이 필요한 이유

정렬된 순서로 `1, 2, 3, 4, 5`를 단순 BST에 넣으면 트리가 한 줄이 됩니다.

```text
1
 \
  2
   \
    3
     \
      4
       \
        5
```

이 상태에서 `contains(5)`는 5개 노드를 모두 봐야 합니다. `n`개가 이런 식이면 탐색, 삽입, 삭제가 `O(n)`입니다.

균형 BST는 높이를 `O(log n)` 근처로 유지하려고 합니다. 방식에 따라 보장과 구현 난이도가 다릅니다.

| 구조 | 균형 유지 방식 | 시간 보장 |
| --- | --- | --- |
| AVL Tree | subtree 높이 차이를 1 이하로 유지 | 최악 `O(log n)` |
| Splay Tree | 접근한 노드를 root로 끌어올림 | amortized `O(log n)` |
| Treap | random priority로 트리 모양을 랜덤화 | 기대 `O(log n)` |

## 5. AVL Tree

AVL Tree는 각 노드에서 왼쪽 subtree와 오른쪽 subtree의 높이 차이가 1 이하가 되도록 유지하는 BST입니다.

```text
balance = height(left) - height(right)
허용 범위: -1, 0, 1
```

삽입이나 삭제 후 어떤 노드의 balance가 `2` 또는 `-2`가 되면 회전으로 고칩니다.

```cpp
struct AvlNode {
    int key;
    int height;
    AvlNode* left;
    AvlNode* right;

    AvlNode(int key) : key(key), height(1), left(nullptr), right(nullptr) {}
};

int height(AvlNode* node) {
    return node ? node->height : 0;
}

void pull(AvlNode* node) {
    if (!node) return;
    node->height = 1 + max(height(node->left), height(node->right));
}

int balance(AvlNode* node) {
    return height(node->left) - height(node->right);
}
```

AVL은 높이를 엄격하게 관리하므로 탐색이 빠르고 안정적입니다. 대신 삽입/삭제 구현이 다소 길고, 회전 경우를 정확히 나누어야 합니다.

## 6. AVL 회전 경우

AVL에서 균형이 깨지는 대표 경우는 네 가지입니다.

| 경우 | 모양 | 처리 |
| --- | --- | --- |
| LL | 왼쪽의 왼쪽이 무거움 | 오른쪽 회전 |
| RR | 오른쪽의 오른쪽이 무거움 | 왼쪽 회전 |
| LR | 왼쪽의 오른쪽이 무거움 | 왼쪽 자식 왼쪽 회전 후 오른쪽 회전 |
| RL | 오른쪽의 왼쪽이 무거움 | 오른쪽 자식 오른쪽 회전 후 왼쪽 회전 |

아래는 삽입 후 균형을 맞추는 함수 형태입니다.

```cpp
AvlNode* rotateRight(AvlNode* y) {
    AvlNode* x = y->left;
    AvlNode* b = x->right;

    x->right = y;
    y->left = b;

    pull(y);
    pull(x);
    return x;
}

AvlNode* rotateLeft(AvlNode* x) {
    AvlNode* y = x->right;
    AvlNode* b = y->left;

    y->left = x;
    x->right = b;

    pull(x);
    pull(y);
    return y;
}

AvlNode* rebalance(AvlNode* node) {
    pull(node);

    if (balance(node) > 1) {
        if (balance(node->left) < 0) {
            node->left = rotateLeft(node->left);
        }
        return rotateRight(node);
    }

    if (balance(node) < -1) {
        if (balance(node->right) > 0) {
            node->right = rotateRight(node->right);
        }
        return rotateLeft(node);
    }

    return node;
}
```

AVL은 "최악의 경우에도 높이를 강하게 보장하고 싶다"는 목적에 잘 맞습니다. 직접 구현 문제에서는 실수가 많아, 구현량을 감당할 수 있을 때 선택합니다.

## 7. Splay Tree

Splay Tree는 어떤 노드를 접근할 때마다 그 노드를 root로 끌어올리는 BST입니다. 이 끌어올리는 연산을 splay라고 합니다.

Splay Tree는 노드마다 height나 priority를 저장하지 않습니다. 대신 자주 접근한 노드가 root 근처에 오도록 트리를 계속 재구성합니다.

```text
최근에 접근한 key가 다시 접근될 가능성이 높다.
구간을 split/merge해야 한다.
amortized 보장이면 충분하다.
```

이런 상황에서 Splay Tree가 유용합니다. 각 연산의 최악 시간은 길 수 있지만, 연산 전체를 평균적으로 보면 amortized `O(log n)`입니다.

## 8. Splay 회전 패턴

Splay는 노드 `x`를 root로 올릴 때 부모 `p`, 조부모 `g`의 위치에 따라 회전합니다.

| 패턴 | 조건 | 처리 |
| --- | --- | --- |
| Zig | `x`의 부모가 root | 한 번 회전 |
| Zig-zig | `x`와 `p`가 같은 방향 자식 | `g` 회전 후 `p` 회전 |
| Zig-zag | `x`와 `p`가 반대 방향 자식 | `p` 회전 후 `g` 회전 |

예를 들어 `x`가 왼쪽-왼쪽으로 내려간 경우는 zig-zig입니다.

```text
      g              p              x
     /              / \              \
    p      ->      x   g      ->      p
   /                                      \
  x                                        g
```

Splay Tree는 구현에서 parent pointer를 쓰는 경우가 많습니다.

```cpp
struct SplayNode {
    int key;
    SplayNode* left;
    SplayNode* right;
    SplayNode* parent;

    SplayNode(int key)
        : key(key), left(nullptr), right(nullptr), parent(nullptr) {}
};
```

회전할 때 child와 parent pointer를 모두 정확히 갱신해야 합니다. 그래서 구현 난이도는 Treap보다 높은 편입니다.

## 9. Splay의 특징

Splay Tree는 접근한 노드가 root가 됩니다.

```text
find(x) 후 x가 root
insert(x) 후 x가 root
split할 때 기준 노드를 root로 올린 뒤 왼쪽/오른쪽을 자름
```

이 성질 때문에 동적 sequence, link-cut tree 같은 고급 자료구조의 기반으로 쓰입니다.

장점은 보조 정보가 적고 split/join에 강하다는 점입니다. 단점은 구현이 섬세하고, 한 연산의 최악 시간이 `O(n)`까지 갈 수 있다는 점입니다. 그래도 전체 연산열에 대해서는 amortized `O(log n)`이 보장됩니다.

## 10. Treap

Treap은 Tree와 Heap을 합친 randomized BST입니다. 각 노드는 `key`와 `priority`를 가집니다.

| 값 | 의미 |
| --- | --- |
| `key` | BST 순서를 정하는 값 |
| `priority` | heap 순서를 정하는 무작위 우선순위 |

Treap은 두 조건을 동시에 만족합니다.

```text
1. key 기준으로는 BST다.
2. priority 기준으로는 heap이다.
```

`priority`를 무작위로 뽑으면 root와 subtree 모양이 입력 순서에 덜 휘둘립니다. 그래서 삽입, 삭제, 탐색, 순위 질의가 모두 기대 `O(log n)`에 동작합니다.

Treap의 장점은 `split`과 `merge`가 자연스럽다는 것입니다. 이 때문에 단순 ordered set뿐 아니라 구간을 자르고 붙이는 Implicit Treap으로도 확장하기 좋습니다.

## 11. Treap 노드와 size

순위 질의와 k번째 원소를 처리하려면 각 subtree 크기를 저장합니다.

```cpp
struct Node {
    int key;
    unsigned priority;
    int size;
    Node* left;
    Node* right;

    Node(int key, unsigned priority)
        : key(key), priority(priority), size(1), left(nullptr), right(nullptr) {}
};

int getSize(Node* node) {
    return node ? node->size : 0;
}

void pull(Node* node) {
    if (!node) return;
    node->size = 1 + getSize(node->left) + getSize(node->right);
}
```

자식을 바꾼 뒤에는 항상 `pull(node)`로 `size`를 다시 계산합니다. AVL의 height 갱신과 같은 습관입니다.

## 12. Treap merge

`merge(a, b)`는 두 Treap을 하나로 합칩니다. 단, `a`의 모든 key가 `b`의 모든 key보다 작아야 합니다.

```cpp
Node* merge(Node* a, Node* b) {
    if (!a) return b;
    if (!b) return a;

    if (a->priority > b->priority) {
        a->right = merge(a->right, b);
        pull(a);
        return a;
    } else {
        b->left = merge(a, b->left);
        pull(b);
        return b;
    }
}
```

BST 조건은 `a < b` 전제 때문에 유지됩니다. Heap 조건은 priority가 높은 쪽을 root로 고르기 때문에 유지됩니다.

## 13. Treap split

`split(root, key, a, b)`는 하나의 Treap을 두 개로 나눕니다.

```text
a: key보다 작은 원소들
b: key 이상인 원소들
```

```cpp
void split(Node* root, int key, Node*& a, Node*& b) {
    if (!root) {
        a = nullptr;
        b = nullptr;
        return;
    }

    if (root->key < key) {
        split(root->right, key, root->right, b);
        a = root;
        pull(a);
    } else {
        split(root->left, key, a, root->left);
        b = root;
        pull(b);
    }
}
```

`root->key < key`이면 root와 왼쪽 subtree는 전부 `a` 쪽에 남을 수 있습니다. 오른쪽 subtree에는 작은 값과 큰 값이 섞여 있을 수 있으므로 오른쪽만 다시 나눕니다.

## 14. Treap 삽입과 삭제

삽입은 split 후 가운데에 새 노드를 끼우고 다시 merge합니다.

```cpp
Node* insert(Node* root, Node* node) {
    Node* left = nullptr;
    Node* right = nullptr;
    split(root, node->key, left, right);
    return merge(merge(left, node), right);
}
```

중복을 허용하지 않는 set이라면 먼저 `contains(key)`를 확인합니다.

삭제는 찾은 노드를 제거하고, 그 노드의 왼쪽 subtree와 오른쪽 subtree를 merge합니다.

```cpp
Node* erase(Node* root, int key) {
    if (!root) return nullptr;

    if (root->key == key) {
        Node* next = merge(root->left, root->right);
        delete root;
        return next;
    }

    if (key < root->key) {
        root->left = erase(root->left, key);
    } else {
        root->right = erase(root->right, key);
    }

    pull(root);
    return root;
}
```

왼쪽 subtree의 모든 key는 삭제된 key보다 작고, 오른쪽 subtree의 모든 key는 더 큽니다. 그래서 `merge(left, right)`의 전제가 맞습니다.

## 15. 순위와 k번째 원소

`orderOfKey(x)`는 `x`보다 작은 원소 개수를 반환합니다.

```cpp
int orderOfKey(Node* root, int key) {
    if (!root) return 0;

    if (key <= root->key) {
        return orderOfKey(root->left, key);
    }
    return getSize(root->left) + 1 + orderOfKey(root->right, key);
}
```

`kth(k)`는 0-indexed로 k번째 작은 원소를 반환합니다.

```cpp
int kth(Node* root, int k) {
    int leftSize = getSize(root->left);

    if (k < leftSize) {
        return kth(root->left, k);
    }
    if (k == leftSize) {
        return root->key;
    }
    return kth(root->right, k - leftSize - 1);
}
```

둘 다 subtree 크기만 보고 한쪽으로 내려가므로 기대 `O(log n)`입니다.

## 16. Treap 전체 구현

아래 구현은 중복 key를 허용하지 않는 ordered set Treap입니다.

```cpp
#include <random>
#include <stdexcept>
using namespace std;

struct Treap {
    struct Node {
        int key;
        unsigned priority;
        int size;
        Node* left;
        Node* right;

        Node(int key, unsigned priority)
            : key(key), priority(priority), size(1), left(nullptr), right(nullptr) {}
    };

    Node* root = nullptr;
    mt19937 rng{random_device{}()};

    Treap() = default;
    Treap(const Treap&) = delete;
    Treap& operator=(const Treap&) = delete;

    ~Treap() {
        clear(root);
    }

    void clear(Node* node) {
        if (!node) return;
        clear(node->left);
        clear(node->right);
        delete node;
    }

    int getSize(Node* node) const {
        return node ? node->size : 0;
    }

    void pull(Node* node) {
        if (!node) return;
        node->size = 1 + getSize(node->left) + getSize(node->right);
    }

    Node* merge(Node* a, Node* b) {
        if (!a) return b;
        if (!b) return a;

        if (a->priority > b->priority) {
            a->right = merge(a->right, b);
            pull(a);
            return a;
        } else {
            b->left = merge(a, b->left);
            pull(b);
            return b;
        }
    }

    void split(Node* node, int key, Node*& a, Node*& b) {
        if (!node) {
            a = nullptr;
            b = nullptr;
            return;
        }

        if (node->key < key) {
            split(node->right, key, node->right, b);
            a = node;
            pull(a);
        } else {
            split(node->left, key, a, node->left);
            b = node;
            pull(b);
        }
    }

    bool contains(int key) const {
        Node* node = root;
        while (node) {
            if (node->key == key) return true;
            if (key < node->key) node = node->left;
            else node = node->right;
        }
        return false;
    }

    void insert(int key) {
        if (contains(key)) return;

        Node* left = nullptr;
        Node* right = nullptr;
        split(root, key, left, right);

        Node* node = new Node(key, rng());
        root = merge(merge(left, node), right);
    }

    Node* erase(Node* node, int key) {
        if (!node) return nullptr;

        if (node->key == key) {
            Node* next = merge(node->left, node->right);
            delete node;
            return next;
        }

        if (key < node->key) {
            node->left = erase(node->left, key);
        } else {
            node->right = erase(node->right, key);
        }
        pull(node);
        return node;
    }

    void erase(int key) {
        root = erase(root, key);
    }

    int orderOfKey(Node* node, int key) const {
        if (!node) return 0;

        if (key <= node->key) {
            return orderOfKey(node->left, key);
        }
        return getSize(node->left) + 1 + orderOfKey(node->right, key);
    }

    int orderOfKey(int key) const {
        return orderOfKey(root, key);
    }

    int kth(Node* node, int k) const {
        int leftSize = getSize(node->left);

        if (k < leftSize) {
            return kth(node->left, k);
        }
        if (k == leftSize) {
            return node->key;
        }
        return kth(node->right, k - leftSize - 1);
    }

    int kth(int k) const {
        if (k < 0 || k >= getSize(root)) {
            throw out_of_range("Treap kth index is out of range");
        }
        return kth(root, k);
    }

    int size() const {
        return getSize(root);
    }
};
```

`orderOfKey(10)`은 10보다 작은 값의 개수이고, `kth(0)`은 가장 작은 값입니다.

## 17. Implicit Treap

Treap은 key를 직접 저장하지 않고, 현재 위치를 key처럼 쓸 수도 있습니다. 이것을 Implicit Treap이라고 부릅니다.

배열을 Treap으로 저장하고 subtree size로 위치를 계산하면 다음 작업을 기대 `O(log n)`에 처리할 수 있습니다.

```text
1. 구간 [l, r]을 잘라낸다.
2. 잘라낸 구간을 다른 위치에 붙인다.
3. 구간을 뒤집는다.
4. 구간 합, 최솟값 같은 값을 관리한다.
```

이때 `split(root, k)`는 앞에서 `k`개와 나머지로 나눕니다. key 값이 아니라 subtree size를 기준으로 내려간다는 점만 다르고, `merge`는 거의 같습니다.

문자열 편집, 배열 구간 이동, 동적 순열 문제에서 Implicit Treap이 자주 등장합니다.

## 18. 구조별 비교

| 구조 | 장점 | 약점 |
| --- | --- | --- |
| 단순 BST | 구현이 쉽고 개념이 단순함 | 입력 순서가 나쁘면 `O(n)` |
| AVL Tree | 높이를 강하게 보장해서 탐색이 안정적 | 삽입/삭제 회전 구현이 길다 |
| Splay Tree | 최근 접근 원소에 강하고 split/join에 좋음 | 구현이 섬세하고 amortized 보장 |
| Treap | 구현이 비교적 짧고 split/merge가 자연스러움 | random priority에 의존하는 기대 시간 |
| `std::set` | 표준 라이브러리라 안전함 | k번째/순위 질의가 기본 제공되지 않음 |

대부분의 실전 문제에서는 `std::set`이나 `std::map`을 먼저 고려합니다. 직접 BST 계열을 구현하는 이유는 보통 아래 중 하나입니다.

```text
k번째 원소나 순위 질의가 필요하다.
subtree에 sum/min/max 같은 정보를 붙여야 한다.
split/merge가 필요하다.
sequence를 동적으로 자르고 붙여야 한다.
```

이 경우에는 Treap이 구현량 대비 강력한 선택입니다. 높이 보장을 엄격히 원하면 AVL, 접근 locality나 고급 동적 트리 응용이 중요하면 Splay를 검토합니다.

## 19. 자주 나는 실수

- 단순 BST를 쓰면서 입력이 정렬될 수 있다는 점을 놓치면 `O(n)`으로 터집니다.
- 회전 후 `height`, `size`, `sum` 같은 보조 정보를 갱신하지 않으면 이후 질의가 틀어집니다.
- AVL의 LR/RL 케이스에서 회전 순서를 반대로 쓰면 균형이 복구되지 않습니다.
- Splay에서 parent pointer를 하나라도 잘못 연결하면 트리 구조가 깨집니다.
- Treap의 `merge(a, b)`는 `a`의 모든 key가 `b`보다 작다는 전제가 필요합니다.
- `kth(k)`의 k가 0-indexed인지 1-indexed인지 문제 전체에서 통일해야 합니다.
- 중복 key를 허용할지 먼저 정해야 합니다. Treap 예시 구현은 중복을 무시합니다.

## 20. 문제를 볼 때 체크할 조건

1. 단순 정렬 집합이면 `std::set`으로 충분한가?
2. 순위나 k번째 원소가 필요한가?
3. key 범위가 커서 Fenwick Tree나 Segment Tree 좌표 압축이 불편한가?
4. split/merge 또는 동적 sequence 조작이 필요한가?
5. 최악 시간 보장이 중요한가, 기대/상각 시간으로 충분한가?
6. 직접 구현할 만큼 자료구조가 문제의 핵심인가?

이 질문을 통과하면 BST 계열을 직접 구현할 이유가 생깁니다. 그중 대회 코드에서 가장 균형 잡힌 선택은 보통 Treap입니다.
