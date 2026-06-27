# Practice Set

Palindrome Structures 계열은 판정, 열거, 구간 DP를 따로 연습해야 합니다. 아직 적절한 h-contest 문제 링크가 없는 항목은 임의 ID를 만들지 않고 `TODO`로 둡니다.

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: palindrome query `/practice/...` 문제 필요 | Manacher 또는 hash 판정 | radius |
| 입문 | TODO: distinct palindrome count `/practice/...` 문제 필요 | Eertree 노드 개수 | palindromic tree |
| 표준 | TODO: online palindrome statistics `/practice/...` 문제 필요 | suffix link 누적 | Eertree count |
| 표준 | TODO: palindrome partition `/practice/...` 문제 필요 | range DP | palindrome table |
| 응용 | TODO: suffix palindrome application `/practice/...` 문제 필요 | suffix 구조와 회문 보조 정보 결합 | suffix + palindrome |

## 완료 기준

- 판정/열거/집계 중 어떤 문제인지 먼저 적습니다.
- Manacher나 hash의 index 변환을 작은 문자열로 검증합니다.
- Eertree occurrence count는 suffix link 역순 누적 후 사용합니다.
- DP는 `O(N^2)` 가능 여부를 제한에서 확인합니다.
