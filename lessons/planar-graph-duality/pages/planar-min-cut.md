# Planar Min-Cut

Planar graph의 특정 min-cut 문제는 dual graph의 shortest path로 바뀝니다. 이 변환은 강력하지만 조건이 좁습니다. source와 sink의 위치, boundary 조건, edge 방향, face 식별이 모두 맞아야 합니다.

## 1. 전형적인 변환

무향 planar graph에서 edge capacity가 있고, 어떤 두 boundary arc를 분리하는 최소 비용 edge set을 찾아야 한다고 하겠습니다. 각 primal edge의 capacity를 같은 weight의 dual edge로 옮기면, dual에서 두 arc에 대응하는 face 또는 boundary marker 사이의 shortest path가 답이 됩니다.

```text
primal cut cost = sum capacity(edge)
dual path cost = sum weight(edge*)
```

edge 하나를 cut에 넣는 것과 dual path가 그 edge를 건너는 것이 같은 비용을 냅니다.

## 2. 필요한 조건

- planar embedding이 고정되어 있어야 합니다.
- cut의 양 끝 조건이 dual에서 시작/도착 face로 표현되어야 합니다.
- edge cost가 음수가 아니어야 Dijkstra를 바로 쓸 수 있습니다.
- directed capacity가 아니라 무향 cut cost이거나, 방향 처리를 별도로 증명해야 합니다.
- bridge와 self-loop를 dual graph에서 어떻게 다룰지 정해야 합니다.

## 3. 풀이 흐름

1. half-edge traversal 또는 입력 face 정보로 face 번호를 구합니다.
2. outer face와 boundary arc가 닿는 face를 표시합니다.
3. primal edge마다 양쪽 face를 찾아 dual edge를 추가합니다.
4. 문제의 분리 조건을 dual의 시작/도착 집합으로 바꿉니다.
5. Dijkstra 또는 0-1 BFS 같은 shortest path 알고리즘을 실행합니다.
6. 작은 입력에서 primal cut과 dual path의 edge id 집합을 비교합니다.

## 4. 변환하면 안 되는 경우

- 일반 s-t max-flow를 묻고 source/sink가 내부 어디든 놓일 수 있습니다.
- directed edge capacity가 핵심입니다.
- face가 아니라 vertex 조건으로 복잡한 여러 terminal을 동시에 분리해야 합니다.
- embedding이 주어지지 않았고 좌표도 planar straight-line embedding을 보장하지 않습니다.
- dual graph가 multi-edge/self-loop를 갖는데 자료구조가 이를 버립니다.

## 5. 복잡도

| 단계 | 시간 |
| --- | ---: |
| half-edge angle sort | `O(E log E)` |
| face traversal | `O(E)` |
| dual graph construction | `O(E)` |
| Dijkstra | `O(E log F)` |

face 정보가 입력으로 직접 주어지면 첫 두 단계는 사라집니다.
