# 그래프와 트리 기본 성질: 트리 지름과 센트로이드

## 5. 트리 지름

트리의 지름은 트리 안에서 가장 먼 두 정점 사이의 거리입니다. 간선 개수로 세기도 하고, 가중치가 있으면 가중치 합으로 세기도 합니다.

가중치가 없는 트리에서는 BFS 두 번으로 지름을 구할 수 있습니다.

```text
1. 아무 정점 A에서 BFS를 해서 가장 먼 정점 X를 찾는다.
2. X에서 다시 BFS를 해서 가장 먼 정점 Y를 찾는다.
3. dist[X][Y]가 트리의 지름이다.
```

트리에서는 경로가 유일하므로, 아무 곳에서 가장 먼 정점은 어떤 지름의 끝점이 됩니다.

```cpp
pair<int, int> farthest(int start, const vector<vector<int>>& tree) {
    int n = (int)tree.size();
    vector<int> dist(n, -1);
    queue<int> q;

    dist[start] = 0;
    q.push(start);

    while (!q.empty()) {
        int u = q.front();
        q.pop();

        for (int v : tree[u]) {
            if (dist[v] != -1) continue;
            dist[v] = dist[u] + 1;
            q.push(v);
        }
    }

    int best = start;
    for (int i = 0; i < n; ++i) {
        if (dist[i] > dist[best]) best = i;
    }
    return {best, dist[best]};
}

int treeDiameter(const vector<vector<int>>& tree) {
    auto [x, ignored] = farthest(0, tree);
    auto [y, diameter] = farthest(x, tree);
    return diameter;
}
```

가중치가 있는 트리에서는 BFS 대신 DFS로 누적 거리를 계산하면 됩니다. 다만 두 번의 BFS/DFS로 지름 끝점을 찾는 알고리즘은 보통 간선 가중치가 비음수라는 조건에서 안전하게 사용합니다. 음수 간선까지 허용하면서 "가장 큰 경로 합"을 묻는다면 지름 공식처럼 끝점 두 번을 고르기보다 트리 DP로 최대 경로를 따로 계산하는 편이 안전합니다.

## 6. 트리 중심과 센트로이드

트리 지름을 배우면 자주 헷갈리는 개념이 두 개 있습니다.

| 개념 | 기준 |
| --- | --- |
| 중심(center) | 모든 정점까지의 최대 거리가 최소가 되는 정점 |
| 센트로이드(centroid) | 제거했을 때 남는 컴포넌트 크기의 최댓값이 최소가 되는 정점 |

중심은 거리 기준이고, 센트로이드는 크기 기준입니다. 같은 정점일 수도 있지만 항상 같지는 않습니다.

센트로이드의 대표 성질은 아래와 같습니다.

```text
정점 c를 제거했을 때 생기는 모든 컴포넌트의 크기가 n / 2 이하이면
c는 트리의 센트로이드다.
```

트리의 센트로이드는 항상 1개 또는 2개 존재합니다. subtree 크기를 한 번 구하면 모든 정점이 센트로이드인지 확인할 수 있습니다.

```cpp
void findCentroids(
    int u,
    int parent,
    const vector<vector<int>>& tree,
    const vector<int>& subtreeSize,
    int n,
    vector<int>& centroids
) {
    int largestPart = n - subtreeSize[u];

    for (int v : tree[u]) {
        if (v == parent) continue;
        largestPart = max(largestPart, subtreeSize[v]);
        findCentroids(v, u, tree, subtreeSize, n, centroids);
    }

    if (largestPart * 2 <= n) {
        centroids.push_back(u);
    }
}
```

`n - subtreeSize[u]`는 `u`의 부모 방향에 남는 컴포넌트 크기입니다. 자식 방향 컴포넌트들은 각 `subtreeSize[v]`입니다. 이 중 최댓값이 `n / 2` 이하이면 `u`를 루트로 삼아도 어느 한쪽이 절반을 넘지 않습니다.
