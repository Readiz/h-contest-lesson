# Link-Cut Tree

Link-Cut Tree는 동적으로 변하는 forest에서 `link`, `cut`, path query를 처리하는 자료구조입니다. Heavy-Light Decomposition이 정적인 트리 경로를 배열 구간으로 나누는 방식이라면, Link-Cut Tree는 preferred path를 splay tree로 관리해 간선 변경까지 처리합니다.

이 레슨은 트리 심화, AVL/Splay 참고, Segment Tree 이후에 보는 dynamic tree 자료구조입니다.

1. 각 정점은 auxiliary splay tree의 노드다.
2. `access(v)`로 root에서 `v`까지의 preferred path를 하나의 splay로 노출한다.
3. `makeroot(v)`로 represented tree의 root 방향을 뒤집어 임의 path를 다룬다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: tree path, splay rotation, lazy reverse, aggregate pull
- 함께 보면 좋은 레슨: 트리 심화, AVL/Splay 참고, Segment Tree, Treap
- 다음에 볼 레슨: dynamic connectivity, Euler tour tree, dynamic forest with edge weights

## 1. 문제 신호

| 문제 표현 | Link-Cut Tree 관점 |
| --- | --- |
| 트리에 간선을 추가/삭제한다 | link/cut |
| 동적 forest에서 두 정점 연결 여부 | findRoot |
| 두 정점 사이 path sum/min/max | makeroot + access |
| edge weight가 바뀐다 | represented edge를 node로 모델링 |
| 온라인 질의가 많다 | amortized `O(log N)` |

단순히 정적 트리 경로 질의라면 Heavy-Light Decomposition이 더 쉽습니다. Link-Cut Tree는 간선 변경이 실제로 필요한 경우에 사용합니다.

## 2. 핵심 연산

| 연산 | 의미 |
| --- | --- |
| `access(x)` | represented root에서 `x`까지의 preferred path를 노출 |
| `splay(x)` | auxiliary tree에서 `x`를 root로 올림 |
| `makeRoot(x)` | represented tree의 root를 `x`로 바꿈 |
| `findRoot(x)` | represented tree의 root를 찾음 |
| `link(u, v)` | 서로 다른 tree의 두 정점을 연결 |
| `cut(u, v)` | 두 정점 사이의 직접 간선을 제거 |

경로 질의 `u-v`는 `makeRoot(u); access(v); splay(v);` 후 `v`의 splay aggregate를 읽습니다.

## 3. 상태 추적: `1-2-3` path query

정점 값이 아래처럼 들어 있다고 하겠습니다.

```text
1(value=10) -- 2(value=20) -- 3(value=30)
```

`queryPathSum(1, 3)`은 아래 순서로 진행합니다.

```text
makeRoot(1)
access(3)
return aggregate at 3
```

### 3.1 `makeRoot(1)`

`makeRoot(1)`은 먼저 `access(1)`로 represented tree root에서 `1`까지의 preferred path를 드러낸 뒤, 그 path에 reverse lazy를 겁니다. 이 reverse는 실제 edge를 삭제하거나 다시 만들지 않습니다. auxiliary splay 안의 좌우 방향만 뒤집어서 "이제 1을 represented root로 보겠다"는 방향을 맞춥니다.

```text
before represented root: 1 또는 2 또는 3일 수 있음
after makeRoot(1): represented root를 1처럼 다룰 수 있음
```

그래서 이후 `1 -> 3` 경로를 root-to-node path처럼 노출할 수 있습니다.

### 3.2 `access(3)`

`access(3)`은 `3`에서 parent pointer를 따라 올라가며 각 auxiliary splay의 오른쪽 child를 직전 path로 교체합니다. 결과적으로 represented root `1`에서 `3`까지의 preferred path가 하나의 auxiliary splay로 드러납니다.

개념적으로는 아래 path가 한 splay의 inorder 순서가 됩니다.

```text
1, 2, 3
```

마지막에 `splay(3)`을 하므로 `3`이 auxiliary root가 되고, `3`의 subtree aggregate에는 path `1-2-3` 전체가 들어 있습니다.

```text
tree[3].sum = 10 + 20 + 30 = 60
```

### 3.3 `cut(u, v)` 조건이 저 모양인 이유

`cut(u, v)`도 같은 원리입니다.

```text
makeRoot(u)
access(v)
```

이후 `u-v`가 직접 edge라면 드러난 path는 `u, v` 두 정점뿐이어야 합니다. 그래서 구현은 아래 조건을 확인합니다.

```text
tree[v].child[0] == u
tree[u].child[1] == 0
```

첫 번째 조건은 `u`가 `v`의 바로 왼쪽에 있다는 뜻이고, 두 번째 조건은 `u`와 `v` 사이에 다른 정점이 끼어 있지 않다는 뜻입니다. 이 확인 없이 `child[0]`만 끊으면 직접 edge가 아닌 긴 path를 잘못 자를 수 있습니다.

## 4. 구현

아래 구현은 정점 값의 path sum을 관리합니다. 간선 weight 문제는 각 간선을 별도 노드로 만들어 두 endpoint와 연결하는 방식으로 확장합니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct LinkCutTree {
    struct Node {
        int child[2] = {0, 0};
        int parent = 0;
        bool reverse = false;
        long long value = 0;
        long long sum = 0;
    };

    vector<Node> tree;

    explicit LinkCutTree(int n) : tree(n + 1) {}

    bool isSplayRoot(int x) const {
        int p = tree[x].parent;
        return p == 0 || (tree[p].child[0] != x && tree[p].child[1] != x);
    }

    void pull(int x) {
        tree[x].sum = tree[tree[x].child[0]].sum + tree[x].value + tree[tree[x].child[1]].sum;
    }

    void applyReverse(int x) {
        if (x == 0) {
            return;
        }
        swap(tree[x].child[0], tree[x].child[1]);
        tree[x].reverse = !tree[x].reverse;
    }

    void push(int x) {
        if (!tree[x].reverse) {
            return;
        }
        applyReverse(tree[x].child[0]);
        applyReverse(tree[x].child[1]);
        tree[x].reverse = false;
    }

    void pushPath(int x) {
        vector<int> stack;
        stack.push_back(x);
        while (!isSplayRoot(x)) {
            x = tree[x].parent;
            stack.push_back(x);
        }
        while (!stack.empty()) {
            push(stack.back());
            stack.pop_back();
        }
    }

    void rotate(int x) {
        int p = tree[x].parent;
        int g = tree[p].parent;
        int direction = tree[p].child[1] == x;
        int moved = tree[x].child[direction ^ 1];

        if (!isSplayRoot(p)) {
            tree[g].child[tree[g].child[1] == p] = x;
        }
        tree[x].parent = g;

        tree[x].child[direction ^ 1] = p;
        tree[p].parent = x;

        tree[p].child[direction] = moved;
        if (moved) {
            tree[moved].parent = p;
        }

        pull(p);
        pull(x);
    }

    void splay(int x) {
        pushPath(x);
        while (!isSplayRoot(x)) {
            int p = tree[x].parent;
            int g = tree[p].parent;
            if (!isSplayRoot(p)) {
                bool zigzig = (tree[p].child[0] == x) == (tree[g].child[0] == p);
                rotate(zigzig ? p : x);
            }
            rotate(x);
        }
    }

    int access(int x) {
        int last = 0;
        for (int y = x; y != 0; y = tree[y].parent) {
            splay(y);
            tree[y].child[1] = last;
            pull(y);
            last = y;
        }
        splay(x);
        return last;
    }

    void makeRoot(int x) {
        access(x);
        applyReverse(x);
    }

    int findRoot(int x) {
        access(x);
        while (tree[x].child[0]) {
            push(x);
            x = tree[x].child[0];
        }
        splay(x);
        return x;
    }

    bool connected(int u, int v) {
        if (u == v) {
            return true;
        }
        makeRoot(u);
        return findRoot(v) == u;
    }

    bool link(int u, int v) {
        makeRoot(u);
        if (findRoot(v) == u) {
            return false;
        }
        tree[u].parent = v;
        return true;
    }

    bool cut(int u, int v) {
        makeRoot(u);
        access(v);
        if (tree[v].child[0] != u || tree[u].child[1] != 0) {
            return false;
        }
        tree[v].child[0] = 0;
        tree[u].parent = 0;
        pull(v);
        return true;
    }

    void setValue(int x, long long value) {
        access(x);
        tree[x].value = value;
        pull(x);
    }

    long long queryPathSum(int u, int v) {
        makeRoot(u);
        access(v);
        return tree[v].sum;
    }
};
```

## 5. Edge Weight 모델링

Link-Cut Tree 노드가 정점이라면 path aggregate는 정점 값 합입니다. 간선 값 합을 구하려면 각 간선을 별도 노드로 만들고 아래처럼 연결합니다.

```text
u -- edgeNode -- v
value(edgeNode) = edge weight
value(original vertex) = 0
```

그러면 path sum이 간선 weight 합이 됩니다. 간선 삭제도 `cut(u, edgeNode)`와 `cut(edgeNode, v)`로 처리합니다.

## 6. HLD와 비교

| 조건 | HLD | Link-Cut Tree |
| --- | --- | --- |
| 트리 구조 | 정적 | 동적 forest |
| 구현 난도 | 중간 | 높음 |
| 경로 query | `O(log^2 N)` 또는 `O(log N)` | amortized `O(log N)` |
| 간선 추가/삭제 | 어려움 | 가능 |
| 디버깅 | 배열 index 중심 | splay/lazy 중심 |

간선 변경이 없다면 HLD를 먼저 선택하는 편이 안전합니다.

## 7. 시간 복잡도

| 연산 | 복잡도 |
| --- | --- |
| `access`, `makeRoot`, `findRoot` | amortized `O(log N)` |
| `link`, `cut` | amortized `O(log N)` |
| path query/update | amortized `O(log N)` |

## 8. 자주 하는 실수

1. `splay` 전에 ancestor path의 lazy reverse를 push하지 않는다.
2. `isSplayRoot`와 represented tree root를 혼동한다.
3. `makeRoot` 없이 `link`나 path query를 수행한다.
4. `cut`에서 두 정점이 직접 연결됐는지 확인하지 않는다.
5. edge weight를 정점 값과 섞어 path sum이 한 칸 어긋난다.

## 9. 문제를 볼 때 체크할 조건

- forest가 유지되는가, cycle이 생길 수 있는가?
- edge weight인지 vertex weight인지 명확한가?
- path aggregate가 commutative하지 않다면 방향 처리가 필요한가?
- `cut`이 edge id로 주어지는가, endpoint pair로 주어지는가?
- offline으로 바꾸면 DSU rollback으로 더 쉽게 풀 수 있는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: dynamic forest connectivity `/practice/...` 문제 필요 | link/cut/findRoot 구현 | link-cut tree |
| 표준 | TODO: dynamic tree path sum `/practice/...` 문제 필요 | makeroot-access path query | splay aggregate |
| 응용 | TODO: dynamic MST edge replacement `/practice/...` 문제 필요 | edge node 모델링 | dynamic forest |
| 함정 | TODO: repeated cut invalid edge `/practice/...` 문제 필요 | 직접 간선 확인 | cut validation |
