# Monte Carlo Tree Search

Monte Carlo Tree Search(MCTS)는 게임 트리를 모두 탐색하기 어려울 때, 유망한 수를 통계적으로 더 많이 시도하면서 선택을 개선하는 탐색 방법입니다. Minimax는 terminal까지 탐색하면 정확하지만 깊이 제한 평가를 쓰면 근사입니다. MCTS는 simulation 결과를 누적해 선택을 근사합니다.


아래 통계는 각 노드로 들어오는 수를 둔 플레이어의 승리 확률입니다. 따라서 부모는 자식의 평균 보상을 최대화합니다. backpropagate에 전달하는 값도 이 관점이며, 두 플레이어가 번갈아 한 수씩 두고 보상이 [0,1]인 게임에 한해 1-result로 전환합니다. 연속 턴·chance node·일반 점수형에는 별도 변환이 필요합니다.

## 언제 MCTS인가

| 문제 신호 | 접근 |
| --- | --- |
| 가능한 수가 많고 깊이가 깊다 | MCTS 후보 |
| 정확 evaluation function이 어렵다 | rollout으로 근사 |
| 시간 제한 안에서 점진적으로 개선해야 한다 | anytime algorithm |
| deterministic perfect information game | 기본 UCT 적용 가능 |
| 확률적 전이나 숨은 정보가 있다 | 별도 모델링 필요 |

MCTS는 "항상 정답"을 주는 알고리즘이 아닙니다. 제한 시간 안에서 좋은 수를 고르는 휴리스틱 탐색입니다.

## 네 단계

MCTS 한 iteration은 보통 아래 네 단계입니다.

| 단계 | 설명 |
| --- | --- |
| Selection | root에서 시작해 UCB가 큰 child를 따라 내려간다 |
| Expansion | 아직 시도하지 않은 move를 새 child로 추가한다 |
| Simulation | leaf에서 rollout policy로 게임을 끝까지 진행한다 |
| Backpropagation | 결과를 지나온 node들의 visit/reward에 반영한다 |

이 과정을 시간 제한까지 반복하고, root의 child 중 visit 수가 가장 큰 수를 선택하는 방식이 흔합니다.

## UCB Score

UCT에서 child 선택에 자주 쓰는 식은 아래입니다.

```text
score = wins / visits + C * sqrt(log(parentVisits) / visits)
```

첫 항은 exploitation입니다. 지금까지 잘 나온 수를 선호합니다. 두 번째 항은 exploration입니다. 방문 수가 적은 수를 더 시험하게 합니다.

## 기본 Node와 UCB

아래 코드는 tree node 통계와 UCB 기반 child 선택의 최소 골격입니다.

```cpp compile-check
#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>
using namespace std;

struct MctsNode {
    int parent = -1;
    vector<int> children;
    int visits = 0;
    double reward = 0.0;
    // 실제 탐색기는 미시도 행동을 별도로 관리한다.
};

double ucbScore(const MctsNode& parent, const MctsNode& child, double exploration) {
    if (child.visits == 0) {
        return numeric_limits<double>::infinity();
    }

    double exploit = child.reward / child.visits;
    double explore = exploration * sqrt(log((double)parent.visits + 1.0) / child.visits);
    return exploit + explore;
}

int selectChild(const vector<MctsNode>& tree, int nodeIndex, double exploration) {
    const MctsNode& node = tree[nodeIndex];
    if (node.children.empty()) return -1;
    return *max_element(
        node.children.begin(),
        node.children.end(),
        [&](int lhs, int rhs) {
            return ucbScore(node, tree[lhs], exploration) < ucbScore(node, tree[rhs], exploration);
        }
    );
}

void backpropagate(vector<MctsNode>& tree, int nodeIndex, double resultForPlayerJustMoved) {
    double result = resultForPlayerJustMoved;
    while (nodeIndex != -1) {
        tree[nodeIndex].visits += 1;
        tree[nodeIndex].reward += result;
        result = 1.0 - result;
        nodeIndex = tree[nodeIndex].parent;
    }
}
```

`result = 1.0 - result`는 두 플레이어 zero-sum 게임에서 관점이 번갈아 바뀐다는 뜻입니다. 점수형 게임이면 reward 변환을 문제에 맞게 바꿉니다.

## Selection과 Expansion

selection은 이미 확장된 child 중 UCB가 큰 쪽으로 내려갑니다. 아직 확장하지 않은 move가 있으면 expansion에서 하나를 추가합니다.

```text
node = root
while node is fully expanded and not terminal:
    node = best UCB child
if node is not terminal:
    node = expand one untried move
```

실전 구현에서는 node마다 `untriedMoves`를 저장하거나, 상태에서 가능한 move를 생성한 뒤 이미 확장한 move를 제외합니다.

## Rollout Policy

rollout은 leaf에서 게임이 끝날 때까지 빠르게 수를 선택하는 과정입니다.

| policy | 특징 |
| --- | --- |
| random rollout | 구현 쉽지만 노이즈 큼 |
| heuristic rollout | 더 안정적이지만 bias 가능 |
| shallow evaluation | 끝까지 진행하지 않고 평가 함수 사용 |
| rule-based rollout | 도메인 지식 반영 |

rollout이 너무 느리면 iteration 수가 줄고, 너무 무작위면 통계가 느리게 수렴합니다.

## 최종 수 선택

시간이 끝나면 root의 child 중 하나를 고릅니다.

| 기준 | 의미 |
| --- | --- |
| 가장 많이 방문한 child | 통계적으로 가장 검증된 수 |
| 평균 reward가 가장 큰 child | 가장 좋아 보이는 수 |
| robust child | visit 우선, tie는 reward |

대부분의 게임 AI에서는 visit 수 기준이 안정적입니다. 탐색 중에는 UCB를 쓰지만 최종 선택에는 exploration 항을 빼는 것이 보통입니다.

## Minimax와 비교

| 기준 | Minimax/Alpha-Beta | MCTS |
| --- | --- | --- |
| 결과 성격 | 완전 탐색 범위에서는 exact | 근사/통계 |
| evaluation | 중요 | rollout으로 대체 가능 |
| branching factor | 크면 부담 | 큰 branching에도 점진적 |
| 시간 제한 | depth로 조절 | iteration/time으로 조절 |
| 랜덤성 | 보통 없음 | 있음 |

규칙이 작고 승패 판정이 빠르면 minimax가 더 명확합니다. 가능한 수가 많고 좋은 평가 함수를 만들기 어렵다면 MCTS가 실용적입니다.

## 시간 복잡도

MCTS는 iteration 수를 직접 제한합니다.

```text
O(iterations * (selection depth * 최대 자식 수 + rollout length))
각 rollout의 상태 전이와 보상 계산 비용은 별도로 곱한다.
```

메모리는 확장한 node 수에 비례합니다. 제한 시간형 문제에서는 iteration을 `while time remains`로 돌리지만, 온라인 저지에서는 시간 측정이 불안정할 수 있어 고정 iteration을 쓰기도 합니다.
