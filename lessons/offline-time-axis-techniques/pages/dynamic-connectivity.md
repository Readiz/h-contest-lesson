# Dynamic Connectivity

Dynamic Connectivity는 간선이 추가되고 삭제되는 그래프에서 두 정점의 연결 여부를 묻는 주제입니다. 온라인으로 처리하면 Link-Cut Tree나 Euler Tour Tree 같은 고급 구조가 필요하지만, 질의를 모두 알고 있다면 시간축 Segment Tree와 Rollback DSU로 실용적으로 풀 수 있습니다.


정점 번호는 링크한 공유 DSU 기준 0..N-1입니다. queryCount>=0, 활성 구간은 0<=l<=r<=Q입니다. 일반 그래프 온라인 연결성은 동적 forest 외에 대체 간선 탐색 구조가 필요합니다. 전체 비용은 O(N+Q+(M log(Q+1)+Q)log(N+1))이며 M은 활성 구간 수입니다.


아래 시간축 어댑터는 [Rollback Techniques](https://h.readiz.com/learn/offline-time-axis-techniques/rollback-techniques)의 RollbackDsu 정의 뒤에 붙입니다.

## 문제 신호

| 문제 표현 | Dynamic Connectivity 관점 |
| --- | --- |
| 간선 추가와 삭제가 섞인다 | edge active interval |
| 각 시점마다 `u`와 `v`가 연결됐는지 묻는다 | rollback DSU |
| 모든 질의를 미리 읽을 수 있다 | offline 가능 |
| 삭제가 어렵다 | rollback으로 시간 DFS에서 되돌림 |
| 그래프가 forest가 아닐 수 있다 | Link-Cut Tree만으로 부족할 수 있음 |

질의가 실시간으로 주어지고 되돌릴 수 없다면 offline 풀이가 불가능합니다. 하지만 대부분의 대회 입력은 전체 질의를 먼저 읽을 수 있으므로 offline 변환을 먼저 검토합니다.

## 간선 생존 구간

간선 `(u, v)`가 시간 `l`에 추가되고 시간 `r`에 삭제되면, 이 간선은 `[l, r)` 구간에서 살아 있습니다.

```text
0: add 1 2
1: query 1 2
2: remove 1 2

edge (1, 2) active on [0, 2)
```

삭제되지 않은 간선은 마지막 질의 이후까지 살아 있다고 보고 `[l, Q)`로 넣습니다.

## 시간축 Segment Tree

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

## Rollback DSU

Path compression은 rollback과 잘 맞지 않습니다. 대신 union by size만 사용하고, 바뀐 parent/size를 stack에 기록합니다.

DSU는 앞서 링크한 `RollbackDsu` 정의를 사용하고, 아래에는 시간축 어댑터를 둡니다.

`unite`가 실패한 경우도 history에 dummy를 넣어 두면, 호출 횟수와 rollback 크기를 안정적으로 맞출 수 있습니다.

## Offline Solver 골격

아래 구조는 이미 계산된 edge interval을 받아 query answer를 채웁니다. 실제 입력 파싱에서는 `map<pair<int,int>, int>`로 add 시점을 저장하고 remove 때 interval을 닫습니다.

```cpp
#include <utility>
#include <vector>
using namespace std;

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

    void solve(int node, int left, int right, RollbackDsu& dsu) {
        if (left >= right) return;
        int snapshot = dsu.snapshot();
        for (Edge edge : tree[node]) {
            dsu.unite(edge.u, edge.v);
        }

        if (right - left == 1) {
            if (hasQuery[left]) {
                Edge query = connectivityQueries[left];
                answer[left] = (dsu.find(query.u) == dsu.find(query.v)) ? 1 : 0;
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

## 간선 Key 정규화

무향 그래프에서는 `(u, v)`와 `(v, u)`가 같은 간선입니다.

```text
if (u > v) swap(u, v)
key = (u, v)
```

중복 add가 가능한 입력인지도 확인해야 합니다. multigraph라면 같은 endpoint라도 edge id나 count를 따로 관리해야 합니다.

## Online 풀이와 비교

| 조건 | 추천 |
| --- | --- |
| 질의를 모두 미리 읽을 수 있음 | segment tree + rollback DSU |
| forest에서 link/cut/path query | Link-Cut Tree |
| 일반 그래프 fully dynamic connectivity | Euler Tour Tree 계열, randomized structure |
| 삭제가 없고 추가만 있음 | 일반 DSU |

실전에서는 offline이 가능한지 먼저 봅니다. Online general dynamic connectivity는 구현 난도가 훨씬 높습니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| 간선 interval 하나 삽입 | `O(log Q)`개 node에 저장 |
| DFS 전체 union 횟수 | `O(M log Q)` |
| DSU 연산 | union by size로 `O(log N)` 이하 깊이 |
| 전체 | `O(N+Q+(M log(Q+1)+Q)log(N+1))` |

Path compression을 쓰지 않으므로 이론상 inverse Ackermann은 아니지만, rollback이 가능한 구조가 더 중요합니다.

## Trace: active interval 만들기

아래 operation을 모두 미리 읽을 수 있다고 하겠습니다.

```text
0: + 0 1
1: + 1 2
2: ? 0 2
3: - 0 1
4: ? 0 2
5: + 2 3
6: ? 0 3
```

간선은 활성 구간으로 바꿉니다.

| edge | active interval |
| --- | --- |
| `(0, 1)` | `[0, 3)` |
| `(1, 2)` | `[1, 7)` |
| `(2, 3)` | `[5, 7)` |

시간축 Segment Tree는 각 interval을 `O(log Q)`개의 node에 넣습니다. DFS가 어떤 node에 들어가면 그 node의 edge들을 rollback DSU에 union하고, leaf에 도착하면 해당 시간의 query를 현재 DSU 상태로 답합니다. node를 빠져나올 때는 진입 전 snapshot으로 되돌립니다.

위 예시의 답은 아래와 같습니다.

```text
YES
NO
NO
```

`2`번 시점에는 `0-1-2`가 연결되어 있습니다. `4`번 시점에는 `(0,1)`이 빠져 `0`과 `2`가 끊어집니다. `6`번 시점에는 `1-2-3`만 연결되어 있고 `0`은 여전히 떨어져 있습니다.

## 로컬 연습: Offline Dynamic Connectivity

### 입력

무향 그래프가 처음에는 비어 있습니다. `Q`개의 operation이 주어집니다.

```text
N Q
op1
op2
...
opQ
```

operation은 세 종류입니다.

```text
+ u v
- u v
? u v
```

`+ u v`는 간선을 추가하고, `- u v`는 현재 활성인 간선을 삭제합니다. `? u v`는 현재 그래프에서 두 정점이 연결되어 있는지 묻습니다. 같은 unordered edge가 동시에 두 번 활성화되지는 않는다고 가정합니다.

### 출력

각 `?` query마다 연결되어 있으면 `YES`, 아니면 `NO`를 출력합니다.

### 제한

- `1 <= N <= 200000`
- `1 <= Q <= 200000`
- `0 <= u, v < N`
- `u != v`

### 예시

```text
4 7
+ 0 1
+ 1 2
? 0 2
- 0 1
? 0 2
+ 2 3
? 0 3
```

```text
YES
NO
NO
```

### 풀이 기준

1. edge key는 `(min(u, v), max(u, v))`로 정규화한다.
2. `+` 시점은 map에 저장한다.
3. `-` 시점이 나오면 `[start, currentTime)` interval을 만든다.
4. 끝까지 삭제되지 않은 edge는 `[start, Q)`로 닫는다.
5. 각 interval을 시간축 Segment Tree에 넣는다.
6. rollback DSU로 DFS를 돌며 leaf의 `?` query를 답한다.

Rollback DSU는 path compression을 쓰지 않습니다. union by size/rank만 쓰고, 바뀐 parent와 size를 stack에 저장합니다. union이 실제로 합치지 못한 경우에도 rollback 횟수를 맞추기 위해 marker를 넣거나, snapshot 크기로 되돌리는 방식을 씁니다.

### Stress 검증

작은 입력에서는 매 query마다 현재 active edge 목록으로 그래프를 새로 만들고 BFS/DFS로 답하는 baseline과 비교합니다.

```text
for seed in 1..1000:
    generate valid add/remove/query sequence
    answer_offline = segment tree over time + rollback DSU
    answer_naive = rebuild graph at every query
    assert answer_offline == answer_naive
```

중복 add를 허용하는 문제라면 edge별 reference count가 필요합니다. 이 로컬 연습은 "동시에 한 번만 활성"이라는 조건에서 active interval 변환과 rollback 구현을 먼저 고정하는 목적입니다.
