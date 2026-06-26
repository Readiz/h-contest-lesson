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

## 3. 손으로 계산하는 작은 예시

아래 두 convex sequence를 min-plus convolution 해 보겠습니다.

```text
A = [0, 2, 5, 9]
B = [0, 1, 4, 10]
C[k] = min_i A[i] + B[k-i]
```

각 `k`에서 가능한 `i`를 모두 써 보면 opt가 오른쪽으로만 움직이는 것을 볼 수 있습니다. tie가 있으면 가장 작은 `i`를 고른다고 하겠습니다.

| `k` | 가능한 값 | `C[k]` | opt `i` |
| ---: | --- | ---: | ---: |
| 0 | `A0+B0 = 0` | 0 | 0 |
| 1 | `A0+B1 = 1`, `A1+B0 = 2` | 1 | 0 |
| 2 | `A0+B2 = 4`, `A1+B1 = 3`, `A2+B0 = 5` | 3 | 1 |
| 3 | `A0+B3 = 10`, `A1+B2 = 6`, `A2+B1 = 6`, `A3+B0 = 9` | 6 | 1 |
| 4 | `A1+B3 = 12`, `A2+B2 = 9`, `A3+B1 = 10` | 9 | 2 |
| 5 | `A2+B3 = 15`, `A3+B2 = 13` | 13 | 3 |
| 6 | `A3+B3 = 19` | 19 | 3 |

opt sequence는 `0, 0, 1, 1, 2, 3, 3`입니다. `k`가 증가할 때 최적 `i`가 감소하지 않으므로, 가운데 `k`를 먼저 계산하고 왼쪽 구간은 `optLeft..bestIndex`, 오른쪽 구간은 `bestIndex..optRight`로 줄이는 divide and conquer가 가능합니다.

반대로 아래처럼 convex/Monge 조건이 깨지면 opt가 바로 감소할 수 있습니다.

```text
A = [0, 0, 100]
B = [0, 100, 0]
```

`k=1`에서는 `A1+B0=0`이 최적이라 opt가 1이지만, `k=2`에서는 `A0+B2=0`이 최적이라 opt가 0으로 되돌아갑니다. 이런 입력에 monotone D&C를 적용하면 탐색 후보를 잘못 버립니다.

## 4. Naive와 Monotone 최적화

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

## 5. Convex Sequence 조건

수열 `A`의 차분이 증가하면 convex sequence입니다.

```text
A[i+1] - A[i] <= A[i+2] - A[i+1]
```

두 convex sequence의 min-plus convolution은 다시 convex가 되고, argmin이 단조롭게 움직입니다. 이때 divide and conquer나 더 특화된 linear 알고리즘을 고려할 수 있습니다.

핵심은 "convex라는 단어가 보인다"가 아니라 실제로 아래 중 하나를 설명할 수 있어야 한다는 점입니다.

1. 두 수열의 차분이 nondecreasing이다.
2. 비용 행렬 `M[k][i] = A[i] + B[k-i]`가 Monge 성질을 가진다.
3. 작은 stress에서 보이는 현상을 넘어, opt가 감소하지 않는다는 증명을 문제 구조에서 끌어낼 수 있다.

## 6. DP Merge 예시

Tree DP에서 각 child의 선택 개수별 비용을 parent DP에 합치는 상황을 보겠습니다.

```text
newDp[k] = min_i parentDp[i] + childDp[k-i]
```

child가 많으면 merge 비용이 커집니다. 배열 길이 합, convex 여부, small-to-large merge를 함께 봐야 합니다. 모든 child DP가 convex라면 min-plus 최적화가 강하게 작동할 수 있습니다.

## 7. Slope Trick과 비교

| 기법 | 관점 |
| --- | --- |
| Slope Trick | convex 함수에 hinge를 더하며 직접 관리 |
| Min-Plus Convolution | 두 비용 함수를 infimal convolution으로 합침 |
| Convex Cost Flow | 네트워크 제약 안에서 convex marginal cost 선택 |
| Monge/SMAWK | argmin 구조를 행렬 최적화로 계산 |

같은 convex DP라도 함수 update가 단순하면 Slope Trick, 두 함수 merge가 핵심이면 Min-Plus Convolution이 더 직접적입니다.

## 8. 시간 복잡도와 적용 조건

### 8.1 naive가 충분한 경우

배열 길이 합이 작거나 merge 횟수가 적으면 `O(NM)`이 가장 안전합니다. 특히 상태 수 제한, pruning, small-to-large merge만으로 통과하는 문제라면 opt 단조성을 억지로 증명할 필요가 없습니다.

### 8.2 opt monotone이 증명되는 경우

`argmin(k)`가 감소하지 않는다는 것을 증명할 수 있으면 divide and conquer 최적화를 씁니다. 위 구현처럼 결과 index 구간을 반으로 나누고 opt 후보 범위를 함께 줄이면 대략 `O((N+M) log(N+M))` 스캔으로 줄어듭니다.

### 8.3 convex sequence라서 더 특수한 알고리즘이 가능한 경우

두 수열이 discrete convex이고 문제에서 필요한 연산이 순수 min-plus convolution이면 더 특화된 `O(N+M)` 계열 알고리즘을 검토할 수 있습니다. 다만 구현 난도가 높고 전제 조건이 좁기 때문에, 대회 풀이에서는 Monge/SMAWK 또는 D&C 최적화로 충분한지 먼저 계산합니다.

### 8.4 조건을 못 증명하면 쓰면 안 되는 경우

최적화의 전제 조건을 증명하지 못하면 naive나 제한 기반 pruning으로 돌아가는 편이 안전합니다. 특히 입력 비용이 임의 배열이거나, DP transition에 추가 조건이 붙어 행렬이 Monge가 아니면 monotone D&C는 답을 틀릴 수 있습니다.

| 접근 | 복잡도 | 사용할 조건 |
| --- | ---: | --- |
| naive | `O(NM)` | 항상 안전 |
| argmin monotone divide and conquer | 대략 `O((N+M) log(N+M))` | opt 단조성 증명 필요 |
| 특수 convex linear algorithm | 조건에 따라 `O(N+M)` | discrete convex 조건과 전용 구현 필요 |
| tree DP repeated merge | 총 상태 수와 merge 순서에 의존 | merge 순서와 상태 크기 관리 필요 |

## 9. 자주 하는 실수

1. 일반 convolution처럼 FFT로 풀 수 있다고 착각한다.
2. argmin 단조성이 없는데 divide and conquer를 적용한다.
3. 결과 index `k`에서 가능한 `i` 범위를 잘못 잡는다.
4. `INF + value` overflow를 확인하지 않는다.
5. max-plus와 min-plus를 부호 변환 없이 섞는다.

## 10. 문제를 볼 때 체크할 조건

- 전이가 정말 `min_i A[i] + B[k-i]` 형태인가?
- 수열이 convex이거나 Monge 조건을 만족하는가?
- argmin이 k에 따라 단조롭다는 증거가 있는가?
- 배열 길이 합이 작아 naive merge가 충분하지는 않은가?
- 여러 번 merge한다면 순서를 바꿔 총 비용을 줄일 수 있는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: min-plus convolution `/practice/...` 문제 필요 | naive merge 구현 | DP merge |
| 표준 | TODO: convex sequence merge `/practice/...` 문제 필요 | argmin monotone 확인 | convex cost |
| 응용 | TODO: tree DP convolution `/practice/...` 문제 필요 | small-to-large merge | group DP |
| 함정 | TODO: non-convex counterexample `/practice/...` 문제 필요 | 최적화 조건 판정 | monotonicity |
