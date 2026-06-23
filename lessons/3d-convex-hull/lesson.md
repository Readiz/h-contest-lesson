# 3D Convex Hull

3D Convex Hull은 3차원 점 집합을 모두 포함하는 가장 작은 convex polyhedron의 face를 구하는 계산기하 심화 주제입니다. 2D Convex Hull처럼 정렬 한 번으로 끝나지 않고, face orientation, visible face 제거, horizon edge 구성, coplanar degeneracy 처리가 핵심입니다.

이 레슨은 기하 기본, Robust Geometry Predicates, Shape Distance Modeling 이후에 보는 3차원 기하 심화입니다.

1. oriented face가 어느 쪽을 바깥으로 보는지 유지한다.
2. 새 점에서 보이는 face를 제거하고 horizon edge로 새 face를 만든다.
3. coplanar, collinear, duplicate point를 별도 정책으로 처리한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 2D convex hull, cross product, signed volume, robust predicate
- 함께 보면 좋은 레슨: Robust Geometry Predicates, Voronoi/Delaunay, Power Diagram
- 다음에 볼 레슨: half-space intersection 3D, regular triangulation, polyhedron queries

## 1. 문제 신호

| 문제 표현 | 3D Convex Hull 관점 |
| --- | --- |
| 3차원 점들의 외피 면 개수 | convex polyhedron |
| 모든 점을 포함하는 최소 다면체 | hull faces |
| 어떤 점이 hull 밖에 있는지 판정 | visible face |
| Delaunay lifting이나 regular triangulation | lower hull |
| face normal과 면적 합이 필요 | oriented triangle faces |

3D hull은 구현량이 크고 degeneracy에 민감합니다. 입력 크기가 작거나 정확도가 낮아도 되는 문제인지 먼저 확인합니다.

## 2. Signed Volume

점 `a, b, c`가 만드는 oriented face에 대해 점 `p`가 어느 쪽에 있는지는 부호 있는 부피로 봅니다.

```text
volume6(a, b, c, p) = dot(cross(b-a, c-a), p-a)
```

부호가 양수이면 face normal 방향 쪽, 음수이면 반대쪽입니다. face 방향을 바깥쪽으로 맞춰 두면 `volume6 > 0`인 점에서 그 face가 보입니다.

## 3. Predicate 구현 조각

아래 코드는 3D hull 구현의 가장 작은 predicate 묶음입니다.

```cpp compile-check
#include <cmath>
using namespace std;

struct Point3D {
    double x = 0;
    double y = 0;
    double z = 0;
};

Point3D operator-(Point3D a, Point3D b) {
    return {a.x - b.x, a.y - b.y, a.z - b.z};
}

Point3D cross(Point3D a, Point3D b) {
    return {
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

double dot(Point3D a, Point3D b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

double signedVolume6(Point3D a, Point3D b, Point3D c, Point3D p) {
    return dot(cross(b - a, c - a), p - a);
}

bool visibleFrom(Point3D a, Point3D b, Point3D c, Point3D p) {
    const double eps = 1e-10;
    return signedVolume6(a, b, c, p) > eps;
}
```

정수 좌표가 크면 `long long` 곱셈이 넘칠 수 있습니다. 그 경우 `__int128` predicate 또는 exact arithmetic 정책을 따로 잡아야 합니다.

## 4. Incremental Hull 흐름

대표 구현은 사면체를 초기 hull로 만든 뒤 점을 하나씩 추가합니다.

```text
for each point p:
  visible faces = p에서 보이는 face
  if none: p is inside or on hull
  horizon edges = visible face와 invisible face의 경계
  remove visible faces
  add faces from horizon edge to p
```

horizon edge 방향을 잘못 잡으면 새 face normal이 안쪽을 보게 됩니다. face를 추가할 때 내부 기준점이나 기존 invisible face 방향으로 orientation을 맞춥니다.

## 5. 작은 예시

```text
초기 tetrahedron:
  A(0,0,0), B(1,0,0), C(0,1,0), D(0,0,1)

새 점 P(1,1,1)
P에서 보이는 face들을 제거하고,
보이는 영역의 boundary edge에 P를 붙여 새 삼각형 face를 만든다.
```

2D hull에서 바깥 점이 보이는 edge 구간을 대체하는 것과 비슷하지만, 3D에서는 보이는 face의 boundary가 cycle 여러 개처럼 보일 수 있어 edge counting이 더 중요합니다.

## 6. Coplanar 처리

| 상황 | 처리 선택 |
| --- | --- |
| coplanar point를 face 위 점으로 보존 | face polygon 병합 필요 |
| triangular face만 필요 | coplanar point는 hull vertex에서 제외 가능 |
| 모든 boundary point 필요 | face별 2D hull 재구성 |
| floating input | EPS 정책 일관성 필요 |

대부분의 contest 구현은 triangular face list를 반환합니다. 문제에서 "hull 위 점 개수"를 요구하면 coplanar boundary point도 세야 하므로 별도 처리가 필요합니다.

## 7. Lower Hull과 Lifting

2D Delaunay나 Power Diagram은 3D lifting으로 설명할 수 있습니다.

```text
(x, y) -> (x, y, x^2 + y^2)
lower convex hull projection -> Delaunay triangulation
```

따라서 3D hull predicate는 고급 Voronoi/Delaunay 구현의 기반이 됩니다. 다만 실제로 robust Delaunay를 만들려면 incircle predicate와 degeneracy 처리가 추가로 필요합니다.

## 8. 시간 복잡도 감각

| 접근 | 시간 |
| --- | ---: |
| incremental naive visible scan | `O(NF)` |
| random incremental expected | 보통 `O(N log N)` 계열 분석 가능 |
| 모든 face pair 검증 baseline | `O(N^4)` |
| output face 수 | 최악 `O(N^2)` |

입력이 수천 점 이하이고 random shuffle이 가능하면 incremental 구현이 실용적입니다. 큰 입력에서는 라이브러리나 더 정교한 구조가 필요합니다.

## 9. 자주 하는 실수

1. face normal 방향을 섞어 visible 판정이 뒤집힌다.
2. 초기 사면체 네 점이 coplanar인 경우를 처리하지 않는다.
3. horizon edge를 양방향으로 중복 저장해 새 face가 두 번 생긴다.
4. coplanar hull point를 내부 점처럼 버려야 하는지 세야 하는지 확인하지 않는다.
5. EPS를 너무 크게 잡아 얇은 tetrahedron을 평면으로 오판한다.
6. face count가 `O(N)`이라고 가정해 최악 입력에서 메모리가 터진다.

## 10. 문제를 볼 때 체크할 조건

- 입력이 일반 위치를 보장하는가?
- coplanar와 duplicate point가 들어올 수 있는가?
- 필요한 출력이 face 삼각형, hull vertex, 부피, 표면적 중 무엇인가?
- 좌표가 정수인지 실수인지 확인했는가?
- exact predicate가 필요한가?
- output size가 제한 안에 들어오는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: signed volume `/practice/...` 문제 필요 | face visibility 판정 | cross, dot |
| 표준 | TODO: tetrahedron hull `/practice/...` 문제 필요 | 초기 hull 구성 | orientation |
| 응용 | TODO: incremental 3D hull `/practice/...` 문제 필요 | visible face와 horizon | face graph |
| 함정 | TODO: coplanar hull points `/practice/...` 문제 필요 | degeneracy 정책 | EPS, boundary |
