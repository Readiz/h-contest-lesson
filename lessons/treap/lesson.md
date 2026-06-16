# Treap

Treap은 **Binary Search Tree**와 **Heap**을 합친 자료구조입니다. 이름도 Tree + Heap에서 왔습니다.

각 노드는 두 값을 가집니다.

| 값 | 의미 |
| --- | --- |
| `key` | 이진 탐색 트리 순서를 정하는 값 |
| `priority` | 트리의 균형을 무작위로 잡기 위한 우선순위 |

Treap은 항상 두 조건을 만족합니다.

```text
1. key 기준으로는 이진 탐색 트리다.
   left subtree의 key < root key < right subtree의 key

2. priority 기준으로는 heap이다.
   root priority가 자식 priority보다 높다.
```

`priority`를 무작위로 뽑으면 트리 모양이 입력 순서에 덜 휘둘립니다. 그래서 삽입, 삭제, 탐색, 순위 질의가 모두 **기대 `O(log n)`**에 동작합니다.

## 1. 왜 Treap을 쓰는가

정렬된 집합에서 다음 작업을 빠르게 하고 싶다고 합시다.

```text
1. x를 넣는다.
2. x를 지운다.
3. x가 있는지 찾는다.
4. x보다 작은 원소 개수를 구한다.
5. k번째로 작은 원소를 구한다.
```

`std::set`은 삽입, 삭제, 탐색은 `O(log n)`에 해 주지만, k번째 원소나 순위 질의는 기본으로 제공하지 않습니다. Segment Tree나 Fenwick Tree로도 순위 질의를 만들 수 있지만, 값의 범위가 크면 좌표 압축이 필요하고 동적으로 새 값이 들어올 때 불편합니다.

Treap은 직접 만든 균형 BST처럼 쓸 수 있어서, 노드에 `size`, `sum`, `min` 같은 정보를 붙여 확장하기 좋습니다.

## 2. 핵심 아이디어

BST 조건만 있으면 정렬 순서가 유지됩니다. 하지만 값이 이미 정렬된 순서로 들어오면 일반 BST는 한쪽으로 길게 늘어져 `O(n)`이 됩니다.

Treap은 각 key에 random priority를 붙입니다.

```text
key 순서:       1   2   3   4   5
priority 예시: 17  90  31  44  12
```

priority가 가장 높은 key가 root가 되고, 왼쪽에는 더 작은 key, 오른쪽에는 더 큰 key가 들어갑니다. 각 subtree에서도 같은 규칙을 반복합니다. priority가 무작위라면 root가 매번 어느 정도 랜덤하게 정해지므로, 트리 높이가 기대 `O(log n)`이 됩니다.

## 3. 노드에 size 저장하기

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

자식을 바꾼 뒤에는 항상 `pull(node)`로 `size`를 다시 계산합니다. Segment Tree에서 부모 값을 다시 계산하는 것과 같은 습관입니다.

## 4. merge

`merge(a, b)`는 두 Treap을 하나로 합칩니다. 단, `a`의 모든 key가 `b`의 모든 key보다 작아야 합니다.

root는 priority가 더 높은 쪽이 됩니다.

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

BST 조건은 `a`의 모든 key가 `b`보다 작다는 전제 때문에 유지됩니다. Heap 조건은 priority가 높은 쪽을 root로 고르기 때문에 유지됩니다.

## 5. split

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

`root->key < key`이면 root와 왼쪽 subtree는 전부 `a` 쪽에 남을 수 있습니다. 다만 오른쪽 subtree에는 작은 값과 큰 값이 섞여 있을 수 있으므로 오른쪽만 다시 나눕니다.

반대로 `root->key >= key`이면 root와 오른쪽 subtree는 `b` 쪽에 남고, 왼쪽만 다시 나눕니다.

## 6. 삽입

새 key를 넣으려면 기존 Treap을 둘로 나눈 뒤, 가운데에 새 노드를 끼우고 다시 합칩니다.

```text
root를 key 기준으로 split
left: key보다 작은 원소
right: key 이상인 원소

root = merge(merge(left, newNode), right)
```

중복을 허용하지 않는 set이라면 먼저 `contains(key)`를 확인합니다.

```cpp
bool contains(Node* root, int key) {
    while (root) {
        if (root->key == key) return true;
        if (key < root->key) root = root->left;
        else root = root->right;
    }
    return false;
}
```

## 7. 삭제

삭제는 찾은 노드를 제거하고, 그 노드의 왼쪽 subtree와 오른쪽 subtree를 `merge`하면 됩니다.

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

## 8. 순위와 k번째 원소

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

## 9. 전체 구현

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

예를 들어 `orderOfKey(10)`은 10보다 작은 값의 개수이고, `kth(0)`은 가장 작은 값입니다.

## 10. 중복 key 처리

중복 원소가 필요하면 보통 두 방법 중 하나를 씁니다.

| 방법 | 설명 |
| --- | --- |
| `(value, id)`를 key로 사용 | 같은 값도 고유한 id로 구분한다 |
| 노드에 `count`를 저장 | 같은 key를 한 노드에 모으고 `size = leftSize + count + rightSize`로 계산한다 |

순위 질의가 "x보다 작은 원소 개수"라면 `count` 방식이 자연스럽습니다. 반대로 특정 삽입을 나중에 정확히 지워야 한다면 `(value, id)` 방식이 단순합니다.

## 11. Implicit Treap

Treap은 key를 직접 저장하지 않고, **현재 위치**를 key처럼 쓸 수도 있습니다. 이것을 Implicit Treap이라고 부릅니다.

배열을 Treap으로 저장하고 subtree size로 위치를 계산하면 다음 작업을 기대 `O(log n)`에 처리할 수 있습니다.

```text
1. 구간 [l, r]을 잘라낸다.
2. 잘라낸 구간을 다른 위치에 붙인다.
3. 구간을 뒤집는다.
4. 구간 합, 최솟값 같은 값을 관리한다.
```

이때 `split(root, k)`는 "앞에서 k개"와 "나머지"로 나눕니다. key 값이 아니라 subtree size를 기준으로 내려간다는 점만 다르고, `merge`는 거의 같습니다.

문자열 편집, 배열 구간 이동, 동적 순열 문제에서 Implicit Treap이 자주 등장합니다.

## 12. 다른 자료구조와 비교

| 자료구조 | 강점 | 약점 |
| --- | --- | --- |
| `std::set` | 표준 라이브러리, 안정적, 구현 불필요 | k번째/순위 질의가 기본 제공되지 않음 |
| Fenwick Tree | 빈도표 기반 순위 질의가 짧고 빠름 | 값 범위 압축이 필요하고 동적 key에 약함 |
| Segment Tree | 구간 정보 관리가 강함 | 동적 삽입/삭제에는 별도 처리가 필요함 |
| Treap | 동적 key, 순위 질의, split/merge 확장이 좋음 | 직접 구현해야 하고 random priority에 의존함 |

Treap은 "내가 원하는 정보를 붙일 수 있는 randomized balanced BST"로 생각하면 됩니다. 단순 정렬 집합만 필요하면 `std::set`이 낫고, 순위나 k번째 원소, split/merge가 필요해질 때 Treap이 좋은 선택지가 됩니다.

## 13. 자주 나는 실수

- 자식을 바꾼 뒤 `pull`을 빼먹으면 `size`가 틀어집니다.
- `merge(a, b)`를 호출할 때 `a`의 모든 key가 `b`보다 작다는 전제가 깨지면 BST 조건이 깨집니다.
- `kth(k)`의 k가 0-indexed인지 1-indexed인지 문제 전체에서 통일해야 합니다.
- 중복 key를 허용할지 먼저 정해야 합니다. 위 구현은 중복을 무시합니다.
- random priority가 같을 수는 있지만, 보통 `unsigned` 난수면 충돌 가능성이 충분히 작습니다. 매우 신경 쓰이면 priority를 64-bit로 두면 됩니다.

## 14. 확인 질문

Treap 문제를 풀 때는 아래를 먼저 정리합니다.

1. key는 실제 값인가, 현재 위치인가?
2. 중복 원소가 있는가?
3. 필요한 집계 정보는 `size`뿐인가, `sum`이나 `min`도 필요한가?
4. split/merge가 필요한가, 단순 삽입/삭제/순위 질의만 필요한가?
5. `kth`의 인덱스 기준은 0-indexed인가 1-indexed인가?

이 다섯 가지가 정리되면 Treap 구현에서 어떤 필드를 노드에 넣어야 하는지 자연스럽게 결정됩니다.
