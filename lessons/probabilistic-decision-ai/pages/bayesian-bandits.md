# Bayesian Bandits

Bayesian Bandits는 여러 선택지의 보상 확률을 모르는 상태에서, 관측할수록 posterior를 갱신하며 다음 선택을 정하는 모델입니다. 단순한 multi-armed bandit이 "탐색과 활용의 균형"을 다룬다면, Bayesian 관점은 불확실성을 확률분포로 들고 다닙니다.

## 문제 신호

| 문제 표현 | Bayesian Bandit 관점 |
| --- | --- |
| 여러 선택지 중 보상 확률을 모른다 | arm별 posterior |
| 선택하면 그 선택지의 결과만 관측된다 | partial feedback |
| 탐색 비용과 활용 이득을 균형 잡아야 한다 | exploration/exploitation |
| 성공/실패 Bernoulli 보상 | Beta posterior |
| finite horizon에서 기대 보상 최대화 | belief-state DP 후보 |

대회 문제에서는 실제 stochastic interaction보다 offline으로 "이 정책의 기대값", "최적 탐색 순서", "posterior 갱신 후 확률"을 계산하는 형태가 더 자주 나옵니다.

## Beta-Bernoulli 모델

성공 확률 `p`를 모르는 Bernoulli arm이 있다고 하겠습니다. prior를 `Beta(alpha, beta)`로 두면 관측 뒤 posterior가 간단합니다.

| 관측 | posterior |
| --- | --- |
| 성공 1회 | `Beta(alpha + 1, beta)` |
| 실패 1회 | `Beta(alpha, beta + 1)` |
| 성공 `s`, 실패 `f` | `Beta(alpha + s, beta + f)` |

posterior mean은 아래와 같습니다.

```text
E[p] = alpha / (alpha + beta)
```

이 값만 쓰면 greedy 정책입니다. Bayesian bandit의 핵심은 mean뿐 아니라 불확실성도 같이 이용하는 것입니다.

## 작은 예시

두 arm이 있습니다.

```text
A: Beta(8, 2), posterior mean = 0.8
B: Beta(1, 1), posterior mean = 0.5
```

당장 한 번만 고르면 `A`가 좋아 보입니다. 하지만 앞으로 기회가 많이 남아 있으면 `B`를 한 번 시도해 볼 가치가 있습니다. `B`가 성공하면 `Beta(2, 1)`이 되어 mean이 `0.667`로 올라가고, 실패하면 `Beta(1, 2)`가 되어 내려갑니다. 관측 자체가 이후 선택의 정보를 만듭니다.

## Thompson Sampling

Thompson Sampling은 각 arm의 posterior에서 보상 확률 후보를 하나씩 sample하고, sample 값이 가장 큰 arm을 선택합니다.

```text
for each arm i:
    theta_i ~ posterior_i
choose argmax theta_i
observe reward
update posterior of chosen arm
```

불확실한 arm은 sample이 크게 나올 가능성이 있어서 자연스럽게 탐색됩니다. 관측이 쌓이면 분포가 좁아져 활용 중심으로 바뀝니다.

## Bayesian UCB

Bayesian UCB는 posterior의 높은 분위수나 mean + uncertainty bonus를 씁니다.

```text
score_i = posterior_mean_i + c * posterior_std_i
```

분산이 큰 arm은 평균이 조금 낮아도 탐색됩니다. contest에서 exact quantile을 구하기 어렵다면, 문제 조건이 간단한 Beta-Bernoulli인지 또는 normal approximation이 허용되는지 확인해야 합니다.

## Finite-Horizon DP

arm 수와 남은 선택 횟수가 작으면 belief state를 DP로 풀 수 있습니다.

```text
dp(a1, b1, a2, b2, ..., remaining)
```

각 arm을 선택했을 때 성공/실패 확률은 posterior mean으로 계산하고, 다음 상태의 기대값을 더합니다.

```text
value(i) =
    mean_i * (reward_success + dp(alpha_i+1, beta_i, remaining-1))
  + (1-mean_i) * (reward_fail + dp(alpha_i, beta_i+1, remaining-1))
```

상태 수는 빠르게 커집니다. arm 수가 크거나 horizon이 길면 Thompson/UCB 같은 근사 정책이나 regret bound 분석으로 넘어갑니다.

## 구현 조각: Posterior Update

```cpp
struct BetaArm {
    long double alpha = 1;
    long double beta = 1;

    long double mean() const {
        return alpha / (alpha + beta);
    }

    void observe(bool success) {
        if (success) {
            alpha += 1;
        } else {
            beta += 1;
        }
    }
};
```

Sampling까지 구현하려면 random generator와 beta distribution이 필요합니다. C++ 표준 라이브러리에는 beta distribution이 직접 없으므로 gamma distribution 두 개를 이용합니다. 대회에서는 sampling 정책 자체보다 posterior 갱신이나 기대값 DP가 더 안전한 출제 형태입니다.

## Regret 관점

Bandit 문제는 최적 arm을 처음부터 알고 있었을 때와 비교한 손실을 regret으로 봅니다.

```text
regret = optimal_fixed_arm_reward - algorithm_reward
```

Bayesian 분석에서는 prior에 대한 기대 regret을 보거나, posterior가 수렴하면서 잘못된 arm을 고르는 횟수가 줄어드는지를 봅니다. 구현 문제에서는 보통 정확한 증명보다 "왜 불확실한 arm도 가끔 선택해야 하는가"를 설명하는 데 쓰입니다.

## 자주 하는 실수

1. posterior mean만 보고 항상 greedy하게 고른다.
2. 선택하지 않은 arm의 posterior까지 갱신한다.
3. Beta prior의 `alpha`, `beta`를 성공/실패 횟수와 반대로 더한다.
4. horizon이 1인 문제와 여러 번 남은 문제를 같은 정책으로 푼다.
5. sampling이 필요한 문제에서 seed와 반복 횟수 검증을 하지 않는다.
