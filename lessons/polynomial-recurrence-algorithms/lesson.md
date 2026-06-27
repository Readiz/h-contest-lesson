# Polynomial and Recurrence Algorithms

Polynomial and Recurrence Algorithms는 convolution, formal power series, multipoint evaluation, interpolation, generating function, linear recurrence를 하나의 수학 알고리즘 트랙으로 묶는 허브입니다. 이 주제들은 모두 "계수열을 어떻게 빠르게 곱하고, 변환하고, n번째 항을 뽑을 것인가"라는 흐름으로 이어집니다.

개별 알고리즘 이름보다 먼저 아래 질문을 결정해야 합니다.

1. 이중 합이 convolution으로 정리되는가?
2. 계수열을 FPS 연산으로 변환해야 하는가?
3. polynomial을 여러 점에서 평가하거나 복원해야 하는가?
4. generating function이 rational form인가?
5. 선형 점화식이 주어졌는가, 아니면 앞 항에서 찾아야 하는가?

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Modular Arithmetic, Combinatorics, Matrix Exponentiation
- 함께 보면 좋은 레슨: Linear Algebra Applications, Black-Box Linear Algebra, Convex DP Optimization
- 다음에 볼 레슨: Black-Box Linear Algebra, Sparse Linear Systems, Randomized Determinant

## 1. 학습 경로

| 단계 | 먼저 볼 페이지 |
| --- | --- |
| 다항식 곱셈과 convolution 모델링 | [FFT and NTT](pages/fft-ntt.md) |
| FPS 기본 연산과 truncate/inverse | [Formal Power Series](pages/formal-power-series.md) |
| FPS log/exp/power 조건 | [FPS Log and Exp](pages/fps-log-exp.md) |
| 여러 점 평가와 subproduct tree | [Multipoint Evaluation](pages/multipoint-evaluation.md) |
| 계수 복원과 Lagrange interpolation | [Polynomial Interpolation](pages/polynomial-interpolation.md) |
| counting 문제를 생성함수로 번역 | [Generating Function Modeling](pages/generating-function-modeling.md) |
| 주어진 선형 점화식의 n번째 항 | [Linear Recurrence and Kitamasa](pages/linear-recurrence-kitamasa.md) |
| rational generating function 계수 추출 | [Bostan-Mori](pages/bostan-mori.md) |
| 문제에서 점화식을 찾아 방법 선택 | [Linear Recurrence Applications](pages/linear-recurrence-applications.md) |
| 앞 항에서 점화식 후보를 추정 | [Recurrence Guessing](pages/recurrence-guessing.md), [Berlekamp-Massey](pages/berlekamp-massey.md) |

## 2. 모델 선택 표

| 문제 신호 | 우선 후보 |
| --- | --- |
| `sum a[i] * b[k-i]` 꼴 | FFT/NTT |
| 다항식 inverse/log/exp가 필요 | Formal Power Series |
| `P(x_i)`를 많은 점에서 평가 | Multipoint Evaluation |
| 점 몇 개로 다항식을 복원 | Polynomial Interpolation |
| counting 구조가 product/sequence/set로 조합 | Generating Function Modeling |
| 낮은 차수 선형 점화식이 주어짐 | Kitamasa, Bostan-Mori |
| 처음 항만 많이 만들 수 있음 | Berlekamp-Massey + nth term |
| 큰 행렬을 직접 저장하기 어렵고 matvec만 가능 | Black-Box Linear Algebra로 이동 |

## 3. 공개 상태

하위 페이지들은 기존 구현과 설명을 보존합니다. practice link가 부족한 항목은 [Practice Set](pages/practice-set.md)에 TODO로 모아 둡니다.
