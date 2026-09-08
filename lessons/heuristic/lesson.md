# 휴리스틱 알고리즘

답 하나를 만든 뒤 일부를 바꾸며 비용을 줄이거나 점수를 높입니다. [배송 순서 개선](pages/ordering-route-improvement.md)은 유효한 순열부터 시작해 거리 계산과 2-opt까지 직접 실행할 수 있는 첫 사례입니다.

상태에는 제출할 답과 계산을 빠르게 하는 보조 값을 구분해 둡니다. ORDERING에서 제출할 것은 `order[]`이고, 현재 경로 비용은 그 순열로 다시 계산할 수 있는 값입니다. 차분 평가를 추가할 때도 전체 재계산을 남겨 두어 두 결과를 대조합니다.

탐색 중의 후보 선택 기준과 최종 점수는 다를 수 있습니다. AIRCONTECH에서는 미래 수익을 예상해 후보를 남기지만, 제출할 일정은 실제 이동·설치 규칙으로 다시 평가합니다. 탐색 중 제약 위반을 허용한 경우에도 최종 답의 유효성은 따로 확인합니다.

정렬·난수·배열 복사는 [공통 코드](https://h.readiz.com/learn/cpp-contest-basics)를 사용합니다. 문제별 코드에서 필요한 블록과 배열 상한을 맞춥니다.

## 본문

- [배송 순서 개선](pages/ordering-route-improvement.md): 열린 경로의 유효한 초기해, 2-opt 차분과 완성 구현.
- [초기해와 지역 탐색](pages/search-strategies.md): 지역 최적, 나쁜 이동의 수락, 재시도와 실험 비교.
- [광고판 도시 배치](pages/placement-and-repair.md): bitmask 점유 검사, 위치 평가와 destroy/repair.
- [31일 설치 일정 Beam Search](pages/aircontech-beam-search.md): 행동 후보와 경로 후보를 따로 줄이고 실제 수익으로 일정을 선택.
