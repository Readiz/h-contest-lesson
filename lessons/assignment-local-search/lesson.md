# 배정 문제의 지역 탐색과 SA

[SCHEDULX](/practice/SCHEDULX)는 작업을 기계에 배정해 가장 늦게 끝나는 기계의 시간을 줄이는 문제입니다. [배송 순서 개선](https://h.readiz.com/learn/heuristic-case-studies/ordering-route-improvement)의 2-opt와 [초기해와 지역 탐색](https://h.readiz.com/learn/heuristic-case-studies/search-strategies)의 SA를 같은 틀로 다시 쓰되, 이번에는 점수가 합이 아니라 **최댓값**이고 상태가 순열이 아니라 **작업 → 기계 배정**입니다. 이 두 차이가 차분 평가와 온도 설정을 어떻게 바꾸는지를 실제 점수로 확인합니다.

> **이 사례가 보여 주는 기법:** [근방 설계와 차분 평가](https://h.readiz.com/learn/neighborhood-and-delta)의 최댓값 점수의 차분 평가, [언덕 오르기와 담금질](https://h.readiz.com/learn/hill-climbing-and-annealing)의 시작 온도 설정. 일반 원리는 그 강의에서, 이 문제에 맞춘 구현과 측정은 아래에서 봅니다.

위 두 방법론 강의와 [Testing과 Stress Test](https://h.readiz.com/learn/testing-and-stress)를 읽었다고 가정합니다. 난수는 [공통 코드의 `random` 블록](https://h.readiz.com/learn/cpp-common-library)을 먼저 붙여 씁니다.

## 이 강의에서 다루는 것

- 점수가 합이 아니라 최댓값일 때, 이동 한 번의 새 최댓값을 어떻게 차분으로 구하는지.
- 작업 → 기계 배정 상태와 이동·교환 이웃을 `rebuild()` 전체 재계산과 대조하는 검사.
- hill climbing이 멈추는 작은 예를 손으로 따라가고 SA로 빠져나오는 과정.
- 시작 온도와 평균 부하 항(부하 합의 변화를 탐색용 에너지에 더하는 항)을 점수로 정하는 실험, 최댓값 차분을 틀렸을 때의 실패.

## 단계별 결과

SCHEDULX 공개 TC 6개의 비용 합입니다(작을수록 좋습니다). TC별 값과 시간, 측정 조건은 [실측과 실패 사례](pages/experiments-and-failures.md)에 있습니다.

<!-- check:hub-summary -->
| 방식 | 합 ↓ |
| --- | ---: |
| 작업 번호 % 기계 수 | 510045 |
| 탐욕 초기해 | 263314 |
| hill climbing, 실제 점수만 | 241494 |
| hill climbing, 평균 부하 항 포함 | 238884 |
| SA, 실제 점수만 | 252177 |
| SA, 평균 부하 항 포함 | 235380 |

## 본문

1. [문제 계약과 기준선](pages/contract-and-baseline.md): 제출 함수의 계약, 작업 → 기계 배정 상태, 번호 순 기준선과 탐욕 초기해.
2. [풀이: 이웃과 차분 평가, hill climbing과 SA](pages/solution.md): 이동·교환의 최댓값 차분, hill climbing이 14에서 멈추는 손계산, 평균 부하 항을 더한 SA.
3. [실측과 실패 사례](pages/experiments-and-failures.md): 제출 진입 함수와 단계별 측정, 시작 온도·평균 부하 가중치 실험, 잘못된 최댓값 차분의 실패.

## 연습: SCHEDULX

[SCHEDULX](/practice/SCHEDULX)에서 다음을 직접 해 봅니다.

1. 기준선과 탐욕 초기해를 제출해 점수를 기록합니다. 이 강의의 표(510045, 263314)와 문제 화면의 점수가 같은 TC 합인지 먼저 확인합니다.
2. 본문 블록을 붙여 SA를 제출합니다. 후보 수를 500,000, 1,000,000, 2,000,000으로 바꿔 점수와 시간을 기록하고, 4초 제한까지 남는 시간을 확인합니다.
3. `factor`를 0.03, 0.1, 0.3, 1, 3으로 바꿔 보고, 직접 만든 입력과 공개 TC 양쪽에서 solver seed 5개 이상의 중앙값을 비교합니다. 한 번의 점수만으로 선택하지 않습니다.
4. 새 이웃을 하나 추가합니다(예: 부하가 가장 큰 기계의 작업만 이동 대상으로 고르기). 추가 후에도 `rebuild()`와의 일치, 범위, 같은 seed 재현성이 유지되는지 먼저 검사한 뒤 점수를 비교합니다.

확인 기준: 모든 TC가 유효하고, `Stats.bestMakespan`이 제출한 `assignment[]`에서 다시 계산한 최대 부하와 같으며, 같은 seed에서 같은 점수가 나오고, `best`가 초기해보다 나쁘지 않아야 합니다.

다음: 승객 배정에 방문 순서가 붙어 점수가 달라지는 [배정과 경로가 결합된 문제: 택시 배정](https://h.readiz.com/learn/assignment-with-routes)에서 같은 최댓값 점수에 경로 항을 더합니다.
