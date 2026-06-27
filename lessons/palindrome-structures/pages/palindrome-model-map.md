# Palindrome Model Map

Palindrome 문제는 "회문인가"를 묻는 판정 문제와 "회문들을 어떻게 세고 조합하는가"를 묻는 집계 문제가 다릅니다.

## 1. 선택 기준

| 질문 | 후보 |
| --- | --- |
| 정적 문자열에서 substring palindrome 판정만 필요한가? | Manacher, rolling hash |
| 한 글자 update가 있는가? | forward/reverse hash segment tree |
| 서로 다른 palindrome substring을 모두 세는가? | Palindromic Tree |
| prefix를 추가하면서 online 통계를 내는가? | Palindromic Tree |
| 구간 `[l, r]` 자체가 DP 상태인가? | Palindrome Range DP |
| suffix와 palindrome 조건이 동시에 필요한가? | suffix structure + palindrome helper |

## 2. 구현 전 체크

- palindrome 판정만 필요한지, occurrence/count가 필요한지 구분합니다.
- hash를 쓰면 collision 정책을 명시합니다.
- Manacher radius의 홀수/짝수 중심 정의를 고정합니다.
- Eertree count는 suffix link 역순 누적 뒤에 사용합니다.
- range DP는 `O(N^2)` 메모리와 시간 제한을 먼저 확인합니다.

## 3. 자주 하는 실수

1. Manacher `even[i]` 중심을 `i`와 `i+1` 사이로 잘못 해석한다.
2. Eertree의 새 노드 수를 occurrence count로 착각한다.
3. hash palindrome 판정에서 reversed index 변환을 한 칸 밀린다.
4. 구간 DP를 써야 하는 문제를 단순 판정 질의로 오해한다.
5. suffix 조건과 palindrome 조건의 기준 문자열 방향을 섞는다.
