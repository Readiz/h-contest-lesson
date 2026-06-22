# Monge와 SMAWK

Monge array는 행과 열의 최솟값 위치가 단조로 움직이는 특수한 행렬입니다. 이런 구조에서는 각 행의 최솟값을 모든 열에 대해 직접 보지 않고도 빠르게 찾을 수 있습니다. SMAWK는 totally monotone matrix에서 행 최솟값을 선형에 가깝게 구하는 알고리즘입니다.

이 레슨은 Knuth Optimization 이후에 보는 더 일반적인 monotone optimization 관점을 정리합니다.

1. Monge inequality와 totally monotone 조건을 구분한다.
2. row minimum index가 단조로 움직이는 이유를 이해한다.
3. SMAWK의 column reduction과 odd/even row recursion을 익힌다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: DP 최적화, 단조성 증명, Knuth Optimization
- 함께 보면 좋은 레슨: Divide and Conquer DP Optimization, Knuth Optimization
- 다음에 볼 레슨: Monge DP, min-plus convolution, SMAWK applications

## 1. Monge Array

행렬 `A`가 Monge라는 것은 모든 `i1 < i2`, `j1 < j2`에 대해 아래가 성립한다는 뜻입니다.

```text
A[i1][j1] + A[i2][j2] <= A[i1][j2] + A[i2][j1]
```

직관적으로는 "왼쪽 위와 오른쪽 아래를 짝짓는 것이 교차 짝짓기보다 좋다"는 성질입니다. 이 성질이 있으면 각 행의 argmin이 오른쪽으로 갈수록 왼쪽으로 되돌아가지 않습니다.

## 2. Totally Monotone

SMAWK가 요구하는 조건은 Monge보다 약한 totally monotone입니다.

```text
어떤 두 행 i1 < i2와 두 열 j1 < j2에 대해
A[i1][j1] <= A[i1][j2] 이면 A[i2][j1] <= A[i2][j2]
```

이 조건은 row minimum의 단조성을 보장합니다. Monge array는 totally monotone이지만, totally monotone이 항상 Monge인 것은 아닙니다.

## 3. 언제 쓰는가

| 문제 신호 | 접근 |
| --- | --- |
| 각 행의 최솟값 열을 찾아야 한다 | row minima |
| cost matrix가 Monge다 | SMAWK 또는 divide-and-conquer |
| DP 전이가 `min_j cost(i,j)` 행렬 형태다 | monotone optimization |
| 행/열 수가 크고 모든 값을 만들 수 없다 | implicit matrix query |

SMAWK는 행렬 값을 전부 저장하지 않고 `value(row, col)` 함수로 계산할 수 있을 때 특히 유용합니다.

## 4. 단순 monotone row minima

SMAWK 전체 구현은 까다롭습니다. 먼저 row minimum이 단조일 때 divide-and-conquer로 찾는 구조를 이해하면 좋습니다.

```cpp compile-check
#include <functional>
#include <limits>
#include <utility>
#include <vector>
using namespace std;

void monotoneRowMinima(
    int rowLeft,
    int rowRight,
    int colLeft,
    int colRight,
    const function<long long(int, int)>& value,
    vector<int>& answer
) {
    if (rowLeft > rowRight) {
        return;
    }

    int rowMid = (rowLeft + rowRight) / 2;
    pair<long long, int> best = {numeric_limits<long long>::max() / 4, colLeft};
    for (int col = colLeft; col <= colRight; ++col) {
        long long current = value(rowMid, col);
        if (current < best.first) {
            best = {current, col};
        }
    }

    answer[rowMid] = best.second;
    monotoneRowMinima(rowLeft, rowMid - 1, colLeft, best.second, value, answer);
    monotoneRowMinima(rowMid + 1, rowRight, best.second, colRight, value, answer);
}
```

이 방식은 SMAWK보다 느릴 수 있지만, 단조 argmin을 쓰는 기본 패턴을 보여 줍니다.

## 5. SMAWK 흐름

SMAWK는 두 단계를 반복합니다.

1. Column reduction: 필요 없는 열을 stack처럼 제거한다.
2. 홀수 행의 최솟값을 재귀적으로 구한다.
3. 짝수 행은 주변 홀수 행의 최솟값 범위 사이에서만 찾는다.

핵심은 totally monotone 조건 덕분에 어떤 열이 이후 행에서도 최솟값이 될 수 없음을 판정할 수 있다는 점입니다.

## 6. SMAWK 구현 스케치

아래 코드는 개념을 보여 주는 간단한 형태입니다. 행과 열은 0-index 배열로 넘깁니다.

```cpp compile-check
#include <functional>
#include <vector>
using namespace std;

void smawk(
    const vector<int>& rows,
    const vector<int>& cols,
    const function<long long(int, int)>& value,
    vector<int>& answer
) {
    if (rows.empty()) {
        return;
    }

    vector<int> reducedCols;
    for (int col : cols) {
        while (!reducedCols.empty()) {
            int row = rows[(int)reducedCols.size() - 1];
            int lastCol = reducedCols.back();
            if (value(row, col) < value(row, lastCol)) {
                reducedCols.pop_back();
            } else {
                break;
            }
        }
        if ((int)reducedCols.size() < (int)rows.size()) {
            reducedCols.push_back(col);
        }
    }

    vector<int> oddRows;
    for (int i = 1; i < (int)rows.size(); i += 2) {
        oddRows.push_back(rows[i]);
    }
    smawk(oddRows, reducedCols, value, answer);

    int start = 0;
    for (int i = 0; i < (int)rows.size(); i += 2) {
        int row = rows[i];
        int end = (int)reducedCols.size() - 1;
        if (i + 1 < (int)rows.size()) {
            while (reducedCols[end] != answer[rows[i + 1]]) {
                --end;
            }
        }

        int bestCol = reducedCols[start];
        for (int j = start; j <= end; ++j) {
            if (value(row, reducedCols[j]) < value(row, bestCol)) {
                bestCol = reducedCols[j];
            }
        }
        answer[row] = bestCol;
        start = end;
    }
}
```

실전에서는 tie-breaking, 행/열 id 압축, `value` 호출 비용을 더 세심하게 관리해야 합니다. 처음에는 monotone divide-and-conquer로 충분한지 먼저 확인하는 편이 안전합니다.

## 7. DP와 연결

DP 전이가 아래처럼 행렬 최솟값 찾기로 바뀌면 Monge/SMAWK 후보가 됩니다.

```text
dp[i] = min_j previous[j] + cost(j, i)
```

`A[i][j] = previous[j] + cost(j, i)`라고 보면, 각 row `i`의 minimum column `j`를 찾는 문제입니다. 이 행렬이 totally monotone이면 SMAWK를 쓸 수 있습니다.

## 8. 시간 복잡도

| 방법 | 시간 |
| --- | ---: |
| 모든 행/열 확인 | `O(RC)` |
| monotone D&C row minima | `O(R log R * 후보)` 형태 |
| SMAWK | `O(R + C)` value calls 수준 |

SMAWK의 이론적 성능은 좋지만 구현 실수 비용도 큽니다. value 계산이 비싸면 호출 횟수 관리가 중요합니다.

## 9. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| Monge/totally monotone 증명 없이 적용 | 오답 | inequality 또는 editorial 확인 |
| 최소/최대 방향 혼동 | 반대 최적값 | 비교 연산 통일 |
| tie-breaking 불안정 | 단조성 흔들림 | 같은 값일 때 작은 column 유지 |
| value 함수가 범위 밖을 허용 | 런타임 오류 | valid column set 제한 |
| SMAWK reduced column stack index 혼동 | 열 누락 | rows size와 stack size 관계 확인 |
| D&C 최적화와 SMAWK 조건 혼동 | 과한 구현 | 필요한 row minima 형태인지 확인 |

## 10. 문제를 볼 때 체크할 조건

1. 문제를 행별 최솟값 찾기로 바꿀 수 있는가?
2. 행의 argmin이 단조로 움직이는가?
3. Monge inequality나 totally monotone 조건을 보일 수 있는가?
4. 행렬 값을 저장하지 않고 계산할 수 있는가?
5. 일반 D&C optimization으로 충분하지 않은가?
6. tie-breaking을 단조성에 맞춰 고정했는가?

Monge와 SMAWK는 자주 쓰이는 편은 아니지만, 맞는 문제에서는 매우 강합니다. 적용 전 조건 확인이 거의 전부이며, 구현은 작은 테스트로 row minima 단조성을 먼저 검증하는 습관이 좋습니다.

## 11. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: Monge row minima `/practice/...` 문제 필요 | argmin 단조성 확인 | Monge array |
| 표준 | TODO: monotone row minima DP `/practice/...` 문제 필요 | D&C row minima 구현 | totally monotone |
| 응용 | TODO: SMAWK 적용 `/practice/...` 문제 필요 | column reduction과 odd row recursion | SMAWK |
| 함정 | TODO: Monge가 아닌 행렬 `/practice/...` 문제 필요 | 적용 조건 반례 찾기 | inequality |
