// Harness for the destroy-and-repair check. Standard headers are fine here; the lesson code is included below.
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <set>
#include <string>
#include <vector>
#include "lesson.cpp"

typedef long long ll;
typedef unsigned long long ull;

// ---------------------------------------------------------------- independent references (this check only)
static ll refRoute(const Route& r, const int* p, int len) {
    ll s = 0;
    for (int k = 0; k + 1 < len; ++k) s += std::abs(r.px[p[k]] - r.px[p[k + 1]]) + std::abs(r.py[p[k]] - r.py[p[k + 1]]);
    return s;
}
static bool refRouteValid(const int* p, int n) {
    std::vector<int> v(p, p + n);
    std::sort(v.begin(), v.end());
    for (int i = 0; i < n; ++i) if (v[i] != i) return false;
    return true;
}
static ll refAssign(const Assign& a, const int* as) {
    std::vector<ll> load(a.m, 0);
    ll c = 0;
    for (int i = 0; i < a.n; ++i) { load[as[i]] += a.d[i]; c += a.c[i][as[i]]; }
    ll sq = 0;
    for (int j = 0; j < a.m; ++j) sq += load[j] * load[j];
    return sq / 100 + c;
}
static bool refAssignValid(const Assign& a, const int* as) {
    std::vector<int> cnt(a.m, 0);
    for (int i = 0; i < a.n; ++i) { if (as[i] < 0 || as[i] >= a.m) return false; ++cnt[as[i]]; }
    for (int j = 0; j < a.m; ++j) if (cnt[j] > a.k) return false;
    return true;
}
static bool cachesOk(const Assign& a) {
    std::vector<ll> load(a.m, 0), cnt(a.m, 0);
    ll cs = 0;
    for (int i = 0; i < a.n; ++i) { load[a.as[i]] += a.d[i]; ++cnt[a.as[i]]; cs += a.c[i][a.as[i]]; }
    ll sq = 0;
    for (int j = 0; j < a.m; ++j) { if (load[j] != a.load[j] || cnt[j] != a.cnt[j]) return false; sq += load[j] * load[j]; }
    return sq == a.sq && cs == a.csum;
}
static ull fnv(const int* v, int n, ull h = 1469598103934665603ULL) {
    for (int i = 0; i < n; ++i) { h ^= (ull)(unsigned)v[i]; h *= 1099511628211ULL; }
    return h;
}

static const ll RB = 4000000, AB = 2000000;       // 기본 예산(연산 수)
static const Cfg RC = {2, 8, 0, 0, 0};            // 순서 틀 기본: 가까운 점 8개, 가장 싼 자리, 좋아질 때만
static const Cfg AC = {0, 8, 1, 0, 0};            // 배정 틀 기본: 무작위 작업 8개, 후회 기준, 좋아질 때만

// ---------------------------------------------------------------- modes
static void modeGen() {
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200);
        ull h = fnv(route.px, 200); h = fnv(route.py, 200, h);
        printf("gen route %d %llu %lld %lld\n", s, h, route.fullCost(), refRoute(route, route.buf[0], 200));
        genAssign(assign, s, 120, 8, 18, 1);
        ull g = fnv(assign.d, 120);
        for (int i = 0; i < 120; ++i) g = fnv(assign.c[i], 8, g);
        printf("gen assign %d %llu %lld %lld\n", s, g, assign.fullCost(), refAssign(assign, assign.as));
    }
}

// checkDR over the options; rollback exactness of the arrays; every kind, rule, accept rule and restore method.
static void modeCheck() {
    const int sizes[] = {1, 8, 200};
    for (int kind = 0; kind < 4; ++kind) for (int rep = 0; rep < 2; ++rep) for (int acc = 0; acc < 3; ++acc) for (int size : sizes) for (int s = 1; s <= 2; ++s) {
        genRoute(route, s, 200);
        hc::Random rng; rng.reset((unsigned)s);
        Cfg c{kind, size, rep, acc, 50};
        const int r = checkDR(route, rng, c, size == 200 ? 12 : 120);
        printf("check route %d %d %d %d %d %d\n", kind, rep, acc, size, s, r);
    }
    for (int kind = 0; kind < 3; ++kind) for (int rep = 0; rep < 2; ++rep) for (int acc = 0; acc < 3; ++acc) for (int lg = 0; lg < 2; ++lg) for (int s = 1; s <= 2; ++s) {
        const int sz = kind == 1 ? 2 : 15;
        genAssign(assign, s, 120, 8, 18, lg);
        hc::Random rng; rng.reset((unsigned)s);
        Cfg c{kind, sz, rep, acc, 5};
        printf("check assign %d %d %d %d %d %d\n", kind, rep, acc, lg, s, checkDR(assign, rng, c, 150));
        genAssign(assign, s, 24, 8, 3, lg);          // 모든 기계가 가득 찬 입력
        hc::Random rng2; rng2.reset((unsigned)s);
        Cfg c2{kind, kind == 1 ? 1 : 12, rep, acc, 5};
        printf("check tight %d %d %d %d %d %d\n", kind, rep, acc, lg, s, checkDR(assign, rng2, c2, 150));
    }
    // 부수기 하나하나: 떼어 낸 것은 부분 해에서 빠지고 나머지의 순서는 유지된다
    ll bad = 0, total = 0;
    for (int kind = 0; kind < 4; ++kind) for (int s = 1; s <= 5; ++s) for (int size : {1, 3, 8, 21}) {
        genRoute(route, s, 200);
        hc::Random rng; rng.reset((unsigned)s);
        for (int t = 0; t < 20; ++t) {
            Cfg c{kind, size, 0, 0, 0};
            route.mark(); route.destroy(rng, c);
            const int* a = route.buf[route.c]; const int* b = route.buf[route.h];
            bool ok = route.np == size && route.m[route.h] == 200 - size;
            std::vector<char> gone(200, 0);
            for (int i = 0; i < route.np; ++i) { if (gone[route.pool[i]]) ok = false; gone[route.pool[i]] = 1; }
            int w = 0;
            for (int i = 0; i < 200 && ok; ++i) if (!gone[a[i]]) { if (b[w++] != a[i]) ok = false; }
            if (kind == 1) {                          // 연속 구간: 길이 size의 이어진 구간
                int first = 200;
                for (int i = 0; i < 200; ++i) if (gone[a[i]]) { first = i; break; }
                for (int i = first; i < first + size; ++i) if (!gone[a[i]]) ok = false;
            }
            if (kind == 2) {                          // 가까운 점: pool[0]이 기준점, 나머지는 기준점에서의 거리가 뽑히지 않은 점보다 작거나 같다
                const int s0 = route.pool[0]; ll far = 0, near = 1 << 30;
                for (int x = 0; x < 200; ++x) {
                    const ll d = std::abs(route.px[s0] - route.px[x]) + std::abs(route.py[s0] - route.py[x]);
                    if (gone[x]) far = std::max(far, d); else near = std::min(near, d);
                }
                if (far > near) ok = false;
            }
            ++total; if (!ok) ++bad;
            route.rollback();
        }
    }
    printf("destroyroute %lld %lld\n", total, bad);
    bad = total = 0;
    for (int s = 1; s <= 5; ++s) for (int lg = 0; lg < 2; ++lg) {
        genAssign(assign, s, 120, 8, 18, lg);
        hc::Random rng; rng.reset((unsigned)s);
        for (int t = 0; t < 40; ++t) {
            Cfg c{1, 1 + t % 3, 0, 0, 0};
            int before[AN]; std::memcpy(before, assign.as, sizeof before);
            assign.mark(); assign.destroy(rng, c);
            bool ok = true; std::vector<char> mach(8, 0); int removed = 0;
            for (int i = 0; i < 120; ++i) if (assign.as[i] < 0) { mach[before[i]] = 1; ++removed; }
            int nm = 0; for (int j = 0; j < 8; ++j) nm += mach[j];
            if (nm != c.size || removed != assign.np) ok = false;
            for (int i = 0; i < 120; ++i) if (mach[before[i]] != (assign.as[i] < 0)) ok = false;
            ++total; if (!ok) ++bad;
            assign.repair(rng, c);
            assign.rollback();
            if (std::memcmp(before, assign.as, sizeof before) != 0 || !cachesOk(assign)) ++bad;
        }
    }
    printf("destroyassign %lld %lld\n", total, bad);
    // route 롤백: 확정된 배열은 부수기·다시 짓기 동안 바뀌지 않는다
    bad = total = 0;
    for (int s = 1; s <= 5; ++s) {
        genRoute(route, s, 200);
        hc::Random rng; rng.reset((unsigned)s);
        Cfg c{2, 8, 1, 0, 0};
        for (int t = 0; t < 30; ++t) {
            int before[RN]; std::memcpy(before, route.buf[route.c], sizeof before);
            const ll lb = route.L[route.c];
            route.mark(); route.destroy(rng, c); route.repair(rng, c);
            route.rollback();
            if (std::memcmp(before, route.buf[route.c], sizeof before) != 0 || route.L[route.c] != lb || route.h != route.c) ++bad;
            ++total;
        }
    }
    printf("rollbackroute %lld %lld\n", total, bad);
}

// 복사 방식과 기록 방식은 같은 제안을 같은 순서로 받고 거절한다(고정 반복 수).
static void modeIdentity() {
    struct K { int kind, size, rule; };
    const K ks[] = {{0, 8, 0}, {0, 8, 1}, {1, 2, 1}, {2, 8, 0}};
    for (const K& k : ks) for (int s = 1; s <= 5; ++s) {
        int sol[2][AN]; ll ops[2], cost[2], wr[2];
        for (int lg = 0; lg < 2; ++lg) {
            genAssign(assign, s, 120, 8, 18, lg);
            hc::Random rng; rng.reset((unsigned)s);
            Cfg c{k.kind, k.size, k.rule, 2, 5};
            ll cur = assign.cost();
            for (int t = 0; t < 400; ++t) {
                ++assign.ops;
                assign.mark(); assign.destroy(rng, c); assign.repair(rng, c);
                const ll now = assign.cost();
                if (accepts(c, now, cur, 1000000000LL, 2000000000LL, rng)) { assign.keep(); cur = now; } else assign.rollback();
            }
            std::memcpy(sol[lg], assign.as, sizeof sol[lg]); ops[lg] = assign.ops; cost[lg] = cur; wr[lg] = assign.writes;
        }
        printf("identity %d %d %d %d %d %lld %lld %lld %lld %lld\n", k.kind, k.size, k.rule, s, std::memcmp(sol[0], sol[1], sizeof sol[0]) == 0, ops[0], ops[1], cost[0], cost[1], wr[0] - wr[1]);
    }
}

// 작은 이동만 쓰는 탐색: 비용은 단조 감소, 추적한 비용은 처음부터 다시 계산한 값과 같고 해는 유효하다.
static void modeSmall() {
    for (int s = 1; s <= 5; ++s) {
        genRoute(route, s, 200);
        hc::Random rng; rng.reset((unsigned)s);
        ll last = route.cost(); int mono = 1;
        for (int t = 0; t < 20000; ++t) { route.smallStep(rng); if (route.cost() > last) mono = 0; last = route.cost(); }
        printf("small route %d %d %d %lld %lld\n", s, mono, refRouteValid(route.buf[route.c], 200), route.cost(), refRoute(route, route.buf[route.c], 200));
        genAssign(assign, s, 120, 8, 18, 1);
        hc::Random rng2; rng2.reset((unsigned)s);
        last = assign.cost(); mono = 1;
        for (int t = 0; t < 20000; ++t) { assign.smallStep(rng2); if (assign.cost() > last) mono = 0; last = assign.cost(); }
        printf("small assign %d %d %d %lld %lld %d\n", s, mono, refAssignValid(assign, assign.as), assign.cost(), refAssign(assign, assign.as), cachesOk(assign));
    }
}

static void modeExpo() {
    const ll nums[] = {0, 16, 32, 64, 128, 256, 512, 960, 1023, 1024};
    for (ll num : nums) printf("expo %lld 64 %d\n", num, expNeg16(num, 64));      // x = num / 64
    printf("expo 1000 1 %d\n", expNeg16(1000, 1));
    printf("expo 5 0 %d\n", expNeg16(5, 0));
    printf("expo 40000000000 1000000 %d\n", expNeg16(40000000000LL, 1000000));
}

// ---------------------------------------------------------------- hand examples (run through the lesson code)
static void printRoute(const char* tag) {
    printf("%s %d %lld %lld", tag, route.m[route.h], route.L[route.h], refRoute(route, route.buf[route.h], route.m[route.h]));
    for (int i = 0; i < route.m[route.h]; ++i) printf(" %d", route.buf[route.h][i]);
    printf("\n");
}
static void modeHand() {
    const int pts[7][2] = {{4, 9}, {0, 7}, {1, 0}, {5, 0}, {2, 1}, {2, 4}, {8, 4}};
    route.n = 7;
    for (int i = 0; i < 7; ++i) { route.px[i] = pts[i][0]; route.py[i] = pts[i][1]; }
    route.init();
    printf("hand route start %lld\n", route.cost());
    for (int rep = 0; rep < 2; ++rep) {
        Cfg c{1, 2, rep, 0, 0};
        int found = -1;
        for (int seed = 1; seed <= 500 && found < 0; ++seed) {
            hc::Random rng; rng.reset((unsigned)seed * 2654435761u);
            route.mark(); route.destroy(rng, c);
            if (route.np == 2 && route.pool[0] == 4 && route.pool[1] == 5) { found = seed; break; }
            route.rollback();
        }
        printf("hand route seed %d rep %d\n", found, rep);
        printRoute("hand route partial");
        if (rep == 0) {
            hc::Random rng0; rng0.reset(1);
            printf("hand route slots4");
            for (int s = 0; s <= route.m[route.h]; ++s) printf(" %lld", route.slotCost(4, s));
            printf("\n");
            long long b, sec; int slot;
            route.scan(4, b, sec, slot);
            printf("hand route best4 %lld %lld %d\n", b, sec, slot);
            route.insertAt(4, slot, b);
            printf("hand route slots5");
            for (int s = 0; s <= route.m[route.h]; ++s) printf(" %lld", route.slotCost(5, s));
            printf("\n");
            route.scan(5, b, sec, slot);
            printf("hand route best5 %lld %lld %d\n", b, sec, slot);
            route.rollback();
            // 같은 부분 해에서 repair 전체를 다시: destroy를 다시 해 같은 pool을 얻는다
            for (int seed = 1; seed <= 500; ++seed) {
                hc::Random rng; rng.reset((unsigned)seed * 2654435761u);
                route.mark(); route.destroy(rng, c);
                if (route.np == 2 && route.pool[0] == 4 && route.pool[1] == 5) break;
                route.rollback();
            }
        }
        hc::Random rr; rr.reset(1);
        route.repair(rr, c);
        printRoute("hand route repaired");
        route.rollback();
    }
    // 배정: 작업 6개, 기계 3대, 한 대에 2개
    const int dd[6] = {28, 24, 12, 18, 31, 60};
    const int cc[6][3] = {{26, 29, 23}, {21, 27, 27}, {3, 15, 18}, {4, 20, 16}, {1, 25, 13}, {25, 4, 1}};
    const int as0[6] = {1, 1, 2, 0, 0, 2};
    for (int lg = 0; lg < 2; ++lg) {
        assign.n = 6; assign.m = 3; assign.k = 2; assign.useLog = lg;
        for (int i = 0; i < 6; ++i) { assign.d[i] = dd[i]; for (int j = 0; j < 3; ++j) assign.c[i][j] = cc[i][j]; assign.as[i] = as0[i]; }
        hc::iota(assign.ids, 6); assign.build(); assign.np = 0; assign.nlog = 0; assign.ops = assign.writes = assign.iters = assign.accepted = 0;
        printf("hand assign start %lld %d %d %d %lld %lld\n", assign.cost(), assign.load[0], assign.load[1], assign.load[2], assign.sq, assign.csum);
        for (int rep = 0; rep < 2; ++rep) {
            Cfg c{1, 2, rep, 0, 0};
            int found = -1;
            for (int seed = 1; seed <= 500 && found < 0; ++seed) {
                hc::Random rng; rng.reset((unsigned)seed * 2654435761u);
                assign.mark(); assign.destroy(rng, c);
                bool mach12 = assign.np == 4 && assign.as[0] < 0 && assign.as[1] < 0 && assign.as[2] < 0 && assign.as[5] < 0;
                if (mach12) { found = seed; break; }
                assign.rollback();
            }
            printf("hand assign seed %d log %d rep %d pool", found, lg, rep);
            for (int i = 0; i < assign.np; ++i) printf(" %d", assign.pool[i]);
            printf("\n");
            hc::Random rr; rr.reset(1);
            assign.repair(rr, c);
            printf("hand assign repaired %d %d %lld %lld", lg, rep, assign.cost(), assign.fullCost());
            for (int i = 0; i < 6; ++i) printf(" %d", assign.as[i]);
            printf(" valid %d\n", refAssignValid(assign, assign.as));
            assign.rollback();
            printf("hand assign rolled %lld %d\n", assign.cost(), cachesOk(assign));
        }
    }
}

// ---------------------------------------------------------------- experiments
template <class F> static void forSeeds(F f) { for (int s = 1; s <= 20; ++s) f(s); }

static void dumpRoute() { for (int k = 0; k < 200; ++k) printf(" %d", route.bestSol[k]); printf("\n"); }
static void dumpAssign() { for (int k = 0; k < 120; ++k) printf(" %d", assign.bestSol[k]); printf("\n"); }

static void rr(const char* tag, const Cfg& c, ll small, ll budget, int seed, const char* extra) {
    const ll r = runRoute(seed, c, small, budget);
    printf("%s route %s %d %lld %lld %lld %lld\n", tag, extra, seed, r, route.iters, route.accepted, refRoute(route, route.bestSol, 200));
}
static void ra(const char* tag, const Cfg& c, int lg, ll small, ll budget, int seed, const char* extra) {
    const ll r = runAssign(seed, c, lg, small, budget);
    printf("%s assign %s %d %lld %lld %lld %lld\n", tag, extra, seed, r, assign.iters, assign.accepted, refAssign(assign, assign.bestSol));
}

static void modeExp() {
    char ex[96];
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200); printf("start route %d %lld\n", s, route.cost());
        genAssign(assign, s, 120, 8, 18, 1); printf("start assign %d %lld\n", s, assign.cost());
    }
    // A: 같은 예산에서 작은 이동만 / 부수고 다시 짓기만 / 작은 이동 1/4 + 부수고 다시 짓기
    const ll rb[] = {1000000, 2000000, 4000000}, ab[] = {400000, 1000000, 2000000};
    for (int bi = 0; bi < 3; ++bi) for (int method = 0; method < 3; ++method) for (int s = 1; s <= 20; ++s) {
        const ll small = method == 0 ? rb[bi] : (method == 1 ? 0 : rb[bi] / 4);
        snprintf(ex, sizeof ex, "%lld %d", rb[bi], method);
        rr("A", RC, small, rb[bi], s, ex);
        if (bi == 2) { printf("final route %d %d", method, s); dumpRoute(); }
        const ll asmall = method == 0 ? ab[bi] : (method == 1 ? 0 : ab[bi] / 4);
        snprintf(ex, sizeof ex, "%lld %d", ab[bi], method);
        ra("A", AC, 1, asmall, ab[bi], s, ex);
        if (bi == 2) { printf("final assign %d %d", method, s); dumpAssign(); }
    }
    // K: 부술 부분을 고르는 방법(예산 전체, 작은 이동 1/4)
    const Cfg rk[] = {{0, 8, 0, 0, 0}, {1, 8, 0, 0, 0}, {2, 8, 0, 0, 0}, {3, 8, 0, 0, 0}};
    for (const Cfg& c : rk) for (int s = 1; s <= 20; ++s) { snprintf(ex, sizeof ex, "%d %d", c.destroy, c.size); rr("K", c, RB / 4, RB, s, ex); }
    const Cfg ak[] = {{0, 8, 1, 0, 0}, {1, 1, 1, 0, 0}, {1, 2, 1, 0, 0}, {2, 8, 1, 0, 0}};
    for (const Cfg& c : ak) for (int s = 1; s <= 20; ++s) { snprintf(ex, sizeof ex, "%d %d", c.destroy, c.size); ra("K", c, 1, AB / 4, AB, s, ex); }
    // R: 다시 짓는 구성법
    const Cfg rrs[] = {{2, 8, 0, 0, 0}, {2, 8, 1, 0, 0}, {1, 8, 0, 0, 0}, {1, 8, 1, 0, 0}};
    for (const Cfg& c : rrs) for (int s = 1; s <= 20; ++s) { snprintf(ex, sizeof ex, "%d %d %d", c.destroy, c.size, c.repair); rr("R", c, RB / 4, RB, s, ex); }
    const Cfg ars[] = {{0, 8, 0, 0, 0}, {0, 8, 1, 0, 0}, {1, 2, 0, 0, 0}, {1, 2, 1, 0, 0}};
    for (const Cfg& c : ars) for (int s = 1; s <= 20; ++s) { snprintf(ex, sizeof ex, "%d %d %d", c.destroy, c.size, c.repair); ra("R", c, 1, AB / 4, AB, s, ex); }
    // C: 받는 기준
    const int rt0[] = {0, 30, 300, 1000}, at0[] = {0, 1, 10, 100};
    for (int accept = 1; accept <= 2; ++accept) for (int ti = 0; ti < 4; ++ti) {
        if (accept == 1 && ti > 0) continue;
        if (accept == 2 && ti == 0) continue;
        for (int s = 1; s <= 20; ++s) {
            Cfg c = RC; c.accept = accept; c.t0 = rt0[ti];
            snprintf(ex, sizeof ex, "%d %d", accept, c.t0);
            rr("C", c, RB / 4, RB, s, ex);
            Cfg d = AC; d.accept = accept; d.t0 = at0[ti];
            snprintf(ex, sizeof ex, "%d %d", accept, d.t0);
            ra("C", d, 1, AB / 4, AB, s, ex);
        }
    }
    // S: 부수는 크기
    const int rsz[] = {1, 2, 3, 5, 8, 13, 21, 40, 80, 200}, asz[] = {1, 2, 4, 8, 16, 32, 64, 120};
    for (int size : rsz) for (int s = 1; s <= 20; ++s) { Cfg c = RC; c.size = size; snprintf(ex, sizeof ex, "%d", size); rr("S", c, RB / 4, RB, s, ex); }
    for (int size : asz) for (int s = 1; s <= 20; ++s) { Cfg c = AC; c.size = size; snprintf(ex, sizeof ex, "%d", size); ra("S", c, 1, AB / 4, AB, s, ex); }
    // H: 설정을 고르는 데 쓰지 않은 시드 21~40에서 작은 이동만과 작은 이동 1/4 + 부수고 다시 짓기(기본 설정)
    for (int method = 0; method < 2; ++method) for (int s = 21; s <= 40; ++s) {
        snprintf(ex, sizeof ex, "%d", method);
        rr("H", RC, method == 0 ? RB : RB / 4, RB, s, ex);
        ra("H", AC, 1, method == 0 ? AB : AB / 4, AB, s, ex);
    }
    // L: 복사 방식과 기록 방식(배정 틀), O: 반복 한 번이 쓰는 연산(작은 이동 없이)
    struct LK { int kind, size, rule; };
    const LK lks[] = {{0, 8, 0}, {0, 8, 1}, {1, 2, 1}};
    for (const LK& k : lks) for (int lg = 0; lg < 2; ++lg) for (int s = 1; s <= 20; ++s) {
        Cfg c{k.kind, k.size, k.rule, 0, 0};
        const ll r = runAssign(s, c, lg, 0, AB);
        printf("L assign %d %d %d %d %d %lld %lld %lld %lld\n", k.kind, k.size, k.rule, lg, s, r, assign.iters, assign.writes, assign.ops);
    }
    for (int s = 1; s <= 20; ++s) {
        const ll r = runRoute(s, RC, 0, RB);
        printf("O route %d %lld %lld %lld %lld\n", s, r, route.iters, route.writes, route.ops);
        const ll q = runAssign(s, AC, 1, 0, AB);
        printf("O assign %d %lld %lld %lld %lld\n", s, q, assign.iters, assign.writes, assign.ops);
    }
}

// ---------------------------------------------------------------- 작은 이동의 지역 최적에서 300번 시도
static ll W(const Route& r, int u, int v) { return (u < 0 || v < 0) ? 0 : std::abs(r.px[u] - r.px[v]) + std::abs(r.py[u] - r.py[v]); }
// 한 점 옮기기와 구간 뒤집기의 근방을 전부 훑어 개선 이동이 없을 때까지 (이 검사 전용 구현)
static void routeLocalOpt(Route& r) {
    int* p = r.buf[0]; const int n = r.n;
    auto at = [&](int k) { return (k < 0 || k >= n) ? -1 : p[k]; };
    for (bool imp = true; imp;) {
        imp = false;
        for (int a = 0; a < n; ++a) for (int b = a + 1; b < n; ++b) {
            const ll d = W(r, at(a - 1), p[b]) + W(r, p[a], at(b + 1)) - W(r, at(a - 1), p[a]) - W(r, p[b], at(b + 1));
            if (d < 0) { std::reverse(p + a, p + b + 1); imp = true; }
        }
        for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b) {
            if (a == b) continue;
            const int x = p[a];
            ll rem = W(r, at(a - 1), x) + W(r, x, at(a + 1)), add = W(r, at(a - 1), at(a + 1));
            if (a < b) { rem += W(r, p[b], at(b + 1)); add += W(r, p[b], x) + W(r, x, at(b + 1)); }
            else { rem += W(r, at(b - 1), p[b]); add += W(r, at(b - 1), x) + W(r, x, p[b]); }
            if (add - rem < 0) {
                if (a < b) for (int k = a; k < b; ++k) p[k] = p[k + 1]; else for (int k = a; k > b; --k) p[k] = p[k - 1];
                p[b] = x; imp = true;
            }
        }
    }
    r.L[0] = refRoute(r, p, n);
}
static void assignLocalOpt(Assign& a) {
    ll cur = refAssign(a, a.as);
    for (bool imp = true; imp;) {
        imp = false;
        for (int i = 0; i < a.n && !imp; ++i) {
            for (int y = 0; y < a.m && !imp; ++y) {
                if (y == a.as[i] || a.cnt[y] >= a.k) continue;
                const int x = a.as[i];
                a.as[i] = y; const ll v = refAssign(a, a.as);
                if (v < cur) { cur = v; imp = true; a.build(); } else a.as[i] = x;
            }
            for (int j = i + 1; j < a.n && !imp; ++j) {
                if (a.as[i] == a.as[j]) continue;
                std::swap(a.as[i], a.as[j]);
                const ll v = refAssign(a, a.as);
                if (v < cur) { cur = v; imp = true; a.build(); } else std::swap(a.as[i], a.as[j]);
            }
        }
    }
    a.build();
}

static void modeStuck() {
    static int lor[21][RN], loa[21][AN];
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200); routeLocalOpt(route); std::memcpy(lor[s], route.buf[0], sizeof lor[s]);
        printf("lo route %d %lld", s, route.L[0]); for (int i = 0; i < 200; ++i) printf(" %d", lor[s][i]); printf("\n");
        genAssign(assign, s, 120, 8, 18, 1); assignLocalOpt(assign); std::memcpy(loa[s], assign.as, sizeof loa[s]);
        printf("lo assign %d %lld", s, refAssign(assign, assign.as)); for (int i = 0; i < 120; ++i) printf(" %d", loa[s][i]); printf("\n");
    }
    const int rsz[] = {1, 2, 3, 5, 8, 13, 21};
    for (int kind = 0; kind < 4; ++kind) for (int size : rsz) for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200);
        std::memcpy(route.buf[0], lor[s], sizeof lor[s]); route.L[0] = refRoute(route, lor[s], 200);
        hc::Random rng; rng.reset((unsigned)s);
        Cfg c{kind, size, 0, 0, 0};
        int found = 0; const ll start = route.L[0];
        for (int t = 0; t < 300; ++t) {
            route.mark(); route.destroy(rng, c); route.repair(rng, c);
            if (route.cost() < start) ++found;
            route.rollback();
        }
        printf("U route %d %d %d %d\n", kind, size, s, found);
    }
    struct AK { int kind, size; };
    const AK aks[] = {{0, 1}, {0, 2}, {0, 4}, {0, 8}, {0, 15}, {1, 1}, {1, 2}};
    for (const AK& k : aks) for (int rule = 0; rule < 2; ++rule) for (int s = 1; s <= 20; ++s) {
        genAssign(assign, s, 120, 8, 18, 1);
        std::memcpy(assign.as, loa[s], sizeof loa[s]); assign.build();
        hc::Random rng; rng.reset((unsigned)s);
        Cfg c{k.kind, k.size, rule, 0, 0};
        int found = 0; const ll start = refAssign(assign, assign.as);
        for (int t = 0; t < 300; ++t) {
            assign.mark(); assign.destroy(rng, c); assign.repair(rng, c);
            if (assign.cost() < start) ++found;
            assign.rollback();
        }
        printf("U assign %d %d %d %d %d\n", k.kind, k.size, rule, s, found);
    }
}

// ---------------------------------------------------------------- 흔한 실수의 검출
struct TracedRoute : Route { ll minSeen; void keep() { Route::keep(); if (cost() < minSeen) minSeen = cost(); } };
struct TracedAssign : Assign { ll minSeen; void keep() { Assign::keep(); if (cost() < minSeen) minSeen = cost(); } };
static TracedRoute troute;
static TracedAssign tassign;

static void modeDetect() {
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200);
        hc::Random rng; rng.reset((unsigned)s);
        const int a = checkDR(route, rng, Cfg{2, 8, 1, 2, 50}, 400);
        genAssign(assign, s, 120, 8, 18, 0);
        hc::Random rng2; rng2.reset((unsigned)s);
        const int b = checkDR(assign, rng2, Cfg{0, 12, 1, 1, 0}, 400);           // 복사 방식
        genAssign(assign, s, 120, 8, 18, 1);
        hc::Random rng3; rng3.reset((unsigned)s);
        const int c = checkDR(assign, rng3, Cfg{0, 12, 1, 1, 0}, 400);           // 기록 방식
        genAssign(assign, s, 24, 8, 3, 1);                                      // 모든 기계가 가득 찬 입력
        hc::Random rng4; rng4.reset((unsigned)s);
        const int d = checkDR(assign, rng4, Cfg{0, 6, 0, 1, 0}, 400);
        printf("D1 %d %d %d %d %d\n", s, a, b, c, d);
    }
    for (int s = 1; s <= 20; ++s) {                                             // 최고해를 따로 보관하는지
        genRoute(troute, s, 200);
        troute.minSeen = troute.cost();
        hc::Random rng; rng.reset((unsigned)s);
        troute.ops = 0;
        runSmall(troute, rng, 250000);
        troute.minSeen = troute.cost();
        const ll best = runDR(troute, rng, Cfg{2, 8, 0, 2, 1000}, 1000000);
        genAssign(tassign, s, 120, 8, 18, 1);
        tassign.minSeen = tassign.cost();
        hc::Random rng2; rng2.reset((unsigned)s);
        tassign.ops = 0;
        runSmall(tassign, rng2, 100000);
        tassign.minSeen = tassign.cost();
        const ll best2 = runDR(tassign, rng2, Cfg{0, 8, 1, 2, 100}, 400000);
        printf("D2 %d %lld %lld %lld %lld %lld %lld\n", s, best, troute.minSeen, refRoute(troute, troute.bestSol, 200), best2, tassign.minSeen, refAssign(tassign, tassign.bestSol));
    }
    // 비용 기여로 부수는 방법이 같은 해에서 부를 때마다 다른 부분을 고르는지
    genRoute(route, 1, 200);
    hc::Random rng; rng.reset(1);
    route.ops = 0;
    runSmall(route, rng, 100000);
    std::set<std::vector<int>> sets;
    for (int t = 0; t < 200; ++t) {
        route.mark(); route.destroy(rng, Cfg{3, 8, 0, 0, 0});
        std::vector<int> v(route.pool, route.pool + route.np);
        std::sort(v.begin(), v.end());
        sets.insert(v);
        route.rollback();
    }
    printf("D3 %zu\n", sets.size());
}

// 비용 기여로 떼어 내는 방법(3)과 무작위(0)의 결과: 결정적으로 고르는 변형과 비교하려고 변형된 코드에서도 돌린다.
static void modeTour() {
    for (int kind = 0; kind <= 3; kind += 3) for (int s = 1; s <= 20; ++s) {
        const ll r = runRoute(s, Cfg{kind, 8, 0, 0, 0}, RB / 4, RB);
        printf("T %d %d %lld %lld\n", kind, s, r, refRoute(route, route.bestSol, 200));
    }
}

int main(int argc, char** argv) {
    const std::string mode = argc > 1 ? argv[1] : "";
    if (mode == "gen") modeGen();
    else if (mode == "check") modeCheck();
    else if (mode == "identity") modeIdentity();
    else if (mode == "small") modeSmall();
    else if (mode == "expo") modeExpo();
    else if (mode == "hand") modeHand();
    else if (mode == "exp") modeExp();
    else if (mode == "stuck") modeStuck();
    else if (mode == "detect") modeDetect();
    else if (mode == "tour") modeTour();
    else return 1;
    return 0;
}
