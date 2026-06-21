# 동적 계획법

동적 계획법(Dynamic Programming, DP)은 큰 문제를 작은 부분문제로 나누고, 이미 계산한 결과를 다시 쓰는 풀이 방법입니다. 한국어로는 보통 **동적 계획법** 또는 그냥 **DP**라고 부릅니다.

DP가 잘 맞는 문제에는 두 가지 성질이 있습니다.

- **부분문제가 겹친다.** 같은 계산이 여러 경로에서 반복해서 등장합니다.
- **최적 부분 구조가 있다.** 큰 답을 작은 답들의 조합으로 만들 수 있습니다.

DP의 어려운 점은 공식을 외우는 것이 아니라 `무엇을 상태로 둘지`, `어떤 순서로 채울지`, `이전 상태에서 현재 상태로 어떻게 넘어올지`를 정하는 것입니다. 이 문서는 기초 형태부터 다양한 실전 기법까지 한 번에 연결합니다.

## 문서 구성

- [상태와 전이](pages/state-and-transition.md): DP 상태, 초기값, 전이, 순서와 top-down/bottom-up 기본기를 정리합니다.
- [배낭과 LIS](pages/knapsack-and-lis.md): 0/1 배낭, 무한 배낭, LIS의 대표 전이와 반복 방향을 다룹니다.
- [구간, 트리, 비트마스크 DP](pages/interval-tree-bitmask.md): 구간 DP, 트리 DP, 비트마스크 DP처럼 상태 구조가 달라지는 유형을 묶어 봅니다.
- [Digit DP와 최적화 감각](pages/digit-dp-and-optimization.md): Digit DP, rolling array, DP 최적화 질문, 실수 점검과 문제 신호를 정리합니다.
- [연습 문제](pages/practice-set.md): DP 유형별 연습 순서와 아직 필요한 h-contest 문제 TODO를 관리합니다.

## 학습 순서

처음에는 [상태와 전이](pages/state-and-transition.md)만 읽고 간단한 1차원/2차원 DP를 구현합니다. 그다음 [배낭과 LIS](pages/knapsack-and-lis.md), [구간, 트리, 비트마스크 DP](pages/interval-tree-bitmask.md), [Digit DP와 최적화 감각](pages/digit-dp-and-optimization.md) 순서로 확장하세요. 실제 문제 연결은 [연습 문제](pages/practice-set.md)에 모아 둡니다.
