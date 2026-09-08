# Suffix and Periodicity Structures

Suffix and Periodicity Structures는 suffix array, suffix automaton, suffix tree, runs, border automaton, period query를 하나의 문자열 구조 트랙으로 묶는 허브입니다. 이 주제들은 모두 "문자열의 모든 suffix/substr/period 정보를 어떻게 압축해서 질의할 것인가"라는 같은 문제군에 속합니다.

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| suffix 순서와 LCP로 패턴 검색·반복·서로 다른 부분 문자열을 처리한다 | [Suffix Array와 LCP](pages/suffix-array-lcp.md) |
| substring 존재/개수/등장 횟수를 상태로 세고 싶다 | [Suffix Automaton](pages/suffix-automaton.md) |
| SAM 위 DP, k번째 substring, 여러 응용을 다룬다 | [Suffix Automaton Applications](pages/suffix-automaton-applications.md) |
| 여러 문자열의 공통 substring을 한 구조로 관리한다 | [Generalized Suffix Automaton](pages/generalized-suffix-automaton.md) |
| explicit suffix tree edge와 Ukkonen construction이 필요하다 | [Suffix Tree and Ukkonen](pages/suffix-tree-ukkonen.md) |
| 주기, run, 반복 구조가 문제의 핵심이다 | [Runs and Periodicity](pages/runs-periodicity.md) |
| prefix-function 기반 상태 전이가 필요하다 | [Border Automaton](pages/border-automaton.md) |
| period query를 여러 번 처리해야 한다 | [String Period Query Applications](pages/string-period-query-applications.md) |

## 연습

문자열 구조를 비교하는 로컬 연습은 [Practice Set](pages/practice-set.md)에서 진행합니다.

## 표현과 인덱스

Alphabet 크기에 따라 transition을 배열로 둘지 정합니다. 여러 문자열을 붙이면 원문에 없는 separator를 쓰고, occurrence의 개수만 필요한지 위치까지 필요한지 구분합니다.

LCP 배열은 `LCP(sa[i], sa[i+1])`와 `LCP(sa[i-1], sa[i])` 중 어느 정의를 쓰는지 구현 전체에서 맞춥니다. SAM의 clone은 생성 시 실제 occurrence를 새로 만든 것이 아니므로 일반 상태와 같은 초기 count를 주지 않습니다. Border가 있다는 것과 문자열 전체가 그 길이로 반복된다는 조건도 구분해야 합니다.
