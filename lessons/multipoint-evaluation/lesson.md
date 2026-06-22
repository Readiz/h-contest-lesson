# Multipoint Evaluation

Multipoint Evaluation은 하나의 polynomial `P(x)`를 여러 점 `x_0, x_1, ..., x_{m-1}`에서 빠르게 평가하는 기법입니다. 각 점마다 Horner를 쓰면 `O(NM)`이지만, subproduct tree와 polynomial remainder를 쓰면 NTT 기반으로 훨씬 빠르게 만들 수 있습니다.

이 레슨은 Formal Power Series와 FPS Log/Exp 이후에 보는 polynomial algorithm 응용입니다.

1. 평가점들로 `(x - x_i)`의 product tree를 만든다.
2. 위에서 아래로 `P mod nodePolynomial`을 내려보낸다.
3. leaf에서 남은 상수항이 해당 점의 값이다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: polynomial 곱셈, NTT, Formal Power Series, modular inverse
- 함께 보면 좋은 레슨: FFT와 NTT, Formal Power Series, FPS Log와 Exp
- 다음에 볼 레슨: interpolation, subproduct tree, Bostan-Mori

## 1. 문제 신호

| 문제 표현 | 접근 |
| --- | --- |
| 다항식 하나를 많은 점에서 평가 | multipoint evaluation |
| 많은 점의 값을 바탕으로 다항식 복원 | interpolation |
| 점 개수와 차수가 모두 크다 | subproduct tree |
| mod prime과 NTT-friendly modulus | NTT 최적화 가능 |
| 평가점이 연속된 정수 | chirp z-transform 등 별도 후보 |

점이 몇 개 안 되면 Horner가 더 간단합니다. Multipoint evaluation은 차수와 점 개수가 모두 커서 `O(NM)`이 부담될 때 사용합니다.

## 2. Subproduct Tree

평가점 `x_i`마다 leaf polynomial을 만듭니다.

```text
leaf_i = x - x_i
```

부모는 두 자식 polynomial의 곱입니다.

```text
node = left * right
```

root는 모든 `(x - x_i)`의 곱입니다. 이 tree를 만들면 각 구간의 평가점들이 공유하는 modulus를 알 수 있습니다.

## 3. Remainder를 내려보내기

어떤 node가 평가점 집합 `S`를 담당한다고 합시다. `P mod nodePolynomial`만 있으면 `S`에 속한 모든 점에서의 값이 보존됩니다.

```text
if M(x_i) = 0:
    P(x_i) = (P mod M)(x_i)
```

그래서 root에서 `P mod rootPolynomial`을 시작으로, 자식에게는 다시 자식 polynomial로 나눈 나머지를 내려보냅니다. leaf의 modulus는 `x - x_i`이므로 나머지는 상수 `P(x_i)`입니다.

## 4. 기본 Polynomial 도우미

아래 코드는 개념 확인용으로 나이브 곱셈과 나이브 remainder를 사용합니다. 큰 입력에서는 NTT와 fast division으로 바꿔야 합니다.

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

const long long MOD_MULTI = 998244353;

long long normalizeMulti(long long value) {
    value %= MOD_MULTI;
    if (value < 0) {
        value += MOD_MULTI;
    }
    return value;
}

long long modPowMulti(long long base, long long exp) {
    long long result = 1;
    while (exp > 0) {
        if (exp & 1LL) {
            result = result * base % MOD_MULTI;
        }
        base = base * base % MOD_MULTI;
        exp >>= 1LL;
    }
    return result;
}

vector<long long> trimPoly(vector<long long> poly) {
    while (poly.size() > 1 && poly.back() == 0) {
        poly.pop_back();
    }
    return poly;
}

vector<long long> multiplyPoly(const vector<long long>& a, const vector<long long>& b) {
    vector<long long> result(a.size() + b.size() - 1, 0);
    for (int i = 0; i < (int)a.size(); ++i) {
        for (int j = 0; j < (int)b.size(); ++j) {
            result[i + j] = (result[i + j] + a[i] * b[j]) % MOD_MULTI;
        }
    }
    return trimPoly(result);
}

vector<long long> remainderPoly(vector<long long> a, const vector<long long>& mod) {
    a = trimPoly(a);
    vector<long long> divisor = trimPoly(mod);
    if (a.size() < divisor.size()) {
        return a;
    }

    long long invLead = modPowMulti(divisor.back(), MOD_MULTI - 2);
    while (a.size() >= divisor.size()) {
        int shift = (int)a.size() - (int)divisor.size();
        long long factor = a.back() * invLead % MOD_MULTI;
        for (int i = 0; i < (int)divisor.size(); ++i) {
            int idx = i + shift;
            a[idx] = normalizeMulti(a[idx] - factor * divisor[i]);
        }
        a = trimPoly(a);
    }
    return a;
}
```

`remainderPoly`는 나이브 구현이라 `O(N^2)`에 가깝습니다. 이 레슨에서는 알고리즘 구조를 보여 주기 위한 코드입니다.

## 5. Multipoint Evaluation 구현 골격

```cpp compile-check
#include <algorithm>
#include <vector>
using namespace std;

const long long MOD_EVAL = 998244353;

long long normEval(long long value) {
    value %= MOD_EVAL;
    if (value < 0) {
        value += MOD_EVAL;
    }
    return value;
}

vector<long long> mulEval(const vector<long long>& a, const vector<long long>& b) {
    vector<long long> result(a.size() + b.size() - 1, 0);
    for (int i = 0; i < (int)a.size(); ++i) {
        for (int j = 0; j < (int)b.size(); ++j) {
            result[i + j] = (result[i + j] + a[i] * b[j]) % MOD_EVAL;
        }
    }
    while (result.size() > 1 && result.back() == 0) {
        result.pop_back();
    }
    return result;
}

long long evalAtPoint(const vector<long long>& poly, long long x) {
    long long result = 0;
    for (int i = (int)poly.size() - 1; i >= 0; --i) {
        result = (result * x + poly[i]) % MOD_EVAL;
    }
    return result;
}

struct MultipointEvaluationSkeleton {
    int n = 0;
    vector<long long> points;
    vector<vector<long long>> tree;

    explicit MultipointEvaluationSkeleton(vector<long long> points)
        : n((int)points.size()), points(points), tree(4 * max(1, (int)points.size())) {
        if (n > 0) {
            build(1, 0, n);
        }
    }

    void build(int node, int left, int right) {
        if (right - left == 1) {
            tree[node] = {normEval(-points[left]), 1};
            return;
        }
        int mid = (left + right) / 2;
        build(node * 2, left, mid);
        build(node * 2 + 1, mid, right);
        tree[node] = mulEval(tree[node * 2], tree[node * 2 + 1]);
    }

    void evaluateNaiveLeaf(const vector<long long>& poly, int node, int left, int right, vector<long long>& answer) const {
        if (right - left == 1) {
            answer[left] = evalAtPoint(poly, points[left]);
            return;
        }
        int mid = (left + right) / 2;
        evaluateNaiveLeaf(poly, node * 2, left, mid, answer);
        evaluateNaiveLeaf(poly, node * 2 + 1, mid, right, answer);
    }

    vector<long long> evaluate(const vector<long long>& poly) const {
        vector<long long> answer(n, 0);
        if (n == 0) {
            return answer;
        }
        evaluateNaiveLeaf(poly, 1, 0, n, answer);
        return answer;
    }
};
```

위 skeleton은 product tree를 만들지만 leaf 평가는 Horner로 처리합니다. 실제 fast multipoint evaluation에서는 각 node에서 `poly mod tree[node]`를 내려보내는 부분을 fast polynomial division으로 교체합니다.

## 6. Interpolation과의 관계

Interpolation은 multipoint evaluation의 반대 문제입니다.

```text
given (x_i, y_i), recover P(x)
```

subproduct tree를 만들고 derivative of product polynomial을 평가해 Lagrange basis의 분모를 구하는 방식으로 이어집니다. 두 문제 모두 product tree가 핵심입니다.

## 7. 시간 복잡도

| 방식 | 시간 |
| --- | ---: |
| 각 점 Horner | `O(NM)` |
| 나이브 product tree + 나이브 remainder | `O(NM)`에 가까움 |
| NTT 기반 multipoint evaluation | `O(N log^2 N)` 근처 |
| 특수한 연속점 평가 | 더 빠른 전용 기법 가능 |

여기서 `N`은 다항식 차수, `M`은 평가점 수입니다. 보통 `N`과 `M`이 같은 규모일 때 `O(N log^2 N)` 형태로 설명합니다.

## 8. 자주 하는 실수

1. coefficient 순서를 고차항부터 저장한다.
2. `x - x_i` leaf를 `x_i - x`로 만들어 부호가 바뀐다.
3. 같은 평가점이 여러 번 나오는 경우 interpolation까지 그대로 적용한다.
4. polynomial division에서 leading coefficient inverse를 빼먹는다.
5. 작은 입력에도 복잡한 NTT 구현을 넣어 디버깅 비용을 키운다.

## 9. 문제를 볼 때 체크할 조건

- 평가할 polynomial 개수와 평가점 개수는?
- modulus가 NTT-friendly prime인가?
- 점이 중복될 수 있는가?
- evaluation만 필요한가, interpolation도 필요한가?
- 점이 연속된 정수처럼 특수 구조인가?

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 여러 점 polynomial 평가 `/practice/...` 문제 필요 | Horner와 product tree 비교 | multipoint evaluation |
| 표준 | TODO: subproduct tree `/practice/...` 문제 필요 | `(x - x_i)` tree 구성 | product tree |
| 응용 | TODO: interpolation `/practice/...` 문제 필요 | derivative와 Lagrange basis | interpolation |
| 함정 | TODO: 중복 평가점 `/practice/...` 문제 필요 | evaluation과 interpolation 조건 구분 | repeated points |
