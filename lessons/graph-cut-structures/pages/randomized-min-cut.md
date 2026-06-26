# Randomized Min Cut

Randomized Min Cut은 Karger contraction처럼 무작위 edge 수축을 반복해 무향 그래프의 global min cut을 찾는 그래프 레슨입니다. Stoer-Wagner가 결정적 알고리즘이라면, Karger 계열은 구현이 짧고 확률 증폭으로 성공률을 높이는 randomized 접근입니다.

이 레슨은 Global Min Cut, Cut Sparsification, Global Min Cut Applications 이후에 보는 그래프 심화입니다.

1. 무작위 contraction이 min cut edge를 피하면 정답 cut이 보존된다.
2. 한 번의 성공 확률은 낮지만 반복하면 실패 확률을 줄일 수 있다.
3. randomized 알고리즘은 seed, 반복 횟수, 검증 가능한 fallback을 함께 설계한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: undirected cut, contraction, DSU, probability amplification
- 함께 보면 좋은 레슨: Global Min Cut, Cut Sparsification, Cactus Representation
- 다음에 볼 레슨: randomized graph algorithms, cut sparsification applications

## 1. 문제 신호

| 문제 표현 | Randomized Min Cut 관점 |
| --- | --- |
| 무향 global min cut을 빠르게 추정 | Karger contraction |
| 구현은 단순해도 확률 허용 | randomized repeated trial |
| 그래프가 작고 여러 번 돌릴 수 있음 | contraction Monte Carlo |
| 정답 검증이 어렵지 않음 | best cut value 반복 갱신 |
| 결정적 보장이 필요 | Stoer-Wagner 또는 Gomory-Hu Tree |

대회 문제는 보통 결정적 정답을 요구합니다. randomized 풀이를 쓸 때는 성공 확률을 충분히 키우거나 결정적 알고리즘이 더 적절한지 먼저 비교합니다.

## 2. Karger Contraction

Karger의 기본 알고리즘은 정점이 2개 남을 때까지 임의 edge를 고르고 양 끝을 contract합니다. 마지막 두 supernode 사이 edge 수가 cut value입니다.

```text
while number of components > 2:
  pick a random edge (u, v)
  if u and v are already in the same component, skip
  contract u and v

answer = edges crossing the two remaining components
```

min cut의 edge를 한 번도 contract하지 않으면 마지막 cut이 원래 min cut과 같습니다.

## 3. 왜 성공하는가

global min cut value를 `lambda`라고 합시다. 현재 정점 수가 `k`일 때 모든 정점의 degree는 적어도 `lambda`입니다. 따라서 edge 수는 적어도 `k * lambda / 2`입니다.

min cut edge를 고를 확률은 최대 아래와 같습니다.

```text
lambda / (k * lambda / 2) = 2 / k
```

따라서 그 phase에서 min cut edge를 피할 확률은 적어도 `1 - 2/k`입니다. 이를 `k = n, n-1, ..., 3`에 대해 곱하면 한 trial 성공 확률은 대략 `2 / (n(n-1))`입니다.

## 4. 기본 구현

아래 코드는 edge list와 DSU로 한 trial의 cut value를 계산합니다. 같은 seed로 재현 가능한 테스트를 만들기 위해 난수 엔진을 인자로 받습니다.

```cpp compile-check
#include <algorithm>
#include <numeric>
#include <random>
#include <vector>
using namespace std;

struct KargerDsu {
    vector<int> parent;
    vector<int> size;

    explicit KargerDsu(int n) : parent(n), size(n, 1) {
        iota(parent.begin(), parent.end(), 0);
    }

    int find(int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }

    bool unite(int a, int b) {
        a = find(a);
        b = find(b);
        if (a == b) {
            return false;
        }
        if (size[a] < size[b]) {
            swap(a, b);
        }
        parent[b] = a;
        size[a] += size[b];
        return true;
    }
};

struct KargerEdge {
    int u = 0;
    int v = 0;
};

int kargerTrial(int n, const vector<KargerEdge>& edges, mt19937& rng) {
    KargerDsu dsu(n);
    int components = n;
    uniform_int_distribution<int> pick(0, (int)edges.size() - 1);

    while (components > 2) {
        const KargerEdge& edge = edges[pick(rng)];
        if (dsu.unite(edge.u, edge.v)) {
            --components;
        }
    }

    int cut = 0;
    for (const KargerEdge& edge : edges) {
        if (dsu.find(edge.u) != dsu.find(edge.v)) {
            ++cut;
        }
    }
    return cut;
}
```

이 구현은 unweighted multigraph 기준입니다. weighted graph는 edge를 weight만큼 복제하면 너무 커질 수 있으므로 별도 sampling 또는 결정적 알고리즘을 고려합니다.

## 5. 반복 횟수와 확률 증폭

한 trial 성공 확률이 `p`일 때 `t`번 반복해서 모두 실패할 확률은 `(1-p)^t`입니다.

```text
p >= 2 / (n(n-1))
t = O(n^2 log n) 이면 실패 확률을 다항식 수준으로 낮출 수 있다.
```

실전에서는 제한 시간 안에서 가능한 반복 횟수를 잡고, 작은 그래프에서는 Stoer-Wagner 결과와 비교해 테스트합니다.

## 6. Karger-Stein 관점

Karger-Stein은 정점이 `n / sqrt(2)` 정도 남을 때까지만 contraction하고 두 recursive branch를 돌립니다. 기본 Karger보다 성공 확률을 끌어올립니다.

```text
contract to ceil(n / sqrt(2))
answer = min(recurse(copy1), recurse(copy2))
```

구현은 기본 Karger보다 복잡합니다. 문제 제한이 빡빡하고 randomized 풀이가 의도된 경우에만 고려합니다.

## 7. 작은 예시

```text
cycle 4개 정점: 0-1-2-3-0
global min cut = 2

edge 0-1을 contract하면 triangle-like multigraph가 된다.
min cut의 두 edge를 모두 피하는 contraction 순서라면 마지막 crossing edge 수는 2다.
min cut edge를 수축하면 그 cut 후보는 사라진다.
```

contraction은 graph를 단순화하지만 모든 cut을 보존하지는 않습니다. 정답 cut을 건드리지 않는 순서가 성공 조건입니다.

## 8. 결정적 알고리즘과 비교

| 접근 | 장점 | 주의 |
| --- | --- | --- |
| Stoer-Wagner | 결정적, weighted 가능 | `O(N^3)`와 matrix 메모리 |
| Karger | 구현 짧음, multigraph 자연스러움 | 반복 횟수와 확률 |
| Karger-Stein | 성공 확률 개선 | 구현 복잡 |
| Gomory-Hu Tree | pair cut query 가능 | 여러 max-flow 필요 |

정답 보장이 필요한 문제에서는 Stoer-Wagner를 먼저 검토합니다. Karger는 randomized가 허용되거나 그래프가 작아 반복이 충분할 때 유효합니다.

## 9. 자주 하는 실수

1. directed graph에 contraction min cut을 적용한다.
2. self-loop를 cut edge로 세어 답을 크게 만든다.
3. 한 번의 trial 결과만 믿고 제출한다.
4. weighted edge를 단순 unweighted edge처럼 처리한다.
5. 난수 seed가 고정되지 않아 디버깅 재현이 어렵다.

## 10. 문제를 볼 때 체크할 조건

- 그래프가 무향 multigraph인가?
- randomized 풀이가 허용되는가?
- weighted edge를 어떻게 처리할 것인가?
- 반복 횟수와 시간 제한이 맞는가?
- 작은 테스트에서 Stoer-Wagner와 비교했는가?

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: randomized min cut `/practice/...` 문제 필요 | Karger contraction 구현 | DSU |
| 표준 | TODO: repeated contraction `/practice/...` 문제 필요 | 반복으로 성공 확률 증폭 | Monte Carlo |
| 응용 | TODO: min cut comparison `/practice/...` 문제 필요 | Stoer-Wagner와 결과 비교 | deterministic fallback |
| 함정 | TODO: weighted randomized cut `/practice/...` 문제 필요 | weighted edge 처리 판단 | multigraph |

