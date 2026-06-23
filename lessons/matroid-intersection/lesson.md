# Matroid Intersection

Matroid Intersection은 두 개의 독립성 조건을 동시에 만족하는 가장 큰 집합을 찾는 모델입니다. 그래프 matching처럼 augmenting path를 찾지만, "간선을 하나 더 넣어도 되는가" 대신 "현재 집합에서 무엇을 빼면 새 원소를 넣을 수 있는가"를 두 matroid 각각에 대해 묻습니다.

이 레슨은 General Matching, Weighted Matching, Linear Basis Applications 이후에 보는 그래프/조합 최적화 심화입니다.

1. 독립 집합을 하나씩 키우는 문제인지 본다.
2. 두 독립성 조건이 모두 matroid 교환 성질을 가지는지 확인한다.
3. exchange graph에서 augmenting path를 찾아 선택 집합을 뒤집는다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: General Matching, Weighted Matching, Greedy proof, Linear Basis
- 함께 보면 좋은 레슨: Max Flow/Min Cut, Linear Basis Applications, Proof and Invariants
- 다음에 볼 레슨: dynamic flow, matroid parity, combinatorial optimization

## 1. 문제 신호

| 문제 표현 | Matroid Intersection 관점 |
| --- | --- |
| 두 종류의 "동시에 가능" 조건이 있다 | 두 matroid의 공통 독립 집합 |
| 하나는 cycle 금지, 하나는 색상별 개수 제한 | graphic matroid + partition matroid |
| 벡터들이 독립이어야 하고 그룹별 제한도 있다 | linear matroid + partition matroid |
| 단순 greedy가 앞 선택 때문에 막힌다 | exchange path 필요 |
| 최대 크기뿐 아니라 가중치 확장이 보인다 | weighted matroid intersection 후보 |

Matroid는 모든 부분집합이 독립이고, 작은 독립 집합은 큰 독립 집합의 어떤 원소를 받아 더 커질 수 있다는 교환 성질을 가집니다. 이 성질 덕분에 augmenting path 기반 알고리즘이 맞습니다.

## 2. 핵심 모델

원소 전체 집합을 `E`, 현재 선택 집합을 `S`라고 하겠습니다. 목표는 `S`가 두 matroid `M1`, `M2`에서 모두 독립이 되도록 하면서 크기를 최대화하는 것입니다.

한 번의 증가 단계는 아래 질문으로 구성됩니다.

```text
어떤 원소 x not in S를 넣고 싶다.
M1에서 x를 넣으려면 어떤 y in S를 빼야 하는가?
M2에서 x를 넣으려면 어떤 y in S를 빼야 하는가?
```

이 질문들의 답을 방향 그래프로 만들면 exchange graph가 됩니다. 시작점은 `S + x`가 `M1`에서 바로 독립인 원소이고, 도착점은 `S + x`가 `M2`에서 바로 독립인 원소입니다. 시작점에서 도착점까지 가는 경로가 있으면, 그 경로의 원소 선택 여부를 뒤집어 `|S|`를 1 늘립니다.

## 3. 작은 예시

간선 4개가 있고, forest 조건과 색상별 최대 1개 조건을 동시에 만족해야 한다고 하겠습니다.

```text
e1: 1-2, red
e2: 2-3, red
e3: 1-3, blue
e4: 3-4, blue
```

현재 `S = {e1, e3}`이라면 forest 조건은 이미 `1-2-3` path라서 독립이고, 색상도 red 1개, blue 1개라서 독립입니다. `e2`를 넣으면 색상 red가 2개라서 partition matroid가 깨집니다. 대신 `e1`을 빼면 색상 조건은 복구됩니다.

`e4`를 넣으면 색상 blue가 2개라서 `e3`을 빼야 합니다. 하지만 forest 쪽에서는 `e4`를 넣어도 cycle이 생기지 않습니다. 이런 "어느 조건에서 무엇을 빼야 하는지"를 양쪽에서 번갈아 연결하면 augmenting path가 됩니다.

## 4. Exchange Graph

현재 선택되지 않은 원소를 `outside`, 선택된 원소를 `inside`라고 부릅니다.

| 간선 종류 | 의미 |
| --- | --- |
| source -> `x` | `S + x`가 `M1`에서 독립 |
| `x` -> sink | `S + x`가 `M2`에서 독립 |
| `y` -> `x` | `S - y + x`가 `M1`에서 독립 |
| `x` -> `y` | `S - y + x`가 `M2`에서 독립 |

방향이 다른 이유가 중요합니다. 하나의 path를 따라 선택 여부를 뒤집었을 때, `M1`과 `M2`의 조건이 번갈아 복구되도록 방향을 맞춥니다.

## 5. 구현 골격

실전 구현에서는 matroid마다 독립성 판정 함수를 준비합니다.

```cpp
struct MatroidOracle {
    bool independent(const vector<int>& chosen) const {
        // chosen 원소들이 이 matroid에서 독립인지 판정한다.
        return true;
    }
};

bool canAdd(const MatroidOracle& matroid, vector<int> chosen, int x) {
    chosen.push_back(x);
    return matroid.independent(chosen);
}

bool canExchange(const MatroidOracle& matroid, vector<int> chosen, int removeValue, int addValue) {
    vector<int> next;
    for (int value : chosen) {
        if (value != removeValue) {
            next.push_back(value);
        }
    }
    next.push_back(addValue);
    return matroid.independent(next);
}
```

이 코드는 느린 골격입니다. 그래프 matroid는 DSU나 dynamic connectivity로, partition matroid는 bucket count로, linear matroid는 basis rebuild로 최적화합니다. 먼저 느린 oracle로 작은 입력을 맞춘 뒤, 병목이 되는 matroid만 빠르게 바꾸는 편이 안전합니다.

## 6. 시간 복잡도

| 단계 | 시간 |
| --- | ---: |
| exchange graph 후보 쌍 | `O(|E| * |S|)` |
| 독립성 oracle 1회 | matroid 종류에 따라 다름 |
| augmenting path 1회 | graph BFS/DFS |
| 총 증가 횟수 | 최대 rank |

순진하게 매번 oracle을 rebuild하면 `O(r * |E| * r * oracle)`이 됩니다. 대회에서는 partition/graphic/linear처럼 oracle을 빠르게 만들 수 있는 구조가 있는지 먼저 봐야 합니다.

## 7. 자주 하는 실수

1. 두 조건이 matroid인지 확인하지 않고 이 모델을 적용한다.
2. exchange graph의 방향을 양쪽 matroid에서 같은 방향으로 만든다.
3. 선택 집합을 뒤집을 때 path의 inside/outside 원소를 반대로 처리한다.
4. graphic matroid에서 multi-edge와 self-loop를 빠뜨린다.
5. weighted 문제를 unweighted augmenting path로 풀려고 한다.

## 8. 문제를 볼 때 체크할 조건

- 독립 집합의 부분집합도 항상 독립인가?
- 작은 독립 집합을 큰 독립 집합의 원소로 확장할 수 있는가?
- 두 조건 중 하나가 단순 cardinality 제한이 아니라 matroid인지 확인했는가?
- 원소 수와 rank가 exchange graph를 직접 만들 수 있는 크기인가?
- 가중치가 있으면 shortest path/potential이 필요한 확장인가?

## 9. 대표 문제로 연결하기

### 문제에서 보이는 신호

- 입력 크기: 원소 수가 수백에서 수천, rank가 비교적 작음
- 필요한 복잡도: 단순 greedy나 flow 하나로 부족함
- 이 레슨의 핵심 개념: 두 독립성 조건의 exchange path

### 풀이 흐름

1. 원소와 선택 집합을 정의한다.
2. 두 조건이 어떤 matroid인지 이름을 붙인다.
3. `M1`, `M2`의 `canAdd`, `canExchange` oracle을 만든다.
4. exchange graph에서 source-sink path를 찾는다.
5. path의 원소 선택 여부를 뒤집고 반복한다.

### 자주 틀리는 지점

- "최대 forest with color limit"처럼 쉬워 보이는 문제에서도 색상 제한이 partition matroid인지 먼저 확인해야 합니다.
- 교환 간선이 많으므로 작은 테스트에서 path를 출력해 보는 것이 좋습니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: matroid intersection `/practice/...` 문제 필요 | partition matroid + partition matroid 모델링 | exchange graph |
| 표준 | TODO: graphic partition matroid `/practice/...` 문제 필요 | forest 조건과 색상 제한 결합 | DSU oracle |
| 응용 | TODO: linear matroid intersection `/practice/...` 문제 필요 | basis 독립성과 그룹 제한 결합 | linear basis |
| 함정 | TODO: weighted matroid intersection `/practice/...` 문제 필요 | unweighted 증가 경로의 한계 확인 | shortest augmenting path |
