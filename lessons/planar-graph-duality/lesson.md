# Planar Graph Duality

Planar Graph Duality는 평면에 교차 없이 그린 그래프에서 face를 정점으로 바꾸고, primal graph의 cut/cycle/path 조건을 dual graph의 연결 조건으로 옮겨 보는 그래프/기하 연결 허브입니다.

핵심은 dual graph를 만들기 전에 embedding을 확정하는 것입니다. face 번호가 입력으로 주어지면 dual graph 구성은 쉽지만, 좌표와 간선만 주어지면 half-edge 정렬과 face 순회가 실제 구현의 대부분입니다.

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| 좌표·간선에서 face를 찾거나 주어진 face 번호로 dual을 만든다 | [Face 순회와 Dual Graph 구성](pages/half-edge-and-face-traversal.md) |
| cut-cycle 대응과 dual shortest path 변환 조건이 필요하다 | [Cut-Cycle Duality](pages/cut-cycle-duality.md) |

## 연습

[로컬 연습](pages/half-edge-and-face-traversal.md)은 face incidence가 주어진 dual graph 구성과 최단 경로를 다룹니다.
