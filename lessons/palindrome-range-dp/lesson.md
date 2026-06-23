# Palindrome Range DP

Palindrome Range DP는 "구간이 palindrome인가"라는 판정 구조를 DP 전이와 결합하는 문자열/DP 응용 레슨입니다. Palindrome Query Structures가 판정 도구를 고르는 레슨이라면, 이 레슨은 그 판정값을 어떻게 구간 DP, 분할 DP, 최소 편집 DP의 상태로 넣을지 다룹니다.

이 레슨은 Palindrome Query Structures와 Dynamic Programming 이후에 보는 응용 주제입니다.

1. 모든 구간 palindrome 여부를 먼저 안정적으로 만든다.
2. DP 상태가 구간 자체인지, prefix 분할인지 구분한다.
3. `isPal[l][r]`를 전이에 넣을 때 길이 순서와 off-by-one을 점검한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Dynamic Programming, Palindrome Query Structures, Rolling Hash
- 함께 보면 좋은 레슨: Palindromic Tree, Suffix와 Palindrome 응용, Interval DP
- 다음에 볼 레슨: string period query applications, palindrome automaton DP, interval optimization

## 1. 문제 신호

| 문제 표현 | 우선 모델 |
| --- | --- |
| 문자열을 palindrome 조각으로 최소 분할 | prefix DP + `isPal[l][r]` |
| 구간을 지워서 palindrome으로 만들기 | interval DP |
| 양끝 문자가 같으면 내부로 줄어듦 | interval recurrence |
| 많은 구간 palindrome 판정 뒤 DP | Manacher 또는 `O(N^2)` table |
| 짧은 문자열, 모든 구간 전이 | `O(N^2)` 또는 `O(N^3)` baseline |

문제에서 palindrome을 "세는지", "분할하는지", "편집하는지"가 다릅니다. 판정만 빠르게 해도 DP는 별도 설계가 필요합니다.

## 2. Palindrome Table 만들기

가장 직관적인 방법은 길이 순서로 `isPal[l][r]`를 채우는 것입니다.

```text
isPal[l][r] =
  s[l] == s[r] and (r - l <= 1 or isPal[l + 1][r - 1])
```

길이가 작은 구간부터 채워야 내부 구간 값이 이미 계산되어 있습니다.

```cpp compile-check
#include <string>
#include <vector>
using namespace std;

vector<vector<char>> buildPalindromeTable(const string& s) {
    int n = (int)s.size();
    vector<vector<char>> isPal(n, vector<char>(n, 0));

    for (int len = 1; len <= n; ++len) {
        for (int left = 0; left + len <= n; ++left) {
            int right = left + len - 1;
            if (s[left] != s[right]) {
                continue;
            }
            if (len <= 2 || isPal[left + 1][right - 1]) {
                isPal[left][right] = 1;
            }
        }
    }

    return isPal;
}
```

`N`이 5000 정도면 `O(N^2)` table이 실용적입니다. `N`이 더 크면 Manacher radius로 판정하거나 문제 구조를 더 봐야 합니다.

## 3. 최소 Palindrome 분할

문자열 prefix `s[0..i)`를 palindrome 조각으로 나누는 최소 개수를 `dp[i]`라고 합시다.

```text
dp[0] = 0
dp[i] = min(dp[l] + 1) where isPal[l][i - 1]
```

```cpp compile-check
#include <algorithm>
#include <string>
#include <vector>
using namespace std;

vector<vector<char>> makePalTableForPartition(const string& s) {
    int n = (int)s.size();
    vector<vector<char>> isPal(n, vector<char>(n, 0));
    for (int len = 1; len <= n; ++len) {
        for (int left = 0; left + len <= n; ++left) {
            int right = left + len - 1;
            if (s[left] == s[right] && (len <= 2 || isPal[left + 1][right - 1])) {
                isPal[left][right] = 1;
            }
        }
    }
    return isPal;
}

int minimumPalindromePieces(const string& s) {
    int n = (int)s.size();
    vector<vector<char>> isPal = makePalTableForPartition(s);
    const int INF = 1'000'000'000;
    vector<int> dp(n + 1, INF);
    dp[0] = 0;

    for (int right = 1; right <= n; ++right) {
        for (int left = 0; left < right; ++left) {
            if (isPal[left][right - 1]) {
                dp[right] = min(dp[right], dp[left] + 1);
            }
        }
    }

    return dp[n];
}
```

컷 개수를 묻는 문제라면 조각 수에서 1을 빼야 할 수 있습니다. 출력이 "분할 횟수"인지 "조각 수"인지 확인합니다.

## 4. Interval DP와의 차이

Prefix 분할 DP는 왼쪽에서 오른쪽으로 조각을 붙입니다. Interval DP는 구간 `[l, r]` 자체를 줄입니다.

| 유형 | 상태 | 전이 |
| --- | --- | --- |
| 최소 palindrome partition | `dp[i]` | 마지막 조각 `[l, i)` |
| 최소 삽입으로 palindrome | `dp[l][r]` | 양끝 비교 후 내부 |
| palindrome subsequence | `dp[l][r]` | 양끝 선택 여부 |
| 구간 삭제 게임 | `dp[l][r]` | palindrome block 제거 |

같은 `isPal` table을 쓰더라도 DP 방향이 다르면 반복 순서가 달라집니다.

## 5. 최소 삽입 예시

문자열을 palindrome으로 만들기 위한 최소 삽입 횟수는 아래처럼 볼 수 있습니다.

```text
if s[l] == s[r]:
  dp[l][r] = dp[l + 1][r - 1]
else:
  dp[l][r] = 1 + min(dp[l + 1][r], dp[l][r - 1])
```

이 문제는 `isPal` table 없이도 풀립니다. 반대로 partition 문제는 마지막 조각이 palindrome인지 빠르게 알아야 하므로 table이 유용합니다.

## 6. Manacher와 결합하기

메모리가 부담되면 Manacher radius로 `isPalindrome(l, r)`를 `O(1)`에 판정할 수 있습니다. 다만 DP가 모든 `l, r`을 방문하면 시간은 여전히 `O(N^2)`입니다.

```text
for right in 1..N:
  for left in 0..right-1:
    if manacherSaysPalindrome(left, right - 1):
      relax
```

Manacher는 table 메모리를 줄여 주지만, DP 전이 수 자체를 줄이지는 않습니다.

## 7. 작은 예시

```text
s = "ababa"

palindrome 구간:
  [0,0] a
  [1,1] b
  [2,2] a
  [3,3] b
  [4,4] a
  [0,2] aba
  [1,3] bab
  [2,4] aba
  [0,4] ababa

prefix DP:
  dp[0] = 0
  dp[1] = 1  ("a")
  dp[3] = 1  ("aba")
  dp[5] = 1  ("ababa")
```

가장 긴 palindrome만 찾으면 답이 되는 것이 아닙니다. 예를 들어 `"abacdc"`는 `"aba" + "cdc"`가 좋고, 중간 선택이 전체 분할에 영향을 줍니다.

## 8. 시간 복잡도

| 접근 | 시간 | 메모리 |
| --- | ---: | ---: |
| `O(N^2)` palindrome table + prefix DP | `O(N^2)` | `O(N^2)` |
| Manacher + prefix DP | `O(N^2)` | `O(N)` |
| interval DP | 보통 `O(N^2)` | `O(N^2)` |
| 모든 분할 복원 | 답 개수에 따라 증가 | parent 저장 필요 |

문자열 길이가 2만 이상이면 모든 pair 전이가 이미 위험합니다. 그때는 문제에 있는 추가 조건을 찾아야 합니다.

## 9. 자주 하는 실수

1. `isPal[left][right]`와 substring `[left, right)` convention을 섞는다.
2. 길이 2 palindrome에서 내부 구간을 잘못 참조한다.
3. 조각 수와 컷 수를 혼동한다.
4. Manacher radius의 odd/even 중심을 한 칸 밀린다.
5. interval DP를 prefix 순서로 채워 아직 계산되지 않은 값을 읽는다.

## 10. 문제를 볼 때 체크할 조건

- 출력이 partition count인지 edit count인지 확인했는가?
- palindrome 판정을 table, Manacher, hash 중 무엇으로 할 것인가?
- DP 상태가 prefix인가 interval인가?
- `N^2` 메모리가 가능한가?
- 답 복원이 필요하면 parent를 어떻게 저장할 것인가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: palindrome partition `/practice/...` 문제 필요 | `isPal` table + prefix DP | last piece |
| 표준 | TODO: minimum insertion palindrome `/practice/...` 문제 필요 | interval DP 반복 순서 | both ends |
| 응용 | TODO: palindrome range DP `/practice/...` 문제 필요 | Manacher 판정과 DP 결합 | radius query |
| 함정 | TODO: cuts vs pieces `/practice/...` 문제 필요 | 출력 convention 확인 | off-by-one |
