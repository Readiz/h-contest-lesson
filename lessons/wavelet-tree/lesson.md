# Wavelet Tree

Wavelet Tree는 값의 범위와 index 범위를 동시에 나누어, 정적 배열에서 k번째 작은 값, 특정 값 이하 개수, 구간 frequency 같은 질의를 빠르게 처리하는 자료구조입니다. Persistent Segment Tree와 비슷한 질의를 다루지만, 배열 자체를 값 기준으로 재귀적으로 나눈다는 관점이 다릅니다.

이 레슨은 정적 order statistic 질의의 또 다른 표준 도구로 Wavelet Tree를 봅니다.

1. 값 범위를 가운데로 나누어 왼쪽/오른쪽 child로 원소를 보낸다.
2. prefix count 배열로 구간 `[l, r]`이 child에서 어디로 가는지 계산한다.
3. kth, LTE, frequency 질의를 재귀적으로 처리한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 좌표 압축, Segment Tree, Persistent Segment Tree
- 함께 보면 좋은 레슨: Persistent Segment Tree, 오프라인 쿼리, 좌표 압축
- 다음에 볼 레슨: wavelet matrix, succinct data structure

## 1. 문제 신호

Wavelet Tree는 배열이 바뀌지 않는 정적 질의에서 강합니다.

| 질의 | Wavelet Tree 관점 |
| --- | --- |
| 구간에서 k번째 작은 값 | 값 범위를 내려가며 왼쪽 개수 확인 |
| 구간에서 `<= x` 개수 | 값 범위와 query 값 비교 |
| 구간에서 값 `x` 빈도 | x가 속한 child로 index 변환 |
| 구간 median | kth 질의 |
| 많은 정적 range order query | `O(log valueRange)` |

업데이트가 필요하면 다른 구조가 필요합니다. 정적 배열이면 Persistent Segment Tree보다 구현과 메모리 특성이 더 나을 수 있습니다.

## 2. 핵심 구조

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

## 3. 기본 구현

아래 구현은 1-indexed query를 사용합니다.

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

## 4. k번째 값 질의

구간 `[l, r]`에서 k번째 작은 값을 찾을 때는 왼쪽 child로 간 원소 수를 먼저 봅니다.

```text
leftCount = prefixLeft[r] - prefixLeft[l - 1]
```

`k <= leftCount`이면 답은 왼쪽 값 범위에 있습니다. 그렇지 않으면 오른쪽으로 가고, `k`에서 `leftCount`를 뺍니다.

이 과정은 값 범위가 leaf가 될 때까지 반복됩니다.

## 5. 값 빈도와 rank

값 `x`의 구간 빈도는 `<= x` 개수에서 `< x` 개수를 빼면 됩니다.

```text
freq(l, r, x) = countLessOrEqual(l, r, x) - countLessOrEqual(l, r, x - 1)
```

좌표 압축을 쓴다면 `x - 1`이 아니라 압축 순서에서 이전 값까지를 묻는 방식으로 바꿉니다.

## 6. Persistent Segment Tree와 비교

| 구조 | 장점 | 주의점 |
| --- | --- | --- |
| Persistent Segment Tree | prefix version 차이가 직관적 | node 수와 포인터/배열 관리 |
| Wavelet Tree | 정적 배열 질의가 compact | update 어려움, build가 배열을 재배치 |
| Merge Sort Tree | 구현 쉬움 | kth는 이분 탐색과 count query 조합 |

둘 다 정적 구간 order statistic을 풀 수 있습니다. 이미 prefix version 모델이 자연스러운 문제는 Persistent Segment Tree가, 다양한 rank/frequency 질의가 섞이면 Wavelet Tree가 편할 수 있습니다.

## 7. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| build | `O(N log V)` | `O(N log V)` bits/ints |
| kth query | `O(log V)` | 없음 |
| count `<= x` | `O(log V)` | 없음 |
| frequency | `O(log V)` | 없음 |

여기서 `V`는 값 범위 또는 압축된 값 개수입니다. 큰 값 범위에서는 좌표 압축으로 `log V`를 줄이는 편이 좋습니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| query index를 0-index와 섞음 | 한 칸 밀림 | public query를 1-index로 고정 |
| 오른쪽 child index 변환 오류 | kth 오답 | `rightL = l - leftBefore` 확인 |
| `stable_partition`이 원본을 바꾸는 점 무시 | 이후 배열 사용 오류 | build용 복사본 사용 |
| 빈 child에서 재귀 호출 | null 접근 | child 존재 또는 count 확인 |
| k 범위 검증 누락 | leaf까지 잘못 이동 | `1 <= k <= r-l+1` 확인 |
| 좌표 압축 복원 누락 | 압축 값 출력 | 원래 값 배열로 복원 |

## 9. 문제를 볼 때 체크할 조건

1. 배열이 정적인가?
2. 구간 kth, rank, frequency 질의가 많은가?
3. 값 범위를 압축할 수 있는가?
4. query index 기준을 1-index로 유지할 수 있는가?
5. 업데이트가 필요한 문제는 아닌가?
6. Persistent Segment Tree나 Merge Sort Tree보다 Wavelet Tree가 더 자연스러운가?

Wavelet Tree는 값 기준 분할과 index 구간 변환을 동시에 이해해야 합니다. `prefixLeft`가 "이 구간이 child에서 어디로 이동하는가"를 알려 준다는 감각이 핵심입니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 구간 kth `/practice/...` 문제 필요 | `prefixLeft`로 child index 변환 | kth order statistic |
| 표준 | TODO: 구간 `<= x` 개수 `/practice/...` 문제 필요 | 값 범위 재귀와 rank query | range rank |
| 응용 | TODO: 구간 frequency `/practice/...` 문제 필요 | `<= x`와 `< x` 차이 | frequency |
| 함정 | TODO: 좌표 압축 wavelet `/practice/...` 문제 필요 | 압축 값 복원과 큰 값 범위 | compression |
