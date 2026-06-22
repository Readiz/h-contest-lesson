# Wavelet Matrix

Wavelet Matrix는 Wavelet Tree의 포인터 구조를 level별 bitvector로 평평하게 만든 자료구조입니다. 정적 배열에서 구간 kth, rank, frequency, 값 범위 count를 빠르게 처리하며, 큰 값 범위에서도 메모리 locality가 좋습니다.

이 레슨은 Wavelet Tree 이후에 보는 같은 아이디어의 더 구현 친화적인 형태입니다.

1. 값을 bit의 높은 자리부터 본다.
2. 각 level에서 0-bit 원소를 앞, 1-bit 원소를 뒤로 안정적으로 재배치한다.
3. bitvector rank로 원래 구간이 다음 level에서 어디로 이동하는지 계산한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 좌표 압축, Wavelet Tree, prefix count, bit operation
- 함께 보면 좋은 레슨: Wavelet Tree, Persistent Segment Tree, 오프라인 쿼리
- 다음에 볼 레슨: succinct bitvector, compressed wavelet matrix, range quantile

## 1. 문제 신호

| 질의 | Wavelet Matrix 관점 |
| --- | --- |
| 구간 `[l, r)`의 k번째 작은 값 | bit를 내려가며 0쪽 개수와 k 비교 |
| 구간에서 `< x` 개수 | x의 bit를 따라가며 0쪽 개수 누적 |
| 구간에서 `[a, b)` 값 개수 | `countLess(b) - countLess(a)` |
| 값 x의 빈도 | `[x, x+1)` count |
| 정적 배열의 많은 order statistic | Wavelet Matrix 후보 |

배열 업데이트가 있으면 일반 Wavelet Matrix만으로는 부족합니다. 이 레슨은 static query를 전제로 합니다.

## 2. Wavelet Tree와 차이

Wavelet Tree는 node마다 값 범위를 나누고 child pointer를 둡니다. Wavelet Matrix는 모든 node를 level별 배열 하나로 합칩니다.

| 구조 | 특징 |
| --- | --- |
| Wavelet Tree | 재귀 node, 값 범위가 직관적 |
| Wavelet Matrix | level별 bitvector, 구현과 캐시 locality가 좋음 |

핵심 질의 원리는 같습니다. 각 level에서 구간 `[l, r)`이 다음 level의 0 영역 또는 1 영역 어디로 이동하는지 rank로 계산합니다.

## 3. BitVector Rank

가장 먼저 필요한 것은 bitvector의 prefix rank입니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct BitVectorRank {
    vector<int> prefixOne;

    void build(const vector<int>& bits) {
        prefixOne.assign(bits.size() + 1, 0);
        for (int i = 0; i < (int)bits.size(); ++i) {
            prefixOne[i + 1] = prefixOne[i] + bits[i];
        }
    }

    int rankOne(int pos) const {
        return prefixOne[pos];
    }

    int rankZero(int pos) const {
        return pos - prefixOne[pos];
    }
};
```

`rankOne(pos)`은 `[0, pos)` 안의 1 개수입니다. 구간 `[l, r)`의 1 개수는 `rankOne(r) - rankOne(l)`입니다.

## 4. 기본 구현

아래 구현은 non-negative `int` 값을 대상으로 합니다. 값 범위가 음수를 포함하면 좌표 압축하거나 unsigned 표현으로 바꿉니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct BitVector {
    vector<int> prefixOne;

    void build(const vector<int>& bits) {
        prefixOne.assign(bits.size() + 1, 0);
        for (int i = 0; i < (int)bits.size(); ++i) {
            prefixOne[i + 1] = prefixOne[i] + bits[i];
        }
    }

    int rankOne(int pos) const {
        return prefixOne[pos];
    }

    int rankZero(int pos) const {
        return pos - prefixOne[pos];
    }
};

struct WaveletMatrix {
    static const int LOG = 31;
    int n = 0;
    vector<BitVector> bitvectors;
    vector<int> zeroCount;

    explicit WaveletMatrix(vector<int> values) {
        n = (int)values.size();
        bitvectors.resize(LOG);
        zeroCount.assign(LOG, 0);

        vector<int> cur = values;
        vector<int> next(n);

        for (int depth = 0; depth < LOG; ++depth) {
            int bit = LOG - 1 - depth;
            vector<int> bits(n, 0);
            int zeros = 0;

            for (int value : cur) {
                if (((value >> bit) & 1) == 0) {
                    ++zeros;
                }
            }
            zeroCount[depth] = zeros;

            int left = 0;
            int right = zeros;
            for (int i = 0; i < n; ++i) {
                int b = (cur[i] >> bit) & 1;
                bits[i] = b;
                if (b == 0) {
                    next[left++] = cur[i];
                } else {
                    next[right++] = cur[i];
                }
            }

            bitvectors[depth].build(bits);
            cur.swap(next);
        }
    }

    int kth(int l, int r, int k) const {
        int result = 0;
        for (int depth = 0; depth < LOG; ++depth) {
            int bit = LOG - 1 - depth;
            int leftCount = bitvectors[depth].rankZero(r) - bitvectors[depth].rankZero(l);

            if (k < leftCount) {
                l = bitvectors[depth].rankZero(l);
                r = bitvectors[depth].rankZero(r);
            } else {
                result |= (1 << bit);
                k -= leftCount;
                l = zeroCount[depth] + bitvectors[depth].rankOne(l);
                r = zeroCount[depth] + bitvectors[depth].rankOne(r);
            }
        }
        return result;
    }

    int countLess(int l, int r, int x) const {
        int result = 0;
        for (int depth = 0; depth < LOG; ++depth) {
            int bit = LOG - 1 - depth;
            int leftL = bitvectors[depth].rankZero(l);
            int leftR = bitvectors[depth].rankZero(r);
            int oneL = zeroCount[depth] + bitvectors[depth].rankOne(l);
            int oneR = zeroCount[depth] + bitvectors[depth].rankOne(r);

            if ((x >> bit) & 1) {
                result += leftR - leftL;
                l = oneL;
                r = oneR;
            } else {
                l = leftL;
                r = leftR;
            }
        }
        return result;
    }

    int rangeFreq(int l, int r, int low, int high) const {
        return countLess(l, r, high) - countLess(l, r, low);
    }
};
```

`kth(l, r, k)`의 `k`는 0-indexed입니다. 구간 길이보다 크거나 같은 `k`는 호출 전에 막아야 합니다.

## 5. 구간 이동 공식

각 level에서 bit가 0인 원소는 앞쪽, bit가 1인 원소는 `zeroCount[level]` 뒤쪽으로 이동합니다.

| 다음 영역 | 변환 |
| --- | --- |
| 0-bit 영역 | `l = rankZero(l)`, `r = rankZero(r)` |
| 1-bit 영역 | `l = zeroCount + rankOne(l)`, `r = zeroCount + rankOne(r)` |

이 공식 하나로 kth, countLess, frequency가 모두 나옵니다.

## 6. 좌표 압축을 쓸 때

값이 음수거나 매우 큰 64-bit 정수이면 좌표 압축을 적용합니다.

1. 원본 값을 정렬해 `coords`를 만든다.
2. 각 값을 `lower_bound(coords, value)` index로 바꾼다.
3. Wavelet Matrix는 compressed value로 만든다.
4. kth 결과 index를 다시 `coords[index]`로 복원한다.

빈도 질의처럼 값 범위가 필요하면 `[low, high)`도 좌표 index 범위로 바꿉니다.

## 7. 시간 복잡도

| 연산 | 시간 | 메모리 |
| --- | ---: | ---: |
| build | `O(N log V)` | `O(N log V)` bit 또는 prefix |
| kth | `O(log V)` | - |
| countLess | `O(log V)` | - |
| rangeFreq | `O(log V)` | - |

실제 succinct bitvector를 쓰면 메모리는 더 줄일 수 있습니다. 위 구현은 이해를 위해 prefix int 배열을 사용합니다.

## 8. 자주 하는 실수

1. `[l, r]`과 `[l, r)` 구간 convention을 섞는다.
2. `k`를 1-indexed로 넣고 kth 결과가 한 칸 밀린다.
3. 1-bit 영역으로 이동할 때 `zeroCount` offset을 빼먹는다.
4. 음수 값을 그대로 bit shift해 정렬 순서가 깨진다.
5. 좌표 압축 후 kth 결과를 원래 값으로 복원하지 않는다.

## 9. 문제를 볼 때 체크할 조건

- 배열이 정적인가?
- 질의가 range kth, rank, frequency, quantile 계열인가?
- 값 범위가 non-negative int로 충분한가, 좌표 압축이 필요한가?
- `k`의 index convention이 무엇인가?
- 메모리 제한에서 prefix int 배열 방식이 가능한가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: range kth query `/practice/...` 문제 필요 | kth 이동 공식 구현 | wavelet matrix kth |
| 표준 | TODO: 구간 값 빈도 `/practice/...` 문제 필요 | `countLess(high) - countLess(low)` 사용 | range frequency |
| 응용 | TODO: 구간 median `/practice/...` 문제 필요 | median을 kth로 변환 | range quantile |
| 함정 | TODO: 음수 좌표 wavelet matrix `/practice/...` 문제 필요 | 좌표 압축과 값 복원 | coordinate compression |
