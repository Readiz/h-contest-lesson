# Polynomial and Recurrence Algorithms

Polynomial and Recurrence Algorithms는 convolution, formal power series, multipoint evaluation, interpolation, generating function, linear recurrence를 하나의 수학 알고리즘 트랙으로 묶는 허브입니다. 이 주제들은 모두 "계수열을 어떻게 빠르게 곱하고, 변환하고, n번째 항을 뽑을 것인가"라는 흐름으로 이어집니다.

## 학습 경로

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
| 앞 항에서 점화식 후보를 추정 | [Recurrence Guessing](pages/recurrence-guessing.md), [Berlekamp-Massey](pages/berlekamp-massey.md) |

## 계산 조건

점화식 계수와 초기항이 주어지면 Kitamasa, `P/Q`가 주어지면 Bostan-Mori, 앞 항만 생성할 수 있으면 Berlekamp-Massey를 검토합니다. BM의 나눗셈은 field 위에서 정의되어야 하며, rational coefficient 추출은 `Q(0) != 0`이 필요합니다. FFT/NTT와 FPS의 modulus·상수항 조건은 해당 구현 페이지에서 확인합니다.

## 연습

[로컬 연습](pages/practice-set.md)에서 입력과 검증 기준을 확인합니다.
