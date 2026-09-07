# 휴리스틱 알고리즘: 실전 예시 - 배송 순서 개선

## 문제 계약을 상태로 옮기기

[미니 물품 배송](/practice/ORDERING)에서 구현할 함수는 다음과 같습니다.

```cpp
extern int get_dist(int a, int b);
extern int get_path_dist(const int order[], int size);

void build_path(int n, const int points[][2], int order[]);
```

`build_path`는 값을 반환하지 않습니다. 최종 방문 순서를 `order[0]`부터 `order[n - 1]`까지 직접 써 넣어야 합니다.

| 항목 | 계약 |
| --- | --- |
| 상태 | `0`부터 `n - 1`까지 정확히 한 번씩 들어간 순열 `order[]` |
| 시작점 | `order[0] = 0`인 창고 고정 |
| 거리 | `get_dist(a, b)`가 주는 맨해튼 거리 |
| 목적 함수 | 인접한 두 위치 사이 거리의 합을 최소화 |
| 끝점 | 마지막 배송지에서 창고로 돌아오지 않는 열린 경로 |
| 보조 함수 | `get_path_dist(order, size)`로 부분 또는 전체 경로 거리 확인 |
| 잘못된 답 | 중복, 누락, 범위 밖 번호, `order[0] != 0`이면 큰 패널티 |

테스트의 `n`은 `4, 8, 12, 16, 20, 36, 52, 68, 84, 100`입니다. 가장 큰 경우에는 모든 순열을 볼 수 없으므로, 작은 경우의 exact 탐색과 큰 경우의 휴리스틱을 분리해 생각할 수 있습니다.

## 점수식을 먼저 정확히 쓴다

이 문제의 점수는 다음과 같습니다.

```text
cost(order) =
    dist(order[0], order[1])
  + dist(order[1], order[2])
  + ...
  + dist(order[n - 2], order[n - 1])
```

TSP 순회와 달리 아래 항은 없습니다.

```text
dist(order[n - 1], order[0])
```

이 차이는 초기해와 개선 연산에 모두 영향을 줍니다. 마지막 위치는 창고 근처로 돌아올 필요가 없고, 경로 끝을 포함하는 구간을 뒤집을 때는 오른쪽 바깥 간선도 존재하지 않습니다.

## 0단계: 유효한 기준선

가장 단순한 기준선은 번호 순서입니다.

```cpp
for (int i = 0; i < n; ++i) {
    order[i] = i;
}
```

이 순열의 비용을 기록해 두고 다음 초기해와 비교합니다.

## 1단계: nearest neighbor 초기해

첫 번째 실전 초기해는 현재 위치에서 가장 가까운 미방문 배송지를 고르는 nearest neighbor입니다.

```text
order[0] = 0
used[0] = true

for pos = 1 .. n - 1:
    current = order[pos - 1]
    current에서 가장 가까운 미방문 cand를 찾는다
    order[pos] = cand
    used[cand] = true
```

시간 복잡도는 `O(n^2)`이고 `n <= 100`에서는 충분히 빠릅니다. 매 단계의 선택만 보면 자연스럽지만, 가까운 점을 먼저 소비해 마지막에 멀리 떨어진 점 하나가 남을 수 있으므로 이것만으로 끝내지는 않습니다.

동점 처리도 하나의 파라미터입니다. 같은 거리라면 번호가 작은 점, 다음 후보가 많은 점, 현재 배송지 밀집 구역 안쪽의 점을 고르는 방식이 서로 다른 초기해를 만듭니다.

## 2단계: 열린 경로의 2-opt 차분

`2-opt`는 `order[left..right]` 구간을 뒤집는 연산입니다. 창고를 고정해야 하므로 `left >= 1`인 구간만 고릅니다.

대칭 거리에서는 구간 내부 간선의 방향만 반대로 바뀌고 비용은 같습니다. 따라서 모든 경로를 다시 더하지 않고 경계 간선만 비교할 수 있습니다.

```text
a = order[left - 1]
b = order[left]
c = order[right]

before = dist(a, b)
after  = dist(a, c)
```

`right + 1 < n`이면 오른쪽 경계도 더합니다.

```text
d = order[right + 1]

before += dist(c, d)
after  += dist(b, d)
```

`after < before`이면 구간을 뒤집습니다. `right == n - 1`일 때는 오른쪽 경계 간선이 없으므로 첫 비교만 해야 합니다. TSP용 2-opt 공식을 그대로 복사해 마지막 위치와 창고 사이의 가짜 복귀 간선을 넣으면 다른 문제를 최적화하게 됩니다.

## 작은 경로를 손으로 따라가기

다음처럼 x축 위에 다섯 위치가 있다고 하겠습니다.

```text
0 = 0, A = 1, B = 9, C = 8, D = 2
```

현재 경로가 `0 -> A -> B -> C -> D`이면 비용은 다음과 같습니다.

```text
1 + 8 + 1 + 6 = 16
```

꼬리 구간 `B -> C -> D`를 뒤집으면 `0 -> A -> D -> C -> B`가 됩니다.

```text
1 + 1 + 6 + 1 = 9
```

이때 내부 간선 `B-C`, `C-D`는 방향만 바뀌므로 총비용이 같습니다. 실제 변화는 `A-B`가 `A-D`로 바뀐 것뿐입니다. 열린 경로의 끝을 뒤집을 때 경계 하나만 비교하는 이유가 여기서 보입니다.

작은 입력에서 모든 `left, right` 조합을 뒤집어 보고, 차분식의 결과가 `get_path_dist`로 다시 구한 비용 변화와 같은지 대조합니다. 인접한 두 점과 경로 끝을 포함하는 구간도 넣습니다.

## 제출 가능한 기본 구현

아래 코드는 nearest neighbor로 초기해를 만든 뒤, 더 좋아지는 2-opt만 반복합니다. STL이나 C 헤더 없이 고정 배열과 helper 함수만 사용합니다.

```cpp compile-check
extern int get_dist(int a, int b);
extern int get_path_dist(const int order[], int size);

static void reverse_range(int order[], int left, int right) {
    while (left < right) {
        int temp = order[left];
        order[left] = order[right];
        order[right] = temp;
        ++left;
        --right;
    }
}

void build_path(int n, const int points[][2], int order[]) {
    int used[100];
    (void)points;

    for (int i = 0; i < n; ++i) {
        used[i] = 0;
    }

    order[0] = 0;
    used[0] = 1;

    for (int pos = 1; pos < n; ++pos) {
        int current = order[pos - 1];
        int best = -1;
        int best_dist = 0;

        for (int cand = 0; cand < n; ++cand) {
            if (used[cand]) continue;

            int dist = get_dist(current, cand);
            if (best == -1 || dist < best_dist) {
                best = cand;
                best_dist = dist;
            }
        }

        order[pos] = best;
        used[best] = 1;
    }

    for (int pass = 0; pass < 80; ++pass) {
        int improved = 0;

        for (int left = 1; left < n - 1; ++left) {
            for (int right = left + 1; right < n; ++right) {
                int a = order[left - 1];
                int b = order[left];
                int c = order[right];
                int before = get_dist(a, b);
                int after = get_dist(a, c);

                if (right + 1 < n) {
                    int d = order[right + 1];
                    before += get_dist(c, d);
                    after += get_dist(b, d);
                }

                if (after < before) {
                    reverse_range(order, left, right);
                    improved = 1;
                }
            }
        }

        if (!improved) break;
    }
}
```

구간 뒤집기는 순열의 원소를 추가하거나 지우지 않으므로 유효성을 자동으로 보존합니다. `left`가 1 이상이므로 창고도 항상 첫 위치에 남습니다.

## 2-opt 다음 개선 연산

2-opt가 멈췄다고 해서 좋은 경로를 모두 본 것은 아닙니다. 서로 다른 모양의 이웃을 추가하면 다른 지역 최적으로 이동할 수 있습니다.

| 연산 | 변화 | 주의할 경계 |
| --- | --- | --- |
| insertion | 한 위치를 빼서 다른 두 위치 사이에 삽입 | index 이동 뒤 위치 보정, 경로 끝 |
| swap | 두 배송지의 순서를 교환 | 두 위치가 인접할 때 겹치는 간선 |
| double bridge | 떨어진 여러 구간의 연결을 크게 변경 | 작은 `n`에서는 변화가 지나치게 큼 |
| perturb + 2-opt | 몇 번 무작위로 흔든 뒤 다시 2-opt | 현재 best와 작업용 current 분리 |

insertion은 2-opt로 만들기 어려운 변화를 한 번에 만들 수 있습니다. 이때도 이동 전후에 달라지는 주변 간선만 계산하면 후보 하나를 `O(1)`에 평가할 수 있습니다. 다만 시작점 `0`은 이동 대상에서 제외해야 합니다.

나쁜 이동을 잠시 허용하려면 `current`와 `best`를 분리합니다. `current`는 흔들 수 있지만, 제출할 `best`는 실제 `get_path_dist`가 더 짧을 때만 교체하면 안전합니다.

## 초기해를 여러 개 만드는 법

nearest neighbor가 만드는 경로는 첫 몇 번의 선택에 크게 좌우됩니다. `order[0] = 0`은 고정이지만 두 번째 배송지는 여러 후보를 시도할 수 있습니다.

```text
창고에서 가까운 후보 K개를 고른다
각 후보를 두 번째 위치로 고정한다
나머지는 nearest neighbor로 채운다
각 완성 경로에 2-opt를 적용한다
get_path_dist로 가장 짧은 경로를 남긴다
```

`n <= 100`이면 `K`를 작게 둔 multi-start도 충분히 가볍습니다. 완전히 무작위인 시작만 반복하는 것보다, 서로 다른 두 번째 배송지를 강제하면 탐색한 초기해의 차이가 분명해집니다.

## 작은 입력은 exact 탐색으로 쓴다

`n = 4`이면 창고를 제외한 순열은 `3! = 6`개이고, `n = 8`이어도 `7! = 5040`개입니다. 이 두 경우는 모든 순열을 직접 확인할 수 있습니다.

작은 입력의 exact 탐색은 두 가지 역할을 합니다.

1. 앞 테스트 케이스의 점수를 실제 최적으로 만든다.
2. nearest neighbor와 2-opt가 최적해에서 얼마나 떨어지는지 확인하는 oracle이 된다.

`n = 12`부터는 `11!`이라 같은 방식이 급격히 비싸집니다.
