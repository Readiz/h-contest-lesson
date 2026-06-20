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

## 문서 구성

본문은 아래 하위 문서로 나누어 두었습니다.

- [BST와 회전 기본기](pages/bst-and-rotation.md) - BST 기본 연산, inorder 순회, 회전, 균형 필요성을 정리합니다.
- [AVL과 Splay Tree](pages/balanced-bst.md) - AVL 회전과 Splay Tree의 회전 패턴 및 특징을 다룹니다.
- [Treap 핵심 연산](pages/treap-core.md) - Treap 노드 구조, merge, split, 삽입과 삭제를 정리합니다.
- [순위, 전체 구현, Implicit Treap](pages/order-statistics-and-implicit.md) - 순위 질의, 전체 구현, Implicit Treap, 구조 비교와 실수 포인트를 모았습니다.
