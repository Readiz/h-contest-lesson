# 휴리스틱 알고리즘: 초기해와 지역 탐색

## 6. 초기해 만들기

좋은 초기해는 이후 탐색의 출발점을 높여 줍니다. 초기해는 반드시 복잡할 필요가 없습니다. 아래 코드는 작업 순서를 한 번 섞은 뒤, 현재 load가 가장 작은 기계에 작업을 넣습니다.

```cpp
void makeInitialState(const Problem& p, State& s, int randomized) {
    int order[MAX_TASKS];
    clearState(p, s);

    for (int i = 0; i < p.taskCount; ++i) {
        order[i] = i;
    }
    if (randomized) {
        shuffleArray(order, p.taskCount);
    }

    for (int k = 0; k < p.taskCount; ++k) {
        int task = order[k];
        int bestMachine = 0;

        for (int m = 1; m < p.machineCount; ++m) {
            if (s.load[m] < s.load[bestMachine]) {
                bestMachine = m;
            }
        }

        s.machineOf[task] = bestMachine;
        s.load[bestMachine] += p.cost[task];
    }
}
```

초기해를 여러 번 만들 수 있다면 `randomized = 1`로 seed마다 다른 출발점을 얻을 수 있습니다. 반대로 디버깅 중에는 `randomized = 0`으로 고정해 같은 결과를 재현하는 편이 좋습니다.

## 7. 지역 탐색

지역 탐색은 현재 답을 조금 바꾼 이웃 답을 만들어 보고, 더 좋으면 그 답으로 이동하는 방식입니다.

대표적인 변경은 아래처럼 작습니다.

```text
1. 원소 하나를 다른 위치로 옮긴다.
2. 원소 두 개를 서로 바꾼다.
3. 구간 하나를 뒤집는다.
4. 일부 선택을 지우고 다시 채운다.
```

작업 배정 예시에서는 작업 하나를 다른 기계로 옮기는 연산을 먼저 만들 수 있습니다.

```cpp
struct Move {
    int task;
    int fromMachine;
    int toMachine;
};

Move makeRandomMove(const Problem& p, const State& s) {
    Move mv;
    mv.task = randomInt(p.taskCount);
    mv.fromMachine = s.machineOf[mv.task];
    mv.toMachine = mv.fromMachine;

    if (p.machineCount >= 2) {
        while (mv.toMachine == mv.fromMachine) {
            mv.toMachine = randomInt(p.machineCount);
        }
    }

    return mv;
}

void applyMove(const Problem& p, State& s, const Move& mv) {
    if (mv.fromMachine == mv.toMachine) return;

    int taskCost = p.cost[mv.task];
    s.machineOf[mv.task] = mv.toMachine;
    s.load[mv.fromMachine] -= taskCost;
    s.load[mv.toMachine] += taskCost;
}

void rollbackMove(const Problem& p, State& s, const Move& mv) {
    Move undo;
    undo.task = mv.task;
    undo.fromMachine = mv.toMachine;
    undo.toMachine = mv.fromMachine;
    applyMove(p, s, undo);
}
```

이제 현재 답을 직접 바꿔 본 뒤, 나빠졌으면 되돌릴 수 있습니다.

```cpp
void improveByHillClimb(const Problem& p, State& current, State& best, long long& bestScore) {
    long long currentScore = scoreState(p, current);
    copyState(p, best, current);
    bestScore = currentScore;

    for (int iter = 0; iter < ITERATION_LIMIT; ++iter) {
        Move mv = makeRandomMove(p, current);
        applyMove(p, current, mv);

        long long nextScore = scoreState(p, current);

        if (nextScore >= currentScore) {
            currentScore = nextScore;

            if (currentScore > bestScore) {
                copyState(p, best, current);
                bestScore = currentScore;
            }
        } else {
            rollbackMove(p, current, mv);
        }
    }
}
```

이 방식은 이해하기 쉽지만, 한 번 주변에서 더 좋은 답이 없어지면 멈추기 쉽습니다. 이것을 지역 최적이라고 부릅니다.

## 8. 나쁜 이동도 가끔 받아들이기

지역 최적을 벗어나려면 가끔은 점수가 조금 나빠지는 이동도 받아들여야 합니다. 대표적인 방법이 simulated annealing, 즉 담금질 기법입니다.

아이디어는 간단합니다.

- 초반에는 나쁜 이동도 어느 정도 받아들여 넓게 탐색합니다.
- 시간이 지날수록 점점 보수적으로 바뀝니다.
- 후반에는 거의 좋은 이동만 받아들여 답을 다듬습니다.

보통 담금질 설명에서는 나빠진 정도를 `loss = currentScore - nextScore`라고 두고 아래 확률로 이동을 받아들입니다.

```text
accept_probability = exp(-loss / temperature)
```

헤더를 쓸 수 있는 일반 C++ 환경이라면 이 식을 그대로 구현하는 것이 정석입니다.

```cpp
#include <cmath>

const int PROBABILITY_SCALE = 1 << 16;

int acceptMoveStandard(long long diff, double temperature) {
    if (diff >= 0) return 1;
    if (temperature <= 0.0) return 0;

    double probability = std::exp((double)diff / temperature);
    return randomInt(PROBABILITY_SCALE) < (int)(probability * PROBABILITY_SCALE);
}
```

여기서 `diff = nextScore - currentScore`이므로 나쁜 이동에서는 `diff`가 음수입니다. 따라서 `std::exp(diff / temperature)`는 `exp(-loss / temperature)`와 같습니다.

이 식에서 중요한 것은 그래프의 모양입니다. `loss / temperature`가 커질수록 채택 확률이 빠르게 작아져야 합니다. 다만 이 글의 나머지 예시는 일부 대회 환경처럼 `cmath`를 쓸 수 없다고 가정하므로, 실전 구현에서는 사람이 외우고 조정하기 쉬운 대체 규칙을 씁니다.

```text
accept_probability = 2^(-loss / temperature)
```

이 규칙에서는 손해가 온도만큼 커질 때마다 채택률이 절반이 됩니다. 원본 `exp(-x)`와 정확히 같은 숫자는 아니지만, 차이는 온도에 상수배를 곱해 어느 정도 흡수할 수 있습니다. 중요한 것은 상수를 맞추는 것이 아니라, 온도가 현재 move의 점수 손해 스케일과 맞아야 한다는 점입니다.

| `loss / temperature` | 원본 `exp(-x)` | 선형 보정 근사 | 보정 없음 |
| --- | --- | --- | --- |
| 0 | 100% | 100% | 100% |
| 0.5 | 61% | 75% | 100% |
| 1 | 37% | 50% | 50% |
| 1.5 | 22% | 37% | 50% |
| 2 | 14% | 25% | 25% |
| 3 | 5% | 12% | 12% |
| 5 | 1% 이하 | 3% | 3% |

![어닐링 채택 확률 비교](../lesson-assets/annealing-acceptance.svg)

헤더 없는 근사는 같은 온도에서는 더 넓게 움직입니다. 보정이 없으면 `0.5T`처럼 중간 손해도 이전 단계와 같은 확률로 받아들입니다. 선형 보정은 이 중간 구간을 완만하게 내려 주는 역할을 합니다. 전체적인 차이는 온도 스케일로 조정하면 됩니다. 같은 실제 채택률을 원하면 온도를 더 작게 잡으면 됩니다. 따라서 SA 튜닝의 핵심은 수식의 상수보다 `START_TEMP`, `END_TEMP`, 반복 횟수, move 크기입니다.

### 실전 구현: 헤더 없이 쓰는 근사

확률 눈금은 `PROBABILITY_SCALE = 1 << 16`으로 둡니다. `threshold`는 이 눈금 안에서 채택 기준을 나타내고, 마지막에는 `randomInt(PROBABILITY_SCALE)`와 비교합니다.

구현은 두 단계입니다. 먼저 `loss`가 `temperature`를 한 번 넘을 때마다 확률을 절반으로 줄입니다. 마지막에 남은 `loss`는 현재 확률과 다음 절반 확률 사이를 선형으로 보정합니다.

```cpp
const int PROBABILITY_SCALE = 1 << 16;

int acceptMove(long long diff, long long temperature) {
    if (diff >= 0) return 1;
    if (temperature <= 0) return 0;

    long long loss = -diff;
    long long whole = loss / temperature;
    long long remain = loss % temperature;

    int highChance = PROBABILITY_SCALE;
    while (whole > 0 && highChance > 0) {
        highChance >>= 1;
        --whole;
    }

    if (highChance == 0) return 0;

    int lowChance = highChance >> 1;
    long long highWeight = temperature - remain;
    long long lowWeight = remain;

    // 더 정밀하게 쓰기 위해 highChance와 lowChance 사이를 선형으로 보정한다.
    int threshold = (int)(((long long)highChance * highWeight
        + (long long)lowChance * lowWeight) / temperature);

    return randomInt(PROBABILITY_SCALE) < threshold;
}
```

`remain == 0`이면 `highChance`를 그대로 쓰고, `remain`이 `temperature`에 가까워질수록 `lowChance`에 가까워집니다. 보정식을 빼면 더 단순하지만, `loss < temperature`인 모든 이동이 같은 확률로 처리됩니다. 이 한 줄을 넣으면 작은 손해와 큰 손해를 조금 더 자연스럽게 구분할 수 있습니다.

예를 들어 `loss == temperature`이면 약 50%만 받아들입니다. `loss == 3 * temperature`이면 확률을 세 번 절반으로 줄였으므로 약 12%만 받아들입니다. `loss`가 그 사이에 있으면 확률도 중간값으로 내려갑니다.

| `loss` | 채택률 |
| --- | --- |
| `0` | 약 100% |
| `temperature / 2` | 약 75% |
| `temperature` | 약 50% |
| `temperature + temperature / 2` | 약 37% |
| `2 * temperature` | 약 25% |
| `3 * temperature` | 약 12% |

### 온도는 어떻게 잡는가

점수 함수의 절댓값보다 더 중요한 값은 **나쁜 move 하나가 보통 얼마나 손해를 내는지**입니다. 초기 점수가 `-100000000`인지 `-5000`인지는 점수 설계에 따라 달라집니다. 반면 `작업 하나를 옮겼을 때 보통 3000점 정도 나빠진다`는 값은 온도를 정하는 데 직접 쓸 수 있습니다.

수렴 속도를 잘 모르는 상태에서는 먼저 현재 해 주변의 나쁜 move를 몇 번 샘플링합니다. 실제 상태는 되돌리면서 손해만 잽니다.

```cpp
long long estimateTypicalLoss(const Problem& p, State& state) {
    const int SAMPLE_COUNT = 512;
    long long baseScore = scoreState(p, state);
    long long lossSum = 0;
    int lossCount = 0;

    for (int i = 0; i < SAMPLE_COUNT; ++i) {
        Move mv = makeRandomMove(p, state);
        applyMove(p, state, mv);

        long long nextScore = scoreState(p, state);
        if (nextScore < baseScore) {
            lossSum += baseScore - nextScore;
            ++lossCount;
        }

        rollbackMove(p, state, mv);
    }

    if (lossCount == 0) return 1;

    long long typicalLoss = lossSum / lossCount;
    if (typicalLoss < 1) typicalLoss = 1;
    return typicalLoss;
}
```

그다음 시작 온도와 끝 온도를 이 손해 기준으로 잡습니다.

```cpp
long long startTemperatureFromLoss(long long typicalLoss) {
    return typicalLoss * 3;
}

long long endTemperatureFromLoss(long long typicalLoss) {
    long long value = typicalLoss / 5;
    return value > 0 ? value : 1;
}

long long temperatureAt(int iter, long long startTemp, long long endTemp) {
    long long left = ITERATION_LIMIT - iter;
    if (left < 0) left = 0;

    return endTemp + (startTemp - endTemp) * left / ITERATION_LIMIT;
}
```

이 값들은 정답이 아니라 출발점입니다.

| 값 | 처음 잡는 기준 | 의미 |
| --- | --- | --- |
| `typicalLoss` | 나쁜 move 손해의 평균 | 점수 변화의 기본 단위 |
| `START_TEMP` | `typicalLoss * 2`에서 `typicalLoss * 5` | 초반에 보통 손해를 자주 받아들임 |
| `END_TEMP` | `typicalLoss / 5`에서 `typicalLoss / 20` | 후반에 보통 손해를 거의 거절 |
| 반복 횟수 | 로컬 최악 입력에서 시간 여유를 두고 측정 | 환경 차이를 감안해 제한보다 짧게 |
| move 크기 | 후반에도 의미 있는 작은 변경 | 너무 큰 move만 있으면 수렴이 거칠어짐 |

초기 점수를 기준으로 온도를 잡을 수도 있지만, 그 경우에는 점수 함수가 안정적인 스케일을 가져야 합니다. 예를 들어 점수가 항상 `0`에서 `1,000,000` 사이이고 move 하나가 전체 점수의 작은 비율만 바꾸는 문제라면 `START_TEMP = initialScore / 1000` 같은 거친 출발점도 가능합니다. 하지만 일반적으로는 초기 점수보다 move 손해 샘플이 더 믿을 만합니다.

튜닝할 때는 채택률을 봅니다.

- 초반에도 나쁜 move를 거의 안 받으면 `START_TEMP`가 너무 낮습니다.
- 후반에도 답이 계속 크게 흔들리면 `END_TEMP`가 너무 높거나 move가 너무 큽니다.
- 초반 점수는 잘 흔들리는데 최고 점수가 안 오르면 move 종류가 부족할 수 있습니다.
- seed마다 편차가 크면 한 번 깊게 도는 것보다 여러 restart가 나을 수 있습니다.

```cpp
void improveByAnnealing(const Problem& p, State& current, State& best, long long& bestScore) {
    long long typicalLoss = estimateTypicalLoss(p, current);
    long long startTemp = startTemperatureFromLoss(typicalLoss);
    long long endTemp = endTemperatureFromLoss(typicalLoss);
    long long currentScore = scoreState(p, current);

    copyState(p, best, current);
    bestScore = currentScore;

    for (int iter = 0; iter < ITERATION_LIMIT; ++iter) {
        Move mv = makeRandomMove(p, current);
        applyMove(p, current, mv);

        long long nextScore = scoreState(p, current);
        long long diff = nextScore - currentScore;
        long long temp = temperatureAt(iter, startTemp, endTemp);

        if (acceptMove(diff, temp)) {
            currentScore = nextScore;

            if (currentScore > bestScore) {
                copyState(p, best, current);
                bestScore = currentScore;
            }
        } else {
            rollbackMove(p, current, mv);
        }
    }
}
```

이 정도로 시작한 뒤 입력 묶음별 점수와 초반/중반/후반 채택률을 보고 조정합니다. SA는 한 번에 맞히는 공식이라기보다, 점수 변화 스케일을 재고 그 스케일에 맞춰 온도를 움직이는 절차입니다.
