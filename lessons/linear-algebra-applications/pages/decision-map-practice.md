# Decision Map Practice

이 페이지는 Linear Algebra Applications의 선택표를 실제 풀이 결정으로 이어 가는 로컬 완결형 연습입니다. 아직 맞는 h-contest practice 문제가 없는 항목은 임의 ID를 만들지 않고, 여기서 작은 입력과 trace로 먼저 검증합니다.

## 1. 먼저 분류하기

아래 네 문장을 보고 바로 구현을 고르지 말고, 필요한 답의 종류를 먼저 표시합니다.

| 문제 신호 | 필요한 답 | 먼저 볼 모델 | 피해야 할 오해 |
| --- | --- | --- | --- |
| xor 값 여러 개로 만들 수 있는 최댓값 | span 안의 최댓값 | GF(2) basis | modulo 덧셈처럼 처리 |
| `a1*x1 + ... + ak*xk = b` 조건 여러 개 | 해 존재, 자유 변수 수 | augmented rank | 식 개수만으로 자유도 계산 |
| 모든 spanning tree 개수 | count | Laplacian cofactor determinant | tree를 직접 나열 |
| `state_{t+1}=A*state_t`이고 `t`가 큼 | 먼 항 하나 | matrix power 또는 recurrence | 일반 DP처럼 `t`번 반복 |

분류가 끝나면 `N`, matrix density, modulo가 prime인지, randomized 허용 여부를 체크합니다. 이 네 조건이 구현 난이도를 거의 결정합니다.

## 2. Trace: Parity Constraints

아래 조건을 봅니다.

```text
x0 xor x1 = 1
x1 xor x2 = 0
x0 xor x2 = 1
```

GF(2)에서 xor는 덧셈이므로 augmented matrix는 아래와 같습니다.

```text
1 1 0 | 1
0 1 1 | 0
1 0 1 | 1
```

row 0을 pivot으로 잡고 row 2를 xor하면 이렇게 됩니다.

```text
1 1 0 | 1
0 1 1 | 0
0 1 1 | 0
```

row 1과 row 2는 같은 제약입니다. rank는 2, 변수는 3개이므로 해 개수는 `2^(3 - 2) = 2`입니다.

같은 왼쪽 식에서 마지막 RHS만 0으로 바꾸면 반례가 됩니다.

```text
x0 xor x1 = 1
x1 xor x2 = 0
x0 xor x2 = 0
```

row 2를 pivot row와 xor하면 `0 1 1 | 1`이 되고, row 1과 다시 xor하면 `0 0 0 | 1`이 나옵니다. 이 행은 모순이므로 해가 없습니다.

## 3. 로컬 연습 A: XOR Constraint Counter

### 입력

`N`개의 0/1 변수와 `M`개의 제약이 있습니다. 각 제약은 `u v b`로 주어지고, 의미는 `x_u xor x_v = b`입니다.

```text
N M
u1 v1 b1
...
uM vM bM
```

### 출력

제약이 모순이면 `0`을 출력합니다. 모순이 아니면 가능한 assignment 수를 `998244353`으로 나눈 값을 출력합니다.

### 제한

- `1 <= N <= 2000`
- `0 <= M <= 4000`
- `0 <= u, v < N`
- `b`는 0 또는 1

### 예시

```text
4 3
0 1 1
1 2 0
0 2 1
```

위 세 제약의 rank는 2입니다. `x3`은 어떤 제약에도 등장하지 않으므로 자유 변수이고, `x0, x1, x2` 묶음에서도 하나가 자유 변수입니다. 답은 `2^(4 - 2) = 4`입니다.

```text
4
```

### 풀이 기준

1. 각 제약을 GF(2) augmented row로 만든다.
2. Gaussian elimination으로 pivot을 잡는다.
3. `0 ... 0 | 1` 행이 나오면 모순이다.
4. 모순이 없으면 `2^(N - rank)`를 출력한다.

이 문제는 parity DSU로도 풀 수 있습니다. 하지만 이 연습의 목표는 "xor 제약을 linear system으로 번역하고 rank로 해 개수를 세는 과정"입니다.

## 4. 로컬 연습 B: Tiny Matrix-Tree

### 입력

무향 단순 그래프가 주어집니다. spanning tree 개수를 `1,000,000,007`로 나눈 값을 구합니다.

```text
N M
a1 b1
...
aM bM
```

### 제한

- `2 <= N <= 80`
- `0 <= M <= 300`
- `0 <= ai, bi < N`

### 예시

```text
4 4
0 1
1 2
2 3
3 0
```

4-cycle은 간선 하나를 빼는 네 가지 방법이 spanning tree입니다.

```text
4
```

### 풀이 기준

1. Laplacian `L`을 만든다.
2. 아무 정점 하나의 행과 열을 지운다.
3. 남은 `(N-1) x (N-1)` matrix의 determinant를 modulo prime에서 계산한다.

이 연습은 determinant가 "행렬 값"이 아니라 graph counting을 압축한 값이라는 감각을 확인합니다.

## 5. 선택 실패를 잡는 체크리스트

- xor가 보이면 carry 없는 GF(2) 연산인지 먼저 확인했는가?
- modulo가 prime이 아니라면 Gaussian elimination의 나눗셈이 안전한가?
- determinant가 필요한 문제인지, rank만 알면 되는 문제인지 구분했는가?
- sparse graph count를 dense determinant로 밀어도 제한에 맞는가?
- randomized determinant를 쓰는 경우 실패 확률과 반복 횟수를 설명할 수 있는가?
