// union-find 하네스: 제출 코드 바깥의 로컬 검사. 이 강의에는 표준 입력 연습이 없다.
static int sample() { return 0; }

// 독립 기준: 원소마다 집합 번호를 두고 합칠 때 전부 다시 칠한다.
struct Naive {
    std::vector<int> label;
    explicit Naive(int n) : label(n) { std::iota(label.begin(), label.end(), 0); }
    bool unite(int a, int b) {
        if (label[a] == label[b]) return false;
        int from = label[b], to = label[a];
        for (int& x : label) if (x == from) x = to;
        return true;
    }
    int size(int a) const { return (int)std::count(label.begin(), label.end(), label[a]); }
};

static int sizeFilled[MAX_N];

static void randomCase(int n, int operations) {
    // 이전 TC가 남긴 값을 흉내 내려고 init 전에 전체를 쓰레기 값으로 채운다.
    for (int i = 0; i < MAX_N; ++i) { dsu.parent[i] = -7; dsu.size[i] = 99; }
    CHECK(dsu.init(n));
    Naive naive(n);
    int components = n;
    for (int op = 0; op < operations && n > 0; ++op) {
        int a = rnd(n), b = rnd(n);
        bool merged = dsu.unite(a, b);
        CHECK(merged == naive.unite(a, b));
        if (merged) --components;
        int c = rnd(n), d = rnd(n);
        CHECK(dsu.same(c, d) == (naive.label[c] == naive.label[d]));
        CHECK(dsu.componentSize(c) == naive.size(c));
    }
    // 대표별 크기의 합은 n이고 집합 수는 합쳐진 횟수만큼 줄어든다.
    int roots = 0, total = 0;
    for (int i = 0; i < n; ++i) if (dsu.find(i) == i) { ++roots; total += dsu.size[i]; }
    CHECK(roots == components && total == n);
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 본문 예: n = 4에서 (0,1), (1,2), (0,2)를 합치면 마지막은 false이고 집합은 2개.
    CHECK(dsu.init(4));
    CHECK(dsu.unite(0, 1) && dsu.unite(1, 2) && !dsu.unite(0, 2));
    CHECK(dsu.componentSize(2) == 3 && dsu.componentSize(3) == 1 && !dsu.same(2, 3));
    CHECK(!dsu.unite(3, 3));
    // 무작위 비교와 크기를 바꾸며 이어 실행하는 TC.
    for (int trial = 0; trial < 400; ++trial) randomCase(rnd(12), rnd(40));
    for (int n : {1000, 3, 0, 5, 1}) randomCase(n, 3 * n);
    CHECK(!dsu.init(-1));
    CHECK(!dsu.init(MAX_N + 1));
    // 모임 처리: 빈 모임, 한 명, 중복 이름 포함.
    CHECK(dsu.init(6));
    int none[1] = {0}, one[1] = {4}, meeting[5] = {2, 5, 2, 3, 5};
    uniteMeeting(none, 0);
    uniteMeeting(one, 1);
    uniteMeeting(meeting, 5);
    CHECK(dsu.componentSize(2) == 3 && dsu.same(2, 3) && dsu.same(3, 5) && !dsu.same(2, 4));
    CHECK(dsu.componentSize(0) == 1 && dsu.componentSize(4) == 1 && dsu.componentSize(1) == 1);
    // 용량 경계: 원소 MAX_N개를 사슬·역사슬·별 모양으로 합쳐도 한 집합이 되고 재귀 깊이가 작다.
    for (int shape = 0; shape < 3; ++shape) {
        CHECK(dsu.init(MAX_N));
        for (int i = 0; i + 1 < MAX_N; ++i) {
            int a = shape == 0 ? i : shape == 1 ? MAX_N - 2 - i : 0;
            int b = shape == 0 ? i + 1 : shape == 1 ? MAX_N - 1 - i : i + 1;
            CHECK(dsu.unite(a, b));
        }
        CHECK(dsu.componentSize(MAX_N - 1) == MAX_N && dsu.same(0, MAX_N - 1));
        for (int i = 0; i < MAX_N; ++i) sizeFilled[i] = dsu.find(i);
        for (int i = 0; i < MAX_N; ++i) CHECK(sizeFilled[i] == sizeFilled[0]);
        CHECK(!dsu.unite(0, MAX_N - 1));
    }
    CHECK(dsu.init(0));
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
