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

## 우선 추가할 주제

| 우선순위 | 후보 lessonId | 주제 | 연습 문제 상태 |
| ---: | --- | --- | --- |
| 1 | `trie-aho-corasick` | Trie, 다중 패턴 매칭, Aho-Corasick | TODO: 문자열 다중 패턴 `/practice/...` 문제 필요 |
| 2 | `suffix-array-lcp` | Suffix Array, LCP, suffix 기반 문자열 질의 | TODO: suffix 구조 `/practice/...` 문제 필요 |
| 3 | `min-cost-flow` | 비용이 있는 Flow, shortest augmenting path | TODO: Min-Cost Flow `/practice/...` 문제 필요 |
| 4 | `rotating-calipers` | Convex Hull 위의 지름, 폭, antipodal pair | TODO: 기하 심화 `/practice/...` 문제 필요 |
| 5 | `combinatorics-ncr` | nCr, inclusion-exclusion, Lucas/CRT 조합론 | TODO: 조합론 `/practice/...` 문제 필요 |

## 추가 후보 묶음

| 영역 | 후보 lessonId |
| --- | --- |
| 문자열 | `trie-aho-corasick`, `suffix-array-lcp` |
| 그래프 심화 | `floyd-warshall`, `min-cost-flow` |
| 자료구조/오프라인 | `persistent-segment-tree`, `sparse-table-rmq` |
| 수학 심화 | `combinatorics-ncr`, `matrix-exponentiation`, `fft-ntt` |
| 기하 | `rotating-calipers`, `sweep-line-geometry` |

## 공개 레슨으로 올리기 전 조건

1. `lessons/<lessonId>/lesson.md` 또는 `pages/` 본문이 "읽기 -> 구현하기 -> 문제 풀기 -> 실수 점검하기" 흐름을 갖춘다.
2. C++ 구현 또는 의사 구현이 있고, 필요한 경우 `cpp compile-check` fence로 컴파일 검증 대상에 올린다.
3. `## 연습 문제` 표는 `단계`, `문제`, `목표`, `힌트 키워드` 열을 사용한다.
4. 적절한 h-contest 문제가 없으면 문제 칸에 `TODO: ... /practice/... 문제 필요`라고 남긴다.
5. 공개하기 전에 `python3 scripts/generate_catalog.py`와 `python3 scripts/validate_lessons.py`를 통과시킨다.
