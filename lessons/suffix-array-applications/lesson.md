# Suffix Array 응용 패턴

Suffix Array 응용 패턴은 suffix를 정렬해 둔 뒤 LCP 배열, RMQ, 구간 질의로 문자열 문제를 푸는 레슨입니다. Suffix Array 자체를 만드는 것보다 더 자주 막히는 지점은 "정렬된 suffix에서 어떤 구간을 봐야 하는가"입니다.

이 레슨은 Suffix Array와 LCP, Suffix와 Palindrome 응용 이후에 보는 문자열 심화 응용입니다.

1. 패턴이 등장하는 suffix 구간을 이분 탐색으로 찾는다.
2. LCP 배열 위의 RMQ로 suffix 사이 공통 prefix를 빠르게 구한다.
3. LCP 구간의 최솟값, 최댓값, sliding window로 반복/공통 substring 조건을 모델링한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Suffix Array, LCP, binary search, RMQ
- 함께 보면 좋은 레슨: Suffix Array와 LCP, Sparse Table RMQ, Runs와 문자열 주기
- 다음에 볼 레슨: border automaton, multi-string suffix query, suffix tree intuition

## 1. 문제 신호

| 문제 표현 | Suffix Array 응용 관점 |
| --- | --- |
| 어떤 패턴이 문자열에 몇 번 등장하는가 | suffix array에서 패턴 prefix 구간 |
| 사전순 k번째 substring | suffix 순서와 LCP로 새 substring 수 누적 |
| 두 suffix의 LCP를 여러 번 묻는다 | rank 배열 + LCP RMQ |
| 여러 문자열의 공통 substring | source id sliding window |
| 반복 substring, period 후보 | LCP의 큰 값과 suffix 위치 차이 |

Suffix Array는 "suffix를 사전순으로 정렬한 좌표계"입니다. 원래 문자열 index가 아니라 suffix array rank를 기준으로 구간을 잡아야 합니다.

## 2. 패턴 등장 구간

패턴 `p`가 등장하는 모든 위치는 suffix array에서 연속 구간을 이룹니다. suffix와 `p`를 사전순으로 비교해서 `lower_bound(p)`와 `upper_bound(p)`를 찾습니다.

```text
suffix < p          -> 왼쪽 구간
suffix starts p     -> 정답 구간
suffix > p          -> 오른쪽 구간
```

`upper_bound`는 보통 `p`보다 바로 큰 문자열을 직접 만들거나, 비교 함수에서 "p가 prefix이면 같음"으로 둔 뒤 첫 번째 non-match 지점을 따로 찾습니다. alphabet이 고정되어 있지 않으면 sentinel 처리를 조심합니다.

## 3. LCP RMQ

`rank[i]`를 suffix `s[i..]`의 suffix array 위치라고 하겠습니다. 두 suffix `i`, `j`의 LCP는 rank 사이의 LCP 배열 최솟값입니다.

```text
ri = rank[i], rj = rank[j]
if ri > rj swap(ri, rj)
lcp(i, j) = min(lcp[ri + 1], ..., lcp[rj])
```

이 구간 최솟값을 자주 묻는다면 Sparse Table을 올립니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct LcpSparseTable {
    vector<int> logValue;
    vector<vector<int>> table;

    explicit LcpSparseTable(const vector<int>& lcp) {
        int n = (int)lcp.size();
        logValue.assign(n + 1, 0);
        for (int i = 2; i <= n; ++i) {
            logValue[i] = logValue[i / 2] + 1;
        }

        int levels = n == 0 ? 1 : logValue[n] + 1;
        table.assign(levels, vector<int>(n, 0));
        if (n > 0) {
            table[0] = lcp;
        }
        for (int k = 1; k < levels; ++k) {
            int len = 1 << k;
            for (int i = 0; i + len <= n; ++i) {
                table[k][i] = min(table[k - 1][i], table[k - 1][i + (len >> 1)]);
            }
        }
    }

    int rangeMin(int left, int right) const {
        if (left > right) {
            return 0;
        }
        int length = right - left + 1;
        int k = logValue[length];
        return min(table[k][left], table[k][right - (1 << k) + 1]);
    }

    int lcpBetweenRanks(int rankA, int rankB) const {
        if (rankA == rankB) {
            return -1;
        }
        if (rankA > rankB) {
            swap(rankA, rankB);
        }
        return rangeMin(rankA + 1, rankB);
    }
};
```

같은 suffix끼리의 LCP는 문자열 끝까지의 길이이므로 호출자가 따로 처리하는 편이 명확합니다.

## 4. 서로 다른 Substring과 k번째 Substring

suffix `sa[i]`가 새로 만드는 substring 수는 이전 suffix와 겹치지 않는 prefix 개수입니다.

```text
newCount(i) = (N - sa[i]) - lcp[i]
```

따라서 서로 다른 substring 총수는 모든 `newCount`의 합입니다. 사전순 k번째 substring은 suffix array 순서로 `newCount`를 빼다가, 남은 k만큼 suffix prefix를 늘려 찾습니다.

```text
answer length = lcp[i] + k
answer = s.substr(sa[i], answer length)
```

`k`와 substring 수는 쉽게 `O(N^2)`까지 커지므로 `long long`을 씁니다.

## 5. 여러 문자열의 공통 Substring

여러 문자열을 separator로 이어 붙이고 suffix array를 만들면, 각 suffix의 원본 문자열 id를 알 수 있습니다.

```text
s1 + # + s2 + $ + s3
```

모든 문자열을 포함하는 suffix array window를 two pointers로 유지하고, 그 window 내부 인접 LCP의 최솟값이 공통 substring 길이 후보가 됩니다. window 안에 source id가 모두 들어왔는지 count 배열로 관리합니다.

이 방식은 "모든 문자열에 등장하는 가장 긴 substring"에 잘 맞습니다. 특정 두 문자열만 비교한다면 combined suffix array에서 인접한 서로 다른 source suffix의 LCP 최댓값만 봐도 됩니다.

## 6. 반복 Substring과 위치 조건

LCP 값이 크다는 것은 인접 suffix 두 개가 긴 prefix를 공유한다는 뜻입니다. 하지만 문제는 종종 위치 조건을 함께 요구합니다.

| 조건 | 추가로 볼 값 |
| --- | --- |
| 두 번 이상 등장 | LCP 최댓값 |
| 겹치지 않고 등장 | suffix 위치 차이 `>= length` |
| 적어도 k번 등장 | suffix array에서 크기 k window의 LCP 최솟값 |
| 서로 다른 source에 등장 | source id count |

`k`번 이상 등장하는 substring 길이는 size `k` window마다 LCP 최솟값을 보며 최댓값을 취합니다. 구간 최솟값은 Sparse Table 또는 deque로 처리할 수 있습니다.

## 7. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| Suffix Array construction | `O(N log N)` 또는 `O(N)` |
| LCP construction | `O(N)` |
| Sparse Table build | `O(N log N)` |
| suffix LCP query | `O(1)` |
| 패턴 구간 탐색 | `O(|P| log N)` |

패턴 탐색에서 suffix와 pattern 비교를 매번 처음부터 하면 최악 입력에서 느려질 수 있습니다. 많은 패턴을 처리한다면 LCP 가속 이분 탐색, suffix automaton, trie 계열도 비교합니다.

## 8. 자주 하는 실수

1. LCP 배열 index를 `lcp[rank]`와 `lcp[rank + 1]` 중 무엇인지 혼동한다.
2. separator가 원문 alphabet에 들어 있어 문자열 경계를 넘는 substring을 세어 버린다.
3. k번째 substring에서 이미 이전 suffix와 겹친 `lcp[i]` 길이를 다시 센다.
4. 반복 substring 길이만 보고 non-overlap 위치 조건을 확인하지 않는다.
5. substring 수를 `int`에 담는다.

## 9. 문제를 볼 때 체크할 조건

- suffix의 사전순 순서가 직접 필요한가?
- 패턴이 prefix로 붙는 suffix 구간을 찾으면 되는가?
- 두 suffix 사이 LCP 질의가 여러 번 나오는가?
- 여러 문자열을 합칠 때 경계와 source id를 보존했는가?
- 온라인 업데이트가 필요해서 suffix array가 맞지 않는 문제는 아닌가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 패턴 등장 구간 `/practice/...` 문제 필요 | suffix array binary search | pattern interval |
| 표준 | TODO: k번째 substring `/practice/...` 문제 필요 | 새 substring 수 누적 | lexicographic kth |
| 응용 | TODO: 여러 문자열 LCS `/practice/...` 문제 필요 | source id sliding window | multi-string suffix |
| 함정 | TODO: non-overlap 반복 substring `/practice/...` 문제 필요 | LCP와 위치 차이 동시 확인 | repeated substring |
