# Meldable Heap

Meldable Heap은 두 힙을 빠르게 합치는 `meld` 또는 `merge` 연산을 핵심으로 하는 우선순위 큐입니다.

일반적인 binary heap은 `push`, `top`, `pop`이 빠르지만, 두 heap을 합치는 연산은 자연스럽지 않습니다. 배열로 된 heap 두 개를 합치려면 원소를 모두 모아서 다시 heapify하거나, 한쪽 원소를 다른 쪽에 하나씩 넣어야 합니다.

```text
heap A에 원소 n개
heap B에 원소 m개

binary heap:
1. 전부 모아서 heapify -> O(n + m)
2. B의 원소를 A에 하나씩 push -> O(m log(n + m))
```

Meldable Heap은 이 합치기 자체를 빠르게 처리하도록 만든 힙입니다. 핵심 장점은 원소를 전부 순회해서 새 heap을 만들지 않고, 두 root에서 시작해 자식 인덱스만 조금 바꿔 합친다는 점입니다. Skew Heap처럼 보장된 merge 규칙을 쓰면 전체 원소 수가 아니라 트리 높이만큼만 내려가므로 amortized `O(log n)` 계열로 heap merge를 처리합니다.

## 언제 필요한가

두 우선순위 큐를 자주 합쳐야 할 때 필요합니다.

```text
각 컴포넌트마다 heap을 들고 있다가 union할 때 합친다.
트리의 subtree 정보를 합치며 가장 작은/큰 후보를 유지한다.
여러 그룹이 병합되고, 그룹마다 우선순위가 가장 높은 원소를 꺼낸다.
```

예를 들어 Union-Find로 컴포넌트를 합치면서 각 컴포넌트의 최솟값 후보를 관리한다고 하겠습니다. 일반 `priority_queue`를 쓰면 두 컴포넌트가 합쳐질 때 작은 heap의 원소를 큰 heap에 하나씩 옮기는 식으로 구현할 수 있습니다. 이 방식도 small-to-large로 하면 꽤 좋지만, heap 자체의 merge가 필요하다면 Meldable Heap이 더 직접적입니다.

## 핵심 연산 meld

Meldable Heap에서 가장 중요한 함수는 두 heap의 root를 받아 하나의 heap root를 반환하는 `merge`입니다.

```text
int merge(int a, int b)
```

min-heap이라면 root에는 가장 작은 값이 있어야 합니다. 두 heap을 합칠 때는 두 root 중 더 작은 쪽이 새 root가 됩니다.

```text
if a.key > b.key:
    swap(a, b)

새 root는 a
b를 a의 한쪽 subtree와 다시 merge
```

여기까지는 간단하지만, 한쪽으로만 계속 붙이면 트리가 한 줄로 길어질 수 있습니다. Skew Heap은 merge 뒤에 자식을 매번 바꾸는 짧은 규칙으로 이 쏠림을 amortized 관점에서 줄입니다.

## Skew Heap: 인덱스 기반 구현

아래 코드는 min-heap 전체 구현입니다. 포인터 대신 `pool`의 인덱스를 저장하고, `-1`을 null처럼 씁니다. `pop`한 노드는 따로 지우지 않고 pool에 남겨 둡니다. 대회 코드에서는 전체 `push` 횟수만큼 메모리를 쓰고, 테스트 케이스가 끝나면 pool을 통째로 비우는 방식이 단순합니다.

```cpp
#include <algorithm>
#include <vector>
using namespace std;

struct SkewHeap {
    struct Node {
        int key;
        int left;
        int right;

        Node(int key) : key(key), left(-1), right(-1) {}
    };

    vector<Node> pool;
    int root = -1;

    int newNode(int key) {
        pool.push_back(Node(key));
        return (int)pool.size() - 1;
    }

    int merge(int a, int b) {
        if (a == -1) return b;
        if (b == -1) return a;
        if (pool[a].key > pool[b].key) swap(a, b);

        pool[a].right = merge(pool[a].right, b);
        swap(pool[a].left, pool[a].right);
        return a;
    }

    bool empty() const {
        return root == -1;
    }

    int top() const {
        return pool[root].key;
    }

    void push(int key) {
        root = merge(root, newNode(key));
    }

    void pop() {
        root = merge(pool[root].left, pool[root].right);
    }

};
```

핵심은 `merge` 하나입니다. `push`는 원소 하나짜리 heap과 합치고, `pop`은 root의 두 자식을 합칩니다. 여러 heap root를 합치려면 그 root들이 같은 `pool`을 공유해야 합니다. 아래 DSU 예시가 그 형태입니다.

Skew Heap 규칙은 단순합니다. root key가 작은 쪽을 위로 두고, 오른쪽 subtree와 merge한 뒤 왼쪽과 오른쪽 자식을 무조건 바꿉니다.

```cpp
int merge(int a, int b) {
    if (a == -1) return b;
    if (b == -1) return a;
    if (pool[a].key > pool[b].key) swap(a, b);

    pool[a].right = merge(pool[a].right, b);
    swap(pool[a].left, pool[a].right);
    return a;
}
```

Skew Heap은 별도 `dist`나 `size`를 저장하지 않으면서도, 매번 swap하는 규칙 때문에 한쪽으로만 계속 내려가는 패턴을 amortized 관점에서 막습니다.

Union-Find와 합치면 아래처럼 각 컴포넌트 대표가 heap root를 하나씩 가집니다. 컴포넌트를 합칠 때 DSU 대표를 합치고, heap root도 같이 merge합니다.

```cpp
#include <algorithm>
#include <vector>
using namespace std;

struct ComponentHeapDSU {
    struct Node {
        int key;
        int left;
        int right;

        Node(int key) : key(key), left(-1), right(-1) {}
    };

    vector<int> parent;
    vector<int> size;
    vector<int> heap;
    vector<Node> pool;

    ComponentHeapDSU(int n) : parent(n), size(n, 1), heap(n, -1) {
        for (int i = 0; i < n; i++) parent[i] = i;
    }

    int newNode(int key) {
        pool.push_back(Node(key));
        return (int)pool.size() - 1;
    }

    int find(int x) {
        if (parent[x] == x) return x;
        return parent[x] = find(parent[x]);
    }

    int merge(int a, int b) {
        if (a == -1) return b;
        if (b == -1) return a;
        if (pool[a].key > pool[b].key) swap(a, b);

        pool[a].right = merge(pool[a].right, b);
        swap(pool[a].left, pool[a].right);
        return a;
    }

    void push(int x, int key) {
        int r = find(x);
        heap[r] = merge(heap[r], newNode(key));
    }

    void unite(int a, int b) {
        int ra = find(a);
        int rb = find(b);
        if (ra == rb) return;

        if (size[ra] < size[rb]) swap(ra, rb);
        parent[rb] = ra;
        size[ra] += size[rb];
        heap[ra] = merge(heap[ra], heap[rb]);
        heap[rb] = -1;
    }

    bool empty(int x) {
        return heap[find(x)] == -1;
    }

    int top(int x) {
        return pool[heap[find(x)]].key;
    }

    void pop(int x) {
        int r = find(x);
        int old = heap[r];
        heap[r] = merge(pool[old].left, pool[old].right);
    }
};
```

실제 제출 코드에서는 `top`, `pop` 전에 해당 컴포넌트 heap이 비어 있지 않은지 확인합니다. `pop`한 노드는 pool에 남지만 다시 root에서 도달하지 않으므로 결과에는 영향을 주지 않습니다.

위 코드는 min-heap입니다. max-heap으로 바꿀 때는 root 비교 방향을 뒤집습니다.

```cpp
if (pool[a].key < pool[b].key) {
    swap(a, b);
}
```

합칠 두 heap은 같은 pool을 사용하되 노드를 공유하면 안 됩니다. 같은 heap을 자기 자신과 합치거나, 이미 소속된 노드를 다시 넣으면 구조가 깨집니다.

## 참고: Leftist Heap

여기부터는 worst-case `O(log n)` 보장을 더 직관적으로 보고 싶을 때 보는 참고 구현입니다. 앞의 Skew Heap DSU 통합 예시를 먼저 이해한 뒤, 쏠림을 줄이는 정보를 하나 더 저장한다고 보면 됩니다.

### Leftist Heap

Leftist Heap은 오른쪽 경로가 짧게 유지되도록 만드는 Meldable Heap입니다.

각 노드에 `dist`를 저장합니다. `dist`는 그 노드에서 null 자식까지 가는 가장 짧은 거리라고 생각하면 됩니다. 보통 null의 dist를 0, 실제 노드의 dist를 `right->dist + 1` 형태로 둡니다.

Leftist Heap은 항상 아래 조건을 유지합니다.

```text
dist(left) >= dist(right)
```

즉 오른쪽 subtree가 왼쪽 subtree보다 길어지면 두 자식을 바꿉니다. merge는 오른쪽으로만 내려가기 때문에 오른쪽 경로가 짧으면 merge가 빠릅니다.

### Leftist Heap 핵심 merge

```cpp
#include <algorithm>
#include <vector>
using namespace std;

struct LeftistHeapCore {
    struct Node {
        int key;
        int dist;
        int left;
        int right;

        Node(int key) : key(key), dist(1), left(-1), right(-1) {}
    };

    vector<Node> pool;

    int getDist(int node) const {
        return node == -1 ? 0 : pool[node].dist;
    }

    int merge(int a, int b) {
        if (a == -1) return b;
        if (b == -1) return a;
        if (pool[a].key > pool[b].key) swap(a, b);

        pool[a].right = merge(pool[a].right, b);
        if (getDist(pool[a].left) < getDist(pool[a].right)) {
            swap(pool[a].left, pool[a].right);
        }
        pool[a].dist = getDist(pool[a].right) + 1;
        return a;
    }
};
```

흐름은 Skew Heap과 거의 같습니다. 다만 매번 무조건 swap하지 않고, `dist(left) >= dist(right)`가 되도록 필요할 때만 swap한 뒤 `dist`를 갱신합니다.

### Leftist Heap과 Skew Heap 비교

| 구조 | 추가 정보 | merge 성능 | 장점 |
| --- | --- | --- | --- |
| Leftist Heap | `dist` 저장 | `O(log n)` | 성능 보장이 직관적 |
| Skew Heap | 없음 | amortized `O(log n)` | 본문 구현처럼 짧음 |
| Binary Heap | 배열 | 빠른 meld 없음 | cache-friendly, 표준 라이브러리 |

대부분의 문제에서는 C++ `priority_queue`가 가장 간단합니다. 두 heap을 합치는 연산이 문제의 중심일 때만 Meldable Heap을 고려합니다.

## priority_queue로 대체할 수 있는 경우

두 heap을 합칠 일이 적거나, 한쪽 heap의 원소 수가 항상 작다면 `priority_queue`와 small-to-large로 충분할 수 있습니다.

```cpp
if (pq[a].size() < pq[b].size()) {
    swap(pq[a], pq[b]);
}

while (!pq[b].empty()) {
    pq[a].push(pq[b].top());
    pq[b].pop();
}
```

각 원소가 작은 heap에서 큰 heap으로 옮겨질 때마다 자신이 들어 있는 heap 크기가 적어도 두 배가 되므로, 전체 이동 횟수를 줄일 수 있습니다.

하지만 문제에서 merge가 매우 많고, heap 자체를 합치는 연산이 핵심이면 Meldable Heap이 더 깔끔합니다.

## 시간 복잡도

오른쪽으로만 내려가는 naive merge는 트리 높이에 그대로 영향을 받아 최악 `O(n)`이 될 수 있습니다. Skew Heap은 같은 node-index 구조에 swap 규칙만 추가해 amortized `O(log n)`을 얻습니다.

| 작업 | 시간 |
| --- | --- |
| `top` | `O(1)` |
| `push` | amortized `O(log n)` |
| `pop` | amortized `O(log n)` |
| `meld` | amortized `O(log n)` |
| 메모리 | `O(총 push 횟수)` |

Leftist Heap은 `push`, `pop`, `meld`가 worst-case `O(log n)`이고, Skew Heap은 amortized `O(log n)`입니다. Skew Heap의 개별 연산은 깊이 `O(n)`까지 내려갈 수 있으므로, 재귀 스택 상한도 따로 확인해야 합니다.

Binary Heap의 `push`, `pop`도 `O(log n)`이지만, `meld`가 빠르지 않다는 차이가 있습니다.
