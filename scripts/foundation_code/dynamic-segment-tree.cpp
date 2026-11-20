// dynamic-segment-tree 하네스: 제출 코드 바깥의 로컬 검사.
static const long long BIG = 1000000000000LL; // 연습의 좌표 상한 10^12

// 로컬 연습: 좌표 [0, 10^12), A l r delta는 [l, r)에 더하기, S l r은 합.
static int sample() {
    int q;
    std::cin >> q;
    dynamicTree.init(0, BIG);
    for (int i = 0; i < q; ++i) {
        std::string op;
        long long l, r, delta;
        std::cin >> op >> l >> r;
        if (op == "A") {
            std::cin >> delta;
            dynamicTree.add(l, r, delta);
        } else {
            std::printf("%lld\n", dynamicTree.sum(l, r));
        }
    }
    return 0;
}

static int heightOf(long long length) { // 2^h >= length인 가장 작은 h
    int h = 0;
    while ((1LL << h) < length) ++h;
    return h;
}

static void garbage() {
    // 이전 TC가 남긴 값을 흉내 내려고 pool 전체를 쓰레기 값으로 채운다.
    for (int i = 0; i < MAX_NODES; ++i) dynamicTree.pool[i] = Node{3, 5, 777, 888};
    dynamicTree.used = MAX_NODES;
}

// 작은 좌표 범위: 원소별 배열과 비교하고 연산마다 새로 만든 node 수가 4 * 높이 이하인지 본다.
static void smallCase(long long length, int operations) {
    garbage();
    CHECK(dynamicTree.init(0, length));
    CHECK(dynamicTree.used == 2);
    std::vector<long long> a((size_t)length, 0);
    int height = heightOf(length);
    for (int op = 0; op < operations; ++op) {
        long long l = rnd((int)length + 1), r = rnd((int)length + 1);
        if (l > r) std::swap(l, r);
        int before = dynamicTree.used;
        if (rnd(2) == 0) {
            long long delta = rnd(201) - 100;
            dynamicTree.add(l, r, delta);
            for (long long i = l; i < r; ++i) a[(size_t)i] += delta;
        } else {
            long long want = 0;
            for (long long i = l; i < r; ++i) want += a[(size_t)i];
            CHECK(dynamicTree.sum(l, r) == want);
        }
        CHECK(dynamicTree.used - before <= 4 * height);
    }
    for (long long i = 0; i < length; ++i) CHECK(dynamicTree.sum(i, i + 1) == a[(size_t)i]);
}

// 큰 좌표 범위: 몇 개의 기준 좌표만 쓰고, 기준 좌표 사이 조각 단위로 기준 구현을 만든다.
static void bigCase(int operations) {
    garbage();
    CHECK(dynamicTree.init(0, BIG));
    std::vector<long long> points = {0, 1, BIG - 1, BIG};
    for (int i = 0; i < 10; ++i) points.push_back((long long)(harnessRng() % (unsigned long long)BIG));
    std::sort(points.begin(), points.end());
    points.erase(std::unique(points.begin(), points.end()), points.end());
    int m = (int)points.size();
    std::vector<long long> piece(m - 1, 0); // 조각 k는 [points[k], points[k + 1])의 원소별 값
    int height = heightOf(BIG);
    for (int op = 0; op < operations; ++op) {
        int i = rnd(m), j = rnd(m);
        if (i > j) std::swap(i, j);
        int before = dynamicTree.used;
        if (rnd(2) == 0) {
            long long delta = rnd(201) - 100;
            dynamicTree.add(points[i], points[j], delta);
            for (int k = i; k < j; ++k) piece[k] += delta;
        } else {
            long long want = 0;
            for (int k = i; k < j; ++k) want += piece[k] * (points[k + 1] - points[k]);
            CHECK(dynamicTree.sum(points[i], points[j]) == want);
        }
        CHECK(dynamicTree.used - before <= 4 * height);
    }
}

int main(int argc, char** argv) {
    if (argc > 1) return sample();
    // 본문 그림: [0, 8)에서 [5, 6)에 3을 더하면 root, [4, 8), [4, 6), [5, 6)의 네 node만 생긴다.
    CHECK(dynamicTree.init(0, 8));
    dynamicTree.add(5, 6, 3);
    CHECK(dynamicTree.used == 2 + 3); // root는 init이 만들고 나머지 세 개가 새로 생긴다.
    CHECK(dynamicTree.sum(0, 8) == 3 && dynamicTree.sum(5, 6) == 3 && dynamicTree.sum(0, 5) == 0);
    // 연습 예시와 같은 입력.
    CHECK(dynamicTree.init(0, BIG));
    dynamicTree.add(0, 10, 2);
    CHECK(dynamicTree.sum(0, 1) == 2);
    dynamicTree.add(5, 8, -1);
    CHECK(dynamicTree.sum(4, 9) == 7 && dynamicTree.sum(9, 10) == 2 && dynamicTree.sum(5, 5) == 0);
    // 무작위 비교와 크기가 다른 TC를 이어 실행한다(매번 pool을 쓰레기로 채운 뒤 init).
    for (long long length : {1LL, 2LL, 3LL, 20LL, 1LL, 64LL, 100LL, 7LL, 1000LL}) smallCase(length, 300);
    for (int trial = 0; trial < 60; ++trial) smallCase(1 + rnd(40), 100);
    for (int trial = 0; trial < 30; ++trial) bigCase(200);
    CHECK(!dynamicTree.init(5, 5));
    CHECK(!dynamicTree.init(6, 5));
    // 용량 경계: 전체 구간 갱신 뒤 부분 질의, 같은 구간의 더하기·빼기, 끝 좌표.
    CHECK(dynamicTree.init(0, BIG));
    dynamicTree.add(0, BIG, 100);
    CHECK(dynamicTree.sum(0, BIG) == 100 * BIG);
    CHECK(dynamicTree.sum(BIG - 1, BIG) == 100 && dynamicTree.sum(7, 7) == 0);
    dynamicTree.add(123456789, 987654321012LL, 100);
    dynamicTree.add(123456789, 987654321012LL, -100);
    CHECK(dynamicTree.sum(0, BIG) == 100 * BIG);
    // 용량 경계: MAX_OPS번 호출(한 구간의 끝점이 계속 달라지는 갱신과 질의)이 pool 안에 든다.
    garbage();
    CHECK(dynamicTree.init(0, BIG));
    for (int op = 0; op < MAX_OPS; ++op) {
        long long l = (long long)(harnessRng() % (unsigned long long)BIG);
        long long r = (long long)(harnessRng() % (unsigned long long)BIG);
        if (l > r) std::swap(l, r);
        if (op % 2 == 0) dynamicTree.add(l, r, 100);
        else (void)dynamicTree.sum(l, r);
        CHECK(dynamicTree.used <= MAX_NODES);
    }
    // 빈 구간.
    CHECK(dynamicTree.init(0, BIG));
    CHECK(dynamicTree.sum(5, 5) == 0);
    dynamicTree.add(9, 9, 100);
    CHECK(dynamicTree.sum(0, BIG) == 0);
    std::printf("%lld checks\n", harnessChecks);
    return 0;
}
