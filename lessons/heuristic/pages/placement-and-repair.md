# 휴리스틱 알고리즘: 실전 예시 - 광고판 도시 배치

## 18. 이 페이지를 읽는 방법

앞 페이지까지는 상태 표현, 점수 함수, 초기해, 지역 탐색, Beam Search, 실험 로그를 따로 보았습니다. 실제 문제에서는 이 개념들이 분리되어 나오지 않습니다.

이 페이지는 [광고판 도시 배치](/practice/BILLCITY)를 따라가며, 휴리스틱 풀이가 어떻게 단계적으로 강해지는지 보는 실전 예시입니다. 목적은 광고판 문제 전용 공식을 외우는 것이 아니라, 아래 흐름을 익히는 것입니다.

```text
문제 구조 읽기
-> 빠른 상태 표현 만들기
-> 단순한 초기해 만들기
-> 좋은 순서와 좋은 위치를 따로 평가하기
-> 작은 local search의 한계를 확인하기
-> 큰 destroy/repair로 구조를 흔들기
-> 작은 부분만 exact repair로 보정하기
```

## 19. 문제 구조 요약

`BILLCITY`는 `process(buildings, ads)` 안에서 `place_ad(adId, buildingId, top, left)`를 호출해 광고판을 놓는 문제입니다.

문제 구조는 다음과 같습니다.

| 항목 | 내용 |
| --- | --- |
| 건물 수 | 20개 |
| 광고 수 | 132개 |
| 건물 타입 | `WAREHOUSE`, `STORE` |
| 점수 | `WAREHOUSE`는 `ad.score`, `STORE`는 `ad.score * 2` |
| 금지 조건 | 건물 밖, 창문 칸, 다른 광고와 겹치기, 같은 광고 재사용 |
| 회전 | 광고는 회전하지 않는다 |
| 출력 | 각 TC의 `SCORE`, 마지막 합산 `SCORE` |

이 문제는 단순히 광고를 많이 넣는 문제가 아닙니다. 좋은 광고를 골라야 하고, `STORE` 보너스를 활용해야 하며, 남은 빈 공간이 나쁘게 쪼개지지 않도록 좌표를 골라야 합니다.

## 20. 앞 페이지 개념과의 대응

| 휴리스틱 개념 | 이 문제에서의 모습 |
| --- | --- |
| 상태 표현 | 건물별 점유 mask, 광고별 배치 여부, 현재 점수 |
| 점수 함수 | 실제 점수와 배치 품질 평가를 분리 |
| 초기해 | 광고 순서와 건물 순서를 정한 뒤 greedy 배치 |
| 개선 연산 | 일부 광고를 제거하고 다시 채우는 destroy/repair |
| 정확 알고리즘 결합 | 한 건물이나 작은 구역만 DFS로 다시 채우기 |
| 실험 로그 | 단계별 score, remove count, 반복 수, 후보 수 비교 |

이 대응표를 먼저 잡으면, 코드를 고칠 때 "무엇을 먼저 개선해야 하는가"가 보입니다.

## 21. 0점에서 first-fit까지

처음에는 아무것도 하지 않는 `process`로 0점을 확인합니다. 이 단계는 쓸모없어 보이지만, 채점기가 어떤 형식으로 점수를 출력하는지 확인하는 기준선입니다.

그다음은 가장 단순한 first-fit입니다.

```text
for ad in input_order:
    for building in input_order:
        for top, left in row_major_order:
            if place_ad(ad, building, top, left):
                break
```

first-fit은 빠르고 구현이 쉽습니다. 하지만 좋은 좌표를 고르지 않습니다. 처음 들어가는 위치에 바로 놓기 때문에 큰 광고가 들어갈 수 있는 공간을 작은 광고가 먼저 잘라 버릴 수 있습니다.

이 단계에서 확인할 것은 점수가 높냐가 아니라, 아래 두 가지입니다.

1. `place_ad` 호출 순서가 맞는가?
2. 로컬 상태를 만들 경우 judge의 성공/실패 판단과 같은가?

## 22. 정렬 greedy: 무엇을 먼저 놓을 것인가

first-fit 다음에는 "무엇을 먼저 볼 것인가"를 고칩니다.

이 문제에서는 광고마다 `score`, `h`, `w`가 다르고 `STORE`는 점수가 2배입니다. 그래서 입력 순서보다 아래 기준이 자연스럽습니다.

```text
광고 순서:
- score가 높은 광고
- score / area가 높은 광고
- 큰 광고를 먼저 넣어야 빈 공간이 덜 망가지는 경우

건물 순서:
- STORE 먼저
- 유효 빈칸이 큰 건물 먼저
- 창문 때문에 모양이 까다로운 건물은 별도 평가
```

정렬 greedy는 "좋은 물건을 먼저 본다"는 의미입니다. 하지만 이것만으로는 아직 부족합니다. 같은 광고를 같은 건물에 넣더라도 좌표에 따라 이후 공간이 달라지기 때문입니다.

## 23. 위치 평가식: 어디에 놓을 것인가

이 문제의 분기점은 "놓을 수 있는 첫 위치"와 "나중에도 좋은 위치"를 구분하는 데 있습니다.

건물 폭이 작기 때문에 각 행을 bitmask로 들면 배치 가능 여부를 빠르게 검사할 수 있습니다.

```cpp
unsigned int occ[20][24];

int canPlaceLocal(int bid, int y, int x, int h, int w) {
    unsigned int mask = ((1u << w) - 1u) << x;

    for (int r = 0; r < h; ++r) {
        if (occ[bid][y + r] & mask) return 0;
    }
    return 1;
}
```

창문도 처음부터 `occ`에 넣어 두면, 이후 배치 검사는 "이미 막힌 칸과 겹치는가" 하나로 단순해집니다. 단, 광고를 제거해야 하므로 창문 mask와 광고 mask를 분리해서 복구할 수 있게 해야 합니다.

좌표를 평가할 때는 실제 점수만 보면 부족합니다.

```text
placement value =
    실제 점수
  + STORE 보너스
  + 벽, 창문, 기존 광고와 붙는 contact 보너스
  - 빈 공간을 얇게 쪼개는 penalty
```

contact가 높으면 광고가 구석이나 기존 물체에 붙어 빈 공간을 덜 조각내는 경우가 많습니다. 단, contact만 크게 주면 큰 광고가 들어갈 중앙 공간을 잃을 수 있으므로 실제 점수와 같이 봐야 합니다.

## 24. 작은 local search의 한계

정렬 greedy 이후에는 이미 놓은 광고 하나를 빼고 다른 광고를 넣어 보는 작은 local search를 시도할 수 있습니다.

```text
1. 점수 대비 효율이 낮은 광고 하나를 제거한다.
2. 미배치 광고 중 좋은 후보를 몇 개 넣어 본다.
3. 점수가 오르면 유지하고, 아니면 rollback한다.
```

이 방식은 local search의 감각을 잡기 좋습니다. 하지만 배치 문제에서는 광고 하나만 빼도 빈 공간 구조가 크게 바뀌지 않습니다. 이미 나쁘게 쪼개진 공간은 작은 이동만으로 회복하기 어렵습니다.

이 지점에서 "작은 move가 충분한 문제인가, 큰 구조를 다시 만들어야 하는 문제인가"를 판단해야 합니다.

## 25. 큰 destroy/repair

배치 구조를 바꾸려면 한 번에 여러 광고를 지우고 다시 채우는 편이 강합니다.

```text
best = contact-aware greedy 결과

repeat:
    current = best 복사
    광고 여러 개를 제거한다
    제거된 광고와 미배치 광고를 다시 후보로 만든다
    contact-aware greedy로 다시 채운다

    current가 좋아졌으면 best로 채택한다
```

여기서 중요한 것은 destroy보다 repair입니다. repair가 first-fit이면 큰 destroy를 해도 낮은 품질의 배치로 돌아가기 쉽습니다. 반대로 repair가 위치 평가식을 잘 쓰면, 같은 공간을 더 좋은 모양으로 다시 채울 수 있습니다.

제거 대상을 완전히 무작위로만 고를 필요도 없습니다.

```text
- 최근에 배치한 광고
- 점수 대비 면적 효율이 낮은 광고
- 특정 건물 하나에 놓인 광고 전체
- 창문 주변에서 공간을 많이 막는 광고
- 무작위 제거와 목적 제거를 섞은 후보
```

remove count는 실험값입니다. 너무 작으면 지역 최적을 벗어나지 못하고, 너무 크면 매번 거의 새로 만드는 것과 비슷해집니다.

## 26. 건물 단위 partial exact repair

전체 문제를 정확히 푸는 것은 어렵습니다. 하지만 건물 하나만 떼어 내면 후보 수가 줄어듭니다.

```text
for each building:
    현재 building에 놓인 광고를 모두 제거한다
    미배치 광고 중 이 building에 넣어 볼 후보를 고른다
    DFS로 이 building만 다시 채워 본다
    좋아졌으면 채택하고, 아니면 rollback한다
```

이 방식은 휴리스틱과 정확 탐색을 섞는 전형적인 패턴입니다. 전체는 greedy와 destroy/repair로 넓게 찾고, 작은 부분은 DFS나 DP로 촘촘하게 다시 봅니다.

DFS는 반드시 제한을 둬야 합니다.

```text
- 후보 수 제한
- node 방문 수 제한
- 남은 후보 점수 upper bound
- 한 건물 또는 한 구역 단위 제한
```

느슨한 upper bound라도 효과가 있습니다. 남은 후보를 모두 넣는다고 가정해도 현재 best를 넘지 못하면 더 내려갈 필요가 없습니다.

## 27. Beam Search보다 repair가 먼저일 수 있다

Beam Search는 부분 상태의 평가식이 좋을 때 강합니다. 그런데 이 문제에서는 미완성 배치의 점수를 평가하기 어렵습니다.

초반에 높은 점수 광고를 많이 넣은 후보가 좋아 보여도, 실제로는 큰 광고가 들어갈 공간을 망쳐 최종 점수가 낮을 수 있습니다. 이럴 때는 미완성 후보를 오래 들고 가는 것보다 완성된 답을 많이 만들고 실제 점수로 비교하는 편이 안정적입니다.

```text
완성된 greedy 답 생성
-> destroy/repair로 완성 답끼리 비교
-> 작은 구역 exact repair
```

Beam Search를 쓰지 말라는 뜻은 아닙니다. 다만 이 문제에서는 repair 함수가 약한 상태에서 Beam 크기를 키우는 것보다, 먼저 repair 품질을 올리는 쪽이 점수 상승으로 이어지기 쉽습니다.

## 28. 단계별 로그를 읽는 방법

광고판 배치 실험 로그는 아래처럼 읽을 수 있습니다.

| 단계 | 관찰할 변화 | 의미 |
| ---: | --- | --- |
| 0 | 아무것도 하지 않음 | 채점 출력과 기준선 확인 |
| 1 | 입력 순서 first-fit | 유효한 답을 만드는 최소선 |
| 2 | 점수순 greedy | 무엇을 먼저 놓을지의 효과 |
| 3 | 작은 local search | 작은 move의 개선 폭과 한계 |
| 4 | contact-aware greedy | repair 함수의 품질 개선 |
| 5 | large destroy/repair | 배치 구조를 크게 흔드는 효과 |
| 6 | building exact repair | 작은 부분 문제를 정확히 다시 푸는 효과 |
| 7 | 반복 수와 제거 개수 튜닝 | seed와 파라미터 로그의 중요성 |

본문에 특정 점수를 외울 필요는 없습니다. 중요한 것은 아래 결론입니다.

```text
first-fit에서 정렬 greedy로 갈 때 큰 폭으로 좋아진다.
contact-aware greedy는 단독 점수보다 repair 품질을 올리는 역할이 크다.
large destroy/repair는 작은 local search가 못 바꾸는 배치 구조를 바꾼다.
partial exact repair는 마지막 빈틈을 줄이는 보정 단계다.
```

## 29. 제출 전 체크리스트

광고판 배치 같은 문제를 제출하기 전에는 아래를 확인합니다.

1. 로컬 `canPlace`와 실제 `place_ad`의 판단이 같은가?
2. 창문 mask와 광고 mask를 분리해 rollback할 수 있는가?
3. `STORE` 2배 보너스가 광고 순서와 건물 순서에 반영되어 있는가?
4. 위치 평가식이 실제 점수만 보지 않고 남은 공간 품질도 보는가?
5. destroy 후 repair가 first-fit으로 돌아가지 않는가?
6. remove count, 반복 수, 후보 수를 seed별로 기록했는가?
7. exact repair는 node limit과 upper bound가 있어 시간 안에 끝나는가?
8. 한두 TC에서만 좋아진 파라미터를 전체에 적용하고 있지 않은가?

## 30. 연습 문제

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | [미니 물품 배송](/practice/ORDERING) | 열린 경로의 유효한 순열을 만들고 nearest neighbor와 2-opt로 개선 | permutation, nearest neighbor, 2-opt |
| 입문 | [맨해튼 TSP](/practice/TSPTESTX) | 순열 해와 점수 함수를 만들고 초기해를 개선 | nearest neighbor, 2-opt |
| 표준 | [광고판 도시 배치](/practice/BILLCITY) | 창문과 기존 광고를 bitmask 점유 상태로 합치고, contact-aware greedy repair를 구현 | bitmask, placement score, contact |
| 응용 | [상자 쌓기](/practice/STACKING) | 배치 문제에서 작은 move와 큰 destroy/repair의 차이 확인 | packing, fragmentation, repair |
| 함정 | [작업 스케줄링](/practice/SCHEDULX) | 지역 탐색이 특정 seed에만 맞춰지는 문제 점검 | load balance, seed |

다음 페이지에서는 같은 휴리스틱 설계 순서를 순열 문제에 적용합니다. [미니 물품 배송](/practice/ORDERING)에서는 배치 상태 대신 방문 순서를 들고, 전체 경로를 매번 다시 계산하지 않는 2-opt 차분 계산이 핵심이 됩니다.
