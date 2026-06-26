# Lagrangian Relaxation Patterns

Lagrangian Relaxation Patterns는 딱 맞춰야 하는 제약을 penalty로 목적식에 흡수해, DP, flow, greedy, shortest path 같은 더 단순한 oracle을 반복 호출하는 모델링 패턴입니다. Alien Optimization은 그중 "정확히 K개" 제약을 DP count와 함께 다루는 대표 사례이고, 이 레슨은 같은 생각을 더 넓은 최적화 문제에 적용하는 기준을 정리합니다.

이 레슨은 Alien Optimization, Parametric DP, Fractional Programming DP 이후에 보는 전략과 최적화 심화입니다.

1. 어려운 제약을 `lambda * violation` penalty로 목적식에 넣는다.
2. 고정된 `lambda`에서 원래보다 쉬운 subproblem을 푼다.
3. 선택 개수, 흐름량, 비용 같은 response가 목표 제약에 가까워지도록 `lambda`를 조정한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Alien Optimization, Parametric DP, Fractional Programming DP
- 함께 보면 좋은 레슨: Convex DP Modeling, Min-Cost Flow, Flow with Lower Bound
- 다음에 볼 레슨: Dual Averaging, convex duality, decomposition methods

## 1. 문제 신호

| 문제 표현 | Lagrangian 관점 |
| --- | --- |
| 정확히 `K`개 골라야 한다 | 개수에 penalty를 붙인 relaxed DP |
| 예산 `B` 이하에서 최대 보상 | 비용 violation에 multiplier 부여 |
| flow 양과 비용 조건이 함께 있다 | capacity/flow 제약을 dual 변수로 분리 |
| 선택 개수가 늘수록 score가 단조적으로 변한다 | multiplier 이분 탐색 후보 |
| 제약만 없으면 greedy/DP가 쉬워진다 | relaxed oracle을 반복 호출 |

핵심은 제약을 없애는 것이 아니라, 제약을 만족하지 않는 정도에 가격을 매겨서 더 쉬운 문제로 바꾸는 것입니다.

### 먼저 걸러야 할 경우

이 기법은 penalty를 붙였을 때 relaxed oracle이 실제로 쉬워질 때만 이득이 있습니다. 고정된 `lambda`에서도 여전히 원래 문제와 같은 차원의 DP, 같은 flow 제약, 같은 어려운 조합 선택을 풀어야 한다면 relaxation이 아니라 문제를 다시 쓴 것에 가깝습니다. 구현 전에 "`lambda`를 고정하면 어떤 상태나 제약이 사라지는가?"를 한 줄로 먼저 적어 보고, 답이 없으면 다른 모델을 찾는 편이 낫습니다.

## 2. 기본 변환

원래 문제가 아래라고 합시다.

```text
maximize value(x)
subject to count(x) = K
```

`lambda`를 고정하고 relaxed objective를 풉니다.

```text
maximize value(x) - lambda * count(x)
```

`lambda`가 커지면 선택 하나가 비싸지므로 선택 개수는 줄어드는 방향으로 움직입니다. 반대로 `lambda`가 작아지면 더 많이 고르는 해가 좋아집니다.

정확히 `K`개짜리 원래 objective는 relaxed score에서 penalty를 되돌려 계산합니다.

```text
answer = relaxedScore(lambda) + lambda * K
```

단, 이 식은 `lambda`에서 얻은 해의 count가 `K`에 맞거나, tie-break와 convex hull 성질로 보정 가능한 경우에 안전합니다.

## 3. 작은 예시

서로 인접한 원소를 동시에 고를 수 없는 배열에서 정확히 `K`개를 고른다고 하겠습니다.

```text
values = [8, 7, 6, 5]
K = 2
```

penalty `lambda = 3`을 붙이면 각 선택 score는 아래처럼 바뀝니다.

```text
relaxed values = [5, 4, 3, 2]
```

인접 금지 DP는 이제 "몇 개를 골라야 하는가"를 상태로 들고 가지 않아도 됩니다. 대신 DP 결과에 `count`를 같이 저장해, 현재 penalty에서 몇 개를 고르는지 관찰합니다.

## 4. Count를 같이 들고 가는 DP

아래 코드는 path independent set에서 penalty가 붙은 최댓값과 선택 개수를 동시에 계산합니다. 동점이면 더 많이 고른 해를 택해 count 단조성을 관찰하기 쉽게 만듭니다.

```cpp compile-check
#include <algorithm>
#include <utility>
#include <vector>
using namespace std;

struct Result {
    long long score = 0;
    int count = 0;
};

Result better(Result a, Result b) {
    if (a.score != b.score) {
        return a.score > b.score ? a : b;
    }
    return a.count > b.count ? a : b;
}

Result solveRelaxedPath(const vector<int>& value, long long penalty) {
    Result prev2{0, 0};
    Result prev1{0, 0};

    for (int x : value) {
        Result take{prev2.score + x - penalty, prev2.count + 1};
        Result skip = prev1;
        Result cur = better(take, skip);
        prev2 = prev1;
        prev1 = cur;
    }

    return prev1;
}

long long candidateExactK(const vector<int>& value, int targetCount, long long penalty) {
    Result relaxed = solveRelaxedPath(value, penalty);
    return relaxed.score + penalty * targetCount;
}
```

실제 정답을 얻으려면 penalty를 이분 탐색하거나, 가능한 breakpoint를 찾거나, count가 정확히 맞는 구간을 확인해야 합니다. 이 코드는 relaxed oracle의 모양을 보여 주는 골격입니다.

## 5. Flow와 Greedy에 붙이는 방식

Lagrangian relaxation은 DP에만 붙지 않습니다.

| 원래 제약 | Relaxed oracle |
| --- | --- |
| 정확히 `K`개 간선 선택 | 간선 선택당 penalty가 붙은 MST/greedy |
| 예산 안에서 최대 flow | 비용에 multiplier를 붙인 min-cost flow |
| coverage를 일정 이상 만족 | uncovered item penalty가 붙은 set 선택 |
| 평균 또는 비율 목적식 | `value - lambda * weight` 판정 |

제약을 penalty로 바꿨을 때 oracle이 정말 쉬워지는지가 중요합니다. penalty를 붙였는데도 같은 난이도의 문제라면 relaxation의 이점이 없습니다.

## 6. Dual 변수 해석

`lambda`는 제약 하나의 그림자 가격입니다.

```text
lambda가 너무 작다 -> 제약 자원을 과하게 사용한다
lambda가 너무 크다 -> 제약 자원을 너무 적게 사용한다
```

문제에서 여러 제약이 동시에 나오면 multiplier도 여러 개가 됩니다. 이 경우 단순 이분 탐색 대신 subgradient, dual averaging, coordinate search 같은 방식이 필요할 수 있습니다.

## 7. 단조성과 Tie-Break

Lagrangian 이분 탐색은 response가 단조적일 때 안전합니다.

| response | penalty 증가 시 기대 방향 |
| --- | --- |
| 선택 개수 | 감소 |
| 사용 예산 | 감소 |
| flow 양 | 감소하거나 유지 |
| violation | 감소 |

동점 처리에 따라 count가 흔들리면 breakpoint 주변에서 같은 `lambda`로 서로 다른 해가 나올 수 있습니다. 그래서 DP 상태에 `(score, count)`를 같이 두고, 최대화 기준 다음의 tie-break를 명시합니다.

## 8. 자주 하는 실수

1. penalty를 더해야 하는데 빼서 단조 방향을 반대로 만든다.
2. relaxed 해의 count가 목표와 다르다는 사실을 무시하고 답을 보정한다.
3. tie-break가 없어 이분 탐색 중 count가 불안정하게 튄다.
4. 원래 제약이 equality인지 inequality인지 구분하지 않는다.
5. penalty를 실수로 둬야 하는 문제를 정수 이분 탐색으로 자른다.
6. relaxation 후 oracle이 여전히 어려운 문제인데 억지로 적용한다.

## 9. 문제를 볼 때 체크할 조건

- 어떤 제약을 penalty로 옮길 것인가?
- 고정된 `lambda`에서 풀리는 subproblem이 무엇인가?
- response가 `lambda`에 대해 단조적인가?
- equality 제약이면 목표 count를 정확히 맞출 수 있는가?
- tie-break를 어느 방향으로 둘 것인가?
- 최종 answer에서 penalty를 되돌리는 식이 맞는가?

## 10. 대표 문제로 연결하기

### 문제에서 보이는 신호

- 입력 크기: `K` 차원을 DP에 넣으면 너무 큼
- 필요한 복잡도: `O(log W * relaxedOracle)` 또는 breakpoint 탐색
- 이 레슨의 핵심 개념: 제약을 가격으로 바꾸고 oracle을 반복 호출

### 풀이 흐름

1. 원래 objective와 제약을 분리한다.
2. 제약 사용량 하나를 `count(x)`처럼 수식화한다.
3. `value(x) - lambda * count(x)` oracle을 만든다.
4. oracle이 반환하는 사용량의 단조 방향을 확인한다.
5. 목표 제약을 만족하는 `lambda` 근처에서 원래 objective를 복원한다.

### 자주 틀리는 지점

- "정확히 K개"와 "최대 K개"는 보정 방식이 다릅니다.
- penalty가 큰 입력에서는 `score` 범위가 커지므로 `long long` 한계를 먼저 계산해야 합니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: exact K selection `/practice/...` 문제 필요 | count penalty와 답 보정 | Alien trick |
| 표준 | TODO: budgeted DP relaxation `/practice/...` 문제 필요 | 비용 제약을 multiplier로 이동 | relaxed DP |
| 응용 | TODO: Lagrangian flow `/practice/...` 문제 필요 | flow 양과 비용 조건 분리 | min-cost flow |
| 함정 | TODO: tie-break counterexample `/practice/...` 문제 필요 | 동점 처리와 count 단조성 확인 | breakpoint |
