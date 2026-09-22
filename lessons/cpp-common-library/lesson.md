# STL 없는 공통 라이브러리

풀이마다 반복되는 배열 처리·난수·정렬·큐·힙을 필요한 블록만 골라 씁니다. **이 자료를 모두 읽은 뒤 문제를 풀 필요는 없습니다.** [제출 계약과 검증](https://h.readiz.com/learn/cpp-contest-basics)에서 ORDERING으로 진행하다 필요한 기능이 생기면 돌아옵니다.

모든 블록은 표준 헤더·STL·동적 할당 없이 C++17로 작성했습니다. `namespace`, `struct`, 참조, `template`는 언어 기능이며 사용할 수 있습니다. 문제별 상태·점수 계산·이동 연산과 공개 API 선언은 풀이에 둡니다.

| 블록과 용도 | 호출자가 준비할 것 |
| --- | --- |
| `array`: 교환·초기화·복사·ID 채우기 | 배열과 유효 길이 |
| `random`: 풀이 전용 난수·부분 셔플 | TC별 solver seed |
| `sort`: 값·구조체의 안정 정렬, 키 기준 ID 정렬 | 원본·임시 배열 각각 n칸, 비교 기준 |
| `queue`: 발견한 순서대로 처리 | 한 탐색의 누적 push 수만큼 용량 |
| `min-heap`: 가장 작은 (key, id)부터 처리 | 동시에 남을 수 있는 항목 수만큼 용량 |

각 블록은 다른 블록 없이 컴파일됩니다. 필요한 블록을 `user.cpp` 앞에 한 번씩 붙이고, 그 뒤에 풀이 함수를 둡니다. 큰 큐·힙과 임시 배열은 전역으로 준비하며, 각 TC나 독립 탐색이 시작될 때 초기화합니다. `hc` namespace는 문제의 공개 API와 이름이 겹치는 일을 줄입니다.

## 필요한 블록만 꺼내기

저장소에서 다음 명령으로 본문의 코드를 그대로 추출할 수 있습니다. 출력은 헤더 파일을 include하는 방식이 아니라 **제출 소스에 붙일 C++ 코드**입니다.

```bash
python3 scripts/export_cpp_library.py --list
python3 scripts/export_cpp_library.py --blocks array random --output /tmp/hc-common.cpp
```

ORDERING의 SA는 `random`, 정렬은 `sort`, [그리디의 강의실·과제 배정](https://h.readiz.com/learn/greedy)은 `sort`와 `min-heap`을 사용합니다. [상위 K개 합](https://h.readiz.com/learn/priority-queue-heap)은 `min-heap`만 필요합니다. 사용하지 않는 블록이나 로컬 테스트의 헤더·`main`은 제출 소스에 붙이지 않습니다.

## 블록 `array`: 초기화·복사·교환

모든 배열은 호출자가 준비합니다. `[0, n)`이 유효해야 하며 `n >= 0`입니다. `copy`는 두 구간이 겹치지 않거나 시작 주소가 같을 때 사용합니다. 시작 주소가 다른 채로 한 칸씩 겹쳐 이동하려면 방향을 정해 별도로 구현합니다.

> **코드 환경: h-contest 공통 코드.** 표준 헤더·STL 없이 사용하는 블록입니다. 필요한 블록만 복사하고 문제별 배열 상한과 TC 초기화를 맞춥니다.

```cpp compile-check snippet=array
namespace hc {
template<class T> void swap(T& a, T& b) {
    T temp = a; a = b; b = temp;
}
template<class T> void fill(T a[], int n, const T& value) {
    const T saved = value;
    for (int i = 0; i < n; ++i) a[i] = saved;
}
template<class T> void copy(T dest[], const T src[], int n) {
    for (int i = 0; i < n; ++i) dest[i] = src[i];
}
void iota(int a[], int n) {
    for (int i = 0; i < n; ++i) a[i] = i;
}
}
```

`swap(a, a)`도 안전합니다. XOR 교환은 같은 원소를 넘겼을 때 값을 지울 수 있으므로 쓰지 않습니다. 배열 복사는 `O(n)`이며, 탐색 한 번마다 큰 상태를 복사하면 이 비용이 탐색 횟수를 제한합니다.

## 블록 `random`: 풀이 자체의 난수

난수를 쓰는 초기해·이웃 선택은 같은 seed에서 재현되어야 비교할 수 있습니다. 아래 상태는 **풀이 전용**이며 채점기의 난수 상태와 독립적입니다. TC마다 사용할 solver seed를 정하고 실험 기록에 남깁니다.

```cpp compile-check snippet=random
namespace hc {
static_assert(sizeof(unsigned) == 4, "32-bit unsigned required");
struct Random {
    unsigned state;
    void reset(unsigned seed) { state = seed; }
    unsigned next() {
        state = state * 1664525u + 1013904223u;
        return state;
    }
    unsigned below(unsigned bound) { // 전제: bound > 0
        const unsigned threshold = (0u - bound) % bound;
        unsigned value;
        do { value = next(); } while (value < threshold);
        return value % bound;
    }
    void shuffle(int a[], int n) { // [0, n), n >= 0
        for (int i = n - 1; i > 0; --i) {
            int j = (int)below((unsigned)i + 1u);
            int temp = a[i]; a[i] = a[j]; a[j] = temp;
        }
    }
};
}
```

처음 호출하기 전에 반드시 `reset(seed)`를 실행합니다. 덧셈·곱셈의 unsigned 32비트 순환을 의도적으로 이용한 간단한 LCG입니다. 암호나 고품질 통계 시뮬레이션용 생성기는 아닙니다. `% bound`만 쓸 때의 나머지 편향을 줄이기 위해 일부 값을 버리지만, LCG의 연속 출력 사이 상관까지 없애지는 못합니다.

손으로 재현할 기준: seed `1`에서 `next()`의 첫 세 값은 `1015568748`, `1586005467`, `2165703038`입니다. seed를 다시 `1`로 설정하면 다시 같은 값이 나와야 합니다.

ORDERING에서는 창고를 고정해야 하므로 전체 배열을 섞으면 안 됩니다. 먼저 `hc::iota(order, n)`으로 순열을 만들고, `n > 1`일 때 `rng.shuffle(order + 1, n - 1)`만 적용합니다. 셔플 후에도 유효성은 유지되지만 점수가 좋아진다는 보장은 없습니다.

## 실험 기록에서 seed를 구분한다

| 항목 | 의미 |
| --- | --- |
| 입력 seed 또는 TC ID | 비교할 문제 인스턴스 |
| solver seed | 초기해·이웃 선택에 쓰는 풀이의 난수 |
| 반복 수 또는 시간 예산 | 탐색에 허용한 작업량 |
| 결과 | 점수, 실행 시간, 무효 답 여부 |

처음에는 고정 반복 수와 같은 solver seed로 수정 전후를 비교합니다. 시간 제한 종료를 사용하면 실행 환경에 따라 반복 횟수가 달라질 수 있습니다. 성능 평가는 여러 입력·solver seed에서 확인하고, 튜닝에 쓰지 않은 입력도 남깁니다.

## 블록 `sort`: 비교 기준과 정렬 구현 분리

`stableSort(a, temp, n, before)`는 정렬 결과를 원본 배열 `a`에 기록하며, 작업용 `temp`는 별도로 `n`칸 이상 준비합니다. 두 배열은 겹치지 않고, `0 <= n <= 1,000,000`입니다. 비교 함수는 엄격한 순서를 정의해야 합니다. 동률에서 양방향 모두 false이면 왼쪽 원소를 먼저 옮겨 기존 순서를 보존합니다.

`sortIds`는 같은 정렬 구현에 키·ID 비교 기준을 붙인 함수입니다. `id[0..n-1]`은 `key[]`의 유효한 인덱스이며, `temp`는 `key`와도 겹치지 않습니다.

> **코드 환경: h-contest 공통 코드.** 표준 헤더·STL·동적 할당 없이 사용하는 블록입니다.

```cpp compile-check snippet=sort
namespace hc {
template<class T, class Before>
void stableSort(T a[], T temp[], int n, Before before) {
    for (int width = 1; width < n; width *= 2) {
        for (int left = 0; left < n; left += width * 2) {
            int mid = left + width;
            int right = left + width * 2;
            if (mid > n) mid = n;
            if (right > n) right = n;
            int i = left, j = mid, k = left;
            while (i < mid && j < right) {
                if (before(a[j], a[i])) temp[k++] = a[j++];
                else temp[k++] = a[i++];
            }
            while (i < mid) temp[k++] = a[i++];
            while (j < right) temp[k++] = a[j++];
        }
        for (int i = 0; i < n; ++i) a[i] = temp[i];
    }
}
struct KeyOrder {
    const long long* key;
    bool operator()(int a, int b) const {
        return key[a] < key[b] || (key[a] == key[b] && a < b);
    }
};
void sortIds(int id[], int temp[], int n, const long long key[]) {
    stableSort(id, temp, n, KeyOrder{key});
}
}
```

`stableSort`는 비교 기준이 같은 원소의 현재 순서를 유지합니다. `sortIds`는 키가 같으면 ID 오름차순이라는 **추가 기준**을 적용하므로, 입력 ID 순서를 유지한다는 뜻은 아닙니다. `key = [8, 3, 3, 10]`, `id = [3, 2, 1, 0]`이면 `sortIds`의 결과는 `[1, 2, 0, 3]`입니다.

원본 주문·작업 번호를 보존하려면 ID 정렬을, 구조체 자체의 순서를 바꿔도 되면 `stableSort`를 씁니다. 시간은 `O(n log n)`, 작업 공간은 `O(n)`입니다. 정렬 후 키가 바뀌면 순서가 낡으므로 재정렬이나 힙 갱신이 필요합니다.

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

매 탐색 시작에 `clear()`를 호출합니다. 꺼낸 칸을 재활용하지 않는 단순 큐이므로 용량은 **누적 push 수** 기준입니다. 격자 BFS에서 방문 표시를 push할 때 하고 각 칸을 한 번만 넣으면 `H × W`칸이면 됩니다. 같은 정점을 여러 번 넣는 알고리즘에는 그 상한을 그대로 적용할 수 없습니다. push/pop은 `O(1)`입니다. 빈 큐의 `pop`은 `false`를 반환하고 출력 인자를 바꾸지 않습니다. 용량을 넘는 `push`도 실패하므로, 로컬 검증에서 반환값을 확인합니다.

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
    bool top(HeapItem& out) const {
        if (size == 0) return false;
        out = data[1];
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

매 독립 탐색 시작에 `clear()`를 호출합니다. `(key, id) = (5, 2), (1, 7), (1, 3)`을 넣으면 `(1, 3), (1, 7), (5, 2)` 순서로 나옵니다. `top`은 삭제 없이 최솟값을 확인하며 `O(1)`, push/pop은 `O(log size)`입니다. 빈 힙의 `top`과 `pop`은 출력 인자를 바꾸지 않고 `false`를 반환하며, 용량을 넘는 `push`도 실패합니다. 큰 `Queue<CAP>`나 `MinHeap<CAP>` 인스턴스는 전역/정적으로 선언합니다.

이 힙은 decrease-key를 제공하지 않습니다. Dijkstra에서 개선된 거리를 새 항목으로 넣는 방식을 사용하면 정점 수보다 많은 항목이 쌓일 수 있습니다. 꺼낸 거리와 최신 거리의 불일치 검사, push 횟수·최대 적재량 계산은 사용하는 풀이의 책임입니다.

## 로컬 연습: 경계와 사용 계약 확인

입력으로 `(key, id) = (5, 2), (1, 7), (1, 3)`을 준비합니다. `MinHeap<3>`를 초기화하고 세 항목을 넣은 뒤 네 번 꺼내 보세요. 기대 결과는 다음과 같습니다.

```text
pop: true,  (1, 3)
pop: true,  (1, 7)
pop: true,  (5, 2)
pop: false, 출력 인자는 직전 값 유지
```

가득 찬 상태의 네 번째 push는 false여야 합니다. `top`은 pop 없이 같은 최솟값을 돌려줘야 합니다. `clear()` 후 같은 입력을 다시 넣으면 같은 순서가 나와야 합니다.

저장소의 실행 검사는 이 본문의 블록과 제출 계약 예제를 직접 추출합니다. 비교용 표준 라이브러리와 `assert`는 로컬 하네스에만 둡니다.

```bash
python3 scripts/check_cpp_basics.py
python3 scripts/check_submission_examples.py
```

첫 명령은 배열 경계·난수 재현·안정 정렬과 ID 동률·큐/힙 용량을 검사합니다. 두 번째는 실제 정렬·그리디·힙 레슨을 공통 블록과 조합해 독립 기준 풀이와 비교합니다. 공통 코드 검사 통과와 실제 문제의 시간·메모리·점수 충족은 별도로 확인합니다.

## 일반 C++ 참고 예제를 연결할 때

다른 자료의 **일반 C++17 학습용** 표시는 로컬 개념 참고 예제입니다. 직접 풀이 흐름에 가져올 때는 문제의 공개 함수·인덱스·입력 상한에 맞춰 바꿉니다.

| 참고 예제 | STL 없는 풀이에 연결하는 기준 |
| --- | --- |
| `vector`·동적 배열 | 입력 상한에 맞춘 고정 배열과 현재 길이, TC별 초기화 |
| `sort`·`stable_sort` | `sort` 블록과 비교 함수, 독립된 작업 배열 |
| BFS의 `queue` | `queue` 블록과 발견 시 방문 표시, 누적 push 상한 |
| `priority_queue` | `min-heap` 블록, 오래된 후보 제거와 최대 적재량 |
| 동적 트리 노드 | 연산 상한으로 잡은 노드 풀과 정수 인덱스 연결 |

큐나 힙만 교체해서 그래프 표현·메모리 상한까지 해결되지는 않습니다. 일반 참고 예제 전체를 제출용으로 바꿨는지는 그 레슨의 적용 환경과 실행 검증 범위로 확인합니다.
