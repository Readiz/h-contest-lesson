# Palindrome Query Structures

Palindrome Query Structures는 substring이 palindrome인지 빠르게 판정하거나, 구간 안의 palindrome 통계를 관리하기 위한 기법 묶음입니다. Manacher, rolling hash, Palindromic Tree는 각각 강한 지점이 다르기 때문에 문제의 질의 형태를 먼저 분류해야 합니다.

## 문제 신호

| 문제 표현 | 우선 볼 구조 |
| --- | --- |
| 많은 substring palindrome 판정 | Manacher radius 또는 rolling hash |
| 모든 서로 다른 palindrome 개수 | Palindromic Tree |
| prefix를 추가하면서 palindrome 통계 | Palindromic Tree |
| 한 글자 update 후 palindrome 질의 | forward/reverse hash segment tree |
| 구간 안 palindrome substring 개수 | 문제 제한에 따라 offline, Eertree, DP 후보 |

중요한 차이는 "판정"과 "열거/집계"입니다. 판정만 있으면 hash나 radius가 훨씬 단순합니다.

## Manacher Radius로 판정하기

Manacher는 각 중심에서 확장 가능한 palindrome radius를 선형 시간에 계산합니다.

| 배열 | 의미 |
| --- | --- |
| `odd[i]` | 중심 `i`인 홀수 길이 palindrome radius |
| `even[i]` | `i-1`과 `i` 사이 중심인 짝수 길이 palindrome radius |

구간 `[l, r]`이 palindrome인지 보려면 길이의 홀짝에 따라 중심과 필요한 radius를 계산합니다.

```text
len = r - l + 1
if len is odd:
  c = (l + r) / 2
  need = len / 2 + 1
  odd[c] >= need
else:
  c = (l + r + 1) / 2
  need = len / 2
  even[c] >= need
```

정적 문자열에 많은 판정 질의가 있을 때 가장 직접적입니다.

## Manacher 구현

정적 문자열의 닫힌 구간 `0 <= l <= r < N`을 판정합니다. 홀수 반지름은 중심을 포함하고 짝수 반지름은 중심 오른쪽 칸을 기준으로 셉니다. 빈 문자열도 전처리할 수 있지만 그 안에는 유효한 비어 있지 않은 질의가 없습니다.

```cpp compile-check
#include <algorithm>
#include <string>
#include <vector>
using namespace std;

struct Manacher {
    vector<int> odd, even;
    explicit Manacher(const string& s) : odd(s.size()), even(s.size()) {
        int n = (int)s.size();
        for (int i = 0, l = 0, r = -1; i < n; ++i) {
            int k = i > r ? 1 : min(odd[l + r - i], r - i + 1);
            while (i - k >= 0 && i + k < n && s[i-k] == s[i+k]) ++k;
            odd[i] = k;
            if (i + k - 1 > r) { l = i - k + 1; r = i + k - 1; }
        }
        for (int i = 0, l = 0, r = -1; i < n; ++i) {
            int k = i > r ? 0 : min(even[l + r - i + 1], r - i + 1);
            while (i - k - 1 >= 0 && i + k < n && s[i-k-1] == s[i+k]) ++k;
            even[i] = k;
            if (i + k - 1 > r) { l = i - k; r = i + k - 1; }
        }
    }
    bool isPalindrome(int l, int r) const {
        int len = r - l + 1;
        return len % 2 ? odd[l + len/2] >= len/2 + 1
                       : even[l + len/2] >= len/2;
    }
};
```

이미 확인한 가장 오른쪽 회문의 대칭 위치에서 반지름을 가져오되, 그 회문의 오른쪽 경계를 넘는 부분만 직접 비교합니다. 성공한 추가 확장은 오른쪽 경계를 전진시키므로 총 `O(N)`입니다.

## Rolling Hash로 판정하기

Forward hash와 reversed string hash를 준비하면 substring과 그 reverse를 비교할 수 있습니다.

원문과 뒤집은 문자열에 기존 Rolling Hash를 각각 만듭니다. 원문의 `[l,r)`와 역문자열의 `[N-r,N-l)` 해시를 비교합니다. 코드 복제 없이 같은 해시 구현을 두 번 사용하며, 충돌 없는 정적 판정에는 위 Manacher 반지름을 씁니다.

Hash는 충돌 가능성이 있습니다. 중요한 판정이면 double hash를 쓰거나 Manacher처럼 deterministic한 방법을 선택합니다.

## Eertree가 필요한 경우

Palindromic Tree는 prefix를 한 글자씩 추가하면서 새로 생기는 서로 다른 palindrome을 node로 만듭니다.

| 필요한 작업 | Eertree가 주는 값 |
| --- | --- |
| 서로 다른 palindrome 개수 | node count |
| 각 palindrome occurrence | suffix link 역순 누적 |
| prefix별 palindrome suffix | current longest suffix node |
| palindrome 종류별 DP | node graph DP |

구간 `[l, r]`이 palindrome인지 묻는 단순 판정에는 Eertree가 과합니다. 하지만 "어떤 palindrome들이 있는지"가 필요하면 가장 강합니다.

## 구간 업데이트가 있는 경우

문자가 바뀌는 update가 있고 palindrome 판정 질의가 있으면 forward hash와 reverse hash를 segment tree로 관리할 수 있습니다.

```text
update position p:
  forward tree의 p 변경
  reverse tree의 n-1-p 변경

query [l, r]:
  forward hash(l, r)
  reverse hash(n-1-r, n-1-l)
  두 값 비교
```

이 모델은 판정에는 강하지만 palindrome 개수 집계에는 약합니다. update 뒤 "구간 안 palindrome substring 수"를 묻는 문제는 훨씬 어렵고, 제한이 작은지 또는 offline 성질이 있는지 먼저 봐야 합니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| Manacher 전처리 | `O(N)` |
| Manacher 판정 | `O(1)` |
| Hash 전처리 | `O(N)` |
| Hash 판정 | `O(1)` |
| Hash segment tree update/query | `O(log N)` |
| Eertree construction | `O(N * suffix fallback cost)` |

alphabet과 hash collision 정책에 따라 상수와 안정성이 달라집니다.
