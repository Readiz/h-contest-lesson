# Succinct Bitvector

Succinct Bitvector는 bit열 위에서 `rank`와 `select`를 빠르게 처리하는 기본 자료구조입니다. Wavelet Matrix, compressed index, 문자열 index에서 거의 항상 바닥에 깔리는 구성 요소입니다.

## 문제 신호

| 질의 | 의미 |
| --- | --- |
| `rank1(pos)` | `[0, pos)` 안의 1 개수 |
| `rank0(pos)` | `[0, pos)` 안의 0 개수 |
| `select1(k)` | k번째 1의 위치 |
| `select0(k)` | k번째 0의 위치 |
| bit열 기반 index | succinct bitvector 후보 |

Wavelet Matrix의 각 level bitvector도 결국 rank 질의를 빠르게 하기 위해 이런 구조를 사용합니다.

## Rank 구조

단순 prefix array를 `int`로 저장하면 rank는 쉽지만 메모리가 큽니다. Succinct 관점에서는 bit 자체는 word에 넣고, 일정 간격마다 prefix count를 둡니다.

```text
words:      raw bits packed in uint64_t
superRank: 512 bits마다 누적 1 개수
blockRank: 64 bits마다 superblock 내부 1 개수
```

rank는 아래 세 값을 더합니다.

1. superblock 이전의 1 개수
2. 현재 superblock 안에서 현재 word 이전의 1 개수
3. 현재 word의 남은 prefix popcount

## Rank 구현

아래 구현은 이해를 위해 64-bit word 단위 block과 512-bit superblock을 사용합니다.

```cpp compile-check
#include <algorithm>
#include <cstdint>
#include <vector>
using namespace std;

struct SuccinctBitvector {
    static const int WORD_BITS = 64;
    static const int SUPER_WORDS = 8;

    int n = 0;
    vector<unsigned long long> words;
    vector<int> superRank{0};
    vector<unsigned short> blockRank{0};

    SuccinctBitvector() = default;

    explicit SuccinctBitvector(const vector<int>& bits) {
        build(bits);
    }

    void build(const vector<int>& bits) {
        n = (int)bits.size();
        int wordCount = (n + WORD_BITS - 1) / WORD_BITS;
        words.assign(wordCount, 0);

        for (int i = 0; i < n; ++i) {
            if (bits[i]) {
                words[i / WORD_BITS] |= 1ULL << (i % WORD_BITS);
            }
        }

        superRank.assign((wordCount + SUPER_WORDS - 1) / SUPER_WORDS + 1, 0);
        blockRank.assign(wordCount + 1, 0);

        int total = 0;
        for (int w = 0; w <= wordCount; ++w) {
            if (w % SUPER_WORDS == 0) {
                superRank[w / SUPER_WORDS] = total;
            }
            int superStart = (w / SUPER_WORDS) * SUPER_WORDS;
            int inside = 0;
            for (int x = superStart; x < w; ++x) {
                inside += __builtin_popcountll(words[x]);
            }
            blockRank[w] = (unsigned short)inside;
            if (w < wordCount) total += __builtin_popcountll(words[w]);
        }
    }

    int rankOne(int pos) const {
        pos = max(0, min(pos, n));
        int wordIndex = pos / WORD_BITS;
        int offset = pos % WORD_BITS;

        int result = superRank[wordIndex / SUPER_WORDS] + blockRank[wordIndex];
        if (wordIndex < (int)words.size() && offset > 0) {
            unsigned long long mask = (1ULL << offset) - 1;
            result += __builtin_popcountll(words[wordIndex] & mask);
        }
        return result;
    }

    int rankZero(int pos) const {
        pos = max(0, min(pos, n));
        return pos - rankOne(pos);
    }

    bool access(int pos) const {
        return (words[pos / WORD_BITS] >> (pos % WORD_BITS)) & 1ULL;
    }

    int selectOne(int kth) const {
        if (kth < 0 || kth >= rankOne(n)) return -1;
        int low = 0, high = n - 1;
        while (low < high) {
            int mid = low + (high - low) / 2;
            if (rankOne(mid + 1) > kth) high = mid;
            else low = mid + 1;
        }
        return low;
    }
};
```

`rankOne(pos)`은 `[0, pos)` 구간을 뜻합니다. `pos` 자체의 bit는 포함하지 않습니다.

## Select 구현

selectOne은 위 구조에 포함되어 있으며 0번째부터 셉니다. 없는 순번은 -1을 반환합니다.

별도 prefix 배열을 다시 만들지 않고 같은 rank 구조를 사용합니다.

## Wavelet Matrix와 연결

Wavelet Matrix의 level bitvector에서 필요한 연산은 대부분 rank입니다.

| 이동 | 필요한 rank |
| --- | --- |
| 0-bit 영역 이동 | `rank0(l)`, `rank0(r)` |
| 1-bit 영역 이동 | `zeroCount + rank1(l)`, `zeroCount + rank1(r)` |
| countLess | 각 level rank0/rank1 |
| kth | 왼쪽 0-bit 개수 |

따라서 Wavelet Matrix 구현을 메모리 효율적으로 만들려면 bitvector를 먼저 탄탄하게 만드는 편이 좋습니다.

## 메모리 계산

길이 `N` bitvector가 있다고 합시다.

| 구성 | 대략 메모리 |
| --- | ---: |
| raw bit words | `N` bits |
| prefix int per position | `32N` bits |
| 512-bit superblock + 64-bit block | 약 `1.3125N` bits (32비트 int·16비트 short 기준, 끝 칸 제외) |

위 고정 블록 구현은 엄밀한 `N + o(N)` 공간 보장은 아닙니다. 대회 구현에서는 완전한 이론적 succinct보다 "raw bit + rank table"의 균형점이 더 실용적입니다.

## Index Convention

rank/select는 index convention이 중요합니다.

| 함수 | 이 레슨의 의미 |
| --- | --- |
| `rank1(pos)` | `[0, pos)`의 1 개수 |
| `rank1(0)` | 0 |
| `rank1(n)` | 전체 1 개수 |
| `select1(0)` | 첫 번째 1의 위치 |
| `select1(k)` | 0-indexed k번째 1 |

문제나 라이브러리마다 select를 1-indexed로 정의할 수 있으니 wrapper를 분리합니다.

## 시간 복잡도

| 연산 | 단순 prefix | succinct rank |
| --- | ---: | ---: |
| access | `O(1)` | `O(1)` |
| rank | `O(1)` | `O(1)` |
| select binary search | `O(log N)` | `O(log N)` |
| build | `O(N)` | `O(N)` |

select까지 `O(1)` 또는 `O(log word)`로 만들려면 추가 index가 필요합니다.
