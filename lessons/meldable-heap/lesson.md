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

Meldable Heap은 이 합치기 자체를 `O(log n)` 수준으로 처리하도록 만든 힙입니다. 대표 구현으로 Leftist Heap, Skew Heap, Binomial Heap, Fibonacci Heap 등이 있습니다. 알고리즘 문제 실전에서는 Leftist Heap과 Skew Heap이 구현 난이도와 성능의 균형이 좋습니다.

## 1. 언제 필요한가

두 우선순위 큐를 자주 합쳐야 할 때 필요합니다.

```text
각 컴포넌트마다 heap을 들고 있다가 union할 때 합친다.
트리의 subtree 정보를 합치며 가장 작은/큰 후보를 유지한다.
여러 그룹이 병합되고, 그룹마다 우선순위가 가장 높은 원소를 꺼낸다.
```

예를 들어 Union-Find로 컴포넌트를 합치면서 각 컴포넌트의 최솟값 후보를 관리한다고 하겠습니다. 일반 `priority_queue`를 쓰면 두 컴포넌트가 합쳐질 때 작은 heap의 원소를 큰 heap에 하나씩 옮기는 식으로 구현할 수 있습니다. 이 방식도 small-to-large로 하면 꽤 좋지만, heap 자체의 merge가 필요하다면 Meldable Heap이 더 직접적입니다.

## 2. 핵심 연산 meld

Meldable Heap에서 가장 중요한 함수는 두 heap의 root를 받아 하나의 heap root를 반환하는 `merge`입니다.

```text
Node* merge(Node* a, Node* b)
```

min-heap이라면 root에는 가장 작은 값이 있어야 합니다. 두 heap을 합칠 때는 두 root 중 더 작은 쪽이 새 root가 됩니다.

```text
if a.key > b.key:
    swap(a, b)

새 root는 a
b를 a의 한쪽 subtree와 다시 merge
```

여기까지는 간단하지만, 한쪽으로만 계속 붙이면 트리가 한 줄로 길어질 수 있습니다. Leftist Heap과 Skew Heap은 이 트리가 너무 나빠지지 않도록 서로 다른 규칙을 사용합니다.

## 3. Leftist Heap

Leftist Heap은 오른쪽 경로가 짧게 유지되도록 만드는 Meldable Heap입니다.

각 노드에 `dist`를 저장합니다. `dist`는 그 노드에서 null 자식까지 가는 가장 짧은 거리라고 생각하면 됩니다. 보통 null의 dist를 0, 실제 노드의 dist를 `right->dist + 1` 형태로 둡니다.

Leftist Heap은 항상 아래 조건을 유지합니다.

```text
dist(left) >= dist(right)
```

즉 오른쪽 subtree가 왼쪽 subtree보다 길어지면 두 자식을 바꿉니다. merge는 오른쪽으로만 내려가기 때문에 오른쪽 경로가 짧으면 merge가 빠릅니다.

## 4. Leftist Heap 노드

아래 구현은 min-heap입니다. 작은 key가 먼저 나옵니다.

```cpp
#include <algorithm>
using namespace std;

struct Node {
    int key;
    int dist;
    Node* left;
    Node* right;

    Node(int key) : key(key), dist(1), left(nullptr), right(nullptr) {}
};

int getDist(Node* node) {
    return node ? node->dist : 0;
}
```

`dist`는 자식이 바뀔 때마다 갱신합니다. null을 0으로 두면 leaf의 dist는 1입니다.

## 5. Leftist Heap merge

```cpp
Node* merge(Node* a, Node* b) {
    if (!a) return b;
    if (!b) return a;

    if (a->key > b->key) {
        swap(a, b);
    }

    a->right = merge(a->right, b);

    if (getDist(a->left) < getDist(a->right)) {
        swap(a->left, a->right);
    }

    a->dist = getDist(a->right) + 1;
    return a;
}
```

흐름은 네 단계입니다.

```text
1. 둘 중 빈 heap이면 다른 쪽을 반환한다.
2. root key가 더 작은 쪽을 a로 만든다.
3. b를 a의 오른쪽 subtree와 merge한다.
4. leftist 조건이 깨졌으면 left/right를 바꾸고 dist를 갱신한다.
```

오른쪽으로만 재귀가 내려가므로, 오른쪽 경로가 짧다는 성질이 중요합니다.

## 6. push, top, pop

새 원소 삽입은 원소 하나짜리 heap을 만들어 기존 heap과 merge하면 됩니다.

```cpp
Node* push(Node* root, int key) {
    return merge(root, new Node(key));
}
```

최솟값은 root에 있습니다.

```cpp
int top(Node* root) {
    return root->key;
}
```

최솟값을 제거할 때는 root의 왼쪽 heap과 오른쪽 heap을 merge합니다.

```cpp
Node* pop(Node* root) {
    Node* left = root->left;
    Node* right = root->right;
    delete root;
    return merge(left, right);
}
```

빈 heap에서 `top`이나 `pop`을 호출하면 안 됩니다. 실제 wrapper에서는 `empty()`를 먼저 확인합니다.

## 7. Wrapper 구현

포인터를 직접 들고 다니면 실수가 나기 쉬우므로 구조체로 감싸면 좋습니다.

```cpp
#include <algorithm>
using namespace std;

struct MeldableHeap {
    struct Node {
        int key;
        int dist;
        Node* left;
        Node* right;

        Node(int key) : key(key), dist(1), left(nullptr), right(nullptr) {}
    };

    Node* root = nullptr;

    static int getDist(Node* node) {
        return node ? node->dist : 0;
    }

    static Node* mergeNodes(Node* a, Node* b) {
        if (!a) return b;
        if (!b) return a;

        if (a->key > b->key) {
            swap(a, b);
        }

        a->right = mergeNodes(a->right, b);

        if (getDist(a->left) < getDist(a->right)) {
            swap(a->left, a->right);
        }

        a->dist = getDist(a->right) + 1;
        return a;
    }

    bool empty() const {
        return root == nullptr;
    }

    int top() const {
        return root->key;
    }

    void push(int key) {
        root = mergeNodes(root, new Node(key));
    }

    void pop() {
        Node* old = root;
        root = mergeNodes(root->left, root->right);
        delete old;
    }

    void meld(MeldableHeap& other) {
        root = mergeNodes(root, other.root);
        other.root = nullptr;
    }
};
```

`meld` 후에는 `other.root = nullptr`로 비워야 합니다. 그렇지 않으면 두 heap 객체가 같은 노드를 동시에 소유하게 됩니다.

## 8. 메모리 정리

위 wrapper는 간단한 설명용이라 남은 노드를 자동으로 지우지 않습니다. 긴 프로그램이나 여러 테스트 케이스에서는 destructor를 두는 것이 안전합니다.

```cpp
void deleteTree(Node* node) {
    if (!node) return;
    deleteTree(node->left);
    deleteTree(node->right);
    delete node;
}

~MeldableHeap() {
    deleteTree(root);
}
```

다만 `meld`로 노드 소유권이 이동하므로, `other.root = nullptr` 처리가 반드시 있어야 합니다. 그래야 destructor에서 같은 노드를 두 번 지우지 않습니다.

알고리즘 문제에서는 많은 노드를 한 번 할당하고 끝나는 경우가 많아 memory pool을 쓰기도 합니다. `vector`를 pool로 쓸 때는 포인터가 무효화되지 않도록 충분히 `reserve`한 뒤 사용합니다.

```cpp
vector<Node> pool;

void initPool(int maxNodes) {
    pool.clear();
    pool.reserve(maxNodes);
}

Node* makeNode(int key) {
    pool.emplace_back(key);
    return &pool.back();
}
```

이 방식은 `delete`를 하지 않는 대신, 전체 테스트 케이스가 끝날 때 한 번에 버리는 구조에 가깝습니다. 여러 테스트 케이스를 처리한다면 `initPool` 호출 시점에 주의해야 합니다. `reserve`한 크기를 넘어 `emplace_back`하면 재할당이 일어나 기존 포인터가 깨질 수 있으므로, 필요한 노드 수를 넉넉하게 잡아야 합니다.

## 9. Skew Heap

Skew Heap은 Leftist Heap보다 더 단순한 Meldable Heap입니다. `dist`를 저장하지 않고, merge할 때마다 양쪽 자식을 무조건 바꿉니다.

```cpp
struct Node {
    int key;
    Node* left;
    Node* right;

    Node(int key) : key(key), left(nullptr), right(nullptr) {}
};

Node* merge(Node* a, Node* b) {
    if (!a) return b;
    if (!b) return a;

    if (a->key > b->key) {
        swap(a, b);
    }

    a->right = merge(a->right, b);
    swap(a->left, a->right);
    return a;
}
```

Skew Heap은 개별 연산 하나가 항상 `O(log n)`이라고 보장되지는 않지만, amortized `O(log n)` 성능을 가집니다. 구현이 매우 짧아서 대회 코드에서는 Skew Heap을 선호하는 경우도 있습니다.

## 10. Leftist Heap과 Skew Heap 비교

| 구조 | 추가 정보 | merge 성능 | 장점 |
| --- | --- | --- | --- |
| Leftist Heap | `dist` 저장 | `O(log n)` | 성능 보장이 직관적 |
| Skew Heap | 없음 | amortized `O(log n)` | 구현이 짧음 |
| Binary Heap | 배열 | 빠른 meld 없음 | cache-friendly, 표준 라이브러리 |

대부분의 문제에서는 C++ `priority_queue`가 가장 간단합니다. 두 heap을 합치는 연산이 문제의 중심일 때만 Meldable Heap을 고려합니다.

## 11. Union-Find와 함께 쓰기

Meldable Heap은 컴포넌트 병합과 잘 맞습니다. 각 컴포넌트 대표가 heap root를 하나씩 들고 있고, 두 컴포넌트를 합칠 때 heap도 같이 meld합니다.

```cpp
vector<int> parent(n);
vector<MeldableHeap> heaps(n);

int find(int x) {
    if (parent[x] == x) return x;
    return parent[x] = find(parent[x]);
}

void unite(int a, int b) {
    int rootA = find(a);
    int rootB = find(b);
    if (rootA == rootB) return;

    parent[rootB] = rootA;
    heaps[rootA].meld(heaps[rootB]);
}
```

실제로는 Union-Find의 size/rank 기준 합치기도 같이 고려합니다. 대표가 바뀌면 heap도 새 대표 쪽에 합쳐야 합니다.

```cpp
if (size[rootA] < size[rootB]) {
    swap(rootA, rootB);
}
parent[rootB] = rootA;
size[rootA] += size[rootB];
heaps[rootA].meld(heaps[rootB]);
```

이 패턴은 "그룹이 합쳐지고, 각 그룹에서 가장 작은 원소를 꺼낸다" 같은 문제에 잘 맞습니다.

## 12. priority_queue로 대체할 수 있는 경우

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

## 13. 시간 복잡도

Leftist Heap 기준 복잡도는 아래와 같습니다.

| 작업 | 시간 |
| --- | --- |
| `top` | `O(1)` |
| `push` | `O(log n)` |
| `pop` | `O(log n)` |
| `meld` | `O(log n)` |
| 메모리 | `O(n)` |

Skew Heap은 `push`, `pop`, `meld`가 amortized `O(log n)`입니다.

Binary Heap의 `push`, `pop`도 `O(log n)`이지만, `meld`가 빠르지 않다는 차이가 있습니다.

## 14. 자주 하는 실수

첫 번째 실수는 `meld` 후에도 두 heap이 같은 노드를 가리키게 두는 것입니다. `other.root = nullptr`로 소유권을 옮겨야 합니다.

두 번째 실수는 max-heap과 min-heap 비교식을 반대로 쓰는 것입니다. 위 구현은 min-heap입니다. max-heap이 필요하면 비교를 반대로 바꿉니다.

```cpp
if (a->key < b->key) {
    swap(a, b);
}
```

세 번째 실수는 Leftist Heap의 `dist`를 갱신하지 않는 것입니다. merge 후 자식 swap까지 끝난 뒤 `dist = getDist(right) + 1`로 갱신합니다.

네 번째 실수는 재귀 깊이를 무시하는 것입니다. Leftist Heap은 오른쪽 경로가 짧게 유지되므로 보통 안전하지만, 잘못 구현하면 한 줄 트리가 되어 깊은 재귀가 생길 수 있습니다.

다섯 번째 실수는 같은 노드를 여러 heap에 넣는 것입니다. 한 노드는 한 heap에만 속해야 합니다. 이미 어떤 heap에 들어간 노드를 다시 다른 heap에 넣으면 구조가 깨집니다.

## 15. 문제를 볼 때 체크할 조건

1. 두 우선순위 큐를 합치는 연산이 자주 나오는가?
2. 그룹이나 컴포넌트가 병합되며 각 그룹의 최솟값/최댓값을 계속 봐야 하는가?
3. 일반 `priority_queue`로 원소를 하나씩 옮기면 너무 느리거나 코드가 복잡한가?
4. heap의 중간 원소 삭제보다 root 조회/삭제와 meld가 핵심인가?
5. pointer ownership과 메모리 관리까지 감당할 가치가 있는가?

이 조건에 맞으면 Meldable Heap을 고려합니다. 단순히 하나의 우선순위 큐만 쓰는 문제라면 표준 `priority_queue`가 더 안전하고 빠른 선택입니다.
