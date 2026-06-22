# h-contest lesson content roadmap

이 문서는 아직 `lessons.json`에 공개 레슨으로 올리지 않은 콘텐츠 TODO를 관리합니다. 새 주제는 본문, 예시 구현, 체크리스트, 연습 문제 표가 준비된 뒤 manifest에 추가합니다.

## 최근 공개로 이동한 주제

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

## 우선 추가할 주제

| 우선순위 | 후보 lessonId | 주제 | 연습 문제 상태 |
| ---: | --- | --- | --- |
| 1 | `flow-with-lower-bound` | lower/upper bound가 있는 flow, feasibility circulation | TODO: lower-bound flow `/practice/...` 문제 필요 |
| 2 | `closest-pair-sweep` | 최근접 점 쌍, divide-and-conquer와 sweep set | TODO: closest pair `/practice/...` 문제 필요 |
| 3 | `monge-smawk` | Monge array, totally monotone matrix, SMAWK | TODO: Monge/SMAWK `/practice/...` 문제 필요 |
| 4 | `fps-log-exp` | FPS log, exp, power와 generating function 응용 | TODO: FPS log/exp `/practice/...` 문제 필요 |
| 5 | `minimax-alpha-beta` | minimax, alpha-beta pruning, game tree search | TODO: minimax `/practice/...` 문제 필요 |

## 추가 후보 묶음

| 영역 | 후보 lessonId |
| --- | --- |
| 문자열 | `palindromic-tree` |
| 그래프 심화 | `flow-with-lower-bound`, `general-matching` |
| 자료구조/오프라인 | `wavelet-matrix`, `succinct-bitvector` |
| 수학 심화 | `fps-log-exp`, `linear-recurrence-kitamasa` |
| DP 최적화 | `monge-smawk` |
| 기하 | `closest-pair-sweep`, `line-arrangement` |
| 게임/탐색 | `minimax-alpha-beta` |

## 공개 레슨으로 올리기 전 조건

1. `lessons/<lessonId>/lesson.md` 또는 `pages/` 본문이 "읽기 -> 구현하기 -> 문제 풀기 -> 실수 점검하기" 흐름을 갖춘다.
2. C++ 구현 또는 의사 구현이 있고, 필요한 경우 `cpp compile-check` fence로 컴파일 검증 대상에 올린다.
3. `## 연습 문제` 표는 `단계`, `문제`, `목표`, `힌트 키워드` 열을 사용한다.
4. 적절한 h-contest 문제가 없으면 문제 칸에 `TODO: ... /practice/... 문제 필요`라고 남긴다.
5. 공개하기 전에 `python3 scripts/generate_catalog.py`와 `python3 scripts/validate_lessons.py`를 통과시킨다.
