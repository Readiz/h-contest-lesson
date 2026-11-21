# h-contest heuristic notes

This repository is the source of truth for h-contest heuristic notes. Lesson source lives in `lessons/` and `lessons.json`; `README.md` and `index.html` are generated entry points.

## 탐색

- 전체 카탈로그: [index.html](index.html)
- 사이트 기능 요구사항과 검증 경계: [docs/site-requirements.md](docs/site-requirements.md)
- Published manifest: https://git.readiz.com/h-contest-lesson/lessons.json
- API mirror (h-contest 로그인 필요): https://h.readiz.com/api/lessons
- 실전 풀이 중심 개편 계획과 practice TODO: [ROADMAP.md](ROADMAP.md)
- 기여 절차: [CONTRIBUTING.md](CONTRIBUTING.md)

## 작업 흐름

1. `lessons/<lessonId>/lesson.md`와 필요 시 `lessons/<lessonId>/pages/*.md`를 수정합니다.
2. `lessons.json`에서 metadata, page 목록, 선수/다음/연관 레슨을 맞춥니다.
3. 아래 명령으로 파생 파일과 검증 상태를 맞춥니다.

```bash
python3 scripts/generate_catalog.py
python3 scripts/validate_lessons.py
```

이미지나 보조 자료는 `lessons/<lessonId>/lesson-assets/`에 둡니다.

## 학습 로드맵

h-contest 실전 문제를 처음 풀 때는 아래 경로로 시작합니다. 카탈로그는 필수 선수 레슨이 먼저 오도록 정렬하며, 선택 참고는 관련 레슨으로 구분합니다.

1. [실전 C++ 제출과 검증](lessons/cpp-contest-basics/lesson.md): 제출 계약 → TC 초기화 → ORDERING의 유효한 기준선.
2. [ORDERING 경로 개선](lessons/heuristic/pages/ordering-route-improvement.md): 번호 순서 → nearest neighbor → 2-opt. 매 단계 같은 TC의 비용과 실행 시간을 비교합니다.
3. [Testing과 Stress Test](lessons/testing-and-stress/lesson.md): 전체 비용과 차분값, apply/undo, 같은 seed의 재현성을 대조합니다.
4. [지역 탐색과 SA](lessons/heuristic/pages/search-strategies.md): 작은 지역 최적 반례를 따라가고, 실행 가능한 탐색의 비용과 시간을 비교합니다.
5. [휴리스틱 모델링과 실전 변형](lessons/heuristic/lesson.md): 배치·repair·빔 탐색으로 확장합니다. 추가 문제 연결은 [ROADMAP.md](ROADMAP.md)를 따릅니다.
6. 정렬·자료구조·그래프 등 기본 알고리즘 강의는 문제에서 필요한 작업과 신호를 보고 찾아봅니다.

필요한 배열·난수·정렬·큐·힙은 별도 [STL 없는 공통 라이브러리](lessons/cpp-common-library/lesson.md)에서 찾아 씁니다. 공통 블록의 사용 계약과 풀이의 선택 기준을 나누며, 라이브러리 전체를 첫 실습의 선수로 요구하지 않습니다.

## 문제 신호별 빠른 길찾기

문제에서 먼저 보이는 신호로 읽을 수 있는 개념 지도입니다.

### 구간 질의/업데이트

질의가 많은 문제에서 온라인/오프라인, 업데이트, 좌표 크기를 먼저 나눕니다.

- 정적 구간 합: [누적합과 차분 배열](lessons/prefix-sum-difference/lesson.md)
- 점 업데이트 + 구간 질의: [Fenwick Tree](lessons/fenwick-tree/lesson.md) / [Segment Tree](lessons/segment-tree/lesson.md)
- 구간 업데이트/블록 처리: [Segment Tree](lessons/segment-tree/lesson.md) / [Sqrt Decomposition](lessons/sqrt-decomposition/lesson.md)
- 좌표가 크다: [좌표 압축](lessons/coordinate-compression/lesson.md) / [Dynamic Segment Tree](lessons/dynamic-segment-tree/lesson.md)
- 질의를 재정렬할 수 있다: [Sqrt Decomposition](lessons/sqrt-decomposition/lesson.md)

### 최적화

답을 판정으로 바꿀 수 있는지와 풀이의 정당성을 검증하는 방법부터 구분합니다.

- 단조 판정: [이분 탐색과 파라메트릭 서치](lessons/binary-search/lesson.md)
- 검증/증명: [Proof와 Invariant](lessons/proof-and-invariants/lesson.md) / [Testing과 Stress Test](lessons/testing-and-stress/lesson.md)

### 그래프

탐색, 최단거리, DAG 순서로 문제 신호를 좁힙니다.

- 탐색/연결성: [BFS/DFS와 격자 탐색](lessons/bfs-dfs-grid/lesson.md) / [그래프와 트리 기본 성질](lessons/graph-tree-basics/lesson.md) / [Union-Find 알고리즘](lessons/union-find/lesson.md)
- 최단거리: [0-1 BFS](lessons/zero-one-bfs/lesson.md) / [Dijkstra 최단거리](lessons/dijkstra/lesson.md) / [Bellman-Ford와 음수 사이클](lessons/bellman-ford-negative-cycle/lesson.md) / [Floyd-Warshall](lessons/floyd-warshall/lesson.md)
- DAG 순서: [위상 정렬과 DAG DP](lessons/topological-sort-dag/lesson.md)

## 카드 배지 기준

- 난이도: `beginner / intermediate / advanced`
- 난이도 축: `implementation / proof / modeling / selection`
- 성격: `core / implementation / overview`
- 완성도: `concept-only / partial / full`
- 연습: `none / todo / linked / verified`
- 대상: `contest-core / advanced-contest`

## 분류

- 휴리스틱 노트: h-contest 문제 풀이에 쓰는 제출·검증, 휴리스틱 탐색, 기본 알고리즘 강의입니다. (레슨 48개)

전체 레슨과 하위 페이지 링크는 [index.html](index.html)에서 확인합니다.
