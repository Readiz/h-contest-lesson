# XOR Linear Basis

XOR Linear Basis는 여러 수의 xor 조합으로 만들 수 있는 값의 공간을 선형대수처럼 다루는 기법입니다. GF(2) 위의 벡터 기저로 생각하면 maximum xor, representability, rank, 부분집합 xor 개수 문제를 일관되게 처리할 수 있습니다.

이 레슨은 Polynomial Interpolation과 수학 심화 이후에 보는 bitwise algebra 주제입니다.

1. 각 정수를 bit vector로 본다.
2. 가장 높은 bit가 같은 vector끼리 Gaussian elimination처럼 정리한다.
3. basis의 rank가 만들 수 있는 xor 공간의 차원을 결정한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: bit operation, Gaussian elimination, xor 성질
- 함께 보면 좋은 레슨: 모듈러 연산, 조합론, Proof와 Invariants
- 다음에 볼 레슨: matroid 관점, xor convolution, linear basis on tree

## 1. 문제 신호

| 문제 표현 | Linear Basis 관점 |
| --- | --- |
| 부분집합 xor 최댓값 | basis로 greedy maximize |
| 어떤 xor 값을 만들 수 있는가 | basis reduction |
| 서로 독립인 xor 값 개수 | rank |
| 모든 부분집합 xor의 개수 | `2^rank` |
| 경로 xor와 query가 섞인다 | prefix xor + basis |

XOR는 carry가 없기 때문에 각 bit가 GF(2) 선형 공간의 좌표처럼 동작합니다. 덧셈/최댓값 문제와 섞이면 이 성질이 깨질 수 있으므로 xor 조합인지 먼저 확인합니다.

## 2. Basis 불변식

`basis[b]`는 최고 set bit가 `b`인 대표 vector입니다.

```text
basis[b] has bit b = 1
for any inserted x, x can be reduced by existing basis
if x becomes 0, it was dependent
if x remains nonzero, it becomes a new basis vector
```

이 불변식만 지키면 삽입 순서와 관계없이 같은 rank를 얻습니다.

## 3. 구현

아래 구현은 unsigned 64-bit 값을 기준으로 합니다. signed integer를 그대로 shift하면 헷갈리므로 bit 문제에서는 unsigned 타입이 안전합니다.

```cpp compile-check
#include <array>
#include <vector>
using namespace std;

struct XorLinearBasis {
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

## 4. Rank와 경우의 수

서로 독립인 basis vector가 `r`개면 만들 수 있는 xor 값은 `2^r`개입니다.

```text
독립 vector마다 선택/미선택 2가지
=> 2^rank distinct xor values
```

원소 수가 `n`이고 rank가 `r`이면 같은 xor 값을 만드는 부분집합 수는 보통 `2^(n-r)`배로 묶입니다. 단, 빈 부분집합 포함 여부와 modulo 조건을 문제마다 확인해야 합니다.

## 5. K번째 Xor 값

K번째 작은 xor 값을 구하려면 basis를 reduced row echelon form처럼 정규화해야 합니다. 단순 `basis[bit]` 배열은 maximize에는 충분하지만 정렬된 순서 enumeration에는 부족합니다.

정규화 방향은 아래와 같습니다.

```text
for high bit i:
  for lower bit j:
    if basis[i] has bit j:
      basis[i] ^= basis[j]
```

그 뒤 낮은 bit basis부터 K의 bit에 맞춰 xor하면 순서 있는 생성이 가능합니다.

## 6. 그래프와 Tree 응용

무방향 그래프에서 DFS tree를 잡고 back edge가 만드는 cycle xor를 basis에 넣으면, 두 정점 사이 path xor를 basis로 최적화할 수 있습니다.

```text
pathXor(u, v) = prefixXor[u] ^ prefixXor[v]
cycle basis를 더해 가능한 경로 xor 최댓값 계산
```

Tree path query에서는 Heavy-Light나 DSU on tree와 basis merge가 함께 나오기도 합니다.

## 7. 시간 복잡도

| 작업 | 복잡도 |
| --- | --- |
| 값 하나 insert | `O(LOG)` |
| representability query | `O(LOG)` |
| maximum xor query | `O(LOG)` |
| basis merge | `O(LOG^2)` 또는 vector 개수만큼 insert |

`LOG`는 보통 60 정도라 상수에 가깝습니다.

## 8. 자주 하는 실수

1. signed `long long`의 최상위 bit를 다루다 비교가 꼬인다.
2. dependent vector를 rank에 포함한다.
3. maximum xor와 minimum xor의 greedy 방향을 섞는다.
4. distinct xor 개수 `2^rank`와 부분집합 개수 `2^n`을 혼동한다.
5. K번째 xor를 구하면서 basis를 정규화하지 않는다.

## 9. 문제를 볼 때 체크할 조건

- 연산이 xor 조합으로 닫혀 있는가?
- 최대값이 필요한가, 표현 가능 여부가 필요한가?
- 중복 원소와 빈 부분집합을 어떻게 처리하는가?
- bit 범위가 30인지 60인지 확인했는가?
- 경로/구간 query라면 basis merge 순서가 시간 안에 들어오는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 부분집합 maximum xor `/practice/...` 문제 필요 | basis insert와 greedy maximize | xor basis |
| 표준 | TODO: xor 값 표현 가능성 `/practice/...` 문제 필요 | value reduction과 rank | linear independence |
| 응용 | TODO: 그래프 경로 xor 최댓값 `/practice/...` 문제 필요 | cycle basis와 prefix xor | graph xor |
| 함정 | TODO: K번째 xor 값 `/practice/...` 문제 필요 | basis 정규화와 순서 생성 | reduced basis |
