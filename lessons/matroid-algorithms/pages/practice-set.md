# Practice Set

Matroid Algorithms 허브의 연습은 일반 범용 알고리즘보다 모델 판독과 특수형 구현 가능성 확인에 초점을 둡니다.

## 로컬 완결형 연습: Weighted Partition Matroid

각 물건은 class와 weight를 가지고, class별로 선택할 수 있는 개수가 제한됩니다. 선택한 물건의 weight 합을 최대화하세요.

### 입력

```text
N C
cap_0 cap_1 ... cap_{C-1}
class_0 weight_0
class_1 weight_1
...
class_{N-1} weight_{N-1}
```

- `1 <= N <= 200000`
- `1 <= C <= 200000`
- `0 <= class_i < C`
- `0 <= cap_c <= N`
- `0 <= weight_i <= 10^12`

### 출력

```text
선택 가능한 최대 weight 합
```

### 예시

```text
5 2
1 2
0 10
0 7
1 6
1 5
1 1
```

```text
21
```

### 손으로 따라가는 Trace

weight 내림차순으로 보면 아래 순서입니다.

| item | class | weight | 선택 여부 | 이유 |
| ---: | ---: | ---: | --- | --- |
| 0 | 0 | 10 | 선택 | class 0 capacity 1 사용 |
| 1 | 0 | 7 | 제외 | class 0 capacity 초과 |
| 2 | 1 | 6 | 선택 | class 1 capacity 2 중 1개 사용 |
| 3 | 1 | 5 | 선택 | class 1 capacity 2 중 2개 사용 |
| 4 | 1 | 1 | 제외 | class 1 capacity 초과 |

답은 `10 + 6 + 5 = 21`입니다.

### 구현 기준

```cpp compile-check
#include <algorithm>
#include <iostream>
#include <vector>
using namespace std;

struct Item {
    int cls = 0;
    long long weight = 0;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    int classCount;
    cin >> n >> classCount;

    vector<int> capacity(classCount);
    for (int& value : capacity) {
        cin >> value;
    }

    vector<Item> items(n);
    for (Item& item : items) {
        cin >> item.cls >> item.weight;
    }

    sort(items.begin(), items.end(), [](const Item& left, const Item& right) {
        return left.weight > right.weight;
    });

    vector<int> used(classCount, 0);
    long long answer = 0;
    for (const Item& item : items) {
        if (used[item.cls] == capacity[item.cls]) {
            continue;
        }
        ++used[item.cls];
        answer += item.weight;
    }

    cout << answer << '\n';
}
```

### 왜 Greedy가 맞는가

Partition matroid의 독립 집합은 "각 class에서 capacity 이하로 고른 집합"입니다. 어떤 최적해 `O`가 greedy가 고른 가장 무거운 item `g`를 포함하지 않는다고 합시다. `g`의 class에 아직 자리가 있으면 그냥 추가할 수 있고, 자리가 없다면 같은 class에서 `g`보다 가볍거나 같은 item 하나를 빼고 `g`로 바꿀 수 있습니다. 이 교환은 독립성을 깨지 않고 weight를 줄이지 않습니다. 이 과정을 greedy 순서대로 반복하면 greedy 해와 같은 weight의 최적해를 만들 수 있습니다.

### Stress 기준

1. `N <= 20`에서는 모든 subset을 열거해 class별 capacity를 만족하는 최대 weight와 비교합니다.
2. capacity가 0인 class, 같은 weight가 많은 입력, item이 한 class에 몰린 입력을 deterministic case로 둡니다.
3. class별로 따로 상위 `cap_c`개를 고른 합과 greedy 결과가 같은지도 cross-check할 수 있습니다.
