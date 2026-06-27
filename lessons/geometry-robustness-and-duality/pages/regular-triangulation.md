# Regular Triangulation

Regular Triangulation은 weighted point를 3차원으로 lifting한 뒤 lower hull을 투영해서 얻는 Power Diagram의 dual 구조입니다. 일반 Delaunay Triangulation이 Voronoi Diagram의 dual이라면, Regular Triangulation은 Power Diagram의 dual입니다.

이 레슨은 Power Diagram, Robust Delaunay, 3D Convex Hull 이후에 보는 계산기하 심화입니다.

1. weight가 있는 점을 `z = x^2 + y^2 - w`로 lifting한다.
2. lifted point들의 lower convex hull을 본다.
3. lower face를 평면에 투영해 weighted Delaunay 구조를 얻는다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Power Diagram, Voronoi/Delaunay, 3D Convex Hull
- 함께 보면 좋은 레슨: Robust Geometry Predicates, Half-Plane Intersection, Power Diagram
- 다음에 볼 레슨: weighted Delaunay, power cell query, robust computational geometry

## 1. 문제 신호

| 문제 표현 | Regular Triangulation 관점 |
| --- | --- |
| weighted Voronoi의 dual이 필요하다 | regular triangulation |
| 원 반지름이나 site weight가 있다 | power distance |
| weighted nearest neighbor adjacency를 묻는다 | power cell adjacency |
| Delaunay 조건에 weight가 붙는다 | in-power-circle predicate |
| lifting과 lower hull이 힌트로 나온다 | 3D convex hull projection |

대회에서 전체 Regular Triangulation을 직접 구현하는 경우는 드뭅니다. 하지만 Power Diagram의 이웃 관계, weighted empty circle 판정, weighted Delaunay 성질을 이해하는 데 중요합니다.

## 2. Lifting 변환

2차원 weighted point `(x, y, w)`를 3차원 점으로 올립니다.

```text
lift(x, y, w) = (x, y, x^2 + y^2 - w)
```

weight가 클수록 lifted z값은 낮아집니다. z값이 낮아진 point는 lower hull에 더 잘 나타나고, Power Diagram에서 더 큰 cell을 가질 가능성이 커집니다.

## 3. Power Diagram과의 관계

Power distance는 아래 식입니다.

```text
power_i(q) = |q - p_i|^2 - w_i
```

여기서 `|q|^2` 항은 모든 site에 공통입니다. 따라서 어떤 site가 최소 power를 가지는지는 lifted plane들의 lower envelope로 볼 수 있습니다.

```text
power_i(q) = |q|^2 - 2 p_i dot q + |p_i|^2 - w_i
```

`|p_i|^2 - w_i`가 lifted z값입니다. 즉 Power Diagram의 cell 경계는 lifted geometry의 lower envelope와 맞물립니다.

## 4. 작은 예시

세 점이 있습니다.

```text
A = (0, 0), w = 0  -> z = 0
B = (2, 0), w = 0  -> z = 4
C = (1, 1), w = 3  -> z = -1
```

가중치가 없다면 `C`의 lifted z는 2입니다. 하지만 weight 3 때문에 z가 -1까지 내려갑니다. 그래서 `C`는 Power Diagram에서 더 넓은 영역을 차지하고, regular triangulation의 face 구성도 일반 Delaunay와 달라질 수 있습니다.

## 5. In-Power-Circle 관점

일반 Delaunay에서 한 점이 triangle의 circumcircle 안에 있는지 검사합니다. Regular Triangulation에서는 weight가 들어간 power circle 조건을 봅니다.

```text
point q is inside weighted circle of triangle abc
<=> power value of q is smaller than the supporting power circle
```

구현은 4x4 determinant나 lifted orientation으로 표현할 수 있습니다. 하지만 부호 convention, 좌표 범위, cocircular degeneracy가 까다롭습니다.

## 6. Lifting 코드 조각

전체 hull 구현은 길기 때문에, 먼저 lifting과 z값 계산을 명확히 분리합니다.

```cpp
struct WeightedPoint2D {
    long double x = 0;
    long double y = 0;
    long double weight = 0;
};

struct Point3D {
    long double x = 0;
    long double y = 0;
    long double z = 0;
};

Point3D liftToRegularTriangulation(const WeightedPoint2D& point) {
    return {
        point.x,
        point.y,
        point.x * point.x + point.y * point.y - point.weight
    };
}
```

실제 lower hull을 만들 때는 3D Convex Hull의 face orientation과 exact predicate 정책을 재사용해야 합니다.

## 7. Cell이 사라지는 경우

Power Diagram에서는 어떤 weighted site의 cell이 비어 있을 수 있습니다. Regular Triangulation에서는 그런 site가 lower hull에 나타나지 않는 점으로 해석됩니다.

| 현상 | Power Diagram | Regular Triangulation |
| --- | --- | --- |
| site가 지배 영역을 가짐 | non-empty cell | lower hull에 참여 |
| site가 완전히 덮임 | empty cell | lower hull에서 사라짐 |
| 두 cell이 변을 공유 | neighboring cells | triangulation edge |
| 세 cell이 만남 | power vertex | triangulation face |

이 대응을 알면 weighted nearest site query와 adjacency 문제를 같은 그림으로 볼 수 있습니다.

## 8. 시간 복잡도와 구현 선택

| 접근 | 장점 | 단점 |
| --- | --- | --- |
| site별 half-plane intersection | 이해와 구현이 쉬움 | 전체 adjacency는 느림 |
| 3D lower hull | 전체 구조를 직접 얻음 | robust predicate가 어려움 |
| 라이브러리/문제 특화 | 안정적 | contest 환경 제약 |
| query only | 필요한 cell만 계산 | 전역 구조는 없음 |

대부분의 대회 문제는 full regular triangulation보다 작은 cell 계산, weighted nearest comparison, 또는 determinant predicate 일부만 요구합니다.

## 9. 자주 하는 실수

1. lifting 식에서 `-w`가 아니라 `+w`를 쓴다.
2. weight가 반지름인지 반지름 제곱인지 확인하지 않는다.
3. lower hull 대신 upper hull을 투영한다.
4. 일반 Delaunay의 incircle predicate를 weight 없이 그대로 쓴다.
5. empty cell을 입력 오류로 처리한다.

## 10. 대표 문제로 연결하기

### 문제에서 보이는 신호

- 입력 크기: weighted site 수가 작거나 geometry predicate 중심
- 필요한 복잡도: weighted Voronoi adjacency 또는 cell existence
- 이 레슨의 핵심 개념: lifting과 lower hull duality

### 풀이 흐름

1. weight의 의미를 `power = dist^2 - w` 형태로 정규화한다.
2. lifting z값을 계산해 어떤 site가 낮아지는지 손으로 확인한다.
3. 필요한 것이 cell 하나인지, 전체 adjacency인지 구분한다.
4. 전체 구조가 필요하면 lower hull orientation convention을 고정한다.
5. 작은 점 집합에서 Power Diagram half-plane 결과와 비교한다.

### 자주 틀리는 지점

- Power Diagram의 경계는 직선이지만, dual triangulation을 만들 때는 3D lower hull degeneracy가 같이 따라옵니다.
- 같은 lifted plane 위에 여러 점이 놓이면 triangulation이 유일하지 않을 수 있습니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: regular triangulation lifting `/practice/...` 문제 필요 | weighted point의 lifted z 계산 | `x^2+y^2-w` |
| 표준 | TODO: power adjacency `/practice/...` 문제 필요 | cell adjacency와 dual edge 연결 | power diagram |
| 응용 | TODO: weighted Delaunay `/practice/...` 문제 필요 | in-power-circle 판정 | lower hull |
| 함정 | TODO: empty weighted site `/practice/...` 문제 필요 | lower hull에서 사라지는 site 처리 | degeneracy |
