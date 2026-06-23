# Online Planning Evaluation

Online Planning Evaluation은 simulator 기반 policy나 search agent를 제출하기 전에, rollout score를 통계적으로 비교하고 시간 예산 안에서 안정성을 검증하는 절차입니다. 좋은 policy를 만드는 것만큼, 우연히 좋아 보이는 policy를 걸러내는 일이 중요합니다.

이 레슨은 Monte Carlo Tree Search, POMCP, Bayesian Bandits 이후에 보는 게임/탐색 평가 심화입니다.

1. 같은 seed 묶음에서 baseline과 후보 policy를 비교한다.
2. 평균뿐 아니라 분산, confidence interval, worst-case를 본다.
3. tuning set과 holdout set을 분리한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Monte Carlo Tree Search, POMCP, Bayesian Bandits
- 함께 보면 좋은 레슨: Testing and Stress, Heuristic, Reinforcement Learning Basics
- 다음에 볼 레슨: policy tuning, simulator benchmark, sequential decision evaluation

## 1. 문제 신호

| 문제 표현 | Online Planning Evaluation 관점 |
| --- | --- |
| simulator가 있고 policy를 여러 번 실행할 수 있다 | rollout evaluation |
| seed에 따라 점수 분산이 크다 | paired seed 비교 |
| MCTS/POMCP/heuristic parameter를 고른다 | tuning and holdout |
| 평균 점수는 올랐지만 특정 case에서 깨진다 | distribution check |
| 시간 제한 안에서 planning depth를 조절한다 | budget-aware benchmark |

대회형 heuristic/game 문제에서는 "좋아 보이는 한 seed"보다 "같은 seed 묶음에서 일관되게 좋아지는지"가 더 중요합니다.

## 2. Paired Seed 비교

baseline policy `A`와 후보 policy `B`를 비교할 때, 서로 다른 seed로 평균을 내면 noise가 큽니다. 같은 seed에서 둘 다 실행하고 차이 `B - A`를 모읍니다.

```text
seed 1: B - A = +12
seed 2: B - A = -3
seed 3: B - A = +8
...
```

이 차이의 평균과 분산을 보면, 후보가 baseline보다 안정적으로 나은지 판단하기 쉽습니다.

## 3. Confidence Interval

rollout 점수 차이를 `d_i`라고 하면 평균 차이와 표준오차를 계산합니다.

```text
mean = sum(d_i) / n
stderr = sample_std(d_i) / sqrt(n)
rough 95% interval = mean +- 2 * stderr
```

구간이 0을 충분히 벗어나면 개선이라고 볼 수 있습니다. 구간이 0을 크게 걸치면 seed를 늘리거나 후보를 더 명확히 바꿔야 합니다.

## 4. 평가 코드 골격

아래 코드는 이미 얻은 score 차이 목록에서 평균과 표준오차를 계산하는 최소 골격입니다.

```cpp
#include <cmath>
#include <vector>
using namespace std;

struct Summary {
    double mean = 0.0;
    double stderr = 0.0;
};

Summary summarizeDifferences(const vector<double>& diff) {
    Summary result;
    if (diff.empty()) {
        return result;
    }
    for (double value : diff) {
        result.mean += value;
    }
    result.mean /= (double)diff.size();

    if (diff.size() == 1) {
        return result;
    }

    double variance = 0.0;
    for (double value : diff) {
        double delta = value - result.mean;
        variance += delta * delta;
    }
    variance /= (double)(diff.size() - 1);
    result.stderr = sqrt(variance / (double)diff.size());
    return result;
}
```

실전 benchmark runner는 seed, parameter, elapsed time, score, fail reason을 모두 로그로 남겨야 합니다.

## 5. Tuning Set과 Holdout Set

parameter를 여러 번 바꾸며 같은 seed에서만 성능을 올리면 overfitting이 생깁니다.

| 데이터 묶음 | 목적 |
| --- | --- |
| tuning seeds | parameter 탐색과 빠른 회귀 확인 |
| holdout seeds | 최종 후보 검증 |
| stress seeds | rare failure, timeout, invalid move 탐지 |
| adversarial cases | 알려진 약점 재현 |

holdout 결과가 tuning 결과보다 훨씬 나쁘면 parameter가 특정 seed에 맞춰진 것입니다.

## 6. Budget-Aware Evaluation

online planning은 시간 예산을 먹습니다. score가 조금 올라도 시간 초과나 variance가 커지면 실전에서는 손해입니다.

```text
score per seed
elapsed milliseconds
number of simulations
timeout count
invalid action count
```

MCTS나 POMCP는 simulation count만 비교하면 안 됩니다. state transition 비용, rollout policy 비용, memory allocation 때문에 같은 simulation 수라도 실제 시간이 달라질 수 있습니다.

## 7. Baseline 설계

좋은 baseline은 약하지만 안정적이어야 합니다.

| baseline | 쓰는 이유 |
| --- | --- |
| greedy policy | 빠른 sanity check |
| previous submitted version | regression 판단 |
| random legal policy | simulator validity check |
| oracle on tiny cases | upper bound 또는 debugging |

후보 policy가 random보다만 좋다고 충분한 것은 아닙니다. 이전 안정 버전과 같은 seed로 비교해야 실제 개선을 볼 수 있습니다.

## 8. 자주 하는 실수

1. 평균 점수만 보고 timeout 수를 보지 않는다.
2. seed를 고정하지 않아 policy 간 비교가 noise에 묻힌다.
3. tuning에 사용한 seed로 최종 성능을 선언한다.
4. invalid action을 낮은 점수로만 기록하고 원인을 잃어버린다.
5. elapsed time을 local debug build에서만 측정한다.

## 9. 문제를 볼 때 체크할 조건

- simulator가 deterministic seed를 지원하는가?
- 같은 seed에서 baseline과 후보를 모두 실행할 수 있는가?
- score가 클수록 좋은가, 작을수록 좋은가?
- timeout과 invalid action을 어떻게 penalty 처리하는가?
- 제출 환경의 시간 예산과 local benchmark 시간이 얼마나 다른가?

## 10. 대표 문제로 연결하기

### 문제에서 보이는 신호

- 입력 크기: exact optimal보다 policy/search가 필요한 크기
- 필요한 복잡도: 제한 시간 안의 반복 simulation
- 이 레슨의 핵심 개념: paired evaluation과 holdout 검증

### 풀이 흐름

1. seed 목록을 tuning/holdout/stress로 나눈다.
2. baseline policy의 score와 elapsed time을 저장한다.
3. 후보 policy를 같은 seed에서 실행해 score 차이를 계산한다.
4. 평균, confidence interval, timeout count를 함께 본다.
5. 최종 후보는 holdout seed에서 다시 검증한다.

### 자주 틀리는 지점

- MCTS simulation 수를 늘려 평균은 올라가도 deadline 근처에서 timeout variance가 커질 수 있습니다.
- simulator bug와 policy bug를 분리하려면 random legal policy가 항상 valid trajectory를 만드는지 먼저 확인하는 편이 좋습니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: online planning evaluation `/practice/...` 문제 필요 | paired seed score 비교 | baseline |
| 표준 | TODO: rollout benchmark `/practice/...` 문제 필요 | confidence interval과 holdout 분리 | standard error |
| 응용 | TODO: MCTS tuning `/practice/...` 문제 필요 | simulation budget과 score tradeoff | time budget |
| 함정 | TODO: noisy policy regression `/practice/...` 문제 필요 | 평균 개선과 timeout 악화 구분 | variance |
