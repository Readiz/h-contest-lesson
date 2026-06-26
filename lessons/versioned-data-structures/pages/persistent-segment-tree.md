# Persistent Segment Tree

Persistent Segment Tree는 업데이트 뒤의 예전 버전을 버리지 않고, 각 버전의 root를 보존하는 Segment Tree입니다. 한 번의 점 업데이트에서 바뀌는 노드는 root에서 leaf까지 `O(log N)`개뿐이므로, 나머지 노드는 이전 버전과 공유할 수 있습니다.

이 레슨은 "시간이 흐른 배열"을 여러 개 들고 있는 관점으로 Persistent Segment Tree를 봅니다.

1. 업데이트 경로만 새 노드로 복사한다.
2. 각 버전의 root를 저장해 과거 배열에 질의한다.
3. prefix 버전 차이로 k번째 수 같은 order statistic 질의를 처리한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Segment Tree, 좌표 압축, prefix sum 감각
- 함께 보면 좋은 레슨: Segment Tree, 좌표 압축, 오프라인 쿼리
- 다음에 볼 레슨: wavelet tree, persistent lazy tree, rollback data structure

## 1. 언제 쓰는가

Persistent Segment Tree는 같은 배열의 여러 시점을 비교해야 할 때 강합니다.

| 문제 신호 | Persistent Segment Tree 관점 |
| --- | --- |
| 업데이트가 여러 번 있고 과거 버전에 질의한다 | 버전별 root 저장 |
| 구간 `[l, r]`에서 k번째 작은 값을 묻는다 | prefix root `r`과 `l - 1`의 차이 |
| rollback 없이 분기된 상태를 관리한다 | 공유 노드로 여러 root 유지 |
| 오프라인으로 값 빈도를 누적한다 | 값 좌표 위의 누적 Segment Tree |

모든 버전을 배열 전체로 복사하면 업데이트 한 번에 `O(N)` 메모리가 듭니다. Persistent Segment Tree는 변경 경로만 복사하므로 업데이트 한 번에 `O(log N)` 노드만 추가합니다.

## 2. Path copying

점 업데이트로 index `pos`의 값을 바꾼다고 합시다. Segment Tree에서 `pos`를 포함하는 노드만 값이 달라집니다.

```text
old root
  left subtree  공유 가능
  right child   새 노드
       ...
       leaf(pos) 새 노드
```

새 버전 root는 새로 만든 root를 가리키고, 바뀌지 않은 child pointer는 이전 버전의 노드를 그대로 가리킵니다. 그래서 각 노드는 왼쪽 child, 오른쪽 child, 구간 값을 저장합니다.

## 3. 기본 구현

아래 코드는 점 업데이트와 구간 합 질의를 지원하는 Persistent Segment Tree입니다. `roots[v]`가 버전 `v`의 root node index입니다.

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

## 4. 버전 간 차이

빈도 배열 위에 persistent tree를 만들면 prefix 버전 차이를 이용할 수 있습니다.

```text
root[i] = a[1..i]의 값 빈도
구간 [l, r]의 값 빈도 = root[r] - root[l - 1]
```

각 node에는 해당 값 범위에 들어온 원소 수를 저장합니다. 어떤 값 범위의 개수는 두 root의 node sum 차이로 얻습니다.

이 방식은 "구간 안에서 k번째 작은 값"을 처리하는 대표 패턴입니다. 값들을 좌표 압축한 뒤, 각 prefix root에 `a[i]`의 압축 index를 1 증가시킵니다.

## 5. k번째 작은 값 질의

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

위 구현은 `tree[0]`을 null node로 씁니다. null node의 child와 count가 모두 0이기 때문에, 아직 만들어지지 않은 범위도 안전하게 차이를 계산할 수 있습니다.

## 6. 좌표 압축

k번째 수 질의에서는 tree의 index가 실제 값이 아니라 압축된 값입니다.

1. 모든 값을 모아 정렬하고 중복을 제거한다.
2. 각 `a[i]`를 압축 index로 바꾼다.
3. query 결과로 나온 압축 index를 원래 값 배열에서 복원한다.

값 범위가 `10^9`여도 서로 다른 값이 `N`개라면 tree 범위는 `1..N`이면 됩니다. 압축 없이 실제 값 범위로 tree를 만들면 메모리가 터집니다.

## 7. 시간과 메모리

| 작업 | 시간 | 추가 메모리 |
| --- | ---: | ---: |
| 버전 하나 추가 | `O(log N)` | `O(log N)` node |
| 버전 하나의 구간 합 질의 | `O(log N)` | 없음 |
| prefix 차이 k번째 값 | `O(log N)` | 없음 |
| 전체 `M`번 업데이트 | `O(M log N)` | `O(M log N)` node |

메모리는 node 개수로 계산합니다. `N = 200000`, 업데이트 `M = 200000`이면 대략 `M * log2(N)` 수준의 노드가 생깁니다. 각 node가 `int left, int right, long long sum`이면 수십 MB 이상이 될 수 있으므로 제한을 먼저 계산해야 합니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| old node를 직접 수정 | 과거 버전이 같이 바뀜 | update에서 반드시 clone |
| root 배열을 덮어씀 | 버전 질의 불가 | 새 root를 별도 저장 |
| 좌표 압축 복원 누락 | 압축 index를 답으로 출력 | result index를 original value로 변환 |
| null node 처리 누락 | k번째 질의에서 범위 밖 접근 | `tree[0]`을 0 node로 유지 |
| k가 구간 원소 수보다 큼 | 잘못된 leaf 도달 | 질의 전 count 확인 |
| 노드 수 메모리 계산 누락 | 메모리 초과 | `updates * logN * sizeof(Node)` 추정 |

## 9. 문제를 볼 때 체크할 조건

1. 같은 자료구조의 과거 상태를 다시 물어보는가?
2. 업데이트가 점 업데이트인가, 구간 업데이트인가?
3. 버전을 선형 prefix로 만들 수 있는가?
4. 구간 `[l, r]` 질의를 prefix 차이로 바꿀 수 있는가?
5. 값 범위가 커서 좌표 압축이 필요한가?
6. 생성될 node 수가 메모리 제한 안에 들어오는가?

Persistent Segment Tree는 "변경된 경로만 복사한다"는 한 문장으로 이해할 수 있습니다. root를 버전의 이름표로 보고, root 두 개의 차이가 구간 정보를 만든다는 감각을 잡으면 k번째 수 질의까지 자연스럽게 이어집니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 버전별 구간 합 `/practice/...` 문제 필요 | path copying과 root 저장 구현 | persistent root |
| 표준 | TODO: 구간 k번째 수 `/practice/...` 문제 필요 | prefix root 차이와 좌표 압축 | kth query |
| 응용 | TODO: 과거 버전 분기 업데이트 `/practice/...` 문제 필요 | 특정 버전에서 새 버전 생성 | version tree |
| 함정 | TODO: 메모리 제한이 빡빡한 persistent tree `/practice/...` 문제 필요 | node 수와 값 타입 계산 | memory budget |
