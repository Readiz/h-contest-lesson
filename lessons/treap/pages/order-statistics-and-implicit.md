# Treap과 BST 기본: 순위, 전체 구현, Implicit Treap

## 순위와 k번째 원소

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

## Treap 전체 구현

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

## Implicit Treap

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
