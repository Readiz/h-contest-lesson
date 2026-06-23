# Inversion Geometry

Inversion Geometry는 한 점을 중심으로 `OP * OP' = r^2`가 되게 변환해 원과 직선 문제를 다른 형태로 단순화하는 계산기하 심화입니다. 접선, 원다발, 교점 조건이 복잡할 때 inversion을 쓰면 원이 직선으로 바뀌거나 거리 조건이 각도 조건으로 바뀝니다.

이 레슨은 Circle Geometry와 Robust Geometry Predicates 이후에 보는 기하 심화입니다.

1. inversion center와 radius를 문제의 대칭점에 맞춘다.
2. 중심을 지나는 원/직선과 지나지 않는 원/직선을 구분한다.
3. 변환 뒤 문제를 풀고 원래 좌표 해석으로 되돌린다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Circle Geometry, Robust Geometry Predicates, Shape Distance Modeling
- 함께 보면 좋은 레슨: Circle Arrangement, Voronoi와 Delaunay, Half-Plane Intersection
- 다음에 볼 레슨: robust Delaunay, advanced circle transformations, angle chasing

## 1. 문제 신호

| 문제 표현 | Inversion 관점 |
| --- | --- |
| 한 점을 지나는 원들이 많음 | 중심을 그 점으로 잡으면 직선으로 변환 |
| 접선/교점 조건이 반복됨 | angle 보존 활용 |
| 원과 직선이 섞여 있음 | 변환 후 같은 유형으로 정리 |
| 거리 곱 조건 `OP * OQ = const` | inversion 정의와 직접 연결 |
| 원다발 coaxal family | 공통점 중심 inversion 후보 |

Inversion은 강력하지만 좌표 구현이 까다롭습니다. 공식 적용 전에 변환 후 도형 타입이 무엇인지 먼저 표로 정리해야 합니다.

## 2. 기본 공식

중심 `O`, 반지름 `R`인 inversion에서 점 `P`는 같은 반직선 위의 `P'`로 이동합니다.

```text
OP * OP' = R^2
P' = O + (P - O) * R^2 / |P - O|^2
```

중심점 `O` 자체는 무한대로 가므로 직접 변환할 수 없습니다.

## 3. 점 변환 구현

```cpp compile-check
#include <cmath>
using namespace std;

struct InversionPoint {
    double x = 0;
    double y = 0;
};

InversionPoint operator+(InversionPoint a, InversionPoint b) {
    return {a.x + b.x, a.y + b.y};
}

InversionPoint operator-(InversionPoint a, InversionPoint b) {
    return {a.x - b.x, a.y - b.y};
}

InversionPoint operator*(InversionPoint a, double scale) {
    return {a.x * scale, a.y * scale};
}

double dotInversion(InversionPoint a, InversionPoint b) {
    return a.x * b.x + a.y * b.y;
}

InversionPoint invertPoint(
    InversionPoint center,
    double radius,
    InversionPoint point
) {
    InversionPoint delta = point - center;
    double lengthSquared = dotInversion(delta, delta);
    double scale = radius * radius / lengthSquared;
    return center + delta * scale;
}
```

`point == center`인 경우는 호출 전에 제외해야 합니다. EPS 기준으로 중심에 너무 가까운 점도 수치적으로 불안정합니다.

## 4. 도형이 어떻게 바뀌는가

| 원래 도형 | inversion 후 |
| --- | --- |
| 중심을 지나는 직선 | 같은 직선 |
| 중심을 지나지 않는 직선 | 중심을 지나는 원 |
| 중심을 지나는 원 | 중심을 지나지 않는 직선 |
| 중심을 지나지 않는 원 | 중심을 지나지 않는 다른 원 |

가장 유용한 경우는 "중심을 지나는 원"이 직선으로 바뀌는 경우입니다. 원 여러 개의 교점/접선 문제가 직선 배열 문제로 내려갈 수 있습니다.

## 5. 작은 예시

중심 `O=(0,0)`, `R=1`인 inversion에서 점 `(2,0)`은 `(1/2,0)`으로 갑니다.

```text
OP = 2
OP' = 1 / 2
OP * OP' = 1
```

점 `(1/2,0)`을 다시 inversion하면 `(2,0)`으로 돌아옵니다. 즉 inversion은 자기 자신의 역변환입니다.

## 6. 원이 직선으로 바뀌는 예시

원 `x^2 + y^2 - ax - by = 0`은 원점 `(0,0)`을 지납니다. 원점 중심 unit inversion을 적용하면 이 원은 직선으로 바뀝니다.

```text
aX + bY = 1
```

그래서 원점을 지나는 원들의 교차/접선 관계를 직선들의 관계로 바꿀 수 있습니다. 이 성질은 원다발 문제에서 특히 자주 쓰입니다.

## 7. Angle 보존

Inversion은 conformal transformation이라 교차각을 보존합니다. 길이는 보존하지 않지만 두 곡선이 만나는 각도는 유지됩니다.

접선 조건이 중요한 문제에서 이 성질이 유용합니다.

```text
두 원이 접한다
-> inversion 후 두 직선/원이 접하거나 평행 관계가 된다
```

단, 방향과 내부/외부 관계는 바뀔 수 있으므로 도형 타입과 위치를 다시 판정해야 합니다.

## 8. 언제 쓰지 않는가

| 상황 | 이유 |
| --- | --- |
| 단순 circle-line intersection | 일반 공식이 더 쉽다 |
| 좌표 출력 정밀도가 매우 빡빡함 | inversion 후 수치 오차 증가 |
| 중심 후보가 명확하지 않음 | 식만 복잡해질 수 있음 |
| 변환 후에도 도형 수가 줄지 않음 | 이득이 작음 |

Inversion은 구현 트릭이 아니라 모델링 도구입니다. 변환 후 문제가 실제로 단순해질 때만 씁니다.

## 9. 구현 체크리스트

1. inversion center가 어떤 점인지 고정한다.
2. center를 지나는 도형인지 EPS로 판정한다.
3. 변환 후 도형 타입을 명시한다.
4. 원래 문제의 포함/접선/교점 조건이 어떻게 바뀌는지 쓴다.
5. 최종 답을 원래 좌표계로 되돌릴 필요가 있는지 확인한다.

## 10. 자주 하는 실수

1. inversion center 자체를 변환하려 한다.
2. 중심을 지나는 원과 지나지 않는 원의 변환 공식을 섞는다.
3. 길이가 보존된다고 착각한다.
4. EPS 때문에 중심을 지나는지 아닌지 불안정하게 분기한다.
5. 변환 후 답의 개수는 맞지만 원래 문제의 내부/외부 조건을 복원하지 않는다.

## 11. 문제를 볼 때 체크할 조건

- 공통으로 지나는 점이나 자연스러운 중심이 있는가?
- 원이 직선으로 바뀌면 문제가 쉬워지는가?
- 필요한 답이 좌표인가, 개수/관계인가?
- 변환 후 degeneracy를 처리할 수 있는가?
- 일반 기하 공식보다 inversion이 실제로 구현을 줄이는가?

## 12. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: inversion geometry `/practice/...` 문제 필요 | 점 inversion과 자기 역변환 확인 | inverse point |
| 표준 | TODO: circle through center `/practice/...` 문제 필요 | 원을 직선으로 변환 | circle-line transform |
| 응용 | TODO: tangent circle inversion `/practice/...` 문제 필요 | 접선 조건 단순화 | conformal |
| 함정 | TODO: inversion degeneracy `/practice/...` 문제 필요 | 중심 통과/중심 일치 처리 | degeneracy |
