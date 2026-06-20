# TSP와 해밀턴 경로: 경로 복원과 메모리

## 6. 경로 문제와 사이클 문제의 차이

문제에서 "다시 시작점으로 돌아오라"고 하지 않는다면 마지막 간선을 더하면 안 됩니다.

```cpp
long long bestPath = INF;

for (int last = 0; last < n; ++last) {
    bestPath = min(bestPath, dp[full - 1][last]);
}
```

반대로 사이클이라면 마지막 정점에서 시작점으로 돌아오는 비용을 반드시 더합니다.

```cpp
long long bestCycle = INF;

for (int last = 1; last < n; ++last) {
    if (cost[last][0] != INF) {
        bestCycle = min(bestCycle, dp[full - 1][last] + cost[last][0]);
    }
}
```

이 차이는 자주 틀리는 지점입니다. "모든 정점을 방문한다"와 "순회한다"는 같은 말이 아닙니다.

## 7. 경로 복원

최소 비용뿐 아니라 실제 방문 순서가 필요하면 부모 상태를 저장합니다.

```cpp
vector<vector<int>> parent(full, vector<int>(n, -1));

for (int mask = 0; mask < full; ++mask) {
    for (int last = 0; last < n; ++last) {
        if (dp[mask][last] == INF) continue;

        for (int next = 0; next < n; ++next) {
            if (mask & (1 << next)) continue;
            if (cost[last][next] == INF) continue;

            int nextMask = mask | (1 << next);
            long long candidate = dp[mask][last] + cost[last][next];
            if (candidate < dp[nextMask][next]) {
                dp[nextMask][next] = candidate;
                parent[nextMask][next] = last;
            }
        }
    }
}
```

마지막 정점을 찾은 뒤 거꾸로 따라갑니다.

```cpp
int mask = full - 1;
int last = bestLast;
vector<int> route;

while (last != -1) {
    route.push_back(last);
    int previous = parent[mask][last];
    mask ^= (1 << last);
    last = previous;
}

reverse(route.begin(), route.end());
route.push_back(0); // TSP cycle이면 시작점으로 복귀
```

`mask`에서 현재 `last` 비트를 제거한 뒤 부모로 이동해야 합니다. 순서를 반대로 하면 잘못된 parent를 따라갈 수 있습니다.

## 8. 메모리 줄이기보다 먼저 정확히 만들기

TSP DP는 메모리가 큽니다. 그래도 처음부터 무리하게 최적화하면 실수가 늘어납니다.

먼저 전체 테이블로 맞춘 뒤, 필요하면 아래를 검토합니다.

- 비용 범위가 작으면 `int`를 쓸 수 있는가?
- 존재 여부 DP라면 `char`, `bitset`을 쓸 수 있는가?
- 시작점을 고정해 불필요한 상태를 줄였는가?
- `mask`가 시작점 `0`을 포함하지 않는 상태를 건너뛰는가?

예를 들어 시작점이 고정된 TSP에서는 `0`번을 포함하지 않는 `mask`는 볼 필요가 없습니다.

```cpp
for (int mask = 0; mask < full; ++mask) {
    if ((mask & 1) == 0) continue;
    // ...
}
```
