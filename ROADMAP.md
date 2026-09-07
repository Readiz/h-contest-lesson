# h-contest heuristic notes roadmap

이 문서는 실전 문제 풀이 중심의 단계별 개편, 아직 공개하지 않은 레슨 후보, 공개 전 품질 기준, practice link 미정 항목을 관리합니다. 완료 기록은 [CHANGELOG.md](CHANGELOG.md)에 남깁니다.

## 실전 풀이 중심 개편 — 다음 작업의 기준

목표는 수강자가 `문제 계약 읽기 → 유효한 기준선 → 점수 측정 → 개선 연산 → 검증 → 실전 변형`을 직접 수행하는 것입니다. 이론 목차를 전부 학습해야 첫 휴리스틱 문제에 도전할 수 있는 구조는 줄입니다. 기존 `heuristic-notes` 30개와 `heuristic-reference` 70개의 두 분류를 유지하고, 한 번에 한 단위씩 개편합니다.

공통 기준:

- 직접 풀이 트랙의 제출 예제는 STL·표준 헤더 없이 고정 배열과 공개 API로 구현합니다. `struct`, 참조, `template` 같은 언어 기능은 사용할 수 있습니다.
- 공통 동작은 `cpp-contest-basics`의 이름 있는 코드 블록을 원문으로 삼습니다. 문제마다 필요한 블록·배열 상한·초기화 시점만 명시합니다. 인덱스 연결 목록, 방문 세대 번호, rollback 기록 등은 이를 실제로 쓰는 다음 레슨에서 필요성을 설명한 뒤 추가합니다.
- 기존 제출은 설계 패턴과 병목을 파악하는 근거로 읽습니다. 강의 예제는 독립적으로 작성하고 공개 입력/API만 사용합니다. 내부 심볼 접근·생성기 미래 입력 재생에 의존하지 않습니다.
- 각 단계는 손계산 예시, 끝까지 실행되는 코드, 실패 사례, 실제 문제 또는 로컬 완결형 연습을 함께 갖춥니다. 코드 문법 검사와 실행·점수 검증은 구분합니다.
- 기존 참고 노트의 일반 C++/STL 예제는 적용 환경을 표시합니다. 실전 트랙으로 연결하는 시점에 필요한 부분부터 공통 코드 방식으로 전환합니다.

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

위 순서는 앞으로 작성할 단위입니다. 공통 코드 기초 레슨의 첫 개편은 CHANGELOG에 기록했습니다. 다음 착수 단위는 **1번 ORDERING 중심의 첫 휴리스틱 실습**입니다.

### 목차와 연결도 함께 정리할 항목

- 기본 트랙의 표시 순서와 선수 관계를 맞춥니다. 현재 meldable-heap → union-find, heuristic → dynamic-programming, tsp-hamiltonian → graph-tree-basics, minimax-alpha-beta → testing-and-stress 등의 역순 의존을 확인하고, 실제 필수 지식과 선택 참고를 분리합니다.
- 휴리스틱 입문에 DP 전체나 고급 matching 이론을 필수 선수로 두는지 다시 판단합니다. 필요한 작은 개념은 해당 실습 안에서 설명합니다.
- 각 레슨의 선수·다음·연관 레슨을 h-contest 화면에서도 이동 가능한 학습 경로로 보여 주는 작업을 별도 UI 단위로 진행합니다.
- 기본 연습 ALLOCATE/CLUSTERX/MINEEXPLORE와 CITYSUM2D 등 이미 있는 문제를 해당 기초 레슨에 연결합니다. 단순 링크 추가가 아니라 계약과 풀이 연결 설명을 함께 작성합니다.
- 로그인 전 강의 접근은 h-contest 서비스에서 제한합니다. 원본 GitHub/Pages의 공개 범위는 별도 운영 정책이며, 서비스의 인증만으로 원본이 비공개가 되지는 않습니다.

새 고급 주제 추가는 아래 구조 개편 후보가 정리될 때까지 보류합니다. 새 주제는 허브 하나, 완성된 대표 페이지 하나, 실제 문제 또는 로컬 완결형 연습 하나를 함께 준비한 뒤 manifest에 추가합니다. 적절한 h-contest 문제가 없으면 임의 문제 ID를 넣지 말고 `TODO: /practice/... 문제 필요`로 남깁니다.

공개 목록은 `휴리스틱 기본 및 심화 노트`와 `휴리스틱 참고 노트` 두 분류로 유지합니다. 현재 h-contest 문제 풀이에 바로 쓰는 핵심/직접 심화 레슨은 `heuristic-notes`, 직접성이 낮은 전통 알고리즘/이론/희소 고급 도구/장기 확장용 레퍼런스는 `heuristic-reference`에 둡니다. `audience`는 레슨의 대상 독자를 나타내므로, 참고 노트에도 `contest-core` 또는 `advanced-contest` 레슨이 들어갈 수 있습니다. 그래프, 수학, 문자열 같은 세부 주제 구분은 별도 폴더를 늘리지 않고 태그, 선수/다음 레슨, 하위 페이지, 문제 신호별 길찾기에서 표현합니다.

## 구조 개편 후보

이미 공개된 심화 레슨 중 개념이 서로 가까운 묶음은 새 레슨을 더 추가하기 전에 허브화 또는 `pages/` 분할을 검토합니다.

| 우선순위 | 묶음 | 제안 | 상태 |
| ---: | --- | --- | --- |
| 1 | `alien-optimization`, `parametric-dp`, `fractional-programming-dp`, `lagrangian-relaxation-patterns` | 제약 완화/파라메트릭 최적화 허브로 penalty, count, ratio, lambda 패턴을 묶음 | 반영: `parametric-optimization` |
| 2 | `markov-decision-process`, `reinforcement-learning-basics`, `stochastic-shortest-path` | MDP/RL 허브 아래 value iteration, policy improvement, absorbing SSP를 분리 | 반영: `stochastic-decision-process` |
| 3 | `online-convex-optimization`, `dual-averaging` | online optimization 허브 아래 OGD, mirror descent, dual averaging 경로로 정리 | 반영: `online-convex-optimization` |
| 4 | `matroid-intersection`, `matroid-parity`, `matroid-union` | Matroid Algorithms 허브로 묶고 구현 완성도에 따라 reference/implementation을 구분 | 반영: `matroid-algorithms` |
| 5 | `global-min-cut`, `gomory-hu-tree`, `cut-sparsification`, `global-min-cut-applications`, `cactus-representation`, `randomized-min-cut`, `cut-cactus-applications` | Graph Cut Structures 허브로 s-t/global/all-pairs/family cut 경로를 정리 | 반영: `graph-cut-structures` |
| 6 | `persistent-segment-tree`, `persistent-lazy-segment-tree`, `persistent-union-find`, `persistent-queue-stack`, `persistent-sequence-queries` | Versioned Data Structures 허브로 persistence/rollback/retroactivity 경계와 구현별 선택 기준을 정리 | 반영: `versioned-data-structures` |
| 7 | `offline-queries`, `rollback-techniques`, `dynamic-connectivity`, `offline-range-query-techniques`, `retroactive-data-structures` | Offline and Time-Axis Techniques 허브로 query reordering, rollback, time segment tree, retroactivity 경계를 정리 | 반영: `offline-time-axis-techniques` |
| 8 | `convex-dp-modeling`, `convex-hull-trick-li-chao`, `convex-hull-trick-variants`, `cht-dp-applications`, `slope-trick`, `min-plus-convolution`, `kinetic-hull`, `fully-dynamic-cht` | Convex DP Optimization 허브로 전이식 기반 기법 선택 트리와 CHT/Slope/Min-Plus 세부 페이지를 정리 | 반영: `convex-dp-optimization` |
| 9 | `suffix-array-lcp`, `suffix-array-applications`, `suffix-automaton`, `suffix-automaton-applications`, `generalized-suffix-automaton`, `suffix-tree-ukkonen`, `runs-periodicity`, `border-automaton`, `string-period-query-applications` | Suffix and Periodicity Structures 허브로 suffix ordering, substring automaton, period query 선택 기준을 정리 | 반영: `suffix-periodicity-structures` |
| 10 | `palindromic-tree`, `palindrome-query-structures`, `palindrome-range-dp`, `suffix-palindrome-applications` | Palindrome Structures 허브로 회문 판정, 열거, 구간 DP, suffix-palindrome 응용 경계를 정리 | 반영: `palindrome-structures` |
| 11 | `fft-ntt`, `formal-power-series`, `fps-log-exp`, `multipoint-evaluation`, `polynomial-interpolation`, `generating-function-modeling`, `linear-recurrence-kitamasa`, `bostan-mori`, `linear-recurrence-applications`, `recurrence-guessing`, `berlekamp-massey` | Polynomial and Recurrence Algorithms 허브로 convolution/FPS/evaluation/generating function/recurrence 흐름을 정리 | 반영: `polynomial-recurrence-algorithms` |
| 12 | `stochastic-decision-process`, `monte-carlo-tree-search`, `imperfect-information-search`, `pomdp`, `point-based-value-iteration`, `pomcp`, `bayesian-bandits`, `online-planning-evaluation` | Probabilistic Decision AI 허브로 정확 MDP와 heuristic/simulator planning reference 경계를 정리 | 반영: `probabilistic-decision-ai` |
| 13 | `dynamic-flow`, `dynamic-mst`, `graph-cut-structures`, `offline-time-axis-techniques` | Dynamic Network Optimization 허브로 residual reuse, rebuild, offline interval, cut/cycle property 경계를 정리하고 graph cut과 MST의 순환 선수 관계를 제거 | 반영: `dynamic-network-optimization` |
| 14 | `robust-geometry-predicates`, `power-diagram`, `robust-delaunay`, `3d-convex-hull`, `regular-triangulation` | Geometry Robustness and Duality 허브로 predicate 안정성, weighted Voronoi, lifting, lower hull duality를 묶고 구현 위험도를 명확히 표시 | 반영: `geometry-robustness-and-duality` |
| 15 | `linear-basis-xor`, `linear-basis-applications`, `black-box-linear-algebra`, `sparse-linear-systems`, `linear-algebra-applications`, `randomized-determinant`, `matrix-tree-theorem-applications` | Linear Algebra Applications를 decision map 허브로 보강해 GF(2), linear system, determinant, sparse solver, graph counting 선택 기준을 먼저 제시 | 반영: `linear-algebra-applications` |

## 우선 추가할 주제

| 우선순위 | 후보 lessonId | 주제 | 연습 문제 상태 |
| ---: | --- | --- | --- |
| 1 | `spectral-graph-basics` | Laplacian eigenvalue, algebraic connectivity, random walk 관점으로 그래프 성질을 읽는 수학/그래프 연결 주제 | TODO: spectral graph `/practice/...` 문제 필요 |
| 2 | `sparse-determinant` | sparse matrix의 determinant/rank를 black-box linear algebra와 modular evaluation으로 계산하는 선형대수 주제 | TODO: sparse determinant `/practice/...` 문제 필요 |
| 3 | `additively-weighted-voronoi` | distance에 additive weight가 붙는 Voronoi variant와 shortest path/geometry 모델링 | TODO: weighted Voronoi `/practice/...` 문제 필요 |
| 4 | `arrangement-duality` | point-line duality와 arrangement level/query를 계산기하 문제 변환으로 다루는 주제 | TODO: arrangement duality `/practice/...` 문제 필요 |
| 5 | `policy-gradient-basics` | policy parameter, score function estimator, baseline을 contest simulator 평가 관점에서 정리하는 주제 | TODO: policy gradient `/practice/...` 문제 필요 |

## 추가 후보 묶음

| 영역 | 후보 lessonId |
| --- | --- |
| 문자열 | `string-period-query-applications` 이후 응용 후보 정리 필요 |
| 그래프 심화 | `spectral-graph-basics`, `algebraic-matching` |
| 자료구조/오프라인 | `persistent-sequence-queries` 이후 versioned sequence 응용 후보 정리 필요 |
| 수학 심화 | `spectral-graph-basics`, `sparse-determinant` |
| DP 최적화 | `convex-optimization-duality`, `risk-sensitive-dp` |
| 기하 | `additively-weighted-voronoi`, `arrangement-duality` |
| 게임/탐색 | `policy-gradient-basics`, `risk-sensitive-planning` |

## 공개 레슨으로 올리기 전 조건

1. `lessonType`이 `core` 또는 `implementation`이면 실제 문제, 끝까지 동작하는 구현, 정당성 설명, trace 또는 반례를 포함한다.
2. 실제 문제가 아직 없거나 구현이 부분적이면 `lessonType: overview` 또는 `reference`, `practiceStatus: todo`, `implementationStatus: partial`로 표시한다.
3. `lessons/<lessonId>/lesson.md` 또는 `pages/` 본문이 "읽기 -> 구현하기 -> 문제 풀기 -> 실수 점검하기" 흐름을 갖춘다.
4. C++ 구현 또는 의사 구현이 있고, 필요한 경우 `cpp compile-check` fence로 컴파일 검증 대상에 올린다.
5. `## 연습 문제` 표는 `단계`, `문제`, `목표`, `힌트 키워드` 열을 사용한다.
6. 적절한 h-contest 문제가 없으면 문제 칸에 `TODO: ... /practice/... 문제 필요`라고 남긴다.
7. 공개하기 전에 `python3 scripts/generate_catalog.py`와 `python3 scripts/validate_lessons.py`를 통과시킨다.
