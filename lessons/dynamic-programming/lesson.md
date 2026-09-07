# 동적 계획법

동적 계획법(Dynamic Programming, DP)은 큰 문제를 작은 부분문제로 나누고, 이미 계산한 결과를 다시 쓰는 풀이 방법입니다.

DP가 잘 맞는 문제에는 두 가지 성질이 있습니다.

- **부분문제가 겹친다.** 같은 계산이 여러 경로에서 반복해서 등장합니다.
- **최적 부분 구조가 있다.** 큰 답을 작은 답들의 조합으로 만들 수 있습니다.

## 문서 구성

- [상태와 전이](pages/state-and-transition.md): DP 상태, 초기값, 전이, 순서와 top-down/bottom-up 기본기를 정리합니다.
- [배낭과 LIS](pages/knapsack-and-lis.md): 0/1 배낭, 무한 배낭, LIS의 대표 전이와 반복 방향을 다룹니다.
- [구간, 트리, 비트마스크 DP](pages/interval-tree-bitmask.md): 구간 DP, 트리 DP, 비트마스크 DP처럼 상태 구조가 달라지는 유형을 묶어 봅니다.
- [Digit DP와 메모리 절약](pages/digit-dp-and-optimization.md): 자릿수 상태와 rolling array를 다룹니다.
