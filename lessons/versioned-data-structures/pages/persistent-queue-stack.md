# Persistent Queue and Stack

Persistent Queue and Stack은 update 뒤에도 과거 version을 조회해야 하는 stack, queue, deque를 어떻게 저장할지 다루는 자료구조 레슨입니다. Persistent Segment Tree처럼 큰 범위 구조를 복제하기 전, 선형 container의 version 관리가 어떤 모델로 단순화되는지 보는 것이 목표입니다.

## 문제 신호

| 문제 표현 | 후보 구조 |
| --- | --- |
| `version v`에 push한 새 version | persistent stack |
| 과거 stack top을 조회 | node pointer |
| queue push/pop 뒤 과거 version 조회 | persistent queue |
| k번째 이전 원소 조회 | binary lifting |
| 과거 operation 자체를 삽입/삭제 | retroactive structure |

새 operation이 항상 기존 version에서 새 version을 만드는 형태면 persistence입니다. 과거 timeline 중간에 operation을 끼워 넣으면 retroactivity입니다.

## Persistent Stack

Stack push는 새 node를 만들고 이전 top을 parent로 둡니다. Pop은 parent를 top으로 하는 새 version을 만들면 됩니다.

```cpp compile-check
#include <vector>
using namespace std;

struct PersistentStack {
    struct Node {
        int value = 0;
        int parent = 0;
        int size = 0;
    };

    vector<Node> nodes;
    vector<int> roots;

    PersistentStack() {
        nodes.push_back(Node{0, 0, 0});
        roots.push_back(0);
    }

    int push(int version, int value) {
        int oldRoot = roots[version];
        nodes.push_back(Node{value, oldRoot, nodes[oldRoot].size + 1});
        roots.push_back((int)nodes.size() - 1);
        return (int)roots.size() - 1;
    }

    int pop(int version) {
        int oldRoot = roots[version];
        int newRoot = nodes[oldRoot].parent;
        roots.push_back(newRoot);
        return (int)roots.size() - 1;
    }

    int top(int version) const {
        return nodes[roots[version]].value;
    }

    int size(int version) const {
        return nodes[roots[version]].size;
    }
};
```

빈 stack에서 pop/top을 어떻게 처리할지는 문제 조건에 맞춰 별도 검사합니다.

## K번째 Ancestor

Stack에서 "top에서 k개 아래 원소"를 자주 묻는다면 binary lifting을 붙입니다.

```text
up[node][0] = parent
up[node][j] = up[up[node][j-1]][j-1]
```

Push 때 새 node의 lifting table만 채우면 됩니다. Pop은 root만 바꾸므로 새 lifting 계산이 필요 없습니다.

## Persistent Queue 모델

Queue는 stack보다 어렵습니다. front에서 pop하고 back에 push하기 때문입니다.

| 접근 | 장점 | 주의 |
| --- | --- | --- |
| persistent sequence | kth 접근이 명확 | segment tree/treap 구현 필요 |
| two persistent stacks | 함수형 queue 직관 | front stack 재빌드 비용 관리 |
| parent pointer + index | append-only queue에 단순 | pop이 앞 index 증가일 때만 가능 |
| rollback queue | offline undo에 쉬움 | version branching에는 약함 |

버전이 분기하면 전역 배열의 연속 구간만으로는 큐를 표현할 수 없습니다. 같은 꼬리에서 서로 다른 값을 push한 두 버전이 같은 위치를 공유하기 때문입니다. 아래처럼 배열 자체도 persistent하게 저장합니다.

## Append-only Persistent Queue

각 version이 이전 version에서 push/pop만 한다면, root에 `head`, `tail`, 그리고 원소 배열의 persistent sequence root를 저장합니다.

```text
version state:
  root: persistent array root
  head: front index
  tail: one past back index

push(x):
  root' = set(root, tail, x)
  head' = head
  tail' = tail + 1

pop():
  head' = head + 1
```

이 모델은 중간 삽입이 없을 때 강합니다. Deque처럼 양쪽 push/pop이 있으면 implicit treap 같은 persistent sequence가 더 자연스럽습니다.

## 작은 예시

```text
v0 = empty
v1 = push(v0, 10)
v2 = push(v1, 20)
v3 = pop(v2)
v4 = push(v1, 30)

v2 top = 20
v3 top = 10
v4 top = 30
v2와 v4는 v1에서 갈라진 서로 다른 branch다.
```

기존 stack을 복사하지 않고 root pointer만 다르게 잡으면 모든 version을 보존할 수 있습니다.

## 시간 복잡도

| 구조 | update | query | 메모리 |
| --- | ---: | ---: | ---: |
| persistent stack | `O(1)` | top `O(1)` | operation당 `O(1)` |
| stack + binary lifting | `O(log Q)` | kth ancestor `O(log Q)` | operation당 `O(log Q)` |
| persistent segment queue | `O(log Q)` | front/kth `O(log Q)` | operation당 `O(log Q)` |
| persistent implicit treap | expected `O(log Q)` | split/merge 기반 | operation당 `O(log Q)` |

문제에서 queue가 정말 필요한지, stack parent pointer로 바꿀 수 있는지 먼저 확인합니다.
