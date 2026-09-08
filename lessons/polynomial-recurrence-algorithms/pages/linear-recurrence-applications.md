# Linear Recurrence Applications

Linear Recurrence Applications는 점화식이 주어진 상황을 넘어, 문제에서 recurrence를 찾아내고 Matrix Exponentiation, Kitamasa, Bostan-Mori, Berlekamp-Massey 중 무엇을 쓸지 고르는 레슨입니다. 핵심은 알고리즘 이름보다 "상태 전이가 선형인가"와 "계수가 고정인가"를 먼저 확인하는 것입니다.

## 문제 신호

| 문제 표현 | Recurrence 관점 |
| --- | --- |
| 이전 K개 항으로 다음 항 결정 | 직접 linear recurrence |
| 격자/그래프 walk 수 `n`번째 | matrix power 또는 characteristic polynomial |
| 동일 전이를 매우 많이 반복 | transition exponentiation |
| 처음 항만 많이 주어짐 | Berlekamp-Massey 후보 |
| 생성함수 분모가 낮은 차수 | Bostan-Mori 후보 |

점화식이 선형이려면 다음 항이 이전 항들의 상수 계수 합이어야 합니다. `min`, `max`, `xor`가 섞이면 다른 구조일 수 있습니다.

## 방법 선택표

| 조건 | 우선 방법 |
| --- | --- |
| 상태 수가 작고 전이가 일반적 | Matrix Exponentiation |
| 단일 K차 recurrence, K가 중간 | Kitamasa |
| 생성함수 `P/Q`가 주어짐 | Bostan-Mori |
| 앞 항만 있고 recurrence를 모름 | Berlekamp-Massey + Kitamasa |
| 같은 recurrence에 많은 n 질의 | polynomial power 전처리 또는 multipoint |

구현 안정성까지 보면, K가 작으면 행렬이 가장 읽기 쉽습니다. K가 커지고 전이가 companion 형태면 Kitamasa가 유리합니다.

## 그래프 Walk를 Recurrence로 보기

정점 수가 `S`인 graph에서 길이 `n` walk 수는 adjacency matrix `A^n`으로 계산합니다. Cayley-Hamilton 정리에 의해 각 entry도 차수 `S` 이하의 선형 recurrence를 가집니다.

```text
walk_n = (A^n)[start][target]
```

`S`가 작으면 matrix exponentiation이 충분합니다. `S`가 크지만 처음 항을 빠르게 만들 수 있으면 Berlekamp-Massey로 recurrence를 추정하는 전략도 후보가 됩니다.

## Berlekamp-Massey 연결

모듈러 prime field에서 수열의 앞 항을 충분히 알고 있으면 최소 선형 점화식을 찾을 수 있습니다.

```text
first terms -> Berlekamp-Massey -> coeff -> Kitamasa nth term
```

주의할 점은 "충분한 앞 항"입니다. 차수 `K` recurrence라면 보통 `2K`개 이상이 필요합니다. 항 생성 자체가 비싸면 이 전략이 이득이 아닐 수 있습니다.

## Companion Matrix와 Kitamasa

K차 recurrence는 companion matrix로도 볼 수 있습니다.

```text
[a_n, a_{n-1}, ..., a_{n-K+1}]^T
  = M * [a_{n-1}, ..., a_{n-K}]^T
```

Kitamasa는 이 companion matrix의 거듭제곱을 polynomial 나머지로 계산하는 관점입니다. 그래서 recurrence가 정확히 K개 이전 항의 선형 결합일 때 잘 맞습니다.

## Bostan-Mori가 좋은 경우

생성함수가 아래처럼 rational form이면 Bostan-Mori가 직접적입니다.

```text
F(x) = P(x) / Q(x)
answer = [x^n] F(x)
```

조합 문제에서 "길이 n 구조의 개수"가 polynomial equation이나 transfer로 나오면 생성함수 분모를 만들 수 있습니다. 이때 nth coefficient extraction이 recurrence 계산과 같은 역할을 합니다.

## 작은 예시

```text
문제: 길이 n 문자열에서 11이 나오지 않는 binary string 개수

dp0[n] = n번째가 0으로 끝남
dp1[n] = n번째가 1로 끝남

dp0[n] = dp0[n-1] + dp1[n-1]
dp1[n] = dp0[n-1]

total[n] = total[n-1] + total[n-2]
```

상태 DP로 보면 2x2 matrix이고, 수열로 보면 Fibonacci 형태의 2차 recurrence입니다. 필요한 질의와 N 범위에 따라 둘 중 하나를 고르면 됩니다.

## 구현 연결

위 이진 문자열 예시는 `a[0]=1`, `a[1]=2`, 계수 `[1,1]`을 [Kitamasa 구현](linear-recurrence-kitamasa.md)에 넣습니다. 다른 문제에서도 먼저 초기항 인덱스와 계수 순서를 맞춥니다.

## 시간 복잡도

| 방법 | 시간 |
| --- | ---: |
| Matrix exponentiation | `O(S^3 log N)` |
| Kitamasa 기본형 | `O(K^2 log N)` |
| Berlekamp-Massey | `O(T^2)` 또는 최적화 가능 |
| Bostan-Mori with NTT | `O(K log K log N)` 근처 |

`S`는 상태 수, `K`는 recurrence 차수입니다. 둘이 같을 수도 있지만 항상 같지는 않습니다.

## 자주 하는 실수

1. recurrence가 선형이 아닌데 BM으로 추정하려 한다.
2. 합성수 mod에서 field inverse가 필요한 알고리즘을 그대로 쓴다.
3. 초기항이 `a_1`부터 주어졌는데 `a_0` 기반 함수에 그대로 넣는다.
4. 여러 질의에서 매번 앞 항을 새로 생성한다.
5. matrix 상태 순서와 recurrence coeff 순서를 섞는다.
