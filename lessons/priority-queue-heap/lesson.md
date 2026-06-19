# 우선순위 큐와 힙

우선순위 큐는 "지금 가장 우선순위가 높은 원소"를 빠르게 꺼내는 자료구조입니다. 일반 큐는 먼저 들어온 원소가 먼저 나오지만, 우선순위 큐는 값이나 조건에 따라 먼저 나올 원소가 정해집니다.

```text
가장 작은 비용의 작업을 먼저 처리한다.
마감이 급한 일을 먼저 꺼낸다.
현재까지 본 값 중 가장 큰 K개만 유지한다.
Dijkstra에서 가장 짧은 후보 정점을 먼저 확정한다.
```

C++의 `priority_queue`는 기본적으로 가장 큰 값이 먼저 나오는 max-heap입니다. 작은 값을 먼저 꺼내려면 비교 기준을 바꾸어 min-heap으로 사용합니다.

## 1. 언제 필요한가

정렬을 한 번만 하고 끝나는 문제라면 `sort`가 충분합니다. 하지만 중간에 원소가 계속 들어오고, 그때마다 최댓값이나 최솟값을 꺼내야 한다면 우선순위 큐가 필요합니다.

```text
1. 후보가 계속 추가된다.
2. 매번 가장 좋은 후보를 꺼낸다.
3. 꺼낸 뒤 상태가 바뀌며 새 후보가 생긴다.
```

이런 흐름은 그리디, 스케줄링, 시뮬레이션, 최단거리에서 자주 나옵니다.

예를 들어 모든 값을 정렬한 뒤 하나씩 꺼낼 수 있다면 `O(n log n)`입니다. 우선순위 큐도 모든 값을 넣고 모두 꺼내면 `O(n log n)`입니다. 차이는 온라인 상황입니다. 값을 하나씩 받으면서 현재 최댓값을 계속 알아야 하면 우선순위 큐가 자연스럽습니다.

## 2. 힙의 핵심 아이디어

우선순위 큐는 보통 binary heap으로 구현합니다. 힙은 완전 이진 트리 모양을 배열에 담고, 부모가 자식보다 우선순위가 높다는 조건을 유지합니다.

max-heap에서는 부모가 자식보다 크거나 같습니다.

```text
        10
      /    \
     7      9
    / \    /
   1   3  4
```

루트에는 항상 최댓값이 있습니다. 그래서 최댓값 조회는 `O(1)`입니다. 삽입과 삭제는 트리 높이만큼 위아래로 이동하므로 `O(log n)`입니다.

배열로 저장할 때 0-indexed 기준으로 관계는 아래와 같습니다.

```text
parent(i) = (i - 1) / 2
left(i) = 2 * i + 1
right(i) = 2 * i + 2
```

직접 힙을 구현할 일은 많지 않지만, 이 구조를 알아두면 `priority_queue`의 시간 복잡도와 동작을 이해하기 쉽습니다.

## 3. 기본 priority_queue

C++의 `priority_queue<int>`는 가장 큰 값부터 꺼냅니다.

```cpp
#include <iostream>
#include <queue>
using namespace std;

int main() {
    priority_queue<int> pq;

    pq.push(3);
    pq.push(10);
    pq.push(1);

    while (!pq.empty()) {
        cout << pq.top() << '\n';
        pq.pop();
    }
}
```

출력은 `10, 3, 1` 순서입니다.

| 연산 | 의미 | 시간 |
| --- | --- | --- |
| `push(x)` | 원소 추가 | `O(log n)` |
| `top()` | 가장 우선순위 높은 원소 조회 | `O(1)` |
| `pop()` | 가장 우선순위 높은 원소 제거 | `O(log n)` |
| `empty()` | 비었는지 확인 | `O(1)` |

`pop()`은 값을 반환하지 않습니다. 값을 쓰려면 `top()`으로 먼저 읽고 `pop()`을 호출합니다.

## 4. min-heap 만들기

가장 작은 값부터 꺼내려면 `greater<int>`를 사용합니다.

```cpp
#include <functional>
#include <queue>
#include <vector>
using namespace std;

priority_queue<int, vector<int>, greater<int>> pq;
```

세 번째 템플릿 인자가 비교 함수입니다. 두 번째 인자인 `vector<int>`는 내부 컨테이너 타입입니다. min-heap을 만들 때는 이 두 인자를 함께 적어야 합니다.

```cpp
pq.push(3);
pq.push(10);
pq.push(1);

int smallest = pq.top(); // 1
```

최솟값을 자주 꺼내는 문제에서는 min-heap이 기본입니다.

## 5. pair와 tuple 우선순위

`pair`는 사전순으로 비교됩니다. 먼저 `first`를 비교하고, 같으면 `second`를 비교합니다.

```cpp
priority_queue<pair<int, int>> pq;

pq.push({5, 100});
pq.push({5, 20});
pq.push({7, 1});
```

max-heap에서는 `{7, 1}`이 먼저 나오고, 그다음 `{5, 100}`, `{5, 20}` 순서입니다.

min-heap도 같은 기준을 반대로 씁니다.

```cpp
priority_queue<
    pair<int, int>,
    vector<pair<int, int>>,
    greater<pair<int, int>>
> pq;
```

Dijkstra에서는 보통 `{거리, 정점}`을 min-heap에 넣습니다.

```cpp
pq.push({0, start});
```

거리가 작은 후보가 먼저 나오고, 거리가 같으면 정점 번호가 작은 후보가 먼저 나옵니다. 거리만 중요하다면 tie-break는 보통 답에 영향을 주지 않습니다.

## 6. 구조체 비교 기준

여러 값을 가진 구조체를 넣을 때는 비교 함수를 직접 정의합니다.

```cpp
#include <queue>
#include <vector>
using namespace std;

struct Job {
    int deadline;
    int duration;
    int id;
};

struct EarlierDeadline {
    bool operator()(const Job& a, const Job& b) const {
        return a.deadline > b.deadline;
    }
};

priority_queue<Job, vector<Job>, EarlierDeadline> pq;
```

C++의 `priority_queue` 비교 함수는 "a가 b보다 뒤에 와야 하는가?"처럼 동작한다고 생각하면 됩니다. min-heap을 만들 때 `a.deadline > b.deadline`를 반환하는 이유입니다.

헷갈리면 작은 예시를 직접 push해서 `top()`이 원하는 값인지 확인하는 습관이 좋습니다.

## 7. 상위 K개 유지

가장 큰 K개만 유지하려면 min-heap을 씁니다. heap 안에는 현재 선택된 K개가 들어 있고, 그중 가장 작은 값이 top입니다.

```cpp
long long sumTopK(const vector<int>& values, int k) {
    priority_queue<int, vector<int>, greater<int>> pq;
    long long sum = 0;

    for (int value : values) {
        pq.push(value);
        sum += value;

        if ((int)pq.size() > k) {
            sum -= pq.top();
            pq.pop();
        }
    }
    return sum;
}
```

새 값이 들어올 때마다 일단 넣고, K개를 넘으면 가장 작은 값을 버립니다. 그러면 남은 값들은 가장 큰 K개입니다.

반대로 가장 작은 K개만 유지하려면 max-heap을 쓰고, K개를 넘으면 가장 큰 값을 버립니다.

## 8. 스케줄링 패턴

우선순위 큐는 "현재 선택 가능한 후보 중 가장 좋은 것"을 골라야 할 때 강합니다.

예를 들어 강의실 배정 문제에서는 시작 시간 순으로 강의를 보면서, 현재 사용 중인 강의실들의 종료 시간을 min-heap에 넣습니다.

```cpp
int minRooms(vector<pair<int, int>> intervals) {
    sort(intervals.begin(), intervals.end());

    priority_queue<int, vector<int>, greater<int>> endTimes;

    for (auto [start, end] : intervals) {
        if (!endTimes.empty() && endTimes.top() <= start) {
            endTimes.pop();
        }
        endTimes.push(end);
    }
    return (int)endTimes.size();
}
```

가장 빨리 끝나는 강의실이 현재 강의 시작 전에 비면 재사용합니다. 그렇지 않으면 새 강의실이 필요합니다.

이 패턴은 자원 배정, 회의실, 기계 스케줄링, 이벤트 시뮬레이션에 자주 등장합니다.

## 9. 지연 삭제

`priority_queue`는 중간 원소를 삭제하거나 값을 수정하는 기능이 없습니다. 특정 원소를 삭제해야 한다면 보통 지연 삭제를 씁니다.

아이디어는 "삭제해야 할 값을 따로 기록하고, top에 올라왔을 때 버린다"입니다.

```cpp
priority_queue<int> pq;
unordered_map<int, int> removed;

void eraseValue(int x) {
    removed[x]++;
}

void cleanTop() {
    while (!pq.empty()) {
        int x = pq.top();
        if (removed[x] == 0) break;
        removed[x]--;
        pq.pop();
    }
}

int getMax() {
    cleanTop();
    return pq.top();
}
```

이 방식은 같은 값이 여러 번 들어갈 수 있으므로 삭제 개수를 세야 합니다. 값만으로 구분이 안 되면 고유 id를 함께 저장합니다.

지연 삭제는 두 heap으로 중앙값을 관리하거나, sliding window 최댓값/최솟값을 heap으로 처리할 때 쓰입니다. 다만 sliding window는 deque로 더 깔끔하게 풀리는 경우도 많습니다.

## 10. Dijkstra의 stale entry

Dijkstra에서 priority queue는 decrease-key를 직접 지원하지 않습니다. 그래서 더 짧은 거리를 찾으면 새 후보를 그냥 push합니다. 이전에 들어 있던 더 긴 후보는 나중에 꺼냈을 때 버립니다.

```cpp
while (!pq.empty()) {
    auto [distHere, u] = pq.top();
    pq.pop();

    if (distHere != dist[u]) continue;

    for (auto edge : graph[u]) {
        int v = edge.to;
        long long nextDist = dist[u] + edge.cost;
        if (nextDist >= dist[v]) continue;

        dist[v] = nextDist;
        pq.push({nextDist, v});
    }
}
```

`distHere != dist[u]`인 항목은 더 이상 최신 후보가 아닙니다. 이런 stale entry를 버리는 방식은 우선순위 큐 실전에서 매우 흔합니다.

## 11. 직접 힙 구현 감각

표준 라이브러리를 쓰면 되지만, 힙이 어떻게 유지되는지 간단히 보면 좋습니다.

삽입은 맨 뒤에 넣고 부모와 비교하며 위로 올립니다.

```cpp
void pushHeap(vector<int>& heap, int value) {
    heap.push_back(value);
    int i = (int)heap.size() - 1;

    while (i > 0) {
        int parent = (i - 1) / 2;
        if (heap[parent] >= heap[i]) break;
        swap(heap[parent], heap[i]);
        i = parent;
    }
}
```

삭제는 루트를 맨 뒤 값으로 바꾼 뒤, 자식 중 더 큰 쪽과 비교하며 아래로 내립니다.

```cpp
int popHeap(vector<int>& heap) {
    int result = heap[0];
    heap[0] = heap.back();
    heap.pop_back();

    int i = 0;
    while (true) {
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        int best = i;

        if (left < (int)heap.size() && heap[left] > heap[best]) best = left;
        if (right < (int)heap.size() && heap[right] > heap[best]) best = right;
        if (best == i) break;

        swap(heap[i], heap[best]);
        i = best;
    }
    return result;
}
```

빈 heap에서 `popHeap`을 호출하면 안 됩니다. 실제 구현에서는 먼저 크기를 확인해야 합니다.

## 12. 시간 복잡도

| 작업 | 시간 |
| --- | --- |
| 최댓값/최솟값 조회 | `O(1)` |
| 삽입 | `O(log n)` |
| top 제거 | `O(log n)` |
| 전체 n개 heapify | `O(n)` |
| n개를 모두 push 후 pop | `O(n log n)` |

`priority_queue`는 임의 원소 검색이 빠르지 않습니다. 특정 값이 있는지 확인하거나 중간 값을 삭제해야 한다면 `set`, `multiset`, `map` 같은 balanced tree가 더 맞을 수 있습니다.

## 13. 자주 하는 실수

첫 번째 실수는 min-heap과 max-heap 비교식을 반대로 쓰는 것입니다. 구조체 comparator는 특히 헷갈리므로 작은 테스트를 해 봅니다.

두 번째 실수는 `top()`을 빈 큐에서 호출하는 것입니다.

```cpp
if (!pq.empty()) {
    int x = pq.top();
}
```

세 번째 실수는 값이 바뀐 원소를 heap 안에서 자동으로 재정렬된다고 생각하는 것입니다. heap에 들어간 원소는 복사본입니다. 외부 배열 값을 바꿔도 heap 내부 순서는 바뀌지 않습니다. 새 값을 push하고 stale entry를 버리는 식으로 처리해야 합니다.

네 번째 실수는 중복 값을 id 없이 삭제하려는 것입니다. 같은 값이 여러 개 있으면 어떤 원소를 지우는지 구분할 수 없습니다. 필요하면 `{priority, id}`처럼 고유 id를 함께 넣습니다.

## 14. 문제를 볼 때 체크할 조건

1. 후보가 계속 추가되고, 매번 최댓값이나 최솟값을 꺼내야 하는가?
2. 정렬 한 번으로는 부족하고 중간 상태가 계속 바뀌는가?
3. top만 필요하고 중간 원소 삭제는 거의 없는가?
4. 작은 값 우선인지 큰 값 우선인지 명확한가?
5. 같은 우선순위일 때 tie-break가 필요한가?

이 조건에 맞으면 우선순위 큐를 먼저 고려합니다. 중간 삭제나 순위 질의가 많아지면 `set`, `multiset`, Fenwick Tree, Segment Tree 같은 다른 자료구조와 비교합니다.
