# Practice Set

Graph Cut Structures 허브의 연습은 cut 모델 선택을 먼저 하고, 그다음 deterministic, randomized, all-pairs, family representation으로 확장하는 순서가 좋습니다. 실제 h-contest 문제가 아직 부족한 주제는 임의 ID를 만들지 않고 `TODO`로 남깁니다.

## 1. 연습 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: global min cut `/practice/...` 문제 필요 | s-t cut과 global cut 구분 | Stoer-Wagner |
| 표준 | TODO: all pair min-cut query `/practice/...` 문제 필요 | cut-equivalent tree 질의 | Gomory-Hu |
| 응용 | TODO: sparse certificate min cut `/practice/...` 문제 필요 | 작은 cut 보존과 edge pruning | cut sparsification |
| 심화 | TODO: min cut family cactus `/practice/...` 문제 필요 | global min cut family 압축 | cactus |
| 함정 | TODO: randomized vs deterministic cut `/practice/...` 문제 필요 | Karger 실패 확률과 fallback | contraction |

## 2. 로컬 완결형 연습 후보

### Stoer-Wagner Partition Trace

작은 무향 weighted graph에서 Stoer-Wagner phase를 손으로 추적하고, 마지막 selected vertex가 만드는 candidate cut을 기록합니다. 값만 반환하지 말고 partition도 함께 저장합니다.

### Gomory-Hu Query Check

정점 4개 그래프에서 Gomory-Hu Tree를 만든 뒤, 모든 pair에 대해 원래 graph의 max-flow 값과 tree path minimum이 같은지 비교합니다.

### Karger Repetition Experiment

cycle graph와 complete graph에서 Karger contraction을 여러 seed로 반복하고, trial 수가 늘어날 때 best cut 값이 어떻게 안정되는지 확인합니다.

## 3. 제출 전 체크리스트

- `s-t`, global, all-pairs, family, threshold 중 어떤 모델인지 명시했는가?
- 무향/방향 조건을 확인했는가?
- disconnected graph의 global min cut 값 0을 처리했는가?
- Gomory-Hu 질의에서 path sum이 아니라 path minimum을 썼는가?
- randomized 풀이를 쓴다면 반복 횟수와 seed 정책을 설명했는가?
