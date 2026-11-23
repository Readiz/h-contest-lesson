# 적용 사례: ORDERING에 SA 붙이기

[배송 순서 개선](ordering-route-improvement.md)의 가장 가까운 점 잇기 + 2-opt 초기해에 SA(담금질)를 붙이고 같은 입력에서 단계별로 측정합니다. 원리는 [언덕 오르기와 담금질](https://h.readiz.com/learn/hill-climbing-and-annealing)에서 다룹니다.

## ORDERING에 붙이는 구현

먼저 [배송 순서 개선](ordering-route-improvement.md)의 완성 코드를 복사하고, 그 코드의 `build_path` 이름만 `build_initial_path`로 바꿉니다. 그러면 같은 초기해를 여러 탐색 방식에서 재사용할 수 있습니다. [공통 코드의 `random` 블록](https://h.readiz.com/learn/cpp-common-library)도 한 번 붙인 뒤 아래 코드를 추가합니다.

이 구현은 최소화 문제에서 `loss = 새 비용 - 현재 비용`이 0 이하이면 채택하고, 양수이면 확률 `exp(-loss / T)`로 채택합니다.

> **코드 환경: h-contest 제출 확장용.** 표준 헤더·STL 없이 공개 거리 API만 사용합니다. `1 <= n <= 100`, 유효한 초기 순열, `attempts >= 0`, 유한한 `startTemperature >= endTemperature >= 0`을 전제로 합니다. `order[]`에는 최선해를 보존하고 작업 배열 `current[]`만 흔듭니다.

```cpp snippet=ordering-sa
namespace ordering_sa {
struct Stats {
    int bestCost;
    int currentCost;
    int accepted;
    int acceptedWorse;
};

// x >= 0. No math header: reduce x, evaluate a short series, then square.
double expNegative(double x) {
    if (x >= 32.0) return 0.0;
    int halves = 0;
    while (x > 0.5) { x *= 0.5; ++halves; }
    double sum = 1.0, term = 1.0;
    for (int k = 1; k <= 12; ++k) {
        term *= -x / k;
        sum += term;
    }
    for (int k = 0; k < halves; ++k) sum *= sum;
    return sum;
}

int delta(int n, const int order[], int left, int right) {
    int a = order[left - 1], b = order[left], c = order[right];
    int change = get_dist(a, c) - get_dist(a, b);
    if (right + 1 < n) {
        int d = order[right + 1];
        change += get_dist(b, d) - get_dist(c, d);
    }
    return change;
}

Stats improve(int n, int order[], int attempts, unsigned seed,
              double startTemperature, double endTemperature) {
    int current[100];
    for (int i = 0; i < n; ++i) current[i] = order[i];
    int initialCost = get_path_dist(order, n);
    Stats stats = {initialCost, initialCost, 0, 0};
    if (n <= 2 || attempts == 0) return stats;

    hc::Random rng;
    rng.reset(seed);
    for (int step = 0; step < attempts; ++step) {
        int left = 1 + (int)rng.below((unsigned)(n - 1));
        int right = 1 + (int)rng.below((unsigned)(n - 2));
        if (right >= left) ++right;
        if (left > right) { int temp = left; left = right; right = temp; }

        double progress = attempts == 1 ? 0.0 : (double)step / (attempts - 1);
        double temperature = startTemperature
                           + (endTemperature - startTemperature) * progress;
        int change = delta(n, current, left, right);
        // Consume one draw on every proposal, including improvements.
        double u = (rng.next() >> 8) / 16777216.0;
        bool accept = change <= 0;
        if (!accept && temperature > 0.0) {
            accept = u < expNegative(change / temperature);
        }
        if (!accept) continue;

        reverse_range(current, left, right);
        stats.currentCost += change;
        ++stats.accepted;
        if (change > 0) ++stats.acceptedWorse;
        if (stats.currentCost < stats.bestCost) {
            stats.bestCost = stats.currentCost;
            for (int i = 0; i < n; ++i) order[i] = current[i];
        }
    }
    return stats;
}
}
```

`expNegative`는 표준 헤더 없이 쓰는 `exp(-x)` 근사입니다. 구현 세부는 아래에 접어 두었습니다.

:::hint expNegative와 난수 u의 정밀도
`x`를 0.5 이하로 줄여 12차 Taylor 합을 구하고 제곱해 되돌립니다. `x >= 32`에서는 0을 반환하며, 생략한 함수값은 `exp(-32) ≈ 1.27×10^-14` 이하입니다. 난수 `u`도 24비트 격자의 값이므로 수식의 연속 확률을 유한 정밀도로 구현한 것입니다. 로컬에서는 `<cmath>`의 `exp(-x)`와 비교하지만 그 헤더는 제출 코드에 넣지 않습니다.
:::

다음 wrapper가 실제 제출 함수입니다. 모든 TC에서 풀이 난수를 다시 초기화하며 채점기 난수나 비공개 상태를 읽지 않습니다.

```cpp snippet=ordering-sa-entry
void build_path(int n, const int points[][2], int order[]) {
    build_initial_path(n, points, order);
    ordering_sa::improve(n, order, 30000, 20260922u, 128.0, 1.0);
}
```

온도는 시도 횟수에 따라 128에서 1까지 선형으로 낮춥니다. 이 상수들은 비교를 시작하기 위한 설정입니다. 0과 0을 넣으면 같은 후보 생성·난수 소비 규칙에서 좋은 이동과 같은 비용의 이동만 받는 hill climbing이 됩니다. 둘의 난수열을 같게 해도 현재 경로가 달라진 뒤의 비용 변화까지 같아지는 것은 아닙니다.

거절한 이동은 배열을 바꾸기 전에 판정하므로 되돌리기가 필요 없습니다. 후보를 먼저 적용해 점수를 재는 방식으로 고친다면 거절 분기에서 반드시 복구해야 합니다. `delta`는 [Testing과 Stress Test](https://h.readiz.com/learn/testing-and-stress)의 전체 비용 재계산과 비교합니다.

## 같은 입력에서 단계별로 측정하기

아래는 2026-09-22에 공개 ORDERING 채점기의 10개 TC를 그대로 실행한 결과입니다. 각 방식은 9번 실행하고 첫 실행을 제외한 8번의 중앙값을 사용했습니다. 시간은 초기해 구성·탐색·채점기 실행을 포함한 **10개 TC 전체 시간**이며, macOS arm64 / Apple clang 17 / C++17에서 측정했습니다.

| 방식 | 10개 TC 비용 합 ↓ | `-O0` 시간(ms) | `-O2` 시간(ms) |
| --- | ---: | ---: | ---: |
| 번호 순서 | 257071 | 0.033 | 0.003 |
| nearest neighbor | 65145 | 0.606 | 0.120 |
| nearest neighbor + 2-opt | 58368 | 4.013 | 0.856 |
| 같은 초기해 + hill climbing | 58368 | 19.634 | 4.980 |
| 같은 초기해 + SA | 56779 | 37.674 | 9.993 |

모든 실행은 유효한 경로를 제출했고, 최적화 옵션에 따른 비용 차이는 없었습니다. 마지막 두 방식은 위 wrapper의 solver seed와 **TC당 추가 후보 30000개**를 맞춘 비교입니다. hill climbing은 이미 2-opt가 멈춘 경로에서 시작해 한 TC도 개선하지 못했습니다(비용이 2-opt와 같습니다). SA는 비용 합을 약 2.7% 낮췄고, 시간은 hill climbing의 약 1.9~2.0배였습니다. **같은 실행 시간에서 SA가 더 좋다는 실험은 아닙니다.** 가장 큰 네 TC의 비용은 두 방식에서 같았습니다.

한 채점 입력 묶음과 한 seed의 기록이므로 일반적인 우열이나 최적 온도로 해석하지 않습니다. 일반화하려면 입력 크기·분포와 seed를 바꾸고 같은 시간에 돌릴 수 있는 후보 수를 따로 맞춰야 합니다. 절대 시간은 기기와 부하에 따라 달라지며, 특히 매우 짧은 기준선 시간은 정밀한 성능 비교에 쓰기 어렵습니다.

:::hint 측정 원본과 재현 방법
[TC별 비용과 측정 원본](https://git.readiz.com/h-contest-lesson/lessons/heuristic-case-studies/lesson-assets/ordering-search-benchmark.json)에는 채점기 파일의 SHA-256과 개별 측정값도 담았습니다. 저장소에서 공개 채점기의 `main.cpp` 경로를 지정하면 같은 본문 코드를 추출해 재현할 수 있습니다. 명령은 `python3 scripts/check_heuristic_search.py --judge /path/to/ORDERING/main.cpp --output /tmp/ordering-bench.json`입니다.
:::

## 로컬 연습: 같은 초기해에서 탐색 비교

입력은 `N`과 `N`개의 정수 좌표이며 `1 <= N <= 100`, 좌표는 `0..999`입니다. 첫 점이 창고입니다. 위 표처럼 번호 순서, nearest neighbor, nearest neighbor + 2-opt, 여기에 hill climbing 또는 SA를 추가한 다섯 방식의 유효성·비용·실행 시간을 같은 입력에서 기록합니다. 두 추가 탐색은 각각 후보 30000개와 solver seed `20260922`를 사용합니다.

작은 고정 입력으로 맨해튼 거리의 여섯 점 `0=(18,8), 1=(17,4), 2=(18,12), 3=(9,4), 4=(2,12), 5=(12,19)`(창고는 0, 마지막 점에서 돌아오지 않음)를 넣고, 경로 `0 1 3 4 2 5`의 비용 57과 열 가지 2-opt 이웃의 비용이 모두 57보다 큼을 먼저 확인합니다. 이어 `[1,3]`, `[1,4]` 구간을 차례로 뒤집으면 비용은 65, 53이 되어, 한 번 나빠진 뒤 더 좋아지는 경로가 됩니다. `N=6`에서는 창고를 제외한 `5!=120`개 순열을 전수 조사해 최적 비용 53도 확인할 수 있습니다.

자동 탐색이 매 실행에서 53을 찾는 것을 정답 조건으로 삼지 않습니다. 항상 검사할 조건은 유효한 순열, 시작점 0, 같은 seed의 재현성, 제출된 경로 비용과 `bestCost`의 일치, 최선 비용이 초기해보다 나빠지지 않음입니다. `attempts=0`, `N=1,2`, 중복 좌표, 같은 비용 이동, 경로 끝을 뒤집는 이동도 검사합니다.

같은 SA를 다른 문제에 붙인 예는 [배정 문제의 지역 탐색과 SA](https://h.readiz.com/learn/assignment-local-search)에 있습니다. SCHEDULX의 최대 부하 점수에서 시작 온도와 수락률을 측정합니다.
