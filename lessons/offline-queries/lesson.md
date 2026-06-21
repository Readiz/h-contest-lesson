# 오프라인 쿼리: Mo, DSU Rollback, Parallel Binary Search

오프라인 쿼리는 모든 질의를 먼저 읽어 둔 뒤, 답하기 좋은 순서로 재배열하거나 여러 질의를 한꺼번에 처리하는 기법입니다. 온라인으로 들어오는 즉시 답해야 하는 문제와 달리, 전체 입력을 알고 있다는 점을 이용합니다.

이 레슨은 대표적인 세 방향을 묶어 봅니다.

| 기법 | 핵심 감각 | 자주 쓰는 상황 |
| --- | --- | --- |
| Mo's Algorithm | 구간 질의를 이동 비용이 작게 정렬한다 | 배열의 정적 구간 질의 |
| DSU Rollback | Union-Find 변경을 되돌릴 수 있게 저장한다 | 시간 구간별 간선 추가/삭제, divide and conquer on time |
| Parallel Binary Search | 여러 질의의 답을 동시에 이분 탐색한다 | 답의 단조성이 있고 업데이트 prefix를 반복 적용할 수 있음 |

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 정렬, Sqrt Decomposition, Union-Find, 이분 탐색
- 함께 보면 좋은 레슨: Sqrt Decomposition, Fenwick Tree, Segment Tree
- 다음에 볼 레슨: Persistent Segment Tree, Divide and Conquer Optimization

## 1. 오프라인으로 바꾸는 이유

질의가 `q`개 있고 각 질의를 독립적으로 처리하면 `O(qn)`이 되는 경우가 많습니다. 하지만 질의를 재정렬하면 이전 질의에서 계산한 상태를 다음 질의에 재사용할 수 있습니다.

오프라인 처리가 가능한지 먼저 확인해야 합니다.

1. 모든 질의를 미리 알고 있는가?
2. 출력 순서는 원래 질의 순서로 되돌릴 수 있는가?
3. 질의 사이에 상태가 독립적인가, 아니면 시간 순서가 의미를 가지는가?
4. 업데이트를 재정렬해도 되는가, 또는 rollback으로 되돌릴 수 있는가?

오프라인 기법은 강력하지만 문제 조건을 바꿔 버리면 안 됩니다. 특히 "이전 질의의 답이 다음 입력에 영향을 주는" 상호작용형 구조에는 쓸 수 없습니다.

## 2. Mo's Algorithm

Mo's Algorithm은 정적 배열의 구간 질의를 `sqrt(n)` 블록 기준으로 정렬합니다. 현재 구간 `[curL, curR]`을 유지하고, 다음 질의의 구간으로 포인터를 움직이며 원소를 추가/삭제합니다.

대표 정렬 기준은 아래와 같습니다.

```text
left block 오름차순
같은 block 안에서는 right 오름차순 또는 지그재그 정렬
```

```cpp compile-check
#include <algorithm>
#include <cmath>
#include <vector>
using namespace std;

struct Query {
    int left;
    int right;
    int index;
};

vector<long long> solveMo(const vector<int>& values, vector<Query> queries) {
    int n = (int)values.size();
    int block = max(1, (int)sqrt(n));
    sort(queries.begin(), queries.end(), [block](const Query& a, const Query& b) {
        int blockA = a.left / block;
        int blockB = b.left / block;
        if (blockA != blockB) return blockA < blockB;
        if (blockA & 1) return a.right > b.right;
        return a.right < b.right;
    });

    vector<long long> answer(queries.size(), 0);
    long long currentSum = 0;
    int curL = 0;
    int curR = -1;

    auto add = [&](int pos) {
        currentSum += values[pos];
    };
    auto remove = [&](int pos) {
        currentSum -= values[pos];
    };

    for (const Query& query : queries) {
        while (curL > query.left) add(--curL);
        while (curR < query.right) add(++curR);
        while (curL < query.left) remove(curL++);
        while (curR > query.right) remove(curR--);
        answer[query.index] = currentSum;
    }
    return answer;
}
```

위 예시는 구간 합이라 Fenwick Tree로도 풀 수 있지만, Mo의 구조를 보여 주기 쉽습니다. 실제로는 distinct count, 빈도 기반 점수, 최빈값 후보처럼 add/remove로 상태를 유지할 수 있는 질의에 자주 씁니다.

## 3. DSU Rollback

일반 Union-Find는 경로 압축을 쓰면 되돌리기 어렵습니다. DSU Rollback은 union 전의 정보를 스택에 저장해 두고, 필요할 때 snapshot 지점까지 되돌립니다.

```cpp compile-check
#include <numeric>
#include <vector>
using namespace std;

struct RollbackDSU {
    vector<int> parent;
    vector<int> size;
    vector<pair<int, int>> history;
    int components;

    explicit RollbackDSU(int n) : parent(n), size(n, 1), components(n) {
        iota(parent.begin(), parent.end(), 0);
    }

    int find(int x) const {
        while (parent[x] != x) {
            x = parent[x];
        }
        return x;
    }

    int snapshot() const {
        return (int)history.size();
    }

    bool unite(int a, int b) {
        a = find(a);
        b = find(b);
        if (a == b) {
            history.push_back({-1, -1});
            return false;
        }
        if (size[a] < size[b]) {
            swap(a, b);
        }
        history.push_back({b, size[a]});
        parent[b] = a;
        size[a] += size[b];
        --components;
        return true;
    }

    void rollback(int checkpoint) {
        while ((int)history.size() > checkpoint) {
            auto [child, oldSize] = history.back();
            history.pop_back();
            if (child == -1) {
                continue;
            }
            int root = parent[child];
            size[root] = oldSize;
            parent[child] = child;
            ++components;
        }
    }
};
```

rollback DSU에서는 경로 압축을 쓰지 않습니다. 대신 union by size/rank로 트리 높이를 관리합니다. 시간 구간 세그먼트 트리와 함께 쓰면 "어떤 간선이 여러 시간 구간 동안 살아 있다"는 문제를 처리할 수 있습니다.

## 4. Parallel Binary Search

Parallel Binary Search는 여러 질의의 답을 각각 이분 탐색하되, 같은 mid를 가진 질의를 모아 한 번의 업데이트 sweep으로 처리하는 기법입니다.

적용 신호는 아래와 같습니다.

1. 각 질의의 답이 어떤 최소 시점/최소 값이다.
2. `mid`까지 업데이트를 적용했을 때 조건 만족 여부를 판정할 수 있다.
3. 만족 여부가 단조적이다.
4. 업데이트를 처음부터 순서대로 적용하는 비용을 여러 질의가 공유할 수 있다.

예를 들어 "몇 번째 업데이트 이후에 각 질의가 처음 만족되는가" 같은 문제에서 자주 등장합니다. 각 질의를 따로 이분 탐색하면 매번 업데이트를 다시 적용해야 하지만, PBS는 같은 라운드의 질의를 mid 기준으로 묶어서 처리합니다.

## 5. 세 기법 비교

| 문제 구조 | 우선 후보 |
| --- | --- |
| 정적 배열 구간 질의, add/remove 가능 | Mo's Algorithm |
| 시간에 따라 간선이 생기고 사라짐 | Segment tree over time + DSU rollback |
| 여러 질의의 최소 만족 시점 | Parallel Binary Search |
| 업데이트와 질의가 섞인 prefix 구조 | Fenwick/Segment + PBS |
| 질의가 들어오는 즉시 답해야 함 | 오프라인 재정렬 불가 |

오프라인 쿼리는 "답하기 좋은 순서"를 설계하는 문제입니다. 어떤 순서로 처리해도 원래 답이 보존되는지 먼저 증명해야 합니다.

## 6. 시간 복잡도 감각

| 기법 | 대표 복잡도 |
| --- | ---: |
| Mo's Algorithm | 보통 `O((n + q) sqrt n * add/remove 비용)` |
| DSU Rollback + time segment tree | `O((m log q) alpha(n))`에 가까운 union 비용 |
| Parallel Binary Search | 라운드 수 `O(log answer)` 곱하기 각 라운드 처리 비용 |

상수도 중요합니다. Mo는 포인터 이동이 많고, rollback DSU는 구현이 길며, PBS는 매 라운드 상태 초기화 비용을 잘 잡아야 합니다.

## 7. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 오프라인 재정렬이 가능한지 확인하지 않음 | 문제 의미 변경 | 질의 독립성 확인 |
| Mo에서 답을 정렬된 순서로 출력 | 출력 순서 오답 | `index`로 원래 위치에 저장 |
| add/remove가 서로 역연산이 아님 | 상태 누적 오류 | 작은 구간 이동으로 테스트 |
| rollback DSU에서 경로 압축 사용 | rollback 불가능 | find는 압축 없이 구현 |
| rollback checkpoint를 저장하지 않음 | 다른 분기 상태 오염 | DFS 진입 전 snapshot |
| PBS의 단조성 조건을 착각 | 이분 탐색 방향 오류 | true/false 경계 정의 |

## 8. 문제를 볼 때 체크할 조건

1. 모든 질의를 미리 읽고 순서를 바꿀 수 있는가?
2. 구간을 조금씩 움직이며 상태를 유지할 수 있는가?
3. 업데이트의 시간 구간을 나눠서 처리할 수 있는가?
4. 각 질의의 답이 단조 조건의 경계인가?
5. 출력은 원래 질의 순서로 복원해야 하는가?
6. 상태 초기화 비용이 전체 복잡도에 포함되어 있는가?

정리하면, 오프라인 쿼리는 자료구조 하나가 아니라 처리 순서 설계입니다. Mo는 공간 이동을 줄이고, rollback은 시간 분기를 되돌리고, PBS는 여러 이분 탐색을 한꺼번에 진행합니다.

## 9. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 정적 배열 구간 질의를 Mo로 처리하는 문제 추가 | 질의 정렬과 원래 순서 복원 | Mo's algorithm |
| 표준 | TODO: 동적 연결성 오프라인 문제 추가 | 시간 구간 세그먼트 트리와 rollback DSU | DSU rollback |
| 응용 | TODO: 여러 질의의 최초 만족 시점 문제 추가 | Parallel Binary Search 라운드 처리 | PBS, monotonicity |
| 함정 | TODO: 온라인 순서가 의미 있는 질의 문제 추가 | 오프라인 재정렬 불가 조건 판별 | online vs offline |
