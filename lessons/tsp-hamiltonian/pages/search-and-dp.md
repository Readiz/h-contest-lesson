# TSP와 해밀턴 경로: 완전탐색과 비트마스크 DP

## 1. 그래프 표현부터 정한다

해밀턴 경로는 보통 간선이 있는지 없는지만 중요합니다.

```cpp
vector<vector<int>> graph(n);
vector<vector<bool>> connected(n, vector<bool>(n, false));
```

TSP는 정점 사이 이동 비용이 필요합니다. 완전 그래프가 아니라면 갈 수 없는 간선을 `INF`로 두고 처리할 수 있습니다.

```cpp
const long long INF = 4e18;
vector<vector<long long>> cost(n, vector<long long>(n, INF));

for (int i = 0; i < n; ++i) {
    cost[i][i] = 0;
}
```

문제에서 "어느 도시에서든 어느 도시로든 이동할 수 있다"고 하면 완전 그래프입니다. 그렇지 않다면 마지막에 시작점으로 돌아오는 간선이 있는지도 반드시 확인해야 합니다.

## 2. 완전탐색: 모든 방문 순서 시험

가장 직접적인 TSP 풀이는 시작점을 하나 고정하고, 나머지 정점의 방문 순서를 모두 시험하는 것입니다.

```cpp
const long long INF = 4e18;
vector<int> order;

for (int v = 1; v < n; ++v) {
    order.push_back(v);
}

long long answer = INF;

do {
    long long total = 0;
    int current = 0;
    bool ok = true;

    for (int next : order) {
        if (cost[current][next] == INF) {
            ok = false;
            break;
        }
        total += cost[current][next];
        current = next;
    }

    if (ok && cost[current][0] != INF) {
        answer = min(answer, total + cost[current][0]);
    }
} while (next_permutation(order.begin(), order.end()));
```

시작점을 `0`으로 고정해도 되는 이유는 순회 사이클에서는 어디서 출발해도 같은 원형 순서를 표현하기 때문입니다. 그래도 경우의 수는 `(n - 1)!`이므로 금방 커집니다.

해밀턴 경로 존재 여부도 순열로 확인할 수 있습니다.

```cpp
vector<int> order(n);
iota(order.begin(), order.end(), 0);

bool exists = false;

do {
    bool ok = true;
    for (int i = 0; i + 1 < n; ++i) {
        if (!connected[order[i]][order[i + 1]]) {
            ok = false;
            break;
        }
    }
    if (ok) {
        exists = true;
        break;
    }
} while (next_permutation(order.begin(), order.end()));
```

이 방식은 구현이 단순하고 디버깅하기 좋습니다. DP 풀이를 작성하기 전에 작은 입력 검증용 brute force로 남겨 두면 도움이 됩니다.

## 3. 중복을 보는 관점

완전탐색은 같은 부분 문제를 여러 번 풉니다.

```text
0 -> 1 -> 2 까지 방문하고 2에 있음
0 -> 3 -> 2 까지 방문하고 2에 있음
```

두 상태는 방문한 집합이 다르므로 미래 선택지가 다릅니다. 반대로 아래 두 경로는 미래 입장에서 같은 상태입니다.

```text
0 -> 1 -> 3 -> 2
0 -> 3 -> 1 -> 2
```

둘 다 `{0, 1, 2, 3}`을 방문했고 마지막 정점이 `2`라면, 앞으로 갈 수 있는 정점 집합은 같습니다. TSP에서는 그 상태에 도달하는 최소 비용만 남기면 됩니다.

그래서 비트마스크 DP의 핵심 상태는 다음입니다.

```text
mask = 지금까지 방문한 정점 집합
last = 현재 마지막 정점
```

## 4. 해밀턴 경로 존재 여부 DP

먼저 비용이 없는 존재 여부 문제부터 봅시다.

```text
dp[mask][last] = mask에 들어 있는 정점들을 모두 한 번씩 방문했고,
                 마지막 정점이 last인 경로가 존재하는가?
```

시작점을 고정하지 않는 해밀턴 경로라면 모든 단일 정점에서 시작할 수 있습니다.

```cpp
int full = 1 << n;
vector<vector<char>> dp(full, vector<char>(n, false));

for (int start = 0; start < n; ++start) {
    dp[1 << start][start] = true;
}

for (int mask = 0; mask < full; ++mask) {
    for (int last = 0; last < n; ++last) {
        if (!dp[mask][last]) continue;

        for (int next = 0; next < n; ++next) {
            if (mask & (1 << next)) continue;
            if (!connected[last][next]) continue;

            dp[mask | (1 << next)][next] = true;
        }
    }
}

bool hasHamiltonianPath = false;
for (int last = 0; last < n; ++last) {
    hasHamiltonianPath = hasHamiltonianPath || dp[full - 1][last];
}
```

해밀턴 사이클은 마지막 정점에서 시작점으로 돌아오는 간선을 추가로 확인해야 합니다. 시작점을 `0`으로 고정하면 상태 수가 줄고, 사이클 확인도 명확해집니다.

```cpp
vector<vector<char>> dp(full, vector<char>(n, false));
dp[1][0] = true;

for (int mask = 0; mask < full; ++mask) {
    for (int last = 0; last < n; ++last) {
        if (!dp[mask][last]) continue;

        for (int next = 0; next < n; ++next) {
            if (mask & (1 << next)) continue;
            if (!connected[last][next]) continue;
            dp[mask | (1 << next)][next] = true;
        }
    }
}

bool hasHamiltonianCycle = false;
for (int last = 1; last < n; ++last) {
    if (dp[full - 1][last] && connected[last][0]) {
        hasHamiltonianCycle = true;
    }
}
```

시간 복잡도는 `O(2^n * n^2)`, 메모리는 `O(2^n * n)`입니다.

## 5. TSP DP: Held-Karp 알고리즘

TSP에서는 `true/false` 대신 최소 비용을 저장합니다.

```text
dp[mask][last] = 0번에서 시작해 mask의 정점들을 방문했고,
                 last에서 끝나는 최소 비용
```

```cpp
const long long INF = 4e18;
int full = 1 << n;
vector<vector<long long>> dp(full, vector<long long>(n, INF));

dp[1][0] = 0;

for (int mask = 0; mask < full; ++mask) {
    for (int last = 0; last < n; ++last) {
        if (dp[mask][last] == INF) continue;

        for (int next = 0; next < n; ++next) {
            if (mask & (1 << next)) continue;
            if (cost[last][next] == INF) continue;

            int nextMask = mask | (1 << next);
            dp[nextMask][next] = min(
                dp[nextMask][next],
                dp[mask][last] + cost[last][next]
            );
        }
    }
}

long long answer = INF;
for (int last = 1; last < n; ++last) {
    if (cost[last][0] == INF) continue;
    answer = min(answer, dp[full - 1][last] + cost[last][0]);
}
```

이 알고리즘을 Held-Karp DP라고 부릅니다. 완전탐색의 `(n - 1)!`보다 훨씬 낫지만, 여전히 지수 시간입니다. `n = 20`이면 상태가 약 `2^20 * 20`, 즉 2천만 개 수준입니다. `long long` 테이블이면 메모리도 커지므로 제한을 먼저 계산해야 합니다.
