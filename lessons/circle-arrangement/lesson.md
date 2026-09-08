# Circle Arrangement

Circle Arrangement는 여러 원의 교점으로 arc를 나누고, union area, union perimeter, depth 같은 값을 angular sweep으로 계산하는 기하 응용 레슨입니다. Circle Geometry가 두 원과 직선의 교점 공식을 다뤘다면, 이 레슨은 많은 원이 만드는 arrangement에서 어떤 arc가 외곽 또는 특정 depth에 속하는지 판정합니다.

## 문제 신호

| 문제 표현 | Circle Arrangement 관점 |
| --- | --- |
| 여러 원의 합집합 넓이 | arc 분할 + Green theorem |
| 원들의 외곽 둘레 | cover depth가 1인 boundary arc |
| 정확히 k개 원에 덮인 영역 | depth별 angular sweep |
| 원끼리 많이 교차 | arrangement vertices |
| 포함된 원 제거 가능 | containment preprocessing |

직사각형 union은 x sweep으로 풀지만, 원 union은 각 원의 둘레를 angular interval로 쪼개는 접근이 자주 쓰입니다.

## Arc 분할 아이디어

각 원 `i`에 대해 다른 원 `j`와의 교점을 구하고, 그 교점들이 만드는 각도를 모읍니다. 인접한 두 angle 사이 arc는 다른 원들과의 포함 관계가 변하지 않습니다.

```text
angles = [0, 2pi]
for every other circle:
  if intersects current circle:
    add angle of intersection point 1
    add angle of intersection point 2
sort angles
for each neighboring angle interval:
  test midpoint
```

midpoint가 몇 개 원 안에 들어가는지 세면 그 arc의 depth를 알 수 있습니다.

## 포함 관계

원 `A`가 원 `B` 안에 완전히 들어가면 `A`의 arc는 union boundary에 기여하지 않을 수 있습니다.

```text
distance(centerA, centerB) + rA <= rB
```

같은 중심, 같은 반지름 원은 중복입니다. union 면적·둘레에서는 같은 원을 하나로 합칩니다. depth별 면적에서는 중복 개수를 multiplicity로 보존해야 하므로 단순 제거하면 안 됩니다.

## Angle 정규화

각도는 `[0, 2pi)`로 정규화하고, wrap-around interval을 처리하기 위해 `0`과 `2pi`를 항상 넣습니다.

각도를 정규화한 뒤 정렬하고 같은 교점 각도를 합칩니다. 0과 2π 경계는 유지합니다.

교점이 접하는 경우 같은 angle이 두 번 나올 수 있습니다. 중복 제거를 하지 않으면 길이 0 arc가 생깁니다.

## Arc Midpoint 판정

원 `i`의 arc angle interval `(a, b)`를 볼 때 midpoint angle `m`을 잡고 점을 만듭니다.

```text
p = center_i + r_i * (cos m, sin m)
depth = p를 포함하는 원 개수
```

같은 원을 제거한 union 계산에서는 현재 원 이외의 어느 원 내부에도 들어가지 않는 arc 길이 `r_i * (b-a)`를 더합니다. 현재 원 위 점을 실수 오차 때문에 자기 자신의 바깥으로 세지 않도록 other-depth=0으로 검사합니다. 다른 원 안에 들어간 arc는 외곽이 아닙니다.

## Area 계산 관점

원 union area는 boundary arc contribution을 더하는 방식으로 계산할 수 있습니다. arc endpoint를 `P(a)`, `P(b)`라고 할 때, Green theorem 기반으로 segment triangle area와 circular sector area를 합칩니다.

```text
arc contribution =
  cross(P(a), P(b)) / 2
  + r^2 * (theta - sin(theta)) / 2
```

부호와 방향을 일관되게 두어야 합니다. 처음 구현할 때는 perimeter나 depth counting부터 맞춘 뒤 area를 붙이는 편이 안전합니다.

## 작은 예시

```text
circle A: center (0,0), r=2
circle B: center (2,0), r=2

A 위 교점 angle은 ±60도다.
A의 오른쪽 arc 일부는 B 안에 들어간다.
A의 왼쪽 큰 arc는 union boundary에 남는다.
B도 대칭적으로 boundary arc를 낸다.
```

두 원 union perimeter는 각 원의 전체 둘레에서 서로 내부에 들어간 arc를 뺀 값입니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| 모든 원 pair 교점 | `O(N^2)` |
| 각 원 angle sort | 전체 `O(N^2 log N)` |
| midpoint depth를 단순 계산 | `O(N^3)` 가능 |
| depth sweep 최적화 | 구현에 따라 `O(N^2 log N)` |

원 개수가 작으면 midpoint마다 모든 원을 검사해도 됩니다. `N`이 커지면 각도 이벤트로 depth를 갱신하는 방식이 필요합니다.
