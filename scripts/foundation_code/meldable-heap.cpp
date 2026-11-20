// meldable-heap 하네스: 제출 코드 바깥의 로컬 검사.
static ComponentHeapDSU heapDsu; // 강의 본문이 "전역으로 선언"하라고 한 객체

// 연습: N Q, N개 값, Q개 연산(M a b / P v). P는 최솟값을 출력하고 제거, 비면 EMPTY.
static int sample() {
    int n, q;
    std::cin >> n >> q;
    CHECK(heapDsu.init(n));
    for (int i = 0; i < n; ++i) {
        int value;
        std::cin >> value;
        CHECK(heapDsu.push(i, value));
    }
    for (int i = 0; i < q; ++i) {
        char op;
        std::cin >> op;
        if (op == 'M') {
            int a, b;
            std::cin >> a >> b;
            heapDsu.unite(a, b);
        } else {
            int v;
            std::cin >> v;
            if (heapDsu.empty(v)) std::printf("EMPTY\n");
            else { std::printf("%d\n", heapDsu.top(v)); heapDsu.pop(v); }
        }
    }
    return 0;
}

// 독립 기준: 원소마다 집합 번호를 두고 합칠 때 값 목록을 합친다. 최솟값은 매번 선형 탐색한다.
struct Naive {
    std::vector<int> label;
    std::vector<std::vector<int>> bag;
    explicit Naive(int n) : label(n), bag(n) { std::iota(label.begin(), label.end(), 0); }
    void push(int x, int key) { bag[label[x]].push_back(key); }
    void unite(int a, int b) {
        int from = label[b], to = label[a];
        if (from == to) return;
        for (int& x : label) if (x == from) x = to;
        bag[to].insert(bag[to].end(), bag[from].begin(), bag[from].end());
        bag[from].clear();
    }
    bool empty(int x) const { return bag[label[x]].empty(); }
    int popMin(int x) {
        std::vector<int>& b = bag[label[x]];
        auto it = std::min_element(b.begin(), b.end());
        int value = *it;
        b.erase(it);
        return value;
    }
};

static void dirtyState() {
    // 이전 TC가 남긴 값을 흉내 내려고 init 전에 전체를 쓰레기 값으로 채운다.
    for (int i = 0; i < MAX_N; ++i) { heapDsu.parent[i] = -7; heapDsu.size[i] = 99; heapDsu.heap[i] = 12345; }
    for (int i = 0; i <= MAX_NODES; ++i) { heapDsu.pool[i].key = -5; heapDsu.pool[i].left = 77; heapDsu.pool[i].right = 78; }
    heapDsu.poolSize = MAX_NODES;
}

static void randomCase(int n, int operations, int keyRange) {
    dirtyState();
    CHECK(heapDsu.init(n));
    Naive naive(n);
    if (n == 0) return;
    for (int i = 0; i < n; ++i) {
        int key = rnd(2 * keyRange + 1) - keyRange;
        CHECK(heapDsu.push(i, key));
        naive.push(i, key);
    }
    for (int op = 0; op < operations; ++op) {
        int kind = rnd(10);
        if (kind < 3) {
            int a = rnd(n), b = rnd(n);
            heapDsu.unite(a, b);
            naive.unite(a, b);
        } else if (kind < 4) {
            int a = rnd(n), key = rnd(2 * keyRange + 1) - keyRange;
            CHECK(heapDsu.push(a, key));
            naive.push(a, key);
        } else {
            int v = rnd(n);
            CHECK(heapDsu.empty(v) == naive.empty(v));
            if (!naive.empty(v)) {
                int expected = naive.popMin(v);
                CHECK(heapDsu.top(v) == expected);
                heapDsu.pop(v);
            }
        }
    }
    // 남은 값을 모두 꺼내 기준과 같은 순서인지 확인한다.
    for (int v = 0; v < n; ++v) {
        while (!naive.empty(v)) {
            CHECK(!heapDsu.empty(v));
            int expected = naive.popMin(v);
            CHECK(heapDsu.top(v) == expected);
            heapDsu.pop(v);
        }
        CHECK(heapDsu.empty(v));
    }
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 본문 예: 그룹 0에 7과 2, 그룹 1에 5를 넣고 합치면 어느 번호로 조회해도 최솟값은 2, 다음은 5.
    CHECK(heapDsu.init(2));
    CHECK(heapDsu.push(0, 7) && heapDsu.push(0, 2) && heapDsu.push(1, 5));
    heapDsu.unite(0, 1);
    heapDsu.unite(1, 0); // 이미 같은 컴포넌트: 힙을 다시 합치지 않는다
    CHECK(!heapDsu.empty(1) && heapDsu.top(1) == 2);
    heapDsu.pop(0);
    CHECK(heapDsu.top(1) == 5);
    heapDsu.pop(0);
    CHECK(heapDsu.top(0) == 7);
    heapDsu.pop(1);
    CHECK(heapDsu.empty(0) && heapDsu.empty(1));
    // 무작위 비교(중복 값 많음/적음)와 크기를 바꿔 이어 실행하는 TC.
    for (int trial = 0; trial < 500; ++trial) randomCase(rnd(10), rnd(60), 1 + rnd(5));
    for (int trial = 0; trial < 100; ++trial) randomCase(1 + rnd(40), 200, 1000000000);
    for (int n : {800, 3, 0, 5, 1, 300}) randomCase(n, 4 * n, 50);
    CHECK(!heapDsu.init(-1));
    CHECK(!heapDsu.init(MAX_N + 1));
    // 용량 경계: 한 정점에 MAX_NODES개를 오름차순·내림차순·무작위로 넣으면 정렬된 순서로 나오고,
    // 한 개 더 넣으면 false이며 힙은 그대로다.
    for (int shape = 0; shape < 3; ++shape) {
        CHECK(heapDsu.init(1));
        std::vector<int> keys(MAX_NODES);
        for (int i = 0; i < MAX_NODES; ++i)
            keys[i] = shape == 0 ? i - 100000 : shape == 1 ? 100000 - i : rnd(2000000001) - 1000000000;
        for (int key : keys) CHECK(heapDsu.push(0, key));
        CHECK(!heapDsu.push(0, 0));
        std::sort(keys.begin(), keys.end());
        for (int key : keys) { CHECK(!heapDsu.empty(0) && heapDsu.top(0) == key); heapDsu.pop(0); }
        CHECK(heapDsu.empty(0));
        // 다음 TC: init만으로 pool이 비워져 다시 쓸 수 있다.
        CHECK(heapDsu.init(1) && heapDsu.push(0, 1) && heapDsu.top(0) == 1);
    }
    // 정점 MAX_N개, 값 MAX_NODES개를 대표 하나로 합친 뒤 정렬 순서로 제거한다.
    CHECK(heapDsu.init(MAX_N));
    std::vector<int> all(MAX_N);
    for (int i = 0; i < MAX_N; ++i) { all[i] = rnd(2000001) - 1000000; CHECK(heapDsu.push(i, all[i])); }
    for (int i = 0; i + 1 < MAX_N; ++i) heapDsu.unite(i, i + 1);
    std::sort(all.begin(), all.end());
    for (int key : all) { CHECK(heapDsu.top(MAX_N - 1) == key); heapDsu.pop(5); }
    CHECK(heapDsu.empty(0));
    CHECK(heapDsu.init(0));
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
