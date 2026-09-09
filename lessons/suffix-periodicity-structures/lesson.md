# Suffix and Periodicity Structures

Suffix and Periodicity Structures는 suffix array, suffix automaton, suffix tree, runs, border automaton, period query를 하나의 문자열 구조 트랙으로 묶는 허브입니다. 이 주제들은 모두 "문자열의 모든 suffix/substr/period 정보를 어떻게 압축해서 질의할 것인가"라는 같은 문제군에 속합니다.

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| suffix 순서와 LCP로 패턴 검색·반복·서로 다른 부분 문자열을 처리한다 | [Suffix Array와 LCP](pages/suffix-array-lcp.md) |
| substring 존재/개수/등장 횟수를 상태로 세고 싶다 | [Suffix Automaton](pages/suffix-automaton.md) |
| 여러 문자열의 공통 substring을 한 구조로 관리한다 | [여러 문자열의 Suffix Automaton 질의](pages/generalized-suffix-automaton.md) |
| explicit suffix tree edge와 Ukkonen construction이 필요하다 | [Suffix Tree and Ukkonen](pages/suffix-tree-ukkonen.md) |
| 주기, run, 반복 구조가 문제의 핵심이다 | [Runs and Periodicity](pages/runs-periodicity.md) |
| prefix-function 기반 상태 전이가 필요하다 | [Border Automaton](pages/border-automaton.md) |

## 표현과 인덱스

Alphabet 크기에 따라 transition을 배열로 둘지 정합니다. 여러 문자열을 붙이면 원문에 없는 separator를 쓰고, occurrence의 개수만 필요한지 위치까지 필요한지 구분합니다.

LCP 배열은 `LCP(sa[i], sa[i+1])`와 `LCP(sa[i-1], sa[i])` 중 어느 정의를 쓰는지 구현 전체에서 맞춥니다. SAM의 clone은 생성 시 실제 occurrence를 새로 만든 것이 아니므로 일반 상태와 같은 초기 count를 주지 않습니다. Border가 있다는 것과 문자열 전체가 그 길이로 반복된다는 조건도 구분해야 합니다.

## Trace: `banana`의 suffix array와 LCP

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
LCP = [0, 1, 3, 0, 0, 2]
```

길이 `N=6`인 문자열의 모든 substring 개수는 `N*(N+1)/2 = 21`입니다. suffix array에서 새 suffix가 추가하는 새로운 substring 수는 `suffixLength - previousLcp`입니다. 따라서 distinct substring 수는 아래처럼 계산합니다.

```text
21 - (1 + 3 + 0 + 0 + 2) = 15
```

Suffix Automaton으로 세면 각 상태의 contribution `len[v] - len[link[v]]`를 더해도 같은 값이 나와야 합니다. 이 연습은 SA/LCP와 SAM이 같은 substring 집합을 다른 방식으로 압축한다는 점을 확인하는 용도입니다.

## 로컬 연습: Distinct Substring Count

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
