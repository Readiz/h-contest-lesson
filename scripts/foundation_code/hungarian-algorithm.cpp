// hungarian-algorithm 하네스: 제출 코드 바깥의 로컬 검사. 이 강의에는 표준 입력 연습이 없다.
static int sample() { return 0; }

static long long gCost[HUNGARIAN_MAX_N][HUNGARIAN_MAX_M];
static int gAssign[HUNGARIAN_MAX_N];

// 독립 기준: 열 집합을 상태로 보는 비트마스크 DP (n <= m <= 14).
static long long oracle(int n, int m) {
    const long long NONE = 4000000000000000000LL;
    std::vector<long long> best(1 << m, NONE);
    best[0] = 0;
    for (int mask = 0; mask < (1 << m); ++mask) {
        int row = __builtin_popcount(mask);
        if (best[mask] == NONE || row >= n) continue;
        for (int j = 0; j < m; ++j) {
            if (mask >> j & 1) continue;
            best[mask | 1 << j] = std::min(best[mask | 1 << j], best[mask] + gCost[row][j]);
        }
    }
    long long answer = NONE;
    for (int mask = 0; mask < (1 << m); ++mask)
        if (__builtin_popcount(mask) == n) answer = std::min(answer, best[mask]);
    return answer;
}

static void scribble() { // 이전 호출이 남긴 값을 흉내 낸다.
    for (int i = 0; i <= HUNGARIAN_MAX_N; ++i) h_u[i] = 123456789;
    for (int j = 0; j <= HUNGARIAN_MAX_M; ++j) { h_v[j] = -987654321; h_p[j] = 5; h_way[j] = 7; h_used[j] = 1; h_minv[j] = 3; }
    for (int i = 0; i < HUNGARIAN_MAX_N; ++i) gAssign[i] = -50;
}

static void checkAssignment(int n, int m, long long total) {
    std::vector<int> used(m, 0);
    long long sum = 0;
    for (int i = 0; i < n; ++i) {
        CHECK(gAssign[i] >= 0 && gAssign[i] < m);
        CHECK(!used[gAssign[i]]);
        used[gAssign[i]] = 1;
        sum += gCost[i][gAssign[i]];
    }
    CHECK(sum == total);
}

static void fill(int n, int m, long long low, long long high) {
    unsigned long long span = (unsigned long long)(high - low + 1);
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < m; ++j) gCost[i][j] = low + (long long)(harnessRng() % span);
}

static void smallCase(int n, int m, long long low, long long high) {
    fill(n, m, low, high);
    scribble();
    long long got = hungarian_min_cost(n, m, gCost, gAssign);
    CHECK(got == oracle(n, m));
    checkAssignment(n, m, got);
}

// 정사각형: 듀얼 해(h_u, h_v)가 가능해이고 배정한 간선이 tight이면 합이 최적이라는 증명이다.
static void certificateCase(int n, long long low, long long high) {
    fill(n, n, low, high);
    scribble();
    long long got = hungarian_min_cost(n, n, gCost, gAssign);
    checkAssignment(n, n, got);
    long long dual = 0;
    for (int i = 1; i <= n; ++i) dual += h_u[i];
    for (int j = 1; j <= n; ++j) dual += h_v[j];
    CHECK(dual == got);
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) CHECK(gCost[i][j] - h_u[i + 1] - h_v[j + 1] >= 0);
        CHECK(gCost[i][gAssign[i]] - h_u[i + 1] - h_v[gAssign[i] + 1] == 0);
    }
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();

    // 본문 예: 그리디는 5, 최적은 A-Y, B-X, C-Z로 4.
    {
        const long long greedy[3][3] = {{1, 2, 100}, {1, 100, 2}, {100, 2, 1}};
        for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) gCost[i][j] = greedy[i][j];
        CHECK(hungarian_min_cost(3, 3, gCost, gAssign) == 4);
        CHECK(gAssign[0] == 1 && gAssign[1] == 0 && gAssign[2] == 2);
    }
    // 본문 손계산 표: 총 비용 5.
    {
        const long long hand[3][3] = {{4, 1, 3}, {2, 0, 5}, {3, 2, 2}};
        for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j) gCost[i][j] = hand[i][j];
        CHECK(hungarian_min_cost(3, 3, gCost, gAssign) == 5);
        CHECK(gAssign[0] == 1 && gAssign[1] == 0 && gAssign[2] == 2);
    }
    // 본문 COUPANG2 예: P7 고객 A, B와 copy 두 개. 최적은 A-copy1, B-copy0으로 30 + 35 = 65.
    {
        const long long p7[2][2] = {{42, 30}, {35, 70}};
        for (int i = 0; i < 2; ++i) for (int j = 0; j < 2; ++j) gCost[i][j] = p7[i][j];
        CHECK(hungarian_min_cost(2, 2, gCost, gAssign) == 65 && gAssign[0] == 1 && gAssign[1] == 0);
    }
    // 빈 입력과 계약 위반: n > m, 상한 초과, 음수 크기.
    CHECK(hungarian_min_cost(0, 0, gCost, gAssign) == 0);
    CHECK(hungarian_min_cost(0, 5, gCost, gAssign) == 0);
    CHECK(hungarian_min_cost(3, 2, gCost, gAssign) == HUNGARIAN_INF);
    CHECK(hungarian_min_cost(HUNGARIAN_MAX_N + 1, HUNGARIAN_MAX_M, gCost, gAssign) == HUNGARIAN_INF);
    CHECK(hungarian_min_cost(1, HUNGARIAN_MAX_M + 1, gCost, gAssign) == HUNGARIAN_INF);
    CHECK(hungarian_min_cost(-1, 3, gCost, gAssign) == HUNGARIAN_INF);
    CHECK(hungarian_min_cost(2, -1, gCost, gAssign) == HUNGARIAN_INF);

    // 작은 입력을 전수 기준과 비교: 정사각·직사각, 같은 값이 많은 비용, 음수 비용(이익 최대화), 큰 비용.
    // 크기가 다른 케이스를 한 프로세스에서 이어서 실행한다.
    for (int trial = 0; trial < 600; ++trial) {
        int n = 1 + rnd(7), m = n + rnd(5);
        smallCase(n, m, 0, 1 + rnd(6));
    }
    for (int trial = 0; trial < 300; ++trial) {
        int n = 1 + rnd(8), m = n + rnd(4);
        smallCase(n, m, -1000, 1000);
    }
    for (int trial = 0; trial < 100; ++trial) {
        int n = 1 + rnd(6), m = n + rnd(3);
        smallCase(n, m, -1000000000000LL, 1000000000000LL);
    }
    for (int shape : {12, 1, 9, 2, 12, 5}) smallCase(shape <= 9 ? shape : 10, shape, 0, 50);
    // 모든 비용이 같으면 어떤 배정도 최적이다(총 비용과 열 중복만 확인).
    for (int i = 0; i < 6; ++i) for (int j = 0; j < 8; ++j) gCost[i][j] = 7;
    scribble();
    CHECK(hungarian_min_cost(6, 8, gCost, gAssign) == 42);
    checkAssignment(6, 8, 42);

    // 중간 크기: 오라클이 없으므로 듀얼 증명으로 확인한다.
    for (int n : {60, 5, 200, 1, 40}) certificateCase(n, 0, 1000);
    certificateCase(150, -1000000000000LL, 1000000000000LL);
    certificateCase(100, 0, 3);

    // 용량 경계 1: n = m = 1000, 한 줄만 싸게 심은 행렬(답은 심은 값의 합).
    {
        std::vector<int> perm(HUNGARIAN_MAX_N);
        for (int i = 0; i < HUNGARIAN_MAX_N; ++i) perm[i] = i;
        std::shuffle(perm.begin(), perm.end(), harnessRng);
        for (int i = 0; i < HUNGARIAN_MAX_N; ++i)
            for (int j = 0; j < HUNGARIAN_MAX_M; ++j) gCost[i][j] = 1000000000000LL;
        long long planted = 0;
        for (int i = 0; i < HUNGARIAN_MAX_N; ++i) { gCost[i][perm[i]] = i % 7; planted += i % 7; }
        scribble();
        CHECK(hungarian_min_cost(HUNGARIAN_MAX_N, HUNGARIAN_MAX_M, gCost, gAssign) == planted);
        for (int i = 0; i < HUNGARIAN_MAX_N; ++i) CHECK(gAssign[i] == perm[i]);
    }
    // 용량 경계 2: n = 1, m = 1000(직사각)과 n = m = 500 무작위.
    fill(1, HUNGARIAN_MAX_M, 5, 1000000);
    gCost[0][777] = 4;
    scribble();
    CHECK(hungarian_min_cost(1, HUNGARIAN_MAX_M, gCost, gAssign) == 4 && gAssign[0] == 777);
    certificateCase(500, 0, 1000000000000LL);
    // 마지막으로 작은 입력을 다시: 큰 호출의 흔적이 남아 있어도 정확하다.
    smallCase(4, 6, -20, 20);
    smallCase(1, 1, 3, 3);

    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
