# Convex DP Optimization

Convex DP Optimization은 DP 전이식의 모양을 보고 어떤 최적화 기법을 골라야 하는지 정리하는 허브입니다. Convex Hull Trick, Li Chao Tree, Slope Trick, Min-Plus Convolution, Kinetic Hull은 모두 강력하지만, 적용 조건이 조금만 어긋나도 틀리거나 과한 구현이 됩니다.

이 허브의 목표는 개별 자료구조를 평면적으로 나열하지 않고, 아래 질문에서 시작하게 하는 것입니다.

1. 전이가 `line at x` 꼴로 분리되는가?
2. 최적 decision index가 단조인가?
3. convex piecewise-linear function 자체를 유지해야 하는가?
4. 두 cost 배열을 min-plus로 합치는 문제인가?
5. 직선 집합이 시간에 따라 움직이거나 삭제되는가?

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Dynamic Programming, Segment Tree, Divide and Conquer DP Optimization
- 함께 보면 좋은 레슨: Monge and SMAWK, Parametric Optimization, Convex Cost Flow, Versioned Data Structures
- 다음에 볼 레슨: Offline and Time-Axis Techniques, Geometry Sweep

Parametric Optimization은 이 허브의 prerequisite이 아니라 related track입니다. `lambda`나 penalty를 고정해 DP oracle을 만드는 문제는 Parametric Optimization 쪽으로, 이미 주어진 DP 전이식의 최적화 구조를 판정하는 문제는 이 허브로 들어옵니다.

## 1. 결정 트리

| 전이식/문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| `dp[i] = min_j(a[j] * x[i] + b[j])` 꼴이다 | [Convex Hull Trick and Li Chao Tree](pages/convex-hull-trick-li-chao.md) |
| slope나 query x의 단조성에 따라 구현을 골라야 한다 | [Convex Hull Trick Variants](pages/convex-hull-trick-variants.md) |
| CHT를 실제 DP 문제에 끼워 넣는 과정이 어렵다 | [CHT DP Applications](pages/cht-dp-applications.md) |
| 절댓값/median 비용이 누적되어 convex function을 유지한다 | [Slope Trick](pages/slope-trick.md) |
| 두 cost sequence를 `min_i A[i] + B[k-i]`로 합친다 | [Min-Plus Convolution](pages/min-plus-convolution.md) |
| 직선이나 hull이 시간에 따라 움직인다 | [Kinetic Hull](pages/kinetic-hull.md) |
| 직선 삽입과 삭제가 모두 필요하다 | [Fully Dynamic CHT](pages/fully-dynamic-cht.md) |
| 조건을 먼저 판정해야 한다 | [Technique Decision Tree](pages/technique-decision-tree.md), [Convex DP Modeling](pages/convex-dp-modeling.md) |

## 2. 먼저 증명할 조건

| 기법 | 필요한 조건 |
| --- | --- |
| Deque CHT | slope 추가 순서와 query x 순서가 단조이거나, 한쪽 단조성과 이분 탐색이 가능 |
| Li Chao Tree | query x domain이 정해져 있고 line 삽입/point query로 모델링 가능 |
| D&C DP Optimization | 각 layer의 argmin index가 단조 |
| Monge/SMAWK | cost matrix가 Monge 또는 totally monotone |
| Slope Trick | 유지하는 함수가 convex piecewise-linear |
| Min-Plus Convolution | sequence 구조가 일반인지, convex/Monge 특수형인지 구분 |

## 3. 공개 상태

하위 페이지들은 구현과 판단 기준을 담고 있습니다. [Practice Set](pages/practice-set.md)은 line-query DP를 Li Chao Tree로 계산하는 로컬 구현, trace, stress 기준을 대표 흐름으로 제공합니다.
