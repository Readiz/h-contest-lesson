# Practice Set

Matroid Algorithms 허브의 연습은 일반 범용 알고리즘보다 모델 판독과 특수형 구현 가능성 확인에 초점을 둡니다. 실제 h-contest 문제가 아직 부족한 주제는 임의 ID를 만들지 않고 `TODO`로 남깁니다.

## 1. 연습 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: partition matroid greedy `/practice/...` 문제 필요 | class별 capacity와 greedy 증명 | exchange |
| 표준 | TODO: graphic + partition matroid `/practice/...` 문제 필요 | forest 조건과 색상 제한 결합 | matroid intersection |
| 응용 | TODO: forest decomposition `/practice/...` 문제 필요 | 여러 forest layer로 간선 분해 | matroid union |
| 함정 | TODO: pair-choice counterexample `/practice/...` 문제 필요 | parity와 partition constraint 구분 | matroid parity |

## 2. 로컬 완결형 연습 후보

### Weighted Partition Matroid

각 물건은 class와 weight를 가지고, class별로 선택할 수 있는 개수가 제한됩니다. weight가 큰 순서로 보며 class capacity를 넘지 않으면 선택하는 greedy를 구현하고, exchange argument로 정당성을 설명합니다.

### Graphic Matroid Greedy

간선마다 weight가 있을 때 cycle이 생기지 않도록 최대 weight forest를 고릅니다. Kruskal의 maximum spanning forest 버전으로 구현하고, "graphic matroid greedy" 관점으로 증명을 다시 써 봅니다.

### Naive Union Failure Trace

간선을 두 forest로 색칠하는 작은 그래프를 만들고, 입력 순서 greedy가 실패하지만 교환하면 성공하는 예시를 손으로 추적합니다. 이 연습은 Matroid Union이 독립 구현 레슨으로 올라가려면 필요한 trace의 최소 형태입니다.

## 3. 제출 전 체크리스트

- 제약이 정말 matroid 공리를 만족하는가?
- 단일 matroid greedy인지, intersection/union/parity인지 구분했는가?
- 독립성 oracle의 시간 복잡도를 입력 제한에 맞췄는가?
- greedy가 깨지는 반례를 하나 만들었는가?
- 일반 이론 대신 문제 특수 구조로 더 쉬워지는 부분이 있는가?
