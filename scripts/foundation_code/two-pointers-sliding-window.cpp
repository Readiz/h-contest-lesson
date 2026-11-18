// two-pointers-sliding-window 하네스: 제출 코드 바깥의 로컬 검사.
#include <climits>
#include <set>

static int gA[MAX_N], gTemp[MAX_N];

// 로컬 연습: 합이 S 이상인 연속 구간의 최소 길이, 없으면 0.
static int sample() {
    int n;
    long long target;
    std::cin >> n >> target;
    for (int i = 0; i < n; ++i) std::cin >> gA[i];
    int answer = minLengthAtLeastSum(gA, n, target);
    std::printf("%d\n", answer == -1 ? 0 : answer);
    return 0;
}

static int randomValue(int range) { return rnd(2 * range + 1) - range; }

static void pairCase(int n, int range) {
    std::vector<int> v(n);
    for (int& x : v) x = randomValue(range);
    for (int target = -2 * range - 1; target <= 2 * range + 1; ++target) {
        bool want = false;
        for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) want |= (long long)v[i] + v[j] == target;
        for (int i = 0; i < n; ++i) gA[i] = v[i];
        CHECK(hasPairWithSum(gA, gTemp, n, target) == want);
        CHECK(std::is_sorted(gA, gA + n));
    }
}

static void shortestCase(int n, int maxValue, long long extra) {
    std::vector<int> v(n);
    long long total = 0;
    for (int& x : v) { x = 1 + rnd(maxValue); total += x; }
    for (int i = 0; i < n; ++i) gA[i] = v[i];
    for (long long target = 1; target <= total + 2 + extra; target += 1 + target / 8) {
        int want = -1;
        for (int l = 0; l < n; ++l) {
            long long sum = 0;
            for (int r = l; r < n; ++r) {
                sum += v[r];
                if (sum >= target && (want == -1 || r - l + 1 < want)) want = r - l + 1;
            }
        }
        CHECK(minLengthAtLeastSum(gA, n, target) == want);
    }
}

static void distinctCase(int n, int range) {
    std::vector<int> v(n);
    for (int& x : v) x = randomValue(range);
    for (int i = 0; i < n; ++i) gA[i] = v[i];
    for (int k = -1; k <= n + 1; ++k) {
        int want = 0;
        for (int l = 0; l < n; ++l) {
            std::set<int> seen;
            for (int r = l; r < n; ++r) {
                seen.insert(v[r]);
                if ((int)seen.size() <= k) want = std::max(want, r - l + 1);
            }
        }
        CHECK(longestAtMostKDistinct(gA, n, k) == want);
        for (int i = 0; i < n; ++i) CHECK(gA[i] == v[i]); // 입력 배열은 바꾸지 않는다
    }
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 본문 예: 양수 배열 2 1 3 2에서 합 5 이상의 가장 짧은 구간은 길이 2 (3, 2).
    {
        int a[4] = {2, 1, 3, 2};
        CHECK(minLengthAtLeastSum(a, 4, 5) == 2);
        CHECK(minLengthAtLeastSum(a, 4, 9) == -1 && minLengthAtLeastSum(a, 4, 8) == 4);
    }
    for (int trial = 0; trial < 200; ++trial) pairCase(rnd(9), 1 + rnd(6));
    for (int trial = 0; trial < 200; ++trial) shortestCase(rnd(10), 1 + rnd(6), 3);
    for (int trial = 0; trial < 150; ++trial) distinctCase(rnd(12), rnd(4));
    // 큰 TC -> 작은 TC -> 큰 TC로 크기를 바꿔 이어 실행: 전역 배열의 이전 값이 섞이지 않는다.
    for (int n : {300, 2, 0, 40, 1}) { pairCase(n < 100 ? n : 20, 50); distinctCase(n < 100 ? n : 40, 6); }
    // 값 범위: INT_MIN, INT_MAX가 섞여도 합은 long long으로 계산한다.
    {
        int a[4] = {INT_MAX, 5, INT_MIN, INT_MAX};
        CHECK(hasPairWithSum(a, gTemp, 4, -1) == true); // INT_MAX + INT_MIN
        int b[4] = {INT_MAX, 5, INT_MIN, INT_MAX};
        CHECK(hasPairWithSum(b, gTemp, 4, 0) == false);
        int c[5] = {INT_MAX, INT_MIN, INT_MAX, INT_MIN, 0};
        CHECK(longestAtMostKDistinct(c, 5, 2) == 4 && longestAtMostKDistinct(c, 5, 3) == 5);
    }
    CHECK(minLengthAtLeastSum(gA, 0, 1) == -1);
    CHECK(!hasPairWithSum(gA, gTemp, 0, 0) && !hasPairWithSum(gA, gTemp, 1, 0));
    CHECK(longestAtMostKDistinct(gA, 0, 3) == 0);
    CHECK(longestAtMostKDistinct(gA, MAX_N + 1, 3) == -1 && longestAtMostKDistinct(gA, -1, 3) == -1);
    // 용량 경계: n = MAX_N.
    for (int i = 0; i < MAX_N; ++i) gA[i] = 1000000;
    CHECK(minLengthAtLeastSum(gA, MAX_N, 200000000000LL) == MAX_N);
    CHECK(minLengthAtLeastSum(gA, MAX_N, 200000000001LL) == -1);
    CHECK(minLengthAtLeastSum(gA, MAX_N, 1000000000000LL) == -1);
    CHECK(longestAtMostKDistinct(gA, MAX_N, 1) == MAX_N);
    for (int i = 0; i < MAX_N; ++i) gA[i] = (MAX_N - i) * 7919 - 1000000000; // 서로 다른 값, 역순
    CHECK(longestAtMostKDistinct(gA, MAX_N, 1) == 1);
    CHECK(longestAtMostKDistinct(gA, MAX_N, 1000) == 1000);
    CHECK(longestAtMostKDistinct(gA, MAX_N, MAX_N) == MAX_N);
    CHECK(hasPairWithSum(gA, gTemp, MAX_N, (1 * 7919 - 1000000000) + (2 * 7919 - 1000000000)));
    CHECK(!hasPairWithSum(gA, gTemp, MAX_N, 1));
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
