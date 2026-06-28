# h-contest lesson content changelog

이 문서는 이미 공개된 레슨의 이동 기록과 콘텐츠 보강 완료 내역을 보관합니다. 아직 공개하지 않은 후보와 practice link TODO는 [ROADMAP.md](ROADMAP.md)에서 관리합니다.

## 2026-06 구조 개편

- `alien-optimization`, `parametric-dp`, `fractional-programming-dp`, `lagrangian-relaxation-patterns`를 `parametric-optimization` 허브와 하위 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `markov-decision-process`, `reinforcement-learning-basics`, `stochastic-shortest-path`를 `stochastic-decision-process` 허브와 하위 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `online-convex-optimization`, `dual-averaging`을 `online-convex-optimization` 허브와 하위 페이지로 재배치했습니다. 기존 `dual-averaging` 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `matroid-intersection`, `matroid-parity`, `matroid-union`을 `matroid-algorithms` 허브와 하위 reference 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `planar-graph-duality`는 독립 lessonId를 유지하되, half-edge face traversal, cut-cycle duality, planar min-cut 페이지를 추가해 구현 전제조건을 보강했습니다.
- `global-min-cut`, `gomory-hu-tree`, `cut-sparsification`, `global-min-cut-applications`, `cactus-representation`, `randomized-min-cut`, `cut-cactus-applications`를 `graph-cut-structures` 허브와 하위 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `graph-cut-structures` Practice Set에 Stoer-Wagner phase trace와 global min cut 로컬 연습을 추가했습니다.
- `persistent-segment-tree`, `persistent-lazy-segment-tree`, `persistent-union-find`, `persistent-queue-stack`, `persistent-sequence-queries`를 `versioned-data-structures` 허브와 하위 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `versioned-data-structures` Practice Set에 prefix root 차이 trace와 persistent segment tree kth query 로컬 연습을 추가했습니다.
- `offline-queries`, `rollback-techniques`, `dynamic-connectivity`, `offline-range-query-techniques`, `retroactive-data-structures`를 `offline-time-axis-techniques` 허브와 하위 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `offline-time-axis-techniques` Practice Set에 active interval trace와 Rollback DSU + Segment Tree over Time 로컬 연습을 추가했습니다.
- `convex-dp-modeling`, `convex-hull-trick-li-chao`, `convex-hull-trick-variants`, `cht-dp-applications`, `slope-trick`, `min-plus-convolution`, `kinetic-hull`, `fully-dynamic-cht`를 `convex-dp-optimization` 허브와 하위 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `suffix-array-lcp`, `suffix-array-applications`, `suffix-automaton`, `suffix-automaton-applications`, `generalized-suffix-automaton`, `suffix-tree-ukkonen`, `runs-periodicity`, `border-automaton`, `string-period-query-applications`를 `suffix-periodicity-structures` 허브와 하위 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `suffix-periodicity-structures` Practice Set에 `banana` suffix array/LCP trace와 distinct substring count 로컬 연습을 추가했습니다.
- `palindromic-tree`, `palindrome-query-structures`, `palindrome-range-dp`, `suffix-palindrome-applications`를 `palindrome-structures` 허브와 하위 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `palindrome-structures` Practice Set에 `ababa` Eertree trace와 distinct palindrome count 로컬 연습을 추가했습니다.
- `fft-ntt`, `formal-power-series`, `fps-log-exp`, `multipoint-evaluation`, `polynomial-interpolation`, `generating-function-modeling`, `linear-recurrence-kitamasa`, `bostan-mori`, `linear-recurrence-applications`, `recurrence-guessing`, `berlekamp-massey`를 `polynomial-recurrence-algorithms` 허브와 하위 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `polynomial-recurrence-algorithms` Practice Set에 Fibonacci coefficient trace와 Kitamasa nth-term 로컬 연습을 추가했습니다.
- `stochastic-decision-process`, `monte-carlo-tree-search`, `imperfect-information-search`, `pomdp`, `point-based-value-iteration`, `pomcp`, `bayesian-bandits`, `online-planning-evaluation`를 `probabilistic-decision-ai` reference 허브와 하위 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `dynamic-flow`, `dynamic-mst`를 `dynamic-network-optimization` 허브와 하위 페이지로 재배치하고, `graph-cut-structures`와 `dynamic-mst` 사이의 순환 선수 관계를 제거했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `dynamic-network-optimization` Practice Set에 residual reuse trace와 incremental max-flow runner 로컬 연습을 추가해 dynamic-flow 보강 기준을 채웠습니다.
- `robust-geometry-predicates`, `power-diagram`, `robust-delaunay`, `3d-convex-hull`, `regular-triangulation`을 `geometry-robustness-and-duality` 허브와 하위 페이지로 재배치했습니다. 기존 경로에는 새 허브로 안내하는 짧은 이동 문서를 남겼습니다.
- `parametric-optimization`과 `convex-dp-optimization` 사이의 순환 선수 관계를 제거하고 서로를 related track으로 정리했습니다.
- `linear-algebra-applications`에 GF(2) basis, sparse solver, determinant, matrix-tree, recurrence를 먼저 고르는 decision map을 추가하고 overview metadata를 붙였습니다.
- `linear-algebra-applications`에 Decision Map Practice 페이지를 추가해 GF(2) rank trace, 로컬 XOR constraint counter, Matrix-Tree counting 연습을 연결했습니다.
- `probabilistic-decision-ai`에 full-information, bandit, simulator, hidden-state observation을 먼저 구분하는 Feedback Model Boundary 페이지와 로컬 분류 연습을 추가했습니다.
- `lessonType`, `status`, `practiceStatus`, `implementationStatus`, `audience`, `seriesId`, `parentLessonId` metadata 검증 기반을 추가했습니다.
- `matroid-algorithms` 허브는 일반 구현 레슨이 아니라 `reference` 성격으로 표시했습니다.

## 2026-06 공개 레슨 이동 기록

- `bellman-ford-negative-cycle`: Dijkstra의 음수 간선 한계를 받아 주는 그래프 최단거리 레슨으로 공개했습니다. 남은 그래프 심화는 SCC/2-SAT와 Flow/Matching 쪽으로 이어갑니다.
- `string-matching-kmp-z`: 문자열 기본 공백을 메우기 위해 KMP, Z algorithm, rolling hash를 하나의 입문 레슨으로 공개했습니다. 남은 문자열 심화는 Trie/Aho-Corasick과 Suffix Array/LCP 쪽으로 이어갑니다.
- `scc-2sat`: 위상 정렬 이후 방향 그래프 심화로 SCC, condensation graph, implication graph, 2-SAT 판정을 공개했습니다. 남은 그래프 심화는 Flow/Matching 쪽으로 이어갑니다.
- `max-flow-min-cut`: Dinic 기반 Max Flow, Min Cut 해석, Bipartite Matching 모델링을 그래프 심화 레슨으로 공개했습니다. 비용까지 포함하는 확장은 Min-Cost Flow 후보로 남깁니다.
- `geometry-ccw-segment-intersection`: CCW, 선분 교차, monotonic chain Convex Hull을 기하 입문 레슨으로 공개했습니다. 남은 기하 심화는 rotating calipers와 sweep line 쪽으로 이어갑니다.
- `offline-queries`: Mo's Algorithm, DSU Rollback, Parallel Binary Search를 오프라인 질의 처리 레슨으로 공개했습니다. 남은 확장은 persistent data structure와 더 세부적인 오프라인 기법입니다.
- `gcd-extended-euclid-crt`: gcd, extended Euclid, 일반 CRT, SPF sieve를 정수론 심화 레슨으로 공개했습니다. 남은 수학 심화는 조합론, 행렬 거듭제곱, FFT/NTT 쪽으로 이어갑니다.
- `testing-and-stress`: edge case, brute force, random stress, 성능 테스트를 풀이 검증 레슨으로 공개했습니다.
- `proof-and-invariants`: invariant, exchange argument, monotonicity, DP 증명 틀, counterexample를 풀이 정당성 레슨으로 공개했습니다.
- `trie-aho-corasick`: KMP/Z 이후 문자열 다중 패턴 매칭으로 이어지는 Trie, 실패 링크, 출력 전파, 각 패턴별 등장 집계를 공개했습니다. 남은 문자열 심화는 Suffix Array/LCP 이후 suffix automaton 후보로 이어갑니다.
- `suffix-array-lcp`: suffix 정렬, Kasai LCP, 패턴 검색, 반복/서로 다른 부분 문자열 계산을 문자열 심화 레슨으로 공개했습니다. 남은 문자열 심화는 suffix automaton 후보로 이어갑니다.
- `min-cost-flow`: Max Flow 이후 비용이 붙은 유량 모델로 이어지는 residual cost, shortest augmenting path, assignment 모델링을 공개했습니다. 남은 그래프 심화는 Floyd-Warshall과 matching/cover duality 후보로 이어갑니다.
- `rotating-calipers`: Convex Hull 이후 antipodal pair, hull 지름, 폭 계산으로 이어지는 기하 심화 레슨을 공개했습니다. 남은 기하 심화는 sweep line geometry 후보로 이어갑니다.
- `sparse-table-rmq`: 정적 배열의 RMQ, idempotent 연산, LCP RMQ, Euler Tour LCA 연결을 자료구조 심화 레슨으로 공개했습니다. 남은 자료구조 확장은 persistent segment tree 후보로 이어갑니다.
- `combinatorics-ncr`: factorial 기반 nCr, 포함-배제, Lucas 정리를 모듈러 조합론 레슨으로 공개했습니다. 남은 수학 심화는 matrix exponentiation과 FFT/NTT 후보로 이어갑니다.
- `persistent-segment-tree`: Segment Tree 이후 path copying, 버전 root, prefix 차이 기반 k번째 수 질의를 공개했습니다. 남은 자료구조 확장은 wavelet tree와 더 세부적인 rollback 기법 후보로 이어갑니다.
- `suffix-automaton`: Suffix Array/LCP 이후 모든 부분 문자열을 상태로 압축하는 문자열 automaton을 공개했습니다. 남은 문자열 심화는 palindromic tree 후보로 이어갑니다.
- `floyd-warshall`: 모든 쌍 최단거리, transitive closure, 경로 복원, 음수 사이클 영향 점검을 공개했습니다. 남은 그래프 심화는 matching/cover duality 후보로 이어갑니다.
- `matrix-exponentiation`: 선형 점화식, 그래프 walk 수, affine transform을 행렬 빠른 거듭제곱으로 처리하는 수학/DP 레슨을 공개했습니다. 남은 수학 심화는 FFT/NTT와 polynomial 계열로 이어갑니다.
- `fft-ntt`: 다항식 곱셈, convolution 모델링, NTT 구현, pair count 응용을 공개했습니다. 남은 polynomial 심화는 formal power series 후보로 이어갑니다.
- `matching-cover-duality`: 이분 매칭에서 minimum vertex cover, maximum independent set, DAG path cover로 이어지는 duality 모델링을 공개했습니다. 남은 그래프 심화는 일반 matching 또는 flow 변형 후보로 이어갑니다.
- `sweep-line-geometry`: 이벤트 정렬, active set, y구간 cover tree를 이용한 직사각형 합집합 넓이와 선분 sweep 관점을 공개했습니다. 남은 기하 심화는 closest pair와 더 세부적인 line arrangement 후보로 이어갑니다.
- `convex-hull-trick-li-chao`: 직선으로 분리되는 DP 전이, Li Chao Tree, CHT 선택 조건을 공개했습니다. 남은 DP 최적화는 divide-and-conquer와 Knuth 후보로 이어갑니다.
- `divide-and-conquer-dp-optimization`: layer DP의 opt 단조성을 이용한 재귀적 후보 범위 축소를 공개했습니다. 남은 DP 최적화는 Knuth optimization 후보로 이어갑니다.
- `probability-expected-value`: 확률 분포 DP, 기대값 식, 기대값의 선형성, 순환 상태와 모듈러 확률을 공개했습니다. 남은 수학/전략 심화는 game theory와 Markov chain 후보로 이어갑니다.
- `palindromic-tree`: 모든 서로 다른 palindrome substring을 Eertree 노드로 압축하고 occurrence를 누적하는 문자열 심화 레슨을 공개했습니다. 남은 문자열 심화는 suffix/palindrome 응용 문제 쪽으로 이어갑니다.
- `wavelet-tree`: 정적 배열의 구간 kth, rank, frequency 질의를 값 범위와 index 범위 변환으로 처리하는 자료구조 레슨을 공개했습니다. 남은 자료구조 심화는 wavelet matrix나 succinct 구조 후보로 이어갑니다.
- `formal-power-series`: FPS의 계수 표현, 미분/적분, polynomial inverse, 생성함수 연결을 공개했습니다. 남은 polynomial 심화는 FPS log/exp와 convolution DP 후보로 이어갑니다.
- `knuth-optimization`: interval DP의 opt 단조 범위를 이용하는 Knuth Optimization을 공개했습니다. 남은 DP 최적화는 Monge/SMAWK 후보로 이어갑니다.
- `game-theory-grundy`: impartial game, mex, Sprague-Grundy theorem, xor 합성을 공개했습니다. 남은 게임/전략 심화는 minimax와 Markov chain 후보로 이어갑니다.
- `flow-with-lower-bound`: lower/upper bound가 있는 간선 제약을 feasible circulation으로 바꾸는 flow 심화를 공개했습니다. 남은 그래프 심화는 일반 matching 후보로 이어갑니다.
- `closest-pair-sweep`: x sweep과 active y set으로 최근접 점 쌍 후보를 제한하는 기하 심화를 공개했습니다. 남은 기하 심화는 line arrangement 후보로 이어갑니다.
- `monge-smawk`: Monge inequality, totally monotone row minima, SMAWK column reduction을 DP 최적화 심화로 공개했습니다.
- `fps-log-exp`: FPS log, exp, power 연산 조건과 Newton iteration 흐름을 polynomial 심화로 공개했습니다. 남은 수학 심화는 선형 점화식 고속 계산 후보로 이어갑니다.
- `minimax-alpha-beta`: game tree minimax, alpha-beta pruning, move ordering을 게임 탐색 레슨으로 공개했습니다. 남은 게임/탐색 심화는 MCTS 후보로 이어갑니다.
- `general-matching`: 일반 무향 그래프의 maximum cardinality matching과 Edmonds blossom 수축을 공개했습니다. 남은 그래프 심화는 dominator tree나 weighted matching 후보로 이어갑니다.
- `wavelet-matrix`: level별 bitvector rank로 kth/count 질의를 처리하는 Wavelet Matrix를 공개했습니다. 남은 succinct 자료구조 심화는 bitvector 후보로 이어갑니다.
- `line-arrangement`: 직선 정규화, rational 교점 dedup, arrangement 영역 수와 선분 sweep 확장 관점을 공개했습니다. 남은 기하 심화는 Voronoi/Delaunay나 half-plane 후보로 이어갑니다.
- `linear-recurrence-kitamasa`: characteristic polynomial과 Kitamasa 방식으로 선형 점화식의 n번째 항을 계산하는 수학 심화를 공개했습니다. 남은 polynomial 심화는 multipoint/Bostan-Mori 후보로 이어갑니다.
- `monte-carlo-tree-search`: UCB, rollout, backpropagation을 이용한 확률적 게임 탐색을 공개했습니다. 남은 게임/탐색 심화는 Markov decision process 후보로 이어갑니다.
- `suffix-palindrome-applications`: suffix 구조와 palindromic tree를 문제 신호별로 선택하는 문자열 응용 레슨을 공개했습니다. 남은 문자열 심화는 Lyndon factorization 후보로 이어갑니다.
- `dominator-tree`: flow graph의 immediate dominator와 Lengauer-Tarjan 흐름을 그래프 심화로 공개했습니다. 남은 그래프 심화는 weighted matching 후보로 이어갑니다.
- `succinct-bitvector`: rank/select와 superblock/block 기반 bitvector를 Wavelet Matrix 내부 구조와 연결해 공개했습니다. 남은 자료구조 심화는 persistent lazy 구조 후보로 이어갑니다.
- `multipoint-evaluation`: subproduct tree와 polynomial remainder 기반의 다점 평가 관점을 공개했습니다. 남은 polynomial 심화는 Bostan-Mori 후보로 이어갑니다.
- `alien-optimization`: Lagrangian relaxation, penalty DP, count 단조성을 이용한 Alien Optimization을 공개했습니다. 남은 DP 최적화는 slope/convex 계열 후보로 이어갑니다.
- `lyndon-factorization`: Lyndon word, Chen-Fox-Lyndon decomposition, Duval algorithm, minimum rotation을 문자열 심화 레슨으로 공개했습니다. 남은 문자열 심화는 suffix tree나 runs/periodicity 후보로 이어갑니다.
- `weighted-matching`: cardinality와 weight 목적식 차이, small-N bitmask DP, assignment/min-cost/weighted blossom 경계를 그래프 심화 레슨으로 공개했습니다. 남은 그래프 심화는 directed MST 후보로 이어갑니다.
- `persistent-lazy-segment-tree`: lazy range update와 path copying을 결합한 versioned range add/range sum 구조를 공개했습니다. 남은 자료구조 심화는 link-cut tree 후보로 이어갑니다.
- `bostan-mori`: rational generating function의 n번째 계수 추출과 선형 점화식 연결을 polynomial 심화 레슨으로 공개했습니다. 남은 수학 심화는 polynomial interpolation 후보로 이어갑니다.
- `voronoi-delaunay`: Voronoi diagram과 Delaunay triangulation의 쌍대성, in-circle predicate, Euclidean MST 응용 관점을 기하 심화 레슨으로 공개했습니다. 남은 기하 심화는 half-plane intersection 후보로 이어갑니다.
- `suffix-tree-ukkonen`: 압축 suffix trie, active point, suffix link, sentinel 처리와 generalized suffix tree 관점을 문자열 구조 심화로 공개했습니다. 남은 문자열 심화는 runs/periodicity 후보로 이어갑니다.
- `directed-mst`: Chu-Liu/Edmonds arborescence, incoming edge 선택, cycle contraction, 비용 보정을 방향 그래프 최적화 레슨으로 공개했습니다. 남은 그래프 심화는 dynamic connectivity 후보로 이어갑니다.
- `link-cut-tree`: access, makeroot, link/cut, path aggregate를 splay 기반 dynamic tree 자료구조로 공개했습니다. 남은 자료구조 심화는 dynamic segment tree 후보로 이어갑니다.
- `polynomial-interpolation`: Lagrange interpolation, consecutive x 최적화, finite difference, 계수 복원 관점을 polynomial 심화로 공개했습니다. 남은 수학 심화는 linear basis/xor 후보로 이어갑니다.
- `half-plane-intersection`: 반평면 표현, angle sort, deque intersection, bounding box와 Voronoi cell 연결을 기하 심화로 공개했습니다. 남은 기하 심화는 Minkowski sum 후보로 이어갑니다.
- `runs-periodicity`: 문자열 period, border chain, Fine-Wilf 직관, run의 maximal 반복 조건을 문자열 심화로 공개했습니다. 남은 문자열 심화는 suffix array 응용 후보로 이어갑니다.
- `dynamic-connectivity`: 간선 활성 구간, 시간축 Segment Tree, Rollback DSU로 오프라인 동적 연결성 질의를 처리하는 그래프 심화를 공개했습니다. 남은 그래프 심화는 Gomory-Hu Tree 후보로 이어갑니다.
- `dynamic-segment-tree`: 큰 좌표 범위에서 필요한 node만 만드는 sparse Segment Tree와 lazy range update를 공개했습니다. 남은 자료구조 심화는 Euler Tour Tree 후보로 이어갑니다.
- `linear-basis-xor`: GF(2) 기저로 maximum xor, 표현 가능성, rank와 그래프 cycle xor를 다루는 수학 심화를 공개했습니다. 남은 수학 심화는 Mobius inversion 후보로 이어갑니다.
- `slope-trick`: convex piecewise-linear 비용 함수를 두 heap과 lazy shift로 관리하는 DP 최적화 심화를 공개했습니다. 남은 DP 최적화는 convex cost flow 후보로 이어갑니다.
- `suffix-array-applications`: Suffix Array 구간 탐색, LCP RMQ, k번째 substring, 여러 문자열 공통 substring 같은 suffix array 응용 패턴을 공개했습니다. 남은 문자열 심화는 border automaton 후보로 이어갑니다.
- `gomory-hu-tree`: 무향 그래프의 all-pairs min cut 값을 cut-equivalent tree로 압축하는 Gomory-Hu Tree를 공개했습니다. 남은 그래프 심화는 dynamic MST 후보로 이어갑니다.
- `euler-tour-tree`: dynamic forest를 Euler tour sequence와 treap split/merge로 관리하는 Euler Tour Tree를 공개했습니다. 남은 자료구조 심화는 persistent union-find 후보로 이어갑니다.
- `mobius-inversion`: Mobius function, divisor inversion, coprime pair count, exact gcd count를 다루는 수학 심화를 공개했습니다. 남은 수학 심화는 linear basis applications 후보로 이어갑니다.
- `convex-cost-flow`: convex marginal cost를 edge split으로 표현해 Min-Cost Flow 모델과 결합하는 최적화 심화를 공개했습니다. 남은 DP 최적화는 min-plus convolution 후보로 이어갑니다.
- `border-automaton`: KMP prefix function을 상태 전이표로 바꾸고 forbidden pattern DP와 overlapping match 처리를 다루는 문자열 심화를 공개했습니다. 남은 문자열 심화는 suffix automaton applications 후보로 이어갑니다.
- `dynamic-mst`: 간선 추가/삭제가 섞인 그래프에서 MST 비용을 유지하는 성질, rebuild baseline, block/offline 전략을 공개했습니다. 남은 그래프 심화는 global min cut 후보로 이어갑니다.
- `persistent-union-find`: parent change time과 size history로 과거 version의 연결성/component size를 조회하는 DSU 심화를 공개했습니다. 남은 자료구조/오프라인 심화는 rollback techniques 후보로 이어갑니다.
- `linear-basis-applications`: XOR basis를 표현 가능성, k번째 xor, graph cycle xor, range query, matroid greedy로 확장하는 수학 심화를 공개했습니다. 남은 수학 심화는 Dirichlet convolution 후보로 이어갑니다.
- `min-plus-convolution`: min-plus DP merge, convex sequence, argmin monotonicity, divide-and-conquer 최적화 관점을 공개했습니다. 남은 DP 최적화는 convex DP modeling 후보로 이어갑니다.
- `suffix-automaton-applications`: Suffix Automaton 이후 transition DAG와 suffix link tree를 활용해 occurrence, k번째 substring, 반복 substring, 여러 문자열 공통 substring을 다루는 응용 레슨을 공개했습니다.
- `global-min-cut`: 무향 그래프의 전체 minimum cut을 Stoer-Wagner 알고리즘과 cut modeling 관점으로 공개했습니다. 남은 cut 심화는 cut sparsification이나 cactus representation 후보로 이어갑니다.
- `rollback-techniques`: Rollback DSU를 중심으로 snapshot, segment tree over time, 상태 변경 기록 패턴을 공개했습니다. 남은 오프라인 심화는 retroactive data structure 후보로 이어갑니다.
- `dirichlet-convolution`: 약수 관계 위 convolution, divisor zeta transform, Mobius inverse, multiplicative function 관점을 공개했습니다. 남은 수학 심화는 multiplicative function sieve 후보로 이어갑니다.
- `convex-dp-modeling`: DP 최적화 적용 전 convex, Monge, argmin 단조 조건을 모델링하고 검증하는 관점을 공개했습니다. 남은 DP 최적화는 CHT variants와 parametric DP 후보로 이어갑니다.
- `minkowski-sum`: 두 convex polygon의 edge vector merge, reflected polygon 충돌 판정, support function 관점을 기하 심화로 공개했습니다. 남은 기하 심화는 rotating calipers applications와 shape-distance 모델링 후보로 이어갑니다.
- `rotating-calipers-applications`: width, tangent, convex polygon distance, minimum rectangle처럼 calipers를 지름 밖으로 확장하는 응용 관점을 공개했습니다.
- `multiplicative-functions`: prime power 공식과 linear sieve로 `phi`, `mu`, `tau` 같은 multiplicative function을 계산하는 정수론 심화를 공개했습니다. 남은 수학 심화는 summatory number theory 후보로 이어갑니다.
- `markov-decision-process`: 상태, 행동, 확률 전이, 보상을 가진 MDP와 Bellman update/value iteration을 공개했습니다. 남은 확률/전략 심화는 imperfect information과 POMDP 후보로 이어갑니다.
- `imperfect-information-search`: information set, belief update, determinization의 한계, information set MCTS를 게임 탐색 심화로 공개했습니다.
- `generalized-suffix-automaton`: 여러 문자열의 substring 집합을 SAM 관점에서 합치고 문자열별 match/coverage를 집계하는 문자열 심화를 공개했습니다. 남은 문자열 심화는 palindrome range 응용과 query 구조 후보로 이어갑니다.
- `palindrome-query-structures`: Manacher, rolling hash, Eertree를 palindrome 판정/집계/동적 질의에 맞춰 선택하는 문자열 query 레슨을 공개했습니다.
- `cut-sparsification`: 작은 cut과 edge connectivity를 보존하는 sparse certificate와 forest layer 관점을 공개했습니다. 남은 cut 심화는 cactus representation과 randomized contraction 후보로 이어갑니다.
- `global-min-cut-applications`: global min cut partition 복원, 여러 minimum cut, Gomory-Hu Tree 기반 pair cut query와 edge criticality 관점을 공개했습니다.
- `retroactive-data-structures`: 과거 operation 삽입/삭제를 시간축 interval로 바꾸고 rollback/persistence와 구분하는 오프라인 retroactive 자료구조 레슨을 공개했습니다.
- `offline-range-query-techniques`: Mo 변형, offline sorting + Fenwick, time dimension이 붙은 range query 처리 기준을 공개했습니다.
- `summatory-number-theory`: floor division grouping과 divisor transform으로 큰 `n`의 정수론 누적합을 계산하는 관점을 공개했습니다.
- `convex-hull-trick-variants`: monotone deque CHT, breakpoint hull, Li Chao 변형을 slope/query 조건별로 고르는 기준을 공개했습니다.
- `parametric-dp`: penalty DP, feasibility parameter, answer binary search로 DP 제약을 분리하는 관점을 공개했습니다.
- `shape-distance-modeling`: Minkowski difference, support function, separating axis로 도형 거리와 충돌 문제를 모델링하는 법을 공개했습니다.
- `palindrome-range-dp`: palindrome 판정 구조를 prefix DP와 interval DP 전이에 결합하는 문자열/DP 응용을 공개했습니다.
- `cactus-representation`: cactus graph와 min cut family 표현을 구분하고 cycle block을 tree처럼 다루는 그래프 모델을 공개했습니다.
- `persistent-queue-stack`: persistent stack, queue, deque의 version root와 rollback/retroactivity 경계를 공개했습니다.
- `linear-recurrence-applications`: DP, graph walk, 생성함수에서 선형 점화식을 찾아 Kitamasa/Bostan-Mori/행렬 거듭제곱 중 방법을 고르는 기준을 공개했습니다.
- `circle-geometry`: 원-직선, 원-원 교점과 접선 construction, 각도 구간 sweep의 case 분기를 공개했습니다.
- `string-period-query-applications`: border, period, runs 정보를 substring range/query 문제로 확장하는 문자열 응용을 공개했습니다.
- `randomized-min-cut`: Karger contraction과 반복 확률 증폭으로 global min cut을 찾는 randomized graph 기법을 공개했습니다.
- `persistent-sequence-queries`: version별 배열과 sequence에서 kth, count, range query를 처리하는 persistent structure 응용을 공개했습니다.
- `quadrangle-inequality-proofs`: Knuth/Monge 최적화에 필요한 quadrangle inequality와 opt 단조성 증명 패턴을 공개했습니다.
- `circle-arrangement`: 여러 원의 교점으로 arc를 나누고 union area/perimeter/depth를 angular sweep으로 계산하는 기하 응용을 공개했습니다.
- `recurrence-guessing`: 앞 항에서 선형 점화식 후보를 찾고 holdout 항으로 검증하는 recurrence 모델링 흐름을 공개했습니다.
- `berlekamp-massey`: field 위 수열에서 최소 선형 점화식을 찾고 Kitamasa/Bostan-Mori로 연결하는 알고리즘을 공개했습니다.
- `cht-dp-applications`: DP 전이식을 직선과 query로 분리하고 단조 조건에 맞는 CHT 구현을 고르는 응용 흐름을 공개했습니다.
- `robust-geometry-predicates`: orientation, segment intersection, incircle 같은 기하 분기 조건의 exact/EPS 정책을 공개했습니다.
- `pomdp`: hidden state와 observation model을 belief state로 올려 푸는 Partially Observable MDP 모델링을 공개했습니다.
- `generating-function-modeling`: counting/DP 식을 생성함수 계수로 번역하고 rational form, recurrence, Bostan-Mori로 연결하는 모델링을 공개했습니다.
- `black-box-linear-algebra`: sparse matrix-vector product와 Krylov sequence, Wiedemann 계열 관점을 이용한 큰 선형대수 모델링을 공개했습니다.
- `game-theory-applications`: Grundy, minimax, MDP, hidden information 모델을 문제 신호별로 고르는 게임 이론 응용 기준을 공개했습니다.
- `inversion-geometry`: 원과 직선을 inversion으로 변환해 접선, 교점, 원다발 문제를 단순화하는 기하 모델링을 공개했습니다.
- `point-based-value-iteration`: POMDP belief space를 대표 belief point와 alpha vector로 근사하는 PBVI planning 기법을 공개했습니다.
- `kinetic-hull`: 시간에 따라 움직이는 점/직선의 최적 후보가 바뀌는 event를 line envelope와 kinetic 구조 관점으로 공개했습니다.
- `fully-dynamic-cht`: 직선 삽입/삭제/질의가 섞인 CHT 문제를 활성 구간, rollback Li Chao, online line container로 고르는 기준을 공개했습니다.
- `robust-delaunay`: Delaunay triangulation의 orientation, incircle, cocircular degeneracy를 안정적으로 다루는 predicate 중심 관점을 공개했습니다.
- `cut-cactus-applications`: global min cut family를 cactus representation으로 압축하고 query/criticality에 활용하는 그래프 cut 응용을 공개했습니다.
- `pomcp`: particle belief와 UCT 기반 MCTS를 결합해 POMDP를 online planning으로 근사하는 POMCP 관점을 공개했습니다.
- `matroid-intersection`: 두 matroid 독립성 조건을 동시에 만족하는 최대 집합을 exchange graph와 augmenting path로 찾는 모델을 공개했습니다.
- `sparse-linear-systems`: sparse row, matvec oracle, rank consistency를 기준으로 큰 선형 시스템을 푸는 선택지를 공개했습니다.
- `linear-algebra-applications`: rank, determinant, xor basis, recurrence, graph counting을 vector space 모델로 번역하는 응용 기준을 공개했습니다.
- `power-diagram`: power distance와 radical axis로 weighted Voronoi cell을 다루는 계산기하 심화 관점을 공개했습니다.
- `bayesian-bandits`: posterior update, Thompson Sampling, Bayesian UCB, finite-horizon belief DP를 연결하는 확률적 의사결정 레슨을 공개했습니다.
- `dynamic-flow`: capacity update, residual graph 재사용, time-expanded network, batch rebuild를 구분하는 flow 심화 레슨을 공개했습니다.
- `online-convex-optimization`: regret, projection, online gradient descent, mirror descent를 sequential decision 모델링 관점으로 공개했습니다.
- `fractional-programming-dp`: 비율 목적식을 `value - lambda * weight` 판정으로 바꾸고 DP/graph feasibility와 결합하는 최적화 레슨을 공개했습니다.
- `3d-convex-hull`: signed volume, oriented face, visible face, horizon edge, coplanar degeneracy를 다루는 3D 기하 심화를 공개했습니다.
- `reinforcement-learning-basics`: Bellman 식, value iteration, policy improvement, Q-value를 contest 모델링 수준으로 공개했습니다.
- `matroid-parity`: pair 단위 선택과 matroid 독립성을 결합하는 matching 일반화 모델을 공개했습니다. 조합 최적화 심화는 matroid union과 algebraic matching 쪽으로 이어갑니다.
- `randomized-determinant`: Schwartz-Zippel, random substitution, modular determinant, Tutte matrix 존재성 판정을 공개했습니다. 남은 선형대수 심화는 spectral graph와 sparse determinant 후보로 이어갑니다.
- `matrix-tree-theorem-applications`: Laplacian cofactor로 spanning tree count, rooted arborescence, edge include/exclude를 계산하는 그래프 수학 레슨을 공개했습니다.
- `regular-triangulation`: weighted point lifting과 lower hull로 Power Diagram의 dual triangulation을 이해하는 계산기하 심화를 공개했습니다.
- `online-planning-evaluation`: simulator 기반 policy를 paired seed, confidence interval, holdout set으로 검증하는 게임/탐색 평가 레슨을 공개했습니다.
- `lagrangian-relaxation-patterns`: 제약을 penalty와 dual variable로 목적식에 흡수하고 relaxed oracle을 반복 호출하는 최적화 패턴을 공개했습니다.
- `matroid-union`: 여러 matroid 독립 집합의 합, union rank, layer exchange 관점을 조합 최적화 레슨으로 공개했습니다.
- `planar-graph-duality`: planar embedding의 face graph와 cut-cycle duality를 이용해 그래프/기하 문제를 변환하는 관점을 공개했습니다.
- `stochastic-shortest-path`: absorbing 목표 상태까지의 기대 비용을 Bellman 식, value iteration, linear equation 관점으로 공개했습니다.
- `dual-averaging`: online convex optimization에서 누적 gradient와 regularizer로 decision을 갱신하는 dual averaging 패턴을 공개했습니다.

## 콘텐츠 보강 우선순위

이미 공개된 심화 레슨은 새 문제를 붙이기 전에 "손으로 따라가는 예시 1개, 조건이 필요한 이유 1개, 구현 trace 1개"를 우선 보강합니다. 연습 문제 TODO는 적절한 h-contest 문제가 생길 때까지 그대로 둡니다.

| 우선순위 | lessonId | 부족한 부분 | 문제 추가 없이 할 일 | 상태 |
| ---: | --- | --- | --- | --- |
| 1 | `convex-cost-flow` | end-to-end 모델링 예시와 nondecreasing marginal cost 반례 | demand allocation 예시, edge 목록, 선택 unit 표 추가 | 반영 |
| 2 | `min-plus-convolution` | argmin monotone 조건을 손으로 확인하는 흐름 | opt 이동 표, opt 감소 반례, 조건별 복잡도 구분 추가 | 반영 |
| 3 | `gomory-hu-tree` | construction parent 갱신 trace | 4정점 예시와 tree path query page 추가 | 반영 |
| 4 | `weighted-matching` | weighted blossom 구현 레슨인지 선택 가이드인지 목표가 모호함 | 목표 재정의, 일반 그래프가 어려운 이유, 선택 기준 강화 | 반영 |
| 5 | `suffix-tree-ukkonen` | sentinel 전제와 Ukkonen phase trace 부족 | `abab$` phase별 active point/split trace page 추가 | 반영 |
| 6 | `link-cut-tree` | `access`, `makeRoot`, `cut` 조건의 상태 변화 설명 부족 | `1-2-3` path query trace와 cut 조건 설명 추가 | 반영 |
| 7 | `euler-tour-tree` | sequence split/merge 예시 부족 | `link(3,4)`, `cut(2,3)` sequence trace 추가 | 반영 |
