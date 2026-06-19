# 이분 탐색과 파라메트릭 서치

이분 탐색은 정렬되어 있거나 단조성이 있는 공간에서 답의 후보를 절반씩 줄이는 기법입니다. 단순히 배열에서 값을 찾는 것뿐 아니라, "이 값으로 가능한가?"라는 판정 함수를 만들고 정답 범위를 좁히는 데에도 자주 쓰입니다.

```text
정렬된 배열에서 x 이상의 첫 위치를 찾는다.
가능한 최소 시간을 찾는다.
조건을 만족하는 최대 길이를 찾는다.
```

이분 탐색의 핵심은 속도가 아니라 **불변식**입니다. 왼쪽과 오른쪽이 각각 어떤 의미인지 정하고, 반복할 때 그 의미가 깨지지 않게 유지해야 합니다.

## 1. 정렬된 배열에서 찾기

오름차순 배열에서 `target`이 있는지 확인하는 기본 형태입니다.

```cpp
bool contains(const vector<int>& a, int target) {
    int left = 0;
    int right = (int)a.size() - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (a[mid] == target) return true;
        if (a[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return false;
}
```

이 코드는 "찾았다/못 찾았다"만 필요할 때는 충분합니다. 하지만 실전에서는 정확한 위치보다 "처음으로 조건을 만족하는 위치"가 더 자주 필요합니다.

## 2. lower_bound

`lower_bound`는 `target` 이상인 첫 위치를 찾습니다.

```text
a[i] >= target 이 되는 가장 작은 i
```

이때 탐색 구간을 반열린 구간 `[left, right)`로 두면 깔끔합니다.

```cpp
int lowerBound(const vector<int>& a, int target) {
    int left = 0;
    int right = (int)a.size();

    while (left < right) {
        int mid = left + (right - left) / 2;
        if (a[mid] < target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    return left;
}
```

반복이 끝나면 `left == right`이고, 그 위치가 답입니다. 모든 원소가 `target`보다 작으면 `a.size()`가 반환됩니다.

```text
a = [1, 3, 3, 7, 9]
lower_bound(3) = 1
lower_bound(4) = 3
lower_bound(10) = 5
```

## 3. upper_bound

`upper_bound`는 `target`보다 큰 첫 위치를 찾습니다.

```text
a[i] > target 이 되는 가장 작은 i
```

구현은 비교식 하나만 다릅니다.

```cpp
int upperBound(const vector<int>& a, int target) {
    int left = 0;
    int right = (int)a.size();

    while (left < right) {
        int mid = left + (right - left) / 2;
        if (a[mid] <= target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    return left;
}
```

정렬된 배열에서 `target`의 개수는 `upperBound(target) - lowerBound(target)`입니다.

```cpp
int countValue(const vector<int>& a, int target) {
    return upperBound(a, target) - lowerBound(a, target);
}
```

## 4. 직접 구현과 표준 라이브러리

C++에는 이미 `lower_bound`, `upper_bound`, `binary_search`가 있습니다.

```cpp
#include <algorithm>
#include <vector>
using namespace std;

int firstAtLeast(const vector<int>& a, int target) {
    auto it = lower_bound(a.begin(), a.end(), target);
    return (int)(it - a.begin());
}
```

실전에서는 표준 라이브러리를 쓰는 것이 안전합니다. 다만 파라메트릭 서치에서는 직접 구현해야 하는 경우가 많으므로, 반열린 구간 방식은 익혀 두는 편이 좋습니다.

정렬되어 있지 않은 배열에 `lower_bound`를 쓰면 결과는 의미가 없습니다. 이분 탐색의 전제는 항상 정렬 또는 단조성입니다.

## 5. 단조 조건

이분 탐색이 가능한 이유는 답 후보가 한 번 기준을 넘으면 그 뒤가 모두 같은 방향으로 유지되기 때문입니다.

```text
false false false true true true
```

이런 배열에서 첫 `true`를 찾는 것이 lower_bound의 본질입니다.

반대로 아래처럼 중간에 다시 바뀌면 이분 탐색을 할 수 없습니다.

```text
false true false true true
```

파라메트릭 서치는 실제 배열 대신 판정 함수 `can(x)`가 이런 단조성을 가진다고 보고 이분 탐색합니다.

## 6. 파라메트릭 서치

파라메트릭 서치는 답 자체를 이분 탐색하는 방식입니다.

예를 들어 어떤 작업을 시간 `t` 안에 끝낼 수 있는지 판단하는 함수가 있다고 하겠습니다.

```cpp
bool can(long long t) {
    // t 안에 모든 작업을 처리할 수 있으면 true
}
```

시간이 충분히 크면 가능하고, 작으면 불가능합니다.

```text
t:      1 2 3 4 5 6 7 8
can(t): F F F F T T T T
```

이때 가능한 최소 시간은 첫 `true`입니다.

```cpp
long long firstTrue(long long left, long long right) {
    // 답은 [left, right] 안에 있고, can(right)는 true라고 가정한다.
    while (left < right) {
        long long mid = left + (right - left) / 2;
        if (can(mid)) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    return left;
}
```

이 형태는 "최소 x"를 찾을 때 씁니다.

## 7. 최대값을 찾는 경우

조건을 만족하는 최대값을 찾는 문제도 많습니다.

```text
t:      1 2 3 4 5 6 7 8
can(t): T T T T F F F F
```

예를 들어 "길이 `x`로 조각을 만들 수 있는가?"는 길이가 작을수록 쉽고, 길이가 커질수록 어려워집니다. 이때는 마지막 `true`를 찾아야 합니다.

```cpp
long long lastTrue(long long left, long long right) {
    // 답은 [left, right] 안에 있고, can(left)는 true라고 가정한다.
    while (left < right) {
        long long mid = left + (right - left + 1) / 2;
        if (can(mid)) {
            left = mid;
        } else {
            right = mid - 1;
        }
    }
    return left;
}
```

여기서는 `mid`를 위쪽으로 올림해서 잡습니다. 그렇지 않으면 `left + 1 == right`인 상태에서 `mid == left`가 되어 반복이 끝나지 않을 수 있습니다.

## 8. 예시: 최소 처리 시간

여러 기계가 있고, 각 기계 `i`는 물건 하나를 만드는 데 `time[i]`가 걸린다고 하겠습니다. 총 `need`개를 만드는 최소 시간을 구하려면 시간 `t` 안에 만들 수 있는 개수를 세면 됩니다.

```cpp
bool canMake(const vector<long long>& time, long long need, long long t) {
    long long made = 0;
    for (long long one : time) {
        made += t / one;
        if (made >= need) return true;
    }
    return false;
}

long long minimumTime(const vector<long long>& time, long long need) {
    long long left = 0;
    long long right = 1;
    while (!canMake(time, need, right)) {
        right *= 2;
    }

    while (left < right) {
        long long mid = left + (right - left) / 2;
        if (canMake(time, need, mid)) {
            right = mid;
        } else {
            left = mid + 1;
        }
    }
    return left;
}
```

처음부터 `right`를 정확히 알기 어려우면, 위처럼 가능한 값이 나올 때까지 두 배씩 늘릴 수 있습니다.

`made`가 너무 커질 수 있으므로 `need` 이상이면 바로 `true`를 반환해 오버플로 위험도 줄입니다.

## 9. 예시: 가능한 최대 거리

정렬된 위치 배열 `pos`에서 물체 `k`개를 놓되, 인접한 물체 사이 최소 거리를 최대화한다고 하겠습니다.

거리 `d`가 가능하면 그보다 작은 거리도 가능합니다. 따라서 마지막 `true`를 찾습니다.

```cpp
bool canPlace(const vector<int>& pos, int k, int d) {
    int count = 1;
    int last = pos[0];

    for (int i = 1; i < (int)pos.size(); ++i) {
        if (pos[i] - last >= d) {
            count++;
            last = pos[i];
            if (count >= k) return true;
        }
    }
    return false;
}

int maximizeMinimumDistance(vector<int> pos, int k) {
    sort(pos.begin(), pos.end());

    int left = 0;
    int right = pos.back() - pos.front();

    while (left < right) {
        int mid = left + (right - left + 1) / 2;
        if (canPlace(pos, k, mid)) {
            left = mid;
        } else {
            right = mid - 1;
        }
    }
    return left;
}
```

이런 문제는 "정답을 직접 만들기 어렵지만, 어떤 값이 가능한지는 빠르게 검사할 수 있다"는 특징이 있습니다.

## 10. 실수 줄이는 불변식

이분 탐색을 짤 때는 아래 문장을 먼저 정합니다.

```text
left는 어떤 의미인가?
right는 어떤 의미인가?
답은 항상 어디에 남아 있는가?
```

예를 들어 첫 `true`를 찾는 코드는 반복 내내 답이 `[left, right]` 안에 남아 있습니다.

```text
can(mid) == true  -> mid도 가능하므로 답은 [left, mid]
can(mid) == false -> mid 이하는 불가능하므로 답은 [mid + 1, right]
```

마지막 `true`를 찾는 코드도 마찬가지입니다.

```text
can(mid) == true  -> mid도 가능하므로 답은 [mid, right]
can(mid) == false -> mid 이상은 불가능하므로 답은 [left, mid - 1]
```

이 문장을 코드와 맞춰 보면 `+1`, `-1`, 올림 mid가 왜 필요한지 보입니다.

## 11. 실수 사례

첫 번째 실수는 무한 루프입니다.

```cpp
// 마지막 true를 찾는데 mid를 내림으로 잡으면 위험하다.
int mid = (left + right) / 2;
if (can(mid)) left = mid;
else right = mid - 1;
```

`left + 1 == right`이고 `mid == left`이면 `left`가 그대로라 반복이 끝나지 않습니다. 마지막 `true`를 찾을 때는 보통 `mid = left + (right - left + 1) / 2`를 씁니다.

두 번째 실수는 범위가 답을 포함하지 않는 것입니다. `right`가 충분히 가능한 값인지, `left`가 충분히 불가능하거나 가능한 기준인지 확인해야 합니다.

세 번째 실수는 판정 함수가 단조가 아닌데 이분 탐색하는 것입니다. `can(x)`의 결과가 한 번만 바뀌는지 먼저 증명해야 합니다.

네 번째 실수는 오버플로입니다.

```cpp
int mid = (left + right) / 2; // left + right가 넘칠 수 있다.
```

아래처럼 쓰는 습관이 안전합니다.

```cpp
long long mid = left + (right - left) / 2;
```

## 12. 실수형 이분 탐색

답이 실수인 경우에는 반복 횟수를 정해 두고 돌립니다.

```cpp
double binarySearchDouble(double left, double right) {
    for (int iter = 0; iter < 80; ++iter) {
        double mid = (left + right) / 2.0;
        if (can(mid)) {
            right = mid;
        } else {
            left = mid;
        }
    }
    return right;
}
```

실수형은 `left < right` 같은 조건으로 종료하려고 하면 정밀도 때문에 까다롭습니다. 보통 60에서 100회 정도 반복하면 충분합니다.

단, 정수 답을 구할 수 있는 문제를 실수 이분 탐색으로 풀면 오차 처리가 더 어려워질 수 있습니다. 정수 문제는 정수 이분 탐색을 우선합니다.

## 13. 문제를 볼 때 체크할 조건

1. 배열이나 후보가 정렬되어 있는가?
2. 조건이 `false false true true` 또는 `true true false false`처럼 한 번만 바뀌는가?
3. "값 x가 가능한가?"를 `O(n)` 또는 `O(n log n)` 안에 검사할 수 있는가?
4. 최소 가능한 값을 찾는가, 최대 가능한 값을 찾는가?
5. `left`, `right`가 답을 반드시 포함하는가?

이 다섯 가지가 명확하면 이분 탐색 코드는 짧습니다. 어려운 부분은 코드를 외우는 것이 아니라, 단조 판정 함수를 정확히 만드는 것입니다.
