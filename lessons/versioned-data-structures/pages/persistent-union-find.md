# Persistent Union-Find

Persistent Union-Find는 Union-Find의 과거 version에 대한 연결성이나 component size를 묻는 기법입니다. 변경을 되돌리는 Rollback DSU와, 특정 시간의 상태를 조회하는 partially persistent DSU를 구분해서 선택해야 합니다.

이 레슨은 Union-Find, Dynamic Connectivity, Euler Tour Tree 이후에 보는 자료구조/오프라인 심화입니다.

1. rollback은 DFS나 divide and conquer에서 이전 snapshot으로 돌아갈 때 쓴다.
2. partially persistent DSU는 union 시간이 증가만 할 때 과거 version을 조회한다.
3. 완전 persistent split/merge는 DSU의 구조와 잘 맞지 않으므로 문제 조건을 먼저 좁힌다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Union-Find, union by size, binary search, rollback
- 함께 보면 좋은 레슨: Dynamic Connectivity, Offline Queries, Euler Tour Tree
- 다음에 볼 레슨: rollback techniques, persistent segment tree, retroactive data structure

## 1. 문제 신호

| 문제 표현 | Persistent Union-Find 관점 |
| --- | --- |
| 과거 시점 `t`에서 `u`, `v`가 연결됐는가 | partially persistent DSU |
| DFS로 상태를 적용하고 되돌린다 | rollback DSU |
| query마다 version root가 주어진다 | persistence 후보 |
| 간선 추가만 있고 삭제가 없다 | union time 저장 |
| 임의 version에서 다시 union을 분기한다 | DSU만으로는 어려움 |

Path compression은 parent를 많이 바꾸기 때문에 rollback이나 persistence와 충돌합니다. 보통 union by size/rank만 쓰고 parent 변경 이력을 명시적으로 관리합니다.

## 2. Rollback과 Persistence 차이

| 방식 | 잘 맞는 상황 | 핵심 저장값 |
| --- | --- | --- |
| Rollback DSU | 시간 DFS, segment tree over time | 변경 stack |
| Partially persistent DSU | union-only history query | parent가 바뀐 시간 |
| Fully persistent DSU | version branching | 별도 persistent array 필요 |

Rollback은 "최근 변경부터 되돌리는" 스택 모델입니다. Partially persistent DSU는 "시간 t에서 parent가 아직 바뀌지 않았으면 root"라는 시간 조건으로 find를 합니다.

## 3. Partially Persistent DSU

간선 추가만 있고, 과거 version에 대해 연결성이나 component size를 묻는 경우를 보겠습니다.

```text
parentTime[x] = x가 parent 아래로 붙은 시간
find(x, t):
  parentTime[x] > t 이면 x는 t 시점의 root
  아니면 parent[x]를 따라감
```

component size는 root마다 `(time, size)` history를 저장하고, query time 이하의 마지막 값을 이분 탐색합니다.

## 4. 구현

아래 구현은 union operation이 한 번 호출될 때마다 시간이 1씩 증가하는 모델입니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct PersistentUnionFind {
    static const int INF = 1'000'000'000;
    int currentTime = 0;
    vector<int> parent;
    vector<int> parentTime;
    vector<vector<pair<int, int>>> sizeHistory;

    explicit PersistentUnionFind(int n)
        : parent(n + 1), parentTime(n + 1, INF), sizeHistory(n + 1) {
        for (int i = 1; i <= n; ++i) {
            parent[i] = i;
            sizeHistory[i].push_back({0, 1});
        }
    }

    int find(int x, int time) const {
        if (parentTime[x] > time) {
            return x;
        }
        return find(parent[x], time);
    }

    int componentSize(int x, int time) const {
        int root = find(x, time);
        const auto& history = sizeHistory[root];
        int left = 0;
        int right = (int)history.size();
        while (left + 1 < right) {
            int mid = (left + right) / 2;
            if (history[mid].first <= time) {
                left = mid;
            } else {
                right = mid;
            }
        }
        return history[left].second;
    }

    bool connected(int a, int b, int time) const {
        return find(a, time) == find(b, time);
    }

    int unite(int a, int b) {
        ++currentTime;
        a = find(a, currentTime);
        b = find(b, currentTime);
        if (a == b) {
            return currentTime;
        }

        int sizeA = componentSize(a, currentTime);
        int sizeB = componentSize(b, currentTime);
        if (sizeA < sizeB) {
            swap(a, b);
            swap(sizeA, sizeB);
        }

        parent[b] = a;
        parentTime[b] = currentTime;
        sizeHistory[a].push_back({currentTime, sizeA + sizeB});
        return currentTime;
    }
};
```

이 구조에서는 `find`가 parent chain을 따라가므로 path compression을 하지 않습니다. union by size 덕분에 depth는 `O(log N)` 안에 머무릅니다.

## 5. Version Query 예시

```text
time 1: unite(1, 2)
time 2: unite(3, 4)
time 3: unite(2, 3)

connected(1, 4, 2) = false
connected(1, 4, 3) = true
componentSize(1, 2) = 2
componentSize(1, 3) = 4
```

과거 time을 명시적으로 묻는 문제에서는 rollback보다 이 방식이 query 순서를 바꾸지 않아도 되어 편합니다.

## 6. Rollback DSU가 더 나은 경우

간선 삭제가 있고 offline segment tree over time을 돌린다면 persistent DSU보다 rollback DSU가 자연스럽습니다.

```text
dfs(time interval):
  snapshot 저장
  이 구간 전체에서 살아 있는 edge union
  child로 내려감
  snapshot으로 rollback
```

이 경우 query는 DFS leaf에서 현재 상태만 보면 됩니다. 특정 과거 time에 랜덤 access하는 것이 아니라 재귀 traversal 상태를 되돌리는 문제이기 때문입니다.

## 7. 시간 복잡도

| 작업 | Partially Persistent DSU |
| --- | ---: |
| unite | `O(log N)` |
| find at time | `O(log N)` |
| connected at time | `O(log N)` |
| component size at time | `O(log N)` |
| memory | `O(N + union count)` |

상수는 작지만 재귀 `find`가 깊어질 수 있으므로 union by size/rank는 필수입니다.

## 8. 자주 하는 실수

1. path compression을 켜서 과거 parent 구조를 망가뜨린다.
2. `parentTime[x] > t`와 `>= t` 경계를 헷갈린다.
3. 같은 component union에서도 time 증가 여부를 문제의 version 정의와 다르게 처리한다.
4. component size를 현재 root 기준으로만 저장해 과거 root query가 깨진다.
5. 삭제가 있는 문제를 partially persistent DSU만으로 처리하려고 한다.

## 9. 문제를 볼 때 체크할 조건

- union operation만 있는가?
- query가 과거 time을 직접 지정하는가?
- version이 선형 history인가, branching인가?
- component size도 필요한가?
- rollback traversal이 더 간단한 구조는 아닌가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: persistent union-find `/practice/...` 문제 필요 | 과거 연결성 조회 | union time |
| 표준 | TODO: versioned component size `/practice/...` 문제 필요 | size history 이분 탐색 | component size |
| 응용 | TODO: offline connectivity versions `/practice/...` 문제 필요 | rollback과 persistence 선택 | query time |
| 함정 | TODO: path compression counterexample `/practice/...` 문제 필요 | parent 변경 이력 보존 | no compression |
