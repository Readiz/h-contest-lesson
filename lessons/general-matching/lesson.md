# General Matching

General Matching은 이분 그래프가 아닌 일반 무향 그래프에서 최대 matching을 찾는 문제입니다. 이분 그래프 matching은 BFS/DFS augmenting path로 충분하지만, 일반 그래프에는 odd cycle이 있어서 단순 alternating path 탐색이 막힙니다.

이 레슨은 Matching과 Cover Duality 이후에 보는 Edmonds blossom 알고리즘의 핵심 아이디어를 정리합니다.

1. matching과 augmenting path의 의미는 그대로 유지한다.
2. odd cycle을 blossom으로 접어 하나의 정점처럼 탐색한다.
3. augmenting path를 찾으면 접힌 cycle을 다시 펴며 matching을 뒤집는다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 그래프 탐색, 이분 매칭, alternating path, BFS tree
- 함께 보면 좋은 레슨: Max Flow, Matching과 Cover Duality, Flow with Lower Bound
- 다음에 볼 레슨: weighted matching, matroid intersection, graph factor

## 1. 문제 신호

| 문제 표현 | 접근 |
| --- | --- |
| 일반 무향 그래프에서 최대 짝짓기 | general matching |
| 삼각형이나 홀수 cycle이 있다 | blossom 필요 |
| 각 정점은 최대 하나의 간선만 선택 | matching constraint |
| 최대 cardinality만 필요 | Edmonds blossom |
| 간선 가중치까지 최대화 | weighted blossom, 별도 주제 |

문제가 이분 그래프임이 보장되면 이 레슨의 알고리즘은 과합니다. 왼쪽/오른쪽 partition이 자연스럽게 잡히면 이분 matching으로 먼저 모델링합니다.

## 2. 왜 이분 Matching으로 안 되는가

이분 그래프에서는 alternating forest를 만들 때 같은 level의 두 정점이 연결되는 일이 없습니다. 일반 그래프에서는 같은 parity level 사이 간선이 생기고, 이 간선이 odd cycle을 만듭니다.

```text
root -- ... -- u
root -- ... -- v
u -- v
```

`u`와 `v`가 같은 짝수 level이면 두 경로와 `u-v` 간선이 합쳐져 odd cycle이 됩니다. 이 cycle 안에서는 어느 간선을 matching으로 선택하느냐에 따라 입구와 출구가 바뀔 수 있으므로, cycle 전체를 하나의 blossom으로 접어 탐색합니다.

## 3. Blossom 수축

Blossom 수축의 관점은 단순합니다.

1. odd cycle의 base를 찾는다.
2. cycle 안의 모든 정점의 base를 같은 대표 정점으로 바꾼다.
3. 밖에서 볼 때 blossom은 하나의 정점처럼 동작한다.

수축 후에도 augmenting path가 존재하면 원래 그래프에서도 존재합니다. path가 blossom을 통과하면 cycle 내부의 alternating 구조를 따라 펴면 됩니다.

## 4. 구현 골격

아래 코드는 최대 cardinality matching을 구하는 표준 Edmonds blossom 구현 골격입니다. 정점은 `0..n-1`입니다.

```cpp compile-check
#include <algorithm>
#include <queue>
#include <vector>
using namespace std;

struct GeneralMatching {
    int n;
    vector<vector<int>> graph;
    vector<int> match;
    vector<int> parent;
    vector<int> base;
    vector<bool> used;
    vector<bool> blossom;
    queue<int> q;

    explicit GeneralMatching(int n) : n(n), graph(n) {}

    void addEdge(int u, int v) {
        if (u == v) {
            return;
        }
        graph[u].push_back(v);
        graph[v].push_back(u);
    }

    int lca(int a, int b) {
        vector<bool> seen(n, false);
        while (true) {
            a = base[a];
            seen[a] = true;
            if (match[a] == -1) {
                break;
            }
            a = parent[match[a]];
        }

        while (true) {
            b = base[b];
            if (seen[b]) {
                return b;
            }
            b = parent[match[b]];
        }
    }

    void markPath(int v, int b, int child) {
        while (base[v] != b) {
            blossom[base[v]] = true;
            blossom[base[match[v]]] = true;
            parent[v] = child;
            child = match[v];
            v = parent[match[v]];
        }
    }

    int findPath(int root) {
        used.assign(n, false);
        parent.assign(n, -1);
        base.resize(n);
        for (int i = 0; i < n; ++i) {
            base[i] = i;
        }

        while (!q.empty()) {
            q.pop();
        }
        q.push(root);
        used[root] = true;

        while (!q.empty()) {
            int v = q.front();
            q.pop();

            for (int u : graph[v]) {
                if (base[v] == base[u] || match[v] == u) {
                    continue;
                }

                if (u == root || (match[u] != -1 && parent[match[u]] != -1)) {
                    int curBase = lca(v, u);
                    blossom.assign(n, false);
                    markPath(v, curBase, u);
                    markPath(u, curBase, v);

                    for (int i = 0; i < n; ++i) {
                        if (!blossom[base[i]]) {
                            continue;
                        }
                        base[i] = curBase;
                        if (!used[i]) {
                            used[i] = true;
                            q.push(i);
                        }
                    }
                } else if (parent[u] == -1) {
                    parent[u] = v;
                    if (match[u] == -1) {
                        return u;
                    }
                    int next = match[u];
                    used[next] = true;
                    q.push(next);
                }
            }
        }

        return -1;
    }

    int maxMatching() {
        match.assign(n, -1);
        int result = 0;

        for (int root = 0; root < n; ++root) {
            if (match[root] != -1) {
                continue;
            }

            int v = findPath(root);
            if (v == -1) {
                continue;
            }

            ++result;
            while (v != -1) {
                int pv = parent[v];
                int nv = (pv == -1 ? -1 : match[pv]);
                match[v] = pv;
                if (pv != -1) {
                    match[pv] = v;
                }
                v = nv;
            }
        }

        return result;
    }
};
```

이 구현은 cardinality matching용입니다. 가중치가 붙으면 dual variable과 slack을 관리하는 weighted blossom이 필요하므로 별도 알고리즘으로 봐야 합니다.

## 5. Augmenting Path 뒤집기

augmenting path는 matching에 속하지 않은 간선과 matching 간선이 번갈아 나오며, 양 끝이 unmatched 정점인 경로입니다.

```text
unmatched - free edge - matched edge - free edge - unmatched
```

이 경로의 간선 선택 상태를 뒤집으면 matching 크기가 1 증가합니다.

| 간선 종류 | 뒤집은 뒤 |
| --- | --- |
| matching이 아니던 간선 | matching에 포함 |
| matching이던 간선 | matching에서 제거 |

Blossom 알고리즘도 결국 augmenting path를 찾아 이 뒤집기를 수행합니다. 어려운 부분은 odd cycle 때문에 path 탐색 중 cycle을 임시로 접는 과정입니다.

## 6. Base와 Parent의 의미

구현에서 자주 헷갈리는 배열은 아래와 같습니다.

| 배열 | 의미 |
| --- | --- |
| `match[v]` | v와 현재 matching으로 연결된 정점, 없으면 `-1` |
| `parent[v]` | alternating forest에서 v로 들어온 이전 정점 |
| `base[v]` | blossom 수축 후 v가 속한 묶음의 대표 정점 |
| `used[v]` | BFS queue에 들어간 outer 정점 |
| `blossom[b]` | 이번 수축에서 base b가 blossom 내부인지 |

`base`는 DSU처럼 영구적으로 합치는 구조가 아닙니다. 한 번의 BFS 탐색 안에서 blossom을 접기 위한 임시 대표입니다.

## 7. 시간 복잡도

위 구현은 보통 `O(N^3)`으로 봅니다.

| 연산 | 비용 |
| --- | ---: |
| 한 root에서 augmenting path 탐색 | `O(N^2)` |
| 최대 augment 횟수 | `O(N)` |
| 전체 | `O(N^3)` |

그래프가 조밀하고 `N`이 수백 단위라면 C++로 충분한 경우가 많습니다. `N`이 수천 이상이면 문제 제약과 그래프 특성을 다시 봐야 합니다.

## 8. 자주 하는 실수

1. 일반 그래프인데 이분 matching을 적용한다.
2. self-loop를 matching 후보로 넣는다.
3. blossom 수축 후 `base`를 갱신했지만 queue에 필요한 정점을 다시 넣지 않는다.
4. augmenting path를 뒤집을 때 이전 matching partner를 잃어버린다.
5. maximum matching과 maximal matching을 혼동한다.

## 9. 문제를 볼 때 체크할 조건

- 그래프가 정말 일반 그래프인가, 아니면 partition이 숨어 있는 이분 그래프인가?
- 필요한 것은 maximum cardinality인가, maximum weight인가?
- 정점 수가 blossom `O(N^3)`에 맞는가?
- matching 크기만 필요한가, 실제 선택 간선 목록도 필요한가?
- unmatched 정점이 허용되는가, perfect matching을 요구하는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 일반 그래프 matching 판정 `/practice/...` 문제 필요 | augmenting path와 blossom 수축 흐름 추적 | Edmonds blossom |
| 표준 | TODO: maximum cardinality matching `/practice/...` 문제 필요 | 구현으로 최대 matching 크기 계산 | general matching |
| 응용 | TODO: perfect matching 존재 `/practice/...` 문제 필요 | matching 크기와 정점 수 비교 | perfect matching |
| 함정 | TODO: 이분 그래프가 아닌 반례 `/practice/...` 문제 필요 | odd cycle 때문에 bipartite matching이 깨지는 사례 확인 | odd cycle |
