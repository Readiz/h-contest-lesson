// coordinate-compression 하네스: 제출 코드 바깥의 로컬 검사.
#include <set>

static long long gA[MAX_N], gValues[MAX_N], gTemp[MAX_N];

// 로컬 연습: 서로 다른 값의 수, 원래 순서의 압축값, 정렬된 서로 다른 원본 값.
static int sample() {
    int n;
    std::cin >> n;
    for (int i = 0; i < n; ++i) std::cin >> gA[i];
    int m = buildCoords(gA, n, gValues, gTemp);
    std::printf("%d\n", m);
    for (int i = 0; i < n; ++i) std::printf("%d%c", compress(gValues, m, gA[i]), i + 1 < n ? ' ' : '\n');
    for (int i = 0; i < m; ++i) std::printf("%lld%c", gValues[i], i + 1 < m ? ' ' : '\n');
    return 0;
}

static void randomCase(int n, long long range) {
    std::vector<long long> a(n);
    for (auto& x : a) x = (long long)(harnessRng() % (unsigned long long)(2 * range + 1)) - range;
    for (int i = 0; i < n; ++i) gA[i] = a[i];
    for (int i = 0; i < MAX_N; ++i) gValues[i] = 999; // 이전 TC의 값
    int m = buildCoords(gA, n, gValues, gTemp);
    std::set<long long> expected(a.begin(), a.end()); // 독립 기준: 순서 있는 집합
    CHECK(m == (int)expected.size());
    int index = 0;
    for (long long x : expected) CHECK(gValues[index++] == x);
    for (int i = 0; i < n; ++i) {
        int r = compress(gValues, m, a[i]);
        CHECK(r >= 0 && r < m && gValues[r] == a[i]); // 복원
        for (int j = 0; j < n && n <= 100; ++j) CHECK((a[i] < a[j]) == (compress(gValues, m, a[i]) < compress(gValues, m, a[j])));
        CHECK(gA[i] == a[i]); // 입력은 바뀌지 않는다
    }
    // 없는 값은 삽입 위치를 돌려준다: 최솟값보다 작으면 0, 최댓값보다 크면 m.
    CHECK(compress(gValues, m, -range - 1) == 0);
    CHECK(compress(gValues, m, range + 1) == m);
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 본문 예: 1, 500000000, 1000000000 -> 0, 1, 2.
    {
        long long a[3] = {1000000000, 1, 500000000}, values[3], temp[3];
        CHECK(buildCoords(a, 3, values, temp) == 3);
        CHECK(compress(values, 3, 1) == 0 && compress(values, 3, 500000000) == 1 && compress(values, 3, 1000000000) == 2);
    }
    for (int trial = 0; trial < 300; ++trial) randomCase(rnd(16), 1 + rnd(8));
    // 크기가 바뀌는 TC, 64비트 값, 모두 같은 값, 감소 순서, 빈 입력.
    for (int n : {2000, 3, 0, 40, 1}) randomCase(n, n < 100 ? 6 : 1000000000000LL);
    for (int i = 0; i < 5; ++i) gA[i] = 7;
    CHECK(buildCoords(gA, 5, gValues, gTemp) == 1 && gValues[0] == 7);
    for (int i = 0; i < 5; ++i) gA[i] = 100 - i;
    CHECK(buildCoords(gA, 5, gValues, gTemp) == 5 && gValues[0] == 96 && gValues[4] == 100);
    CHECK(buildCoords(gA, 0, gValues, gTemp) == 0);
    CHECK(buildCoords(gA, -1, gValues, gTemp) == -1 && buildCoords(gA, MAX_N + 1, gValues, gTemp) == -1);
    // 용량 경계: n = MAX_N, 서로 다른 값 +-10^12와 전부 같은 값.
    for (int i = 0; i < MAX_N; ++i) gA[i] = (i % 2 ? 1 : -1) * 1000000000000LL + (MAX_N - i);
    CHECK(buildCoords(gA, MAX_N, gValues, gTemp) == MAX_N);
    CHECK(std::is_sorted(gValues, gValues + MAX_N));
    for (int i = 0; i < MAX_N; ++i) CHECK(gValues[compress(gValues, MAX_N, gA[i])] == gA[i]);
    for (int i = 0; i < MAX_N; ++i) gA[i] = -1000000000000LL;
    CHECK(buildCoords(gA, MAX_N, gValues, gTemp) == 1 && compress(gValues, 1, gA[5]) == 0);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
