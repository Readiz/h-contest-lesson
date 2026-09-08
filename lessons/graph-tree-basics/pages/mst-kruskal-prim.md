# 그래프와 트리 기본 성질: 최소 신장 트리

## 최소 신장 트리

최소 신장 트리(MST, Minimum Spanning Tree)는 가중치가 있는 무방향 연결 그래프에서 모든 정점을 연결하면서 간선 비용 합이 최소인 트리입니다.

MST를 생각할 때 조건을 분리하면 실수가 줄어듭니다.

```text
1. 모든 정점이 연결되어야 한다.
2. 사이클은 필요 없다. 정점 n개를 잇는 트리는 간선 n - 1개다.
3. 비용 합이 최소여야 한다.
```

대표 알고리즘은 Kruskal과 Prim입니다.

| 알고리즘 | 핵심 아이디어 | 잘 맞는 표현 |
| --- | --- | --- |
| Kruskal | 간선을 비용 오름차순으로 보며, 사이클을 만들지 않으면 선택 | 간선 리스트 + Union-Find |
| Prim | 현재 연결된 정점 집합에서 바깥으로 나가는 가장 싼 간선을 선택 | 인접 리스트 + 우선순위 큐 |

아래 코드는 [Union-Find 강의](https://h.readiz.com/learn/union-find)의 `DSU`를 사용합니다. `unite`가 성공한 간선만 비용에 더합니다.

```cpp
struct Edge {
    int u;
    int v;
    long long cost;
};

long long kruskal(int n, vector<Edge> edges) {
    sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {
        return a.cost < b.cost;
    });

    DSU dsu(n);
    long long total = 0;
    int used = 0;

    for (const Edge& edge : edges) {
        if (!dsu.unite(edge.u, edge.v)) continue;
        total += edge.cost;
        used++;
    }

    if (used != n - 1) {
        return -1; // 모든 정점을 연결할 수 없음
    }
    return total;
}
```

왜 가장 싼 간선부터 봐도 될까요? 핵심은 절단 성질입니다.

```text
어떤 정점 집합 S와 나머지를 가르는 절단을 생각한다.
그 절단을 건너는 간선 중 가장 싼 간선은 MST에 넣어도 안전하다.
```

Kruskal은 비용이 작은 간선부터 보면서, 이미 같은 컴포넌트 안의 간선은 사이클을 만들기 때문에 버립니다. 서로 다른 컴포넌트를 잇는 간선은 그 순간 두 컴포넌트를 가르는 절단의 싼 후보로 볼 수 있어 안전하게 선택합니다.

선택한 간선이 `n - 1`개보다 적으면 입력이 연결되지 않은 것입니다. 비용 합은 `long long`으로 계산합니다. MST는 전체 연결 비용을 최소화하며, 두 정점 사이의 경로가 최단거리라는 보장은 없습니다.
