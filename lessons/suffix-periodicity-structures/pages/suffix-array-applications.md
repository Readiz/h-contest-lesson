# Suffix Array 응용 패턴

Suffix Array 응용 패턴은 suffix를 정렬해 둔 뒤 LCP 배열, RMQ, 구간 질의로 문자열 문제를 푸는 레슨입니다. Suffix Array 자체를 만드는 것보다 더 자주 막히는 지점은 "정렬된 suffix에서 어떤 구간을 봐야 하는가"입니다.

## 문제 신호

| 문제 표현 | Suffix Array 응용 관점 |
| --- | --- |
| 어떤 패턴이 문자열에 몇 번 등장하는가 | suffix array에서 패턴 prefix 구간 |
| 사전순 k번째 substring | suffix 순서와 LCP로 새 substring 수 누적 |
| 두 suffix의 LCP를 여러 번 묻는다 | rank 배열 + LCP RMQ |
| 여러 문자열의 공통 substring | source id sliding window |
| 반복 substring, period 후보 | LCP의 큰 값과 suffix 위치 차이 |

Suffix Array는 "suffix를 사전순으로 정렬한 좌표계"입니다. 원래 문자열 index가 아니라 suffix array rank를 기준으로 구간을 잡아야 합니다.

## 패턴 등장 구간

패턴 `p`가 등장하는 모든 위치는 suffix array에서 연속 구간을 이룹니다. suffix와 `p`를 사전순으로 비교해서 `lower_bound(p)`와 `upper_bound(p)`를 찾습니다.

```text
suffix < p          -> 왼쪽 구간
suffix starts p     -> 정답 구간
suffix > p          -> 오른쪽 구간
```

기본 페이지의 비교 함수를 그대로 쓰고, 반환값이 0인 경우도 왼쪽으로 넘기면 첫 양수 위치가 upper bound입니다. 별도의 다음 문자열을 만들 필요가 없습니다.

## LCP RMQ

`rank[i]`를 suffix `s[i..]`의 suffix array 위치라고 하겠습니다. 두 suffix `i`, `j`의 LCP는 rank 사이의 LCP 배열 최솟값입니다.

```text
ri = rank[i], rj = rank[j]
if ri > rj swap(ri, rj)
lcp(i, j) = min(lcp[ri + 1], ..., lcp[rj])
```

이 구간 최솟값을 자주 묻는다면 Sparse Table을 올립니다.

[Sparse Table](https://h.readiz.com/learn/sparse-table-rmq)의 `SparseTableMin(lcp)`를 그대로 사용합니다. `i == j`이면 `N-i`, 아니면 `queryMin(min(ri,rj)+1,max(ri,rj))`가 답입니다.

## 서로 다른 Substring과 k번째 Substring

suffix `sa[i]`가 새로 만드는 substring 수는 이전 suffix와 겹치지 않는 prefix 개수입니다.

```text
newCount(i) = (N - sa[i]) - lcp[i]
```

따라서 서로 다른 substring 총수는 모든 `newCount`의 합입니다. 사전순 k번째 substring은 suffix array 순서로 `newCount`를 빼다가, 남은 k만큼 suffix prefix를 늘려 찾습니다.

```text
answer length = lcp[i] + k
answer = s.substr(sa[i], answer length)
```

`k`와 substring 수는 쉽게 `O(N^2)`까지 커지므로 `long long`을 씁니다.

## 여러 문자열의 공통 Substring

여러 문자열을 separator로 이어 붙이고 suffix array를 만들면, 각 suffix의 원본 문자열 id를 알 수 있습니다.

```text
s1 + # + s2 + $ + s3
```

모든 문자열을 포함하는 suffix array window를 two pointers로 유지하고, 그 window 내부 인접 LCP의 최솟값이 공통 substring 길이 후보가 됩니다. window 안에 source id가 모두 들어왔는지 count 배열로 관리합니다.

이 방식은 "모든 문자열에 등장하는 가장 긴 substring"에 잘 맞습니다. 특정 두 문자열만 비교한다면 combined suffix array에서 인접한 서로 다른 source suffix의 LCP 최댓값만 봐도 됩니다.

## 반복 Substring과 위치 조건

LCP 값이 크다는 것은 인접 suffix 두 개가 긴 prefix를 공유한다는 뜻입니다. 하지만 문제는 종종 위치 조건을 함께 요구합니다.

| 조건 | 추가로 볼 값 |
| --- | --- |
| 두 번 이상 등장 | LCP 최댓값 |
| 겹치지 않고 등장 | suffix 위치 차이 `>= length` |
| 적어도 k번 등장 | suffix array에서 크기 k window의 LCP 최솟값 |
| 서로 다른 source에 등장 | source id count |

겹치지 않는 반복은 인접 suffix만 검사하면 놓칠 수 있습니다. 후보 길이 이상 LCP로 연결된 전체 그룹의 최소·최대 시작 위치 차이를 봅니다. `k=1`이면 전체 문자열 길이가 답입니다. `k >= 2`에서 `k`번 이상 등장하는 substring 길이는 size `k` window마다 LCP 최솟값을 보며 최댓값을 취합니다. 구간 최솟값은 Sparse Table 또는 deque로 처리할 수 있습니다.

## 시간 복잡도

| 작업 | 복잡도 |
| --- | ---: |
| Suffix Array construction | 기본 페이지 구현은 `O(N log² N)` |
| LCP construction | `O(N)` |
| Sparse Table build | `O(N log N)` |
| suffix LCP query | `O(1)` |
| 패턴 구간 탐색 | `O(|P| log N)` |

패턴 탐색에서 suffix와 pattern 비교를 매번 처음부터 하면 최악 입력에서 느려질 수 있습니다. 많은 패턴을 처리한다면 LCP 가속 이분 탐색, suffix automaton, trie 계열도 비교합니다.
