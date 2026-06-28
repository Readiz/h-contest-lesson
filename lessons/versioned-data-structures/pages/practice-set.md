# Practice Set

Versioned Data Structures 허브의 연습은 path copying, partial persistence, container versioning, sequence query 순서로 진행합니다. 실제 h-contest 문제가 아직 부족한 주제는 임의 ID를 만들지 않고 `TODO`로 남깁니다.

## 1. 연습 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 버전별 구간 합 `/practice/...` 문제 필요 | path copying과 root 저장 | persistent segment tree |
| 표준 | [Range Kth with Prefix Roots](#3-로컬-연습-range-kth-with-prefix-roots) | prefix root 차이와 좌표 압축 | order statistic |
| 응용 | TODO: persistent union-find `/practice/...` 문제 필요 | 과거 연결성 조회 | union time |
| 심화 | TODO: persistent sequence `/practice/...` 문제 필요 | split/merge 또는 version root 관리 | implicit treap |
| 함정 | TODO: rollback vs persistence `/practice/...` 문제 필요 | version branch와 undo log 구분 | rollback |

## 2. Trace: prefix root 차이

정적 배열이 아래와 같다고 하겠습니다.

```text
A = [4, 1, 4, 2]
```

값을 압축하면 `1 -> 0`, `2 -> 1`, `4 -> 2`입니다. `root[i]`는 prefix `A[1..i]`의 빈도 persistent segment tree입니다.

| root | 담긴 값 | compressed frequency |
| --- | --- | --- |
| `root[0]` | empty | `[0, 0, 0]` |
| `root[1]` | `4` | `[0, 0, 1]` |
| `root[2]` | `4, 1` | `[1, 0, 1]` |
| `root[3]` | `4, 1, 4` | `[1, 0, 2]` |
| `root[4]` | `4, 1, 4, 2` | `[1, 1, 2]` |

query `[2, 4]`의 2번째 작은 값은 `root[4] - root[1]`로 봅니다.

```text
root[4] - root[1] = [1, 1, 1]
```

왼쪽 절반 `1, 2`에 2개가 있으므로 그쪽으로 내려갑니다. 그 안에서 `1`의 count는 1이고 `k=2`이므로 `2`로 이동합니다. 답은 원래 값 `2`입니다.

이 방식은 node를 직접 빼는 것이 아니라, 같은 구간을 가리키는 두 root의 count 차이를 내려가며 보는 것입니다. 그래서 old root를 수정하면 모든 query가 깨집니다.

## 3. 로컬 연습: Range Kth with Prefix Roots

### 입력

정적 배열 `A`와 `Q`개의 구간 kth query가 주어집니다.

```text
N Q
A1 A2 ... AN
l1 r1 k1
...
lQ rQ kQ
```

`l`, `r`은 1-based inclusive입니다. 각 query는 `A[l..r]`에서 `k`번째로 작은 값을 출력합니다.

### 출력

각 query마다 답을 한 줄에 출력합니다.

### 제한

- `1 <= N, Q <= 200000`
- `-10^9 <= Ai <= 10^9`
- `1 <= l <= r <= N`
- `1 <= k <= r - l + 1`

### 예시

```text
5 3
5 1 4 2 3
2 5 2
1 3 3
3 5 1
```

```text
2
5
2
```

첫 query의 구간은 `[1, 4, 2, 3]`이고 정렬하면 `[1, 2, 3, 4]`라서 2번째 값은 `2`입니다.

### 풀이 기준

1. 모든 `Ai`를 좌표 압축한다.
2. `root[0]`은 빈 segment tree다.
3. `root[i] = update(root[i-1], compressed(Ai), +1)`로 prefix root를 만든다.
4. query `(l, r, k)`는 `kth(root[r], root[l-1], k)`로 답한다.
5. compressed index를 원래 값으로 복원한다.

`update`는 지나가는 node만 clone합니다. 범위 밖 child pointer는 old node를 그대로 공유합니다. 전체 node 수는 대략 `N * (log uniqueValues + 1)`이므로, `N=200000`이면 메모리 예산을 먼저 계산해야 합니다.

### kth 내려가기

각 node에서 왼쪽 count 차이를 봅니다.

```text
leftCount = count(leftChild(rootR)) - count(leftChild(rootLMinusOne))
if k <= leftCount:
    go left
else:
    k -= leftCount
    go right
```

leaf에 도착하면 그 leaf의 compressed index가 답입니다.

### Stress 검증

작은 입력에서는 query마다 slice를 복사해 정렬하는 baseline과 비교합니다.

```text
for seed in 1..1000:
    random array and valid kth queries
    answer_persistent = prefix root kth
    answer_naive = sorted(A[l..r])[k-1]
    assert answer_persistent == answer_naive
```

중복 값이 있는 배열을 반드시 포함합니다. 좌표 압축을 값의 등장 횟수가 아니라 distinct value 기준으로 해야 한다는 점을 확인하기 좋습니다.

## 4. 다른 로컬 완결형 연습 후보

### Versioned Array Sum

초기 배열에 point update를 적용할 때마다 새 version을 만들고, `(version, l, r)` 질의에 range sum을 답합니다. old node를 직접 수정하지 않는지 root별로 비교합니다.

### Union History Query

간선 추가만 있는 그래프에서 time `t`의 연결성과 component size를 묻습니다. path compression 없이 union by size와 parent change time을 사용합니다.

## 5. 제출 전 체크리스트

- version root를 덮어쓰지 않았는가?
- old node를 직접 수정하지 않았는가?
- node 수 메모리 예산을 계산했는가?
- query가 read-only여야 하는 구조에서 lazy push가 상태를 바꾸지 않는가?
- rollback으로 더 단순해지는 문제를 persistent로 과하게 풀지 않았는가?
