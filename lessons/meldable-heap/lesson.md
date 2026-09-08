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

## 컴포넌트별 Skew Heap

각 컴포넌트의 후보를 최소 힙에 넣고, 컴포넌트가 합쳐질 때 두 힙도 합칩니다. 모든 힙이 같은 `pool`을 공유하며 `-1`을 빈 자식으로 씁니다.

`merge`는 더 작은 루트를 위에 두고 오른쪽 자식과 나머지 힙을 합친 뒤 두 자식을 바꿉니다. `push`는 원소 하나짜리 힙과의 병합, `pop`은 루트의 두 자식 사이의 병합입니다.

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

예를 들어 그룹 0에 7과 2, 그룹 1에 5를 넣고 합치면 어느 그룹 번호로 조회해도 최솟값은 2입니다. 한 번 꺼내면 다음 값은 5입니다. 이미 같은 컴포넌트를 합칠 때는 힙도 다시 합치지 않아야 합니다.

`top`, `pop` 전에는 `empty`를 확인합니다. 꺼낸 노드는 pool에 남으므로 메모리는 현재 원소 수가 아니라 **총 삽입 횟수**에 비례합니다. 합칠 두 힙은 같은 pool을 사용하되 노드를 공유하면 안 됩니다. 최대 힙이 필요하면 루트의 대소 비교를 뒤집습니다.

## 한 번의 병합 시간도 제한해야 한다면

Skew Heap의 로그 시간은 여러 연산에 나눈 상각 비용입니다. 개별 병합은 깊이 `O(n)`까지 내려갈 수 있습니다.

Leftist Heap은 각 노드에서 빈 자식까지의 최단 거리 `dist`를 저장하고 `dist(left) >= dist(right)`를 유지합니다. 병합이 내려가는 오른쪽 경로가 `O(log n)`으로 제한되어 한 번의 병합에도 로그 시간을 보장합니다. 재귀 스택과 개별 연산 지연이 중요한 환경에서 이 차이를 고려합니다.

## 병합이 드문 경우

두 힙을 거의 합치지 않는다면 작은 힙에서 큰 힙으로 원소를 하나씩 옮기는 방법도 가능합니다. 삽입·삭제 없이 병합만 반복하는 상황에서는 원소가 이동할 때마다 소속 힙 크기가 두 배 이상이 되어 원소당 이동이 `O(log n)`번으로 제한됩니다. 중간에 원소를 제거한다면 이 크기 증가 논리를 그대로 적용할 수는 없습니다.

## 시간 복잡도

아래는 힙 자체의 비용입니다. 컴포넌트 번호를 받는 위 메서드에는 DSU의 상각 `O(alpha(n))` 조회 비용도 추가됩니다.

| 작업 | 시간 |
| --- | --- |
| `top` | `O(1)` |
| `push` | amortized `O(log n)` |
| `pop` | amortized `O(log n)` |
| `meld` | amortized `O(log n)` |
| 메모리 | `O(총 push 횟수)` |

Binary Heap의 `push`, `pop`도 `O(log n)`이지만, `meld`가 빠르지 않다는 차이가 있습니다.
