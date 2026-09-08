# Convex DP Optimization

Convex DP Optimization은 DP 전이식의 모양을 보고 어떤 최적화 기법을 골라야 하는지 정리하는 허브입니다. Convex Hull Trick, Li Chao Tree, Slope Trick, Min-Plus Convolution, Kinetic Hull은 모두 강력하지만, 적용 조건이 조금만 어긋나도 틀리거나 과한 구현이 됩니다.

## 결정 트리

| 전이식/문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| `dp[i] = min_j(a[j] * x[i] + b[j])` 꼴이다 | [Convex Hull Trick and Li Chao Tree](pages/convex-hull-trick-li-chao.md) |
| slope나 query x의 단조성에 따라 구현을 골라야 한다 | [Convex Hull Trick Variants](pages/convex-hull-trick-variants.md) |
| CHT를 실제 DP 문제에 끼워 넣는 과정이 어렵다 | [CHT DP Applications](pages/cht-dp-applications.md) |
| 절댓값/median 비용이 누적되어 convex function을 유지한다 | [Slope Trick](pages/slope-trick.md) |
| 두 cost sequence를 `min_i A[i] + B[k-i]`로 합친다 | [Min-Plus Convolution](pages/min-plus-convolution.md) |
| 직선이나 hull이 시간에 따라 움직인다 | [Kinetic Hull](pages/kinetic-hull.md) |
| 직선 삽입과 삭제가 모두 필요하다 | [Fully Dynamic CHT](pages/fully-dynamic-cht.md) |

## 전이식부터 분해하기

`dp[i] = min_j(previous[j] + cost(j, i))`에서 후보 `j`에만 의존하는 항과 현재 위치 `i`에만 의존하는 항을 분리합니다. `m[j] * x[i] + b[j]`로 쓰이면 직선 질의가 됩니다. `j`와 `i`가 비선형으로 섞인 식은 Li Chao Tree를 가져오는 것만으로 해결되지 않습니다.

1차원 convex 수열은 차분이 증가하는지, Monge 비용은 교차 부등식이 성립하는지 봅니다. `argmin`이 `0, 2, 1, 3`처럼 되돌아가는 작은 입력이 있으면 단조 argmin을 전제로 한 최적화는 적용할 수 없습니다. 작은 입력의 전수 DP 비교는 반례를 찾는 방법이며 조건 증명을 대신하지 않습니다.

같은 기울기·같은 비용의 tie-break도 조건에 포함됩니다. 분할정복 전이 구현은 [Divide and Conquer DP Optimization](https://h.readiz.com/learn/divide-and-conquer-dp-optimization)에 두고, 이 개요에서는 식과 적용 조건을 구분합니다.

| 구현 | 조건 |
| --- | --- |
| Deque CHT | slope 삽입과 query x가 모두 단조 |
| Hull + 이분 탐색 | slope 삽입만 단조 |
| Li Chao Tree | 일반 삽입·질의 순서, 정해진 x 범위 |
| D&C DP | layer별 argmin 단조 |
| SMAWK | totally monotone matrix |
| Slope Trick | convex piecewise-linear 함수 갱신 |

## 연습

[로컬 연습](pages/practice-set.md)에서 입력과 검증 기준을 확인합니다.
