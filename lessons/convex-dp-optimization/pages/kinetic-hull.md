# Kinetic Hull

Kinetic Hull은 점이나 직선이 시간에 따라 움직일 때, 현재 최적 점이나 볼록 껍질을 event 단위로 갱신하는 관점입니다. 정적인 Convex Hull이나 Convex Hull Trick은 한 번 만든 구조를 질의하지만, kinetic 문제는 시간이 흐르면서 최적 후보가 바뀌는 순간을 추적합니다.

## 문제 신호

| 문제 표현 | Kinetic Hull 관점 |
| --- | --- |
| 점의 좌표가 시간에 따라 선형으로 변함 | moving points hull |
| 직선 `y = m(t)x + b(t)` 중 최솟값/최댓값 | time-dependent line envelope |
| 가장 먼 점 쌍, support direction 최댓값이 바뀜 | event between candidates |
| 모든 시간에 대해 답이 필요하지 않고 변화 시점만 필요 | event queue |
| 시간이 단조로 진행됨 | invalid event lazy deletion 가능 |

정확한 대회 문제에서는 event 수가 제한되는 구조가 있어야 합니다. 아무 제약 없이 모든 교차를 추적하면 `O(N^2)` event가 생길 수 있습니다.

## 기본 모델

후보 `i`의 값이 시간에 대한 일차식이라고 합시다.

```text
value_i(t) = a_i * t + b_i
```

현재 최댓값 후보는 위쪽 envelope입니다. 두 후보 `i`, `j`의 우열이 바뀌는 시간은 다음과 같습니다.

```text
a_i * t + b_i = a_j * t + b_j
t = (b_j - b_i) / (a_i - a_j)
```

이 식은 CHT의 교점과 비슷하지만, x query가 시간이 되고 후보 집합 자체가 event로 변할 수 있다는 점이 다릅니다.

## 작은 예시

```text
candidate A: 2t + 1
candidate B: 1t + 5
candidate C: 4t - 3

t = 0: B = 5가 최댓값
A와 B 교차: 2t+1 = t+5 -> t = 4
B와 C 교차: t+5 = 4t-3 -> t = 8/3
A와 C 교차: 2t+1 = 4t-3 -> t = 2
```

하지만 모든 교차가 envelope 변화가 아닙니다. `t=2`에서 C가 A를 이겨도, 그 시점의 최댓값은 아직 B일 수 있습니다. event를 만들 때는 "두 후보가 만난다"와 "답이 바뀐다"를 구분해야 합니다.

## 이벤트의 수명

교차 시각만 저장하면 후보가 바뀐 뒤 남아 있는 오래된 이벤트를 구별할 수 없습니다. 이벤트를 만들 때 양쪽 후보의 version을 함께 저장하고, 꺼낼 때 현재 version·이웃 관계·현재 시각과 비교합니다. 처리 뒤 바뀐 이웃의 이벤트를 다시 계산해야 합니다.

## Moving Point Hull

점 `p_i(t) = p_i0 + v_i * t`가 움직이면, 특정 방향 `d`에서 support 값은 일차식이 됩니다.

```text
dot(p_i(t), d)
= dot(p_i0, d) + t * dot(v_i, d)
```

따라서 "방향이 고정된 support point"는 line envelope 문제로 바뀝니다. 하지만 전체 convex hull의 vertex 순서를 유지하려면 adjacent edge orientation이 바뀌는 event를 추적해야 하므로 훨씬 어렵습니다.

## 적용 범위를 구분하기

고정 후보 value_i(t)=a_i*t+b_i의 최적값만 묻는다면 t를 query x로 보는 정적 CHT입니다. 질의 시각을 정렬할 수 있고 직선의 유효 기간까지 알려져 있다면 시간 구간 분해도 검토할 수 있습니다. 질의 시각을 안다는 사실만으로 일반 moving-point hull 문제가 정적 CHT로 바뀌지는 않습니다.

전체 2D hull 유지에는 hull 바깥 점이 경계에 진입하는 사건도 검출해야 합니다. 현재 hull의 이웃 세 점 orientation만 감시하면 이를 놓칩니다. 유지할 certificate의 완전성, 실패 시 재구성 방법, 총 사건 수 상한을 별도로 증명해야 하며 이 페이지는 범용 kinetic hull 구현을 제공하지 않습니다.

교차 시각은 유리수가 될 수 있습니다. 정수 교차곱으로 비교할 때도 중간값 범위를 확인합니다.
