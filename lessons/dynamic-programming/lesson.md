# 동적 계획법

상태가 같으면 남은 선택도 같은지 먼저 따져 봅니다. 이를 만족해야 여러 경로로 도달한 상태를 하나로 합치고, 최소 비용이나 경우의 수를 재사용할 수 있습니다.

- [상태와 전이](pages/state-and-transition.md): 격자 경로, 최소 동전 개수, 트리의 정점 선택에서 상태와 계산 순서를 잡습니다.
- [배낭과 LIS](pages/knapsack-and-lis.md): 같은 물건의 중복 사용을 막는 반복 방향과, 증가 부분수열의 끝값만 남기는 방법을 다룹니다.

방문한 집합까지 상태에 필요하다면 [TSP의 비트마스크 DP](https://h.readiz.com/learn/tsp-hamiltonian/search-and-dp)로 이어집니다.
