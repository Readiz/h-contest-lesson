# Treap과 BST 기본

Treap은 직접 구현하기 쉬운 randomized balanced BST입니다. `key`로 탐색 순서를, 무작위 `priority`로 트리의 모양을 정합니다.

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

BST를 왼쪽 자식, 현재 노드, 오른쪽 자식 순으로 방문하면 key가 오름차순으로 나옵니다. Treap은 이 순서를 유지한 채 priority로 부모를 정합니다.

[핵심 연산과 순위](pages/treap-core.md)에서 노드 크기 갱신, split·merge, 삽입·삭제, k번째 원소 찾기를 이어서 구현합니다.
