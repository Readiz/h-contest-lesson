# Linear Basis Applications

Linear Basis Applications는 maximum xor를 넘어서 표현 가능성, k번째 xor, graph cycle xor, range query처럼 XOR Linear Basis를 여러 문제 형태에 적용하는 레슨입니다. 핵심은 "xor 조합으로 만들 수 있는 값의 공간"과 "basis를 어떤 형태로 정규화해야 하는가"를 분리해서 보는 것입니다.


아래 확장은 [XOR Linear Basis](https://h.readiz.com/learn/linear-basis-xor)의 XorLinearBasis(LOG=63) 뒤에 붙입니다. rank=64이면 모든 unsigned long long k가 유효하며 1ULL<<64는 계산하지 않습니다.

## 문제 신호

| 문제 표현 | Linear Basis 응용 관점 |
| --- | --- |
| k번째로 작은 subset xor | normalized basis |
| 어떤 xor 값이 몇 개의 부분집합으로 만들어지는가 | rank와 nullity |
| 그래프 경로 xor를 최대화 | cycle basis |
| 구간마다 maximum xor query | mergeable basis |
| 독립인 값 최대 개수 선택 | GF(2) matroid |

Maximum xor는 가장 대표적인 입문 문제일 뿐입니다. basis가 표현하는 선형 공간 자체를 쓰면 counting, ordering, graph path optimization으로 이어집니다.

## Rank와 표현 개수

원소가 `n`개이고 basis rank가 `r`이면 서로 다른 subset xor 값은 `2^r`개입니다. 어떤 값 `x`를 표현할 수 있다면, 그 값을 만드는 subset 수는 `2^(n-r)`개입니다.

```text
kernel dimension = n - rank
각 표현 가능한 xor 값마다 같은 수의 preimage가 있음
```

단, 빈 부분집합을 제외하거나 non-empty 조건이 있으면 `x = 0`에서 보정이 필요합니다.

## 정규화된 Basis와 k번째 xor

일반적인 high-bit basis는 maximum query에는 충분하지만, k번째 작은 xor 값을 만들려면 lower bit가 서로 정리된 형태가 필요합니다.

```cpp
#include <stdexcept>

struct NormalizedXorBasis : XorLinearBasis {
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
        if (rank < 64 && k >= (1ULL << rank)) throw out_of_range("k");
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

## Graph Cycle Basis

무방향 weighted graph에서 각 edge의 weight를 xor로 보고 DFS tree를 잡으면, non-tree edge는 cycle xor를 만듭니다.

```text
cycleXor = distXor[u] ^ distXor[v] ^ edgeWeight
basis.insert(cycleXor)
pathXor(u, v) = distXor[u] ^ distXor[v]
answer = maximize(pathXor(u, v))
```

이 방식은 두 정점 사이의 walk에서 cycle을 추가로 돌아 xor 값을 바꿀 수 있을 때 사용합니다. simple path만 허용되는 문제라면 이 모델이 맞지 않을 수 있습니다.

## Range Query Basis

구간 `l..r`의 maximum subset xor를 묻는 문제는 basis merge가 필요합니다.

| 제약 | 후보 구조 |
| --- | --- |
| static array, offline query | divide and conquer offline |
| point update 없음 | segment tree of basis |
| prefix append만 있음 | prefix basis with timestamp |
| tree path query | HLD + segment tree basis |

Basis merge는 작은 basis의 vector들을 큰 basis에 insert하면 됩니다. bit 수가 60 정도라 `O(LOG^2)`가 대개 충분합니다.

## Matroid 관점

XOR vector의 독립성은 linear matroid입니다. "가중치가 있는 값들 중 독립인 subset의 최대 weight"는 가중치 내림차순으로 보며 독립이면 선택하는 greedy가 맞습니다.

```text
sort by weight descending
if weight >= 0 and insert(vector) succeeds:
    choose it
```

이때 maximize xor greedy와 목적식이 다릅니다. 하나는 만들어지는 xor 값을 키우는 것이고, 다른 하나는 독립인 원소의 가중치 합을 키우는 것입니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| basis insert | `O(LOG)` |
| can represent | `O(LOG)` |
| normalize | `O(LOG^2)` |
| 현재 kthSmallest 호출(정규화 포함) | `O(LOG^2)` |
| 정규화 벡터를 캐시한 뒤 kth xor | `O(LOG)` |
| basis merge | `O(LOG^2)` |

정규화는 매 query마다 하면 비쌀 수 있습니다. 구조가 static이면 node마다 정규화된 basis를 캐시할지 검토합니다.
