// Harness for the experiments-and-tuning check. Standard headers are fine here; the lesson code is included below.
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include "lesson.cpp"

typedef long long ll;
typedef unsigned long long ull;

static const Cfg HOT = {1, 1, 0};        // 거의 0도
static const Cfg C0 = {128, 128, 0};     // 일정 온도
static const Cfg C1 = {256, 32, 0};      // 격자에서 고른 설정
static const ll B_ROUTE = 300000, B_ASSIGN = 100000;

static ull fnv(const int* v, int n, ull h = 1469598103934665603ULL) {
    for (int i = 0; i < n; ++i) { h ^= (ull)(unsigned)v[i]; h *= 1099511628211ULL; }
    return h;
}
static ll refRoute(const Route& r) {
    ll s = 0;
    for (int k = 0; k + 1 < r.n; ++k) s += std::abs(r.px[r.p[k]] - r.px[r.p[k + 1]]) + std::abs(r.py[r.p[k]] - r.py[r.p[k + 1]]);
    return s;
}
static ll refAssign(const Assign& a) {
    std::vector<ll> load(a.m, 0);
    ll c = 0;
    for (int i = 0; i < a.n; ++i) { load[a.as[i]] += a.d[i]; c += a.c[i][a.as[i]]; }
    ll sq = 0;
    for (int j = 0; j < a.m; ++j) sq += load[j] * load[j];
    return sq / 100 + c;
}
static bool routeValid(const Route& r) {
    std::vector<int> v(r.p, r.p + r.n);
    std::sort(v.begin(), v.end());
    for (int i = 0; i < r.n; ++i) if (v[i] != i) return false;
    return true;
}
static bool assignValid(const Assign& a) {
    std::vector<int> cnt(a.m, 0);
    for (int i = 0; i < a.n; ++i) { if (a.as[i] < 0 || a.as[i] >= a.m) return false; ++cnt[a.as[i]]; }
    for (int j = 0; j < a.m; ++j) if (cnt[j] > a.k) return false;
    return true;
}

static ll runCase(int cs, const Cfg& c, int seed) {   // x7 cases
    switch (cs) {
        case 0: return runRoute(c, seed, seed, 200, 0, B_ROUTE);       // 확인 시드 21..40
        case 1: return runRoute(c, seed, seed, 100, 0, B_ROUTE);
        case 2: return runRoute(c, seed, seed, 400, 0, B_ROUTE);
        case 3: return runRoute(c, seed, seed, 200, 1, B_ROUTE);
        case 4: return runAssign(c, seed, seed, B_ASSIGN);
        case 5: return runRoute(c, seed, seed, 200, 0, 100000);
        default: return runRoute(c, seed, seed, 200, 0, 1000000);
    }
}

int main(int argc, char** argv) {
    if (argc < 2) return 1;
    const std::string mode = argv[1];
    if (mode == "gen") {
        for (int s = 1; s <= 20; ++s) {
            runRoute(C0, s, s, 200, 0, 0);
            printf("gen route0 %d %llu %lld %lld %llu\n", s, fnv(route.py, 200, fnv(route.px, 200)), route.fullCost(), refRoute(route), lastPrint);
        }
        for (int s = 1; s <= 5; ++s) {
            genRoute(route, s, 200, 1);
            printf("gen route1 %d %llu %lld %lld %llu\n", s, fnv(route.py, 200, fnv(route.px, 200)), route.fullCost(), refRoute(route), 0ULL);
        }
        for (int s = 1; s <= 20; ++s) {
            runAssign(C0, s, s, 0);
            ull h = fnv(assign.d, 120);
            for (int i = 0; i < 120; ++i) h = fnv(assign.c[i], 8, h);
            printf("gen assign %d %llu %lld %lld %llu\n", s, h, assign.fullCost(), refAssign(assign), lastPrint);
        }
    } else if (mode == "trace") {
        // 본문의 anneal과 같은 순서로 도는 검사용 루프: 매 단계 delta를 전체 재계산과 대조하고 유효성을 확인한다.
        buildAcc();
        for (int frame = 0; frame < 2; ++frame) {
            for (int s = 1; s <= 4; ++s) {
                const Cfg cfgs[3] = {C0, C1, {64, 64, 50}};
                for (int ci = 0; ci < 3; ++ci) {
                    const Cfg cfg = cfgs[ci];
                    const ll budget = 3000;
                    ll lessonBest, checkBest, mism = 0;
                    if (frame == 0) {
                        lessonBest = runRoute(cfg, s, s, 60, 0, budget);
                        genRoute(route, s, 60, 0);
                        hc::Random rng; rng.reset(s);
                        ll cost = route.fullCost(); checkBest = cost;
                        Schedule sc; sc.init((ll)cfg.t0 * TS / 8, std::max<ll>((ll)cfg.t1 * TS / 8, 1), budget);
                        for (ll e = 0; e < budget; ++e) {
                            const ll t = sc.at(e);
                            Move mv;
                            if (!route.propose(rng, mv, cfg)) continue;
                            const ll before = refRoute(route);
                            const ll d = route.delta(mv);
                            if (d > 0 && !acceptWorse(d, t, rng)) continue;
                            route.apply(mv); cost += d;
                            if (refRoute(route) - before != d || !routeValid(route)) ++mism;
                            if (cost < checkBest) checkBest = cost;
                        }
                        if (cost != refRoute(route)) ++mism;
                    } else {
                        lessonBest = runAssign(cfg, s, s, budget);
                        genAssign(assign, s, 120, 8, 18);
                        hc::Random rng; rng.reset(s);
                        ll cost = assign.fullCost(); checkBest = cost;
                        Schedule sc; sc.init((ll)cfg.t0 * TS / 8, std::max<ll>((ll)cfg.t1 * TS / 8, 1), budget);
                        for (ll e = 0; e < budget; ++e) {
                            const ll t = sc.at(e);
                            Move mv;
                            if (!assign.propose(rng, mv, cfg)) continue;
                            const ll before = refAssign(assign);
                            const ll d = assign.delta(mv);
                            if (d > 0 && !acceptWorse(d, t, rng)) continue;
                            assign.apply(mv); cost += d;
                            if (refAssign(assign) - before != d || !assignValid(assign)) ++mism;
                            if (cost < checkBest) checkBest = cost;
                        }
                        if (cost != refAssign(assign)) ++mism;
                    }
                    printf("trace %d %d %d %lld %lld %lld\n", frame, s, ci, lessonBest, checkBest, mism);
                }
            }
        }
        // 짧은 실행의 최고 비용(독립 파이썬 구현과 대조): 순서 틀 n=40, 배정 틀 기본 크기, 예산 2000
        for (int s = 1; s <= 3; ++s) {
            printf("short route %d %lld\n", s, runRoute(C1, s, s, 40, 0, 2000));
            printf("short assign %d %lld\n", s, runAssign(C1, s, s, 2000));
        }
    } else if (mode == "stats") {
        // 통계 함수의 값. 파이썬이 math.comb와 분수로 다시 계산한다.
        for (int n = 1; n <= 40; ++n) {
            printf("tail %d", n);
            for (int k = 0; k <= n; ++k) printf(" %llu", tailCount(n, k));
            printf("\n");
        }
        const ll dens[] = {20, 40, 100, 200, 400, 1000};
        for (int n = 5; n <= 40; ++n) {
            printf("need %d", n);
            for (ll den : dens) printf(" %d", needWins(n, den));
            printf("\n");
        }
        hc::Random rng; rng.reset(7);
        for (int rep = 0; rep < 5; ++rep) {
            const int n = 7 + rep * 6;
            ll a[MAXS], b[MAXS];
            for (int i = 0; i < n; ++i) { a[i] = pick(rng, 10); b[i] = pick(rng, 10); }
            const Tally t = paired(a, b, n);
            printf("pair %d %d %d %d", n, t.win, t.lose, t.tie);
            printf(" %lld %lld %lld |", medianOf(a, n), q1Of(a, n), q3Of(a, n));
            for (int i = 0; i < n; ++i) printf(" %lld %lld", a[i], b[i]);
            printf("\n");
        }
        const ll ka[4] = {1, 2, 3, 4}, kb[4] = {2, 2, 1, 0};
        const Tally kt = paired(ka, kb, 4);
        printf("known %d %d %d\n", kt.win, kt.lose, kt.tie);
        printf("known2 %llu %d %d %d\n", tailCount(20, 15), needWins(20, 20), needWins(20, 40), needWins(20, 20 * 46));
        ull pa[3] = {1, 2, 3}, pb[3] = {1, 2, 4};
        printf("known3 %d %d %d %d\n", samePrints(pa, pa, 3), samePrints(pa, pb, 3), disjoint(1, 20, 21, 20), disjoint(1, 20, 20, 20));
    } else if (mode == "x1") {
        const int bud[4] = {30000, 100000, 300000, 1000000};
        const Cfg cf[3] = {HOT, C0, C1};
        for (int ci = 0; ci < 3; ++ci) for (int b = 0; b < 4; ++b) for (int s = 1; s <= 20; ++s)
            printf("x1 route %d %d %d %lld\n", ci, bud[b], s, runRoute(cf[ci], s, s, 200, 0, bud[b]));
        const int ab[2] = {10000, 100000};
        for (int ci = 0; ci < 2; ++ci) for (int b = 0; b < 2; ++b) for (int s = 1; s <= 20; ++s) {
            const ll c = runAssign(cf[ci * 2], s, s, ab[b]);
            printf("x1 assign %d %d %d %lld %lld %lld\n", ci * 2, ab[b], s, c, assign.props, assign.blocked);
        }
    } else if (mode == "x2") {
        for (int s = 1; s <= 20; ++s) {
            const ll c = runRoute(C0, s, s, 200, 0, B_ROUTE);
            printf("x2 A %d %lld %llu\n", s, c, lastPrint);
        }
        for (int s = 1; s <= 100; ++s) {
            const ll c = runRoute(C1, s, s, 200, 0, B_ROUTE);
            printf("x2 B %d %lld %llu\n", s, c, lastPrint);
        }
        for (int in = 1; in <= 3; ++in) for (int s = 1; s <= 20; ++s)
            printf("x2 S %d %d %lld\n", in, s, runRoute(C1, in, s, 200, 0, B_ROUTE));
    } else if (mode == "x3") {
        for (int j = 0; j <= 40; ++j) for (int s = 1; s <= 40; ++s)
            printf("x3 %d %d %lld\n", j, s, runRoute(C1, s, s + 1000 * j, 200, 0, B_ROUTE));
    } else if (mode == "x5") {
        const Cfg list[] = {{128,128,0},{256,128,0},{64,64,0},{128,64,0},{128,128,25},{128,32,0},{512,128,0},
                            {256,64,0},{256,32,0},{256,16,0},{512,32,0},{512,16,0}};
        for (const Cfg& c : list) for (int s = 1; s <= 40; ++s)
            printf("x5 cfg %d %d %d %d %lld\n", c.t0, c.t1, c.ins, s, runRoute(c, s, s, 200, 0, B_ROUTE));
        // 걸음 두 가지: need 15(엄격)와 need 11(이긴 시드가 더 많으면)
        for (int need = 11; need <= 15; need += 4) {
            Cfg cur = C0;
            for (int step = 0; step < 8; ++step) {
                const Cfg before = cur;
                int bw;
                const bool moved = stepOnce([&](const Cfg& c, int s) { return runRoute(c, s, s, 200, 0, B_ROUTE); }, cur, 1, 20, need, bw);
                printf("x5 step %d %d %d %d %d %d %d %d %d %d\n", need, step, before.t0, before.t1, before.ins, bw, moved, cur.t0, cur.t1, cur.ins);
                if (!moved) break;
            }
            printf("x5 end %d %d %d %d\n", need, cur.t0, cur.t1, cur.ins);
            for (int s = 1; s <= 40; ++s) printf("x5 endcost %d %d %lld\n", need, s, runRoute(cur, s, s, 200, 0, B_ROUTE));
        }
    } else if (mode == "x6") {
        int ids[G * G];
        const int cnt = validLattice(ids);
        for (int a = 0; a < cnt; ++a) {
            Cfg c; latticeCfg(ids[a], c);
            printf("x6 %d %d", c.t0, c.t1);
            for (int s = 1; s <= 40; ++s) printf(" %lld", runRoute(c, s, s, 200, 0, B_ROUTE));
            printf("\n");
        }
        // 무작위 탐색의 뽑기: 반복 r = 0..39, 시드 r + 1, 격자 점 9개
        for (int r = 0; r < 40; ++r) {
            int v[G * G];
            const int n = validLattice(v);
            hc::Random rng; rng.reset(r + 1);
            drawWithoutRepeat(rng, v, n, 9);
            printf("x6draw %d", r);
            for (int i = 0; i < 9; ++i) printf(" %d", v[i]);
            printf("\n");
        }
    } else if (mode == "x7") {
        const Cfg cf[3] = {C0, C1, HOT};
        for (int cs = 0; cs < 7; ++cs) for (int ci = 0; ci < 3; ++ci) for (int s = 1; s <= 20; ++s)
            printf("x7 %d %d %d %lld\n", cs, ci, s, runCase(cs, cf[ci], cs == 0 ? s + 20 : s));
    } else if (mode == "smoke") {
        // 짧은 예산으로 튜닝 코드를 한 번 돌려 본다(새니타이저 빌드용).
        Cfg cur = C0; int bw;
        for (int i = 0; i < 3; ++i)
            stepOnce([&](const Cfg& c, int s) { return runRoute(c, s, s, 30, 0, 800); }, cur, 1, 5, 3, bw);
        int v[G * G];
        const int n = validLattice(v);
        hc::Random rng; rng.reset(3);
        drawWithoutRepeat(rng, v, n, 9);
        bool seen[G * G] = {false};
        for (int i = 0; i < n; ++i) { if (seen[v[i]]) return 2; seen[v[i]] = true; }
        printf("smoke %d %d %d %d %d\n", cur.t0, cur.t1, cur.ins, bw, n);
    } else if (mode == "mut") {
        // 실수를 넣은 빌드에서도 안전하게 도는 known-answer 검사만 출력한다.
        const ll a[4] = {1, 2, 3, 4}, b[4] = {2, 2, 1, 0};
        const Tally t = paired(a, b, 4);
        ull pa[3] = {1, 2, 3}, pb[3] = {1, 2, 4};
        printf("mut %d %d %d %llu %d %d %d %d %d %d\n", t.win, t.lose, t.tie, tailCount(20, 15), needWins(20, 20), needWins(20, 40), needWins(20, 920),
               samePrints(pa, pb, 3), disjoint(1, 20, 21, 20), disjoint(1, 20, 20, 20));
    }
    return 0;
}
