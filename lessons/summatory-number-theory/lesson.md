# Summatory Number Theory

Summatory Number Theory는 `sum_{i=1}^n f(i)` 형태의 누적 정수론 값을 큰 `n`에 대해 빠르게 계산하는 관점입니다. `phi`, `mu`, divisor count 같은 multiplicative function을 전부 직접 구할 수 없는 범위에서는 floor division grouping, prefix transform, memoized recursion을 조합합니다.

이 레슨은 Multiplicative Functions, Mobius Inversion 이후에 보는 정수론 심화입니다.

1. `n / i` 값이 같은 구간을 한 번에 묶는다.
2. divisor sum 식을 prefix sum 형태로 바꾼다.
3. sieve 가능한 범위와 큰 `n` query를 분리한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: multiplicative function, Mobius inversion, linear sieve, prefix sum
- 함께 보면 좋은 레슨: Multiplicative Functions, Dirichlet Convolution, Mobius Inversion
- 다음에 볼 레슨: Min_25 sieve, Du Jiao sieve, floor-sum applications

## 1. 문제 신호

| 문제 표현 | Summatory 관점 |
| --- | --- |
| `sum phi(i)` 또는 `sum mu(i)`를 큰 `n`에 대해 묻는다 | summatory multiplicative function |
| `floor(n / i)`가 식에 반복된다 | floor division grouping |
| `sum_{d|n}` 또는 `sum_{i,j}` gcd 조건 | divisor transform, Mobius inversion |
| query가 많고 `n`이 크다 | small prefix sieve + memoization |
| `O(n)`도 안 된다 | 같은 quotient 구간 압축 |

먼저 식에서 `floor(n / i)`가 몇 번 등장하는지 봅니다. 이 값은 서로 다른 값이 `O(sqrt n)`개뿐이라 많은 합을 구간 단위로 줄일 수 있습니다.

## 2. Floor Division Grouping

`q = n / i`가 같은 `i`의 범위는 아래처럼 구합니다.

```text
l = 1
while l <= n:
  q = n / l
  r = n / q
  i in [l, r]에서는 floor(n / i) = q
  l = r + 1
```

아래 코드는 이 구간들을 반환합니다.

```cpp compile-check
#include <tuple>
#include <vector>
using namespace std;

struct FloorBlock {
    long long left = 0;
    long long right = 0;
    long long quotient = 0;
};

vector<FloorBlock> floorDivisionBlocks(long long n) {
    vector<FloorBlock> blocks;
    for (long long left = 1; left <= n; ) {
        long long quotient = n / left;
        long long right = n / quotient;
        blocks.push_back({left, right, quotient});
        left = right + 1;
    }
    return blocks;
}
```

`n = 20`이면 quotient는 `20, 10, 6, 5, 4, 3, 2, 1`처럼 몇 개만 나옵니다. 뒤쪽 큰 구간에서는 같은 quotient가 길게 반복됩니다.

## 3. 작은 예시

```text
n = 10
i:            1  2  3  4  5  6  7  8  9 10
floor(10/i): 10  5  3  2  2  1  1  1  1  1

blocks:
[1,1] -> 10
[2,2] -> 5
[3,3] -> 3
[4,5] -> 2
[6,10] -> 1
```

예를 들어 `sum floor(n / i)`는 각 block의 길이에 quotient를 곱해 더하면 됩니다.

## 4. Divisor Sum을 Prefix로 바꾸기

많은 합은 divisor 기준으로 순서를 바꾸면 쉬워집니다.

```text
sum_{i=1}^n sum_{d|i} f(d)
= sum_{d=1}^n f(d) * floor(n / d)
```

이때 `f(d)`의 prefix sum을 알고 있으면 floor division grouping으로 구간 합을 빠르게 계산합니다.

| 원래 식 | 바꾼 식 |
| --- | --- |
| `sum tau(i)` | `sum_d floor(n / d)` |
| `sum sigma(i)` | `sum_d d * floor(n / d)` |
| gcd가 1인 pair 수 | `sum_d mu(d) * floor(n/d)^2` |

Mobius inversion과 결합하면 gcd 조건을 divisor block으로 바꿀 수 있습니다.

## 5. Summatory Phi의 재귀 직관

Euler phi는 아래 항등식을 가집니다.

```text
sum_{d|n} phi(d) = n
```

이를 summatory로 누적하면 작은 prefix와 큰 quotient 구간을 나눠 `Phi(n) = sum_{i<=n} phi(i)`를 재귀적으로 구할 수 있습니다.

```text
sum_{i=1}^n i = sum_{d=1}^n phi(d) * floor(n / d)^2 형태로 볼 수 있음
```

실전에서는 Du Jiao sieve 같은 이름으로 등장합니다. 구현 전에 필요한 항등식과 base prefix를 정확히 적는 것이 먼저입니다.

## 6. Sieve 범위와 Memoization

큰 `n` query가 있을 때는 모든 값을 sieve하지 않습니다.

1. `B`까지는 linear sieve로 `f(i)`와 prefix를 구한다.
2. `n <= B` query는 prefix에서 바로 답한다.
3. `n > B` query는 floor quotient로 나뉘는 값만 재귀 계산한다.
4. `n / l` 값별 결과를 hash map에 memoization한다.

`n`이 커도 재귀에서 만나는 서로 다른 quotient는 제한적입니다. 하지만 여러 함수가 섞이면 memo key에 함수 종류도 들어가야 합니다.

## 7. 구현 체크리스트

| 항목 | 확인 |
| --- | --- |
| 합 범위 | `1..n`인지 `0..n`인지 |
| 나눗셈 구간 | `right = n / (n / left)` |
| prefix sum | `[l, r]` 구간 합은 `prefix[r] - prefix[l-1]` |
| overflow | `floor(n/d)^2`와 곱셈은 `__int128` 필요 가능 |
| modulo | 음수 Mobius 합을 modulo로 정규화 |

정수론 summatory 문제의 오답은 대부분 수식보다 index와 overflow에서 나옵니다.

## 8. 시간 복잡도 감각

| 작업 | 복잡도 |
| --- | ---: |
| floor division blocks | `O(sqrt n)`개 block |
| small sieve | `O(B)` 또는 `O(B log log B)` |
| prefix 기반 divisor sum | block마다 `O(1)`이면 `O(sqrt n)` |
| memoized summatory recursion | 식과 cache 범위에 따라 달라짐 |

여러 query가 있으면 큰 값의 quotient 결과가 재사용되는지에 따라 성능이 크게 갈립니다.

## 9. 자주 하는 실수

1. `right = n / quotient` 대신 `right = n / (quotient + 1)` 같은 식으로 off-by-one을 만든다.
2. `i = 0`이 포함되지 않는 식에 0을 넣는다.
3. Mobius prefix의 음수를 modulo로 제대로 정리하지 않는다.
4. `floor(n / d)^2`를 `long long` 범위라고 가정한다.
5. multiplicative function의 point value와 summatory value를 같은 cache에 넣는다.
6. convolution 항등식을 확인하지 않고 Du Jiao 형태를 외워서 적용한다.

## 10. 문제를 볼 때 체크할 조건

- 식에 `floor(n / i)`가 반복되는가?
- divisor 기준으로 합의 순서를 바꿀 수 있는가?
- 필요한 `f(i)`가 sieve로 prefix 가능인가?
- 큰 `n`에서 만나는 quotient를 memoization할 수 있는가?
- modulo와 overflow 처리를 식마다 분리했는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: floor division grouping `/practice/...` 문제 필요 | quotient block 만들기 | `n / i` 구간 |
| 표준 | TODO: divisor summatory `/practice/...` 문제 필요 | 합 순서 바꾸기 | divisor transform |
| 응용 | TODO: summatory phi/mu `/practice/...` 문제 필요 | prefix + memoization | Du Jiao 관점 |
| 함정 | TODO: large modulo gcd pair `/practice/...` 문제 필요 | overflow와 음수 정규화 | Mobius, `__int128` |
