# Persistent Sequence Queries

Persistent Sequence Queries는 version별 배열, sequence, multiset에 대해 kth, count, range sum 같은 질의를 처리하는 자료구조 응용 레슨입니다. Persistent Queue and Stack이 root pointer로 version을 보존하는 가장 단순한 형태라면, 이 레슨은 persistent segment tree와 implicit sequence를 이용해 구간 질의까지 확장합니다.

이 레슨은 Persistent Queue and Stack, Persistent Segment Tree, Wavelet Tree 이후에 보는 자료구조 심화입니다.

1. version root가 어떤 sequence 상태를 대표하는지 명확히 둔다.
2. update가 point인지 range인지, query가 kth인지 sum인지 먼저 분리한다.
3. prefix version 차이는 static range kth 문제에서 강력한 모델이다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: segment tree, persistence, coordinate compression, kth order statistic
- 함께 보면 좋은 레슨: Persistent Segment Tree, Wavelet Tree, Persistent Queue and Stack
- 다음에 볼 레슨: persistent lazy structure, retroactive data structures, offline range query techniques

## 1. 문제 신호

| 문제 표현 | Persistent Sequence 관점 |
| --- | --- |
| `version v`의 배열 값 조회 | persistent array |
| update마다 새 version 생성 | path copying |
| 구간 `[l, r]`에서 k번째 작은 값 | prefix persistent segment tree |
| 과거 version의 range sum | persistent segment tree |
| sequence 중간 삽입/삭제 | persistent implicit treap 후보 |

모든 version이 독립 배열처럼 보이지만 실제로는 바뀐 경로만 새로 만들고 나머지 node를 공유합니다.

## 2. Version Root 모델

Persistent segment tree의 각 root는 하나의 version을 나타냅니다.

```text
root[0] = empty tree
root[1] = update(root[0], pos, +1)
root[2] = update(root[1], pos, +1)
```

기존 root는 수정하지 않습니다. update가 지나간 node만 복사하고, 지나가지 않은 child는 그대로 공유합니다.

## 3. Prefix Version으로 Range Query

정적 배열 `a[1..n]`에서 `[l, r]`의 k번째 작은 값을 묻는 전형적인 방식은 prefix root를 만듭니다.

```text
root[i] = a[1..i]의 frequency tree
range [l, r] frequency = root[r] - root[l-1]
```

왼쪽 child count 차이를 보면 k번째 값이 왼쪽에 있는지 오른쪽에 있는지 결정할 수 있습니다.

## 4. Kth Query 구현

아래 코드는 coordinate-compressed 값 범위에서 prefix persistent segment tree를 구성하고 range kth를 찾는 핵심입니다.

```cpp compile-check
#include <vector>
using namespace std;

struct PersistentKthTree {
    struct Node {
        int left = 0;
        int right = 0;
        int sum = 0;
    };

    vector<Node> tree;

    PersistentKthTree() {
        tree.push_back(Node{0, 0, 0});
    }

    int update(int node, int left, int right, int position) {
        int current = (int)tree.size();
        tree.push_back(tree[node]);
        tree[current].sum += 1;
        if (left == right) {
            return current;
        }
        int mid = (left + right) / 2;
        if (position <= mid) {
            tree[current].left = update(tree[node].left, left, mid, position);
        } else {
            tree[current].right = update(tree[node].right, mid + 1, right, position);
        }
        return current;
    }

    int kth(int leftRoot, int rightRoot, int left, int right, int k) const {
        if (left == right) {
            return left;
        }
        int mid = (left + right) / 2;
        int leftCount = tree[tree[rightRoot].left].sum - tree[tree[leftRoot].left].sum;
        if (k <= leftCount) {
            return kth(tree[leftRoot].left, tree[rightRoot].left, left, mid, k);
        }
        return kth(tree[leftRoot].right, tree[rightRoot].right, mid + 1, right, k - leftCount);
    }
};
```

`leftRoot`는 `root[l-1]`, `rightRoot`는 `root[r]`입니다. 반환값은 압축 좌표 index이므로 원래 값 배열로 되돌립니다.

## 5. Persistent Array와 Sequence

point assignment가 있는 versioned array는 segment tree leaf에 값을 저장하면 됩니다.

```text
set(version, index, value):
  root' = copy path root -> leaf(index)
  leaf value = value
```

중간 삽입/삭제가 있는 sequence는 index가 변하므로 단순 segment tree보다 implicit treap이 자연스럽습니다. 각 node에 subtree size를 저장하고 split/merge를 persistent하게 만듭니다.

## 6. Range Update가 있으면

range add, range assign 같은 lazy update도 persistent하게 만들 수 있지만 복잡도가 올라갑니다.

| 요구 | 구조 |
| --- | --- |
| point update + range query | persistent segment tree |
| static range kth | prefix persistent tree |
| range add + point query | persistent lazy tree 가능 |
| 중간 삽입/삭제 sequence | persistent implicit treap |
| 과거 operation 삽입/삭제 | retroactive structure |

문제에서 진짜 range update persistence가 필요한지, offline 변환으로 단순화할 수 있는지 먼저 봅니다.

## 7. 작은 예시

```text
a = [5, 1, 4, 2]
압축 값 = [1, 2, 4, 5]

root[1]: {5}
root[2]: {1, 5}
root[3]: {1, 4, 5}
root[4]: {1, 2, 4, 5}

query [2, 4], k=2:
root[4] - root[1] = {1, 2, 4}
2번째 작은 값 = 2
```

prefix root 차이는 원래 배열의 구간 빈도만 남깁니다.

## 8. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| point update version 생성 | `O(log V)` | update당 `O(log V)` |
| range kth query | `O(log V)` | 추가 없음 |
| persistent array get | `O(log N)` | 추가 없음 |
| persistent implicit treap split/merge | expected `O(log N)` | update당 `O(log N)` |

`V`는 압축된 값 개수입니다. node 수는 대략 `(update 수) * log V`이므로 메모리 제한을 먼저 계산해야 합니다.

## 9. 자주 하는 실수

1. 기존 node를 직접 수정해 과거 version을 깨뜨린다.
2. `root[r] - root[l-1]`에서 왼쪽 root를 잘못 잡는다.
3. kth가 1-index인지 0-index인지 섞는다.
4. 압축 좌표 index를 원래 값으로 되돌리지 않는다.
5. range update까지 path copying만으로 충분하다고 착각한다.

## 10. 문제를 볼 때 체크할 조건

- version이 update마다 새로 생기는가?
- query가 prefix 차이로 표현되는가?
- 값 범위 압축이 가능한가?
- 중간 삽입/삭제로 index가 바뀌는가?
- node 수 메모리가 제한 안에 들어가는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: persistent array `/practice/...` 문제 필요 | point update version 보존 | path copying |
| 표준 | TODO: persistent kth query `/practice/...` 문제 필요 | prefix root 차이 | order statistic |
| 응용 | TODO: persistent sequence `/practice/...` 문제 필요 | split/merge로 중간 삽입 처리 | implicit treap |
| 함정 | TODO: persistent lazy query `/practice/...` 문제 필요 | lazy tag 복사 조건 | range update |

