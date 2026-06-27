# Dynamic Network Optimization Practice Set

이 페이지는 Dynamic Flow와 Dynamic MST를 완전한 online 자료구조부터 시작하지 않고, 제한된 update 모델로 낮추는 연습을 모읍니다. 아직 적절한 h-contest 문제가 없는 칸은 임의 ID를 넣지 않고 `TODO`로 둡니다.

## 로컬 완결형 연습

### Residual Reuse Trace

정점 `S, A, T`와 간선 `S -> A`, `A -> T`, `S -> T`가 있는 작은 네트워크를 잡습니다.

1. 초기 max flow를 손으로 구합니다.
2. `S -> A` capacity를 1 늘립니다.
3. 기존 residual graph에서 추가 augmenting path가 있는지 찾습니다.
4. 같은 간선 capacity를 줄였을 때 기존 flow가 feasible하지 않을 수 있음을 확인합니다.

출력해야 할 것은 code가 아니라 residual edge의 capacity 표입니다.

### MST Replacement Counterexample

네 정점 cycle에 diagonal 하나를 추가한 그래프를 만듭니다. MST에 들어간 edge를 삭제하면 어떤 non-tree edge가 replacement가 되는지 직접 찾고, MST 밖 edge를 삭제하면 답이 변하지 않는다는 것도 같이 확인합니다.

## h-contest 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: incremental flow `/practice/...` 문제 필요 | capacity 증가만 있는 residual 재사용 | feasible old flow |
| 표준 | TODO: time-expanded flow `/practice/...` 문제 필요 | 시간별 edge를 정적 network로 펼치기 | wait edge |
| 표준 | TODO: dynamic MST rebuild `/practice/...` 문제 필요 | 활성 간선 Kruskal baseline | active set |
| 응용 | TODO: MST block rebuild `/practice/...` 문제 필요 | 변경 edge 후보만 합치기 | sqrt decomposition |
| 함정 | TODO: flow decrease counterexample `/practice/...` 문제 필요 | 용량 감소에서 repair 필요성 확인 | infeasible flow |
