# 동적 계획법: 배낭과 LIS

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
