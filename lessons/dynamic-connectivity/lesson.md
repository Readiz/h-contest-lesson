# Dynamic Connectivity

Dynamic Connectivity는 간선이 추가되고 삭제되는 그래프에서 두 정점의 연결 여부를 묻는 주제입니다. 온라인으로 처리하면 Link-Cut Tree나 Euler Tour Tree 같은 고급 구조가 필요하지만, 질의를 모두 알고 있다면 시간축 Segment Tree와 Rollback DSU로 실용적으로 풀 수 있습니다.

이 레슨은 Directed MST, Offline Queries, Link-Cut Tree 이후에 보는 그래프 심화입니다.

1. 간선이 살아 있는 시간 구간을 모은다.
2. 시간축 segment tree의 구간 노드에 간선을 넣는다.
3. DFS로 내려가며 DSU union을 적용하고, 돌아올 때 rollback한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Union-Find, segment tree over intervals, DFS, offline processing
- 함께 보면 좋은 레슨: Union-Find, Offline Queries, Link-Cut Tree
- 다음에 볼 레슨: Euler Tour Tree, fully dynamic graph, dynamic MST

## 1. 문제 신호

| 문제 표현 | Dynamic Connectivity 관점 |
| --- | --- |
| 간선 추가와 삭제가 섞인다 | edge active interval |
| 각 시점마다 `u`와 `v`가 연결됐는지 묻는다 | rollback DSU |
| 모든 질의를 미리 읽을 수 있다 | offline 가능 |
| 삭제가 어렵다 | rollback으로 시간 DFS에서 되돌림 |
| 그래프가 forest가 아닐 수 있다 | Link-Cut Tree만으로 부족할 수 있음 |

질의가 실시간으로 주어지고 되돌릴 수 없다면 offline 풀이가 불가능합니다. 하지만 대부분의 대회 입력은 전체 질의를 먼저 읽을 수 있으므로 offline 변환을 먼저 검토합니다.

## 2. 간선 생존 구간

간선 `(u, v)`가 시간 `l`에 추가되고 시간 `r`에 삭제되면, 이 간선은 `[l, r)` 구간에서 살아 있습니다.

```text
0: add 1 2
1: query 1 2
2: remove 1 2

edge (1, 2) active on [0, 2)
```

삭제되지 않은 간선은 마지막 질의 이후까지 살아 있다고 보고 `[l, Q)`로 넣습니다.

## 3. 시간축 Segment Tree

각 간선의 활성 구간 `[l, r)`을 segment tree에 넣습니다. DFS가 어떤 node 구간을 담당할 때, 그 node에 들어 있는 간선은 해당 시간 구간 전체에서 항상 존재합니다.

```text
dfs(node):
  snapshot = dsu.snapshot()
  node의 모든 edge union
  leaf면 query answer
  아니면 left/right 재귀
  dsu.rollback(snapshot)
```

삭제를 직접 처리하지 않고, 재귀를 빠져나올 때 DSU를 이전 상태로 되돌리는 것이 핵심입니다.

## 4. Rollback DSU

Path compression은 rollback과 잘 맞지 않습니다. 대신 union by size만 사용하고, 바뀐 parent/size를 stack에 기록합니다.

```cpp compile-check
#include <algorithm>
#include <utility>
#include <vector>
using namespace std;

struct RollbackDSU {
    vector<int> parent;
    vector<int> size;
    vector<pair<int, int>> history;
    int components = 0;

    explicit RollbackDSU(int n) : parent(n + 1), size(n + 1, 1), components(n) {
        for (int i = 1; i <= n; ++i) {
            parent[i] = i;
        }
    }

    int find(int x) const {
        while (parent[x] != x) {
            x = parent[x];
        }
        return x;
    }

    bool unite(int a, int b) {
        a = find(a);
        b = find(b);
        if (a == b) {
            history.push_back({-1, -1});
            return false;
        }
        if (size[a] < size[b]) {
            swap(a, b);
        }
        parent[b] = a;
        size[a] += size[b];
        history.push_back({a, b});
        --components;
        return true;
    }

    int snapshot() const {
        return (int)history.size();
    }

    void rollback(int snapshotSize) {
        while ((int)history.size() > snapshotSize) {
            auto [a, b] = history.back();
            history.pop_back();
            if (a == -1) {
                continue;
            }
            size[a] -= size[b];
            parent[b] = b;
            ++components;
        }
    }

    bool connected(int a, int b) const {
        return find(a) == find(b);
    }
};
```

`unite`가 실패한 경우도 history에 dummy를 넣어 두면, 호출 횟수와 rollback 크기를 안정적으로 맞출 수 있습니다.

## 5. Offline Solver 골격

아래 구조는 이미 계산된 edge interval을 받아 query answer를 채웁니다. 실제 입력 파싱에서는 `map<pair<int,int>, int>`로 add 시점을 저장하고 remove 때 interval을 닫습니다.

```cpp compile-check
#include <utility>
#include <vector>
using namespace std;

struct RollbackDSUConnectivity {
    vector<int> parent;
    vector<int> size;
    vector<pair<int, int>> history;

    explicit RollbackDSUConnectivity(int n) : parent(n + 1), size(n + 1, 1) {
        for (int i = 1; i <= n; ++i) {
            parent[i] = i;
        }
    }

    int find(int x) const {
        while (parent[x] != x) {
            x = parent[x];
        }
        return x;
    }

    void unite(int a, int b) {
        a = find(a);
        b = find(b);
        if (a == b) {
            history.push_back({-1, -1});
            return;
        }
        if (size[a] < size[b]) {
            int temp = a;
            a = b;
            b = temp;
        }
        parent[b] = a;
        size[a] += size[b];
        history.push_back({a, b});
    }

    int snapshot() const {
        return (int)history.size();
    }

    void rollback(int snapshotSize) {
        while ((int)history.size() > snapshotSize) {
            pair<int, int> last = history.back();
            history.pop_back();
            if (last.first == -1) {
                continue;
            }
            size[last.first] -= size[last.second];
            parent[last.second] = last.second;
        }
    }

    bool connected(int a, int b) const {
        return find(a) == find(b);
    }
};

struct OfflineDynamicConnectivity {
    struct Edge {
        int u;
        int v;
    };

    int queryCount;
    vector<vector<Edge>> tree;
    vector<Edge> connectivityQueries;
    vector<int> hasQuery;
    vector<int> answer;

    explicit OfflineDynamicConnectivity(int q)
        : queryCount(q), tree(4 * q + 4), connectivityQueries(q), hasQuery(q, 0), answer(q, 0) {}

    void addInterval(int node, int left, int right, int ql, int qr, Edge edge) {
        if (qr <= left || right <= ql) {
            return;
        }
        if (ql <= left && right <= qr) {
            tree[node].push_back(edge);
            return;
        }
        int mid = (left + right) / 2;
        addInterval(node * 2, left, mid, ql, qr, edge);
        addInterval(node * 2 + 1, mid, right, ql, qr, edge);
    }

    void addActiveEdgeInterval(int left, int right, int u, int v) {
        if (left < right) {
            addInterval(1, 0, queryCount, left, right, {u, v});
        }
    }

    void setConnectivityQuery(int time, int u, int v) {
        connectivityQueries[time] = {u, v};
        hasQuery[time] = 1;
    }

    void solve(int node, int left, int right, RollbackDSUConnectivity& dsu) {
        int snapshot = dsu.snapshot();
        for (Edge edge : tree[node]) {
            dsu.unite(edge.u, edge.v);
        }

        if (right - left == 1) {
            if (hasQuery[left]) {
                Edge query = connectivityQueries[left];
                answer[left] = dsu.connected(query.u, query.v) ? 1 : 0;
            }
        } else {
            int mid = (left + right) / 2;
            solve(node * 2, left, mid, dsu);
            solve(node * 2 + 1, mid, right, dsu);
        }

        dsu.rollback(snapshot);
    }
};
```

## 6. 간선 Key 정규화

무향 그래프에서는 `(u, v)`와 `(v, u)`가 같은 간선입니다.

```text
if (u > v) swap(u, v)
key = (u, v)
```

중복 add가 가능한 입력인지도 확인해야 합니다. multigraph라면 같은 endpoint라도 edge id나 count를 따로 관리해야 합니다.

## 7. Online 풀이와 비교

| 조건 | 추천 |
| --- | --- |
| 질의를 모두 미리 읽을 수 있음 | segment tree + rollback DSU |
| forest에서 link/cut/path query | Link-Cut Tree |
| 일반 그래프 fully dynamic connectivity | Euler Tour Tree 계열, randomized structure |
| 삭제가 없고 추가만 있음 | 일반 DSU |

실전에서는 offline이 가능한지 먼저 봅니다. Online general dynamic connectivity는 구현 난도가 훨씬 높습니다.

## 8. 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| 간선 interval 하나 삽입 | `O(log Q)`개 node에 저장 |
| DFS 전체 union 횟수 | `O(M log Q)` |
| DSU 연산 | union by size로 `O(log N)` 이하 깊이 |
| 전체 | 보통 `O((M log Q) log N)` 또는 충분히 빠른 상수 |

Path compression을 쓰지 않으므로 이론상 inverse Ackermann은 아니지만, rollback이 가능한 구조가 더 중요합니다.

## 9. 자주 하는 실수

1. DSU path compression을 켜서 rollback이 깨진다.
2. 간선 활성 구간을 `[l, r]`로 착각해 삭제 시점 query에 간선을 남긴다.
3. 무향 간선 endpoint 정규화를 빠뜨린다.
4. 같은 간선이 중복 추가되는 입력에서 add 시점을 하나만 저장한다.
5. rollback snapshot을 node 진입 전이 아니라 union 후에 잡는다.

## 10. 문제를 볼 때 체크할 조건

- 질의를 모두 미리 읽을 수 있는가?
- add/remove가 edge id 기준인가 endpoint pair 기준인가?
- 삭제되지 않은 간선을 마지막까지 닫았는가?
- 연결 여부만 묻는가, component size나 bipartite 여부도 묻는가?
- multigraph와 self-loop 처리가 필요한가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 간선 추가만 있는 연결성 `/practice/...` 문제 필요 | DSU 기본 연결성 | union-find |
| 표준 | TODO: offline dynamic connectivity `/practice/...` 문제 필요 | 시간축 segment tree와 rollback | rollback DSU |
| 응용 | TODO: component size 동적 질의 `/practice/...` 문제 필요 | rollback 시 size 복원 | component aggregate |
| 함정 | TODO: 중복 간선 삭제 질의 `/practice/...` 문제 필요 | edge id와 multiset active count 관리 | multigraph |
