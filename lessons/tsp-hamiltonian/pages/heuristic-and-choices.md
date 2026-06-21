# TSP와 해밀턴 경로: 휴리스틱 개선과 선택 기준

## 9. 더 큰 입력: 정확한 최적해를 포기하는 순간

`n = 30`만 되어도 `2^n` DP는 현실적으로 어렵습니다. 이때 문제의 목표가 "정확한 최적 비용"인지, "제한 시간 안에 좋은 경로"인지 확인해야 합니다.

휴리스틱 TSP 풀이의 기본 구조는 보통 아래와 같습니다.

```text
1. 빠른 초기 경로를 만든다.
2. 경로를 조금 바꿔 더 좋아지는지 본다.
3. 좋아지면 반영한다.
4. 제한 시간까지 반복한다.
```

정확한 알고리즘과 달리, 휴리스틱은 최적해를 보장하지 않습니다. 대신 입력이 커도 실행할 수 있고, 실험으로 품질을 끌어올릴 수 있습니다.

## 10. Nearest Neighbor 초기해

가장 쉬운 초기해는 현재 정점에서 아직 방문하지 않은 정점 중 가장 가까운 곳으로 가는 방식입니다.

```cpp
vector<int> nearestNeighborRoute(int n, const vector<vector<long long>>& cost) {
    vector<int> route;
    vector<char> used(n, false);

    int current = 0;
    route.push_back(current);
    used[current] = true;

    for (int step = 1; step < n; ++step) {
        int best = -1;
        for (int next = 0; next < n; ++next) {
            if (used[next]) continue;
            if (cost[current][next] == INF) continue;

            if (best == -1 || cost[current][next] < cost[current][best]) {
                best = next;
            }
        }

        if (best == -1) {
            return {}; // 더 이상 갈 수 있는 미방문 정점이 없음
        }

        current = best;
        route.push_back(current);
        used[current] = true;
    }

    if (cost[current][0] == INF) {
        return {}; // 시작점으로 돌아올 수 없음
    }

    route.push_back(0);
    return route;
}
```

빈 `vector`가 반환되면 nearest neighbor 방식으로는 유효한 tour를 만들지 못했다는 뜻입니다. 완전 그래프가 아닌 TSP에서는 초기해 생성 단계에서도 없는 간선을 반드시 건너뛰어야 합니다.

이 방법은 빠르고 구현이 쉽지만, 눈앞의 가까운 정점을 고르다가 나중에 비싼 간선을 강제로 탈 수 있습니다. 그래서 초기해로 쓰고, 이후 개선을 붙이는 편이 좋습니다.

## 11. 2-opt 지역 탐색

TSP에서 가장 유명한 개선 연산 중 하나가 2-opt입니다. 경로의 간선 두 개를 끊고, 가운데 구간을 뒤집어 다시 연결합니다.

![2-opt가 교차 간선을 줄이는 모습](../lesson-assets/two-opt-improvement.svg)

경로가 `... a - b ... c - d ...` 형태일 때, `a-b`, `c-d`를 끊고 `a-c`, `b-d`로 바꿉니다. 가운데 구간 `b ... c`는 뒤집힙니다.

```cpp
long long delta =
    cost[a][c] + cost[b][d]
    - cost[a][b] - cost[c][d];

if (delta < 0) {
    reverse(route.begin() + i, route.begin() + j + 1);
}
```

완전한 형태는 다음과 같습니다. `route`는 마지막에 시작점 `0`이 한 번 더 들어 있는 사이클 표현이라고 가정합니다.

```cpp
bool improve2Opt(vector<int>& route, const vector<vector<long long>>& cost) {
    int m = (int)route.size();

    for (int i = 1; i + 2 < m; ++i) {
        for (int j = i + 1; j + 1 < m; ++j) {
            int a = route[i - 1];
            int b = route[i];
            int c = route[j];
            int d = route[j + 1];

            long long before = cost[a][b] + cost[c][d];
            long long after = cost[a][c] + cost[b][d];

            if (after < before) {
                reverse(route.begin() + i, route.begin() + j + 1);
                return true;
            }
        }
    }

    return false;
}

while (improve2Opt(route, cost)) {
    // 더 이상 좋아지는 2-opt 이동이 없을 때까지 반복
}
```

이 구현은 첫 번째 개선을 바로 반영하는 방식입니다. 모든 후보를 훑어 가장 큰 개선을 고르는 방식도 가능합니다. 전자는 빠르게 움직이고, 후자는 한 번의 반복 품질이 좋을 수 있습니다.

## 12. 지역 최적을 벗어나기

2-opt만 반복하면 더 이상 좋아지는 2-opt 이동이 없는 상태, 즉 지역 최적에 멈춥니다. 이를 벗어나려면 아래 전략을 섞습니다.

- 시작점을 바꾸거나 random seed를 바꿔 여러 초기해를 만듭니다.
- 가끔은 점수가 나빠지는 이동도 받아들입니다.
- 2-opt뿐 아니라 swap, insert, 3-opt 같은 다른 이동을 섞습니다.
- 큰 구간을 무작위로 흔든 뒤 다시 2-opt로 정리합니다.

담금질 기법을 쓰면 나쁜 이동을 확률적으로 받아들일 수 있습니다.

```cpp
double progress = elapsedTime() / timeLimit;
double temperature = startTemp * pow(endTemp / startTemp, progress);

long long diff = nextScore - currentScore; // 비용 최소화라면 작을수록 좋다
bool accept = false;

if (diff <= 0) {
    accept = true;
} else {
    double probability = exp(-(double)diff / temperature);
    accept = random01() < probability;
}
```

최대화 문제에서는 부호가 반대로 바뀝니다. TSP는 보통 비용 최소화이므로 `diff <= 0`이면 좋은 이동입니다.

## 13. Metric TSP와 보장 있는 근사

모든 간선 비용이 삼각 부등식 `dist[a][c] <= dist[a][b] + dist[b][c]`를 만족하면 Metric TSP라고 부릅니다. 좌표 평면의 유클리드 거리 TSP가 대표적입니다.

이 조건이 있으면 MST를 두 번 따라가는 방식으로 최적해의 2배 이하 경로를 만들 수 있습니다.

```text
1. 모든 정점의 MST를 만든다.
2. MST 간선을 두 번씩 지나 Euler tour를 만든다.
3. 이미 방문한 정점을 건너뛰며 TSP tour로 줄인다.
```

이것은 단순 휴리스틱보다 강한 "근사 보장"이 있는 접근입니다. 다만 삼각 부등식이 없으면 건너뛰기가 비용을 줄인다는 보장이 깨집니다. 문제에서 비용 구조가 무엇인지 먼저 확인해야 합니다.

## 14. 자주 나오는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 경로와 사이클을 혼동함 | 마지막 복귀 비용을 빼거나 더함 | 문제 문장에 "돌아온다", "순회"가 있는지 확인 |
| 시작점을 여러 번 세거나 빠뜨림 | 순열/DP 초기값 오류 | TSP cycle은 보통 `0`을 고정 |
| 없는 간선을 0으로 둠 | 불가능한 경로가 최적해가 됨 | 없는 간선은 `INF` |
| `1 << n` overflow | `n >= 31`에서 잘못된 mask | `1LL << n` 또는 제한 확인 |
| `INF + cost` overflow | 음수처럼 wrap됨 | `dp == INF` 상태는 전이하지 않음 |
| parent 복원 순서 오류 | 경로가 뒤섞임 | 현재 정점 비트를 제거한 뒤 parent로 이동 |
| 휴리스틱을 정답 보장처럼 믿음 | 숨은 케이스에서 큰 오차 | brute force/DP 가능한 작은 입력으로 품질 비교 |

## 15. 문제를 볼 때의 선택 순서

TSP나 해밀턴 경로처럼 보이는 문제를 만나면 아래 순서로 판단합니다.

1. 모든 정점을 한 번씩 방문해야 하는가?
2. 존재 여부인가, 최소/최대 비용인가?
3. 다시 시작점으로 돌아와야 하는가?
4. `n`이 완전탐색, 비트마스크 DP, 휴리스틱 중 어디에 맞는가?
5. 간선이 없는 경우가 있는가, 비용이 대칭인가, 삼각 부등식이 있는가?
6. 실제 경로 출력이 필요한가, 비용만 필요한가?

정리하면, 해밀턴 경로와 TSP는 "방문 집합 + 마지막 정점"이라는 상태를 배우기에 좋은 문제입니다. 작은 입력에서는 완전탐색으로 정답을 만들고, 중간 크기에서는 비트마스크 DP로 중복을 줄이고, 큰 입력에서는 좋은 초기해와 지역 탐색으로 제한 시간 안의 답을 개선합니다.

## 16. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 작은 해밀턴 경로 완전탐색 문제 추가 | 순열 탐색과 pruning 기준 확인 | permutation, pruning |
| 표준 | [맨해튼 해밀턴 경로](/practice/HAMPATHX) | 시작점 고정 경로를 만들고 거리 합 줄이기 | Hamiltonian path |
| 응용 | [맨해튼 TSP](/practice/TSPTESTX) | 순회 비용과 마지막 복귀 비용을 함께 최적화 | TSP cycle, 2-opt |
| 함정 | TODO: 비트마스크 TSP DP 문제 추가 | `mask`, `last`, 경로 복원과 메모리 확인 | Held-Karp |
