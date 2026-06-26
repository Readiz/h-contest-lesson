# Matroid Algorithms

Matroid Algorithms는 greedy가 맞는 독립성 구조와, greedy가 막힐 때 필요한 exchange 기반 조합 최적화를 묶는 reference 허브입니다. Matroid Intersection, Matroid Union, Matroid Parity는 모두 가치 있는 모델이지만 일반 구현 난도가 높고, 현재 저장소의 본문도 완성된 범용 알고리즘보다 문제 신호와 특수형 판독에 가깝습니다.

따라서 이 허브는 세 문서를 독립 구현 강의로 노출하지 않고, 조합 최적화 참고 트랙으로 배치합니다. 대회에서는 partition, graphic, linear matroid처럼 oracle을 구체적으로 구현할 수 있는 경우에만 깊게 내려가는 것이 안전합니다.

## 0. 선수 지식과 이어지는 레슨

- 선수 지식: Greedy proof, General Matching, Weighted Matching, Linear Basis Applications
- 함께 보면 좋은 레슨: Proof and Invariants, Linear Algebra Applications, Randomized Determinant
- 다음에 볼 레슨: algebraic matching, randomized determinant, sparse linear systems

## 1. 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 | 상태 |
| --- | --- | --- |
| greedy가 맞는 독립성 구조인지 판정해야 한다 | [Matroid Basics and Exchange](pages/matroid-basics-and-exchange.md) | 개념 기반 |
| 두 독립성 조건을 동시에 만족해야 한다 | [Matroid Intersection](pages/matroid-intersection.md) | reference |
| 여러 독립 집합의 합이나 분해를 묻는다 | [Matroid Union](pages/matroid-union.md) | reference |
| pair 단위 선택과 독립성 조건이 결합된다 | [Matroid Parity](pages/matroid-parity.md) | reference |
| 일반 oracle 알고리즘을 구현해야 할 것처럼 보인다 | [Contest Boundaries](pages/contest-boundaries.md) | 경계 설명 |

## 2. 읽는 순서

1. [Matroid Basics and Exchange](pages/matroid-basics-and-exchange.md)에서 독립성 공리, greedy가 맞는 이유, exchange 사고를 확인합니다.
2. [Matroid Intersection](pages/matroid-intersection.md)은 두 matroid의 공통 독립 집합을 exchange graph로 보는 reference입니다.
3. [Matroid Union](pages/matroid-union.md)은 여러 독립 집합으로 덮거나 나누는 모델입니다.
4. [Matroid Parity](pages/matroid-parity.md)는 pair를 통째로 선택하는 matching 일반화입니다.
5. [Contest Boundaries](pages/contest-boundaries.md)에서 어떤 경우에 실제 구현 레슨으로 내려갈 수 있는지 판단합니다.

## 3. 구현 레슨으로 다루기 어려운 이유

- 일반 matroid oracle만 주어지면 exchange graph나 augmenting 구조가 매우 비쌉니다.
- graphic, partition, linear matroid마다 독립성 판정과 교환 최적화가 다릅니다.
- weighted variant는 unweighted 증가 경로보다 훨씬 복잡한 shortest augmenting path/potential이 필요합니다.
- Matroid Parity와 Union은 일반 범용 구현보다 특수 구조 reduction이 더 현실적입니다.
- 현재 본문들의 코드는 느린 oracle 골격이나 쉬운 특수 사례에 머물러 있습니다.

## 4. 독립 구현 강의로 올리는 기준

Matroid 계열 문서를 `implementation`으로 올리려면 최소한 아래 중 하나를 갖춰야 합니다.

1. 실제 augmenting algorithm과 선택 집합 뒤집기 구현
2. forest decomposition, partition matroid intersection처럼 제한형의 완결 풀이
3. naive greedy가 깨지는 입력을 끝까지 추적한 예시
4. 정당성 설명과 oracle 복잡도 분석
5. 실제 문제 또는 로컬 완결형 문제와 테스트

그 전까지는 이 허브 아래 reference로 유지합니다.

## 5. 연습 문제

이 허브의 연습 흐름은 [Practice Set](pages/practice-set.md)에 모읍니다. 적절한 h-contest 문제가 아직 없는 칸은 임의 ID를 넣지 않고 `TODO`로 둡니다.
