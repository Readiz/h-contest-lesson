# 누적합과 차분 배열

누적합은 배열의 앞에서부터 합을 미리 저장해 두고, 구간 합을 빠르게 꺼내는 기법입니다. 차분 배열은 반대로 여러 구간에 값을 더하는 작업을 표시만 해 두었다가 마지막에 한 번에 실제 값을 복원하는 기법입니다.

두 기법은 모두 "구간을 매번 직접 훑지 않는다"는 생각에서 출발합니다.

```text
구간 합을 많이 물어본다 -> 누적합
구간 업데이트를 많이 한 뒤 최종 배열만 필요하다 -> 차분 배열
격자 직사각형 합을 많이 물어본다 -> 2차원 누적합
격자 직사각형 업데이트를 많이 모은다 -> 2차원 차분 배열
```

Fenwick Tree나 Segment Tree보다 단순하지만, 업데이트와 질의가 섞이지 않는 문제에서는 더 빠르고 구현도 짧습니다.

## 1. 1차원 누적합

배열 `a`가 있을 때 `prefix[i]`를 `a[0]`부터 `a[i - 1]`까지의 합으로 정의합니다. 즉 `prefix[0] = 0`이고, `prefix`의 길이는 `n + 1`입니다.

```text
a:       3   1   4   1   5
prefix:  0   3   4   8   9   14
index:   0   1   2   3   4    5
```

이렇게 잡으면 0-indexed 구간 `[l, r]`의 합은 아래처럼 구합니다.

```text
sum(l, r) = prefix[r + 1] - prefix[l]
```

예를 들어 `a[1] + a[2] + a[3] = 1 + 4 + 1 = 6`입니다.

```text
prefix[4] - prefix[1] = 9 - 3 = 6
```

## 2. 구현

`long long`을 기본으로 쓰는 습관이 좋습니다. 값 하나는 `int` 범위여도 `n`개를 더하면 쉽게 넘칠 수 있습니다.

```cpp
#include <tuple>
#include <vector>
using namespace std;

vector<long long> buildPrefix(const vector<int>& a) {
    int n = (int)a.size();
    vector<long long> prefix(n + 1, 0);

    for (int i = 0; i < n; ++i) {
        prefix[i + 1] = prefix[i] + a[i];
    }
    return prefix;
}

long long rangeSum(const vector<long long>& prefix, int l, int r) {
    return prefix[r + 1] - prefix[l];
}
```

구간이 비어 있을 수 있는 문제라면 호출 전에 약속을 정합니다. 예를 들어 `l > r`이면 0을 반환하게 만들 수 있습니다.

```cpp
long long safeRangeSum(const vector<long long>& prefix, int l, int r) {
    if (l > r) return 0;
    return prefix[r + 1] - prefix[l];
}
```

## 3. 왜 n + 1칸을 쓰는가

`prefix[i] = a[0] + ... + a[i]`처럼 `n`칸으로 만들 수도 있습니다. 하지만 그러면 `l == 0`인 구간을 따로 처리해야 합니다.

```cpp
long long sum;
if (l == 0) sum = prefix[r];
else sum = prefix[r] - prefix[l - 1];
```

`prefix[0] = 0`인 `n + 1`칸 방식은 모든 구간을 같은 식으로 처리합니다.

```cpp
long long sum = prefix[r + 1] - prefix[l];
```

실전에서는 이 방식이 off-by-one 실수를 줄입니다.

## 4. 여러 구간을 빠르게 합산하기

누적합은 질의가 많은 문제에서 효과가 큽니다.

```text
n = 100000
q = 100000
각 질의마다 [l, r] 합을 출력
```

매 질의마다 직접 더하면 최악의 경우 `O(nq)`입니다. 누적합을 만들면 전처리 `O(n)`, 각 질의 `O(1)`입니다.

```cpp
vector<long long> prefix = buildPrefix(a);

for (int qi = 0; qi < q; ++qi) {
    int l, r;
    cin >> l >> r;
    cout << rangeSum(prefix, l, r) << '\n';
}
```

입력이 1-indexed로 들어오면 내부에서 0-indexed로 바꾸거나, 아예 배열도 1-indexed로 잡습니다.

```cpp
// 입력 l, r이 1-indexed이고 양 끝 포함이라면
cout << prefix[r] - prefix[l - 1] << '\n';
```

한 파일 안에서 0-indexed와 1-indexed를 섞으면 실수가 많아집니다. 처음에 기준을 정하고 끝까지 유지하는 것이 좋습니다.

## 5. 차분 배열

차분 배열은 인접한 값의 차이를 저장합니다.

```text
a:    3   1   4   1   5
diff: 3  -2   3  -3   4
```

`diff[0] = a[0]`이고, `diff[i] = a[i] - a[i - 1]`입니다. 이 차분 배열의 누적합을 다시 구하면 원래 배열이 복원됩니다.

```text
3
3 + (-2) = 1
1 + 3 = 4
4 + (-3) = 1
1 + 4 = 5
```

차분 배열의 장점은 구간에 값을 더할 때 나타납니다.

```text
a[l]부터 a[r]까지 x를 더하고 싶다.
```

이 작업은 차분 배열에서 두 곳만 바꾸면 됩니다.

```text
diff[l] += x
diff[r + 1] -= x
```

`l`부터 값이 x만큼 올라가고, `r + 1`부터 다시 x만큼 내려가도록 표시하는 것입니다.

## 6. 차분 배열 구현

구간 업데이트를 모두 모은 뒤 마지막 배열만 필요하면 차분 배열을 씁니다.

```cpp
#include <vector>
using namespace std;

vector<long long> applyRangeAdds(int n, const vector<tuple<int, int, long long>>& queries) {
    vector<long long> diff(n + 1, 0);

    for (auto [l, r, value] : queries) {
        diff[l] += value;
        if (r + 1 < n) {
            diff[r + 1] -= value;
        }
    }

    vector<long long> result(n, 0);
    long long current = 0;
    for (int i = 0; i < n; ++i) {
        current += diff[i];
        result[i] = current;
    }
    return result;
}
```

`diff`를 `n + 1`칸으로 만들면 `r + 1 == n`일 때도 안전하게 뺄 수 있습니다.

```cpp
diff[l] += value;
diff[r + 1] -= value;
```

그 대신 복원할 때는 `0`부터 `n - 1`까지만 봅니다.

## 7. 기존 배열에 구간 업데이트를 더하기

처음 배열 `a`가 이미 있고, 그 위에 여러 구간 업데이트를 더해야 한다면 `diff`에 업데이트만 모은 뒤 마지막에 더하면 됩니다.

```cpp
vector<long long> addRangesToArray(
    const vector<long long>& a,
    const vector<tuple<int, int, long long>>& queries
) {
    int n = (int)a.size();
    vector<long long> diff(n + 1, 0);

    for (auto [l, r, value] : queries) {
        diff[l] += value;
        diff[r + 1] -= value;
    }

    vector<long long> result(n);
    long long extra = 0;
    for (int i = 0; i < n; ++i) {
        extra += diff[i];
        result[i] = a[i] + extra;
    }
    return result;
}
```

최종 배열의 최댓값만 필요하다면 `result` 배열도 만들 필요가 없습니다.

```cpp
long long best = -(1LL << 60);
long long extra = 0;
for (int i = 0; i < n; ++i) {
    extra += diff[i];
    best = max(best, a[i] + extra);
}
```

## 8. 누적합과 차분 배열의 관계

누적합과 차분 배열은 서로 반대 방향의 도구입니다.

| 하고 싶은 일 | 쓰는 도구 |
| --- | --- |
| 값은 고정, 구간 합 질의가 많다 | 누적합 |
| 구간 업데이트가 많고 마지막 배열만 필요하다 | 차분 배열 |
| 구간 업데이트와 구간 합 질의가 섞인다 | Fenwick Tree 또는 Segment Tree |

차분 배열에 누적합을 취하면 실제 배열이 됩니다. 실제 배열에 다시 누적합을 취하면 구간 합을 빠르게 구할 수 있습니다.

그래서 다음처럼 두 단계를 이어 쓰는 문제도 있습니다.

```text
1. 여러 구간에 값을 더한다.
2. 최종 배열을 만든다.
3. 최종 배열의 구간 합 질의를 처리한다.
```

이 경우 차분 배열로 2번을 만들고, 그 결과에 누적합을 한 번 더 만들면 됩니다.

## 9. 2차원 누적합

격자에서 직사각형 합을 많이 물어보면 2차원 누적합을 씁니다.

`prefix[y][x]`를 왼쪽 위부터 `(y - 1, x - 1)`까지의 직사각형 합으로 정의합니다. 배열 크기는 `(h + 1) x (w + 1)`로 둡니다.

```cpp
vector<vector<long long>> buildPrefix2D(const vector<vector<int>>& grid) {
    int h = (int)grid.size();
    int w = (int)grid[0].size();
    vector<vector<long long>> prefix(h + 1, vector<long long>(w + 1, 0));

    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            prefix[y + 1][x + 1] =
                prefix[y][x + 1]
                + prefix[y + 1][x]
                - prefix[y][x]
                + grid[y][x];
        }
    }
    return prefix;
}
```

`prefix[y][x]`가 두 번 더해지는 영역을 한 번 빼는 것이 핵심입니다.

## 10. 2차원 직사각형 합

위쪽 행 `y1`, 아래쪽 행 `y2`, 왼쪽 열 `x1`, 오른쪽 열 `x2`가 모두 0-indexed이고 양 끝 포함이라고 하겠습니다.

```cpp
long long rectSum(
    const vector<vector<long long>>& prefix,
    int y1,
    int x1,
    int y2,
    int x2
) {
    return prefix[y2 + 1][x2 + 1]
        - prefix[y1][x2 + 1]
        - prefix[y2 + 1][x1]
        + prefix[y1][x1];
}
```

그림으로 생각하면 큰 직사각형에서 위쪽과 왼쪽을 빼고, 두 번 빠진 왼쪽 위를 다시 더합니다.

```text
answer = 전체 - 위쪽 - 왼쪽 + 왼쪽 위 중복 영역
```

2차원 누적합도 질의는 `O(1)`입니다. 전처리는 `O(hw)`입니다.

## 11. 2차원 차분 배열

격자의 여러 직사각형에 값을 더한 뒤 최종 격자만 필요하다면 2차원 차분 배열을 씁니다.

직사각형 `(y1, x1)`부터 `(y2, x2)`까지 `value`를 더하려면 네 꼭짓점에 표시합니다.

```cpp
diff[y1][x1] += value;
diff[y2 + 1][x1] -= value;
diff[y1][x2 + 1] -= value;
diff[y2 + 1][x2 + 1] += value;
```

이후 행 방향과 열 방향으로 누적합을 취하면 각 칸의 최종 증가량이 됩니다.

```cpp
#include <tuple>
#include <vector>
using namespace std;

vector<vector<long long>> applyRectAdds(
    int h,
    int w,
    const vector<tuple<int, int, int, int, long long>>& queries
) {
    vector<vector<long long>> diff(h + 1, vector<long long>(w + 1, 0));

    for (auto [y1, x1, y2, x2, value] : queries) {
        diff[y1][x1] += value;
        diff[y2 + 1][x1] -= value;
        diff[y1][x2 + 1] -= value;
        diff[y2 + 1][x2 + 1] += value;
    }

    vector<vector<long long>> result(h, vector<long long>(w, 0));
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            long long value = diff[y][x];
            if (y > 0) value += result[y - 1][x];
            if (x > 0) value += result[y][x - 1];
            if (y > 0 && x > 0) value -= result[y - 1][x - 1];
            result[y][x] = value;
        }
    }
    return result;
}
```

`diff`를 `(h + 1) x (w + 1)`로 만들면 `y2 + 1 == h`나 `x2 + 1 == w`인 표시도 안전합니다. 최종 결과는 `h x w`만 사용합니다.

## 12. Imos 방식

차분 배열을 이용해 구간 업데이트를 모으는 방식을 일본식으로 Imos method라고 부르기도 합니다. 이름은 달라도 핵심은 같습니다.

```text
시작점에서 +1
끝난 다음 위치에서 -1
마지막에 누적합
```

가장 대표적인 예시는 시간표 겹침입니다.

```text
회의가 [start, end) 시간 동안 열린다.
각 시간에 동시에 열리는 회의 수의 최댓값을 구한다.
```

반열린 구간 `[start, end)`라면 아래처럼 표시합니다.

```cpp
diff[start] += 1;
diff[end] -= 1;
```

양 끝 포함 `[start, end]`와 반열린 구간 `[start, end)`를 섞지 않는 것이 중요합니다.

## 13. 자주 하는 실수

가장 흔한 실수는 인덱스 기준을 섞는 것입니다.

```text
입력은 1-indexed인데 내부 함수는 0-indexed
구간은 [l, r]인데 코드 일부는 [l, r)로 생각
prefix 길이는 n인데 prefix[r + 1]을 읽음
```

처음에 아래 세 가지를 코드 주석이나 변수명으로 분명히 해 두면 좋습니다.

```text
1. 입력 구간이 0-indexed인지 1-indexed인지
2. 구간이 양 끝 포함인지, 오른쪽 제외인지
3. prefix 배열이 n칸인지 n + 1칸인지
```

두 번째 실수는 오버플로입니다. 합이나 누적 업데이트 값은 `long long`으로 받는 것이 안전합니다.

세 번째 실수는 누적합으로 해결할 수 없는 문제를 억지로 푸는 것입니다. 값 변경과 구간 질의가 온라인으로 섞이면 누적합만으로는 부족합니다. 그때는 Fenwick Tree나 Segment Tree를 사용합니다.

## 14. 문제를 볼 때 체크할 조건

1. 배열이나 격자의 값이 고정되어 있고 구간 합 질의가 많은가?
2. 구간 업데이트가 많지만 중간 질의 없이 최종 상태만 필요한가?
3. 직사각형 합 또는 직사각형 업데이트가 필요한가?
4. 입력 구간이 `[l, r]`인지 `[l, r)`인지 명확한가?
5. 합이 `int` 범위를 넘을 수 있는가?

이 질문에 대부분 "그렇다"라고 답할 수 있으면 누적합이나 차분 배열이 가장 먼저 떠올릴 도구입니다.
