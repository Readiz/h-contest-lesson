# Time-Axis Model Map

오프라인/시간축 문제는 "질의를 뒤섞는다"와 "시간을 자료구조로 만든다"가 섞여 보입니다. 먼저 모델을 나누면 구현 선택이 훨씬 선명해집니다.

## 1. 네 가지 모델

| 모델 | 할 수 있는 일 | 대표 기법 | 주의점 |
| --- | --- | --- | --- |
| Offline reordering | query 순서를 바꿔 상태 이동 비용을 줄임 | Mo's Algorithm, offline sorting | 답 출력 순서를 원래 index로 되돌려야 함 |
| Offline answer search | 여러 질의의 답 후보를 동시에 좁힘 | Parallel Binary Search, divide and conquer on answer | 판정이 단조여야 함 |
| Rollback over time | 시간 구간에 update를 올리고 DFS 중 적용/복구 | segment tree over time, rollback DSU | path compression처럼 복구 어려운 최적화 금지 |
| Offline retroactivity | 과거 operation 편집을 active interval로 정리 | time tree + rollback | online fully retroactive와 다름 |

## 2. Persistence와의 차이

| 표현 | 더 가까운 구조 |
| --- | --- |
| "version v의 값을 알려 달라" | persistence |
| "이 재귀 구간에서만 update를 적용했다가 빼라" | rollback |
| "간선이 시간 l부터 r 전까지 살아 있다" | segment tree over time |
| "과거 operation을 삽입/삭제한 뒤 timeline 답을 물어본다" | retroactivity |

Persistent Segment Tree를 만들면 rollback이 자동으로 해결되는 것은 아닙니다. 반대로 Rollback DSU는 임의 version id를 빠르게 조회하기 위한 구조가 아닙니다.

## 3. 구현 전에 적을 문장

풀이를 쓰기 전에 아래 네 문장을 채우면 잘못된 기법 선택을 많이 줄일 수 있습니다.

```text
query 순서 변경: 가능 / 불가능
update 생존 구간: [l, r)로 표현 가능 / 불가능
상태 복구 방법: stack rollback / node copy / 재계산
leaf 답변 조건: 현재 상태만 필요 / 과거 history 추가 필요
```

이 네 줄 중 하나라도 애매하면 바로 구현하지 말고 모델을 다시 정해야 합니다.

## 4. 자주 하는 오독

1. online 문제를 offline으로 재정렬해도 된다고 가정한다.
2. rollback DSU에 path compression을 넣는다.
3. active interval의 오른쪽 끝을 inclusive로 처리했다가 leaf가 한 칸 밀린다.
4. query index와 논리 시간 index를 같은 배열에 섞는다.
5. persistence가 있으면 retroactive operation 삽입도 된다고 생각한다.
