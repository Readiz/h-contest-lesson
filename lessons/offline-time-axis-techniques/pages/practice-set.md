# Practice Set

Offline and Time-Axis Techniques 계열은 같은 입력을 여러 모델로 바꿔 보는 연습이 중요합니다.

## 권장 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 표준 | [Offline Dynamic Connectivity](#로컬-연습-offline-dynamic-connectivity) | edge active interval + rollback DSU | segment tree over time |

## Trace: active interval 만들기

아래 operation을 모두 미리 읽을 수 있다고 하겠습니다.

```text
0: + 0 1
1: + 1 2
2: ? 0 2
3: - 0 1
4: ? 0 2
5: + 2 3
6: ? 0 3
```

간선은 활성 구간으로 바꿉니다.

| edge | active interval |
| --- | --- |
| `(0, 1)` | `[0, 3)` |
| `(1, 2)` | `[1, 7)` |
| `(2, 3)` | `[5, 7)` |

시간축 Segment Tree는 각 interval을 `O(log Q)`개의 node에 넣습니다. DFS가 어떤 node에 들어가면 그 node의 edge들을 rollback DSU에 union하고, leaf에 도착하면 해당 시간의 query를 현재 DSU 상태로 답합니다. node를 빠져나올 때는 진입 전 snapshot으로 되돌립니다.

위 예시의 답은 아래와 같습니다.

```text
YES
NO
NO
```

`2`번 시점에는 `0-1-2`가 연결되어 있습니다. `4`번 시점에는 `(0,1)`이 빠져 `0`과 `2`가 끊어집니다. `6`번 시점에는 `1-2-3`만 연결되어 있고 `0`은 여전히 떨어져 있습니다.

## 로컬 연습: Offline Dynamic Connectivity

### 입력

무향 그래프가 처음에는 비어 있습니다. `Q`개의 operation이 주어집니다.

```text
N Q
op1
op2
...
opQ
```

operation은 세 종류입니다.

```text
+ u v
- u v
? u v
```

`+ u v`는 간선을 추가하고, `- u v`는 현재 활성인 간선을 삭제합니다. `? u v`는 현재 그래프에서 두 정점이 연결되어 있는지 묻습니다. 같은 unordered edge가 동시에 두 번 활성화되지는 않는다고 가정합니다.

### 출력

각 `?` query마다 연결되어 있으면 `YES`, 아니면 `NO`를 출력합니다.

### 제한

- `1 <= N <= 200000`
- `1 <= Q <= 200000`
- `0 <= u, v < N`
- `u != v`

### 예시

```text
4 7
+ 0 1
+ 1 2
? 0 2
- 0 1
? 0 2
+ 2 3
? 0 3
```

```text
YES
NO
NO
```

### 풀이 기준

1. edge key는 `(min(u, v), max(u, v))`로 정규화한다.
2. `+` 시점은 map에 저장한다.
3. `-` 시점이 나오면 `[start, currentTime)` interval을 만든다.
4. 끝까지 삭제되지 않은 edge는 `[start, Q)`로 닫는다.
5. 각 interval을 시간축 Segment Tree에 넣는다.
6. rollback DSU로 DFS를 돌며 leaf의 `?` query를 답한다.

Rollback DSU는 path compression을 쓰지 않습니다. union by size/rank만 쓰고, 바뀐 parent와 size를 stack에 저장합니다. union이 실제로 합치지 못한 경우에도 rollback 횟수를 맞추기 위해 marker를 넣거나, snapshot 크기로 되돌리는 방식을 씁니다.

### Stress 검증

작은 입력에서는 매 query마다 현재 active edge 목록으로 그래프를 새로 만들고 BFS/DFS로 답하는 baseline과 비교합니다.

```text
for seed in 1..1000:
    generate valid add/remove/query sequence
    answer_offline = segment tree over time + rollback DSU
    answer_naive = rebuild graph at every query
    assert answer_offline == answer_naive
```

중복 add를 허용하는 문제라면 edge별 reference count가 필요합니다. 이 로컬 연습은 "동시에 한 번만 활성"이라는 조건에서 active interval 변환과 rollback 구현을 먼저 고정하는 목적입니다.
