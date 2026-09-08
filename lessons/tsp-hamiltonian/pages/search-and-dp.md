# TSP와 해밀턴 경로: 완전탐색과 비트마스크 DP

## 간선과 비용의 의미

해밀턴 경로에서는 `connected[u][v]`로 간선 유무를, TSP에서는 `cost[u][v]`로 이동 비용을 나타냅니다. 아래 코드의 `INF`는 갈 수 없는 간선입니다. `n >= 2`를 가정하며, 비용 합이 `INF`와 정수 범위를 넘지 않아야 합니다.

## 완전탐색: 모든 방문 순서 시험

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

작은 입력에서는 이 결과를 DP의 기준 답으로 사용할 수 있습니다.

## 중복을 보는 관점

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

## 해밀턴 경로 존재 여부 DP

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

해밀턴 사이클은 `dp[1][0]`만 시작 상태로 두고, 마지막 정점에서 0으로 돌아오는 간선까지 확인합니다. 시작점을 고정하지 않는 경로와 초기값을 혼동하면 안 됩니다.

시간은 `O(2^n × n²)`, 메모리는 `O(2^n × n)`입니다.

## TSP DP: Held-Karp 알고리즘

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

시작점으로 돌아오지 않는 경로가 목표라면 마지막 `cost[last][0]`을 더하지 않고 `dp[full - 1][last]`의 최솟값만 고릅니다.

## 경로 복원과 메모리

방문 순서가 필요하면 `parent[mask][last]`를 -1로 초기화합니다. 더 작은 비용으로 `dp[nextMask][next]`를 갱신하는 순간 `parent[nextMask][next] = last`도 기록합니다. 최종 비용을 결정한 정점을 `bestLast`에 저장한 뒤 거꾸로 따라갑니다.

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

현재 `last`의 부모를 읽고 그 비트를 지운 뒤 부모로 이동합니다. 순서를 바꾸면 다른 상태의 부모를 읽게 됩니다.

`n = 20`에서 `long long dp[1 << n][n]`은 160MiB이고 `int` 부모 테이블은 80MiB를 더 씁니다. 시작점을 포함하지 않는 마스크를 **건너뛰기만 해서는 할당한 메모리가 줄지 않습니다**. 메모리가 부족하다면 시작점 비트를 제외한 별도 인덱스로 테이블을 만들거나, 비용 범위가 허용할 때 자료형을 줄여야 합니다.
