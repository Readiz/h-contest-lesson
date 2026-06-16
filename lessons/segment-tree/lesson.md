# Segment Tree

Segment Tree는 배열을 여러 구간으로 나누어 저장하고, 구간 합/최솟값/최댓값 같은 질의를 빠르게 처리하는 자료구조입니다. 한국어로는 보통 **세그먼트 트리**라고 부릅니다.

대표적인 문제는 다음과 같습니다.

```text
배열 값이 바뀔 수 있다.
중간중간 구간 [l, r]의 합, 최솟값, 최댓값을 빠르게 물어본다.
```

배열을 매번 전부 훑으면 질의 하나가 `O(n)`입니다. Segment Tree를 쓰면 점 업데이트와 구간 질의를 모두 `O(log n)`에 처리할 수 있습니다.

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

## 6. Bottom-up 반복 구현

Segment Tree는 재귀 없이 bottom-up으로도 구현할 수 있습니다. 이 방식은 leaf를 배열 뒤쪽에 놓고, 부모를 앞쪽에 채웁니다.

```text
tree[n + i] = a[i]
tree[i] = tree[i * 2] + tree[i * 2 + 1]
```

구현이 짧고 재귀 호출 비용이 없어 실전에서 자주 씁니다.

```cpp
#include <vector>
using namespace std;

struct IterSegmentTree {
    int n;
    vector<long long> tree;

    IterSegmentTree(const vector<long long>& values) {
        n = (int)values.size();
        tree.assign(2 * n, 0);

        for (int i = 0; i < n; ++i) {
            tree[n + i] = values[i];
        }
        for (int i = n - 1; i >= 1; --i) {
            tree[i] = tree[i * 2] + tree[i * 2 + 1];
        }
    }

    void update(int idx, long long newValue) {
        int pos = idx + n;
        tree[pos] = newValue;

        while (pos > 1) {
            pos /= 2;
            tree[pos] = tree[pos * 2] + tree[pos * 2 + 1];
        }
    }

    long long query(int left, int right) {
        long long result = 0;
        left += n;
        right += n;

        while (left <= right) {
            if (left % 2 == 1) {
                result += tree[left];
                left++;
            }
            if (right % 2 == 0) {
                result += tree[right];
                right--;
            }
            left /= 2;
            right /= 2;
        }
        return result;
    }
};
```

이 구현의 `query(left, right)`는 양 끝을 안쪽으로 좁혀 가며, 현재 구간을 정확히 덮는 노드만 더합니다. `left`가 오른쪽 자식이면 그 노드는 바로 답에 넣고 다음 구간으로 넘어갑니다. `right`가 왼쪽 자식일 때도 같은 방식입니다.

bottom-up 구현은 점 업데이트와 구간 질의까지는 깔끔합니다. 하지만 lazy propagation이 필요한 구간 업데이트는 top-down 재귀 구현이 더 이해하기 쉽습니다.

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

## 12. Bottom-up과 top-down 중 무엇을 쓸까

| 상황 | 추천 |
| --- | --- |
| 점 업데이트 + 구간 합/최솟값 | bottom-up 반복 구현 |
| 설명과 디버깅이 중요하다 | top-down 재귀 구현 |
| lazy 구간 업데이트가 필요하다 | top-down 재귀 구현 |
| 재귀 제한이나 함수 호출 비용이 부담된다 | bottom-up 반복 구현 |

둘 다 같은 Segment Tree입니다. 차이는 노드를 어떻게 번호 붙이고 순회하느냐입니다. 처음 배울 때는 top-down으로 구간 관계를 이해하고, 익숙해진 뒤 bottom-up 구현을 쓰면 좋습니다.

## 13. 시간 복잡도

| 작업 | 시간 |
| --- | --- |
| 빌드 | `O(n)` |
| 점 업데이트 | `O(log n)` |
| 구간 질의 | `O(log n)` |
| lazy 구간 업데이트 | `O(log n)` |
| 메모리 | `O(n)` |

`4 * n` 재귀 구현은 실제 메모리를 네 배 가까이 잡지만 복잡도 표기상은 `O(n)`입니다. bottom-up 구현은 보통 `2 * n` 정도를 사용합니다.

Segment Tree는 구간을 작은 조각으로 분해해 필요한 조각만 합치는 도구입니다. 저장 값의 결합 규칙과 lazy를 합치는 규칙만 정확히 정하면 합, 최솟값, 최댓값, gcd 같은 많은 구간 문제에 적용할 수 있습니다.
