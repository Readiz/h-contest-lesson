# 그래프와 트리 기본 성질: 최소 신장 트리

## 7. 최소 신장 트리

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

Kruskal은 Union-Find를 거의 그대로 사용합니다.

```cpp
struct DSU {
    vector<int> parent;
    vector<int> size;

    DSU(int n) : parent(n), size(n, 1) {
        for (int i = 0; i < n; ++i) parent[i] = i;
    }

    int find(int x) {
        if (parent[x] == x) return x;
        return parent[x] = find(parent[x]);
    }

    bool unite(int a, int b) {
        int rootA = find(a);
        int rootB = find(b);
        if (rootA == rootB) return false;

        if (size[rootA] < size[rootB]) swap(rootA, rootB);
        parent[rootB] = rootA;
        size[rootA] += size[rootB];
        return true;
    }
};

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

## 8. MST에서 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 방향 그래프에 MST 적용 | 정의가 맞지 않음 | MST는 보통 무방향 그래프에서 사용 |
| 연결되지 않은 그래프 처리 누락 | 간선이 `n - 1`개보다 적게 선택됨 | 마지막에 `used == n - 1` 확인 |
| 같은 컴포넌트 간선 선택 | 사이클 생성 | Union-Find의 `unite` 반환값 사용 |
| 비용 합을 `int`로 저장 | overflow | 비용 합은 `long long` 사용 |
| 최대 신장 트리와 혼동 | 반대 답 | 최소면 오름차순, 최대면 내림차순 |

MST는 "최단 경로"와 다릅니다. MST는 전체 네트워크 연결 비용을 최소화하지만, 두 정점 사이의 경로가 반드시 최단거리라는 보장은 없습니다.

## 9. 문제를 볼 때 체크할 조건

그래프나 트리 문제가 나오면 아래 순서로 정리해 봅니다.

1. 정점과 간선 수가 커서 `O(V^2)`가 가능한가, `O(V + E)`가 필요한가?
2. 입력이 트리인지, 일반 그래프인지, 연결 그래프인지 확인했는가?
3. 간선에 방향이나 가중치가 있는가?
4. 거리 문제라면 BFS, Dijkstra, Bellman-Ford 중 어느 조건인가?
5. 연결성만 필요하다면 DFS/BFS 또는 Union-Find로 충분한가?
6. 모든 정점을 싸게 연결하는 문제라면 MST 조건인가?
7. 트리에서 "가장 먼 거리"라면 지름, "균형 잡힌 제거점"이라면 센트로이드를 떠올렸는가?

정리하면, 그래프 문제의 출발점은 표현과 탐색이고, 트리 문제의 출발점은 `n - 1`개 간선과 경로 유일성입니다. 그 위에서 지름은 거리, 센트로이드는 크기, MST는 전체 연결 비용을 묻는 도구로 구분하면 됩니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 연결 요소 세기 문제 추가 | 인접 리스트와 DFS/BFS 방문 배열 확인 | DFS, BFS, visited |
| 표준 | [모임으로 나뉜 팀](/practice/TEAMSIZE) | 연결성만 필요한 상황에서 Union-Find 선택 | component, DSU |
| 응용 | TODO: 트리 지름/센트로이드 문제 추가 | 트리 거리 기준과 크기 기준을 구분 | BFS 두 번, subtree size |
| 함정 | TODO: MST 문제 추가 | 최단거리와 MST를 혼동하지 않기 | Kruskal, cut property |
