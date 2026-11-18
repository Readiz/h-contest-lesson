# 휴리스틱 알고리즘

답 하나를 만든 뒤 일부를 바꾸며 비용을 줄이거나 점수를 높입니다. [배송 순서 개선](pages/ordering-route-improvement.md)은 유효한 순열부터 시작해 거리 계산과 2-opt까지 직접 실행할 수 있는 첫 사례입니다.

상태에는 제출할 답과 계산을 빠르게 하는 보조 값을 구분해 둡니다. ORDERING에서 제출할 것은 `order[]`이고, 현재 경로 비용은 그 순열로 다시 계산할 수 있는 값입니다. 차분 평가를 추가할 때도 전체 재계산을 남겨 두어 두 결과를 대조합니다.

탐색 중의 후보 선택 기준과 최종 점수는 다를 수 있습니다. AIRCONTECH에서는 미래 수익을 예상해 후보를 남기지만, 제출할 일정은 실제 이동·설치 규칙으로 다시 평가합니다. 탐색 중 제약 위반을 허용한 경우에도 최종 답의 유효성은 따로 확인합니다.

정렬·난수·배열 복사는 [공통 코드](https://h.readiz.com/learn/cpp-common-library)를 사용합니다. 문제별 코드에서 필요한 블록과 배열 상한을 맞춥니다.

## 본문

1. [배송 순서 개선](pages/ordering-route-improvement.md): 열린 경로의 유효한 초기해, 2-opt 차분과 완성 구현.
2. [Testing과 Stress Test](https://h.readiz.com/learn/testing-and-stress): 차분을 전체 비용 재계산과 대조하고 복구·재현성을 확인.
3. [초기해와 지역 탐색](pages/search-strategies.md): 지역 최적 반례에서 출발해 ORDERING에 SA를 붙이고 후보 수·비용·실행 시간을 비교.
4. [광고판 도시 배치](pages/placement-and-repair.md): bitmask 점유 검사, 위치 평가와 destroy/repair.
5. [31일 설치 일정 Beam Search](pages/aircontech-beam-search.md): 행동 후보와 경로 후보를 따로 줄이고 실제 수익으로 일정을 선택.
6. [배정 문제의 지역 탐색과 SA](https://h.readiz.com/learn/assignment-local-search): SCHEDULX의 최대 부하 차분, hill climbing이 멈추는 예, 시작 온도와 수락률 실험.
7. [채점기 상태를 따라 그리며 행동하기](https://h.readiz.com/learn/observe-and-act): MINEEXPLORE에서 내 호출 기록으로 채점기 상태를 따라 그리고, 계획과 행동을 나눠 이동당 이득으로 목표를 선택.
8. [배정과 경로가 결합된 문제](https://h.readiz.com/learn/assignment-with-routes): TAXIASSIGN에서 담당자와 삽입 위치를 함께 고르는 이웃과 최대 이동 거리의 차분.
9. [격자 배치 문제](https://h.readiz.com/learn/placement-search): LANDINGX에서 탐욕, 국소 이동, destroy/repair를 같은 후보 검사 수로 비교.
10. [특수한 점수식 읽기](https://h.readiz.com/learn/reading-the-score): ENTROPY2D에서 채점식을 내 코드로 재현해 대조하고, 축별 분리에서 O(1) 차분식을 만들어 풀이로 옮김.
11. [입력이 클 때](https://h.readiz.com/learn/large-input-search): COUPANG1에서 연산 수 예산을 먼저 계산하고, 좌표 칸으로 후보를 줄여 남은 시간을 배분.
12. [보이는 만큼만 아는 문제](https://h.readiz.com/learn/explore-unknown-map): ROBOTCLEAN에서 스캔과 이동 결과로 지도와 자세를 그려 가며, 스캔 비용과 헛걸음 비용의 균형을 실측.
