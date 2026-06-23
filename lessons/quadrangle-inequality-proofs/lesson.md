# Quadrangle Inequality Proofs

Quadrangle Inequality Proofs는 Knuth Optimization, Monge 최적화, divide-and-conquer DP 최적화를 적용하기 전에 필요한 부등식과 opt 단조성 증명 패턴을 정리하는 DP 최적화 레슨입니다. 알고리즘 구현보다 "왜 후보 범위를 줄여도 되는가"를 확인하는 것이 목표입니다.

이 레슨은 Knuth Optimization, Monge와 SMAWK, Divide and Conquer DP Optimization 이후에 보는 전략 심화입니다.

1. quadrangle inequality와 Monge inequality가 같은 모양의 조건임을 이해한다.
2. opt monotonicity는 증명하거나 작은 반례 탐색으로 의심해야 한다.
3. Knuth 조건은 단순히 `cost`가 볼록해 보인다는 감각만으로 적용하지 않는다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: interval DP, Monge array, Knuth optimization, argmin monotonicity
- 함께 보면 좋은 레슨: Knuth Optimization, Monge와 SMAWK, Convex DP Modeling
- 다음에 볼 레슨: min-plus convolution, convex DP modeling, parametric DP

## 1. 문제 신호

| 문제 표현 | 증명 관점 |
| --- | --- |
| interval DP에서 split point가 단조 | Knuth optimization 후보 |
| `cost(a,c)+cost(b,d) <= cost(a,d)+cost(b,c)` | quadrangle inequality |
| 행렬 row minima가 오른쪽으로만 이동 | Monge/totally monotone |
| editorial이 "opt monotone"만 말함 | tie-breaking 포함 확인 |
| 조건이 애매함 | 작은 brute force로 반례 탐색 |

최적화는 구현보다 적용 조건이 더 중요합니다. 조건이 틀리면 빠르게 틀린 답을 냅니다.

## 2. Quadrangle Inequality

구간 cost `w(l, r)`가 있을 때 보통 아래 조건을 봅니다.

```text
a <= b <= c <= d
w(a, c) + w(b, d) <= w(a, d) + w(b, c)
```

이는 "교차하지 않는 짝이 교차 짝보다 좋다"는 Monge 형태입니다. interval length가 커질수록 marginal cost가 일정 방향으로 움직이면 자주 성립합니다.

## 3. Knuth Optimization 조건

대표적인 interval DP는 아래 꼴입니다.

```text
dp[l][r] = min k in [l, r):
  dp[l][k] + dp[k+1][r] + w(l, r)
```

Knuth optimization을 쓰려면 보통 아래 단조성이 필요합니다.

```text
opt[l][r-1] <= opt[l][r] <= opt[l+1][r]
```

이 단조성은 quadrangle inequality와 monotone interval cost 조건에서 나옵니다. 문제마다 index convention이 다르므로 `k`, `k+1` 경계를 먼저 통일해야 합니다.

## 4. 작은 예시

파일 합치기 DP에서 `w(l, r) = prefix[r] - prefix[l-1]`는 구간 합입니다.

```text
a <= b <= c <= d
w(a,c) + w(b,d)
= sum[a..c] + sum[b..d]

w(a,d) + w(b,c)
= sum[a..d] + sum[b..c]
```

두 식은 같은 원소 합을 다른 방식으로 센 것이어서 같은 값입니다. 따라서 quadrangle inequality가 등호로 성립하고 Knuth optimization 후보가 됩니다.

## 5. 반례를 찾는 습관

증명이 애매하면 작은 입력에서 opt가 단조인지 먼저 확인합니다. 아래 함수는 이미 계산된 `opt[l][r]` 테이블에서 Knuth 단조성을 검사합니다.

```cpp compile-check
#include <vector>
using namespace std;

bool checkKnuthOptMonotone(const vector<vector<int>>& opt) {
    int n = (int)opt.size();
    for (int length = 2; length < n; ++length) {
        for (int left = 0; left + length < n; ++left) {
            int right = left + length;
            if (opt[left][right] < opt[left][right - 1]) {
                return false;
            }
            if (opt[left][right] > opt[left + 1][right]) {
                return false;
            }
        }
    }
    return true;
}
```

이 검사는 증명을 대신하지는 못하지만, 잘못된 직관을 빨리 잡아냅니다. 특히 tie-breaking을 작은 `k`로 할지 큰 `k`로 할지에 따라 단조성이 흔들릴 수 있습니다.

## 6. Monge Row Minima와 연결

DP 전이가 아래처럼 행렬 최소값으로 표현되면 Monge 조건을 볼 수 있습니다.

```text
dp[i] = min_j A[i][j]
A[i][j] = previous[j] + cost(j, i)
```

`A`가 Monge이면 row minimum index가 단조입니다. 그러면 divide-and-conquer row minima나 SMAWK를 적용할 수 있습니다.

## 7. 증명 패턴

| 패턴 | 확인할 것 |
| --- | --- |
| 구간 합 | 두 식을 전개해 같은 항이 어떻게 상쇄되는지 본다 |
| 거리/정렬 cost | crossing pair를 uncrossing했을 때 비용이 줄어드는지 본다 |
| convex cost | marginal difference가 단조인지 본다 |
| DP split | opt가 왼쪽/오른쪽으로 이동할 때 교환 논증을 만든다 |
| max/min 방향 전환 | inequality 부호가 뒤집히는지 확인한다 |

증명은 보통 "두 후보를 교차시킨 상태보다 정렬된 상태가 낫다"는 uncrossing 논리로 정리됩니다.

## 8. 조건별 적용 알고리즘

| 확인한 조건 | 쓸 수 있는 최적화 |
| --- | --- |
| `opt[i][j]` 후보 범위가 단조 | divide-and-conquer DP |
| interval DP에서 Knuth bound 성립 | Knuth optimization |
| cost matrix가 Monge | monotone row minima, SMAWK |
| convex hull 형태 전이 | CHT 또는 Li Chao |
| 조건 없음 | 최적화 적용 금지 |

비슷해 보이는 최적화끼리도 요구 조건이 다릅니다. editorial의 키워드만 보고 바꿔 끼우면 위험합니다.

## 9. 자주 하는 실수

1. Monge inequality의 부호를 min/max 방향과 반대로 쓴다.
2. `a <= b <= c <= d` index 조건을 무시하고 임의 네 점에 적용한다.
3. opt tie-breaking을 고정하지 않아 단조성이 깨진다.
4. Knuth optimization을 divide-and-conquer DP 조건만으로 적용한다.
5. 작은 반례에서 opt가 감소하는데도 cost가 볼록해 보인다는 이유로 진행한다.

## 10. 문제를 볼 때 체크할 조건

- DP 전이가 어떤 행렬 또는 interval cost로 표현되는가?
- 필요한 inequality를 정확히 쓸 수 있는가?
- opt 단조성이 tie-breaking 후에도 유지되는가?
- 작은 brute force에서 반례가 없는가?
- 최적화 후 후보 범위가 빈 구간이 되지 않는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: quadrangle inequality `/practice/...` 문제 필요 | 구간 합 cost 전개 | interval DP |
| 표준 | TODO: Knuth proof `/practice/...` 문제 필요 | opt bound 증명 | monotone opt |
| 응용 | TODO: Monge DP proof `/practice/...` 문제 필요 | row minima 단조성 연결 | Monge array |
| 함정 | TODO: non-Monge counterexample `/practice/...` 문제 필요 | 반례 생성과 tie-breaking 확인 | inequality |

