# Cut-Cycle Duality

연결된 무향 평면 그래프의 embedding을 고정합니다. 각 primal edge와 dual edge는 일대일 대응하고 용량을 dual 길이로 옮깁니다.

## 정확한 대응

단순 primal cycle은 dual의 inclusion-minimal nonempty cut인 bond와 대응합니다. 반대로 primal bond는 dual의 단순 cycle과 대응합니다. 일반 cut의 dual 간선 집합은 하나의 단순 cycle이 아니라 여러 cycle로 분해되는 Eulerian 부분그래프일 수 있습니다. Bridge는 dual self-loop입니다.

## 같은 face에 있는 s,t

서로 다른 s,t가 같은 face 경계에 있으면 그 face 안에 가상 edge st를 그립니다. 가상 edge가 나누는 두 face를 dual의 시작·끝으로 둡니다. 가상 edge에 대응하는 dual edge를 제외한 최단 경로를 구하면 원래 s-t 최소 cut 비용을 얻습니다.

이 구성은 outer face를 단순히 하나의 dual 정점으로 둔 채 아무 내부 face 두 개를 고르는 것과 다릅니다. 경계가 반복 정점을 포함하면 가상 edge를 붙일 정확한 corner도 정해야 합니다. 설명이 쉬운 기본형은 단순 face 경계 위의 s,t입니다.

## 풀이 순서

1. 입력 embedding 또는 half-edge 순회로 face와 간선 대응을 구합니다.
2. 공통 face에 가상 st edge를 추가하여 face를 둘로 나눕니다.
3. 가상 edge를 제외한 dual에서 두 새 face 사이 최단 경로를 찾습니다.
4. 경로의 primal edge ID 집합이 s,t를 실제로 분리하고 비용이 같은지 작은 전수 cut과 비교합니다.

비음수 용량이면 Dijkstra를 사용합니다. 방향 그래프는 dual 방향·용량 모델을 별도로 증명해야 하며 여기의 무향 변환을 그대로 쓰지 않습니다. s,t가 공통 face에 없으면 이 간단한 단일 경로 변환의 전제 밖입니다.

## 복잡도

정수 각도 정렬은 O(E log E), face 순회·dual 구성은 O(E), 최단 경로는 O((E+F)log(F+1))입니다. face 정보를 직접 받으면 기하 전처리는 생략됩니다.
