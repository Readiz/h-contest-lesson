# Linear Basis Applications

Linear Basis Applications는 maximum xor를 넘어서 표현 가능성, k번째 xor, graph cycle xor, range query처럼 XOR Linear Basis를 여러 문제 형태에 적용하는 레슨입니다. 핵심은 "xor 조합으로 만들 수 있는 값의 공간"과 "basis를 어떤 형태로 정규화해야 하는가"를 분리해서 보는 것입니다.

이 레슨은 XOR Linear Basis, Mobius Inversion, Proof와 Invariant 이후에 보는 수학 심화입니다.

1. basis rank로 만들 수 있는 xor 값의 개수와 표현 가능 여부를 판정한다.
2. normalized basis로 k번째 xor 값을 만든다.
3. graph cycle, range query, matroid 관점으로 응용 범위를 넓힌다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: XOR Linear Basis, Gaussian elimination over GF(2), graph path xor
- 함께 보면 좋은 레슨: XOR Linear Basis, Proof와 Invariants, Combinatorics
- 다음에 볼 레슨: xor convolution, matroid basis, linear algebra over finite fields

## 1. 문제 신호

| 문제 표현 | Linear Basis 응용 관점 |
| --- | --- |
| k번째로 작은 subset xor | normalized basis |
| 어떤 xor 값이 몇 개의 부분집합으로 만들어지는가 | rank와 nullity |
| 그래프 경로 xor를 최대화 | cycle basis |
| 구간마다 maximum xor query | mergeable basis |
| 독립인 값 최대 개수 선택 | GF(2) matroid |

Maximum xor는 가장 대표적인 입문 문제일 뿐입니다. basis가 표현하는 선형 공간 자체를 쓰면 counting, ordering, graph path optimization으로 이어집니다.

## 2. Rank와 표현 개수

원소가 `n`개이고 basis rank가 `r`이면 서로 다른 subset xor 값은 `2^r`개입니다. 어떤 값 `x`를 표현할 수 있다면, 그 값을 만드는 subset 수는 `2^(n-r)`개입니다.

```text
kernel dimension = n - rank
각 표현 가능한 xor 값마다 같은 수의 preimage가 있음
```

단, 빈 부분집합을 제외하거나 non-empty 조건이 있으면 `x = 0`에서 보정이 필요합니다.

## 3. 정규화된 Basis와 k번째 xor

일반적인 high-bit basis는 maximum query에는 충분하지만, k번째 작은 xor 값을 만들려면 lower bit가 서로 정리된 형태가 필요합니다.

```cpp compile-check
#include <array>
#include <vector>
using namespace std;

struct NormalizedXorBasis {
    static const int LOG = 62;
    array<unsigned long long, LOG + 1> basis{};
    int rank = 0;

    bool insert(unsigned long long value) {
        for (int bit = LOG; bit >= 0; --bit) {
            if (((value >> bit) & 1ULL) == 0) {
                continue;
            }
            if (basis[bit] == 0) {
                basis[bit] = value;
                ++rank;
                return true;
            }
            value ^= basis[bit];
        }
        return false;
    }

    bool canRepresent(unsigned long long value) const {
        for (int bit = LOG; bit >= 0; --bit) {
            if (((value >> bit) & 1ULL) == 0) {
                continue;
            }
            if (basis[bit] == 0) {
                return false;
            }
            value ^= basis[bit];
        }
        return true;
    }

    vector<unsigned long long> normalizedVectors() const {
        array<unsigned long long, LOG + 1> reduced = basis;
        for (int bit = 0; bit <= LOG; ++bit) {
            if (reduced[bit] == 0) {
                continue;
            }
            for (int high = bit + 1; high <= LOG; ++high) {
                if ((reduced[high] >> bit) & 1ULL) {
                    reduced[high] ^= reduced[bit];
                }
            }
        }

        vector<unsigned long long> vectors;
        for (int bit = 0; bit <= LOG; ++bit) {
            if (reduced[bit] != 0) {
                vectors.push_back(reduced[bit]);
            }
        }
        return vectors;
    }

    unsigned long long kthSmallest(unsigned long long k) const {
        vector<unsigned long long> vectors = normalizedVectors();
        unsigned long long result = 0;
        for (int i = 0; i < (int)vectors.size(); ++i) {
            if ((k >> i) & 1ULL) {
                result ^= vectors[i];
            }
        }
        return result;
    }
};
```

위 `k`는 0-indexed입니다. 표현 가능한 값이 `2^rank`개이므로 `k < 2^rank` 조건을 호출자가 확인해야 합니다.

## 4. Graph Cycle Basis

무방향 weighted graph에서 각 edge의 weight를 xor로 보고 DFS tree를 잡으면, non-tree edge는 cycle xor를 만듭니다.

```text
cycleXor = distXor[u] ^ distXor[v] ^ edgeWeight
basis.insert(cycleXor)
pathXor(u, v) = distXor[u] ^ distXor[v]
answer = maximize(pathXor(u, v))
```

이 방식은 두 정점 사이의 walk에서 cycle을 추가로 돌아 xor 값을 바꿀 수 있을 때 사용합니다. simple path만 허용되는 문제라면 이 모델이 맞지 않을 수 있습니다.

## 5. Range Query Basis

구간 `l..r`의 maximum subset xor를 묻는 문제는 basis merge가 필요합니다.

| 제약 | 후보 구조 |
| --- | --- |
| static array, offline query | divide and conquer offline |
| point update 없음 | segment tree of basis |
| prefix append만 있음 | prefix basis with timestamp |
| tree path query | HLD + segment tree basis |

Basis merge는 작은 basis의 vector들을 큰 basis에 insert하면 됩니다. bit 수가 60 정도라 `O(LOG^2)`가 대개 충분합니다.

## 6. Matroid 관점

XOR vector의 독립성은 linear matroid입니다. "가중치가 있는 값들 중 독립인 subset의 최대 weight"는 가중치 내림차순으로 보며 독립이면 선택하는 greedy가 맞습니다.

```text
sort by weight descending
if insert(vector) succeeds:
    choose it
```

이때 maximize xor greedy와 목적식이 다릅니다. 하나는 만들어지는 xor 값을 키우는 것이고, 다른 하나는 독립인 원소의 가중치 합을 키우는 것입니다.

## 7. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| basis insert | `O(LOG)` |
| can represent | `O(LOG)` |
| normalize | `O(LOG^2)` |
| kth xor after normalize | `O(LOG)` |
| basis merge | `O(LOG^2)` |

정규화는 매 query마다 하면 비쌀 수 있습니다. 구조가 static이면 node마다 정규화된 basis를 캐시할지 검토합니다.

## 8. 자주 하는 실수

1. `k`를 1-indexed로 받았는데 0-indexed kth 함수에 그대로 넣는다.
2. `rank`와 원소 수를 혼동해 표현 개수를 잘못 계산한다.
3. graph cycle basis를 simple path 문제에 적용한다.
4. signed integer 비교로 maximum xor가 깨진다.
5. range basis를 merge할 때 dependent vector 개수를 counting에 반영하지 않는다.

## 9. 문제를 볼 때 체크할 조건

- 목표가 maximum xor인가, 표현 가능성인가, ordering인가?
- 중복 원소와 빈 부분집합을 어떻게 처리하는가?
- graph에서는 walk와 simple path 중 무엇이 허용되는가?
- query 구조가 static인지 update가 있는지 확인했는가?
- `LOG` 범위가 입력 값의 bit 수를 덮는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: linear basis applications `/practice/...` 문제 필요 | 표현 가능성과 rank | representability |
| 표준 | TODO: kth subset xor `/practice/...` 문제 필요 | normalized basis | kth xor |
| 응용 | TODO: graph cycle xor `/practice/...` 문제 필요 | path xor와 cycle basis | graph xor |
| 함정 | TODO: weighted independent xor set `/practice/...` 문제 필요 | matroid greedy 구분 | independence |
