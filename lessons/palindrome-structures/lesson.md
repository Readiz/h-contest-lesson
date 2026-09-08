# Palindrome Structures

Palindrome Structures는 회문 substring을 판정, 열거, 집계, DP로 처리하는 문자열 구조 허브입니다. Manacher/rolling hash는 빠른 판정에 강하고, Palindromic Tree는 서로 다른 palindrome substring을 노드로 보존할 때 강하며, range DP는 구간 자체가 상태가 될 때 필요합니다.

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 서로 다른 palindrome substring 개수와 occurrence를 관리한다 | [Palindromic Tree](pages/palindromic-tree.md) |
| substring palindrome 판정을 많이 한다 | [Palindrome Query Structures](pages/palindrome-query-structures.md) |
| 구간 자체를 상태로 두고 palindrome partition/count를 계산한다 | [Palindrome Range DP](pages/palindrome-range-dp.md) |
| suffix 구조와 palindrome 조건을 함께 써야 한다 | [Suffix and Palindrome Applications](pages/suffix-palindrome-applications.md) |

## 표현 범위

정적 문자열의 판정은 Manacher나 rolling hash로 처리하고, 한 글자 갱신이 있으면 정방향·역방향 hash를 Segment Tree로 관리합니다. Hash는 충돌 가능성이 있으므로 판정의 정확성 요구를 먼저 정합니다. 서로 다른 회문과 occurrence는 Eertree, 구간 자체를 상태로 쓰는 문제는 DP 페이지로 이어집니다.

## 연습

[로컬 연습](pages/practice-set.md)에서 입력과 검증 기준을 확인합니다.
