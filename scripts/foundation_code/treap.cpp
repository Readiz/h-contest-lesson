// treap 하네스: 제출 코드 바깥의 로컬 검사.
#include <set>

static bool contains(int root, int key) {
    int order = orderOfKey(root, key);
    return order < getSize(root) && kth(root, order) == key;
}

// 연습: Q 뒤 Q개 연산(I x / D x / R x / K k). 중복 삽입·없는 값 삭제는 무시한다.
static int sample() {
    int q;
    std::cin >> q;
    initTreap(12345u);
    int root = 0;
    for (int i = 0; i < q; ++i) {
        char op;
        long long x;
        std::cin >> op >> x;
        if (op == 'I') {
            if (!contains(root, (int)x)) {
                int node = newNode((int)x);
                CHECK(node != 0);
                root = insert(root, node);
            }
        } else if (op == 'D') {
            root = erase(root, (int)x);
        } else if (op == 'R') {
            std::printf("%d\n", orderOfKey(root, (int)x));
        } else {
            if (x >= getSize(root)) std::printf("INVALID\n");
            else std::printf("%d\n", kth(root, (int)x));
        }
    }
    return 0;
}

// 구조 검사: key 범위(BST), priority(힙), size, 깊이. 반환값은 부분 트리의 노드 수.
static int validate(int node, long long low, long long high, int depth, int& maxDepth) {
    if (node == 0) return 0;
    CHECK(node >= 1 && node <= poolSize);
    CHECK(low < pool[node].key && pool[node].key < high);
    if (depth > maxDepth) maxDepth = depth;
    int l = pool[node].left, r = pool[node].right;
    if (l) CHECK(pool[l].priority <= pool[node].priority);
    if (r) CHECK(pool[r].priority <= pool[node].priority);
    int count = 1 + validate(l, low, pool[node].key, depth + 1, maxDepth)
                  + validate(r, pool[node].key, high, depth + 1, maxDepth);
    CHECK(pool[node].size == count);
    return count;
}

static int checkTree(int root, const std::set<int>& oracle) {
    int maxDepth = 0;
    CHECK(validate(root, -2000000000000LL, 2000000000000LL, 1, maxDepth) == (int)oracle.size());
    CHECK(getSize(root) == (int)oracle.size());
    return maxDepth;
}

static void dirtyState() {
    // 이전 TC가 남긴 값을 흉내 내려고 init 전에 pool 전체를 쓰레기 값으로 채운다.
    for (int i = 0; i <= MAX_NODES; ++i) {
        pool[i].key = -5; pool[i].priority = 4000000000u; pool[i].size = 99;
        pool[i].left = 77; pool[i].right = 78;
    }
    poolSize = MAX_NODES;
}

static void randomCase(int operations, int keyRange, unsigned seed) {
    dirtyState();
    initTreap(seed);
    std::set<int> oracle;
    std::vector<int> sorted;
    int root = 0;
    int inserts = 0;
    for (int op = 0; op < operations; ++op) {
        int kind = rnd(8);
        int x = rnd(2 * keyRange + 1) - keyRange;
        if (kind < 3) {
            bool had = oracle.count(x) != 0;
            CHECK(contains(root, x) == had);
            if (!had) {
                int node = newNode(x);
                CHECK(node != 0);
                ++inserts;
                root = insert(root, node);
                oracle.insert(x);
            }
        } else if (kind < 5) {
            root = erase(root, x);
            oracle.erase(x);
        } else if (kind < 7) {
            CHECK(orderOfKey(root, x) == (int)std::distance(oracle.begin(), oracle.lower_bound(x)));
        } else {
            int k = rnd((int)oracle.size() + 2);
            if (k < (int)oracle.size()) {
                CHECK(kth(root, k) == *std::next(oracle.begin(), k));
            } else {
                CHECK(k >= getSize(root)); // 호출부가 INVALID로 처리하는 경우
            }
        }
        if (op % 17 == 0) checkTree(root, oracle);
    }
    checkTree(root, oracle);
    CHECK(poolSize == inserts);
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 빈 트리와 한 노드.
    initTreap(1u);
    int root = 0;
    CHECK(getSize(root) == 0 && orderOfKey(root, 5) == 0);
    root = erase(root, 5);
    CHECK(root == 0);
    int node = newNode(5);
    CHECK(node == 1 && pool[node].size == 1 && pool[node].left == 0 && pool[node].right == 0);
    root = insert(root, node);
    CHECK(kth(root, 0) == 5 && orderOfKey(root, 5) == 0 && orderOfKey(root, 6) == 1);
    root = erase(root, 5);
    CHECK(root == 0);
    // 무작위 비교(키 범위가 좁으면 중복 삽입·없는 값 삭제가 많다)와 크기를 바꿔 이어 실행하는 TC.
    for (int trial = 0; trial < 300; ++trial) randomCase(rnd(80), 1 + rnd(12), (unsigned)trial);
    for (int trial = 0; trial < 40; ++trial) randomCase(400, 1000000000, 100u + (unsigned)trial);
    for (int n : {3000, 0, 7, 1, 1500}) randomCase(n, 400, 7u);
    // 용량 경계: MAX_NODES개를 오름차순·내림차순·무작위로 넣으면 모두 들어가고, 한 개 더는 0이다.
    // 정렬된 입력에서도 priority 덕분에 깊이가 작다.
    for (int shape = 0; shape < 3; ++shape) {
        initTreap(20261119u + (unsigned)shape);
        root = 0;
        std::set<int> none;
        for (int i = 0; i < MAX_NODES; ++i) {
            int key = shape == 0 ? i : shape == 1 ? MAX_NODES - i : (int)(((long long)i * 7919) % 1000003);
            int made = newNode(key);
            CHECK(made == i + 1);
            root = insert(root, made);
        }
        CHECK(newNode(0) == 0 && poolSize == MAX_NODES);
        CHECK(getSize(root) == MAX_NODES);
        int maxDepth = 0;
        CHECK(validate(root, -1, 2000000000, 1, maxDepth) == MAX_NODES);
        CHECK(maxDepth < 80);
        // 앞쪽 절반을 지우면 크기와 k번째가 맞는다(shape 0, 1은 키가 연속).
        if (shape == 0) {
            for (int i = 0; i < MAX_NODES / 2; ++i) root = erase(root, i);
            CHECK(getSize(root) == MAX_NODES - MAX_NODES / 2);
            CHECK(kth(root, 0) == MAX_NODES / 2 && orderOfKey(root, MAX_NODES / 2) == 0);
        }
    }
    // init으로 pool을 되돌리면 다시 가득 채울 수 있다.
    initTreap(3u);
    CHECK(poolSize == 0 && newNode(9) == 1 && newNode(8) == 2);
    initTreap(3u);
    CHECK(poolSize == 0);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
