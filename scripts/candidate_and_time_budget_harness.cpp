// Harness for the candidate-and-time-budget check. Standard headers are fine here; the lesson code is included below.
// Everything printed is an integer count or an integer cost (operation counts, never wall-clock time), so the numbers
// are the same on every platform. Mutated builds (the check script's injected mistakes) only report "caught or not".
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include "lesson.cpp"

typedef long long ll;
typedef unsigned long long ull;

// ---------------------------------------------------------------- independent references (this check only)
static ll refRoute(const Route& r) {
    ll s = 0;
    for (int k = 0; k + 1 < r.n; ++k) s += std::abs(r.px[r.p[k]] - r.px[r.p[k + 1]]) + std::abs(r.py[r.p[k]] - r.py[r.p[k + 1]]);
    return s;
}
static bool refRouteValid(const Route& r) {
    std::vector<int> v(r.p, r.p + r.n);
    std::sort(v.begin(), v.end());
    for (int i = 0; i < r.n; ++i) if (v[i] != i) return false;
    for (int k = 0; k < r.n; ++k) if (r.pos[r.p[k]] != k) return false;
    return true;
}
static ll refAssign(const Assign& a) {
    std::vector<ll> load(a.m, 0);
    ll c = 0;
    for (int i = 0; i < a.n; ++i) { load[a.as[i]] += a.d[i]; c += a.c[i][a.as[i]]; }
    ll sq = 0;
    for (int j = 0; j < a.m; ++j) sq += load[j] * load[j];
    return sq / 100 + c;
}
static bool refAssignValid(const Assign& a) {
    std::vector<int> cnt(a.m, 0);
    for (int i = 0; i < a.n; ++i) { if (a.as[i] < 0 || a.as[i] >= a.m) return false; ++cnt[a.as[i]]; }
    for (int j = 0; j < a.m; ++j) if (cnt[j] > a.k) return false;
    std::vector<ll> load(a.m, 0);
    for (int i = 0; i < a.n; ++i) load[a.as[i]] += a.d[i];
    ll sq = 0;
    for (int j = 0; j < a.m; ++j) { if (load[j] != a.load[j] || cnt[j] != a.cnt[j]) return false; sq += load[j] * load[j]; }
    return sq == a.sq;
}
static ull fnv(const int* v, int n, ull h = 1469598103934665603ULL) {
    for (int i = 0; i < n; ++i) { h ^= (ull)(unsigned)v[i]; h *= 1099511628211ULL; }
    return h;
}
static int mdist(const Route& r, int u, int v) { return std::abs(r.px[u] - r.px[v]) + std::abs(r.py[u] - r.py[v]); }

// reference delta of reversing [l, r] (explicit edges, written for this check)
static ll refRevDelta(const Route& r, int l, int rr) {
    ll d = 0;
    if (l > 0) d += mdist(r, r.p[l - 1], r.p[rr]) - mdist(r, r.p[l - 1], r.p[l]);
    if (rr < r.n - 1) d += mdist(r, r.p[l], r.p[rr + 1]) - mdist(r, r.p[rr], r.p[rr + 1]);
    return d;
}
// reference k nearest lists (distance, index) by sorting everything (small n only)
static std::vector<int> refList(const Route& r, int u, int k) {
    std::vector<std::pair<int, int>> v;
    for (int x = 0; x < r.n; ++x) if (x != u) v.push_back({mdist(r, u, x), x});
    std::sort(v.begin(), v.end());
    std::vector<int> out;
    for (int i = 0; i < k; ++i) out.push_back(v[i].second);
    return out;
}

static Plan plain(ll limit, int k, int every = 1, int clockCost = 0) { Plan pl; pl.limit = limit; pl.finish = 0; pl.every = every; pl.clockCost = clockCost; pl.kFirst = pl.kLast = k; pl.kFinish = 0; return pl; }

static const int AN_N = 2000, AN_M = 200, AN_K = 14;     // the assignment variant used throughout

// ---------------------------------------------------------------- runners that also report the pieces
static ll buildOps;
static ll startRoute(ull seed, int n, int k, bool grid, int side = 0) {
    genRoute(route, seed, n);
    route.buildCells(side > 0 ? side : defaultSide(n)); route.initSnake();
    if (k > 0) { if (grid) route.buildNbGrid(k); else route.buildNbBrute(k); }
    buildOps = route.ops;
    const ll save = route.ops; const ll start = route.fullCost(); route.ops = save;
    return start;
}
static ll doRoute(ull seed, int n, int k, bool grid, const Plan& pl) {
    const ll start = startRoute(seed, n, k, grid);
    hc::Random rng; rng.reset((unsigned)seed);
    return climbPlan(route, rng, start, pl);
}
static ll startAssign(ull seed, int k) {
    genAssign(assign, seed, AN_N, AN_M, AN_K);
    if (k > 0) assign.buildCand(k);
    buildOps = assign.ops;
    const ll save = assign.ops; const ll start = assign.fullCost(); assign.ops = save;
    return start;
}
static ll doAssign(ull seed, int k, const Plan& pl) {
    const ll start = startAssign(seed, k);
    hc::Random rng; rng.reset((unsigned)seed);
    return climbPlan(assign, rng, start, pl);
}
static void dumpRoute() { for (int k = 0; k < route.n; ++k) printf(" %d", route.p[k]); printf("\n"); }
static void dumpAssign() { for (int k = 0; k < assign.n; ++k) printf(" %d", assign.as[k]); printf("\n"); }

// ---------------------------------------------------------------- gen: generator hashes, start solutions, lists
static ull hashLists(const Route& r, int k) { ull h = 1469598103934665603ULL; for (int u = 0; u < r.n; ++u) h = fnv(r.nb[u], k, h); return h; }

static void modeGen() {
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 2000);
        ull h = fnv(route.px, 2000); h = fnv(route.py, 2000, h);
        route.buildCells(defaultSide(2000)); route.initSnake();
        const ll save = route.ops; const ll c = route.fullCost(); route.ops = save;
        printf("gen route %d %d %llu %lld %lld %llu %d\n", 2000, s, h, c, refRoute(route), fnv(route.p, 2000), route.cs);
        genAssign(assign, s, AN_N, AN_M, AN_K);
        ull g = fnv(assign.d, AN_N);
        for (int i = 0; i < AN_N; ++i) g = fnv(assign.c[i], AN_M, g);
        printf("gen assign %d %llu %lld %lld\n", s, g, assign.fullCost(), refAssign(assign));
    }
    for (int s = 1; s <= 3; ++s) {
        genRoute(route, s, 10000);
        ull h = fnv(route.px, 10000); h = fnv(route.py, 10000, h);
        route.buildCells(defaultSide(10000)); route.initSnake();
        const ll save = route.ops; const ll c = route.fullCost(); route.ops = save;
        printf("gen route %d %d %llu %lld %lld %llu %d\n", 10000, s, h, c, refRoute(route), fnv(route.p, 10000), route.cs);
    }
}

// grid lists == brute-force lists == lists sorted by the reference, exact comparison
static void modeLists() {
    for (int s = 1; s <= 20; ++s) {
        ll startRoute32 = startRoute(s, 2000, 32, true);
        (void)startRoute32;
        const ll gridOps = buildOps;
        static int saved[2000][32];
        std::memcpy(saved, route.nb, sizeof saved);
        const ull hg = hashLists(route, 8);
        // brute force on the same points
        route.ops = 0; route.buildNbBrute(32);
        const ll bruteOps = route.ops;
        int diff = 0;
        for (int u = 0; u < 2000; ++u) if (std::memcmp(saved[u], route.nb[u], sizeof saved[u]) != 0) ++diff;
        int diffRef = 0;
        for (int u = 0; u < 2000; u += 37) { std::vector<int> ref = refList(route, u, 32); for (int r = 0; r < 32; ++r) if (ref[r] != route.nb[u][r]) { ++diffRef; break; } }
        printf("lists %d %d %d %lld %lld %llu\n", s, diff, diffRef, gridOps, bruteOps, hg);
    }
    // k = 8 build costs of the two methods and the cells+snake part, n = 2000
    for (int s = 1; s <= 20; ++s) {
        startRoute(s, 2000, 8, true);
        const ll gridOps = buildOps;
        genRoute(route, s, 2000); route.buildCells(defaultSide(2000)); route.initSnake();
        const ll cellsOps = route.ops;
        route.buildNbBrute(8);
        printf("build 2000 %d %lld %lld %lld\n", s, cellsOps, gridOps, route.ops - cellsOps);
    }
    for (int s = 1; s <= 20; ++s) {
        startRoute(s, 10000, 8, true);
        const ll gridOps = buildOps;
        genRoute(route, s, 10000); route.buildCells(defaultSide(10000)); route.initSnake();
        const ll cellsOps = route.ops;
        printf("build 10000 %d %lld %lld\n", s, cellsOps, gridOps);
    }
    {   // n = 10000, seed 1: brute force against grid, both lists exact
        startRoute(1, 10000, 8, true);
        static int saved[10000][KMAX];
        std::memcpy(saved, route.nb, sizeof saved);
        const ll gridOps = buildOps;
        const int g0 = route.g;
        route.ops = 0; route.buildNbBrute(8);
        int diff = 0;
        for (int u = 0; u < 10000; ++u) if (std::memcmp(saved[u], route.nb[u], 8 * sizeof(int)) != 0) ++diff;
        printf("lists10000 1 %d %lld %lld %d\n", diff, gridOps, route.ops, g0);
    }
    // cell sizes at n = 10000, k = 8: build ops for 20 seeds
    const int sides[] = {5, 10, 14, 30, 60, 125, 250};
    for (int side : sides) for (int s = 1; s <= 20; ++s) {
        startRoute(s, 10000, 8, true, side);
        printf("side %d %d %lld %d\n", side, s, buildOps, route.g);
    }
    // assignment candidate lists against a sort written here
    for (int s = 1; s <= 20; ++s) {
        genAssign(assign, s, AN_N, AN_M, AN_K);
        assign.buildCand(32);
        int diff = 0;
        for (int i = 0; i < AN_N; ++i) {
            std::vector<std::pair<int, int>> v;
            for (int j = 0; j < AN_M; ++j) v.push_back({assign.c[i][j], j});
            std::sort(v.begin(), v.end());
            for (int r = 0; r < 32; ++r) if (v[r].second != assign.cl[i][r]) { ++diff; break; }
        }
        ull h = 1469598103934665603ULL;
        for (int i = 0; i < AN_N; ++i) h = fnv(assign.cl[i], 8, h);
        printf("alists %d %d %llu %lld\n", s, diff, h, assign.ops);
    }
}

// ---------------------------------------------------------------- correctness of delta / apply / cand moves
static void modeCheck() {
    // route: candidate moves make the intended edge, delta == full recomputation, apply/undo restore
    ll bad = 0, tested = 0, invalid = 0, notAdjacent = 0, badAny = 0;
    for (int n : {200, 2000}) for (int s = 1; s <= 5; ++s) {
        startRoute(s, n, 16, true);
        hc::Random rng; rng.reset((unsigned)s);
        for (int t = 0; t < 4000; ++t) {
            Move mv;
            const bool useCand = (t % 4 != 3);
            bool ok;
            int a = 0, r = 0;
            if (useCand) { a = pick(rng, route.n); r = pick(rng, 16); ok = route.cand(a, r, mv); }
            else ok = route.any(rng, mv);
            if (!ok) continue;
            const int u = useCand ? route.p[a] : -1, v = useCand ? route.nb[u][r] : -1;
            const ll before = refRoute(route), d = route.delta(mv);
            if (d != refRevDelta(route, mv.a, mv.b)) ++bad;
            int saved[RN]; std::memcpy(saved, route.p, sizeof saved);
            route.apply(mv);
            if (!refRouteValid(route) || !route.valid()) ++invalid;
            if (refRoute(route) - before != d) ++badAny;
            if (useCand && std::abs(route.pos[u] - route.pos[v]) != 1) ++notAdjacent;
            route.undo(mv);
            if (std::memcmp(saved, route.p, sizeof saved) != 0 || !refRouteValid(route)) ++bad;
            ++tested;
            if (d < 0 || (t & 1)) route.apply(mv);          // walk to other states
        }
    }
    printf("check route %lld %lld %lld %lld %lld\n", tested, bad, invalid, badAny, notAdjacent);
    // assignment
    bad = tested = invalid = 0; ll badCand = 0;
    for (int s = 1; s <= 5; ++s) {
        startAssign(s, 16);
        hc::Random rng; rng.reset((unsigned)s);
        for (int t = 0; t < 6000; ++t) {
            Move mv;
            const bool useCand = (t % 4 != 3);
            bool ok;
            if (useCand) { const int i = pick(rng, AN_N), r = pick(rng, 16); ok = assign.cand(i, r, mv); if (ok && mv.b != assign.cl[i][r]) ++badCand; }
            else ok = assign.any(rng, mv);
            if (!ok) continue;
            const ll before = refAssign(assign), d = assign.delta(mv);
            assign.apply(mv);
            if (!refAssignValid(assign) || !assign.valid()) ++invalid;
            if (refAssign(assign) - before != d) ++bad;
            assign.undo(mv);
            if (refAssign(assign) != before || !refAssignValid(assign)) ++bad;
            ++tested;
            if (d < 0 || (t & 1)) assign.apply(mv);
        }
    }
    printf("check assign %lld %lld %lld %lld\n", tested, bad, invalid, badCand);
    // full runs: tracked cost == reference, solution valid, ops stay within limit + overshoot bound
    for (int s = 1; s <= 3; ++s) {
        Plan pl = plain(300000, 8);
        pl.finish = 30000; pl.kFinish = 16; pl.every = 32; pl.clockCost = 5; pl.kFirst = 16; pl.kLast = 4;
        const ll c = doRoute(s, 2000, 16, true, pl);
        printf("run route %d %lld %lld %d %d\n", s, c, refRoute(route), refRouteValid(route), (int)(route.ops >= pl.limit));
        const ll q = doAssign(s, 16, pl);
        printf("run assign %d %lld %lld %d %d\n", s, q, refAssign(assign), refAssignValid(assign), (int)(assign.ops >= pl.limit));
    }
    // the clock-check mistake guard: the loop never stops later than every * (largest one-iteration cost) after the limit
    ll worst = 0;
    for (int s = 1; s <= 5; ++s) {
        const int every = 64;
        Plan pl = plain(500000, 8, every, 0);
        doRoute(s, 2000, 8, true, pl);
        worst = std::max(worst, route.ops - pl.limit);
    }
    printf("overshoot route %lld\n", worst);
}

// ---------------------------------------------------------------- the experiments
static void modeExp() {
    const int ks[] = {0, 2, 4, 8, 16, 32};
    // T2: candidate list size at the same operation budget (a tight and an ample budget per size)
    const ll routeBudget[2][2] = {{400000, 2000000}, {3000000, 12000000}};
    const int routeN[2] = {2000, 10000};
    for (int bi = 0; bi < 2; ++bi) for (int bj = 0; bj < 2; ++bj) for (int k : ks) for (int s = 1; s <= 20; ++s) {
        const ll start = startRoute(s, routeN[bi], k, true);
        const ll built = buildOps;
        hc::Random rng; rng.reset((unsigned)s);
        const ll c = climbPlan(route, rng, start, plain(routeBudget[bi][bj], k));
        printf("T2 route %d %lld %d %d %lld %lld %lld %lld %lld %lld %lld %lld\n", routeN[bi], routeBudget[bi][bj], k, s, c, route.props, route.ops, route.writes, built, start, refRoute(route), (ll)route.reads);
        if (bj == 1 && (k == 0 || k == 8)) { printf("final route %d %d %d", routeN[bi], k, s); dumpRoute(); }
    }
    {   // list built by brute force at n = 2000: the build alone nearly or fully uses the budget
        for (int s = 1; s <= 20; ++s) {
            const ll start = startRoute(s, 2000, 8, false);
            const ll built = buildOps;
            hc::Random rng; rng.reset((unsigned)s);
            const ll c = climbPlan(route, rng, start, plain(2000000, 8));
            printf("T2b route 2000 8 %d %lld %lld %lld %lld %lld\n", s, c, route.props, route.ops, built, start);
        }
    }
    for (int k : ks) for (int s = 1; s <= 20; ++s) {
        const ll start = startAssign(s, k);
        const ll built = buildOps;
        hc::Random rng; rng.reset((unsigned)s);
        const ll c = climbPlan(assign, rng, start, plain(2000000, k));
        printf("T2 assign %d %lld %d %d %lld %lld %lld %lld %lld %lld %lld %lld\n", AN_N, 2000000LL, k, s, c, assign.props, assign.ops, assign.writes, built, start, refAssign(assign), (ll)assign.reads);
        if (k == 0 || k == 4) { printf("final assign %d %d %d", AN_N, k, s); dumpAssign(); }
    }
    {   // small budget: the lists cost more than the budget
        for (int k : {0, 4}) for (int s = 1; s <= 20; ++s) {
            const ll start = startAssign(s, k);
            hc::Random rng; rng.reset((unsigned)s);
            const ll c = climbPlan(assign, rng, start, plain(1000000, k));
            printf("T2c assign %d %d %d %lld %lld %lld\n", AN_N, k, s, c, assign.props, assign.ops);
        }
    }
    // T4: stages and schedules by remaining budget, lists of 16
    struct Conf { int first, last, fin; } confs[5] = {{8, 8, 0}, {16, 16, 0}, {16, 4, 0}, {4, 16, 0}, {8, 8, 1}};
    for (int ci = 0; ci < 5; ++ci) for (int s = 1; s <= 20; ++s) {
        Plan pl = plain(2000000, 8); pl.kFirst = confs[ci].first; pl.kLast = confs[ci].last;
        if (confs[ci].fin) { pl.finish = 200000; pl.kFinish = 16; }
        const ll c = doRoute(s, 2000, 16, true, pl);
        printf("T4 route %d %d %lld %lld %lld\n", ci, s, c, route.props, route.ops);
        Plan pa = plain(2000000, 8); pa.kFirst = confs[ci].first; pa.kLast = confs[ci].last;
        if (confs[ci].fin) { pa.finish = 200000; pa.kFinish = 16; }
        const ll q = doAssign(s, 16, pa);
        printf("T4 assign %d %d %lld %lld %lld\n", ci, s, q, assign.props, assign.ops);
    }
    // T5: doubling the budget
    const ll b2000[] = {250000, 500000, 1000000, 2000000, 4000000, 8000000};
    const ll b10000[] = {1500000, 3000000, 6000000, 12000000, 24000000};
    const ll bassign[] = {1000000, 2000000, 4000000, 8000000};
    for (ll b : b2000) for (int s = 1; s <= 20; ++s) { const ll c = doRoute(s, 2000, 8, true, plain(b, 8)); printf("T5 route 2000 %lld %d %lld %lld\n", b, s, c, route.props); }
    for (ll b : b10000) for (int s = 1; s <= 20; ++s) { const ll c = doRoute(s, 10000, 8, true, plain(b, 8)); printf("T5 route 10000 %lld %d %lld %lld\n", b, s, c, route.props); }
    for (ll b : bassign) for (int s = 1; s <= 20; ++s) { const ll c = doAssign(s, 4, plain(b, 4)); printf("T5 assign 2000 %lld %d %lld %lld\n", b, s, c, assign.props); }
    // T6: how often to read the clock; one read costs 40 operations in this model
    const int everys[] = {1, 4, 16, 64, 256, 1024, 4096};
    for (int e : everys) for (int s = 1; s <= 20; ++s) {
        const ll c = doRoute(s, 2000, 8, true, plain(2000000, 8, e, 40));
        printf("T6 route %d %d %lld %lld %lld %lld\n", e, s, c, (ll)route.reads, route.ops, route.props);
        const ll q = doAssign(s, 4, plain(2000000, 4, e, 40));
        printf("T6 assign %d %d %lld %lld %lld %lld\n", e, s, q, (ll)assign.reads, assign.ops, assign.props);
    }
}

// ---------------------------------------------------------------- misses: what the best full-neighbourhood move is, and whether the candidates contain it
static unsigned char rk[2000][2000];

static void modeMiss() {
    const int kList[] = {2, 4, 8, 16, 32};
    for (int state = 0; state < 2; ++state) for (int s = 1; s <= 20; ++s) {
        startRoute(s, 2000, 32, true);
        hc::Random rng; rng.reset((unsigned)s);
        ll cost = route.fullCost();
        if (state == 1) {                                   // run the 8-candidate sweeps until one finds nothing
            for (int guard = 0; guard < 400; ++guard) {
                const ll c2 = sweepAll(route, cost, 8, (ll)4e18);
                if (c2 == cost) break;
                cost = c2;
            }
        }
        std::memset(rk, 255, sizeof rk);
        for (int u = 0; u < 2000; ++u) for (int r = 0; r < 32; ++r) rk[u][route.nb[u][r]] = (unsigned char)r;
        ll bestAll = 0, bestK[5] = {0, 0, 0, 0, 0};
        ll improving = 0, improvingIn8 = 0;
        for (int l = 0; l < 1999; ++l) for (int r = l + 1; r < 2000; ++r) {
            const ll d = refRevDelta(route, l, r);
            int rank = 255;
            if (l > 0) rank = std::min<int>(rank, rk[route.p[l - 1]][route.p[r]]);
            if (r < 1999) rank = std::min<int>(rank, rk[route.p[r + 1]][route.p[l]]);
            if (d < bestAll) bestAll = d;
            for (int q = 0; q < 5; ++q) if (rank < kList[q] && d < bestK[q]) bestK[q] = d;
            if (d < 0) { ++improving; if (rank < 8) ++improvingIn8; }
        }
        printf("miss route %d %d %lld %lld %lld %lld %lld %lld %lld %lld %lld\n", state, s, bestAll, bestK[0], bestK[1], bestK[2], bestK[3], bestK[4], improving, improvingIn8, cost);
    }
    for (int state = 0; state < 2; ++state) for (int s = 1; s <= 20; ++s) {
        startAssign(s, 32);
        hc::Random rng; rng.reset((unsigned)s);
        ll cost = assign.fullCost();
        if (state == 1) {
            for (int guard = 0; guard < 400; ++guard) {
                const ll c2 = sweepAll(assign, cost, 8, (ll)4e18);
                if (c2 == cost) break;
                cost = c2;
            }
        }
        ll bestAll = 0, bestK[5] = {0, 0, 0, 0, 0};
        ll improving = 0, improvingIn8 = 0;
        for (int i = 0; i < AN_N; ++i) for (int y = 0; y < AN_M; ++y) {
            if (y == assign.as[i] || assign.cnt[y] >= assign.k) continue;
            Move mv; mv.kind = 0; mv.a = i; mv.b = y; mv.old = assign.as[i];
            const ll d = assign.delta(mv);
            int rank = 255;
            for (int r = 0; r < 32; ++r) if (assign.cl[i][r] == y) { rank = r; break; }
            if (d < bestAll) bestAll = d;
            for (int q = 0; q < 5; ++q) if (rank < kList[q] && d < bestK[q]) bestK[q] = d;
            if (d < 0) { ++improving; if (rank < 8) ++improvingIn8; }
        }
        printf("miss assign %d %d %lld %lld %lld %lld %lld %lld %lld %lld %lld\n", state, s, bestAll, bestK[0], bestK[1], bestK[2], bestK[3], bestK[4], improving, improvingIn8, cost);
    }
}

// ---------------------------------------------------------------- the hand examples
static const int HP[8][2] = {{90, 430}, {390, 780}, {760, 10}, {770, 870}, {910, 440}, {90, 400}, {460, 400}, {620, 900}};

static void modeHand() {
    route.n = 8;
    for (int i = 0; i < 8; ++i) { route.px[i] = HP[i][0]; route.py[i] = HP[i][1]; }
    route.ops = route.writes = route.props = route.reads = 0;
    route.buildCells(250); route.initSnake();
    printf("hand route snake %lld", route.ops);
    for (int k = 0; k < 8; ++k) printf(" %d", route.p[k]);
    printf(" %lld\n", route.fullCost());
    const ll opsBefore = route.ops;
    route.buildNbGrid(3);
    const ll gridOps = route.ops - opsBefore;
    int gridLists[8][3];
    for (int u = 0; u < 8; ++u) for (int r = 0; r < 3; ++r) gridLists[u][r] = route.nb[u][r];
    const ll before2 = route.ops;
    route.buildNbBrute(3);
    const ll bruteOps = route.ops - before2;
    int diff = 0;
    for (int u = 0; u < 8; ++u) for (int r = 0; r < 3; ++r) if (gridLists[u][r] != route.nb[u][r]) ++diff;
    printf("hand lists %lld %lld %d\n", gridOps, bruteOps, diff);
    for (int u = 0; u < 8; ++u) printf("hand nb %d %d %d %d\n", u, route.nb[u][0], route.nb[u][1], route.nb[u][2]);
    // every reversal: delta, and whether the generator can produce it with k = 2 and k = 3
    for (int l = 0; l < 7; ++l) for (int r = l + 1; r < 8; ++r) {
        int rank = 255;
        for (int a = 0; a < 8; ++a) for (int q = 0; q < 3; ++q) {
            Move mv;
            if (route.cand(a, q, mv) && mv.a == l && mv.b == r) rank = std::min(rank, q);
        }
        Move m; m.kind = 2; m.a = l; m.b = r; m.old = 0;
        printf("hand rev %d %d %lld %d\n", l, r, route.delta(m), rank);
    }
}

// ---------------------------------------------------------------- mistakes: only caught / not caught is reported

// a stand-in problem that only records which candidate ranks the loop asks for early and late (checks the remaining-budget schedule)
struct Spy {
    ll ops, props, reads, limit; int maxEarly, maxLate;
    int items() { return 1; }
    bool cand(int, int r, Move& mv) {
        if (ops < limit / 20) maxEarly = std::max(maxEarly, r);
        if (ops >= limit - limit / 20) maxLate = std::max(maxLate, r);
        mv.kind = 0; mv.a = mv.b = mv.old = 0;
        return true;
    }
    bool any(hc::Random&, Move&) { return false; }
    ll delta(const Move&) { return 0; }
    void apply(const Move&) {}
};

static void modeDetect() {
    int gridWrong = 0, posWrong = 0;
    for (int s = 1; s <= 20; ++s) {
        startRoute(s, 2000, 8, true);
        static int saved[2000][8];
        for (int u = 0; u < 2000; ++u) for (int r = 0; r < 8; ++r) saved[u][r] = route.nb[u][r];
        route.buildNbBrute(8);
        bool diff = false;
        for (int u = 0; u < 2000 && !diff; ++u) for (int r = 0; r < 8; ++r) if (saved[u][r] != route.nb[u][r]) { diff = true; break; }
        if (diff) ++gridWrong;
        startRoute(s, 2000, 8, true);
        hc::Random rng; rng.reset((unsigned)s);
        ll cost = route.fullCost();
        climbPlan(route, rng, cost, plain(300000, 8));
        if (!route.valid()) ++posWrong;
    }
    printf("D %d %d\n", gridWrong, posWrong);
    Spy spy; spy.ops = spy.props = spy.reads = 0; spy.limit = 100000; spy.maxEarly = spy.maxLate = 0;
    Plan pl = plain(100000, 8); pl.kFirst = 16; pl.kLast = 4;
    hc::Random rng; rng.reset(7);
    climbPlan(spy, rng, 0, pl);
    printf("S %d %d\n", spy.maxEarly + 1, spy.maxLate + 1);
}

// ---------------------------------------------------------------- timing code smoke test: runs, prints nothing about time
static void modeTiming() {
    // time one fixed operation budget; the check script only needs this to compile and run (the number is machine dependent)
    const auto t0 = std::chrono::steady_clock::now();
    doRoute(1, 2000, 8, true, plain(200000, 8));
    const auto t1 = std::chrono::steady_clock::now();
    const double ns = (double)std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count();
    printf("timing ok %d\n", (int)(ns >= 0 && route.ops >= 200000));
}

int main(int argc, char** argv) {
    const std::string mode = argc > 1 ? argv[1] : "";
    if (mode == "gen") modeGen();
    else if (mode == "lists") modeLists();
    else if (mode == "check") modeCheck();
    else if (mode == "exp") modeExp();
    else if (mode == "miss") modeMiss();
    else if (mode == "hand") modeHand();
    else if (mode == "detect") modeDetect();
    else if (mode == "timing") modeTiming();
    else { fprintf(stderr, "unknown mode\n"); return 2; }
    return 0;
}
