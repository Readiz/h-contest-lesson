# 대회용 C++ 기본기

알고리즘 문제에서 C++은 풀이 아이디어를 빠르게 구현하기 좋은 언어입니다. 하지만 입출력, 정수 범위, 컨테이너 사용법, 디버깅 출력 같은 기본기를 놓치면 알고리즘을 맞게 생각하고도 틀릴 수 있습니다.

이 레슨은 알고리즘 레슨을 따라가기 전에 익혀 두면 좋은 대회용 C++ 습관을 정리합니다. 문법 전체를 다루기보다, 문제 풀이에서 자주 막히는 부분에 집중합니다.

> 이 레슨은 `#include <bits/stdc++.h>`, STL 컨테이너, C++17 표준 라이브러리를 사용할 수 있는 일반적인 C++ 알고리즘 대회 환경을 기준으로 합니다. 일부 h-contest 휴리스틱/제한 환경에서는 STL이나 C 표준 헤더 사용이 제한될 수 있으므로, 그런 문제에서는 휴리스틱 레슨의 고정 배열/직접 구현 방식을 따릅니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 변수, 조건문, 반복문, 함수
- 함께 보면 좋은 레슨: 복잡도와 입력 크기 감각, 정렬 알고리즘
- 다음에 볼 레슨: 정렬 알고리즘, BFS/DFS와 격자 탐색, 동적 계획법

## 1. 기본 템플릿과 빠른 입출력

대부분의 문제는 아래 템플릿으로 시작할 수 있습니다.

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<int> a(n);
    for (int i = 0; i < n; ++i) {
        cin >> a[i];
    }

    long long sum = 0;
    for (int x : a) {
        sum += x;
    }

    cout << sum << '\n';
    return 0;
}
```

`ios::sync_with_stdio(false)`와 `cin.tie(nullptr)`는 C++ 스트림 입출력을 빠르게 쓰기 위한 기본 설정입니다. 이 설정을 켠 뒤에는 `scanf`/`printf`와 `cin`/`cout`을 섞지 않는 편이 안전합니다.

출력에서는 `endl`보다 `'\n'`을 기본으로 씁니다. `endl`은 줄바꿈뿐 아니라 flush까지 수행해서 반복 출력에서 느려질 수 있습니다.

## 2. vector와 string

크기가 입력으로 주어지는 배열은 `vector`로 잡는 편이 안전합니다.

```cpp
int n;
cin >> n;

vector<int> a(n);
for (int i = 0; i < n; ++i) {
    cin >> a[i];
}
```

`vector<vector<int>>`로 2차원 배열도 만들 수 있습니다.

```cpp
int h, w;
cin >> h >> w;

vector<vector<int>> grid(h, vector<int>(w, 0));
```

문자열은 `string`을 사용합니다. 공백 없는 단어는 `cin >> s`, 한 줄 전체는 `getline(cin, s)`로 받습니다. `cin >>` 다음에 `getline`을 바로 쓰면 남아 있는 줄바꿈 때문에 빈 줄을 읽을 수 있으므로 조심해야 합니다.

```cpp
string s;
cin >> s;

for (char ch : s) {
    if (ch == 'A') {
        cout << "found\n";
    }
}
```

## 3. pair, tuple, struct

두 값을 묶을 때는 `pair`가 편합니다.

```cpp
vector<pair<int, int>> points;
points.push_back({3, 5});
points.push_back({1, 9});

sort(points.begin(), points.end());
```

`pair`는 기본적으로 첫 번째 값, 두 번째 값 순서로 비교됩니다. 값의 의미가 분명해야 하거나 필드가 세 개 이상이면 `struct`를 쓰는 편이 읽기 좋습니다.

```cpp
struct Edge {
    int from;
    int to;
    long long cost;
};

vector<Edge> edges;
edges.push_back({0, 1, 7});
```

정렬 기준이 필요하면 비교 함수를 직접 씁니다.

```cpp
sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {
    if (a.cost != b.cost) return a.cost < b.cost;
    return a.to < b.to;
});
```

비교 함수에서는 같은 원소에 대해 `true`가 나오면 안 됩니다. `<=` 대신 `<`를 써야 정렬 기준이 깨지지 않습니다.

## 4. long long과 overflow

`int`는 보통 약 21억까지 표현합니다. 입력 하나는 `int` 범위여도 합, 곱, 거리, 경우의 수는 쉽게 범위를 넘습니다.

```cpp
int n;
cin >> n;

long long sum = 0;
for (int i = 0; i < n; ++i) {
    int x;
    cin >> x;
    sum += x;
}
```

곱셈에서는 왼쪽 피연산자를 먼저 `long long`으로 바꿔야 합니다.

```cpp
int a = 100000;
int b = 100000;

long long wrong = a * b;       // int 곱셈이 먼저 overflow될 수 있음
long long right = 1LL * a * b; // long long 곱셈
```

최단거리나 DP에서 큰 값을 나타낼 때는 안전한 `INF`를 씁니다.

```cpp
const long long INF = 4e18;
```

`INF + cost`가 overflow되지 않도록, 실제 가능한 답보다 충분히 크되 `long long` 최댓값보다는 여유 있게 작은 값을 잡습니다.

## 5. 자주 쓰는 컨테이너 감각

컨테이너를 고를 때는 필요한 작업을 먼저 봅니다.

| 컨테이너 | 자주 쓰는 상황 | 주요 비용 |
| --- | --- | --- |
| `vector` | 순서대로 저장, 인덱스 접근 | 뒤에 추가 평균 `O(1)`, 접근 `O(1)` |
| `deque` | 앞뒤로 넣고 빼기 | 앞뒤 추가/삭제 `O(1)` |
| `queue` | BFS처럼 먼저 들어온 것부터 처리 | push/pop `O(1)` |
| `priority_queue` | 최댓값/최솟값 후보 관리 | push/pop `O(log n)` |
| `set`, `map` | 정렬된 상태로 찾기 | `O(log n)` |
| `unordered_set`, `unordered_map` | 해시 기반 빠른 찾기 | 평균 `O(1)`, 최악은 나쁠 수 있음 |

문제에서 "가장 작은 후보를 계속 꺼낸다"면 `priority_queue`, "방문한 값을 빠르게 찾는다"면 `set` 또는 `unordered_set`, "인덱스로 자주 접근한다"면 `vector`를 먼저 생각합니다.

## 6. 디버깅 출력과 assert

채점 출력에는 정답만 나가야 합니다. 중간 확인은 `cerr`로 보내면 `cout`과 분리되어 로컬 디버깅이 편합니다.

```cpp
int value = 42;
cerr << "value=" << value << '\n';
```

제출 전에는 디버깅 출력을 지우는 것이 원칙입니다. 필요하면 매크로로 로컬에서만 켜는 방식도 쓸 수 있습니다.

```cpp
#ifdef LOCAL
#define DBG(x) cerr << #x << "=" << (x) << '\n'
#else
#define DBG(x) ((void)0)
#endif
```

`assert`는 "절대 깨지면 안 되는 조건"을 확인할 때 유용합니다.

```cpp
assert(0 <= idx && idx < n);
```

다만 온라인 채점 환경에서 assert가 실패하면 런타임 에러가 납니다. 디버깅 단계에서 조건을 잡는 용도로 쓰고, 실제 예외 처리가 필요한 입력 조건은 코드로 처리해야 합니다.

## 7. 함수로 쪼개기

코드를 모두 `main`에 넣으면 짧은 문제는 빠르지만, 그래프 탐색이나 DP처럼 상태가 늘어나는 문제에서는 실수가 늘어납니다.

```cpp
bool inside(int r, int c, int h, int w) {
    return 0 <= r && r < h && 0 <= c && c < w;
}
```

작은 조건 함수를 분리하면 반복되는 경계 체크를 줄일 수 있습니다. 함수 이름이 곧 설명이 되므로 디버깅도 쉬워집니다.

## 8. 자주 하는 실수

- `ios::sync_with_stdio(false)`를 켠 뒤 C 입출력과 C++ 입출력을 섞는다.
- 반복 출력에서 `endl`을 과하게 쓴다.
- 합과 곱을 `int`로 계산해 overflow를 만든다.
- `vector` 크기를 잡지 않고 인덱스로 대입한다.
- 정렬 비교 함수에서 `<=`를 쓴다.
- `getline` 전에 남은 줄바꿈을 처리하지 않는다.
- 디버깅 출력을 `cout`에 남긴 채 제출한다.
- 0-index와 1-index를 섞는다.

## 9. 문제를 볼 때 체크할 조건

1. 입력이 많아서 빠른 입출력이 필요한가?
2. 합, 곱, 거리, 경우의 수에 `long long`이 필요한가?
3. 배열 크기가 입력으로 정해져서 `vector`가 적절한가?
4. 필요한 작업이 인덱스 접근인지, 정렬 상태 유지인지, 최솟값 추출인지 구분했는가?
5. 디버깅 출력이 정답 출력에 섞이지 않는가?
6. 제출 전 로컬 테스트와 예제 테스트를 모두 통과했는가?

## 대표 문제로 연결하기

### 문제에서 보이는 신호

| 신호 | 판단 |
| --- | --- |
| 입력 크기 | 수십만 줄 이상이면 빠른 입출력과 `O(n log n)` 이하 구현 습관이 중요 |
| 키워드 | "합", "최대 비용", "최단거리", "경우의 수"가 보이면 `long long`부터 검토 |
| 자주 나오는 변형 | 좌표가 1-index로 들어오지만 배열은 0-index로 관리하는 문제, 여러 필드를 정렬하는 문제 |

### 풀이 흐름

1. 기본 템플릿을 놓고 입력을 정확히 받는다.
2. 필요한 타입을 먼저 정한다. 합과 곱은 기본적으로 `long long`을 의심한다.
3. 필요한 작업에 맞는 컨테이너를 고른다.
4. 정렬 기준이나 경계 체크를 함수로 분리한다.
5. 예제, 최소 입력, 최대에 가까운 입력을 직접 만들어 본다.

### 자주 틀리는 지점

- 입력을 다 읽기 전에 출력하거나, 줄 단위 입력에서 빈 줄을 읽는다.
- `1LL * a * b`가 필요한 곳에서 `a * b`를 먼저 계산한다.
- `priority_queue`가 기본적으로 max heap이라는 점을 잊는다.
- `vector<int> a; a[i] = x;`처럼 크기 없는 vector에 인덱스 대입을 한다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 배열 합과 최댓값 출력 문제 추가 | 빠른 입출력, `vector`, `long long` 합계 | `ios::sync_with_stdio(false)` |
| 표준 | TODO: 값과 인덱스를 함께 정렬하는 문제 추가 | `pair`, `struct`, comparator 작성 | comparator, tie-break |
| 응용 | TODO: 여러 컨테이너로 후보 관리하는 문제 추가 | `queue`, `priority_queue`, `set`의 선택 기준 확인 | container choice |
| 함정 | TODO: 큰 수 곱셈과 1-index 입력 처리 문제 추가 | overflow와 인덱스 변환 실수 줄이기 | `1LL`, 0-index |
