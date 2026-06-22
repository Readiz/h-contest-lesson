# Cut Sparsification

Cut Sparsification은 그래프의 모든 cut 값을 정확히 또는 근사적으로 보존하면서 edge 수를 줄이는 관점입니다. 대회 문제에서는 이론적인 spectral sparsifier보다, MST/forest 기반 certificate, Nagamochi-Ibaraki 스타일의 edge connectivity 보존, cut 후보를 줄이는 모델링으로 자주 등장합니다.

이 레슨은 Global Min Cut, Gomory-Hu Tree, Max Flow/Min Cut 이후에 보는 그래프 심화입니다.

1. cut value를 보존해야 하는 범위가 global min cut인지, 모든 작은 cut인지 구분한다.
2. sparse certificate는 "작은 cut을 망가뜨리지 않는 edge subset"으로 이해한다.
3. min cut 응용에서 불필요한 큰 connectivity edge를 제거해 계산량을 줄이는 흐름을 익힌다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: undirected cut, global min cut, edge connectivity, spanning forest
- 함께 보면 좋은 레슨: Global Min Cut, Gomory-Hu Tree, Max Flow와 Min Cut
- 다음에 볼 레슨: Global Min Cut Applications, cactus representation, randomized contraction

## 1. 문제 신호

| 문제 표현 | Cut Sparsification 관점 |
| --- | --- |
| edge가 너무 많지만 작은 cut만 중요 | sparse certificate |
| k-edge-connected 여부만 필요 | k-certificate |
| global min cut 값을 빠르게 반복 계산 | small cut 보존 |
| 모든 cut을 정확히 보존할 필요는 없음 | thresholded cut preservation |
| dense graph에서 edge pruning 가능 | spanning forest layering |

핵심은 "어떤 cut을 보존해야 하는가"입니다. 모든 cut 값을 정확히 보존하려면 원래 그래프와 거의 같은 정보가 필요할 수 있지만, 작은 cut이나 connectivity threshold만 보면 훨씬 줄일 수 있습니다.

## 2. Sparse Certificate 직관

무향 unweighted graph에서 k-edge-connectivity를 확인하려면 모든 edge가 필요하지 않을 수 있습니다. 여러 번 spanning forest를 뽑아 합치면 작은 cut을 건드리는 edge를 일정 수준 보존할 수 있습니다.

```text
repeat k times:
  남은 edge로 spanning forest를 만든다
  forest edge를 certificate에 넣는다
  forest edge를 남은 edge에서 제거한다
```

어떤 cut의 크기가 k 이하라면, 각 forest는 그 cut을 건너는 edge를 적어도 하나 포함하려고 합니다. 그래서 작은 cut은 certificate 안에서도 관찰됩니다.

## 3. Cut Threshold

문제에서 "min cut이 k보다 작은가?"만 필요하면, cut 값이 큰 부분을 정확히 보존할 필요가 없습니다.

| 목표 | 보존해야 할 정보 |
| --- | --- |
| global min cut 값 전체 | 모든 최소 cut 후보 |
| min cut `< k` 판정 | k 미만 cut |
| k-edge-connected 판정 | k보다 작은 cut이 없음 |
| 모든 쌍 min cut 질의 | Gomory-Hu 또는 더 강한 구조 |

threshold가 있으면 sparse certificate가 실용적입니다. 반대로 정확한 모든 pair cut 값이 필요하면 sparsification만으로는 부족합니다.

## 4. Forest Layer Certificate

아래 코드는 unweighted undirected graph에서 forest layer를 최대 `k`번 뽑아 certificate edge를 만드는 뼈대입니다. 실제 문제에서는 multi-edge id와 edge removal을 정확히 관리해야 합니다.

```cpp compile-check
#include <numeric>
#include <tuple>
#include <vector>
using namespace std;

struct CutCertificate {
    struct Dsu {
        vector<int> parent;
        vector<int> size;

        explicit Dsu(int n) : parent(n), size(n, 1) {
            iota(parent.begin(), parent.end(), 0);
        }

        int find(int x) {
            while (parent[x] != x) {
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

    static vector<int> build(int n, const vector<pair<int, int>>& edges, int layers) {
        vector<int> alive(edges.size(), 1);
        vector<int> certificate;

        for (int round = 0; round < layers; ++round) {
            Dsu dsu(n);
            vector<int> picked;
            for (int id = 0; id < (int)edges.size(); ++id) {
                if (!alive[id]) {
                    continue;
                }
                if (dsu.unite(edges[id].first, edges[id].second)) {
                    picked.push_back(id);
                    certificate.push_back(id);
                }
            }
            if (picked.empty()) {
                break;
            }
            for (int id : picked) {
                alive[id] = 0;
            }
        }

        return certificate;
    }
};
```

이 코드는 개념 확인용입니다. weighted graph, directed graph, exact min cut preservation은 별도 조건이 필요합니다.

## 5. Min Cut과의 연결

Cut sparsification은 보통 min cut 알고리즘을 대체하기보다 앞단에서 edge 수를 줄이는 역할을 합니다.

```text
dense graph
  -> small cut을 보존하는 certificate 추출
  -> certificate 위에서 min cut 또는 connectivity 판정
  -> 필요한 경우 원래 graph로 후보 검증
```

특히 반복적으로 min cut 후보를 검사하거나, k가 작은 connectivity 판정이면 효과가 큽니다.

## 6. 정확 보존과 근사 보존

| 종류 | 설명 | 대회에서의 쓰임 |
| --- | --- | --- |
| exact sparse certificate | threshold 이하 cut을 정확히 보존 | k-edge-connected 판정 |
| cut-equivalent tree | 모든 pair min cut 값을 tree path min으로 표현 | Gomory-Hu Tree |
| randomized contraction | min cut 후보를 확률적으로 보존 | Karger 계열 |
| spectral/cut sparsifier | 모든 cut을 근사 보존 | 이론 지향, 구현 부담 큼 |

문제에서 "정확히"와 "확률적으로"와 "근사"가 섞이지 않게 조건을 읽어야 합니다.

## 7. 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| forest layer 1회 | `O(M alpha(N))` |
| k-layer certificate | `O(k M alpha(N))` |
| certificate edge 수 | 최대 `k(N-1)` |
| 이후 min cut | certificate 크기에 따라 감소 |

k가 작을 때 edge 수가 `M`에서 `O(kN)`으로 줄어드는 것이 핵심 이점입니다.

## 8. 자주 하는 실수

1. directed graph에 undirected certificate 논리를 그대로 적용한다.
2. weighted cut에서 unweighted forest layer를 그대로 쓰면 된다고 가정한다.
3. threshold 이하 cut만 보존하는데 모든 cut 값이 보존된다고 착각한다.
4. certificate를 만든 뒤 원래 그래프 기준 검증이 필요한 문제에서 검증을 생략한다.
5. multi-edge를 하나로 합치며 cut capacity를 잃어버린다.

## 9. 문제를 볼 때 체크할 조건

- 그래프가 무향 unweighted인가?
- 필요한 것은 cut 값인가, k-edge-connected 판정인가?
- 작은 cut만 보존하면 충분한가?
- `k`가 작아서 `O(kM)` 전처리가 의미 있는가?
- certificate 위 답을 원래 그래프에서 다시 검증해야 하는가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: cut sparsification `/practice/...` 문제 필요 | forest certificate 이해 | k-edge connectivity |
| 표준 | TODO: sparse certificate min cut `/practice/...` 문제 필요 | 작은 cut 보존 | spanning forest layers |
| 응용 | TODO: repeated connectivity threshold `/practice/...` 문제 필요 | dense graph pruning | certificate verification |
| 함정 | TODO: weighted cut certificate `/practice/...` 문제 필요 | 적용 조건 구분 | weighted vs unweighted |
