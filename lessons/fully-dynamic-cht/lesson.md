# Fully Dynamic CHT

Fully Dynamic CHT는 직선 삽입, 삭제, 임의 x 질의가 모두 섞일 때 Convex Hull Trick 계열을 어떻게 선택할지 정리하는 레슨입니다. 단순 CHT나 Li Chao Tree는 삽입만 있을 때 강하지만, 삭제가 들어오면 online 자료구조보다 offline 변환이 더 안전한 경우가 많습니다.

이 레슨은 Convex Hull Trick Variants와 Kinetic Hull 이후에 보는 DP 최적화 심화입니다.

1. 삭제가 진짜 online인지, 시간 구간으로 바꿀 수 있는지 확인한다.
2. x 좌표 범위와 query 좌표를 미리 알 수 있는지 확인한다.
3. online 구현이 필요한 경우에는 precision, equal slope, rollback 비용을 먼저 정한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Convex Hull Trick Variants, Li Chao Tree, Rollback Techniques
- 함께 보면 좋은 레슨: Kinetic Hull, Parametric DP, Convex DP Modeling
- 다음에 볼 레슨: segment tree over time, dynamic Li Chao, online line container

## 1. 문제 신호

| 조건 | 추천 접근 |
| --- | --- |
| 직선의 활성 구간을 미리 알 수 있음 | segment tree over time + Li Chao |
| 삭제가 최근 삽입만 되돌림 | rollback Li Chao |
| online 삽입/삭제/질의가 강제됨 | multiset line container |
| x query 좌표가 모두 알려짐 | compressed Li Chao over time |
| 삭제 수가 작음 | rebuild 또는 small deleted buffer |

대부분의 contest 문제는 완전 online 삭제가 아니라 "각 직선이 살아 있는 시간 구간"으로 변환할 수 있습니다.

## 2. 시간 구간 변환

직선이 시간 `l`에 추가되고 시간 `r`에 삭제되면, 이 직선은 `[l, r)` 동안 활성입니다.

```text
add line A at query 2
delete line A at query 8
=> A is active on [2, 8)
```

이 구간을 query index segment tree에 넣으면 각 node에는 그 시간 범위 전체에서 살아 있는 직선만 들어갑니다. DFS로 내려가며 node의 직선을 Li Chao에 넣고, leaf query를 처리한 뒤 rollback합니다.

## 3. Segment Tree over Time Skeleton

아래 코드는 활성 구간을 segment tree node에 분배하는 부분입니다.

```cpp compile-check
#include <vector>
using namespace std;

struct Line {
    long long slope = 0;
    long long intercept = 0;
};

struct TimeSegmentTree {
    int size = 1;
    vector<vector<Line>> bucket;

    explicit TimeSegmentTree(int queryCount) {
        while (size < queryCount) {
            size <<= 1;
        }
        bucket.assign(size << 1, {});
    }

    void addInterval(int left, int right, Line line) {
        addInterval(left, right, line, 1, 0, size);
    }

    void addInterval(int left, int right, Line line, int node, int nodeLeft, int nodeRight) {
        if (right <= nodeLeft || nodeRight <= left) {
            return;
        }
        if (left <= nodeLeft && nodeRight <= right) {
            bucket[node].push_back(line);
            return;
        }
        int mid = (nodeLeft + nodeRight) / 2;
        addInterval(left, right, line, node * 2, nodeLeft, mid);
        addInterval(left, right, line, node * 2 + 1, mid, nodeRight);
    }
};
```

Li Chao rollback은 구현량이 있으므로, 먼저 "구간 분배가 맞는지"를 독립적으로 테스트하는 편이 좋습니다.

## 4. Rollback Li Chao 관점

DFS 중 node에 들어 있는 직선을 삽입했다가, 자식 처리가 끝나면 삽입 전 상태로 되돌립니다.

```text
enter node:
  save changes stack size
  insert all node lines
  recurse children or answer leaf
  rollback to saved stack size
```

동적 node Li Chao에서는 새 node 생성, 기존 line 교체, child pointer 변경을 모두 change log에 남겨야 합니다.

## 5. Online Line Container

정말로 online 삭제가 필요하면 multiset 기반 lower hull을 유지하는 구현이 후보입니다. 각 직선이 최적인 x 구간의 시작점을 저장하고, 삽입/삭제 시 주변 교점을 갱신합니다.

| 장점 | 단점 |
| --- | --- |
| online 삽입/삭제 가능 | 구현이 길고 tie 처리가 어렵다 |
| x 범위가 없어도 됨 | 정수 나눗셈 floor/ceil 오류가 잦다 |
| amortized `O(log N)` 기대 | 같은 slope, duplicate line 삭제가 까다롭다 |

삭제가 문제의 핵심이 아니라면 offline으로 바꾸는 편이 더 안정적입니다.

## 6. 작은 예시

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

## 7. 삭제가 작을 때

삭제가 드물다면 완전 동적 구조보다 rebuild가 더 쉽습니다.

```text
base lines: 삭제되지 않은 대부분의 직선
buffer lines: 최근 추가/삭제가 얽힌 작은 집합
query: base structure answer + buffer scan
periodically rebuild
```

복잡도는 보통 `O((N/B) rebuild + B scan)` 식으로 조절합니다. 구현 난도를 낮추고 싶을 때 실용적인 선택입니다.

## 8. 구현 전 결정표

| 질문 | 답이 yes면 |
| --- | --- |
| 모든 연산을 미리 읽을 수 있는가? | segment tree over time |
| query x가 모두 알려져 있는가? | compressed Li Chao |
| 삭제가 LIFO인가? | rollback stack |
| 삭제가 거의 없는가? | rebuild |
| 진짜 online인가? | line container 검토 |

이 표에서 위쪽일수록 구현이 단순하고 검증하기 쉽습니다.

## 9. 자주 하는 실수

1. 삭제를 처리하려고 Li Chao node에서 직선을 직접 제거한다.
2. 활성 구간의 오른쪽 끝을 inclusive로 처리해 삭제된 직선이 query에 남는다.
3. rollback change log에 child pointer 변경을 기록하지 않는다.
4. 같은 slope 직선을 여러 개 넣고 삭제할 때 identity를 잃는다.
5. max/min convention을 offline과 online 구현에서 다르게 둔다.
6. 모든 query를 읽을 수 있는데도 online container부터 구현한다.

## 10. 문제를 볼 때 체크할 조건

- 직선의 생존 구간을 query index로 만들 수 있는가?
- x 좌표가 정수 범위인지, 압축 가능한지 확인했는가?
- 삭제되는 대상의 identity가 명확한가?
- 최솟값과 최댓값 convention을 통일했는가?
- rollback해야 하는 mutation 목록을 빠짐없이 기록했는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: offline dynamic CHT `/practice/...` 문제 필요 | add/delete를 활성 구간으로 변환 | segment tree over time |
| 표준 | TODO: rollback Li Chao `/practice/...` 문제 필요 | DFS rollback 구현 | change log |
| 응용 | TODO: online line container `/practice/...` 문제 필요 | 임의 삭제와 query 처리 | multiset hull |
| 함정 | TODO: duplicate line deletion `/practice/...` 문제 필요 | 같은 slope와 identity 관리 | tie-breaking |
