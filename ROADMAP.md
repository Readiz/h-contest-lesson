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

## 우선 추가할 주제

| 우선순위 | 후보 lessonId | 주제 | 연습 문제 상태 |
| ---: | --- | --- | --- |
| 1 | `persistent-segment-tree` | 버전이 있는 Segment Tree, k번째 수 질의 | TODO: persistent 자료구조 `/practice/...` 문제 필요 |
| 2 | `suffix-automaton` | 모든 부분 문자열을 상태로 압축하는 문자열 automaton | TODO: suffix automaton `/practice/...` 문제 필요 |
| 3 | `floyd-warshall` | 모든 정점 쌍 최단거리, transitive closure | TODO: APSP `/practice/...` 문제 필요 |
| 4 | `matrix-exponentiation` | 선형 점화식, 그래프 walk 수, 행렬 빠른 거듭제곱 | TODO: 행렬 거듭제곱 `/practice/...` 문제 필요 |
| 5 | `fft-ntt` | 다항식 곱셈, convolution, NTT | TODO: convolution `/practice/...` 문제 필요 |

## 추가 후보 묶음

| 영역 | 후보 lessonId |
| --- | --- |
| 문자열 | `suffix-automaton` |
| 그래프 심화 | `floyd-warshall`, `matching-cover-duality` |
| 자료구조/오프라인 | `persistent-segment-tree` |
| 수학 심화 | `matrix-exponentiation`, `fft-ntt` |
| 기하 | `sweep-line-geometry` |

## 공개 레슨으로 올리기 전 조건

1. `lessons/<lessonId>/lesson.md` 또는 `pages/` 본문이 "읽기 -> 구현하기 -> 문제 풀기 -> 실수 점검하기" 흐름을 갖춘다.
2. C++ 구현 또는 의사 구현이 있고, 필요한 경우 `cpp compile-check` fence로 컴파일 검증 대상에 올린다.
3. `## 연습 문제` 표는 `단계`, `문제`, `목표`, `힌트 키워드` 열을 사용한다.
4. 적절한 h-contest 문제가 없으면 문제 칸에 `TODO: ... /practice/... 문제 필요`라고 남긴다.
5. 공개하기 전에 `python3 scripts/generate_catalog.py`와 `python3 scripts/validate_lessons.py`를 통과시킨다.
