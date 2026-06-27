# Practice Set

Polynomial and Recurrence Algorithms 계열은 모델링 실수가 많으므로 작은 naive 구현과 비교하는 연습이 중요합니다. 아직 적절한 h-contest 문제 링크가 없는 항목은 임의 ID를 만들지 않고 `TODO`로 둡니다.

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: polynomial multiplication `/practice/...` 문제 필요 | NTT 입출력과 결과 길이 처리 | convolution |
| 입문 | TODO: polynomial inverse `/practice/...` 문제 필요 | FPS inverse와 truncate | Newton iteration |
| 표준 | TODO: multipoint evaluation `/practice/...` 문제 필요 | subproduct tree | polynomial remainder |
| 표준 | TODO: interpolation `/practice/...` 문제 필요 | Lagrange basis | interpolation |
| 표준 | TODO: linear recurrence nth term `/practice/...` 문제 필요 | Kitamasa 또는 Bostan-Mori | recurrence |
| 응용 | TODO: generating function coefficient `/practice/...` 문제 필요 | rational form 계수 추출 | Bostan-Mori |
| 심화 | TODO: Berlekamp-Massey `/practice/...` 문제 필요 | 앞 항에서 최소 점화식 찾기 | discrepancy |

## 완료 기준

- 작은 차수 naive polynomial 연산과 비교합니다.
- mod/root/primitive root 조건을 명시합니다.
- FPS 연산의 상수항 조건을 확인합니다.
- BM 결과는 holdout 항으로 검증합니다.
- n번째 항 알고리즘은 0-index/1-index를 고정합니다.
