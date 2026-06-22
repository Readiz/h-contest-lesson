# Min-Plus Convolution

Min-Plus Convolution은 두 수열 `A`, `B`에서 `C[k] = min_i A[i] + B[k-i]`를 계산하는 연산입니다. 일반적으로는 느리지만, convex sequence, Monge 성질, DP 전이 구조가 있으면 argmin 단조성을 이용해 크게 줄일 수 있습니다.

이 레슨은 Convex Cost Flow, Slope Trick, Monge와 SMAWK 이후에 보는 DP 최적화 심화입니다.

1. DP 전이가 min-plus convolution 형태인지 확인한다.
2. 제한이 없으면 naive `O(NM)`이 기본이다.
3. convex/Monge 조건이 있으면 argmin monotonicity로 divide and conquer를 적용한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: DP transition, convex sequence, Monge inequality, divide and conquer optimization
- 함께 보면 좋은 레슨: Monge와 SMAWK, Slope Trick, Convex Cost Flow
- 다음에 볼 레슨: distance transform, convex DP modeling, tropical algebra

## 1. 문제 신호

| 문제 표현 | Min-Plus Convolution 관점 |
| --- | --- |
| 두 비용 배열을 합쳐 총 k개 선택 | `min_i A[i] + B[k-i]` |
| 그룹 DP를 merge한다 | convolution transition |
| 비용이 convex하게 증가 | argmin monotone 후보 |
| 여러 convex penalty를 합친다 | min-plus convolution 반복 |
| max 대신 min, 곱 대신 덧셈 | tropical semiring |

일반 convolution은 곱하고 더하지만, min-plus convolution은 더하고 최솟값을 취합니다. FFT로 바로 빨라지는 형태가 아니라 구조적 성질이 필요합니다.

## 2. 기본 형태

길이 `n`, `m`인 배열에서 결과 길이는 `n + m - 1`입니다.

```text
C[k] = min over i:
  0 <= i < n
  0 <= k - i < m
  A[i] + B[k - i]
```

이 식은 "왼쪽에서 i개, 오른쪽에서 k-i개를 선택"하는 merge DP에서 자주 등장합니다.

## 3. Naive와 Monotone 최적화

아래 구현은 naive와 argmin monotone을 가정한 divide and conquer 버전을 함께 보여 줍니다. convex sequence 조합처럼 argmin이 k에 대해 감소하지 않는 경우에만 최적화 버전을 사용합니다.

```cpp compile-check
#include <algorithm>
#include <functional>
#include <vector>
using namespace std;

struct MinPlusConvolution {
    static const long long INF = (1LL << 60);

    static vector<long long> naive(const vector<long long>& a, const vector<long long>& b) {
        int n = (int)a.size();
        int m = (int)b.size();
        vector<long long> result(n + m - 1, INF);
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < m; ++j) {
                result[i + j] = min(result[i + j], a[i] + b[j]);
            }
        }
        return result;
    }

    static vector<long long> monotoneArgmin(const vector<long long>& a, const vector<long long>& b) {
        int n = (int)a.size();
        int m = (int)b.size();
        int total = n + m - 1;
        vector<long long> result(total, INF);

        function<void(int, int, int, int)> solve = [&](int left, int right, int optLeft, int optRight) {
            if (left > right) {
                return;
            }
            int mid = (left + right) / 2;
            int from = max(0, mid - (m - 1));
            int to = min(n - 1, mid);
            from = max(from, optLeft);
            to = min(to, optRight);

            int bestIndex = from;
            long long bestValue = INF;
            for (int i = from; i <= to; ++i) {
                long long value = a[i] + b[mid - i];
                if (value < bestValue) {
                    bestValue = value;
                    bestIndex = i;
                }
            }
            result[mid] = bestValue;

            solve(left, mid - 1, optLeft, bestIndex);
            solve(mid + 1, right, bestIndex, optRight);
        };

        solve(0, total - 1, 0, n - 1);
        return result;
    }
};
```

`monotoneArgmin`은 조건이 없으면 틀릴 수 있습니다. 최적화 전에는 작은 입력에서 naive 결과와 비교하는 stress test를 먼저 둡니다.

## 4. Convex Sequence 조건

수열 `A`의 차분이 증가하면 convex sequence입니다.

```text
A[i+1] - A[i] <= A[i+2] - A[i+1]
```

두 convex sequence의 min-plus convolution은 다시 convex가 되고, argmin이 단조롭게 움직입니다. 이때 divide and conquer나 더 특화된 linear 알고리즘을 고려할 수 있습니다.

## 5. DP Merge 예시

Tree DP에서 각 child의 선택 개수별 비용을 parent DP에 합치는 상황을 보겠습니다.

```text
newDp[k] = min_i parentDp[i] + childDp[k-i]
```

child가 많으면 merge 비용이 커집니다. 배열 길이 합, convex 여부, small-to-large merge를 함께 봐야 합니다. 모든 child DP가 convex라면 min-plus 최적화가 강하게 작동할 수 있습니다.

## 6. Slope Trick과 비교

| 기법 | 관점 |
| --- | --- |
| Slope Trick | convex 함수에 hinge를 더하며 직접 관리 |
| Min-Plus Convolution | 두 비용 함수를 infimal convolution으로 합침 |
| Convex Cost Flow | 네트워크 제약 안에서 convex marginal cost 선택 |
| Monge/SMAWK | argmin 구조를 행렬 최적화로 계산 |

같은 convex DP라도 함수 update가 단순하면 Slope Trick, 두 함수 merge가 핵심이면 Min-Plus Convolution이 더 직접적입니다.

## 7. 시간 복잡도

| 접근 | 복잡도 |
| --- | ---: |
| naive | `O(NM)` |
| argmin monotone divide and conquer | `O((N+M) log(N+M))` 정도 |
| 특수 convex linear algorithm | 조건에 따라 `O(N+M)` |
| tree DP repeated merge | 총 상태 수와 merge 순서에 의존 |

최적화의 전제 조건을 증명하지 못하면 naive나 제한 기반 pruning으로 돌아가는 편이 안전합니다.

## 8. 자주 하는 실수

1. 일반 convolution처럼 FFT로 풀 수 있다고 착각한다.
2. argmin 단조성이 없는데 divide and conquer를 적용한다.
3. 결과 index `k`에서 가능한 `i` 범위를 잘못 잡는다.
4. `INF + value` overflow를 확인하지 않는다.
5. max-plus와 min-plus를 부호 변환 없이 섞는다.

## 9. 문제를 볼 때 체크할 조건

- 전이가 정말 `min_i A[i] + B[k-i]` 형태인가?
- 수열이 convex이거나 Monge 조건을 만족하는가?
- argmin이 k에 따라 단조롭다는 증거가 있는가?
- 배열 길이 합이 작아 naive merge가 충분하지는 않은가?
- 여러 번 merge한다면 순서를 바꿔 총 비용을 줄일 수 있는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: min-plus convolution `/practice/...` 문제 필요 | naive merge 구현 | DP merge |
| 표준 | TODO: convex sequence merge `/practice/...` 문제 필요 | argmin monotone 확인 | convex cost |
| 응용 | TODO: tree DP convolution `/practice/...` 문제 필요 | small-to-large merge | group DP |
| 함정 | TODO: non-convex counterexample `/practice/...` 문제 필요 | 최적화 조건 판정 | monotonicity |
