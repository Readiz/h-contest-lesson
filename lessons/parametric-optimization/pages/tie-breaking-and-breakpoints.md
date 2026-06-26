# Tie-breaking and Breakpoints

Parametric Optimization에서 가장 자주 틀리는 지점은 relaxed score만 보고 원래 답을 복원하는 것입니다. 같은 `lambda`에서 같은 relaxed score를 가진 해가 여러 개이고 count가 다르면, 이분 탐색 경계와 최종 보정이 흔들릴 수 있습니다.

## 1. 왜 count를 같이 저장하는가

exact-K 문제에서 relaxed objective가 아래라고 합시다.

```text
relaxed = original + lambda * count
```

`lambda`를 고정하면 DP는 `relaxed`가 가장 작은 해를 찾습니다. 그런데 `relaxed`가 같은 해가 여러 개라면 어떤 count를 반환하느냐에 따라 "현재 lambda에서 K개 이상을 고를 수 있는가"의 답이 달라질 수 있습니다.

그래서 DP 값은 보통 아래처럼 pair로 둡니다.

```text
(relaxedScore, count)
```

최소화 문제에서 더 많은 선택이 필요하면 score가 같을 때 `count`가 큰 쪽을 고릅니다. 반대로 적은 선택을 보장해야 하면 작은 쪽을 고릅니다.

## 2. 작은 예시

두 선택지가 있다고 합시다.

```text
A: original = 10, count = 1
B: original =  7, count = 2
```

`lambda = 3`이면 둘의 relaxed score가 같습니다.

```text
A: 10 + 3 * 1 = 13
B:  7 + 3 * 2 = 13
```

이 지점이 breakpoint입니다. 이때 DP가 A를 반환하면 count는 1이고, B를 반환하면 count는 2입니다. 목표가 `K = 2`라면 같은 relaxed score라도 B를 고르는 tie-break가 필요합니다.

## 3. 답 복원 공식 점검

최소화에서 penalty를 더했다면 원래 답은 penalty를 뺍니다.

```text
original = relaxed - lambda * K
```

최대화에서 penalty를 뺐다면 원래 답은 penalty를 더합니다.

```text
original = relaxed + lambda * K
```

부호를 암기하지 말고 relaxed objective를 먼저 적은 뒤, 원래 objective만 남도록 항을 옮깁니다.

## 4. Breakpoint 주변에서 할 일

1. 이분 탐색 조건을 `count >= K`인지 `count <= K`인지 먼저 고정합니다.
2. score 동점일 때 count 방향을 이 조건과 맞춥니다.
3. 탐색 후 얻은 `lambda`에서 count가 정확히 K인지 확인합니다.
4. 정확히 K가 아니면 convex hull 보정, 인접 breakpoint 확인, 또는 원래 `K` 차원 DP가 필요한 문제인지 다시 판단합니다.

## 5. 자주 하는 실수

- tie-break 없이 pair의 첫 값만 비교합니다.
- 최소화와 최대화의 penalty 부호를 섞습니다.
- `lambda`가 실수인데 정수 이분 탐색으로 breakpoint를 놓칩니다.
- count는 단조지만 최종 objective가 단순 보정으로 복원되지 않는 문제에 억지로 적용합니다.
- count가 목표와 다르다는 사실을 무시하고 `relaxed - lambda * K`만 출력합니다.
