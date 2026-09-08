# Global Min Cut

Global Min Cut은 무향 가중 그래프에서 두 집합으로 정점을 나눌 때 끊기는 edge capacity 합의 최솟값을 찾는 문제입니다. 특정 두 정점 `s`, `t`를 분리하는 min cut이 아니라, 어떤 두 집합이든 허용하는 전체 graph connectivity의 최약 지점을 찾습니다.

## 문제 신호

| 문제 표현 | Global Min Cut 관점 |
| --- | --- |
| 네트워크를 둘로 끊는 최소 비용 | global cut |
| 임의 두 정점이 분리되면 됨 | `s-t`가 고정되지 않음 |
| edge connectivity를 전체 그래프에서 묻는다 | minimum cut value |
| 무향 capacity graph | Stoer-Wagner 후보 |
| 모든 쌍 min cut 값도 필요 | Gomory-Hu Tree 후보 |

global min cut은 "가장 약한 분리"입니다. 특정 source와 sink가 주어진 max-flow 문제와 목적이 다릅니다.

## Cut Value

정점 집합 `A`와 나머지 `V-A` 사이를 잇는 edge weight 합을 cut value라고 합니다.

```text
cut(A) = sum weight(u, v)
where u in A, v not in A
```

빈 집합과 전체 집합은 cut으로 보지 않습니다. 그래프가 이미 disconnected이면 global min cut 값은 0입니다.

## Stoer-Wagner 개요

Stoer-Wagner는 매 phase마다 아직 contraction되지 않은 정점 중 하나를 마지막까지 키워 가며 minimum `s-t` cut 후보를 얻습니다.

```text
phase:
  A = empty
  가장 많이 A와 연결된 정점을 반복해서 추가
  마지막으로 추가된 t와 그 직전 s의 cut weight가 후보
  s와 t를 contract
```

이 과정을 정점이 하나 남을 때까지 반복하면 전체 global min cut 후보가 모두 고려됩니다.

## 구현

아래 구현은 정점 수가 중간 이하이고 adjacency matrix를 둘 수 있는 경우에 쓰는 `O(N^3)` Stoer-Wagner입니다. 입력에서 parallel edge가 있으면 matrix에 더해서 넣습니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

long long stoerWagnerMinCut(vector<vector<long long>> weight) {
    int n = (int)weight.size();
    if (n <= 1) {
        return 0;
    }

    const long long INF = (1LL << 60);
    long long best = INF;
    vector<int> vertex(n);
    for (int i = 0; i < n; ++i) {
        vertex[i] = i;
    }

    for (int active = n; active > 1; --active) {
        vector<long long> connection(active, 0);
        vector<int> used(active, 0);
        int previous = -1;
        int selected = -1;

        for (int step = 0; step < active; ++step) {
            selected = -1;
            for (int i = 0; i < active; ++i) {
                if (!used[i] && (selected == -1 || connection[i] > connection[selected])) {
                    selected = i;
                }
            }

            if (step == active - 1) {
                best = min(best, connection[selected]);

                int s = vertex[previous];
                int t = vertex[selected];
                for (int i = 0; i < active; ++i) {
                    if (i == selected) {
                        continue;
                    }
                    int v = vertex[i];
                    weight[s][v] += weight[t][v];
                    weight[v][s] = weight[s][v];
                }
                vertex.erase(vertex.begin() + selected);
                break;
            }

            used[selected] = 1;
            previous = selected;
            for (int i = 0; i < active; ++i) {
                if (!used[i]) {
                    connection[i] += weight[vertex[selected]][vertex[i]];
                }
            }
        }
    }

    return best;
}
```

`previous`는 마지막으로 추가된 정점 직전의 정점입니다. phase의 마지막 정점을 그 직전 정점에 contract하면서 다음 phase로 넘어갑니다.

## Max-Flow 반복과 비교

| 접근 | 특징 |
| --- | --- |
| 모든 `s-t` max-flow 반복 | 단순하지만 너무 느림 |
| Stoer-Wagner | 무향 global min cut에 특화 |
| Gomory-Hu Tree | 모든 쌍 min cut 질의까지 처리 |
| Karger contraction | randomized, 구현은 간단하지만 확률 분석 필요 |

global min cut 값만 필요하면 Stoer-Wagner가 가장 직접적입니다. 질의가 많으면 Gomory-Hu Tree로 cut-equivalent tree를 만드는 편이 낫습니다.

## 입력 모델

무향 edge `(u, v, w)`는 양방향 matrix에 같은 값을 더합니다.

```text
weight[u][v] += w
weight[v][u] += w
```

self-loop는 cut을 가로지르지 않으므로 무시합니다. capacity가 0인 edge는 있어도 값에 영향을 주지 않습니다.

## 시간 복잡도

| 항목 | 복잡도 |
| --- | ---: |
| adjacency matrix Stoer-Wagner | `O(N^3)` |
| 메모리 | `O(N^2)` |
| disconnected graph 판정 포함 | 자연스럽게 0 후보 발생 |
| 모든 쌍 min cut 질의 | 별도 구조 필요 |

`N`이 수천 이상이면 matrix 방식은 어렵습니다. 문제 제한을 보고 sparse graph 전용 구현이나 다른 접근을 검토합니다.

## 자주 하는 실수

1. 방향 그래프에 Stoer-Wagner를 적용한다.
2. global min cut과 특정 `s-t` min cut을 혼동한다.
3. parallel edge를 덮어쓰고 합치지 않는다.
4. contract 후 matrix를 대칭으로 갱신하지 않는다.
5. disconnected graph의 답 0을 예외로 잘못 처리한다.
