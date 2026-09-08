# Matrix-Tree Theorem Applications

Matrix-Tree Theorem은 그래프의 spanning tree 개수를 Laplacian matrix의 cofactor determinant로 계산하는 정리입니다. 단순 count뿐 아니라 edge criticality, rooted arborescence, graph reliability 모델링으로 이어집니다.


cofactor 입력은 n>=1, 유효한 정점·removed, 양수 mod를 받습니다. n=1이면 0x0 determinant를 1로 정의하여 단일 정점 tree 하나를 셉니다. 간선 포함 contraction 공식은 self-loop가 아닌 특정 간선에 적용합니다.

## 문제 신호

| 문제 표현 | Matrix-Tree 관점 |
| --- | --- |
| spanning tree의 개수를 묻는다 | Laplacian cofactor |
| 특정 간선을 반드시 포함하거나 제외한다 | contraction/deletion 또는 minor |
| directed rooted tree count가 필요하다 | directed Matrix-Tree |
| 모든 tree를 나열할 수 없다 | determinant로 count |
| modulo prime으로 답을 요구한다 | modular determinant |

트리 개수는 조합적으로 커지기 쉽습니다. Matrix-Tree Theorem은 count 문제를 `O(N^3)` determinant 문제로 낮춥니다.

## Undirected Laplacian

무향 그래프의 Laplacian `L`은 아래처럼 만듭니다.

```text
L[i][i] = degree(i)
L[i][j] = -number_of_edges(i, j), i != j
```

정점 하나 `r`을 고르고, `r`행과 `r`열을 지운 matrix의 determinant가 spanning tree 개수입니다.

```text
treeCount(G) = det(L without row r and column r)
```

어떤 정점을 지워도 값은 같습니다. Multi-edge가 있으면 off-diagonal에 간선 수만큼 더하고 빼야 합니다.

## 작은 예시

삼각형 그래프 `1-2-3-1`을 보겠습니다.

```text
L = [ 2 -1 -1
     -1  2 -1
     -1 -1  2 ]
```

3번 정점의 행과 열을 지우면 아래 matrix가 됩니다.

```text
[ 2 -1
 -1  2 ]
```

determinant는 `4 - 1 = 3`입니다. 실제로 삼각형에서 간선 하나를 빼는 3가지가 spanning tree입니다.

## Modular 구현 골격

Laplacian을 만든 뒤 cofactor determinant를 계산합니다.

```cpp
vector<vector<long long>> buildCofactor(
    int n,
    const vector<pair<int, int>>& edges,
    long long mod,
    int removed
) {
    vector<vector<long long>> laplacian(n, vector<long long>(n, 0));
    for (auto [u, v] : edges) {
        if (u == v) continue;
        laplacian[u][u] = (laplacian[u][u] + 1) % mod;
        laplacian[v][v] = (laplacian[v][v] + 1) % mod;
        laplacian[u][v] = (laplacian[u][v] + mod - 1) % mod;
        laplacian[v][u] = (laplacian[v][u] + mod - 1) % mod;
    }

    vector<vector<long long>> matrix;
    for (int i = 0; i < n; ++i) {
        if (i == removed) {
            continue;
        }
        vector<long long> row;
        for (int j = 0; j < n; ++j) {
            if (j != removed) {
                row.push_back(laplacian[i][j]);
            }
        }
        matrix.push_back(row);
    }
    return matrix;
}
```

determinant 함수는 Randomized Determinant 레슨의 modular Gaussian elimination을 그대로 재사용할 수 있습니다.

## Directed Arborescence

방향 그래프에서는 root로 들어오는 arborescence인지, root에서 나가는 arborescence인지에 따라 Laplacian 방향이 달라집니다.

일반적인 기준 하나를 고르면 아래처럼 둡니다.

```text
edge u -> v
in-degree Laplacian:
L[v][v] += 1
L[v][u] -= 1
```

이 in-degree Laplacian에서 root r의 행·열을 지운 determinant는 root에서 바깥으로 뻗는 arborescence를 셉니다. root로 모이는 tree는 out-degree Laplacian을 사용합니다. `0->1` 한 간선에서 root 0의 outward count가 1인지 검산하면 방향을 고정할 수 있습니다.

## 간선 포함과 제외

특정 간선 `e`를 제외한 spanning tree 수는 그 간선을 제거한 그래프에서 다시 Matrix-Tree를 계산하면 됩니다.

특정 간선 `e = (u, v)`를 반드시 포함하는 tree 수는 `e`를 contraction한 그래프의 spanning tree 수와 같습니다.

```text
count(include e) = treeCount(G / e)
count(exclude e) = treeCount(G - e)
```

모든 간선에 대해 이 값을 하나씩 계산하면 너무 느릴 수 있습니다. 그때는 effective resistance나 Laplacian inverse 같은 고급 도구가 필요하지만, 기본 문제에서는 contraction/deletion 관점만으로도 모델링이 됩니다.

## 시간 복잡도

| 작업 | 시간 |
| --- | ---: |
| Laplacian 구성 | `O(N^2 + M)` 또는 sparse 구성 |
| determinant 1회 | `O(N^3)` |
| 간선별 재계산 | `O(MN^3)` |
| sparse/특수 그래프 최적화 | 문제 구조에 따라 다름 |

정점 수가 수백 정도면 dense determinant가 가능합니다. 정점 수가 수천 이상이면 sparse structure, modulo 특성, 또는 그래프 형태를 더 이용해야 합니다.

검산할 때는 완전 그래프의 spanning tree 수 `n^(n-2)`와, 연결되지 않은 그래프의 cofactor determinant가 0인 경우를 비교합니다.
