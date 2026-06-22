# Palindrome Query Structures

Palindrome Query Structures는 substring이 palindrome인지 빠르게 판정하거나, 구간 안의 palindrome 통계를 관리하기 위한 기법 묶음입니다. Manacher, rolling hash, Palindromic Tree는 각각 강한 지점이 다르기 때문에 문제의 질의 형태를 먼저 분류해야 합니다.

이 레슨은 Palindromic Tree와 Suffix/Palindrome 응용 이후에 보는 문자열 심화입니다.

1. 정적 문자열의 palindrome 판정은 radius 또는 hash로 빠르게 처리한다.
2. palindrome substring을 열거하거나 occurrence를 누적해야 하면 Eertree를 고려한다.
3. 구간 질의와 업데이트가 섞이면 hash segment tree, offline, 또는 더 제한된 모델을 먼저 검토한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: palindrome, Manacher, rolling hash, Palindromic Tree
- 함께 보면 좋은 레슨: Palindromic Tree, Suffix와 Palindrome 응용, String Matching
- 다음에 볼 레슨: palindrome range query, eertree applications, hash segment tree

## 1. 문제 신호

| 문제 표현 | 우선 볼 구조 |
| --- | --- |
| 많은 substring palindrome 판정 | Manacher radius 또는 rolling hash |
| 모든 서로 다른 palindrome 개수 | Palindromic Tree |
| prefix를 추가하면서 palindrome 통계 | Palindromic Tree |
| 한 글자 update 후 palindrome 질의 | forward/reverse hash segment tree |
| 구간 안 palindrome substring 개수 | 문제 제한에 따라 offline, Eertree, DP 후보 |

중요한 차이는 "판정"과 "열거/집계"입니다. 판정만 있으면 hash나 radius가 훨씬 단순합니다.

## 2. Manacher Radius로 판정하기

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

## 3. Rolling Hash로 판정하기

Forward hash와 reversed string hash를 준비하면 substring과 그 reverse를 비교할 수 있습니다.

```cpp compile-check
#include <string>
#include <vector>
using namespace std;

struct PalindromeHash {
    static const long long MOD = 1000000007LL;
    static const long long BASE = 911382323LL;

    string s;
    vector<long long> power;
    vector<long long> forwardHash;
    vector<long long> reverseHash;

    explicit PalindromeHash(const string& input) : s(input) {
        int n = (int)s.size();
        string reversed(s.rbegin(), s.rend());
        power.assign(n + 1, 1);
        forwardHash.assign(n + 1, 0);
        reverseHash.assign(n + 1, 0);

        for (int i = 0; i < n; ++i) {
            power[i + 1] = power[i] * BASE % MOD;
            forwardHash[i + 1] = (forwardHash[i] * BASE + s[i]) % MOD;
            reverseHash[i + 1] = (reverseHash[i] * BASE + reversed[i]) % MOD;
        }
    }

    long long getHash(const vector<long long>& h, int left, int right) const {
        long long value = (h[right] - h[left] * power[right - left]) % MOD;
        if (value < 0) {
            value += MOD;
        }
        return value;
    }

    bool isPalindrome(int left, int right) const {
        int n = (int)s.size();
        int revLeft = n - right - 1;
        int revRight = n - left;
        return getHash(forwardHash, left, right + 1) == getHash(reverseHash, revLeft, revRight);
    }
};
```

Hash는 충돌 가능성이 있습니다. 중요한 판정이면 double hash를 쓰거나 Manacher처럼 deterministic한 방법을 선택합니다.

## 4. Eertree가 필요한 경우

Palindromic Tree는 prefix를 한 글자씩 추가하면서 새로 생기는 서로 다른 palindrome을 node로 만듭니다.

| 필요한 작업 | Eertree가 주는 값 |
| --- | --- |
| 서로 다른 palindrome 개수 | node count |
| 각 palindrome occurrence | suffix link 역순 누적 |
| prefix별 palindrome suffix | current longest suffix node |
| palindrome 종류별 DP | node graph DP |

구간 `[l, r]`이 palindrome인지 묻는 단순 판정에는 Eertree가 과합니다. 하지만 "어떤 palindrome들이 있는지"가 필요하면 가장 강합니다.

## 5. 구간 업데이트가 있는 경우

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

## 6. 구조 선택표

| 질의 형태 | 추천 |
| --- | --- |
| 정적 문자열, substring palindrome 판정 | Manacher |
| 정적 문자열, LCP/비교와 함께 판정 | rolling hash |
| 동적 point update + 판정 | hash segment tree |
| 모든 palindrome 종류/occurrence | Palindromic Tree |
| 가장 긴 palindrome substring | Manacher |
| 온라인 append 통계 | Palindromic Tree |

복잡한 구조를 고르기 전에, 문제에서 정말 palindrome을 "세는지" 아니면 "판정하는지"를 분리합니다.

## 7. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| Manacher 전처리 | `O(N)` |
| Manacher 판정 | `O(1)` |
| Hash 전처리 | `O(N)` |
| Hash 판정 | `O(1)` |
| Hash segment tree update/query | `O(log N)` |
| Eertree construction | `O(N * suffix fallback cost)` |

alphabet과 hash collision 정책에 따라 상수와 안정성이 달라집니다.

## 8. 자주 하는 실수

1. odd/even radius의 중심 index를 한 칸 밀린다.
2. substring hash의 reverse 좌표를 `n-1-r`, `n-1-l`로 뒤집지 않는다.
3. hash 하나만 쓰고 collision 가능성을 전혀 고려하지 않는다.
4. 판정 문제에 Eertree를 써서 구현량을 불필요하게 키운다.
5. Eertree occurrence를 suffix link 역순으로 누적하지 않는다.

## 9. 문제를 볼 때 체크할 조건

- 문자열이 정적인가, update가 있는가?
- 필요한 것은 palindrome 판정인가, 개수/종류 집계인가?
- 질의 수가 많아 `O(1)` 판정이 필요한가?
- hash collision이 허용되는 환경인가?
- 구간 query가 substring 자체인지, palindrome node 통계인지 확인했는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: palindrome query `/practice/...` 문제 필요 | Manacher radius 판정 | odd/even center |
| 표준 | TODO: dynamic palindrome hash `/practice/...` 문제 필요 | update와 구간 판정 | forward/reverse hash |
| 응용 | TODO: palindrome occurrence `/practice/...` 문제 필요 | Eertree occurrence | suffix link aggregation |
| 함정 | TODO: even palindrome off-by-one `/practice/...` 문제 필요 | 중심 좌표 검증 | radius indexing |
