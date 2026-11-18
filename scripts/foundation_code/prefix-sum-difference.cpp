// prefix-sum-difference 하네스: 제출 코드 바깥의 로컬 검사.
static long long gA[MAX_N], gResult[MAX_N], gPrefix[MAX_N + 1];
static RangeAdd gAdds[MAX_N];
static int gGrid[MAX_H][MAX_W];
static long long gPrefix2D[MAX_H + 1][MAX_W + 1], gResult2D[MAX_H][MAX_W];
static RectAdd gRects[1000];

// 로컬 연습: 반열린 구간 [l, r) 갱신을 모두 적용한 뒤 구간 합 질의.
static int sample() {
    int n, m, q;
    std::cin >> n >> m >> q;
    for (int i = 0; i < n; ++i) std::cin >> gA[i];
    int adds = 0;
    for (int i = 0; i < m; ++i) {
        int l, r;
        long long delta;
        std::cin >> l >> r >> delta;
        if (l < r) gAdds[adds++] = {l, r - 1, delta}; // 빈 구간은 건너뛴다
    }
    addRangesToArray(gA, n, gAdds, adds, gResult);
    buildPrefix(gResult, n, gPrefix);
    for (int i = 0; i < q; ++i) {
        int l, r;
        std::cin >> l >> r;
        std::printf("%lld\n", l < r ? rangeSum(gPrefix, l, r - 1) : 0LL);
    }
    return 0;
}

static void case1D(int n, int q, unsigned long long magnitude) {
    for (int i = 0; i <= MAX_N; ++i) diff[i] = 424242; // 이전 TC의 표시
    std::vector<long long> a(n), want(n);
    for (int i = 0; i < n; ++i) want[i] = gA[i] = a[i] = (long long)(harnessRng() % (2 * magnitude + 1)) - (long long)magnitude;
    int count = 0;
    for (int k = 0; k < q && n > 0; ++k) {
        int l = rnd(n), r = rnd(n);
        if (l > r) std::swap(l, r);
        long long value = (long long)rnd(21) - 10;
        gAdds[count++] = {l, r, value};
        for (int i = l; i <= r; ++i) want[i] += value;
    }
    for (int i = 0; i < n; ++i) gResult[i] = -999;
    addRangesToArray(gA, n, gAdds, count, gResult);
    for (int i = 0; i < n; ++i) CHECK(gResult[i] == want[i]);
    for (int i = 0; i <= n; ++i) gPrefix[i] = -5;
    buildPrefix(gResult, n, gPrefix);
    CHECK(gPrefix[0] == 0);
    for (int l = 0; l < n; ++l) {
        long long sum = 0;
        for (int r = l; r < n; ++r) {
            sum += want[r];
            CHECK(rangeSum(gPrefix, l, r) == sum);
        }
    }
}

static void case2D(int h, int w, int q) {
    std::vector<std::vector<long long>> want(h, std::vector<long long>(w));
    for (int y = 0; y < h; ++y) for (int x = 0; x < w; ++x) {
        gGrid[y][x] = rnd(21) - 10;
        want[y][x] = 0; // applyRectAdds는 더한 양만 만든다
    }
    for (int y = 0; y <= MAX_H; ++y) for (int x = 0; x <= MAX_W; ++x) {
        gPrefix2D[y][x] = 31337; // 0행·0열도 함수가 직접 0으로 만들어야 한다
        diff2D[y][x] = 777;
    }
    buildPrefix2D(gGrid, h, w, gPrefix2D);
    for (int y1 = 0; y1 < h; ++y1) for (int x1 = 0; x1 < w; ++x1)
        for (int y2 = y1; y2 < h; ++y2) for (int x2 = x1; x2 < w; ++x2) {
            long long sum = 0;
            for (int y = y1; y <= y2; ++y) for (int x = x1; x <= x2; ++x) sum += gGrid[y][x];
            CHECK(rectSum(gPrefix2D, y1, x1, y2, x2) == sum);
        }
    int count = 0;
    for (int k = 0; k < q && h > 0 && w > 0; ++k) {
        int y1 = rnd(h), y2 = rnd(h), x1 = rnd(w), x2 = rnd(w);
        if (y1 > y2) std::swap(y1, y2);
        if (x1 > x2) std::swap(x1, x2);
        long long value = (long long)rnd(21) - 10;
        gRects[count++] = {y1, x1, y2, x2, value};
        for (int y = y1; y <= y2; ++y) for (int x = x1; x <= x2; ++x) want[y][x] += value;
    }
    for (int y = 0; y < MAX_H; ++y) for (int x = 0; x < MAX_W; ++x) gResult2D[y][x] = -1;
    applyRectAdds(h, w, gRects, count, gResult2D);
    for (int y = 0; y < h; ++y) for (int x = 0; x < w; ++x) CHECK(gResult2D[y][x] == want[y][x]);
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 본문 예: 3 1 4 1 5의 누적합과 구간 [1, 3]의 합 6.
    {
        long long a[5] = {3, 1, 4, 1, 5}, prefix[6];
        buildPrefix(a, 5, prefix);
        long long expected[6] = {0, 3, 4, 8, 9, 14};
        for (int i = 0; i < 6; ++i) CHECK(prefix[i] == expected[i]);
        CHECK(rangeSum(prefix, 1, 3) == 6);
    }
    // 무작위 비교, 크기를 바꾸며 한 프로세스에서 이어 실행.
    for (int trial = 0; trial < 300; ++trial) case1D(rnd(14), rnd(20), 1000000000);
    for (int n : {2000, 3, 0, 5, 1}) case1D(n, 40, 1000000);
    for (int trial = 0; trial < 200; ++trial) case2D(rnd(7), rnd(7), rnd(8));
    for (int size : {20, 3, 0, 5, 1}) case2D(size, size, 30);
    case2D(0, 5, 3);
    case2D(5, 0, 3);
    // 용량 경계 1: n = MAX_N, 모든 구간 [0, n - 1]에 +10^6을 MAX_N번. r + 1 == n 표시(diff[MAX_N])를 쓴다.
    for (int i = 0; i < MAX_N; ++i) { gA[i] = 1000000; gAdds[i] = {0, MAX_N - 1, 1000000}; }
    addRangesToArray(gA, MAX_N, gAdds, MAX_N, gResult);
    for (int i = 0; i < MAX_N; ++i) CHECK(gResult[i] == 1000000LL + 1000000LL * MAX_N);
    buildPrefix(gResult, MAX_N, gPrefix);
    CHECK(rangeSum(gPrefix, 0, MAX_N - 1) == MAX_N * (1000000LL + 1000000LL * MAX_N));
    CHECK(rangeSum(gPrefix, MAX_N - 1, MAX_N - 1) == 1000000LL + 1000000LL * MAX_N);
    // 큰 TC 뒤에 n = 0과 n = 1: 이전 값이 남아 있어도 결과가 섞이지 않는다.
    addRangesToArray(gA, 0, gAdds, 0, gResult);
    gA[0] = 7;
    gAdds[0] = {0, 0, 5};
    addRangesToArray(gA, 1, gAdds, 1, gResult);
    CHECK(gResult[0] == 12);
    // 용량 경계 2: 500 x 500 전체 격자에 값 10^6, 전체 직사각형에 +10^6을 1000번.
    for (int y = 0; y < MAX_H; ++y) for (int x = 0; x < MAX_W; ++x) gGrid[y][x] = 1000000;
    buildPrefix2D(gGrid, MAX_H, MAX_W, gPrefix2D);
    CHECK(rectSum(gPrefix2D, 0, 0, MAX_H - 1, MAX_W - 1) == 1000000LL * MAX_H * MAX_W);
    CHECK(rectSum(gPrefix2D, MAX_H - 1, MAX_W - 1, MAX_H - 1, MAX_W - 1) == 1000000);
    for (int k = 0; k < 1000; ++k) gRects[k] = {0, 0, MAX_H - 1, MAX_W - 1, 1000000};
    applyRectAdds(MAX_H, MAX_W, gRects, 1000, gResult2D);
    for (int y = 0; y < MAX_H; ++y) for (int x = 0; x < MAX_W; ++x) CHECK(gResult2D[y][x] == 1000000000LL);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
