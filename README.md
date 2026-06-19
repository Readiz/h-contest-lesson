# h-contest lesson content

This repository is the source of truth for h-contest algorithm lessons.
The public API is generated from or synchronized with this repository.

- Published manifest: https://blog.readiz.com/h-contest-lesson/lessons.json
- API mirror: https://h.readiz.com/api/lessons

## Contributing

Pull requests should edit this repository directly. For details, see [CONTRIBUTING.md](CONTRIBUTING.md).

When adding a new lesson, update these source files:

- `lessons/<lessonId>/lesson.md`
- `lessons.json`

Then regenerate derived files:

```bash
python3 scripts/generate_catalog.py
```

Generated files:

- `README.md`
- `index.html`

If the lesson uses images or other local assets, add them under `lessons/<lessonId>/lesson-assets/`.

## Lessons

- [정렬 알고리즘](lessons/sorting/lesson.md)
- [누적합과 차분 배열](lessons/prefix-sum-difference/lesson.md)
- [그리디 알고리즘](lessons/greedy/lesson.md)
- [이분 탐색과 파라메트릭 서치](lessons/binary-search/lesson.md)
- [휴리스틱 알고리즘](lessons/heuristic/lesson.md)
- [동적 계획법](lessons/dynamic-programming/lesson.md)
- [TSP와 해밀턴 경로](lessons/tsp-hamiltonian/lesson.md)
- [Union-Find 알고리즘](lessons/union-find/lesson.md)
- [BFS/DFS와 격자 탐색](lessons/bfs-dfs-grid/lesson.md)
- [그래프와 트리 기본 성질](lessons/graph-tree-basics/lesson.md)
- [Dijkstra 최단거리](lessons/dijkstra/lesson.md)
- [Sqrt Decomposition](lessons/sqrt-decomposition/lesson.md)
- [Fenwick Tree](lessons/fenwick-tree/lesson.md)
- [Segment Tree](lessons/segment-tree/lesson.md)
- [트리 심화: 분할 기법](lessons/tree-advanced/lesson.md)
- [Treap](lessons/treap/lesson.md)
