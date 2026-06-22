# Dynamic Segment Tree

Dynamic Segment Tree는 좌표 범위가 매우 크지만 실제로 접근하는 지점이나 구간이 적을 때 필요한 node만 만드는 Segment Tree입니다. 좌표 압축이 어렵거나 온라인으로 새로운 좌표가 계속 등장하는 문제에서 유용합니다.

이 레슨은 Segment Tree, Persistent Segment Tree, Link-Cut Tree 이후에 보는 자료구조 심화입니다.

1. 전체 좌표 범위 `[L, R)`를 루트 하나로 둔다.
2. update/query가 내려가는 경로의 node만 생성한다.
3. lazy propagation을 결합하면 sparse range update도 처리할 수 있다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: segment tree, lazy propagation, coordinate range, recursion
- 함께 보면 좋은 레슨: Segment Tree, Persistent Segment Tree, Coordinate Compression
- 다음에 볼 레슨: implicit treap, sparse 2D segment tree, Li Chao Tree

## 1. 문제 신호

| 문제 표현 | Dynamic Segment Tree 관점 |
| --- | --- |
| 좌표가 `10^9` 또는 `10^18`까지 크다 | array tree 불가 |
| 업데이트/질의 수는 상대적으로 작다 | touched node만 생성 |
| 온라인으로 좌표가 들어온다 | 사전 좌표 압축 어려움 |
| 구간 update와 구간 sum/min query | lazy node 필요 |
| 대부분 구간은 기본값 0이다 | sparse structure |

좌표를 모두 미리 알고 있고 정렬해도 의미가 보존된다면 좌표 압축이 더 단순합니다. Dynamic Segment Tree는 압축이 불편하거나 구간 전체 길이가 의미 있을 때 선택합니다.

## 2. 기본 구조

일반 Segment Tree는 `4N` 배열을 잡지만, Dynamic Segment Tree는 node pool을 두고 child index를 필요할 때 만듭니다.

```text
node {
  left child index
  right child index
  aggregate
  lazy
}
```

좌표 범위는 inclusive보다 half-open `[left, right)`로 두는 편이 overflow와 off-by-one을 줄이기 좋습니다.

## 3. Range Add / Range Sum 구현

아래 구현은 큰 좌표 범위에서 구간 덧셈과 구간 합 질의를 처리합니다.

```cpp compile-check
#include <vector>
using namespace std;

struct DynamicSegmentTree {
    struct Node {
        int leftChild = 0;
        int rightChild = 0;
        long long sum = 0;
        long long lazy = 0;
    };

    vector<Node> tree;
    long long rootLeft;
    long long rootRight;

    DynamicSegmentTree(long long left, long long right) : rootLeft(left), rootRight(right) {
        tree.push_back(Node());
        tree.push_back(Node());
    }

    int newNode() {
        tree.push_back(Node());
        return (int)tree.size() - 1;
    }

    void apply(int node, long long left, long long right, long long value) {
        tree[node].sum += (right - left) * value;
        tree[node].lazy += value;
    }

    void push(int node, long long left, long long right) {
        if (tree[node].lazy == 0 || right - left <= 1) {
            return;
        }
        long long mid = left + (right - left) / 2;
        if (tree[node].leftChild == 0) {
            tree[node].leftChild = newNode();
        }
        if (tree[node].rightChild == 0) {
            tree[node].rightChild = newNode();
        }
        long long value = tree[node].lazy;
        apply(tree[node].leftChild, left, mid, value);
        apply(tree[node].rightChild, mid, right, value);
        tree[node].lazy = 0;
    }

    long long childSum(int child) const {
        return child == 0 ? 0 : tree[child].sum;
    }

    void pull(int node) {
        tree[node].sum = childSum(tree[node].leftChild) + childSum(tree[node].rightChild);
    }

    void rangeAdd(int node, long long left, long long right, long long ql, long long qr, long long value) {
        if (qr <= left || right <= ql) {
            return;
        }
        if (ql <= left && right <= qr) {
            apply(node, left, right, value);
            return;
        }
        push(node, left, right);
        long long mid = left + (right - left) / 2;
        if (ql < mid) {
            if (tree[node].leftChild == 0) {
                tree[node].leftChild = newNode();
            }
            rangeAdd(tree[node].leftChild, left, mid, ql, qr, value);
        }
        if (mid < qr) {
            if (tree[node].rightChild == 0) {
                tree[node].rightChild = newNode();
            }
            rangeAdd(tree[node].rightChild, mid, right, ql, qr, value);
        }
        pull(node);
    }

    long long rangeSum(int node, long long left, long long right, long long ql, long long qr) {
        if (node == 0 || qr <= left || right <= ql) {
            return 0;
        }
        if (ql <= left && right <= qr) {
            return tree[node].sum;
        }
        push(node, left, right);
        long long mid = left + (right - left) / 2;
        return rangeSum(tree[node].leftChild, left, mid, ql, qr)
             + rangeSum(tree[node].rightChild, mid, right, ql, qr);
    }

    void add(long long left, long long right, long long value) {
        rangeAdd(1, rootLeft, rootRight, left, right, value);
    }

    long long sum(long long left, long long right) {
        return rangeSum(1, rootLeft, rootRight, left, right);
    }
};
```

루트 범위는 문제 조건보다 한 칸 넓은 half-open 범위로 잡습니다. 예를 들어 좌표가 `0 <= x <= 1e9`이면 `[0, 1000000001)`처럼 둡니다.

## 4. 좌표 압축과 비교

| 조건 | 좌표 압축 | Dynamic Segment Tree |
| --- | --- | --- |
| 모든 좌표를 미리 알 수 있음 | 좋음 | 가능하지만 과함 |
| 구간 길이가 답에 직접 영향 | endpoint 보강 필요 | 자연스러움 |
| 온라인 좌표 등장 | 어려움 | 좋음 |
| 메모리 예측 | `O(K)` | `O(Q log C)` |
| 구현 난도 | 낮음 | 중간 |

좌표 압축에서는 구간 길이를 잃기 쉽습니다. 구간 합집합 길이처럼 실제 좌표 간격이 중요하면 compression interval을 별도로 관리해야 합니다.

## 5. Persistent와 결합

Dynamic Segment Tree는 node를 새로 만드는 구조라 persistent와도 잘 맞습니다. update 경로의 node만 clone하면 sparse persistent segment tree가 됩니다.

```text
newRoot = update(oldRoot, range)
```

다만 lazy propagation과 persistence를 함께 쓰면 query에서 node를 변경하지 않도록 push 방식을 조심해야 합니다.

## 6. 메모리 계산

구간 update 하나가 깊이 `log C`만큼 node를 만들고, segment tree interval decomposition 때문에 여러 경로에 닿을 수 있습니다.

```text
node count = O(number_of_operations * log coordinate_range)
```

좌표 범위가 `2^60`이어도 깊이는 60입니다. 문제는 범위 크기보다 연산 수와 lazy node 생성량입니다.

## 7. 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| point update/query | `O(log C)` |
| range update/query | `O(log C)`개의 canonical node 중심 |
| 생성 node 수 | touched interval 수에 비례 |
| 전체 메모리 | 보통 `O(Q log C)` |

## 8. 자주 하는 실수

1. `[left, right]`와 `[left, right)`를 섞어 한 칸을 잃는다.
2. `mid = (left + right) / 2`에서 overflow를 만든다.
3. query에서 lazy를 push하며 불필요한 child를 대량 생성한다.
4. root 범위를 실제 좌표 최댓값까지로 잡고 오른쪽 끝 query를 놓친다.
5. 좌표 압축이 더 쉬운 문제에 dynamic tree를 써서 구현만 복잡해진다.

## 9. 문제를 볼 때 체크할 조건

- 모든 좌표를 미리 읽을 수 있는가?
- 구간 길이 자체가 aggregate에 들어가는가?
- update/query가 point인지 range인지 명확한가?
- 값의 기본 상태가 0인가, 다른 초기값이 있는가?
- persistent나 lazy가 query 중 node를 바꾸면 안 되는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: sparse point update `/practice/...` 문제 필요 | 필요한 경로 node만 생성 | implicit segment tree |
| 표준 | TODO: 큰 좌표 range add sum `/practice/...` 문제 필요 | lazy propagation과 half-open interval | dynamic segment tree |
| 응용 | TODO: online rectangle sweep `/practice/...` 문제 필요 | 좌표 압축 없이 sparse cover 관리 | sweep, sparse range |
| 함정 | TODO: persistent sparse query `/practice/...` 문제 필요 | query 중 node 변경 방지 | persistence, lazy |
