# Sparse Table과 RMQ

Sparse Table은 배열이 바뀌지 않을 때 구간 최솟값, 최댓값, gcd 같은 질의를 매우 빠르게 처리하는 자료구조입니다. 전처리에 `O(N log N)`을 쓰고, 질의는 `O(1)` 또는 `O(log N)`에 답합니다.

## 언제 Sparse Table을 쓰는가

Sparse Table은 업데이트가 없는 정적 배열에서 강합니다.

| 문제 신호 | Sparse Table 관점 |
| --- | --- |
| 배열이 한 번 주어지고 바뀌지 않는다 | 전처리를 크게 해도 된다 |
| 구간 최솟값/최댓값 질의가 많다 | idempotent 연산이라 `O(1)` 질의 가능 |
| LCP 배열에서 구간 최솟값을 묻는다 | suffix rank 사이 RMQ |
| 트리 LCA를 Euler Tour + RMQ로 구한다 | depth 배열의 최소 depth index |

업데이트가 있으면 Segment Tree나 Fenwick Tree가 더 자연스럽습니다. Sparse Table은 "정적 질의가 매우 많다"는 조건에서 선택합니다.

## `2^k` 길이 구간 저장

`table[k][i]`를 `i`에서 시작하는 길이 `2^k` 구간의 최솟값이라고 합시다.

```text
table[0][i] = a[i]
table[k][i] = min(table[k-1][i], table[k-1][i + 2^(k-1)])
```

길이 `2^k` 구간은 길이 `2^(k-1)` 구간 두 개로 나눌 수 있습니다. 그래서 작은 길이부터 차례대로 전처리합니다.

## RMQ 구현

아래 구현은 정적 배열에서 inclusive 구간 `[left, right]`의 최솟값을 `O(1)`에 구합니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct SparseTableMin {
    vector<int> log2Value;
    vector<vector<int>> table;

    explicit SparseTableMin(const vector<int>& values) {
        int n = (int)values.size();
        log2Value.assign(n + 1, 0);
        for (int i = 2; i <= n; ++i) {
            log2Value[i] = log2Value[i / 2] + 1;
        }

        int levels = log2Value[n] + 1;
        table.assign(levels, vector<int>(n));
        table[0] = values;

        for (int k = 1; k < levels; ++k) {
            int length = 1 << k;
            int half = length >> 1;
            for (int i = 0; i + length <= n; ++i) {
                table[k][i] = min(table[k - 1][i], table[k - 1][i + half]);
            }
        }
    }

    int queryMin(int left, int right) const {
        int length = right - left + 1;
        int k = log2Value[length];
        int blockLength = 1 << k;
        return min(table[k][left], table[k][right - blockLength + 1]);
    }
};
```

질의할 때 길이 `len`에 대해 `2^k <= len`인 가장 큰 `k`를 고릅니다. 왼쪽에서 길이 `2^k` 구간 하나, 오른쪽에서 길이 `2^k` 구간 하나를 잡으면 전체 구간을 덮습니다. 두 구간이 겹칠 수 있지만 `min`은 같은 원소가 두 번 들어가도 결과가 변하지 않습니다.

## Idempotent 연산과 아닌 연산

Sparse Table의 `O(1)` 질의는 연산이 idempotent일 때 성립합니다.

```text
min(x, x) = x
max(x, x) = x
gcd(x, x) = x
```

겹치는 두 구간을 합쳐도 중복 원소가 답을 바꾸지 않습니다. 반면 합은 `x + x`가 `x`와 다르므로 같은 방식으로 겹치면 안 됩니다.

| 연산 | `O(1)` 겹침 질의 가능? | 이유 |
| --- | --- | --- |
| min/max | 가능 | 중복되어도 결과 불변 |
| gcd | 가능 | 중복되어도 결과 불변 |
| bitwise and/or | 가능 | 중복되어도 결과 불변 |
| sum | 불가능 | 중복되면 값이 커짐 |
| xor | 불가능 | 중복되면 사라짐 |

sum처럼 겹치면 안 되는 연산도 Sparse Table로 `O(log N)` 질의는 가능합니다. 구간 길이를 이진수로 쪼개 서로 겹치지 않는 블록들을 합치면 됩니다. 하지만 합 질의만 필요하면 prefix sum이 더 단순합니다.

## LCP 배열과 RMQ

Suffix Array에서 두 suffix의 LCP를 묻고 싶다면, 두 suffix의 rank 사이에 있는 LCP 배열의 최솟값을 구합니다.

```text
rank[a] < rank[b] 라면
LCP(suffix a, suffix b) = min(lcp[rank[a] + 1 ... rank[b]])
```

이 질의가 많으면 LCP 배열 위에 Sparse Table을 올립니다. 문자열 문제에서 "두 suffix의 공통 접두사 길이를 여러 번 묻는다"면 Suffix Array + LCP + RMQ 조합을 고려합니다.

## LCA와 Euler Tour

트리의 LCA도 RMQ로 바꿀 수 있습니다.

1. DFS Euler Tour를 하며 방문한 정점과 depth를 기록한다.
2. 각 정점이 처음 등장한 위치를 저장한다.
3. 두 정점의 첫 등장 위치 사이에서 depth가 최소인 정점이 LCA다.

이때 질의는 "구간에서 depth가 최소인 index"가 됩니다. 단순 최솟값이 아니라 정점 번호까지 필요하므로, table에는 `(depth, vertex)` 쌍 또는 depth 비교용 index를 저장합니다.

## 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| 로그 배열 전처리 | `O(N)` | `O(N)` |
| Sparse Table 빌드 | `O(N log N)` | `O(N log N)` |
| min/max/gcd RMQ | `O(1)` | table 사용 |
| sum 같은 비-idempotent 질의 | `O(log N)` | table 사용 |

메모리는 `N log N`입니다. `N = 200000`이면 약 18단계 정도라 충분할 수 있지만, 값 타입이 크거나 여러 table을 만들면 메모리를 먼저 계산해야 합니다.

## 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 업데이트가 있는데 Sparse Table 사용 | 변경 후 질의 오답 | 정적 배열인지 확인 |
| `right - blockLength + 1` 계산 누락 | 구간 오른쪽 일부 누락 | 두 블록이 구간 양끝에서 시작하는지 확인 |
| sum을 `O(1)` 겹침 방식으로 처리 | 중복 합산 오답 | idempotent 연산인지 확인 |
| `log2`를 실수 함수로 매번 계산 | 느리거나 오차 가능 | 정수 로그 배열 전처리 |
| 빈 구간 질의 처리 누락 | 런타임 에러 | `left <= right` 보장 |
| LCP RMQ 인덱스 off-by-one | 한 칸 밀린 LCP | `rank[a] + 1 ... rank[b]` 범위 확인 |
