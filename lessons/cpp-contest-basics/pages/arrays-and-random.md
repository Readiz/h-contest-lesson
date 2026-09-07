# 배열과 재현 가능한 난수

## 블록 `array`: 초기화·복사·교환

모든 배열은 호출자가 준비합니다. `[0, n)`이 유효해야 하며 `n >= 0`입니다. `copy`의 두 구간은 서로 겹치지 않아야 합니다. 같은 배열 자체를 복사하는 것은 가능하지만, 한 칸씩 겹쳐 이동하려면 방향을 정해 별도로 구현합니다.

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
