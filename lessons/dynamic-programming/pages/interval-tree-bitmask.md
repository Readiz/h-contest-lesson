# 동적 계획법: 구간, 트리, 비트마스크 DP

## 8. 구간 DP

구간 DP는 어떤 연속 구간 `[l, r]`의 답을 더 작은 구간들의 답으로 합쳐 만드는 방식입니다. 괄호 묶기, 파일 합치기, 행렬 곱셈 순서처럼 "어디서 나눌지"를 고르는 문제가 자주 여기에 들어갑니다.

```text
dp[l][r] = l부터 r까지 하나로 합치는 최소 비용
dp[l][r] = min(dp[l][k] + dp[k + 1][r] + cost(l, r))
```

길이가 짧은 구간부터 채워야 합니다.

```cpp
const long long INF = 4e18;
vector<vector<long long>> dp(n, vector<long long>(n, 0));

for (int len = 2; len <= n; ++len) {
    for (int l = 0; l + len - 1 < n; ++l) {
        int r = l + len - 1;
        dp[l][r] = INF;

        for (int k = l; k < r; ++k) {
            long long candidate = dp[l][k] + dp[k + 1][r] + cost(l, r);
            dp[l][r] = min(dp[l][r], candidate);
        }
    }
}
```

구간 DP의 실수는 보통 순서에서 나옵니다. `dp[l][r]`를 계산하기 전에 `dp[l][k]`와 `dp[k + 1][r]`가 이미 있어야 하므로 `len`을 작은 값부터 키웁니다.

## 9. 트리 DP

트리에서는 부모를 하나 정하면 자식 부분트리들이 서로 독립이 됩니다. 이 구조를 이용해 각 정점의 부분트리 답을 계산합니다.

대표 예시로, 인접한 두 정점을 동시에 고를 수 없을 때 고른 정점 가중치 합의 최댓값을 구해 봅시다.

```text
dp[u][0] = u를 고르지 않았을 때 u의 부분트리 최대값
dp[u][1] = u를 골랐을 때 u의 부분트리 최대값
```

`u`를 고르면 자식은 고를 수 없습니다. `u`를 고르지 않으면 자식은 고르거나 고르지 않거나 더 좋은 쪽을 택합니다.

```cpp
void dfs(int u, int parent) {
    dp[u][0] = 0;
    dp[u][1] = weight[u];

    for (int v : graph[u]) {
        if (v == parent) continue;
        dfs(v, u);

        dp[u][0] += max(dp[v][0], dp[v][1]);
        dp[u][1] += dp[v][0];
    }
}
```

트리 DP에서는 "부모로 다시 올라가는 간선"을 제외해야 하고, 루트를 어디로 잡아도 답이 같은지 또는 루트 선택이 의미 있는지 확인해야 합니다.

## 10. 비트마스크 DP

원소 수가 20개 안팎이면, 선택한 원소 집합을 비트마스크로 표현할 수 있습니다.

대표적인 예시는 작은 TSP입니다.

```text
dp[mask][last] = mask에 포함된 정점들을 방문했고, last에서 끝나는 최소 비용
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

            int nextMask = mask | (1 << next);
            dp[nextMask][next] = min(
                dp[nextMask][next],
                dp[mask][last] + cost[last][next]
            );
        }
    }
}
```

상태 수가 `2^n * n`이므로 `n`이 조금만 커져도 불가능합니다. 비트마스크 DP는 입력 크기를 가장 먼저 확인해야 합니다.
