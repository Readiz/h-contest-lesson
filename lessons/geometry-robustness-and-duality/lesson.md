# Geometry Robustness and Duality

Geometry Robustness and Duality는 robust predicate, Voronoi/Delaunay, Power Diagram, 3D lifting, Regular Triangulation을 하나의 계산기하 심화 흐름으로 묶는 허브입니다. 이 묶음은 전체 구현을 외우기보다 "어떤 predicate가 필요하고, 어떤 duality로 문제를 낮출 수 있는가"를 먼저 판단해야 합니다.

기존 단발 문서들은 각각 의미가 있지만, 독자가 바로 구현 레슨으로 받아들이면 위험합니다. 특히 weighted Voronoi와 regular triangulation은 대회에서 전체 구조를 직접 구현하는 경우보다 cell 계산, predicate, lifting 해석만 필요한 경우가 많습니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Geometry CCW와 Segment Intersection, Circle Geometry, Sweep Line Geometry, Half-Plane Intersection
- 함께 보면 좋은 레슨: Shape Distance Modeling, Circle Arrangement, Inversion Geometry
- 다음에 볼 레슨: robust Delaunay implementation, weighted Voronoi cell query, 3D lower hull

## 1. 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| orientation, incircle, EPS 정책이 답을 좌우한다 | [Robust Geometry Predicates](pages/robust-geometry-predicates.md) |
| weighted site의 nearest cell이 필요하다 | [Power Diagram](pages/power-diagram.md) |
| Delaunay edge flip과 incircle degeneracy가 핵심이다 | [Robust Delaunay](pages/robust-delaunay.md) |
| 2D weighted 구조를 3D lower hull로 이해해야 한다 | [Regular Triangulation](pages/regular-triangulation.md) |
| signed volume, visible face, horizon edge가 필요하다 | [3D Convex Hull](pages/3d-convex-hull.md) |

가장 먼저 볼 것은 "좌표를 실제로 만들 것인가, 부호만 판정할 것인가"입니다. predicate만 필요하면 exact arithmetic으로 안정성을 잡고, cell이나 교점 좌표가 필요하면 construction 오차와 tie policy를 따로 설계합니다.

## 2. Robustness와 Duality를 분리하기

| 질문 | Robustness 관점 | Duality 관점 |
| --- | --- | --- |
| 세 점의 방향이 필요한가 | orientation 부호와 overflow | convex hull, sweep ordering |
| 점이 원 안에 있는가 | incircle determinant | Delaunay edge legality |
| weighted nearest가 필요한가 | power distance 비교 | Power Diagram과 regular triangulation |
| 2D 경계가 복잡한가 | half-plane intersection 안정성 | lifting 후 lower envelope |
| 입력이 degeneracy를 포함하는가 | tie-breaking policy | 여러 가능한 triangulation |

robust predicate 없이 duality만 쓰면 구현이 불안정해지고, duality 없이 predicate만 외우면 왜 그 부호를 보는지 흐름이 끊깁니다.

## 3. 쓰지 말아야 할 경우

- 좌표 범위가 큰 정수인데 모든 predicate를 `double` cross product로 처리합니다.
- weighted Voronoi 문제인데 weight가 반지름인지 반지름 제곱인지 확인하지 않습니다.
- 한 cell만 필요할 뿐인데 full Delaunay 또는 regular triangulation을 구현하려고 합니다.
- 3D hull degeneracy를 처리할 준비가 없는데 regular triangulation 전체 구조를 직접 만듭니다.
- EPS comparator로 balanced tree의 strict ordering을 깨뜨립니다.

## 4. 로컬 완결형 연습

Practice Set은 `__int128` orientation 기반 선분 교차 구현을 대표 predicate 연습으로 제공하고, weighted power boundary trace로 duality 흐름을 이어갑니다.

### Power Cell by Half-Planes

작은 weighted point set과 bounding box가 주어졌다고 가정합니다. 한 site `i`에 대해 모든 다른 site `j`가 만드는 부등식 `power_i(x) <= power_j(x)`를 half-plane으로 바꾸고, 남는 polygon을 손으로 계산합니다.

```text
A = (0, 0), w = 0
B = (4, 0), w = 12
bounding box: -10 <= x,y <= 10
```

먼저 두 site의 경계가 `x = 0.5`가 되는지 확인합니다. 그다음 site를 하나 더 추가해 cell이 사라지는 입력을 만듭니다.

### Predicate Policy Table

정수 좌표 orientation, 실수 좌표 circle intersection, sweep comparator를 각각 한 줄씩 적고, 어떤 부분은 exact predicate로 처리하고 어떤 부분은 floating construction으로 처리할지 표로 분리합니다.

## 5. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: robust orientation `/practice/...` 문제 필요 | exact sign과 overflow 방지 | `__int128` |
| 표준 | TODO: power cell `/practice/...` 문제 필요 | weighted distance를 half-plane으로 변환 | radical axis |
| 응용 | TODO: robust Delaunay `/practice/...` 문제 필요 | incircle predicate와 edge flip | degeneracy |
| 심화 | TODO: regular triangulation lifting `/practice/...` 문제 필요 | weighted point를 3D lower hull로 해석 | lifting |
| 함정 | TODO: EPS comparator `/practice/...` 문제 필요 | strict weak ordering 유지 | tie policy |
