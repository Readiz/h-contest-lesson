# Dynamic Network Optimization Practice Set

이 페이지는 Dynamic Flow와 Dynamic MST를 완전한 online 자료구조부터 시작하지 않고, 제한된 update 모델로 낮추는 연습을 모읍니다. 아직 적절한 h-contest 문제가 없는 칸은 임의 ID를 넣지 않고 `TODO`로 둡니다.

## 로컬 완결형 연습

### Residual Reuse Trace

정점 `S, A, B, T`와 아래 간선이 있는 작은 네트워크를 잡습니다.

```text
S -> A capacity 2
S -> B capacity 2
A -> T capacity 1
B -> T capacity 2
A -> B capacity 1
```

초기 max flow는 3입니다.

```text
S -> A -> T : 1
S -> B -> T : 2
```

이 상태에서 `A -> T` capacity를 1 늘리면 old flow는 여전히 feasible입니다. residual graph에는 `S -> A -> T`로 1을 더 보낼 수 있으므로 답은 4가 됩니다.

반대로 `S -> B` capacity를 1 줄이면 old flow 2가 capacity 1을 초과합니다. 이때는 추가 augment만으로는 고칠 수 없고, 초과 flow를 되돌리거나 rebuild해야 합니다.

이 trace에서 써야 할 표는 아래 네 칸입니다.

| 단계 | max flow | 바뀐 간선 | 가능한 처리 |
| --- | ---: | --- | --- |
| 초기 | 3 | 없음 | Dinic 한 번 |
| capacity 증가 | 4 | `A -> T += 1` | residual에서 추가 augment |
| capacity 감소 | 알 수 없음 | `S -> B -= 1` | repair 또는 rebuild |
| source/sink 변경 | 알 수 없음 | `S/T` 변경 | batch query나 rebuild |

핵심은 "capacity 증가에서는 기존 flow가 계속 feasible하다"는 조건입니다. 이 조건을 놓치면 dynamic flow를 dynamic connectivity처럼 단순 rollback으로 착각하게 됩니다.

### Incremental Max Flow Runner

아래 로컬 문제는 실제 Dinic 구현까지 붙여서 끝낼 수 있는 형태입니다.

#### 입력

초기 directed network와 `Q`개의 capacity increase query가 주어집니다. 각 query 뒤의 max flow 값을 출력합니다.

```text
N M Q S T
u1 v1 c1
...
uM vM cM
edgeId1 delta1
...
edgeIdQ deltaQ
```

간선 ID는 입력 간선의 0-based index입니다. `delta`는 양수입니다.

#### 제한

- `2 <= N <= 300`
- `1 <= M <= 2000`
- `0 <= Q <= 2000`
- `0 <= S, T < N`, `S != T`
- 모든 capacity와 delta는 `1..10^6`

#### 예시

```text
4 5 2 0 3
0 1 2
0 2 2
1 3 1
2 3 2
1 2 1
2 1
0 1
```

초기 flow는 3입니다. 첫 query는 `1 -> 3` capacity를 1 늘려 flow가 4가 됩니다. 두 번째 query는 `0 -> 1` capacity를 늘리지만 `T`로 들어가는 병목이 이미 찼으므로 답은 그대로 4입니다.

```text
4
4
```

#### 구현 기준

1. 초기 간선마다 Dinic edge index를 저장한다.
2. 초기 max flow를 한 번 계산한다.
3. query가 들어오면 해당 forward edge의 residual capacity를 `delta`만큼 늘린다.
4. 같은 residual graph에서 Dinic을 다시 호출해 추가 flow만 더한다.
5. 누적 flow를 출력한다.

Dinic을 다시 호출해도 reverse edge와 기존 residual capacity를 초기화하면 안 됩니다. 이 연습의 목적은 "정적 max-flow 구현을 재사용하되 residual state를 유지하는 법"을 확인하는 것입니다.

#### Stress 검증

작은 입력에서는 query마다 원래 capacity 배열을 갱신한 뒤 Dinic을 처음부터 돌리는 baseline과 비교합니다.

```text
for seed in 1..1000:
    random graph and positive increase queries
    answer_incremental = residual reuse
    answer_rebuild = rebuild Dinic every query
    assert answer_incremental == answer_rebuild
```

capacity decrease query를 일부러 섞으면 이 assert가 깨질 수 있어야 합니다. 그 반례가 바로 이 기법의 적용 경계입니다.

### MST Replacement Counterexample

네 정점 cycle에 diagonal 하나를 추가한 그래프를 만듭니다. MST에 들어간 edge를 삭제하면 어떤 non-tree edge가 replacement가 되는지 직접 찾고, MST 밖 edge를 삭제하면 답이 변하지 않는다는 것도 같이 확인합니다.

## h-contest 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: incremental flow `/practice/...` 문제 필요 | capacity 증가만 있는 residual 재사용 | feasible old flow |
| 표준 | TODO: time-expanded flow `/practice/...` 문제 필요 | 시간별 edge를 정적 network로 펼치기 | wait edge |
| 표준 | TODO: dynamic MST rebuild `/practice/...` 문제 필요 | 활성 간선 Kruskal baseline | active set |
| 응용 | TODO: MST block rebuild `/practice/...` 문제 필요 | 변경 edge 후보만 합치기 | sqrt decomposition |
| 함정 | TODO: flow decrease counterexample `/practice/...` 문제 필요 | 용량 감소에서 repair 필요성 확인 | infeasible flow |
