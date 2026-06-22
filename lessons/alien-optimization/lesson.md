# Alien Optimization

Alien Optimization은 "정확히 K개를 선택해야 하는 최적화"를 직접 풀기 어려울 때, 선택 개수에 벌점 `lambda`를 붙여 parametric search로 맞추는 기법입니다. Lagrangian relaxation이라고도 부르며, DP 최적화 문제에서 자주 등장합니다.

이 레슨은 Divide and Conquer DP Optimization, Knuth Optimization, Monge/SMAWK 이후에 보는 비용 함수 관점의 최적화입니다.

1. 선택 하나마다 벌점 `lambda`를 더하거나 뺀다.
2. 바뀐 목적식으로 "선택 개수 제한 없는" 최적 DP를 푼다.
3. `lambda`를 이분 탐색해 선택 개수가 K에 맞는 지점을 찾는다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: DP, 이분 탐색, 최적화 목적식, monotonicity
- 함께 보면 좋은 레슨: Divide and Conquer DP Optimization, Monge와 SMAWK, Convex Hull Trick
- 다음에 볼 레슨: Lagrangian relaxation, slope trick, convex DP

## 1. 문제 신호

| 문제 표현 | Alien Optimization 관점 |
| --- | --- |
| 정확히 K개 segment/edge/group을 선택 | 선택 개수에 penalty 부여 |
| K가 크고 DP 차원이 부담 | count dimension 제거 |
| penalty가 커질수록 선택 개수가 단조 변화 | binary search 가능 |
| 최적값과 선택 개수를 함께 추적 가능 | DP state에 pair 저장 |
| 최종 답 보정이 필요 | relaxed answer에서 `lambda*K` 제거 |

단조성이 없으면 alien optimization을 적용할 수 없습니다. penalty가 증가할수록 선택을 덜 하거나 더 하는 방향이 일관되어야 합니다.

## 2. Relaxation

원래 문제가 아래라고 합시다.

```text
minimize cost
subject to selected_count = K
```

선택 하나당 벌점 `lambda`를 더해 제한 없는 문제로 바꿉니다.

```text
minimize cost + lambda * selected_count
```

`lambda`가 커질수록 선택을 많이 하는 해는 불리해집니다. 그래서 최적해의 `selected_count`는 보통 감소 방향으로 움직입니다.

최종적으로 relaxed DP가 준 값이 `relaxedCost = cost + lambda * count`라면, count가 K인 지점의 원래 비용은 아래입니다.

```text
answer = relaxedCost - lambda * K
```

## 3. Pair 비교

DP는 비용과 선택 개수를 같이 들고 다닙니다. 비용이 같다면 선택 개수를 원하는 방향으로 tie-break해야 binary search가 안정됩니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct RelaxedValue {
    long long cost = 0;
    int count = 0;
};

RelaxedValue betterMin(const RelaxedValue& a, const RelaxedValue& b) {
    if (a.cost != b.cost) {
        return a.cost < b.cost ? a : b;
    }
    return a.count > b.count ? a : b;
}
```

위 tie-break는 같은 relaxed cost라면 선택 개수가 큰 해를 고릅니다. 이분 탐색 조건을 어떻게 잡느냐에 따라 반대로 둘 수도 있습니다.

## 4. 단순 DP 예시

아래 예시는 각 item을 선택하면 `value[i]` 비용을 얻고, 선택할 때마다 penalty를 추가하는 최소화 DP 골격입니다. 실제 문제에서는 transition이 더 복잡하지만, penalty가 들어가는 위치는 같습니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct AlienResult {
    long long cost;
    int count;
};

AlienResult minPair(const AlienResult& a, const AlienResult& b) {
    if (a.cost != b.cost) {
        return a.cost < b.cost ? a : b;
    }
    return a.count > b.count ? a : b;
}

AlienResult solveRelaxed(const vector<long long>& value, long long penalty) {
    const long long INF = (1LL << 60);
    AlienResult dpSkip{0, 0};
    AlienResult dpTake{INF, 0};

    for (long long x : value) {
        AlienResult nextSkip = minPair(dpSkip, dpTake);
        AlienResult bestPrev = minPair(dpSkip, dpTake);
        AlienResult nextTake{bestPrev.cost + x + penalty, bestPrev.count + 1};
        dpSkip = nextSkip;
        dpTake = nextTake;
    }

    return minPair(dpSkip, dpTake);
}

long long exactlyKByAlien(const vector<long long>& value, int k) {
    long long low = -1000000000LL;
    long long high = 1000000000LL;

    while (low < high) {
        long long mid = (low + high + 1) / 2;
        AlienResult result = solveRelaxed(value, mid);
        if (result.count >= k) {
            low = mid;
        } else {
            high = mid - 1;
        }
    }

    AlienResult result = solveRelaxed(value, low);
    return result.cost - low * k;
}
```

이 예시는 구조 설명용입니다. 실제 alien optimization은 segment DP, tree DP, path cover류에서 transition 비용을 penalty와 함께 넣는 형태로 자주 쓰입니다.

## 5. Binary Search 방향

최소화 문제에서 선택마다 `+lambda`를 더하면:

| lambda | 선택 개수 |
| ---: | ---: |
| 작아짐 | 선택이 많아짐 |
| 커짐 | 선택이 적어짐 |

반대로 최대화 문제에서 선택마다 `+lambda` 보상을 주면 lambda가 커질수록 선택이 많아집니다. 문제를 최대화/최소화 중 무엇으로 두었는지에 따라 조건문이 바뀝니다.

## 6. 답 보정

DP가 계산한 것은 relaxed objective입니다.

```text
relaxed = original + lambda * count
```

정확히 K개 선택한 원래 값을 원하면:

```text
original = relaxed - lambda * K
```

최대화에서 `original + lambda*count`를 최대화한 경우도 같은 방식으로 `lambda*K`를 빼지만, penalty를 반대로 넣었다면 부호를 다시 확인해야 합니다.

## 7. 적용 조건

Alien optimization을 쓰려면 아래 조건이 필요합니다.

1. 선택 개수 제한을 제거하면 DP가 쉬워진다.
2. penalty 변화에 따라 최적해의 선택 개수가 단조적이다.
3. DP가 최적 비용과 선택 개수를 함께 반환할 수 있다.
4. 원하는 K가 가능한 범위 안에 있다.

단조성은 보통 convex hull이나 lower envelope 관점으로 설명할 수 있습니다. 하지만 대회에서는 penalty를 움직였을 때 count가 실제로 단조인지 먼저 증명해야 합니다.

## 8. 시간 복잡도

`solveRelaxed(lambda)`가 `T(N)`이면 전체 시간은:

```text
O(T(N) * log C)
```

여기서 `C`는 penalty 탐색 범위입니다. 정수 cost라면 이분 탐색이 편하고, 실수 penalty라면 precision과 tie-break 문제가 더 까다롭습니다.

## 9. 자주 하는 실수

1. relaxed 답에서 `lambda*K`를 빼지 않는다.
2. tie-break 방향을 잘못 잡아 count가 흔들린다.
3. 최소화/최대화에 따라 binary search 조건을 반대로 쓴다.
4. 원하는 K가 불가능한데도 답을 보정한다.
5. penalty 범위를 너무 좁게 잡는다.

## 10. 문제를 볼 때 체크할 조건

- 정확히 K개 조건을 penalty로 옮길 수 있는가?
- penalty가 커질 때 선택 개수가 단조적인가?
- relaxed DP가 count를 함께 반환하는가?
- 최종 답 보정 부호가 맞는가?
- cost 범위에 맞는 penalty search bounds를 잡았는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 정확히 K개 segment DP `/practice/...` 문제 필요 | penalty와 count 추적 | alien trick |
| 표준 | TODO: DP 차원 제거 `/practice/...` 문제 필요 | K dimension을 이분 탐색으로 대체 | Lagrangian relaxation |
| 응용 | TODO: tree/path 선택 최적화 `/practice/...` 문제 필요 | relaxed transition 설계 | parametric DP |
| 함정 | TODO: tie-break 반례 `/practice/...` 문제 필요 | 같은 비용에서 count 방향 고정 | monotonicity |
