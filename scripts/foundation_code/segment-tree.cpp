// segment-tree 하네스: 제출 코드 바깥의 로컬 검사. 이 강의에는 표준 입력 연습이 없다.
static int sample() { return 0; }

static long long gValues[MAX_N];

static long long naiveSum(const std::vector<long long>& a, int l, int r) {
    long long sum = 0;
    for (int i = l; i <= r; ++i) sum += a[i];
    return sum;
}

static void garbage() {
    // 이전 TC가 남긴 값을 흉내 내려고 build 전에 전체를 쓰레기 값으로 채운다.
    for (int i = 0; i < 4 * MAX_N; ++i) {
        segmentTree.tree[i] = 555555;
        lazyTree.tree[i] = 444444;
        lazyTree.lazy[i] = 333333;
    }
    segmentTree.n = lazyTree.n = MAX_N;
}

static void randomCase(int n, int operations, long long magnitude) {
    garbage();
    auto value = [&]() {
        return (long long)(harnessRng() % (unsigned long long)(2 * magnitude + 1)) - magnitude;
    };
    std::vector<long long> a(n), b(n);
    for (int i = 0; i < n; ++i) a[i] = b[i] = gValues[i] = value();
    CHECK(segmentTree.build(gValues, n));
    CHECK(lazyTree.build(gValues, n));
    for (int op = 0; op < operations; ++op) {
        int l = rnd(n), r = rnd(n);
        if (l > r) std::swap(l, r);
        switch (rnd(4)) {
        case 0: {
            int idx = rnd(n);
            long long v = value();
            segmentTree.update(idx, v);
            a[idx] = v;
            break;
        }
        case 1: {
            long long v = value();
            lazyTree.rangeAdd(l, r, v);
            for (int i = l; i <= r; ++i) b[i] += v;
            break;
        }
        case 2:
            CHECK(segmentTree.query(l, r) == naiveSum(a, l, r));
            break;
        default:
            CHECK(lazyTree.query(l, r) == naiveSum(b, l, r));
            break;
        }
    }
    for (int i = 0; i < n; ++i) {
        CHECK(segmentTree.query(i, i) == a[i]);
        CHECK(lazyTree.query(i, i) == b[i]);
    }
    CHECK(segmentTree.query(0, n - 1) == naiveSum(a, 0, n - 1));
    CHECK(lazyTree.query(0, n - 1) == naiveSum(b, 0, n - 1));
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 본문 그림: 배열 1..8에서 구간 [2, 5]의 합은 18.
    long long fig[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    CHECK(segmentTree.build(fig, 8));
    CHECK(segmentTree.query(2, 5) == 18);
    segmentTree.update(0, 10);
    CHECK(segmentTree.query(0, 7) == 45);
    // lazy 그림: 배열 1, 2, 3, 4의 전체에 3을 더하면 합이 22.
    long long lz[4] = {1, 2, 3, 4};
    CHECK(lazyTree.build(lz, 4));
    lazyTree.rangeAdd(0, 3, 3);
    CHECK(lazyTree.query(0, 3) == 22 && lazyTree.query(0, 1) == 9);
    // 무작위 비교와 크기를 바꾸며 이어 실행하는 TC.
    for (int trial = 0; trial < 400; ++trial) randomCase(1 + rnd(20), 80, 10);
    for (int n : {1000, 3, 1, 5, 1, 2, 17, 1}) randomCase(n, 3 * n + 10, 1000000000LL);
    // 용량 경계: n = MAX_N, 마지막 칸과 큰 값, 전체 구간 lazy 뒤 일부 질의.
    CHECK(!segmentTree.build(gValues, 0));
    CHECK(!segmentTree.build(gValues, MAX_N + 1));
    CHECK(!lazyTree.build(gValues, 0));
    CHECK(!lazyTree.build(gValues, MAX_N + 1));
    garbage();
    for (int i = 0; i < MAX_N; ++i) gValues[i] = 1000000000LL;
    CHECK(segmentTree.build(gValues, MAX_N));
    CHECK(lazyTree.build(gValues, MAX_N));
    CHECK(segmentTree.query(0, MAX_N - 1) == 1000000000LL * MAX_N);
    segmentTree.update(MAX_N - 1, -1000000000LL);
    CHECK(segmentTree.query(MAX_N - 2, MAX_N - 1) == 0);
    lazyTree.rangeAdd(0, MAX_N - 1, 1000000000LL);
    CHECK(lazyTree.query(0, MAX_N - 1) == 2000000000LL * MAX_N);
    CHECK(lazyTree.query(MAX_N - 1, MAX_N - 1) == 2000000000LL);
    lazyTree.rangeAdd(MAX_N - 1, MAX_N - 1, -2000000000LL);
    CHECK(lazyTree.query(MAX_N - 2, MAX_N - 1) == 2000000000LL);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
