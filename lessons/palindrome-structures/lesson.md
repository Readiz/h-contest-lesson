# Palindrome Structures

Palindrome Structures는 회문 substring을 판정, 열거, 집계, DP로 처리하는 문자열 구조 허브입니다. Manacher/rolling hash는 빠른 판정에 강하고, Palindromic Tree는 서로 다른 palindrome substring을 노드로 보존할 때 강하며, range DP는 구간 자체가 상태가 될 때 필요합니다.

이 허브는 회문 문제를 아래 네 질문으로 먼저 나눕니다.

1. substring이 palindrome인지 판정만 하면 되는가?
2. 서로 다른 palindrome substring을 모두 세거나 저장해야 하는가?
3. 구간 안의 회문 통계를 질의해야 하는가?
4. suffix 구조와 palindrome 구조를 함께 써야 하는가?

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: String Matching, Suffix and Periodicity Structures, Dynamic Programming
- 함께 보면 좋은 레슨: Suffix and Periodicity Structures, Rolling Hash, Palindromic Tree
- 다음에 볼 레슨: Advanced String DP, String Period Queries

## 1. 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 서로 다른 palindrome substring 개수와 occurrence를 관리한다 | [Palindromic Tree](pages/palindromic-tree.md) |
| substring palindrome 판정을 많이 한다 | [Palindrome Query Structures](pages/palindrome-query-structures.md) |
| 구간 자체를 상태로 두고 palindrome partition/count를 계산한다 | [Palindrome Range DP](pages/palindrome-range-dp.md) |
| suffix 구조와 palindrome 조건을 함께 써야 한다 | [Suffix and Palindrome Applications](pages/suffix-palindrome-applications.md) |
| Manacher, hash, Eertree, DP 중 무엇을 고를지 헷갈린다 | [Palindrome Model Map](pages/palindrome-model-map.md) |

## 2. 판정과 집계의 차이

| 목표 | 보통 맞는 구조 |
| --- | --- |
| `s[l..r]`가 palindrome인지 빠르게 판정 | Manacher radius, rolling hash |
| 모든 서로 다른 palindrome substring 개수 | Palindromic Tree |
| prefix 추가마다 새 palindrome 수 | Palindromic Tree |
| 구간별 palindrome partition/count | range DP, precomputed palindrome table |
| suffix/prefix와 palindrome 조건 결합 | suffix structure + palindrome helper |

판정만 필요한 문제에 Eertree를 쓰면 과한 경우가 많습니다. 반대로 서로 다른 palindrome을 노드로 저장해야 하면 hash만으로는 집계가 복잡해집니다.

## 3. 공개 상태

하위 페이지는 기존 구현과 설명을 보존합니다. [Practice Set](pages/practice-set.md)은 Eertree 기반 distinct palindrome count 로컬 연습과 trace를 대표 구현 흐름으로 제공합니다.
