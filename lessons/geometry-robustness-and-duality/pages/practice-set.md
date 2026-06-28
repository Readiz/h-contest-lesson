# Geometry Robustness and Duality Practice Set

이 페이지는 robust predicate와 weighted Voronoi duality를 작은 입력에서 끝까지 따라가기 위한 연습을 모읍니다. 실제 h-contest 문제가 아직 없는 칸은 임의 ID 대신 `TODO`로 두고, 로컬 완결형 연습과 검증 기준을 먼저 둡니다.

## 로컬 완결형 연습

### Exact Segment Intersection

정수 좌표 선분 두 개가 교차하는지 판정합니다. 교점 좌표를 만들지 말고, orientation sign과 bounding box만으로 답합니다.

#### 입력

```text
Q
ax ay bx by cx cy dx dy
...
```

- `1 <= Q <= 200000`
- 각 좌표의 절댓값은 `10^18` 이하입니다.
- 각 줄은 선분 `AB`와 `CD`를 의미합니다.

#### 출력

각 query마다 교차하면 `YES`, 아니면 `NO`를 출력합니다. 끝점에서 접하거나 collinear overlap인 경우도 교차입니다.

#### 예시

```text
3
0 0 4 4 0 4 4 0
0 0 1 0 2 0 3 0
0 0 4 0 2 0 6 0
```

```text
YES
NO
YES
```

#### 손으로 따라가는 Trace

첫 번째 query는 `A=(0,0)`, `B=(4,4)`, `C=(0,4)`, `D=(4,0)`입니다.

| predicate | cross sign | 의미 |
| --- | ---: | --- |
| `orient(A,B,C)` | `+16` | `C`는 `AB`의 왼쪽 |
| `orient(A,B,D)` | `-16` | `D`는 `AB`의 오른쪽 |
| `orient(C,D,A)` | `-16` | `A`는 `CD`의 오른쪽 |
| `orient(C,D,B)` | `+16` | `B`는 `CD`의 왼쪽 |

두 선분이 서로의 양쪽에 끝점을 하나씩 가지므로 교차합니다. 세 번째 query처럼 모든 점이 collinear이면 orientation만으로 끝내지 말고 bounding box overlap을 확인해야 합니다.

#### 구현 기준

```cpp compile-check
#include <algorithm>
#include <iostream>
using namespace std;

struct Point {
    long long x = 0;
    long long y = 0;
};

int sign(__int128 value) {
    if (value < 0) {
        return -1;
    }
    if (value > 0) {
        return 1;
    }
    return 0;
}

int orientation(Point a, Point b, Point c) {
    __int128 x1 = (__int128)b.x - a.x;
    __int128 y1 = (__int128)b.y - a.y;
    __int128 x2 = (__int128)c.x - a.x;
    __int128 y2 = (__int128)c.y - a.y;
    return sign(x1 * y2 - y1 * x2);
}

bool between(long long left, long long right, long long value) {
    if (left > right) {
        swap(left, right);
    }
    return left <= value && value <= right;
}

bool onSegment(Point a, Point b, Point p) {
    return orientation(a, b, p) == 0
        && between(a.x, b.x, p.x)
        && between(a.y, b.y, p.y);
}

bool intersects(Point a, Point b, Point c, Point d) {
    int abC = orientation(a, b, c);
    int abD = orientation(a, b, d);
    int cdA = orientation(c, d, a);
    int cdB = orientation(c, d, b);

    if (abC == 0 && onSegment(a, b, c)) {
        return true;
    }
    if (abD == 0 && onSegment(a, b, d)) {
        return true;
    }
    if (cdA == 0 && onSegment(c, d, a)) {
        return true;
    }
    if (cdB == 0 && onSegment(c, d, b)) {
        return true;
    }
    return abC * abD < 0 && cdA * cdB < 0;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int queries;
    cin >> queries;
    while (queries-- > 0) {
        Point a, b, c, d;
        cin >> a.x >> a.y >> b.x >> b.y >> c.x >> c.y >> d.x >> d.y;
        cout << (intersects(a, b, c, d) ? "YES" : "NO") << '\n';
    }
}
```

#### Stress 기준

1. 좌표가 작은 격자 `[-5,5]`에서는 모든 선분 쌍을 열거해 endpoint permutation에 대해 결과가 같은지 확인합니다.
2. `AB`와 `BA`, `CD`와 `DC`를 바꿔도 결과가 같아야 합니다.
3. collinear disjoint, collinear overlap, endpoint touch, duplicate point segment를 deterministic case로 둡니다.
4. 좌표 범위를 키울 때는 cross product가 `__int128` 범위 안인지 계산합니다.

### Weighted Boundary Trace

두 weighted site `A=(0,0,w=0)`, `B=(4,0,w=12)`의 power boundary를 전개합니다.

```text
|x-A|^2 - 0 = |x-B|^2 - 12
=> x = 0.5
```

가중치가 없을 때의 경계 `x=2`와 비교하고, weight가 커질수록 어느 site의 cell이 넓어지는지 설명합니다.

### Empty Cell Example

세 weighted site를 만들어 한 site의 power cell이 비도록 합니다. 답안에는 각 boundary half-plane과, 왜 교집합이 비는지 쓰면 됩니다. full diagram 구현은 필요 없습니다.

## h-contest 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | 로컬: exact segment intersection | 정수 좌표 orientation과 선분 교차 | robust predicate |
| 표준 | TODO: power diagram cell `/practice/...` 문제 필요 | power distance 비교와 half-plane | weighted Voronoi |
| 응용 | TODO: Delaunay predicate `/practice/...` 문제 필요 | incircle 부호와 tie 처리 | cocircular |
| 심화 | TODO: 3D lower hull `/practice/...` 문제 필요 | lifting과 lower face projection | regular triangulation |
| 함정 | TODO: empty power cell `/practice/...` 문제 필요 | cell이 사라지는 경우 처리 | degeneracy |
