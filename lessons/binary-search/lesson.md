# 이분 탐색과 파라메트릭 서치

이분 탐색은 정렬되어 있거나 단조성이 있는 공간에서 답의 후보를 절반씩 줄이는 기법입니다. 단순히 배열에서 값을 찾는 것뿐 아니라, "이 값으로 가능한가?"라는 판정 함수를 만들고 정답 범위를 좁히는 데에도 자주 쓰입니다.

```text
정렬된 배열에서 x 이상의 첫 위치를 찾는다.
가능한 최소 시간을 찾는다.
조건을 만족하는 최대 길이를 찾는다.
```

반복 중에도 유지되는 조건인 **불변식**으로 양 끝의 의미를 정합니다. 탐색 구간을 줄일 때도 답이 그 안에 남아 있어야 합니다.

## lower_bound

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

## 같은 값이 여러 개 있을 때

`lowerBound`가 돌려준 위치가 배열 안에 있고 그 값이 `target`과 같으면 값이 존재합니다. `target`보다 **큰** 첫 위치가 필요하면 비교 조건을 `a[mid] < target`에서 `a[mid] <= target`으로 바꿉니다. 이것이 `upper_bound`입니다.

같은 값의 개수는 두 경계의 차이입니다. `[1, 3, 3, 7, 9]`에서 3의 경계는 1과 3이므로 개수는 2입니다. 두 함수 모두 배열이 오름차순으로 정렬되어 있어야 합니다.

## 단조 조건

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

## 가능한 최소값 찾기

시간 `t` 안에 작업을 끝낼 수 있는지 판정할 수 있다면 답 자체를 이분 탐색할 수 있습니다. 더 긴 시간을 주었을 때 가능했던 작업이 불가능해지지는 않으므로, 판정 결과는 `F F F T T T`처럼 한 번만 바뀝니다.

답을 포함하는 `[left, right]`에서 `mid`가 가능하면 `right = mid`, 불가능하면 `left = mid + 1`로 줄입니다. 시작할 때 `right`가 가능한 값이어야 합니다.

## 가능한 최대값 찾기

반대로 요구하는 최소 간격이 커질수록 배치가 어려워지는 문제는 `T T T F F F`에서 마지막 `true`를 찾습니다. `mid`가 가능하면 `left = mid`, 불가능하면 `right = mid - 1`입니다.

이때는 `mid = left + (right - left + 1) / 2`로 올림합니다. `[3, 4]`에서 내림한 3이 가능하다고 `left = 3`을 다시 대입하면 구간이 줄지 않기 때문입니다. 아래 최대 거리 구현에서 이 차이를 볼 수 있습니다.

## 예시: 최소 처리 시간

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

기계는 하나 이상이고, 각 처리 시간과 목표 수량은 양수라고 가정합니다. 가능한 상한을 모르면 위처럼 두 배씩 늘릴 수 있습니다. 다만 `right *= 2`와 생산량 누적이 `long long`을 넘지 않는 입력 범위에서 사용해야 합니다.

## 예시: 가능한 최대 거리

정렬된 위치 배열 `pos`에서 물체 `k`개를 놓되, 인접한 물체 사이 최소 거리를 최대화한다고 하겠습니다.

`2 <= k <= pos.size()`이고 좌표가 `0..10^9`라고 가정합니다. 거리 `d`가 가능하면 그보다 작은 거리도 가능하므로 마지막 `true`를 찾습니다.

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
