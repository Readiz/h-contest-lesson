# Geometry Robustness and Duality Practice Set

이 페이지는 robust predicate와 weighted Voronoi duality를 작은 입력에서 끝까지 따라가기 위한 연습을 모읍니다. 실제 h-contest 문제가 아직 없는 칸은 임의 ID 대신 `TODO`로 둡니다.

## 로컬 완결형 연습

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
| 입문 | TODO: exact ccw `/practice/...` 문제 필요 | 정수 좌표 orientation과 선분 교차 | robust predicate |
| 표준 | TODO: power diagram cell `/practice/...` 문제 필요 | power distance 비교와 half-plane | weighted Voronoi |
| 응용 | TODO: Delaunay predicate `/practice/...` 문제 필요 | incircle 부호와 tie 처리 | cocircular |
| 심화 | TODO: 3D lower hull `/practice/...` 문제 필요 | lifting과 lower face projection | regular triangulation |
| 함정 | TODO: empty power cell `/practice/...` 문제 필요 | cell이 사라지는 경우 처리 | degeneracy |
