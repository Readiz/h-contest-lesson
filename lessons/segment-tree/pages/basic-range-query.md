# Segment Tree: 기본 구간 질의

## 1. 구간을 반으로 나누는 트리

Segment Tree의 각 노드는 배열의 한 구간을 담당합니다.

```text
[0, 7]
├─ [0, 3]
│  ├─ [0, 1]
│  └─ [2, 3]
└─ [4, 7]
   ├─ [4, 5]
   └─ [6, 7]
```

루트는 전체 구간을 담당하고, 자식은 구간을 절반씩 나누어 담당합니다. 길이가 1인 구간이 leaf입니다.

구간 합 Segment Tree라면 각 노드는 자신이 담당하는 구간의 합을 저장합니다.

```text
node [l, r] = a[l] + a[l + 1] + ... + a[r]
```

구간 최솟값이면 합 대신 최솟값을 저장하면 됩니다. 중요한 점은 두 자식의 값을 합쳐 부모 값을 만들 수 있어야 한다는 것입니다.

## 2. Top-down 재귀 구현

가장 설명하기 쉬운 구현은 재귀로 구간을 내려가는 top-down 방식입니다. `tree[node]`가 `[start, end]` 구간의 값을 저장한다고 합시다.

```cpp
void build(int node, int start, int end) {
    if (start == end) {
        tree[node] = a[start];
        return;
    }

    int mid = (start + end) / 2;
    build(node * 2, start, mid);
    build(node * 2 + 1, mid + 1, end);
    tree[node] = tree[node * 2] + tree[node * 2 + 1];
}
```

`node * 2`는 왼쪽 자식, `node * 2 + 1`은 오른쪽 자식입니다. 구현을 단순하게 하기 위해 `tree` 배열 크기는 보통 `4 * n`으로 잡습니다.

## 3. 구간 질의

구간 `[left, right]`의 합을 구할 때는 현재 노드의 구간 `[start, end]`와의 관계를 봅니다.

| 관계 | 처리 |
| --- | --- |
| 겹치지 않는다 | 0을 반환 |
| 완전히 포함된다 | `tree[node]`를 반환 |
| 일부만 겹친다 | 두 자식으로 내려가서 합친다 |

```cpp
long long query(int node, int start, int end, int left, int right) {
    if (right < start || end < left) {
        return 0;
    }
    if (left <= start && end <= right) {
        return tree[node];
    }

    int mid = (start + end) / 2;
    long long leftSum = query(node * 2, start, mid, left, right);
    long long rightSum = query(node * 2 + 1, mid + 1, end, left, right);
    return leftSum + rightSum;
}
```

한 질의에서 내려가는 노드는 트리 높이마다 많아야 몇 개씩입니다. 그래서 시간 복잡도는 `O(log n)`입니다.

## 4. 점 업데이트

한 위치 `idx`의 값을 `newValue`로 바꿀 때는 leaf까지 내려간 뒤, 돌아오면서 지나온 노드 값을 다시 계산합니다.

```cpp
void update(int node, int start, int end, int idx, long long newValue) {
    if (start == end) {
        tree[node] = newValue;
        return;
    }

    int mid = (start + end) / 2;
    if (idx <= mid) {
        update(node * 2, start, mid, idx, newValue);
    } else {
        update(node * 2 + 1, mid + 1, end, idx, newValue);
    }

    tree[node] = tree[node * 2] + tree[node * 2 + 1];
}
```

변한 위치를 포함하는 노드만 고치면 되므로 점 업데이트도 `O(log n)`입니다.

## 5. Top-down 전체 구현

아래 구현은 0-indexed 배열에서 구간 합과 점 업데이트를 처리합니다.

아래 구현은 `values`가 비어 있지 않다고 가정합니다. 대회 문제에서는 보통 `n >= 1`이 입력 제한으로 주어지지만, 라이브러리처럼 재사용하려면 생성자뿐 아니라 `query`, `update`에서도 빈 배열 처리를 따로 넣어야 합니다.

```cpp
#include <vector>
using namespace std;

struct SegmentTree {
    int n;
    vector<long long> tree;

    SegmentTree(const vector<long long>& values) {
        n = (int)values.size();
        tree.assign(4 * n, 0);
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

    long long query(int left, int right) {
        return query(1, 0, n - 1, left, right);
    }

    long long query(int node, int start, int end, int left, int right) {
        if (right < start || end < left) return 0;
        if (left <= start && end <= right) return tree[node];

        int mid = (start + end) / 2;
        return query(node * 2, start, mid, left, right)
            + query(node * 2 + 1, mid + 1, end, left, right);
    }

    void update(int idx, long long newValue) {
        update(1, 0, n - 1, idx, newValue);
    }

    void update(int node, int start, int end, int idx, long long newValue) {
        if (start == end) {
            tree[node] = newValue;
            return;
        }

        int mid = (start + end) / 2;
        if (idx <= mid) {
            update(node * 2, start, mid, idx, newValue);
        } else {
            update(node * 2 + 1, mid + 1, end, idx, newValue);
        }
        tree[node] = tree[node * 2] + tree[node * 2 + 1];
    }
};
```

입력 구간이 1-indexed라면 `query(l - 1, r - 1)`처럼 바꿔 호출합니다.
