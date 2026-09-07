# 정렬·큐·최소 힙

필요한 것은 컨테이너 이름보다 **후보를 꺼내는 순서**입니다. 아래 세 블록은 서로 독립적이며 다른 공통 코드 없이 복사할 수 있습니다.

| 작업 | 선택 | 용량 계산 |
| --- | --- | --- |
| 후보 전체의 우선순위를 한 번 정함 | 인덱스 병합 정렬 | ID 배열·임시 배열 각각 `n`개 |
| 발견한 순서대로 처리 | FIFO 큐 | 한 탐색에서 넣을 수 있는 전체 항목 수 |
| 넣고 빼는 동안 가장 작은 후보 선택 | 최소 힙 | 동시에 들어갈 수 있는 항목 수 |

## 블록 `index-sort`: 원본 대신 ID를 정렬

`id[0..n-1]`에는 `key[]`의 유효한 인덱스가 있어야 합니다. `temp`는 길이 `n` 이상인 별도 배열이고 `id`, `key`와 겹치지 않습니다. 이 구현은 `0 <= n <= 1,000,000` 범위를 전제로 합니다.

```cpp compile-check snippet=index-sort
namespace hc {
bool keyBefore(int a, int b, const long long key[]) {
    return key[a] < key[b] || (key[a] == key[b] && a < b);
}
void sortIds(int id[], int temp[], int n, const long long key[]) {
    for (int width = 1; width < n; width *= 2) {
        for (int left = 0; left < n; left += width * 2) {
            int mid = left + width;
            int right = left + width * 2;
            if (mid > n) mid = n;
            if (right > n) right = n;
            int i = left, j = mid, k = left;
            while (i < mid && j < right) {
                if (keyBefore(id[j], id[i], key)) temp[k++] = id[j++];
                else temp[k++] = id[i++];
            }
            while (i < mid) temp[k++] = id[i++];
            while (j < right) temp[k++] = id[j++];
        }
        for (int i = 0; i < n; ++i) id[i] = temp[i];
    }
}
}
```

키 오름차순, 동점이면 ID 오름차순입니다. `key = [8, 3, 3, 10]`, `id = [0, 1, 2, 3]`이면 결과는 `[1, 2, 0, 3]`입니다. 원본 정보를 재배열하지 않으므로 주문·작업의 원래 번호를 보존할 수 있습니다. 시간 `O(n log n)`, 추가 공간 `O(n)`입니다.

정렬 후 키가 바뀌면 순서는 낡습니다. 변화가 잦다면 재정렬 비용과 힙 갱신 비용을 비교합니다. 문제별로 매번 계산되는 평가식을 그대로 `key[]`로 쓸 수 있는지도 확인합니다.

## 블록 `queue`: 한 탐색용 FIFO

```cpp compile-check snippet=queue
namespace hc {
template<int CAP> struct Queue {
    static_assert(CAP > 0, "positive capacity required");
    int data[CAP];
    int head, tail;
    void clear() { head = tail = 0; }
    bool push(int value) {
        if (tail == CAP) return false;
        data[tail++] = value;
        return true;
    }
    bool pop(int& value) {
        if (head == tail) return false;
        value = data[head++];
        return true;
    }
};
}
```

매 탐색 시작에 `clear()`를 호출합니다. 꺼낸 칸을 재활용하지 않는 단순 큐이므로 용량은 **누적 push 수** 기준입니다. 격자 BFS에서 방문 표시를 push할 때 하고 각 칸을 한 번만 넣으면 `H × W`칸이면 됩니다. 같은 정점을 여러 번 넣는 알고리즘에는 그 상한을 그대로 적용할 수 없습니다. push/pop은 `O(1)`입니다.

## 블록 `min-heap`: 가장 작은 키부터

```cpp compile-check snippet=min-heap
namespace hc {
struct HeapItem { long long key; int id; };
bool heapBefore(const HeapItem& a, const HeapItem& b) {
    return a.key < b.key || (a.key == b.key && a.id < b.id);
}
template<int CAP> struct MinHeap {
    static_assert(CAP > 0, "positive capacity required");
    HeapItem data[CAP + 1]; // 1-index, 0번 칸은 사용하지 않는다.
    int size;
    void clear() { size = 0; }
    bool push(long long key, int id) {
        if (size == CAP) return false;
        HeapItem item = {key, id};
        int i = ++size;
        while (i > 1 && heapBefore(item, data[i / 2])) {
            data[i] = data[i / 2];
            i /= 2;
        }
        data[i] = item;
        return true;
    }
    bool pop(HeapItem& out) {
        if (size == 0) return false;
        out = data[1];
        HeapItem last = data[size--];
        if (size == 0) return true;
        int i = 1;
        while (i * 2 <= size) {
            int child = i * 2;
            if (child < size && heapBefore(data[child + 1], data[child])) ++child;
            if (!heapBefore(data[child], last)) break;
            data[i] = data[child];
            i = child;
        }
        data[i] = last;
        return true;
    }
};
}
```

매 독립 탐색 시작에 `clear()`를 호출합니다. `(key, id) = (5, 2), (1, 7), (1, 3)`을 넣으면 `(1, 3), (1, 7), (5, 2)` 순서로 나옵니다. push/pop은 `O(log size)`입니다. 큰 `Queue<CAP>`나 `MinHeap<CAP>` 인스턴스는 전역/정적으로 선언합니다.

이 힙은 decrease-key를 제공하지 않습니다. Dijkstra에서 개선된 거리를 새 항목으로 넣는 방식을 사용하면 정점 수보다 많은 항목이 쌓일 수 있습니다. 꺼낸 거리와 최신 거리의 불일치 검사, push 횟수·최대 적재량 계산은 사용하는 풀이의 책임입니다.

## 구현 전 체크리스트

- 실패한 push를 무시하면 후보가 사라집니다. 용량을 증명하고, 로컬 검증에서 반환값을 확인했는가?
- 빈 큐·힙의 pop은 `false`이며 출력 인자를 변경하지 않는다. 성공할 때만 결과를 쓰는가?
- 큐의 누적 push 상한과 힙의 동시 적재 상한을 구분했는가?
- 정렬된 키와 현재 평가값이 다를 수 있는가? 동점 처리도 고정했는가?
