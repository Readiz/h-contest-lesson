# Kinetic Hull

Kinetic Hull은 점이나 직선이 시간에 따라 움직일 때, 현재 최적 점이나 볼록 껍질을 event 단위로 갱신하는 관점입니다. 정적인 Convex Hull이나 Convex Hull Trick은 한 번 만든 구조를 질의하지만, kinetic 문제는 시간이 흐르면서 최적 후보가 바뀌는 순간을 추적합니다.

이 레슨은 Convex Hull Trick Variants와 Rotating Calipers Applications 이후에 보는 동적 최적화 심화입니다.

1. 각 후보의 값이 시간 `t`의 함수인지 확인한다.
2. 현재 최적인 후보가 언제 다른 후보에게 밀리는지 event를 만든다.
3. event가 실제로 유효한지 다시 확인하면서 구조를 갱신한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Convex Hull Trick Variants, Rotating Calipers Applications, Robust Geometry Predicates
- 함께 보면 좋은 레슨: Shape Distance Modeling, Fully Dynamic CHT, Sweep Line Geometry
- 다음에 볼 레슨: fully dynamic CHT, kinetic data structures, event-driven optimization

## 1. 문제 신호

| 문제 표현 | Kinetic Hull 관점 |
| --- | --- |
| 점의 좌표가 시간에 따라 선형으로 변함 | moving points hull |
| 직선 `y = m(t)x + b(t)` 중 최솟값/최댓값 | time-dependent line envelope |
| 가장 먼 점 쌍, support direction 최댓값이 바뀜 | event between candidates |
| 모든 시간에 대해 답이 필요하지 않고 변화 시점만 필요 | event queue |
| 시간이 단조로 진행됨 | invalid event lazy deletion 가능 |

정확한 대회 문제에서는 event 수가 제한되는 구조가 있어야 합니다. 아무 제약 없이 모든 교차를 추적하면 `O(N^2)` event가 생길 수 있습니다.

## 2. 기본 모델

후보 `i`의 값이 시간에 대한 일차식이라고 합시다.

```text
value_i(t) = a_i * t + b_i
```

현재 최댓값 후보는 위쪽 envelope입니다. 두 후보 `i`, `j`의 우열이 바뀌는 시간은 다음과 같습니다.

```text
a_i * t + b_i = a_j * t + b_j
t = (b_j - b_i) / (a_i - a_j)
```

이 식은 CHT의 교점과 비슷하지만, x query가 시간이 되고 후보 집합 자체가 event로 변할 수 있다는 점이 다릅니다.

## 3. 작은 예시

```text
candidate A: 2t + 1
candidate B: 1t + 5
candidate C: 4t - 3

t = 0: B = 5가 최댓값
A와 B 교차: 2t+1 = t+5 -> t = 4
B와 C 교차: t+5 = 4t-3 -> t = 8/3
A와 C 교차: 2t+1 = 4t-3 -> t = 2
```

하지만 모든 교차가 envelope 변화가 아닙니다. `t=2`에서 C가 A를 이겨도, 그 시점의 최댓값은 아직 B일 수 있습니다. event를 만들 때는 "두 후보가 만난다"와 "답이 바뀐다"를 구분해야 합니다.

## 4. Event Queue Skeleton

아래 코드는 후보 쌍의 교차 시간을 priority queue에 넣고, 꺼낼 때 여전히 이웃인지 확인하는 형태의 skeleton입니다.

```cpp compile-check
#include <queue>
#include <vector>
using namespace std;

struct Event {
    long double time = 0.0L;
    int left = -1;
    int right = -1;

    bool operator<(const Event& other) const {
        return time > other.time;
    }
};

struct KineticQueue {
    priority_queue<Event> events;
    vector<int> version;

    explicit KineticQueue(int n) : version(n, 0) {}

    void pushEvent(long double time, int left, int right) {
        if (left < 0 || right < 0) {
            return;
        }
        events.push(Event{time, left, right});
    }

    bool isStillValid(const Event& event, const vector<int>& currentVersion) const {
        return version[event.left] == currentVersion[event.left]
            && version[event.right] == currentVersion[event.right];
    }
};
```

실전 구현에서는 후보의 linked-list 이웃, 현재 시간, 교차 계산, version bump가 함께 필요합니다. skeleton의 핵심은 오래된 event를 바로 삭제하지 않고, 꺼낼 때 무효화하는 방식입니다.

## 5. Moving Point Hull

점 `p_i(t) = p_i0 + v_i * t`가 움직이면, 특정 방향 `d`에서 support 값은 일차식이 됩니다.

```text
dot(p_i(t), d)
= dot(p_i0, d) + t * dot(v_i, d)
```

따라서 "방향이 고정된 support point"는 line envelope 문제로 바뀝니다. 하지만 전체 convex hull의 vertex 순서를 유지하려면 adjacent edge orientation이 바뀌는 event를 추적해야 하므로 훨씬 어렵습니다.

## 6. Kinetic과 Offline의 경계

모든 query 시간이 미리 주어지면 kinetic structure를 만들지 않고 offline으로 정렬할 수 있습니다.

| 상황 | 우선 후보 |
| --- | --- |
| query 시간이 모두 주어짐 | offline CHT, divide and conquer over time |
| 시간이 실시간으로 증가 | kinetic event queue |
| update가 많고 event bound가 애매함 | rebuild/sqrt decomposition |
| 삭제와 삽입까지 섞임 | fully dynamic CHT 또는 segment tree over time |

대회에서는 kinetic이라는 이름보다 "time을 x로 보는 envelope"로 단순화되는 경우가 더 많습니다.

## 7. 유효 Event 확인

event queue에서 꺼낸 쌍이 지금도 구조상 이웃인지 확인해야 합니다.

```text
초기 이웃: A - B - C
event(A,C)가 queue에 있어도 A와 C는 이웃이 아니면 무시
event(A,B) 처리 후 순서가 바뀌면 B와 C event의 version도 다시 확인
```

이 검사를 빼면 이미 사라진 후보가 다시 답을 바꾸는 것처럼 처리됩니다.

## 8. 구현 전략

1. 후보 값을 시간에 대한 함수로 만든다.
2. 두 후보의 교차 시간이 현재 시간 이후인지 계산한다.
3. hull/envelope에서 이웃 후보끼리만 event를 만든다.
4. event를 처리할 때 후보 version과 이웃 관계를 확인한다.
5. 바뀐 이웃 주변의 event만 다시 넣는다.

정수 좌표라도 교차 시간은 유리수가 될 수 있습니다. 비교는 곱셈으로 처리하거나 `long double` 오차를 받아들일 수 있는 문제인지 확인합니다.

## 9. 자주 하는 실수

1. 모든 후보 쌍 event를 넣어 `O(N^2 log N)`으로 터진다.
2. 오래된 event를 무효화하지 않아 답이 되돌아간다.
3. 교차 시간이 현재 시간보다 과거인데도 queue에 넣는다.
4. 같은 속도 후보의 우열을 따로 처리하지 않는다.
5. floating comparison으로 동시에 일어나는 event 순서가 흔들린다.
6. kinetic이 필요한 문제를 offline query 정렬로 더 쉽게 풀 수 있는데도 어렵게 구현한다.

## 10. 문제를 볼 때 체크할 조건

- 후보 값이 시간에 대해 선형 또는 단순 함수인가?
- 답이 바뀌는 event 수에 상한이 있는가?
- query 시간이 online인가 offline인가?
- 같은 시간에 여러 event가 생기면 순서를 어떻게 처리할 것인가?
- exact rational comparison이 필요한가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: kinetic line envelope `/practice/...` 문제 필요 | 시간축 교점으로 최댓값 변화 찾기 | line envelope |
| 표준 | TODO: moving point support `/practice/...` 문제 필요 | 방향 고정 support point 추적 | dot product |
| 응용 | TODO: event queue kinetic hull `/practice/...` 문제 필요 | stale event lazy deletion | versioning |
| 함정 | TODO: simultaneous kinetic events `/practice/...` 문제 필요 | 동시 event와 tie 처리 | rational compare |
