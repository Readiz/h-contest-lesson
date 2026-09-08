# Wavelet Tree

Wavelet Tree는 값의 범위와 index 범위를 동시에 나누어, 정적 배열에서 k번째 작은 값, 특정 값 이하 개수, 구간 frequency 같은 질의를 빠르게 처리하는 자료구조입니다. Persistent Segment Tree와 비슷한 질의를 다루지만, 배열 자체를 값 기준으로 재귀적으로 나눈다는 관점이 다릅니다.

## 문제 신호

Wavelet Tree는 배열이 바뀌지 않는 정적 질의에서 강합니다.

| 질의 | Wavelet Tree 관점 |
| --- | --- |
| 구간에서 k번째 작은 값 | 값 범위를 내려가며 왼쪽 개수 확인 |
| 구간에서 `<= x` 개수 | 값 범위와 query 값 비교 |
| 구간에서 값 `x` 빈도 | x가 속한 child로 index 변환 |
| 구간 median | kth 질의 |
| 많은 정적 range order query | `O(log valueRange)` |

업데이트가 필요하면 다른 구조가 필요합니다. 정적 배열이면 Persistent Segment Tree보다 구현과 메모리 특성이 더 나을 수 있습니다.

## 핵심 구조

각 node는 값 범위 `[low, high]`를 담당합니다. 원소를 `mid = (low + high) / 2` 기준으로 나눕니다.

```text
left child: value <= mid
right child: value > mid
```

`prefixLeft[i]`는 이 node의 앞 `i`개 원소 중 왼쪽 child로 간 원소 수입니다. 그러면 원래 node의 구간 `[l, r]`이 왼쪽 child에서는 아래 범위가 됩니다.

```text
leftL = prefixLeft[l - 1] + 1
leftR = prefixLeft[r]
```

오른쪽 child는 왼쪽으로 가지 않은 개수를 이용합니다.

## 기본 구현

아래 구현은 `1 <= l <= r <= N`, `1 <= k <= r-l+1`인 1-indexed query를 사용합니다. 값은 `[low,high]` 안이고 `high-low`가 int 범위 안이어야 합니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct WaveletTree {
    int low;
    int high;
    WaveletTree* left = nullptr;
    WaveletTree* right = nullptr;
    vector<int> prefixLeft;

    WaveletTree(vector<int>::iterator from, vector<int>::iterator to, int low, int high)
        : low(low), high(high) {
        if (from >= to || low == high) {
            return;
        }

        int mid = low + (high - low) / 2;
        auto goesLeft = [mid](int value) {
            return value <= mid;
        };

        prefixLeft.reserve((int)(to - from) + 1);
        prefixLeft.push_back(0);
        for (auto it = from; it != to; ++it) {
            prefixLeft.push_back(prefixLeft.back() + (goesLeft(*it) ? 1 : 0));
        }

        auto pivot = stable_partition(from, to, goesLeft);
        if (from < pivot) {
            left = new WaveletTree(from, pivot, low, mid);
        }
        if (pivot < to) {
            right = new WaveletTree(pivot, to, mid + 1, high);
        }
    }

    WaveletTree(const WaveletTree&) = delete;
    WaveletTree& operator=(const WaveletTree&) = delete;

    ~WaveletTree() {
        delete left;
        delete right;
    }

    int kth(int l, int r, int k) const {
        if (low == high) {
            return low;
        }

        int leftBefore = prefixLeft[l - 1];
        int leftInRange = prefixLeft[r] - leftBefore;
        if (k <= leftInRange) {
            return left->kth(leftBefore + 1, prefixLeft[r], k);
        }

        int rightL = l - leftBefore;
        int rightR = r - prefixLeft[r];
        return right->kth(rightL, rightR, k - leftInRange);
    }

    int countLessOrEqual(int l, int r, int value) const {
        if (l > r || value < low) {
            return 0;
        }
        if (high <= value) {
            return r - l + 1;
        }

        int leftBefore = prefixLeft[l - 1];
        int leftNow = prefixLeft[r];
        int result = 0;
        if (left) {
            result += left->countLessOrEqual(leftBefore + 1, leftNow, value);
        }
        if (right) {
            int rightL = l - leftBefore;
            int rightR = r - leftNow;
            result += right->countLessOrEqual(rightL, rightR, value);
        }
        return result;
    }
};
```

생성자에서 배열을 재배치하므로 원본 배열을 보존해야 한다면 복사본으로 tree를 만듭니다.

## k번째 값 질의

구간 `[l, r]`에서 k번째 작은 값을 찾을 때는 왼쪽 child로 간 원소 수를 먼저 봅니다.

```text
leftCount = prefixLeft[r] - prefixLeft[l - 1]
```

`k <= leftCount`이면 답은 왼쪽 값 범위에 있습니다. 그렇지 않으면 오른쪽으로 가고, `k`에서 `leftCount`를 뺍니다.

이 과정은 값 범위가 leaf가 될 때까지 반복됩니다.

## 값 빈도와 rank

값 `x`의 구간 빈도는 `<= x` 개수에서 `< x` 개수를 빼면 됩니다.

```text
freq(l, r, x) = countLessOrEqual(l, r, x) - countLessOrEqual(l, r, x - 1)
```

`x`가 int 최솟값이면 `x-1`을 계산하지 말고 두 번째 항을 0으로 둡니다. 좌표 압축을 쓴다면 압축 순서의 이전 값까지를 묻습니다.

## Persistent Segment Tree와 비교

| 구조 | 장점 | 주의점 |
| --- | --- | --- |
| Persistent Segment Tree | prefix version 차이가 직관적 | node 수와 포인터/배열 관리 |
| Wavelet Tree | 정적 배열 질의가 compact | update 어려움, build가 배열을 재배치 |
| Merge Sort Tree | 구현 쉬움 | kth는 이분 탐색과 count query 조합 |

둘 다 정적 구간 order statistic을 풀 수 있습니다. 이미 prefix version 모델이 자연스러운 문제는 Persistent Segment Tree가, 다양한 rank/frequency 질의가 섞이면 Wavelet Tree가 편할 수 있습니다.

## 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| build | `O(N log V)` | `O(N log V)`개의 int |
| kth query | `O(log V)` | 없음 |
| count `<= x` | `O(log V)` | 없음 |
| frequency | `O(log V)` | 없음 |

여기서 `V`는 값 범위 또는 압축된 값 개수입니다. 큰 값 범위에서는 좌표 압축으로 `log V`를 줄이는 편이 좋습니다.
