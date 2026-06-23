# h-contest lesson content

This repository is the source of truth for h-contest algorithm lessons.
The public API is generated from or synchronized with this repository.

- Published manifest: https://blog.readiz.com/h-contest-lesson/lessons.json
- API mirror: https://h.readiz.com/api/lessons

## Contributing

Pull requests should edit this repository directly. For details, see [CONTRIBUTING.md](CONTRIBUTING.md).

Planned topics and missing practice-problem links are tracked in [ROADMAP.md](ROADMAP.md).

When adding a new lesson, update these source files:

- `lessons/<lessonId>/lesson.md`
- `lessons.json` (`folderId` included, optional `pages` included)

Then regenerate derived files:

```bash
python3 scripts/generate_catalog.py
python3 scripts/validate_lessons.py
```

Generated files:

- `README.md`
- `index.html`

If the lesson uses images or other local assets, add them under `lessons/<lessonId>/lesson-assets/`.

## 학습 로드맵

처음 보는 주제라면 아래 순서로 훑는 것을 권장합니다. 이미 익숙한 내용은 건너뛰고, 각 레슨의 `prerequisites`와 `nextLessons` 메타데이터를 참고해 앞뒤 개념을 확인하세요.

1. 입문 0단계: 복잡도 감각, 대회용 C++ 기본기
2. 입문 1단계: 정렬, 누적합, 이분 탐색, 투 포인터
3. 입문 2단계: BFS/DFS, 그리디, 우선순위 큐, Union-Find, 좌표 압축
4. 중급 1단계: DP, Dijkstra, 위상 정렬, Fenwick Tree, Segment Tree, 모듈러 연산
5. 중급 2단계: 트리 심화, TSP, Treap, 휴리스틱
6. 심화 확장: 문자열 매칭, SCC/2-SAT, Flow, 정수론 심화, 기하, 오프라인 쿼리, 검증/증명

## Lessons

### 기본기

정렬, 누적합, 이분 탐색처럼 문제 풀이의 출발점이 되는 개념입니다.

- [복잡도와 입력 크기 감각](lessons/complexity-input-size/lesson.md)
- [대회용 C++ 기본기](lessons/cpp-contest-basics/lesson.md)
- [정렬 알고리즘](lessons/sorting/lesson.md)
- [누적합과 차분 배열](lessons/prefix-sum-difference/lesson.md)
- [투 포인터와 슬라이딩 윈도우](lessons/two-pointers-sliding-window/lesson.md)
- [이분 탐색과 파라메트릭 서치](lessons/binary-search/lesson.md)
- [좌표 압축](lessons/coordinate-compression/lesson.md)

### 전략과 최적화

그리디, 동적 계획법, 휴리스틱처럼 풀이 방향을 정하는 사고 도구입니다.

- [그리디 알고리즘](lessons/greedy/lesson.md)
- [휴리스틱 알고리즘](lessons/heuristic/lesson.md)
  - [문제 모델링과 점수 함수](lessons/heuristic/pages/modeling-and-scoring.md)
  - [초기해와 지역 탐색](lessons/heuristic/pages/search-strategies.md)
  - [Beam Search와 시간 관리](lessons/heuristic/pages/beam-and-time.md)
  - [실험 로그와 점검](lessons/heuristic/pages/experiments-and-checklist.md)
- [동적 계획법](lessons/dynamic-programming/lesson.md)
  - [상태와 전이](lessons/dynamic-programming/pages/state-and-transition.md)
  - [배낭과 LIS](lessons/dynamic-programming/pages/knapsack-and-lis.md)
  - [구간, 트리, 비트마스크 DP](lessons/dynamic-programming/pages/interval-tree-bitmask.md)
  - [Digit DP와 최적화 감각](lessons/dynamic-programming/pages/digit-dp-and-optimization.md)
  - [연습 문제](lessons/dynamic-programming/pages/practice-set.md)
- [TSP와 해밀턴 경로](lessons/tsp-hamiltonian/lesson.md)
  - [완전탐색과 비트마스크 DP](lessons/tsp-hamiltonian/pages/search-and-dp.md)
  - [경로 복원과 메모리](lessons/tsp-hamiltonian/pages/restore-and-memory.md)
  - [휴리스틱 개선과 선택 기준](lessons/tsp-hamiltonian/pages/heuristic-and-choices.md)
- [Testing과 Stress Test](lessons/testing-and-stress/lesson.md)
- [Proof와 Invariant](lessons/proof-and-invariants/lesson.md)
- [Divide and Conquer DP Optimization](lessons/divide-and-conquer-dp-optimization/lesson.md)
- [Knuth Optimization](lessons/knuth-optimization/lesson.md)
- [Monge와 SMAWK](lessons/monge-smawk/lesson.md)
- [Alien Optimization](lessons/alien-optimization/lesson.md)
- [Slope Trick](lessons/slope-trick/lesson.md)
- [Convex Cost Flow](lessons/convex-cost-flow/lesson.md)
- [Min-Plus Convolution](lessons/min-plus-convolution/lesson.md)
- [Convex DP Modeling](lessons/convex-dp-modeling/lesson.md)
- [Parametric DP](lessons/parametric-dp/lesson.md)
- [Quadrangle Inequality Proofs](lessons/quadrangle-inequality-proofs/lesson.md)
- [CHT DP Applications](lessons/cht-dp-applications/lesson.md)

### 그래프와 트리

탐색, 최단거리, DAG, 트리 구조를 다루는 그래프 계열 개념입니다.

- [BFS/DFS와 격자 탐색](lessons/bfs-dfs-grid/lesson.md)
- [그래프와 트리 기본 성질](lessons/graph-tree-basics/lesson.md)
  - [표현과 기본 탐색](lessons/graph-tree-basics/pages/representation-and-traversal.md)
  - [트리 지름과 센트로이드](lessons/graph-tree-basics/pages/tree-diameter-centroid.md)
  - [최소 신장 트리](lessons/graph-tree-basics/pages/mst-kruskal-prim.md)
- [0-1 BFS](lessons/zero-one-bfs/lesson.md)
- [위상 정렬과 DAG DP](lessons/topological-sort-dag/lesson.md)
- [Dijkstra 최단거리](lessons/dijkstra/lesson.md)
- [Bellman-Ford와 음수 사이클](lessons/bellman-ford-negative-cycle/lesson.md)
- [SCC와 2-SAT](lessons/scc-2sat/lesson.md)
- [Max Flow, Min Cut, Bipartite Matching](lessons/max-flow-min-cut/lesson.md)
- [Matching과 Cover Duality](lessons/matching-cover-duality/lesson.md)
- [Min-Cost Flow](lessons/min-cost-flow/lesson.md)
- [Flow with Lower Bound](lessons/flow-with-lower-bound/lesson.md)
- [General Matching](lessons/general-matching/lesson.md)
- [Floyd-Warshall](lessons/floyd-warshall/lesson.md)
- [Dominator Tree](lessons/dominator-tree/lesson.md)
- [Weighted Matching](lessons/weighted-matching/lesson.md)
- [Directed MST](lessons/directed-mst/lesson.md)
- [Dynamic Connectivity](lessons/dynamic-connectivity/lesson.md)
- [Gomory-Hu Tree](lessons/gomory-hu-tree/lesson.md)
  - [4정점 construction trace](lessons/gomory-hu-tree/pages/construct-trace.md)
- [Dynamic MST](lessons/dynamic-mst/lesson.md)
- [Global Min Cut](lessons/global-min-cut/lesson.md)
- [Cut Sparsification](lessons/cut-sparsification/lesson.md)
- [Global Min Cut Applications](lessons/global-min-cut-applications/lesson.md)
- [Cactus Representation](lessons/cactus-representation/lesson.md)
- [Randomized Min Cut](lessons/randomized-min-cut/lesson.md)

### 자료구조

우선순위 큐, Union-Find, 구간 자료구조, 균형 트리 계열을 모았습니다.

- [우선순위 큐와 힙](lessons/priority-queue-heap/lesson.md)
- [Meldable Heap](lessons/meldable-heap/lesson.md)
- [Union-Find 알고리즘](lessons/union-find/lesson.md)
- [Sqrt Decomposition](lessons/sqrt-decomposition/lesson.md)
- [Sparse Table과 RMQ](lessons/sparse-table-rmq/lesson.md)
- [Fenwick Tree](lessons/fenwick-tree/lesson.md)
- [Segment Tree](lessons/segment-tree/lesson.md)
  - [기본 구간 질의](lessons/segment-tree/pages/basic-range-query.md)
  - [Bottom-up 구현](lessons/segment-tree/pages/bottom-up-implementation.md)
  - [Lazy Propagation](lessons/segment-tree/pages/lazy-propagation.md)
  - [Monoid와 Lazy 합성](lessons/segment-tree/pages/monoid-and-lazy-composition.md)
- [Persistent Segment Tree](lessons/persistent-segment-tree/lesson.md)
- [Persistent Lazy Segment Tree](lessons/persistent-lazy-segment-tree/lesson.md)
- [Convex Hull Trick과 Li Chao Tree](lessons/convex-hull-trick-li-chao/lesson.md)
- [Wavelet Tree](lessons/wavelet-tree/lesson.md)
- [Wavelet Matrix](lessons/wavelet-matrix/lesson.md)
- [Succinct Bitvector](lessons/succinct-bitvector/lesson.md)
- [트리 심화: 분할 기법](lessons/tree-advanced/lesson.md)
- [Link-Cut Tree](lessons/link-cut-tree/lesson.md)
- [BST 계열: AVL, Splay, Treap](lessons/treap/lesson.md)
  - [BST와 회전 기본기](lessons/treap/pages/bst-and-rotation.md)
  - [AVL과 Splay Tree](lessons/treap/pages/balanced-bst.md)
  - [Treap 핵심 연산](lessons/treap/pages/treap-core.md)
  - [순위, 전체 구현, Implicit Treap](lessons/treap/pages/order-statistics-and-implicit.md)
- [오프라인 쿼리: Mo, DSU Rollback, Parallel Binary Search](lessons/offline-queries/lesson.md)
- [Dynamic Segment Tree](lessons/dynamic-segment-tree/lesson.md)
- [Euler Tour Tree](lessons/euler-tour-tree/lesson.md)
- [Persistent Union-Find](lessons/persistent-union-find/lesson.md)
- [Rollback Techniques](lessons/rollback-techniques/lesson.md)
- [Retroactive Data Structures](lessons/retroactive-data-structures/lesson.md)
- [Offline Range Query Techniques](lessons/offline-range-query-techniques/lesson.md)
- [Convex Hull Trick Variants](lessons/convex-hull-trick-variants/lesson.md)
- [Persistent Queue and Stack](lessons/persistent-queue-stack/lesson.md)
- [Persistent Sequence Queries](lessons/persistent-sequence-queries/lesson.md)

### 문자열

패턴 매칭, 해싱, Trie, suffix 구조처럼 문자열을 빠르게 비교하고 탐색하는 개념입니다.

- [문자열 매칭: KMP, Z, Rolling Hash](lessons/string-matching-kmp-z/lesson.md)
- [Trie와 Aho-Corasick](lessons/trie-aho-corasick/lesson.md)
- [Suffix Array와 LCP](lessons/suffix-array-lcp/lesson.md)
- [Suffix Automaton](lessons/suffix-automaton/lesson.md)
- [Palindromic Tree](lessons/palindromic-tree/lesson.md)
- [Suffix와 Palindrome 응용](lessons/suffix-palindrome-applications/lesson.md)
- [Lyndon Factorization](lessons/lyndon-factorization/lesson.md)
- [Suffix Tree와 Ukkonen](lessons/suffix-tree-ukkonen/lesson.md)
  - [abab$ phase trace](lessons/suffix-tree-ukkonen/pages/phase-trace.md)
- [Runs와 문자열 주기](lessons/runs-periodicity/lesson.md)
- [Suffix Array 응용 패턴](lessons/suffix-array-applications/lesson.md)
- [Border Automaton](lessons/border-automaton/lesson.md)
- [Suffix Automaton Applications](lessons/suffix-automaton-applications/lesson.md)
- [Generalized Suffix Automaton](lessons/generalized-suffix-automaton/lesson.md)
- [Palindrome Query Structures](lessons/palindrome-query-structures/lesson.md)
- [Palindrome Range DP](lessons/palindrome-range-dp/lesson.md)
- [String Period Query Applications](lessons/string-period-query-applications/lesson.md)

### 기하

CCW, 선분 교차, 볼록 껍질처럼 좌표와 벡터를 다루는 기하 기본 개념입니다.

- [기하 기본: CCW, 선분 교차, Convex Hull](lessons/geometry-ccw-segment-intersection/lesson.md)
- [Rotating Calipers](lessons/rotating-calipers/lesson.md)
- [Sweep Line Geometry](lessons/sweep-line-geometry/lesson.md)
- [Closest Pair Sweep](lessons/closest-pair-sweep/lesson.md)
- [Line Arrangement](lessons/line-arrangement/lesson.md)
- [Voronoi와 Delaunay](lessons/voronoi-delaunay/lesson.md)
- [Half-Plane Intersection](lessons/half-plane-intersection/lesson.md)
- [Minkowski Sum](lessons/minkowski-sum/lesson.md)
- [Rotating Calipers Applications](lessons/rotating-calipers-applications/lesson.md)
- [Shape Distance Modeling](lessons/shape-distance-modeling/lesson.md)
- [Circle Geometry](lessons/circle-geometry/lesson.md)
- [Circle Arrangement](lessons/circle-arrangement/lesson.md)
- [Robust Geometry Predicates](lessons/robust-geometry-predicates/lesson.md)

### 수학

모듈러 연산, 정수론, 조합론처럼 경우의 수와 수식 처리에 필요한 개념입니다.

- [모듈러 연산과 빠른 거듭제곱](lessons/modular-arithmetic/lesson.md)
- [정수론 심화: GCD, Extended Euclid, CRT, Sieve](lessons/gcd-extended-euclid-crt/lesson.md)
- [조합론: nCr, 포함-배제, Lucas](lessons/combinatorics-ncr/lesson.md)
- [Matrix Exponentiation](lessons/matrix-exponentiation/lesson.md)
- [Linear Recurrence와 Kitamasa](lessons/linear-recurrence-kitamasa/lesson.md)
- [FFT와 NTT](lessons/fft-ntt/lesson.md)
- [Formal Power Series](lessons/formal-power-series/lesson.md)
- [FPS Log와 Exp](lessons/fps-log-exp/lesson.md)
- [Multipoint Evaluation](lessons/multipoint-evaluation/lesson.md)
- [Bostan-Mori](lessons/bostan-mori/lesson.md)
- [Polynomial Interpolation](lessons/polynomial-interpolation/lesson.md)
- [확률과 기대값](lessons/probability-expected-value/lesson.md)
- [Game Theory와 Grundy Number](lessons/game-theory-grundy/lesson.md)
- [Minimax와 Alpha-Beta Pruning](lessons/minimax-alpha-beta/lesson.md)
- [Monte Carlo Tree Search](lessons/monte-carlo-tree-search/lesson.md)
- [XOR Linear Basis](lessons/linear-basis-xor/lesson.md)
- [Mobius Inversion](lessons/mobius-inversion/lesson.md)
- [Linear Basis Applications](lessons/linear-basis-applications/lesson.md)
- [Dirichlet Convolution](lessons/dirichlet-convolution/lesson.md)
- [Multiplicative Functions](lessons/multiplicative-functions/lesson.md)
- [Markov Decision Process](lessons/markov-decision-process/lesson.md)
- [Imperfect Information Search](lessons/imperfect-information-search/lesson.md)
- [Summatory Number Theory](lessons/summatory-number-theory/lesson.md)
- [Linear Recurrence Applications](lessons/linear-recurrence-applications/lesson.md)
- [Recurrence Guessing](lessons/recurrence-guessing/lesson.md)
- [Berlekamp-Massey](lessons/berlekamp-massey/lesson.md)
- [Partially Observable MDP](lessons/pomdp/lesson.md)
