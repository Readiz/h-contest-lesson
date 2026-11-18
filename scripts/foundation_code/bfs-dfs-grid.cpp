// bfs-dfs-grid 하네스: 제출 코드 바깥의 로컬 검사.
static char gGrid[MAX_H][MAX_W];
static int gDist[MAX_H][MAX_W];
static Graph gGraph;
static int gVisited[MAX_V], gDistV[MAX_V];

static int sample() {
    int h, w, sy, sx, ty, tx;
    std::cin >> h >> w >> sy >> sx >> ty >> tx;
    for (int y = 0; y < h; ++y) {
        std::string row;
        std::cin >> row;
        for (int x = 0; x < w; ++x) gGrid[y][x] = row[x];
    }
    CHECK(gridDistance(gGrid, h, w, sy, sx, gDist));
    std::printf("%d\n", gDist[ty][tx]);
    return 0;
}

// 독립 기준: 모든 통로 칸 쌍의 거리를 Floyd-Warshall로 구한다.
static std::vector<int> gridOracle(int h, int w, int sy, int sx) {
    const int INF = 1 << 28;
    int n = h * w;
    std::vector<std::vector<int>> d(n, std::vector<int>(n, INF));
    for (int y = 0; y < h; ++y) for (int x = 0; x < w; ++x) {
        if (gGrid[y][x] == '#') continue;
        d[y * w + x][y * w + x] = 0;
        int dy[4] = {-1, 1, 0, 0}, dx[4] = {0, 0, -1, 1};
        for (int k = 0; k < 4; ++k) {
            int ny = y + dy[k], nx = x + dx[k];
            if (ny >= 0 && ny < h && nx >= 0 && nx < w && gGrid[ny][nx] != '#')
                d[y * w + x][ny * w + nx] = 1;
        }
    }
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j)
        if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
    std::vector<int> result(n, -1);
    if (sy >= 0 && sy < h && sx >= 0 && sx < w && gGrid[sy][sx] != '#')
        for (int i = 0; i < n; ++i)
            if (d[sy * w + sx][i] < INF) result[i] = d[sy * w + sx][i];
    return result;
}

static void gridCase(int h, int w, int wallPercent) {
    for (int y = 0; y < h; ++y) for (int x = 0; x < w; ++x)
        gGrid[y][x] = rnd(100) < wallPercent ? '#' : '.';
    int sy = rnd(h + 2) - 1, sx = rnd(w + 2) - 1; // 범위 밖 시작점도 포함
    // 이전 TC의 값이 남아 있는 상태를 흉내 내려고 전체를 쓰레기 값으로 채운다.
    for (int y = 0; y < MAX_H; ++y) for (int x = 0; x < MAX_W; ++x) gDist[y][x] = 777;
    CHECK(gridDistance(gGrid, h, w, sy, sx, gDist));
    auto want = gridOracle(h, w, sy, sx);
    for (int y = 0; y < h; ++y) for (int x = 0; x < w; ++x)
        CHECK(gDist[y][x] == want[y * w + x]);
}

// 독립 기준: n^3 거리 행렬과 단순 라벨 전파.
static void graphCase(int n, int edges, bool undirected) {
    const int INF = 1 << 28;
    gGraph.init(n);
    std::vector<std::vector<int>> d(n, std::vector<int>(n, INF)), reach;
    std::vector<int> label(n);
    for (int i = 0; i < n; ++i) { d[i][i] = 0; label[i] = i; }
    for (int e = 0; e < edges && n > 0; ++e) {
        int u = rnd(n), v = rnd(n);
        CHECK(gGraph.addEdge(u, v));
        d[u][v] = std::min(d[u][v], 1);
        if (undirected) {
            CHECK(gGraph.addEdge(v, u));
            d[v][u] = std::min(d[v][u], 1);
        }
    }
    for (int k = 0; k < n; ++k) for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j)
        if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
    for (int s = 0; s < n; ++s) {
        for (int i = 0; i < n; ++i) gDistV[i] = 99;
        shortestDistance(s, gGraph, n, gDistV);
        for (int i = 0; i < n; ++i) CHECK(gDistV[i] == (d[s][i] < INF ? d[s][i] : -1));
        for (int i = 0; i < n; ++i) gVisited[i] = 0;
        int count = dfsSizeIterative(s, gGraph, gVisited);
        int expected = 0;
        for (int i = 0; i < n; ++i) expected += d[s][i] < INF;
        CHECK(count == expected);
        for (int i = 0; i < n; ++i) CHECK((gVisited[i] != 0) == (d[s][i] < INF));
        for (int i = 0; i < n; ++i) gVisited[i] = 0;
        dfs(s, gGraph, gVisited);
        for (int i = 0; i < n; ++i) CHECK((gVisited[i] != 0) == (d[s][i] < INF));
    }
    if (undirected) { // 연결 요소: 도달 가능한 최소 번호로 대표를 정해 센다.
        int components = 0;
        for (int i = 0; i < n; ++i) {
            bool first = true;
            for (int j = 0; j < i; ++j) if (d[i][j] < INF) first = false;
            components += first;
        }
        for (int i = 0; i < n; ++i) gVisited[i] = 5; // 함수가 초기화해야 한다
        CHECK(countComponents(gGraph, n, gVisited) == components);
    }
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 작은 격자 무작위 비교: 크기가 계속 바뀌는 TC를 한 프로세스에서 이어 실행한다.
    const int walls[4] = {0, 20, 40, 70};
    for (int trial = 0; trial < 300; ++trial)
        gridCase(1 + rnd(5), 1 + rnd(5), walls[rnd(4)]);
    gridCase(0, 0, 0);
    gridCase(0, 4, 0);
    gridCase(5, 0, 0);
    // 큰 TC -> 작은 TC -> 큰 TC. 작은 TC가 끝난 뒤 남은 값이 큰 TC에 섞이면 안 된다.
    for (int size : {500, 2, 500, 1}) {
        for (int y = 0; y < size; ++y) for (int x = 0; x < size; ++x) gGrid[y][x] = '.';
        for (int y = 0; y < MAX_H; ++y) for (int x = 0; x < MAX_W; ++x) gDist[y][x] = 777;
        CHECK(gridDistance(gGrid, size, size, 0, 0, gDist));
        for (int y = 0; y < size; ++y) for (int x = 0; x < size; ++x) CHECK(gDist[y][x] == y + x);
    }
    // 용량 경계: 위 루프의 500 x 500 전체 통로가 한 번씩 큐에 들어갔다. 이번에는 뱀 모양 긴 경로.
    for (int y = 0; y < MAX_H; ++y) for (int x = 0; x < MAX_W; ++x)
        gGrid[y][x] = (y % 2 == 1 && x != ((y / 2) % 2 == 0 ? MAX_W - 1 : 0)) ? '#' : '.';
    CHECK(gridDistance(gGrid, MAX_H, MAX_W, 0, 0, gDist));
    // 짝수 행 250개를 모두 가로로 지나고(각 499칸) 세로로 499칸 내려간다.
    CHECK(gDist[MAX_H - 1][0] == 250 * (MAX_W - 1) + (MAX_H - 1));
    CHECK(gDist[MAX_H - 1][1] == -1);
    CHECK(!gridDistance(gGrid, MAX_H + 1, MAX_W, 0, 0, gDist));
    CHECK(!gridDistance(gGrid, 1, MAX_W + 1, 0, 0, gDist));
    CHECK(!gridDistance(gGrid, -1, 1, 0, 0, gDist));
    // 벽 시작점, 격자 밖 시작점은 전체 -1.
    gGrid[0][0] = '#';
    CHECK(gridDistance(gGrid, MAX_H, MAX_W, 0, 0, gDist) && gDist[0][1] == -1);

    // 그래프: 방향·무방향 무작위, 빈 그래프, 자기 간선·중복 간선 포함.
    for (int trial = 0; trial < 300; ++trial) {
        int n = rnd(9);
        graphCase(n, rnd(2 * n + 3), trial % 2 == 0);
    }
    // 큰 그래프 -> 작은 그래프 -> 큰 그래프.
    for (int n : {60, 3, 0, 40, 1}) graphCase(n, n * 2, true);
    // 용량 경계: 정점 MAX_V개의 경로(무방향, 간선 399998개)와 간선 상한 초과.
    gGraph.init(MAX_V);
    for (int i = 0; i + 1 < MAX_V; ++i) {
        CHECK(gGraph.addEdge(i, i + 1));
        CHECK(gGraph.addEdge(i + 1, i));
    }
    CHECK(gGraph.addEdge(0, 0) && gGraph.addEdge(0, 0));
    CHECK(gGraph.edgeCount == MAX_E);
    CHECK(!gGraph.addEdge(0, 0));
    shortestDistance(0, gGraph, MAX_V, gDistV);
    for (int i = 0; i < MAX_V; ++i) CHECK(gDistV[i] == i);
    for (int i = 0; i < MAX_V; ++i) gVisited[i] = 0;
    CHECK(dfsSizeIterative(MAX_V / 2, gGraph, gVisited) == MAX_V); // 반복형은 깊이와 무관
    CHECK(countComponents(gGraph, MAX_V, gVisited) == 1);
    gGraph.init(MAX_V); // 간선 없음: 연결 요소 MAX_V개
    CHECK(countComponents(gGraph, MAX_V, gVisited) == MAX_V);
    gGraph.init(0);
    CHECK(countComponents(gGraph, 0, gVisited) == 0);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
