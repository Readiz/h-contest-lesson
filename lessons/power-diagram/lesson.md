# Power Diagram

Power Diagram은 점마다 가중치가 있을 때 "가까움"을 `거리 제곱 - weight`로 정의하는 weighted Voronoi 구조입니다. 일반 Voronoi가 가장 가까운 점을 나누는 구조라면, Power Diagram은 반지름이 다른 원이나 영향력이 다른 점의 지배 영역을 선형 경계로 나눕니다.

이 레슨은 Voronoi와 Delaunay, Half-Plane Intersection, Shape Distance Modeling 이후에 보는 기하 심화입니다.

1. weighted distance를 power distance로 바꾼다.
2. 두 site의 경계가 직선이 된다는 점을 이용한다.
3. cell을 half-plane intersection이나 lower envelope로 계산한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Voronoi/Delaunay, Half-Plane Intersection, Robust Geometry Predicates
- 함께 보면 좋은 레슨: Shape Distance Modeling, Circle Geometry, Robust Delaunay
- 다음에 볼 레슨: regular triangulation, weighted nearest neighbor, 3D convex hull lifting

## 1. 문제 신호

| 문제 표현 | Power Diagram 관점 |
| --- | --- |
| 점마다 반지름이나 영향력이 다르다 | additive weight |
| `dist^2 - r^2`가 최소인 영역 | power distance |
| weighted Voronoi가 필요하다 | power cell |
| 원들의 radical axis가 나온다 | 두 weighted site의 경계 |
| 일반 Voronoi보다 큰 점이 영역을 더 가져간다 | weight가 cell을 밀어냄 |

Power distance는 아래처럼 정의합니다.

```text
power_i(x) = |x - p_i|^2 - w_i
```

가중치가 클수록 같은 위치에서 power value가 작아지므로 더 넓은 영역을 차지할 수 있습니다.

## 2. 경계가 직선이 되는 이유

두 site `a`, `b`의 경계는 `power_a(x) = power_b(x)`입니다.

```text
|x - a|^2 - w_a = |x - b|^2 - w_b
```

제곱항 `|x|^2`가 양쪽에서 사라지므로 남는 식은 일차식입니다.

```text
2(b - a) dot x = |b|^2 - |a|^2 + w_a - w_b
```

따라서 Power Diagram의 cell은 여러 half-plane의 교집합입니다. 일반 Voronoi와 마찬가지로 convex polygon이 됩니다. 다만 어떤 site는 weight 차이 때문에 cell이 아예 사라질 수 있습니다.

## 3. 작은 예시

두 점이 있습니다.

```text
A = (0, 0), w_A = 0
B = (4, 0), w_B = 12
```

경계는 아래 식입니다.

```text
x^2 + y^2 = (x - 4)^2 + y^2 - 12
0 = -8x + 16 - 12
x = 0.5
```

가중치가 없었다면 경계는 `x = 2`입니다. `B`의 weight가 크기 때문에 `B`가 왼쪽까지 더 넓게 가져가고, 경계가 `A` 쪽으로 밀립니다.

## 4. Cell 계산

특정 site `i`의 cell을 계산하려면 모든 다른 site `j`에 대해 아래 조건을 만족해야 합니다.

```text
power_i(x) <= power_j(x)
```

이를 half-plane으로 바꿔서 bounding box와 함께 교집합을 구합니다.

```text
2(p_j - p_i) dot x <= |p_j|^2 - |p_i|^2 + w_i - w_j
```

site 수가 작으면 site마다 half-plane intersection을 돌려도 됩니다. 전체 diagram을 효율적으로 만들려면 regular triangulation이나 lifting 관점을 사용하지만, 구현 난도는 훨씬 높습니다.

## 5. 구현 조각

```cpp
struct WeightedPoint {
    long double x = 0;
    long double y = 0;
    long double weight = 0;
};

long double powerDistance(const WeightedPoint& point, long double x, long double y) {
    long double dx = x - point.x;
    long double dy = y - point.y;
    return dx * dx + dy * dy - point.weight;
}

long double boundaryValue(const WeightedPoint& a, const WeightedPoint& b, long double x, long double y) {
    return powerDistance(a, x, y) - powerDistance(b, x, y);
}
```

`boundaryValue(a, b, x, y) <= 0`이면 점 `(x, y)`는 `a`가 `b`보다 같거나 더 가까운 쪽입니다. 실제 half-plane intersection에서는 이 부등식을 직선 계수로 바꿔 사용하는 편이 안정적입니다.

## 6. Radical Axis와 원

원 `i`의 중심을 `p_i`, 반지름을 `r_i`라고 하면 `w_i = r_i^2`로 둘 수 있습니다. 그러면 power distance는 점이 원에 대해 가지는 power와 같습니다.

두 원에 대한 power가 같은 점들의 집합은 radical axis입니다. 그래서 Power Diagram은 여러 원의 radical axis들이 만드는 cell 구조로 볼 수 있습니다.

## 7. 시간 복잡도

| 접근 | 시간 |
| --- | ---: |
| 한 site cell을 모든 half-plane으로 계산 | `O(N log N)` 또는 구현에 따라 `O(N^2)` |
| 모든 site에 대해 반복 | `O(N^2 log N)` 이상 |
| regular triangulation 기반 전체 구성 | 구현/라이브러리 의존 |

대회에서는 보통 전체 diagram 라이브러리 구현보다 "특정 점이 어느 site에 속하는지", "site 몇 개의 경계가 어디인지", "cell이 비었는지" 같은 제한된 형태로 나옵니다.

## 8. 자주 하는 실수

1. `dist - weight`로 정의해서 경계가 직선이 아니게 만든다.
2. weight를 반지름으로 넣고 `r^2`를 빼야 하는 문제에서 `r`만 뺀다.
3. cell이 사라질 수 있다는 점을 잊는다.
4. 일반 Voronoi처럼 경계가 항상 두 점의 수직이등분선이라고 가정한다.
5. floating EPS와 exact predicate 정책을 섞어 경계 위 점을 불안정하게 처리한다.

## 9. 문제를 볼 때 체크할 조건

- 거리 정의가 `squared distance - weight`인가?
- weight가 반지름인지, 반지름 제곱인지 문제에서 어떻게 주는가?
- 전체 diagram이 필요한가, 한 cell이나 query만 필요한가?
- 좌표 범위가 exact integer predicate로 처리 가능한가?
- cell이 비어도 되는 입력인가?

## 10. 대표 문제로 연결하기

### 문제에서 보이는 신호

- 입력 크기: site 수가 중간 이하이거나 query 중심
- 필요한 복잡도: half-plane 또는 lower envelope
- 이 레슨의 핵심 개념: power distance와 radical axis

### 풀이 흐름

1. 각 site의 weight를 문제 조건에 맞게 정규화한다.
2. 두 site 경계식을 일차 부등식으로 전개한다.
3. 필요한 cell의 half-plane 목록을 만든다.
4. 빈 cell, 경계 위 tie, bounding box를 처리한다.
5. 작은 입력을 grid sampling으로 시각적으로 검증한다.

### 자주 틀리는 지점

- Power Diagram의 경계는 weighted point 두 개의 radical axis입니다.
- 가중치가 큰 site가 항상 cell을 갖는 것은 아닙니다. 다른 site와 위치에 따라 사라질 수 있습니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: power distance `/practice/...` 문제 필요 | weighted nearest site 판정 | `dist^2 - w` |
| 표준 | TODO: radical axis `/practice/...` 문제 필요 | 두 원의 power 경계 계산 | linear boundary |
| 응용 | TODO: power cell `/practice/...` 문제 필요 | half-plane intersection으로 cell 구하기 | convex polygon |
| 함정 | TODO: empty weighted cell `/practice/...` 문제 필요 | 사라지는 cell과 tie 처리 | degeneracy |
