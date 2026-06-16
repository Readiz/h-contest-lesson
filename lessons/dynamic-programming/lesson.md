# 동적 계획법

동적 계획법(Dynamic Programming, DP)은 큰 문제를 작은 부분문제로 나누고, 이미 계산한 결과를 다시 쓰는 풀이 방법입니다. 한국어로는 보통 **동적 계획법** 또는 그냥 **DP**라고 부릅니다.

DP가 잘 맞는 문제에는 두 가지 성질이 있습니다.

- **부분문제가 겹친다.** 같은 계산이 여러 경로에서 반복해서 등장합니다.
- **최적 부분 구조가 있다.** 큰 답을 작은 답들의 조합으로 만들 수 있습니다.

DP의 어려운 점은 공식을 외우는 것이 아니라 `무엇을 상태로 둘지`, `어떤 순서로 채울지`, `이전 상태에서 현재 상태로 어떻게 넘어올지`를 정하는 것입니다. 이 문서는 기초 형태부터 다양한 실전 기법까지 한 번에 연결합니다.

## 1. DP를 설계하는 네 가지 질문

DP 풀이를 시작할 때는 아래 네 가지를 먼저 적어 봅니다.

| 질문 | 의미 |
| --- | --- |
| 상태 | `dp[i]` 또는 `dp[i][j]`가 정확히 무엇을 뜻하는가? |
| 초기값 | 가장 작은 문제의 답은 무엇인가? |
| 전이 | 더 작은 상태에서 현재 상태를 어떻게 만드는가? |
| 순서 | 전이에 필요한 값이 먼저 계산되도록 어떤 순서로 훑는가? |

예를 들어 피보나치 수열은 가장 단순한 DP입니다.

```text
dp[i] = i번째 피보나치 수
dp[0] = 0, dp[1] = 1
dp[i] = dp[i - 1] + dp[i - 2]
작은 i부터 큰 i로 계산
```

```cpp
vector<long long> dp(n + 1, 0);
dp[0] = 0;
dp[1] = 1;

for (int i = 2; i <= n; ++i) {
    dp[i] = dp[i - 1] + dp[i - 2];
}
```

피보나치는 너무 쉽지만, DP의 핵심 질문 네 개가 모두 들어 있습니다.

## 2. Top-down 메모이제이션

재귀로 문제를 자연스럽게 표현하고, 계산한 값을 배열에 저장하는 방식을 **메모이제이션**이라고 합니다. 필요할 때만 상태를 계산하므로 상태 공간이 크지만 실제로 방문하는 상태가 적을 때 유용합니다.

```cpp
vector<long long> memo(n + 1, -1);

long long fib(int x) {
    if (x <= 1) return x;
    if (memo[x] != -1) return memo[x];

    memo[x] = fib(x - 1) + fib(x - 2);
    return memo[x];
}
```

top-down은 점화식을 코드로 옮기기 쉽습니다. 대신 재귀 깊이가 커질 수 있고, 방문 여부를 표현할 수 없는 값과 실제 답이 겹치지 않게 조심해야 합니다. 답이 `-1`이 될 수 있는 문제라면 별도의 `visited` 배열을 두는 편이 안전합니다.

## 3. Bottom-up 테이블 채우기

작은 상태부터 큰 상태까지 반복문으로 채우는 방식은 **bottom-up DP**입니다. 순회 순서를 명확히 잡을 수 있고, 재귀 깊이 걱정이 없습니다.

```cpp
vector<long long> dp(n + 1, 0);
dp[0] = 1;

for (int i = 1; i <= n; ++i) {
    dp[i] = dp[i - 1];
    if (i >= 2) dp[i] += dp[i - 2];
}
```

bottom-up에서 가장 중요한 것은 반복문 순서입니다. `dp[i]`를 계산할 때 필요한 `dp[i - 1]`, `dp[i - 2]`가 이미 계산되어 있어야 합니다.

## 4. 2차원 DP: 격자 경로 세기

격자에서 오른쪽 또는 아래로만 이동해 `(0, 0)`에서 `(h - 1, w - 1)`까지 가는 경우의 수를 구해 봅시다. 장애물이 있는 칸은 지나갈 수 없습니다.

상태는 자연스럽게 잡을 수 있습니다.

```text
dp[r][c] = (0, 0)에서 (r, c)까지 오는 경로 수
```

현재 칸에 도착하는 방법은 위에서 내려오거나 왼쪽에서 오는 것뿐입니다.

```cpp
vector<vector<long long>> dp(h, vector<long long>(w, 0));
dp[0][0] = 1;

for (int r = 0; r < h; ++r) {
    for (int c = 0; c < w; ++c) {
        if (blocked[r][c]) {
            dp[r][c] = 0;
            continue;
        }
        if (r > 0) dp[r][c] += dp[r - 1][c];
        if (c > 0) dp[r][c] += dp[r][c - 1];
    }
}
```

이 문제에서는 위쪽 행과 왼쪽 칸이 먼저 계산되어야 하므로 `r`을 위에서 아래로, `c`를 왼쪽에서 오른쪽으로 훑습니다.

## 5. 최소 동전 개수: 그리디가 깨질 때

동전 단위가 `{1, 3, 4}`이고 6원을 만들 때, 가장 큰 동전부터 고르면 `4 + 1 + 1`로 3개가 됩니다. 하지만 최적해는 `3 + 3`으로 2개입니다. 이런 문제는 보통 DP로 접근합니다.

```text
dp[x] = 금액 x를 만드는 데 필요한 최소 동전 개수
dp[0] = 0
dp[x] = min(dp[x - coin] + 1)
```

```cpp
const int INF = 1e9;
vector<int> dp(target + 1, INF);
dp[0] = 0;

for (int x = 1; x <= target; ++x) {
    for (int coin : coins) {
        if (x >= coin) {
            dp[x] = min(dp[x], dp[x - coin] + 1);
        }
    }
}
```

이 형태는 같은 동전을 여러 번 써도 되는 **unbounded knapsack**과 비슷합니다.

## 6. 0/1 배낭 DP

각 물건은 한 번만 고를 수 있고, 무게 제한 안에서 가치 합을 최대로 만들고 싶습니다.

```text
dp[i][w] = 앞 i개 물건만 보고, 용량 w일 때 얻을 수 있는 최대 가치
```

`i`번째 물건을 고르지 않거나, 고르는 두 경우를 비교합니다.

```cpp
vector<vector<int>> dp(n + 1, vector<int>(capacity + 1, 0));

for (int i = 1; i <= n; ++i) {
    int weight = items[i - 1].weight;
    int value = items[i - 1].value;

    for (int w = 0; w <= capacity; ++w) {
        dp[i][w] = dp[i - 1][w];
        if (w >= weight) {
            dp[i][w] = max(dp[i][w], dp[i - 1][w - weight] + value);
        }
    }
}
```

공간은 1차원으로 줄일 수 있습니다. 단, 물건을 한 번만 써야 하므로 용량을 큰 쪽에서 작은 쪽으로 내려가야 합니다.

```cpp
vector<int> dp(capacity + 1, 0);

for (auto item : items) {
    for (int w = capacity; w >= item.weight; --w) {
        dp[w] = max(dp[w], dp[w - item.weight] + item.value);
    }
}
```

반대로 같은 물건을 여러 번 쓸 수 있는 unbounded knapsack은 작은 용량에서 큰 용량으로 올라갑니다. 반복 방향 하나로 문제 조건이 바뀌므로 특히 조심해야 합니다.

| 문제 | 1차원 반복 방향 | 이유 |
| --- | --- | --- |
| 0/1 배낭 | 큰 용량에서 작은 용량 | 같은 물건을 중복 사용하지 않음 |
| 무한 배낭 | 작은 용량에서 큰 용량 | 같은 물건을 다시 사용할 수 있음 |

## 7. LIS: 가장 긴 증가 부분수열

수열에서 순서를 유지하며 증가하는 원소를 골라 가장 긴 길이를 구하는 문제입니다.

가장 직관적인 상태는 다음과 같습니다.

```text
dp[i] = i번째 원소를 마지막으로 하는 LIS 길이
```

`i`보다 앞에 있고 `a[j] < a[i]`인 원소 뒤에 `a[i]`를 붙일 수 있습니다.

```cpp
vector<int> dp(n, 1);

for (int i = 0; i < n; ++i) {
    for (int j = 0; j < i; ++j) {
        if (a[j] < a[i]) {
            dp[i] = max(dp[i], dp[j] + 1);
        }
    }
}

int answer = *max_element(dp.begin(), dp.end());
```

시간 복잡도는 `O(n^2)`입니다. `n`이 크면 `tails[len] = 길이가 len인 증가 부분수열의 가능한 마지막 값 중 최솟값`을 유지해 `O(n log n)`으로 줄일 수 있습니다.

```cpp
vector<int> tails;

for (int x : a) {
    auto it = lower_bound(tails.begin(), tails.end(), x);
    if (it == tails.end()) {
        tails.push_back(x);
    } else {
        *it = x;
    }
}

int answer = (int)tails.size();
```

`tails` 배열 자체가 실제 LIS를 그대로 저장한다고 생각하면 헷갈립니다. 핵심은 각 길이의 끝값을 최대한 작게 유지해 미래 선택지를 넓히는 것입니다.

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

## 11. Digit DP

`0`부터 `N`까지의 정수 중 어떤 조건을 만족하는 개수를 세는 문제에서는 자릿수를 왼쪽부터 보며 DP를 할 수 있습니다. 예를 들어 "숫자에 3이 들어가지 않는 수의 개수"처럼 범위가 크지만 자릿수는 적은 문제가 여기에 맞습니다.

자주 쓰는 상태는 다음과 같습니다.

```text
pos = 지금 보고 있는 자리
tight = 지금까지 N의 prefix와 정확히 같은가?
started = 아직 leading zero만 봤는가?
state = 문제 조건에 필요한 추가 정보
```

```cpp
long long solve(int pos, bool tight, bool started, int state) {
    if (pos == digits.size()) {
        return isValid(started, state) ? 1 : 0;
    }

    long long& cached = memo[pos][tight][started][state];
    if (!tight && cached != -1) return cached;

    int limit = tight ? digits[pos] : 9;
    long long result = 0;

    for (int d = 0; d <= limit; ++d) {
        bool nextTight = tight && (d == limit);
        bool nextStarted = started || (d != 0);
        int nextState = update(state, d, nextStarted);
        result += solve(pos + 1, nextTight, nextStarted, nextState);
    }

    if (!tight) cached = result;
    return result;
}
```

`tight`가 참인 상태는 상한 `N`에 묶여 있어 재사용이 제한됩니다. 보통 `tight == false`인 상태만 메모하면 구현이 단순합니다.

## 12. 상태 압축과 rolling array

`dp[i]`를 계산할 때 바로 이전 행만 필요하다면 전체 2차원 배열을 저장하지 않아도 됩니다.

```cpp
vector<long long> previous(w, 0), current(w, 0);

for (int r = 0; r < h; ++r) {
    fill(current.begin(), current.end(), 0);

    for (int c = 0; c < w; ++c) {
        current[c] += previous[c];
        if (c > 0) current[c] += current[c - 1];
    }

    previous.swap(current);
}
```

공간 최적화는 답을 바꾸지 않지만, 전이 순서를 더 헷갈리게 만듭니다. 처음에는 2차원으로 맞춘 뒤, 메모리 제한 때문에 필요할 때 줄이는 방식이 안전합니다.

## 13. DP 최적화 감각

DP가 맞아도 상태 수나 전이 수가 너무 크면 시간 제한을 넘습니다. 이때는 다음 질문을 던집니다.

- 전이에서 매번 보는 후보를 prefix sum, prefix min, deque, segment tree로 줄일 수 있는가?
- `dp[i][j] = min(dp[i - 1][k] + cost(k, j))`처럼 이전 행의 최솟값을 빠르게 찾는 문제인가?
- 구간 DP에서 최적 분할점이 단조롭게 움직이는 성질이 있는가?
- 그래프 위 상태라면 Dijkstra, 0-1 BFS, shortest path 관점으로 바꿀 수 있는가?
- bitmask의 부분집합을 훑을 때 `sub = (sub - 1) & mask` 패턴이 필요한가?

최적화 기법 이름보다 중요한 것은 "반복문 하나가 왜 필요한지"를 보는 것입니다. `O(n^3)`에서 안 되는 이유가 안쪽의 `k` 전체 탐색이라면, 그 `k`를 줄일 구조가 있는지 찾습니다.

## 14. 자주 나오는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 상태 의미가 모호함 | 전이가 서로 다른 의미를 섞음 | `dp[i][j] = ...` 문장을 한국어로 정확히 쓰기 |
| 초기값 누락 | 불가능한 상태가 답에 섞임 | `0`, `INF`, `-INF` 중 무엇이 맞는지 확인 |
| 반복 방향 오류 | 같은 물건을 여러 번 쓰거나 못 씀 | 0/1 배낭은 역방향, 무한 배낭은 정방향 |
| 계산 순서 오류 | 아직 없는 값을 참조 | 전이에 필요한 상태가 먼저 채워지는지 확인 |
| overflow | 큰 입력에서 오답 | 비용 합은 `long long`, `INF`는 충분히 크게 |
| 메모리 초과 | 배열 크기 초과 | 상태 수를 먼저 곱해 보기 |
| mod 처리 누락 | 경우의 수 문제 오답 | 덧셈과 곱셈 직후 mod 적용 |

## 15. 문제를 볼 때 체크할 신호

DP를 떠올릴 만한 신호는 다음과 같습니다.

1. "최대/최소/경우의 수"를 묻고, 선택이 여러 단계로 이어집니다.
2. 같은 prefix, 같은 위치, 같은 남은 용량, 같은 선택 집합 같은 상태가 반복됩니다.
3. 그리디 기준을 세워 봤지만 작은 반례가 나옵니다.
4. 전체 경우의 수는 크지만, 상태를 요약하면 개수가 줄어듭니다.
5. 답을 만들 때 마지막 선택이나 첫 번째 분할 위치를 기준으로 나눌 수 있습니다.

정리하면, DP는 "미래에 필요한 정보만 상태로 남기고, 같은 상태는 한 번만 계산하는 방법"입니다. 상태를 정확히 정의하면 전이는 자연스럽게 따라오고, 전이에 맞는 순서를 잡으면 구현이 안정됩니다.
