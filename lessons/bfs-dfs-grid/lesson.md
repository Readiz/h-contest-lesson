# BFS/DFS와 격자 탐색

BFS와 DFS는 그래프에서 갈 수 있는 곳을 빠짐없이 방문하는 가장 기본적인 탐색 방법입니다. 문제에서 정점과 간선이 직접 나오지 않아도, 격자 칸, 지도, 상태 전이, 이동 가능한 위치를 그래프로 보면 같은 도구를 쓸 수 있습니다.

```text
DFS: 한 방향으로 깊게 들어갔다가 돌아온다.
BFS: 시작점에서 가까운 곳부터 차례로 본다.
```

연결 여부, 연결 요소 개수, 섬의 넓이, 격자 최단거리, 로봇 이동 문제의 기본 뼈대가 모두 여기에서 나옵니다.

## 1. 그래프로 생각하기

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

## 2. 방문 배열

탐색에서 가장 중요한 것은 이미 본 정점을 다시 보지 않는 것입니다. 그렇지 않으면 사이클이 있는 그래프에서 무한히 돌 수 있습니다.

```cpp
vector<int> visited(n, 0);
```

정점 `u`를 처음 방문할 때 표시합니다.

```cpp
visited[u] = 1;
```

인접한 정점 `v`를 볼 때 이미 방문했다면 건너뜁니다.

```cpp
if (visited[v]) continue;
```

BFS든 DFS든 이 원칙은 같습니다.

## 3. DFS

DFS는 깊게 들어가는 탐색입니다. 재귀로 구현하면 코드가 짧습니다.

```cpp
void dfs(int u, const vector<vector<int>>& graph, vector<int>& visited) {
    visited[u] = 1;

    for (int v : graph[u]) {
        if (visited[v]) continue;
        dfs(v, graph, visited);
    }
}
```

DFS는 연결 요소를 세거나, 한 컴포넌트의 크기를 구하거나, 트리에서 부모와 subtree를 계산할 때 자주 씁니다.

```cpp
int dfsSize(int u, const vector<vector<int>>& graph, vector<int>& visited) {
    visited[u] = 1;
    int size = 1;

    for (int v : graph[u]) {
        if (visited[v]) continue;
        size += dfsSize(v, graph, visited);
    }
    return size;
}
```

재귀 DFS는 정점 수가 크고 경로가 길면 스택 오버플로가 날 수 있습니다. 그런 환경에서는 반복문 스택으로 바꿉니다.

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

반복 DFS에서는 스택에 넣을 때 방문 표시를 하는 편이 중복 push를 막기 쉽습니다.

## 4. BFS

BFS는 가까운 정점부터 보는 탐색입니다. 큐를 사용합니다.

```cpp
#include <queue>
#include <vector>
using namespace std;

void bfs(int start, const vector<vector<int>>& graph, vector<int>& visited) {
    queue<int> q;

    visited[start] = 1;
    q.push(start);

    while (!q.empty()) {
        int u = q.front();
        q.pop();

        for (int v : graph[u]) {
            if (visited[v]) continue;
            visited[v] = 1;
            q.push(v);
        }
    }
}
```

간선 비용이 모두 1이라면 BFS로 최단거리도 구할 수 있습니다.

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

`dist[v] == -1`을 방문하지 않았다는 뜻으로 같이 쓰면 별도 `visited` 배열이 없어도 됩니다.

## 5. 연결 요소 세기

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

각 컴포넌트의 크기가 필요하면 `dfsSize` 또는 BFS로 방문한 개수를 반환하면 됩니다.

```text
팀 묶기, 섬 개수, 연결된 방 개수, 같은 색 영역 크기
```

이런 표현이 나오면 연결 요소 탐색을 먼저 떠올릴 수 있습니다.

## 6. 격자 방향 배열

격자 탐색에서는 상하좌우 이동을 배열로 둡니다.

```cpp
int dy[4] = {-1, 1, 0, 0};
int dx[4] = {0, 0, -1, 1};
```

현재 칸 `(y, x)`에서 다음 칸은 아래처럼 만듭니다.

```cpp
for (int dir = 0; dir < 4; ++dir) {
    int ny = y + dy[dir];
    int nx = x + dx[dir];
}
```

경계 확인은 항상 먼저 합니다.

```cpp
if (ny < 0 || ny >= h || nx < 0 || nx >= w) continue;
```

그다음 벽인지, 이미 방문했는지 확인합니다.

```cpp
if (grid[ny][nx] == '#') continue;
if (visited[ny][nx]) continue;
```

이 순서가 중요합니다. 경계 밖의 `grid[ny][nx]`를 먼저 읽으면 런타임 에러가 납니다.

## 7. 격자 BFS 최단거리

상하좌우 이동 비용이 모두 1이면 격자 최단거리는 BFS입니다.

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

목표 칸에 도착하자마자 답을 반환해도 됩니다. 단, 큐에 넣을 때 거리 값을 확정한다는 점은 유지해야 합니다.

```cpp
if (ny == targetY && nx == targetX) {
    return dist[ny][nx];
}
```

## 8. Flood Fill

Flood fill은 같은 성질을 가진 인접 칸을 한 덩어리로 칠하거나 세는 탐색입니다. 그림판의 채우기 기능과 비슷합니다.

아래 코드는 시작 칸과 같은 문자를 가진 영역의 크기를 구합니다.

```cpp
int floodFillSize(vector<string>& grid, int sy, int sx) {
    int h = (int)grid.size();
    int w = (int)grid[0].size();
    char target = grid[sy][sx];
    queue<pair<int, int>> q;

    int dy[4] = {-1, 1, 0, 0};
    int dx[4] = {0, 0, -1, 1};

    grid[sy][sx] = '.';
    q.push({sy, sx});

    int size = 0;
    while (!q.empty()) {
        auto [y, x] = q.front();
        q.pop();
        size++;

        for (int dir = 0; dir < 4; ++dir) {
            int ny = y + dy[dir];
            int nx = x + dx[dir];

            if (ny < 0 || ny >= h || nx < 0 || nx >= w) continue;
            if (grid[ny][nx] != target) continue;

            grid[ny][nx] = '.';
            q.push({ny, nx});
        }
    }
    return size;
}
```

방문 배열 대신 `grid` 자체를 바꾸는 방식입니다. 원본 격자가 나중에 필요하다면 별도 `visited` 배열을 써야 합니다.

## 9. 다중 시작점 BFS

시작점이 여러 개일 때도 BFS는 그대로 쓸 수 있습니다. 모든 시작점을 거리 0으로 큐에 넣고 시작합니다.

```cpp
vector<vector<int>> multiSourceBfs(
    const vector<string>& grid,
    const vector<pair<int, int>>& starts
) {
    int h = (int)grid.size();
    int w = (int)grid[0].size();
    vector<vector<int>> dist(h, vector<int>(w, -1));
    queue<pair<int, int>> q;

    for (auto [y, x] : starts) {
        dist[y][x] = 0;
        q.push({y, x});
    }

    int dy[4] = {-1, 1, 0, 0};
    int dx[4] = {0, 0, -1, 1};

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

가장 가까운 출발점까지의 거리, 여러 불씨가 퍼지는 시간, 여러 병원이나 충전소 중 가장 가까운 곳 같은 문제에 쓸 수 있습니다.

## 10. 상태 그래프

격자 칸만 정점이 되는 것은 아닙니다. 방향, 남은 자원, 열쇠 보유 상태까지 포함해야 할 때도 있습니다.

```text
(y, x)만으로는 부족하다.
로봇 방향까지 같아야 같은 상태다.
남은 배터리나 사용한 특수 이동 횟수가 다르면 다른 상태다.
```

이때 정점은 `(y, x, dir)` 또는 `(y, x, used)` 같은 상태가 됩니다. 방문 배열도 그 차원만큼 늘어납니다.

```cpp
vector<vector<vector<int>>> dist(
    h,
    vector<vector<int>>(w, vector<int>(4, -1))
);
```

상태를 넓히면 정점 수가 크게 늘어납니다. `h * w * stateCount`가 시간과 메모리 안에 들어오는지 먼저 계산해야 합니다.

## 11. BFS와 Dijkstra의 차이

BFS가 최단거리를 보장하는 이유는 모든 간선 비용이 같기 때문입니다. 큐에서 먼저 나오는 상태가 항상 더 짧은 거리입니다.

간선 비용이 서로 다르면 일반 BFS는 틀릴 수 있습니다.

| 간선 비용 | 적합한 알고리즘 |
| --- | --- |
| 모두 1 | BFS |
| 0 또는 1 | 0-1 BFS |
| 음수 없음, 여러 양수 | Dijkstra |
| 음수 가능 | Bellman-Ford 등 별도 기법 |

격자라도 이동마다 비용이 다르면 BFS가 아니라 Dijkstra를 검토해야 합니다.

## 12. 시간 복잡도

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

## 13. 자주 하는 실수

첫 번째 실수는 방문 표시 시점입니다. BFS에서 큐에서 꺼낼 때 방문 표시를 하면 같은 정점이 큐에 여러 번 들어갈 수 있습니다. 보통 큐에 넣는 순간 방문 표시를 합니다.

두 번째 실수는 경계 확인보다 배열 접근을 먼저 하는 것입니다.

```cpp
// 잘못된 순서
if (grid[ny][nx] == '#') continue;
if (ny < 0 || ny >= h || nx < 0 || nx >= w) continue;
```

경계 밖 접근은 즉시 문제가 됩니다. 항상 경계부터 확인합니다.

세 번째 실수는 BFS로 풀 수 없는 가중치 문제를 BFS로 푸는 것입니다. 이동 비용이 다르면 Dijkstra를 떠올립니다.

네 번째 실수는 시작점 자체가 벽이거나 범위 밖인 경우를 처리하지 않는 것입니다. 입력 조건이 보장하지 않는다면 탐색 시작 전에 확인해야 합니다.

## 14. 문제를 볼 때 체크할 조건

1. 한 번의 이동 비용이 모두 같은가?
2. 방문해야 하는 대상이 정점인가, 격자 칸인가, 더 큰 상태인가?
3. 같은 상태를 다시 방문하지 않도록 표시할 수 있는가?
4. 연결 요소 크기/개수인지, 최단거리인지 구분했는가?
5. 격자라면 상하좌우인지, 대각선까지 포함하는지 확인했는가?

연결성만 필요하면 DFS와 BFS 중 편한 것을 쓰면 됩니다. 최단 칸 수가 필요하면 BFS를 선택합니다. 이동 비용이 달라지는 순간부터는 Dijkstra 같은 다른 최단거리 알고리즘을 검토해야 합니다.

## 15. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 연결 요소 세기 문제 추가 | 방문 배열과 DFS/BFS 기본 구조 확인 | connected component |
| 표준 | TODO: 격자 최단거리 문제 추가 | 큐에 넣는 순간 방문 표시하기 | grid BFS, distance |
| 응용 | TODO: 여러 시작점 BFS 문제 추가 | 시작점을 한꺼번에 큐에 넣고 거리 확산 | multi-source BFS |
| 함정 | TODO: 위치에 방향/열쇠가 붙는 상태 그래프 문제 추가 | 방문 배열 차원을 상태에 맞게 확장 | state graph |
