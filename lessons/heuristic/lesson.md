# 휴리스틱 알고리즘

작업 배정, 광고판 배치, 배송 경로처럼 답의 후보가 너무 많을 때는 유효한 답 하나를 만든 뒤 점수를 개선해 갑니다. 이 레슨의 코드는 고정 배열과 공개 API를 기준으로 작성했습니다. 함수별 역할을 설명하는 골격과 그대로 실행할 수 있는 구현은 본문에서 구분합니다.

## 문서 구성

- [문제 모델링과 점수 함수](pages/modeling-and-scoring.md) - 휴리스틱이 필요한 상황, 상태 표현, 점수 함수 설계를 정리합니다.
- [초기해와 지역 탐색](pages/search-strategies.md) - 초기해 구성, 지역 탐색, 나쁜 이동 수용 전략을 다룹니다.
- [Beam Search와 시간 관리](pages/beam-and-time.md) - Beam Search, 무작위 재시도, 제한 시간 관리 방법을 정리합니다.
- [실험 로그와 개선 연산](pages/experiments-and-checklist.md) - 같은 입력에서 비교할 로그와 swap·reverse 구현을 다룹니다.
- [실전 예시: 광고판 도시 배치](pages/placement-and-repair.md) - `BILLCITY`를 따라가며 bitmask 상태 표현, 위치 평가식, 큰 destroy/repair, 부분 exact repair가 한 풀이 안에서 연결되는 흐름을 봅니다.
- [실전 예시: 배송 순서 개선](pages/ordering-route-improvement.md) - `ORDERING`을 따라가며 유효한 순열 초기해, 열린 경로의 2-opt 차분 계산, insertion과 작은 입력 exact 탐색을 연결합니다.
- [실전 예시: 31일 설치 일정 Beam Search](pages/aircontech-beam-search.md) - `AIRCONTECH`를 따라가며 다음 행동 상위 8개와 경로 상태 상위 32개를 남기는 두 단계 가지치기, 실제 점수와 탐색 평가값의 분리를 연결합니다.
