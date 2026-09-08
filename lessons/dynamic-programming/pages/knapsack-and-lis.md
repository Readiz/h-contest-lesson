# 동적 계획법: 배낭과 LIS

## 0/1 배낭 DP

용량은 음이 아닌 정수, 물건 무게는 양의 정수이며 가치 합은 사용 자료형 범위 안입니다. 각 물건을 한 번씩만 골라 무게 제한 안에서 가치 합을 최대화합니다. 앞 `i`개 물건을 본 답을 `dp[i][w]`라 두면, 현재 물건을 건너뛴 `dp[i - 1][w]`와 고른 `dp[i - 1][w - weight] + value` 중 큰 값이 답입니다.

이전 행만 필요하므로 배열 하나로 줄일 수 있습니다. 아직 현재 물건이 반영되지 않은 칸을 읽도록 용량을 큰 쪽부터 갱신합니다.

```cpp
vector<int> dp(capacity + 1, 0);

for (auto item : items) {
    for (int w = capacity; w >= item.weight; --w) {
        dp[w] = max(dp[w], dp[w - item.weight] + item.value);
    }
}
```

무게 2, 가치 3인 물건 하나와 용량 4를 생각해 봅시다. 용량을 올리며 갱신하면 `dp[2] = 3`을 같은 물건에서 다시 읽어 `dp[4] = 6`으로 만듭니다. 이는 같은 물건을 두 번 고른 결과입니다. 내림차순이면 `dp[4]`를 계산할 때 `dp[2]`는 아직 0이어서 답 3을 얻습니다.

같은 물건을 여러 번 쓸 수 있는 문제라면 반대로 오름차순으로 갱신합니다.

## LIS: 가장 긴 증가 부분수열

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

int answer = dp.empty() ? 0 : *max_element(dp.begin(), dp.end());
```

시간 복잡도는 `O(n^2)`입니다. `n`이 크면 `tails[len - 1] = 길이가 len인 증가 부분수열의 가능한 마지막 값 중 최솟값`을 유지해 `O(n log n)`으로 줄일 수 있습니다.

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

`tails[len - 1]`은 길이가 `len`인 증가 부분 수열의 가능한 최소 끝값입니다. 각 칸을 만든 부분 수열은 서로 다를 수 있어 `tails` 전체가 실제 LIS인 것은 아닙니다.
