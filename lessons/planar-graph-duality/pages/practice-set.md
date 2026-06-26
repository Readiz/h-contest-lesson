# Practice Set

Planar Graph Duality 허브의 연습은 face traversal, dual graph 구성, cut-cycle 변환을 순서대로 확인하는 흐름이 좋습니다. 실제 h-contest 문제가 아직 부족한 주제는 임의 ID를 만들지 않고 `TODO`로 남깁니다.

## 1. 연습 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: planar dual construction `/practice/...` 문제 필요 | face adjacency로 dual 만들기 | outer face |
| 표준 | TODO: half-edge face traversal `/practice/...` 문제 필요 | 좌표에서 face 번호 찾기 | angle sort |
| 응용 | TODO: planar cut shortest path `/practice/...` 문제 필요 | cut을 dual path로 변환 | cut-cycle duality |
| 함정 | TODO: bridge in dual graph `/practice/...` 문제 필요 | self-loop와 bridge 처리 | Euler formula |

## 2. 로컬 완결형 연습 후보

### Square with a Diagonal

정점 네 개로 사각형을 만들고 대각선 하나를 추가합니다. half-edge traversal로 outer face와 두 내부 삼각형 face를 찾은 뒤, 대각선 edge의 양쪽 face가 서로 다른지 확인합니다.

### Tree as a Planar Graph

간선이 모두 bridge인 tree를 입력으로 넣고 face traversal 결과를 확인합니다. 이 경우 dual graph에 self-loop가 생기거나 모든 edge가 같은 face 양쪽을 가질 수 있음을 관찰합니다.

### Boundary Cut to Dual Path

작은 격자 그래프에서 위쪽 boundary와 아래쪽 boundary를 분리하는 최소 edge cut을 만들고, dual graph에서 좌우 또는 boundary arc 사이 shortest path와 비용이 같은지 비교합니다.

## 3. 제출 전 체크리스트

- `V - E + F = 1 + C`를 출력해 확인했는가?
- outer face 번호를 signed area로 찾았는가?
- dual graph가 multi-edge와 self-loop를 허용하는가?
- directed 문제를 무향 dual shortest path로 바꾸지 않았는가?
- 작은 그림에서 primal edge id와 dual edge id가 같은 비용으로 대응하는가?
