# SCC와 2-SAT

SCC(Strongly Connected Component)는 방향 그래프에서 서로 왕복 도달 가능한 정점들을 하나로 묶은 컴포넌트입니다. 방향 그래프에 사이클이 섞여 있으면 위상 정렬을 바로 적용할 수 없지만, SCC로 압축하면 컴포넌트 사이의 그래프는 DAG가 됩니다.

2-SAT은 각 조건이 두 개의 boolean literal로 이루어진 논리식을 만족시킬 수 있는지 판정하는 문제입니다. `x 또는 y` 형태의 절을 implication graph로 바꾸면 SCC로 모순 여부를 판단할 수 있습니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: DFS, 방향 그래프, 위상 정렬과 DAG DP
- 함께 보면 좋은 레슨: 그래프와 트리 기본 성질, Bellman-Ford와 음수 사이클
- 다음에 볼 레슨: Flow와 Bipartite Matching

## 1. SCC가 필요한 상황

방향 그래프에서 아래 질문이 나오면 SCC를 떠올립니다.

| 질문 | SCC 관점 |
| --- | --- |
| `u`에서 `v`로도 가고 `v`에서 `u`로도 갈 수 있는가? | 같은 SCC인지 확인 |
| 방향 그래프의 사이클을 묶어 DAG로 만들 수 있는가? | SCC condensation graph |
| 어떤 조건들이 서로 강제로 연결되는가? | implication graph의 SCC |
| 2-SAT을 만족시킬 수 있는가? | 변수와 부정이 같은 SCC인지 확인 |

SCC 안에서는 모든 정점이 서로 도달 가능합니다. SCC 사이의 간선만 남겨 만든 압축 그래프에는 사이클이 없습니다. 만약 SCC 압축 뒤에도 사이클이 있다면, 그 사이클에 속한 컴포넌트들은 사실 하나의 SCC였어야 하기 때문입니다.

## 2. Kosaraju 알고리즘

SCC를 구하는 대표적인 방법 중 하나가 Kosaraju 알고리즘입니다.

1. 원래 그래프에서 DFS를 하며 정점의 종료 순서를 기록한다.
2. 모든 간선을 뒤집은 그래프에서, 종료 순서의 역순으로 DFS를 한다.
3. 두 번째 DFS 한 번에 방문되는 정점들이 하나의 SCC다.

첫 번째 DFS의 종료 순서는 "나중에 닫힌 정점일수록 압축 DAG에서 앞쪽 후보"라는 정보를 줍니다. 간선을 뒤집은 뒤 그 순서로 탐색하면 한 SCC를 밖으로 새지 않고 모을 수 있습니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct SCCResult {
    int componentCount;
    vector<int> componentOf;
    vector<vector<int>> components;
};

void dfsOrder(int u, const vector<vector<int>>& graph, vector<int>& visited, vector<int>& order) {
    visited[u] = 1;
    for (int v : graph[u]) {
        if (!visited[v]) {
            dfsOrder(v, graph, visited, order);
        }
    }
    order.push_back(u);
}

void dfsComponent(
    int u,
    int componentId,
    const vector<vector<int>>& reversed,
    vector<int>& componentOf,
    vector<int>& current
) {
    componentOf[u] = componentId;
    current.push_back(u);
    for (int v : reversed[u]) {
        if (componentOf[v] == -1) {
            dfsComponent(v, componentId, reversed, componentOf, current);
        }
    }
}

SCCResult kosaraju(const vector<vector<int>>& graph) {
    int n = (int)graph.size();
    vector<vector<int>> reversed(n);
    for (int u = 0; u < n; ++u) {
        for (int v : graph[u]) {
            reversed[v].push_back(u);
        }
    }

    vector<int> visited(n, 0);
    vector<int> order;
    for (int i = 0; i < n; ++i) {
        if (!visited[i]) {
            dfsOrder(i, graph, visited, order);
        }
    }
    reverse(order.begin(), order.end());

    vector<int> componentOf(n, -1);
    vector<vector<int>> components;
    for (int start : order) {
        if (componentOf[start] != -1) {
            continue;
        }
        vector<int> current;
        int componentId = (int)components.size();
        dfsComponent(start, componentId, reversed, componentOf, current);
        components.push_back(current);
    }

    return {(int)components.size(), componentOf, components};
}
```

시간 복잡도는 `O(V + E)`입니다. DFS를 두 번 하고, 간선을 한 번 뒤집기 때문입니다.

## 3. SCC 압축 그래프

각 SCC를 하나의 정점으로 바꾸고, 서로 다른 SCC 사이의 간선만 남기면 condensation graph가 됩니다.

```text
u -> v 가 있고 comp[u] != comp[v] 이면
comp[u] -> comp[v] 간선을 만든다.
```

이 그래프는 DAG입니다. 그래서 SCC로 사이클을 묶은 뒤에는 위상 정렬, DP, 도달성 전파 같은 DAG 기법을 적용할 수 있습니다.

중복 간선은 문제에 따라 제거할 수도 있고 그대로 둬도 됩니다. DP 전이에 중복이 영향을 주면 `sort + unique`나 `set`으로 정리합니다.

## 4. 2-SAT 모델링

2-SAT은 아래처럼 각 절이 두 literal의 OR로 이루어진 식입니다.

```text
(a or b) and (!a or c) and (!b or !c)
```

`(x or y)`는 implication 두 개로 바꿀 수 있습니다.

```text
!x -> y
!y -> x
```

왜냐하면 `x`가 거짓이면 절을 만족시키려면 `y`가 참이어야 하고, `y`가 거짓이면 `x`가 참이어야 하기 때문입니다.

각 변수 `i`에 대해 `i가 false`와 `i가 true`를 서로 다른 정점으로 둡니다. 한 변수의 참/거짓 정점 번호를 일관되게 정하는 것이 중요합니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

struct SCCResult {
    int componentCount;
    vector<int> componentOf;
    vector<vector<int>> components;
};

void dfsOrder(int u, const vector<vector<int>>& graph, vector<int>& visited, vector<int>& order) {
    visited[u] = 1;
    for (int v : graph[u]) {
        if (!visited[v]) dfsOrder(v, graph, visited, order);
    }
    order.push_back(u);
}

void dfsComponent(int u, int id, const vector<vector<int>>& reversed, vector<int>& comp) {
    comp[u] = id;
    for (int v : reversed[u]) {
        if (comp[v] == -1) dfsComponent(v, id, reversed, comp);
    }
}

SCCResult kosaraju(const vector<vector<int>>& graph) {
    int n = (int)graph.size();
    vector<vector<int>> reversed(n);
    for (int u = 0; u < n; ++u) {
        for (int v : graph[u]) reversed[v].push_back(u);
    }

    vector<int> visited(n, 0);
    vector<int> order;
    for (int i = 0; i < n; ++i) {
        if (!visited[i]) dfsOrder(i, graph, visited, order);
    }
    reverse(order.begin(), order.end());

    vector<int> comp(n, -1);
    int componentCount = 0;
    for (int u : order) {
        if (comp[u] == -1) {
            dfsComponent(u, componentCount, reversed, comp);
            ++componentCount;
        }
    }
    return {componentCount, comp, {}};
}

struct TwoSat {
    int variableCount;
    vector<vector<int>> graph;

    explicit TwoSat(int n) : variableCount(n), graph(2 * n) {}

    int node(int variable, bool value) const {
        return 2 * variable + (value ? 1 : 0);
    }

    int neg(int x) const {
        return x ^ 1;
    }

    void addImplication(int from, int to) {
        graph[from].push_back(to);
    }

    void addOr(int aVariable, bool aValue, int bVariable, bool bValue) {
        int a = node(aVariable, aValue);
        int b = node(bVariable, bValue);
        addImplication(neg(a), b);
        addImplication(neg(b), a);
    }

    bool satisfiable() const {
        SCCResult result = kosaraju(graph);
        for (int i = 0; i < variableCount; ++i) {
            if (result.componentOf[node(i, false)] == result.componentOf[node(i, true)]) {
                return false;
            }
        }
        return true;
    }
};
```

`x`와 `!x`가 같은 SCC에 있으면 모순입니다. `x -> !x`와 `!x -> x`가 모두 가능하다는 뜻이라, 어떤 값을 골라도 자기 부정을 강제하게 됩니다.

## 5. 값을 실제로 정해야 할 때

만족 가능 여부만 묻는 문제도 있지만, 실제 변수 값을 하나 출력해야 하는 문제도 있습니다. SCC 번호가 위상 순서와 어떤 방향으로 매겨졌는지에 따라 비교식이 달라질 수 있으므로 구현마다 확인해야 합니다.

Kosaraju를 위 코드처럼 종료 순서 역순으로 두 번째 DFS를 돌리면, 앞쪽 SCC부터 번호가 작게 붙습니다. 일반적으로는 `comp[false]`와 `comp[true]`의 위상 순서 관계로 값을 정합니다. 불안하면 압축 DAG를 만들고 역위상 순서로 값을 배정하는 방식이 더 명시적입니다.

입문 단계에서는 먼저 만족 가능성 판정까지 정확히 익히고, 값 복원은 문제 요구가 있을 때 SCC 번호 방향을 작은 예제로 검증하세요.

## 6. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| SCC 계산 | `O(V + E)` | `O(V + E)` |
| SCC 압축 그래프 생성 | `O(V + E)` | `O(V + E)` |
| 2-SAT 그래프 생성 | 절 개수 `C`에 대해 `O(C)` | `O(variable + C)` |
| 2-SAT 판정 | `O(variable + C)` | `O(variable + C)` |

2-SAT에서 정점 수는 변수 수의 2배이고, 절 하나는 implication 간선 2개가 됩니다.

## 7. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 일반 연결 요소처럼 무방향으로 처리 | 방향성 손실 | 반드시 방향 그래프 DFS 사용 |
| reversed graph를 만들지 않음 | Kosaraju 두 번째 단계 실패 | 모든 간선 `u -> v`를 `v -> u`로 뒤집기 |
| 2-SAT에서 `x or y`를 `x -> y`로 잘못 변환 | 전혀 다른 조건 | `!x -> y`, `!y -> x` 사용 |
| 변수와 부정 번호를 일관되지 않게 매핑 | 모순 판정 오류 | `x ^ 1`로 부정이 되게 번호 설계 |
| 값 복원에서 SCC 번호 방향을 착각 | 만족하지 않는 배정 출력 | 작은 식으로 comp 순서 검증 |
| 재귀 DFS 깊이 초과 | 런타임 에러 | 입력이 크면 반복 DFS 또는 스택 제한 검토 |

## 8. 문제를 볼 때 체크할 조건

1. 방향 그래프에서 서로 도달 가능한 묶음이 필요한가?
2. 사이클을 묶은 뒤 DAG로 처리해야 하는가?
3. 조건이 `A이면 B` 형태의 implication으로 바뀌는가?
4. 각 제약이 `(x or y)` 꼴의 2-SAT 절로 표현되는가?
5. 만족 가능성만 필요한가, 실제 배정도 출력해야 하는가?
6. DFS 재귀 깊이가 입력 제한에서 안전한가?

정리하면, SCC는 방향 그래프의 사이클을 압축해 DAG로 바꾸는 도구이고, 2-SAT은 boolean 조건을 implication graph로 바꾼 뒤 SCC 모순을 찾는 응용입니다.

## 9. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 방향 그래프의 SCC 개수를 세는 문제 추가 | Kosaraju 두 번의 DFS 흐름 익히기 | finish order, reversed graph |
| 표준 | TODO: SCC 압축 DAG를 만드는 문제 추가 | 컴포넌트 번호와 중복 간선 정리 | condensation graph |
| 응용 | TODO: 2-SAT 만족 가능성 판정 문제 추가 | OR 절을 implication 두 개로 변환 | implication graph |
| 함정 | TODO: 실제 boolean 배정을 출력하는 문제 추가 | SCC 번호 방향과 값 복원 검증 | assignment reconstruction |
