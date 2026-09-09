# Global Min Cut

Global Min Cut은 무향 가중 그래프에서 두 집합으로 정점을 나눌 때 끊기는 edge capacity 합의 최솟값을 찾는 문제입니다. 특정 두 정점 `s`, `t`를 분리하는 min cut이 아니라, 어떤 두 집합이든 허용하는 전체 graph connectivity의 최약 지점을 찾습니다.


입력은 비음수 대칭 용량 행렬이며 self-loop를 제외합니다. 모든 용량 합은 INF 미만이어야 합니다. n<=1의 반환 0은 코드의 관례이며 비자명한 cut이 존재한다는 뜻은 아닙니다. 고정 root와 나머지 정점 간 N-1번 min-cut의 최솟값으로도 global cut을 구할 수 있습니다.

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

## 최소 cut 한쪽 집합 복원

각 active vertex에 원래 정점 목록 group[v]를 둡니다. phase의 마지막 t가 답을 갱신하면 group[t]를 저장합니다. s,t를 합칠 때 group[t]를 group[s]에 이어 붙입니다. 이 방법은 최소 cut 하나를 복원하며 모든 최소 cut family를 나열하지는 않습니다.

## 간선 용량의 민감도

간선 e의 용량을 늘려 global cut 값이 엄격히 증가하려면 e가 모든 기존 global minimum cut을 가로질러야 합니다. 일부 최소 cut만 가로지르면 다른 최소 cut이 그대로 남습니다. 반대로 양의 용량을 조금 줄일 때 e를 가로지르는 최소 cut 하나가 있으면 그 cut 값이 감소합니다. “어떤 최소 cut에 포함”과 “모든 최소 cut에 포함”을 구분합니다.

## Trace: Stoer-Wagner 한 phase

아래 무향 weighted graph를 봅니다.

```text
0-1: 3
0-2: 1
0-3: 2
1-2: 4
1-3: 1
2-3: 2
```

첫 phase에서 시작 정점을 `0`으로 잡으면 selected set `A`는 아래처럼 커집니다.

| 단계 | `A` | 남은 정점의 연결 weight | 다음 선택 |
| --- | --- | --- | --- |
| 시작 | `{0}` | `w(1)=3`, `w(2)=1`, `w(3)=2` | `1` |
| 1 선택 후 | `{0,1}` | `w(2)=1+4=5`, `w(3)=2+1=3` | `2` |
| 2 선택 후 | `{0,1,2}` | `w(3)=2+1+2=5` | `3` |

마지막으로 선택된 정점은 `t=3`, 그 직전 정점은 `s=2`입니다. 이 phase가 주는 candidate cut은 `{3}`과 나머지를 가르는 cut이고 값은 `5`입니다.

```text
cut({3}) = capacity(3-0) + capacity(3-1) + capacity(3-2)
         = 2 + 1 + 2
         = 5
```

그다음 Stoer-Wagner는 `s=2`와 `t=3`을 merge합니다. 전체 알고리즘은 이런 phase를 정점이 하나 남을 때까지 반복하고, 각 phase의 candidate cut 최솟값을 답으로 둡니다.

## 로컬 연습: Stoer-Wagner Global Min Cut

### 입력

무향 weighted graph가 주어집니다. 전체 global min cut 값을 구합니다.

```text
N M
u1 v1 w1
...
uM vM wM
```

multi-edge가 들어오면 capacity를 더합니다. self-loop는 무시합니다.

### 출력

global min cut 값을 한 줄에 출력합니다. 그래프가 disconnected이면 답은 `0`입니다.

### 제한

- `2 <= N <= 500`
- `0 <= M <= 5000`
- `0 <= u, v < N`
- `1 <= w <= 10^9`

### 예시

```text
4 6
0 1 3
0 2 1
0 3 2
1 2 4
1 3 1
2 3 2
```

```text
5
```

### 풀이 기준

1. `long long` adjacency matrix에 undirected capacity를 누적한다.
2. active vertex list를 유지한다.
3. phase마다 아직 선택되지 않은 vertex 중 `A`와의 연결 weight가 최대인 vertex를 고른다.
4. phase의 마지막 vertex `t`가 만드는 candidate cut weight를 답 후보로 갱신한다.
5. 마지막 직전 vertex `s`와 `t`를 merge한다.
6. `t`를 active list에서 제거하고 다음 phase로 간다.

partition 복원까지 연습하려면 각 active vertex가 대표하는 원래 정점 목록도 같이 merge합니다. phase candidate가 최솟값을 갱신할 때 `t`의 그룹을 저장하면 됩니다.

### Stress 검증

작은 입력에서는 모든 non-empty proper subset을 열거해 cut 값을 계산하는 baseline과 비교합니다.

```text
for seed in 1..1000:
    random undirected weighted graph with N <= 12
    answer_stoer_wagner = O(N^3) implementation
    answer_bruteforce = min cut over all subsets
    assert answer_stoer_wagner == answer_bruteforce
```

반드시 포함할 case는 disconnected graph, multi-edge, 한 정점만 약하게 연결된 graph입니다.
