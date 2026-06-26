# h-contest lesson content

This repository is the source of truth for h-contest algorithm lessons. Lesson source lives in `lessons/` and `lessons.json`; `README.md` and `index.html` are generated entry points.

## 탐색

- 전체 카탈로그: [index.html](index.html)
- Published manifest: https://blog.readiz.com/h-contest-lesson/lessons.json
- API mirror: https://h.readiz.com/api/lessons
- 공개 기록: [CHANGELOG.md](CHANGELOG.md)
- 미공개 후보와 practice TODO: [ROADMAP.md](ROADMAP.md)
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

처음 보는 주제라면 아래 순서로 훑는 것을 권장합니다. 이미 익숙한 내용은 건너뛰고, 각 레슨의 `prerequisites`와 `nextLessons` 메타데이터를 참고해 앞뒤 개념을 확인하세요.

1. 입문 0단계: 복잡도 감각, 대회용 C++ 기본기
2. 입문 1단계: 정렬, 누적합, 이분 탐색, 투 포인터
3. 입문 2단계: BFS/DFS, 그리디, 우선순위 큐, Union-Find, 좌표 압축
4. 중급 1단계: DP, Dijkstra, 위상 정렬, Fenwick Tree, Segment Tree, 모듈러 연산
5. 중급 2단계: 트리 심화, TSP, Treap, 휴리스틱
6. 심화 확장: 문자열 매칭, SCC/2-SAT, Flow, 정수론 심화, 기하, 오프라인 쿼리, 검증/증명

## 카테고리 요약

| 카테고리 | 설명 | 레슨 수 |
| --- | --- | ---: |
| 기본기 | 정렬, 누적합, 이분 탐색처럼 문제 풀이의 출발점이 되는 개념입니다. | 7 |
| 전략과 최적화 | 그리디, 동적 계획법, 휴리스틱처럼 풀이 방향을 정하는 사고 도구입니다. | 20 |
| 그래프와 트리 | 탐색, 최단거리, DAG, 트리 구조를 다루는 그래프 계열 개념입니다. | 31 |
| 자료구조 | 우선순위 큐, Union-Find, 구간 자료구조, 균형 트리 계열을 모았습니다. | 26 |
| 문자열 | 패턴 매칭, 해싱, Trie, suffix 구조처럼 문자열을 빠르게 비교하고 탐색하는 개념입니다. | 16 |
| 기하 | CCW, 선분 교차, 볼록 껍질처럼 좌표와 벡터를 다루는 기하 기본 개념입니다. | 18 |
| 수학 | 모듈러 연산, 정수론, 조합론처럼 경우의 수와 수식 처리에 필요한 개념입니다. | 36 |

전체 레슨과 하위 페이지 링크는 [index.html](index.html)에서 확인합니다.
