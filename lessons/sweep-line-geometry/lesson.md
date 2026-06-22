# Sweep Line Geometry

Sweep Line은 좌표 평면의 이벤트를 한 방향으로 정렬해 훑으면서, 현재 선을 가로지르는 active object만 관리하는 기법입니다. 모든 쌍을 직접 비교하면 `O(N^2)`이 되는 기하 문제를 정렬과 자료구조로 줄일 때 자주 씁니다.

이 레슨은 기하 심화에서 이벤트 정렬과 active set을 연결합니다.

1. 이벤트를 x좌표 또는 y좌표 순서로 정렬한다.
2. sweep line이 지나간 상태를 자료구조에 유지한다.
3. 직사각형 넓이, 교차 판정, 최근접 후보처럼 active set만 보면 되는 문제를 처리한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 정렬, 좌표 압축, Segment Tree, CCW와 선분 교차
- 함께 보면 좋은 레슨: 기하 기본, Rotating Calipers, Segment Tree
- 다음에 볼 레슨: Bentley-Ottmann, closest pair, kinetic ordering

## 1. 문제 신호

Sweep line은 평면 객체를 한 축 기준으로 훑을 수 있을 때 나옵니다.

| 문제 표현 | Sweep 관점 |
| --- | --- |
| 많은 직사각형의 합집합 넓이 | x 이벤트 + y 구간 cover length |
| 선분들이 교차하는지 판정 | x 이벤트 + 인접 선분만 검사 |
| 점과 구간의 포함 관계 | 이벤트 순서 + active interval |
| 거리 후보가 가까운 점만 필요 | x 순서 + y active window |
| 시간에 따라 시작/끝이 있는 객체 | 시작/끝 이벤트 |

핵심은 이벤트 사이 구간에서는 active 상태가 변하지 않는다는 점입니다.

## 2. 이벤트 설계

직사각형 합집합 넓이를 예로 보면, 각 직사각형 `[x1, x2) x [y1, y2)`는 두 이벤트로 바뀝니다.

```text
x = x1: y 구간 [y1, y2)를 active에 추가
x = x2: y 구간 [y1, y2)를 active에서 제거
```

이벤트를 x좌표 순서로 처리하면서, 다음 이벤트 x까지의 폭과 현재 active y 길이를 곱해 넓이를 더합니다.

```text
area += coveredYLength * (nextX - currentX)
```

## 3. 좌표 압축과 구간 의미

y좌표를 압축할 때 node가 나타내는 것은 점이 아니라 인접 좌표 사이의 구간입니다.

```text
ys = [1, 4, 10]
index 0 구간은 [1, 4)
index 1 구간은 [4, 10)
```

따라서 `[y1, y2)`를 덮으려면 압축 index `l`부터 `r - 1`까지 갱신합니다. 이 off-by-one이 직사각형 union area에서 가장 자주 틀리는 부분입니다.

## 4. 직사각형 합집합 넓이 구현

아래 코드는 정수 좌표 직사각형들의 합집합 넓이를 계산합니다. y축 구간 cover count와 실제 덮인 길이를 Segment Tree로 관리합니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct Rectangle {
    long long x1;
    long long y1;
    long long x2;
    long long y2;
};

struct Event {
    long long x;
    long long y1;
    long long y2;
    int delta;

    bool operator<(const Event& other) const {
        return x < other.x;
    }
};

struct CoverSegmentTree {
    vector<long long> ys;
    vector<int> cover;
    vector<long long> length;

    explicit CoverSegmentTree(vector<long long> ys)
        : ys(move(ys)), cover(4 * (int)ys.size(), 0), length(4 * (int)ys.size(), 0) {}

    void pull(int node, int start, int end) {
        if (cover[node] > 0) {
            length[node] = ys[end + 1] - ys[start];
        } else if (start == end) {
            length[node] = 0;
        } else {
            length[node] = length[node * 2] + length[node * 2 + 1];
        }
    }

    void update(int node, int start, int end, int left, int right, int delta) {
        if (right < start || end < left) {
            return;
        }
        if (left <= start && end <= right) {
            cover[node] += delta;
            pull(node, start, end);
            return;
        }
        int mid = (start + end) / 2;
        update(node * 2, start, mid, left, right, delta);
        update(node * 2 + 1, mid + 1, end, left, right, delta);
        pull(node, start, end);
    }

    void updateRange(long long y1, long long y2, int delta) {
        int left = (int)(lower_bound(ys.begin(), ys.end(), y1) - ys.begin());
        int right = (int)(lower_bound(ys.begin(), ys.end(), y2) - ys.begin()) - 1;
        if (left <= right) {
            update(1, 0, (int)ys.size() - 2, left, right, delta);
        }
    }

    long long coveredLength() const {
        return length[1];
    }
};

long long unionArea(const vector<Rectangle>& rectangles) {
    vector<Event> events;
    vector<long long> ys;
    for (const Rectangle& rect : rectangles) {
        if (rect.x1 == rect.x2 || rect.y1 == rect.y2) {
            continue;
        }
        events.push_back(Event{rect.x1, rect.y1, rect.y2, 1});
        events.push_back(Event{rect.x2, rect.y1, rect.y2, -1});
        ys.push_back(rect.y1);
        ys.push_back(rect.y2);
    }
    if (events.empty()) {
        return 0;
    }

    sort(events.begin(), events.end());
    sort(ys.begin(), ys.end());
    ys.erase(unique(ys.begin(), ys.end()), ys.end());

    CoverSegmentTree tree(ys);
    long long area = 0;
    long long previousX = events[0].x;

    for (int i = 0; i < (int)events.size(); ) {
        long long currentX = events[i].x;
        area += tree.coveredLength() * (currentX - previousX);

        while (i < (int)events.size() && events[i].x == currentX) {
            tree.updateRange(events[i].y1, events[i].y2, events[i].delta);
            ++i;
        }
        previousX = currentX;
    }

    return area;
}
```

좌표와 넓이 곱은 커질 수 있으므로 `long long`을 씁니다. 문제에서 모듈러 넓이를 요구하지 않는 한 중간 계산도 실제 정수 범위를 확인해야 합니다.

## 5. 선분 교차 sweep

선분 교차 판정은 이벤트와 active set을 쓰지만 직사각형 넓이보다 구현 난도가 높습니다.

1. 각 선분의 왼쪽 끝점과 오른쪽 끝점을 이벤트로 만든다.
2. 현재 x에서 선분의 y순서를 active set에 유지한다.
3. 새 선분을 넣을 때 이웃 선분과만 교차를 검사한다.
4. 선분을 제거할 때 제거 전 이웃끼리 교차를 검사한다.

단, 같은 x좌표 이벤트, 수직 선분, 겹치는 collinear 선분까지 포함하면 comparator와 이벤트 순서가 까다롭습니다. 입문 단계에서는 직사각형 union area처럼 구간 cover가 명확한 sweep부터 익히는 것이 좋습니다.

## 6. 이벤트 순서

같은 좌표의 이벤트 처리 순서는 문제 의미에 맞춰 고정해야 합니다.

| 상황 | 처리 기준 |
| --- | --- |
| 반열린 구간 `[l, r)` | 같은 좌표에서 제거/추가 순서 영향이 적음 |
| 닫힌 구간 `[l, r]` | 끝점에서 만나는 것을 포함할지 결정 |
| 점 query와 구간 update | update 후 query인지 query 후 update인지 문제 조건 확인 |
| 선분 교차 | 시작, 수직 질의, 끝 이벤트 순서 분리 |

같은 x좌표를 한 번에 묶어 처리하면 이벤트 사이 폭이 0인 구간에서 잘못된 면적을 더하는 일을 줄일 수 있습니다.

## 7. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| 이벤트 정렬 | `O(N log N)` | `O(N)` |
| 좌표 압축 | `O(N log N)` | `O(N)` |
| 직사각형 union area | `O(N log N)` | `O(N)` |
| active set 기반 선분 sweep | `O(N log N)` + 교차 검사 | `O(N)` |

여기서 `N`은 보통 이벤트 수입니다. 직사각형 `R`개면 이벤트는 `2R`개입니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 좌표 압축 index를 점으로 해석 | 구간 길이 off-by-one | `ys[i]..ys[i+1]` 구간 관리 |
| 같은 x 이벤트를 따로 면적 계산 | 폭 0 처리 혼동 | 같은 x를 묶어서 update |
| y2를 inclusive로 업데이트 | 한 구간 더 덮음 | `[y1, y2)`면 `r - 1` |
| cover count가 있는데 child length만 사용 | 중복 직사각형 누락 | `cover[node] > 0`이면 전체 길이 |
| 선분 active comparator가 현재 x를 반영하지 않음 | set 순서 깨짐 | comparator 설계 주의 |
| 좌표 곱을 int로 계산 | overflow | `long long` |

## 9. 문제를 볼 때 체크할 조건

1. 이벤트를 한 축 기준으로 정렬할 수 있는가?
2. 이벤트 사이에서 답에 필요한 active 상태가 변하지 않는가?
3. active 상태가 구간 cover, set, heap 중 무엇으로 표현되는가?
4. 좌표 압축이 필요한가?
5. 닫힌/반열린 구간과 같은 좌표 이벤트 순서가 명확한가?
6. 모든 쌍 비교보다 sweep이 실제로 이득인가?

Sweep Line은 "움직이는 선"보다 "상태가 바뀌는 시점만 본다"는 발상이 중요합니다. 이벤트 설계와 active 자료구조가 맞으면 기하 문제뿐 아니라 시간 구간 문제에도 같은 패턴을 적용할 수 있습니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 직사각형 합집합 넓이 `/practice/...` 문제 필요 | x 이벤트와 y cover length 관리 | rectangle union |
| 표준 | TODO: 점과 구간 포함 질의 `/practice/...` 문제 필요 | 이벤트 순서와 active count | offline sweep |
| 응용 | TODO: 선분 교차 존재 판정 `/practice/...` 문제 필요 | active set의 이웃만 검사 | segment intersection |
| 함정 | TODO: 같은 좌표 이벤트가 많은 sweep `/practice/...` 문제 필요 | tie-breaking과 grouped events | event order |
