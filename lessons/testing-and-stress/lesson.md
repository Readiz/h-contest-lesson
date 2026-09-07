# Testing과 Stress Test

빠른 풀이와 작은 입력용 완전탐색에 같은 입력을 넣고 답을 비교하면, 예제에 없는 반례를 자동으로 찾을 수 있습니다. Stress test는 이 비교를 여러 입력에서 반복하는 방법입니다.

## 테스트의 층위

| 테스트 | 목적 |
| --- | --- |
| 예제 테스트 | 입출력 형식과 기본 동작 확인 |
| 직접 만든 edge case | 경계 조건 확인 |
| brute force 비교 | 작은 입력에서 정답성 확인 |
| random stress | 생각하지 못한 반례 탐색 |
| 최대 입력 성능 테스트 | 시간/메모리 확인 |

## Edge Case 목록 만들기

입력에서 허용되는 조건을 골라 테스트를 만듭니다. 예를 들어 `n >= 1`인 문제에 빈 배열을 넣으면 풀이의 반례가 아닙니다.

| 조건 | 예시 |
| --- | --- |
| 최소 크기 | `n = 0`, `n = 1`, 빈 문자열, 간선 없음 |
| 최대 값 | 좌표 `10^9`, 비용 합 `10^18`, 배열 길이 최대 |
| 중복 | 같은 값 여러 개, 같은 간선 여러 개, 같은 점 |
| 경계 접촉 | 구간 끝점, 선분 끝점, inclusive/exclusive |
| 불가능 상태 | 도달 불가, 답 없음, 음수 사이클, 모순 |
| tie-break | 같은 점수, 같은 거리, 같은 정렬 기준 |

## Brute Force 만들기

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

## Random Generator와 비교 루프

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

위 `fastDistinctCountForDemo`는 연결 위치를 보여 주려고 기준 함수를 그대로 호출합니다. 검증할 빠른 풀이로 교체해야 비교가 의미를 갖습니다.

실제 제출 코드에 stress loop를 넣으면 안 됩니다. 로컬에서 반례를 찾는 별도 모드로 두고, 제출 전에는 제거하거나 `#ifdef LOCAL`로 감쌉니다.

## 반례를 찾았을 때

Stress test가 실패하면 입력을 출력해야 합니다. 그래야 재현하고 디버깅할 수 있습니다.

반례를 찾은 뒤에는 바로 코드를 고치기보다 아래 순서로 봅니다.

1. brute force가 정말 맞는가?
2. 빠른 풀이의 전제 조건이 깨졌는가?
3. indexing이나 inclusive/exclusive가 틀렸는가?
4. tie-break 또는 중복 처리가 빠졌는가?
5. overflow가 있는가?

실패 입력을 저장하고, 원소나 간선을 줄여도 같은 불일치가 남는지 봅니다. 작아진 반례는 수정 후에도 재현 테스트로 남깁니다.

## 성능 테스트

정답성이 맞아도 시간 안에 들어와야 합니다. 최대 입력을 직접 생성해 로컬에서 실행 시간을 봅니다.

성능 테스트에서는 답이 맞는지보다 아래를 봅니다.

- 입력 생성과 파싱이 병목인지
- `O(n log n)`이라고 생각한 코드 안에 `substr`, `erase`, `map` 중첩이 숨어 있는지
- 메모리가 제한을 넘는지
- 재귀 깊이가 큰지

성능 테스트는 로컬 환경과 채점 환경이 다르므로 절대 기준은 아닙니다. 그래도 명백한 `O(n^2)` 실수나 큰 메모리 사용은 잡을 수 있습니다.

## assert와 local debug

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
