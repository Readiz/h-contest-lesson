# FPS Log와 Exp

형식적 거듭제곱급수에서 log와 exp는 계수 연산입니다. 소수 MOD 위에서 필요한 차수가 MOD보다 작아 1..N의 역원이 존재한다고 가정합니다.

## Log

F(0)=1일 때 `log F = integral(F'/F)`입니다. [Formal Power Series](https://h.readiz.com/learn/polynomial-recurrence-algorithms/formal-power-series)의 derivative, inversePolynomial, multiplyTruncated, integral을 순서대로 사용하고 원하는 길이로 자릅니다. 적분 상수는 0입니다.

`log(1+x) = x-x²/2+x³/3-...`가 작은 검산 예시입니다. 나눗셈은 field 역원입니다.

## Exp

G(0)=0일 때 F=exp(G)는 F(0)=1이고 `F'=G'F`를 만족합니다. 따라서 작은 입력은 다음 계수 점화식으로 검산할 수 있습니다.

```text
f[0] = 1
f[n] = inverse(n) * sum(i*g[i]*f[n-i], i=1..n)
```

이 방법은 O(N²)입니다. `exp(x)=1+x+x²/2+x³/6+...`를 확인합니다. 빠른 구현은 `F <- F*(1+G-log F)`로 맞는 계수 길이를 두 배씩 늘리고 NTT 곱셈을 사용합니다. 수학식만 같다고 단순 곱셈이 O(N log N)이 되지는 않습니다.

## 생성함수에서의 의미

라벨이 붙은 조합 대상이 연결 성분들의 집합으로 유일하게 분해될 때 지수 생성함수는 `A(x)=exp(C(x))` 관계를 가질 수 있습니다. 이때 C(0)=0이며 계수의 n! 정규화를 포함해야 합니다. 임의의 일반 생성함수에 같은 관계를 적용하지 않습니다.
