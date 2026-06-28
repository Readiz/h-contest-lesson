# Practice Set

Graph Cut Structures 허브의 연습은 cut 모델 선택을 먼저 하고, 그다음 deterministic, randomized, all-pairs, family representation으로 확장하는 순서가 좋습니다. 실제 h-contest 문제가 아직 부족한 주제는 임의 ID를 만들지 않고 `TODO`로 남깁니다.

## 1. 연습 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | [Stoer-Wagner Global Min Cut](#3-로컬-연습-stoer-wagner-global-min-cut) | s-t cut과 global cut 구분 | Stoer-Wagner |
| 표준 | TODO: all pair min-cut query `/practice/...` 문제 필요 | cut-equivalent tree 질의 | Gomory-Hu |
| 응용 | TODO: sparse certificate min cut `/practice/...` 문제 필요 | 작은 cut 보존과 edge pruning | cut sparsification |
| 심화 | TODO: min cut family cactus `/practice/...` 문제 필요 | global min cut family 압축 | cactus |
| 함정 | TODO: randomized vs deterministic cut `/practice/...` 문제 필요 | Karger 실패 확률과 fallback | contraction |

## 2. Trace: Stoer-Wagner 한 phase

아래 무향 weighted graph를 봅니다.

```text
0-1: 3
0-2: 1
0-3: 2
1-2: 4
1-3: 1
2-3: 2
```

첫 phase에서 시작 정점을 `0`으로 잡으면 selected set `A`는 아래처럼 커집니다.

| 단계 | `A` | 남은 정점의 연결 weight | 다음 선택 |
| --- | --- | --- | --- |
| 시작 | `{0}` | `w(1)=3`, `w(2)=1`, `w(3)=2` | `1` |
| 1 선택 후 | `{0,1}` | `w(2)=1+4=5`, `w(3)=2+1=3` | `2` |
| 2 선택 후 | `{0,1,2}` | `w(3)=2+1+2=5` | `3` |

마지막으로 선택된 정점은 `t=3`, 그 직전 정점은 `s=2`입니다. 이 phase가 주는 candidate cut은 `{3}`과 나머지를 가르는 cut이고 값은 `5`입니다.

```text
cut({3}) = capacity(3-0) + capacity(3-1) + capacity(3-2)
         = 2 + 1 + 2
         = 5
```

그다음 Stoer-Wagner는 `s=2`와 `t=3`을 merge합니다. 전체 알고리즘은 이런 phase를 정점이 하나 남을 때까지 반복하고, 각 phase의 candidate cut 최솟값을 답으로 둡니다.

## 3. 로컬 연습: Stoer-Wagner Global Min Cut

### 입력

무향 weighted graph가 주어집니다. 전체 global min cut 값을 구합니다.

```text
N M
u1 v1 w1
...
uM vM wM
```

multi-edge가 들어오면 capacity를 더합니다. self-loop는 무시합니다.

### 출력

global min cut 값을 한 줄에 출력합니다. 그래프가 disconnected이면 답은 `0`입니다.

### 제한

- `2 <= N <= 500`
- `0 <= M <= 5000`
- `0 <= u, v < N`
- `1 <= w <= 10^9`

### 예시

```text
4 6
0 1 3
0 2 1
0 3 2
1 2 4
1 3 1
2 3 2
```

```text
5
```

### 풀이 기준

1. `long long` adjacency matrix에 undirected capacity를 누적한다.
2. active vertex list를 유지한다.
3. phase마다 아직 선택되지 않은 vertex 중 `A`와의 연결 weight가 최대인 vertex를 고른다.
4. phase의 마지막 vertex `t`가 만드는 candidate cut weight를 답 후보로 갱신한다.
5. 마지막 직전 vertex `s`와 `t`를 merge한다.
6. `t`를 active list에서 제거하고 다음 phase로 간다.

partition 복원까지 연습하려면 각 active vertex가 대표하는 원래 정점 목록도 같이 merge합니다. phase candidate가 최솟값을 갱신할 때 `t`의 그룹을 저장하면 됩니다.

### Stress 검증

작은 입력에서는 모든 non-empty proper subset을 열거해 cut 값을 계산하는 baseline과 비교합니다.

```text
for seed in 1..1000:
    random undirected weighted graph with N <= 12
    answer_stoer_wagner = O(N^3) implementation
    answer_bruteforce = min cut over all subsets
    assert answer_stoer_wagner == answer_bruteforce
```

반드시 포함할 case는 disconnected graph, multi-edge, 한 정점만 약하게 연결된 graph입니다.

## 4. 다른 로컬 완결형 연습 후보

### Gomory-Hu Query Check

정점 4개 그래프에서 Gomory-Hu Tree를 만든 뒤, 모든 pair에 대해 원래 graph의 max-flow 값과 tree path minimum이 같은지 비교합니다.

### Karger Repetition Experiment

cycle graph와 complete graph에서 Karger contraction을 여러 seed로 반복하고, trial 수가 늘어날 때 best cut 값이 어떻게 안정되는지 확인합니다.

## 5. 제출 전 체크리스트

- `s-t`, global, all-pairs, family, threshold 중 어떤 모델인지 명시했는가?
- 무향/방향 조건을 확인했는가?
- disconnected graph의 global min cut 값 0을 처리했는가?
- Gomory-Hu 질의에서 path sum이 아니라 path minimum을 썼는가?
- randomized 풀이를 쓴다면 반복 횟수와 seed 정책을 설명했는가?
