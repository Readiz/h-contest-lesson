# Treap과 BST 기본

Treap은 직접 구현하기 쉬운 randomized balanced BST입니다. 여기서는 일반 BST의 핵심 성질을 먼저 잡고, 그 위에 Treap의 `priority`, `split`, `merge`, 순위 질의를 얹는 흐름으로 봅니다.

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

균형 BST는 이 문제를 해결하려는 자료구조입니다. Treap은 각 노드에 무작위 `priority`를 붙여 트리 모양을 입력 순서에 덜 민감하게 만들고, 기대 `O(log n)`에 삽입, 삭제, 탐색, 순위 질의를 처리합니다.

```text
정렬된 key 집합을 유지하면서 삽입, 삭제, 탐색을 빠르게 한다.
```

AVL Tree와 Splay Tree도 중요한 균형 BST지만, 이 레슨의 본선은 Treap입니다. AVL/Splay의 회전 패턴과 보장 방식은 참고 노트의 `AVL과 Splay Tree 참고`로 분리해 두었습니다.

## 문서 구성

본문은 아래 하위 문서로 나누어 두었습니다.

- [BST 기본기와 균형이 필요한 이유](pages/bst-and-rotation.md) - BST 기본 연산, inorder 순회, 회전, 균형 필요성을 정리합니다.
- [Treap 핵심 연산](pages/treap-core.md) - Treap 노드 구조, merge, split, 삽입과 삭제를 정리합니다.
- [순위, 전체 구현, Implicit Treap](pages/order-statistics-and-implicit.md) - 순위 질의, 전체 구현, Implicit Treap, 구조 비교와 실수 포인트를 모았습니다.
