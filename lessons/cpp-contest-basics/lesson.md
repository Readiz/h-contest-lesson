# 실전 C++ 제출과 검증

첫 목표는 **문제의 공개 API만으로 유효한 답을 끝까지 만드는 것**입니다. h-contest의 함수 구현형 `user.cpp`를 기준으로, STL·표준 헤더 없이 제출 계약과 TC 초기화를 확인하고 ORDERING의 기준선을 실행합니다.

변수·반복문·함수·배열의 기초 문법은 알고 있다고 가정합니다. `struct`, 참조, `template`는 사용할 수 있습니다.

## 문제를 풀기 시작하는 순서

1. [제출 계약과 상태 초기화](pages/submission-and-state.md)에서 호출 순서·배열 상한·점수 방향을 확인합니다.
2. [ORDERING 기준선 실행과 검증](pages/practice.md)에서 유효한 답을 만들고 실제 채점기의 비용을 기록합니다.
3. [배송 순서 개선](https://h.readiz.com/learn/heuristic/ordering-route-improvement)에서 nearest neighbor와 2-opt를 추가합니다.
4. [차분·복구 검증](https://h.readiz.com/learn/testing-and-stress)을 거쳐 [지역 탐색과 SA](https://h.readiz.com/learn/heuristic/search-strategies)로 진행합니다.

배열·난수·정렬·큐·힙은 별도 [STL 없는 공통 라이브러리](https://h.readiz.com/learn/cpp-common-library)에서 찾아 씁니다. 필요한 블록만 풀이 앞에 붙입니다. 라이브러리 전체를 선행 학습하거나 문제마다 다시 구현할 필요는 없습니다.

문제별 상태·평가 함수·이동 연산은 풀이에 두고, 재사용할 배열·자료구조 연산은 공통 라이브러리에 둡니다. 제출 코드와 비교용 로컬 하네스의 환경은 각 페이지에서 구분합니다.
