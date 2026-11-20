// sqrt-decomposition 하네스: 제출 코드 바깥의 로컬 검사. 이 강의에는 표준 입력 연습이 없다.
static int sample() { return 0; }

static long long gValues[MAX_N];

static long long naiveSum(const std::vector<long long>& a, int l, int r) {
    long long sum = 0;
    for (int i = l; i <= r; ++i) sum += a[i];
    return sum;
}

static void garbage() {
    // 이전 TC가 남긴 값을 흉내 내려고 build 전에 전체를 쓰레기 값으로 채운다.
    for (int i = 0; i < MAX_N; ++i) { sqrtSum.a[i] = 99; sqrtLazy.a[i] = 77; }
    for (int i = 0; i < MAX_BLOCKS; ++i) { sqrtSum.blockSum[i] = 55; sqrtLazy.lazy[i] = 33; }
    sqrtSum.n = sqrtLazy.n = MAX_N;
    sqrtSum.B = sqrtLazy.B = 1;
}

static void randomCase(int n, int operations, long long magnitude) {
    garbage();
    auto value = [&]() {
        return (long long)(harnessRng() % (unsigned long long)(2 * magnitude + 1)) - magnitude;
    };
    std::vector<long long> a(n), b(n);
    for (int i = 0; i < n; ++i) a[i] = b[i] = gValues[i] = value();
    CHECK(sqrtSum.build(gValues, n));
    CHECK(sqrtLazy.build(gValues, n));
    // 블록 크기는 B * B >= n인 가장 작은 정수이고 블록 수는 상한 안에 든다.
    CHECK(sqrtSum.B * sqrtSum.B >= n && (sqrtSum.B == 1 || (sqrtSum.B - 1) * (sqrtSum.B - 1) < n));
    CHECK((n + sqrtSum.B - 1) / sqrtSum.B <= MAX_BLOCKS);
    for (int op = 0; op < operations && n > 0; ++op) {
        int l = rnd(n), r = rnd(n);
        if (l > r) std::swap(l, r);
        switch (rnd(4)) {
        case 0: {
            int idx = rnd(n);
            long long v = value();
            sqrtSum.update(idx, v);
            a[idx] = v;
            break;
        }
        case 1: {
            long long v = value();
            sqrtLazy.rangeAdd(l, r, v);
            for (int i = l; i <= r; ++i) b[i] += v;
            break;
        }
        case 2:
            CHECK(sqrtSum.query(l, r) == naiveSum(a, l, r));
            break;
        default:
            CHECK(sqrtLazy.get(l) == b[l] && sqrtLazy.get(r) == b[r]);
            break;
        }
    }
    for (int i = 0; i < n; ++i) {
        CHECK(sqrtSum.query(i, i) == a[i]);
        CHECK(sqrtLazy.get(i) == b[i]);
    }
    if (n > 0) CHECK(sqrtSum.query(0, n - 1) == naiveSum(a, 0, n - 1));
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 본문 예: a = [5, 2, 7, 1, 4, 6, 3, 8, 9, 2], B = 4, blockSum = [15, 21, 11], [2, 9]의 합은 40.
    long long fig[10] = {5, 2, 7, 1, 4, 6, 3, 8, 9, 2};
    CHECK(sqrtSum.build(fig, 10));
    CHECK(sqrtSum.B == 4);
    CHECK(sqrtSum.blockSum[0] == 15 && sqrtSum.blockSum[1] == 21 && sqrtSum.blockSum[2] == 11);
    CHECK(sqrtSum.query(2, 9) == 40);
    // lazy 그림: n = 8, B = 4. build는 B = 3을 고르므로 그림과 같은 블록 크기 4로 바꿔 확인한다.
    long long zeros[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    CHECK(sqrtLazy.build(zeros, 8));
    CHECK(sqrtLazy.B == 3);
    sqrtLazy.B = 4;
    sqrtLazy.rangeAdd(2, 7, 3);
    CHECK(sqrtLazy.a[2] == 3 && sqrtLazy.a[3] == 3 && sqrtLazy.a[4] == 0 && sqrtLazy.lazy[1] == 3);
    for (int i = 0; i < 8; ++i) CHECK(sqrtLazy.get(i) == (i >= 2 ? 3 : 0));
    CHECK(sqrtLazy.build(zeros, 8));
    sqrtLazy.rangeAdd(2, 7, 3);
    for (int i = 0; i < 8; ++i) CHECK(sqrtLazy.get(i) == (i >= 2 ? 3 : 0));
    // ceilSqrt 자체.
    for (int x = 0; x <= 5000; ++x) {
        int r = ceilSqrt(x);
        CHECK(r >= 1 && r * r >= x && (r == 1 || (r - 1) * (r - 1) < x));
    }
    CHECK(MAX_BLOCKS == 448);
    // 무작위 비교와 크기를 바꾸며 이어 실행하는 TC.
    for (int trial = 0; trial < 400; ++trial) randomCase(rnd(30), 100, 10);
    for (int n : {1000, 3, 0, 5, 1, 2, 17, 1}) randomCase(n, 3 * n + 10, 1000000000LL);
    // 용량 경계: n = MAX_N에서 마지막 블록과 큰 값, 블록 수 상한.
    CHECK(!sqrtSum.build(gValues, -1));
    CHECK(!sqrtSum.build(gValues, MAX_N + 1));
    CHECK(!sqrtLazy.build(gValues, MAX_N + 1));
    garbage();
    for (int i = 0; i < MAX_N; ++i) gValues[i] = 1000000000LL;
    CHECK(sqrtSum.build(gValues, MAX_N));
    CHECK(sqrtLazy.build(gValues, MAX_N));
    CHECK((MAX_N + sqrtSum.B - 1) / sqrtSum.B <= MAX_BLOCKS);
    CHECK(sqrtSum.query(0, MAX_N - 1) == 1000000000LL * MAX_N);
    sqrtSum.update(MAX_N - 1, -1000000000LL);
    CHECK(sqrtSum.query(MAX_N - 2, MAX_N - 1) == 0);
    sqrtLazy.rangeAdd(0, MAX_N - 1, 5);
    sqrtLazy.rangeAdd(MAX_N - 1, MAX_N - 1, 7);
    CHECK(sqrtLazy.get(0) == 1000000005LL && sqrtLazy.get(MAX_N - 1) == 1000000012LL);
    // 빈 입력.
    CHECK(sqrtSum.build(gValues, 0));
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
