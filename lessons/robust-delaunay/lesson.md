# Robust Delaunay

Robust Delaunay는 Delaunay triangulation을 구현하거나 검증할 때 orientation, incircle, degeneracy 처리를 안정화하는 레슨입니다. Voronoi-Delaunay의 개념을 알아도 실제 좌표 문제에서는 거의 같은 점, 같은 원 위 점, collinear case가 답을 흔듭니다.

이 레슨은 Voronoi-Delaunay와 Robust Geometry Predicates 이후에 보는 계산기하 심화입니다.

1. predicate와 construction을 분리한다.
2. Delaunay 조건은 incircle predicate로 검증한다.
3. degeneracy가 있는 입력에서 tie policy를 먼저 정한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Voronoi-Delaunay, Robust Geometry Predicates, Circle Geometry
- 함께 보면 좋은 레슨: Inversion Geometry, Circle Arrangement, Shape Distance Modeling
- 다음에 볼 레슨: power diagram, Euclidean MST, randomized incremental triangulation

## 1. 문제 신호

| 문제 표현 | Robust Delaunay 관점 |
| --- | --- |
| 가장 가까운 이웃, 빈 원 조건 | Delaunay edge candidate |
| Euclidean MST 후보 간선 줄이기 | Delaunay graph superset |
| 원 안에 다른 점이 없어야 함 | incircle predicate |
| 점이 같은 원 위에 많음 | degeneracy tie policy |
| double 오차로 edge flip이 불안정 | exact or filtered predicate |

Delaunay 자체를 구현하지 않아도, "Delaunay edge일 수 있는가"를 판정하는 문제에서 predicate 안정성이 필요합니다.

## 2. Orientation과 Incircle

Delaunay edge flip의 핵심은 네 점 `a, b, c, d`에서 `d`가 triangle `abc`의 circumcircle 안에 있는지 판정하는 것입니다.

```text
orient(a,b,c) > 0인 CCW triangle에 대해
incircle(a,b,c,d) > 0이면 d가 circumcircle 내부
```

orientation 부호가 바뀌면 incircle 부호 convention도 바뀝니다. 따라서 incircle을 호출하기 전에 triangle 방향을 통일하는 편이 안전합니다.

## 3. Exact Integer Predicate

좌표가 정수이고 범위가 작다면 `__int128` determinant로 predicate를 안정화할 수 있습니다.

```cpp compile-check
#include <cstdint>
using namespace std;

struct Point {
    long long x = 0;
    long long y = 0;
};

__int128 cross(Point a, Point b, Point c) {
    __int128 x1 = b.x - a.x;
    __int128 y1 = b.y - a.y;
    __int128 x2 = c.x - a.x;
    __int128 y2 = c.y - a.y;
    return x1 * y2 - y1 * x2;
}

int sign128(__int128 value) {
    if (value < 0) return -1;
    if (value > 0) return 1;
    return 0;
}

int orientation(Point a, Point b, Point c) {
    return sign128(cross(a, b, c));
}
```

incircle determinant는 좌표 제곱이 들어가므로 overflow 여유를 더 크게 잡아야 합니다. 좌표가 `1e9`급이면 `__int128`로도 중간식 설계를 조심해야 합니다.

## 4. Edge Flip 조건

두 triangle `abc`, `abd`가 edge `ab`를 공유한다고 합시다.

```text
if d is inside circumcircle(a,b,c):
  flip edge ab to cd
```

단, `a,b,c`의 방향이 CCW라는 전제가 있습니다. collinear triangle이면 circumcircle이 정의되지 않으므로 입력 전처리나 tie policy가 필요합니다.

## 5. 작은 예시

```text
a=(0,0), b=(2,0), c=(0,2)
circumcircle center=(1,1), radius^2=2
d=(1,1)
```

`d`는 원 내부이므로 edge flip 후보입니다. 반면 `d=(2,2)`는 같은 원 위에 있습니다. 이때 flip을 할지 말지는 Delaunay가 unique하지 않은 degeneracy case라서, 구현 전체에서 일관된 tie policy를 써야 합니다.

## 6. Degeneracy 처리

| 상황 | 권장 정책 |
| --- | --- |
| duplicate point | 입력에서 제거하거나 index list로 병합 |
| collinear all points | triangulation 대신 sorted edge chain |
| four cocircular points | index tie로 diagonal 선택 |
| nearly cocircular double input | EPS 대신 filtered exact predicate 검토 |
| zero-area triangle | incircle 호출 금지 |

문제 statement가 "no three collinear, no four cocircular"를 보장하면 구현은 훨씬 단순해집니다. 보장이 없으면 tie policy를 답의 일부로 봐야 합니다.

## 7. Predicate와 Construction 분리

좌표를 실제로 계산하는 construction은 double을 쓸 수 있습니다. 하지만 분기 조건(predicate)은 exact 또는 filtered 방식으로 두는 편이 안전합니다.

```text
predicate: orientation, incircle, on-circle
construction: circumcenter coordinate, edge length, angle
```

분기가 한번 틀리면 triangulation topology가 바뀌므로, construction 오차보다 predicate 오차가 더 위험합니다.

## 8. 구현 선택

| 알고리즘 | 특징 |
| --- | --- |
| Bowyer-Watson | 개념이 단순하지만 cavity boundary 처리 필요 |
| Divide and Conquer | 빠르지만 merge 구현 난도 높음 |
| Incremental edge flip | locally Delaunay 검증이 직관적 |
| Library use | 실전 서비스/연구에서는 가장 안전 |

대회에서 직접 Delaunay를 짜야 한다면 입력 제약이 강한지 먼저 확인합니다. 제약이 약하면 문제 의도가 다른 변환일 가능성도 큽니다.

## 9. 자주 하는 실수

1. triangle 방향을 통일하지 않고 incircle 부호를 해석한다.
2. cocircular case에서 flip을 계속 반복한다.
3. duplicate point를 남겨 zero-area triangle을 만든다.
4. EPS로 predicate와 construction을 동시에 처리한다.
5. super triangle의 가짜 vertex가 최종 edge에 남는다.
6. Delaunay graph가 MST의 superset이라는 성질만 필요할 때 전체 triangulation을 구현한다.

## 10. 문제를 볼 때 체크할 조건

- 입력이 general position을 보장하는가?
- 좌표 범위상 exact integer predicate가 가능한가?
- 필요한 것이 triangulation 전체인가, candidate edge 집합인가?
- cocircular tie를 어떻게 고정할 것인가?
- predicate와 construction을 분리했는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: incircle predicate `/practice/...` 문제 필요 | orientation convention과 incircle 부호 확인 | determinant |
| 표준 | TODO: Delaunay edge flip `/practice/...` 문제 필요 | local Delaunay 조건 검증 | edge flip |
| 응용 | TODO: Euclidean MST candidate `/practice/...` 문제 필요 | Delaunay graph 성질 활용 | empty circle |
| 함정 | TODO: cocircular degeneracy `/practice/...` 문제 필요 | tie policy 고정 | degeneracy |
