# h-contest heuristic notes roadmap

이 문서는 실전 문제 풀이 중심의 단계별 개편과 기본 강의의 추가 연습 후보를 관리합니다. 변경 기록은 git 기록을 사용합니다.

## 방법론 중심 재편 (2026-11-21) — 현재 작업의 기준

이 강의 묶음의 목표는 **일반적인 휴리스틱 알고리즘 방법론**입니다. 이 사이트의 특정 문제 풀이집이 아닙니다. 강의의 단위는 문제가 아니라 기법이고, 읽고 나면 처음 보는 문제에서도 쓸 수 있는 판단 기준과 코드 틀이 남아야 합니다. 아래 "실전 풀이 중심 개편"에서 만든 문제별 강의 8개와 `heuristic`의 문제별 페이지는 **적용 사례**로 내려 두고, 방법론 강의가 그쪽을 예시로 가리킵니다. 문제 하나를 끝까지 푸는 강의는 새로 추가하지 않습니다.

### 방법론 강의 목차

| 순서 | id | 제목 | 다루는 것 |
| --- | --- | --- | --- |
| 1 | `problem-modeling` | 문제를 상태·행동·점수로 옮기기 | 계약에서 상태·불변식·무효 조건 뽑기, 내 점수 계산을 채점과 맞추기, 항상 유효한 기준선, 점수의 하한·상한으로 남은 여지 가늠하기 |
| 2 | `construction-heuristics` | 초기해 만들기: 탐욕·삽입·무작위화 | 한 번에 하나씩 정하는 구성법, 선택 기준(가까운 것·후회가 큰 것·삽입 비용), 정렬 기준 바꾸기, 무작위화와 여러 번 만들기, 구성법이 뒤 탐색에 주는 영향 |
| 3 | `neighborhood-and-delta` | 근방 설계와 차분 평가 | 이동의 종류(바꾸기·옮기기·뒤집기·교환), 근방의 크기와 연결성, 점수 변화만 계산하기, 차분을 전체 재계산과 대조하기, 유효성을 깨지 않는 이동 |
| 4 | `hill-climbing-and-annealing` | 언덕 오르기와 담금질 | 첫 개선·최고 개선, 지역 최적, 나쁜 이동을 받는 확률, 온도 범위를 차분 크기에서 정하기, 일정, 재시작, 최고해 보관 |
| 5 | `beam-search` | 빔 서치와 평가 함수 | 순차 결정 문제, 폭과 깊이, 중간 상태의 평가 함수 설계, 같은 상태 합치기, 다양성, 탐욕·완전 탐색과의 관계 |
| 6 | `destroy-and-repair` | 크게 부수고 다시 짓기 | 작은 이동으로 못 나가는 구조, 부술 부분 고르기, 다시 짓는 구성법, 수락 기준, 부수는 크기 조절 |
| 7 | `candidate-and-time-budget` | 후보 줄이기와 시간 예산 | 입력 상한에서 연산 수 세기, 가까운 후보만 보기(칸·이웃 목록), 시간 재기와 단계별 배분, 반복 횟수와 품질의 교환 |
| 8 | `partial-information` | 정보가 부분적일 때 결정하기 | 아는 것·관측한 것·모르는 것 나누기, 관측을 기억하는 자료구조, 탐색과 활용, 낙관적 추정, 온라인 결정의 평가 |
| 9 | `experiments-and-tuning` | 실험과 튜닝 | 무엇을 재는가, 같은 입력·여러 시드, 짝지은 비교, 흔들림과 "결정 못 함", 매개변수를 한 번에 하나씩, 과적합 피하기 |

2026-11-22에 목차의 9개 강의가 모두 들어갔습니다(`problem-modeling`부터 `experiments-and-tuning`까지, 각 허브 + 3쪽과 검사 스크립트). 앱의 `/learn`은 이 9개와 기존 `heuristic`을 `휴리스틱 방법론` 묶음으로, 문제별 강의 8개를 `적용 사례` 묶음으로 보여 줍니다.

2026-11-22 정리: 방법론 강의와 겹치던 `testing-and-stress`의 실험 평가 쪽을 지우고(신뢰구간 문단만 `experiments-and-tuning`으로 옮김), `heuristic-case-studies/search-strategies`는 ORDERING에 SA를 붙인 구현과 측정만 남겼습니다. 배정 틀 입력 생성 순서를 작업 단위로 통일했고(1·2번 강의 재측정), 1·2번 강의에 데모 `score-check`, `construction-steps`를 넣었습니다.

### 방법론 강의의 공통 기준

- **문제에 묶이지 않는다.** 설명은 아래 세 가지 연습용 문제 틀과 작은 손계산 예로 한다. 이 사이트의 문제는 마지막 "적용 사례" 절에서 링크와 한두 문장으로만 가리킨다. 본문 수치가 사이트 문제의 채점 결과에 의존하지 않는다.
- **옮겨 쓸 수 있는 것을 남긴다.** 강의마다 (1) 언제 이 기법을 쓰고 언제 쓰지 않는지의 판단 기준, (2) 문제가 바뀌어도 그대로 쓰는 코드 틀과 문제마다 채워 넣는 부분의 구분, (3) 순서·배정·배치·순차 결정 가운데 두 가지 이상의 문제 유형에 적용한 짧은 예, (4) 흔한 실수와 그것을 잡는 검사를 싣는다.
- **수치는 재현 가능해야 한다.** 본문에 나오는 점수·횟수는 검사 스크립트가 정해진 시드의 연습용 입력으로 다시 계산해 본문과 대조한다. 문제 패키지 없이 CI에서 돈다. 시간(ms)은 싣지 않고 연산 횟수·반복 횟수로 말한다. 차이가 시드 흔들림 안이면 "결정 못 함"이라고 쓴다.
- **코드는 제출용 형식이다.** 표준 헤더·STL·동적 할당 없이 고정 배열로 쓰고, 필요한 공통 블록(`random`, `sort`, `queue`, `min-heap`, `array`)을 밝힌다.
- **구성은 허브 + 3쪽이다.** `lesson.md`(무엇을 다루는지, 판단 기준 요약, 본문 링크), `pages/idea.md`(원리와 손으로 따라가는 예), `pages/implementation.md`(코드 틀과 두 유형 적용), `pages/practice.md`(실험, 흔한 실수, 다른 문제에 옮기기, 적용 사례, 연습).

### 연습용 문제 틀 (모든 방법론 강의가 공유)

검사 스크립트는 아래 생성 규칙을 그대로 구현한다. 난수는 `x = x * 6364136223846793005 + 1442695040888963407`(64비트), 값은 `(x >> 33) % 범위`이며 시드는 본문에 적는다.

- **순서 문제(경로):** 점 `N`개가 `0..999` 정수 좌표에 있다. 모든 점을 한 번씩 지나는 순서를 정한다(시작점 자유, 돌아오지 않음). 비용은 이웃한 점 사이 맨해튼 거리의 합이고 작을수록 좋다. 기본 크기 `N = 200`.
- **배정 문제(작업):** 작업 `N`개와 기계 `M`대가 있다. 입력은 작업 `i = 0, 1, …` 순서로, 작업마다 길이 `d[i]`를 뽑고 이어서 그 작업의 `c[i][0..M-1]`을 뽑아 만든다(길이를 전부 뽑은 뒤 비용을 뽑지 않는다). 작업 `i`의 길이는 `d[i]`(1..100), 기계 `m`에 맡길 때의 추가 비용은 `c[i][m]`(0..50)이다. 모든 작업을 정확히 한 기계에 맡기고, 한 기계에는 작업을 `K`개까지만 맡길 수 있다(위반하면 무효). 비용은 `Σ_m load[m]² / 100 + Σ_i c[i][assign[i]]`(`load[m]`은 맡은 작업 길이의 합, 나눗셈은 합에 대해 한 번 정수 나눗셈)이고 작을수록 좋다. 기본 크기 `N = 120, M = 8, K = 18`.
- **순차 결정 문제(격자 수집):** `H × W` 격자의 칸마다 값 `v`(0..9, 값의 60%는 0)가 있다. 정해진 칸에서 시작해 상하좌우로 `T`번 움직이고, 처음 밟는 칸의 값을 얻는다(시작 칸 포함). 격자 밖으로는 못 나간다. 얻은 값의 합이 클수록 좋다. 기본 크기 `H = W = 20, T = 60`. 부분 정보 변형에서는 현재 칸에서 맨해튼 거리 2 이내의 칸만 값이 보인다.

2026-11-22에 `heuristic`을 [휴리스틱 방법론 지도](lessons/heuristic/lesson.md) 허브로 바꿨습니다. 처음 보는 문제의 흐름(문제 옮기기 → 초기해 → 근방과 차분 → 탐색 고르기 → 후보·시간 예산 → 실험), 문제 모양별 탐색 방법 표, 공통 원칙과 그림 `method-map.svg`를 담고 하위 쪽은 없습니다. 하위 4쪽(`ordering-route-improvement`, `search-strategies`, `placement-and-repair`, `aircontech-beam-search`)은 pageId를 그대로 두고 새 강의 [적용 사례 모음](lessons/heuristic-case-studies/lesson.md)(`heuristic-case-studies`)으로 옮겼고, 쪽이 쓰던 그림과 측정 원본도 함께 옮겼습니다. 옛 주소 `/learn/heuristic/<pageId>`는 앱이 `/learn/heuristic-case-studies/<pageId>`로 넘깁니다. 지도 허브의 구조는 `scripts/check_method_map.py`가 검사합니다.

## 실전 풀이 중심 개편 — 적용 사례를 만든 이전 기준

목표는 수강자가 `문제 계약 읽기 → 유효한 기준선 → 점수 측정 → 개선 연산 → 검증 → 실전 변형`을 직접 수행하는 것입니다. 이론 목차를 전부 학습해야 첫 휴리스틱 문제에 도전할 수 있는 구조는 줄입니다. 현재 강의 32개를 `heuristic-notes` 한 분류로 유지하고, 한 번에 한 단위씩 개편합니다.

공통 기준:

- 직접 풀이 트랙의 제출 예제는 STL·표준 헤더 없이 고정 배열과 공개 API로 구현합니다. `struct`, 참조, `template` 같은 언어 기능은 사용할 수 있습니다.
- 공통 동작은 별도 `cpp-common-library`의 이름 있는 코드 블록을 원문으로 삼습니다. 문제마다 필요한 블록·배열 상한·초기화 시점만 명시합니다. 인덱스 연결 목록, 방문 세대 번호, rollback 기록 등은 이를 실제로 쓰는 다음 레슨에서 필요성을 설명한 뒤 추가합니다.
- 기존 제출은 설계 패턴과 병목을 파악하는 근거로 읽습니다. 강의 예제는 독립적으로 작성하고 공개 입력/API만 사용합니다. 내부 심볼 접근·생성기 미래 입력 재생에 의존하지 않습니다.
- 각 단계는 손계산 예시, 끝까지 실행되는 코드, 실패 사례, 실제 문제 또는 로컬 완결형 연습을 함께 갖춥니다. 코드 문법 검사와 실행·점수 검증은 구분합니다.
- 기존 일반 C++/STL 예제는 적용 환경을 표시합니다. 실전 트랙으로 연결하는 시점에 필요한 부분부터 공통 코드 방식으로 전환합니다.

2026-09-22 후속 작업에서 제출·검증과 공통 라이브러리를 별도 레슨으로 분리했습니다. ORDERING → 검증 → SA 흐름을 유지하며, 라이브러리는 필요한 블록만 찾아 쓰는 자료입니다. 정렬·그리디·힙의 실제 예제는 공통 블록을 조합하는 STL 없는 코드로 전환했습니다. 2026-11-19에 실전 강의가 쓰는 기초 도구인 BFS/DFS·Dijkstra·Union-Find·누적합/차분·이분 탐색·투 포인터·좌표 압축·0-1 BFS 8개를 head/next 인접 리스트·고정 배열·공통 `queue`/`min-heap`/`sort` 블록의 STL 없는 코드로 전환하고 `scripts/check_foundation_code.py`로 실행 검증했습니다. 2026-11-21에 남은 기초·자료구조·그래프 강의 13개(graph-tree-basics와 MST 페이지, topological-sort-dag, bellman-ford-negative-cycle, floyd-warshall, fenwick-tree, segment-tree, sqrt-decomposition, dynamic-segment-tree, dynamic-programming, tsp-hamiltonian, hungarian-algorithm, meldable-heap, treap)도 같은 방식으로 전환했습니다. 동적 노드 구조는 고정 크기 pool과 정수 번호로 바꿨고, 검사 대상은 21개 강의입니다. 일반 C++ 환경 표시는 로컬에서만 돌리는 `testing-and-stress`의 실험 페이지에만 남습니다.

| 순서 | 다음 개편 단위 | 연결 문제와 핵심 변화 | 완료 기준 |
| --- | --- | --- | --- |
| 1 | 첫 휴리스틱 실습 | ORDERING을 복잡한 배치 사례보다 먼저 배치. 번호 순서 → nearest neighbor → 열린 경로 2-opt | 같은 TC에서 단계별 비용·시간·유효성 기록, 차분값을 전체 재평가와 대조 |
| 2 | 검증과 실험을 앞당김 | 현재 testing-and-stress 및 실험 페이지의 핵심을 ORDERING 직후 연결 | 고정 입력/solver seed, 여러 seed 비교, 튜닝 외 입력, 실패 원인 기록을 수행하는 연습 |
| 3 | 국소 탐색과 SA | 상태·이웃·제약·차분 → hill climbing → 막히는 예 → SA. SCHEDULX의 `cost[job][machine]` 계약과 연결 | apply/undo·best/current 검증, 실제 점수 차이에 맞춘 온도·수락률 실험 |
| 4 | 탐색과 행동 분리 | MINEEXPLORE의 관측/행동 구분에서 AIRCONTECH 빔 탐색으로 연결 | 예측 깊이·빔 너비·실행 길이를 따로 바꾸고, 미래 평가값과 실제 점수를 비교 |
| 5 | 배정과 경로 결합 | SCHEDULX → TAXIASSIGN/MULTIDRONE → COUPANG2. 최대 부하, 재고 매칭, 배송 순서·적재 제약 | 작은 예제부터 전체 목적 함수까지 연결. Hungarian 전체 이론을 입문 선수로 강제하지 않음 |
| 6 | 배치와 복구 | ALLOCATE/CLUSTERX 기초 사례와 LANDINGX/CHIPDESIGN/TENSORALLOC | 유효한 배치·수리 → 국소 이동 → destroy/repair 비교, 무효 후보 처리 검증 |
| 7 | 규모·부분 관측·변하는 상태 | COUPANG1 후보 축소, ROBOTCLEAN/DRONESORT 관측 메모리, FRIEGHTFIX 갱신, ANTENNAS/TELEVISION 자원 배분 | 실제 입력 상한·API 비용·갱신 빈도로 자료구조와 탐색 예산을 선택하는 연습 |
| 8 | 특수 점수식 읽기 | GERMMATCH의 동기화 비용, ENTROPY2D의 거리 합과 이동 예산 | 채점식을 손으로 재현한 작은 TC와 실측 대조, 수학적 성질을 풀이로 옮기는 기준 |

2026-09-22 기준으로 1번은 번호 순서·nearest neighbor·2-opt의 동일 TC 비용·시간과 차분 검증까지 반영했습니다. 2번은 ORDERING 다음에 검증 레슨을 읽도록 연결했고, 실패·복구·재현성 검사와 입력/seed를 바꾸는 실험 과제를 제공합니다. 3번은 지역 최적 반례와 실행 가능한 ORDERING SA, best/current·전체 차분 대조, 같은 후보 수의 측정까지 반영했습니다. 여러 seed·미사용 입력을 통한 성능 일반화와 같은 시간 비교는 아직 ORDERING에서 남아 있습니다.

2026-11-18에 3번의 SCHEDULX 연결을 [배정 문제의 지역 탐색과 SA](lessons/assignment-local-search/lesson.md)로 반영했습니다. 작업→기계 배정 상태, 최대 부하의 이동·교환 차분(`load[]` 유지), 5작업·2기계 손계산(14 → 15 → 12 → 9)과 11개 이웃 전수 표, 평균 부하 항을 더한 에너지, 중앙 손해로 정하는 시작 온도, 온도 구간별 수락률과 solver seed 9개의 중앙값, 직접 만든 입력에서의 확인, 최댓값 차분 오류 사례를 포함하며 `scripts/check_assignment_search.py`가 코드 추출·ASan/UBSan·손계산 표·저장된 측정 대조를 수행합니다. 같은 실행 시간 비교와 숨은 채점 입력에서의 일반화는 남아 있습니다.

4번은 [채점기 상태를 따라 그리며 행동하기](lessons/observe-and-act/lesson.md)로 MINEEXPLORE의 채점기 상태·관측 기록·추정 구분, TC 시작 초기화, 가까운 칸 정책과 이동당 이득 평가식, 예측 대비 실제 점수 기록까지 반영했습니다. AIRCONTECH 빔 너비·예측 깊이를 따로 바꾸는 실험과 7번의 다른 문제(ROBOTCLEAN/DRONESORT 등) 연결은 남아 있습니다.

2026-11-18에 5번의 TAXIASSIGN 연결을 [배정과 경로가 결합된 문제: 택시 배정](lessons/assignment-with-routes/lesson.md)으로 반영했습니다. 기사 부하 항을 승객의 탑승 거리(담당자가 정함)와 빈 차 구간(담당자와 순서가 정함)으로 나누고, 배정만·경로만·번갈아·결합 탐욕·결합 이웃(옮기며 끼우기·자리 바꾸기)을 같은 TC 5개의 점수와 시간으로 비교하며, 기사 2명·승객 4명의 16개 배정 전수 손계산, solver seed 9개의 설정 비교, 차분 오류 두 가지의 재현을 포함합니다. `scripts/check_assignment_routes.py`가 코드 추출·ASan/UBSan·손계산 표·저장된 측정을 대조합니다. MULTIDRONE·COUPANG2 연결(재고·적재 제약), SA 온도 실험, 같은 실행 시간 비교와 숨은 채점 입력에서의 일반화는 남아 있습니다.

6번은 [격자 배치 문제: 유효한 후보, 국소 이동, destroy/repair 비교](lessons/placement-search/lesson.md)로 LANDINGX를 반영했습니다. 후보 선택 집합 상태와 점유 격자의 `put`/`take`(apply/undo), 제안 단계의 무효 거절, 추가·교체 차분, 4×6 지도 손계산(35점에서 멈추고 두 개를 함께 빼면 40점), 같은 후보 검사 수에서 first-fit·정렬 탐욕·국소 이동·destroy/repair를 solver seed 9개로 비교한 예산별·destroy 크기별·무작위 배율별 표, 되돌리기 누락과 종류별 한도 누락 실패 재현을 포함하며 `scripts/check_placement_search.py`가 코드 추출·후보 완전 열거 대조·ASan/UBSan·손계산 표·저장된 측정 대조를 수행합니다. CHIPDESIGN/TENSORALLOC 연결, 같은 시간 예산 비교, 숨은 채점 입력에서의 일반화는 남아 있습니다.

2026-11-18에 7번 중 규모(COUPANG1 후보 축소)를 [입력이 클 때: 공간 칸으로 후보를 줄이고 시간 예산 나누기](lessons/large-input-search/lesson.md)로 반영했습니다. 입력 상한에서 만든 연산 수 예산표(남은 배송을 전부 훑는 방법은 5.0×10^11번, 약 223초), 좌표 칸과 링 확장·마지막 후보와 자리를 바꾸는 삭제·메모리 계산(약 37MB), 16×16 지도 손계산(세 번 고르기와 링 종료 조건을 한 겹 일찍 끊으면 틀리는 첫 번째 고르기), 번호 순서 기준선(107,926,719,860)에서 운행 단위·적재 20개·센터 선택·순서 개선(9,306,067,620, 통과 기준 15,000,000,000)까지의 단계별 점수와 시간, 칸 크기·근사 탐색·적재·밀도 가중치·개선 횟수를 설정마다 5번 돌려 가며 잰 중앙값, 종료 조건 오류(점수 +0.3%만 나빠짐)와 지우기 누락(패널티)의 재현을 포함하며 `scripts/check_large_input_search.py`가 코드 추출·전수 탐색 대조·ASan/UBSan·손계산 표·저장된 측정 대조를 수행합니다. ROBOTCLEAN/DRONESORT 관측 메모리, FRIEGHTFIX 갱신, ANTENNAS/TELEVISION 자원 배분 연결, 마지막 10% 배송(비용의 25%)을 줄이는 여러 센터 운행, 같은 시간 예산 비교와 숨은 채점 입력에서의 일반화는 남아 있습니다.

8번 중 ENTROPY2D는 [특수한 점수식 읽기: 채점식을 손으로 재현하고 성질을 풀이로 옮기기](lessons/reading-the-score/lesson.md)로 반영했습니다. 공개 채점 규칙(감소 비율의 제곱과 남은 이동 횟수의 보너스, 실패 호출도 횟수를 쓰는 점)을 `myScore`로 옮겨 손계산 TC(5개 입자, 42 → 38, 9077점)·내 점수·채점기 점수를 맞추고, 거리 합이 열·행 경계의 `pre × (n − pre)`로 갈라지는 성질에서 이동 한 번의 O(1) 차분과 빈 칸 경로 재배치의 차분을 유도합니다. 기준선·중앙으로 밀기·차분 탐욕·큰 이득부터·경로 재배치를 공개 TC 10개의 점수와 시간으로 비교하고(4단계 1908789, 통과 기준 1917000에 8211점 부족), 5단계로 끝 배치를 먼저 정해 가까운 쌍부터 짝짓고 직선 경로로 옮겨 이동 하한의 1.001배만 쓰며 1918179점으로 통과 기준을 넘고(하나씩 끄는 실험 포함), 축별 하한과 원판 참고 배치 대비 위치, 문턱 실험, 쌍 이중 계산·`int` 누적·차분 off-by-one 실패 재현을 포함하며 `scripts/check_reading_the_score.py`가 코드 추출·기준 채점기 대조·ASan/UBSan·차분 전수 대조·손계산·저장된 측정 대조를 수행합니다. GERMMATCH의 동기화 비용 연결과 숨은 채점 입력에서의 일반화는 남아 있습니다.

2026-11-19에 7번 중 부분 관측(ROBOTCLEAN 관측 메모리)을 [보이는 만큼만 아는 문제: 지도를 그려 가며 청소하기](lessons/explore-unknown-map/lesson.md)로 반영했습니다. 지도도 자기 위치도 모르는 로봇의 `scan`, `move`, `turn` 결과를 시작 칸 기준 좌표계의 내 지도와 자세로 옮기는 변환(배열 상한 계산, 회전된 관측 되돌리기, subtask 시작 초기화)과 6×8 지도 손계산(스캔 `011000000`, 비용 25 동점, 막힌 이동에서 위치 불변)을 다루고, DFS 기준선(15411250)에서 BFS와 (칸, 방향) Dijkstra로 키웁니다. 스캔 기준(`SCAN_MIN`), 회전 비용, 모르는 칸 비용을 하나씩 바꾼 표와 직접 만든 홀드아웃 지도 10개, 관측 미회전·막힌 이동 위치 갱신·이전 지도 잔존·회전 부호 실패 재현을 포함하며 `scripts/check_explore_unknown_map.py`가 코드 추출·기준 채점기와의 상태 대조(모든 호출 뒤 내 지도와 자세 == 실제)·계획 함수의 별도 구현 대조·손계산·저장된 측정 대조를 수행합니다. DRONESORT 관측 메모리, 같은 TC의 subtask가 같은 지도를 쓴다는 점을 이용한 위치 추정, 숨은 채점 입력에서의 일반화는 남아 있습니다.

2026-11-19에 7번 중 DRONESORT의 관측 메모리를 [열어 본 상자를 기억해 쌓고 정렬하기](lessons/remember-and-sort/lesson.md)로 반영했습니다. 이 문제에는 관측 전용 API가 없고 `pick`으로 상자를 꺼내야만 목적지와 무게를 주므로, 거울(칸 높이 `H`, 열지 않은 상자 수 `orig`, 열어 본 상자 값)과 계획(비행 고도, 정렬)을 나눈 풀이로 다뤘습니다. 기준선(항상 `z = 99`, 삽입 정렬, 3,135,082,558)에서 지형 따라 날기(325,362,282), 인내 정렬(235,236,510, 통과 기준 250,000,000, 입력에서 구한 하한 68,653,459)까지 단계별 점수와 시간, 경로 선택·임시 칸 수 실험(생성기 seed 5개와 한쪽 구석에 몰린 직접 만든 입력), 높이 갱신·맡긴 칸·TC 시작 위치·정렬 방향 실패 재현을 포함하며 `scripts/check_remember_and_sort.py`가 코드 추출·기준 시뮬레이터(매 호출 직전 거울과 실제 상태 대조)·ASan/UBSan·손계산(인내 정렬 14번 대 삽입 정렬 34번, 비행 12번 대 196번)·저장된 측정 대조를 수행합니다. 비우기의 수평 이동(2단계 호출의 58%)을 줄이는 다음 개선, 7번의 다른 문제 연결, 숨은 채점 입력에서의 일반화는 남아 있습니다.

1~8번의 첫 강의가 모두 들어갔습니다. 7번의 부분 관측·갱신(ROBOTCLEAN, DRONESORT, FRIEGHTFIX)과 자원 배분(ANTENNAS, TELEVISION), 각 강의에 남긴 연습 과제는 후속으로 진행합니다. Digit DP, 구간 DP, Implicit Treap은 미완성 골격을 본문에 두지 않고, 실제 문제와 끝까지 동작하는 풀이가 준비될 때 다시 다룹니다.

### 목차와 연결도 함께 정리할 항목

- 기본 트랙의 표시 순서는 필수 선수 레슨이 먼저 오도록 정리했습니다. 휴리스틱 입문의 DP, Hungarian의 고급 matching, minimax의 게임 이론 확장 등 선택 참고는 필수 선수에서 관련 레슨으로 옮겼습니다. 새 레슨에서도 필수 지식과 선택 참고를 구분합니다.
- 각 레슨의 선수·다음·연관 레슨을 h-contest 화면에서도 이동 가능한 학습 경로로 보여 주는 작업을 별도 UI 단위로 진행합니다.
- 기본 연습 ALLOCATE/CLUSTERX/MINEEXPLORE와 CITYSUM2D 등 이미 있는 문제를 해당 기초 레슨에 연결합니다. 단순 링크 추가가 아니라 계약과 풀이 연결 설명을 함께 작성합니다.
- 로그인 전 강의 접근은 h-contest 서비스에서 제한합니다. 원본 GitHub/Pages의 공개 범위는 별도 운영 정책이며, 서비스의 인증만으로 원본이 비공개가 되지는 않습니다.

새 주제는 허브 하나, 완성된 대표 페이지 하나, 실제 문제 또는 로컬 완결형 연습 하나를 함께 준비한 뒤 manifest에 추가합니다. 적절한 h-contest 문제가 없으면 임의 문제 ID나 빈 표를 본문에 넣지 말고 이 로드맵에 연습 후보를 남깁니다.

공개 목록은 `휴리스틱 노트` 한 분류로 유지합니다. 그래프, 수학, 문자열 같은 세부 주제 구분은 별도 폴더를 늘리지 않고 태그, 선수/다음 레슨, 하위 페이지, 문제 신호별 길찾기에서 표현합니다.

## 기본 강의의 추가 연습 후보

2026-09-22에 연습이 없던 19개 기본 강의에 입력·출력·제한·검산 방법을 갖춘 로컬 연습을 추가해, 모든 강의를 실제 연습으로 연결했습니다. 아래는 그 첫 연습 이후의 추가 후보입니다. 네 단계 분량을 채우는 할당량은 아닙니다. `FUNCSUM1`·`SORTTEST`만으로 누적합·좌표 압축 실습을 대체하지 않습니다.

| 강의 | 아직 마련할 연습 후보 |
| --- | --- |
| [복잡도와 입력 크기 감각](lessons/complexity-input-size/lesson.md) | 입력 제한 보고 풀이 후보 고르기; 큰 2차원 DP 테이블의 메모리 검토 |
| [정렬 알고리즘](lessons/sorting/lesson.md) | 값과 인덱스 동반 정렬; 좌표 압축 전처리; 안정성이 필요한 다중 기준 정렬 |
| [누적합과 차분 배열](lessons/prefix-sum-difference/lesson.md) | 2차원 직사각형 합과 직사각형 업데이트 |
| [그리디 알고리즘](lessons/greedy/lesson.md) | 회의실 배정; 마감이 있는 과제 선택; 그리디 반례 찾기 |
| [투 포인터와 슬라이딩 윈도우](lessons/two-pointers-sliding-window/lesson.md) | 두 수의 합 찾기; 서로 다른 값이 K개 이하인 가장 긴 구간; 음수가 섞인 구간 합 |
| [이분 탐색과 파라메트릭 서치](lessons/binary-search/lesson.md) | 정렬 배열에서 lower_bound 찾기; 최소 간격 최대화; 실수형 이분 탐색 |
| [좌표 압축](lessons/coordinate-compression/lesson.md) | inversion count; 구간 칠하기와 전체 길이 계산 |
| [우선순위 큐와 힙](lessons/priority-queue-heap/lesson.md) | 최댓값 반복 추출; 최솟값 후보를 계속 고르는 스케줄링; stale entry 제거; 같은 우선순위 tie-break |
| [Meldable Heap](lessons/meldable-heap/lesson.md) | 그룹별 지연 가산과 병합; pool 공유 실수 확인 |
| [동적 계획법](lessons/dynamic-programming/lesson.md) | 동전의 무제한 사용; LIS 또는 구간 DP; 비트마스크 DP |
| [TSP와 해밀턴 경로](lessons/tsp-hamiltonian/lesson.md) | 작은 해밀턴 경로 완전탐색; 비트마스크 TSP DP |
| [Union-Find 알고리즘](lessons/union-find/lesson.md) | Kruskal MST; rollback이 필요한 오프라인 연결성 |
| [BFS/DFS와 격자 탐색](lessons/bfs-dfs-grid/lesson.md) | 연결 요소 세기; 여러 시작점 BFS; 위치에 방향/열쇠가 붙는 상태 그래프 |
| [그래프와 트리 기본 성질](lessons/graph-tree-basics/lesson.md) | 연결 요소 세기; 트리 지름/센트로이드; MST |
| [0-1 BFS](lessons/zero-one-bfs/lesson.md) | 무료 이동과 유료 이동이 있는 선형 그래프; 방향 전환 비용이 있는 격자 최단거리; 벽을 부수는 횟수를 최소화하는 미로; 비용이 0, 1, 2인 그래프 |
| [위상 정렬과 DAG DP](lessons/topological-sort-dag/lesson.md) | DAG 최장/최단 경로; 작업별 소요 시간을 포함한 완료 시점 |
| [Dijkstra 최단거리](lessons/dijkstra/lesson.md) | 다중 시작점과 단일 목표 최단거리; 경로 복원; 음수 간선이 섞일 때의 반례 |
| [Bellman-Ford와 음수 사이클](lessons/bellman-ford-negative-cycle/lesson.md) | 음수 사이클 자체를 출력; 시작점과 무관한 전체 그래프의 음수 사이클 탐지 |
| [Floyd-Warshall](lessons/floyd-warshall/lesson.md) | 도달 가능성 전파; 최단 경로 복원; 음수 사이클 영향 |
| [Sqrt Decomposition](lessons/sqrt-decomposition/lesson.md) | 정적 구간 합 질의; 구간에서 k보다 작은 원소 개수; Mo's Algorithm |
| [Fenwick Tree](lessons/fenwick-tree/lesson.md) | inversion count; k번째 원소 찾기 |
| [Segment Tree](lessons/segment-tree/lesson.md) | 점 업데이트 + 구간 합; 구간 최솟값 + 구간 덧셈; 구간 대입과 덧셈의 합성 |
| [Hungarian Algorithm](lessons/hungarian-algorithm/lesson.md) | 작은 assignment problem; forbidden edge가 있는 sparse assignment |
| [Treap과 BST 기본](lessons/treap/lesson.md) | 구간 뒤집기 Implicit Treap; 중복 횟수를 세는 multiset 변형 |
| [Minimax와 Alpha-Beta Pruning](lessons/minimax-alpha-beta/lesson.md) | depth-limited game search; 반복 상태 게임 |
| [Testing과 Stress Test](lessons/testing-and-stress/lesson.md) | 배열 구간 질의와 brute force 비교; 그리디 후보 풀이의 반례 찾기; 기하/그래프의 edge case 수집; 빠른 풀이와 brute force가 같은 버그를 공유하는 사례 |
| [Proof와 Invariant](lessons/proof-and-invariants/lesson.md) | 이분 탐색 invariant 작성; exchange argument로 그리디 선택 증명; DP 상태 정의와 전이 완전성 설명 |
| [Dynamic Segment Tree](lessons/dynamic-segment-tree/lesson.md) | online rectangle sweep; persistent sparse query |
