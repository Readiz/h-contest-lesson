# 좌표 압축

좌표 압축은 값의 크기 자체는 크지만 서로 다른 값의 개수가 작을 때, 값을 `0..m-1` 또는 `1..m` 범위의 인덱스로 바꾸는 기법입니다. Fenwick Tree, Segment Tree, 스위프 라인, 오프라인 쿼리에서 자주 함께 쓰입니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: 정렬, 이분 탐색, 배열 인덱스
- 함께 보면 좋은 레슨: 정렬 알고리즘, 이분 탐색과 파라메트릭 서치
- 다음에 볼 레슨: Fenwick Tree, Segment Tree, Sqrt Decomposition

## 1. 값은 크지만 서로 다른 값의 개수는 작을 때

예를 들어 좌표가 `1`, `1,000,000,000`, `500,000,000`처럼 크면 좌표를 그대로 배열 인덱스로 쓸 수 없습니다. 하지만 실제로 등장한 값이 3개뿐이라면, 정렬 순서만 유지해서 아래처럼 바꿀 수 있습니다.

```text
원래 값: 1, 500000000, 1000000000
압축 값: 0, 1, 2
```

중요한 것은 **대소 관계를 보존한다**는 점입니다. 원래 값이 작을수록 압축 인덱스도 작습니다.

## 2. 정렬 + unique

먼저 모든 값을 한 벡터에 모아 정렬하고 중복을 제거합니다.

```cpp
vector<int> values = a;
sort(values.begin(), values.end());
values.erase(unique(values.begin(), values.end()), values.end());
```

이제 `values[i]`는 압축 인덱스 `i`가 나타내는 원래 값입니다.

## 3. lower_bound로 압축 인덱스 만들기

원래 값 `x`의 압축 인덱스는 `lower_bound`로 찾습니다.

```cpp
int compress(const vector<int>& values, int x) {
    return lower_bound(values.begin(), values.end(), x) - values.begin();
}
```

모든 `x`가 `values`에 들어 있다는 전제가 있어야 합니다. 온라인으로 새로운 값이 중간에 들어오는 문제라면, 먼저 모든 쿼리를 읽어 등장 가능한 값을 모으는 오프라인 처리가 필요할 수 있습니다.

## 4. 원래 값 복원하기

압축 인덱스에서 원래 값으로 돌아가야 할 때는 `values[idx]`를 읽으면 됩니다.

```cpp
int originalValue = values[compressedIndex];
```

압축은 값의 순서만 보존합니다. 값 사이의 실제 거리까지 보존하지는 않습니다. `100`과 `200`의 차이도 1칸이고, `100`과 `1,000,000,000`의 차이도 압축 후에는 이웃일 수 있습니다.

## 5. Fenwick Tree와 함께 쓰기

좌표 압축은 "값 기준으로 prefix를 관리"할 때 특히 자주 씁니다. 예를 들어 지금까지 본 원소 중 `x` 이하가 몇 개인지 세고 싶다면, 값 `x`를 압축 인덱스로 바꾼 뒤 Fenwick Tree prefix sum을 질의합니다.

```cpp
struct Fenwick {
    int n;
    vector<int> tree;

    Fenwick(int n) : n(n), tree(n + 1, 0) {}

    void add(int idx, int delta) {
        for (idx++; idx <= n; idx += idx & -idx) tree[idx] += delta;
    }

    int sumPrefix(int idx) const {
        int result = 0;
        for (idx++; idx > 0; idx -= idx & -idx) result += tree[idx];
        return result;
    }
};

long long countInversions(const vector<int>& a) {
    vector<int> values = a;
    sort(values.begin(), values.end());
    values.erase(unique(values.begin(), values.end()), values.end());

    Fenwick bit((int)values.size());
    long long inversions = 0;
    for (int i = 0; i < (int)a.size(); i++) {
        int idx = lower_bound(values.begin(), values.end(), a[i]) - values.begin();
        int notGreater = bit.sumPrefix(idx);
        inversions += i - notGreater;
        bit.add(idx, 1);
    }
    return inversions;
}
```

## 6. 구간 좌표 압축에서 주의할 점

구간 `[l, r]`을 다룰 때는 문제의 의미에 따라 `r + 1`도 같이 넣어야 할 수 있습니다. 예를 들어 차분 배열처럼 `[l, r]`에 더하고 `r + 1`에서 빼는 방식이면 `r + 1` 좌표가 반드시 필요합니다.

또 면적이나 길이를 계산하는 문제에서는 압축 인덱스 차이가 실제 거리와 다릅니다. 이때는 `values[i + 1] - values[i]`처럼 원래 좌표 간격을 곱해야 합니다.

## 7. 시간 복잡도

| 작업 | 시간 |
| --- | --- |
| 값 수집 | `O(n)` |
| 정렬과 중복 제거 | `O(n log n)` |
| 값 하나 압축 | `O(log n)` |
| unordered map으로 미리 매핑 | 평균 `O(1)` |
| 메모리 | `O(n)` |

## 8. 자주 하는 실수

| 실수 | 결과 | 점검 |
| --- | --- | --- |
| 등장하지 않은 값을 압축하려 함 | 잘못된 인덱스 | 모든 후보 값을 먼저 수집 |
| 0-index와 1-index를 섞음 | Fenwick Tree off-by-one | 외부 인덱스 규칙 고정 |
| 실제 거리도 보존된다고 착각 | 길이/면적 오답 | 원래 좌표 간격 별도 사용 |
| 구간 끝점만 넣고 `r + 1`을 빼먹음 | 차분 복원 오답 | 닫힌/반열린 구간 확인 |

## 9. 문제를 볼 때 체크할 조건

1. 값의 범위가 배열로 만들기엔 너무 큰가?
2. 등장하는 값의 개수는 입력 크기 이하로 제한되는가?
3. 값의 대소 관계만 필요하고 실제 거리 차이는 필요 없는가?
4. 모든 쿼리를 먼저 읽을 수 있는 오프라인 문제인가?
5. 구간 문제라면 끝점과 다음 지점을 모두 넣어야 하는가?

## 대표 문제로 연결하기

### 문제에서 보이는 신호

- 입력 크기: 값은 `10^9` 이상이지만 원소나 쿼리는 `2 * 10^5` 정도다.
- 필요한 복잡도: 정렬 `O(n log n)` 후 각 연산 `O(log n)` 또는 `O(1)`.
- 이 레슨의 핵심 개념: 큰 값을 조밀한 인덱스로 바꾸고 순서를 보존한다.

### 풀이 흐름

1. 배열 값, 쿼리 좌표, 필요한 보조 좌표를 모두 `values`에 모은다.
2. 정렬 후 `unique`로 중복을 제거한다.
3. 각 값을 `lower_bound`로 압축하고 자료구조 인덱스로 사용한다.

### 자주 틀리는 지점

- 압축 인덱스로 실제 거리 계산을 하면 틀립니다.
- `lower_bound` 결과가 `values.end()`인지 확인하지 않으면 등장하지 않은 값을 조용히 잘못 처리할 수 있습니다.

## 10. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 값 목록을 압축해 원래 순서로 출력하는 문제 추가 | 정렬 + unique + lower_bound 적용 | `unique`, `lower_bound` |
| 표준 | TODO: inversion count 문제 추가 | 압축과 Fenwick Tree 연결 | 압축 인덱스, 누적 빈도 |
| 응용 | TODO: 구간 칠하기와 전체 길이 계산 문제 추가 | 실제 좌표 간격을 별도로 곱하기 | 좌표 간격, sweep |
| 함정 | [정수 정렬 함수](/practice/SORTTEST) | 값 범위와 입력 크기를 보고 정렬 전략 구분 | 값 범위, 정렬 전략 |
