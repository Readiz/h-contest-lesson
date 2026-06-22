# Succinct Bitvector

Succinct Bitvector는 bit열 위에서 `rank`와 `select`를 빠르게 처리하는 기본 자료구조입니다. Wavelet Matrix, compressed index, 문자열 index에서 거의 항상 바닥에 깔리는 구성 요소입니다.

이 레슨은 Wavelet Matrix 이후에 보는 rank/select 기반 구조를 정리합니다.

1. bit를 64-bit word로 압축해 저장한다.
2. superblock과 block prefix로 rank를 빠르게 계산한다.
3. select는 binary search 또는 block index로 구현한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: bit operation, prefix sum, Wavelet Matrix
- 함께 보면 좋은 레슨: Wavelet Matrix, Sparse Table과 RMQ, 좌표 압축
- 다음에 볼 레슨: compressed wavelet tree, FM-index, succinct tree

## 1. 문제 신호

| 질의 | 의미 |
| --- | --- |
| `rank1(pos)` | `[0, pos)` 안의 1 개수 |
| `rank0(pos)` | `[0, pos)` 안의 0 개수 |
| `select1(k)` | k번째 1의 위치 |
| `select0(k)` | k번째 0의 위치 |
| bit열 기반 index | succinct bitvector 후보 |

Wavelet Matrix의 각 level bitvector도 결국 rank 질의를 빠르게 하기 위해 이런 구조를 사용합니다.

## 2. Rank 구조

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

## 3. Rank 구현

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
    vector<int> superRank;
    vector<unsigned short> blockRank;

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
        for (int w = 0; w < wordCount; ++w) {
            if (w % SUPER_WORDS == 0) {
                superRank[w / SUPER_WORDS] = total;
            }
            int superStart = (w / SUPER_WORDS) * SUPER_WORDS;
            int inside = 0;
            for (int x = superStart; x < w; ++x) {
                inside += __builtin_popcountll(words[x]);
            }
            blockRank[w] = (unsigned short)inside;
            total += __builtin_popcountll(words[w]);
        }
        superRank[(wordCount + SUPER_WORDS - 1) / SUPER_WORDS] = total;
    }

    int rankOne(int pos) const {
        pos = max(0, min(pos, n));
        int wordIndex = pos / WORD_BITS;
        int offset = pos % WORD_BITS;

        int result = superRank[wordIndex / SUPER_WORDS] + blockRank[wordIndex];
        if (wordIndex < (int)words.size() && offset > 0) {
            unsigned long long mask = (offset == 64 ? ~0ULL : ((1ULL << offset) - 1));
            result += __builtin_popcountll(words[wordIndex] & mask);
        }
        return result;
    }

    int rankZero(int pos) const {
        return pos - rankOne(pos);
    }

    bool access(int pos) const {
        return (words[pos / WORD_BITS] >> (pos % WORD_BITS)) & 1ULL;
    }
};
```

`rankOne(pos)`은 `[0, pos)` 구간을 뜻합니다. `pos` 자체의 bit는 포함하지 않습니다.

## 4. Select 구현

가장 단순한 select는 rank를 이용한 binary search입니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct SimpleRankForSelect {
    vector<int> prefix;

    explicit SimpleRankForSelect(const vector<int>& bits) {
        prefix.assign(bits.size() + 1, 0);
        for (int i = 0; i < (int)bits.size(); ++i) {
            prefix[i + 1] = prefix[i] + bits[i];
        }
    }

    int rankOne(int pos) const {
        return prefix[pos];
    }

    int selectOne(int kth) const {
        int total = prefix.back();
        if (kth < 0 || kth >= total) {
            return -1;
        }
        int low = 0;
        int high = (int)prefix.size() - 1;
        while (low < high) {
            int mid = (low + high) / 2;
            if (rankOne(mid + 1) >= kth + 1) {
                high = mid;
            } else {
                low = mid + 1;
            }
        }
        return low;
    }
};
```

실전 succinct 구현에서는 select도 block index를 따로 두어 더 빠르게 만들 수 있습니다. 하지만 많은 대회 문제에서는 rank가 핵심이고 select는 binary search로 충분한 경우가 많습니다.

## 5. Wavelet Matrix와 연결

Wavelet Matrix의 level bitvector에서 필요한 연산은 대부분 rank입니다.

| 이동 | 필요한 rank |
| --- | --- |
| 0-bit 영역 이동 | `rank0(l)`, `rank0(r)` |
| 1-bit 영역 이동 | `zeroCount + rank1(l)`, `zeroCount + rank1(r)` |
| countLess | 각 level rank0/rank1 |
| kth | 왼쪽 0-bit 개수 |

따라서 Wavelet Matrix 구현을 메모리 효율적으로 만들려면 bitvector를 먼저 탄탄하게 만드는 편이 좋습니다.

## 6. 메모리 계산

길이 `N` bitvector가 있다고 합시다.

| 구성 | 대략 메모리 |
| --- | ---: |
| raw bit words | `N` bits |
| prefix int per position | `32N` bits |
| 512-bit superblock + 64-bit block | `N + O(N/64 log N)` bits |

대회 구현에서는 완전한 이론적 succinct보다 "raw bit + rank table"의 균형점이 더 실용적입니다.

## 7. Index Convention

rank/select는 index convention이 중요합니다.

| 함수 | 이 레슨의 의미 |
| --- | --- |
| `rank1(pos)` | `[0, pos)`의 1 개수 |
| `rank1(0)` | 0 |
| `rank1(n)` | 전체 1 개수 |
| `select1(0)` | 첫 번째 1의 위치 |
| `select1(k)` | 0-indexed k번째 1 |

문제나 라이브러리마다 select를 1-indexed로 정의할 수 있으니 wrapper를 분리합니다.

## 8. 시간 복잡도

| 연산 | 단순 prefix | succinct rank |
| --- | ---: | ---: |
| access | `O(1)` | `O(1)` |
| rank | `O(1)` | `O(1)` |
| select binary search | `O(log N)` | `O(log N)` |
| build | `O(N)` | `O(N)` |

select까지 `O(1)` 또는 `O(log word)`로 만들려면 추가 index가 필요합니다.

## 9. 자주 하는 실수

1. `rank(pos)`에 pos 위치 bit를 포함할지 헷갈린다.
2. `1ULL << 64` 같은 undefined shift를 만든다.
3. 마지막 word의 padding bit를 실제 bit로 센다.
4. select의 k를 0-indexed/1-indexed로 섞는다.
5. `unsigned short` block count가 superblock 크기보다 작다는 전제를 깨뜨린다.

## 10. 문제를 볼 때 체크할 조건

- 필요한 연산이 rank만인지, select도 필요한지?
- bitvector가 static인가?
- 메모리 제한이 prefix int 배열을 허용하는가?
- index convention이 `[0, pos)`인가 `[0, pos]`인가?
- Wavelet Matrix나 compressed index의 내부 부품으로 쓰는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: bitvector rank `/practice/...` 문제 필요 | raw bit와 prefix rank 구현 | rank |
| 표준 | TODO: select query `/practice/...` 문제 필요 | binary search select | select |
| 응용 | TODO: wavelet matrix memory 개선 `/practice/...` 문제 필요 | level bitvector 압축 | succinct |
| 함정 | TODO: padding bit 처리 `/practice/...` 문제 필요 | 마지막 word mask | bit operation |
