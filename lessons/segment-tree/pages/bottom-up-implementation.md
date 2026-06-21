# Segment Tree: Bottom-up 구현

## 6. Bottom-up 반복 구현

Segment Tree는 재귀 없이 bottom-up으로도 구현할 수 있습니다. 이 방식은 leaf를 배열 뒤쪽에 놓고, 부모를 앞쪽에 채웁니다.

```text
tree[n + i] = a[i]
tree[i] = tree[i * 2] + tree[i * 2 + 1]
```

구현이 짧고 재귀 호출 비용이 없어 실전에서 자주 씁니다.

```cpp
#include <vector>
using namespace std;

struct IterSegmentTree {
    int n;
    vector<long long> tree;

    IterSegmentTree(const vector<long long>& values) {
        n = (int)values.size();
        tree.assign(2 * n, 0);

        for (int i = 0; i < n; ++i) {
            tree[n + i] = values[i];
        }
        for (int i = n - 1; i >= 1; --i) {
            tree[i] = tree[i * 2] + tree[i * 2 + 1];
        }
    }

    void update(int idx, long long newValue) {
        int pos = idx + n;
        tree[pos] = newValue;

        while (pos > 1) {
            pos /= 2;
            tree[pos] = tree[pos * 2] + tree[pos * 2 + 1];
        }
    }

    long long query(int left, int right) {
        long long result = 0;
        left += n;
        right += n;

        while (left <= right) {
            if (left % 2 == 1) {
                result += tree[left];
                left++;
            }
            if (right % 2 == 0) {
                result += tree[right];
                right--;
            }
            left /= 2;
            right /= 2;
        }
        return result;
    }
};
```

이 구현의 `query(left, right)`는 양 끝을 안쪽으로 좁혀 가며, 현재 구간을 정확히 덮는 노드만 더합니다. `left`가 오른쪽 자식이면 그 노드는 바로 답에 넣고 다음 구간으로 넘어갑니다. `right`가 왼쪽 자식일 때도 같은 방식입니다.

bottom-up 구현은 점 업데이트와 구간 질의까지는 깔끔합니다. 하지만 lazy propagation이 필요한 구간 업데이트는 top-down 재귀 구현이 더 이해하기 쉽습니다.
