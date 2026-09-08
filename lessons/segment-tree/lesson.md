# Segment Tree

배열 값이 바뀌는 동안 구간 합·최솟값·최댓값을 묻는다면, 구간을 반으로 나눈 트리에 결과를 저장할 수 있습니다. 바뀐 위치를 포함하는 구간만 고쳐 점 갱신과 구간 질의를 `O(log n)`에 처리합니다.


## 구간을 반으로 나누는 트리

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

## Top-down 재귀 구현

가장 설명하기 쉬운 구현은 재귀로 구간을 내려가는 top-down 방식입니다. `tree[node]`가 `[start, end]` 구간의 값을 저장한다고 합시다.

`node * 2`는 왼쪽 자식, `node * 2 + 1`은 오른쪽 자식입니다. 구현을 단순하게 하기 위해 `tree` 배열 크기는 보통 `4 * n`으로 잡습니다.

## 구간 질의

구간 `[left, right]`의 합을 구할 때는 현재 노드의 구간 `[start, end]`와의 관계를 봅니다.

| 관계 | 처리 |
| --- | --- |
| 겹치지 않는다 | 0을 반환 |
| 완전히 포함된다 | `tree[node]`를 반환 |
| 일부만 겹친다 | 두 자식으로 내려가서 합친다 |

한 질의에서 내려가는 노드는 트리 높이마다 많아야 몇 개씩입니다. 그래서 시간 복잡도는 `O(log n)`입니다.

## 점 업데이트

한 위치 `idx`의 값을 `newValue`로 바꿀 때는 leaf까지 내려간 뒤, 돌아오면서 지나온 노드 값을 다시 계산합니다.

변한 위치를 포함하는 노드만 고치면 되므로 점 업데이트도 `O(log n)`입니다.

## Top-down 전체 구현

아래 구현은 비어 있지 않은 0-indexed 배열에서 구간 합과 점 업데이트를 처리합니다. 질의는 `0 <= l <= r < n`, 갱신 위치는 `0..n-1` 범위입니다.

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

## 합 말고 다른 연산일 때

Segment Tree에서 바뀌는 것은 세 가지입니다.

1. 두 자식 값을 합치는 `merge`
2. 구간 밖을 만났을 때 돌려줄 항등원
3. 업데이트 뒤 노드 값을 다시 계산하는 방법

| 질의 | merge | 항등원 |
| --- | --- | --- |
| 구간 합 | `a + b` | `0` |
| 구간 최솟값 | `min(a, b)` | 충분히 큰 `INF` |
| 구간 최댓값 | `max(a, b)` | 충분히 작은 `-INF` |
| 구간 gcd | `gcd(a, b)` | `0` |

이처럼 결합 법칙이 성립하고 항등원이 있는 연산을 monoid로 볼 수 있습니다. Segment Tree는 사실상 "구간을 나눠 monoid 값을 합치는 자료구조"입니다.

## Lazy Propagation

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

아래 구현에서 `lazy[node]`는 현재 노드의 합에도 아직 반영하지 않은 증가량입니다. `push`가 합을 갱신한 뒤 그 증가량을 자식 lazy로 넘깁니다.

## lazy 내려보내기

재귀로 노드를 방문할 때 먼저 `push`를 호출해 현재 노드에 밀려 있는 값을 처리합니다.

이 함수는 세 가지 일을 합니다.

1. 현재 노드의 합에 밀린 증가량을 반영합니다.
2. leaf가 아니면 자식 lazy에 증가량을 넘깁니다.
3. 현재 노드의 lazy 값을 비웁니다.

## lazy 구간 업데이트

업데이트 구간이 현재 노드를 완전히 덮으면, 그 노드의 lazy만 기록하고 바로 처리합니다. 일부만 겹치면 자식으로 내려갑니다.

완전히 포함되는 노드는 자식까지 내려가지 않습니다. 그래서 구간 업데이트도 `O(log n)`에 가까운 비용으로 처리됩니다.

## lazy 구간 질의

질의도 마찬가지로 방문한 노드에서 `push`를 먼저 호출합니다.

`push`를 빼먹으면 부모에는 업데이트가 반영되어 있는데 자식 값은 오래된 상태로 남을 수 있습니다.

## Lazy 전체 구현

아래 구현은 0-indexed 배열에서 구간 덧셈과 구간 합 질의를 처리합니다. 합에는 `구간 길이 × 증가량`이 누적되므로 노드 값과 lazy는 `long long`으로 저장합니다.

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

## 업데이트 순서가 달라지면

lazy propagation에서는 lazy 값끼리 어떻게 합쳐지는지도 따로 정해야 합니다.

| 업데이트 | 노드 값 변화 | lazy 합성 |
| --- | --- | --- |
| 구간 덧셈 + 구간 합 | `tree += value * length` | 기존 lazy에 더함 |
| 구간 덧셈 + 구간 최솟값 | `tree += value` | 기존 lazy에 더함 |
| 구간 대입 + 구간 합 | `tree = value * length` | 이전 lazy를 새 대입 값으로 덮음 |
| 구간 대입 + 구간 최솟값 | `tree = value` | 이전 lazy를 새 대입 값으로 덮음 |

구간 덧셈과 구간 대입이 동시에 있으면 "대입 뒤 덧셈"과 "덧셈 뒤 대입"의 순서가 결과를 바꿉니다. 이 경우 lazy 상태를 단일 숫자로 두기보다 `hasAssign`, `assignValue`, `addValue`처럼 의미를 분리해 합성 규칙을 명시하는 편이 안전합니다.

빌드는 `O(n)`, 구간 덧셈과 합 질의는 `O(log n)`, 메모리는 `O(n)`입니다. 위 구현은 생성자에 전달한 비어 있지 않은 배열에서 시작합니다.

## 구간 갱신 실습

[창고 구역 장부](/practice/SHELFLOG)에 구간 덧셈·구간 합 구현을 적용할 수 있습니다. 전체 구간을 갱신한 직후 일부 구간을 조회하면 lazy 전달이 맞는지 확인하기 좋습니다.
