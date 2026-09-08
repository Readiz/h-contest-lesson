# Robust Delaunay

Robust Delaunay는 Delaunay triangulation을 구현하거나 검증할 때 orientation, incircle, degeneracy 처리를 안정화하는 레슨입니다. Voronoi-Delaunay의 개념을 알아도 실제 좌표 문제에서는 거의 같은 점, 같은 원 위 점, collinear case가 답을 흔듭니다.


네 점의 incircle 판정만으로 전역 Delaunay 간선 여부를 확정하지 않습니다. 삼각분할의 인접·볼록성 조건과 다른 점들의 빈 원 조건이 함께 필요합니다.

## 문제 신호

| 문제 표현 | Robust Delaunay 관점 |
| --- | --- |
| 가장 가까운 이웃, 빈 원 조건 | Delaunay edge candidate |
| Euclidean MST 후보 간선 줄이기 | Delaunay graph superset |
| 원 안에 다른 점이 없어야 함 | incircle predicate |
| 점이 같은 원 위에 많음 | degeneracy tie policy |
| double 오차로 edge flip이 불안정 | exact or filtered predicate |

Delaunay 자체를 구현하지 않아도, "Delaunay edge일 수 있는가"를 판정하는 문제에서 predicate 안정성이 필요합니다.

## Orientation과 Incircle

Delaunay edge flip의 핵심은 네 점 `a, b, c, d`에서 `d`가 triangle `abc`의 circumcircle 안에 있는지 판정하는 것입니다.

```text
orient(a,b,c) > 0인 CCW triangle에 대해
incircle(a,b,c,d) > 0이면 d가 circumcircle 내부
```

orientation 부호가 바뀌면 incircle 부호 convention도 바뀝니다. 따라서 incircle을 호출하기 전에 triangle 방향을 통일하는 편이 안전합니다.

## Exact Integer Predicate

좌표가 정수이고 범위가 작다면 `__int128` determinant로 predicate를 안정화할 수 있습니다.

orientation은 [Robust Geometry Predicates](https://h.readiz.com/learn/geometry-robustness-and-duality/robust-geometry-predicates)의 정수 구현을 사용합니다. incircle은 4차식이므로 좌표 범위에 따라 128비트보다 큰 정확 연산이 필요할 수 있습니다.

incircle determinant는 좌표 제곱이 들어가므로 overflow 여유를 더 크게 잡아야 합니다. 좌표가 `1e9`급이면 `__int128`로도 중간식 설계를 조심해야 합니다.

## Edge Flip 조건

두 triangle `abc`, `abd`가 edge `ab`를 공유한다고 합시다.

```text
if d is inside circumcircle(a,b,c):
  flip edge ab to cd
```

단, `a,b,c`의 방향이 CCW라는 전제가 있습니다. collinear triangle이면 circumcircle이 정의되지 않으므로 입력 전처리나 tie policy가 필요합니다.

## 작은 예시

공유 대각선 a=(0,0), b=(2,0)에 대해 c=(0,2), d=(1,-0.1)은 반대쪽에 있고 사각형을 이룹니다. d는 abc의 외접원 내부이므로 ab를 cd로 바꾸는 flip 후보입니다. d=(1,1-sqrt(2))이면 같은 원 위의 경우가 되어 tie 규칙을 정해야 합니다. 실제 flip은 인접한 두 삼각형이 볼록 사각형을 이루는지까지 확인합니다.

## Degeneracy 처리

| 상황 | 권장 정책 |
| --- | --- |
| duplicate point | 입력에서 제거하거나 index list로 병합 |
| collinear all points | triangulation 대신 sorted edge chain |
| four cocircular points | index tie로 diagonal 선택 |
| nearly cocircular double input | EPS 대신 filtered exact predicate 검토 |
| zero-area triangle | incircle 호출 금지 |

문제 statement가 "no three collinear, no four cocircular"를 보장하면 구현은 훨씬 단순해집니다. 보장이 없으면 tie policy를 답의 일부로 봐야 합니다.

## Predicate와 Construction 분리

좌표를 실제로 계산하는 construction은 double을 쓸 수 있습니다. 하지만 분기 조건(predicate)은 exact 또는 filtered 방식으로 두는 편이 안전합니다.

```text
predicate: orientation, incircle, on-circle
construction: circumcenter coordinate, edge length, angle
```

분기가 한번 틀리면 triangulation topology가 바뀌므로, construction 오차보다 predicate 오차가 더 위험합니다.

## 구현 선택

| 알고리즘 | 특징 |
| --- | --- |
| Bowyer-Watson | 개념이 단순하지만 cavity boundary 처리 필요 |
| Divide and Conquer | 빠르지만 merge 구현 난도 높음 |
| Incremental edge flip | locally Delaunay 검증이 직관적 |
| Library use | 실전 서비스/연구에서는 가장 안전 |

대회에서 직접 Delaunay를 짜야 한다면 입력 제약이 강한지 먼저 확인합니다. 제약이 약하면 문제 의도가 다른 변환일 가능성도 큽니다.
