# Practice Set

Suffix and Periodicity Structures 계열은 같은 문제를 suffix array와 SAM 양쪽으로 풀어 보는 연습이 좋습니다. 아직 적절한 h-contest 문제 링크가 없는 항목은 임의 ID를 만들지 않고 `TODO`로 둡니다.

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: suffix array pattern search `/practice/...` 문제 필요 | suffix 정렬과 lower_bound | suffix array |
| 입문 | [Distinct Substring Count](#2-로컬-연습-distinct-substring-count) | LCP sum 또는 SAM contribution | LCP, SAM |
| 표준 | TODO: repeated substring `/practice/...` 문제 필요 | LCP maximum과 occurrence 조건 | LCP RMQ |
| 표준 | TODO: longest common substring `/practice/...` 문제 필요 | generalized SAM 또는 separator SA | source mask |
| 응용 | TODO: period query `/practice/...` 문제 필요 | prefix function, border, runs | period |
| 심화 | TODO: suffix tree traversal `/practice/...` 문제 필요 | explicit edge와 depth | Ukkonen |

## 1. Trace: `banana`의 suffix array와 LCP

문자열 `banana`의 suffix를 정렬하면 아래와 같습니다.

| SA index | suffix start | suffix |
| ---: | ---: | --- |
| 0 | 5 | `a` |
| 1 | 3 | `ana` |
| 2 | 1 | `anana` |
| 3 | 0 | `banana` |
| 4 | 4 | `na` |
| 5 | 2 | `nana` |

인접 suffix의 LCP는 아래입니다.

```text
LCP = [1, 3, 0, 0, 2]
```

길이 `N=6`인 문자열의 모든 substring 개수는 `N*(N+1)/2 = 21`입니다. suffix array에서 새 suffix가 추가하는 새로운 substring 수는 `suffixLength - previousLcp`입니다. 따라서 distinct substring 수는 아래처럼 계산합니다.

```text
21 - (1 + 3 + 0 + 0 + 2) = 15
```

Suffix Automaton으로 세면 각 상태의 contribution `len[v] - len[link[v]]`를 더해도 같은 값이 나와야 합니다. 이 연습은 SA/LCP와 SAM이 같은 substring 집합을 다른 방식으로 압축한다는 점을 확인하는 용도입니다.

## 2. 로컬 연습: Distinct Substring Count

### 입력

소문자 영어 문자열 `S`가 주어집니다.

```text
S
```

### 출력

서로 다른 non-empty substring의 개수를 출력합니다.

### 제한

- `1 <= |S| <= 200000`
- `S`는 `a`부터 `z`까지의 소문자만 포함합니다.

### 예시

```text
banana
```

```text
15
```

### 풀이 기준: Suffix Array

1. suffix array를 만든다.
2. Kasai algorithm 등으로 LCP 배열을 만든다.
3. `N*(N+1)/2 - sum(LCP)`를 출력한다.
4. 답은 최대 `N*(N+1)/2`이므로 64-bit 정수를 사용한다.

### 풀이 기준: Suffix Automaton

SAM으로 검증 구현을 하나 더 만들 수 있습니다.

```text
answer = sum over states v != root of (len[v] - len[link[v]])
```

두 구현이 같은 답을 내면 suffix array의 index 정의와 SAM의 suffix link 누적 방향을 동시에 점검할 수 있습니다.

### Stress 검증

작은 입력에서는 모든 substring을 set에 넣는 baseline과 비교합니다.

```text
for seed in 1..1000:
    random string with length <= 10
    answer_sa = suffix array + LCP
    answer_sam = suffix automaton contribution
    answer_naive = size of substring set
    assert answer_sa == answer_sam == answer_naive
```

반드시 포함할 case는 모든 문자가 같은 문자열, 모두 다른 문자열, `abababab`처럼 period가 강한 문자열입니다.

## 3. 완료 기준

- suffix array와 LCP index 정의를 고정합니다.
- SAM occurrence count는 suffix link 역순 누적 뒤에 사용합니다.
- 여러 문자열을 합칠 때 separator 충돌을 막습니다.
- period query에서는 inclusive/exclusive 구간을 통일합니다.
- naive substring set과 비교하는 작은 stress test를 준비합니다.
