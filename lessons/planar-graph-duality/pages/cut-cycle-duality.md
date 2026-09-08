# Cut-Cycle Duality

Planar graph에서 primal graph의 cycle과 cut은 dual graph에서 서로 역할이 바뀝니다. 이 대응을 정확히 이해해야 min-cut을 shortest path로 바꾸거나, 영역 분리 조건을 dual 연결 조건으로 옮길 수 있습니다.

## 기본 대응

| Primal | Dual |
| --- | --- |
| edge | 같은 edge weight를 가진 dual edge |
| face | dual vertex |
| cycle | dual cut |
| cut | dual cycle 또는 path |
| bridge | dual self-loop |

Primal edge 하나가 두 face 사이의 경계라면 dual edge는 그 두 face를 연결합니다. 어떤 primal cycle은 내부 face들과 외부 face들을 나누므로 dual에서는 cut이 됩니다.

## Cut을 Path로 보는 경우

planar s-t cut이 항상 단순한 dual shortest path가 되는 것은 아닙니다. 보통 source와 sink가 outer boundary 위에 있고, 두 boundary arc를 분리하는 형태로 조건이 주어질 때 dual path 해석이 깔끔해집니다.

```text
primal에서 s와 t를 분리하는 edge set
-> dual에서 두 boundary arc 사이를 잇는 path
```

이때 primal edge capacity를 dual edge length로 두면, 최소 cut 비용이 dual shortest path 길이가 됩니다.

## 방향 그래프 주의

무향 planar graph에서는 cut-cycle 대응이 비교적 단순합니다. 방향 그래프에서는 dual edge 방향과 capacity 방향이 얽히므로, edge를 그냥 양방향 dual edge로 만들면 틀릴 수 있습니다.

방향이 있는 문제에서는 다음을 먼저 확인합니다.

- primal edge를 끊는 비용이 방향과 무관한가?
- residual capacity를 dual에서 어떻게 표현하는가?
- source/sink가 face인지 vertex인지?
- 문제에서 요구하는 것이 min cut인지, circulation인지, shortest separating curve인지?

## 필요한 조건

- planar embedding이 고정되어 있어야 합니다.
- cut의 양 끝 조건이 dual에서 시작/도착 face로 표현되어야 합니다.
- edge cost가 음수가 아니어야 Dijkstra를 바로 쓸 수 있습니다.
- directed capacity가 아니라 무향 cut cost이거나, 방향 처리를 별도로 증명해야 합니다.
- bridge와 self-loop를 dual graph에서 어떻게 다룰지 정해야 합니다.

## 풀이 흐름

1. half-edge traversal 또는 입력 face 정보로 face 번호를 구합니다.
2. outer face와 boundary arc가 닿는 face를 표시합니다.
3. primal edge마다 양쪽 face를 찾아 dual edge를 추가합니다.
4. 문제의 분리 조건을 dual의 시작/도착 집합으로 바꿉니다.
5. Dijkstra 또는 0-1 BFS 같은 shortest path 알고리즘을 실행합니다.
6. 작은 입력에서 primal cut과 dual path의 edge id 집합을 비교합니다.

## 복잡도

| 단계 | 시간 |
| --- | ---: |
| half-edge angle sort | `O(E log E)` |
| face traversal | `O(E)` |
| dual graph construction | `O(E)` |
| Dijkstra | `O(E log F)` |

face 정보가 입력으로 직접 주어지면 첫 두 단계는 사라집니다.
