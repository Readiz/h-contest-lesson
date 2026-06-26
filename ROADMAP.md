# h-contest lesson content roadmap

이 문서는 아직 공개하지 않은 레슨 후보, 심화 레슨 구조 개편 후보, 공개 전 품질 기준, practice link 미정 항목만 관리합니다. 이미 공개된 레슨의 이동 기록과 보강 완료 기록은 [CHANGELOG.md](CHANGELOG.md)로 옮깁니다.

새 주제는 본문, 예시 구현, 체크리스트, 연습 문제 표가 준비된 뒤 manifest에 추가합니다. 적절한 h-contest 문제가 없으면 임의 문제 ID를 넣지 말고 `TODO: /practice/... 문제 필요`로 남깁니다.

## 구조 개편 후보

이미 공개된 심화 레슨 중 개념이 서로 가까운 묶음은 새 레슨을 더 추가하기 전에 허브화 또는 `pages/` 분할을 검토합니다.

| 우선순위 | 묶음 | 제안 | 상태 |
| ---: | --- | --- | --- |
| 1 | `online-convex-optimization`, `dual-averaging` | online optimization 허브 아래 OGD, mirror descent, dual averaging 경로로 정리 | TODO |
| 2 | `markov-decision-process`, `reinforcement-learning-basics`, `stochastic-shortest-path` | MDP/RL 허브 아래 value iteration, policy improvement, absorbing SSP를 분리 | TODO |
| 3 | `alien-optimization`, `parametric-dp`, `fractional-programming-dp`, `lagrangian-relaxation-patterns` | 제약 완화/파라메트릭 최적화 허브로 penalty, count, ratio, lambda 패턴을 묶음 | TODO |

## 우선 추가할 주제

| 우선순위 | 후보 lessonId | 주제 | 연습 문제 상태 |
| ---: | --- | --- | --- |
| 1 | `spectral-graph-basics` | Laplacian eigenvalue, algebraic connectivity, random walk 관점으로 그래프 성질을 읽는 수학/그래프 연결 주제 | TODO: spectral graph `/practice/...` 문제 필요 |
| 2 | `sparse-determinant` | sparse matrix의 determinant/rank를 black-box linear algebra와 modular evaluation으로 계산하는 선형대수 주제 | TODO: sparse determinant `/practice/...` 문제 필요 |
| 3 | `additively-weighted-voronoi` | distance에 additive weight가 붙는 Voronoi variant와 shortest path/geometry 모델링 | TODO: weighted Voronoi `/practice/...` 문제 필요 |
| 4 | `arrangement-duality` | point-line duality와 arrangement level/query를 계산기하 문제 변환으로 다루는 주제 | TODO: arrangement duality `/practice/...` 문제 필요 |
| 5 | `policy-gradient-basics` | policy parameter, score function estimator, baseline을 contest simulator 평가 관점에서 정리하는 주제 | TODO: policy gradient `/practice/...` 문제 필요 |

## 추가 후보 묶음

| 영역 | 후보 lessonId |
| --- | --- |
| 문자열 | `string-period-query-applications` 이후 응용 후보 정리 필요 |
| 그래프 심화 | `spectral-graph-basics`, `algebraic-matching` |
| 자료구조/오프라인 | `persistent-sequence-queries` 이후 versioned sequence 응용 후보 정리 필요 |
| 수학 심화 | `spectral-graph-basics`, `sparse-determinant` |
| DP 최적화 | `convex-optimization-duality`, `risk-sensitive-dp` |
| 기하 | `additively-weighted-voronoi`, `arrangement-duality` |
| 게임/탐색 | `policy-gradient-basics`, `risk-sensitive-planning` |

## 공개 레슨으로 올리기 전 조건

1. `lessons/<lessonId>/lesson.md` 또는 `pages/` 본문이 "읽기 -> 구현하기 -> 문제 풀기 -> 실수 점검하기" 흐름을 갖춘다.
2. C++ 구현 또는 의사 구현이 있고, 필요한 경우 `cpp compile-check` fence로 컴파일 검증 대상에 올린다.
3. `## 연습 문제` 표는 `단계`, `문제`, `목표`, `힌트 키워드` 열을 사용한다.
4. 적절한 h-contest 문제가 없으면 문제 칸에 `TODO: ... /practice/... 문제 필요`라고 남긴다.
5. 공개하기 전에 `python3 scripts/generate_catalog.py`와 `python3 scripts/validate_lessons.py`를 통과시킨다.
