# Regular Triangulation

Regular Triangulation은 weighted point를 3차원으로 lifting한 뒤 lower hull을 투영해서 얻는 Power Diagram의 dual 구조입니다. 일반 Delaunay Triangulation이 Voronoi Diagram의 dual이라면, Regular Triangulation은 Power Diagram의 dual입니다.


일반 위치가 아니면 lower hull의 투영은 삼각형보다 큰 cell을 가진 regular subdivision일 수 있습니다. 이를 일관되게 삼각분할하는 tie 정책이 필요합니다. cell의 내부가 비는 퇴화 상태와 완전히 빈 cell도 구분합니다.

## 문제 신호

| 문제 표현 | Regular Triangulation 관점 |
| --- | --- |
| weighted Voronoi의 dual이 필요하다 | regular triangulation |
| 원 반지름이나 site weight가 있다 | power distance |
| weighted nearest neighbor adjacency를 묻는다 | power cell adjacency |
| Delaunay 조건에 weight가 붙는다 | in-power-circle predicate |
| lifting과 lower hull이 힌트로 나온다 | 3D convex hull projection |

대회에서 전체 Regular Triangulation을 직접 구현하는 경우는 드뭅니다. 하지만 Power Diagram의 이웃 관계, weighted empty circle 판정, weighted Delaunay 성질을 이해하는 데 중요합니다.

## Lifting 변환

2차원 weighted point `(x, y, w)`를 3차원 점으로 올립니다.

```text
lift(x, y, w) = (x, y, x^2 + y^2 - w)
```

weight가 클수록 lifted z값은 낮아집니다. z값이 낮아진 point는 lower hull에 더 잘 나타나고, Power Diagram에서 더 큰 cell을 가질 가능성이 커집니다.

## Power Diagram과의 관계

Power distance는 아래 식입니다.

```text
power_i(q) = |q - p_i|^2 - w_i
```

여기서 `|q|^2` 항은 모든 site에 공통입니다. 따라서 어떤 site가 최소 power를 가지는지는 lifted plane들의 lower envelope로 볼 수 있습니다.

```text
power_i(q) = |q|^2 - 2 p_i dot q + |p_i|^2 - w_i
```

`|p_i|^2 - w_i`가 lifted z값입니다. 즉 Power Diagram의 cell 경계는 lifted geometry의 lower envelope와 맞물립니다.

## 작은 예시

세 점이 있습니다.

```text
A = (0, 0), w = 0  -> z = 0
B = (2, 0), w = 0  -> z = 4
C = (1, 1), w = 3  -> z = -1
```

가중치가 없다면 `C`의 lifted z는 2입니다. 하지만 weight 3 때문에 z가 -1까지 내려갑니다. 그래서 `C`는 Power Diagram에서 더 넓은 영역을 차지하고, 이 세 비공선 점만으로는 삼각형 연결 구조가 바뀌지 않습니다. 더 많은 점에서는 lower hull 참여 여부와 연결 구조가 달라질 수 있습니다.

## In-Power-Circle 관점

일반 Delaunay에서 한 점이 triangle의 circumcircle 안에 있는지 검사합니다. Regular Triangulation에서는 weight가 들어간 power circle 조건을 봅니다.

```text
point q is inside weighted circle of triangle abc
<=> power value of q is smaller than the supporting power circle
```

구현은 4x4 determinant나 lifted orientation으로 표현할 수 있습니다. 하지만 부호 convention, 좌표 범위, cocircular degeneracy가 까다롭습니다.

## Cell이 사라지는 경우

Power Diagram에서는 어떤 weighted site의 cell이 비어 있을 수 있습니다. Regular Triangulation에서는 그런 site가 lower hull에 나타나지 않는 점으로 해석됩니다.

| 현상 | Power Diagram | Regular Triangulation |
| --- | --- | --- |
| site가 지배 영역을 가짐 | non-empty cell | lower hull에 참여 |
| site가 완전히 덮임 | empty cell | lower hull에서 사라짐 |
| 두 cell이 변을 공유 | neighboring cells | triangulation edge |
| 세 cell이 만남 | power vertex | triangulation face |

위 표는 퇴화가 없는 일반 위치의 대응입니다. 셀이 선이나 점으로 퇴화하거나 여러 셀이 한 점에서 만나면 subdivision과 삼각분할 tie 정책을 함께 봅니다.

이 대응을 알면 weighted nearest site query와 adjacency 문제를 같은 그림으로 볼 수 있습니다.

## 시간 복잡도와 구현 선택

| 접근 | 장점 | 단점 |
| --- | --- | --- |
| site별 half-plane intersection | 이해와 구현이 쉬움 | 전체 adjacency는 느림 |
| 3D lower hull | 전체 구조를 직접 얻음 | robust predicate가 어려움 |
| 라이브러리/문제 특화 | 안정적 | contest 환경 제약 |
| query only | 필요한 cell만 계산 | 전역 구조는 없음 |

대부분의 대회 문제는 full regular triangulation보다 작은 cell 계산, weighted nearest comparison, 또는 determinant predicate 일부만 요구합니다.
