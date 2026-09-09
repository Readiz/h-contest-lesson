# 학습 노트 전체 본문 검토 기록

## 2026-09-09 후속 시각화 12개

앞선 전체 검토 뒤 남긴 후속 후보를 보강했습니다. 기본자료의 기존 시각화 8개에 이어 12개를 추가했으며 강의 97개·본문 169개는 유지합니다. 각 그림은 해당 설명 옆에 두고 원본 확대 링크와 입력 전제를 함께 적었습니다.

- 복잡도 증가 비율, 좌표 압축의 거리 손실, 힙의 배열 인덱스, Skew Heap 병합, BFS 방문 시점, 0-1 BFS deque 순서, 위상 정렬 진입 차수, 음수 사이클 영향 범위, Floyd-Warshall의 경유지, Treap split, 동적 세그먼트 트리 노드 생성, 트리 중심/센트로이드 반례.
- 표의 P2 완료는 이번 후속 보강을 뜻합니다. 기존 도식이 충분하거나 그림보다 계약·검증 코드가 중요한 자료는 유지했습니다.
- 검증: 전체 validator(97개 강의·공통 코드 7개·조합/경계/차분 사례 41개, ASan/UBSan) 통과. 실제 앱의 1280px·390px에서 새 그림 12개를 각각 촬영해 직접 확인했습니다. 트리 반례의 모든 시작점 거리와 삭제 후 성분 크기도 별도 계산으로 검산했습니다.
- 화면 검증 중 발견한 대체 텍스트의 Markdown 대괄호 충돌을 수정했습니다. 앱이 상대 SVG 링크를 `#`으로 바꾸므로 앞선 8개까지 포함한 확대 링크 20개를 공개 원본 절대 URL로 교정했습니다. 보호된 운영 로그인 본문을 직접 확인했다는 뜻은 아닙니다.

## 2026-09-09 전수 재검토와 기본자료 시각화

기준 커밋 `92ead1f`. 당시 등록된 97개 강의의 본문·하위 페이지 **190개 모두**를 코드 블록까지 읽고 개별 판단을 기록했습니다. 앞선 부분 검토나 최초 216개 기록으로 이번 검토를 대신하지 않았습니다. 아래 판단은 읽을 당시 발견한 사항이며, 편집 결과는 통합 경로와 이번 변경에 반영했습니다. 알고리즘의 모든 입력에 대한 형식적 증명을 의미하지는 않습니다.

- 직접 이어지는 정의·구현·실습 등 21개 경계 통합: **190 → 169개 본문**, **97개 강의(기본 30, 참고 67) 유지**.
- SAM의 중복 construction을 한 구현으로 통합하고, MDP의 유한 지평·할인·정책 반복은 각 전제를 유지한 한 페이지로 정리했습니다. 일반 Lagrangian과 Exact-K도 최소화/최대화 부호 및 복원 조건을 함께 비교합니다.
- Manacher 전처리와 구간 판정을 보충하고 길이 10 이하 모든 이진 문자열의 모든 비어 있지 않은 구간을 직접 회문 판정과 비교했습니다.
- 누적합·투 포인터·이분 탐색·배낭 DP·Fenwick·Segment Tree·Dijkstra·Alpha-Beta에 SVG 8개와 확대 링크를 추가했습니다.
- 전체 validator: 97개 강의, 공통 코드 7개 및 조합·경계·차분 검증 41개, ASan/UBSan 통과.
- 실제 production frontend dist와 격리된 로컬 backend에서 169개 강의 경로를 열었습니다. 새 그림 8개는 1280px·390px에서 각각 전체 화면과 그림 영역을 촬영하고 직접 확인했습니다. 운영 로그인 상태에서의 보호 본문 확인과는 구분합니다.

### 문서별 읽기 기록

| 번호 | 검토한 원문 | 통합 후 위치 | 읽기 판단 |
| --- | --- | --- | --- |
| 1 | `lessons/complexity-input-size/lesson.md` | [본문](lessons/complexity-input-size/lesson.md) | 유지: 연산량·전체 TC·메모리 계산을 한 흐름으로 설명. 복잡도 비교 시각화 후보 P2. |
| 2 | `lessons/cpp-contest-basics/lesson.md` | [본문](lessons/cpp-contest-basics/lesson.md) | 유지: 제출 계약·자료구조·실제 채점은 서로 다른 사용 목적. 독립 스니펫 탐색 허브. |
| 3 | `lessons/cpp-contest-basics/pages/submission-and-state.md` | [본문](lessons/cpp-contest-basics/pages/submission-and-state.md) | 유지: TC 초기화·공개 API 계약과 예제 일치. 초기화 시점 도식 후보 P2. |
| 4 | `lessons/cpp-contest-basics/pages/arrays-and-random.md` | [본문](lessons/cpp-contest-basics/pages/arrays-and-random.md) | 유지: seed·부분 셔플·배열 계약과 구현 일치. seed 반복 예시가 충분함. |
| 5 | `lessons/cpp-contest-basics/pages/sorting-queue-heap.md` | [본문](lessons/cpp-contest-basics/pages/sorting-queue-heap.md) | 유지: 정렬·큐·힙 독립 복사 코드와 용량 의미 명시. 큐/힙 시각화는 해당 기본 강의 우선. |
| 6 | `lessons/cpp-contest-basics/pages/practice.md` | [본문](lessons/cpp-contest-basics/pages/practice.md) | 유지: 공통 코드 검사와 실제 채점 결과의 증거 범위를 구분. 별도 실습 역할 있음. |
| 7 | `lessons/sorting/lesson.md` | [본문](lessons/sorting/lesson.md) | 유지: 정렬 기준·안정성·counting·radix 연결. 기존 radix 그림 있음. |
| 8 | `lessons/prefix-sum-difference/lesson.md` | [본문](lessons/prefix-sum-difference/lesson.md) | 유지: 1D/2D 누적합과 차분은 같은 역연산 흐름. 포함배제·네 모서리 시각화 P1. |
| 9 | `lessons/greedy/lesson.md` | [본문](lessons/greedy/lesson.md) | 유지: 증명 패턴과 실제 문제 사례가 연결됨. 기존 시각화 6개로 추가 우선순위 낮음. |
| 10 | `lessons/two-pointers-sliding-window/lesson.md` | [본문](lessons/two-pointers-sliding-window/lesson.md) | 유지: 양끝 포인터와 창 축소의 단조성 명시. 양수 창의 확장/축소 시각화 P1. |
| 11 | `lessons/binary-search/lesson.md` | [본문](lessons/binary-search/lesson.md) | 유지: lower/upper bound와 최소/최대 판정의 경계 방향 구분. F/T 경계·올림 mid 시각화 P1. |
| 12 | `lessons/coordinate-compression/lesson.md` | [본문](lessons/coordinate-compression/lesson.md) | 유지: 순서 보존과 실제 거리 비보존 구분. 압축 전후 간격 그림 P2. |
| 13 | `lessons/priority-queue-heap/lesson.md` | [본문](lessons/priority-queue-heap/lesson.md) | 유지: 힙 불변식과 공통 코드 링크. 배열/트리 대응 및 pop 이동 시각화 P1. |
| 14 | `lessons/meldable-heap/lesson.md` | [본문](lessons/meldable-heap/lesson.md) | 유지: meld가 별도 목적이며 binary heap과 통합하지 않음. 상각/최악 구분과 pool 계약 확인. |
| 15 | `lessons/heuristic/lesson.md` | [본문](lessons/heuristic/lesson.md) | 유지: 경로·배치·일정이라는 별도 문제 모델을 안내하는 허브. |
| 16 | `lessons/heuristic/pages/ordering-route-improvement.md` | [본문](lessons/heuristic/pages/ordering-route-improvement.md) | 유지: 열린 경로·창고 고정·꼬리 2-opt 계약과 구현 일치. 끝점 간선 한 개 변경 시각화 P1. |
| 17 | `lessons/heuristic/pages/search-strategies.md` | [본문](lessons/heuristic/pages/search-strategies.md) | 문제 공통 탐색 전략으로 독립 유지. SA 확률과 현재해/최선해 구분 타당. 국소 최적 그림은 후순위. |
| 18 | `lessons/heuristic/pages/placement-and-repair.md` | [본문](lessons/heuristic/pages/placement-and-repair.md) | 배치 모델과 공개 API 되돌림 불가 경계를 명시해 독립 유지. 비트마스크 전제와 repair 연결 타당. |
| 19 | `lessons/heuristic/pages/aircontech-beam-search.md` | [본문](lessons/heuristic/pages/aircontech-beam-search.md) | 일정 Beam 예제는 배치/경로와 상태가 달라 독립 유지. 기존 Beam 그림 활용. |
| 20 | `lessons/modular-arithmetic/lesson.md` | [본문](lessons/modular-arithmetic/lesson.md) | mod>0, 지수 비음수, mod=1 처리와 곱셈 범위 타당. |
| 21 | `lessons/dynamic-programming/lesson.md` | [본문](lessons/dynamic-programming/lesson.md) | 통합 뒤 상태 소개 중복 및 아래 세 문제라는 낡은 개수 표현 수정 필요. 0/1 배낭 역순 갱신 시각화 우선. |
| 22 | `lessons/tsp-hamiltonian/lesson.md` | [본문](lessons/tsp-hamiltonian/lesson.md) | 완전탐색에서 상태 병합, 복원, 휴리스틱과 근사 보장까지 연결됨. 기존 그림 3개로 설명 충분. 대칭 거리/복귀 조건 분명. |
| 23 | `lessons/union-find/lesson.md` | [본문](lessons/union-find/lesson.md) | 경로압축과 size 대표 조건, 실패한 unite 예시 타당. 기존 그림 3개가 핵심 과정을 포함하므로 신규 추가 후순위. |
| 24 | `lessons/bfs-dfs-grid/lesson.md` | [본문](lessons/bfs-dfs-grid/lesson.md) | 방문 표시와 거리 확정 조건, 다중 시작점/상태 확장을 한 흐름으로 유지. BFS 층별 진행 시각화 우선. |
| 25 | `lessons/graph-tree-basics/lesson.md` | [본문](lessons/graph-tree-basics/lesson.md) | 표현과 루트/부분트리 기본 설명 타당. 지름 페이지는 기본 성질의 직접 연장이므로 본문 통합 후보. MST는 별도 최적화 질문으로 유지. |
| 26 | `lessons/graph-tree-basics/pages/tree-diameter-centroid.md` | [본문](lessons/graph-tree-basics/lesson.md) | 지름과 중심/센트로이드 비교, 부모 방향 크기 계산 타당. 기본 트리 본문과 통합해 구조 설명에서 이어 읽도록 개선 후보. |
| 27 | `lessons/graph-tree-basics/pages/mst-kruskal-prim.md` | [본문](lessons/graph-tree-basics/pages/mst-kruskal-prim.md) | Kruskal의 DSU 의존과 연결 실패, 최단경로와의 차이를 설명. 독립 학습 질문으로 유지. |
| 28 | `lessons/zero-one-bfs/lesson.md` | [본문](lessons/zero-one-bfs/lesson.md) | 0-1 가중치의 deque 규칙과 재완화 설명 적합. 독립 알고리즘 유지. |
| 29 | `lessons/topological-sort-dag/lesson.md` | [본문](lessons/topological-sort-dag/lesson.md) | Kahn과 작업 DP 연결 자연스러움. 사이클 전제와 동시 실행 가정 명시. |
| 30 | `lessons/dijkstra/lesson.md` | [본문](lessons/dijkstra/lesson.md) | 완화와 낡은 힙 항목 예시, 조기 종료 위치, 다중 간선 복잡도 명시 타당. 시각화는 기존 표에 없는 힙 변화 우선. |
| 31 | `lessons/bellman-ford-negative-cycle/lesson.md` | [본문](lessons/bellman-ford-negative-cycle/lesson.md) | 음수 사이클 도달성과 목표 영향 범위를 구분하고 조기 종료와 INF 전제를 제시. 유지. |
| 32 | `lessons/scc-2sat/lesson.md` | [본문](lessons/scc-2sat/lesson.md) | SCC에서 2-SAT으로 연결된 결합 예제 적합. SCC 번호 방향과 참값 복원 설명 일치. |
| 33 | `lessons/max-flow-min-cut/lesson.md` | [본문](lessons/max-flow-min-cut/lesson.md) | 잔여 간선/최소 절단/매칭 연결 일관. self-loop 역인덱스와 source!=sink 전제 포함. 기본자료 잔여 용량 재배치 그림 우선 후보. |
| 34 | `lessons/matching-cover-duality/lesson.md` | [본문](lessons/matching-cover-duality/lesson.md) | 최대매칭 뒤 cover 복원 전제, 교대 경로 방향과 DAG 경로 덮개 변환 타당. 별도 쌍대성 질문 유지. |
| 35 | `lessons/min-cost-flow/lesson.md` | [본문](lessons/min-cost-flow/lesson.md) | 역비용, requiredFlow 미달, 초기 음수사이클 배제 및 수치 범위 명시. 독립 비용 최적화 흐름 유지. |
| 36 | `lessons/flow-with-lower-bound/lesson.md` | [본문](lessons/flow-with-lower-bound/lesson.md) | demand 부호와 super 간선 방향 일치. 일회성 feasible 사용, 보조 간선 양방향 제거 명시. 유지. |
| 37 | `lessons/general-matching/lesson.md` | [본문](lessons/general-matching/lesson.md) | cardinality와 weighted/maximal 구별 및 base 임시성 설명 유효. 일반 매칭 고유 질문 유지. |
| 38 | `lessons/floyd-warshall/lesson.md` | [본문](lessons/floyd-warshall/lesson.md) | 경유 정점 DP와 복원/음수 사이클 범위 연결 타당. 초기화 순서는 대각 0 뒤 간선 min으로 음수 self-loop 보존. |
| 39 | `lessons/sqrt-decomposition/lesson.md` | [본문](lessons/sqrt-decomposition/lesson.md) | 블록 합과 lazy 변형을 구별하고 기존 블록/질의 그림 충분. 유지. |
| 40 | `lessons/sparse-table-rmq/lesson.md` | [본문](lessons/sparse-table-rmq/lesson.md) | 겹침 허용 연산과 LCP/Euler 규약 명시. min query 범위와 빈 입력 질의 제한 타당. |
| 41 | `lessons/fenwick-tree/lesson.md` | [본문](lessons/fenwick-tree/lesson.md) | lowbit 구간과 query/add 반대 진행, 비음수 lowerBound 전제 타당. 13→12→8 구간 그림 우선. |
| 42 | `lessons/dominator-tree/lesson.md` | [본문](lessons/dominator-tree/lesson.md) | DFS번호/원정점과 idom root 규약 구별, 재build 초기화 타당. 전문 독립 주제 유지. |
| 43 | `lessons/weighted-matching/lesson.md` | [본문](lessons/weighted-matching/lesson.md) | perfect small-N DP와 큰 일반 weighted blossom 제공 범위 정직. 목적식과 음수 가중치 구분 적합. |
| 44 | `lessons/directed-mst/lesson.md` | [본문](lessons/directed-mst/lesson.md) | 수축 비용과 불가능 판정 코드 타당. 최단거리 트리를 루트에서 나가는 간선만 본다고 한 도입 문장은 부정확하므로 수정 필요. |
| 45 | `lessons/segment-tree/lesson.md` | [본문](lessons/segment-tree/lesson.md) | 기본과 lazy 코드 통합 흐름 적합. lazy가 현재 합에 아직 미반영인 규약을 그림에 그대로 반영 필요. |
| 46 | `lessons/versioned-data-structures/lesson.md` | [본문](lessons/versioned-data-structures/lesson.md) | 버전 모델 구분 허브 유지. Practice Set 별도 필요성은 실습 본문 확인 뒤 판단. |
| 47 | `lessons/versioned-data-structures/pages/persistent-segment-tree.md` | [본문](lessons/versioned-data-structures/pages/persistent-segment-tree.md) | 합 버전과 prefix kth가 경로 복사로 연결됨. null node와 압축/질의 전제 타당. |
| 48 | `lessons/versioned-data-structures/pages/persistent-lazy-segment-tree.md` | [본문](lessons/versioned-data-structures/pages/persistent-lazy-segment-tree.md) | 과거 노드 보존과 query carry 구현 일치. 점 버전과 다른 핵심 불변식이라 하위 페이지 유지. |
| 49 | `lessons/versioned-data-structures/pages/persistent-union-find.md` | [본문](lessons/versioned-data-structures/pages/persistent-union-find.md) | union-only 시간과 분기 제한 명시. 실패 union도 시간 증가 규약 코드 일치. 유지. |
| 50 | `lessons/versioned-data-structures/pages/persistent-queue-stack.md` | [본문](lessons/versioned-data-structures/pages/persistent-queue-stack.md) | 큐 모델 뒤 작은 예시가 실제로 스택 top/pop 예시라 혼동. 예시를 스택 설명 바로 뒤로 옮기고 제목에 스택 명시 필요. |
| 51 | `lessons/versioned-data-structures/pages/practice-set.md` | [본문](lessons/versioned-data-structures/pages/persistent-segment-tree.md) | 허브 전반 실습을 표방하지만 실제 내용은 prefix kth뿐. Persistent Segment Tree 본문에 통합하고 기존 짧은 중복 예시 대체. |
| 52 | `lessons/hungarian-algorithm/lesson.md` | [본문](lessons/hungarian-algorithm/lesson.md) | 손풀이, potential 구현과 실제 배정 사례 연결 완결. 기존 그림 충분. 행렬목표/실제 운행비 분리 명시. |
| 53 | `lessons/wavelet-tree/lesson.md` | [본문](lessons/wavelet-tree/lesson.md) | 값/위치 재배치와 rank 변환, 원본변경 및 복사금지 명시. static order질의 독립 유지. |
| 54 | `lessons/wavelet-matrix/lesson.md` | [본문](lessons/wavelet-matrix/lesson.md) | 31층 실제 저장량과 경계 countLess longlong 처리 적합. Tree와 레이아웃 차이 있어 독립 유지. |
| 55 | `lessons/succinct-bitvector/lesson.md` | [본문](lessons/succinct-bitvector/lesson.md) | selectOne이 이미 본체에 있는데 다음 멤버를 추가하라는 잔재 문장과 중복 설명 수정. 코드 selectOne 들여쓰기도 정리 필요. |
| 56 | `lessons/tree-advanced/lesson.md` | [본문](lessons/tree-advanced/lesson.md) | Euler/LCA/HLD/centroid 집계가 트리 분할 관점으로 연결. LOG 설명의 20보다18이면 표현 다듬기. HLD 경로→배열 그림 우선 후보. |
| 57 | `lessons/avl-splay-tree/lesson.md` | [본문](lessons/avl-splay-tree/lesson.md) | 회전 코드와 보장 비교 완결. Splay 접근 실패 시에는 찾은 x가 없으므로 find(x)후 root 문장 성공 탐색으로 한정 필요. |
| 58 | `lessons/link-cut-tree/lesson.md` | [본문](lessons/link-cut-tree/lesson.md) | LCT 경로노출과 직접 간선 cut 조건, null0 및 연결 전제 타당. 추적 하위제목 3.1~3.3은 상위 번호 없는 잔재라 제거. |
| 59 | `lessons/treap/lesson.md` | [본문](lessons/treap/lesson.md) | BST 설명과 split/merge/순위 구현 연결 자연스러움. unique key, 소유권, 난수 독립 조건 명시. |
| 60 | `lessons/string-matching-kmp-z/lesson.md` | [본문](lessons/string-matching-kmp-z/lesson.md) | KMP 실패/겹침, Z 구분자, hash 충돌 구분 적합. 실패 시 이미 일치한 접미사 재사용 그림 우선 후보. |
| 61 | `lessons/trie-aho-corasick/lesson.md` | [본문](lessons/trie-aho-corasick/lesson.md) | Trie에서 실패링크로 이어지는 자연스러운 구성. build 일회/빈패턴 금지와 출력 집계 경계 타당. |
| 62 | `lessons/suffix-periodicity-structures/lesson.md` | [본문](lessons/suffix-periodicity-structures/lesson.md) | SAM 응용과 주기질의/실습 분리 여부를 하위 본문에서 재판단. 선택 허브 자체는 유지. |
| 63 | `lessons/suffix-periodicity-structures/pages/suffix-array-lcp.md` | [본문](lessons/suffix-periodicity-structures/pages/suffix-array-lcp.md) | 정렬에서 검색/개수/반복 응용까지 합쳐져 완결. LCP 인덱스와 겹침 없는 반복 그룹 조건 적합. |
| 64 | `lessons/suffix-periodicity-structures/pages/suffix-automaton.md` | [본문](lessons/suffix-periodicity-structures/pages/suffix-automaton.md) | 구축과 상태 공식/등장횟수/LCS 연결. 응용 페이지와 중복 정도 확인 필요. clone 초기 count 설명 적합. |
| 65 | `lessons/suffix-periodicity-structures/pages/suffix-automaton-applications.md` | [본문](lessons/suffix-periodicity-structures/pages/suffix-automaton.md) | 기본 SAM의 구축/occurrence를 크게 반복. 기본 SAM에 합쳐 구축 예제 하나와 집계/kth 확장으로 정리 필요. 상태 최대2N-1은 N>=2 조건 누락 보완. |
| 66 | `lessons/suffix-periodicity-structures/pages/generalized-suffix-automaton.md` | [본문](lessons/suffix-periodicity-structures/pages/generalized-suffix-automaton.md) | 제목은 generalized 구축이나 실제 코드는 다문자열 LCS. 독립 질문은 유효하므로 제목을 여러 문자열의 SAM 질의로 맞추고 일반화 모델과 구현 범위 분명히. |
| 67 | `lessons/suffix-periodicity-structures/pages/suffix-tree-ukkonen.md` | [본문](lessons/suffix-periodicity-structures/pages/suffix-tree-ukkonen.md) | 구축 추적과 실제 코드 연결 완결. offline 최종문자열 전제 명시. 기존 통합 유지. |
| 68 | `lessons/suffix-periodicity-structures/pages/runs-periodicity.md` | [본문](lessons/suffix-periodicity-structures/pages/runs-periodicity.md) | 일반 주기/완전 반복 구분 타당. 구간 질의 페이지가 같은 period검증 연장이므로 합칠 후보. |
| 69 | `lessons/suffix-periodicity-structures/pages/border-automaton.md` | [본문](lessons/suffix-periodicity-structures/pages/border-automaton.md) | 상태m에서 pi로 돌아간다는 설명과 go[m]이 처리하는 코드 차이를 연결 문장으로 명시 필요. |
| 70 | `lessons/suffix-periodicity-structures/pages/string-period-query-applications.md` | [본문](lessons/suffix-periodicity-structures/pages/runs-periodicity.md) | 구간 주기 식과 비단조성 예시 타당. Runs/Periodicity에 통합해 전체→구간 흐름으로 구성. |
| 71 | `lessons/suffix-periodicity-structures/pages/practice-set.md` | [본문](lessons/suffix-periodicity-structures/lesson.md) | SA/SAM 두 표현 대조가 독립 연습 질문이지만 본 허브에 실습으로 합쳐도 자연스러움. 한 줄 단계표는 불필요해 제거; 허브 통합 후보. |
| 72 | `lessons/palindrome-structures/lesson.md` | [본문](lessons/palindrome-structures/lesson.md) | Suffix and Palindrome Applications 링크가 SAM응용이며 회문 응용 없음. 오해 유발 항목 제거. |
| 73 | `lessons/palindrome-structures/pages/palindromic-tree.md` | [본문](lessons/palindrome-structures/pages/palindromic-tree.md) | 상단은 생성순 길이 비단조라고 바로잡았으나 하단은 길이 대체로 증가를 근거로 누적 설명. suffix link가 먼저 생긴 노드로 향한다는 근거로 통일. |
| 74 | `lessons/palindrome-structures/pages/palindrome-query-structures.md` | [본문](lessons/palindrome-structures/pages/palindrome-query-structures.md) | 판정 질문 독립 유지. Manacher 계산 구현 없이 radius만 등장하므로 기존 구현 위치 검색 후 연결/보충 필요. |
| 75 | `lessons/palindrome-structures/pages/palindrome-range-dp.md` | [본문](lessons/palindrome-structures/pages/palindrome-range-dp.md) | 판정과 분할 DP 차이, 메모리만 감소 설명 타당. 독립 DP 주제 유지. |
| 76 | `lessons/palindrome-structures/pages/practice-set.md` | [본문](lessons/palindrome-structures/pages/palindromic-tree.md) | Eertree 추적만 다뤄 해당 본문 통합. 없는 distinctCount() 호출을 tree.tree.size()-2로 수정 필요. |
| 77 | `lessons/lyndon-factorization/lesson.md` | [본문](lessons/lyndon-factorization/lesson.md) | Duval분해와 최소회전 코드 및 빈문자열 규약 타당. 독립 표현 질문 유지. |
| 78 | `lessons/geometry-ccw-segment-intersection/lesson.md` | [본문](lessons/geometry-ccw-segment-intersection/lesson.md) | CCW/교차/hull 공통정의 일관. 범위10^9에서 곱차/거리8e18 이내. 외적 방향/collinear 그림 우선 후보. |
| 79 | `lessons/rotating-calipers/lesson.md` | [본문](lessons/rotating-calipers/lesson.md) | 기존 지름과 폭 통합 완결. CCW hull과 동률 정책, 거리제곱 및 최소폭 정의 타당. |
| 80 | `lessons/sweep-line-geometry/lesson.md` | [본문](lessons/sweep-line-geometry/lesson.md) | union면적 이벤트와 실제좌표 길이, 같은x 일괄처리 타당. 독립 sweep 유지. |
| 81 | `lessons/closest-pair-sweep/lesson.md` | [본문](lessons/closest-pair-sweep/lesson.md) | limit은 sqrtl+1인데 설명은2의거듭제곱 상한이라고 함. 실제 구현과 일치하게 수정 필요. |
| 82 | `lessons/line-arrangement/lesson.md` | [본문](lessons/line-arrangement/lesson.md) | 중복직선 제거와 유리수 교점별 k+1 영역 계산 타당. 정확한 수치 범위 전제 명시. |
| 83 | `lessons/voronoi-delaunay/lesson.md` | [본문](lessons/voronoi-delaunay/lesson.md) | incircle은 방향 보정해 양방향 모두 내부 양수인데 반시계만 설명. 일반위치에서 Voronoi dual 삼각형 관계임을 명시 필요. |
| 84 | `lessons/half-plane-intersection/lesson.md` | [본문](lessons/half-plane-intersection/lesson.md) | 유한영역 clipping 제공범위 정직. NlogN HPI와 구별하고 퇴화 검산 제시. 유지. |
| 85 | `lessons/gcd-extended-euclid-crt/lesson.md` | [본문](lessons/gcd-extended-euclid-crt/lesson.md) | CRT 양수mod/LCM범위, 역원 및 SPF 범위 명시. 연결 흐름 타당. |
| 86 | `lessons/combinatorics-ncr/lesson.md` | [본문](lessons/combinatorics-ncr/lesson.md) | 소수/maxN<p/Lucas 준비 범위 명시. 순열/조합/포함배제 연결 유지. |
| 87 | `lessons/matrix-exponentiation/lesson.md` | [본문](lessons/matrix-exponentiation/lesson.md) | 행렬 차원과mod1 처리, walk와경로 구분 적합. 마지막 min-plus 최적화는 일반행렬의 대안으로 오해 가능하므로 목적에 맞는별도연산으로 문장 수정 후보. |
| 88 | `lessons/polynomial-recurrence-algorithms/lesson.md` | [본문](lessons/polynomial-recurrence-algorithms/lesson.md) | 계수열 트랙별 입력모델 구분 적합. 실습 페이지 실제 범위 확인 뒤 통합 판단. |
| 89 | `lessons/polynomial-recurrence-algorithms/pages/fft-ntt.md` | [본문](lessons/polynomial-recurrence-algorithms/pages/fft-ntt.md) | NTT padding/계수/CRT복원 상한 타당. 독립 합성곱 질문 유지. |
| 90 | `lessons/polynomial-recurrence-algorithms/pages/formal-power-series.md` | [본문](lessons/polynomial-recurrence-algorithms/pages/formal-power-series.md) | 통합 코드가 미분/적분뿐이라는 소개와 아래코드 역원 예시라는 잔재 수정. 중복 include/using 제거. Newton/log/exp 흐름 유지. |
| 91 | `lessons/polynomial-recurrence-algorithms/pages/multipoint-evaluation.md` | [본문](lessons/polynomial-recurrence-algorithms/pages/multipoint-evaluation.md) | remainder tree 추적과 제공범위 분명. 평가라는 독립 질문 유지. |
| 92 | `lessons/polynomial-recurrence-algorithms/pages/polynomial-interpolation.md` | [본문](lessons/polynomial-recurrence-algorithms/pages/polynomial-interpolation.md) | 보간 차수 전제, 모듈러 좌표 정규화,복원복잡도 적합. 유지. |
| 93 | `lessons/polynomial-recurrence-algorithms/pages/generating-function-modeling.md` | [본문](lessons/polynomial-recurrence-algorithms/pages/generating-function-modeling.md) | Truncated Polynomial 구현 소개는 곱셈이라지만 실제로 무한 선택 계수 생성. 제목/소개를 코드 역할에 맞춤. 함수 n이 아니라 limit이라는 인자명도 수정. |
| 94 | `lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-kitamasa.md` | [본문](lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-kitamasa.md) | Kitamasa reduction방향과K1 조건, BM field 경계 적합. 독립 nth질문 유지. |
| 95 | `lessons/polynomial-recurrence-algorithms/pages/bostan-mori.md` | [본문](lessons/polynomial-recurrence-algorithms/pages/bostan-mori.md) | 짝홀 추출과 q0전제 일치. naive복잡도와NTT분리 적합. |
| 96 | `lessons/polynomial-recurrence-algorithms/pages/berlekamp-massey.md` | [본문](lessons/polynomial-recurrence-algorithms/pages/berlekamp-massey.md) | BM→Kitamasa 예시의 nthByRecurrence는 실제 함수명이 아님. nthLinearRecurrence로 수정. 차수상한 증명/holdout 역할 표현 중복 정리. |
| 97 | `lessons/polynomial-recurrence-algorithms/pages/practice-set.md` | [본문](lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-kitamasa.md) | Kitamasa만 다루는 실습은 해당 본문으로 통합. 허브 전체 실습인듯 분리한 경계 불필요. |
| 98 | `lessons/probability-expected-value/lesson.md` | [본문](lessons/probability-expected-value/lesson.md) | 확률/기대값 단위와 유한성 조건, 선형성 설명 타당. 유지. |
| 99 | `lessons/game-theory-grundy/lesson.md` | [본문](lessons/game-theory-grundy/lesson.md) | DAG normalplay 전제, mex공간과 xor 독립조건 적합. 유지. |
| 100 | `lessons/minimax-alpha-beta/lesson.md` | [본문](lessons/minimax-alpha-beta/lesson.md) | 작은 트리로 pruning과 상한캐시 설명 완결. 기존 text트리를 시각화 후보로 판단. |
| 101 | `lessons/probabilistic-decision-ai/lesson.md` | [본문](lessons/probabilistic-decision-ai/lesson.md) | 자기 허브로 연결된 Exact Model vs Sampling 항목은 실제 본문 앵커로 변경 필요. MDP 분리 4개는 내용 확인 후 통합 판단. |
| 102 | `lessons/probabilistic-decision-ai/pages/feedback-model-boundary.md` | [본문](lessons/probabilistic-decision-ai/lesson.md) | 모델 축과 관측 누출 반례 유용하지만 허브 선택 안내와 겹침. 허브 본문에 통합 후보. |
| 103 | `lessons/probabilistic-decision-ai/pages/finite-horizon-mdp.md` | [본문](lessons/probabilistic-decision-ai/pages/finite-horizon-mdp.md) | 턴 DP는 종료/정책 모델 독립성이 있으나 할인/정책평가 짧은페이지와 공통 Bellman 비교 본문으로 통합 후보. |
| 104 | `lessons/probabilistic-decision-ai/pages/discounted-value-iteration.md` | [본문](lessons/probabilistic-decision-ai/pages/finite-horizon-mdp.md) | finite와discount를 비교하며 같은 설명 반복. MDP 본문에 finite/discount/policy를 연결하고 모델 조건은 절별 유지. -1e100 sentinel은 유한보상만으로 안전하지 않아 -infinity로 교체. |
| 105 | `lessons/probabilistic-decision-ai/pages/policy-evaluation-and-improvement.md` | [본문](lessons/probabilistic-decision-ai/pages/finite-horizon-mdp.md) | 정책 평가/개선은 할인MDP 바로 다음 단계이며독립 내용짧음. MDP 통합. 실수Gaussian을 정확하게 푼다는 문구는 수치 해법으로 수정. |
| 106 | `lessons/probabilistic-decision-ai/pages/stochastic-shortest-path.md` | [본문](lessons/probabilistic-decision-ai/pages/stochastic-shortest-path.md) | proper조건 반례와 SSP 경계 적절해 독립 유지. best1e100은 비용상한 없으므로 infinity로 교체. |
| 107 | `lessons/probabilistic-decision-ai/pages/monte-carlo-tree-search.md` | [본문](lessons/probabilistic-decision-ai/pages/monte-carlo-tree-search.md) | 노드 관점/보상반전 전제와근사성 명확. 독립 탐색 유지. |
| 108 | `lessons/probabilistic-decision-ai/pages/imperfect-information-search.md` | [본문](lessons/probabilistic-decision-ai/pages/imperfect-information-search.md) | 삭제된 예제의 isConsistentWithObservation 언급 잔재 제거. 정보집합 질문은독립 유지. |
| 109 | `lessons/probabilistic-decision-ai/pages/pomdp.md` | [본문](lessons/probabilistic-decision-ai/pages/pomdp.md) | Bayes와영확률 posterior 처리 타당. belief근사와exact구분. 별도 유지. |
| 110 | `lessons/probabilistic-decision-ai/pages/point-based-value-iteration.md` | [본문](lessons/probabilistic-decision-ai/pages/point-based-value-iteration.md) | Alpha 선택 구현이라고 했으나 코드없음. 선택 원리라는 제목/소개로 수정. 대표 belief backup 주제 유지. |
| 111 | `lessons/probabilistic-decision-ai/pages/pomcp.md` | [본문](lessons/probabilistic-decision-ai/pages/pomcp.md) | UCT skeleton 코드가 없으므로 골격 소개 잔재 수정. history 통계와 root샘플링 경계 유효. |
| 112 | `lessons/probabilistic-decision-ai/pages/bayesian-bandits.md` | [본문](lessons/probabilistic-decision-ai/pages/bayesian-bandits.md) | Beta posterior/quantile과근사식 차이 명시. 독립 partial feedback 모델 유지. |
| 113 | `lessons/probabilistic-decision-ai/pages/online-planning-evaluation.md` | [본문](lessons/probabilistic-decision-ai/pages/online-planning-evaluation.md) | pairedseed와 외생사건 차이,holdout/시간검증 구분 적합. 학습용독립평가 질문 유지. |
| 114 | `lessons/probabilistic-decision-ai/pages/practice-set.md` | [본문](lessons/probabilistic-decision-ai/pages/finite-horizon-mdp.md) | finite MDP 하나의 추적/실습이므로 MDP본문으로 통합. 근사평가 전체라는 도입 제거. |
| 115 | `lessons/offline-time-axis-techniques/lesson.md` | [본문](lessons/offline-time-axis-techniques/lesson.md) | 기법 선택 허브 유지. 중복 Mo 선택표 행 두 개 합칠 수 있음. |
| 116 | `lessons/offline-time-axis-techniques/pages/offline-queries.md` | [본문](lessons/offline-time-axis-techniques/pages/offline-queries.md) | PBS의 sweep공유와sentinel 조건 타당. 독립 판정 재사용 질문 유지. |
| 117 | `lessons/offline-time-axis-techniques/pages/offline-range-query-techniques.md` | [본문](lessons/offline-time-axis-techniques/pages/offline-range-query-techniques.md) | Mo 상태 역연산과sweep 비교 적합. 시간표의 수정Mo는 동일규모 조건 본문과 맞춰 명시. |
| 118 | `lessons/offline-time-axis-techniques/pages/rollback-techniques.md` | [본문](lessons/offline-time-axis-techniques/pages/rollback-techniques.md) | snapshot및dummy marker 규약 타당. 일반rollback패턴은 연결성 외에도쓰여 독립 유지. |
| 119 | `lessons/offline-time-axis-techniques/pages/dynamic-connectivity.md` | [본문](lessons/offline-time-axis-techniques/pages/dynamic-connectivity.md) | DSU 구현이 아래있다는 잔재를 앞서링크한 공유정의로 수정. 동적forest만으로 일반연결성 해결하지못한다는 도입도 본문과통일. |
| 120 | `lessons/offline-time-axis-techniques/pages/retroactive-data-structures.md` | [본문](lessons/offline-time-axis-techniques/pages/retroactive-data-structures.md) | 두 시간축/deleteMin 반례 독립 모델 구분유효. 유지. |
| 121 | `lessons/offline-time-axis-techniques/pages/practice-set.md` | [본문](lessons/offline-time-axis-techniques/pages/dynamic-connectivity.md) | 동적연결성 실습뿐이므로 해당 본문으로 통합. 한줄권장순서표 제거. |
| 122 | `lessons/testing-and-stress/lesson.md` | [본문](lessons/testing-and-stress/lesson.md) | 독립 기준구현/차분/상태복원과점수평가 구별. 실전검증 흐름 완결. |
| 123 | `lessons/proof-and-invariants/lesson.md` | [본문](lessons/proof-and-invariants/lesson.md) | 이분불변식/그리디교환/DP중복배제 독립 설명 충분. 유지. |
| 124 | `lessons/divide-and-conquer-dp-optimization/lesson.md` | [본문](lessons/divide-and-conquer-dp-optimization/lesson.md) | 상단 g층computeLayer(g,N,g-1,..)인데 본문 호출은1부터인 잔재 수정. cost[j][i]소개를 cost[j+1][i]로 통일. |
| 125 | `lessons/knuth-optimization/lesson.md` | [본문](lessons/knuth-optimization/lesson.md) | 비음수파일비용 조건/동률/증명 일관. 유지. |
| 126 | `lessons/monge-smawk/lesson.md` | [본문](lessons/monge-smawk/lesson.md) | row minima가 오른쪽으로 갈수록이라는 표현을 아래 행으로갈수록으로 수정. 위strict부등식 지시어도 아래로. 코드 조건/동률은 일치. |
| 127 | `lessons/parametric-optimization/lesson.md` | [본문](lessons/parametric-optimization/lesson.md) | 실습 최대평균 한개는fractional로 연결. parameter유형 선택 허브유지. |
| 128 | `lessons/parametric-optimization/pages/exact-k-alien-optimization.md` | [본문](lessons/parametric-optimization/pages/general-lagrangian-relaxation.md) | count단조성만으로 exact복원 불가 반례와tie조건 타당. 일반Lagrangian과공통 설명많아 같은 본문에 일반→exactK로 통합 후보. |
| 129 | `lessons/parametric-optimization/pages/fractional-objectives.md` | [본문](lessons/parametric-optimization/pages/fractional-objectives.md) | 양수분모와길이제약 판정 타당. 실습을 이어붙여 완결. |
| 130 | `lessons/parametric-optimization/pages/general-lagrangian-relaxation.md` | [본문](lessons/parametric-optimization/pages/general-lagrangian-relaxation.md) | 정확K와dual상계/불평등 완화가 같은 흐름. ExactK 본문과통합해복원조건 반복 제거. |
| 131 | `lessons/parametric-optimization/pages/practice-set.md` | [본문](lessons/parametric-optimization/pages/fractional-objectives.md) | 최대평균 실습은fractional본문으로 통합. 허브전체 목록이라는 도입 제거. |
| 132 | `lessons/dynamic-segment-tree/lesson.md` | [본문](lessons/dynamic-segment-tree/lesson.md) | query도노드생성해메모리 포함설명 타당. 독립 sparse범위문제 유지. |
| 133 | `lessons/linear-basis-xor/lesson.md` | [본문](lessons/linear-basis-xor/lesson.md) | 정규화kth/rank64 및walk조건 구분 타당. 기존통합 유지. |
| 134 | `lessons/convex-dp-optimization/lesson.md` | [본문](lessons/convex-dp-optimization/lesson.md) | 식과단조성선택 허브 적합. 실습이CHT뿐이면 해당본문 통합. |
| 135 | `lessons/convex-dp-optimization/pages/convex-hull-trick-li-chao.md` | [본문](lessons/convex-dp-optimization/pages/convex-hull-trick-li-chao.md) | 기존CHT통합 코드와기울기조건 정확. 실제실습 아래따로있으면 결합. |
| 136 | `lessons/convex-dp-optimization/pages/slope-trick.md` | [본문](lessons/convex-dp-optimization/pages/slope-trick.md) | hinge/shift코드와적용범위 명시. 일반볼록함수와구분 유지. |
| 137 | `lessons/convex-dp-optimization/pages/min-plus-convolution.md` | [본문](lessons/convex-dp-optimization/pages/min-plus-convolution.md) | naive/단조반례/볼록차분merge 연결 완결. 유지. |
| 138 | `lessons/convex-dp-optimization/pages/kinetic-hull.md` | [본문](lessons/convex-dp-optimization/pages/kinetic-hull.md) | 정적envelope와kinetic범위/certificate불완전성 구별. 독립 유지. |
| 139 | `lessons/convex-dp-optimization/pages/fully-dynamic-cht.md` | [본문](lessons/convex-dp-optimization/pages/fully-dynamic-cht.md) | 삭제로 버린선부활 반례/rollback 계약과block재구축 타당. 독립 모델 유지. |
| 140 | `lessons/convex-dp-optimization/pages/practice-set.md` | [본문](lessons/convex-dp-optimization/pages/convex-hull-trick-li-chao.md) | CHT본문에 LiChao실습으로 통합. DP 숫자trace335정확. |
| 141 | `lessons/graph-cut-structures/lesson.md` | [본문](lessons/graph-cut-structures/lesson.md) | cut값/partition/family와가중조건 구분 적합. 실습범위 확인후배치. |
| 142 | `lessons/graph-cut-structures/pages/global-min-cut.md` | [본문](lessons/graph-cut-structures/pages/global-min-cut.md) | global/고정root N-1계산/partition복원 구분 타당. 독립 유지. |
| 143 | `lessons/graph-cut-structures/pages/randomized-min-cut.md` | [본문](lessons/graph-cut-structures/pages/randomized-min-cut.md) | 균등간선instance 수축과비연결처리, 반복실패확률 적합. 독립 확률알고리즘 유지. |
| 144 | `lessons/graph-cut-structures/pages/gomory-hu-tree.md` | [본문](lessons/graph-cut-structures/pages/gomory-hu-tree.md) | parent추적과 oracle source-side/초기화 계약 완결. 기존통합 유지. |
| 145 | `lessons/graph-cut-structures/pages/cut-sparsification.md` | [본문](lessons/graph-cut-structures/pages/cut-sparsification.md) | certificate조건 타당. forest비용표에서 DSU초기화 O(N) 누락: O(k(N+M alpha(N)))로 수정. |
| 146 | `lessons/graph-cut-structures/pages/cactus-representation.md` | [본문](lessons/graph-cut-structures/pages/cactus-representation.md) | 입력cactus와cutfamily구축 구분타당. 양의globalcut전제 반복과mapping명시 유지. |
| 147 | `lessons/graph-cut-structures/pages/practice-set.md` | [본문](lessons/graph-cut-structures/pages/global-min-cut.md) | StoerWagner추적실습은globalmincut본문에통합; 두추가실험은허브간단연습으로 이동. |
| 148 | `lessons/euler-tour-tree/lesson.md` | [본문](lessons/euler-tour-tree/lesson.md) | marker중복방지/cut arc핸들 설명 완결. 독립component자료구조 유지. |
| 149 | `lessons/mobius-inversion/lesson.md` | [본문](lessons/mobius-inversion/lesson.md) | 마지막 좌표압축 권장이 약수보존불가 전제와충돌. 실제약수 key를관리하는희소사전/약수열거로 구체화. |
| 150 | `lessons/convex-cost-flow/lesson.md` | [본문](lessons/convex-cost-flow/lesson.md) | convex조건검사/비볼록반례 완결. concave를음수cycle만검토하면되는듯한 문장 수정. |
| 151 | `lessons/dynamic-network-optimization/lesson.md` | [본문](lessons/dynamic-network-optimization/lesson.md) | 허브 모델경계 유효. 실습은flow로이동하고block MST설명중복정리. |
| 152 | `lessons/dynamic-network-optimization/pages/dynamic-flow.md` | [본문](lessons/dynamic-network-optimization/pages/dynamic-flow.md) | capacity증가feasibility와시간확장모델 구분적합. 실습통합. |
| 153 | `lessons/dynamic-network-optimization/pages/dynamic-mst.md` | [본문](lessons/dynamic-network-optimization/pages/dynamic-mst.md) | block고정간선은미래변경전체제외라는 상단조건을 하단단계에도반영. baseline복잡도DSU초기화N 포함. |
| 154 | `lessons/dynamic-network-optimization/pages/practice-set.md` | [본문](lessons/dynamic-network-optimization/pages/dynamic-flow.md) | flow만의실습을dynamic-flow로통합. capacity감소검증은허용범위밖반례임을유지. |
| 155 | `lessons/dirichlet-convolution/lesson.md` | [본문](lessons/dirichlet-convolution/lesson.md) | 약수 합성 및 역변환, 곱셈적 함수 연결과 코드 경계 확인. 별도 학습 모델로 유지. |
| 156 | `lessons/minkowski-sum/lesson.md` | [본문](lessons/minkowski-sum/lesson.md) | 엄격한 CCW 다각형과 좌표 제한 아래 변 각도 병합, 정규화 및 퇴화 조건 확인. 유지. |
| 157 | `lessons/multiplicative-functions/lesson.md` | [본문](lessons/multiplicative-functions/lesson.md) | 소수 거듭제곱 선형 체와 tau 갱신 확인. int 배열 6개이므로 N=1e7 메모리 280MB를 240MB와 primes로 수정 필요. |
| 158 | `lessons/summatory-number-theory/lesson.md` | [본문](lessons/summatory-number-theory/lesson.md) | 몫 구간 분할과 마지막 구간 오버플로 방지, summatory phi 재귀 조건 확인. 유지. |
| 159 | `lessons/shape-distance-modeling/lesson.md` | [본문](lessons/shape-distance-modeling/lesson.md) | 거리 baseline 및 Minkowski 변환 확인. SAT overlap을 포함 투영의 끝점 이동량으로 수정. |
| 160 | `lessons/circle-geometry/lesson.md` | [본문](lessons/circle-geometry/lesson.md) | 원-직선 projection과 퇴화 조건 확인. 유지. |
| 161 | `lessons/circle-arrangement/lesson.md` | [본문](lessons/circle-arrangement/lesson.md) | 원 합집합 arc, Green 기여식 및 multiplicity 확인. 유지. |
| 162 | `lessons/geometry-robustness-and-duality/lesson.md` | [본문](lessons/geometry-robustness-and-duality/lesson.md) | 기하 선택 허브 유지. 실습을 각 알고리즘에 통합. |
| 163 | `lessons/geometry-robustness-and-duality/pages/robust-geometry-predicates.md` | [본문](lessons/geometry-robustness-and-duality/pages/robust-geometry-predicates.md) | 정수 predicate 범위 확인. EPS 근사 동치 비추이성으로 예시 수정. |
| 164 | `lessons/geometry-robustness-and-duality/pages/power-diagram.md` | [본문](lessons/geometry-robustness-and-duality/pages/power-diagram.md) | Power 부등식 검산. 무한 cell 표현 보완. |
| 165 | `lessons/geometry-robustness-and-duality/pages/robust-delaunay.md` | [본문](lessons/geometry-robustness-and-duality/pages/robust-delaunay.md) | Delaunay flip 전제와 예제 확인. 유지. |
| 166 | `lessons/geometry-robustness-and-duality/pages/3d-convex-hull.md` | [본문](lessons/geometry-robustness-and-duality/pages/3d-convex-hull.md) | 3D hull horizon, orientation과 복잡도 확인. 유지. |
| 167 | `lessons/geometry-robustness-and-duality/pages/regular-triangulation.md` | [본문](lessons/geometry-robustness-and-duality/pages/regular-triangulation.md) | weighted lifting 검산. 대응표 일반 위치 조건 보완. |
| 168 | `lessons/geometry-robustness-and-duality/pages/practice-set.md` | [본문](lessons/geometry-robustness-and-duality/pages/robust-geometry-predicates.md) | 교차 실습은 predicate로, power 실습은 power 본문으로 통합. |
| 169 | `lessons/black-box-linear-algebra/lesson.md` | [본문](lessons/black-box-linear-algebra/lesson.md) | Krylov matvec와 투영 최소 다항식 조건 확인. 유지. |
| 170 | `lessons/game-theory-applications/lesson.md` | [본문](lessons/game-theory-applications/lesson.md) | 게임 모델 분류 유지. MDP 식에 horizon 조건 명시. |
| 171 | `lessons/inversion-geometry/lesson.md` | [본문](lessons/inversion-geometry/lesson.md) | 반전 코드와 원-직선 변환 확인. 방향 보존 conformal 대신 무방향 교차각 보존으로 표현. |
| 172 | `lessons/matroid-algorithms/lesson.md` | [본문](lessons/matroid-algorithms/lesson.md) | Matroid 모델 허브 유지. 실습은 basics로 통합. |
| 173 | `lessons/matroid-algorithms/pages/matroid-basics-and-exchange.md` | [본문](lessons/matroid-algorithms/pages/matroid-basics-and-exchange.md) | 교환 공리 반례와 음수 greedy 조건 확인. 유지. |
| 174 | `lessons/matroid-algorithms/pages/matroid-intersection.md` | [본문](lessons/matroid-algorithms/pages/matroid-intersection.md) | 교환 그래프 방향 확인. 예제는 증가 경로가 없다는 점을 해당 문단에도 명시. |
| 175 | `lessons/matroid-algorithms/pages/matroid-union.md` | [본문](lessons/matroid-algorithms/pages/matroid-union.md) | Union rank 및 partition 용량 곱 코드 확인. 유지. |
| 176 | `lessons/matroid-algorithms/pages/matroid-parity.md` | [본문](lessons/matroid-algorithms/pages/matroid-parity.md) | Parity 모델 확인. 없는 코드를 지칭하는 표현 수정. |
| 177 | `lessons/matroid-algorithms/pages/practice-set.md` | [본문](lessons/matroid-algorithms/pages/matroid-basics-and-exchange.md) | Partition greedy 실습을 basics에 통합. |
| 178 | `lessons/sparse-linear-systems/lesson.md` | [본문](lessons/sparse-linear-systems/lesson.md) | Sparse 모델 유지. 링크한 matvec 복잡도를 초기화 포함 O(N+nnz)로 수정. |
| 179 | `lessons/linear-algebra-applications/lesson.md` | [본문](lessons/linear-algebra-applications/lesson.md) | 선형대수 모델 선택과 두 실제 연습 확인. 유지. |
| 180 | `lessons/online-convex-optimization/lesson.md` | [본문](lessons/online-convex-optimization/lesson.md) | OCO 허브 유지. 실습을 multiplicative weights에 통합. |
| 181 | `lessons/online-convex-optimization/pages/online-decision-and-regret.md` | [본문](lessons/online-convex-optimization/pages/online-decision-and-regret.md) | OGD 구현과 마지막 점 의미 확인. 유지. |
| 182 | `lessons/online-convex-optimization/pages/mirror-descent-and-multiplicative-weights.md` | [본문](lessons/online-convex-optimization/pages/mirror-descent-and-multiplicative-weights.md) | Mirror descent 조건 및 고정 eta 대응 확인. 실습 연결. |
| 183 | `lessons/online-convex-optimization/pages/dual-averaging.md` | [본문](lessons/online-convex-optimization/pages/dual-averaging.md) | Dual averaging 안정화 확인. eta*누적손실도 유한해야 한다는 전제 보완. |
| 184 | `lessons/online-convex-optimization/pages/practice-set.md` | [본문](lessons/online-convex-optimization/pages/mirror-descent-and-multiplicative-weights.md) | Expert loss 실습을 mirror descent 본문에 통합. |
| 185 | `lessons/randomized-determinant/lesson.md` | [본문](lessons/randomized-determinant/lesson.md) | modular determinant 코드와 독립 trial 조건 확인. 유지. |
| 186 | `lessons/matrix-tree-theorem-applications/lesson.md` | [본문](lessons/matrix-tree-theorem-applications/lesson.md) | Matrix-tree 방향 및 contraction 검산. cofactor mod 상한 명시 필요. |
| 187 | `lessons/planar-graph-duality/lesson.md` | [본문](lessons/planar-graph-duality/lesson.md) | Planar 허브 유지. 실습은 face 구성 본문으로 통합. |
| 188 | `lessons/planar-graph-duality/pages/half-edge-and-face-traversal.md` | [본문](lessons/planar-graph-duality/pages/half-edge-and-face-traversal.md) | Half-edge 순회와 dual 구성 확인. 정수 면적 0 표현 명확화. |
| 189 | `lessons/planar-graph-duality/pages/cut-cycle-duality.md` | [본문](lessons/planar-graph-duality/pages/cut-cycle-duality.md) | Cut-cycle 및 공통 face 조건 확인. 유지. |
| 190 | `lessons/planar-graph-duality/pages/practice-set.md` | [본문](lessons/planar-graph-duality/pages/half-edge-and-face-traversal.md) | Face incidence 실습과 두 검산 예시를 face 본문으로 통합. |

### 기본자료 30개 시각화 우선순위

P1은 이번에 보강한 상태 변화·경계·불변식입니다. P2는 도식의 추가 효용이 있지만 본문의 코드·예시로 따라갈 수 있어 다음 보강 대상으로 둡니다. 유지 항목은 이미 있는 도식이 질문을 충분히 설명하거나, 이번 목적에 그림보다 계약·검증 절차가 더 중요한 경우입니다.

| 강의 | 판단 | 근거 |
| --- | --- | --- |
| [복잡도와 입력 크기 감각](lessons/complexity-input-size/lesson.md) | P2 완료 | 입력 2배가 연산 2배는 아닙니다 |
| [실전 C++ 기본기와 공통 코드](lessons/cpp-contest-basics/lesson.md) | 유지 | TC 초기화와 제출 계약은 코드·호출 순서가 핵심. |
| [정렬 알고리즘](lessons/sorting/lesson.md) | 유지 | 기존 Radix 도식 유지. |
| [누적합과 차분 배열](lessons/prefix-sum-difference/lesson.md) | P1 완료 | 2차원 누적합: 겹친 부분을 한 번 복구 |
| [그리디 알고리즘](lessons/greedy/lesson.md) | 유지 | 기존 여섯 예시 그림 유지. |
| [투 포인터와 슬라이딩 윈도우](lessons/two-pointers-sliding-window/lesson.md) | P1 완료 | 투 포인터: 확장과 축소의 역할 |
| [이분 탐색과 파라메트릭 서치](lessons/binary-search/lesson.md) | P1 완료 | 이분 탐색: 첫 번째 참의 경계 |
| [좌표 압축](lessons/coordinate-compression/lesson.md) | P2 완료 | 좌표 압축: 순위와 거리는 다릅니다 |
| [우선순위 큐와 힙](lessons/priority-queue-heap/lesson.md) | P2 완료 | 힙: 트리와 배열은 같은 구조입니다 |
| [Meldable Heap](lessons/meldable-heap/lesson.md) | P2 완료 | Skew Heap: 오른쪽 병합 후 교환 |
| [휴리스틱 알고리즘](lessons/heuristic/lesson.md) | 유지 | 기존 실전 하위 자료와 AIRCONTECH 전이 그림 유지. |
| [동적 계획법](lessons/dynamic-programming/lesson.md) | P1 완료 | 0/1 배낭: 큰 용량부터 갱신 |
| [TSP와 해밀턴 경로](lessons/tsp-hamiltonian/lesson.md) | 유지 | 기존 방문 상태·경로 그림 세 개 유지. |
| [Union-Find 알고리즘](lessons/union-find/lesson.md) | 유지 | 기존 합치기와 경로 압축 그림 세 개 유지. |
| [BFS/DFS와 격자 탐색](lessons/bfs-dfs-grid/lesson.md) | P2 완료 | BFS: 같은 정점을 두 번 넣지 않기 |
| [그래프와 트리 기본 성질](lessons/graph-tree-basics/lesson.md) | P2 완료 | 트리 중심과 센트로이드는 다릅니다 |
| [0-1 BFS](lessons/zero-one-bfs/lesson.md) | P2 완료 | 0-1 BFS: 같은 거리면 앞에 넣습니다 |
| [위상 정렬과 DAG DP](lessons/topological-sort-dag/lesson.md) | P2 완료 | 위상 정렬: 마지막 의존성이 풀릴 때 |
| [Dijkstra 최단거리](lessons/dijkstra/lesson.md) | P1 완료 | Dijkstra: 큐에 남은 낡은 후보 |
| [Bellman-Ford와 음수 사이클](lessons/bellman-ford-negative-cycle/lesson.md) | P2 완료 | 음수 사이클의 영향은 앞으로 퍼집니다 |
| [Floyd-Warshall](lessons/floyd-warshall/lesson.md) | P2 완료 | Floyd-Warshall: 경유지 하나를 허용 |
| [Sqrt Decomposition](lessons/sqrt-decomposition/lesson.md) | 유지 | 기존 블록 분해·lazy 그림 두 개 유지. |
| [Fenwick Tree](lessons/fenwick-tree/lesson.md) | P1 완료 | Fenwick: prefix를 구간으로 분해 |
| [Segment Tree](lessons/segment-tree/lesson.md) | P1 완료 | Lazy: 합과 대기 중인 증가량 |
| [Hungarian Algorithm](lessons/hungarian-algorithm/lesson.md) | 유지 | 기존 potential과 tight edge 그림 두 개 유지. |
| [Treap과 BST 기본](lessons/treap/lesson.md) | P2 완료 | Treap split: 경계에서 연결만 바꿉니다 |
| [Minimax와 Alpha-Beta Pruning](lessons/minimax-alpha-beta/lesson.md) | P1 완료 | Alpha-Beta: 이미 확보한 선택과 비교 |
| [Testing과 Stress Test](lessons/testing-and-stress/lesson.md) | 유지 | 재현 가능한 입력과 실제 비교 코드가 핵심. |
| [Proof와 Invariant](lessons/proof-and-invariants/lesson.md) | 유지 | 증명 질문과 반례를 먼저 읽도록 현재 예시 유지. |
| [Dynamic Segment Tree](lessons/dynamic-segment-tree/lesson.md) | P2 완료 | 동적 세그먼트 트리: 필요한 경로만 |

---

2026-09-09 화면 기반 후속 검토: CHT의 정의·변형·적용 3개 페이지를 한 본문으로 통합하고 기울기 방향 설명을 바로잡았습니다. 현재 공개 97개 강의, 190개 본문입니다. 운영 게시본을 격리 로컬 UI에서 읽었으며 운영 로그인 본문 확인은 아닙니다.


2026-09-09 추가 구조 검토: XOR Basis·Rotating Calipers의 기본/응용 카드와 DP·Segment Tree·TSP의 소개/본문, FPS log·exp와 점화식 추정/구현을 통합했습니다. 공개 강의는 97개, 본문은 192개입니다. Calipers의 점·외적 코드를 공유하도록 바꾼 부분은 지름·폭의 퇴화 입력과 사각형·삼각형 검산으로 확인합니다.


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
| 59 | [lessons/polynomial-recurrence-algorithms/pages/fps-log-exp.md](lessons/polynomial-recurrence-algorithms/pages/formal-power-series.md) | 완료 | 본문·코드 정독. 반영: log/exp 없이 미분·곱셈만 복제한 블록 제거, 실제 log/exp 작은 점화 예제로 대체. |
| 60 | [lessons/polynomial-recurrence-algorithms/pages/multipoint-evaluation.md](lessons/polynomial-recurrence-algorithms/pages/multipoint-evaluation.md) | 완료 | 본문 정독. 반영: chirp-z는 연속 정수가 아닌 등비점, x-xi 부호 반전 실수 단정 삭제, 선형몫 전제. |
| 61 | [lessons/polynomial-recurrence-algorithms/pages/polynomial-interpolation.md](lessons/polynomial-recurrence-algorithms/pages/polynomial-interpolation.md) | 완료 | 반영: 연속점 보간의 입력 범위와 정규화, 전처리 비용, 잘못된 분모 설명을 수정한다. |
| 62 | [lessons/polynomial-recurrence-algorithms/pages/generating-function-modeling.md](lessons/polynomial-recurrence-algorithms/pages/generating-function-modeling.md) | 완료 | 반영: 순서 있는 동전 예시를 고치고 중복 다항식 코드를 줄이며 생성함수의 성립 조건을 명시한다. |
| 63 | [lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-kitamasa.md](lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-kitamasa.md) | 완료 | 반영: Kitamasa 입력 조건과 계수 정규화, 중복 설명을 정리한다. |
| 64 | [lessons/polynomial-recurrence-algorithms/pages/bostan-mori.md](lessons/polynomial-recurrence-algorithms/pages/bostan-mori.md) | 완료 | 반영: Bostan–Mori의 빈 다항식·상수항 조건과 계수 정규화 및 복잡도를 보완한다. |
| 65 | [lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-applications.md](lessons/polynomial-recurrence-algorithms/pages/linear-recurrence-kitamasa.md) | 완료 | 통합 반영: Kitamasa와 겹치는 선택 설명을 합치고 XOR 및 유리 생성함수 설명 오류를 고친다. |
| 66 | [lessons/polynomial-recurrence-algorithms/pages/recurrence-guessing.md](lessons/polynomial-recurrence-algorithms/pages/berlekamp-massey.md) | 완료 | 반영: 임의의 holdout 10항 권장과 affine 수열 오해를 제거하고 증명된 차수 상한과 검증을 구분한다. |
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
| 106 | [lessons/convex-dp-optimization/pages/convex-hull-trick-variants.md](lessons/convex-dp-optimization/pages/convex-hull-trick-li-chao.md) | 완료 | 반영: 최소 deque는 기울기 감소·x 증가로 조건 수정, 128비트 변환을 뺄셈 전으로 이동. 일반 line container 임의 삭제 가능 오해 제거. |
| 107 | [lessons/convex-dp-optimization/pages/cht-dp-applications.md](lessons/convex-dp-optimization/pages/convex-hull-trick-li-chao.md) | 완료 | 통합 반영: 중복 CHT 클래스는 106 재사용. 감소 slope 설명, 잘못된 Li Chao 조건 목록 정리. 제곱 비용 전개·trace 유지. |
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
| 129 | [lessons/linear-basis-applications/lesson.md](lessons/linear-basis-xor/lesson.md) | 완료 | 통합 반영: basis 삽입·표현 가능성 중복은 103 재사용. bit63·rank64·kth 실제 정규화 비용·음수 가중치 greedy 조건 수정. |
| 130 | [lessons/dirichlet-convolution/lesson.md](lessons/dirichlet-convolution/lesson.md) | 완료 | 반영: 입력 배열 길이·산술 범위·multiplicative f(1)=1 전제와 반복 실수 목록 정리. |
| 131 | [lessons/minkowski-sum/lesson.md](lessons/minkowski-sum/lesson.md) | 완료 | 반영: 빈 집합 Minkowski 합을 빈 집합으로 고치고 퇴화 입력 조건·외적 범위·일반 점집합 hull은 정확 합이 아니라 볼록화임을 명시. |
| 132 | [lessons/rotating-calipers-applications/lesson.md](lessons/rotating-calipers/lesson.md) | 완료 | 반영: 최소 폭 코드에 엄격 볼록·중복 없음·좌표 범위 전제, 모호한 접선 의사코드와 반복 조건 목록 축약. |
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
| 190 | [lessons/dynamic-programming/pages/state-and-transition.md](lessons/dynamic-programming/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 격자 양수 크기와 동전 입력 전제 보완. |
| 191 | [lessons/dynamic-programming/pages/knapsack-and-lis.md](lessons/dynamic-programming/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 빈 LIS 역참조, tails 인덱스 설명 수정, 배낭 입력 전제. |
| 192 | [lessons/tsp-hamiltonian/lesson.md](lessons/tsp-hamiltonian/lesson.md) | 완료 | 본문 정독. 경로/사이클 문제 구분과 페이지 안내 유지. |
| 193 | [lessons/tsp-hamiltonian/pages/search-and-dp.md](lessons/tsp-hamiltonian/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: INF 상태의 복귀 비용 합산 차단, 복원 가능 여부 전제. |
| 194 | [lessons/tsp-hamiltonian/pages/heuristic-and-choices.md](lessons/tsp-hamiltonian/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: metric 대칭·비음수 전제 명시. |
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
| 208 | [lessons/segment-tree/pages/basic-range-query.md](lessons/segment-tree/lesson.md) | 완료 | 본문·코드 정독. 비어 있지 않은 배열·항등원 계약 유지. |
| 209 | [lessons/segment-tree/pages/lazy-propagation.md](lessons/segment-tree/lesson.md) | 완료 | 본문·코드 정독. 수정 반영: 구현과 맞지 않는 lazy 저장 의미 수정. |
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
