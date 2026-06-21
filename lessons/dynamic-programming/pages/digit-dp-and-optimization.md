# 동적 계획법: Digit DP와 최적화 감각

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
