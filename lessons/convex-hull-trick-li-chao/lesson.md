# Convex Hull Trick과 Li Chao Tree

Convex Hull Trick은 여러 직선 중 특정 x에서 최솟값이나 최댓값을 빠르게 찾는 기법입니다. DP 전이가 `dp[i] = min_j(a_j * x_i + b_j)` 꼴로 정리되면, 각 후보 `j`를 직선으로 보고 query를 빠르게 처리할 수 있습니다.

이 레슨은 DP 최적화와 자료구조가 만나는 지점으로 Convex Hull Trick과 Li Chao Tree를 봅니다.

1. DP 전이를 직선과 점 query로 바꾼다.
2. slope가 정렬된 경우의 deque CHT를 이해한다.
3. 일반 삽입/질의에는 Li Chao Tree를 사용한다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 일차함수, 이분 탐색, Segment Tree, DP 전이
- 함께 보면 좋은 레슨: 동적 계획법, Segment Tree, Matrix Exponentiation
- 다음에 볼 레슨: divide-and-conquer DP optimization, dynamic Li Chao, kinetic hull

## 1. 문제 신호

아래처럼 후보 `j`와 현재 `i`가 곱으로 분리되면 CHT를 의심합니다.

```text
dp[i] = min_j(dp[j] + A[j] * X[i] + B[j])
```

`j`마다 직선 `y = A[j] * x + (dp[j] + B[j])`를 만들고, `x = X[i]`에서 최소 y를 query합니다.

| 조건 | 어울리는 구현 |
| --- | --- |
| slope가 단조로 추가되고 x query도 단조 | deque CHT |
| slope만 단조 | hull + binary search |
| 삽입 순서와 query 순서가 일반적 | Li Chao Tree |
| x좌표 범위가 크지만 query 좌표만 안다 | 좌표 압축 Li Chao |

## 2. 직선으로 바꾸는 법

예를 들어 전이가 아래라고 합시다.

```text
dp[i] = min_j(dp[j] + m[j] * x[i] + c[j])
```

후보 `j`가 정해지면 `m[j]`와 `dp[j] + c[j]`는 고정입니다. 따라서 line을 추가하고, 현재 `x[i]`에서 가장 작은 값을 묻습니다.

중요한 것은 변형 후 후보마다 x의 계수와 절편이 현재 i와 독립이어야 한다는 점입니다. `j`와 `i`가 더 복잡하게 섞이면 CHT가 바로 적용되지 않습니다.

## 3. Li Chao Tree

Li Chao Tree는 x좌표 구간을 Segment Tree처럼 나누고, 각 node에 그 구간 중앙에서 좋은 직선을 저장합니다. 새 직선을 넣을 때 기존 직선과 비교해 더 좋은 쪽을 node에 남기고, 밀려난 직선을 한쪽 child로 내려보냅니다.

아래 구현은 정수 x 범위 `[xLeft, xRight]`에서 최솟값을 구합니다.

```cpp compile-check
#include <algorithm>
#include <limits>
#include <vector>
using namespace std;

struct LiChaoTree {
    struct Line {
        long long m = 0;
        long long b = numeric_limits<long long>::max() / 4;

        long long value(long long x) const {
            return m * x + b;
        }
    };

    struct Node {
        Line line;
        int left = -1;
        int right = -1;
    };

    long long xLeft;
    long long xRight;
    vector<Node> tree;

    LiChaoTree(long long xLeft, long long xRight) : xLeft(xLeft), xRight(xRight) {
        tree.push_back(Node{});
    }

    int newNode() {
        tree.push_back(Node{});
        return (int)tree.size() - 1;
    }

    void addLine(Line line) {
        addLine(0, xLeft, xRight, line);
    }

    void addLine(int node, long long left, long long right, Line line) {
        long long mid = (left + right) / 2;
        bool betterLeft = line.value(left) < tree[node].line.value(left);
        bool betterMid = line.value(mid) < tree[node].line.value(mid);

        if (betterMid) {
            swap(line, tree[node].line);
        }
        if (left == right) {
            return;
        }

        if (betterLeft != betterMid) {
            if (tree[node].left == -1) {
                tree[node].left = newNode();
            }
            addLine(tree[node].left, left, mid, line);
        } else {
            if (tree[node].right == -1) {
                tree[node].right = newNode();
            }
            addLine(tree[node].right, mid + 1, right, line);
        }
    }

    long long query(long long x) const {
        return query(0, xLeft, xRight, x);
    }

    long long query(int node, long long left, long long right, long long x) const {
        long long result = tree[node].line.value(x);
        if (left == right) {
            return result;
        }
        long long mid = (left + right) / 2;
        if (x <= mid && tree[node].left != -1) {
            result = min(result, query(tree[node].left, left, mid, x));
        }
        if (x > mid && tree[node].right != -1) {
            result = min(result, query(tree[node].right, mid + 1, right, x));
        }
        return result;
    }
};
```

이 구현은 x 범위가 정수이고 `m * x + b`가 `long long` 범위에 들어간다는 전제가 있습니다. 값이 더 커질 수 있으면 `__int128`을 고려합니다.

## 4. 좌표 압축 Li Chao

query가 나올 x좌표를 모두 미리 알 수 있다면, 실제 x값 전체 범위 대신 query 좌표 배열 위에서만 Li Chao Tree를 만들 수 있습니다.

| 방식 | 장점 | 주의점 |
| --- | --- | --- |
| 전체 정수 범위 Li Chao | 온라인 query 가능 | 범위와 overflow 주의 |
| 좌표 압축 Li Chao | 필요한 x만 관리 | 모든 query x를 미리 알아야 함 |
| deque CHT | 매우 빠르고 간단 | slope/query 단조 조건 필요 |

좌표 압축 방식에서도 line의 값은 압축 index가 아니라 실제 x좌표에서 계산해야 합니다.

## 5. Deque CHT 조건

Deque CHT는 구현이 더 짧고 빠르지만 조건이 강합니다.

1. 직선의 slope가 단조 순서로 추가된다.
2. query x도 단조 순서로 들어온다.
3. 최솟값 또는 최댓값 중 하나로 고정된다.

이 조건이 깨지면 front에서 pop하는 방식이 틀릴 수 있습니다. 문제에서 정렬로 slope와 query 순서를 맞출 수 있는지 먼저 확인합니다.

## 6. DP 적용 절차

1. 원래 전이를 `j` 후보와 `i` query로 분리한다.
2. 후보 `j`의 line slope와 intercept를 적는다.
3. 현재 `i`의 x값을 적는다.
4. `dp[i] = query(x)` 뒤에 현재 i의 line을 추가할지, 먼저 추가할지 순서를 정한다.
5. 자기 자신을 후보로 쓰면 안 되는 문제인지 확인한다.

line 추가 순서가 오답을 만드는 경우가 많습니다. `j < i`만 허용되면 query 후 add 또는 add 후 query를 문제에 맞게 고정해야 합니다.

## 7. 시간 복잡도

| 작업 | 시간 | 메모리 |
| --- | ---: | ---: |
| Li Chao line 추가 | `O(log X)` | 동적 node |
| Li Chao query | `O(log X)` | 없음 |
| 좌표 압축 Li Chao | `O(log Q)` | `O(Q)` |
| 단조 deque CHT | amortized `O(1)` | `O(N)` |

여기서 `X`는 x좌표 범위 크기, `Q`는 압축된 query x 개수입니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| DP 전이를 직선으로 잘못 분리 | 전혀 다른 값 query | slope/intercept/x를 식으로 다시 확인 |
| x 범위를 너무 좁게 잡음 | query 누락 | 모든 query x의 min/max 확인 |
| 최댓값 문제에 최솟값 Li Chao 사용 | 부호 반대 오답 | line 부호를 뒤집거나 비교 변경 |
| 같은 slope 처리 누락 | 불필요한 line 또는 overflow | 더 좋은 intercept만 남기기 |
| `m*x+b` overflow | 음수 wrap | `long long` 범위 계산 |
| 자기 자신 line을 먼저 추가 | 불가능한 전이 사용 | add/query 순서 점검 |

## 9. 문제를 볼 때 체크할 조건

1. 전이가 `m_j * x_i + b_j` 꼴로 분리되는가?
2. 최솟값인지 최댓값인지 명확한가?
3. line 추가와 query 순서가 온라인으로 가능한가?
4. slope나 query x가 단조라 더 단순한 CHT를 쓸 수 있는가?
5. x 범위와 값 범위가 자료형 안에 들어오는가?
6. 후보가 없는 초기 상태의 INF 처리를 했는가?

Convex Hull Trick은 이름과 달리 대회에서는 DP 전이 변형 도구로 더 자주 만납니다. 식을 직선으로 분리하는 순간, 남은 일은 문제 조건에 맞는 hull 구현을 고르는 것입니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 단조 slope CHT `/practice/...` 문제 필요 | 직선 추가와 단조 x query | deque CHT |
| 표준 | TODO: Li Chao Tree 기본 `/practice/...` 문제 필요 | 임의 순서 line과 point query | Li Chao |
| 응용 | TODO: DP 전이 최적화 `/practice/...` 문제 필요 | `m_j*x_i+b_j`로 식 변형 | CHT DP |
| 함정 | TODO: 큰 좌표와 overflow `/practice/...` 문제 필요 | x 범위, INF, `m*x+b` 점검 | overflow |
