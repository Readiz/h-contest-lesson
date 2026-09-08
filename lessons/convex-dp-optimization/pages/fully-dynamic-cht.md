# Fully Dynamic CHT

Fully Dynamic CHT는 직선 삽입, 삭제, 임의 x 질의가 모두 섞일 때 Convex Hull Trick 계열을 어떻게 선택할지 정리하는 레슨입니다. 단순 CHT나 Li Chao Tree는 삽입만 있을 때 강하지만, 삭제가 들어오면 online 자료구조보다 offline 변환이 더 안전한 경우가 많습니다.

## 문제 신호

| 조건 | 추천 접근 |
| --- | --- |
| 직선의 활성 구간을 미리 알 수 있음 | segment tree over time + Li Chao |
| 삭제가 최근 삽입만 되돌림 | rollback Li Chao |
| online 삽입/삭제/질의가 강제됨 | 임의 삭제를 지원하는 별도 동적 hull |
| x query 좌표가 모두 알려짐 | compressed Li Chao over time |
| 삭제 수가 작음 | rebuild 또는 small deleted buffer |

대부분의 contest 문제는 완전 online 삭제가 아니라 "각 직선이 살아 있는 시간 구간"으로 변환할 수 있습니다.

## 시간 구간 변환

직선이 시간 `l`에 추가되고 시간 `r`에 삭제되면, 이 직선은 `[l, r)` 동안 활성입니다.

```text
add line A at query 2
delete line A at query 8
=> A is active on [2, 8)
```

이 구간을 query index segment tree에 넣으면 각 node에는 그 시간 범위 전체에서 살아 있는 직선만 들어갑니다. DFS로 내려가며 node의 직선을 Li Chao에 넣고, leaf query를 처리한 뒤 rollback합니다.

## 시간축 구간 저장

구간을 Segment Tree 노드에 나누는 구현은 [Dynamic Connectivity](https://h.readiz.com/learn/offline-time-axis-techniques/dynamic-connectivity)의 활성 간선 저장과 같습니다. 저장 대상을 edge에서 line으로 바꾸되, DFS가 쓰는 자료구조는 아래의 rollback Li Chao 계약을 만족해야 합니다.

## Rollback Li Chao 관점

DFS 중 node에 들어 있는 직선을 삽입했다가, 자식 처리가 끝나면 삽입 전 상태로 되돌립니다.

```text
enter node:
  save changes stack size
  insert all node lines
  recurse children or answer leaf
  rollback to saved stack size
```

동적 node Li Chao에서는 새 node 생성, 기존 line 교체, child pointer 변경을 모두 change log에 남겨야 합니다.

## 삽입 전용 hull에서 삭제할 수 없는 이유

삽입 전용 hull은 새 직선에 항상 밀리는 기존 직선을 버릴 수 있습니다. 나중에 새 직선을 삭제하면 버렸던 직선이 다시 최적 후보가 될 수 있으므로, 단순 `erase`만으로 임의 삭제를 지원하지 못합니다. 예를 들어 최대 질의에서 `y=0`을 넣은 뒤 `y=1`을 넣으면 전자가 가려지지만, 후자를 삭제하면 전자가 다시 필요합니다.

[KACTL LineContainer](https://github.com/kth-competitive-programming/kactl/blob/main/content/data-structures/LineContainer.h)도 삽입과 최대 질의를 위한 구현입니다. 임의 삭제를 요구하면 별도의 fully dynamic 구조가 필요합니다. 전체 연산을 미리 읽을 수 있을 때는 위 시간축 변환을 사용할 수 있습니다.

## 작은 예시

```text
1: add A
2: query x=3
3: add B
4: delete A
5: query x=5
6: delete B

A active: [1, 4)
B active: [3, 6)
```

query 2에서는 A만 보이고, query 5에서는 B만 보입니다. Segment tree over time은 이 사실을 query index 구간으로 보존합니다.

## 삭제가 작을 때

삽입 전용 base hull에서 삭제된 최적 직선을 buffer로 가리는 것은 불가능합니다. 삭제마다 활성 직선 전체로 재구축하거나, 연산을 미리 아는 block에서는 그 block 중 바뀔 직선을 모두 base에서 제외합니다. 남은 고정 base와 현재 활성 buffer의 답 중 좋은 값을 택합니다. 재구축과 buffer 스캔 비용을 실제 크기로 계산합니다.

## 구현 전 결정표

| 질문 | 답이 yes면 |
| --- | --- |
| 모든 연산을 미리 읽을 수 있는가? | segment tree over time |
| query x가 모두 알려져 있는가? | compressed Li Chao |
| 삭제가 LIFO인가? | rollback stack |
| 삭제가 거의 없는가? | rebuild |
| 진짜 online인가? | 별도 동적 hull 검토 |

이 표에서 위쪽일수록 구현이 단순하고 검증하기 쉽습니다.
