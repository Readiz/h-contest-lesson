# Suffix and Periodicity Structures

Suffix and Periodicity Structures는 suffix array, suffix automaton, suffix tree, runs, border automaton, period query를 하나의 문자열 구조 트랙으로 묶는 허브입니다. 이 주제들은 모두 "문자열의 모든 suffix/substr/period 정보를 어떻게 압축해서 질의할 것인가"라는 같은 문제군에 속합니다.

개별 자료구조 이름보다 먼저 아래 질문을 결정해야 합니다.

1. suffix를 사전순으로 정렬해야 하는가?
2. 모든 substring을 상태 DAG로 세거나 탐색해야 하는가?
3. 여러 문자열을 동시에 처리해야 하는가?
4. 반복 주기, border, run을 질의해야 하는가?
5. suffix tree 수준의 explicit edge 구조가 필요한가?

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: KMP/Z/Rolling Hash, Trie/Aho-Corasick, Sorting, Sparse Table/RMQ
- 함께 보면 좋은 레슨: Lyndon Factorization, Palindrome Structures, String Matching
- 다음에 볼 레슨: Palindrome Structures, String Period Query Applications, Advanced String DP

## 1. 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| suffix의 사전순 순서와 LCP가 필요하다 | [Suffix Array and LCP](pages/suffix-array-lcp.md) |
| suffix array로 반복 부분 문자열, distinct substring, pattern search를 처리한다 | [Suffix Array Applications](pages/suffix-array-applications.md) |
| substring 존재/개수/등장 횟수를 상태로 세고 싶다 | [Suffix Automaton](pages/suffix-automaton.md) |
| SAM 위 DP, k번째 substring, 여러 응용을 다룬다 | [Suffix Automaton Applications](pages/suffix-automaton-applications.md) |
| 여러 문자열의 공통 substring을 한 구조로 관리한다 | [Generalized Suffix Automaton](pages/generalized-suffix-automaton.md) |
| explicit suffix tree edge와 Ukkonen construction이 필요하다 | [Suffix Tree and Ukkonen](pages/suffix-tree-ukkonen.md) |
| 주기, run, 반복 구조가 문제의 핵심이다 | [Runs and Periodicity](pages/runs-periodicity.md) |
| prefix-function 기반 상태 전이가 필요하다 | [Border Automaton](pages/border-automaton.md) |
| period query를 여러 번 처리해야 한다 | [String Period Query Applications](pages/string-period-query-applications.md) |
| 구조 선택이 헷갈린다 | [Suffix Model Map](pages/suffix-model-map.md) |

## 2. 자료구조별 강점

| 구조 | 강점 | 약점 |
| --- | --- | --- |
| Suffix Array + LCP | 정렬 순서, LCP RMQ, offline pattern search | dynamic update에 약함 |
| Suffix Automaton | substring 상태 압축, count/DP | 사전순/구간 위치 복원이 별도 작업 |
| Generalized SAM | 여러 문자열 공통 substring | source mask/count 관리가 중요 |
| Suffix Tree | explicit edge와 깊이 기반 탐색 | 구현 난도가 높음 |
| Runs/Periodicity | 반복 구조와 최소 주기 | 기본 matching과 관점이 다름 |
| Border Automaton | prefix-function 상태 전이 | suffix 전체 정렬 문제에는 맞지 않음 |

## 3. 공개 상태

하위 페이지들은 기존 구현과 설명을 보존합니다. 아직 실제 practice link가 부족한 항목은 [Practice Set](pages/practice-set.md)에 TODO로 모아 둡니다.
