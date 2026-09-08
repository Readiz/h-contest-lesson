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

이번 예시 정리에서 ORDERING을 휴리스틱의 첫 페이지로 옮기고 테스트 강의에 2-opt 차분·복구 대조 절차를 연결했습니다. 위 단계의 제출별 성능 기록과 실전 확장까지 완료한 것은 아닙니다. Digit DP, 구간 DP, Implicit Treap은 미완성 골격을 본문에 두지 않고, 실제 문제와 끝까지 동작하는 풀이가 준비될 때 다시 다룹니다.

### 목차와 연결도 함께 정리할 항목

- 기본 트랙의 표시 순서와 선수 관계를 맞춥니다. 현재 meldable-heap → union-find, heuristic → dynamic-programming, tsp-hamiltonian → graph-tree-basics, minimax-alpha-beta → testing-and-stress 등의 역순 의존을 확인하고, 실제 필수 지식과 선택 참고를 분리합니다.
- 휴리스틱 입문에 DP 전체나 고급 matching 이론을 필수 선수로 두는지 다시 판단합니다. 필요한 작은 개념은 해당 실습 안에서 설명합니다.
- 각 레슨의 선수·다음·연관 레슨을 h-contest 화면에서도 이동 가능한 학습 경로로 보여 주는 작업을 별도 UI 단위로 진행합니다.
- 기본 연습 ALLOCATE/CLUSTERX/MINEEXPLORE와 CITYSUM2D 등 이미 있는 문제를 해당 기초 레슨에 연결합니다. 단순 링크 추가가 아니라 계약과 풀이 연결 설명을 함께 작성합니다.
- 로그인 전 강의 접근은 h-contest 서비스에서 제한합니다. 원본 GitHub/Pages의 공개 범위는 별도 운영 정책이며, 서비스의 인증만으로 원본이 비공개가 되지는 않습니다.

새 고급 주제 추가는 아래 구조 개편 후보가 정리될 때까지 보류합니다. 새 주제는 허브 하나, 완성된 대표 페이지 하나, 실제 문제 또는 로컬 완결형 연습 하나를 함께 준비한 뒤 manifest에 추가합니다. 적절한 h-contest 문제가 없으면 임의 문제 ID나 빈 표를 본문에 넣지 말고 이 로드맵에 연습 후보를 남깁니다.

공개 목록은 `휴리스틱 기본 및 심화 노트`와 `휴리스틱 참고 노트` 두 분류로 유지합니다. 현재 h-contest 문제 풀이에 바로 쓰는 핵심/직접 심화 레슨은 `heuristic-notes`, 직접성이 낮은 전통 알고리즘/이론/희소 고급 도구/장기 확장용 레퍼런스는 `heuristic-reference`에 둡니다. `audience`는 레슨의 대상 독자를 나타내므로, 참고 노트에도 `contest-core` 또는 `advanced-contest` 레슨이 들어갈 수 있습니다. 그래프, 수학, 문자열 같은 세부 주제 구분은 별도 폴더를 늘리지 않고 태그, 선수/다음 레슨, 하위 페이지, 문제 신호별 길찾기에서 표현합니다.

## 기본 30개 강의의 연습 보강 대기

기존 본문의 빈 연습표를 이 목록으로 옮겼습니다. 아래 항목은 문제나 완결형 로컬 연습이 준비되면 본문에 연결할 후보이며, 네 단계 분량을 채우는 할당량이 아닙니다. `FUNCSUM1`·`SORTTEST`만으로 누적합·좌표 압축 실습을 대체하던 연결도 걷어냈습니다.

| 강의 | 아직 마련할 연습 후보 |
| --- | --- |
| [복잡도와 입력 크기 감각](lessons/complexity-input-size/lesson.md) | 반복문 횟수 직접 세기; 입력 제한 보고 풀이 후보 고르기; 여러 테스트 케이스 비용 계산; 큰 2차원 DP 테이블 검토 |
| [정렬 알고리즘](lessons/sorting/lesson.md) | 값과 인덱스 동반 정렬; 좌표 압축 전처리; 안정성이 필요한 다중 기준 정렬 |
| [누적합과 차분 배열](lessons/prefix-sum-difference/lesson.md) | 여러 구간 합 질의; 여러 구간 업데이트 후 최종 배열; 2차원 직사각형 합 |
| [그리디 알고리즘](lessons/greedy/lesson.md) | 회의실 배정; 마감이 있는 과제 선택; 그리디 반례 찾기 |
| [투 포인터와 슬라이딩 윈도우](lessons/two-pointers-sliding-window/lesson.md) | 두 수의 합 찾기; 합이 S 이상인 가장 짧은 양수 구간; 서로 다른 값이 K개 이하인 가장 긴 구간; 음수가 섞인 구간 합 |
| [이분 탐색과 파라메트릭 서치](lessons/binary-search/lesson.md) | 정렬 배열에서 lower_bound 찾기; 최소 가능한 답 찾기; 최대 거리/최소 시간 최적화; 실수형 이분 탐색 |
| [좌표 압축](lessons/coordinate-compression/lesson.md) | 압축 인덱스를 원래 입력 순서로 출력; inversion count; 구간 칠하기와 전체 길이 계산 |
| [우선순위 큐와 힙](lessons/priority-queue-heap/lesson.md) | 최댓값 반복 추출; 최솟값 후보를 계속 고르는 스케줄링; stale entry 제거; 같은 우선순위 tie-break |
| [Meldable Heap](lessons/meldable-heap/lesson.md) | 두 heap meld 연산 추적; 그룹별 최소값 조회; 여러 우선순위 큐 병합; pool 공유 실수 확인 |
| [동적 계획법](lessons/dynamic-programming/lesson.md) | 계단 오르기/피보나치 계열; 동전/0-1 배낭; LIS 또는 구간 DP; 비트마스크 DP |
| [TSP와 해밀턴 경로](lessons/tsp-hamiltonian/lesson.md) | 작은 해밀턴 경로 완전탐색; 비트마스크 TSP DP |
| [Union-Find 알고리즘](lessons/union-find/lesson.md) | Kruskal MST; rollback이 필요한 오프라인 연결성 |
| [BFS/DFS와 격자 탐색](lessons/bfs-dfs-grid/lesson.md) | 연결 요소 세기; 격자 최단거리; 여러 시작점 BFS; 위치에 방향/열쇠가 붙는 상태 그래프 |
| [그래프와 트리 기본 성질](lessons/graph-tree-basics/lesson.md) | 연결 요소 세기; 트리 지름/센트로이드; MST |
| [0-1 BFS](lessons/zero-one-bfs/lesson.md) | 무료 이동과 유료 이동이 있는 선형 그래프; 방향 전환 비용이 있는 격자 최단거리; 벽을 부수는 횟수를 최소화하는 미로; 비용이 0, 1, 2인 그래프 |
| [위상 정렬과 DAG DP](lessons/topological-sort-dag/lesson.md) | 작업 순서 출력; 사이클이면 불가능 판정; DAG 최장/최단 경로; 사전순 위상 정렬 |
| [Dijkstra 최단거리](lessons/dijkstra/lesson.md) | 모든 간선 비용이 1인 최단거리; 양수 가중치 그래프 최단거리; 다중 시작점과 단일 목표 최단거리; 음수 간선이 섞인 그래프 |
| [Bellman-Ford와 음수 사이클](lessons/bellman-ford-negative-cycle/lesson.md) | 음수 간선이 있지만 음수 사이클은 없는 최단거리; 음수 사이클 존재 판정; 목표 정점의 음수 사이클 영향 판정; 음수 간선이 있는 DAG 최단거리 |
| [Floyd-Warshall](lessons/floyd-warshall/lesson.md) | 모든 쌍 최단거리; 도달 가능성 전파; 최단 경로 복원; 음수 사이클 영향 |
| [Sqrt Decomposition](lessons/sqrt-decomposition/lesson.md) | 정적 구간 합 질의; 구간에서 k보다 작은 원소 개수; Mo's Algorithm |
| [Fenwick Tree](lessons/fenwick-tree/lesson.md) | 점 업데이트 + prefix 합; 점 업데이트 + 구간 합; inversion count; k번째 원소 찾기 |
| [Segment Tree](lessons/segment-tree/lesson.md) | 점 업데이트 + 구간 합; 구간 최솟값 + 구간 덧셈; 구간 대입과 덧셈의 합성 |
| [Hungarian Algorithm](lessons/hungarian-algorithm/lesson.md) | 작은 assignment problem; forbidden edge가 있는 sparse assignment |
| [Treap과 BST 기본](lessons/treap/lesson.md) | BST inorder 순회; k번째 원소/순위 질의; 구간 뒤집기 Implicit Treap; 중복 key 처리 |
| [Minimax와 Alpha-Beta Pruning](lessons/minimax-alpha-beta/lesson.md) | 작은 게임 minimax; alpha-beta pruning; depth-limited game search; 반복 상태 게임 |
| [Testing과 Stress Test](lessons/testing-and-stress/lesson.md) | 배열 구간 질의와 brute force 비교; 그리디 후보 풀이의 반례 찾기; 기하/그래프의 edge case 수집; 빠른 풀이와 brute force가 같은 버그를 공유하는 사례 |
| [Proof와 Invariant](lessons/proof-and-invariants/lesson.md) | 이분 탐색 invariant 작성; exchange argument로 그리디 선택 증명; DP 상태 정의와 전이 완전성 설명; 틀린 그리디의 최소 반례 찾기 |
| [Dynamic Segment Tree](lessons/dynamic-segment-tree/lesson.md) | sparse point update; 큰 좌표 range add sum; online rectangle sweep; persistent sparse query |

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
3. 구체적인 문제 상황과 예시에서 구현으로 이어진다. 조건은 사용 지점에 설명하며, 같은 내용을 결론·실수 표·체크리스트로 반복하지 않는다.
4. C++ 구현 또는 의사 구현이 있고, 필요한 경우 `cpp compile-check` fence로 컴파일 검증 대상에 올린다.
5. 연습은 실제 문제나 완결형 로컬 과제로 연결한다. 목차, 표 형식, 네 단계 분량은 강제하지 않는다.
6. 미완성 연습은 이 문서에 남긴다. 기본 30개 강의 본문에는 `TODO` 표나 빈 연습 페이지를 두지 않는다.
7. 공개하기 전에 `python3 scripts/generate_catalog.py`와 `python3 scripts/validate_lessons.py`를 통과시킨다.

## 참고 70개 강의의 연습 보강 대기

본문에서 미완성 표를 옮겼습니다. 아래 후보는 실제 문제 또는 입력·과제·확인 방법이 갖춰진 로컬 연습을 준비한 뒤 본문에 연결합니다. 기존의 목표와 힌트는 후보별로 보존하며, 단계별 분량을 채우기 위한 목록으로 사용하지 않습니다.

### [모듈러 연산과 빠른 거듭제곱](lessons/modular-arithmetic/lesson.md)

- TODO: 큰 피보나치 수를 mod로 출력하는 문제 추가 / DP 전이마다 mod 적용 / mod 덧셈
- TODO: `a^b mod M` 문제 추가 / 빠른 거듭제곱 구현 / binary exponentiation
- TODO: 여러 `nCr` 질의 문제 추가 / factorial과 inverse factorial 전처리 / Fermat inverse
- TODO: 포함-배제 경우의 수 문제 추가 / 음수 나머지 정규화 / negative modulo

### [SCC와 2-SAT](lessons/scc-2sat/lesson.md)

- TODO: 방향 그래프의 SCC 개수를 세는 문제 추가 / Kosaraju 두 번의 DFS 흐름 익히기 / finish order, reversed graph
- TODO: SCC 압축 DAG를 만드는 문제 추가 / 컴포넌트 번호와 중복 간선 정리 / condensation graph
- TODO: 2-SAT 만족 가능성 판정 문제 추가 / OR 절을 implication 두 개로 변환 / implication graph
- TODO: 실제 boolean 배정을 출력하는 문제 추가 / SCC 번호 방향과 값 복원 검증 / assignment reconstruction

### [Max Flow, Min Cut, Bipartite Matching](lessons/max-flow-min-cut/lesson.md)

- TODO: source에서 sink까지 최대 유량을 구하는 문제 추가 / Dinic level graph와 residual edge 구현 / max flow, residual graph
- TODO: 이분 그래프 최대 매칭 문제 추가 / source-left-right-sink 모델링 / bipartite matching
- TODO: 정점 용량이 있는 경로 선택 문제 추가 / vertex split으로 capacity 표현 / node capacity
- TODO: min cut 간선을 출력하는 문제 추가 / residual reachable과 원래 capacity 구분 / min cut

### [Matching과 Cover Duality](lessons/matching-cover-duality/lesson.md)

- TODO: 기본 이분 매칭 `/practice/...` 문제 필요 / augmenting path 매칭 구현 / bipartite matching
- TODO: minimum vertex cover `/practice/...` 문제 필요 / alternating path로 cover 복원 / Konig theorem
- TODO: DAG path cover `/practice/...` 문제 필요 / split graph와 `N - matching` / path cover
- TODO: maximum independent set 변환 `/practice/...` 문제 필요 / vertex cover의 보수 출력 / independent set

### [Min-Cost Flow](lessons/min-cost-flow/lesson.md)

- TODO: 정해진 유량의 최소 비용 `/practice/...` 문제 필요 / residual cost와 역방향 비용 구현 / shortest augmenting path
- TODO: assignment 모델링 `/practice/...` 문제 필요 / worker-job-sink capacity 1 모델 / assignment
- TODO: 이익 최대화 매칭 `/practice/...` 문제 필요 / profit을 음수 cost로 변환 / negative cost
- TODO: 불가능한 요구 유량 `/practice/...` 문제 필요 / `totalFlow == requiredFlow` 확인 / infeasible flow

### [Flow with Lower Bound](lessons/flow-with-lower-bound/lesson.md)

- TODO: lower bound feasibility `/practice/...` 문제 필요 / demand 배열과 super source/sink 구성 / feasible circulation
- TODO: 수요가 있는 배정 `/practice/...` 문제 필요 / job lower/upper 모델링 / bounded assignment
- TODO: s-t lower bound max flow `/practice/...` 문제 필요 / `t -> s` 간선과 추가 max flow / bounded st flow
- TODO: 실제 flow 복원 `/practice/...` 문제 필요 / lower + residual 사용량 계산 / flow reconstruction

### [General Matching](lessons/general-matching/lesson.md)

- TODO: 일반 그래프 matching 판정 `/practice/...` 문제 필요 / augmenting path와 blossom 수축 흐름 추적 / Edmonds blossom
- TODO: maximum cardinality matching `/practice/...` 문제 필요 / 구현으로 최대 matching 크기 계산 / general matching
- TODO: perfect matching 존재 `/practice/...` 문제 필요 / matching 크기와 정점 수 비교 / perfect matching
- TODO: 이분 그래프가 아닌 반례 `/practice/...` 문제 필요 / odd cycle 때문에 bipartite matching이 깨지는 사례 확인 / odd cycle

### [Sparse Table과 RMQ](lessons/sparse-table-rmq/lesson.md)

- TODO: 정적 RMQ `/practice/...` 문제 필요 / `2^k` table과 `O(1)` min 질의 구현 / sparse table
- TODO: LCP 구간 최솟값 `/practice/...` 문제 필요 / suffix rank 사이 RMQ 처리 / lcp rmq
- TODO: Euler Tour LCA `/practice/...` 문제 필요 / depth 배열의 argmin RMQ / euler tour
- TODO: 비-idempotent 연산 구분 `/practice/...` 문제 필요 / 겹침 질의 가능 여부 판단 / idempotent

### [Dominator Tree](lessons/dominator-tree/lesson.md)

- TODO: 필수 관문 판정 `/practice/...` 문제 필요 / dominate 정의와 tree ancestor 연결 / dominator
- TODO: immediate dominator tree `/practice/...` 문제 필요 / Lengauer-Tarjan 구현 / idom
- TODO: 지배하는 정점 수 `/practice/...` 문제 필요 / dominator tree subtree size / dominance subtree
- TODO: 도달 불가능 정점 포함 `/practice/...` 문제 필요 / reachable filtering / flow graph

### [Weighted Matching](lessons/weighted-matching/lesson.md)

- TODO: small weighted perfect matching `/practice/...` 문제 필요 / bitmask DP로 일반 그래프 처리 / weighted matching
- TODO: assignment problem `/practice/...` 문제 필요 / Hungarian 또는 Min-Cost Flow 모델링 / bipartite matching
- TODO: maximum cardinality 후 weight `/practice/...` 문제 필요 / 큰 상수 tie-break / lexicographic objective
- TODO: 음수 weight matching `/practice/...` 문제 필요 / unmatched 허용 여부 확인 / negative weight

### [Directed MST](lessons/directed-mst/lesson.md)

- TODO: directed arborescence cost `/practice/...` 문제 필요 / 각 정점 incoming edge 선택 / directed MST
- TODO: Chu-Liu/Edmonds `/practice/...` 문제 필요 / cycle 수축 구현 / Edmonds
- TODO: super root arborescence `/practice/...` 문제 필요 / 루트 후보 모델링 / super root
- TODO: unreachable directed MST `/practice/...` 문제 필요 / 불가능 판정 / incoming edge

### [Persistent Lazy Segment Tree](lessons/versioned-data-structures/pages/persistent-lazy-segment-tree.md)

- TODO: versioned range add sum `/practice/...` 문제 필요 / clone 후 lazy 적용 / persistent lazy segment tree
- TODO: 과거 버전 range query `/practice/...` 문제 필요 / root 배열 관리 / version root
- TODO: branching update history `/practice/...` 문제 필요 / 임의 version에서 새 version 생성 / full persistence
- TODO: read-only query 검증 `/practice/...` 문제 필요 / lazy carry 방식 / pure query

### [Persistent Queue and Stack](lessons/versioned-data-structures/pages/persistent-queue-stack.md)

- TODO: persistent stack `/practice/...` 문제 필요 / root pointer와 parent 저장 / version root
- TODO: kth in persistent stack `/practice/...` 문제 필요 / binary lifting 추가 / ancestor
- TODO: persistent queue `/practice/...` 문제 필요 / head/tail version 관리 / persistent sequence
- TODO: rollback vs persistence `/practice/...` 문제 필요 / branching version 판별 / undo log

### [Persistent Segment Tree](lessons/versioned-data-structures/pages/persistent-segment-tree.md)

- TODO: 버전별 구간 합 `/practice/...` 문제 필요 / path copying과 root 저장 구현 / persistent root
- TODO: 구간 k번째 수 `/practice/...` 문제 필요 / prefix root 차이와 좌표 압축 / kth query
- TODO: 과거 버전 분기 업데이트 `/practice/...` 문제 필요 / 특정 버전에서 새 버전 생성 / version tree
- TODO: 메모리 제한이 빡빡한 persistent tree `/practice/...` 문제 필요 / node 수와 값 타입 계산 / memory budget

### [Persistent Sequence Queries](lessons/versioned-data-structures/pages/persistent-sequence-queries.md)

- TODO: persistent array `/practice/...` 문제 필요 / point update version 보존 / path copying
- TODO: persistent kth query `/practice/...` 문제 필요 / prefix root 차이 / order statistic
- TODO: persistent sequence `/practice/...` 문제 필요 / split/merge로 중간 삽입 처리 / implicit treap
- TODO: persistent lazy query `/practice/...` 문제 필요 / lazy tag 복사 조건 / range update

### [Persistent Union-Find](lessons/versioned-data-structures/pages/persistent-union-find.md)

- TODO: persistent union-find `/practice/...` 문제 필요 / 과거 연결성 조회 / union time
- TODO: versioned component size `/practice/...` 문제 필요 / size history 이분 탐색 / component size
- TODO: offline connectivity versions `/practice/...` 문제 필요 / rollback과 persistence 선택 / query time
- TODO: path compression counterexample `/practice/...` 문제 필요 / parent 변경 이력 보존 / no compression

### [Practice Set](lessons/versioned-data-structures/pages/practice-set.md)

- TODO: 버전별 구간 합 `/practice/...` 문제 필요 / path copying과 root 저장 / persistent segment tree
- TODO: persistent union-find `/practice/...` 문제 필요 / 과거 연결성 조회 / union time
- TODO: persistent sequence `/practice/...` 문제 필요 / split/merge 또는 version root 관리 / implicit treap
- TODO: rollback vs persistence `/practice/...` 문제 필요 / version branch와 undo log 구분 / rollback

### [Wavelet Tree](lessons/wavelet-tree/lesson.md)

- TODO: 구간 kth `/practice/...` 문제 필요 / `prefixLeft`로 child index 변환 / kth order statistic
- TODO: 구간 `<= x` 개수 `/practice/...` 문제 필요 / 값 범위 재귀와 rank query / range rank
- TODO: 구간 frequency `/practice/...` 문제 필요 / `<= x`와 `< x` 차이 / frequency
- TODO: 좌표 압축 wavelet `/practice/...` 문제 필요 / 압축 값 복원과 큰 값 범위 / compression

### [Wavelet Matrix](lessons/wavelet-matrix/lesson.md)

- TODO: range kth query `/practice/...` 문제 필요 / kth 이동 공식 구현 / wavelet matrix kth
- TODO: 구간 값 빈도 `/practice/...` 문제 필요 / `countLess(high) - countLess(low)` 사용 / range frequency
- TODO: 구간 median `/practice/...` 문제 필요 / median을 kth로 변환 / range quantile
- TODO: 음수 좌표 wavelet matrix `/practice/...` 문제 필요 / 좌표 압축과 값 복원 / coordinate compression

### [Succinct Bitvector](lessons/succinct-bitvector/lesson.md)

- TODO: bitvector rank `/practice/...` 문제 필요 / raw bit와 prefix rank 구현 / rank
- TODO: select query `/practice/...` 문제 필요 / binary search select / select
- TODO: wavelet matrix memory 개선 `/practice/...` 문제 필요 / level bitvector 압축 / succinct
- TODO: padding bit 처리 `/practice/...` 문제 필요 / 마지막 word mask / bit operation

### [트리 심화: 분할 기법](lessons/tree-advanced/lesson.md)

- TODO: subtree 합 질의 문제 추가 / Euler Tour로 subtree를 연속 구간으로 변환 / `tin`, `subtree`
- TODO: LCA와 거리 질의 문제 추가 / binary lifting 전처리와 깊이 맞추기 / LCA, depth
- TODO: 경로 질의 문제 추가 / HLD로 경로를 여러 구간으로 분해 / chain, segment tree
- TODO: 센트로이드 분할 거리 후보 문제 추가 / 제거된 centroid 표시와 거리 캐시 관리 / centroid decomposition

### [AVL과 Splay Tree 참고](lessons/avl-splay-tree/lesson.md)

- TODO: AVL 회전 trace 문제 필요 / LL/RR/LR/RL 회전 순서 확인 / balance factor
- TODO: Splay 접근 trace 문제 필요 / zig, zig-zig, zig-zag 구분 / amortized BST
- TODO: Link-Cut Tree 보조 연습 필요 / Splay lazy reverse와 aggregate 연결 / auxiliary tree

### [Link-Cut Tree](lessons/link-cut-tree/lesson.md)

- TODO: dynamic forest connectivity `/practice/...` 문제 필요 / link/cut/findRoot 구현 / link-cut tree
- TODO: dynamic tree path sum `/practice/...` 문제 필요 / makeroot-access path query / splay aggregate
- TODO: dynamic MST edge replacement `/practice/...` 문제 필요 / edge node 모델링 / dynamic forest
- TODO: repeated cut invalid edge `/practice/...` 문제 필요 / 직접 간선 확인 / cut validation

### [문자열 매칭: KMP, Z, Rolling Hash](lessons/string-matching-kmp-z/lesson.md)

- TODO: 한 패턴의 등장 위치를 모두 찾는 문제 추가 / KMP 실패 함수와 겹치는 매칭 처리 / prefix function
- TODO: 접두사 일치 길이를 이용하는 문자열 분석 문제 추가 / Z function의 `[left, right]` 구간 재사용 / Z-box
- TODO: 많은 부분 문자열 비교 문제 추가 / Rolling Hash 전처리와 구간 해시 비교 / double hash
- TODO: 해시 충돌 또는 separator 경계가 중요한 문제 추가 / 정확 알고리즘과 해시 후보 검증 구분 / collision, separator

### [Trie와 Aho-Corasick](lessons/trie-aho-corasick/lesson.md)

- TODO: Trie 사전 조회 `/practice/...` 문제 필요 / 단어 삽입과 prefix 탐색 구현 / trie node
- TODO: 다중 패턴 등장 여부 `/practice/...` 문제 필요 / 실패 링크와 출력 전파 구현 / fail link
- TODO: 각 패턴별 등장 횟수 `/practice/...` 문제 필요 / fail tree 누적과 terminal id 관리 / occurrence count
- TODO: 금지 문자열 DP `/practice/...` 문제 필요 / automaton 상태와 DP 결합 / forbidden pattern

### [Border Automaton](lessons/suffix-periodicity-structures/pages/border-automaton.md)

- TODO: border automaton `/practice/...` 문제 필요 / KMP 전이표 구성 / prefix function
- TODO: forbidden pattern DP `/practice/...` 문제 필요 / accepting state 제외 / automaton DP
- TODO: online pattern counter `/practice/...` 문제 필요 / stream transition / border state
- TODO: overlapping occurrence `/practice/...` 문제 필요 / match 후 fallback / pi chain

### [Generalized Suffix Automaton](lessons/suffix-periodicity-structures/pages/generalized-suffix-automaton.md)

- TODO: generalized suffix automaton `/practice/...` 문제 필요 / 여러 문자열 LCS / state별 match length
- TODO: at least K strings substring `/practice/...` 문제 필요 / coverage count / suffix link propagation
- TODO: group substring difference `/practice/...` 문제 필요 / 그룹별 mask 집계 / bitset aggregation
- TODO: separator crossing substring `/practice/...` 문제 필요 / separator 제거 / per-string scan

### [Practice Set](lessons/suffix-periodicity-structures/pages/practice-set.md)

- TODO: suffix array pattern search `/practice/...` 문제 필요 / suffix 정렬과 lower_bound / suffix array
- TODO: repeated substring `/practice/...` 문제 필요 / LCP maximum과 occurrence 조건 / LCP RMQ
- TODO: longest common substring `/practice/...` 문제 필요 / generalized SAM 또는 separator SA / source mask
- TODO: period query `/practice/...` 문제 필요 / prefix function, border, runs / period
- TODO: suffix tree traversal `/practice/...` 문제 필요 / explicit edge와 depth / Ukkonen

### [Runs와 문자열 주기](lessons/suffix-periodicity-structures/pages/runs-periodicity.md)

- TODO: 문자열 전체 반복 판정 `/practice/...` 문제 필요 / longest border로 minimal period 계산 / prefix function
- TODO: 모든 border 길이 `/practice/...` 문제 필요 / failure link chain 순회 / border tree
- TODO: 반복 substring 개수 `/practice/...` 문제 필요 / LCP와 period 후보 결합 / periodic substring
- TODO: maximal run 판정 `/practice/...` 문제 필요 / 좌우 확장 가능성과 minimal period 구분 / runs theorem

### [String Period Query Applications](lessons/suffix-periodicity-structures/pages/string-period-query-applications.md)

- TODO: string period query `/practice/...` 문제 필요 / 후보 period 검증 / substring equality
- TODO: range minimal period `/practice/...` 문제 필요 / 약수 후보와 hash 결합 / rolling hash
- TODO: repeated substring query `/practice/...` 문제 필요 / LCP/LCS로 확장 길이 계산 / suffix array RMQ
- TODO: maximal run query `/practice/...` 문제 필요 / maximality와 중복 제거 / runs

### [Suffix Array 응용 패턴](lessons/suffix-periodicity-structures/pages/suffix-array-applications.md)

- TODO: 패턴 등장 구간 `/practice/...` 문제 필요 / suffix array binary search / pattern interval
- TODO: k번째 substring `/practice/...` 문제 필요 / 새 substring 수 누적 / lexicographic kth
- TODO: 여러 문자열 LCS `/practice/...` 문제 필요 / source id sliding window / multi-string suffix
- TODO: non-overlap 반복 substring `/practice/...` 문제 필요 / LCP와 위치 차이 동시 확인 / repeated substring

### [Suffix Array와 LCP](lessons/suffix-periodicity-structures/pages/suffix-array-lcp.md)

- TODO: suffix array 생성 `/practice/...` 문제 필요 / doubling 순위 갱신 구현 / rank pair
- TODO: 가장 긴 반복 부분 문자열 `/practice/...` 문제 필요 / LCP 배열의 최댓값 해석 / Kasai
- TODO: 서로 다른 부분 문자열 수 `/practice/...` 문제 필요 / 전체 부분 문자열 수에서 LCP 합 제거 / distinct substrings
- TODO: 여러 문자열 공통 부분 문자열 `/practice/...` 문제 필요 / 구분자와 suffix 출처 관리 / separator, source id

### [Suffix Automaton Applications](lessons/suffix-periodicity-structures/pages/suffix-automaton-applications.md)

- TODO: suffix automaton applications `/practice/...` 문제 필요 / occurrence 누적 / suffix link order
- TODO: kth substring `/practice/...` 문제 필요 / transition DAG DP / lexicographic path
- TODO: repeated substring query `/practice/...` 문제 필요 / occurrence threshold / endpos
- TODO: multiple strings LCS `/practice/...` 문제 필요 / state별 match 전파 / generalized scan

### [Suffix Automaton](lessons/suffix-periodicity-structures/pages/suffix-automaton.md)

- TODO: 서로 다른 부분 문자열 수 `/practice/...` 문제 필요 / `len[v] - len[link[v]]` 합 계산 / distinct substrings
- TODO: 패턴 포함 여부 다중 질의 `/practice/...` 문제 필요 / automaton transition 탐색 / substring query
- TODO: 두 문자열 LCS `/practice/...` 문제 필요 / suffix link로 matched 길이 줄이기 / lcs on sam
- TODO: 등장 횟수 집계 `/practice/...` 문제 필요 / clone count 0과 길이 내림차순 누적 / occurrence

### [Suffix Tree와 Ukkonen](lessons/suffix-periodicity-structures/pages/suffix-tree-ukkonen.md)

- TODO: suffix tree construction `/practice/...` 문제 필요 / 압축 간선과 sentinel 이해 / suffix tree
- TODO: pattern occurrence subtree `/practice/...` 문제 필요 / pattern 경로 아래 leaf 수 세기 / subtree leaves
- TODO: generalized suffix tree LCS `/practice/...` 문제 필요 / 여러 문자열 공통 substring / unique sentinel
- TODO: repeated string implicit tree `/practice/...` 문제 필요 / sentinel 없는 경우 비교 / implicit suffix tree

### [Palindrome Query Structures](lessons/palindrome-structures/pages/palindrome-query-structures.md)

- TODO: palindrome query `/practice/...` 문제 필요 / Manacher radius 판정 / odd/even center
- TODO: dynamic palindrome hash `/practice/...` 문제 필요 / update와 구간 판정 / forward/reverse hash
- TODO: palindrome occurrence `/practice/...` 문제 필요 / Eertree occurrence / suffix link aggregation
- TODO: even palindrome off-by-one `/practice/...` 문제 필요 / 중심 좌표 검증 / radius indexing

### [Palindrome Range DP](lessons/palindrome-structures/pages/palindrome-range-dp.md)

- TODO: palindrome partition `/practice/...` 문제 필요 / `isPal` table + prefix DP / last piece
- TODO: minimum insertion palindrome `/practice/...` 문제 필요 / interval DP 반복 순서 / both ends
- TODO: palindrome range DP `/practice/...` 문제 필요 / Manacher 판정과 DP 결합 / radius query
- TODO: cuts vs pieces `/practice/...` 문제 필요 / 출력 convention 확인 / off-by-one

### [Palindromic Tree](lessons/palindrome-structures/pages/palindromic-tree.md)

- TODO: 서로 다른 palindrome 개수 `/practice/...` 문제 필요 / 새 노드 개수 세기 / eertree
- TODO: palindrome 등장 횟수 `/practice/...` 문제 필요 / suffix link 역순 count 누적 / occurrence
- TODO: prefix별 palindrome 통계 `/practice/...` 문제 필요 / 온라인 추가와 last 관리 / palindromic suffix
- TODO: 큰 alphabet palindrome `/practice/...` 문제 필요 / transition 구조 변경 / alphabet mapping

### [Practice Set](lessons/palindrome-structures/pages/practice-set.md)

- TODO: palindrome query `/practice/...` 문제 필요 / Manacher 또는 hash 판정 / radius
- TODO: online palindrome statistics `/practice/...` 문제 필요 / suffix link 누적 / Eertree count
- TODO: palindrome partition `/practice/...` 문제 필요 / range DP / palindrome table
- TODO: suffix palindrome application `/practice/...` 문제 필요 / suffix 구조와 회문 보조 정보 결합 / suffix + palindrome

### [Suffix와 Palindrome 응용](lessons/palindrome-structures/pages/suffix-palindrome-applications.md)

- TODO: 서로 다른 substring 개수 `/practice/...` 문제 필요 / SAM 기여 또는 SA LCP 합 사용 / distinct substring
- TODO: 최장 공통 substring `/practice/...` 문제 필요 / SAM walk 또는 combined SA / longest common substring
- TODO: palindrome occurrence `/practice/...` 문제 필요 / Eertree count 누적 / palindromic tree
- TODO: 여러 문자열 substring `/practice/...` 문제 필요 / separator와 source id 관리 / multi-string suffix

### [Lyndon Factorization](lessons/lyndon-factorization/lesson.md)

- TODO: Lyndon factorization 출력 `/practice/...` 문제 필요 / Duval algorithm 구현 / Lyndon word
- TODO: 최소 회전 `/practice/...` 문제 필요 / `s+s`와 Duval/Booth 연결 / minimum rotation
- TODO: 문자열 분해 기반 비교 `/practice/...` 문제 필요 / factor sequence 활용 / lexicographic decomposition
- TODO: 반복 문자 circular string `/practice/...` 문제 필요 / 동률 회전 처리 / periodic string

### [기하 기본: CCW, 선분 교차, Convex Hull](lessons/geometry-ccw-segment-intersection/lesson.md)

- TODO: 세 점의 방향을 판정하는 문제 추가 / 외적 부호와 `long long` 감각 익히기 / CCW, cross product
- TODO: 두 선분의 교차 여부를 판정하는 문제 추가 / 일직선과 끝점 접촉 처리 / segment intersection
- TODO: 점 집합의 convex hull을 구하는 문제 추가 / monotonic chain과 collinear 정책 확인 / convex hull
- TODO: 경계 위 모든 점 포함 여부가 갈리는 문제 추가 / `<= 0`와 `< 0` 조건 차이 체감 / collinear boundary

### [Rotating Calipers](lessons/rotating-calipers/lesson.md)

- TODO: Convex Hull 지름 `/practice/...` 문제 필요 / antipodal pair와 제곱 거리 계산 / diameter
- TODO: 가장 먼 두 점 `/practice/...` 문제 필요 / hull 생성 후 calipers 적용 / farthest pair
- TODO: 볼록 다각형 폭 `/practice/...` 문제 필요 / 변-점 높이와 외적 비교 / width
- TODO: collinear 경계 점 처리 `/practice/...` 문제 필요 / hull 정책과 작은 입력 처리 / collinear, edge case

### [Sweep Line Geometry](lessons/sweep-line-geometry/lesson.md)

- TODO: 직사각형 합집합 넓이 `/practice/...` 문제 필요 / x 이벤트와 y cover length 관리 / rectangle union
- TODO: 점과 구간 포함 질의 `/practice/...` 문제 필요 / 이벤트 순서와 active count / offline sweep
- TODO: 선분 교차 존재 판정 `/practice/...` 문제 필요 / active set의 이웃만 검사 / segment intersection
- TODO: 같은 좌표 이벤트가 많은 sweep `/practice/...` 문제 필요 / tie-breaking과 grouped events / event order

### [Closest Pair Sweep](lessons/closest-pair-sweep/lesson.md)

- TODO: closest pair 기본 `/practice/...` 문제 필요 / 정렬과 active set 유지 / closest pair
- TODO: 중복 점 포함 closest pair `/practice/...` 문제 필요 / 답 0 처리와 index key / duplicate points
- TODO: 가장 가까운 점 쌍 복원 `/practice/...` 문제 필요 / best pair 저장 / pair restore
- TODO: 큰 좌표 closest pair `/practice/...` 문제 필요 / 거리 제곱 overflow 점검 / squared distance

### [Line Arrangement](lessons/line-arrangement/lesson.md)

- TODO: 직선 arrangement 영역 수 `/practice/...` 문제 필요 / 중복/평행 제거와 교점 count / line arrangement
- TODO: concurrency 포함 교점 수 `/practice/...` 문제 필요 / 같은 교점 dedup / rational point
- TODO: 선분 arrangement face count `/practice/...` 문제 필요 / vertex/edge/face 계산 / Euler formula
- TODO: overlap segment `/practice/...` 문제 필요 / 같은 직선 위 겹침 처리 / degeneracy

### [Voronoi와 Delaunay](lessons/voronoi-delaunay/lesson.md)

- TODO: circumcircle 판정 `/practice/...` 문제 필요 / in-circle determinant 구현 / Delaunay predicate
- TODO: Voronoi cell 반평면 `/practice/...` 문제 필요 / 수직이등분선과 HPI 모델링 / Voronoi cell
- TODO: Euclidean MST 후보 축소 `/practice/...` 문제 필요 / Delaunay edge 성질 활용 / EMST
- TODO: cocircular points `/practice/...` 문제 필요 / triangulation non-unique 처리 / degeneracy

### [Half-Plane Intersection](lessons/half-plane-intersection/lesson.md)

- TODO: convex polygon clipping `/practice/...` 문제 필요 / 한 반평면씩 polygon 자르기 / clipping
- TODO: half-plane intersection `/practice/...` 문제 필요 / angle sort와 deque 구현 / HPI
- TODO: Voronoi cell area `/practice/...` 문제 필요 / 수직이등분선 반평면 구성 / Voronoi cell
- TODO: unbounded feasible region `/practice/...` 문제 필요 / bounding box 처리 / unbounded

### [정수론 심화: GCD, Extended Euclid, CRT, Sieve](lessons/gcd-extended-euclid-crt/lesson.md)

- TODO: gcd와 lcm을 반복 계산하는 문제 추가 / 유클리드 알고리즘과 overflow 확인 / gcd, lcm
- TODO: 합성수 mod에서 역원을 판정하는 문제 추가 / extended gcd와 역원 존재 조건 / modular inverse
- TODO: 여러 합동식을 합치는 문제 추가 / 일반 CRT의 모순 조건 처리 / CRT
- TODO: 많은 수를 소인수분해하는 질의 문제 추가 / SPF 전처리와 반복 분해 / sieve, factorization

### [조합론: nCr, 포함-배제, Lucas](lessons/combinatorics-ncr/lesson.md)

- TODO: 여러 `nCr mod` 질의 `/practice/...` 문제 필요 / factorial과 inverse factorial 전처리 / nCr
- TODO: 빈 상자 없는 배치 `/practice/...` 문제 필요 / 포함-배제 공식 세우기 / inclusion-exclusion
- TODO: 큰 `n`, 작은 소수 mod `/practice/...` 문제 필요 / Lucas 정리 적용 / Lucas theorem
- TODO: 합성수 mod 조합 `/practice/...` 문제 필요 / Fermat 역원 조건 구분 / composite mod

### [Matrix Exponentiation](lessons/matrix-exponentiation/lesson.md)

- TODO: 피보나치 큰 n `/practice/...` 문제 필요 / 2x2 전이 행렬과 빠른 거듭제곱 / fibonacci matrix
- TODO: k차 선형 점화식 `/practice/...` 문제 필요 / companion matrix 구성 / linear recurrence
- TODO: 길이 K walk 수 `/practice/...` 문제 필요 / 인접 행렬의 K제곱 해석 / graph walks
- TODO: 상수항 포함 전이 `/practice/...` 문제 필요 / 상태 벡터에 1 추가 / affine transform

### [Berlekamp-Massey](lessons/polynomial-recurrence-algorithms/pages/berlekamp-massey.md)

- TODO: Berlekamp-Massey basics `/practice/...` 문제 필요 / 최소 recurrence 찾기 / discrepancy
- TODO: BM + Kitamasa `/practice/...` 문제 필요 / 큰 n번째 항 계산 / nth term
- TODO: graph walk BM `/practice/...` 문제 필요 / sparse 항 생성 / Cayley-Hamilton
- TODO: composite mod recurrence `/practice/...` 문제 필요 / field 조건 확인 / modular inverse

### [Bostan-Mori](lessons/polynomial-recurrence-algorithms/pages/bostan-mori.md)

- TODO: rational generating function 계수 `/practice/...` 문제 필요 / `P/Q`에서 n번째 계수 추출 / Bostan-Mori
- TODO: 선형 점화식 n번째 항 `/practice/...` 문제 필요 / `Q(x)=1-cx...` 구성 / linear recurrence
- TODO: 조합 생성함수 계수 `/practice/...` 문제 필요 / 분모/분자 모델링 / generating function
- TODO: `Q(0) != 1` 보정 `/practice/...` 문제 필요 / constant inverse 처리 / normalization

### [FFT와 NTT](lessons/polynomial-recurrence-algorithms/pages/fft-ntt.md)

- TODO: 다항식 곱셈 `/practice/...` 문제 필요 / NTT 입출력과 결과 길이 처리 / polynomial multiplication
- TODO: 합이 k인 쌍 개수 `/practice/...` 문제 필요 / 빈도 배열 convolution / pair sum
- TODO: 차이별 pair count `/practice/...` 문제 필요 / 한쪽 배열 뒤집기와 offset / reversed convolution
- TODO: 다른 mod의 convolution `/practice/...` 문제 필요 / FFT 또는 여러 NTT mod 선택 / arbitrary modulus

### [Formal Power Series](lessons/polynomial-recurrence-algorithms/pages/formal-power-series.md)

- TODO: polynomial derivative/integral `/practice/...` 문제 필요 / 계수 index와 modular inverse 처리 / FPS basics
- TODO: polynomial inverse `/practice/...` 문제 필요 / Newton iteration 구현 / inverse FPS
- TODO: generating function convolution `/practice/...` 문제 필요 / 경우의 수 계수 결합 / generating function
- TODO: truncate가 필요한 FPS `/practice/...` 문제 필요 / `mod x^n` 유지 / truncation

### [FPS Log와 Exp](lessons/polynomial-recurrence-algorithms/pages/fps-log-exp.md)

- TODO: FPS log `/practice/...` 문제 필요 / `integral(F'/F)` 구현 / FPS logarithm
- TODO: FPS exp `/practice/...` 문제 필요 / Newton iteration 보정 / FPS exponential
- TODO: polynomial power `/practice/...` 문제 필요 / `exp(k log F)`와 shift 처리 / polynomial power
- TODO: OGF/EGF 구분 `/practice/...` 문제 필요 / factorial 계수 해석 / generating function

### [Generating Function Modeling](lessons/polynomial-recurrence-algorithms/pages/generating-function-modeling.md)

- TODO: generating function modeling `/practice/...` 문제 필요 / 선택 구조를 다항식으로 번역 / coefficient
- TODO: bounded coin generating function `/practice/...` 문제 필요 / truncate와 DP loop 연결 / polynomial product
- TODO: rational generating function `/practice/...` 문제 필요 / Bostan-Mori 입력 구성 / coefficient extraction
- TODO: ordered vs unordered counting `/practice/...` 문제 필요 / sequence와 product 구분 / combinatorial model

### [Linear Recurrence Applications](lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-applications.md)

- TODO: recurrence modeling `/practice/...` 문제 필요 / DP에서 recurrence 추출 / state compression
- TODO: many nth recurrence `/practice/...` 문제 필요 / Kitamasa 선택 / characteristic polynomial
- TODO: Berlekamp-Massey application `/practice/...` 문제 필요 / 앞 항에서 점화식 추정 / minimal recurrence
- TODO: non-linear sequence `/practice/...` 문제 필요 / 선형성 검증 / counterexample

### [Linear Recurrence와 Kitamasa](lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-kitamasa.md)

- TODO: Fibonacci 큰 n `/practice/...` 문제 필요 / `x^n mod P(x)` 계수 계산 / Kitamasa
- TODO: K차 선형 점화식 `/practice/...` 문제 필요 / `O(K^2 log N)` 구현 / linear recurrence
- TODO: 점화식 추정 후 nth `/practice/...` 문제 필요 / Berlekamp-Massey와 연결 / recurrence guessing
- TODO: 음수 계수 점화식 `/practice/...` 문제 필요 / 모듈러 정규화 / characteristic polynomial

### [Multipoint Evaluation](lessons/polynomial-recurrence-algorithms/pages/multipoint-evaluation.md)

- TODO: 여러 점 polynomial 평가 `/practice/...` 문제 필요 / Horner와 product tree 비교 / multipoint evaluation
- TODO: subproduct tree `/practice/...` 문제 필요 / `(x - x_i)` tree 구성 / product tree
- TODO: interpolation `/practice/...` 문제 필요 / derivative와 Lagrange basis / interpolation
- TODO: 중복 평가점 `/practice/...` 문제 필요 / evaluation과 interpolation 조건 구분 / repeated points

### [Polynomial Interpolation](lessons/polynomial-recurrence-algorithms/pages/polynomial-interpolation.md)

- TODO: consecutive Lagrange `/practice/...` 문제 필요 / `f(0..k)`로 `f(n)` 계산 / Lagrange
- TODO: finite difference polynomial `/practice/...` 문제 필요 / 차수 추정과 증명 / finite difference
- TODO: arbitrary point interpolation `/practice/...` 문제 필요 / 전체 계수 복원 / basis polynomial
- TODO: non-prime modulus interpolation `/practice/...` 문제 필요 / 역원 조건 확인 / modular inverse

### [Practice Set](lessons/polynomial-recurrence-algorithms/pages/practice-set.md)

- TODO: polynomial multiplication `/practice/...` 문제 필요 / NTT 입출력과 결과 길이 처리 / convolution
- TODO: polynomial inverse `/practice/...` 문제 필요 / FPS inverse와 truncate / Newton iteration
- TODO: multipoint evaluation `/practice/...` 문제 필요 / subproduct tree / polynomial remainder
- TODO: interpolation `/practice/...` 문제 필요 / Lagrange basis / interpolation
- TODO: generating function coefficient `/practice/...` 문제 필요 / rational form 계수 추출 / Bostan-Mori
- TODO: Berlekamp-Massey `/practice/...` 문제 필요 / 앞 항에서 최소 점화식 찾기 / discrepancy

### [Recurrence Guessing](lessons/polynomial-recurrence-algorithms/pages/recurrence-guessing.md)

- TODO: recurrence guessing `/practice/...` 문제 필요 / 앞 항 생성과 holdout 검증 / sequence modeling
- TODO: graph walk recurrence `/practice/...` 문제 필요 / Cayley-Hamilton 활용 / black-box sequence
- TODO: affine recurrence `/practice/...` 문제 필요 / 상수항 상태 추가 / affine transition
- TODO: false recurrence `/practice/...` 문제 필요 / 충분한 검증 항 유지 / counterexample

### [확률과 기대값](lessons/probability-expected-value/lesson.md)

- TODO: 주사위 기대 횟수 `/practice/...` 문제 필요 / `1 + 평균 다음 기대값` 식 세우기 / expectation DP
- TODO: 확률 분포 DP `/practice/...` 문제 필요 / 상태별 확률 합 전파 / probability distribution
- TODO: indicator 기대값 `/practice/...` 문제 필요 / 기대값의 선형성 적용 / linearity
- TODO: 순환 기대값 `/practice/...` 문제 필요 / 연립방정식 또는 식 변형 / Markov chain

### [Game Theory와 Grundy Number](lessons/game-theory-grundy/lesson.md)

- TODO: 돌 가져가기 게임 `/practice/...` 문제 필요 / terminal losing과 win/lose DP / impartial game
- TODO: Grundy number 계산 `/practice/...` 문제 필요 / mex와 DFS memoization / Sprague-Grundy
- TODO: 여러 pile 게임 `/practice/...` 문제 필요 / Grundy xor 합성 / nim xor
- TODO: misere play `/practice/...` 문제 필요 / 마지막 수 조건 별도 처리 / misere

### [Bayesian Bandits](lessons/probabilistic-decision-ai/pages/bayesian-bandits.md)

- TODO: Bayesian bandits `/practice/...` 문제 필요 / Beta posterior 갱신 계산 / Beta-Bernoulli
- TODO: finite horizon bandit `/practice/...` 문제 필요 / belief-state DP 작성 / expected value
- TODO: Thompson sampling `/practice/...` 문제 필요 / posterior sampling 정책 비교 / exploration
- TODO: greedy failure `/practice/...` 문제 필요 / 정보 가치 때문에 탐색해야 하는 상황 / regret

### [Markov Decision Process](lessons/probabilistic-decision-ai/pages/discounted-value-iteration.md)

- TODO: finite horizon MDP `/practice/...` 문제 필요 / 남은 턴 DP 작성 / stochastic action
- TODO: value iteration `/practice/...` 문제 필요 / Bellman update 구현 / policy
- TODO: absorbing MDP `/practice/...` 문제 필요 / terminal value와 기대 보상 / absorbing state
- TODO: non-convergent MDP `/practice/...` 문제 필요 / discount/종료 조건 확인 / gamma

### [Reinforcement Learning Basics](lessons/probabilistic-decision-ai/pages/exact-model-vs-sampling.md)

- TODO: finite-horizon MDP `/practice/...` 문제 필요 / 뒤에서 앞으로 기대값 DP / Bellman
- TODO: discounted value iteration `/practice/...` 문제 필요 / 반복 갱신과 수렴 / gamma
- TODO: policy iteration `/practice/...` 문제 필요 / evaluation과 improvement / policy
- TODO: MDP vs POMDP `/practice/...` 문제 필요 / 관측 가능한 상태 구분 / hidden state

### [Feedback Model Boundary](lessons/probabilistic-decision-ai/pages/feedback-model-boundary.md)

- TODO: feedback classification `/practice/...` 문제 필요 / full-information과 bandit 구분 / observed loss
- TODO: simulator planning boundary `/practice/...` 문제 필요 / exact DP와 rollout 근사 구분 / generative model
- TODO: hidden-state feedback `/practice/...` 문제 필요 / belief 기준 policy 확인 / observation history
- TODO: leakage counterexample `/practice/...` 문제 필요 / 관측하지 않은 값 사용 금지 / information leak

### [Imperfect Information Search](lessons/probabilistic-decision-ai/pages/imperfect-information-search.md)

- TODO: hidden card belief `/practice/...` 문제 필요 / 가능한 상태 필터링 / belief update
- TODO: imperfect-information game `/practice/...` 문제 필요 / determinization baseline 구현 / sampling
- TODO: information set MCTS `/practice/...` 문제 필요 / 관측 단위 통계 저장 / ISMCTS
- TODO: strategy fusion counterexample `/practice/...` 문제 필요 / 정보 누출과 행동 묶음 확인 / information set

### [Monte Carlo Tree Search](lessons/probabilistic-decision-ai/pages/monte-carlo-tree-search.md)

- TODO: 작은 보드게임 MCTS `/practice/...` 문제 필요 / selection/rollout/backprop 구현 / UCT
- TODO: 시간 제한 game AI `/practice/...` 문제 필요 / iteration budget 조정 / MCTS
- TODO: heuristic rollout `/practice/...` 문제 필요 / random rollout 개선 / rollout policy
- TODO: reward 관점 전환 `/practice/...` 문제 필요 / backpropagation 값 뒤집기 / zero-sum

### [Online Planning Evaluation](lessons/probabilistic-decision-ai/pages/online-planning-evaluation.md)

- TODO: online planning evaluation `/practice/...` 문제 필요 / paired seed score 비교 / baseline
- TODO: rollout benchmark `/practice/...` 문제 필요 / confidence interval과 holdout 분리 / standard error
- TODO: MCTS tuning `/practice/...` 문제 필요 / simulation budget과 score tradeoff / time budget
- TODO: noisy policy regression `/practice/...` 문제 필요 / 평균 개선과 timeout 악화 구분 / variance

### [Point-Based Value Iteration](lessons/probabilistic-decision-ai/pages/point-based-value-iteration.md)

- TODO: point-based value iteration `/practice/...` 문제 필요 / belief point와 alpha value 계산 / alpha vector
- TODO: small PBVI planning `/practice/...` 문제 필요 / action/observation backup / belief update
- TODO: reachable belief sampling `/practice/...` 문제 필요 / point set 확장 / L1 distance
- TODO: exact vs approximate POMDP `/practice/...` 문제 필요 / 근사 허용 조건 판별 / planning

### [POMCP](lessons/probabilistic-decision-ai/pages/pomcp.md)

- TODO: POMCP toy simulator `/practice/...` 문제 필요 / history node와 UCT 구현 / particle belief
- TODO: observation resampling `/practice/...` 문제 필요 / root belief update / reinvigoration
- TODO: online hidden-state planning `/practice/...` 문제 필요 / rollout policy 설계 / simulator
- TODO: POMCP vs PBVI `/practice/...` 문제 필요 / offline policy와 online planning 구분 / POMDP

### [Partially Observable MDP](lessons/probabilistic-decision-ai/pages/pomdp.md)

- TODO: POMDP belief update `/practice/...` 문제 필요 / observation likelihood 반영 / Bayes update
- TODO: finite horizon POMDP `/practice/...` 문제 필요 / belief tree DP / expected value
- TODO: particle belief planning `/practice/...` 문제 필요 / sampling belief 유지 / particle filter
- TODO: hidden-state leakage `/practice/...` 문제 필요 / 실제 상태 기준 행동 금지 / information leak

### [Practice Set](lessons/probabilistic-decision-ai/pages/practice-set.md)

- TODO: feedback boundary `/practice/...` 문제 필요 / 관측 모델 분류 / full-information vs bandit
- TODO: stochastic shortest path `/practice/...` 문제 필요 / absorbing goal과 proper policy / SSP
- TODO: MCTS toy game `/practice/...` 문제 필요 / selection/rollout/backprop / UCT
- TODO: hidden-state search `/practice/...` 문제 필요 / belief filtering / imperfect information
- TODO: POMDP belief update `/practice/...` 문제 필요 / Bayes update / observation model
- TODO: bandit simulation `/practice/...` 문제 필요 / posterior update와 regret / Thompson sampling
- TODO: online planning evaluation `/practice/...` 문제 필요 / paired seed benchmark / time budget

### [Stochastic Decision Process Practice Set](lessons/probabilistic-decision-ai/pages/practice-set.md)

- TODO: finite horizon MDP `/practice/...` 문제 필요 / 남은 턴 DP 작성 / layer DP
- TODO: discounted value iteration `/practice/...` 문제 필요 / 오차 기준이 있는 Bellman 반복 / gamma
- TODO: policy evaluation `/practice/...` 문제 필요 / 고정 policy의 value 계산 / linear equation
- TODO: stochastic shortest path `/practice/...` 문제 필요 / improper policy와 INF 처리 / absorbing state

### [Stochastic Shortest Path](lessons/probabilistic-decision-ai/pages/stochastic-shortest-path.md)

- TODO: expected hitting time `/practice/...` 문제 필요 / 자기 상태로 돌아오는 기대 비용 계산 / geometric
- TODO: stochastic shortest path `/practice/...` 문제 필요 / Bellman optimality equation 작성 / absorbing state
- TODO: policy evaluation linear system `/practice/...` 문제 필요 / 고정 policy의 value 계산 / Gaussian elimination
- TODO: improper policy `/practice/...` 문제 필요 / 무한 기대 비용 상태 구분 / proper policy

### [Dynamic Connectivity](lessons/offline-time-axis-techniques/pages/dynamic-connectivity.md)

- TODO: 간선 추가만 있는 연결성 `/practice/...` 문제 필요 / DSU 기본 연결성 / union-find
- TODO: offline dynamic connectivity `/practice/...` 문제 필요 / 시간축 segment tree와 rollback / rollback DSU
- TODO: component size 동적 질의 `/practice/...` 문제 필요 / rollback 시 size 복원 / component aggregate
- TODO: 중복 간선 삭제 질의 `/practice/...` 문제 필요 / edge id와 multiset active count 관리 / multigraph

### [오프라인 쿼리: Mo, DSU Rollback, Parallel Binary Search](lessons/offline-time-axis-techniques/pages/offline-queries.md)

- TODO: 정적 배열 구간 질의를 Mo로 처리하는 문제 추가 / 질의 정렬과 원래 순서 복원 / Mo's algorithm
- TODO: 동적 연결성 오프라인 문제 추가 / 시간 구간 세그먼트 트리와 rollback DSU / DSU rollback
- TODO: 여러 질의의 최초 만족 시점 문제 추가 / Parallel Binary Search 라운드 처리 / PBS, monotonicity
- TODO: 온라인 순서가 의미 있는 질의 문제 추가 / 오프라인 재정렬 불가 조건 판별 / online vs offline

### [Offline Range Query Techniques](lessons/offline-time-axis-techniques/pages/offline-range-query-techniques.md)

- TODO: offline range distinct `/practice/...` 문제 필요 / add/remove 상태 설계 / Mo, frequency
- TODO: value threshold range query `/practice/...` 문제 필요 / offline sorting + Fenwick / prefix sweep
- TODO: range query with updates `/practice/...` 문제 필요 / time dimension 처리 / Mo with modifications
- TODO: online-dependent query `/practice/...` 문제 필요 / 오프라인 불가 판정 / query dependency

### [Practice Set](lessons/offline-time-axis-techniques/pages/practice-set.md)

- TODO: static range query `/practice/...` 문제 필요 / Mo ordering과 answer index 복구 / sqrt block, add/remove
- TODO: value threshold range query `/practice/...` 문제 필요 / offline sorting + Fenwick / sweep by value
- TODO: parallel binary search `/practice/...` 문제 필요 / 여러 질의의 답 후보 동시 축소 / monotone predicate
- TODO: retroactive operation `/practice/...` 문제 필요 / operation interval 모델링 / offline retroactivity

### [Retroactive Data Structures](lessons/offline-time-axis-techniques/pages/retroactive-data-structures.md)

- TODO: retroactive data structure `/practice/...` 문제 필요 / operation interval 만들기 / active interval
- TODO: offline retroactive connectivity `/practice/...` 문제 필요 / time tree + rollback DSU / segment tree over time
- TODO: retroactive frequency query `/practice/...` 문제 필요 / rollback counter / old value history
- TODO: online retroactive priority queue `/practice/...` 문제 필요 / offline 불가 판정 / fully retroactive

### [Rollback Techniques](lessons/offline-time-axis-techniques/pages/rollback-techniques.md)

- TODO: rollback techniques `/practice/...` 문제 필요 / snapshot과 원복 구현 / rollback stack
- TODO: offline dynamic connectivity `/practice/...` 문제 필요 / segment tree over time / rollback DSU
- TODO: rollback frequency queries `/practice/...` 문제 필요 / 배열 변경 기록 / old value
- TODO: path compression rollback `/practice/...` 문제 필요 / 숨은 parent 변경 제거 / no compression

### [Divide and Conquer DP Optimization](lessons/divide-and-conquer-dp-optimization/lesson.md)

- TODO: 구간 분할 DP `/practice/...` 문제 필요 / layer DP와 `cost(l, r)` 계산 / partition DP
- TODO: opt 단조성 있는 DP `/practice/...` 문제 필요 / `computeLayer` 재귀 구현 / monotone opt
- TODO: cost 이동이 필요한 DP `/practice/...` 문제 필요 / cost 계산과 D&C 결합 / moving cost
- TODO: 단조성이 깨지는 반례 `/practice/...` 문제 필요 / 최적화 적용 조건 판정 / quadrangle inequality

### [Knuth Optimization](lessons/knuth-optimization/lesson.md)

- TODO: 파일 합치기 `/practice/...` 문제 필요 / interval DP와 prefix sum cost / file merging
- TODO: Knuth 최적화 DP `/practice/...` 문제 필요 / opt 범위 축소 구현 / Knuth optimization
- TODO: optimal BST `/practice/...` 문제 필요 / 구간 확률 비용과 opt 단조성 / optimal BST
- TODO: Knuth 조건이 없는 interval DP `/practice/...` 문제 필요 / 적용 가능성 판정 / quadrangle inequality

### [Monge와 SMAWK](lessons/monge-smawk/lesson.md)

- TODO: Monge row minima `/practice/...` 문제 필요 / argmin 단조성 확인 / Monge array
- TODO: monotone row minima DP `/practice/...` 문제 필요 / D&C row minima 구현 / totally monotone
- TODO: SMAWK 적용 `/practice/...` 문제 필요 / column reduction과 odd row recursion / SMAWK
- TODO: Monge가 아닌 행렬 `/practice/...` 문제 필요 / 적용 조건 반례 찾기 / inequality

### [Alien Optimization](lessons/parametric-optimization/pages/exact-k-alien-optimization.md)

- TODO: 정확히 K개 segment DP `/practice/...` 문제 필요 / penalty와 count 추적 / alien trick
- TODO: DP 차원 제거 `/practice/...` 문제 필요 / K dimension을 이분 탐색으로 대체 / Lagrangian relaxation
- TODO: tree/path 선택 최적화 `/practice/...` 문제 필요 / relaxed transition 설계 / parametric DP
- TODO: tie-break 반례 `/practice/...` 문제 필요 / 같은 비용에서 count 방향 고정 / monotonicity

### [Parametric DP](lessons/parametric-optimization/pages/feasibility-and-answer-search.md)

- TODO: max average DP `/practice/...` 문제 필요 / answer binary search / `a_i - x`
- TODO: penalty segment DP `/practice/...` 문제 필요 / value + count 저장 / Alien Optimization
- TODO: ratio optimization `/practice/...` 문제 필요 / `profit - x*weight` 판정 / feasibility DP
- TODO: non-monotone parameter `/practice/...` 문제 필요 / 이분 탐색 불가 판별 / monotonicity

### [Fractional Programming DP](lessons/parametric-optimization/pages/fractional-objectives.md)

- TODO: maximum average subarray `/practice/...` 문제 필요 / `a_i - x` 판정 / prefix minimum
- TODO: ratio knapsack DP `/practice/...` 문제 필요 / transformed score DP / binary search
- TODO: average path feasibility `/practice/...` 문제 필요 / graph weight 변환 / parametric search
- TODO: zero denominator ratio `/practice/...` 문제 필요 / 예외와 precision 처리 / denominator

### [Lagrangian Relaxation Patterns](lessons/parametric-optimization/pages/general-lagrangian-relaxation.md)

- TODO: exact K selection `/practice/...` 문제 필요 / count penalty와 답 보정 / Alien trick
- TODO: budgeted DP relaxation `/practice/...` 문제 필요 / 비용 제약을 multiplier로 이동 / relaxed DP
- TODO: Lagrangian flow `/practice/...` 문제 필요 / flow 양과 비용 조건 분리 / min-cost flow
- TODO: tie-break counterexample `/practice/...` 문제 필요 / 동점 처리와 count 단조성 확인 / breakpoint

### [Parametric Optimization Practice Set](lessons/parametric-optimization/pages/practice-set.md)

- TODO: exact K DP `/practice/...` 문제 필요 / penalty와 count tie-break / Alien trick
- TODO: fractional graph path `/practice/...` 문제 필요 / 비율 목적식과 shortest path 결합 / transformed weight
- TODO: breakpoint counterexample `/practice/...` 문제 필요 / 동점 처리와 답 복원 검증 / breakpoint

### [XOR Linear Basis](lessons/linear-basis-xor/lesson.md)

- TODO: 부분집합 maximum xor `/practice/...` 문제 필요 / basis insert와 greedy maximize / xor basis
- TODO: xor 값 표현 가능성 `/practice/...` 문제 필요 / value reduction과 rank / linear independence
- TODO: 그래프 경로 xor 최댓값 `/practice/...` 문제 필요 / cycle basis와 prefix xor / graph xor
- TODO: K번째 xor 값 `/practice/...` 문제 필요 / basis 정규화와 순서 생성 / reduced basis

### [CHT DP Applications](lessons/convex-dp-optimization/pages/cht-dp-applications.md)

- TODO: quadratic partition CHT `/practice/...` 문제 필요 / 식 전개와 line 분리 / prefix square
- TODO: Li Chao DP `/practice/...` 문제 필요 / 임의 query 처리 / dynamic hull
- TODO: online CHT DP `/practice/...` 문제 필요 / add/query 순서 설계 / transition ordering
- TODO: non-monotone CHT `/practice/...` 문제 필요 / deque 전제 검증 / counterexample

### [Convex DP Modeling](lessons/convex-dp-optimization/lesson.md)

- TODO: convex DP modeling `/practice/...` 문제 필요 / 전이식 분리 / decision variable
- TODO: quadrangle inequality `/practice/...` 문제 필요 / argmin 단조 증명 / Monge
- TODO: penalty DP modeling `/practice/...` 문제 필요 / Alien Optimization 선택 / parametric search
- TODO: non-convex DP counterexample `/practice/...` 문제 필요 / 최적화 조건 반례 / stress test

### [Convex Hull Trick과 Li Chao Tree](lessons/convex-dp-optimization/pages/convex-hull-trick-li-chao.md)

- TODO: 단조 slope CHT `/practice/...` 문제 필요 / 직선 추가와 단조 x query / deque CHT
- TODO: Li Chao Tree 기본 `/practice/...` 문제 필요 / 임의 순서 line과 point query / Li Chao
- TODO: DP 전이 최적화 `/practice/...` 문제 필요 / `m_j*x_i+b_j`로 식 변형 / CHT DP
- TODO: 큰 좌표와 overflow `/practice/...` 문제 필요 / x 범위, INF, `m*x+b` 점검 / overflow

### [Convex Hull Trick Variants](lessons/convex-dp-optimization/pages/convex-hull-trick-variants.md)

- TODO: monotone CHT `/practice/...` 문제 필요 / slope/query 단조 조건 사용 / deque CHT
- TODO: arbitrary query CHT `/practice/...` 문제 필요 / breakpoint binary search / lower hull
- TODO: Li Chao variant `/practice/...` 문제 필요 / x 압축과 min/max 변환 / compressed Li Chao
- TODO: same slope overflow `/practice/...` 문제 필요 / convention과 자료형 점검 / same slope, `__int128`

### [Fully Dynamic CHT](lessons/convex-dp-optimization/pages/fully-dynamic-cht.md)

- TODO: offline dynamic CHT `/practice/...` 문제 필요 / add/delete를 활성 구간으로 변환 / segment tree over time
- TODO: rollback Li Chao `/practice/...` 문제 필요 / DFS rollback 구현 / change log
- TODO: online line container `/practice/...` 문제 필요 / 임의 삭제와 query 처리 / multiset hull
- TODO: duplicate line deletion `/practice/...` 문제 필요 / 같은 slope와 identity 관리 / tie-breaking

### [Kinetic Hull](lessons/convex-dp-optimization/pages/kinetic-hull.md)

- TODO: kinetic line envelope `/practice/...` 문제 필요 / 시간축 교점으로 최댓값 변화 찾기 / line envelope
- TODO: moving point support `/practice/...` 문제 필요 / 방향 고정 support point 추적 / dot product
- TODO: event queue kinetic hull `/practice/...` 문제 필요 / stale event lazy deletion / versioning
- TODO: simultaneous kinetic events `/practice/...` 문제 필요 / 동시 event와 tie 처리 / rational compare

### [Min-Plus Convolution](lessons/convex-dp-optimization/pages/min-plus-convolution.md)

- TODO: min-plus convolution `/practice/...` 문제 필요 / naive merge 구현 / DP merge
- TODO: convex sequence merge `/practice/...` 문제 필요 / argmin monotone 확인 / convex cost
- TODO: tree DP convolution `/practice/...` 문제 필요 / small-to-large merge / group DP
- TODO: non-convex counterexample `/practice/...` 문제 필요 / 최적화 조건 판정 / monotonicity

### [Practice Set](lessons/convex-dp-optimization/pages/practice-set.md)

- TODO: arbitrary x Li Chao `/practice/...` 문제 필요 / 일반 삽입/질의 구현 / Li Chao Tree
- TODO: monotone opt DP `/practice/...` 문제 필요 / argmin 단조성 확인 / D&C DP
- TODO: absolute value convex cost `/practice/...` 문제 필요 / breakpoints 관리 / Slope Trick
- TODO: min-plus merge `/practice/...` 문제 필요 / convolution 모델링 / convex sequence
- TODO: dynamic line set `/practice/...` 문제 필요 / offline deletion 또는 dynamic hull / fully dynamic CHT

### [Slope Trick](lessons/convex-dp-optimization/pages/slope-trick.md)

- TODO: median absolute deviation `/practice/...` 문제 필요 / `addAbs`와 minimizer 구간 이해 / two heaps
- TODO: nondecreasing adjustment `/practice/...` 문제 필요 / heap으로 convex cost 관리 / isotonic regression
- TODO: 이동 범위가 있는 DP `/practice/...` 문제 필요 / shift와 hinge 추가 결합 / slope trick
- TODO: non-convex transition 반례 `/practice/...` 문제 필요 / slope trick 적용 조건 판정 / convexity

### [Cactus Representation](lessons/graph-cut-structures/pages/cactus-representation.md)

- TODO: cactus graph validation `/practice/...` 문제 필요 / edge가 cycle에 중복 포함되는지 확인 / DFS cycle
- TODO: cactus distance query `/practice/...` 문제 필요 / cycle prefix와 block tree 결합 / LCA
- TODO: min cut cactus `/practice/...` 문제 필요 / minimum cut family 해석 / cut representation
- TODO: bridge tree is not enough `/practice/...` 문제 필요 / cycle 내부 정보 보존 / block compression

### [Cut Cactus Applications](lessons/graph-cut-structures/pages/cactus-representation.md)

- TODO: cactus cut query `/practice/...` 문제 필요 / tree edge와 cycle cut 구분 / cactus
- TODO: min cut family count `/practice/...` 문제 필요 / cycle pair 선택 세기 / global min cut
- TODO: edge criticality `/practice/...` 문제 필요 / 원래 edge와 cactus cut 매핑 / witness
- TODO: gomory-hu vs cactus `/practice/...` 문제 필요 / pair cut과 global cut 구분 / cut family

### [Cut Sparsification](lessons/graph-cut-structures/pages/cut-sparsification.md)

- TODO: cut sparsification `/practice/...` 문제 필요 / forest certificate 이해 / k-edge connectivity
- TODO: sparse certificate min cut `/practice/...` 문제 필요 / 작은 cut 보존 / spanning forest layers
- TODO: repeated connectivity threshold `/practice/...` 문제 필요 / dense graph pruning / certificate verification
- TODO: weighted cut certificate `/practice/...` 문제 필요 / 적용 조건 구분 / weighted vs unweighted

### [Global Min Cut Applications](lessons/graph-cut-structures/pages/global-min-cut-applications.md)

- TODO: global min cut partition `/practice/...` 문제 필요 / partition 복원 / Stoer-Wagner group tracking
- TODO: all pair cut query `/practice/...` 문제 필요 / pair min cut 질의 / Gomory-Hu Tree
- TODO: critical cut edge `/practice/...` 문제 필요 / edge sensitivity / min cut family
- TODO: source sink vs global `/practice/...` 문제 필요 / 모델 구분 / global vs s-t

### [Global Min Cut](lessons/graph-cut-structures/pages/global-min-cut.md)

- TODO: global min cut `/practice/...` 문제 필요 / cut value와 disconnected case / Stoer-Wagner
- TODO: network weakest cut `/practice/...` 문제 필요 / contraction 구현 / undirected capacity
- TODO: many cut comparisons `/practice/...` 문제 필요 / Gomory-Hu와 선택 / all-pairs min cut
- TODO: directed counterexample `/practice/...` 문제 필요 / 적용 조건 판정 / global vs s-t

### [Gomory-Hu Tree](lessons/graph-cut-structures/pages/gomory-hu-tree.md)

- TODO: pair min-cut query `/practice/...` 문제 필요 / cut tree path minimum 이해 / Gomory-Hu
- TODO: edge connectivity all pairs `/practice/...` 문제 필요 / `N-1` max-flow construction / cut-equivalent tree
- TODO: many min-cut queries `/practice/...` 문제 필요 / LCA minimum edge query / tree path RMQ
- TODO: directed graph counterexample `/practice/...` 문제 필요 / 적용 조건 판정 / undirected cut

### [Practice Set](lessons/graph-cut-structures/pages/practice-set.md)

- TODO: all pair min-cut query `/practice/...` 문제 필요 / cut-equivalent tree 질의 / Gomory-Hu
- TODO: sparse certificate min cut `/practice/...` 문제 필요 / 작은 cut 보존과 edge pruning / cut sparsification
- TODO: min cut family cactus `/practice/...` 문제 필요 / global min cut family 압축 / cactus
- TODO: randomized vs deterministic cut `/practice/...` 문제 필요 / Karger 실패 확률과 fallback / contraction

### [Randomized Min Cut](lessons/graph-cut-structures/pages/randomized-min-cut.md)

- TODO: randomized min cut `/practice/...` 문제 필요 / Karger contraction 구현 / DSU
- TODO: repeated contraction `/practice/...` 문제 필요 / 반복으로 성공 확률 증폭 / Monte Carlo
- TODO: min cut comparison `/practice/...` 문제 필요 / Stoer-Wagner와 결과 비교 / deterministic fallback
- TODO: weighted randomized cut `/practice/...` 문제 필요 / weighted edge 처리 판단 / multigraph

### [Euler Tour Tree](lessons/euler-tour-tree/lesson.md)

- TODO: dynamic forest connectivity `/practice/...` 문제 필요 / root 비교로 연결성 확인 / Euler tour sequence
- TODO: online link cut `/practice/...` 문제 필요 / reroot, split, merge 구현 / implicit treap
- TODO: component sum `/practice/...` 문제 필요 / treap aggregate 유지 / component aggregate
- TODO: non-forest dynamic graph `/practice/...` 문제 필요 / ETT 단독 적용 한계 판정 / replacement edge

### [Mobius Inversion](lessons/mobius-inversion/lesson.md)

- TODO: coprime pair count `/practice/...` 문제 필요 / `sum mu(d) cnt[d]^2` 적용 / gcd equals one
- TODO: exact gcd pair `/practice/...` 문제 필요 / `g`로 나눈 뒤 inversion / divisor multiples
- TODO: divisor transform `/practice/...` 문제 필요 / 약수 합 관계 복원 / Mobius inversion
- TODO: unordered pair 보정 `/practice/...` 문제 필요 / diagonal/order 처리 / pair counting

### [Convex Cost Flow](lessons/convex-cost-flow/lesson.md)

- TODO: convex production cost `/practice/...` 문제 필요 / marginal edge split 이해 / convex cost
- TODO: assignment with penalty `/practice/...` 문제 필요 / min-cost flow 모델 확장 / piecewise linear
- TODO: demand allocation `/practice/...` 문제 필요 / capacity와 convex cost 결합 / network modeling
- TODO: concave cost counterexample `/practice/...` 문제 필요 / 적용 조건 판정 / marginal cost

### [Dynamic Network Optimization](lessons/dynamic-network-optimization/lesson.md)

- TODO: incremental max flow `/practice/...` 문제 필요 / old flow feasibility와 추가 augment 확인 / residual graph
- TODO: dynamic MST block rebuild `/practice/...` 문제 필요 / 변경 후보만 작은 Kruskal로 합치기 / block rebuild
- TODO: time-expanded evacuation `/practice/...` 문제 필요 / 시간 node와 wait edge 모델링 / time expansion
- TODO: capacity decrease repair `/practice/...` 문제 필요 / old flow가 infeasible해지는 반례 처리 / feasibility repair

### [Dynamic Flow](lessons/dynamic-network-optimization/pages/dynamic-flow.md)

- TODO: incremental max flow `/practice/...` 문제 필요 / capacity 증가 후 추가 augment / residual graph
- TODO: time-expanded evacuation `/practice/...` 문제 필요 / 시간 node 모델링 / wait edge
- TODO: dynamic flow block rebuild `/practice/...` 문제 필요 / 변경 묶음 재계산 / batch rebuild
- TODO: capacity decrease repair `/practice/...` 문제 필요 / infeasible old flow 처리 / feasibility repair

### [Dynamic MST](lessons/dynamic-network-optimization/pages/dynamic-mst.md)

- TODO: dynamic MST rebuild `/practice/...` 문제 필요 / Kruskal baseline 유지 / active edges
- TODO: edge insertion MST `/practice/...` 문제 필요 / cycle maximum 교체 / path max
- TODO: block rebuild MST `/practice/...` 문제 필요 / 변경 후보 축소 / sqrt decomposition
- TODO: deleted tree edge replacement `/practice/...` 문제 필요 / crossing edge 탐색 / replacement edge

### [Dynamic Network Optimization Practice Set](lessons/dynamic-network-optimization/pages/practice-set.md)

- TODO: incremental flow `/practice/...` 문제 필요 / capacity 증가만 있는 residual 재사용 / feasible old flow
- TODO: time-expanded flow `/practice/...` 문제 필요 / 시간별 edge를 정적 network로 펼치기 / wait edge
- TODO: dynamic MST rebuild `/practice/...` 문제 필요 / 활성 간선 Kruskal baseline / active set
- TODO: MST block rebuild `/practice/...` 문제 필요 / 변경 edge 후보만 합치기 / sqrt decomposition
- TODO: flow decrease counterexample `/practice/...` 문제 필요 / 용량 감소에서 repair 필요성 확인 / infeasible flow

### [Linear Basis Applications](lessons/linear-basis-applications/lesson.md)

- TODO: linear basis applications `/practice/...` 문제 필요 / 표현 가능성과 rank / representability
- TODO: kth subset xor `/practice/...` 문제 필요 / normalized basis / kth xor
- TODO: graph cycle xor `/practice/...` 문제 필요 / path xor와 cycle basis / graph xor
- TODO: weighted independent xor set `/practice/...` 문제 필요 / matroid greedy 구분 / independence

### [Dirichlet Convolution](lessons/dirichlet-convolution/lesson.md)

- TODO: Dirichlet convolution `/practice/...` 문제 필요 / 약수 합 함수 계산 / divisor zeta
- TODO: multiplicative function `/practice/...` 문제 필요 / prime power 공식 / linear sieve
- TODO: gcd summatory function `/practice/...` 문제 필요 / gcd별 pair count / Mobius inverse
- TODO: sparse divisor transform `/practice/...` 문제 필요 / 값 범위와 개수 구분 / coordinate values

### [Minkowski Sum](lessons/minkowski-sum/lesson.md)

- TODO: Minkowski sum `/practice/...` 문제 필요 / 두 convex polygon edge merge 구현 / convex polygon
- TODO: polygon collision `/practice/...` 문제 필요 / `A + (-B)`와 원점 포함 판정 / reflected polygon
- TODO: expanded obstacle `/practice/...` 문제 필요 / configuration space obstacle 모델링 / robot shape
- TODO: collinear Minkowski `/practice/...` 문제 필요 / 같은 방향 edge와 중복 점 처리 / collinear edge

### [Rotating Calipers Applications](lessons/rotating-calipers-applications/lesson.md)

- TODO: rotating calipers width `/practice/...` 문제 필요 / edge-point 높이 sweep / minimum width
- TODO: convex polygon tangent `/practice/...` 문제 필요 / support point 포인터 전진 / tangent
- TODO: minimum rectangle `/practice/...` 문제 필요 / 네 caliper 동시 회전 / bounding rectangle
- TODO: polygon distance edge case `/practice/...` 문제 필요 / 교차와 collinear tie 처리 / convex distance

### [Multiplicative Functions](lessons/multiplicative-functions/lesson.md)

- TODO: multiplicative function sieve `/practice/...` 문제 필요 / `phi`, `mu` linear sieve 구현 / prime power
- TODO: divisor count sum `/practice/...` 문제 필요 / `tau` exponent 상태 관리 / least prime factor
- TODO: multiplicative convolution `/practice/...` 문제 필요 / convolution 관계로 함수 설계 / Dirichlet convolution
- TODO: large summatory function `/practice/...` 문제 필요 / prefix와 floor grouping 구분 / summatory

### [Summatory Number Theory](lessons/summatory-number-theory/lesson.md)

- TODO: floor division grouping `/practice/...` 문제 필요 / quotient block 만들기 / `n / i` 구간
- TODO: divisor summatory `/practice/...` 문제 필요 / 합 순서 바꾸기 / divisor transform
- TODO: summatory phi/mu `/practice/...` 문제 필요 / prefix + memoization / Du Jiao 관점
- TODO: large modulo gcd pair `/practice/...` 문제 필요 / overflow와 음수 정규화 / Mobius, `__int128`

### [Shape Distance Modeling](lessons/shape-distance-modeling/lesson.md)

- TODO: point segment distance `/practice/...` 문제 필요 / projection과 clamp 구현 / dot product
- TODO: convex collision `/practice/...` 문제 필요 / separating axis 판정 / projection interval
- TODO: moving shape distance `/practice/...` 문제 필요 / reflected shape 모델링 / Minkowski difference
- TODO: touching polygons `/practice/...` 문제 필요 / 접점과 EPS 정책 확인 / zero distance

### [Circle Geometry](lessons/circle-geometry/lesson.md)

- TODO: circle line intersection `/practice/...` 문제 필요 / projection과 offset 계산 / point-line distance
- TODO: circle circle intersection `/practice/...` 문제 필요 / 교점 개수 case 분기 / center distance
- TODO: common tangents `/practice/...` 문제 필요 / 외접선/내접선 변환 / tangent construction
- TODO: angular interval sweep `/practice/...` 문제 필요 / 각도 wrap 처리 / atan2, acos

### [Quadrangle Inequality Proofs](lessons/quadrangle-inequality-proofs/lesson.md)

- TODO: quadrangle inequality `/practice/...` 문제 필요 / 구간 합 cost 전개 / interval DP
- TODO: Knuth proof `/practice/...` 문제 필요 / opt bound 증명 / monotone opt
- TODO: Monge DP proof `/practice/...` 문제 필요 / row minima 단조성 연결 / Monge array
- TODO: non-Monge counterexample `/practice/...` 문제 필요 / 반례 생성과 tie-breaking 확인 / inequality

### [Circle Arrangement](lessons/circle-arrangement/lesson.md)

- TODO: circle arrangement `/practice/...` 문제 필요 / 교점 angle로 arc 분할 / atan2
- TODO: circle union perimeter `/practice/...` 문제 필요 / depth 1 arc 길이 합산 / angular sweep
- TODO: circle union area `/practice/...` 문제 필요 / arc contribution 계산 / Green theorem
- TODO: contained circles `/practice/...` 문제 필요 / 포함/중복 원 처리 / EPS

### [Geometry Robustness and Duality](lessons/geometry-robustness-and-duality/lesson.md)

- TODO: robust orientation `/practice/...` 문제 필요 / exact sign과 overflow 방지 / `__int128`
- TODO: power cell `/practice/...` 문제 필요 / weighted distance를 half-plane으로 변환 / radical axis
- TODO: robust Delaunay `/practice/...` 문제 필요 / incircle predicate와 edge flip / degeneracy
- TODO: regular triangulation lifting `/practice/...` 문제 필요 / weighted point를 3D lower hull로 해석 / lifting
- TODO: EPS comparator `/practice/...` 문제 필요 / strict weak ordering 유지 / tie policy

### [3D Convex Hull](lessons/geometry-robustness-and-duality/pages/3d-convex-hull.md)

- TODO: signed volume `/practice/...` 문제 필요 / face visibility 판정 / cross, dot
- TODO: tetrahedron hull `/practice/...` 문제 필요 / 초기 hull 구성 / orientation
- TODO: incremental 3D hull `/practice/...` 문제 필요 / visible face와 horizon / face graph
- TODO: coplanar hull points `/practice/...` 문제 필요 / degeneracy 정책 / EPS, boundary

### [Power Diagram](lessons/geometry-robustness-and-duality/pages/power-diagram.md)

- TODO: power distance `/practice/...` 문제 필요 / weighted nearest site 판정 / `dist^2 - w`
- TODO: radical axis `/practice/...` 문제 필요 / 두 원의 power 경계 계산 / linear boundary
- TODO: power cell `/practice/...` 문제 필요 / half-plane intersection으로 cell 구하기 / convex polygon
- TODO: empty weighted cell `/practice/...` 문제 필요 / 사라지는 cell과 tie 처리 / degeneracy

### [Geometry Robustness and Duality Practice Set](lessons/geometry-robustness-and-duality/pages/practice-set.md)

- TODO: power diagram cell `/practice/...` 문제 필요 / power distance 비교와 half-plane / weighted Voronoi
- TODO: Delaunay predicate `/practice/...` 문제 필요 / incircle 부호와 tie 처리 / cocircular
- TODO: 3D lower hull `/practice/...` 문제 필요 / lifting과 lower face projection / regular triangulation
- TODO: empty power cell `/practice/...` 문제 필요 / cell이 사라지는 경우 처리 / degeneracy

### [Regular Triangulation](lessons/geometry-robustness-and-duality/pages/regular-triangulation.md)

- TODO: regular triangulation lifting `/practice/...` 문제 필요 / weighted point의 lifted z 계산 / `x^2+y^2-w`
- TODO: power adjacency `/practice/...` 문제 필요 / cell adjacency와 dual edge 연결 / power diagram
- TODO: weighted Delaunay `/practice/...` 문제 필요 / in-power-circle 판정 / lower hull
- TODO: empty weighted site `/practice/...` 문제 필요 / lower hull에서 사라지는 site 처리 / degeneracy

### [Robust Delaunay](lessons/geometry-robustness-and-duality/pages/robust-delaunay.md)

- TODO: incircle predicate `/practice/...` 문제 필요 / orientation convention과 incircle 부호 확인 / determinant
- TODO: Delaunay edge flip `/practice/...` 문제 필요 / local Delaunay 조건 검증 / edge flip
- TODO: Euclidean MST candidate `/practice/...` 문제 필요 / Delaunay graph 성질 활용 / empty circle
- TODO: cocircular degeneracy `/practice/...` 문제 필요 / tie policy 고정 / degeneracy

### [Robust Geometry Predicates](lessons/geometry-robustness-and-duality/pages/robust-geometry-predicates.md)

- TODO: robust orientation `/practice/...` 문제 필요 / `__int128` cross sign / ccw
- TODO: segment intersection edge cases `/practice/...` 문제 필요 / 접함/겹침 처리 / bounding box
- TODO: robust incircle `/practice/...` 문제 필요 / determinant sign / Delaunay
- TODO: sweep comparator `/practice/...` 문제 필요 / strict ordering 유지 / EPS policy

### [Black-Box Linear Algebra](lessons/black-box-linear-algebra/lesson.md)

- TODO: sparse matrix-vector `/practice/...` 문제 필요 / row/col 방향과 modulo 처리 / matvec
- TODO: Krylov recurrence `/practice/...` 문제 필요 / `u^T A^k v` 수열 생성 / Berlekamp-Massey
- TODO: black-box determinant `/practice/...` 문제 필요 / randomized projection 검증 / Wiedemann
- TODO: composite modulo linear algebra `/practice/...` 문제 필요 / field 조건 판별 / modular inverse

### [Game Theory Applications](lessons/game-theory-applications/lesson.md)

- TODO: game theory applications `/practice/...` 문제 필요 / Grundy와 minimax 분류 / impartial
- TODO: split game xor `/practice/...` 문제 필요 / 독립 subgame 판정 / Sprague-Grundy
- TODO: stochastic game modeling `/practice/...` 문제 필요 / chance node와 max node 분리 / MDP
- TODO: hidden information game `/practice/...` 문제 필요 / 정보 누출 방지 / belief state

### [Inversion Geometry](lessons/inversion-geometry/lesson.md)

- TODO: inversion geometry `/practice/...` 문제 필요 / 점 inversion과 자기 역변환 확인 / inverse point
- TODO: circle through center `/practice/...` 문제 필요 / 원을 직선으로 변환 / circle-line transform
- TODO: tangent circle inversion `/practice/...` 문제 필요 / 접선 조건 단순화 / conformal
- TODO: inversion degeneracy `/practice/...` 문제 필요 / 중심 통과/중심 일치 처리 / degeneracy

### [Matroid Intersection](lessons/matroid-algorithms/pages/matroid-intersection.md)

- TODO: matroid intersection `/practice/...` 문제 필요 / partition matroid + partition matroid 모델링 / exchange graph
- TODO: graphic partition matroid `/practice/...` 문제 필요 / forest 조건과 색상 제한 결합 / DSU oracle
- TODO: linear matroid intersection `/practice/...` 문제 필요 / basis 독립성과 그룹 제한 결합 / linear basis
- TODO: weighted matroid intersection `/practice/...` 문제 필요 / unweighted 증가 경로의 한계 확인 / shortest augmenting path

### [Matroid Parity](lessons/matroid-algorithms/pages/matroid-parity.md)

- TODO: matroid parity `/practice/...` 문제 필요 / pair 선택과 독립성 조건 구분 / pair union
- TODO: linear matroid parity `/practice/...` 문제 필요 / vector pair의 rank 유지 / linear basis
- TODO: matching parity reduction `/practice/...` 문제 필요 / matching과 parity 모델 연결 / blossom, Tutte
- TODO: pair-choice counterexample `/practice/...` 문제 필요 / pair 중 하나 선택과 둘 다 선택 구분 / partition constraint

### [Matroid Union](lessons/matroid-algorithms/pages/matroid-union.md)

- TODO: partition matroid union `/practice/...` 문제 필요 / class capacity가 여러 copy로 늘어나는 경우 / capacity
- TODO: forest decomposition `/practice/...` 문제 필요 / 간선을 여러 forest로 색칠 / graphic matroid
- TODO: matroid union augmenting `/practice/...` 문제 필요 / layer 사이 교환 경로 구성 / exchange
- TODO: greedy failure `/practice/...` 문제 필요 / 바로 넣기 greedy 반례 확인 / augmenting path

### [Practice Set](lessons/matroid-algorithms/pages/practice-set.md)

- TODO: graphic + partition matroid `/practice/...` 문제 필요 / forest 조건과 색상 제한 결합 / matroid intersection
- TODO: forest decomposition `/practice/...` 문제 필요 / 여러 forest layer로 간선 분해 / matroid union
- TODO: pair-choice counterexample `/practice/...` 문제 필요 / parity와 partition constraint 구분 / matroid parity

### [Sparse Linear Systems](lessons/sparse-linear-systems/lesson.md)

- TODO: sparse linear system `/practice/...` 문제 필요 / sparse row와 dense baseline 비교 / rank
- TODO: graph equation `/practice/...` 문제 필요 / incidence/Laplacian 식 세우기 / nullspace
- TODO: black-box solver `/practice/...` 문제 필요 / matvec 기반 검증 / Wiedemann
- TODO: singular system `/practice/...` 문제 필요 / 해 없음/여러 해 구분 / augmented rank

### [Linear Algebra Applications](lessons/linear-algebra-applications/lesson.md)

- TODO: linear constraints `/practice/...` 문제 필요 / 해 없음/여러 해 판정 / augmented matrix
- TODO: determinant counting `/practice/...` 문제 필요 / determinant로 구조 세기 / Matrix-Tree
- TODO: randomized algebra `/practice/...` 문제 필요 / zero test 실패 확률 줄이기 / Schwartz-Zippel

### [Dual Averaging](lessons/online-convex-optimization/pages/dual-averaging.md)

- TODO: multiplicative weights `/practice/...` 문제 필요 / 누적 loss 기반 simplex update / entropy
- TODO: dual averaging regret `/practice/...` 문제 필요 / learning rate와 regret 계산 / cumulative gradient
- TODO: primal-dual online allocation `/practice/...` 문제 필요 / 제약 violation을 dual 변수로 갱신 / Lagrangian
- TODO: full information vs bandit `/practice/...` 문제 필요 / feedback 모델 구분 / observed loss

### [Online Decision and Regret](lessons/online-convex-optimization/pages/online-decision-and-regret.md)

- TODO: online gradient descent `/practice/...` 문제 필요 / gradient step과 projection / regret
- TODO: multiplicative weights `/practice/...` 문제 필요 / simplex decision 갱신 / entropy
- TODO: online scheduling convex loss `/practice/...` 문제 필요 / sequential decision 설계 / projection
- TODO: bandit vs full information `/practice/...` 문제 필요 / feedback model 구분 / exploration

### [Practice Set](lessons/online-convex-optimization/pages/practice-set.md)

- TODO: online gradient descent `/practice/...` 문제 필요 / gradient step과 projection 구현 / regret
- TODO: dual averaging regret `/practice/...` 문제 필요 / 누적 gradient와 regularizer 해석 / cumulative gradient
- TODO: bandit vs full information `/practice/...` 문제 필요 / feedback 모델 구분 / exploration

### [Randomized Determinant](lessons/randomized-determinant/lesson.md)

- TODO: randomized determinant `/practice/...` 문제 필요 / modular determinant와 prime field 점검 / Gaussian elimination
- TODO: polynomial identity `/practice/...` 문제 필요 / random substitution으로 nonzero 판정 / Schwartz-Zippel
- TODO: Tutte matrix `/practice/...` 문제 필요 / matching 존재성을 determinant로 바꾸기 / skew-symmetric matrix
- TODO: determinant false zero `/practice/...` 문제 필요 / 반복과 seed 검증 / Monte Carlo

### [Matrix-Tree Theorem Applications](lessons/matrix-tree-theorem-applications/lesson.md)

- TODO: matrix-tree theorem `/practice/...` 문제 필요 / 무향 Laplacian cofactor 계산 / spanning tree count
- TODO: directed arborescence `/practice/...` 문제 필요 / root 방향 convention 맞추기 / directed Laplacian
- TODO: edge criticality `/practice/...` 문제 필요 / include/exclude edge count / contraction, deletion
- TODO: multigraph tree count `/practice/...` 문제 필요 / multi-edge와 self-loop 처리 / Laplacian weight

### [Dual Graph Construction](lessons/planar-graph-duality/pages/dual-graph-construction.md)

- TODO: planar dual construction `/practice/...` 문제 필요 / face adjacency로 dual 만들기 / outer face
- TODO: planar cut shortest path `/practice/...` 문제 필요 / cut을 dual path로 변환 / cut-cycle duality
- TODO: half-edge face traversal `/practice/...` 문제 필요 / 좌표에서 face 번호 찾기 / angle sort
- TODO: bridge in dual graph `/practice/...` 문제 필요 / self-loop와 bridge 처리 / Euler formula

### [Practice Set](lessons/planar-graph-duality/pages/practice-set.md)

- TODO: half-edge face traversal `/practice/...` 문제 필요 / 좌표에서 face 번호 찾기 / angle sort
- TODO: planar cut shortest path `/practice/...` 문제 필요 / cut을 dual path로 변환 / cut-cycle duality
- TODO: bridge in dual graph `/practice/...` 문제 필요 / self-loop와 bridge 처리 / Euler formula

## 참고 구현의 보강 조건

- Multipoint Evaluation은 product tree만 만드는 골격 대신, remainder를 실제로 전파하는 구현과 작은 Horner 기준 답 비교를 준비한 뒤 구현 예제를 보강합니다.
- Kinetic Hull은 event별 version·이웃 검증과 실제 event 갱신까지 포함한 문제를 확보해야 합니다. 단순 priority queue wrapper는 예제로 다시 추가하지 않습니다.
- Cut cactus 구성과 질의는 원래 정점 mapping 및 cycle block 처리가 있는 경우에만 구현으로 보강합니다. 일반 tree DFS만으로 대체하지 않습니다.
