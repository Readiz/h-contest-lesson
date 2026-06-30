# Treap과 BST 기본: 순위, 전체 구현, Implicit Treap

## 1. 순위와 k번째 원소

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

## 2. Treap 전체 구현

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

## 3. Implicit Treap

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

## 4. 구조별 비교

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

이 경우에는 Treap이 구현량 대비 강력한 선택입니다. 높이 보장을 엄격히 원하면 AVL, 접근 locality나 고급 동적 트리 응용이 중요하면 Splay를 검토합니다. 자세한 AVL/Splay 비교는 참고 노트의 `AVL과 Splay Tree 참고`에 남겨 두었습니다.

## 5. 자주 나는 실수

- 단순 BST를 쓰면서 입력이 정렬될 수 있다는 점을 놓치면 `O(n)`으로 터집니다.
- 회전 후 `height`, `size`, `sum` 같은 보조 정보를 갱신하지 않으면 이후 질의가 틀어집니다.
- AVL의 LR/RL 케이스에서 회전 순서를 반대로 쓰면 균형이 복구되지 않습니다.
- Splay에서 parent pointer를 하나라도 잘못 연결하면 트리 구조가 깨집니다.
- Treap의 `merge(a, b)`는 `a`의 모든 key가 `b`보다 작다는 전제가 필요합니다.
- `kth(k)`의 k가 0-indexed인지 1-indexed인지 문제 전체에서 통일해야 합니다.
- 중복 key를 허용할지 먼저 정해야 합니다. Treap 예시 구현은 중복을 무시합니다.

## 6. 문제를 볼 때 체크할 조건

1. 단순 정렬 집합이면 `std::set`으로 충분한가?
2. 순위나 k번째 원소가 필요한가?
3. key 범위가 커서 Fenwick Tree나 Segment Tree 좌표 압축이 불편한가?
4. split/merge 또는 동적 sequence 조작이 필요한가?
5. 최악 시간 보장이 중요한가, 기대/상각 시간으로 충분한가?
6. 직접 구현할 만큼 자료구조가 문제의 핵심인가?

이 질문을 통과하면 BST 계열을 직접 구현할 이유가 생깁니다. 그중 대회 코드에서 가장 균형 잡힌 선택은 보통 Treap입니다.

## 7. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: BST inorder 순회 문제 추가 | key 순서와 subtree 구조 확인 | inorder |
| 표준 | TODO: k번째 원소/순위 질의 문제 추가 | subtree size 갱신과 `kth` 구현 | order statistics |
| 응용 | TODO: 구간 뒤집기 Implicit Treap 문제 추가 | split/merge와 lazy reverse 결합 | implicit treap |
| 함정 | TODO: 중복 key 처리 문제 추가 | key 중복 허용 정책과 tie-break 설계 | duplicate key |
