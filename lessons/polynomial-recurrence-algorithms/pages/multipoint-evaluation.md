# Multipoint Evaluation

Multipoint Evaluation은 하나의 polynomial `P(x)`를 여러 점 `x_0, x_1, ..., x_{m-1}`에서 빠르게 평가하는 기법입니다. 각 점마다 Horner를 쓰면 `O(NM)`이지만, subproduct tree와 polynomial remainder를 쓰면 NTT 기반으로 훨씬 빠르게 만들 수 있습니다.


Product tree의 점 개수 M과 다항식 길이 N이 같은 규모일 때 빠른 평가 비용을 `O(N log² N)`으로 씁니다. 선형 인수는 monic인 `x-x_i`로 통일합니다. `x_i-x`도 근은 같지만 계수 스케일을 일관되게 처리해야 합니다.

## 문제 신호

| 문제 표현 | 접근 |
| --- | --- |
| 다항식 하나를 많은 점에서 평가 | multipoint evaluation |
| 많은 점의 값을 바탕으로 다항식 복원 | interpolation |
| 점 개수와 차수가 모두 크다 | subproduct tree |
| mod prime과 NTT-friendly modulus | NTT 최적화 가능 |
| 평가점이 기하급수열의 점 | chirp z-transform 등 별도 후보 |

점이 몇 개 안 되면 Horner가 더 간단합니다. Multipoint evaluation은 차수와 점 개수가 모두 커서 `O(NM)`이 부담될 때 사용합니다.

## Subproduct Tree

평가점 `x_i`마다 leaf polynomial을 만듭니다.

```text
leaf_i = x - x_i
```

부모는 두 자식 polynomial의 곱입니다.

```text
node = left * right
```

root는 모든 `(x - x_i)`의 곱입니다. 이 tree를 만들면 각 구간의 평가점들이 공유하는 modulus를 알 수 있습니다.

## Remainder를 내려보내기

어떤 node가 평가점 집합 `S`를 담당한다고 합시다. `P mod nodePolynomial`만 있으면 `S`에 속한 모든 점에서의 값이 보존됩니다.

```text
if M(x_i) = 0:
    P(x_i) = (P mod M)(x_i)
```

그래서 root에서 `P mod rootPolynomial`을 시작으로, 자식에게는 다시 자식 polynomial로 나눈 나머지를 내려보냅니다. leaf의 modulus는 `x - x_i`이므로 나머지는 상수 `P(x_i)`입니다.

## 나머지를 따라가는 예시

`P(x)=x^2+1`을 `0, 1, 2`에서 평가합니다. 계수는 낮은 차수부터 `[1, 0, 1]`로 저장합니다.

| 노드의 평가점 | modulus | 내려가는 나머지 |
| --- | --- | --- |
| `{0,1,2}` | `x(x-1)(x-2)` | `x^2+1` |
| `{0,1}` | `x(x-1)` | `x+1` |
| `{0}` | `x` | `1` |
| `{1}` | `x-1` | `2` |
| `{2}` | `x-2` | `5` |

`x^2+1 = x(x-1)+(x+1)`이므로 `{0,1}` 쪽에서는 원래 다항식 대신 `x+1`만 전달해도 됩니다. 각 leaf에 원래 다항식을 그대로 전달해 Horner로 계산하면 이 차수 감소를 활용하지 못합니다.

## 구현에 필요한 연산

Product tree에는 [다항식 곱셈](fft-ntt.md)이, remainder 전파에는 다항식 나눗셈이 필요합니다. 계수를 뒤집은 다항식의 역원을 이용한 division은 [Formal Power Series](formal-power-series.md)의 inverse와 연결됩니다. 이 페이지는 remainder 전파 원리를 다루며 고속 division까지 포함한 완성 구현은 제공하지 않습니다.

## Interpolation과의 관계

Interpolation은 multipoint evaluation의 반대 문제입니다.

```text
given (x_i, y_i), recover P(x)
```

subproduct tree를 만들고 derivative of product polynomial을 평가해 Lagrange basis의 분모를 구하는 방식으로 이어집니다. 두 문제 모두 product tree가 핵심입니다.

## 시간 복잡도

| 방식 | 시간 |
| --- | ---: |
| 각 점 Horner | `O(NM)` |
| 나이브 product tree + 나이브 remainder | `O(NM)`에 가까움 |
| NTT 기반 multipoint evaluation | `O(N log^2 N)` 근처 |
| 특수한 연속점 평가 | 더 빠른 전용 기법 가능 |

여기서 `N`은 다항식 차수, `M`은 평가점 수입니다. 보통 `N`과 `M`이 같은 규모일 때 `O(N log^2 N)` 형태로 설명합니다.
