# Suffix Array와 LCP

Suffix Array는 문자열의 모든 suffix를 사전순으로 정렬한 배열입니다. KMP와 Z algorithm이 한 패턴의 등장 위치를 찾는 데 강하다면, Suffix Array는 suffix 전체의 순서를 만들어 반복 부분 문자열, 서로 다른 부분 문자열 개수, 패턴 검색, LCP 질의 같은 문제를 넓게 처리합니다.

## Suffix Array가 필요한 상황

문자열 하나에서 suffix들의 상대 순서가 필요하면 Suffix Array를 떠올립니다.

| 질문 | Suffix Array 관점 |
| --- | --- |
| 어떤 패턴이 등장하는가 | 정렬된 suffix에서 lower_bound로 찾는다 |
| 가장 긴 반복 부분 문자열은 무엇인가 | 인접 suffix의 LCP 최댓값 |
| 서로 다른 부분 문자열은 몇 개인가 | 전체 부분 문자열 수에서 LCP 합을 뺀다 |
| 두 suffix의 LCP를 빠르게 묻는다 | LCP 배열 위 RMQ |
| 여러 문자열의 공통 부분 문자열 | 구분자를 붙이고 suffix 출처를 관리한다 |

모든 suffix를 실제 문자열로 만들어 정렬하면 비교 한 번에 `O(N)`이 걸려 너무 느립니다. 그래서 suffix의 앞 `2^k`글자 순위를 반복적으로 두 배씩 늘리며 정렬합니다.

## Doubling 알고리즘

처음에는 한 글자 기준 순위를 둡니다. 그다음 길이 `1`, `2`, `4`, `8`처럼 두 배씩 늘리며 suffix를 `(현재 순위, 다음 절반 순위)` 쌍으로 정렬합니다.

```text
rank[i] = s[i..]의 앞 len 글자 기준 순위
key(i) = (rank[i], rank[i + len])
```

`len`이 문자열 길이 이상이 되면 전체 suffix 순서가 완성됩니다.

```cpp compile-check
#include <algorithm>
#include <string>
#include <vector>
using namespace std;

vector<int> buildSuffixArray(const string& s) {
    int n = (int)s.size();
    vector<int> sa(n);
    vector<int> rank(n);
    vector<int> nextRank(n);

    for (int i = 0; i < n; ++i) {
        sa[i] = i;
        rank[i] = (unsigned char)s[i];
    }

    for (int len = 1; len < n; len <<= 1) {
        sort(sa.begin(), sa.end(), [&](int a, int b) {
            if (rank[a] != rank[b]) {
                return rank[a] < rank[b];
            }
            int ra = a + len < n ? rank[a + len] : -1;
            int rb = b + len < n ? rank[b + len] : -1;
            return ra < rb;
        });

        nextRank[sa[0]] = 0;
        for (int i = 1; i < n; ++i) {
            int prev = sa[i - 1];
            int cur = sa[i];
            bool different = rank[prev] != rank[cur];
            if (!different) {
                int prevNext = prev + len < n ? rank[prev + len] : -1;
                int curNext = cur + len < n ? rank[cur + len] : -1;
                different = prevNext != curNext;
            }
            nextRank[cur] = nextRank[prev] + (different ? 1 : 0);
        }

        rank.swap(nextRank);
        if (rank[sa[n - 1]] == n - 1) {
            break;
        }
    }

    return sa;
}
```

이 구현은 `sort`를 매 단계 쓰므로 `O(N log^2 N)`입니다. 충분히 큰 입력에서는 counting sort를 써서 `O(N log N)`으로 줄이는 구현도 있습니다. 입문 단계에서는 먼저 doubling의 순위 갱신 의미를 정확히 잡는 것이 중요합니다.

## LCP 배열

LCP 배열은 Suffix Array에서 이웃한 suffix 사이의 최장 공통 접두사 길이입니다.

```text
lcp[i] = LCP(suffix sa[i - 1], suffix sa[i])
```

Kasai 알고리즘은 suffix 시작 위치의 rank를 이용해 전체 LCP를 `O(N)`에 계산합니다. 핵심은 다음 suffix로 한 칸 이동하면 새 LCP가 이전 값보다 최대 1만 작아져, `max(이전 값-1,0)`부터 비교할 수 있다는 점입니다.

```cpp compile-check
#include <string>
#include <vector>
using namespace std;

vector<int> buildLcpArray(const string& s, const vector<int>& sa) {
    int n = (int)s.size();
    vector<int> rank(n, 0);
    for (int i = 0; i < n; ++i) {
        rank[sa[i]] = i;
    }

    vector<int> lcp(n, 0);
    int matched = 0;
    for (int i = 0; i < n; ++i) {
        int order = rank[i];
        if (order == 0) {
            matched = 0;
            continue;
        }

        int previousSuffix = sa[order - 1];
        while (i + matched < n &&
               previousSuffix + matched < n &&
               s[i + matched] == s[previousSuffix + matched]) {
            ++matched;
        }
        lcp[order] = matched;
        if (matched > 0) {
            --matched;
        }
    }
    return lcp;
}
```

`lcp[0]`은 비교할 이전 suffix가 없으므로 보통 `0`으로 둡니다. 문제나 라이브러리에 따라 `lcp[i]`의 의미가 `sa[i]`와 `sa[i + 1]` 사이인 경우도 있으니 인덱스 정의를 먼저 고정해야 합니다.

## 패턴 검색

정렬된 suffix 배열에서 패턴은 연속 구간으로 나타납니다. suffix와 pattern을 비교하는 함수를 만들고 이분 탐색하면 됩니다.

```cpp compile-check
#include <string>
#include <vector>
using namespace std;

int compareSuffixWithPattern(const string& s, int start, const string& pattern) {
    int n = (int)s.size();
    int m = (int)pattern.size();
    for (int i = 0; i < m; ++i) {
        if (start + i == n) {
            return -1;
        }
        if (s[start + i] != pattern[i]) {
            return (unsigned char)s[start + i] < (unsigned char)pattern[i] ? -1 : 1;
        }
    }
    return 0;
}

bool containsPattern(const string& s, const vector<int>& sa, const string& pattern) {
    if (pattern.empty()) return true;
    int left = 0;
    int right = (int)sa.size();
    while (left < right) {
        int mid = (left + right) / 2;
        if (compareSuffixWithPattern(s, sa[mid], pattern) < 0) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    return left < (int)sa.size() &&
        compareSuffixWithPattern(s, sa[left], pattern) == 0;
}
```

패턴 길이가 `M`이면 비교 한 번이 최악 `O(M)`입니다. 단순 이분 탐색은 `O(M log N)`이고, 여러 패턴을 많이 처리한다면 LCP를 활용한 최적화나 다른 자료구조도 고려합니다.

패턴 등장 횟수가 필요하면 위 비교 함수가 처음 0 이상이 되는 위치와 처음 양수가 되는 위치를 각각 이분 탐색합니다. 두 경계의 차이가 등장 횟수이며, 별도의 다음 문자열을 만들 필요가 없습니다.

## LCP RMQ

`rank[i]`를 suffix `s[i..]`의 suffix array 위치라고 하겠습니다. 두 suffix `i`, `j`의 LCP는 rank 사이의 LCP 배열 최솟값입니다.

```text
ri = rank[i], rj = rank[j]
if ri > rj swap(ri, rj)
lcp(i, j) = min(lcp[ri + 1], ..., lcp[rj])
```

이 구간 최솟값을 자주 묻는다면 Sparse Table을 올립니다.

[Sparse Table](https://h.readiz.com/learn/sparse-table-rmq)의 `SparseTableMin(lcp)`를 그대로 사용합니다. `i == j`이면 `N-i`, 아니면 `queryMin(min(ri,rj)+1,max(ri,rj))`가 답입니다.

## 서로 다른 부분 문자열과 k번째 부분 문자열

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

## 여러 문자열의 공통 Substring

입력에 없는 서로 다른 separator로 여러 문자열을 이어 붙이고 suffix array를 만들면, 각 suffix의 원본 문자열 id를 알 수 있습니다.

```text
s1 + # + s2 + $ + s3
```

모든 문자열을 포함하는 suffix array window를 two pointers로 유지하고, 그 window 내부 인접 LCP의 최솟값이 공통 substring 길이 후보가 됩니다. window 안에 source id가 모두 들어왔는지 count 배열로 관리합니다.

이 방식은 "모든 문자열에 등장하는 가장 긴 substring"에 잘 맞습니다. 특정 두 문자열만 비교한다면 combined suffix array에서 인접한 서로 다른 source suffix의 LCP 최댓값만 봐도 됩니다.

## 반복 Substring과 위치 조건

LCP 값이 크다는 것은 인접 suffix 두 개가 긴 prefix를 공유한다는 뜻입니다. 하지만 문제는 종종 위치 조건을 함께 요구합니다.

| 조건 | 추가로 볼 값 |
| --- | --- |
| 두 번 이상 등장 | LCP 최댓값 |
| 겹치지 않고 등장 | suffix 위치 차이 `>= length` |
| 적어도 k번 등장 | suffix array에서 크기 k window의 LCP 최솟값 |
| 서로 다른 source에 등장 | source id count |

겹치지 않는 반복은 인접 suffix만 검사하면 놓칠 수 있습니다. 후보 길이 이상 LCP로 연결된 전체 그룹의 최소·최대 시작 위치 차이를 봅니다. `k=1`이면 전체 문자열 길이가 답입니다. `k >= 2`에서 `k`번 이상 등장하는 substring 길이는 size `k` window마다 LCP 최솟값을 보며 최댓값을 취합니다. 구간 최솟값은 Sparse Table 또는 deque로 처리할 수 있습니다.

## 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| Doubling Suffix Array | `O(N log^2 N)` | `O(N)` |
| Counting sort 최적화 Doubling | `O(N log N)` | `O(N)` |
| Kasai LCP | `O(N)` | `O(N)` |
| 패턴 존재 확인 | `O(M log N)` | Suffix Array 사용 |
| 서로 다른 부분 문자열 수 | `O(N)` | LCP 배열 사용 |

`N`이 수십만이고 시간 제한이 빡빡하면 `sort` 기반 `O(N log^2 N)` 구현은 위험할 수 있습니다. 그때는 radix/counting sort 기반 doubling 또는 suffix automaton을 검토합니다.
