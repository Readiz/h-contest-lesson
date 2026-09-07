# 휴리스틱 알고리즘: 실험 로그와 개선 연산

## 실험 로그를 남긴다

로컬 실험에서는 입력과 solver seed를 고정한 뒤 다음 값을 기록합니다. 로그 출력은 제출 파일 바깥의 하네스에 둡니다.

- seed
- 초기해 점수
- 최종 점수
- 최고 점수가 나온 반복 번호
- 반복 횟수
- 사용한 파라미터

예를 들어 `START_TEMP`, `END_TEMP`, `BEAM_SIZE`, 변경 연산 비율을 바꿨다면 같은 입력 묶음에서 평균 점수와 최악 점수를 비교합니다. 한두 케이스에서만 좋아진 파라미터는 전체 성능을 망칠 수 있습니다.

## 자주 쓰는 개선 연산

| 연산 | 설명 | 잘 맞는 문제 |
| --- | --- | --- |
| swap | 두 원소의 위치를 바꾼다 | 순열, 방문 순서 |
| insert | 원소 하나를 빼서 다른 위치에 넣는다 | 작업 순서, 라우팅 |
| reverse | 구간을 뒤집는다 | 경로, 순회 |
| reassign | 원소 하나의 배정 대상을 바꾼다 | 스케줄링, 그룹 배정 |
| destroy/repair | 일부를 지우고 다시 채운다 | 제약이 많은 배치 |

예를 들어 순열 문제에서 `reverse` 연산은 배열만으로도 구현할 수 있습니다.

```cpp
void reverseRange(int a[], int left, int right) {
    while (left < right) {
        swapInt(a[left], a[right]);
        ++left;
        --right;
    }
}
```

두 작업의 배정을 바꾸는 연산은 다음처럼 만들 수 있습니다.

```cpp
void swapAssignedMachines(const Problem& p, State& s, int taskA, int taskB) {
    int machineA = s.machineOf[taskA];
    int machineB = s.machineOf[taskB];
    if (machineA == machineB) return;

    s.load[machineA] -= p.cost[taskA];
    s.load[machineB] -= p.cost[taskB];

    s.machineOf[taskA] = machineB;
    s.machineOf[taskB] = machineA;

    s.load[machineB] += p.cost[taskA];
    s.load[machineA] += p.cost[taskB];
}
```
