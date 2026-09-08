# Practice Set

Palindrome Structures 계열은 판정, 열거, 구간 DP를 따로 연습해야 합니다. 아직 적절한 h-contest 문제 링크가 없는 항목은 임의 ID를 만들지 않고, 이 페이지에 로컬 완결형 연습과 검증 기준을 둡니다.

## 대표 로컬 연습: 서로 다른 Palindrome Substring 개수

문자열 `S`가 주어졌을 때, `S`에 등장하는 서로 다른 non-empty palindrome substring의 개수를 출력합니다.

### 입력

```text
S
```

- `1 <= |S| <= 200000`
- `S`는 영어 소문자로만 이루어져 있습니다.

### 출력

```text
서로 다른 palindrome substring 개수
```

### 예시

```text
ababa
```

```text
5
```

`ababa`의 서로 다른 palindrome substring은 `a`, `b`, `aba`, `bab`, `ababa`입니다.

## 손으로 따라가는 Trace

Eertree는 두 root를 먼저 둡니다.

| node | 길이 | 의미 | suffix link |
| ---: | ---: | --- | --- |
| 0 | `-1` | odd root | 0 |
| 1 | `0` | even root | 0 |

`S = ababa`를 왼쪽부터 추가하면 새로 생기는 node는 아래처럼 하나씩만 늘어납니다.

| 위치 | 문자 | 추가 뒤 longest palindromic suffix | 새 node | distinct 개수 |
| ---: | --- | --- | --- | ---: |
| 0 | `a` | `a` | `a` | 1 |
| 1 | `b` | `b` | `b` | 2 |
| 2 | `a` | `aba` | `aba` | 3 |
| 3 | `b` | `bab` | `bab` | 4 |
| 4 | `a` | `ababa` | `ababa` | 5 |

이때 suffix link는 "가장 긴 proper palindromic suffix"로 이어집니다.

| palindrome | suffix link 대상 |
| --- | --- |
| `a` | even root |
| `b` | even root |
| `aba` | `a` |
| `bab` | `b` |
| `ababa` | `aba` |

답은 항상 `node count - 2`입니다. 두 root는 실제 substring이 아니므로 빼야 합니다.

## 구현 기준

```cpp
// https://h.readiz.com/learn/palindrome-structures/palindromic-tree의 PalindromicTree를 앞에 둔다.
#include <iostream>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    string s;
    cin >> s;

    PalindromicTree tree;
    for (char ch : s) {
        tree.addChar(ch);
    }
    cout << (tree.tree.size() - 2) << '\n';
}
```

## 검증용 Case

| 입력 | 정답 | 확인 포인트 |
| --- | ---: | --- |
| `a` | 1 | 길이 1 node의 suffix link는 even root |
| `aa` | 2 | `a`, `aa`가 서로 다른 palindrome |
| `aaaa` | 4 | 매 prefix에서 새 palindrome 하나가 생김 |
| `abcd` | 4 | 길이 1 palindrome만 존재 |
| `ababa` | 5 | suffix link가 `ababa -> aba -> a`로 이어짐 |
| `abacaba` | 7 | `a`, `b`, `c`, `aba`, `aca`, `bacab`, `abacaba` |

## Stress 기준

짧은 문자열에서는 brute force set과 비교합니다.

1. 길이 `1..10`, alphabet `{a,b,c}`에서 모든 substring을 잘라 palindrome인지 직접 검사합니다.
2. palindrome인 substring만 `set<string>`에 넣고 크기를 구합니다.
3. Eertree의 `distinctCount()`와 brute force set size가 항상 같은지 비교합니다.

이 stress를 통과하면 root 개수 제외, suffix link 후보 탐색, 새 node 생성 조건의 흔한 실수를 대부분 잡을 수 있습니다.
