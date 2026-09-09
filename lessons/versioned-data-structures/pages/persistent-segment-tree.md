# Persistent Segment Tree

Persistent Segment Tree는 업데이트 뒤의 예전 버전을 버리지 않고, 각 버전의 root를 보존하는 Segment Tree입니다. 한 번의 점 업데이트에서 바뀌는 노드는 root에서 leaf까지 `O(log N)`개뿐이므로, 나머지 노드는 이전 버전과 공유할 수 있습니다.

## 언제 쓰는가

Persistent Segment Tree는 같은 배열의 여러 시점을 비교해야 할 때 강합니다.

| 문제 신호 | Persistent Segment Tree 관점 |
| --- | --- |
| 업데이트가 여러 번 있고 과거 버전에 질의한다 | 버전별 root 저장 |
| 구간 `[l, r]`에서 k번째 작은 값을 묻는다 | prefix root `r`과 `l - 1`의 차이 |
| rollback 없이 분기된 상태를 관리한다 | 공유 노드로 여러 root 유지 |
| 오프라인으로 값 빈도를 누적한다 | 값 좌표 위의 누적 Segment Tree |

모든 버전을 배열 전체로 복사하면 업데이트 한 번에 `O(N)` 메모리가 듭니다. Persistent Segment Tree는 변경 경로만 복사하므로 업데이트 한 번에 `O(log N)` 노드만 추가합니다.

## Path copying

점 업데이트로 index `pos`의 값을 바꾼다고 합시다. Segment Tree에서 `pos`를 포함하는 노드만 값이 달라집니다.

```text
old root
  left subtree  공유 가능
  right child   새 노드
       ...
       leaf(pos) 새 노드
```

새 버전 root는 새로 만든 root를 가리키고, 바뀌지 않은 child pointer는 이전 버전의 노드를 그대로 가리킵니다. 그래서 각 노드는 왼쪽 child, 오른쪽 child, 구간 값을 저장합니다.

## 기본 구현

`n >= 1`, 위치는 `1..n`, 질의는 `1 <= left <= right <= n`이며 버전 번호는 이미 생성된 버전입니다. 아래 코드는 점 업데이트와 구간 합 질의를 지원하는 Persistent Segment Tree입니다. `roots[v]`가 버전 `v`의 root node index입니다.

```cpp compile-check
#include <vector>
using namespace std;

struct PersistentSegmentTree {
    struct Node {
        int left = 0;
        int right = 0;
        long long sum = 0;
    };

    int n;
    vector<Node> tree;
    vector<int> roots;

    explicit PersistentSegmentTree(int n) : n(n) {
        tree.push_back(Node{});
        roots.push_back(build(1, n));
    }

    int build(int start, int end) {
        int node = newNode();
        if (start == end) {
            return node;
        }
        int mid = (start + end) / 2;
        tree[node].left = build(start, mid);
        tree[node].right = build(mid + 1, end);
        return node;
    }

    int newNode() {
        tree.push_back(Node{});
        return (int)tree.size() - 1;
    }

    int cloneNode(int oldNode) {
        tree.push_back(tree[oldNode]);
        return (int)tree.size() - 1;
    }

    int update(int oldNode, int start, int end, int pos, long long delta) {
        int node = cloneNode(oldNode);
        if (start == end) {
            tree[node].sum += delta;
            return node;
        }
        int mid = (start + end) / 2;
        if (pos <= mid) {
            tree[node].left = update(tree[oldNode].left, start, mid, pos, delta);
        } else {
            tree[node].right = update(tree[oldNode].right, mid + 1, end, pos, delta);
        }
        tree[node].sum = tree[tree[node].left].sum + tree[tree[node].right].sum;
        return node;
    }

    int addVersion(int baseVersion, int pos, long long delta) {
        int root = update(roots[baseVersion], 1, n, pos, delta);
        roots.push_back(root);
        return (int)roots.size() - 1;
    }

    long long query(int node, int start, int end, int left, int right) const {
        if (right < start || end < left) {
            return 0;
        }
        if (left <= start && end <= right) {
            return tree[node].sum;
        }
        int mid = (start + end) / 2;
        return query(tree[node].left, start, mid, left, right)
             + query(tree[node].right, mid + 1, end, left, right);
    }

    long long rangeSum(int version, int left, int right) const {
        return query(roots[version], 1, n, left, right);
    }
};
```

초기 배열이 있다면 빈 tree를 만든 뒤 각 위치를 업데이트해 첫 버전을 만들거나, build 단계에서 값을 채워 넣으면 됩니다. 중요한 것은 update가 old node를 직접 바꾸지 않는다는 점입니다.

## 버전 간 차이

빈도 배열 위에 persistent tree를 만들면 prefix 버전 차이를 이용할 수 있습니다.

```text
root[i] = a[1..i]의 값 빈도
구간 [l, r]의 값 빈도 = root[r] - root[l - 1]
```

각 node에는 해당 값 범위에 들어온 원소 수를 저장합니다. 어떤 값 범위의 개수는 두 root의 node sum 차이로 얻습니다.

이 방식은 "구간 안에서 k번째 작은 값"을 처리하는 대표 패턴입니다. 값들을 좌표 압축한 뒤, 각 prefix root에 `a[i]`의 압축 index를 1 증가시킵니다.

## k번째 작은 값 질의

두 prefix root `rightRoot`, `leftRoot`가 있을 때 왼쪽 child에 들어 있는 원소 수 차이를 보면 k번째 값이 왼쪽 절반에 있는지 오른쪽 절반에 있는지 알 수 있습니다.

```cpp compile-check
#include <vector>
using namespace std;

struct PersistentKthTree {
    struct Node {
        int left = 0;
        int right = 0;
        int count = 0;
    };

    int valueCount;
    vector<Node> tree{{}};
    vector<int> roots{0};

    explicit PersistentKthTree(int valueCount) : valueCount(valueCount) {}

    int cloneNode(int oldNode) {
        tree.push_back(tree[oldNode]);
        return (int)tree.size() - 1;
    }

    int update(int oldNode, int start, int end, int pos) {
        int node = cloneNode(oldNode);
        tree[node].count += 1;
        if (start == end) {
            return node;
        }
        int mid = (start + end) / 2;
        if (pos <= mid) {
            tree[node].left = update(tree[oldNode].left, start, mid, pos);
        } else {
            tree[node].right = update(tree[oldNode].right, mid + 1, end, pos);
        }
        return node;
    }

    void appendValue(int compressedValue) {
        roots.push_back(update(roots.back(), 1, valueCount, compressedValue));
    }

    int kth(int leftRoot, int rightRoot, int start, int end, int k) const {
        if (start == end) {
            return start;
        }
        int mid = (start + end) / 2;
        int leftCount = tree[tree[rightRoot].left].count - tree[tree[leftRoot].left].count;
        if (k <= leftCount) {
            return kth(tree[leftRoot].left, tree[rightRoot].left, start, mid, k);
        }
        return kth(tree[leftRoot].right, tree[rightRoot].right, mid + 1, end, k - leftCount);
    }

    int kthInRange(int leftIndex, int rightIndex, int k) const {
        return kth(roots[leftIndex - 1], roots[rightIndex], 1, valueCount, k);
    }
};
```

`valueCount >= 1`, 압축값은 `1..valueCount`, 질의는 `1 <= leftIndex <= rightIndex <= 삽입 수`, `1 <= k <= rightIndex-leftIndex+1`입니다. 위 구현은 `tree[0]`을 null node로 씁니다. null node의 child와 count가 모두 0이기 때문에, 아직 만들어지지 않은 범위도 안전하게 차이를 계산할 수 있습니다.

## 좌표 압축

k번째 수 질의에서는 tree의 index가 실제 값이 아니라 압축된 값입니다.

1. 모든 값을 모아 정렬하고 중복을 제거한다.
2. 각 `a[i]`를 압축 index로 바꾼다.
3. query 결과로 나온 압축 index를 원래 값 배열에서 복원한다.

값 범위가 `10^9`여도 서로 다른 값이 `N`개라면 tree 범위는 `1..N`이면 됩니다. 전체 값 범위를 미리 build하면 메모리가 커집니다. 위 kth 구현은 null 노드에서 필요한 경로만 생성하므로 넓은 범위도 처리할 수 있지만, 압축하면 높이와 노드 수를 줄일 수 있습니다.

## 시간과 메모리

| 작업 | 시간 | 추가 메모리 |
| --- | ---: | ---: |
| 버전 하나 추가 | `O(log N)` | `O(log N)` node |
| 버전 하나의 구간 합 질의 | `O(log N)` | 없음 |
| prefix 차이 k번째 값 | `O(log N)` | 없음 |
| 전체 build + `M`번 업데이트 | `O(N + M log N)` | `O(N + M log N)` node |

메모리는 node 개수로 계산합니다. `N = 200000`, 업데이트 `M = 200000`이면 대략 `M * log2(N)` 수준의 노드가 생깁니다. 각 node가 `int left, int right, long long sum`이면 수십 MB 이상이 될 수 있으므로 제한을 먼저 계산해야 합니다.

## Trace: prefix root 차이

정적 배열이 아래와 같다고 하겠습니다.

```text
A = [4, 1, 4, 2]
```

값을 압축하면 `1 -> 1`, `2 -> 2`, `4 -> 3`입니다. `root[i]`는 prefix `A[1..i]`의 빈도 persistent segment tree입니다.

| root | 담긴 값 | compressed frequency |
| --- | --- | --- |
| `root[0]` | empty | `[0, 0, 0]` |
| `root[1]` | `4` | `[0, 0, 1]` |
| `root[2]` | `4, 1` | `[1, 0, 1]` |
| `root[3]` | `4, 1, 4` | `[1, 0, 2]` |
| `root[4]` | `4, 1, 4, 2` | `[1, 1, 2]` |

query `[2, 4]`의 2번째 작은 값은 `root[4] - root[1]`로 봅니다.

```text
root[4] - root[1] = [1, 1, 1]
```

왼쪽 절반 `1, 2`에 2개가 있으므로 그쪽으로 내려갑니다. 그 안에서 `1`의 count는 1이고 `k=2`이므로 `2`로 이동합니다. 답은 원래 값 `2`입니다.

이 방식은 node를 직접 빼는 것이 아니라, 같은 구간을 가리키는 두 root의 count 차이를 내려가며 보는 것입니다. 그래서 old root를 수정하면 모든 query가 깨집니다.

## 로컬 연습: Range Kth with Prefix Roots

### 입력

정적 배열 `A`와 `Q`개의 구간 kth query가 주어집니다.

```text
N Q
A1 A2 ... AN
l1 r1 k1
...
lQ rQ kQ
```

`l`, `r`은 1-based inclusive입니다. 각 query는 `A[l..r]`에서 `k`번째로 작은 값을 출력합니다.

### 출력

각 query마다 답을 한 줄에 출력합니다.

### 제한

- `1 <= N, Q <= 200000`
- `-10^9 <= Ai <= 10^9`
- `1 <= l <= r <= N`
- `1 <= k <= r - l + 1`

### 예시

```text
5 3
5 1 4 2 3
2 5 2
1 3 3
3 5 1
```

```text
2
5
2
```

첫 query의 구간은 `[1, 4, 2, 3]`이고 정렬하면 `[1, 2, 3, 4]`라서 2번째 값은 `2`입니다.

### 풀이 기준

1. 모든 `Ai`를 좌표 압축한다.
2. `root[0]`은 빈 segment tree다.
3. `root[i] = update(root[i-1], compressed(Ai), +1)`로 prefix root를 만든다.
4. query `(l, r, k)`는 `kth(root[l-1], root[r], 1, valueCount, k)`로 답한다.
5. compressed index를 원래 값으로 복원한다.

`update`는 지나가는 node만 clone합니다. 범위 밖 child pointer는 old node를 그대로 공유합니다. 전체 node 수는 대략 `N * (log uniqueValues + 1)`이므로, `N=200000`이면 메모리 예산을 먼저 계산해야 합니다.

### kth 내려가기

각 node에서 왼쪽 count 차이를 봅니다.

```text
leftCount = count(leftChild(rootR)) - count(leftChild(rootLMinusOne))
if k <= leftCount:
    go left
else:
    k -= leftCount
    go right
```

leaf에 도착하면 그 leaf의 compressed index가 답입니다.

### Stress 검증

작은 입력에서는 query마다 slice를 복사해 정렬하는 baseline과 비교합니다.

```text
for seed in 1..1000:
    random array and valid kth queries
    answer_persistent = prefix root kth
    answer_naive = sorted(A[l..r])[k-1]
    assert answer_persistent == answer_naive
```

중복 값이 있는 배열을 반드시 포함합니다. 좌표 압축을 값의 등장 횟수가 아니라 distinct value 기준으로 해야 한다는 점을 확인하기 좋습니다.
