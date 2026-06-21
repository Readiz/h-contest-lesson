# 그래프와 트리 기본 성질

그래프는 정점과 간선으로 관계를 표현하는 자료구조입니다. 트리는 그래프 중에서도 **연결되어 있고 사이클이 없는** 특별한 형태입니다.

문제에서 그래프나 트리가 나오면 먼저 아래 질문을 확인합니다.

```text
정점과 간선 수가 얼마인가?
방향 그래프인가, 무방향 그래프인가?
간선에 가중치가 있는가?
그래프가 연결되어 있는가?
입력이 트리라고 보장되는가?
```

이 질문에 따라 DFS/BFS, Dijkstra, Union-Find, 최소 신장 트리, 트리 DP 같은 선택지가 갈립니다.

## 문서 구성

- [표현과 기본 탐색](pages/representation-and-traversal.md): 인접 리스트, DFS/BFS, 트리 기본 성질과 루트 기준 처리를 정리합니다.
- [트리 지름과 센트로이드](pages/tree-diameter-centroid.md): 트리에서 거리 기준 지름과 크기 기준 센트로이드를 분리해 이해합니다.
- [최소 신장 트리](pages/mst-kruskal-prim.md): Kruskal, Prim, 절단 성질, MST 실수와 연습 문제 TODO를 정리합니다.

## 학습 순서

처음에는 [표현과 기본 탐색](pages/representation-and-traversal.md)만으로도 BFS/DFS 문제를 시작할 수 있습니다. 입력이 트리라면 [트리 지름과 센트로이드](pages/tree-diameter-centroid.md)를 이어 보고, 모든 정점을 최소 비용으로 연결해야 한다면 [최소 신장 트리](pages/mst-kruskal-prim.md)로 넘어가세요.
