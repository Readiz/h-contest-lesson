# Polynomial Model Map

Polynomial/recurrence 문제는 같은 계수열을 보더라도 관점이 다릅니다. 먼저 "곱셈", "변환", "평가/복원", "n번째 항" 중 무엇이 필요한지 나눕니다.

## 1. 네 축

| 축 | 필요한 정보 | 대표 기법 |
| --- | --- | --- |
| Convolution | 두 계수열의 곱 | FFT/NTT |
| FPS transform | inverse, log, exp, power | Formal Power Series |
| Evaluation/interpolation | 많은 점의 값 또는 계수 복원 | Multipoint Evaluation, Interpolation |
| Recurrence coefficient | 큰 n번째 항 | Kitamasa, Bostan-Mori, Berlekamp-Massey |

## 2. Kitamasa, Bostan-Mori, BM 구분

| 상황 | 후보 |
| --- | --- |
| 점화식 계수와 초기항이 주어진다 | Kitamasa |
| rational generating function `P/Q`가 주어진다 | Bostan-Mori |
| 앞 항만 만들 수 있고 점화식을 모른다 | Berlekamp-Massey |
| 상태 수가 작고 구현 안정성이 중요하다 | Matrix Exponentiation |

BM은 field 위 알고리즘입니다. modulo가 prime이 아니거나 나눗셈이 안전하지 않으면 그대로 쓰면 안 됩니다.

## 3. 구현 전에 확인할 것

- 결과 mod가 NTT-friendly인가?
- convolution 길이가 단순 `O(N^2)`보다 FFT/NTT가 이득일 만큼 큰가?
- FPS 상수항 조건이 맞는가?
- rational form의 분모 `Q(0)`가 0이 아닌가?
- recurrence 차수와 필요한 앞 항 개수가 충분한가?
- naive small-degree 구현으로 식을 먼저 검증했는가?
