# 트리 심화: 분할 기법

기본 트리 문제는 DFS 한 번으로 깊이, 부모, subtree 크기를 구하면 풀리는 경우가 많습니다. 심화 트리 문제는 한 단계 더 나아가서 트리를 **다른 순서나 더 작은 조각**으로 바꿔 다룹니다.

이 문서에서는 아래 도구를 연결해서 봅니다.

```text
Euler Tour: subtree를 배열 구간으로 바꾼다.
LCA: 두 정점 사이 경로의 교차점을 빠르게 찾는다.
Centroid Decomposition: 트리를 균형 있게 쪼갠다.
Heavy-Light Decomposition: 경로를 몇 개의 배열 구간으로 쪼갠다.
Small-to-large: subtree 정보를 큰 쪽에 작은 쪽을 합치며 관리한다.
```

## 1. 언제 심화 기법이 필요한가

트리에서 질의가 한 번만 나오면 DFS나 BFS로 충분한 경우가 많습니다. 하지만 아래 조건이 붙으면 전처리와 자료구조가 필요합니다.

| 문제 형태 | 자주 쓰는 도구 |
| --- | --- |
| subtree 전체에 업데이트/질의 | Euler Tour + Fenwick Tree 또는 Segment Tree |
| 두 정점 사이 경로 질의 | LCA, Heavy-Light Decomposition |
| 가장 가까운 표시 정점, 거리 기반 동적 질의 | Centroid Decomposition |
| 각 subtree의 색/값 종류 집계 | small-to-large, DSU on tree |
| 여러 중요 정점만 압축해서 처리 | Virtual Tree |

핵심은 트리를 그대로 보지 않는 것입니다. subtree는 배열의 연속 구간으로, 경로는 여러 heavy path 구간으로, 거리 질의는 센트로이드 조상들의 후보 비교로 바꿉니다.

## 2. Euler Tour

DFS로 정점을 처음 방문한 시간을 `tin[u]`, subtree를 빠져나온 직후를 `tout[u]`라고 합시다.

```cpp
int timer = 0;
vector<int> tin, tout, order;

void dfsEuler(int u, int parent, const vector<vector<int>>& tree) {
    tin[u] = timer++;
    order.push_back(u);

    for (int v : tree[u]) {
        if (v == parent) continue;
        dfsEuler(v, u, tree);
    }

    tout[u] = timer;
}
```

그러면 `u`의 subtree에 있는 정점들은 Euler 배열에서 아래 구간에 모입니다.

```text
[tin[u], tout[u])
```

이 성질 덕분에 subtree 합, subtree 색칠, subtree 최댓값 같은 문제를 배열 구간 질의로 바꿀 수 있습니다.

```cpp
// 정점 u의 subtree 전체 합
long long subtreeSum(int u) {
    return segmentTree.query(tin[u], tout[u] - 1);
}
```

주의할 점은 Euler Tour가 subtree에는 강하지만, 임의의 두 정점 사이 경로는 일반적으로 한 구간이 아니라는 것입니다. 경로 질의에는 Heavy-Light Decomposition이 더 자연스럽습니다.

## 3. LCA

LCA(Lowest Common Ancestor)는 두 정점의 가장 가까운 공통 조상입니다. 두 정점 사이 거리도 LCA로 계산할 수 있습니다.

```text
dist(u, v) = depth[u] + depth[v] - 2 * depth[lca(u, v)]
```

Binary Lifting은 각 정점의 `2^k`번째 조상을 미리 저장합니다.

```cpp
const int LOG = 20;
vector<array<int, LOG>> up;
vector<int> depth;

void dfsLca(int u, int parent, const vector<vector<int>>& tree) {
    up[u][0] = parent;
    for (int k = 1; k < LOG; ++k) {
        up[u][k] = up[up[u][k - 1]][k - 1];
    }

    for (int v : tree[u]) {
        if (v == parent) continue;
        depth[v] = depth[u] + 1;
        dfsLca(v, u, tree);
    }
}

int lift(int u, int diff) {
    for (int k = 0; k < LOG; ++k) {
        if (diff & (1 << k)) {
            u = up[u][k];
        }
    }
    return u;
}

int lca(int a, int b) {
    if (depth[a] < depth[b]) swap(a, b);
    a = lift(a, depth[a] - depth[b]);
    if (a == b) return a;

    for (int k = LOG - 1; k >= 0; --k) {
        if (up[a][k] != up[b][k]) {
            a = up[a][k];
            b = up[b][k];
        }
    }
    return up[a][0];
}
```

`LOG`는 `2^LOG > n`이 되도록 잡습니다. `n <= 200000`이면 `LOG = 20`보다 `19`가 딱 맞지만, 여유 있게 `20` 또는 `21`을 쓰는 식입니다.

루트의 부모는 보통 자기 자신으로 둡니다. 예를 들어 `root = 0`이면 아래처럼 호출합니다. 루트 부모를 `-1`로 둘 경우에는 `up[u][k]`를 계산할 때 `-1` 접근을 막는 별도 처리가 필요합니다.

```cpp
depth[0] = 0;
dfsLca(0, 0, tree);
```

## 4. 센트로이드 분할

센트로이드는 제거했을 때 남는 모든 컴포넌트 크기가 전체의 절반 이하인 정점입니다. 센트로이드 분할은 이 정점을 루트처럼 잡아 트리를 균형 있게 쪼개고, 각 조각에서 다시 센트로이드를 찾는 방법입니다.

분할 결과는 원래 트리가 아니라 **센트로이드 트리**입니다.

```text
원래 트리: 거리와 경로가 정의된 실제 입력 트리
센트로이드 트리: 분할 순서를 나타내는 보조 트리
```

기본 빌드는 아래처럼 진행합니다.

```cpp
vector<int> sub;
vector<int> blocked;
vector<int> centroidParent;

int calcSize(int u, int parent, const vector<vector<int>>& tree) {
    sub[u] = 1;
    for (int v : tree[u]) {
        if (v == parent || blocked[v]) continue;
        sub[u] += calcSize(v, u, tree);
    }
    return sub[u];
}

int findCentroid(int u, int parent, int total, const vector<vector<int>>& tree) {
    for (int v : tree[u]) {
        if (v == parent || blocked[v]) continue;
        if (sub[v] * 2 > total) {
            return findCentroid(v, u, total, tree);
        }
    }
    return u;
}

void buildCentroidTree(int entry, int parent, const vector<vector<int>>& tree) {
    int total = calcSize(entry, -1, tree);
    int c = findCentroid(entry, -1, total, tree);

    centroidParent[c] = parent;
    blocked[c] = 1;

    for (int v : tree[c]) {
        if (blocked[v]) continue;
        buildCentroidTree(v, c, tree);
    }
}
```

각 단계에서 조각 크기가 절반 이하로 줄어들기 때문에 센트로이드 트리의 높이는 `O(log n)`입니다.

## 5. 센트로이드 분할로 거리 질의 처리하기

대표 문제는 동적으로 색칠되는 정점 중 `u`에서 가장 가까운 정점까지의 거리를 묻는 형태입니다.

```text
update(x): x를 빨간 정점으로 표시한다.
query(u): u에서 가장 가까운 빨간 정점까지의 거리를 구한다.
```

각 정점은 센트로이드 트리에서 자기 조상 센트로이드들을 `O(log n)`개만 가집니다. 빨간 정점 `x`를 추가할 때, `x`의 모든 센트로이드 조상 `c`에 대해 `best[c] = min(best[c], dist(x, c))`를 갱신합니다.

질의 `u`도 자기 센트로이드 조상 `c`들을 보면서 아래 값을 비교합니다.

```text
best[c] + dist(u, c)
```

코드 모양은 단순합니다. `distance(a, b)`는 LCA로 계산한다고 가정합니다.

```cpp
const int INF = 1e9;
vector<int> best;

void paintRed(int x) {
    for (int c = x; c != -1; c = centroidParent[c]) {
        best[c] = min(best[c], distance(x, c));
    }
}

int nearestRed(int u) {
    int answer = INF;
    for (int c = u; c != -1; c = centroidParent[c]) {
        answer = min(answer, best[c] + distance(u, c));
    }
    return answer;
}
```

각 update/query는 센트로이드 조상 수만큼만 보므로 `O(log n * cost(distance))`입니다. LCA 거리 계산이 `O(log n)`이면 전체는 `O(log^2 n)`, 거리 값을 분할 과정에서 미리 저장하면 `O(log n)`까지 줄일 수 있습니다.

센트로이드 분할은 "거리 후보를 모든 정점에서 찾는 대신, 균형 분할의 조상 센트로이드들만 본다"는 관점으로 이해하면 됩니다.

## 6. Heavy-Light Decomposition

Heavy-Light Decomposition, 줄여서 HLD는 트리의 경로를 배열 구간 몇 개로 나누는 기법입니다.

각 정점에서 subtree 크기가 가장 큰 자식을 heavy child로 고릅니다. heavy edge를 따라 이어지는 경로를 하나의 chain으로 만들면, 임의의 루트-정점 경로는 `O(log n)`개의 chain 조각으로 나뉩니다.

먼저 부모, 깊이, subtree 크기, heavy child를 구합니다.

```cpp
vector<int> parent, depth, heavy, head, pos, sub;
int currentPos = 0;

int dfsHld(int u, const vector<vector<int>>& tree) {
    sub[u] = 1;
    int bestSize = 0;

    for (int v : tree[u]) {
        if (v == parent[u]) continue;
        parent[v] = u;
        depth[v] = depth[u] + 1;
        int childSize = dfsHld(v, tree);
        sub[u] += childSize;

        if (childSize > bestSize) {
            bestSize = childSize;
            heavy[u] = v;
        }
    }
    return sub[u];
}
```

그다음 heavy child는 같은 chain으로, light child는 새 chain의 head로 내려갑니다.

```cpp
void decompose(int u, int chainHead, const vector<vector<int>>& tree) {
    head[u] = chainHead;
    pos[u] = currentPos++;

    if (heavy[u] != -1) {
        decompose(heavy[u], chainHead, tree);
    }

    for (int v : tree[u]) {
        if (v == parent[u] || v == heavy[u]) continue;
        decompose(v, v, tree);
    }
}
```

처음 빌드할 때는 모든 배열을 초기화하고, 루트의 부모를 자기 자신으로 둔 뒤 시작합니다.

```cpp
void buildHld(const vector<vector<int>>& tree, int root = 0) {
    int n = (int)tree.size();

    parent.assign(n, -1);
    depth.assign(n, 0);
    heavy.assign(n, -1);
    head.assign(n, -1);
    pos.assign(n, -1);
    sub.assign(n, 0);

    currentPos = 0;
    parent[root] = root;
    dfsHld(root, tree);
    decompose(root, root, tree);
}
```

`pos[u]`는 정점 `u`가 세그먼트 트리 배열에서 차지하는 위치입니다. 같은 chain에 있는 정점들은 `pos`가 연속으로 배치됩니다.

## 7. HLD로 경로 질의 처리하기

두 정점 `a`, `b` 사이 경로를 처리할 때는 두 정점이 같은 chain에 올 때까지 chain head가 더 깊은 쪽을 위로 올립니다.

```cpp
long long queryPath(int a, int b) {
    long long result = 0;

    while (head[a] != head[b]) {
        if (depth[head[a]] < depth[head[b]]) {
            swap(a, b);
        }

        result += segmentTree.query(pos[head[a]], pos[a]);
        a = parent[head[a]];
    }

    if (depth[a] > depth[b]) {
        swap(a, b);
    }
    result += segmentTree.query(pos[a], pos[b]);
    return result;
}
```

경로 위의 값 갱신도 같은 방식으로 구간 업데이트를 여러 번 호출하면 됩니다.

```cpp
void updatePath(int a, int b, long long delta) {
    while (head[a] != head[b]) {
        if (depth[head[a]] < depth[head[b]]) {
            swap(a, b);
        }

        segmentTree.add(pos[head[a]], pos[a], delta);
        a = parent[head[a]];
    }

    if (depth[a] > depth[b]) {
        swap(a, b);
    }
    segmentTree.add(pos[a], pos[b], delta);
}
```

정점 값 문제라면 위 코드처럼 양 끝을 포함합니다. 간선 값 문제라면 보통 간선 값을 더 깊은 정점 쪽 위치에 저장하므로 마지막 구간에서 `pos[a] + 1`부터 처리해야 할 때가 많습니다.

```text
정점 값 경로: [pos[lca], pos[child]]
간선 값 경로: [pos[lca] + 1, pos[child]]
```

## 8. HLD와 Euler Tour의 관계

HLD의 `pos` 배열은 heavy path를 우선해서 정점을 배치합니다. 그래도 DFS 순서이기 때문에 subtree가 연속 구간이 되도록 구현할 수 있습니다.

```cpp
long long querySubtree(int u) {
    return segmentTree.query(pos[u], pos[u] + sub[u] - 1);
}
```

따라서 같은 세그먼트 트리로 아래 두 종류의 질의를 함께 처리할 수 있습니다.

| 질의 | 구간 변환 |
| --- | --- |
| subtree 질의 | `[pos[u], pos[u] + sub[u] - 1]` |
| 경로 질의 | HLD chain 구간 여러 개 |

다만 모든 HLD 구현이 subtree 연속성을 보장하는 것은 아닙니다. 위 코드처럼 정점을 처음 방문할 때 `pos`를 부여하고 모든 자식을 이어서 방문해야 subtree 구간이 연속이 됩니다.

## 9. small-to-large

subtree마다 색 종류 수, 값 빈도, 문자열 집합 같은 것을 모아야 할 때 모든 subtree를 매번 새로 만들면 `O(n^2)`가 됩니다. small-to-large는 작은 컨테이너를 큰 컨테이너에 합쳐 전체 이동 횟수를 줄이는 기법입니다.

```cpp
vector<unordered_map<int, int>*> bag;

void dfsSmallToLarge(int u, int parent, const vector<vector<int>>& tree, const vector<int>& color) {
    int heavyChild = -1;
    for (int v : tree[u]) {
        if (v == parent) continue;
        dfsSmallToLarge(v, u, tree, color);
        if (heavyChild == -1 || bag[v]->size() > bag[heavyChild]->size()) {
            heavyChild = v;
        }
    }

    if (heavyChild == -1) {
        bag[u] = new unordered_map<int, int>();
    } else {
        bag[u] = bag[heavyChild];
    }

    (*bag[u])[color[u]]++;

    for (int v : tree[u]) {
        if (v == parent || v == heavyChild) continue;
        for (auto [key, value] : *bag[v]) {
            (*bag[u])[key] += value;
        }
    }
}
```

각 원소는 자신보다 큰 컨테이너로 이동할 때마다 소속 컨테이너 크기가 적어도 두 배 가까이 커집니다. 그래서 전체 이동 횟수를 `O(n log n)` 수준으로 볼 수 있습니다.

실전에서는 메모리 관리가 번거로우면 포인터 대신 `vector<map<int, int>>`와 swap을 쓰기도 합니다.

## 10. 어떤 기법을 고를까

| 필요한 작업 | 우선 후보 |
| --- | --- |
| subtree 업데이트/질의 | Euler Tour + Fenwick/Segment Tree |
| 두 정점 거리만 빠르게 계산 | LCA |
| 경로 합/최댓값/업데이트 | Heavy-Light Decomposition |
| 동적 거리 후보 질의 | Centroid Decomposition |
| subtree별 값 종류/빈도 집계 | small-to-large, DSU on tree |
| 중요 정점 집합 위에서 DP | Virtual Tree |

센트로이드 분할과 HLD는 둘 다 트리를 쪼개지만 목적이 다릅니다. 센트로이드 분할은 트리를 균형 있게 줄여 거리 후보를 압축하고, HLD는 경로를 배열 구간으로 압축합니다.

정리하면, subtree는 Euler Tour, 경로는 HLD, 거리 후보는 센트로이드 분할로 먼저 분류하면 됩니다. 그 뒤 필요한 연산이 합인지 최댓값인지, 업데이트가 있는지에 따라 Fenwick Tree나 Segment Tree를 붙이면 됩니다.

## 11. 시간 복잡도

| 기법 | 전처리 | 질의/업데이트 |
| --- | --- | --- |
| Euler Tour + Fenwick/Segment Tree | `O(n)` | `O(log n)` |
| LCA binary lifting | `O(n log n)` | `O(log n)` |
| Centroid Decomposition | `O(n log n)` | 보통 `O(log n)` |
| Heavy-Light Decomposition | `O(n)` | 경로당 `O(log^2 n)` 또는 구현에 따라 `O(log n)` |
| small-to-large | 전체 `O(n log n)` 수준 | subtree 집계 문제에 따라 다름 |

## 12. 자주 하는 실수

- Euler Tour에서 subtree 구간의 오른쪽 끝을 `tin[u] + sub[u] - 1`로 잡지 않습니다.
- LCA 전처리 루프에서 없는 조상을 참조합니다.
- HLD에서 간선 값을 더 깊은 정점 위치에 저장한다는 규칙을 잊습니다.
- Centroid Decomposition의 "이미 제거한 centroid" 표시를 빼먹어 같은 정점을 다시 처리합니다.
- small-to-large에서 작은 컨테이너를 큰 컨테이너로 합치지 않아 `O(n^2)`가 됩니다.

## 13. 문제를 볼 때 체크할 조건

1. subtree 전체를 배열 구간처럼 다룰 수 있는가?
2. 두 정점의 LCA나 거리가 반복해서 필요한가?
3. 경로 업데이트/질의가 많아 HLD가 필요한가?
4. 특정 정점 집합까지의 거리 후보를 빠르게 관리해야 하는가?
5. subtree마다 색/값 빈도를 모두 모아야 하는가?

## 14. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: subtree 합 질의 문제 추가 | Euler Tour로 subtree를 연속 구간으로 변환 | `tin`, `subtree` |
| 표준 | TODO: LCA와 거리 질의 문제 추가 | binary lifting 전처리와 깊이 맞추기 | LCA, depth |
| 응용 | TODO: 경로 질의 문제 추가 | HLD로 경로를 여러 구간으로 분해 | chain, segment tree |
| 함정 | TODO: 센트로이드 분할 거리 후보 문제 추가 | 제거된 centroid 표시와 거리 캐시 관리 | centroid decomposition |
