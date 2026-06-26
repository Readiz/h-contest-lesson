# Versioning Model Map

Versioned data structure 문제를 풀기 전에 가장 먼저 정해야 하는 것은 "과거 상태를 어떻게 다시 만나는가"입니다. 같은 과거 상태라도 persistence, rollback, retroactivity는 다른 구현을 요구합니다.

## 1. 모델 비교표

| 질문 | 모델 | 대표 구조 |
| --- | --- | --- |
| 과거 version id가 query에 직접 주어지는가? | persistence | persistent segment tree |
| DFS를 내려갔다가 올라오며 상태만 되돌리는가? | rollback | rollback DSU |
| union 시간이 증가만 하고 과거 연결성을 묻는가? | partial persistence | persistent union-find |
| 과거 operation을 삽입/삭제해 이후 전체가 바뀌는가? | retroactivity | retroactive data structures |
| 정적 배열 prefix 차이로 구간을 만들 수 있는가? | prefix persistence | persistent kth tree |

## 2. 선택 순서

```text
1. query가 version id를 직접 지정하는가?
2. version이 branch되는가?
3. update가 point인지 range인지 확인한다.
4. index가 고정 배열인지, sequence 삽입/삭제로 움직이는지 본다.
5. rollback/offline으로 더 쉽게 바꿀 수 있는지 확인한다.
```

branch가 없고 모든 query를 시간 순서로 처리할 수 있으면 persistent tree보다 Fenwick/Segment Tree sweep이 더 간단할 수 있습니다. 반대로 version tree가 생기면 root를 보존하는 persistent 구조가 자연스럽습니다.

## 3. 메모리 예산

Persistent structure는 시간은 깔끔하지만 node 수가 빠르게 늘어납니다.

```text
node count ~= initial build + update_count * nodes_per_update
nodes_per_update ~= O(log N)
```

lazy propagation, implicit treap, binary lifting을 붙이면 상수가 커집니다. 문제를 읽을 때 `Q * logN * sizeof(Node)`를 먼저 계산합니다.

## 4. 실수 방지

1. path compression처럼 내부 구조를 직접 바꾸는 최적화를 켜지 않는다.
2. query가 read-only인지, lazy push로 node를 바꾸는지 구분한다.
3. rollback 문제에 full persistence를 과하게 쓰지 않는다.
4. retroactive 문제를 단순 persistence로 착각하지 않는다.
5. 압축 좌표를 답으로 출력하지 않도록 원래 값 복원을 둔다.
