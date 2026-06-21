# Testing과 Stress Test

알고리즘 문제를 풀 때 예제만 맞는다고 정답이라고 볼 수 없습니다. 특히 그리디, DP, 자료구조, 기하 문제는 작은 반례 하나로 틀릴 수 있습니다. Testing과 Stress Test는 풀이를 제출하기 전에 오답 가능성을 줄이는 검증 절차입니다.

이 레슨은 아래 네 가지를 다룹니다.

1. 예제 테스트와 직접 만든 edge case를 구분한다.
2. 느리지만 확실한 brute force를 만든다.
3. random generator로 많은 작은 입력을 만든다.
4. 빠른 풀이와 brute force를 비교해 반례를 찾는다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 대회용 C++ 기본기, 복잡도와 입력 크기 감각
- 함께 보면 좋은 레슨: 그리디 알고리즘, 동적 계획법, 기하 기본
- 다음에 볼 레슨: Proof와 Invariant

## 1. 테스트의 층위

테스트는 한 종류가 아닙니다.

| 테스트 | 목적 |
| --- | --- |
| 예제 테스트 | 입출력 형식과 기본 동작 확인 |
| 직접 만든 edge case | 경계 조건 확인 |
| brute force 비교 | 작은 입력에서 정답성 확인 |
| random stress | 생각하지 못한 반례 탐색 |
| 최대 입력 성능 테스트 | 시간/메모리 확인 |

예제는 최소 기준입니다. 예제가 맞아도 indexing, overflow, tie-break, 빈 집합, 중복 값, collinear 같은 케이스는 따로 확인해야 합니다.

## 2. Edge Case 목록 만들기

문제를 읽으면 바로 작은 체크리스트를 만듭니다.

| 조건 | 예시 |
| --- | --- |
| 최소 크기 | `n = 0`, `n = 1`, 빈 문자열, 간선 없음 |
| 최대 값 | 좌표 `10^9`, 비용 합 `10^18`, 배열 길이 최대 |
| 중복 | 같은 값 여러 개, 같은 간선 여러 개, 같은 점 |
| 경계 접촉 | 구간 끝점, 선분 끝점, inclusive/exclusive |
| 불가능 상태 | 도달 불가, 답 없음, 음수 사이클, 모순 |
| tie-break | 같은 점수, 같은 거리, 같은 정렬 기준 |

이 목록은 풀이보다 먼저 적어도 좋습니다. 문제의 함정이 보통 경계 조건에 있기 때문입니다.

## 3. Brute Force 만들기

Brute force는 느리지만 작은 입력에서 확실한 답을 주는 코드입니다. 빠른 풀이를 검증하기 위한 기준으로 씁니다.

예를 들어 구간의 서로 다른 값 개수를 빠르게 구하는 풀이를 작성한다면, 작은 입력에서는 직접 세면 됩니다.

```cpp compile-check
#include <set>
#include <vector>
using namespace std;

int bruteDistinctCount(const vector<int>& a, int left, int right) {
    set<int> values;
    for (int i = left; i <= right; ++i) {
        values.insert(a[i]);
    }
    return (int)values.size();
}
```

Brute force는 짧고 명확해야 합니다. 빠른 풀이와 같은 아이디어를 공유하면 같은 버그를 가질 수 있습니다.

## 4. Random Generator와 비교 루프

Stress test는 작은 입력을 무작위로 많이 만들고, 빠른 풀이와 brute force의 답을 비교합니다.

```cpp compile-check
#include <cassert>
#include <random>
#include <set>
#include <vector>
using namespace std;

int bruteDistinctCount(const vector<int>& a, int left, int right) {
    set<int> values;
    for (int i = left; i <= right; ++i) {
        values.insert(a[i]);
    }
    return (int)values.size();
}

int fastDistinctCountForDemo(const vector<int>& a, int left, int right) {
    return bruteDistinctCount(a, left, right);
}

void stressDistinctCount() {
    mt19937 rng(1);
    for (int test = 0; test < 1000; ++test) {
        int n = 1 + (int)(rng() % 8);
        vector<int> a(n);
        for (int i = 0; i < n; ++i) {
            a[i] = (int)(rng() % 5);
        }
        int left = (int)(rng() % n);
        int right = (int)(rng() % n);
        if (left > right) {
            swap(left, right);
        }

        int expected = bruteDistinctCount(a, left, right);
        int actual = fastDistinctCountForDemo(a, left, right);
        assert(expected == actual);
    }
}
```

실제 제출 코드에 stress loop를 넣으면 안 됩니다. 로컬에서 반례를 찾는 별도 모드로 두고, 제출 전에는 제거하거나 `#ifdef LOCAL`로 감쌉니다.

## 5. 반례를 찾았을 때

Stress test가 실패하면 입력을 출력해야 합니다. 그래야 재현하고 디버깅할 수 있습니다.

반례를 찾은 뒤에는 바로 코드를 고치기보다 아래 순서로 봅니다.

1. brute force가 정말 맞는가?
2. 빠른 풀이의 전제 조건이 깨졌는가?
3. indexing이나 inclusive/exclusive가 틀렸는가?
4. tie-break 또는 중복 처리가 빠졌는가?
5. overflow가 있는가?

반례 하나를 고친 뒤에는 같은 stress test를 더 오래 돌립니다. 고친 버그가 다른 케이스를 깨뜨릴 수 있습니다.

## 6. 성능 테스트

정답성이 맞아도 시간 안에 들어와야 합니다. 최대 입력을 직접 생성해 로컬에서 실행 시간을 봅니다.

성능 테스트에서는 답이 맞는지보다 아래를 봅니다.

- 입력 생성과 파싱이 병목인지
- `O(n log n)`이라고 생각한 코드 안에 `substr`, `erase`, `map` 중첩이 숨어 있는지
- 메모리가 제한을 넘는지
- 재귀 깊이가 큰지

성능 테스트는 로컬 환경과 채점 환경이 다르므로 절대 기준은 아닙니다. 그래도 명백한 `O(n^2)` 실수나 큰 메모리 사용은 잡을 수 있습니다.

## 7. assert와 local debug

`assert`는 "내 풀이의 불변식이 깨지지 않는다"를 확인하는 데 좋습니다.

```cpp compile-check
#include <cassert>
#include <vector>
using namespace std;

void checkIndex(int index, const vector<int>& a) {
    assert(0 <= index && index < (int)a.size());
}
```

제출 환경에서 assert 실패는 런타임 에러가 됩니다. 디버깅용 assert는 의도적으로 남길 수도 있지만, 입력으로 발생 가능한 상황은 assert가 아니라 일반 조건문으로 처리해야 합니다.

## 8. 자주 하는 실수

| 실수 | 결과 | 확인 방법 |
| --- | --- | --- |
| 예제만 맞추고 제출 | 숨은 경계에서 오답 | edge case 목록 만들기 |
| brute force도 빠른 풀이와 같은 로직 | 같은 버그 공유 | 더 단순한 완전탐색 작성 |
| random 범위가 너무 큼 | brute force가 느림 | 작은 입력에서 많이 반복 |
| 반례를 출력하지 않음 | 재현 불가 | 실패 시 입력 전체 출력 |
| stress 코드를 제출 | 컴파일/런타임 문제 | `#ifdef LOCAL` 또는 제거 |
| assert로 입력 예외 처리 | 런타임 에러 | 가능한 입력은 조건문 처리 |

## 9. 문제를 볼 때 체크할 조건

1. 최소 입력과 최대 입력을 따로 테스트했는가?
2. 중복, 빈 구간, 끝점 접촉, 불가능 상태가 있는가?
3. 작은 입력의 brute force를 만들 수 있는가?
4. 빠른 풀이와 brute force를 같은 입력에서 비교했는가?
5. 반례가 나오면 재현 가능한 형태로 출력하는가?
6. 최대 입력 성능을 한 번이라도 확인했는가?

정리하면, stress test는 정답을 증명하지 않습니다. 대신 내가 놓친 반례를 빠르게 찾아 주는 도구입니다. 특히 그리디와 복잡한 자료구조 구현에서 효과가 큽니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 배열 구간 질의 풀이에 brute force를 붙이는 연습 추가 | 작은 입력 비교 루프 작성 | brute force |
| 표준 | TODO: 그리디 후보 풀이의 반례를 찾는 연습 추가 | random generator로 실패 케이스 탐색 | stress test |
| 응용 | TODO: 기하/그래프 구현의 edge case를 수집하는 연습 추가 | 경계 조건 체크리스트 만들기 | edge case |
| 함정 | TODO: 빠른 풀이와 brute force가 같은 버그를 공유하는 사례 추가 | 독립적인 검증 코드 작성 | independent oracle |
