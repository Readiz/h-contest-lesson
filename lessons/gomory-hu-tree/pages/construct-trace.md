# 4정점 construction trace

이 페이지는 Gomory-Hu Tree construction에서 `parent` 배열이 어떻게 갱신되는지 작은 무향 그래프로 추적합니다. 핵심은 min-cut 값보다 `s`에서 residual graph로 도달 가능한 쪽이 어떤 정점들을 함께 끌고 가는지입니다.

## 예시 그래프

정점은 `0, 1, 2, 3`이고, 무향 edge capacity는 아래와 같습니다.

| edge | capacity |
| --- | ---: |
| `0-1` | 3 |
| `0-2` | 2 |
| `1-2` | 4 |
| `1-3` | 2 |
| `2-3` | 5 |

초기 cut tree parent는 모두 0입니다.

```text
parent[1] = 0
parent[2] = 0
parent[3] = 0
```

아래 trace에서는 min-cut oracle이 `s` 쪽 source side를 `reachable side`로 반환한다고 가정합니다.

## 1단계: `s=1`, `t=parent[1]=0`

`1-0` min cut을 구합니다. 이 그래프에서는 `{1,2,3}`과 `{0}`을 가르는 cut이 capacity `3 + 2 = 5`로 최소입니다.

```text
cut value = 5
reachable side = {1,2,3}
```

현재 `parent[v] == 0`인 정점 중 reachable side에 있는 `2`, `3`은 `1`과 같은 쪽에 있으므로 `1` 아래로 옮깁니다.

```text
parent[1] = 0, weight[1] = 5
parent[2] = 1
parent[3] = 1
```

tree 모양은 아직 임시입니다.

```text
0 --5-- 1
        |
        2
        |
        3
```

여기서 `2`, `3`의 edge weight는 아직 확정되지 않았습니다.

## 2단계: `s=2`, `t=parent[2]=1`

`2-1` min cut을 구합니다. `{2,3}`과 `{0,1}`을 가르면 crossing edge는 `0-2`, `1-2`, `1-3`이고 총 capacity는 `2 + 4 + 2 = 8`입니다.

```text
cut value = 8
reachable side = {2,3}
```

현재 `parent[v] == 1`인 정점 중 `s=2`보다 뒤에 있고 reachable side에 있는 정점은 `3`입니다. 따라서 `3`을 `2` 아래로 옮깁니다.

```text
parent[1] = 0, weight[1] = 5
parent[2] = 1, weight[2] = 8
parent[3] = 2
```

임시 tree는 아래처럼 더 세분화됩니다.

```text
0 --5-- 1 --8-- 2
                 |
                 3
```

## 3단계: `s=3`, `t=parent[3]=2`

`3-2` min cut을 구합니다. `{3}`과 `{0,1,2}`를 가르면 crossing edge는 `1-3`, `2-3`이고 총 capacity는 `2 + 5 = 7`입니다.

```text
cut value = 7
reachable side = {3}
```

더 옮길 자식이 없으므로 `3`의 parent edge weight만 확정합니다.

```text
parent[1] = 0, weight[1] = 5
parent[2] = 1, weight[2] = 8
parent[3] = 2, weight[3] = 7
```

완성된 Gomory-Hu Tree는 아래와 같습니다.

```text
0 --5-- 1 --8-- 2 --7-- 3
```

## Query를 답하는 방법

완성된 tree에서 `2`와 `3` 사이 경로는 edge 하나입니다.

```text
2 --7-- 3
```

따라서 원래 그래프의 `minCut(2, 3)` 값은 path minimum인 `7`입니다.

`0`과 `3`을 묻는다면 tree path는 `0-1-2-3`이고 edge weight는 `5, 8, 7`입니다. 이때 답은 합 `20`이 아니라 최솟값 `5`입니다.

```text
minCut_G(0, 3) = min(5, 8, 7) = 5
```

이 trace에서 꼭 기억할 부분은 두 가지입니다.

1. `reachable side`는 cut value만큼 중요하다. 이 side 없이는 parent 재배치를 할 수 없다.
2. 각 단계는 새 tree edge 하나를 확정하고, 최종 질의는 tree path의 최소 edge weight로 답한다.
