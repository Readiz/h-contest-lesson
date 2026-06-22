# Lyndon Factorization

Lyndon Factorization은 문자열을 사전순으로 엄격히 작은 Lyndon word들의 비증가열로 분해하는 기법입니다. Duval algorithm을 쓰면 전체 문자열을 선형 시간에 분해할 수 있고, 최소 회전이나 문자열 주기 분석에도 연결됩니다.

이 레슨은 Suffix와 Palindrome 응용 이후에 보는 문자열 분해 관점입니다.

1. Lyndon word의 정의를 이해한다.
2. Duval algorithm으로 문자열을 선형 시간에 분해한다.
3. 최소 표현, 주기성, suffix 구조와의 차이를 구분한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 문자열 비교, Suffix Array/Suffix Automaton 감각
- 함께 보면 좋은 레슨: Suffix와 Palindrome 응용, 문자열 매칭, Suffix Array와 LCP
- 다음에 볼 레슨: Booth algorithm, suffix tree, runs theorem

## 1. Lyndon Word

문자열 `w`가 Lyndon word라는 것은, `w`의 모든 non-empty proper suffix보다 `w`가 사전순으로 작다는 뜻입니다.

```text
w < every proper suffix of w
```

동치로, `w`는 자신의 모든 non-trivial rotation보다 사전순으로 작습니다. 그래서 Lyndon word는 최소 회전과도 연결됩니다.

## 2. Chen-Fox-Lyndon 분해

모든 문자열은 Lyndon word들의 sequence로 유일하게 분해됩니다.

```text
s = w1 w2 ... wk
w1 >= w2 >= ... >= wk
```

여기서 비교는 사전순입니다. 이 유일한 분해를 Lyndon factorization이라고 합니다.

## 3. Duval Algorithm

Duval algorithm은 현재 위치에서 시작하는 가장 긴 Lyndon factor를 찾고, 같은 factor가 반복되면 한 번에 여러 개를 내보냅니다.

```cpp compile-check
#include <string>
#include <utility>
#include <vector>
using namespace std;

vector<pair<int, int>> lyndonFactorization(const string& s) {
    int n = (int)s.size();
    vector<pair<int, int>> factors;
    int i = 0;

    while (i < n) {
        int j = i + 1;
        int k = i;

        while (j < n && s[k] <= s[j]) {
            if (s[k] < s[j]) {
                k = i;
            } else {
                ++k;
            }
            ++j;
        }

        int length = j - k;
        while (i <= k) {
            factors.push_back({i, length});
            i += length;
        }
    }

    return factors;
}
```

반환값 `{start, length}`는 각 Lyndon factor의 위치와 길이입니다.

## 4. 동작 예시

문자열이 아래와 같다고 합시다.

```text
ababbab
```

Duval algorithm은 비교 포인터 `i, j, k`를 움직이며 현재 후보보다 큰 문자가 나오면 `k`를 다시 `i`로 돌립니다. 같은 문자가 이어지면 `k`만 전진합니다. 후보가 깨지는 순간 `j - k`가 factor 길이가 됩니다.

핵심은 이미 비교한 문자를 다시 많이 보지 않는다는 점입니다. 그래서 전체 시간은 `O(N)`입니다.

## 5. 최소 회전

문자열의 lexicographically minimum rotation을 찾을 때도 비슷한 아이디어를 씁니다. 가장 단순한 방식은 `s+s`에 대해 Duval을 적용하고 시작 위치가 `n`보다 작은 첫 factor 후보를 찾는 것입니다.

```cpp compile-check
#include <string>
using namespace std;

int minimumRotationIndex(const string& s) {
    string doubled = s + s;
    int n = (int)s.size();
    int i = 0;
    int answer = 0;

    while (i < n) {
        answer = i;
        int j = i + 1;
        int k = i;
        while (j < 2 * n && doubled[k] <= doubled[j]) {
            if (doubled[k] < doubled[j]) {
                k = i;
            } else {
                ++k;
            }
            ++j;
        }
        while (i <= k) {
            i += j - k;
        }
    }

    return answer;
}
```

문자열이 모두 같은 문자라면 여러 회전이 같은 최소값입니다. 이 구현은 그중 하나를 반환합니다.

## 6. Suffix 구조와 차이

| 목표 | 도구 |
| --- | --- |
| 모든 suffix의 정렬 순서 | Suffix Array |
| 모든 substring 상태 압축 | Suffix Automaton |
| palindrome substring 보존 | Palindromic Tree |
| 문자열을 Lyndon word로 분해 | Duval algorithm |
| 최소 회전 | Duval/Booth |

Lyndon factorization은 suffix index라기보다 문자열 자체의 분해입니다. 반복 구조, 최소 표현, 사전순 분할이 핵심일 때 사용합니다.

## 7. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| Lyndon factorization | `O(N)` | `O(number of factors)` |
| minimum rotation | `O(N)` | `O(N)` 또는 index view |
| 모든 factor 출력 | `O(number of factors)` | - |

`s+s`를 실제로 만들지 않고 modulo index로 처리하면 minimum rotation 메모리를 줄일 수 있습니다.

## 8. 자주 하는 실수

1. `s[k] <= s[j]` 조건을 `<`로 써서 같은 문자 반복을 깨뜨린다.
2. factor 길이 `j-k`를 `j-i`로 착각한다.
3. Lyndon factor들이 사전순 비증가라는 조건을 반대로 기억한다.
4. minimum rotation에서 `s+s` 전체 factor를 끝까지 보며 시작점 `>= n`을 반환한다.
5. empty string 처리를 빼먹는다.

## 9. 문제를 볼 때 체크할 조건

- 문자열 분해가 필요한가, suffix 정렬이 필요한가?
- 최소 회전 또는 circular string 비교인가?
- 같은 회전이 여러 개일 때 어떤 index를 요구하는가?
- factor 자체가 필요한가, 개수나 길이만 필요한가?
- alphabet 비교가 일반 문자 순서와 같은가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: Lyndon factorization 출력 `/practice/...` 문제 필요 | Duval algorithm 구현 | Lyndon word |
| 표준 | TODO: 최소 회전 `/practice/...` 문제 필요 | `s+s`와 Duval/Booth 연결 | minimum rotation |
| 응용 | TODO: 문자열 분해 기반 비교 `/practice/...` 문제 필요 | factor sequence 활용 | lexicographic decomposition |
| 함정 | TODO: 반복 문자 circular string `/practice/...` 문제 필요 | 동률 회전 처리 | periodic string |
