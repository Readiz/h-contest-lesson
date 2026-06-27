# Practice Set

Suffix and Periodicity Structures 계열은 같은 문제를 suffix array와 SAM 양쪽으로 풀어 보는 연습이 좋습니다. 아직 적절한 h-contest 문제 링크가 없는 항목은 임의 ID를 만들지 않고 `TODO`로 둡니다.

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: suffix array pattern search `/practice/...` 문제 필요 | suffix 정렬과 lower_bound | suffix array |
| 입문 | TODO: distinct substring count `/practice/...` 문제 필요 | LCP sum 또는 SAM contribution | LCP, SAM |
| 표준 | TODO: repeated substring `/practice/...` 문제 필요 | LCP maximum과 occurrence 조건 | LCP RMQ |
| 표준 | TODO: longest common substring `/practice/...` 문제 필요 | generalized SAM 또는 separator SA | source mask |
| 응용 | TODO: period query `/practice/...` 문제 필요 | prefix function, border, runs | period |
| 심화 | TODO: suffix tree traversal `/practice/...` 문제 필요 | explicit edge와 depth | Ukkonen |

## 완료 기준

- suffix array와 LCP index 정의를 고정합니다.
- SAM occurrence count는 suffix link 역순 누적 뒤에 사용합니다.
- 여러 문자열을 합칠 때 separator 충돌을 막습니다.
- period query에서는 inclusive/exclusive 구간을 통일합니다.
- naive substring set과 비교하는 작은 stress test를 준비합니다.
