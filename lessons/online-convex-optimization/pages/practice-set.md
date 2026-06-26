# Practice Set

Online Convex Optimization 허브의 연습은 먼저 feedback 모델을 판독하고, 그다음 feasible set에 맞는 update를 고르는 순서로 진행합니다. 실제 h-contest 문제가 아직 부족한 주제는 임의 ID를 만들지 않고 `TODO`로 남깁니다.

## 1. 연습 순서

| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: online gradient descent `/practice/...` 문제 필요 | gradient step과 projection 구현 | regret |
| 표준 | TODO: multiplicative weights `/practice/...` 문제 필요 | simplex decision 갱신 | entropy |
| 응용 | TODO: dual averaging regret `/practice/...` 문제 필요 | 누적 gradient와 regularizer 해석 | cumulative gradient |
| 함정 | TODO: bandit vs full information `/practice/...` 문제 필요 | feedback 모델 구분 | exploration |

## 2. 로컬 완결형 연습 후보

### Expert Advice with Full Loss Vectors

`N`개의 expert와 `T`라운드가 있습니다. 각 라운드가 끝날 때 모든 expert의 loss가 공개됩니다. Multiplicative Weights로 확률분포를 갱신하고, 최종 cumulative expected loss와 가장 좋은 고정 expert의 loss 차이를 출력합니다.

이 문제는 OCO full-information 모델을 확인하기 위한 연습입니다. 선택한 expert의 loss만 주어지는 bandit 문제로 바꾸면 같은 구현을 그대로 쓸 수 없습니다.

### Projected Gradient on a Box

매 라운드 linear loss `a_t * x`가 공개되고, `x`는 항상 `[L, R]` 범위 안에 있어야 합니다. Online Gradient Descent와 clamp projection을 구현하고, 작은 입력에서 `x_t`가 어떻게 이동하는지 손으로 추적합니다.

## 3. 제출 전 체크리스트

- loss와 reward의 부호를 맞췄는가?
- full-information feedback인지 bandit feedback인지 표로 설명할 수 있는가?
- probability vector 합이 1인지 매 라운드 검증했는가?
- exponential update에서 max-shift를 했는가?
- learning rate가 입력 scale과 horizon에 맞는가?
