# Euler Tour Tree

Euler Tour Tree(ETT)는 동적 forest의 각 component를 순환 Euler tour로 저장합니다. balanced sequence tree의 split/merge로 link, cut, 연결성, component 합을 관리합니다. 일반 그래프 연결성에는 삭제한 tree edge를 대신할 간선 탐색이 추가로 필요합니다.

## 중복 집계를 막는 표현

정점마다 marker V(u)를 정확히 하나 두고, 무향 간선마다 방향 arc (u,v), (v,u)를 하나씩 둡니다. 정점 값은 marker에만, arc의 집계 값은 0으로 저장합니다. 그러면 component 합에서 같은 정점이 여러 번 더해지지 않습니다. singleton은 [V(u)]입니다.

트리 1-2-3의 순환 sequence 한 가지는 다음과 같습니다.

```text
[V(1), (1,2), V(2), (2,3), V(3), (3,2), (2,1)]
```

## Reroot와 Link

V(u) 앞에서 split한 A+B를 B+A로 붙이면 u 기준으로 회전합니다. 서로 다른 component의 u,v를 연결할 때 두 sequence를 각각 u,v 기준으로 회전한 뒤 T_u+(u,v)+T_v+(v,u)로 붙입니다. 같은 component를 연결하면 cycle이 되므로 거부합니다.

```text
reroot(3): [V(3), (3,2), (2,1), V(1), (1,2), V(2), (2,3)]
link(3,4): 위 sequence + [(3,4), V(4), (4,3)]
```

## Cut

간선별 두 arc node의 핸들을 보관합니다. 순환 sequence를 (u,v)가 맨 앞이 되게 회전하면 [(u,v)]+A+[(v,u)]+B가 됩니다. 두 arc를 제거한 A와 B가 두 component입니다.

```text
원래 1-2-3에서 cut(2,3):
[(2,3), V(3), (3,2), (2,1), V(1), (1,2), V(2)]
A = [V(3)]
B = [(2,1), V(1), (1,2), V(2)]
```

각 정점 marker는 제거되지 않으며 B도 올바른 순환 tour입니다.

## 구현에 필요한 연결 정보

implicit treap을 쓰려면 subtree size·aggregate 외에 parent pointer가 있어야 marker에서 현재 root와 index를 찾을 수 있습니다. split/merge의 모든 자식 변경에서 parent를 갱신하고, 반환 root의 parent를 비웁니다. 잘린 두 arc는 핸들을 무효화한 뒤 해제합니다. 단순 split/merge 코드만으로 ETT가 완성되지는 않습니다.

무작위 priority treap에서 root/index, reroot, link, cut은 기대 O(log N), root를 찾은 뒤 component aggregate 조회는 O(1)입니다. 메모리는 forest 전체 O(N)입니다. 경로 aggregate가 핵심이면 Link-Cut Tree, 질의가 offline이면 Rollback DSU가 더 직접적입니다.
