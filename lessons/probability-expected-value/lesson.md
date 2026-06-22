# 확률과 기대값

확률과 기대값 문제는 경우의 수를 직접 세는 대신, 상태별로 "앞으로 얼마나 걸리는가" 또는 "성공할 가능성이 얼마인가"를 식으로 세웁니다. 대회에서는 주사위, 랜덤 이동, 흡수 상태, 기댓값 DP 형태로 자주 등장합니다.

이 레슨은 확률 DP와 기대값 식 세우기의 기본 패턴을 정리합니다.

1. 상태와 전이 확률을 명확히 둔다.
2. 확률은 합으로, 기대값은 `1 + 다음 기대값 평균`으로 세운다.
3. DAG가 아닌 전이는 연립방정식 또는 식 변형이 필요함을 구분한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 동적 계획법, 모듈러 연산, 선형 방정식 기본 감각
- 함께 보면 좋은 레슨: 동적 계획법, 조합론, Matrix Exponentiation
- 다음에 볼 레슨: Markov chain, absorbing probability, Gaussian elimination

## 1. 확률 DP와 기대값 DP

확률은 특정 사건이 일어날 가능성을 구합니다. 기대값은 어떤 값의 평균적인 결과를 구합니다.

| 질문 | 식의 형태 |
| --- | --- |
| 성공할 확률은? | `prob[state] = sum p * prob[next]` |
| 끝날 때까지 평균 몇 번? | `E[state] = 1 + sum p * E[next]` |
| 얻는 점수의 평균은? | `E[state] = reward + sum p * E[next]` |
| 여러 선택 중 최적인 기대값은? | `min` 또는 `max`와 기대값 결합 |

확률의 합은 1이어야 합니다. 기대값은 단위가 "횟수", "점수", "비용" 중 무엇인지 먼저 고정해야 합니다.

## 2. DAG 기대값

상태가 항상 더 큰 번호로만 이동한다면 뒤에서부터 계산할 수 있습니다. 예를 들어 칸 `pos`에서 주사위를 던져 `target` 이상이 되면 끝난다고 합시다.

```cpp compile-check
#include <vector>
using namespace std;

vector<double> expectedDiceThrows(int target) {
    vector<double> expected(target + 1, 0.0);
    expected[target] = 0.0;

    for (int pos = target - 1; pos >= 0; --pos) {
        double sum = 0.0;
        for (int dice = 1; dice <= 6; ++dice) {
            int next = pos + dice;
            if (next > target) {
                next = target;
            }
            sum += expected[next];
        }
        expected[pos] = 1.0 + sum / 6.0;
    }

    return expected;
}
```

`expected[pos]`는 현재 위치에서 끝까지 필요한 평균 던짐 수입니다. 한 번 던지는 행동이 있으므로 항상 `1.0`이 더해집니다.

## 3. 확률 분포 DP

주사위를 `n`번 던졌을 때 합의 분포는 DP로 계산할 수 있습니다.

```cpp compile-check
#include <vector>
using namespace std;

vector<double> diceSumDistribution(int throws) {
    vector<double> dp(6 * throws + 1, 0.0);
    dp[0] = 1.0;

    for (int t = 0; t < throws; ++t) {
        vector<double> next(6 * throws + 1, 0.0);
        for (int sum = 0; sum <= 6 * t; ++sum) {
            for (int dice = 1; dice <= 6; ++dice) {
                next[sum + dice] += dp[sum] / 6.0;
            }
        }
        dp.swap(next);
    }

    return dp;
}
```

확률 분포 DP에서는 전체 확률 합이 1에 가까운지 확인하면 디버깅에 도움이 됩니다. 실수 오차가 있으므로 `1e-9` 정도의 오차는 허용합니다.

## 4. 기대값의 선형성

기대값은 사건들이 독립이 아니어도 합을 분리할 수 있습니다.

```text
E[X + Y] = E[X] + E[Y]
```

예를 들어 여러 indicator 변수를 세는 문제에서는 각 사건이 일어날 확률을 더하면 전체 기대 개수가 됩니다.

```text
기대 개수 = sum P(각 항목이 선택됨)
```

이 성질은 복잡한 상관관계를 직접 세지 않아도 되는 강력한 도구입니다.

## 5. 순환이 있는 기대값

상태가 자기 자신이나 이전 상태로 돌아올 수 있으면 단순한 역순 DP가 안 됩니다.

예를 들어 어떤 상태에서 확률 `p`로 성공하고, 확률 `1-p`로 같은 상태에 남는다면:

```text
E = 1 + (1 - p) * E
p * E = 1
E = 1 / p
```

상태가 여러 개면 이런 식들이 연립방정식이 됩니다. 작은 상태 수에서는 Gaussian elimination을 쓰고, 특수 구조가 있으면 식을 변형해 닫힌 형태로 풉니다.

## 6. 모듈러 확률

정답을 `MOD`로 출력하라는 문제에서는 확률 `a / b`를 `a * inv(b) mod MOD`로 표현합니다. `MOD`가 소수이고 `b`가 `MOD`의 배수가 아니어야 Fermat 역원을 사용할 수 있습니다.

```cpp compile-check
long long modPow(long long base, long long exp, long long mod) {
    long long result = 1 % mod;
    base %= mod;
    while (exp > 0) {
        if (exp & 1LL) {
            result = result * base % mod;
        }
        base = base * base % mod;
        exp >>= 1LL;
    }
    return result;
}

long long probabilityMod(long long numerator, long long denominator, long long mod) {
    return numerator % mod * modPow(denominator, mod - 2, mod) % mod;
}
```

실수 출력 문제인지 모듈러 출력 문제인지에 따라 구현이 완전히 달라집니다. 문제의 출력 형식을 먼저 확인합니다.

## 7. 최적 선택과 기대값

랜덤 전이가 있지만 중간에 선택도 할 수 있다면 DP에 `min` 또는 `max`가 섞입니다.

```text
E[state] = min_action( cost(action) + sum p(next) * E[next] )
```

이 경우에도 각 action을 고정하면 기대값 식이고, 그중 최적 action을 선택합니다. 단, 순환이 있으면 최적성 방정식이 되어 더 어려워질 수 있습니다.

## 8. 시간 복잡도

| 형태 | 시간 |
| --- | ---: |
| DAG 기대값 DP | `O(states * transitions)` |
| 확률 분포 DP | `O(steps * states * outcomes)` |
| Gaussian elimination | `O(states^3)` |
| Monte Carlo simulation | 정확도에 따라 다름 |

대회 문제는 보통 정확한 값을 요구합니다. "랜덤으로 많이 돌려 평균"은 검증용으로는 쓸 수 있지만 정답 제출용으로는 거의 맞지 않습니다.

## 9. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 기대값 식에 현재 1회를 더하지 않음 | 1씩 작아짐 | 행동 횟수의 단위 확인 |
| 확률 합이 1이 아님 | 전체 값 왜곡 | transition probability 합 검사 |
| 순환 상태를 역순 DP로 처리 | 아직 모르는 값 사용 | DAG인지 확인 |
| 독립성이 필요 없는 선형성을 독립 조건으로 오해 | 풀이 과복잡 | indicator expectation 활용 |
| 모듈러 확률에서 나눗셈 직접 사용 | 오답 | modular inverse 사용 |
| 실수 오차 출력 형식 무시 | Wrong Answer | 오차 허용/자리수 확인 |

## 10. 문제를 볼 때 체크할 조건

1. 구하는 것이 확률인지 기대값인지 명확한가?
2. 상태와 전이 확률의 합이 1인가?
3. 상태 그래프가 DAG인가, 순환이 있는가?
4. 현재 행동의 비용이나 횟수 `+1`이 들어가는가?
5. 출력이 실수인가, 모듈러 분수인가?
6. 기대값의 선형성으로 각 항목 기여를 따로 셀 수 있는가?

확률과 기대값 문제는 식을 세우는 순간 절반 이상 풀립니다. 상태의 의미, 한 번의 행동, 다음 상태의 분포를 한 줄로 정확히 쓰는 습관이 가장 중요합니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 주사위 기대 횟수 `/practice/...` 문제 필요 | `1 + 평균 다음 기대값` 식 세우기 | expectation DP |
| 표준 | TODO: 확률 분포 DP `/practice/...` 문제 필요 | 상태별 확률 합 전파 | probability distribution |
| 응용 | TODO: indicator 기대값 `/practice/...` 문제 필요 | 기대값의 선형성 적용 | linearity |
| 함정 | TODO: 순환 기대값 `/practice/...` 문제 필요 | 연립방정식 또는 식 변형 | Markov chain |
