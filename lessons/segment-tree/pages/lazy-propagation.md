# Segment Tree: Lazy Propagation

## 7. Lazy Propagation

점 하나가 아니라 구간 전체에 값을 더해야 한다면 어떻게 해야 할까요?

```text
1. 구간 [l, r]의 모든 값에 x를 더한다.
2. 구간 [l, r]의 합을 구한다.
```

구간에 포함된 원소를 하나씩 업데이트하면 한 번에 `O(k log n)`이 걸립니다. Lazy Propagation은 "이 구간 전체에 더해야 할 값이 있다"는 표시를 노드에 남겨 두고, 자식으로 내려갈 때만 밀어 넣는 방식입니다.

구간 합에서 노드 `[start, end]` 전체에 `value`를 더하면 그 노드의 합은 다음만큼 증가합니다.

```text
(end - start + 1) * value
```

그리고 자식에게는 아직 내려보내지 않은 증가량을 `lazy[node]`에 저장합니다.

## 8. lazy 내려보내기

재귀로 노드를 방문할 때 먼저 `push`를 호출해 현재 노드에 밀려 있는 값을 처리합니다.

```cpp
void push(int node, int start, int end) {
    if (lazy[node] == 0) return;

    tree[node] += (end - start + 1) * lazy[node];

    if (start != end) {
        lazy[node * 2] += lazy[node];
        lazy[node * 2 + 1] += lazy[node];
    }

    lazy[node] = 0;
}
```

이 함수는 세 가지 일을 합니다.

1. 현재 노드의 합에 밀린 증가량을 반영합니다.
2. leaf가 아니면 자식 lazy에 증가량을 넘깁니다.
3. 현재 노드의 lazy 값을 비웁니다.

## 9. lazy 구간 업데이트

업데이트 구간이 현재 노드를 완전히 덮으면, 그 노드의 lazy만 기록하고 바로 처리합니다. 일부만 겹치면 자식으로 내려갑니다.

```cpp
void rangeAdd(int node, int start, int end, int left, int right, long long value) {
    push(node, start, end);

    if (right < start || end < left) {
        return;
    }
    if (left <= start && end <= right) {
        lazy[node] += value;
        push(node, start, end);
        return;
    }

    int mid = (start + end) / 2;
    rangeAdd(node * 2, start, mid, left, right, value);
    rangeAdd(node * 2 + 1, mid + 1, end, left, right, value);
    tree[node] = tree[node * 2] + tree[node * 2 + 1];
}
```

완전히 포함되는 노드는 자식까지 내려가지 않습니다. 그래서 구간 업데이트도 `O(log n)`에 가까운 비용으로 처리됩니다.

## 10. lazy 구간 질의

질의도 마찬가지로 방문한 노드에서 `push`를 먼저 호출합니다.

```cpp
long long query(int node, int start, int end, int left, int right) {
    push(node, start, end);

    if (right < start || end < left) {
        return 0;
    }
    if (left <= start && end <= right) {
        return tree[node];
    }

    int mid = (start + end) / 2;
    return query(node * 2, start, mid, left, right)
        + query(node * 2 + 1, mid + 1, end, left, right);
}
```

`push`를 빼먹으면 부모에는 업데이트가 반영되어 있는데 자식 값은 오래된 상태로 남을 수 있습니다. lazy Segment Tree의 버그는 대부분 "언제 push해야 하는가"에서 나옵니다.

## 11. Lazy 전체 구현

아래 구현은 0-indexed 배열에서 구간 덧셈과 구간 합 질의를 처리합니다.

```cpp
#include <vector>
using namespace std;

struct LazySegmentTree {
    int n;
    vector<long long> tree;
    vector<long long> lazy;

    LazySegmentTree(const vector<long long>& values) {
        n = (int)values.size();
        tree.assign(4 * n, 0);
        lazy.assign(4 * n, 0);
        build(1, 0, n - 1, values);
    }

    void build(int node, int start, int end, const vector<long long>& values) {
        if (start == end) {
            tree[node] = values[start];
            return;
        }
        int mid = (start + end) / 2;
        build(node * 2, start, mid, values);
        build(node * 2 + 1, mid + 1, end, values);
        tree[node] = tree[node * 2] + tree[node * 2 + 1];
    }

    void push(int node, int start, int end) {
        if (lazy[node] == 0) return;

        tree[node] += (end - start + 1) * lazy[node];
        if (start != end) {
            lazy[node * 2] += lazy[node];
            lazy[node * 2 + 1] += lazy[node];
        }
        lazy[node] = 0;
    }

    void rangeAdd(int left, int right, long long value) {
        rangeAdd(1, 0, n - 1, left, right, value);
    }

    void rangeAdd(int node, int start, int end, int left, int right, long long value) {
        push(node, start, end);

        if (right < start || end < left) return;
        if (left <= start && end <= right) {
            lazy[node] += value;
            push(node, start, end);
            return;
        }

        int mid = (start + end) / 2;
        rangeAdd(node * 2, start, mid, left, right, value);
        rangeAdd(node * 2 + 1, mid + 1, end, left, right, value);
        tree[node] = tree[node * 2] + tree[node * 2 + 1];
    }

    long long query(int left, int right) {
        return query(1, 0, n - 1, left, right);
    }

    long long query(int node, int start, int end, int left, int right) {
        push(node, start, end);

        if (right < start || end < left) return 0;
        if (left <= start && end <= right) return tree[node];

        int mid = (start + end) / 2;
        return query(node * 2, start, mid, left, right)
            + query(node * 2 + 1, mid + 1, end, left, right);
    }
};
```

구간 덧셈 + 구간 최솟값이라면 `tree[node]`는 합 대신 최솟값을 저장하고, 전체 구간에 값을 더할 때 `tree[node] += value`만 하면 됩니다. 반면 구간 대입처럼 기존 lazy와 새 lazy가 덮어쓰기 관계를 갖는 문제는 lazy 값을 합치는 규칙을 따로 설계해야 합니다.
