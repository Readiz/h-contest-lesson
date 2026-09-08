# h-contest heuristic notes

This repository is the source of truth for h-contest heuristic notes. Lesson source lives in `lessons/` and `lessons.json`; `README.md` and `index.html` are generated entry points.

## 탐색

- 전체 카탈로그: [index.html](index.html)
- Published manifest: https://blog.readiz.com/h-contest-lesson/lessons.json
- API mirror (h-contest 로그인 필요): https://h.readiz.com/api/lessons
- 공개 기록: [CHANGELOG.md](CHANGELOG.md)
- 학습 노트 전체 본문 검토: [LESSON_REVIEW.md](LESSON_REVIEW.md)
- 실전 풀이 중심 개편 계획과 practice TODO: [ROADMAP.md](ROADMAP.md)
- 기여 절차: [CONTRIBUTING.md](CONTRIBUTING.md)

## 작업 흐름

1. `lessons/<lessonId>/lesson.md`와 필요 시 `lessons/<lessonId>/pages/*.md`를 수정합니다.
2. `lessons.json`에서 metadata, page 목록, 선수/다음/연관 레슨을 맞춥니다.
3. 아래 명령으로 파생 파일과 검증 상태를 맞춥니다.

```bash
python3 scripts/generate_catalog.py
python3 scripts/validate_lessons.py
```

이미지나 보조 자료는 `lessons/<lessonId>/lesson-assets/`에 둡니다.

## 학습 로드맵

h-contest 실전 문제를 처음 풀 때는 아래 경로로 시작합니다. 기존 카탈로그 전체의 순번과 선수 관계 개편은 [ROADMAP.md](ROADMAP.md)에 따라 진행합니다. 참고 노트를 모두 선행 학습할 필요는 없습니다.

1. [실전 C++ 기본기와 공통 코드](lessons/cpp-contest-basics/lesson.md): 제출 계약 → 고정 배열 → 필요한 스니펫 → ORDERING의 유효한 기준선.
2. [ORDERING 경로 개선](lessons/heuristic/pages/ordering-route-improvement.md): 번호 순서 → nearest neighbor → 2-opt. 매 단계 같은 TC의 비용과 실행 시간을 비교합니다.
3. [휴리스틱 모델링과 점수](lessons/heuristic/lesson.md): 상태·유효성·목적 함수·이웃 연산·차분 평가를 정리합니다.
4. 이후 실전 연결 개편: 실험/검증 → SA → MINEEXPLORE와 AIRCONTECH의 탐색/행동 분리 → 배정·경로·배치 문제. 현재 진행 단계와 완료 기준은 로드맵을 따릅니다.
5. 정렬·자료구조·그래프·수학과 참고 노트는 문제에서 필요한 작업과 신호를 보고 찾아봅니다.

## 문제 신호별 빠른 길찾기

두 노트 분류와 별개로, 문제에서 먼저 보이는 신호로 읽을 수 있는 개념 지도입니다.

### 구간 질의/업데이트

질의가 많은 문제에서 온라인/오프라인, 업데이트, 좌표 크기, 시간축을 먼저 나눕니다.

- 정적 구간 합: [누적합과 차분 배열](lessons/prefix-sum-difference/lesson.md)
- 점 업데이트 + 구간 질의: [Fenwick Tree](lessons/fenwick-tree/lesson.md) / [Segment Tree](lessons/segment-tree/lesson.md)
- 구간 업데이트/블록 처리: [Segment Tree](lessons/segment-tree/lesson.md) / [Sqrt Decomposition](lessons/sqrt-decomposition/lesson.md)
- 좌표가 크다: [좌표 압축](lessons/coordinate-compression/lesson.md) / [Dynamic Segment Tree](lessons/dynamic-segment-tree/lesson.md)
- 질의를 재정렬할 수 있다: [Offline and Time-Axis Techniques](lessons/offline-time-axis-techniques/lesson.md) / [Sqrt Decomposition](lessons/sqrt-decomposition/lesson.md)
- 되돌리기/버전이 필요하다: [Versioned Data Structures](lessons/versioned-data-structures/lesson.md) / [Offline and Time-Axis Techniques](lessons/offline-time-axis-techniques/lesson.md)

### 최적화

답을 판정으로 바꿀지, DP 전이를 줄일지, 제약을 완화할지부터 구분합니다.

- 단조 판정: [이분 탐색과 파라메트릭 서치](lessons/binary-search/lesson.md) → [Parametric Optimization](lessons/parametric-optimization/lesson.md)
- DP 전이 최적화: [Divide and Conquer DP Optimization](lessons/divide-and-conquer-dp-optimization/lesson.md) / [Knuth Optimization](lessons/knuth-optimization/lesson.md) / [Monge와 SMAWK](lessons/monge-smawk/lesson.md) / [Convex DP Optimization](lessons/convex-dp-optimization/lesson.md)
- 정확히 K개/penalty: [Parametric Optimization](lessons/parametric-optimization/lesson.md) / [Convex Cost Flow](lessons/convex-cost-flow/lesson.md)
- convex 비용: [Convex DP Optimization](lessons/convex-dp-optimization/lesson.md) / [Convex Cost Flow](lessons/convex-cost-flow/lesson.md) / [Online Convex Optimization](lessons/online-convex-optimization/lesson.md)
- 검증/증명: `quadrangle-inequality-proofs` / [Proof와 Invariant](lessons/proof-and-invariants/lesson.md) / [Testing과 Stress Test](lessons/testing-and-stress/lesson.md)

### 그래프

탐색, 최단거리, DAG, 트리, flow/cut, 동적 변화 순서로 문제 신호를 좁힙니다.

- 탐색/연결성: [BFS/DFS와 격자 탐색](lessons/bfs-dfs-grid/lesson.md) / [그래프와 트리 기본 성질](lessons/graph-tree-basics/lesson.md) / [Union-Find 알고리즘](lessons/union-find/lesson.md)
- 최단거리: [0-1 BFS](lessons/zero-one-bfs/lesson.md) / [Dijkstra 최단거리](lessons/dijkstra/lesson.md) / [Bellman-Ford와 음수 사이클](lessons/bellman-ford-negative-cycle/lesson.md) / [Floyd-Warshall](lessons/floyd-warshall/lesson.md)
- DAG 순서: [위상 정렬과 DAG DP](lessons/topological-sort-dag/lesson.md)
- 트리: [트리 심화: 분할 기법](lessons/tree-advanced/lesson.md) / [Link-Cut Tree](lessons/link-cut-tree/lesson.md) / [Euler Tour Tree](lessons/euler-tour-tree/lesson.md)
- Flow/Cut: [Max Flow, Min Cut, Bipartite Matching](lessons/max-flow-min-cut/lesson.md) / [Min-Cost Flow](lessons/min-cost-flow/lesson.md) / [Flow with Lower Bound](lessons/flow-with-lower-bound/lesson.md) / [Graph Cut Structures](lessons/graph-cut-structures/lesson.md)
- 동적/오프라인: [Offline and Time-Axis Techniques](lessons/offline-time-axis-techniques/lesson.md) / [Dynamic Network Optimization](lessons/dynamic-network-optimization/lesson.md)

### 수학/모델링

계산 루틴과 모델링 도구를 분리해, 수식 처리가 필요한 이유부터 확인합니다.

- 기본 계산: [모듈러 연산과 빠른 거듭제곱](lessons/modular-arithmetic/lesson.md) / [정수론 심화: GCD, Extended Euclid, CRT, Sieve](lessons/gcd-extended-euclid-crt/lesson.md) / [조합론: nCr, 포함-배제, Lucas](lessons/combinatorics-ncr/lesson.md)
- 행렬/점화식: [Matrix Exponentiation](lessons/matrix-exponentiation/lesson.md) / [Polynomial and Recurrence Algorithms](lessons/polynomial-recurrence-algorithms/lesson.md)
- 정수론 변환: [Mobius Inversion](lessons/mobius-inversion/lesson.md) / [Dirichlet Convolution](lessons/dirichlet-convolution/lesson.md) / [Multiplicative Functions](lessons/multiplicative-functions/lesson.md) / [Summatory Number Theory](lessons/summatory-number-theory/lesson.md)
- 선형대수 모델링: [XOR Linear Basis](lessons/linear-basis-xor/lesson.md) / [Black-Box Linear Algebra](lessons/black-box-linear-algebra/lesson.md) / [Sparse Linear Systems](lessons/sparse-linear-systems/lesson.md) / [Linear Algebra Applications](lessons/linear-algebra-applications/lesson.md)
- 확률/게임/의사결정: [확률과 기대값](lessons/probability-expected-value/lesson.md) / [Game Theory와 Grundy Number](lessons/game-theory-grundy/lesson.md) / [Probabilistic Decision AI](lessons/probabilistic-decision-ai/lesson.md)

## 심화 트랙 지도

고급 주제는 선형 난이도보다 여러 축의 선택 문제에 가깝습니다. 아래 지도는 허브끼리의 관계를 먼저 보여 줍니다.

### 최적화 트랙

최적화는 하나의 선형 순서가 아니라 판정, 전이 축소, 제약 완화, 증명 검증이 서로 교차합니다.

- A. 판정으로 바꾸기: [이분 탐색과 파라메트릭 서치](lessons/binary-search/lesson.md) → [Parametric Optimization](lessons/parametric-optimization/lesson.md)
- B. DP 전이 줄이기: [Divide and Conquer DP Optimization](lessons/divide-and-conquer-dp-optimization/lesson.md) / [Knuth Optimization](lessons/knuth-optimization/lesson.md) / [Monge와 SMAWK](lessons/monge-smawk/lesson.md) / [Convex DP Optimization](lessons/convex-dp-optimization/lesson.md)
- C. 제약 완화: [Parametric Optimization](lessons/parametric-optimization/lesson.md) / [Convex Cost Flow](lessons/convex-cost-flow/lesson.md)
- D. 증명/검증: [Proof와 Invariant](lessons/proof-and-invariants/lesson.md) / `quadrangle-inequality-proofs` / [Testing과 Stress Test](lessons/testing-and-stress/lesson.md)

### 그래프 트랙

저장소 폴더와 별개로, 학습 목차는 탐색에서 동적 네트워크까지 단계별로 읽습니다.

- 그래프 기본: [BFS/DFS와 격자 탐색](lessons/bfs-dfs-grid/lesson.md) / [그래프와 트리 기본 성질](lessons/graph-tree-basics/lesson.md) / [위상 정렬과 DAG DP](lessons/topological-sort-dag/lesson.md) / [Union-Find 알고리즘](lessons/union-find/lesson.md)
- 최단거리: [0-1 BFS](lessons/zero-one-bfs/lesson.md) / [Dijkstra 최단거리](lessons/dijkstra/lesson.md) / [Bellman-Ford와 음수 사이클](lessons/bellman-ford-negative-cycle/lesson.md) / [Floyd-Warshall](lessons/floyd-warshall/lesson.md)
- 트리: [트리 심화: 분할 기법](lessons/tree-advanced/lesson.md) / [Link-Cut Tree](lessons/link-cut-tree/lesson.md) / [Euler Tour Tree](lessons/euler-tour-tree/lesson.md)
- Flow/Cut: [Max Flow, Min Cut, Bipartite Matching](lessons/max-flow-min-cut/lesson.md) / [Min-Cost Flow](lessons/min-cost-flow/lesson.md) / [Flow with Lower Bound](lessons/flow-with-lower-bound/lesson.md) / [Graph Cut Structures](lessons/graph-cut-structures/lesson.md)
- 동적/오프라인 그래프: [Offline and Time-Axis Techniques](lessons/offline-time-axis-techniques/lesson.md) / [Dynamic Network Optimization](lessons/dynamic-network-optimization/lesson.md)

### 수학 트랙

계산 도구와 모델링 도구를 분리하면 advanced 수학 레슨의 어려운 이유가 더 선명해집니다.

- 수학 기본 계산: [모듈러 연산과 빠른 거듭제곱](lessons/modular-arithmetic/lesson.md) / [정수론 심화: GCD, Extended Euclid, CRT, Sieve](lessons/gcd-extended-euclid-crt/lesson.md) / [조합론: nCr, 포함-배제, Lucas](lessons/combinatorics-ncr/lesson.md) / [Matrix Exponentiation](lessons/matrix-exponentiation/lesson.md)
- 정수론 변환: [Mobius Inversion](lessons/mobius-inversion/lesson.md) / [Dirichlet Convolution](lessons/dirichlet-convolution/lesson.md) / [Multiplicative Functions](lessons/multiplicative-functions/lesson.md) / [Summatory Number Theory](lessons/summatory-number-theory/lesson.md)
- 선형대수 모델링: [XOR Linear Basis](lessons/linear-basis-xor/lesson.md) / [Linear Basis Applications](lessons/linear-basis-applications/lesson.md) / [Black-Box Linear Algebra](lessons/black-box-linear-algebra/lesson.md) / [Linear Algebra Applications](lessons/linear-algebra-applications/lesson.md)
- 확률/게임: [확률과 기대값](lessons/probability-expected-value/lesson.md) / [Game Theory와 Grundy Number](lessons/game-theory-grundy/lesson.md) / [Game Theory Applications](lessons/game-theory-applications/lesson.md) / [Probabilistic Decision AI](lessons/probabilistic-decision-ai/lesson.md)

### 기하 트랙

predicate에서 시작해 convex, sweep, arrangement, duality와 robustness로 확장합니다.

- 기하 입문: [기하 기본: CCW, 선분 교차, Convex Hull](lessons/geometry-ccw-segment-intersection/lesson.md) / [Rotating Calipers](lessons/rotating-calipers/lesson.md)
- Convex polygon: [Minkowski Sum](lessons/minkowski-sum/lesson.md) / [Rotating Calipers Applications](lessons/rotating-calipers-applications/lesson.md) / [Shape Distance Modeling](lessons/shape-distance-modeling/lesson.md)
- Sweep/Arrangement: [Sweep Line Geometry](lessons/sweep-line-geometry/lesson.md) / [Closest Pair Sweep](lessons/closest-pair-sweep/lesson.md) / [Line Arrangement](lessons/line-arrangement/lesson.md) / [Circle Arrangement](lessons/circle-arrangement/lesson.md)
- Half-plane/Voronoi: [Half-Plane Intersection](lessons/half-plane-intersection/lesson.md) / [Voronoi와 Delaunay](lessons/voronoi-delaunay/lesson.md) / [Geometry Robustness and Duality](lessons/geometry-robustness-and-duality/lesson.md)
- Robustness/Advanced: [Geometry Robustness and Duality](lessons/geometry-robustness-and-duality/lesson.md) / [Inversion Geometry](lessons/inversion-geometry/lesson.md)

## 카드 배지 기준

- 난이도: `beginner / intermediate / advanced`
- 난이도 축: `implementation / proof / modeling / selection`
- 성격: `core / implementation / overview / reference / experimental`
- 완성도: `concept-only / partial / full`
- 연습: `none / todo / linked / verified`
- 대상: `contest-core / advanced-contest / research-reference`

## 카테고리 요약

| 카테고리 | 설명 | 레슨 수 |
| --- | --- | ---: |
| 휴리스틱 기본 및 심화 노트 | 현재 h-contest 문제 풀이에 바로 쓰는 기본 구현, 모델링, 최적화, 검증 개념을 모은 직접 학습 트랙입니다. | 30 |
| 휴리스틱 참고 노트 | 현재 문제 풀이의 직접 범위를 넘는 전통 알고리즘, 희소 고급 도구, 장기 확장용 레퍼런스 노트입니다. | 69 |

전체 레슨과 하위 페이지 링크는 [index.html](index.html)에서 확인합니다.
