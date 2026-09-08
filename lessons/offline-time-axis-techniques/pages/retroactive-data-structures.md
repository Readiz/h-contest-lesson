# Retroactive Data Structures

Retroactivity는 과거 연산 자체를 삽입·삭제해서 그 이후의 결과를 바꾸는 모델입니다. Persistence는 이미 만든 버전을 보존하고, rollback은 현재 실행 경로를 되돌립니다. 세 모델은 서로 대체되지 않습니다.

## 두 시간축

“현재 명령에서 과거 t에 연산을 추가”한다면 명령이 도착한 시간과 연산의 논리 시간이 따로 있습니다. 중간 답도 요구할 때 두 좌표를 하나로 합치거나 최종 timeline만 재생하면 틀립니다.

최종 수정된 timeline의 답만 묻는다면 수정사항을 모은 뒤 논리 시간 순서로 재실행할 수 있습니다. 명령 시간별로 활성 원소 집합만 답하면 되는 교환 가능한 연산은 생존 구간으로 바꿀 수 있습니다. 일반적인 과거 연산 삽입·삭제 전체가 이 형태는 아닙니다.

## deleteMin 반례

```text
t=1 insert 5
t=2 deleteMin
t=3 insert 3
```

원래 현재 집합은 {3}입니다. t=1에 insert 1을 추가하면 deleteMin이 1을 지워 현재 집합은 {3,5}가 됩니다. 뒤 연산의 의미가 바뀌므로 단순히 추가 원소의 활성 구간만 적용해서는 해결되지 않습니다.

시간별 간선 생존 구간이 이미 정해지는 제한형은 [Dynamic Connectivity](https://h.readiz.com/learn/offline-time-axis-techniques/dynamic-connectivity)의 구현을 사용합니다. 일반 fully retroactive priority queue 등은 별도 알고리즘과 복잡도 분석이 필요합니다.
