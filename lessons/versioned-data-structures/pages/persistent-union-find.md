# Persistent Union-Find

Persistent Union-Find는 Union-Find의 과거 version에 대한 연결성이나 component size를 묻는 기법입니다. 변경을 되돌리는 Rollback DSU와, 특정 시간의 상태를 조회하는 partially persistent DSU를 구분해서 선택해야 합니다.

## 문제 신호

| 문제 표현 | Persistent Union-Find 관점 |
| --- | --- |
| 과거 시점 `t`에서 `u`, `v`가 연결됐는가 | partially persistent DSU |
| DFS로 상태를 적용하고 되돌린다 | rollback DSU |
| query마다 version root가 주어진다 | persistence 후보 |
| 간선 추가만 있고 삭제가 없다 | union time 저장 |
| 임의 version에서 다시 union을 분기한다 | DSU만으로는 어려움 |

Path compression은 parent를 많이 바꾸기 때문에 rollback이나 persistence와 충돌합니다. 보통 union by size/rank만 쓰고 parent 변경 이력을 명시적으로 관리합니다.

## Rollback과 Persistence 차이

| 방식 | 잘 맞는 상황 | 핵심 저장값 |
| --- | --- | --- |
| Rollback DSU | 시간 DFS, segment tree over time | 변경 stack |
| Partially persistent DSU | union-only history query | parent가 바뀐 시간 |
| Fully persistent DSU | version branching | 별도 persistent array 필요 |

Rollback은 "최근 변경부터 되돌리는" 스택 모델입니다. Partially persistent DSU는 "시간 t에서 parent가 아직 바뀌지 않았으면 root"라는 시간 조건으로 find를 합니다.

## Partially Persistent DSU

간선 추가만 있고, 과거 version에 대해 연결성이나 component size를 묻는 경우를 보겠습니다.

```text
parentTime[x] = x가 parent 아래로 붙은 시간
find(x, t):
  parentTime[x] > t 이면 x는 t 시점의 root
  아니면 parent[x]를 따라감
```

component size는 root마다 `(time, size)` history를 저장하고, query time 이하의 마지막 값을 이분 탐색합니다.

## 구현

정점은 `1..n`, 조회 시각은 `0..currentTime`이고 전체 union 호출 수는 `INF`보다 작아야 합니다. 아래 구현은 union operation이 한 번 호출될 때마다 시간이 1씩 증가하는 모델입니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct PersistentUnionFind {
    inline static constexpr int INF = 1'000'000'000;
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

## Version Query 예시

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

## Rollback DSU가 더 나은 경우

간선 삭제가 있고 offline segment tree over time을 돌린다면 persistent DSU보다 rollback DSU가 자연스럽습니다.

```text
dfs(time interval):
  snapshot 저장
  이 구간 전체에서 살아 있는 edge union
  child로 내려감
  snapshot으로 rollback
```

이 경우 query는 DFS leaf에서 현재 상태만 보면 됩니다. 특정 과거 time에 랜덤 access하는 것이 아니라 재귀 traversal 상태를 되돌리는 문제이기 때문입니다.

## 시간 복잡도

| 작업 | Partially Persistent DSU |
| --- | ---: |
| unite | `O(log N)` |
| find at time | `O(log N)` |
| connected at time | `O(log N)` |
| component size at time | `O(log N)` |
| memory | `O(N + union count)` |

상수는 작지만 재귀 `find`가 깊어질 수 있으므로 union by size/rank는 필수입니다.
