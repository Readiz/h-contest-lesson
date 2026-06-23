# Parametric DP

Parametric DP는 답이나 제약을 직접 상태에 넣기 어렵거나 너무 큰 경우, parameter를 고정한 DP를 반복해서 최적의 값을 찾는 관점입니다. 대표적으로 penalty를 붙여 선택 개수를 조절하는 Alien Optimization, 평균을 이분 탐색하는 feasibility DP, 목적값을 parameter로 둔 decision DP가 있습니다.

이 레슨은 Convex DP Modeling, Alien Optimization 이후에 보는 DP 최적화 심화입니다.

1. 원래 최적화 문제를 parameter가 고정된 판정 또는 완화 문제로 바꾼다.
2. parameter가 커질 때 답의 성질이 단조인지 확인한다.
3. DP 값과 함께 선택 개수, tie-breaking 정보를 같이 들고 다닌다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: binary search, DP transition, monotonicity, Alien Optimization
- 함께 보면 좋은 레슨: Alien Optimization, Convex DP Modeling, Divide and Conquer DP Optimization
- 다음에 볼 레슨: Lagrangian relaxation, DP sensitivity analysis, ternary search pitfalls

## 1. 문제 신호

| 문제 표현 | Parametric DP 관점 |
| --- | --- |
| 정확히 `K`개를 선택해야 하는데 상태가 너무 크다 | penalty DP |
| 평균, 비율, 밀도 최댓값 | answer binary search |
| 비용 제한 안에서 가치 최대 | 제한을 parameter로 둔 feasibility |
| 선택 개수가 penalty에 따라 단조 | Alien Optimization |
| convex/concave 목적값 | slope 또는 marginal cost parameter |

parameter를 넣었을 때 "더 큰 parameter가 더 어렵다" 또는 "선택 개수가 줄어든다" 같은 단조성이 있어야 탐색이 가능합니다.

## 2. Penalty DP의 기본 형태

정확히 `K`개 segment를 고르는 문제를 생각합시다. segment를 하나 고를 때마다 `lambda` penalty를 더하면, 고정된 `lambda`에서는 선택 개수 제한을 없앤 DP를 계산할 수 있습니다.

```text
score(lambda) = min over any segment count:
  original cost + lambda * segmentCount
```

`lambda`가 커질수록 segment를 덜 고르는 답이 유리해지는 경향이 있습니다. 그래서 `segmentCount >= K`인지 보고 lambda를 이분 탐색할 수 있습니다.

## 3. DP 값과 Count를 함께 저장

아래 코드는 segment cost 함수가 주어졌을 때 penalty를 붙인 naive DP를 계산하는 skeleton입니다. 실제 문제에서는 cost 계산과 DP 최적화를 별도로 붙입니다.

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

tie-breaking이 중요합니다. 같은 penalty value라면 count가 큰 쪽을 택할지 작은 쪽을 택할지 정해야 이분 탐색 경계가 안정됩니다.

## 4. 원래 답 복원

penalty DP에서 `lambda`로 계산한 값은 원래 비용이 아닙니다. 선택 개수 `K`를 맞춘 답은 penalty를 다시 빼야 합니다.

```text
relaxed = original + lambda * count
if count == K:
  original = relaxed - lambda * K
```

이분 탐색으로 적절한 lambda를 찾은 뒤에도, count가 정확히 K가 되는지 또는 concave hull 위의 값을 보정해야 하는지 확인해야 합니다. Alien Optimization 문제는 이 보정이 핵심입니다.

## 5. Feasibility DP

평균 최댓값 문제는 후보 평균 `x`를 고정하고 값을 변형합니다.

```text
average >= x
<=> sum(a_i - x) >= 0
```

그 뒤 "조건을 만족하는 부분구조가 존재하는가"를 DP나 prefix minimum으로 판정합니다. `x`가 커질수록 조건은 어려워지므로 binary search가 가능합니다.

| 원래 문제 | parameter 고정 후 |
| --- | --- |
| 최대 평균 구간 | `a_i - x` 합이 0 이상인 구간 존재 |
| 최소 최대 비용 | 비용 limit `x`로 feasible 여부 판정 |
| 비율 최적화 | `profit - x * weight` 부호 판정 |

실수 이분 탐색은 반복 횟수와 오차 기준을 문제 요구에 맞춥니다.

## 6. Ternary Search와 DP

목적 함수가 convex 또는 concave라고 보이면 ternary search를 떠올릴 수 있지만, 정수 DP에서는 plateau와 tie가 많습니다. 가능하면 다음 순서로 봅니다.

1. 단조 판정으로 binary search가 가능한가?
2. marginal cost가 단조라서 penalty DP로 바꿀 수 있는가?
3. 정말 unimodal이면 정수 ternary보다 주변 후보까지 확인하는가?

증명 없는 ternary search는 위험합니다. 작은 반례에서 같은 최댓값 구간이 길게 생기면 경계 처리로 틀릴 수 있습니다.

## 7. 작은 예시

```text
원래 문제: 정확히 2개 그룹으로 나누는 최소 비용
lambda = 0이면 그룹을 많이 쓰는 답이 유리할 수 있음
lambda = 10이면 그룹 수가 줄어드는 답이 유리함

lambda를 키워 보며 DP가 선택한 group count를 관찰한다.
count >= 2이면 penalty가 아직 낮다.
count < 2이면 penalty가 너무 높다.
```

이 관찰이 성립하려면 lambda가 증가할 때 선택 개수가 단조로 감소한다는 증명이 필요합니다.

## 8. 시간 복잡도

| 방식 | 복잡도 |
| --- | ---: |
| penalty DP 1회 | 원래 DP 1회 비용 |
| integer lambda binary search | `O(log answerRange)`회 DP |
| real answer binary search | 고정 반복 횟수 `*` feasibility 비용 |
| DP 내부 최적화 결합 | D&C, CHT, Monge 조건에 따라 감소 |

parameter 탐색은 DP를 여러 번 돌립니다. 따라서 DP 1회가 충분히 빠른지 먼저 계산해야 합니다.

## 9. 자주 하는 실수

1. parameter에 대한 단조성을 증명하지 않고 이분 탐색한다.
2. penalty를 더한 값을 원래 답으로 출력한다.
3. tie-breaking 때문에 count가 흔들리는데 경계를 그대로 믿는다.
4. 실수 이분 탐색에서 반복 횟수가 부족하다.
5. `K`개 선택 조건이 "최대 K"인지 "정확히 K"인지 섞는다.
6. DP 내부 최적화 조건과 parameter 단조 조건을 같은 것으로 착각한다.

## 10. 문제를 볼 때 체크할 조건

- 어떤 값을 parameter로 고정할 수 있는가?
- parameter가 커질 때 feasible 여부나 선택 개수가 단조인가?
- DP 결과에 원래 objective와 보조 count를 함께 저장해야 하는가?
- penalty를 제거해 원래 답으로 복원하는 식이 명확한가?
- 실수 탐색이면 오차와 반복 횟수를 정했는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: max average DP `/practice/...` 문제 필요 | answer binary search | `a_i - x` |
| 표준 | TODO: penalty segment DP `/practice/...` 문제 필요 | value + count 저장 | Alien Optimization |
| 응용 | TODO: ratio optimization `/practice/...` 문제 필요 | `profit - x*weight` 판정 | feasibility DP |
| 함정 | TODO: non-monotone parameter `/practice/...` 문제 필요 | 이분 탐색 불가 판별 | monotonicity |
