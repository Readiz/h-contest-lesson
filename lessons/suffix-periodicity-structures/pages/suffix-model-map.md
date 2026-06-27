# Suffix Model Map

문자열 고급 구조는 이름이 많지만 선택 기준은 비교적 명확합니다. 먼저 "정렬", "상태 압축", "반복 구조" 중 무엇이 필요한지 나눕니다.

## 1. 세 축

| 축 | 필요한 정보 | 대표 구조 |
| --- | --- | --- |
| Suffix ordering | suffix들의 사전순 순서와 인접 LCP | Suffix Array + LCP |
| Substring automaton | 모든 substring의 존재, 개수, 등장 횟수 | Suffix Automaton |
| Periodicity | border, period, run, 반복 구간 | Prefix function, Runs, Border Automaton |

Suffix Tree는 suffix ordering과 substring traversal을 모두 explicit edge 구조로 담지만, 구현 비용이 큽니다. 대회에서는 suffix array나 SAM으로 충분한지 먼저 봅니다.

## 2. 문제 문장별 선택

| 문제 문장 | 후보 |
| --- | --- |
| "사전순 k번째 suffix/substr" | suffix array, SAM DP |
| "서로 다른 부분 문자열 개수" | suffix array LCP sum, SAM state contribution |
| "두 suffix의 LCP를 여러 번" | suffix array + LCP RMQ |
| "여러 문자열의 최장 공통 부분 문자열" | generalized SAM, suffix array with separators |
| "문자열의 주기/최소 period" | prefix function, runs |
| "prefix가 상태처럼 전이된다" | border automaton |

## 3. 구현 전에 확인할 것

- alphabet 크기가 작은가, transition을 array로 둘 수 있는가?
- 여러 문자열을 붙일 때 separator가 안전한가?
- LCP query가 필요한가, 아니면 substring 존재만 필요한가?
- 모든 occurrence 위치가 필요한가, count만 필요한가?
- period 조건이 exact period인지, border 기반 후보인지 구분했는가?

## 4. 자주 하는 실수

1. suffix array의 LCP index를 `lcp[i] = LCP(sa[i], sa[i+1])`와 `LCP(sa[i-1], sa[i])`로 섞는다.
2. SAM clone 상태의 count를 그대로 occurrence count로 쓴다.
3. 여러 문자열을 붙일 때 separator가 원문 alphabet과 충돌한다.
4. period와 border를 같은 말로 처리한다.
5. suffix tree가 필요한 문제라고 생각하고 더 단순한 suffix array/SAM 풀이를 놓친다.
