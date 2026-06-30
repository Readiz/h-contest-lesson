# AVL과 Splay Tree 참고

AVL Tree와 Splay Tree는 Treap과 같은 BST 계열이지만, 현재 기본 학습 트랙에서는 Treap을 먼저 봅니다. Treap은 `split`과 `merge` 구현이 짧고 order statistics나 implicit sequence로 확장하기 쉬워 대회 코드에서 바로 쓰기 좋습니다.

이 문서는 Treap 이후에 "다른 균형 BST는 어떤 보장을 주는가"를 확인하는 참고 노트입니다. BST 기본 연산과 회전이 낯설다면 먼저 기본 트랙의 `Treap과 BST 기본`에서 BST 페이지를 봅니다.

## 1. AVL Tree

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

## 2. AVL 회전 경우

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

## 3. Splay Tree

Splay Tree는 어떤 노드를 접근할 때마다 그 노드를 root로 끌어올리는 BST입니다. 이 끌어올리는 연산을 splay라고 합니다.

Splay Tree는 노드마다 height나 priority를 저장하지 않습니다. 대신 자주 접근한 노드가 root 근처에 오도록 트리를 계속 재구성합니다.

```text
최근에 접근한 key가 다시 접근될 가능성이 높다.
구간을 split/merge해야 한다.
amortized 보장이면 충분하다.
```

이런 상황에서 Splay Tree가 유용합니다. 각 연산의 최악 시간은 길 수 있지만, 연산 전체를 평균적으로 보면 amortized `O(log n)`입니다.

## 4. Splay 회전 패턴

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

## 5. Splay의 특징

Splay Tree는 접근한 노드가 root가 됩니다.

```text
find(x) 후 x가 root
insert(x) 후 x가 root
split할 때 기준 노드를 root로 올린 뒤 왼쪽/오른쪽을 자름
```

이 성질 때문에 동적 sequence, Link-Cut Tree 같은 고급 자료구조의 기반으로 쓰입니다.

장점은 보조 정보가 적고 split/join에 강하다는 점입니다. 단점은 구현이 섬세하고, 한 연산의 최악 시간이 `O(n)`까지 갈 수 있다는 점입니다. 그래도 전체 연산열에 대해서는 amortized `O(log n)`이 보장됩니다.

## 6. Treap과의 선택 기준

| 구조 | 먼저 고를 상황 | 주의할 점 |
| --- | --- | --- |
| Treap | 짧은 구현, split/merge, order statistics, implicit sequence | random priority와 중복 key 정책 |
| AVL Tree | 최악 `O(log n)` 높이 보장이 중요함 | 삽입/삭제 회전 case 구현량 |
| Splay Tree | 접근 locality, amortized 보장, Link-Cut Tree 기반 | parent pointer와 lazy reverse 관리 |

일반 대회 풀이에서 직접 BST가 필요하면 Treap을 먼저 고려합니다. AVL은 최악 시간 보장이 중요하고 구현 검증 시간이 충분할 때, Splay는 Link-Cut Tree처럼 Splay 자체가 구조의 핵심일 때 선택합니다.

## 7. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 참고 | TODO: AVL 회전 trace 문제 필요 | LL/RR/LR/RL 회전 순서 확인 | balance factor |
| 참고 | TODO: Splay 접근 trace 문제 필요 | zig, zig-zig, zig-zag 구분 | amortized BST |
| 심화 | TODO: Link-Cut Tree 보조 연습 필요 | Splay lazy reverse와 aggregate 연결 | auxiliary tree |
