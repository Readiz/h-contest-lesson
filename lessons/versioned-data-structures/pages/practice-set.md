# Practice Set

Versioned Data Structures 허브의 연습은 path copying, partial persistence, container versioning, sequence query 순서로 진행합니다. 실제 h-contest 문제가 아직 부족한 주제는 임의 ID를 만들지 않고 `TODO`로 남깁니다.

## 1. 연습 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: 버전별 구간 합 `/practice/...` 문제 필요 | path copying과 root 저장 | persistent segment tree |
| 표준 | TODO: persistent kth query `/practice/...` 문제 필요 | prefix root 차이와 좌표 압축 | order statistic |
| 응용 | TODO: persistent union-find `/practice/...` 문제 필요 | 과거 연결성 조회 | union time |
| 심화 | TODO: persistent sequence `/practice/...` 문제 필요 | split/merge 또는 version root 관리 | implicit treap |
| 함정 | TODO: rollback vs persistence `/practice/...` 문제 필요 | version branch와 undo log 구분 | rollback |

## 2. 로컬 완결형 연습 후보

### Versioned Array Sum

초기 배열에 point update를 적용할 때마다 새 version을 만들고, `(version, l, r)` 질의에 range sum을 답합니다. old node를 직접 수정하지 않는지 root별로 비교합니다.

### Prefix Kth Query

정적 배열에서 `[l, r]`의 k번째 작은 값을 묻습니다. `root[r] - root[l-1]` 차이로 구간 빈도를 만들고, 압축 좌표를 원래 값으로 복원합니다.

### Union History Query

간선 추가만 있는 그래프에서 time `t`의 연결성과 component size를 묻습니다. path compression 없이 union by size와 parent change time을 사용합니다.

## 3. 제출 전 체크리스트

- version root를 덮어쓰지 않았는가?
- old node를 직접 수정하지 않았는가?
- node 수 메모리 예산을 계산했는가?
- query가 read-only여야 하는 구조에서 lazy push가 상태를 바꾸지 않는가?
- rollback으로 더 단순해지는 문제를 persistent로 과하게 풀지 않았는가?
