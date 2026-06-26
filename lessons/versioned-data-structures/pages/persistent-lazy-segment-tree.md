# Persistent Lazy Segment Tree

Persistent Lazy Segment Tree는 구간 업데이트와 구간 질의를 처리하면서, 업데이트 이전 버전도 계속 보존하는 자료구조입니다. 일반 Persistent Segment Tree는 point update가 단순하지만, lazy propagation이 붙으면 clone 시점과 lazy 값 전달이 까다로워집니다.

이 레슨은 Persistent Segment Tree와 Lazy Segment Tree를 결합할 때의 원칙을 정리합니다.

1. 수정할 node만 clone한다.
2. lazy 값을 자식에게 밀 때도 자식 clone이 필요하다.
3. 각 version root를 저장해 과거 상태를 질의한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Segment Tree, Lazy Propagation, Persistent Segment Tree
- 함께 보면 좋은 레슨: Segment Tree, Persistent Segment Tree, 오프라인 쿼리
- 다음에 볼 레슨: dynamic segment tree, rollback data structure, link-cut tree

## 1. 문제 신호

| 문제 표현 | 접근 |
| --- | --- |
| 구간 업데이트 후 과거 버전 질의 | persistent lazy segment tree |
| version별 range sum/min query | version root 저장 |
| 업데이트가 많고 복사 비용을 줄여야 함 | path copying |
| 시간이 되돌아가는 쿼리 | persistence 또는 rollback |
| 좌표 범위가 매우 큼 | dynamic persistent tree 고려 |

과거 버전으로 되돌아가기만 하고 branching이 없으면 rollback lazy segment tree가 더 간단할 수 있습니다. 여러 version을 자유롭게 질의하면 persistence가 맞습니다.

## 2. Clone 원칙

Persistence에서는 기존 node를 직접 바꾸면 안 됩니다. 값을 바꿀 node는 먼저 clone합니다.

```text
newNode = copy(oldNode)
modify(newNode)
return newNode
```

lazy propagation에서도 마찬가지입니다. `push`가 자식의 lazy 값을 바꾸는 순간 자식도 clone해야 합니다.

## 3. Range Add, Range Sum 구현

아래 구현은 구간 add와 구간 sum을 처리합니다. 각 업데이트는 새 root index를 반환합니다.

```cpp compile-check
#include <vector>
using namespace std;

struct PersistentLazySegmentTree {
    struct Node {
        long long sum = 0;
        long long lazy = 0;
        int left = -1;
        int right = -1;
    };

    int n;
    vector<Node> nodes;

    explicit PersistentLazySegmentTree(int n) : n(n) {
        nodes.reserve(n * 40);
    }

    int newNode() {
        nodes.push_back(Node{});
        return (int)nodes.size() - 1;
    }

    int newNode(const Node& node) {
        nodes.push_back(node);
        return (int)nodes.size() - 1;
    }

    int build(int left, int right, const vector<long long>& values) {
        int idx = newNode();
        if (right - left == 1) {
            nodes[idx].sum = values[left];
            return idx;
        }

        int mid = (left + right) / 2;
        nodes[idx].left = build(left, mid, values);
        nodes[idx].right = build(mid, right, values);
        pull(idx);
        return idx;
    }

    void pull(int idx) {
        nodes[idx].sum = nodes[nodes[idx].left].sum + nodes[nodes[idx].right].sum;
    }

    int cloneNode(int idx) {
        return newNode(nodes[idx]);
    }

    void apply(int idx, int left, int right, long long delta) {
        nodes[idx].sum += delta * (right - left);
        nodes[idx].lazy += delta;
    }

    void push(int idx, int left, int right) {
        if (nodes[idx].lazy == 0 || right - left == 1) {
            return;
        }

        int mid = (left + right) / 2;
        nodes[idx].left = cloneNode(nodes[idx].left);
        nodes[idx].right = cloneNode(nodes[idx].right);

        long long delta = nodes[idx].lazy;
        apply(nodes[idx].left, left, mid, delta);
        apply(nodes[idx].right, mid, right, delta);
        nodes[idx].lazy = 0;
    }

    int rangeAdd(int idx, int left, int right, int queryLeft, int queryRight, long long delta) {
        if (queryRight <= left || right <= queryLeft) {
            return idx;
        }

        int cur = cloneNode(idx);
        if (queryLeft <= left && right <= queryRight) {
            apply(cur, left, right, delta);
            return cur;
        }

        push(cur, left, right);
        int mid = (left + right) / 2;
        nodes[cur].left = rangeAdd(nodes[cur].left, left, mid, queryLeft, queryRight, delta);
        nodes[cur].right = rangeAdd(nodes[cur].right, mid, right, queryLeft, queryRight, delta);
        pull(cur);
        return cur;
    }

    long long rangeSum(int idx, int left, int right, int queryLeft, int queryRight) {
        if (queryRight <= left || right <= queryLeft) {
            return 0;
        }
        if (queryLeft <= left && right <= queryRight) {
            return nodes[idx].sum;
        }

        push(idx, left, right);
        int mid = (left + right) / 2;
        return rangeSum(nodes[idx].left, left, mid, queryLeft, queryRight)
            + rangeSum(nodes[idx].right, mid, right, queryLeft, queryRight);
    }
};
```

주의할 점은 `rangeSum`에서 `push`가 node를 바꾸는 구현이라는 점입니다. 완전한 read-only query가 필요하면 query 중 lazy carry를 인자로 넘기는 방식으로 바꾸는 편이 더 엄격합니다.

## 4. Read-only Query 변형

과거 version을 질의하는 작업이 tree를 바꾸면 디버깅이 어려울 수 있습니다. 이때는 query에서 lazy를 내려보내지 않고 누적 lazy를 들고 갑니다.

```text
query(node, l, r, ql, qr, carryLazy)
```

완전히 포함된 구간에서는:

```text
return node.sum + carryLazy * (r-l)
```

부분 겹침에서는 `carryLazy + node.lazy`를 자식으로 넘깁니다. 이 방식은 query가 node를 clone하지 않으므로 순수합니다.

## 5. 메모리 계산

구간 업데이트 하나는 방문한 경로와 필요한 lazy child clone을 만듭니다.

| 작업 | 새 node 수 |
| --- | ---: |
| point update | `O(log N)` |
| range update with lazy | `O(log N)` 중심, push clone 포함 |
| build | `O(N)` |

실제 상수는 일반 persistent tree보다 큽니다. `Q log N * 2~4` 정도의 node 수를 넉넉히 잡습니다.

## 6. Rollback과 비교

| 방식 | 장점 | 제한 |
| --- | --- | --- |
| rollback | 구현 단순, 메모리 적음 | 최신 상태에서 되돌리기 중심 |
| persistence | 임의 version 질의 가능 | node clone과 메모리 관리 필요 |
| offline divide conquer | 특정 쿼리 구조에 강함 | 쿼리 재배치 필요 |

문제에서 version graph가 tree처럼 branching하면 persistence가 자연스럽습니다.

## 7. 시간 복잡도

| 연산 | 시간 |
| --- | ---: |
| build | `O(N)` |
| range update | `O(log N)` |
| range query | `O(log N)` |
| version root 저장 | `O(1)` |

lazy propagation이 있어도 segment tree의 높이는 유지됩니다.

## 8. 자주 하는 실수

1. 기존 node에 lazy를 직접 더해 과거 version을 깨뜨린다.
2. `push`에서 자식을 clone하지 않는다.
3. query가 node를 바꾸는 구현인데 read-only라고 착각한다.
4. node pool 크기를 point update 기준으로 너무 작게 잡는다.
5. range boundary를 `[l, r]`와 `[l, r)`로 섞는다.

## 9. 문제를 볼 때 체크할 조건

- version을 임의로 질의해야 하는가?
- update가 range update인가 point update인가?
- query가 read-only여야 하는가?
- 값 범위가 커서 dynamic tree가 필요한가?
- node 수 상한이 메모리 제한에 맞는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: versioned range add sum `/practice/...` 문제 필요 | clone 후 lazy 적용 | persistent lazy segment tree |
| 표준 | TODO: 과거 버전 range query `/practice/...` 문제 필요 | root 배열 관리 | version root |
| 응용 | TODO: branching update history `/practice/...` 문제 필요 | 임의 version에서 새 version 생성 | full persistence |
| 함정 | TODO: read-only query 검증 `/practice/...` 문제 필요 | lazy carry 방식 | pure query |
