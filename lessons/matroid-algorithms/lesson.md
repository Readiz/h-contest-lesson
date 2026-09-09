# Matroid Algorithms

Matroid Algorithms는 greedy가 맞는 독립성 구조와, greedy가 막힐 때 필요한 exchange 기반 조합 최적화를 묶는 reference 허브입니다. 각 페이지는 모델과 제한형을 다루며 범용 구현을 제공하지 않습니다.

## 모델 선택 표

| 문제 신호 | 먼저 볼 페이지 |
| --- | --- |
| greedy가 맞는 독립성 구조인지 판정해야 한다 | [Matroid Basics and Exchange](pages/matroid-basics-and-exchange.md) |
| 두 독립성 조건을 동시에 만족해야 한다 | [Matroid Intersection](pages/matroid-intersection.md) |
| 여러 독립 집합의 합이나 분해를 묻는다 | [Matroid Union](pages/matroid-union.md) |
| pair 단위 선택과 독립성 조건이 결합된다 | [Matroid Parity](pages/matroid-parity.md) |

## 독립성 판정 비용

| 구조 | 구현해야 할 판정 |
| --- | --- |
| Partition matroid | 그룹별 count와 capacity |
| Graphic matroid | 추가는 DSU, 삭제·교환은 별도 처리 |
| Linear matroid | basis 구성과 rank 판정 |
| 일반 oracle | exchange graph 후보 수와 oracle 호출 비용 분석 |

현재 Intersection·Union·Parity 페이지는 모델과 제한형을 설명합니다. 범용 알고리즘 구현이 필요하면 독립성 판정뿐 아니라 교환 경로 탐색·선택 복구와 그 복잡도까지 준비되어야 합니다.

## 연습

[로컬 연습](pages/matroid-basics-and-exchange.md)에서 입력과 검증 기준을 확인합니다.
