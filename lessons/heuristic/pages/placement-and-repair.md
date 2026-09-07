# 휴리스틱 알고리즘: 실전 예시 - 광고판 도시 배치

## 문제 구조 요약

[광고판 도시 배치](/practice/BILLCITY)는 `process(buildings, ads)` 안에서 `place_ad(adId, buildingId, top, left)`를 호출해 광고판을 놓는 문제입니다.

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

## 0점에서 first-fit까지

아무것도 하지 않는 `process`의 점수는 0입니다.

그다음은 가장 단순한 first-fit입니다.

```text
for ad in input_order:
    for building in input_order:
        for top, left in row_major_order:
            if place_ad(ad, building, top, left):
                break
```

first-fit은 빠르고 구현이 쉽습니다. 하지만 좋은 좌표를 고르지 않습니다. 처음 들어가는 위치에 바로 놓기 때문에 큰 광고가 들어갈 수 있는 공간을 작은 광고가 먼저 잘라 버릴 수 있습니다.

로컬 `canPlace`를 작성했다면, 같은 위치에 대한 `place_ad`의 성공·실패 결과와 먼저 대조합니다.

## 정렬 greedy: 무엇을 먼저 놓을 것인가

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

## 위치 평가식: 어디에 놓을 것인가

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

## 작은 local search의 한계

정렬 greedy 이후에는 이미 놓은 광고 하나를 빼고 다른 광고를 넣어 보는 작은 local search를 시도할 수 있습니다.

```text
1. 점수 대비 효율이 낮은 광고 하나를 제거한다.
2. 미배치 광고 중 좋은 후보를 몇 개 넣어 본다.
3. 점수가 오르면 유지하고, 아니면 rollback한다.
```

광고 하나만 빼서는 빈 공간 구조가 크게 바뀌지 않습니다. 이미 나쁘게 쪼개진 공간은 작은 이동만으로 회복하기 어렵습니다.

## 큰 destroy/repair

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

## 건물 단위 partial exact repair

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

## Beam Search보다 repair가 먼저일 수 있다

Beam Search는 부분 상태의 평가식이 좋을 때 강합니다. 그런데 이 문제에서는 미완성 배치의 점수를 평가하기 어렵습니다.

초반에 높은 점수 광고를 많이 넣은 후보가 좋아 보여도, 실제로는 큰 광고가 들어갈 공간을 망쳐 최종 점수가 낮을 수 있습니다. 이럴 때는 미완성 후보를 오래 들고 가는 것보다 완성된 답을 많이 만들고 실제 점수로 비교하는 편이 안정적입니다.

```text
완성된 greedy 답 생성
-> destroy/repair로 완성 답끼리 비교
-> 작은 구역 exact repair
```

repair가 계속 같은 나쁜 배치를 만들면 반복 횟수나 빔 폭을 늘려도 개선 폭이 작습니다. 제거 개수와 repair 평가식을 따로 바꾸어 비교합니다.

## 다른 배치 문제

[상자 쌓기](/practice/STACKING)에서도 작은 이동으로 해소되지 않는 빈 공간이 생깁니다. 일부 배치를 제거한 뒤 다시 채우는 destroy/repair를 비교해 볼 수 있습니다.
