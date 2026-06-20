# h-contest lesson content

This repository is the source of truth for h-contest algorithm lessons.
The public API is generated from or synchronized with this repository.

- Published manifest: https://blog.readiz.com/h-contest-lesson/lessons.json
- API mirror: https://h.readiz.com/api/lessons

## Contributing

Pull requests should edit this repository directly. For details, see [CONTRIBUTING.md](CONTRIBUTING.md).

When adding a new lesson, update these source files:

- `lessons/<lessonId>/lesson.md`
- `lessons.json` (`folderId` included, optional `pages` included)

Then regenerate derived files:

```bash
python3 scripts/generate_catalog.py
```

Generated files:

- `README.md`
- `index.html`

If the lesson uses images or other local assets, add them under `lessons/<lessonId>/lesson-assets/`.

## 학습 로드맵

처음 보는 주제라면 아래 순서로 훑는 것을 권장합니다. 이미 익숙한 내용은 건너뛰고, 각 레슨의 `prerequisites`와 `nextLessons` 메타데이터를 참고해 앞뒤 개념을 확인하세요.

1. 입문 1단계: 복잡도 감각, 정렬, 누적합, 이분 탐색, 투 포인터
2. 입문 2단계: BFS/DFS, 그리디, 우선순위 큐, Union-Find, 좌표 압축
3. 중급 1단계: DP, Dijkstra, 위상 정렬, Fenwick Tree, Segment Tree, 모듈러 연산
4. 중급 2단계: 트리 심화, TSP, Treap, 휴리스틱
5. 심화 확장: Flow, 문자열, 수학 심화, 기하, 오프라인 쿼리

## Lessons

### 기본기

정렬, 누적합, 이분 탐색처럼 문제 풀이의 출발점이 되는 개념입니다.

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
- [TSP와 해밀턴 경로](lessons/tsp-hamiltonian/lesson.md)
  - [완전탐색과 비트마스크 DP](lessons/tsp-hamiltonian/pages/search-and-dp.md)
  - [경로 복원과 메모리](lessons/tsp-hamiltonian/pages/restore-and-memory.md)
  - [휴리스틱 개선과 선택 기준](lessons/tsp-hamiltonian/pages/heuristic-and-choices.md)

### 그래프와 트리

탐색, 최단거리, DAG, 트리 구조를 다루는 그래프 계열 개념입니다.

- [BFS/DFS와 격자 탐색](lessons/bfs-dfs-grid/lesson.md)
- [그래프와 트리 기본 성질](lessons/graph-tree-basics/lesson.md)
- [0-1 BFS](lessons/zero-one-bfs/lesson.md)
- [위상 정렬과 DAG DP](lessons/topological-sort-dag/lesson.md)
- [Dijkstra 최단거리](lessons/dijkstra/lesson.md)

### 자료구조

우선순위 큐, Union-Find, 구간 자료구조, 균형 트리 계열을 모았습니다.

- [우선순위 큐와 힙](lessons/priority-queue-heap/lesson.md)
- [Meldable Heap](lessons/meldable-heap/lesson.md)
- [Union-Find 알고리즘](lessons/union-find/lesson.md)
- [Sqrt Decomposition](lessons/sqrt-decomposition/lesson.md)
- [Fenwick Tree](lessons/fenwick-tree/lesson.md)
- [Segment Tree](lessons/segment-tree/lesson.md)
- [트리 심화: 분할 기법](lessons/tree-advanced/lesson.md)
- [BST 계열: AVL, Splay, Treap](lessons/treap/lesson.md)
  - [BST와 회전 기본기](lessons/treap/pages/bst-and-rotation.md)
  - [AVL과 Splay Tree](lessons/treap/pages/balanced-bst.md)
  - [Treap 핵심 연산](lessons/treap/pages/treap-core.md)
  - [순위, 전체 구현, Implicit Treap](lessons/treap/pages/order-statistics-and-implicit.md)

### 수학

모듈러 연산, 정수론, 조합론처럼 경우의 수와 수식 처리에 필요한 개념입니다.

- [모듈러 연산과 빠른 거듭제곱](lessons/modular-arithmetic/lesson.md)
