# Fenwick Tree

Fenwick Tree는 배열의 **prefix 합**을 빠르게 관리하는 자료구조입니다. Binary Indexed Tree, 줄여서 BIT라고도 부릅니다.

가장 대표적인 문제는 다음 형태입니다.

```text
배열 a가 있다.
1. a[idx]에 값을 더한다.
2. 구간 [l, r]의 합을 빠르게 구한다.
```

누적합 배열만 있으면 구간 합은 `O(1)`이지만, 중간 값이 바뀔 때 누적합을 다시 고치는 데 `O(n)`이 걸립니다. Fenwick Tree는 값을 바꾸는 작업과 합을 묻는 작업을 모두 `O(log n)`에 처리합니다.

Segment Tree보다 할 수 있는 일은 좁지만, 구간 합처럼 prefix로 표현되는 문제에서는 코드가 짧고 빠릅니다.

## 1. prefix 합으로 생각하기

구간 합은 prefix 합 두 개로 바꿀 수 있습니다.

```text
sum(l, r) = prefixSum(r) - prefixSum(l - 1)
```

그래서 Fenwick Tree는 `prefixSum(x)`를 빠르게 구하는 데 집중합니다. 각 칸은 배열의 한 구간 합을 저장하고, 여러 칸을 더해 원하는 prefix를 만듭니다.

Fenwick Tree는 보통 1-indexed로 구현합니다. 입력이 0-indexed라면 함수에 넣기 전에 `idx + 1`로 바꾸거나, wrapper에서 처리하면 됩니다.

## 2. lowbit

Fenwick Tree의 핵심은 `lowbit(x)`입니다.

```cpp
int lowbit(int x) {
    return x & -x;
}
```

`lowbit(x)`는 `x`의 이진수에서 가장 낮은 1비트가 나타내는 값을 반환합니다.

| x | 이진수 | lowbit(x) |
| --- | --- | --- |
| 1 | `0001` | 1 |
| 2 | `0010` | 2 |
| 3 | `0011` | 1 |
| 4 | `0100` | 4 |
| 6 | `0110` | 2 |
| 8 | `1000` | 8 |

Fenwick Tree의 `tree[i]`는 길이가 `lowbit(i)`인 구간의 합을 저장합니다. 정확히는 다음 구간입니다.

```text
tree[i] = a[i - lowbit(i) + 1] + ... + a[i]
```

예를 들어 `tree[8]`은 `lowbit(8) = 8`이므로 `a[1]`부터 `a[8]`까지의 합을 담고, `tree[6]`은 `lowbit(6) = 2`이므로 `a[5] + a[6]`을 담습니다.

## 3. prefixSum

`prefixSum(idx)`는 `a[1] + ... + a[idx]`를 구합니다. 현재 위치의 구간을 더한 뒤, 그 구간 바로 앞 위치로 이동합니다.

```cpp
long long prefixSum(int idx) {
    long long result = 0;
    while (idx > 0) {
        result += tree[idx];
        idx -= idx & -idx;
    }
    return result;
}
```

예를 들어 `prefixSum(13)`은 다음 칸들을 더합니다.

```text
13 -> 12 -> 8 -> 0
```

`tree[13]`은 마지막 1개, `tree[12]`는 그 앞 4개, `tree[8]`은 그 앞 8개를 담당합니다. 합치면 1부터 13까지의 합이 됩니다.

## 4. add

`a[idx]`에 `delta`를 더할 때는 `idx`를 포함하는 Fenwick Tree 칸들을 모두 고쳐야 합니다.

```cpp
void add(int idx, long long delta) {
    while (idx <= n) {
        tree[idx] += delta;
        idx += idx & -idx;
    }
}
```

`prefixSum`이 아래쪽으로 내려간다면, `add`는 위쪽으로 올라갑니다. `idx += lowbit(idx)`를 반복하면 현재 원소를 포함하는 더 큰 구간으로 이동합니다.

## 5. 구간 합

구간 합은 prefix 합 두 개로 계산합니다.

```cpp
long long rangeSum(int l, int r) {
    return prefixSum(r) - prefixSum(l - 1);
}
```

여기서 `l`, `r`은 1-indexed이고, `l <= r`이라고 가정합니다. 입력이 0-indexed라면 `rangeSum(l + 1, r + 1)`처럼 호출하면 됩니다.

## 6. 전체 구현

아래 구현은 1-indexed Fenwick Tree입니다.

```cpp
#include <vector>
using namespace std;

struct FenwickTree {
    int n;
    vector<long long> tree;

    FenwickTree(int n) : n(n), tree(n + 1, 0) {}

    FenwickTree(const vector<long long>& values) {
        n = (int)values.size();
        tree.assign(n + 1, 0);
        for (int i = 0; i < n; ++i) {
            add(i + 1, values[i]);
        }
    }

    void add(int idx, long long delta) {
        while (idx <= n) {
            tree[idx] += delta;
            idx += idx & -idx;
        }
    }

    long long prefixSum(int idx) const {
        long long result = 0;
        while (idx > 0) {
            result += tree[idx];
            idx -= idx & -idx;
        }
        return result;
    }

    long long rangeSum(int l, int r) const {
        return prefixSum(r) - prefixSum(l - 1);
    }

    void setValue(int idx, long long oldValue, long long newValue) {
        add(idx, newValue - oldValue);
    }
};
```

`setValue`처럼 값을 대입하는 연산을 만들 때는 기존 값을 알아야 합니다. Fenwick Tree 자체는 "얼마를 더할지"를 받는 구조이므로, 원본 배열을 따로 들고 있으면 더 편합니다.

## 7. O(n) 빌드

위 구현처럼 모든 원소에 대해 `add`를 호출하면 빌드는 `O(n log n)`입니다. 구간 합 Fenwick Tree는 `O(n)` 빌드도 가능합니다.

```cpp
FenwickTree(const vector<long long>& values) {
    n = (int)values.size();
    tree.assign(n + 1, 0);

    for (int i = 1; i <= n; ++i) {
        tree[i] += values[i - 1];
        int parent = i + (i & -i);
        if (parent <= n) {
            tree[parent] += tree[i];
        }
    }
}
```

각 칸이 맡은 구간 합을 만든 뒤, 그 구간을 포함하는 다음 칸에 한 번만 올려 보내는 방식입니다.

## 8. lower_bound

모든 값이 음수가 아니면, Fenwick Tree로 "prefix 합이 처음으로 target 이상이 되는 위치"도 찾을 수 있습니다.

```cpp
int lowerBound(long long target) const {
    int idx = 0;
    int bit = 1;
    while ((bit << 1) <= n) bit <<= 1;

    for (; bit > 0; bit >>= 1) {
        int next = idx + bit;
        if (next <= n && tree[next] < target) {
            idx = next;
            target -= tree[next];
        }
    }
    return idx + 1;
}
```

이 함수는 Fenwick Tree 위에서 이진 탐색을 하는 느낌입니다. 왼쪽부터 구간을 크게 붙여 보면서 target에 아직 못 미치면 그 구간을 통째로 건너뜁니다.

주의할 점은 값이 음수일 수 있으면 prefix 합이 단조 증가하지 않는다는 것입니다. 그 경우에는 이 방식으로 lower_bound를 할 수 없습니다.

## 9. 가능한 변형

Fenwick Tree는 prefix로 바꿀 수 있는 연산에 강합니다.

| 작업 | 구현 아이디어 |
| --- | --- |
| 점 업데이트 + 구간 합 | 기본형 |
| 구간 업데이트 + 점 질의 | 차이 배열에 Fenwick Tree를 둔다 |
| 구간 업데이트 + 구간 합 | Fenwick Tree 두 개를 사용한다 |
| 빈도표 + k번째 원소 | 빈도를 저장하고 `lowerBound(k)`를 사용한다 |

최솟값, 최댓값처럼 "prefix 두 개를 빼서 구간 값을 얻는" 형태가 아닌 연산은 Fenwick Tree와 잘 맞지 않습니다. 그런 문제는 Segment Tree가 더 자연스럽습니다.

## 10. Segment Tree와 비교

| 관점 | Fenwick Tree | Segment Tree |
| --- | --- | --- |
| 구현량 | 짧다 | 더 길다 |
| 점 업데이트 + 구간 합 | 좋다 | 좋다 |
| 구간 최솟값/최댓값 | 제한적 | 자연스럽다 |
| lazy 구간 업데이트 | 일부 형태만 간단하다 | 범용적으로 가능하다 |
| 메모리 | `O(n)` | 보통 `O(4n)` 또는 `O(2n)` |

Fenwick Tree는 "prefix 합을 빠르게 관리하는 도구"로 생각하면 실수가 줄어듭니다. 구간 합, 빈도 누적, 순위 찾기처럼 prefix 관점이 선명하면 좋은 선택입니다.
