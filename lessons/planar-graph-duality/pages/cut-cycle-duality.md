# Cut-Cycle Duality

Planar graph에서 primal graph의 cycle과 cut은 dual graph에서 서로 역할이 바뀝니다. 이 대응을 정확히 이해해야 min-cut을 shortest path로 바꾸거나, 영역 분리 조건을 dual 연결 조건으로 옮길 수 있습니다.

## 1. 기본 대응

| Primal | Dual |
| --- | --- |
| edge | 같은 edge weight를 가진 dual edge |
| face | dual vertex |
| cycle | dual cut |
| cut | dual cycle 또는 path |
| bridge | dual self-loop |

Primal edge 하나가 두 face 사이의 경계라면 dual edge는 그 두 face를 연결합니다. 어떤 primal cycle은 내부 face들과 외부 face들을 나누므로 dual에서는 cut이 됩니다.

## 2. Cut을 Path로 보는 경우

planar s-t cut이 항상 단순한 dual shortest path가 되는 것은 아닙니다. 보통 source와 sink가 outer boundary 위에 있고, 두 boundary arc를 분리하는 형태로 조건이 주어질 때 dual path 해석이 깔끔해집니다.

```text
primal에서 s와 t를 분리하는 edge set
-> dual에서 두 boundary arc 사이를 잇는 path
```

이때 primal edge capacity를 dual edge length로 두면, 최소 cut 비용이 dual shortest path 길이가 됩니다.

## 3. 방향 그래프 주의

무향 planar graph에서는 cut-cycle 대응이 비교적 단순합니다. 방향 그래프에서는 dual edge 방향과 capacity 방향이 얽히므로, edge를 그냥 양방향 dual edge로 만들면 틀릴 수 있습니다.

방향이 있는 문제에서는 다음을 먼저 확인합니다.

- primal edge를 끊는 비용이 방향과 무관한가?
- residual capacity를 dual에서 어떻게 표현하는가?
- source/sink가 face인지 vertex인지?
- 문제에서 요구하는 것이 min cut인지, circulation인지, shortest separating curve인지?

## 4. 작은 검증

사각형 안쪽에 장애물 face가 있고, outer boundary의 두 arc를 분리해야 한다고 합시다. Primal에서 선택한 cut edge들이 장애물 주변을 둘러싸면, dual에서는 outer face에서 장애물 face로 들어가는 path 또는 두 boundary face를 잇는 path로 보입니다.

작은 그림에서는 다음을 손으로 확인합니다.

1. 선택한 primal edge들이 실제로 s와 t를 분리하는가?
2. 그 edge들의 dual edge가 끊기지 않은 연속 path를 이루는가?
3. 같은 edge cost 합이 유지되는가?
4. outer face 번호가 올바른가?

## 5. 실수 포인트

1. primal cycle과 dual cycle을 그대로 대응시킨다.
2. bridge의 dual self-loop를 shortest path에 넣어 의미 없는 완화를 만든다.
3. outer face를 제거해 boundary 조건을 잃는다.
4. directed capacity 문제를 무향 dual shortest path로 바꾼다.
5. embedding이 바뀌어도 dual이 같다고 가정한다.
