# h-contest lesson content

This repository is the source of truth for h-contest algorithm lessons.
The public API is generated from or synchronized with this repository.

- Published manifest: https://blog.readiz.com/h-contest-lesson/lessons.json
- API mirror: https://h.readiz.com/api/lessons

## Contributing

Pull requests should edit this repository directly. For details, see [CONTRIBUTING.md](CONTRIBUTING.md).

When adding a new lesson, update these source files:

- `lessons/<lessonId>/lesson.md`
- `lessons.json` (`folderId` included)

Then regenerate derived files:

```bash
python3 scripts/generate_catalog.py
```

Generated files:

- `README.md`
- `index.html`

If the lesson uses images or other local assets, add them under `lessons/<lessonId>/lesson-assets/`.

## Lessons

### 기본기

정렬, 누적합, 이분 탐색처럼 문제 풀이의 출발점이 되는 개념입니다.

- [정렬 알고리즘](lessons/sorting/lesson.md)
- [누적합과 차분 배열](lessons/prefix-sum-difference/lesson.md)
- [이분 탐색과 파라메트릭 서치](lessons/binary-search/lesson.md)

### 전략과 최적화

그리디, 동적 계획법, 휴리스틱처럼 풀이 방향을 정하는 사고 도구입니다.

- [그리디 알고리즘](lessons/greedy/lesson.md)
- [휴리스틱 알고리즘](lessons/heuristic/lesson.md)
- [동적 계획법](lessons/dynamic-programming/lesson.md)
- [TSP와 해밀턴 경로](lessons/tsp-hamiltonian/lesson.md)

### 그래프와 트리

탐색, 최단거리, DAG, 트리 구조를 다루는 그래프 계열 개념입니다.

- [BFS/DFS와 격자 탐색](lessons/bfs-dfs-grid/lesson.md)
- [그래프와 트리 기본 성질](lessons/graph-tree-basics/lesson.md)
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
