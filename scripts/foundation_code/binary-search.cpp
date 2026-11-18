// binary-search 하네스: 제출 코드 바깥의 로컬 검사.
static const int HARNESS_N = 200000;
static long long gTime[HARNESS_N];
static int gA[HARNESS_N], gTemp[HARNESS_N];

// 로컬 연습: 기계들이 K개 이상을 처음 완성하는 정수 시각.
static int sample() {
    int n;
    long long k;
    std::cin >> n >> k;
    for (int i = 0; i < n; ++i) std::cin >> gTime[i];
    std::printf("%lld\n", minimumTime(gTime, n, k));
    return 0;
}

static void lowerBoundCase(int n, int range) {
    for (int i = 0; i < n; ++i) gA[i] = rnd(range) - range / 2;
    std::sort(gA, gA + n);
    for (int target = -range / 2 - 2; target <= range / 2 + 2; ++target) {
        int want = (int)(std::lower_bound(gA, gA + n, target) - gA);
        CHECK(lowerBound(gA, n, target) == want);
        // upper_bound는 비교 조건만 바꾼다: 같은 값의 개수 = 두 경계의 차이.
        int upper = (int)(std::upper_bound(gA, gA + n, target) - gA);
        CHECK(upper - want == (int)std::count(gA, gA + n, target));
    }
}

static long long slowTime(const std::vector<long long>& t, long long need) {
    for (long long x = 0;; ++x) {
        long long made = 0;
        for (long long one : t) made += x / one;
        if (made >= need) return x;
    }
}

// 독립 기준: 정렬한 뒤 모든 k개 부분집합을 전수 조사해 인접 간격의 최솟값을 최대화한다.
static int bruteDistance(std::vector<int> pos, int k) {
    std::sort(pos.begin(), pos.end());
    int n = (int)pos.size(), best = -1;
    for (int mask = 0; mask < (1 << n); ++mask) {
        if (__builtin_popcount(mask) != k) continue;
        int last = -1, smallest = 2000000000;
        for (int i = 0; i < n; ++i) if (mask >> i & 1) {
            if (last >= 0) smallest = std::min(smallest, pos[i] - last);
            last = pos[i];
        }
        best = std::max(best, smallest);
    }
    return best;
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 본문 예: [1, 3, 3, 7, 9]에서 lower_bound(3) = 1, (4) = 3, (10) = 5.
    {
        int a[5] = {1, 3, 3, 7, 9};
        CHECK(lowerBound(a, 5, 3) == 1 && lowerBound(a, 5, 4) == 3 && lowerBound(a, 5, 10) == 5);
        CHECK(lowerBound(a, 5, 0) == 0 && lowerBound(a, 0, 3) == 0);
    }
    for (int trial = 0; trial < 300; ++trial) lowerBoundCase(rnd(12), 1 + rnd(9));
    for (int n : {1000, 3, 0, 5, HARNESS_N}) lowerBoundCase(n, 50);
    // 가능한 최소값: 시각을 하나씩 늘리는 기준 풀이와 비교.
    for (int trial = 0; trial < 400; ++trial) {
        int n = 1 + rnd(5);
        std::vector<long long> t(n);
        for (int i = 0; i < n; ++i) gTime[i] = t[i] = 1 + rnd(12);
        long long need = 1 + rnd(40);
        CHECK(minimumTime(gTime, n, need) == slowTime(t, need));
    }
    // 연습 예시와 경계: 최대 입력에서 누적합이 넘치지 않는다.
    gTime[0] = 2; gTime[1] = 3; gTime[2] = 7;
    CHECK(minimumTime(gTime, 3, 10) == 12);
    for (int i = 0; i < HARNESS_N; ++i) gTime[i] = 1000000000LL;
    CHECK(minimumTime(gTime, HARNESS_N, 1000000000LL) == 5000000000000LL); // 5000 * 10^9
    CHECK(minimumTime(gTime, 1, 1000000000LL) == 1000000000LL * 1000000000LL);
    for (int i = 0; i < HARNESS_N; ++i) gTime[i] = 1;
    CHECK(minimumTime(gTime, HARNESS_N, 1000000000LL) == 5000);
    CHECK(minimumTime(gTime, 1, 1) == 1);
    // 가능한 최대값: 전수 조사와 비교하고, 입력이 정렬되어 있지 않아도 함수가 정렬한다.
    for (int trial = 0; trial < 500; ++trial) {
        int n = 2 + rnd(9), k = 2 + rnd(n - 1);
        std::vector<int> pos(n);
        for (int& x : pos) x = rnd(30);
        for (int i = 0; i < n; ++i) gA[i] = pos[i];
        int want = bruteDistance(pos, k);
        CHECK(maximizeMinimumDistance(gA, gTemp, n, k) == want);
        CHECK(std::is_sorted(gA, gA + n));
    }
    // 용량 경계: n = 200000, 역순 입력, 좌표 상한 10^9 근처.
    for (int i = 0; i < HARNESS_N; ++i) gA[i] = (HARNESS_N - 1 - i) * 5000;
    CHECK(maximizeMinimumDistance(gA, gTemp, HARNESS_N, HARNESS_N) == 5000);
    CHECK(maximizeMinimumDistance(gA, gTemp, HARNESS_N, 2) == (HARNESS_N - 1) * 5000);
    gA[0] = 0; gA[1] = 1000000000;
    CHECK(maximizeMinimumDistance(gA, gTemp, 2, 2) == 1000000000);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
