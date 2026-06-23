# Offline Range Query Techniques

Offline Range Query Techniques는 정적 배열과 구간 질의가 섞인 문제에서 질의 순서를 바꾸거나 시간축을 나눠서 전체 비용을 줄이는 레슨입니다. 기본 Offline Queries 레슨이 Mo, rollback, parallel binary search의 큰 그림을 다뤘다면, 여기서는 배열 구간 질의에서 add/remove 상태를 어떻게 설계하고 어떤 변형을 고를지에 집중합니다.

이 레슨은 Offline Queries, Sqrt Decomposition 이후에 보는 자료구조 심화입니다.

1. add/remove가 가능한 구간 상태를 먼저 정의한다.
2. 업데이트가 없으면 Mo ordering, 업데이트가 있으면 time dimension을 추가한다.
3. 질의 답이 merge 가능하면 divide and conquer on queries나 offline Fenwick으로 바꾼다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Offline Queries, Sqrt Decomposition, Fenwick Tree, frequency table
- 함께 보면 좋은 레슨: Offline Queries, Sqrt Decomposition, Rollback Techniques
- 다음에 볼 레슨: persistent segment tree, retroactive data structures, range query lower bounds

## 1. 문제 신호

| 문제 표현 | 우선 후보 |
| --- | --- |
| 배열은 고정이고 `l, r` 질의가 많다 | Mo's Algorithm |
| 구간을 움직일 때 값 하나를 넣고 빼면 답이 갱신된다 | add/remove 상태 설계 |
| point update와 range query가 함께 있다 | Mo with modifications 또는 offline divide and conquer |
| `k`번째 update 이후 답을 묻는다 | time dimension 또는 parallel binary search |
| 질의가 `value <= x` 같은 prefix 조건이다 | offline sorting + Fenwick |

핵심은 "구간 답을 다시 계산하지 않고 다음 질의로 이동할 수 있는가"입니다. add/remove가 `O(1)` 또는 `O(log V)`로 가능하면 Mo 계열이 강합니다.

## 2. Add/Remove 상태 설계

Mo를 적용하기 전에는 현재 구간의 상태가 어떤 변수로 유지되는지 적어야 합니다.

```text
current range [L, R]
add(pos): a[pos]가 구간에 들어올 때 상태 갱신
remove(pos): a[pos]가 구간에서 빠질 때 상태 갱신
answer(): 현재 상태에서 질의 답 반환
```

예를 들어 서로 다른 값 개수는 frequency가 0에서 1로 바뀌는 순간만 세면 됩니다.

| 답 | 상태 |
| --- | --- |
| distinct count | `freq[value]`, `distinct` |
| pair count | `freq[value]`, `sum C(freq, 2)` |
| 구간 mode 후보 | block frequency, value bucket |
| xor sum | 현재 xor |

add와 remove가 정확히 역연산이어야 합니다. 한쪽에서만 보조 변수를 갱신하면 다음 질의부터 상태가 누적되어 틀립니다.

## 3. 기본 Mo 구현

아래 코드는 구간의 distinct count를 답하는 기본 Mo skeleton입니다.

```cpp compile-check
#include <algorithm>
#include <cmath>
#include <vector>
using namespace std;

struct RangeQuery {
    int left = 0;
    int right = 0;
    int index = 0;
};

vector<int> distinctCountMo(const vector<int>& compressed, vector<RangeQuery> queries) {
    int n = (int)compressed.size();
    int block = max(1, (int)sqrt(max(1, n)));
    sort(queries.begin(), queries.end(), [block](const RangeQuery& a, const RangeQuery& b) {
        int blockA = a.left / block;
        int blockB = b.left / block;
        if (blockA != blockB) {
            return blockA < blockB;
        }
        if (blockA & 1) {
            return a.right > b.right;
        }
        return a.right < b.right;
    });

    int valueCount = 0;
    for (int value : compressed) {
        valueCount = max(valueCount, value + 1);
    }

    vector<int> frequency(valueCount, 0);
    vector<int> answer(queries.size(), 0);
    int distinct = 0;
    int currentLeft = 0;
    int currentRight = -1;

    auto add = [&](int position) {
        int value = compressed[position];
        if (frequency[value] == 0) {
            ++distinct;
        }
        ++frequency[value];
    };

    auto remove = [&](int position) {
        int value = compressed[position];
        --frequency[value];
        if (frequency[value] == 0) {
            --distinct;
        }
    };

    for (const RangeQuery& query : queries) {
        while (currentLeft > query.left) {
            add(--currentLeft);
        }
        while (currentRight < query.right) {
            add(++currentRight);
        }
        while (currentLeft < query.left) {
            remove(currentLeft++);
        }
        while (currentRight > query.right) {
            remove(currentRight--);
        }
        answer[query.index] = distinct;
    }

    return answer;
}
```

값이 크면 좌표 압축을 먼저 합니다. 빈도 배열 대신 hash map을 쓰면 상수가 커지므로 가능한 한 압축하는 편이 좋습니다.

## 4. Mo With Modifications

point update가 섞이면 질의에 세 번째 좌표인 time이 생깁니다.

```text
query(l, r, t)
t = 이 질의보다 앞에 적용된 update 개수
```

정렬은 보통 `left block`, `right block`, `time` 순서로 잡습니다. 현재 구간을 움직이는 add/remove와 별개로, 현재 time을 움직이는 apply/undo update가 필요합니다.

| 함수 | 역할 |
| --- | --- |
| `add(pos)` | 현재 배열 값이 구간에 들어옴 |
| `remove(pos)` | 현재 배열 값이 구간에서 빠짐 |
| `applyUpdate(id)` | 배열 값을 새 값으로 바꿈 |
| `undoUpdate(id)` | 배열 값을 이전 값으로 되돌림 |

update 대상 위치가 현재 구간 안에 있으면 remove old, add new를 같이 해야 합니다. 구간 밖이면 배열 값만 바꾸면 됩니다.

## 5. Offline Sorting + Fenwick

모든 range query가 Mo에 맞는 것은 아닙니다. 예를 들어 "`[l, r]` 안에서 값이 `x` 이하인 원소 개수"는 질의를 `x` 오름차순으로 정렬하고 Fenwick Tree에 원소를 하나씩 넣으면 됩니다.

```text
values를 value 오름차순 정렬
queries를 x 오름차순 정렬
value <= x인 index를 Fenwick에 1로 추가
answer = sum(r) - sum(l-1)
```

이 방식은 add/remove보다 단조 sweep이 더 자연스러운 경우입니다. 질의 조건이 prefix 형태이면 Mo보다 간단하고 빠릅니다.

## 6. Divide and Conquer on Queries

질의 답이 "최소 mid"이고 조건 판정이 update prefix에 대해 단조라면 parallel binary search나 divide and conquer on answer를 씁니다.

```text
solve(query set, answer range)
  mid 기준으로 update를 적용
  만족하는 질의는 왼쪽 답 범위로
  불만족 질의는 오른쪽 답 범위로
```

이때 업데이트를 되돌릴 수 있는지, 아니면 매 단계마다 새로 sweep할지에 따라 구현이 달라집니다. rollback 가능한 상태라면 재귀가 편하고, Fenwick처럼 초기화가 싼 구조라면 라운드별 재구성이 더 단순합니다.

## 7. 작은 예시

```text
array: 1 2 1 3 2
queries:
  Q0 [0, 2] distinct = 2
  Q1 [1, 4] distinct = 3
  Q2 [2, 4] distinct = 3

Mo order가 Q0 -> Q2 -> Q1이면
  [0,2]에서 시작
  left를 2로 이동하며 1,2 제거
  right를 4로 이동하며 3,2 추가
  다시 left를 1로 줄이며 2 추가
```

각 이동에서 distinct가 어떻게 변하는지 손으로 따라가면 add/remove가 서로 맞는지 바로 보입니다.

## 8. 시간 복잡도 감각

| 기법 | 대표 복잡도 |
| --- | ---: |
| 기본 Mo | `O((N + Q) sqrt N * add/remove)` |
| Mo with modifications | 보통 `O((N + Q)^(2/3) Q)` 계열의 튜닝 필요 |
| offline sorting + Fenwick | `O((N + Q) log N)` |
| parallel binary search | `O((update cost + query cost) log answer)` |

Mo는 상수가 큽니다. Fenwick이나 Segment Tree sweep으로 풀리는 문제를 굳이 Mo로 바꾸지 않습니다.

## 9. 자주 하는 실수

1. 구간을 `[l, r]`로 둘지 `[l, r)`로 둘지 섞는다.
2. 좌표 압축 전 값을 frequency index로 바로 쓴다.
3. Mo with modifications에서 구간 안 update와 구간 밖 update를 구분하지 않는다.
4. 원래 출력 순서를 저장하지 않아 정렬된 순서로 답을 낸다.
5. add/remove가 역연산인지 작은 예시로 검증하지 않는다.
6. offline sorting으로 더 쉽게 풀 문제를 Mo로 구현해 시간 제한을 잃는다.

## 10. 문제를 볼 때 체크할 조건

- 모든 질의를 미리 알고 있는가?
- 구간 포인터 이동이 원래 답을 보존하는가?
- add/remove가 충분히 빠르고 정확한가?
- update가 있다면 time을 되돌릴 수 있는가?
- 질의 조건이 value나 time prefix라면 Fenwick sweep으로 더 단순하지 않은가?
- 답을 원래 query index로 복원하는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: offline range distinct `/practice/...` 문제 필요 | add/remove 상태 설계 | Mo, frequency |
| 표준 | TODO: value threshold range query `/practice/...` 문제 필요 | offline sorting + Fenwick | prefix sweep |
| 응용 | TODO: range query with updates `/practice/...` 문제 필요 | time dimension 처리 | Mo with modifications |
| 함정 | TODO: online-dependent query `/practice/...` 문제 필요 | 오프라인 불가 판정 | query dependency |
