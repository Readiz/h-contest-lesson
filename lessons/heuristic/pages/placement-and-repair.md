# 휴리스틱 알고리즘: 배치형 문제의 destroy/repair와 부분 정확 탐색

## 18. 배치형 문제는 왜 어렵나

배치형 문제에서는 선택해야 할 것이 두 가지입니다.

1. 어떤 물건을 놓을 것인가
2. 어디에 놓을 것인가

일반적인 작업 배정 문제라면 `task -> machine`처럼 배정 대상만 정하면 됩니다. 하지만 2D 배치 문제에서는 같은 물건을 같은 판에 놓더라도 좌표에 따라 이후 빈 공간의 모양이 달라집니다.

그래서 first-fit은 빠르지만 자주 약합니다.

```text
나쁜 예:
- 처음 들어가는 위치에 바로 놓는다.
- 큰 물건이 들어갈 수 있는 공간을 작은 물건이 먼저 잘라 버린다.
- 남은 공간이 얇고 긴 조각으로 쪼개진다.
```

배치형 문제에서는 "가능한 위치"가 아니라 "나중에도 좋은 위치"를 골라야 합니다.

## 19. bitmask로 점유 상태를 표현하기

격자의 폭이 작다면 각 행을 bitmask 하나로 표현할 수 있습니다.

예를 들어 폭이 24라면 `unsigned int` 하나로 한 행의 점유 상태를 저장할 수 있습니다.

```cpp
const int MAX_BOARD = 32;
const int MAX_H = 32;

unsigned int occ[MAX_BOARD][MAX_H];

int canPlace(int board, int y, int x, int h, int w) {
    unsigned int mask = ((1u << w) - 1u) << x;

    for (int r = 0; r < h; ++r) {
        if (occ[board][y + r] & mask) {
            return 0;
        }
    }
    return 1;
}

void setPlace(int board, int y, int x, int h, int w) {
    unsigned int mask = ((1u << w) - 1u) << x;

    for (int r = 0; r < h; ++r) {
        occ[board][y + r] |= mask;
    }
}

void clearPlace(int board, int y, int x, int h, int w) {
    unsigned int mask = ((1u << w) - 1u) << x;

    for (int r = 0; r < h; ++r) {
        occ[board][y + r] &= ~mask;
    }
}
```

이 방식의 장점은 배치 가능 여부 검사가 빠르다는 점입니다. 특히 destroy/repair처럼 배치를 수천 번 지우고 다시 채우는 알고리즘에서는 이 차이가 큽니다.

주의할 점은 폭이 32 이상이면 `unsigned long long`을 쓰거나 행을 여러 블록으로 나누어야 한다는 것입니다.

## 20. 금지 칸도 bitmask에 합친다

창문, 벽, 장애물, 예약 구역처럼 배치할 수 없는 칸이 있다면 이를 별도 조건으로 매번 검사할 필요가 없습니다. 처음부터 점유 mask에 합치면 `canPlace`가 단순해집니다.

```cpp
unsigned int blocked[MAX_BOARD][MAX_H];
unsigned int occ[MAX_BOARD][MAX_H];

void initBoard(int board, int h) {
    for (int y = 0; y < h; ++y) {
        occ[board][y] = blocked[board][y];
    }
}
```

이렇게 하면 창문과 이미 놓인 물건을 같은 방식으로 처리할 수 있습니다.

```text
배치 불가능한 칸 = blocked mask
이미 사용한 칸 = placed item mask
검사할 때는 둘을 구분하지 않고 occ만 본다.
```

단, 나중에 물건을 제거해야 한다면 blocked와 item mask를 분리해서 가지고 있어야 합니다. 초기화할 때는 `occ = blocked`로 시작하고, 물건을 놓고 지우는 연산은 item 영역만 바꾸는 방식이 안전합니다.

## 21. first-fit 대신 위치 평가식을 만든다

배치형 문제에서 가장 흔한 실수는 "처음 가능한 위치"에 바로 놓는 것입니다.

```text
for each item:
    for y:
        for x:
            if canPlace(y, x):
                place(y, x)
                break
```

이 방식은 빠르지만, 좋은 공간을 쉽게 망가뜨립니다. 대신 가능한 모든 좌표를 보고 점수가 가장 높은 위치를 고릅니다.

```cpp
long long evaluatePlacement(int board, int item, int y, int x) {
    long long value = 0;

    value += itemScore(item);
    value += boardBonus(board);

    value += contactScore(board, item, y, x);
    value -= fragmentationPenalty(board, item, y, x);

    return value;
}
```

여기서 중요한 것은 실제 점수뿐 아니라 "이 배치가 이후 repair에 좋은 형태를 남기는가"입니다.

## 22. contact-aware placement

직사각형 배치 문제에서는 벽, 장애물, 기존 물건에 잘 붙여 놓는 것이 유리할 때가 많습니다. 이를 contact라고 부를 수 있습니다.

```text
contact = 새 물건의 변이 벽, 장애물, 기존 물건과 맞닿는 길이
```

contact가 높으면 빈 공간이 덜 조각나는 경우가 많습니다.

```cpp
long long placementScore(int realScore, int area, int contact) {
    long long score = 0;

    score += realScore * 1000;
    score += contact * 10;
    score += contact * contact * 100 / area;

    return score;
}
```

`contact * contact / area` 같은 항을 넣으면 작은 물건이 구석이나 틈에 깔끔하게 붙는 배치를 더 선호하게 만들 수 있습니다.

단, contact만 너무 크게 주면 큰 물건이 들어갈 중앙 공간을 잃을 수 있습니다. 따라서 실제 점수, 면적, 남은 공간 평가와 함께 써야 합니다.

## 23. repair 함수가 강해야 destroy/repair가 강하다

`destroy/repair`는 일부 배치를 지운 뒤 다시 채우는 방식입니다.

```text
current = greedy_initial_solution()

repeat:
    backup = current
    remove several placed items
    repair by greedy placement

    if score(current) improves:
        keep current
    else:
        rollback to backup
```

여기서 핵심은 repair입니다. repair가 단순 first-fit이면, destroy를 여러 번 해도 비슷한 답으로 돌아가기 쉽습니다. 반대로 repair가 contact-aware placement를 쓰면 제거된 공간을 더 좋은 형태로 다시 채울 수 있습니다.

## 24. 작은 destroy와 큰 destroy

처음에는 원소 1개나 2개를 지우는 작은 destroy를 시도할 수 있습니다. 하지만 배치형 문제에서는 작은 destroy만으로는 구조가 거의 바뀌지 않는 경우가 많습니다.

```text
작은 destroy:
- 장점: 안정적이다.
- 단점: 지역 최적을 벗어나기 어렵다.

큰 destroy:
- 장점: 나쁜 배치 구조를 크게 흔들 수 있다.
- 단점: repair가 약하면 점수가 크게 떨어진다.
```

그래서 큰 destroy는 강한 repair 함수와 함께 써야 합니다.

```cpp
const int REMOVE_COUNT = 30;
const int ITERATION_LIMIT = 10000;

for (int iter = 0; iter < ITERATION_LIMIT; ++iter) {
    backupState();

    for (int k = 0; k < REMOVE_COUNT; ++k) {
        removeRandomPlacedItem();
    }

    repairByPlacementGreedy();

    if (currentScore > bestScore) {
        saveBest();
    } else {
        rollbackState();
    }
}
```

`REMOVE_COUNT`에는 정답이 없습니다. 작게 잡으면 안정적이지만 개선 폭이 작고, 크게 잡으면 넓게 움직이지만 repair 실패가 늘어납니다. 실험 로그를 남기면서 문제별로 조정해야 합니다.

## 25. 제거 대상을 완전히 무작위로만 고르지 않는다

큰 destroy를 할 때 제거 대상을 완전히 무작위로만 고르면 개선이 느릴 수 있습니다. 다음 기준을 섞으면 더 빠르게 좋아질 때가 많습니다.

```text
- 최근에 배치한 물건을 지운다.
- 점수 대비 면적 효율이 낮은 물건을 지운다.
- 특정 구역 하나를 통째로 비운다.
- 충돌이 많이 나는 중심 구역 주변을 비운다.
- 랜덤 제거와 목적 제거를 일정 비율로 섞는다.
```

예를 들어 70%는 무작위 제거, 30%는 특정 판 하나를 비우는 식으로 섞을 수 있습니다. 완전 무작위는 다양한 답을 보게 해 주고, 목적 제거는 나쁜 구조를 빠르게 고치는 데 도움이 됩니다.

## 26. 부분 exact repair

휴리스틱과 정확 알고리즘은 반대가 아닙니다. 전체 문제는 너무 커서 정확히 풀 수 없어도, 작은 부분은 정확히 다시 풀 수 있습니다.

배치형 문제에서는 다음 단위를 부분 문제로 잡기 좋습니다.

```text
- 특정 판 하나
- 특정 행 범위
- 특정 구역
- 최근 destroy에서 제거된 물건 집합
- 점수가 낮은 구역과 그 주변 물건
```

예를 들어 특정 판 하나에 들어갈 후보가 40개 이하라면 DFS로 다시 채워 볼 수 있습니다.

```cpp
void dfsRepair(int idx, long long score) {
    if (idx == candidateCount) {
        updateBest(score);
        return;
    }

    int item = candidate[idx];

    // 1. 이 물건을 배치하지 않는 경우
    dfsRepair(idx + 1, score);

    // 2. 가능한 모든 위치에 배치하는 경우
    for (int y = 0; y + height[item] <= boardH; ++y) {
        for (int x = 0; x + width[item] <= boardW; ++x) {
            if (!canPlace(board, y, x, height[item], width[item])) continue;

            setPlace(board, y, x, height[item], width[item]);
            dfsRepair(idx + 1, score + itemScore(item));
            clearPlace(board, y, x, height[item], width[item]);
        }
    }
}
```

이 코드는 그대로 쓰기에는 느릴 수 있습니다. 실전에서는 후보 수 제한, 점수순 정렬, 남은 최대 점수 upper bound, 시간 제한을 함께 둡니다.

## 27. upper bound로 DFS 가지치기

부분 exact repair가 느리면 남은 후보의 최대 가능 점수를 이용해 가지치기합니다.

```cpp
long long suffixMaxScore[MAX_CANDIDATE + 1];

void dfsRepair(int idx, long long score) {
    if (score + suffixMaxScore[idx] <= bestRepairScore) {
        return;
    }

    if (idx == candidateCount) {
        updateBest(score);
        return;
    }

    // 배치하지 않는 경우와 배치하는 경우를 탐색한다.
}
```

`suffixMaxScore[idx]`는 `idx` 이후 후보를 모두 넣는다고 가정한 느슨한 상한입니다. 실제로는 겹쳐서 모두 넣을 수 없더라도, 상한으로는 충분합니다. 이 상한조차 현재 best를 넘지 못하면 더 내려갈 필요가 없습니다.

## 28. Beam Search보다 repair가 나을 때

Beam Search는 후보 평가식이 정확할 때 강합니다. 하지만 배치형 문제에서는 완성 전 후보의 점수가 부정확한 경우가 많습니다.

예를 들어 초반에 점수가 높은 물건을 많이 넣은 후보가 좋아 보이지만, 실제로는 남은 큰 물건이 들어갈 공간을 망쳐 최종 점수가 낮아질 수 있습니다.

이런 문제에서는 다음 전략이 더 잘 맞을 수 있습니다.

```text
1. greedy로 빠르게 완성된 답을 만든다.
2. 완성된 답의 실제 점수를 본다.
3. destroy/repair로 완성된 답끼리 비교한다.
4. 작은 구역은 exact repair로 보정한다.
```

즉, 평가가 어려운 미완성 후보를 오래 들고 가기보다, 완성된 답을 많이 만들고 실제 점수로 비교하는 쪽이 더 안정적일 수 있습니다.

## 29. 배치형 휴리스틱 체크리스트

배치형 문제를 풀 때는 아래 질문을 확인합니다.

1. 점유 상태 검사가 충분히 빠른가?
2. first-fit으로 빈 공간을 망가뜨리고 있지 않은가?
3. 위치 평가식에 실제 점수 외의 packing 품질이 들어 있는가?
4. repair 함수가 destroy 이후 좋은 답을 다시 만들 수 있는가?
5. destroy 크기가 너무 작거나 너무 크지 않은가?
6. 작은 부분 문제를 exact DFS/DP로 다시 풀 수 있는가?
7. seed, remove count, 반복 수, 후보 수를 실험 로그로 남겼는가?
8. 특정 seed에서만 좋아진 파라미터를 전체에 적용하고 있지 않은가?

배치형 문제는 한 번의 깔끔한 공식보다 상태 표현, 위치 평가식, repair 품질, 반복 실험이 더 중요합니다. 처음에는 단순 greedy로 시작하고, 그 다음에는 "어디에 놓을지"와 "무엇을 다시 지울지"를 점점 똑똑하게 만드는 방향으로 개선하는 것이 좋습니다.

## 30. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 표준 | [광고판 도시 배치](/practice/BILLCITY) | 창문과 기존 광고를 bitmask 점유 상태로 합치고, contact-aware greedy repair를 구현 | bitmask, placement score, contact |
| 응용 | [상자 쌓기](/practice/STACKING) | 3D 배치에서 작은 move와 큰 destroy/repair의 차이 확인 | packing, fragmentation, repair |
| 함정 | TODO: 부분 exact repair 검증 `/practice/...` 문제 필요 | 작은 구역만 정확 탐색으로 다시 푸는 기준 잡기 | upper bound, candidate limit |
