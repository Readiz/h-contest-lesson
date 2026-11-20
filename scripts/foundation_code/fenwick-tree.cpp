// fenwick-tree 하네스: 제출 코드 바깥의 로컬 검사.
static long long gValues[MAX_N];

// 로컬 연습: 점 덧셈 A i delta, 구간 합 S l r (1-indexed).
static int sample() {
    int n, q;
    std::cin >> n >> q;
    for (int i = 0; i < n; ++i) std::cin >> gValues[i];
    fenwick.build(gValues, n);
    for (int i = 0; i < q; ++i) {
        std::string op;
        long long x, y;
        std::cin >> op >> x >> y;
        if (op == "A") fenwick.add((int)x, y);
        else std::printf("%lld\n", fenwick.rangeSum((int)x, (int)y));
    }
    return 0;
}

// 독립 기준: 원본 배열을 직접 갱신하고 구간을 직접 더한다(1-indexed).
static long long naiveRange(const std::vector<long long>& a, int l, int r) {
    long long sum = 0;
    for (int i = l; i <= r; ++i) sum += a[i];
    return sum;
}

static void randomCase(int n, int operations, long long magnitude, bool nonNegative) {
    // 이전 TC가 남긴 값을 흉내 내려고 build 전에 전체를 쓰레기 값으로 채운다.
    for (int i = 0; i <= MAX_N; ++i) fenwick.tree[i] = 777777;
    fenwick.n = MAX_N;
    auto value = [&]() {
        long long v = (long long)(harnessRng() % (unsigned long long)(2 * magnitude + 1)) - magnitude;
        return nonNegative ? (v < 0 ? -v : v) : v;
    };
    std::vector<long long> a(n + 1, 0);
    for (int i = 0; i < n; ++i) { gValues[i] = value(); a[i + 1] = gValues[i]; }
    CHECK(fenwick.build(gValues, n));
    for (int op = 0; op < operations && n > 0; ++op) {
        int kind = rnd(4);
        if (kind == 0) {
            int idx = 1 + rnd(n);
            long long delta = value();
            fenwick.add(idx, delta);
            a[idx] += delta;
        } else if (kind == 1) {
            int idx = 1 + rnd(n);
            long long newValue = value();
            fenwick.setValue(idx, a[idx], newValue);
            a[idx] = newValue;
        } else if (kind == 2) {
            int l = 1 + rnd(n), r = 1 + rnd(n);
            if (l > r) std::swap(l, r);
            CHECK(fenwick.rangeSum(l, r) == naiveRange(a, l, r));
            CHECK(fenwick.prefixSum(r) == naiveRange(a, 1, r));
        } else if (nonNegative) {
            long long total = naiveRange(a, 1, n);
            long long target = (long long)(harnessRng() % (unsigned long long)(total + 3)) - 1;
            int want = n + 1;
            long long running = 0;
            if (target <= 0) want = 1;
            else for (int i = 1; i <= n; ++i) {
                running += a[i];
                if (running >= target) { want = i; break; }
            }
            CHECK(lowerBound(fenwick, target) == want);
        }
    }
    CHECK(fenwick.prefixSum(0) == 0);
    for (int i = 1; i <= n; ++i) CHECK(fenwick.rangeSum(i, i) == a[i]);
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 본문 예: 연습 예시와 같은 배열.
    long long base[5] = {1, 2, 3, 4, 5};
    CHECK(fenwick.build(base, 5));
    CHECK(fenwick.rangeSum(1, 5) == 15);
    fenwick.add(3, -5);
    CHECK(fenwick.rangeSum(2, 4) == 4);
    fenwick.add(1, 10);
    CHECK(fenwick.rangeSum(1, 1) == 11);
    // lowbit 표: tree[i]는 길이 lowbit(i) 구간의 합이고 prefixSum(13)은 13, 12, 8을 더한다.
    long long ones[16];
    for (int i = 0; i < 16; ++i) ones[i] = 1;
    CHECK(fenwick.build(ones, 16));
    CHECK(fenwick.tree[8] == 8 && fenwick.tree[6] == 2 && fenwick.tree[13] == 1 && fenwick.tree[12] == 4);
    CHECK(fenwick.prefixSum(13) == 13);
    // 무작위 비교와 크기를 바꾸며 이어 실행하는 TC.
    for (int trial = 0; trial < 400; ++trial) randomCase(rnd(20), 60, 10, trial % 2 == 0);
    for (int n : {1000, 3, 0, 5, 1, 2, 17, 1}) randomCase(n, 3 * n + 10, 1000000000LL, n % 2 == 1);
    // 용량 경계: n = MAX_N에서 첫 칸과 마지막 칸, 큰 값의 합.
    CHECK(!fenwick.init(-1));
    CHECK(!fenwick.init(MAX_N + 1));
    CHECK(fenwick.init(MAX_N));
    fenwick.add(1, 1000000000LL);
    fenwick.add(MAX_N, 1000000000LL);
    CHECK(fenwick.rangeSum(1, MAX_N) == 2000000000LL);
    CHECK(fenwick.rangeSum(MAX_N, MAX_N) == 1000000000LL);
    CHECK(fenwick.rangeSum(2, MAX_N - 1) == 0);
    CHECK(lowerBound(fenwick, 1000000001LL) == MAX_N);
    CHECK(lowerBound(fenwick, 2000000001LL) == MAX_N + 1);
    for (int i = 1; i <= MAX_N; ++i) fenwick.add(i, 1000000000LL);
    CHECK(fenwick.prefixSum(MAX_N) == 2000000000LL + 1000000000LL * MAX_N);
    // 빈 입력.
    CHECK(fenwick.init(0));
    CHECK(fenwick.prefixSum(0) == 0);
    CHECK(lowerBound(fenwick, 1) == 1);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
