# Sqrt Decomposition

Sqrt Decomposition은 긴 배열을 길이 약 `sqrt(n)`인 블록들로 나누고, 각 블록에 미리 계산한 값을 저장해 질의를 빠르게 처리하는 방법입니다. 한국어로는 보통 **제곱근 분할**이라고 부릅니다.

이 기법이 다루는 대표 질문은 다음과 같습니다.

```text
배열 값이 바뀔 수 있다.
중간중간 구간 [l, r]의 합, 최솟값, 등장 횟수 같은 정보를 빠르게 물어본다.
```

배열을 매번 전부 훑으면 질의 하나가 `O(n)`입니다. Segment Tree를 쓰면 `O(log n)`까지 줄일 수 있지만, 구현이 부담스럽거나 블록 단위로 쉽게 정리되는 문제가 있습니다. 이때 Sqrt Decomposition은 구현 난이도와 속도 사이에서 좋은 선택지가 됩니다.

![배열 5 2 7 1 4 6 3 8 9 2를 길이 4 블록으로 나누면 블록 0, 1, 2의 합이 15, 21, 11로 저장됩니다.](lesson-assets/block-layout.svg)

[그림 크게 보기](https://git.readiz.com/h-contest-lesson/lessons/sqrt-decomposition/lesson-assets/block-layout.svg)

## 핵심 아이디어

배열 길이가 `n`일 때 블록 크기를 `B`라고 합시다. 보통 `B = sqrt(n)` 근처로 잡습니다. 배열의 각 위치 `i`는 `i / B`번째 블록에 들어갑니다.

```text
index: 0 1 2 3 | 4 5 6 7 | 8 9 10 11 | 12 13
block: 0 0 0 0 | 1 1 1 1 | 2 2  2  2 | 3  3
```

구간 질의 `[l, r]`을 처리할 때는 구간 안에 완전히 들어오는 블록은 미리 저장한 블록 값을 한 번에 사용합니다. 양 끝에서 블록이 잘리는 부분만 원소를 직접 훑습니다.

이렇게 하면 한 질의에서 직접 보는 원소 수는 양 끝 블록의 최대 `2B`개 정도이고, 가운데에서 사용하는 전체 블록 수는 대략 `n / B`개입니다.

```text
한 질의 비용 = O(B + n / B)
```

`B`가 너무 작으면 블록 개수가 많아지고, 너무 크면 양 끝에서 직접 훑는 원소가 많아집니다. 둘을 비슷하게 맞추면 `B = sqrt(n)` 근처가 됩니다.

## 구간 합 예시

가장 기본적인 예시는 구간 합입니다. 원본 배열 `a`와 블록별 합 `blockSum`을 같이 저장합니다.

```text
a        = [5, 2, 7, 1, 4, 6, 3, 8, 9, 2]
B        = 4
blockSum = [15, 21, 11]
```

첫 번째 블록의 합은 `5 + 2 + 7 + 1 = 15`입니다. 두 번째 블록의 합은 `4 + 6 + 3 + 8 = 21`입니다.

## 양 끝만 직접 읽기

위 배열에서 `B = 4`이고 `[2, 9]`를 물으면 `2, 3`은 직접 보고, `[4, 7]` 블록은 저장된 합으로 한 번에 처리하고, `8, 9`는 직접 봅니다.

![같은 배열에서 위치 2부터 9까지 질의하면 위치 2, 3은 7+1을 직접 더하고 블록 1은 저장된 합 21을 쓰며 위치 8, 9는 9+2를 직접 더해 40이 됩니다.](lesson-assets/range-query.svg)

[그림 크게 보기](https://git.readiz.com/h-contest-lesson/lessons/sqrt-decomposition/lesson-assets/range-query.svg)

아래 `query`의 세 반복문이 이 세 부분을 처리합니다. 점 하나를 바꾸는 `update`는 해당 블록의 합에 `새 값 - 옛 값`만 더하므로 `O(1)`입니다.

## 전체 구현

아래 구현은 0-indexed 배열에서 점 업데이트와 구간 합 질의를 처리합니다.

> **코드 환경: h-contest 제출용 코드.** 표준 헤더·STL·동적 할당 없이 고정 배열로 구현하므로 앞에 붙일 [공통 코드](https://h.readiz.com/learn/cpp-common-library) 블록이 없습니다. `cmath`의 `sqrt` 대신 정수 반복으로 블록 크기를 구합니다.

원소 수 상한 `MAX_N = 200000`은 이 사이트 연습의 입력 상한이며, 실제 문제에서는 제한에 맞춰 바꿉니다. 블록 크기는 `B * B >= n`인 가장 작은 정수 `B`로 정하는 `ceilSqrt(n)`입니다. 이때 블록 수는 `B` 이하이므로 `blockSum`은 `ceilSqrt(MAX_N)`칸이면 충분합니다. `a`와 `blockSum`은 정적 배열이라 이전 TC의 값이 남습니다. 큰 `SqrtSum`은 전역으로 선언하고, TC가 시작될 때마다 `build`가 사용할 `[0, n)`과 블록 합을 새로 채웁니다.

```cpp
const int MAX_N = 200000; // 원소 수 상한

// B * B >= x인 가장 작은 B(= sqrt(x)의 올림)를 정수 반복으로 구한다.
constexpr int ceilSqrt(int x) {
    int r = 1;
    while (r * r < x) ++r;
    return r;
}

const int MAX_BLOCKS = ceilSqrt(MAX_N); // 블록 수의 상한

struct SqrtSum {
    int n;
    int B;
    long long a[MAX_N];
    long long blockSum[MAX_BLOCKS];

    bool build(const long long values[], int size) { // 0 <= size <= MAX_N이 아니면 false
        if (size < 0 || size > MAX_N) return false;
        n = size;
        B = ceilSqrt(n);
        int blockCount = (n + B - 1) / B;
        for (int block = 0; block < blockCount; ++block) {
            blockSum[block] = 0;
        }

        for (int i = 0; i < n; ++i) {
            a[i] = values[i];
            blockSum[i / B] += a[i];
        }
        return true;
    }

    void update(int idx, long long newValue) {
        int block = idx / B;
        blockSum[block] += newValue - a[idx];
        a[idx] = newValue;
    }

    long long query(int l, int r) {
        long long result = 0;

        while (l <= r && l % B != 0) {
            result += a[l];
            l++;
        }
        while (l + B - 1 <= r) {
            result += blockSum[l / B];
            l += B;
        }
        while (l <= r) {
            result += a[l];
            l++;
        }

        return result;
    }
};

SqrtSum sqrtSum;
```

사용할 때는 입력 구간이 1-indexed라면 `l--`, `r--`로 변환한 뒤 호출합니다.

## 시간 복잡도

구간 합 버전의 복잡도는 다음과 같습니다.

| 작업 | 시간 |
| --- | --- |
| 전처리 | `O(n)` |
| 점 업데이트 | `O(1)` |
| 구간 합 질의 | `O(sqrt(n))` |
| 메모리 | `O(n)` |

정확히는 질의가 `O(B + n / B)`이고, `B`를 `sqrt(n)` 근처로 잡았을 때 `O(sqrt(n))`입니다.

`n = 100000`이면 `sqrt(n)`은 약 316입니다. 한 질의에서 원소 수십만 개를 전부 훑는 대신 몇백 단위 작업으로 줄어듭니다.

## 최솟값 질의는 왜 조금 다를까

구간 최솟값도 비슷하게 블록별 최솟값 `blockMin`을 저장하면 됩니다. 질의는 구간 합과 같은 방식으로 처리할 수 있습니다.

하지만 점 업데이트가 달라집니다. 합은 `newValue - oldValue`만큼 더하면 되지만, 최솟값은 한 원소가 바뀌었을 때 블록 최솟값이 어떻게 변하는지 바로 알기 어렵습니다.

그래서 업데이트가 일어나면 해당 블록을 다시 훑어 `blockMin`을 계산합니다.

이 경우 업데이트는 `O(B)`, 질의는 `O(sqrt(n))`입니다.

## Lazy 블록 갱신

Sqrt Decomposition은 블록 전체에 같은 변경을 적용하는 문제에도 자주 쓰입니다. 예를 들어 구간 `[l, r]`에 `x`를 더하고, 한 위치의 값을 묻는 문제를 생각해 봅시다.

블록 전체가 구간 안에 들어오면 모든 원소를 직접 바꾸지 않고 `lazy[block] += x`만 기록합니다. 양 끝의 잘린 부분만 원소를 직접 바꿉니다. 다음 코드는 앞의 구간 합 자료구조와 별개의 변형으로, `build`가 `a`에 원래 값을 넣고 블록별 `lazy`를 0으로 초기화합니다. `B`와 인덱스 범위는 앞과 같고, `MAX_N`·`MAX_BLOCKS`·`ceilSqrt`도 앞 코드와 같은 파일에서 씁니다.

```cpp
struct SqrtLazy {
    int n;
    int B;
    long long a[MAX_N];
    long long lazy[MAX_BLOCKS];

    bool build(const long long values[], int size) { // 0 <= size <= MAX_N이 아니면 false
        if (size < 0 || size > MAX_N) return false;
        n = size;
        B = ceilSqrt(n);
        int blockCount = (n + B - 1) / B;
        for (int block = 0; block < blockCount; ++block) {
            lazy[block] = 0;
        }
        for (int i = 0; i < n; ++i) {
            a[i] = values[i];
        }
        return true;
    }

    void rangeAdd(int l, int r, long long x) {
        while (l <= r && l % B != 0) {
            a[l] += x;
            l++;
        }
        while (l + B - 1 <= r) {
            lazy[l / B] += x;
            l += B;
        }
        while (l <= r) {
            a[l] += x;
            l++;
        }
    }

    long long get(int idx) {
        return a[idx] + lazy[idx / B];
    }
};

SqrtLazy sqrtLazy;
```

여기서 `a[i]`는 개별로 직접 바꾼 값이고, `lazy[block]`은 블록 전체에 밀려 있는 증가량입니다. 실제 값은 둘을 더해야 합니다.

![구간2부터7에3을 더하면 a의2와3만3이 됩니다. 블록1의 lazy가3이므로4부터7의 실제 값도3입니다.](lesson-assets/lazy-values.svg)

[그림 크게 보기](https://git.readiz.com/h-contest-lesson/lessons/sqrt-decomposition/lesson-assets/lazy-values.svg)

`n=8`, `B=4`(`B`는 `sqrt(n)` 근처이면 되므로 그림에서는 4로 둡니다), 모든 값이 0인 상태에서 닫힌 구간 `[2,7]`에 3을 더했습니다. 블록 전체 갱신에서는 `a`와 `lazy`를 동시에 증가시키지 않습니다. 둘 다 더하면 조회 때 증가량이 두 번 반영됩니다.

## 구간 갱신 실습

[창고 구역 장부](/practice/SHELFLOG)에서 구간 덧셈과 구간 합을 구현해 봅니다. 블록 전체를 갱신할 때는 합에 `증가량 × 블록 길이`를 반영하고, 양 끝의 일부 구간은 직접 처리합니다.

## 휴리스틱 풀이에서 쓰는 곳

제곱근 분할은 데이터를 적당한 크기의 블록(버킷)으로 나눠, 질의마다 전체를 훑지 않고 이웃 블록과 블록 안의 일부만 보게 하는 데 씁니다. 휴리스틱에서는 점 수가 많을 때 "가까운 후보"를 찾는 공간 버킷으로 가장 자주 나타납니다. 블록 크기는 질의 범위와 데이터 수에 맞춰 정합니다.

- [물류 상품 배송 1](/practice/COUPANG1): 배송 요청이 1,000,000개이고 좌표는 `0 <= y, x < 1000`입니다. 가까운 처리 전 배송지를 찾을 때마다 100만 개를 전수 조사하면 느리므로, 좌표 칸이나 작은 블록별로 배송지 목록을 두고 가까운 블록부터 보는 방법을 쓸 수 있습니다.
- [택시 호출 지도](/practice/TAXICALL): 택시는 최대 200,000대이고 호출은 220,000번 이하이며 `mapSize / callDistance <= 2000`입니다. 호출 거리 크기의 칸으로 나누면 한 번의 질의가 사용자 주변 칸만 확인하게 되어 전체 순회를 피합니다.
