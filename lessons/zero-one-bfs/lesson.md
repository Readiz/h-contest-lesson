# 0-1 BFS

0-1 BFS는 간선 비용이 `0` 또는 `1`인 그래프에서 최단거리를 구하는 알고리즘입니다. 일반 BFS처럼 큐를 쓰지만, 비용이 0인 이동은 앞에 넣고 비용이 1인 이동은 뒤에 넣기 위해 `deque`를 사용합니다.

## 간선 비용이 0 또는 1일 때

일반 BFS는 모든 간선 비용이 1일 때만 최단거리를 보장합니다. 비용이 0인 간선이 섞이면, 한 번 이동했는데 거리 증가가 없을 수 있습니다.

```text
u --0--> v  거리 증가 없음
u --1--> w  거리 1 증가
```

이때 Dijkstra를 써도 됩니다. 하지만 비용이 0과 1뿐이라면 우선순위 큐 대신 deque만으로 더 간단하게 처리할 수 있습니다.

## deque를 쓰는 이유

현재 정점 `u`에서 이웃 `v`로 가는 비용이 `0`이면 `dist[v]`는 `dist[u]`와 같습니다. 이 정점은 지금 처리 중인 거리 그룹과 같은 우선순위이므로 deque 앞쪽에 넣습니다.

비용이 `1`이면 다음 거리 그룹이므로 뒤쪽에 넣습니다.

```text
cost 0: push_front
cost 1: push_back
```

이렇게 하면 deque의 앞쪽에는 항상 현재까지 가장 작은 거리 후보가 옵니다.

## 기본 구현

```cpp
struct Edge {
    int to;
    int cost; // 0 or 1
};

vector<int> zeroOneBfs(const vector<vector<Edge>>& graph, int start) {
    const int INF = 1e9;
    int n = (int)graph.size();
    vector<int> dist(n, INF);
    deque<int> dq;

    dist[start] = 0;
    dq.push_back(start);

    while (!dq.empty()) {
        int u = dq.front();
        dq.pop_front();

        for (const Edge& e : graph[u]) {
            int nd = dist[u] + e.cost;
            if (nd >= dist[e.to]) continue;
            dist[e.to] = nd;
            if (e.cost == 0) dq.push_front(e.to);
            else dq.push_back(e.to);
        }
    }

    return dist;
}
```

일반 BFS처럼 처음 발견한 순간 방문을 확정하지 않습니다. 더 짧은 0비용 경로가 나중에 발견될 수 있어 같은 정점이 deque에 여러 번 들어갈 수 있습니다. deque에 넣은 거리 후보는 두 인접 거리 층으로 정렬됩니다. 한 정점은 같은 층의 0비용 경로로 한 번 더 개선될 수 있지만 반복 개선이 누적되지는 않아 전체 복잡도는 `O(V + E)`입니다.

## 격자 상태 그래프 예시

방향을 바꾸는 비용이 1이고, 같은 방향으로 가는 비용이 0인 격자 문제를 생각해 봅시다. 상태는 `(r, c, dir)`이고, 이동 비용은 방향이 바뀌는지에 따라 정합니다.

이런 문제는 단순 칸 방문 배열로는 부족합니다. 같은 칸이라도 어떤 방향으로 들어왔는지에 따라 다음 비용이 달라지므로 방향까지 상태에 포함해야 합니다.

## 시간 복잡도

| 작업 | 시간 |
| --- | --- |
| 초기화 | `O(V)` |
| 간선 relax 전체 | `O(E)` |
| deque 삽입/삭제 | `O(V + E)` |
| 전체 | `O(V + E)` |
| 메모리 | `O(V + E)` |
