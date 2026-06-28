# Planar Graph Duality

Planar Graph Duality는 평면에 교차 없이 그린 그래프에서 face를 정점으로 바꾸고, primal graph의 cut/cycle/path 조건을 dual graph의 연결 조건으로 옮겨 보는 그래프/기하 연결 허브입니다. 기존 단일 문서는 face 정보가 이미 주어진 경우의 dual graph 구성에 가까웠으므로, 이제 좌표 기반 half-edge traversal과 planar min-cut 변환을 별도 페이지로 분리합니다.

핵심은 dual graph를 만들기 전에 embedding을 확정하는 것입니다. face 번호가 입력으로 주어지면 dual graph 구성은 쉽지만, 좌표와 간선만 주어지면 half-edge 정렬과 face 순회가 실제 구현의 대부분입니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Graph Tree Basics, Max Flow Min Cut, Geometry CCW
- 함께 보면 좋은 레슨: Sweep Line Geometry, Matrix-Tree Theorem Applications, Global Min Cut
- 다음에 볼 레슨: planar max-flow, separator theorem, arrangement duality

## 1. 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 좌표와 무향 간선만 주어진다 | [Half-edge and Face Traversal](pages/half-edge-and-face-traversal.md) |
| 각 edge 양쪽 face 번호가 이미 주어진다 | [Dual Graph Construction](pages/dual-graph-construction.md) |
| cycle과 cut을 서로 바꾸는 정당성이 필요하다 | [Cut-Cycle Duality](pages/cut-cycle-duality.md) |
| planar s-t cut을 shortest path로 바꾸고 싶다 | [Planar Min-Cut](pages/planar-min-cut.md) |
| bridge, outer face, multi-edge 때문에 헷갈린다 | [Half-edge and Face Traversal](pages/half-edge-and-face-traversal.md) |

## 2. 구현 순서

1. [Half-edge and Face Traversal](pages/half-edge-and-face-traversal.md)에서 directed half-edge, polar-angle sort, face 순회를 구현합니다.
2. [Dual Graph Construction](pages/dual-graph-construction.md)에서 primal edge 양쪽 face를 dual edge로 바꿉니다.
3. [Cut-Cycle Duality](pages/cut-cycle-duality.md)에서 primal cut과 dual cycle/path 대응을 정리합니다.
4. [Planar Min-Cut](pages/planar-min-cut.md)은 dual shortest path로 내려갈 수 있는 조건을 확인합니다.
5. [Practice Set](pages/practice-set.md)에서 face traversal과 dual 변환을 함께 연습합니다.

## 3. 구현 전 체크리스트

- 입력이 planar embedding을 고정하는가, 아니면 embedding을 직접 찾아야 하는가?
- 같은 좌표 방향으로 겹치는 multi-edge가 있는가? 있다면 rotation order가 따로 필요한가?
- half-edge traversal 뒤 `V - E + F = 1 + C`를 통과하는가?
- outer face를 signed area로 식별했는가?
- bridge edge의 양쪽 face가 같을 수 있음을 dual graph가 허용하는가?
- primal에서 찾는 것이 cut, cycle, path 중 무엇이며 dual에서 무엇으로 바뀌는가?

## 4. 연습 문제

이 허브의 연습 흐름은 [Practice Set](pages/practice-set.md)에 모읍니다. Practice Set은 face incidence가 주어진 경우의 dual graph 구성과 shortest path를 로컬 완결형으로 제공하고, 좌표 기반 half-edge traversal은 추가 연습 후보로 남깁니다.
