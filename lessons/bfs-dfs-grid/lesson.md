# BFS/DFS와 격자 탐색

BFS와 DFS는 그래프에서 갈 수 있는 곳을 빠짐없이 방문하는 가장 기본적인 탐색 방법입니다. 문제에서 정점과 간선이 직접 나오지 않아도, 격자 칸, 지도, 상태 전이, 이동 가능한 위치를 그래프로 보면 같은 도구를 쓸 수 있습니다.

```text
DFS: 한 방향으로 깊게 들어갔다가 돌아온다.
BFS: 시작점에서 가까운 곳부터 차례로 본다.
```

아래 예시는 미방문 정점 표시와 최단거리 계산의 차이를 다룹니다. 인접 목록 표현은 [그래프와 트리](https://h.readiz.com/learn/graph-tree-basics)에 있습니다.

## 그래프로 생각하기

그래프는 정점과 간선으로 이루어집니다.

```text
정점: 위치, 사람, 도시, 상태
간선: 한 번에 이동할 수 있는 관계
```

격자에서는 보통 한 칸이 정점이고, 상하좌우로 이동할 수 있으면 간선이 있다고 봅니다.

```text
....
.##.
....
```

`.` 칸은 지나갈 수 있고, `#` 칸은 벽이라면 각 `.` 칸이 정점입니다. 상하좌우로 붙어 있는 `.` 칸 사이에 간선이 있습니다.

## 발견한 시점에 방문 표시하기

이미 발견한 정점을 다시 넣지 않도록 표시합니다. BFS나 반복 DFS에서는 큐·스택에서 꺼낼 때까지 기다리지 않고 **넣는 순간** 표시해야 여러 이웃이 같은 정점을 중복으로 넣지 않습니다.

## DFS

한 경로를 따라 깊이 들어갔다가 되돌아옵니다. 아래 함수는 `u`와 연결된 모든 정점을 표시합니다.

```cpp
void dfs(int u, const vector<vector<int>>& graph, vector<int>& visited) {
    visited[u] = 1;

    for (int v : graph[u]) {
        if (visited[v]) continue;
        dfs(v, graph, visited);
    }
}
```

길게 이어진 그래프에서는 재귀 깊이도 정점 수만큼 늘어납니다. 실행 환경의 스택 제한을 넘는다면 명시적인 스택으로 바꿉니다. 다음 구현은 방문한 정점 수도 반환합니다.

```cpp
int dfsSizeIterative(int start, const vector<vector<int>>& graph, vector<int>& visited) {
    int size = 0;
    vector<int> stack;

    visited[start] = 1;
    stack.push_back(start);

    while (!stack.empty()) {
        int u = stack.back();
        stack.pop_back();
        size++;

        for (int v : graph[u]) {
            if (visited[v]) continue;
            visited[v] = 1;
            stack.push_back(v);
        }
    }
    return size;
}
```

## BFS로 최단거리 구하기

모든 간선 비용이 1이면 거리 0, 1, 2인 정점 순서로 큐에서 나옵니다. `dist[v] == -1`을 미방문 표시로 함께 사용합니다.

```cpp
vector<int> shortestDistance(int start, const vector<vector<int>>& graph) {
    int n = (int)graph.size();
    vector<int> dist(n, -1);
    queue<int> q;

    dist[start] = 0;
    q.push(start);

    while (!q.empty()) {
        int u = q.front();
        q.pop();

        for (int v : graph[u]) {
            if (dist[v] != -1) continue;
            dist[v] = dist[u] + 1;
            q.push(v);
        }
    }
    return dist;
}
```

새 정점은 현재 거리보다 정확히 1 멀리 있으므로 처음 넣을 때 거리가 확정됩니다. 다른 비용의 간선이 섞이면 이 성질이 깨집니다. 큐의 배열 구현은 [공통 코드](https://h.readiz.com/learn/cpp-contest-basics/sorting-queue-heap)를 참고합니다.

## 연결 요소 세기

무방향 그래프에서 연결 요소 개수는 아직 방문하지 않은 정점마다 탐색을 시작해서 셉니다.

```cpp
int countComponents(const vector<vector<int>>& graph) {
    int n = (int)graph.size();
    vector<int> visited(n, 0);
    int components = 0;

    for (int i = 0; i < n; ++i) {
        if (visited[i]) continue;
        components++;
        dfs(i, graph, visited);
    }
    return components;
}
```

## 격자를 탐색할 때의 경계

격자 칸을 정점으로 보고 상하좌우 이웃을 생성합니다. 다음 좌표를 만든 뒤에는 **배열을 읽기 전에 범위를 확인**해야 합니다. 범위 안이면 벽인지, 이미 방문했는지 검사합니다. 이 순서를 아래 `gridDistance`의 내부 반복문에서 확인할 수 있습니다.

## 격자 BFS 최단거리

상하좌우 이동 비용이 모두 1이면 격자 최단거리는 BFS입니다. 시작점이 유효한 빈 칸이라는 보장이 없다면, 큐에 넣기 전에 범위와 벽 여부를 검사합니다.

```cpp
vector<vector<int>> gridDistance(
    const vector<string>& grid,
    int sy,
    int sx
) {
    int h = (int)grid.size();
    int w = (int)grid[0].size();
    vector<vector<int>> dist(h, vector<int>(w, -1));
    queue<pair<int, int>> q;

    int dy[4] = {-1, 1, 0, 0};
    int dx[4] = {0, 0, -1, 1};

    dist[sy][sx] = 0;
    q.push({sy, sx});

    while (!q.empty()) {
        auto [y, x] = q.front();
        q.pop();

        for (int dir = 0; dir < 4; ++dir) {
            int ny = y + dy[dir];
            int nx = x + dx[dir];

            if (ny < 0 || ny >= h || nx < 0 || nx >= w) continue;
            if (grid[ny][nx] == '#') continue;
            if (dist[ny][nx] != -1) continue;

            dist[ny][nx] = dist[y][x] + 1;
            q.push({ny, nx});
        }
    }
    return dist;
}
```

## 여러 곳에서 동시에 퍼질 때

위 구현에서 시작점 하나를 넣는 부분만 바꿉니다. 모든 유효한 시작점의 거리를 0으로 두고 큐에 넣은 뒤 같은 반복문을 실행합니다. 같은 좌표가 여러 번 주어지면 처음 한 번만 넣습니다.

얻는 거리는 시작점 각각까지의 거리가 아니라 **가장 가까운 시작점까지의 거리**입니다. 불이 여러 곳에서 동시에 번진다면 각 칸에 최초로 도착하는 시간을 한 번의 탐색으로 구할 수 있습니다.

## 상태 그래프

격자 칸만 정점이 되는 것은 아닙니다. 방향, 남은 자원, 열쇠 보유 상태까지 포함해야 할 때도 있습니다.

```text
(y, x)만으로는 부족하다.
로봇 방향까지 같아야 같은 상태다.
남은 배터리나 사용한 특수 이동 횟수가 다르면 다른 상태다.
```

이때 정점은 `(y, x, dir)` 또는 `(y, x, used)` 같은 상태가 됩니다. 방문 배열도 그 차원만큼 늘어납니다.

상태를 넓히면 정점 수가 크게 늘어납니다. `h * w * stateCount`가 시간과 메모리 안에 들어오는지 먼저 계산해야 합니다.

## BFS와 Dijkstra의 차이

BFS가 최단거리를 보장하는 이유는 모든 간선 비용이 같기 때문입니다. 큐에서 먼저 나오는 상태가 항상 더 짧은 거리입니다.

간선 비용이 서로 다르면 일반 BFS는 틀릴 수 있습니다.

| 간선 비용 | 적합한 알고리즘 |
| --- | --- |
| 모두 1 | BFS |
| 0 또는 1 | 0-1 BFS |
| 음수 없음, 여러 양수 | Dijkstra |
| 음수 가능 | Bellman-Ford 등 별도 기법 |

격자라도 이동마다 비용이 다르면 BFS가 아니라 Dijkstra를 검토해야 합니다.

## 시간 복잡도

각 정점과 간선을 한 번씩 보면 됩니다.

```text
인접 리스트 그래프: O(V + E)
격자 상하좌우 탐색: O(HW)
메모리: 방문 배열 또는 거리 배열 O(V)
```

격자에서 각 칸의 이웃은 최대 4개라서 간선 수가 `O(HW)`입니다. 그래서 격자 BFS/DFS도 전체 칸 수에 비례합니다.

상태 그래프에서는 `V`가 실제 상태 수입니다.

```text
위치만 상태: H * W
위치 + 방향: H * W * 4
위치 + 열쇠 bitmask: H * W * 2^K
```

상태를 추가할수록 복잡도가 곱으로 늘어납니다.
