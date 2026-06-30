# Treap과 BST 기본: BST 기본기와 균형이 필요한 이유

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

## 3. 회전이 하는 일

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

실제 균형 BST에서는 회전 후 `height`, `size`, `sum` 같은 보조 정보를 다시 계산해야 합니다. Treap도 회전으로 설명할 수 있지만, 대회 구현에서는 `split`과 `merge`로 쓰는 편이 더 짧고 실수가 적습니다.

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
| 구조 | 균형 유지 방식 | 시간 보장 | 이 레슨에서의 위치 |
| --- | --- | --- | --- |
| Treap | random priority로 트리 모양을 랜덤화 | 기대 `O(log n)` | 기본 트랙 본문 |
| AVL Tree | subtree 높이 차이를 1 이하로 유지 | 최악 `O(log n)` | 참고 노트 |
| Splay Tree | 접근한 노드를 root로 끌어올림 | amortized `O(log n)` | 참고 노트 |

Treap을 구현할 때는 "BST 순서를 보존한다"와 "`priority`가 높은 노드가 위에 온다"는 두 조건만 계속 확인하면 됩니다. AVL/Splay의 자세한 회전 경우는 참고 노트의 `AVL과 Splay Tree 참고`에서 따로 봅니다.
