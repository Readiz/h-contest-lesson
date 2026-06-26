# Contest Boundaries

Matroid 계열은 문제를 읽는 언어로는 강력하지만, 일반 알고리즘을 그대로 구현하는 주제로는 부담이 큽니다. 대회에서 실제로 풀 수 있는 형태인지 판단하는 기준을 먼저 세워야 합니다.

## 1. 구현 가능성 표

| 구조 | 대회 구현 가능성 | 이유 |
| --- | --- | --- |
| Partition matroid | 높음 | class별 count와 capacity로 판정 가능 |
| Graphic matroid | 중간 | DSU는 추가 판정만 쉽고 교환은 별도 구조 필요 |
| Linear matroid over GF(2) | 중간 | XOR basis로 작은 rank 처리가 가능 |
| General oracle matroid | 낮음 | exchange graph와 oracle 호출이 비싸고 증명이 무거움 |
| Weighted matroid intersection | 낮음 | shortest augmenting path와 potential이 필요 |
| General matroid parity | 매우 낮음 | 범용 구현이 대회 범위를 넘기 쉬움 |

현재 허브의 Intersection, Union, Parity 페이지는 reference입니다. 완성 구현 강의가 아니라 "이 문제를 어떤 조합 최적화 모델로 볼 수 있는가"를 알려 주는 역할입니다.

## 2. 실제 풀이로 내려가는 신호

아래 중 하나가 있으면 구현 레슨으로 다룰 여지가 있습니다.

1. 독립성 oracle이 `O(log n)` 또는 거의 선형으로 구현된다.
2. exchange graph 크기가 입력 제한에서 직접 탐색 가능하다.
3. 문제 statement가 partition, forest, rank 같은 제한형을 명확히 준다.
4. weight가 없고 cardinality 최대화만 묻는다.
5. 작은 rank라서 basis rebuild나 brute force 검증이 가능하다.

반대로 "임의 matroid oracle"이나 "weighted general variant"가 보이면, contest problem이라기보다 이론 참고로 읽는 편이 맞습니다.

## 3. 독립 카드로 빼지 말아야 하는 상태

다음 상태라면 독립 `implementation` 레슨으로 공개하지 않습니다.

- 정의와 문제 신호는 있지만 augmenting algorithm이 없다.
- 코드는 partition matroid 같은 쉬운 특수 사례뿐이다.
- greedy failure 반례나 교환 trace가 없다.
- 실제 `/practice/...` 문제나 로컬 완결형 연습이 없다.
- 제목은 일반 알고리즘인데 본문은 "구현 난도 높음"으로 끝난다.

이 조건에 해당하는 문서는 허브 하위 reference로 두는 것이 사용자 기대와 맞습니다.

## 4. 다른 레슨과의 경계

- Matching 문제는 우선 General Matching, Weighted Matching을 본다.
- Rank와 determinant가 핵심이면 Linear Algebra Applications, Randomized Determinant를 본다.
- Greedy 증명이 핵심이면 Proof and Invariants를 본다.
- Flow나 cut으로 모델링되면 Max Flow/Min Cut 또는 Min-Cost Flow 쪽이 더 직접적일 수 있다.

Matroid는 마지막에 붙이는 이름이 아니라, 실제 구현 도구가 단순해지는 경우에만 전면에 둡니다.
