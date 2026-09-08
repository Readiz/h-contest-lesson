# Parallel Binary Search

여러 단조 질의를 같은 업데이트 sweep에서 판정하여 이분 탐색 비용을 공유합니다. 입력 전체를 미리 볼 수 있고 이전 답으로 다음 입력을 복호화하지 않는 조건에서 사용합니다.

## 적용과 처리


Parallel Binary Search는 여러 질의의 답을 각각 이분 탐색하되, 같은 mid를 가진 질의를 모아 한 번의 업데이트 sweep으로 처리하는 기법입니다.

적용 신호는 아래와 같습니다.

1. 각 질의의 답이 어떤 최소 시점/최소 값이다.
2. `mid`까지 업데이트를 적용했을 때 조건 만족 여부를 판정할 수 있다.
3. 만족 여부가 단조적이다.
4. 업데이트를 처음부터 순서대로 적용하는 비용을 여러 질의가 공유할 수 있다.

예를 들어 "몇 번째 업데이트 이후에 각 질의가 처음 만족되는가" 같은 문제에서 자주 등장합니다. 각 질의를 따로 이분 탐색하면 매번 업데이트를 다시 적용해야 하지만, PBS는 같은 라운드의 질의를 mid 기준으로 묶어서 처리합니다.


## 한 라운드

각 질의의 탐색 범위를 [lo,hi]로 두고 mid별 bucket에 넣습니다. 자료구조를 초기 상태로 되돌린 뒤 업데이트를 시간 순서로 한 번 적용하며 해당 mid bucket을 판정합니다. true면 hi=mid, false면 lo=mid+1로 줄입니다. 끝까지 만족하지 않는 질의를 위한 sentinel 시점을 별도로 둡니다.

한 sweep의 업데이트·판정·초기화 비용을 T라 하면 전체는 O(T log(answerRange))입니다. “parallel”은 여러 CPU가 아니라 질의들이 sweep을 공유한다는 뜻입니다.

Mo는 [Offline Range Query Techniques](https://h.readiz.com/learn/offline-time-axis-techniques/offline-range-query-techniques), 시간축 rollback은 [Rollback Techniques](https://h.readiz.com/learn/offline-time-axis-techniques/rollback-techniques)에서 봅니다.
