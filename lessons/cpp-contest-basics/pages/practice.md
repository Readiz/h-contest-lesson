# ORDERING 기준선 실행과 검증

먼저 [제출 계약과 상태 초기화](https://h.readiz.com/learn/cpp-contest-basics/submission-and-state)의 번호 순서 기준선을 실행합니다. 배열·난수·자료구조의 공통 구현과 경계 연습은 별도 [공통 라이브러리](https://h.readiz.com/learn/cpp-common-library)에서 다룹니다. 여기서는 공개 API에 맞는 유효한 결과와 실제 비용을 확인합니다.

## 실제 ORDERING 채점기로 유효한 기준선 만들기

[ORDERING](/practice/ORDERING)의 패키지에서 `main.cpp`와 제공 `user.cpp`를 별도 작업 폴더로 복사합니다. `user.cpp`에는 첫 페이지의 `ordering-baseline` 블록을 넣습니다. 원본 문제 패키지의 템플릿은 풀이로 덮어쓰지 않습니다.

```bash
c++ -std=c++17 -O2 main.cpp user.cpp -o ordering-baseline
./ordering-baseline
```

채점기가 출력한 TC별 비용과 총점을 기록합니다. ORDERING은 **비용이 낮을수록 좋고**, 마지막 배송지에서 창고로 돌아오는 비용은 더하지 않는 열린 경로입니다. 번호 순서 기준선은 유효하지만 통과 기준 충족을 보장하지 않습니다. 2026-09-08의 로컬 패키지 10개 TC에서 이 블록의 총 비용은 `257071`이었습니다. 실행 시간은 환경에 따라 달라지므로 직접 측정합니다. 이 값은 운영 제출 결과가 아닌 제공 채점기의 로컬 실행 결과입니다.

| 확인할 것 | 통과 조건 |
| --- | --- |
| 배열 범위 | `order[0..n-1]`만 기록 |
| 창고 | `order[0] == 0` |
| 방문 | 모든 번호가 범위 안에서 정확히 한 번 등장 |
| 다음 TC | 이전 배열의 남은 값에 의존하지 않음 |
| 평가 | TC별 원래 비용, 총 비용, 실행 시간을 기록 |

첫 개선은 [ORDERING 경로 개선 사례](https://h.readiz.com/learn/heuristic/ordering-route-improvement)의 nearest neighbor입니다. 번호 순서 → 가까운 곳부터 선택 → 2-opt 순서로 한 번에 한 요소만 바꾸고 같은 TC에서 비교합니다. 난수 셔플이나 SA는 이 비교가 가능해진 다음에 추가합니다.
