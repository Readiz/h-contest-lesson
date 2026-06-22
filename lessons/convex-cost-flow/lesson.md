# Convex Cost Flow

Convex Cost Flow는 한 간선이나 선택 항목의 사용량이 늘수록 marginal cost가 증가하는 상황을 flow 모델로 표현하는 기법입니다. 일반 Min-Cost Flow는 edge cost가 단위 유량마다 일정하지만, convex cost는 단위별 비용을 여러 edge로 쪼개서 표현할 수 있습니다.

이 레슨은 Min-Cost Flow, Slope Trick, Alien Optimization 이후에 보는 최적화 심화입니다.

1. 사용량 `k`의 비용 `C(k)`를 marginal cost `C(k)-C(k-1)`로 나눈다.
2. marginal cost가 nondecreasing이면 unit capacity edge들을 비용순으로 추가한다.
3. min-cost flow가 싼 단위부터 선택하면서 convex cost를 재현한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Min-Cost Flow, convex function, marginal cost, DP optimization
- 함께 보면 좋은 레슨: Min-Cost Flow, Slope Trick, Alien Optimization
- 다음에 볼 레슨: min-plus convolution, convex DP, cost scaling flow

## 1. 문제 신호

| 문제 표현 | Convex Cost Flow 관점 |
| --- | --- |
| 같은 선택을 여러 번 할수록 비용이 증가 | marginal cost edge split |
| 작업량 배분과 convex penalty | flow amount with convex cost |
| piecewise linear cost | segment별 capacity/cost edge |
| assignment에 추가 penalty가 붙음 | min-cost flow 확장 |
| 비용이 concave로 감소 | 단순 edge split만으로는 선택 순서가 달라짐 |

핵심 조건은 marginal cost가 nondecreasing이라는 점입니다. 그래야 min-cost flow가 낮은 marginal unit부터 차례로 고르는 것이 원래 convex cost와 일치합니다.

## 2. Marginal Cost로 쪼개기

사용량별 비용이 아래와 같다고 하겠습니다.

```text
C(0)=0, C(1)=3, C(2)=8, C(3)=15
```

marginal cost는 `3, 5, 7`입니다. 이때 capacity 1짜리 edge를 비용 `3`, `5`, `7`로 3개 넣으면, 유량 2를 보낼 때 비용 `3+5=8`이 됩니다.

```text
u -> v (cap 1, cost 3)
u -> v (cap 1, cost 5)
u -> v (cap 1, cost 7)
```

같은 cost가 여러 번 반복되면 capacity를 합쳐 edge 수를 줄일 수 있습니다.

## 3. Edge 생성 골격

아래 코드는 convex marginal cost list를 min-cost flow edge list로 바꾸는 작은 helper입니다.

```cpp compile-check
#include <vector>
using namespace std;

struct ConvexCostEdgeBuilder {
    struct Arc {
        int from;
        int to;
        long long capacity;
        long long cost;
    };

    vector<Arc> arcs;

    static bool isNondecreasing(const vector<long long>& marginalCosts) {
        for (int i = 1; i < (int)marginalCosts.size(); ++i) {
            if (marginalCosts[i - 1] > marginalCosts[i]) {
                return false;
            }
        }
        return true;
    }

    void addConvexUnits(int from, int to, const vector<long long>& marginalCosts) {
        if (marginalCosts.empty()) {
            return;
        }

        long long currentCost = marginalCosts[0];
        long long capacity = 1;
        for (int i = 1; i < (int)marginalCosts.size(); ++i) {
            if (marginalCosts[i] == currentCost) {
                ++capacity;
            } else {
                arcs.push_back({from, to, capacity, currentCost});
                currentCost = marginalCosts[i];
                capacity = 1;
            }
        }
        arcs.push_back({from, to, capacity, currentCost});
    }
};
```

실전에서는 `isNondecreasing`이 false인 입력을 그대로 넣지 않습니다. concave cost라면 다른 모델링이나 min-cost max-flow의 음수 cycle 안정성까지 다시 봐야 합니다.

## 4. Piecewise Linear Cost

비용이 구간별로 선형이면 각 구간을 capacity가 큰 edge 하나로 만들 수 있습니다.

| 사용량 구간 | marginal cost | edge |
| --- | ---: | --- |
| 1..10 | 2 | cap 10, cost 2 |
| 11..20 | 5 | cap 10, cost 5 |
| 21..30 | 9 | cap 10, cost 9 |

이 방식은 unit edge를 너무 많이 만드는 문제를 줄입니다. 단, 각 구간의 marginal cost는 nondecreasing이어야 convex입니다.

## 5. 모델링 예시

여러 공장에 총 수요 4개를 배분하고, 각 공장의 생산량이 늘수록 추가 비용이 증가한다고 하겠습니다.

```text
source -> factory marginal unit edges
factory marginal unit -> sink
전체 demand 4만큼 flow를 보냄
```

공장별 누적 비용은 아래와 같습니다.

| 공장 | `C(0)` | `C(1)` | `C(2)` | `C(3)` |
| --- | ---: | ---: | ---: | ---: |
| A | 0 | 2 | 5 | 10 |
| B | 0 | 3 | 4 | 8 |

각 공장의 marginal cost는 누적 비용의 차분입니다.

| 공장 | 1번째 unit | 2번째 unit | 3번째 unit |
| --- | ---: | ---: | ---: |
| A | 2 | 3 | 5 |
| B | 3 | 1 | 4 |

여기서 A는 convex이지만 B는 `3, 1, 4`로 감소 구간이 있어 convex가 아닙니다. Convex Cost Flow로 그대로 넣기 전에 이 조건 위반을 발견해야 합니다. 만약 B의 비용표가 `0, 1, 4, 8`이었다면 marginal cost는 `1, 3, 4`가 되어 아래처럼 안전하게 edge split을 만들 수 있습니다.

```text
source -> A1 cap 1 cost 2
source -> A2 cap 1 cost 3
source -> A3 cap 1 cost 5
source -> B1 cap 1 cost 1
source -> B2 cap 1 cost 3
source -> B3 cap 1 cost 4

A1, A2, A3 -> sink cap 1 cost 0
B1, B2, B3 -> sink cap 1 cost 0
```

총 demand 4를 보내면 Min-Cost Flow는 marginal unit을 비용순으로 고릅니다.

| 선택 순서 | unit | marginal cost | 누적 선택 비용 |
| ---: | --- | ---: | ---: |
| 1 | B1 | 1 | 1 |
| 2 | A1 | 2 | 3 |
| 3 | A2 또는 B2 | 3 | 6 |
| 4 | B2 또는 A2 | 3 | 9 |

결과적으로 A에서 2개, B에서 2개를 생산하면 비용은 `A C(2)=5`, `B C(2)=4`, 총 `9`입니다. 같은 cost tie는 어느 쪽을 먼저 골라도 누적 비용은 같습니다.

이 방식은 단순 "싼 unit 정렬"처럼 보이지만, 실제 네트워크에서는 factory capacity, 작업-공장 compatibility, lower bound, assignment edge를 같은 flow 안에 함께 넣을 수 있습니다. 그래서 greedy로 분리해서 풀 수 없는 제약이 섞일 때 가치가 생깁니다.

### Nondecreasing marginal cost가 필요한 이유

아까 B의 원래 비용 `0, 3, 4, 8`을 생각해 봅시다. marginal cost는 `3, 1, 4`입니다. 두 번째 unit이 첫 번째 unit보다 싸기 때문에 "B2만 고르고 B1은 안 고르는" 선택이 edge split 모델에서는 가능해 보입니다.

```text
source -> B1 cap 1 cost 3
source -> B2 cap 1 cost 1
source -> B3 cap 1 cost 4
```

하지만 실제 생산량 2개는 반드시 첫 번째 unit과 두 번째 unit을 함께 포함해야 하므로 비용이 `3+1=4`입니다. unit edge들이 서로 독립이면 Min-Cost Flow는 cost 1짜리 B2를 먼저 선택할 수 있고, 이것은 원래 비용 함수의 prefix 선택 조건을 깨뜨립니다.

따라서 단순 parallel edge split은 marginal cost가 nondecreasing인 convex 비용에서만 안전합니다. 감소 구간이 있다면 prefix dependency를 표현하는 추가 구조를 넣거나, 다른 DP/flow 모델로 바꿔야 합니다.

## 6. Slope Trick과 비교

| 기법 | 잘 맞는 상황 |
| --- | --- |
| Slope Trick | 1차원 convex DP 함수 직접 관리 |
| Convex Cost Flow | 여러 선택/제약이 network 형태 |
| Alien Optimization | 선택 개수 제약을 penalty로 완화 |
| Min-Plus Convolution | 두 convex sequence 결합 |

상태가 선형 순서 하나로 정리되면 Slope Trick이 더 가볍고, 제약이 bipartite/flow network로 얽히면 Convex Cost Flow가 자연스럽습니다.

## 7. 시간 복잡도

| 항목 | 비용 |
| --- | ---: |
| unit split edge 수 | 총 capacity 합 |
| piecewise split edge 수 | 구간 수 |
| min-cost flow | 사용한 알고리즘과 edge 수에 의존 |

convex cost를 무작정 unit edge로 쪼개면 edge 수가 폭발할 수 있습니다. marginal cost가 같은 구간을 합치거나, cost scaling/문제 특화 DP를 고려합니다.

## 8. 자주 하는 실수

1. 누적 비용 `C(k)`를 edge cost로 넣고 marginal cost로 바꾸지 않는다.
2. marginal cost가 감소하는데 convex라고 착각한다.
3. 같은 cost 구간을 합치지 않아 edge 수가 너무 커진다.
4. 음수 marginal cost가 있을 때 potential 초기화나 negative edge 처리를 빼먹는다.
5. demand를 정확히 보내야 하는지, 최대한 많이 보내야 하는지 목적식을 혼동한다.

## 9. 문제를 볼 때 체크할 조건

- 사용량별 비용이 convex인가?
- 비용표를 marginal cost로 바꿨을 때 nondecreasing인가?
- unit split이 시간/메모리에 가능한가, 구간 압축이 필요한가?
- flow network에 다른 capacity/lower bound 제약이 함께 있는가?
- 더 단순한 greedy, DP, Slope Trick으로 풀리는 구조는 아닌가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: convex production cost `/practice/...` 문제 필요 | marginal edge split 이해 | convex cost |
| 표준 | TODO: assignment with penalty `/practice/...` 문제 필요 | min-cost flow 모델 확장 | piecewise linear |
| 응용 | TODO: demand allocation `/practice/...` 문제 필요 | capacity와 convex cost 결합 | network modeling |
| 함정 | TODO: concave cost counterexample `/practice/...` 문제 필요 | 적용 조건 판정 | marginal cost |
