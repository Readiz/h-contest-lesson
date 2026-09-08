# Half-Plane Intersection

반평면들의 공통 영역을 구합니다. 각 제약을 `a*x+b*y<=c`로 쓰면 볼록 영역이 남습니다. Power cell이나 선형 제약의 가능한 위치를 계산할 때 사용합니다.

## 작은 입력: 볼록 영역 자르기

아래 구현은 주어진 반시계 볼록 다각형을 제약마다 자릅니다. 초기 영역이 사각형이고 제약이 N개면 최악 `O(N²)`, 메모리 `O(N)`입니다. 무한 영역 전체를 표현하는 구현이 아니므로 bounding box 자체가 문제의 제약이어야 합니다. 임의로 큰 상자를 넣어 무한 영역·공집합을 구분할 수는 없습니다.

```cpp compile-check
#include <vector>
using namespace std;
struct HpiPoint { long double x, y; };
struct HalfPlane { long double a, b, c; };
vector<HpiPoint> clipHalfPlanes(vector<HpiPoint> polygon, const vector<HalfPlane>& constraints) {
    for (auto h : constraints) {
        vector<HpiPoint> next;
        for (int i=0; i<(int)polygon.size(); ++i) {
            auto p=polygon[i], q=polygon[(i+1)%polygon.size()];
            long double fp=h.a*p.x+h.b*p.y-h.c;
            long double fq=h.a*q.x+h.b*q.y-h.c;
            bool pin=fp<=0, qin=fq<=0;
            if (pin) next.push_back(p);
            if (pin!=qin) {
                long double t=fp/(fp-fq);
                next.push_back({p.x+t*(q.x-p.x), p.y+t*(q.y-p.y)});
            }
        }
        polygon.swap(next);
        if (polygon.empty()) break;
    }
    return polygon;
}
```

유한한 실수 입력을 전제로 한 수치 구현입니다. 경계가 거의 일치하면 계산 오차가 결과의 차원을 바꿀 수 있습니다. 정확한 판정이 필요하면 유리수 또는 검증된 exact predicate를 사용합니다. `a=b=0`인 제약은 `c>=0`이면 전체, 아니면 공집합으로 위 식에서 처리됩니다.

## 큰 입력: 각도 정렬과 deque

반평면 경계를 방향별로 정렬하고, 새 경계 밖에 있는 deque 앞·뒤 교점을 제거하는 방법은 `O(N log N)`입니다. 같은 방향의 평행선은 더 강한 제약만 남기지만 반대 방향 평행선은 서로 다른 제약입니다. 교점 계산 전 평행 여부를 확인하고, 정렬 comparator에 EPS를 넣지 않습니다.

전체 알고리즘과 평행·무한 영역 처리는 [CP-Algorithms의 Half-plane intersection](https://cp-algorithms.com/geometry/halfplane-intersection.html)을 참고합니다. 위 clipping 구현의 복잡도와 구분합니다.

## 검산

`0<=x,y<=2` 상자에 `x+y<=2`를 적용하면 `(0,0),(2,0),(0,2)` 삼각형이 남습니다. 여기에 `x+y>=3`을 추가하면 공집합입니다. 같은 방향 중복 제약, 반대 방향 평행 제약, 한 점에서 접하는 경우를 함께 확인합니다.
