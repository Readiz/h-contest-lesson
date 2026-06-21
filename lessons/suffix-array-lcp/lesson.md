# Suffix Array와 LCP

Suffix Array는 문자열의 모든 suffix를 사전순으로 정렬한 배열입니다. KMP와 Z algorithm이 한 패턴의 등장 위치를 찾는 데 강하다면, Suffix Array는 suffix 전체의 순서를 만들어 반복 부분 문자열, 서로 다른 부분 문자열 개수, 패턴 검색, LCP 질의 같은 문제를 넓게 처리합니다.

이 레슨은 suffix 정렬과 LCP(Longest Common Prefix)를 함께 봅니다.

1. suffix를 사전순으로 정렬한다.
2. 인접한 suffix 사이의 LCP를 선형 시간에 계산한다.
3. 정렬된 suffix와 LCP를 문제 요구에 맞게 해석한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 문자열 매칭, 정렬, 좌표 압축, sparse table 감각
- 함께 보면 좋은 레슨: 문자열 매칭: KMP, Z, Rolling Hash, Trie와 Aho-Corasick
- 다음에 볼 레슨: Sparse Table/RMQ, Suffix Automaton

## 1. Suffix Array가 필요한 상황

문자열 하나에서 suffix들의 상대 순서가 필요하면 Suffix Array를 떠올립니다.

| 질문 | Suffix Array 관점 |
| --- | --- |
| 어떤 패턴이 등장하는가 | 정렬된 suffix에서 lower_bound로 찾는다 |
| 가장 긴 반복 부분 문자열은 무엇인가 | 인접 suffix의 LCP 최댓값 |
| 서로 다른 부분 문자열은 몇 개인가 | 전체 부분 문자열 수에서 LCP 합을 뺀다 |
| 두 suffix의 LCP를 빠르게 묻는다 | LCP 배열 위 RMQ |
| 여러 문자열의 공통 부분 문자열 | 구분자를 붙이고 suffix 출처를 관리한다 |

모든 suffix를 실제 문자열로 만들어 정렬하면 비교 한 번에 `O(N)`이 걸려 너무 느립니다. 그래서 suffix의 앞 `2^k`글자 순위를 반복적으로 두 배씩 늘리며 정렬합니다.

## 2. Doubling 알고리즘

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

## 3. LCP 배열

LCP 배열은 Suffix Array에서 이웃한 suffix 사이의 최장 공통 접두사 길이입니다.

```text
lcp[i] = LCP(suffix sa[i - 1], suffix sa[i])
```

Kasai 알고리즘은 suffix 시작 위치의 rank를 이용해 전체 LCP를 `O(N)`에 계산합니다. 핵심은 다음 suffix로 한 칸 이동하면 기존 LCP 길이가 최소 1 줄어든 상태에서 시작할 수 있다는 점입니다.

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

## 4. 패턴 검색

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
            return s[start + i] < pattern[i] ? -1 : 1;
        }
    }
    return 0;
}

bool containsPattern(const string& s, const vector<int>& sa, const string& pattern) {
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

## 5. 대표 응용

Suffix Array와 LCP의 대표 응용은 아래처럼 계산합니다.

| 문제 | 해석 |
| --- | --- |
| 가장 긴 반복 부분 문자열 | `max(lcp)` |
| 서로 다른 부분 문자열 수 | `N * (N + 1) / 2 - sum(lcp)` |
| 두 suffix의 LCP | suffix rank 사이의 LCP 구간 최솟값 |
| 사전순 k번째 suffix | `sa[k]` |
| 패턴 등장 개수 | pattern과 일치하는 suffix 구간 길이 |

서로 다른 부분 문자열 개수 공식은 각 suffix가 만드는 새 부분 문자열 개수를 세는 방식입니다. suffix `sa[i]`는 길이 `N - sa[i]`개의 prefix 부분 문자열을 만들 수 있지만, 바로 앞 suffix와 겹치는 `lcp[i]`개는 이미 나온 부분 문자열입니다.

## 6. 여러 문자열을 붙일 때

두 문자열의 가장 긴 공통 부분 문자열 같은 문제에서는 구분자를 넣어 문자열을 합칩니다.

```text
combined = A + '$' + B + '#'
```

구분자는 입력에 등장하지 않는 문자여야 하고, 서로 다른 구분자를 쓰는 편이 안전합니다. Suffix Array를 만든 뒤 인접 suffix가 서로 다른 원본 문자열에서 왔는지 확인하고, 그때의 LCP를 후보로 봅니다.

문자열이 여러 개라면 sliding window와 LCP RMQ를 결합하거나, suffix automaton 같은 다른 구조가 더 자연스러울 수 있습니다.

## 7. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| Doubling Suffix Array | `O(N log^2 N)` | `O(N)` |
| Counting sort 최적화 Doubling | `O(N log N)` | `O(N)` |
| Kasai LCP | `O(N)` | `O(N)` |
| 패턴 존재 확인 | `O(M log N)` | Suffix Array 사용 |
| 서로 다른 부분 문자열 수 | `O(N)` | LCP 배열 사용 |

`N`이 수십만이고 시간 제한이 빡빡하면 `sort` 기반 `O(N log^2 N)` 구현은 위험할 수 있습니다. 그때는 radix/counting sort 기반 doubling 또는 suffix automaton을 검토합니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| suffix를 실제 `substr`로 만들어 정렬 | 시간/메모리 초과 | 시작 인덱스만 정렬 |
| `rank[i + len]` 경계 처리 누락 | 범위 밖 접근 | 범위 밖은 `-1`로 둔다 |
| 빈 문자열 또는 길이 1 처리 누락 | 런타임 에러 | `n == 0`, `n == 1` 별도 확인 |
| LCP 인덱스 정의 혼동 | RMQ 구간 off-by-one | `lcp[i] = LCP(sa[i-1], sa[i])`로 고정 |
| 구분자가 입력에 등장 | 문자열 경계 넘어 매칭 | 입력 alphabet 밖 문자 사용 |
| `int`로 부분 문자열 개수 계산 | overflow | `long long` 사용 |

## 9. 문제를 볼 때 체크할 조건

1. suffix의 사전순 순서가 필요한가?
2. 반복 부분 문자열이나 서로 다른 부분 문자열 개수를 묻는가?
3. 한 텍스트에 대해 패턴 질의가 여러 개인가?
4. 두 suffix의 LCP 질의가 많은가?
5. 문자열을 여러 개 붙일 때 구분자를 안전하게 고를 수 있는가?
6. 입력 크기가 `O(N log^2 N)` 구현으로 충분한가?

Suffix Array는 문자열을 정렬 문제로 바꾸는 도구입니다. 정렬된 suffix 위에서 인접 관계는 LCP로, 구간 질의는 RMQ로 확장된다고 이해하면 응용을 잡기 쉽습니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: suffix array 생성 `/practice/...` 문제 필요 | doubling 순위 갱신 구현 | rank pair |
| 표준 | TODO: 가장 긴 반복 부분 문자열 `/practice/...` 문제 필요 | LCP 배열의 최댓값 해석 | Kasai |
| 응용 | TODO: 서로 다른 부분 문자열 수 `/practice/...` 문제 필요 | 전체 부분 문자열 수에서 LCP 합 제거 | distinct substrings |
| 함정 | TODO: 여러 문자열 공통 부분 문자열 `/practice/...` 문제 필요 | 구분자와 suffix 출처 관리 | separator, source id |
