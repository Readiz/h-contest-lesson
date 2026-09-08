# Geometry Robustness and Duality Practice Set

이 페이지는 robust predicate와 weighted Voronoi duality를 작은 입력에서 끝까지 따라가기 위한 연습을 모읍니다.


입출력 코드는 [Robust Geometry Predicates](https://h.readiz.com/learn/geometry-robustness-and-duality/robust-geometry-predicates)의 공통 predicate 정의 뒤에 붙입니다.

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

```cpp
#include <iostream>

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int queries;
    cin >> queries;
    while (queries-- > 0) {
        RobustPoint a, b, c, d;
        cin >> a.x >> a.y >> b.x >> b.y >> c.x >> c.y >> d.x >> d.y;
        cout << (segmentsIntersect(a, b, c, d) ? "YES" : "NO") << '\n';
    }
}
```

#### Stress 기준

1. 좌표가 작은 격자 `[-5,5]`에서는 모든 선분 쌍을 열거해 endpoint permutation에 대해 결과가 같은지 확인합니다.
2. `AB`와 `BA`, `CD`와 `DC`를 바꿔도 결과가 같아야 합니다.
3. collinear disjoint, collinear overlap, endpoint touch, duplicate point segment를 deterministic case로 둡니다.
4. 좌표 범위를 키울 때는 cross product가 `__int128` 범위 안인지 계산합니다.

### Power Cell 경계와 빈 Cell

[Power Diagram](https://h.readiz.com/learn/geometry-robustness-and-duality/power-diagram)의 power 부등식을 사용합니다. A=(0,0,w=0), B=(4,0,w=12)의 경계는 x=0.5입니다. 여기에 C=(-4,0,w=20)를 추가하면 A가 C보다 가까운 영역은 x>=0.5가 되어 A의 cell은 선으로 퇴화합니다. C의 w를 24로 바꾸면 x>=1과 x<=0.5를 동시에 만족해야 하므로 A의 cell은 비어 있습니다.
