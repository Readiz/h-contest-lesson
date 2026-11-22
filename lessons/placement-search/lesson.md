# 격자 배치 문제: 유효한 후보, 국소 이동, destroy/repair 비교

[우주선 착륙](/practice/LANDINGX)은 `1000 x 1000` 고도 지도에 직사각형 우주선 10000척을 놓는 문제입니다. 지도 안에 있어야 하고, 겹치면 안 되고, 네 꼭짓점의 고도 차가 6 이하여야 합니다. [광고판 도시 배치](https://h.readiz.com/learn/heuristic-case-studies/placement-and-repair)는 destroy/repair를 서술로 다뤘습니다. 이 강의는 한 문제에서 **탐욕, 국소 이동, destroy/repair를 같은 후보 검사 수로 실제 비교**하고, 무효 후보를 어디서 걸러야 하는지 실패를 재현해 확인합니다. [Testing과 Stress Test](https://h.readiz.com/learn/testing-and-stress)와 [초기해와 지역 탐색](https://h.readiz.com/learn/heuristic-case-studies/search-strategies)을 읽었다고 가정하며, 난수와 정렬은 [공통 코드의 `random`, `sort` 블록](https://h.readiz.com/learn/cpp-common-library)을 먼저 붙여 씁니다.

## 이 강의에서 다루는 것

- 고도 차와 겹침, 종류별 한도를 한 함수로 검사해 무효 후보를 어디서 거를지 정하는 설계.
- 점수 큰 순 탐욕과 추가·교체 국소 이동, 그리고 국소 이동이 멈추는 작은 예.
- 영역을 빼고 무작위 배율로 다시 채우는 destroy/repair와 되돌리기.
- 같은 후보 검사 수로 세 방법을 비교하는 실험, 되돌리기와 종류별 한도를 빠뜨린 실패.

## 단계별 결과

LANDINGX 공개 TC 10개의 점수 합입니다(클수록 좋고 통과 기준은 3001673입니다). 후보 검사 수와 시간, 예산별 곡선은 [실측과 실패 사례](pages/experiments-and-failures.md)에 있습니다.

<!-- check:hub-summary -->
| 방식 | 합 ↑ |
| --- | ---: |
| 기준선: 후보 번호 순 first-fit | 2574208 |
| 탐욕: 점수 큰 후보부터 | 2993803 |
| 국소 이동(hill climbing) | 2999023 |
| destroy/repair(한 영역) | 3001673 |

## 본문

1. [문제 계약과 기준선](pages/contract-and-baseline.md): 고도 차·겹침·종류별 한도를 한 함수로 검사하는 상태, first-fit 기준선과 점수 큰 순 탐욕.
2. [풀이: 국소 이동과 destroy/repair](pages/solution.md): 추가·교체 이동과 차분 평가, 국소 이동이 멈추는 손계산, destroy/repair의 상태·되돌리기와 완성 코드.
3. [실측과 실패 사례](pages/experiments-and-failures.md): 같은 후보 검사 수의 단계별 비교와 예산 곡선, destroy 크기·무작위 배율 실험, 되돌리기·종류별 한도 실패.

## 연습: LANDINGX

[LANDINGX](/practice/LANDINGX)에서 다음을 직접 해 봅니다.

1. 후보 번호 순 first-fit과 점수 큰 순 탐욕을 제출해 이 강의의 표(2574208, 2993803)와 같은 TC 합이 나오는지 확인합니다.
2. 국소 이동을 붙여 후보 검사 수를 1만, 10만, 100만으로 바꾸며 점수와 시간을 기록하고, 멈춘 배치에서 `evaluate`로 전체 후보를 평가해 개선 이동이 정말 0개인지 확인합니다.
3. destroy/repair의 `size`, `noise`, 제거 방식을 바꿔 solver seed 5개 이상의 중앙값으로 비교합니다. 한 번의 점수로 고르지 않습니다.
4. 새 이웃을 하나 추가합니다(예: 빈 칸이 많은 구역에서 시작하는 영역). 추가 후에도 점유 격자 재구성 대조, 되돌린 뒤의 상태 동일, 제출 직전의 규칙 검사를 먼저 통과시킨 뒤 점수를 비교합니다.

확인 기준: 모든 TC가 유효하고, 같은 seed에서 같은 점수가 나오고, 반환한 `row/col/dir`을 처음부터 다시 검증한 점수가 탐색 중의 `score`와 같아야 합니다. 같은 방법을 서술로 다룬 [광고판 도시 배치](https://h.readiz.com/learn/heuristic-case-studies/placement-and-repair)와 아래 단계별 데모도 함께 봅니다.

[Destroy/Repair: 제거하고 다시 채워 점수 비교하기](https://git.readiz.com/h-contest-lesson/demos/index.html?demo=destroy-repair)
