# XOR Linear Basis

XOR Linear Basis는 여러 수의 xor 조합으로 만들 수 있는 값의 공간을 선형대수처럼 다루는 기법입니다. GF(2) 위의 벡터 기저로 생각하면 maximum xor, representability, rank, 부분집합 xor 개수 문제를 일관되게 처리할 수 있습니다.


모든 64비트를 사용합니다. rank=64이면 2^rank는 unsigned long long 한 칸에 표현되지 않습니다. 그래프 cycle XOR 응용은 같은 연결 성분의 walk에 적용하며 단순 경로만 허용하면 별도 문제입니다.

## 문제 신호

| 문제 표현 | Linear Basis 관점 |
| --- | --- |
| 부분집합 xor 최댓값 | basis로 greedy maximize |
| 어떤 xor 값을 만들 수 있는가 | basis reduction |
| 서로 독립인 xor 값 개수 | rank |
| 모든 부분집합 xor의 개수 | `2^rank` |
| 경로 xor와 query가 섞인다 | prefix xor + basis |

XOR는 carry가 없기 때문에 각 bit가 GF(2) 선형 공간의 좌표처럼 동작합니다. 덧셈/최댓값 문제와 섞이면 이 성질이 깨질 수 있으므로 xor 조합인지 먼저 확인합니다.

## Basis 불변식

`basis[b]`는 최고 set bit가 `b`인 대표 vector입니다.

```text
basis[b] has bit b = 1
for any inserted x, x can be reduced by existing basis
if x becomes 0, it was dependent
if x remains nonzero, it becomes a new basis vector
```

이 불변식만 지키면 삽입 순서와 관계없이 같은 rank를 얻습니다.

## 구현

아래 구현은 unsigned 64-bit 값을 기준으로 합니다. signed integer를 그대로 shift하면 헷갈리므로 bit 문제에서는 unsigned 타입이 안전합니다.

```cpp compile-check
#include <array>
#include <vector>
using namespace std;

struct XorLinearBasis {
    static const int LOG = 63;
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

    unsigned long long maximize(unsigned long long seed = 0) const {
        unsigned long long result = seed;
        for (int bit = LOG; bit >= 0; --bit) {
            if ((result ^ basis[bit]) > result) {
                result ^= basis[bit];
            }
        }
        return result;
    }

    vector<unsigned long long> vectors() const {
        vector<unsigned long long> result;
        for (int bit = 0; bit <= LOG; ++bit) {
            if (basis[bit] != 0) {
                result.push_back(basis[bit]);
            }
        }
        return result;
    }
};
```

`maximize(seed)`는 이미 가진 xor 값에 basis vector를 추가로 xor해서 만들 수 있는 최댓값을 구합니다. 부분집합 xor 최댓값은 `seed = 0`입니다.

## Rank와 표현 개수

원소가 `n`개이고 basis rank가 `r`이면 서로 다른 subset xor 값은 `2^r`개입니다. 어떤 값 `x`를 표현할 수 있다면, 그 값을 만드는 subset 수는 `2^(n-r)`개입니다.

```text
kernel dimension = n - rank
각 표현 가능한 xor 값마다 같은 수의 preimage가 있음
```

단, 빈 부분집합을 제외하거나 non-empty 조건이 있으면 `x = 0`에서 보정이 필요합니다.

## 정규화된 Basis와 k번째 xor

위 `XorLinearBasis`의 high-bit basis는 maximum query에는 충분하지만, k번째 작은 xor 값을 만들려면 lower bit가 서로 정리된 형태가 필요합니다. 아래 확장은 같은 문서의 `XorLinearBasis` 뒤에 붙입니다. rank가 64이면 모든 unsigned long long k가 유효하며 `1ULL << 64`는 계산하지 않습니다.

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
