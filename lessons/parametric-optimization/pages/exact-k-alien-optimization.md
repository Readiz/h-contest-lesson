# Exact-K Alien Optimization

정확히 K개 선택하는 비용 F(K)를 직접 계산하기 어려울 때 G(lambda)=min_k(F(k)+lambda*k)를 푸는 oracle을 사용합니다. 고정 lambda에서 실제로 계산이 쉬워져야 이득이 있습니다.

## 단조성과 복원 조건

lambda가 증가하면 최적 선택 수는 비증가합니다. 두 최적해의 부등식을 더하면 이를 보일 수 있습니다. 그러나 이 단조성만으로 모든 K의 정답을 복원할 수는 없습니다.

```text
F(0)=0, F(1)=10, F(2)=0
```

어떤 lambda에서도 k=1은 최적이 되지 않습니다. K=1에 G(lambda)-lambda를 출력하면 실제 값 10을 복원하지 못합니다. F의 이산 볼록성 등으로 각 K가 lower hull 위에 놓인다는 조건을 증명해야 합니다. 정수 lambda만 탐색할 수 있는지도 별도 조건입니다.

## DP oracle

아래는 배열을 비어 있지 않은 구간들로 나누는 O(N²) oracle입니다. cost(l,r)는 구간 비용이고 모든 비용·penalty 합은 INF/2 미만의 유효 범위여야 합니다. n>=0이며 같은 비용이면 더 많은 구간을 선택합니다.

```cpp compile-check
#include <algorithm>
#include <functional>
#include <utility>
#include <vector>
using namespace std;

struct ParametricDpResult {
    long long value = 0;
    int count = 0;
};

struct ParametricDp {
    static constexpr long long INF = (1LL << 60);

    template <class Cost>
    static ParametricDpResult solveWithPenalty(int n, long long lambda, Cost cost) {
        vector<ParametricDpResult> dp(n + 1, {INF, 0});
        dp[0] = {0, 0};

        for (int right = 1; right <= n; ++right) {
            ParametricDpResult best{INF, 0};
            for (int left = 0; left < right; ++left) {
                if (dp[left].value >= INF / 2) {
                    continue;
                }
                ParametricDpResult candidate{
                    dp[left].value + cost(left + 1, right) + lambda,
                    dp[left].count + 1
                };
                if (candidate.value < best.value ||
                    (candidate.value == best.value && candidate.count > best.count)) {
                    best = candidate;
                }
            }
            dp[right] = best;
        }

        return dp[n];
    }
};
```

같은 lambda에서 최소·최대 count가 필요하면 tie-break를 각각 두 방향으로 실행합니다. 최소화에서 정확한 K의 relaxed 해를 얻었을 때 답은 G(lambda)-lambda*K입니다. 최대화에서 value-lambda*k를 풀었다면 lambda*K를 더합니다.

## Breakpoint 예시

비용10·count1인 A와 비용7·count2인 B는 lambda=3에서 relaxed 값13으로 같습니다. 더 큰 count를 택하면 B, 작은 count를 택하면 A가 반환됩니다. K가 두 count 사이에 있다는 사실만으로 내부 K의 정확한 비용을 보장하지는 않습니다.

정수 이분 탐색은 충분한 penalty 범위를 먼저 증명하고 count>=K 경계를 찾습니다. oracle 비용 T(N)에 탐색 횟수를 곱합니다. 실제 인접 금지 선택 oracle은 [Lagrangian Relaxation Patterns](https://h.readiz.com/learn/parametric-optimization/general-lagrangian-relaxation)에서 비교합니다.
