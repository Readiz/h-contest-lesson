# 적용 사례 모음: 경로 개선·SA·배치 수리·일정 빔

이 모음은 [방법론 강의](https://h.readiz.com/learn/heuristic)의 기법을 실제 문제 하나에 적용해 본 예 4개입니다. 새 기법을 처음 가르치는 곳이 아니라, 방법론 강의에서 배운 기법이 문제의 계약과 채점 안에서 어떻게 쓰이는지를 따라가는 곳입니다. 방법론 강의를 먼저 읽고 이 쪽들로 오면 각 쪽이 어느 기법의 예인지 바로 알아볼 수 있고, 반대로 이 쪽들을 읽다가 기법 자체가 궁금하면 아래 표의 강의로 돌아가면 됩니다.

쪽의 본문은 문제 하나를 끝까지 따라가므로 문제 이름과 제출 형식이 그대로 나옵니다. 방법론 강의의 연습용 문제 틀과 달리 여기의 수치는 해당 문제의 공개 채점기로 잰 값입니다.

## 쪽마다 보여 주는 기법

| 쪽 | 문제 | 보여 주는 기법 | 방법론 강의 |
| --- | --- | --- | --- |
| [배송 순서 개선](pages/ordering-route-improvement.md) | ORDERING | 유효한 번호 순서 기준선, nearest neighbor 초기해, 열린 경로 2-opt의 경계 간선 차분 | [초기해 만들기](https://h.readiz.com/learn/construction-heuristics), [근방 설계와 차분 평가](https://h.readiz.com/learn/neighborhood-and-delta) |
| [초기해와 지역 탐색](pages/search-strategies.md) | ORDERING | ORDERING에 붙이는 SA 구현, 같은 후보 수의 단계별 비용 비교 | [언덕 오르기와 담금질](https://h.readiz.com/learn/hill-climbing-and-annealing) |
| [광고판 도시 배치](pages/placement-and-repair.md) | BILLCITY | 행 bitmask 점유 검사, 위치 평가식, 큰 제거 뒤 다시 채우기 | [크게 부수고 다시 짓기](https://h.readiz.com/learn/destroy-and-repair) |
| [31일 설치 일정 Beam Search](pages/aircontech-beam-search.md) | AIRCONTECH | 행동 후보와 경로 후보를 따로 줄이는 두 단계 가지치기, 탐색 평가값과 실제 점수의 분리 | [빔 서치와 평가 함수](https://h.readiz.com/learn/beam-search) |

## 각 쪽을 읽을 때 볼 것

- 문제의 계약에서 상태·행동·점수를 어떻게 뽑았는지: [문제를 상태·행동·점수로 옮기기](https://h.readiz.com/learn/problem-modeling)의 표와 같은 순서로 읽으면 됩니다.
- 내 점수 계산이 채점기의 값과 맞는지, 차분 계산이 전체 재계산과 맞는지를 어디서 확인하는지.
- 개선이 있었다는 근거로 어떤 비교(같은 TC, 비용, 후보 수, 실행 시간)를 썼는지: [실험과 튜닝](https://h.readiz.com/learn/experiments-and-tuning)의 기준으로 보면 여러 시드로 짝지어 본 비교와 한 번의 측정을 구분할 수 있습니다.

## 읽는 순서

1. [배송 순서 개선](pages/ordering-route-improvement.md): 열린 경로의 유효한 초기해와 2-opt를 직접 실행할 수 있는 코드까지 따라갑니다. 나머지 쪽의 바탕입니다.
2. [초기해와 지역 탐색](pages/search-strategies.md): 같은 문제에 SA를 붙이고 후보 수·비용·실행 시간을 비교합니다.
3. [광고판 도시 배치](pages/placement-and-repair.md): 작은 이동으로 풀리지 않는 배치를 부수고 다시 채웁니다.
4. [31일 설치 일정 Beam Search](pages/aircontech-beam-search.md): 순차 결정 문제에서 상태를 폭 만큼만 남깁니다.

차분을 전체 재계산과 대조하는 방법은 [Testing과 Stress Test](https://h.readiz.com/learn/testing-and-stress), 정렬·난수·배열 복사 같은 공통 코드는 [공통 코드](https://h.readiz.com/learn/cpp-common-library)를 봅니다.

같은 방식의 다른 적용 사례는 [배정 문제의 지역 탐색과 SA](https://h.readiz.com/learn/assignment-local-search), [택시 배정](https://h.readiz.com/learn/assignment-with-routes), [격자 배치 문제](https://h.readiz.com/learn/placement-search), [입력이 클 때](https://h.readiz.com/learn/large-input-search) 같은 문제별 강의에 있습니다.
