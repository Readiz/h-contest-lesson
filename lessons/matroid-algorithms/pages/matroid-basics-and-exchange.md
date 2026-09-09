# Matroid Basics and Exchange

Matroid는 greedy가 맞는 독립성 구조를 추상화한 모델입니다. 독립 집합의 모든 부분집합도 독립이고, 작은 독립 집합은 큰 독립 집합의 어떤 원소를 받아 더 커질 수 있다는 exchange 성질이 핵심입니다.


최대 가중치 독립 집합은 음수 weight 원소를 건너뜁니다. 반드시 기저를 골라야 하는 문제는 최대 rank까지 채워야 하므로 음수도 필요할 수 있습니다. 단일 matroid의 가중치 문제 자체는 greedy 적용 대상입니다.

## 독립성 공리

원소 집합 `E`와 독립 집합들의 모음 `I`가 있을 때, matroid는 보통 아래 성질을 만족합니다.

```text
1. empty set is independent
2. A is independent and B subset A -> B is independent
3. |A| < |B| and A, B independent -> exists x in B-A such that A+x independent
```

세 번째 성질이 greedy와 exchange algorithm의 근거입니다. 단순히 "제약이 있다"는 이유만으로 matroid가 되는 것은 아닙니다.

## 대표 예시

| Matroid | 독립 집합 | 구현 신호 |
| --- | --- | --- |
| Partition matroid | class별 capacity를 넘지 않는 집합 | count array |
| Graphic matroid | cycle이 없는 edge set | DSU, forest |
| Linear matroid | 선형 독립인 vector set | Gaussian elimination, XOR basis |
| Uniform matroid | 크기가 `k` 이하인 집합 | cardinality |

대회 문제에서 matroid라는 이름이 직접 나오지 않아도, 위 구조가 보이면 greedy 증명이나 exchange graph를 의심할 수 있습니다.

## Greedy가 맞는 경우

하나의 matroid에서 가중치 합이 최대인 독립 집합을 찾는 문제는 weight 내림차순 greedy가 맞습니다.

```text
sort elements by weight desc
for e in sorted order:
    if weight(e) >= 0 and S + e is independent:
        add e
```

이때 필요한 것은 `S + e` 독립성 판정입니다. Partition matroid라면 count, graphic matroid라면 DSU, linear matroid라면 basis insertion입니다.

## Greedy가 부족한 경우

아래 상황에서는 단일 matroid greedy가 아니라 별도 알고리즘이 필요할 수 있습니다.

- 두 matroid 조건을 동시에 만족해야 한다.
- pair 단위로만 선택할 수 있다.
- 여러 independent set으로 전체를 나눠야 한다.
- 이미 고른 원소를 빼고 다른 원소를 넣는 연쇄 교환이 필요하다.

이때부터 Matroid Intersection, Parity, Union 같은 reference 페이지로 내려갑니다.

## 교환 공리가 깨지는 반례

양수 크기 3,2,2인 원소 a,b,c에서 총 크기<=4인 집합을 독립이라고 둡니다. 부분집합 폐쇄성은 성립하지만 A={a}, B={b,c}에서 |A|<|B|이고 B의 어느 원소도 A에 추가할 수 없습니다. 따라서 matroid가 아닙니다. “정확히 2개” 조건은 애초에 빈 집합·부분집합 폐쇄성을 만족하지 않습니다.

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
