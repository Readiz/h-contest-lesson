# Segment Tree

Segment Tree는 배열을 여러 구간으로 나누어 저장하고, 구간 합/최솟값/최댓값 같은 질의를 빠르게 처리하는 자료구조입니다. 한국어로는 보통 **세그먼트 트리**라고 부릅니다.

대표적인 문제는 다음과 같습니다.

```text
배열 값이 바뀔 수 있다.
중간중간 구간 [l, r]의 합, 최솟값, 최댓값을 빠르게 물어본다.
```

배열을 매번 전부 훑으면 질의 하나가 `O(n)`입니다. Segment Tree를 쓰면 점 업데이트와 구간 질의를 모두 `O(log n)`에 처리할 수 있습니다.

## 문서 구성

- [기본 구간 질의](pages/basic-range-query.md): Top-down 재귀 Segment Tree로 구간 합 질의와 점 업데이트를 구현합니다.
- [Bottom-up 구현](pages/bottom-up-implementation.md): 반복문 기반 Segment Tree의 배열 배치와 질의 방식을 정리합니다.
- [Lazy Propagation](pages/lazy-propagation.md): 구간 업데이트와 구간 질의를 lazy 값으로 처리하는 구현을 다룹니다.
- [Monoid와 Lazy 합성](pages/monoid-and-lazy-composition.md): merge, 항등원, lazy 합성 규칙, 구현 선택 기준과 연습 문제를 정리합니다.

## 학습 순서

먼저 [기본 구간 질의](pages/basic-range-query.md)에서 구간을 나누는 관점을 익히고, [Bottom-up 구현](pages/bottom-up-implementation.md)으로 짧은 실전 구현을 봅니다. 구간 업데이트가 필요할 때 [Lazy Propagation](pages/lazy-propagation.md)을 읽고, 연산이 합이 아닐 때는 [Monoid와 Lazy 합성](pages/monoid-and-lazy-composition.md)에서 merge와 항등원을 다시 정리하세요.
