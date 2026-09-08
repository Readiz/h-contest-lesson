# 그래프와 트리 기본 성질

## 그래프 표현

인접 리스트의 `graph[u]`에는 `u`에서 갈 수 있는 정점을 저장합니다. 무방향 간선 `u-v`는 양쪽 목록에 넣고, 방향 간선 `u→v`는 `u`의 목록에만 넣습니다.

가중치가 있으면 이웃 정점 번호와 이동 비용을 함께 저장합니다.

인접 행렬은 `adj[u][v]`처럼 바로 확인할 수 있어서 편하지만, 메모리가 `O(n^2)`입니다. 정점 수가 크고 간선 수가 적은 일반적인 문제에서는 인접 리스트가 기본입니다.

| 표현 | 메모리 | 좋은 경우 |
| --- | --- | --- |
| 인접 리스트 | `O(V + E)` | 정점/간선이 큰 대부분의 문제 |
| 인접 행렬 | `O(V^2)` | 정점 수가 작고 두 정점 연결 여부를 자주 볼 때 |
| 간선 리스트 | `O(E)` | Kruskal처럼 간선을 정렬하거나 전체 간선을 훑을 때 |

연결된 영역을 직접 순회하는 구현은 [BFS/DFS](https://h.readiz.com/learn/bfs-dfs-grid)에 있습니다. [모임으로 나뉜 팀](/practice/TEAMSIZE)처럼 경로가 필요 없는 문제에서는 [Union-Find](https://h.readiz.com/learn/union-find)로 관계를 합칠 수도 있습니다.

## 트리의 기본 성질

정점이 `n`개인 무방향 그래프가 트리라면 항상 간선은 `n - 1`개입니다. 또 임의의 두 정점 사이에는 단순 경로가 정확히 하나만 있습니다.

간선 하나를 제거하면 두 컴포넌트로 나뉩니다. 입력이 트리인지 판정할 때는 간선 수 `n - 1`과 연결 여부를 함께 봐야 합니다. 간선 수만 같아도 일부 정점이 떨어져 있고 나머지에 사이클이 있을 수 있습니다.

## 트리를 루트 기준으로 보기

트리는 원래 루트가 없을 수 있습니다. 하지만 DFS/BFS를 시작할 정점을 하나 잡으면 부모, 깊이, subtree를 정의할 수 있습니다.

```cpp
void buildTree(
    int u,
    int parent,
    const vector<vector<int>>& tree,
    vector<int>& depth,
    vector<int>& subtreeSize
) {
    subtreeSize[u] = 1;
    for (int v : tree[u]) {
        if (v == parent) continue;
        depth[v] = depth[u] + 1;
        buildTree(v, u, tree, depth, subtreeSize);
        subtreeSize[u] += subtreeSize[v];
    }
}
```

`parent`를 인자로 들고 다니면 방문 배열 없이도 부모로 되돌아가는 간선을 건너뛸 수 있습니다. 단, 입력이 트리가 아니라 일반 그래프라면 방문 배열이 필요합니다.

트리에서 subtree 크기는 많은 문제의 기본 재료입니다.

```text
subtreeSize[u] = u를 루트로 하는 부분트리의 정점 수
```

이 값으로 균형 잡힌 루트, 센트로이드, 간선을 끊었을 때 생기는 컴포넌트 크기 등을 계산합니다.

## 트리 구조를 이용하는 풀이

- [지름과 센트로이드](pages/tree-diameter-centroid.md): 거리로 가장 먼 두 점과, 정점 수를 균형 있게 나누는 점을 구합니다.
- [최소 신장 트리](pages/mst-kruskal-prim.md): 간선을 골라 전체 연결 비용을 최소화합니다.
