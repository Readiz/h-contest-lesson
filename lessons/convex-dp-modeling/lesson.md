# Convex DP Modeling

Convex DP Modeling은 특정 최적화 기법을 바로 적용하기 전에, 전이 비용이 정말 convex/Monge/단조 구조를 갖는지 판정하는 레슨입니다. Divide and Conquer Optimization, CHT, Slope Trick, Min-Plus Convolution은 모두 조건이 맞을 때만 강력합니다.

이 레슨은 Min-Plus Convolution, Alien Optimization, Convex Cost Flow 이후에 보는 DP 최적화 심화입니다.

1. 상태와 decision variable을 분리한다.
2. 비용 함수의 차분, 교차 부등식, argmin 이동을 확인한다.
3. 조건을 증명하지 못하면 작은 입력 stress test로 최적화 후보를 검증한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: DP transition, convex sequence, Monge inequality, divide and conquer optimization
- 함께 보면 좋은 레슨: Min-Plus Convolution, Monge와 SMAWK, Slope Trick, Alien Optimization
- 다음에 볼 레슨: convex hull trick variants, quadrangle inequality proofs, parametric DP

## 1. 문제 신호

| 문제 표현 | Convex DP Modeling 관점 |
| --- | --- |
| 그룹을 나누는 비용이 구간 길이에 따라 증가 | quadrangle inequality 후보 |
| 선택 수에 penalty를 붙이면 개수가 단조 | Alien Optimization 후보 |
| 직선의 최솟값/최댓값을 반복 질의 | CHT/Li Chao 후보 |
| 두 convex cost 배열을 합침 | Min-Plus Convolution 후보 |
| 절댓값 거리 비용이 누적 | Slope Trick 또는 median 구조 |

핵심은 "어떤 최적화가 떠오르는가"보다 "전이가 어떤 수학적 구조를 갖는가"입니다.

## 2. 모델링 순서

DP 최적화 전에 아래 순서로 식을 정리합니다.

```text
dp[i] = min over k < i:
  previous[k] + cost(k, i)
```

1. `k`가 decision variable인지 확인한다.
2. `cost(k, i)`가 독립적으로 계산 가능한지 본다.
3. `argmin[i]`가 i에 따라 단조인지 확인한다.
4. 단조가 아니면 다른 구조인 CHT, SMAWK, Slope Trick을 찾는다.

식 정리가 안 되면 구현 최적화보다 상태 설계가 먼저입니다.

## 3. Convex와 Monge 체크

1차원 수열에서는 차분이 증가하면 convex입니다.

```text
a[i+1] - a[i] <= a[i+2] - a[i+1]
```

2차원 cost matrix에서는 Monge inequality를 확인합니다.

```text
cost(a, c) + cost(b, d) <= cost(a, d) + cost(b, c)
where a <= b <= c <= d
```

이 조건이 있으면 row minima나 DP argmin이 단조로울 가능성이 큽니다. 부등호 방향이 반대면 max 문제나 anti-Monge 문제인지 다시 봅니다.

## 4. Divide and Conquer DP 골격

아래 코드는 argmin이 단조라는 전제가 있을 때 한 layer를 계산하는 골격입니다.

```cpp compile-check
#include <algorithm>
#include <functional>
#include <vector>
using namespace std;

struct ConvexDpModeling {
    static constexpr long long INF = (1LL << 60);

    template <class Cost>
    static vector<long long> computeLayer(
        const vector<long long>& previous,
        int n,
        Cost cost
    ) {
        vector<long long> current(n + 1, INF);

        function<void(int, int, int, int)> solve = [&](int left, int right, int optLeft, int optRight) {
            if (left > right) {
                return;
            }
            int mid = (left + right) / 2;
            int bestK = optLeft;
            long long bestValue = INF;
            int upper = min(mid - 1, optRight);

            for (int k = optLeft; k <= upper; ++k) {
                if (previous[k] >= INF / 2) {
                    continue;
                }
                long long value = previous[k] + cost(k + 1, mid);
                if (value < bestValue) {
                    bestValue = value;
                    bestK = k;
                }
            }

            current[mid] = bestValue;
            solve(left, mid - 1, optLeft, bestK);
            solve(mid + 1, right, bestK, optRight);
        };

        solve(1, n, 0, n - 1);
        return current;
    }
};
```

이 코드는 조건을 증명해 주지 않습니다. `bestK`가 단조라는 모델링이 맞을 때만 빠른 구현입니다.

## 5. Stress Test로 조건 확인

증명이 바로 떠오르지 않으면 작은 입력에서 naive DP와 최적화 DP를 비교합니다.

```text
for random small cases:
  naive answer 계산
  optimized answer 계산
  다르면 argmin 단조 조건이나 cost 구현을 재검토
```

stress test는 증명의 대체재가 아니지만, 잘못된 최적화를 초기에 잡는 안전장치입니다.

## 6. 어떤 최적화를 고를까

| 구조 | 후보 기법 |
| --- | --- |
| `argmin[i]`가 단조 | Divide and Conquer Optimization |
| Monge matrix의 모든 row minima | SMAWK |
| `m*x + b` 형태 | Convex Hull Trick, Li Chao |
| convex piecewise-linear function update | Slope Trick |
| 선택 개수와 penalty가 단조 | Alien Optimization |
| 두 cost function merge | Min-Plus Convolution |

여러 기법이 가능하면 구현 복잡도와 제한을 같이 봅니다. 예를 들어 `O(KN log N)` CHT보다 `O(KN)` D&C가 더 간단할 수 있습니다.

## 7. 반례를 만드는 습관

최적화 조건이 애매할 때는 가장 작은 반례를 만들어 봅니다.

1. `N=4` 정도의 cost matrix를 직접 써 본다.
2. `argmin`이 `0, 2, 1, 3`처럼 되돌아가는지 확인한다.
3. Monge inequality를 한 칸이라도 깨는 조합을 찾는다.
4. penalty를 바꾸었을 때 선택 개수가 단조인지 본다.

작은 반례가 있으면 최적화는 틀립니다. 문제의 추가 제약이 그 반례를 막는지 확인해야 합니다.

## 8. 자주 하는 실수

1. convex function과 convex sequence를 같은 검증 없이 섞는다.
2. argmin 단조를 샘플 몇 개만 보고 가정한다.
3. `<=`와 `<` tie-breaking을 다르게 해서 단조성이 깨진다.
4. max 문제를 min 문제 공식에 그대로 넣는다.
5. cost precomputation이 overflow나 index 경계에서 틀린다.

## 9. 문제를 볼 때 체크할 조건

- decision variable이 명확하게 하나인가?
- cost가 구간, 개수, 좌표 차이 같은 독립 함수로 분리되는가?
- 차분 증가나 Monge inequality를 증명할 수 있는가?
- tie-breaking을 포함해 argmin이 단조인가?
- 최적화 전 naive DP와 비교할 작은 generator가 있는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: convex DP modeling `/practice/...` 문제 필요 | 전이식 분리 | decision variable |
| 표준 | TODO: quadrangle inequality `/practice/...` 문제 필요 | argmin 단조 증명 | Monge |
| 응용 | TODO: penalty DP modeling `/practice/...` 문제 필요 | Alien Optimization 선택 | parametric search |
| 함정 | TODO: non-convex DP counterexample `/practice/...` 문제 필요 | 최적화 조건 반례 | stress test |
