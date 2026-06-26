# Rollback Techniques

Rollback Techniques는 오프라인 알고리즘에서 상태를 적용한 뒤 정확히 이전 snapshot으로 되돌리는 구현 패턴입니다. 대표 예시는 Rollback DSU지만, stack에 변경 전 값을 기록하는 방식은 Fenwick, segment tree, DP state, frequency table에도 적용할 수 있습니다.

이 레슨은 Offline Queries, Persistent Union-Find, Dynamic Connectivity 이후에 보는 자료구조/오프라인 심화입니다.

1. 변경을 할 때마다 "되돌리기 위한 최소 정보"를 stack에 쌓는다.
2. 재귀나 divide and conquer 구간에 들어가기 전 snapshot 크기를 저장한다.
3. 구간 처리가 끝나면 stack을 snapshot 크기까지 되돌린다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Union-Find, offline query, recursion over intervals
- 함께 보면 좋은 레슨: Offline Queries, Dynamic Connectivity, Persistent Union-Find
- 다음에 볼 레슨: segment tree over time, divide and conquer on queries, retroactive structures

## 1. 문제 신호

| 문제 표현 | Rollback 관점 |
| --- | --- |
| 구간에 적용되는 update가 있고 leaf에서 query | segment tree over time |
| DFS로 선택을 넣었다 빼며 탐색 | snapshot rollback |
| 삭제가 있지만 offline으로 처리 가능 | add interval + rollback |
| path compression을 쓰면 되돌리기 어려움 | rollback-friendly structure 필요 |
| query 순서를 바꾸어도 됨 | offline divide and conquer |

rollback은 online으로 과거 version에 random access하는 persistence와 다릅니다. 현재 재귀 경로의 상태만 유지하고, 빠져나오면 이전 상태로 되돌립니다.

## 2. 변경 기록 원칙

rollback을 하려면 update가 바꾼 값을 모두 기록해야 합니다.

| 변경 | 기록할 것 |
| --- | --- |
| 배열 한 칸 대입 | index, old value |
| DSU parent 변경 | child, old parent |
| DSU size 변경 | root, old size |
| answer 변수 변경 | old answer |
| 여러 값 동시 변경 | 하나의 operation marker 또는 stack 크기 snapshot |

가장 안전한 방식은 "snapshot = stack size"를 저장하고, 되돌릴 때 stack이 그 크기가 될 때까지 pop하는 것입니다.

## 3. Rollback DSU 구현

아래 구현은 path compression을 쓰지 않고 union by size만 사용합니다. 각 union은 parent와 size 변경 전 값을 기록합니다.

```cpp compile-check
#include <numeric>
#include <utility>
#include <vector>
using namespace std;

struct RollbackDsu {
    struct Change {
        int child;
        int parentBefore;
        int root;
        int sizeBefore;
        int componentsBefore;
    };

    vector<int> parent;
    vector<int> componentSize;
    vector<Change> history;
    int components = 0;

    explicit RollbackDsu(int n) : parent(n), componentSize(n, 1), components(n) {
        iota(parent.begin(), parent.end(), 0);
    }

    int find(int x) const {
        while (parent[x] != x) {
            x = parent[x];
        }
        return x;
    }

    int snapshot() const {
        return (int)history.size();
    }

    bool unite(int a, int b) {
        a = find(a);
        b = find(b);
        if (a == b) {
            history.push_back({-1, -1, -1, -1, components});
            return false;
        }
        if (componentSize[a] < componentSize[b]) {
            swap(a, b);
        }
        history.push_back({b, parent[b], a, componentSize[a], components});
        parent[b] = a;
        componentSize[a] += componentSize[b];
        --components;
        return true;
    }

    void rollback(int snapshotSize) {
        while ((int)history.size() > snapshotSize) {
            Change change = history.back();
            history.pop_back();
            components = change.componentsBefore;
            if (change.child == -1) {
                continue;
            }
            parent[change.child] = change.parentBefore;
            componentSize[change.root] = change.sizeBefore;
        }
    }
};
```

같은 component를 union한 경우에도 history marker를 남기면 "union 호출 수만큼 rollback"하는 코드가 단순해집니다. snapshot 방식만 쓴다면 marker 없이도 처리할 수 있습니다.

## 4. Segment Tree over Time

간선이 시간 구간 `[l, r]` 동안 활성이라면 segment tree의 해당 구간을 덮는 노드들에 간선을 넣습니다.

```text
dfs(node):
  snap = dsu.snapshot()
  node에 들어 있는 edge들을 unite
  if leaf: query 답변
  else: child dfs
  dsu.rollback(snap)
```

각 간선은 `O(log Q)`개 노드에 들어갑니다. leaf에서는 그 시점에 활성인 모든 간선이 현재 DSU에 적용되어 있습니다.

## 5. Divide and Conquer with Rollback

정답 후보 범위를 나눠 가며 update를 적용하는 divide and conquer에서도 rollback을 씁니다. 핵심은 재귀 호출 사이에 상태가 섞이지 않게 하는 것입니다.

```text
solve(l, r, candidates):
  snap 저장
  왼쪽에 필요한 update 적용
  solve(left)
  rollback
  오른쪽에 필요한 update 적용
  solve(right)
  rollback
```

적용 순서가 복잡해질수록 snapshot을 촘촘히 잡는 편이 안전합니다.

## 6. Rollback 가능한 구조 만들기

Rollback은 "변경 전 값을 기록하고 원복"할 수 있으면 됩니다.

| 구조 | rollback 포인트 |
| --- | --- |
| frequency array | `(index, oldCount)` |
| Fenwick Tree | update한 모든 tree index와 delta 또는 old value |
| Segment Tree | 방문한 node의 old aggregate |
| DP table | 바뀐 cell 목록 |
| Hash map | old existence/value marker |

변경 범위가 너무 넓으면 기록 비용이 update 비용보다 커질 수 있습니다. 이때는 persistent structure가 더 나을 수 있습니다.

## 7. Persistence와 비교

| 방식 | 장점 | 한계 |
| --- | --- | --- |
| Rollback | 구현이 단순하고 메모리 예측 쉬움 | 최신 경로 밖 version random access 불가 |
| Partial persistence | 과거 version query가 직접 가능 | update 모델이 제한됨 |
| Full persistence | version branching 가능 | 구현과 메모리 부담 큼 |

오프라인 DFS처럼 상태가 stack discipline을 따르면 rollback이 가장 실용적입니다.

## 8. 자주 하는 실수

1. DSU rollback에서 path compression을 사용한다.
2. answer 변수나 component count 같은 전역 상태를 기록하지 않는다.
3. same-component union의 marker 처리 방식을 섞는다.
4. recursion child 사이에 snapshot을 복구하지 않는다.
5. hash map에서 "기존에 없던 key"와 "값이 0인 key"를 구분하지 않는다.

## 9. 문제를 볼 때 체크할 조건

- update/query를 offline으로 재배열할 수 있는가?
- 상태 변경이 stack 순서로 되돌아오는가?
- 변경 전 값을 모두 기록할 수 있는가?
- path compression처럼 숨은 변경이 있지는 않은가?
- persistence가 더 간단한 random access query는 아닌가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: rollback techniques `/practice/...` 문제 필요 | snapshot과 원복 구현 | rollback stack |
| 표준 | TODO: offline dynamic connectivity `/practice/...` 문제 필요 | segment tree over time | rollback DSU |
| 응용 | TODO: rollback frequency queries `/practice/...` 문제 필요 | 배열 변경 기록 | old value |
| 함정 | TODO: path compression rollback `/practice/...` 문제 필요 | 숨은 parent 변경 제거 | no compression |
