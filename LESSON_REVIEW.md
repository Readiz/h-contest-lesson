# 학습 노트 전체 본문 검토 기록

2026-09-09 후속 편집: 아래 최초 정독 기록과 별도로 Treap, 선형대수 선택·연습, Gomory-Hu, Ukkonen, Suffix Array, planar dual의 설명 경계 6개를 통합했습니다. 이동된 본문 링크는 통합 위치로 갱신했습니다. 전체 강의 수는 유지하며 본문은 208개에서 202개로 줄었습니다.


[README로 돌아가기](README.md)

기준: `6df3fec`, 2026-09-09 시작. 참고노트 70개 강의 169개 본문과 기본·심화 노트 30개 강의 47개 본문, 총 216개를 대상으로 합니다. 앞선 일괄 편집을 정독 완료로 세지 않습니다. 본문과 코드 블록을 처음부터 끝까지 읽은 뒤 개별 판단을 기록합니다. 정독 여부와 수정·실행 검증 여부는 구분합니다.

- 본문·코드 정독 완료: 216 / 216
- 편집 반영: 참고 169 → 161개 본문, 기본·심화 47개 본문 유지. 합계 216 → 208개.
- 실행 검증: 전체 validator와 실제 Markdown 코드 조합 검사를 수행하며 아래 결과 절에 기록합니다.
- 범위: 불필요한 설명·중복 구현·빈 골격의 삭제, 관련 페이지 통합, 발견한 오류 수정. 모든 알고리즘의 형식적 증명이나 전체 입력 공간 검증을 의미하지 않습니다.

| 번호 | 문서 | 정독 | 판단·반영 내용 |
| --- | --- | --- | --- |
| 1 | [lessons/modular-arithmetic/lesson.md](lessons/modular-arithmetic/lesson.md) | 완료 | 본문·코드 정독. 반영: 음수 밑 정규화와 역원 설명 중복 정리. |
| 2 | [lessons/scc-2sat/lesson.md](lessons/scc-2sat/lesson.md) | 완료 | 본문·코드 정독. 반영: 항상 빈 components 반환 제거, 변수 배정 설명 구체화. |
| 3 | [lessons/max-flow-min-cut/lesson.md](lessons/max-flow-min-cut/lesson.md) | 완료 | 본문·코드 정독. 반영: BFS 거리 설명 수정, 중복 residual BFS를 Dinic 결과 활용으로 통합. |
| 4 | [lessons/matching-cover-duality/lesson.md](lessons/matching-cover-duality/lesson.md) | 완료 | 본문·코드 정독. 반영: maximumMatching 재호출 초기화, cover 호출 순서 명시, 반복 실수표 삭제. |
| 5 | [lessons/min-cost-flow/lesson.md](lessons/min-cost-flow/lesson.md) | 완료 | 본문·코드 정독. 반영: 음수 사이클 미지원·source/sink·정수범위 전제, self-loop 역간선, 반복 실수표 삭제. |
| 6 | [lessons/flow-with-lower-bound/lesson.md](lessons/flow-with-lower-bound/lesson.md) | 완료 | 본문·코드 정독. 반영: Dinic 중복 통합, feasible 단발 호출과 입력 전제, 추가 최대유량의 보조 간선 제거 설명 수정. |
| 7 | [lessons/general-matching/lesson.md](lessons/general-matching/lesson.md) | 완료 | 본문·코드 정독. 반영: 완성 구현을 골격이라 부르는 표현, 최대/극대 구분 외 반복 실수 삭제. |
| 8 | [lessons/sparse-table-rmq/lesson.md](lessons/sparse-table-rmq/lesson.md) | 완료 | 본문·코드 정독. 반영: LCP 정의와 같은 suffix 경계, Euler 재방문 명시, 실수표 중복 통합. |
| 9 | [lessons/dominator-tree/lesson.md](lessons/dominator-tree/lesson.md) | 완료 | 본문·코드 정독. 반영: 도달 불가 tree 삽입 차단, 단순 LT의 log N 복잡도 원 논문 확인, 재귀·번호 구분 남기고 실수표 제거. |
| 10 | [lessons/weighted-matching/lesson.md](lessons/weighted-matching/lesson.md) | 완료 | 본문·코드 정독. 반영: 미존재 간선 DP 처리, 실제 O(N2^N) 복잡도, 중복 선택표·불명확 slack 식 삭제. |
| 11 | [lessons/directed-mst/lesson.md](lessons/directed-mst/lesson.md) | 완료 | 본문·코드 정독. 반영: 단순 구현 복잡도만 유지, super root 다중 루트 오해 방지, 반복 실수표 삭제. |
| 12 | [lessons/versioned-data-structures/lesson.md](lessons/versioned-data-structures/lesson.md) | 완료 | 본문 정독. 반영: full/partial persistence 명칭 분리, 허브 소개 반복 축약. |
| 13 | [lessons/versioned-data-structures/pages/persistent-segment-tree.md](lessons/versioned-data-structures/pages/persistent-segment-tree.md) | 완료 | 본문·코드 정독. 반영: 입력 범위·빌드 메모리 보완, sparse 값범위 불가 단정 수정, 17과 통합. |
| 14 | [lessons/versioned-data-structures/pages/persistent-lazy-segment-tree.md](lessons/versioned-data-structures/pages/persistent-lazy-segment-tree.md) | 완료 | 본문·코드 정독. 반영: query를 carry 기반 read-only로 통합하고 변형 설명 중복 삭제, 임의 reserve 제거. |
| 15 | [lessons/versioned-data-structures/pages/persistent-union-find.md](lessons/versioned-data-structures/pages/persistent-union-find.md) | 완료 | 본문·코드 정독. 반영: 시간/정점 범위, inline static constexpr 상수, 반복 실수표 삭제. |
| 16 | [lessons/versioned-data-structures/pages/persistent-queue-stack.md](lessons/versioned-data-structures/pages/persistent-queue-stack.md) | 완료 | 본문·코드 정독. 반영: 분기 queue를 전역 배열 구간으로 표현할 수 있다는 잘못된 단순화 제거, rollback 비교 중복 삭제. |
| 17 | [lessons/versioned-data-structures/pages/persistent-sequence-queries.md](lessons/versioned-data-structures/pages/persistent-segment-tree.md) | 완료 | 본문·코드 정독. 통합 반영: kth 구현과 prefix 예제가 13과 중복. 예시·sequence 차이만 13으로 이동 후 페이지 통합. |
| 18 | [lessons/versioned-data-structures/pages/practice-set.md](lessons/versioned-data-structures/pages/practice-set.md) | 완료 | 본문 정독. 반영: 실제 kth 인자 순서와 압축 1-index 맞춤, 미완성 연습 후보·반복 체크리스트 삭제. |
| 19 | [lessons/wavelet-tree/lesson.md](lessons/wavelet-tree/lesson.md) | 완료 | 본문·코드 정독. 반영: shallow copy 금지, 값/질의 범위와 x-1 overflow 설명, 메모리 ints 명확화. |
| 20 | [lessons/wavelet-matrix/lesson.md](lessons/wavelet-matrix/lesson.md) | 완료 | 본문·코드 정독. 반영: countLess 음수 및 INT_MAX+1 경계 처리, 고정 31층 복잡도, 반복 실수 삭제. |
| 21 | [lessons/succinct-bitvector/lesson.md](lessons/succinct-bitvector/lesson.md) | 완료 | 본문·코드 정독(잘린 출력 재독 포함). 반영: 64bit 배수 길이 rankOne(n) 오류, rankZero clamp 일치, select를 같은 구조에 통합. |
| 22 | [lessons/tree-advanced/lesson.md](lessons/tree-advanced/lesson.md) | 완료 | 본문·코드 정독. 반영: LOG 최소값, 배열 초기화, centroid 거리 초기화, HLD rangeAdd 이름·small-to-large 소유권 및 저장 답, 반복 선택표 삭제. |
| 23 | [lessons/avl-splay-tree/lesson.md](lessons/avl-splay-tree/lesson.md) | 완료 | 본문·코드 정독. 반영: 빈 rebalance 방어, 아무 기능 없는 SplayNode 블록 삭제, 오래된 BST 페이지 안내 수정. |
| 24 | [lessons/link-cut-tree/lesson.md](lessons/link-cut-tree/lesson.md) | 완료 | 본문·코드 정독. 반영: 연결된 두 정점 질의 전제, 1-index 범위, findRoot lazy 확인 순서, 반복 실수표 삭제. |
| 25 | [lessons/string-matching-kmp-z/lesson.md](lessons/string-matching-kmp-z/lesson.md) | 완료 | 본문·코드 정독. 반영: proper prefix 설명, 빈 패턴 계약·separator 전제·출력 메모리, 반복 실수표 통합. |
| 26 | [lessons/trie-aho-corasick/lesson.md](lessons/trie-aho-corasick/lesson.md) | 완료 | 본문·코드 정독. 반영: build 단발·빈 패턴 금지, 출력 ID 복사 비용 주의, 겹친 예시/실수표 중복 삭제. |
| 27 | [lessons/suffix-periodicity-structures/lesson.md](lessons/suffix-periodicity-structures/lesson.md) | 완료 | 본문 정독. 반영: 도입·중복 구조표 축약, 공개 상태 제목 정리. |
| 28 | [lessons/suffix-periodicity-structures/pages/suffix-array-lcp.md](lessons/suffix-periodicity-structures/pages/suffix-array-lcp.md) | 완료 | 본문·코드 정독. 반영: Kasai 감소 방향 설명, unsigned 비교 통일, 빈 패턴 계약, 반복 실수표 삭제. |
| 29 | [lessons/suffix-periodicity-structures/pages/suffix-array-applications.md](lessons/suffix-periodicity-structures/pages/suffix-array-lcp.md) | 완료 | 본문·코드 정독. 반영: SparseTable 중복 구현을 기존 API 사용으로 통합, non-overlap 전체 suffix 그룹 범위 명시, SA 복잡도 맞춤. |
| 30 | [lessons/suffix-periodicity-structures/pages/suffix-automaton.md](lessons/suffix-periodicity-structures/pages/suffix-automaton.md) | 완료 | 본문·코드 정독. 반영: build 초기화, endpos/가장 긴 다른 상태 suffix 정의, 호환되지 않는 상태 구조 중복을 템플릿 함수로 통합. |
| 31 | [lessons/suffix-periodicity-structures/pages/suffix-automaton-applications.md](lessons/suffix-periodicity-structures/pages/suffix-automaton-applications.md) | 완료 | 본문·코드 정독. 반영: build 초기화·집계 후 append 금지, LIMIT 링크 상수, occurrence 정렬 비용, 중복 소개 제거. |
| 32 | [lessons/suffix-periodicity-structures/pages/generalized-suffix-automaton.md](lessons/suffix-periodicity-structures/pages/generalized-suffix-automaton.md) | 완료 | 본문·코드 정독. 반영: others 빈 경우가 0인 버그, build 초기화, 전체 비용 정렬항, 실제 구현이 첫문자열 SAM임을 명확히. |
| 33 | [lessons/suffix-periodicity-structures/pages/suffix-tree-ukkonen.md](lessons/suffix-periodicity-structures/pages/suffix-tree-ukkonen.md) | 완료 | 본문·코드 정독. 반영: 실제 코드는 완성 문자열 일괄 빌드임을 명시, 불필요 map 복사 제거, 반복 비교·실수표 축약. |
| 34 | [lessons/suffix-periodicity-structures/pages/suffix-tree-phase-trace.md](lessons/suffix-periodicity-structures/pages/suffix-tree-ukkonen.md) | 완료 | 본문 정독. 반영: 작은 trace 통과가 큰 입력 안정성을 보장한다는 단정 삭제. |
| 35 | [lessons/suffix-periodicity-structures/pages/runs-periodicity.md](lessons/suffix-periodicity-structures/pages/runs-periodicity.md) | 완료 | 본문·코드 정독. 반영: 일반 period와 완전 반복 함수명 분리, 두 prefixFunction 중복 통합. |
| 36 | [lessons/suffix-periodicity-structures/pages/border-automaton.md](lessons/suffix-periodicity-structures/pages/border-automaton.md) | 완료 | 본문·코드 정독. 반영: 빈 패턴 matchPositions 접근 방어, m 상태 전이가 있어 수동 fallback 필수라는 설명 수정. |
| 37 | [lessons/suffix-periodicity-structures/pages/string-period-query-applications.md](lessons/suffix-periodicity-structures/pages/string-period-query-applications.md) | 완료 | 본문·코드 정독. 반영: RollingHash 중복 구현 제거·기존 get 사용, 반복확장 구간 길이 정확화, 전처리 비용 맞춤. |
| 38 | [lessons/suffix-periodicity-structures/pages/practice-set.md](lessons/suffix-periodicity-structures/pages/practice-set.md) | 완료 | 본문 정독. 반영: 기본 본문과 LCP 정의 통일, 무관한 완료 체크리스트 삭제. |
| 39 | [lessons/palindrome-structures/lesson.md](lessons/palindrome-structures/lesson.md) | 완료 | 본문 정독. 모델 선택과 hash 정확성 범위 유지. |
| 40 | [lessons/palindrome-structures/pages/palindromic-tree.md](lessons/palindrome-structures/pages/palindromic-tree.md) | 완료 | 본문·코드 정독. 반영: 등장 횟수 템플릿으로 실제 Node 호환, suffix link 생성 순서 근거, build 초기화·누적 단발. |
| 41 | [lessons/palindrome-structures/pages/palindrome-query-structures.md](lessons/palindrome-structures/pages/palindrome-query-structures.md) | 완료 | 본문·코드 정독. 반영: hash 복제를 기존 두 RollingHash 사용으로 통합, 중복 구조표 삭제. |
| 42 | [lessons/palindrome-structures/pages/palindrome-range-dp.md](lessons/palindrome-structures/pages/palindrome-range-dp.md) | 완료 | 본문·코드 정독. 반영: 최소 삽입 기저·빈 문자열 컷 처리, 무관한 모든 분할 복원 행 삭제. |
| 43 | [lessons/palindrome-structures/pages/suffix-palindrome-applications.md](lessons/suffix-periodicity-structures/pages/suffix-automaton-applications.md) | 완료 | 본문·코드 정독. 통합 반영: 별도 SAM 구현·문자열 선택표가 30/31/39/40과 중복. 선형 occurrence 누적만 31로 옮기고 페이지 제거. |
| 44 | [lessons/palindrome-structures/pages/practice-set.md](lessons/palindrome-structures/pages/practice-set.md) | 완료 | 본문·코드 정독. 반영: Eertree 전체 복제 제거·기존 객체로 호출, 반복 연습표·체크리스트 삭제. |
| 45 | [lessons/lyndon-factorization/lesson.md](lessons/lyndon-factorization/lesson.md) | 완료 | 본문·코드 정독. 반영: 동작 예시에 실제 분해 결과, 최소 회전 첫 factor 오설명 수정, 빈 문자열 계약. |
| 46 | [lessons/geometry-ccw-segment-intersection/lesson.md](lessons/geometry-ccw-segment-intersection/lesson.md) | 완료 | 본문·코드 정독. 반영: 좌표 절댓값<=1e9 전제, Point/cross 복제 통합, collinear 전체 일직선 중복 처리 설명. |
| 47 | [lessons/rotating-calipers/lesson.md](lessons/rotating-calipers/lesson.md) | 완료 | 본문·코드 정독. 반영: 엄격 convex hull·좌표 범위 전제, 폭 외적/면적 배율 명료화, 실수표 삭제. |
| 48 | [lessons/sweep-line-geometry/lesson.md](lessons/sweep-line-geometry/lesson.md) | 완료 | 본문·코드 정독. 반영: move한 ys 인자로 크기를 계산해 빈 tree가 되는 생성자 오류, 사각형 좌표 정렬 전제, 실수표 삭제. |
| 49 | [lessons/closest-pair-sweep/lesson.md](lessons/closest-pair-sweep/lesson.md) | 완료 | 본문·코드 정독. 반영: 실제 최소거리보다 작은 초기 INF·limit 제곱 overflow, 중복점 조기 종료, 기하적 후보 상한 설명. |
| 50 | [lessons/line-arrangement/lesson.md](lessons/line-arrangement/lesson.md) | 완료 | 본문·코드 정독. 반영: 중복 normalize 구현 통합, a=b=0 제외와 계수 범위. |
| 51 | [lessons/voronoi-delaunay/lesson.md](lessons/voronoi-delaunay/lesson.md) | 완료 | 본문·코드 정독. 반영: collinear 외접원 방어, orientation 보정 설명 일치, 중복 선택표 축약. |
| 52 | [lessons/half-plane-intersection/lesson.md](lessons/half-plane-intersection/lesson.md) | 완료 | 본문·코드 정독. 반영: EPS sort 비추이성·반대방향 평행 제거·마지막 평행 교점 오류. 검증 가능한 bounded clipping으로 교체. |
| 53 | [lessons/gcd-extended-euclid-crt/lesson.md](lessons/gcd-extended-euclid-crt/lesson.md) | 완료 | 본문·코드 정독. 반영: extendedGcd 3중 복제 통합, 음수 역원 정규화, CRT lcm만 안전해도 중간곱은 넘는 문제 수정. |
| 54 | [lessons/combinatorics-ncr/lesson.md](lessons/combinatorics-ncr/lesson.md) | 완료 | 본문·코드 정독. 반영: Lucas factorial 구현 재사용, maxN<mod·질의 범위 전제, 단순 addSigned 래퍼 삭제. |
| 55 | [lessons/matrix-exponentiation/lesson.md](lessons/matrix-exponentiation/lesson.md) | 완료 | 본문·코드 정독. 반영: 행렬 shape·mod 범위, exp0 mod1 처리, min-plus가 일반 모듈러 행렬 가속이라는 오해 제거. |
| 56 | [lessons/polynomial-recurrence-algorithms/lesson.md](lessons/polynomial-recurrence-algorithms/lesson.md) | 완료 | 본문 정독. 반영: 학습 경로와 같은 모델 선택표 통합. |
| 57 | [lessons/polynomial-recurrence-algorithms/pages/fft-ntt.md](lessons/polynomial-recurrence-algorithms/pages/fft-ntt.md) | 완료 | 본문·코드 정독. 반영: 입력 계수 정규화·2^23 상한, CRT 복원 범위 조건, 반복 실수표 삭제. |
| 58 | [lessons/polynomial-recurrence-algorithms/pages/formal-power-series.md](lessons/polynomial-recurrence-algorithms/pages/formal-power-series.md) | 완료 | 본문·코드 정독. 반영: 적분 분모<nMod·n0 경계, modPow 중복과 실제 적분 복잡도, log 상수항 조건. |
| 59 | [lessons/polynomial-recurrence-algorithms/pages/fps-log-exp.md](lessons/polynomial-recurrence-algorithms/pages/fps-log-exp.md) | 완료 | 본문·코드 정독. 반영: log/exp 없이 미분·곱셈만 복제한 블록 제거, 실제 log/exp 작은 점화 예제로 대체. |
| 60 | [lessons/polynomial-recurrence-algorithms/pages/multipoint-evaluation.md](lessons/polynomial-recurrence-algorithms/pages/multipoint-evaluation.md) | 완료 | 본문 정독. 반영: chirp-z는 연속 정수가 아닌 등비점, x-xi 부호 반전 실수 단정 삭제, 선형몫 전제. |
| 61 | [lessons/polynomial-recurrence-algorithms/pages/polynomial-interpolation.md](lessons/polynomial-recurrence-algorithms/pages/polynomial-interpolation.md) | 완료 | 반영: 연속점 보간의 입력 범위와 정규화, 전처리 비용, 잘못된 분모 설명을 수정한다. |
| 62 | [lessons/polynomial-recurrence-algorithms/pages/generating-function-modeling.md](lessons/polynomial-recurrence-algorithms/pages/generating-function-modeling.md) | 완료 | 반영: 순서 있는 동전 예시를 고치고 중복 다항식 코드를 줄이며 생성함수의 성립 조건을 명시한다. |
| 63 | [lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-kitamasa.md](lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-kitamasa.md) | 완료 | 반영: Kitamasa 입력 조건과 계수 정규화, 중복 설명을 정리한다. |
| 64 | [lessons/polynomial-recurrence-algorithms/pages/bostan-mori.md](lessons/polynomial-recurrence-algorithms/pages/bostan-mori.md) | 완료 | 반영: Bostan–Mori의 빈 다항식·상수항 조건과 계수 정규화 및 복잡도를 보완한다. |
| 65 | [lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-applications.md](lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-kitamasa.md) | 완료 | 통합 반영: Kitamasa와 겹치는 선택 설명을 합치고 XOR 및 유리 생성함수 설명 오류를 고친다. |
| 66 | [lessons/polynomial-recurrence-algorithms/pages/recurrence-guessing.md](lessons/polynomial-recurrence-algorithms/pages/recurrence-guessing.md) | 완료 | 반영: 임의의 holdout 10항 권장과 affine 수열 오해를 제거하고 증명된 차수 상한과 검증을 구분한다. |
| 67 | [lessons/polynomial-recurrence-algorithms/pages/berlekamp-massey.md](lessons/polynomial-recurrence-algorithms/pages/berlekamp-massey.md) | 완료 | 반영: 임의 dummy 초기항 삽입 안내를 제거하고 영 수열의 차수 0 처리 및 차수 상한 조건을 명시한다. |
| 68 | [lessons/polynomial-recurrence-algorithms/pages/practice-set.md](lessons/polynomial-recurrence-algorithms/pages/practice-set.md) | 완료 | 통합 반영: Kitamasa 구현은 본문을 재사용하고 중복 다음 연습·무관한 완료 기준 삭제, K 제한 현실화. |
| 69 | [lessons/probability-expected-value/lesson.md](lessons/probability-expected-value/lesson.md) | 완료 | 반영: 흡수하지 않는 경우 무한 기대값을 명시하고 모듈러 거듭제곱 중복과 반복 체크리스트를 줄인다. |
| 70 | [lessons/game-theory-grundy/lesson.md](lessons/game-theory-grundy/lesson.md) | 완료 | 반영: Grundy DFS의 실제 임시 벡터 메모리와 재귀 조건을 명시하고 반복 체크리스트를 줄인다. |
| 71 | [lessons/probabilistic-decision-ai/lesson.md](lessons/probabilistic-decision-ai/lesson.md) | 완료 | 유지: 확률 모델과 세부 페이지 탐색 허브로 역할이 분명하다. |
| 72 | [lessons/probabilistic-decision-ai/pages/feedback-model-boundary.md](lessons/probabilistic-decision-ai/pages/feedback-model-boundary.md) | 완료 | 반영: 서로 배타적이지 않은 관측·모델 접근 축을 명시하고 반복 분류 예시를 축약한다. |
| 73 | [lessons/probabilistic-decision-ai/pages/finite-horizon-mdp.md](lessons/probabilistic-decision-ai/pages/finite-horizon-mdp.md) | 완료 | 반영: 코드의 종료 보상 0 가정과 확률·턴 입력 조건을 명시하고 반복 실수 목록을 줄인다. |
| 74 | [lessons/probabilistic-decision-ai/pages/discounted-value-iteration.md](lessons/probabilistic-decision-ai/pages/discounted-value-iteration.md) | 완료 | 반영: 제목을 할인 가치 반복으로 맞추고 유한 지평·모델 비교 중복 삭제, 수축 오차 기준을 보완한다. |
| 75 | [lessons/probabilistic-decision-ai/pages/policy-evaluation-and-improvement.md](lessons/probabilistic-decision-ai/pages/policy-evaluation-and-improvement.md) | 완료 | 반영: 할인율 범위와 안정적 동률 처리, 실수 선형 해법의 오차를 명시하고 반복 목록을 줄인다. |
| 76 | [lessons/probabilistic-decision-ai/pages/stochastic-shortest-path.md](lessons/probabilistic-decision-ai/pages/stochastic-shortest-path.md) | 완료 | 반영: proper 정책 존재만으로 부족한 0비용 무한 순환 반례를 반영하고 모든 정책 proper인 코드 전제를 명시한다. |
| 77 | [lessons/probabilistic-decision-ai/pages/exact-model-vs-sampling.md](lessons/probabilistic-decision-ai/lesson.md) | 완료 | 통합 반영: 모델·Bellman·정책 설명이 기존 페이지와 중복. 정확 모델과 표본 차이만 허브로 옮겨 페이지를 합친다. |
| 78 | [lessons/probabilistic-decision-ai/pages/monte-carlo-tree-search.md](lessons/probabilistic-decision-ai/pages/monte-carlo-tree-search.md) | 완료 | 반영: 자식 보상을 수를 둔 플레이어 관점으로 통일하고 빈 자식 처리, 선택 비용 및 불필요 필드를 정리한다. |
| 79 | [lessons/probabilistic-decision-ai/pages/imperfect-information-search.md](lessons/probabilistic-decision-ai/pages/imperfect-information-search.md) | 완료 | 반영: 임의 mod 3 관측 예제 코드를 삭제하고 실제 베이즈 갱신 페이지를 연결한다. 정보 집합과 확률분포 구분 보존. |
| 80 | [lessons/probabilistic-decision-ai/pages/pomdp.md](lessons/probabilistic-decision-ai/pages/pomdp.md) | 완료 | 반영: 불가능한 관측을 영 확률분포로 반환하지 않도록 처리하고 belief 반올림은 근사임을 명시한다. |
| 81 | [lessons/probabilistic-decision-ai/pages/point-based-value-iteration.md](lessons/probabilistic-decision-ai/pages/point-based-value-iteration.md) | 완료 | 반영: 단순 내적 선택 코드와 반복 선택표를 제거하고 PBVI backup 및 오차 보장 차이에 집중한다. |
| 82 | [lessons/probabilistic-decision-ai/pages/pomcp.md](lessons/probabilistic-decision-ai/pages/pomcp.md) | 완료 | 반영: MCTS와 중복 UCT 코드를 줄이고 simulation 의사코드에 방문·가치 갱신과 root sampling을 넣는다. |
| 83 | [lessons/probabilistic-decision-ai/pages/bayesian-bandits.md](lessons/probabilistic-decision-ai/pages/bayesian-bandits.md) | 완료 | 반영: Bayesian UCB의 분위수와 평균+표준편차 휴리스틱을 구분하고 사전분포 조건·중복 목록을 정리한다. |
| 84 | [lessons/probabilistic-decision-ai/pages/online-planning-evaluation.md](lessons/probabilistic-decision-ai/pages/online-planning-evaluation.md) | 완료 | 반영: 0·1개 표본의 표준오차 0 반환 오류, 작은 표본 신뢰구간 및 paired 난수 조건을 보완한다. |
| 85 | [lessons/probabilistic-decision-ai/pages/practice-set.md](lessons/probabilistic-decision-ai/pages/practice-set.md) | 완료 | 통합 반영: 분류 연습은 72와 통합하고 MDP 중복 구현은 73 호출로 대체. 구체적 입출력·trace는 보존한다. |
| 86 | [lessons/offline-time-axis-techniques/lesson.md](lessons/offline-time-axis-techniques/lesson.md) | 완료 | 유지: 시간축 접근 선택과 인덱스 기준을 연결하는 허브. |
| 87 | [lessons/offline-time-axis-techniques/pages/offline-queries.md](lessons/offline-time-axis-techniques/pages/offline-queries.md) | 완료 | 통합 반영: Mo·rollback 중복 구현을 제거하고 PBS 설명만 남겨 제목과 링크를 정리한다. alpha 복잡도 오류 수정. |
| 88 | [lessons/offline-time-axis-techniques/pages/offline-range-query-techniques.md](lessons/offline-time-axis-techniques/pages/offline-range-query-techniques.md) | 완료 | 반영: 압축값·구간·query index 전제 및 수정 Mo의 균형 규모 조건 명시, 중복 PBS와 실수 목록 축약. |
| 89 | [lessons/offline-time-axis-techniques/pages/rollback-techniques.md](lessons/offline-time-axis-techniques/pages/rollback-techniques.md) | 완료 | 반영: 시간 구간을 반열림으로 통일하고 snapshot 유효 범위와 rollback 비용을 명시한다. |
| 90 | [lessons/offline-time-axis-techniques/pages/dynamic-connectivity.md](lessons/offline-time-axis-techniques/pages/dynamic-connectivity.md) | 완료 | 반영: rollback 구현을 89와 공유하고 Q=0 종료 처리, 질의 비용을 포함한 복잡도 및 일반 그래프 추가 구조를 명시한다. |
| 91 | [lessons/offline-time-axis-techniques/pages/retroactive-data-structures.md](lessons/offline-time-axis-techniques/pages/retroactive-data-structures.md) | 완료 | 통합 반영: 시간축 skeleton 중복 삭제. 명령 시간과 논리 시간은 한 좌표로 합칠 수 없고 일반 소급 변경을 단순 생존 구간으로 풀 수 없음을 수정한다. |
| 92 | [lessons/offline-time-axis-techniques/pages/practice-set.md](lessons/offline-time-axis-techniques/pages/practice-set.md) | 완료 | 반영: 모호한 추가 연습과 반복 완료 기준 삭제. 완결된 연결성 연습·trace·stress 유지. |
| 93 | [lessons/divide-and-conquer-dp-optimization/lesson.md](lessons/divide-and-conquer-dp-optimization/lesson.md) | 완료 | 반영: INF 전이 제외, g층의 유효 범위, cost 인덱스 및 근거 없는 선형 복잡도 문구 수정. |
| 94 | [lessons/knuth-optimization/lesson.md](lessons/knuth-optimization/lesson.md) | 완료 | 반영: 빈 배열 반환과 비음수 파일 크기·합산 범위를 명시하고 반복 비교·실수 목록 축약. |
| 95 | [lessons/monge-smawk/lesson.md](lessons/monge-smawk/lesson.md) | 완료 | 반영: totally monotone 부등호 방향 오류와 SMAWK 보간 열 탐색의 이차 시간 문제 수정. 열 비어 있지 않음 전제 및 D&C 복잡도 정정. |
| 96 | [lessons/parametric-optimization/lesson.md](lessons/parametric-optimization/lesson.md) | 완료 | 반영: 공통 흐름과 구현 전 체크리스트 반복 축약. |
| 97 | [lessons/parametric-optimization/pages/feasibility-and-answer-search.md](lessons/parametric-optimization/lesson.md) | 완료 | 통합 반영: penalty DP 구현·설명은 Exact-K 페이지로 옮기고 feasibility 핵심은 비율 페이지 및 허브에 통합. |
| 98 | [lessons/parametric-optimization/pages/exact-k-alien-optimization.md](lessons/parametric-optimization/pages/exact-k-alien-optimization.md) | 완료 | 반영: 단조성은 정확 oracle에서 따름을 설명하고 복원에 필요한 이산 볼록성 조건, 중복 보정식·단순 pair 코드 정리. |
| 99 | [lessons/parametric-optimization/pages/fractional-objectives.md](lessons/parametric-optimization/pages/fractional-objectives.md) | 완료 | 반영: 모든 feasible 해의 분모 양수·비어 있지 않음과 minLength 조건, 반복 횟수로 판정 오차가 사라지지 않음을 명시. |
| 100 | [lessons/parametric-optimization/pages/general-lagrangian-relaxation.md](lessons/parametric-optimization/pages/general-lagrangian-relaxation.md) | 완료 | 반영: candidateExactK를 dualUpperBound로 정정하고 MST의 고정 간선 수에 일괄 벌점 예시 삭제, 부등식 multiplier 부호·산술 범위 명시. |
| 101 | [lessons/parametric-optimization/pages/tie-breaking-and-breakpoints.md](lessons/parametric-optimization/pages/exact-k-alien-optimization.md) | 완료 | 통합 반영: Exact-K와 합쳐 동점·breakpoint·복원 불가 반례를 한곳에서 설명한다. |
| 102 | [lessons/parametric-optimization/pages/practice-set.md](lessons/parametric-optimization/pages/practice-set.md) | 완료 | 반영: 평균 구현은 99 재사용, 구체적 cost 없는 Exact-K 연습 삭제, 실제 입출력·trace 유지. |
| 103 | [lessons/linear-basis-xor/lesson.md](lessons/linear-basis-xor/lesson.md) | 완료 | 반영: unsigned 64비트인데 bit 63을 누락한 오류 수정. 그래프는 단순 경로가 아닌 walk XOR이며 rank64 개수 표현 주의. |
| 104 | [lessons/convex-dp-optimization/lesson.md](lessons/convex-dp-optimization/lesson.md) | 완료 | 유지: 최적화 전이별 진입 허브. 삭제·통합 페이지 링크 갱신. |
| 105 | [lessons/convex-dp-optimization/pages/convex-hull-trick-li-chao.md](lessons/convex-dp-optimization/pages/convex-hull-trick-li-chao.md) | 완료 | 반영: 음수 좌표 midpoint 무한 재귀 오류, 빈 직선 sentinel 한계·좌표 및 값 범위 보완. 반복 전이 분해·실수 목록 축약. |
| 106 | [lessons/convex-dp-optimization/pages/convex-hull-trick-variants.md](lessons/convex-dp-optimization/pages/convex-hull-trick-variants.md) | 완료 | 반영: 최소 deque는 기울기 감소·x 증가로 조건 수정, 128비트 변환을 뺄셈 전으로 이동. 일반 line container 임의 삭제 가능 오해 제거. |
| 107 | [lessons/convex-dp-optimization/pages/cht-dp-applications.md](lessons/convex-dp-optimization/pages/cht-dp-applications.md) | 완료 | 통합 반영: 중복 CHT 클래스는 106 재사용. 감소 slope 설명, 잘못된 Li Chao 조건 목록 정리. 제곱 비용 전개·trace 유지. |
| 108 | [lessons/convex-dp-optimization/pages/slope-trick.md](lessons/convex-dp-optimization/pages/slope-trick.md) | 완료 | 반영: 빈 heap의 최적 구간 해석과 산술 범위를 명시하고 일반 볼록 함수와 단위 hinge 표현 범위를 구분한다. |
| 109 | [lessons/convex-dp-optimization/pages/min-plus-convolution.md](lessons/convex-dp-optimization/pages/min-plus-convolution.md) | 완료 | 반영: 빈 입력 반환·INF 조건 수정. 두 이산 볼록 수열은 차분 merge로 선형임을 설명하고 반복 복잡도 절 축약. |
| 110 | [lessons/convex-dp-optimization/pages/kinetic-hull.md](lessons/convex-dp-optimization/pages/kinetic-hull.md) | 완료 | 반영: 고정 후보 일차식은 일반 CHT로 충분하며 전체 kinetic hull에 단순 이웃 교차 규칙을 일반화하지 않도록 범위 축소. |
| 111 | [lessons/convex-dp-optimization/pages/fully-dynamic-cht.md](lessons/convex-dp-optimization/pages/fully-dynamic-cht.md) | 완료 | 반영: 삭제 buffer만으로 base hull 삭제가 해결되지 않음. 삭제 시 재구축 또는 알려진 block 삭제 대상을 미리 제외하는 조건 명시. |
| 112 | [lessons/convex-dp-optimization/pages/practice-set.md](lessons/convex-dp-optimization/pages/practice-set.md) | 완료 | 통합 반영: Li Chao 중복 클래스를 105 재사용하여 누수도 제거. x 단조만으로 deque 가능 문구 수정, 모호한 Slope 연습·반복 목록 삭제. |
| 113 | [lessons/graph-cut-structures/lesson.md](lessons/graph-cut-structures/lesson.md) | 완료 | 반영: cactus 동일 링크 중복 제거 및 max-flow 링크 연결. |
| 114 | [lessons/graph-cut-structures/pages/global-min-cut.md](lessons/graph-cut-structures/pages/global-min-cut.md) | 완료 | 반영: 비음수 대칭 행렬·총 용량 범위 명시, 모든 쌍 대신 고정 root의 N-1 flow로도 global cut 가능 정정. |
| 115 | [lessons/graph-cut-structures/pages/randomized-min-cut.md](lessons/graph-cut-structures/pages/randomized-min-cut.md) | 완료 | 반영: 빈·비연결 그래프에서 무한 반복/잘못된 난수 범위 오류를 없애고 무작위 간선 순열 contraction으로 유한 실행 보장. |
| 116 | [lessons/graph-cut-structures/pages/gomory-hu-tree.md](lessons/graph-cut-structures/pages/gomory-hu-tree.md) | 완료 | 반영: build 재호출 초기화와 비음수 용량·side 계약, 서로 다른 정점 질의 전제. 병렬 간선은 합산이 필수 아님 수정. |
| 117 | [lessons/graph-cut-structures/pages/gomory-hu-tree-construct-trace.md](lessons/graph-cut-structures/pages/gomory-hu-tree.md) | 완료 | 반영: 첫 단계 그림이 parent 배열과 달리 1-2-3 사슬로 그려져 있어 형제 구조로 정정. 수치 trace 보존. |
| 118 | [lessons/graph-cut-structures/pages/cut-sparsification.md](lessons/graph-cut-structures/pages/cut-sparsification.md) | 완료 | 반영: 경로 압축 없는 DSU와 alpha 복잡도 불일치 수정. 각 cut의 min(k,cut) 보존 명확화. |
| 119 | [lessons/graph-cut-structures/pages/global-min-cut-applications.md](lessons/graph-cut-structures/pages/global-min-cut.md) | 완료 | 통합 반영: partition 복원은 114로, 간선 민감도는 모든 최소 cut과 일부 최소 cut을 구분해 허브에 통합. 나머지 선택표 중복 삭제. |
| 120 | [lessons/graph-cut-structures/pages/cactus-representation.md](lessons/graph-cut-structures/pages/cactus-representation.md) | 완료 | 반영: min-cut cactus의 양의 최소 cut 전제와 원래 정점 mapping 조건, DFS는 cactus 입력·고유 간선 ID·self-loop 없음 전제 명시. |
| 121 | [lessons/graph-cut-structures/pages/practice-set.md](lessons/graph-cut-structures/pages/practice-set.md) | 완료 | 반영: 완결된 global-cut 연습·trace 유지, 반복 제출 체크리스트 축약. |
| 122 | [lessons/euler-tour-tree/lesson.md](lessons/euler-tour-tree/lesson.md) | 완료 | 반영: ETT가 아닌 generic treap skeleton 중복 제거. 정점 마커 1개·양방향 arc 기준으로 일관된 link/cut trace 재작성 및 기대 복잡도 명시. |
| 123 | [lessons/mobius-inversion/lesson.md](lessons/mobius-inversion/lesson.md) | 완료 | 반영: limit0 처리, frequency 범위·양수 값·쌍 인덱스 의미 명시. 일반 좌표 압축은 약수 관계를 보존하지 않는다는 오류 수정. |
| 124 | [lessons/convex-cost-flow/lesson.md](lessons/convex-cost-flow/lesson.md) | 완료 | 반영: convex 검사 함수를 실제 생성에서 호출하고 C(0)=0·고정 수요·음수 cycle 전제 명시. 반복 비교·실수 목록 축약. |
| 125 | [lessons/dynamic-network-optimization/lesson.md](lessons/dynamic-network-optimization/lesson.md) | 완료 | 반영: block MST는 시작 MST와 변경 간선만 합치면 틀림. 미변경 간선의 MSF certificate를 먼저 만드는 조건으로 수정하고 모호한 연습 축약. |
| 126 | [lessons/dynamic-network-optimization/pages/dynamic-flow.md](lessons/dynamic-network-optimization/pages/dynamic-flow.md) | 완료 | 반영: 기다림 용량 1e9를 총 물량 인자로 대체하고 T+1층·정점 ID 범위를 명시. 반복 선택표 축약. |
| 127 | [lessons/dynamic-network-optimization/pages/dynamic-mst.md](lessons/dynamic-network-optimization/pages/dynamic-mst.md) | 완료 | 반영: 정적 HLD만으로 교체 MST 유지 불가, 고정 간선 MSF block 조건 및 실제 N+B 재계산 비용 명시. 삭제 뒤 전체 재계산 기준 풀이로 Kruskal baseline은 유지. |
| 128 | [lessons/dynamic-network-optimization/pages/practice-set.md](lessons/dynamic-network-optimization/pages/practice-set.md) | 완료 | 반영: 감소 후 flow를 알 수 없음 대신 실제 값 3과 불가능한 기존 flow를 구분. 모호한 MST 연습 삭제. |
| 129 | [lessons/linear-basis-applications/lesson.md](lessons/linear-basis-applications/lesson.md) | 완료 | 통합 반영: basis 삽입·표현 가능성 중복은 103 재사용. bit63·rank64·kth 실제 정규화 비용·음수 가중치 greedy 조건 수정. |
| 130 | [lessons/dirichlet-convolution/lesson.md](lessons/dirichlet-convolution/lesson.md) | 완료 | 반영: 입력 배열 길이·산술 범위·multiplicative f(1)=1 전제와 반복 실수 목록 정리. |
| 131 | [lessons/minkowski-sum/lesson.md](lessons/minkowski-sum/lesson.md) | 완료 | 반영: 빈 집합 Minkowski 합을 빈 집합으로 고치고 퇴화 입력 조건·외적 범위·일반 점집합 hull은 정확 합이 아니라 볼록화임을 명시. |
| 132 | [lessons/rotating-calipers-applications/lesson.md](lessons/rotating-calipers-applications/lesson.md) | 완료 | 반영: 최소 폭 코드에 엄격 볼록·중복 없음·좌표 범위 전제, 모호한 접선 의사코드와 반복 조건 목록 축약. |
| 133 | [lessons/multiplicative-functions/lesson.md](lessons/multiplicative-functions/lesson.md) | 완료 | 반영: limit0 처리와 f(1)=1 조건. 1e7에서 다중 int 배열 메모리 약280MB 명시, 중복 공식·실수 목록 축약. |
| 134 | [lessons/summatory-number-theory/lesson.md](lessons/summatory-number-theory/lesson.md) | 완료 | 반영: summatory phi 항등식의 잘못된 floor 제곱 제거, 실제 Phi 재귀식 제시. 최댓값에서 right+1 overflow 처리. |
| 135 | [lessons/shape-distance-modeling/lesson.md](lessons/shape-distance-modeling/lesson.md) | 완료 | 반영: 포함 관계인 다각형 거리를 양수로 내는 baseline 오류와 점 선분 퇴화 교차 오류 수정. SAT 포함시 단순 overlap 길이로 이동거리 산정 오류 명시. |
| 136 | [lessons/circle-geometry/lesson.md](lessons/circle-geometry/lesson.md) | 완료 | 반영: 원-직선 교점이 직선 방향이 아닌 법선 방향으로 생성되는 오류 수정. 중복 Point 연산 삭제, 퇴화 직선·동심원·acos 조건 보완. |
| 137 | [lessons/quadrangle-inequality-proofs/lesson.md](lessons/knuth-optimization/lesson.md) | 완료 | 통합 반영: 파일 합 비용의 비음수 조건을 94에 합치고 중복 Knuth 검사·선택표 삭제. 실제 Monge opt 교환 증명을 95에 보강. |
| 138 | [lessons/circle-arrangement/lesson.md](lessons/circle-arrangement/lesson.md) | 완료 | 반영: union에서 중복 원 제거 필수와 depth 문제의 중복 보존 구분. 단순 각도 helper 삭제하고 arc 기여식·복잡도 중심으로 축약. |
| 139 | [lessons/geometry-robustness-and-duality/lesson.md](lessons/geometry-robustness-and-duality/lesson.md) | 완료 | 반영: 편집 메타 설명과 본문·연습 중복을 줄이고 탐색 허브 및 실제 power 경계 예시는 보존. |
| 140 | [lessons/geometry-robustness-and-duality/pages/robust-geometry-predicates.md](lessons/geometry-robustness-and-duality/pages/robust-geometry-predicates.md) | 완료 | 반영: 128비트도 전체 long long 좌표에 안전하지 않음을 명시. 실제 거의 평행한 예제로 수정하고 EPS 정렬의 비추이 동치 문제 설명. |
| 141 | [lessons/geometry-robustness-and-duality/pages/power-diagram.md](lessons/geometry-robustness-and-duality/pages/power-diagram.md) | 완료 | 반영: weighted Voronoi 모든 종류가 power diagram은 아님. unbounded cell·동일 좌표 지배 관계 및 clipping 복잡도 구분. |
| 142 | [lessons/geometry-robustness-and-duality/pages/robust-delaunay.md](lessons/geometry-robustness-and-duality/pages/robust-delaunay.md) | 완료 | 통합 반영: orientation 복제 코드는 140 재사용. flip 예시는 서로 반대쪽 두 삼각형·볼록 사각형으로 수정, predicate만으로 Delaunay 간선 판정 충분 오해 제거. |
| 143 | [lessons/geometry-robustness-and-duality/pages/3d-convex-hull.md](lessons/geometry-robustness-and-duality/pages/3d-convex-hull.md) | 완료 | 반영: 3D hull 최종 면수는 O(N)이고 단순 scan은 O(N²)임을 정정. shuffle만으로 NlogN 아님, coplanar 바깥 점 처리 보완. |
| 144 | [lessons/geometry-robustness-and-duality/pages/regular-triangulation.md](lessons/geometry-robustness-and-duality/pages/regular-triangulation.md) | 완료 | 반영: 일반 위치와 퇴화 regular subdivision/triangulation을 구분하고 3점만으로 face 구성이 바뀐다는 예시 수정. |
| 145 | [lessons/geometry-robustness-and-duality/pages/practice-set.md](lessons/geometry-robustness-and-duality/pages/practice-set.md) | 완료 | 통합 반영: 정수 선분 교차 구현은 140 재사용. predicate 정의는140 재사용. power boundary에서 실제 빈 cell이 되는 수치 예제로 구체화. |
| 146 | [lessons/black-box-linear-algebra/lesson.md](lessons/black-box-linear-algebra/lesson.md) | 완료 | 반영: 투영 수열 최소 다항식과 행렬 최소 다항식을 구분. N 포함 matvec 비용·정규화 입력 계약 및 CRT로 rank 해결 오해 제거. |
| 147 | [lessons/game-theory-applications/lesson.md](lessons/game-theory-applications/lesson.md) | 완료 | 반영: 깊이 제한 minimax는 게임 전체 정확해가 아님, normal play·유한성 조건을 명시하고 반복 분류표 축약. |
| 148 | [lessons/inversion-geometry/lesson.md](lessons/inversion-geometry/lesson.md) | 완료 | 반영: 반전 반지름 양수, 방향 반전과 무방향 각 보존, 중심 제외 조건 명시. 반복 체크리스트 축약. |
| 149 | [lessons/matroid-algorithms/lesson.md](lessons/matroid-algorithms/lesson.md) | 완료 | 반영: 저장소 편집 메타 설명과 상태 열을 줄이고 모델 선택·oracle 비용만 유지. |
| 150 | [lessons/matroid-algorithms/pages/matroid-basics-and-exchange.md](lessons/matroid-algorithms/pages/matroid-basics-and-exchange.md) | 완료 | 반영: 모든 부분집합 독립이라는 잘못된 도입 수정. 음수 가중치 제외 조건과 정확히2 반례의 hereditary 오류를 실제 교환 반례로 대체. |
| 151 | [lessons/matroid-algorithms/pages/matroid-intersection.md](lessons/matroid-algorithms/pages/matroid-intersection.md) | 완료 | 반영: hereditary 오류 수정. 임의 DFS 경로가 아닌 최단 증가 경로 필요 명시, 예시는 최대 크기2로 더 증대 불가라는 실제 결론 표시. |
| 152 | [lessons/matroid-algorithms/pages/matroid-union.md](lessons/matroid-algorithms/pages/matroid-union.md) | 완료 | 반영: copies*capacity int overflow 수정, 유효 class·비음수 전제, 반복 exchange 설명 축약. |
| 153 | [lessons/matroid-algorithms/pages/matroid-parity.md](lessons/matroid-algorithms/pages/matroid-parity.md) | 완료 | 통합 반영: XOR basis 복제는103 재사용. pair 내부 순서는 독립성 결과에 영향 없다는 오류 정정, matching 환원에서 endpoint occurrence 원소 구분. |
| 154 | [lessons/matroid-algorithms/pages/practice-set.md](lessons/matroid-algorithms/pages/practice-set.md) | 완료 | 반영: 완결된 partition 연습·교환 증명 유지. 모호한 union 실패 연습과 반복 체크리스트 삭제. |
| 155 | [lessons/sparse-linear-systems/lesson.md](lessons/sparse-linear-systems/lesson.md) | 완료 | 반영: 일관성 없는 rank 부족계는 다중 해가 아님. elimination 절의 matvec 복제 삭제 및 실수/유한체 Laplacian rank 조건 구분. |
| 156 | [lessons/linear-algebra-applications/lesson.md](lessons/linear-algebra-applications/lesson.md) | 완료 | 반영: 선택표 3개를 실제 링크 있는 1개로 통합, XOR rank 중복 코드는103 연결. determinant 자체는 확률 알고리즘 아님 구분. |
| 157 | [lessons/linear-algebra-applications/pages/decision-map-practice.md](lessons/linear-algebra-applications/lesson.md) | 완료 | 반영: 자기 제약 u=v 행 생성은 XOR toggle임을 명시. 실제 두 연습·trace 유지, 반복 체크리스트 삭제. |
| 158 | [lessons/online-convex-optimization/lesson.md](lessons/online-convex-optimization/lesson.md) | 완료 | 반영: 이전 문서 편집 내역 도입 삭제, 관측 모델·연결 허브 유지. |
| 159 | [lessons/online-convex-optimization/pages/online-decision-and-regret.md](lessons/online-convex-optimization/pages/online-decision-and-regret.md) | 완료 | 반영: gradient 일괄 함수는 선형 손실 재생/최종점 반환임을 명시. 일반 online은 선택 뒤 gradient 계산, regret 보장 조건과 최종점 보장 구분. |
| 160 | [lessons/online-convex-optimization/pages/mirror-descent-and-multiplicative-weights.md](lessons/online-convex-optimization/pages/mirror-descent-and-multiplicative-weights.md) | 완료 | 반영: 일반 mirror descent는 Bregman 제약 최소화 포함. log weight 수치 안정성과 고정 eta 동치 보존, 반복 목록 축약. |
| 161 | [lessons/online-convex-optimization/pages/dual-averaging.md](lessons/online-convex-optimization/pages/dual-averaging.md) | 완료 | 반영: actionCount 양수·loss 차원·유한 누적값 전제, maxLogWeight 실제 최댓값 초기화 및 최종 다음 라운드 분포 의미 명시. |
| 162 | [lessons/online-convex-optimization/pages/practice-set.md](lessons/online-convex-optimization/pages/practice-set.md) | 완료 | 반영: 구체적 expected-loss 연습 유지, 모호한 추가 box 연습과 반복 체크리스트 삭제. 매 라운드 손실 누적을 보여 주는 실행 예제는 유지. |
| 163 | [lessons/randomized-determinant/lesson.md](lessons/randomized-determinant/lesson.md) | 완료 | 반영: determinant 입력 정규화·prime 및 곱 범위 명시, random diagonal은 rank를 바꾸거나 상쇄를 없애지 않는 오류 삭제. Tutte 실패확률 조건 보존. |
| 164 | [lessons/matrix-tree-theorem-applications/lesson.md](lessons/matrix-tree-theorem-applications/lesson.md) | 완료 | 반영: 제시한 in-degree Laplacian은 root에서 뻗는 arborescence라는 방향 오류 정정. self-loop 명시적 제외와 n1 빈 determinant 계약. |
| 165 | [lessons/planar-graph-duality/lesson.md](lessons/planar-graph-duality/lesson.md) | 완료 | 반영: 이전 편집 내역 도입 삭제, embedding 조건과 페이지 연결 유지. |
| 166 | [lessons/planar-graph-duality/pages/half-edge-and-face-traversal.md](lessons/planar-graph-duality/pages/half-edge-and-face-traversal.md) | 완료 | 반영: 비연결 성분의 boundary walk는 face와 다름을 명시하여 연결 입력으로 제한, 정수 polar comparator·128비트 면적 및 간선 없는 경우 처리. Euler는 좌우 반전 검출 못함. |
| 167 | [lessons/planar-graph-duality/pages/dual-graph-construction.md](lessons/planar-graph-duality/pages/half-edge-and-face-traversal.md) | 완료 | 반영: bond와 simple dual cycle 대응으로 정정, 중복 face 순회는166 링크, face ID·비용 자료형 계약 보완. |
| 168 | [lessons/planar-graph-duality/pages/cut-cycle-duality.md](lessons/planar-graph-duality/pages/cut-cycle-duality.md) | 완료 | 반영: 일반 cut은 dual Eulerian 부분그래프. 공통 face를 둘로 분할해야 s-t min-cut이 경로가 되는 실제 구성과 조건 명시. |
| 169 | [lessons/planar-graph-duality/pages/practice-set.md](lessons/planar-graph-duality/pages/practice-set.md) | 완료 | 반영: E·시작/끝 face 제한 추가, 중복 Dijkstra는 기본노트 재사용, 모호한 boundary 연습·반복 체크리스트 축약. |
| 170 | [lessons/complexity-input-size/lesson.md](lessons/complexity-input-size/lesson.md) | 완료 | 본문·코드 정독. canExtend의 상수 시간 전제 보완. 예시 유지. |
| 171 | [lessons/cpp-contest-basics/lesson.md](lessons/cpp-contest-basics/lesson.md) | 완료 | 본문 정독. 페이지 안내와 독립 스니펫 사용 계약 유지. |
| 172 | [lessons/cpp-contest-basics/pages/submission-and-state.md](lessons/cpp-contest-basics/pages/submission-and-state.md) | 완료 | 본문·코드 정독. 초기화 시점·활성 구간·공개 API 계약 유지. |
| 173 | [lessons/cpp-contest-basics/pages/arrays-and-random.md](lessons/cpp-contest-basics/pages/arrays-and-random.md) | 완료 | 본문·코드 정독. copy 구간 겹침 조건 명료화. 난수 예제 유지. |
| 174 | [lessons/cpp-contest-basics/pages/sorting-queue-heap.md](lessons/cpp-contest-basics/pages/sorting-queue-heap.md) | 완료 | 본문·코드 정독. 정렬·큐·힙은 다른 사용 목적과 용량 계약이 있어 유지. |
| 175 | [lessons/cpp-contest-basics/pages/practice.md](lessons/cpp-contest-basics/pages/practice.md) | 완료 | 본문·코드 정독. 공통 스니펫 검사와 ORDERING 채점 절차는 검증 범위가 달라 유지. |
| 176 | [lessons/sorting/lesson.md](lessons/sorting/lesson.md) | 완료 | 본문·코드 정독. quick sort 평균/최악 구분, counting 빈도 재초기화, radix 배열 상한 보완. |
| 177 | [lessons/prefix-sum-difference/lesson.md](lessons/prefix-sum-difference/lesson.md) | 완료 | 본문·코드 정독. 빈 2차원 배열 접근 수정, 직사각형 전제 명시. 차분/누적합 예제 유지. |
| 178 | [lessons/greedy/lesson.md](lessons/greedy/lesson.md) | 완료 | 본문·코드 정독. 과제 점수 비음수 전제, 만료 요청 제거 순서 수정. 증명 예시는 유지. |
| 179 | [lessons/two-pointers-sliding-window/lesson.md](lessons/two-pointers-sliding-window/lesson.md) | 완료 | 본문·코드 정독. k<=0 경계 처리, 이동당 비용·해시 평균 시간 명시. |
| 180 | [lessons/binary-search/lesson.md](lessons/binary-search/lesson.md) | 완료 | 본문·코드 정독. 최소/최대 경계와 overflow 전제 포함해 유지. |
| 181 | [lessons/coordinate-compression/lesson.md](lessons/coordinate-compression/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 원래 거리 설명 중복을 한 섹션으로 통합. |
| 182 | [lessons/priority-queue-heap/lesson.md](lessons/priority-queue-heap/lesson.md) | 완료 | 본문·코드 정독. 직접 힙 구현은 공통 노트 링크로 이미 통합되어 있어 유지. |
| 183 | [lessons/meldable-heap/lesson.md](lessons/meldable-heap/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 반복된 상각/최악 시간 설명 축약, DSU 조회 비용 구분. |
| 184 | [lessons/heuristic/lesson.md](lessons/heuristic/lesson.md) | 완료 | 본문 정독. 문제별 사례 안내와 평가 계약 유지. |
| 185 | [lessons/heuristic/pages/ordering-route-improvement.md](lessons/heuristic/pages/ordering-route-improvement.md) | 완료 | 본문·코드 정독. 열린 경로 2-opt 차분·완성 구현 유지. |
| 186 | [lessons/heuristic/pages/search-strategies.md](lessons/heuristic/pages/search-strategies.md) | 완료 | 본문 정독. SA와 재시도는 서로 다른 탐색 전략으로 유지. |
| 187 | [lessons/heuristic/pages/placement-and-repair.md](lessons/heuristic/pages/placement-and-repair.md) | 완료 | 본문·코드 정독. 수정 반영: first-fit 다중 루프 탈출, bitmask 경계, 로컬 repair와 공개 API 실행 구분, 점수 이중 보너스 제거. |
| 188 | [lessons/heuristic/pages/aircontech-beam-search.md](lessons/heuristic/pages/aircontech-beam-search.md) | 완료 | 본문·코드 정독. 수정 반영: 상태 복사·720분 검증 코드 명시, 반복 계약 설명 축약. |
| 189 | [lessons/dynamic-programming/lesson.md](lessons/dynamic-programming/lesson.md) | 완료 | 본문 정독. 두 DP 페이지 안내 유지. |
| 190 | [lessons/dynamic-programming/pages/state-and-transition.md](lessons/dynamic-programming/pages/state-and-transition.md) | 완료 | 본문·코드 정독. 수정 반영: 격자 양수 크기와 동전 입력 전제 보완. |
| 191 | [lessons/dynamic-programming/pages/knapsack-and-lis.md](lessons/dynamic-programming/pages/knapsack-and-lis.md) | 완료 | 본문·코드 정독. 수정 반영: 빈 LIS 역참조, tails 인덱스 설명 수정, 배낭 입력 전제. |
| 192 | [lessons/tsp-hamiltonian/lesson.md](lessons/tsp-hamiltonian/lesson.md) | 완료 | 본문 정독. 경로/사이클 문제 구분과 페이지 안내 유지. |
| 193 | [lessons/tsp-hamiltonian/pages/search-and-dp.md](lessons/tsp-hamiltonian/pages/search-and-dp.md) | 완료 | 본문·코드 정독. 수정 반영: INF 상태의 복귀 비용 합산 차단, 복원 가능 여부 전제. |
| 194 | [lessons/tsp-hamiltonian/pages/heuristic-and-choices.md](lessons/tsp-hamiltonian/pages/heuristic-and-choices.md) | 완료 | 본문·코드 정독. 수정 반영: metric 대칭·비음수 전제 명시. |
| 195 | [lessons/union-find/lesson.md](lessons/union-find/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 단일 연산과 상각 비용 구분. |
| 196 | [lessons/bfs-dfs-grid/lesson.md](lessons/bfs-dfs-grid/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: gridDistance 빈 입력·시작점 방어, 중복 그래프 설명 축약. |
| 197 | [lessons/graph-tree-basics/lesson.md](lessons/graph-tree-basics/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 루트 깊이 초기화와 재귀 깊이 전제. |
| 198 | [lessons/graph-tree-basics/pages/tree-diameter-centroid.md](lessons/graph-tree-basics/pages/tree-diameter-centroid.md) | 완료 | 본문·코드 정독. 수정 반영: 빈 트리 처리, 센트로이드 곱 overflow 회피. |
| 199 | [lessons/graph-tree-basics/pages/mst-kruskal-prim.md](lessons/graph-tree-basics/pages/mst-kruskal-prim.md) | 완료 | 본문·코드 정독. 수정 반영: 음수 MST 비용과 실패 -1의 충돌 제거. |
| 200 | [lessons/zero-one-bfs/lesson.md](lessons/zero-one-bfs/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: BFS 비용표 중복 삭제, 선형 시간 근거 명료화. |
| 201 | [lessons/topological-sort-dag/lesson.md](lessons/topological-sort-dag/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 진입 차수의 정점 수/간선 수 혼동 수정. |
| 202 | [lessons/dijkstra/lesson.md](lessons/dijkstra/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: lazy heap 시간의 log E/log V 구분. |
| 203 | [lessons/bellman-ford-negative-cycle/lesson.md](lessons/bellman-ford-negative-cycle/lesson.md) | 완료 | 본문·코드 정독. 음수 사이클 영향 범위와 overflow 전제 유지. |
| 204 | [lessons/floyd-warshall/lesson.md](lessons/floyd-warshall/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 시작=목표 복원 초기값과 덧셈 범위 전제. |
| 205 | [lessons/sqrt-decomposition/lesson.md](lessons/sqrt-decomposition/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 예시 배열 범위를 벗어난 질의 수정. |
| 206 | [lessons/fenwick-tree/lesson.md](lessons/fenwick-tree/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: bit<<1 대신 n/2로 상한 비교. |
| 207 | [lessons/segment-tree/lesson.md](lessons/segment-tree/lesson.md) | 완료 | 본문 정독. 기본/lazy 링크 안내 유지. |
| 208 | [lessons/segment-tree/pages/basic-range-query.md](lessons/segment-tree/pages/basic-range-query.md) | 완료 | 본문·코드 정독. 비어 있지 않은 배열·항등원 계약 유지. |
| 209 | [lessons/segment-tree/pages/lazy-propagation.md](lessons/segment-tree/pages/lazy-propagation.md) | 완료 | 본문·코드 정독. 수정 반영: 구현과 맞지 않는 lazy 저장 의미 수정. |
| 210 | [lessons/hungarian-algorithm/lesson.md](lessons/hungarian-algorithm/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: n>m 전환 목적 구분, 직사각형 복잡도 정밀화, 비용 범위 구체화. |
| 211 | [lessons/treap/lesson.md](lessons/treap/lesson.md) | 완료 | 본문 정독. BST 소개와 구현 안내 유지. |
| 212 | [lessons/treap/pages/treap-core.md](lessons/treap/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 상위 페이지와 중복된 Treap 도입 삭제, 메모리 소유권 명시. |
| 213 | [lessons/minimax-alpha-beta/lesson.md](lessons/minimax-alpha-beta/lesson.md) | 완료 | 본문 정독. Alpha-Beta 상한/하한 예시 유지. |
| 214 | [lessons/testing-and-stress/lesson.md](lessons/testing-and-stress/lesson.md) | 완료 | 본문 정독. 별도 기준 답·차분 복구·재현 절차 유지. |
| 215 | [lessons/proof-and-invariants/lesson.md](lessons/proof-and-invariants/lesson.md) | 완료 | 본문 정독. 이분 탐색 불변식·교환·경우의 수 증명은 역할이 달라 유지. |
| 216 | [lessons/dynamic-segment-tree/lesson.md](lessons/dynamic-segment-tree/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 루트/질의 범위와 시간 복잡도 명료화. |

## 통합 및 검증 결과

통합 대상과 남은 경로는 [review-merges.json](scripts/review-merges.json)에 기록했습니다. 삭제된 파일의 고유 예시·조건은 연결된 본문에 남겼습니다. 위 표의 문서 이름은 검토 당시 경로이고 링크는 통합 후 경로입니다.

- 정독: 기준 커밋의 216개 파일 전체를 읽고 개별 판단을 기록했습니다.
- 편집: 반복 실수표·선택표·불완전 연습·빈 골격을 정리하고, 공통 구현은 재사용하도록 바꿨습니다.
- 검증 완료: `python3 scripts/validate_lessons.py` 통과. 99개 강의의 구조·링크·독립 C++ 블록을 검사하고, STL 없는 공통 코드 7개와 실제 본문을 조합한 경계·단순 풀이 비교 38개를 ASan/UBSan으로 실행했습니다.
- 재현: [검증 스크립트](scripts/check_review_examples.py), [문서 블록과 검증 사례](scripts/review-example-cases.json). 코드가 없는 개념 문서의 검토와 컴파일·실행 검증은 구분합니다.
