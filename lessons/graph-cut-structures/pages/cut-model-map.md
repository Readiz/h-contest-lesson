# Cut Model Map

Cut 문제는 모두 비슷해 보이지만, source와 sink가 고정됐는지, 전체 graph의 최약 지점인지, 모든 pair 질의인지에 따라 도구가 완전히 달라집니다. Graph Cut Structures 허브에서는 먼저 이 분류를 끝내고 알고리즘을 고릅니다.

## 1. 모델 비교표

| 질문 | 모델 | 대표 도구 |
| --- | --- | --- |
| `s`와 `t`를 분리하는 최소 capacity는? | s-t min cut | Max Flow |
| 아무 두 non-empty 집합으로 나누는 최소 cut은? | global min cut | Stoer-Wagner, Karger |
| 모든 `u, v`의 min cut 값을 질의해야 하는가? | all-pairs min cut | Gomory-Hu Tree |
| min cut 값이 `k` 미만인지가 핵심인가? | threshold connectivity | sparse certificate |
| 모든 global min cut partition을 표현해야 하는가? | cut family | cactus representation |
| planar embedding으로 cut을 path로 바꿀 수 있는가? | planar dual cut | Planar Graph Duality |

이 표에서 한 줄을 고르지 못하면 구현을 시작하지 않는 편이 낫습니다. 특히 global min cut과 s-t min cut을 혼동하면 맞는 알고리즘을 써도 틀립니다.

## 2. 선후 관계

가장 기본은 max-flow/min-cut theorem입니다. 그러나 max-flow는 특정 pair를 분리하는 문제이고, global min cut은 pair가 고정되지 않습니다.

```text
s-t min cut
  -> single pair separation

global min cut
  -> weakest separation anywhere

Gomory-Hu Tree
  -> all pair min cut values compressed in a tree

cut cactus
  -> all global minimum cut partitions compressed
```

Gomory-Hu Tree와 cut cactus는 둘 다 tree/cactus처럼 보이지만 압축 대상이 다릅니다. Gomory-Hu는 pair별 min cut value, cactus는 global minimum cut family입니다.

## 3. 알고리즘 선택

| 제한/요구 | 선택 |
| --- | --- |
| `N` 중간, 무향 weighted, 값 하나 | Stoer-Wagner |
| unweighted multigraph, randomized 허용 | Karger 반복 |
| pair query가 많고 max-flow가 가능 | Gomory-Hu Tree |
| dense graph, 작은 `k` connectivity만 필요 | forest-layer certificate |
| 모든 global min cut family | cactus 관점, construction 난도 확인 |
| planar embedding과 boundary cut | dual shortest path |

## 4. 실수 방지 질문

1. directed graph인가? 그렇다면 이 허브의 많은 구조가 바로 적용되지 않습니다.
2. cut partition을 출력해야 하는가, 값만 출력하면 되는가?
3. all-pairs 질의인가, global value 하나인가?
4. capacity가 weighted인지 unweighted인지, multi-edge가 있는지 확인했는가?
5. randomized 풀이의 실패 확률을 제한 안에서 충분히 낮출 수 있는가?
