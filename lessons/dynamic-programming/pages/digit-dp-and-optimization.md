# 동적 계획법: Digit DP와 메모리 절약

## Digit DP

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

## 상태 압축과 rolling array

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

`previous`에는 이전 행, `current`에는 계산 중인 행만 남습니다. 이전의 모든 행을 다시 읽는 전이가 있다면 이 방식으로 줄일 수 없습니다.
