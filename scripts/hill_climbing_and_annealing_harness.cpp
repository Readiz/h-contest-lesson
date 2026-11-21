// Harness for the hill-climbing-and-annealing check. Standard headers are fine here; the lesson code is included below.
#include <algorithm>
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
static ll refAssign(const Assign& a) {
    std::vector<ll> load(a.m, 0);
    ll c = 0;
    for (int i = 0; i < a.n; ++i) { load[a.as[i]] += a.d[i]; c += a.c[i][a.as[i]]; }
    ll sq = 0;
    for (int j = 0; j < a.m; ++j) sq += load[j] * load[j];
    return sq / 100 + c;
}
static bool refRouteValid(const Route& r) {
    std::vector<int> v(r.p, r.p + r.n);
    std::sort(v.begin(), v.end());
    for (int i = 0; i < r.n; ++i) if (v[i] != i) return false;
    return true;
}
static bool refAssignValid(const Assign& a) {
    std::vector<int> cnt(a.m, 0);
    for (int i = 0; i < a.n; ++i) { if (a.as[i] < 0 || a.as[i] >= a.m) return false; ++cnt[a.as[i]]; }
    for (int j = 0; j < a.m; ++j) if (cnt[j] > a.k) return false;
    return true;
}
static bool cachesOk(const Assign& a) {
    std::vector<ll> load(a.m, 0), cnt(a.m, 0);
    for (int i = 0; i < a.n; ++i) { load[a.as[i]] += a.d[i]; ++cnt[a.as[i]]; }
    ll sq = 0;
    for (int j = 0; j < a.m; ++j) { if (load[j] != a.load[j] || cnt[j] != a.cnt[j]) return false; sq += load[j] * load[j]; }
    return sq == a.sq;
}
static ull fnv(const int* v, int n, ull h = 1469598103934665603ULL) {
    for (int i = 0; i < n; ++i) { h ^= (ull)(unsigned)v[i]; h *= 1099511628211ULL; }
    return h;
}
static ll refCost(const Route& r) { return refRoute(r); }
static ll refCost(const Assign& a) { return refAssign(a); }
static bool refValid(const Route& r) { return refRouteValid(r); }
static bool refValid(const Assign& a) { return refAssignValid(a) && cachesOk(a); }
static int* solOf(Route& r) { return r.p; }
static int* solOf(Assign& a) { return a.as; }
static int lenOf(const Route& r) { return r.n; }
static int lenOf(const Assign& a) { return a.n; }

// Counting wrappers: the lesson loops call p.apply, so the derived class sees every applied move.
struct CRoute : Route { ll applies; void apply(const Move& mv) { ++applies; Route::apply(mv); } };
struct CAssign : Assign { ll applies; void apply(const Move& mv) { ++applies; Assign::apply(mv); } };
static CRoute croute;
static CAssign cassign;

// every valid move of the current solution, enumerated here (not with the lesson's nthMove)
static void allMoves(const Route& r, std::vector<Move>& out) {
    out.clear();
    Move m; m.kind = 0; m.old = 0;
    for (int a = 0; a < r.n; ++a) for (int b = a + 1; b < r.n; ++b) { m.a = a; m.b = b; out.push_back(m); }
}
static void allMoves(const Assign& s, std::vector<Move>& out) {
    out.clear();
    Move m;
    for (int i = 0; i < s.n; ++i) {
        for (int to = 0; to < s.m; ++to) if (to != s.as[i] && s.cnt[to] < s.k) { m.kind = 0; m.a = i; m.b = to; m.old = s.as[i]; out.push_back(m); }
        for (int j = i + 1; j < s.n; ++j) if (s.as[i] != s.as[j]) { m.kind = 1; m.a = i; m.b = j; m.old = 0; out.push_back(m); }
    }
}
// number of moves that improve, found by applying each one and recomputing the cost with the reference
template <class P>
static int improvingByReference(P& p) {
    std::vector<Move> mv; allMoves(p, mv);
    const ll before = refCost(p);
    int c = 0;
    for (const Move& m : mv) { p.apply(m); if (refCost(p) < before) ++c; p.undo(m); }
    return c;
}
template <class P>
static void walk(P& p, hc::Random& rng, int steps) {
    for (int t = 0; t < steps; ++t) { Move mv; if (propose(p, rng, mv)) p.apply(mv); }
}

// ---------------------------------------------------------------- modes
static void modeGen() {
    for (int s = 1; s <= 120; ++s) {
        if (s > 20 && s < 101) continue;
        genRoute(route, s, 200);
        ull h = fnv(route.px, 200); h = fnv(route.py, 200, h);
        printf("gen route %d %llu %lld %lld\n", s, h, route.fullCost(), refRoute(route));
        genAssign(assign, s, 120, 8, 18);
        ull g = fnv(assign.d, 120);
        for (int i = 0; i < 120; ++i) g = fnv(assign.c[i], 8, g);
        printf("gen assign %d %llu %lld %lld\n", s, g, assign.fullCost(), refAssign(assign));
    }
}

// delta == reference difference for every move on small inputs; undo restores; the move numbering covers exactly the valid moves.
static void modeDiff() {
    ll moves = 0, bad = 0, invalid = 0, cacheBad = 0, numberBad = 0;
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 8);
        hc::Random rng; rng.reset((unsigned)s);
        for (int state = 0; state < 12; ++state) {
            if (state) walk(route, rng, 3);
            std::vector<Move> mv; allMoves(route, mv);
            int valid = 0;
            for (ll idx = 0; idx < moveCount(route); ++idx) { Move m; if (nthMove(route, idx, m)) ++valid; }
            if (valid != (int)mv.size()) ++numberBad;
            for (const Move& m : mv) {
                int saved[RN]; std::memcpy(saved, route.p, sizeof saved);
                const ll before = refRoute(route), d = route.delta(m);
                route.apply(m);
                if (!refRouteValid(route) || !route.valid()) ++invalid;
                if (refRoute(route) - before != d) ++bad;
                route.undo(m);
                if (std::memcmp(saved, route.p, sizeof saved) != 0) ++bad;
                ++moves;
            }
        }
    }
    printf("diff route %lld %lld %lld %lld\n", moves, bad, invalid, numberBad);
    moves = bad = invalid = numberBad = 0;
    for (int s = 1; s <= 20; ++s) {
        genAssign(assign, s, 7, 3, 3);
        hc::Random rng; rng.reset((unsigned)s);
        for (int state = 0; state < 12; ++state) {
            if (state) walk(assign, rng, 3);
            std::vector<Move> mv; allMoves(assign, mv);
            int valid = 0;
            for (ll idx = 0; idx < moveCount(assign); ++idx) { Move m; if (nthMove(assign, idx, m)) ++valid; }
            if (valid != (int)mv.size()) ++numberBad;
            for (const Move& m : mv) {
                int saved[AN]; std::memcpy(saved, assign.as, sizeof saved);
                const ll before = refAssign(assign), d = assign.delta(m);
                assign.apply(m);
                if (!refAssignValid(assign) || !assign.valid()) ++invalid;
                if (!cachesOk(assign)) ++cacheBad;
                if (refAssign(assign) - before != d) ++bad;
                assign.undo(m);
                if (std::memcmp(saved, assign.as, sizeof saved) != 0 || !cachesOk(assign)) ++cacheBad;
                ++moves;
            }
        }
    }
    printf("diff assign %lld %lld %lld %lld %lld\n", moves, bad, invalid, cacheBad, numberBad);
    // the default sizes: random walk, delta against the reference, every proposal valid
    ll badRoute = 0, badAssign = 0, tried = 0;
    for (int s = 1; s <= 5; ++s) {
        genRoute(route, s, 200); genAssign(assign, s, 120, 8, 18);
        hc::Random rng; rng.reset((unsigned)s);
        for (int t = 0; t < 2000; ++t) {
            Move m;
            if (propose(route, rng, m)) { const ll b = refRoute(route), d = route.delta(m); route.apply(m); if (refRoute(route) - b != d || !refRouteValid(route)) ++badRoute; }
            if (propose(assign, rng, m)) { const ll b = refAssign(assign), d = assign.delta(m); assign.apply(m); if (refAssign(assign) - b != d || !refAssignValid(assign) || !cachesOk(assign)) ++badAssign; }
            ++tried;
        }
    }
    printf("diff default %lld %lld %lld\n", tried, badRoute, badAssign);
}

// the exponent table and the acceptance frequency
static void modeAccTab() {
    buildAcc();
    for (int q = 0; q <= XMAX; ++q) printf("acctab %d %d\n", q, accTab[q]);
}
static void modeAccept() {
    buildAcc();
    hc::Random rng; rng.reset(12345);
    const ll T = 100 * TS;                                  // d = 100 x is x in units of T
    const int xs[] = {1, 25, 50, 100, 200, 300, 500};       // x = 0.01, 0.25, 0.5, 1, 2, 3, 5
    for (int x : xs) {
        int taken = 0;
        const int draws = 200000;
        for (int i = 0; i < draws; ++i) if (acceptWorse(x, T, rng)) ++taken;
        printf("accept %d %d %d\n", x, draws, taken);
    }
}

// schedule values
static void modeSchedule() {
    const ll budgets[] = {1000, 100000, 1000000};
    for (int shape = 0; shape <= 1; ++shape) for (ll B : budgets) {
        Schedule sc; sc.init(250 * TS, 3 * TS, B, shape);
        printf("schedule %d %lld %d", shape, B, sc.stages);
        const ll marks[] = {0, B / 4, B / 2, B * 3 / 4, B - 1, B};
        for (ll u : marks) printf(" %lld", sc.at(u));
        printf("\n");
    }
    Schedule sc; sc.init(5 * TS, 5 * TS, 100, 0);     // t0 == t1: constant
    printf("schedule const %d %lld %lld\n", sc.stages, sc.at(0), sc.at(99));
}

// temperature from deltas: the sample, and the minimality of the found temperature
template <class P>
static void tempRows(const char* name, P& p, int seed) {
    hc::Random rng; rng.reset((unsigned)seed);
    ll evals = 0;
    const int cnt = sampleUphill(p, rng, 2000, evals);
    printf("temp %s %d %lld %d", name, seed, evals, cnt);
    for (int i = 0; i < cnt; ++i) printf(" %lld", ups[i]);
    printf("\n");
    const int rates[] = {5, 100, 300, 900};
    for (int r : rates) {
        const ll t = tempForRate(ups, cnt, r);
        const ll want = (ll)ONE / 1000 * r;
        printf("temprate %s %d %lld %d %lld %lld %lld\n", name, r, t, (int)(meanAccept(ups, cnt, t) >= want), meanAccept(ups, cnt, t), t > 1 ? meanAccept(ups, cnt, t - 1) : -1, want);
    }
}
static void modeTemp() {
    buildAcc();
    genRoute(route, 1, 200); tempRows("route", route, 1);
    genAssign(assign, 1, 120, 8, 18); tempRows("assign", assign, 1);
    printf("temp none %lld\n", tempForRate(ups, 0, 100));
}

// hill climbing: the certificate, first versus best improvement
template <class P, class G>
static void hillFrame(const char* name, P& p, G gen, int firstSeed, int lastSeed) {
    for (int s = firstSeed; s <= lastSeed; ++s) for (int method = 0; method <= 1; ++method) {
        gen(s);
        p.applies = 0;
        const ll start = p.fullCost();
        ll evals = 0; bool opt;
        const ll cost = method == 0 ? climbFirst(p, start, 1000000000LL, evals, opt) : climbBest(p, start, 1000000000LL, evals, opt);
        const ll applies = p.applies;
        const int left = improvingByReference(p);
        printf("hill %s %d %d %lld %lld %d %d %lld %lld %d\n", name, s, method, evals, cost, (int)opt, left, applies, refCost(p), (int)refValid(p));
    }
}
static void modeHill() {
    hillFrame("route", croute, [](int s) { genRoute(croute, s, 200); }, 1, 20);
    hillFrame("assign", cassign, [](int s) { genAssign(cassign, s, 120, 8, 18); }, 1, 20);
}

// annealing: best/last bookkeeping against a reference loop that copies the whole solution at every new best
template <class P>
static ll annealRef(P& p, hc::Random& rng, ll cost, ll budget, Schedule& sc, ll& evals, ll& last, std::vector<int>& bestSol) {
    ll best = cost;
    bestSol.assign(solOf(p), solOf(p) + lenOf(p));
    while (evals < budget) {
        const ll t = sc.at(evals);
        ++evals;
        Move mv;
        if (!propose(p, rng, mv)) continue;
        const ll d = p.delta(mv);
        if (d > 0 && !acceptWorse(d, t, rng)) continue;
        p.apply(mv); cost += d;
        if (cost < best) { best = cost; bestSol.assign(solOf(p), solOf(p) + lenOf(p)); }
    }
    last = cost;
    return best;
}
template <class P, class G>
static void annealFrame(const char* name, P& p, G gen, ll budget) {
    for (int variant = 0; variant < 2; ++variant) for (int s = 1; s <= 20; ++s) {
        gen(s);
        const ll start = p.fullCost();
        hc::Random rng; rng.reset((unsigned)s);
        ll evals = 0;
        const int cnt = sampleUphill(p, rng, 2000, evals);
        ll t0 = tempForRate(ups, cnt, 100), t1 = tempForRate(ups, cnt, 5);
        if (variant) { t0 *= 16; t1 *= 16; }                 // hot: the end is hot, so current != best at the end
        if (t1 > t0) t1 = t0;
        Schedule sc1; sc1.init(t0, t1, budget, 0);
        Schedule sc2 = sc1;
        hc::Random rng2 = rng;
        ll e1 = evals, e2 = evals, last1, last2;
        Trace tr;
        std::vector<int> refSol;
        // the reference runs first on a copy of the input, then the lesson loop runs on the original
        P q = p;
        const ll refBest = annealRef(q, rng2, start, budget, sc2, e2, last2, refSol);
        const ll best = anneal(p, rng, start, budget, sc1, e1, last1, tr);
        ll up = 0, taken = 0;
        for (int i = 0; i < 10; ++i) { up += tr.up[i]; taken += tr.taken[i]; }
        printf("anneal %s %d %d %lld %lld %lld %lld %lld %d %d %lld %lld %lld %lld\n", name, variant, s, best, refBest, last1, last2, refCost(p), (int)refValid(p),
               (int)(e1 == e2), up, taken, (ll)(last1 > best), (ll)0);
    }
}
static void modeAnneal() {
    buildAcc();
    annealFrame("route", route, [](int s) { genRoute(route, s, 200); }, 300000);
    annealFrame("assign", assign, [](int s) { genAssign(assign, s, 120, 8, 18); }, 60000);
}

// restarts: the number of runs, the best solution kept
static void modeRestarts() {
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200);
        hc::Random rng; rng.reset((unsigned)s);
        ll evals = 0; int runs;
        const ll best = restarts(route, rng, 300000, evals, runs);
        printf("restarts route %d %lld %lld %d %d\n", s, best, refRoute(route), runs, (int)refRouteValid(route));
        genAssign(assign, s, 120, 8, 18);
        hc::Random rng2; rng2.reset((unsigned)s);
        evals = 0;
        const ll best2 = restarts(assign, rng2, 40000, evals, runs);
        printf("restarts assign %d %lld %lld %d %d\n", s, best2, refAssign(assign), runs, (int)refAssignValid(assign) && cachesOk(assign));
    }
}

// hand examples on the 7-point instance: neighbourhood of the local optimum, the climbs, the SA steps
static void loadHand(const int* order) {
    const int pts[7][2] = {{1,1},{8,2},{2,4},{7,5},{3,8},{9,7},{5,9}};
    route.n = 7;
    for (int i = 0; i < 7; ++i) { route.px[i] = pts[i][0]; route.py[i] = pts[i][1]; route.p[i] = order[i]; }
}
// logs every applied move of the 7-point examples
struct HRoute : Route {
    const char* tag;
    void apply(const Move& mv) {
        Route::apply(mv);
        if (tag) printf("hand %s %d %d %lld %d %d %d %d %d %d %d\n", tag, mv.a, mv.b, fullCost(), p[0], p[1], p[2], p[3], p[4], p[5], p[6]);
    }
};
static HRoute hroute;
static void modeHand() {
    buildAcc();
    const int id[7] = {0, 1, 2, 3, 4, 5, 6};
    const int L[7] = {5, 3, 1, 0, 2, 4, 6};
    loadHand(id);
    printf("hand start %lld\n", route.fullCost());
    // the lesson's own climbs from the number order, logged move by move through a wrapper that sees every apply
    {
        for (int method = 0; method <= 1; ++method) {
            const int* base = id;
            hroute.n = 7;
            for (int i = 0; i < 7; ++i) { hroute.px[i] = route.px[i]; hroute.py[i] = route.py[i]; hroute.p[i] = base[i]; }
            hroute.tag = method == 0 ? "first" : "best";
            ll evals = 0; bool opt;
            const ll c = method == 0 ? climbFirst(hroute, hroute.fullCost(), 1000000, evals, opt) : climbBest(hroute, hroute.fullCost(), 1000000, evals, opt);
            printf("hand %send %lld %lld %d\n", hroute.tag, c, evals, (int)opt);
        }
        hroute.tag = nullptr;
    }
    // where the first improvement goes from the solution one worsening move away from L (the path of the move (1, 6))
    {
        loadHand(L);
        hroute.n = 7;
        for (int i = 0; i < 7; ++i) { hroute.px[i] = route.px[i]; hroute.py[i] = route.py[i]; hroute.p[i] = L[i]; }
        Move m; m.kind = 0; m.a = 1; m.b = 6; m.old = 0;
        hroute.Route::apply(m);
        hroute.tag = "via";
        ll evals = 0; bool opt;
        printf("hand viastart %lld\n", hroute.fullCost());
        const ll c = climbFirst(hroute, hroute.fullCost(), 1000000, evals, opt);
        printf("hand viaend %lld %lld %d\n", c, evals, (int)opt);
        hroute.tag = nullptr;
    }
    // the neighbourhood of the first-improvement local optimum L and where each worsening move leads under first improvement
    loadHand(L);
    printf("hand L %lld %d\n", route.fullCost(), improvingByReference(route));
    for (int a = 0; a < 7; ++a) for (int b = a + 1; b < 7; ++b) {
        loadHand(L);
        Move m; m.kind = 0; m.a = a; m.b = b; m.old = 0;
        const ll d = route.delta(m);
        route.apply(m);
        ll evals = 0; bool opt;
        const ll after = climbFirst(route, route.fullCost(), 1000000, evals, opt);
        printf("hand nb %d %d %lld %lld\n", a, b, d, after);
    }
    // SA steps at a fixed temperature T = 3 from L (the lesson's propose, delta, acceptWorse)
    loadHand(L);
    hc::Random rng; rng.reset(417);
    const ll T = 3 * TS;
    ll cost = route.fullCost(), best = cost;
    for (int ev = 1; ev <= 10; ++ev) {
        Move mv;
        const bool ok = propose(route, rng, mv);
        if (!ok) { printf("hand sa %d none\n", ev); continue; }
        const ll d = route.delta(mv);
        if (d > 0) {
            hc::Random peek = rng;
            const ll q = d * XS * TS / T;
            const int r = (int)(peek.next() >> 2);
            const bool take = acceptWorse(d, T, rng);
            printf("hand sa %d %d %d %lld %lld %d %d %d", ev, mv.a, mv.b, d, q, q < XMAX ? accTab[q] : 0, r, (int)take);
            if (take) { route.apply(mv); cost += d; }
        } else {
            printf("hand sa %d %d %d %lld 0 0 0 1", ev, mv.a, mv.b, d);
            route.apply(mv); cost += d;
        }
        if (cost < best) best = cost;
        printf(" %lld %lld\n", cost, best);
    }
    // the mean acceptance of the worsening moves at L for a few temperatures
    loadHand(L);
    {
        static ll ds[64]; int cnt = 0;
        for (int a = 0; a < 7; ++a) for (int b = a + 1; b < 7; ++b) { Move m; m.kind = 0; m.a = a; m.b = b; m.old = 0; const ll d = route.delta(m); if (d > 0) ds[cnt++] = d; }
        printf("hand ups %d", cnt); for (int i = 0; i < cnt; ++i) printf(" %lld", ds[i]); printf("\n");
        const int Ts[] = {1, 2, 3, 4, 6, 10};
        for (int t : Ts) printf("hand mean %d %lld\n", t, meanAccept(ds, cnt, (ll)t * TS));
        const int rates[] = {100, 300};
        for (int r : rates) printf("hand rate %d %lld\n", r, tempForRate(ds, cnt, r));
    }
}

// ---------------------------------------------------------------- experiments
static ll medianOf(std::vector<ll> v) { std::sort(v.begin(), v.end()); return v[9]; }

static const Plan DEFAULT_PLAN = {100, 5, 100, 100, 0};

template <class F>
static void forSeeds(int a, int b, F f) { for (int s = a; s <= b; ++s) f(s); }

static void modeExp() {
    buildAcc();
    // start costs
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200); printf("start route %d %lld\n", s, route.fullCost());
        genAssign(assign, s, 120, 8, 18); printf("start assign %d %lld\n", s, assign.fullCost());
    }
    // B: distribution of the worsening deltas at the start and at the local optimum
    for (int s = 1; s <= 20; ++s) {
        for (int frame = 0; frame < 2; ++frame) {
            ll e = 0;
            hc::Random rng; rng.reset((unsigned)s);
            std::vector<ll> q0, q1;
            ll t0, t1;
            int cnt0, cnt1;
            if (frame == 0) {
                genRoute(route, s, 200);
                cnt0 = sampleUphill(route, rng, 2000, e); q0.assign(ups, ups + cnt0); t0 = tempForRate(ups, cnt0, 100); t1 = tempForRate(ups, cnt0, 5);
                bool o; climbFirst(route, route.fullCost(), 1000000000LL, e, o);
                cnt1 = sampleUphill(route, rng, 2000, e); q1.assign(ups, ups + cnt1);
            } else {
                genAssign(assign, s, 120, 8, 18);
                cnt0 = sampleUphill(assign, rng, 2000, e); q0.assign(ups, ups + cnt0); t0 = tempForRate(ups, cnt0, 100); t1 = tempForRate(ups, cnt0, 5);
                bool o; climbFirst(assign, assign.fullCost(), 1000000000LL, e, o);
                cnt1 = sampleUphill(assign, rng, 2000, e); q1.assign(ups, ups + cnt1);
            }
            std::sort(q0.begin(), q0.end()); std::sort(q1.begin(), q1.end());
            printf("B %s %d %d %lld %lld %lld %lld %d %lld %lld %lld\n", frame ? "assign" : "route", s, cnt0, q0[cnt0 / 10], q0[cnt0 / 2], q0[cnt0 * 9 / 10], t0, cnt1, q1[cnt1 / 10], q1[cnt1 / 2], q1[cnt1 * 9 / 10]);
            printf("Bt %s %d %lld\n", frame ? "assign" : "route", s, t1);
        }
    }
    // C: methods at equal evaluation budgets
    const ll routeBudgets[] = {100000, 300000, 1000000, 3000000};
    const ll assignBudgets[] = {20000, 100000, 400000};
    for (int hold = 0; hold < 2; ++hold) for (int frame = 0; frame < 2; ++frame) {
        const int s0 = hold ? 101 : 1, s1 = hold ? 120 : 20;
        const int nb = frame ? 3 : 4;
        for (int bi = 0; bi < nb; ++bi) {
            const ll B = frame ? assignBudgets[bi] : routeBudgets[bi];
            if (hold && B != (frame ? 100000 : 1000000)) continue;
            for (int s = s0; s <= s1; ++s) for (int method : {0, 2, 3}) {
                Stat st;
                const ll cost = frame ? solveAssign(s, method, B, DEFAULT_PLAN, st) : solveRoute(s, method, B, DEFAULT_PLAN, st);
                const ll ref = frame ? refAssign(assign) : refRoute(route);
                printf("C %d %s %lld %d %d %lld %lld %d %lld %lld\n", hold, frame ? "assign" : "route", B, s, method, cost, st.evals, st.runs, st.last, ref);
            }
        }
    }
    // D: schedule shape, E: temperature scale sweeps (default budget per frame)
    for (int frame = 0; frame < 2; ++frame) {
        const ll B = frame ? 100000 : 1000000;
        struct Cfg { const char* tag; Plan pl; };
        const Cfg cfgs[] = {
            {"exp", {100, 5, 100, 100, 0}}, {"lin", {100, 5, 100, 100, 1}},
            {"t0x6", {100, 5, 6, 100, 0}}, {"t0x25", {100, 5, 25, 100, 0}}, {"t0x400", {100, 5, 400, 100, 0}}, {"t0x1600", {100, 5, 1600, 100, 0}},
            {"t1x6", {100, 5, 100, 6, 0}}, {"t1x25", {100, 5, 100, 25, 0}}, {"t1x400", {100, 5, 100, 400, 0}}, {"t1x1600", {100, 5, 100, 1600, 0}},
            {"r300", {300, 5, 100, 100, 0}}, {"r500", {500, 5, 100, 100, 0}}, {"r30", {30, 5, 100, 100, 0}},
        };
        for (const Cfg& c : cfgs) for (int s = 1; s <= 20; ++s) {
            Stat st;
            const ll cost = frame ? solveAssign(s, 3, B, c.pl, st) : solveRoute(s, 3, B, c.pl, st);
            const ll ref = frame ? refAssign(assign) : refRoute(route);
            printf("E %s %s %lld %d %lld %lld %lld %lld %lld\n", frame ? "assign" : "route", c.tag, B, s, cost, st.last, st.t0, st.t1, ref);
        }
    }
    // F: acceptance of the worsening moves per tenth of the run (summed over the seeds)
    for (int frame = 0; frame < 2; ++frame) {
        const ll B = frame ? 100000 : 1000000;
        ll up[10] = {0}, taken[10] = {0};
        for (int s = 1; s <= 20; ++s) {
            Stat st;
            if (frame) solveAssign(s, 3, B, DEFAULT_PLAN, st); else solveRoute(s, 3, B, DEFAULT_PLAN, st);
            for (int i = 0; i < 10; ++i) { up[i] += st.tr.up[i]; taken[i] += st.tr.taken[i]; }
        }
        printf("F %s", frame ? "assign" : "route");
        for (int i = 0; i < 10; ++i) printf(" %lld %lld", up[i], taken[i]);
        printf("\n");
    }
}

// ---------------------------------------------------------------- detection of the common mistakes
static void modeDetect() {
    buildAcc();
    // D1: the local optimum certificate of the first improvement on the route frame, seeds 1..20
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200);
        ll evals = 0; bool opt;
        climbFirst(route, route.fullCost(), 3000000, evals, opt);
        printf("D1 %d %d %d\n", s, (int)opt, improvingByReference(route));
    }
    // D3: acceptance frequency at x = 1
    {
        hc::Random rng; rng.reset(12345);
        int taken = 0;
        for (int i = 0; i < 200000; ++i) if (acceptWorse(100, 100 * TS, rng)) ++taken;
        printf("D3 %d\n", taken);
    }
    // D4: the solution that anneal leaves behind has the cost it returns (hot run so that current != best)
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200);
        const ll start = route.fullCost();
        hc::Random rng; rng.reset((unsigned)s);
        Schedule sc; sc.init(300 * TS, 100 * TS, 20000, 0);
        ll evals = 0, last; Trace tr;
        const ll best = anneal(route, rng, start, 20000, sc, evals, last, tr);
        printf("D4 %d %lld %lld %lld\n", s, best, refRoute(route), last);
    }
    // D5: the temperature at the end of the budget for three budgets, and the route cost at 1,000,000
    const ll budgets[] = {10000, 100000, 1000000};
    for (ll B : budgets) {
        Schedule sc; sc.init(250 * TS, 3 * TS, B, 0);
        printf("D5 %lld %lld\n", B, sc.at(B - 1));
    }
    std::vector<ll> costs;
    for (int s = 1; s <= 20; ++s) { Stat st; costs.push_back(solveRoute(s, 3, 1000000, DEFAULT_PLAN, st)); }
    printf("D5cost %lld\n", medianOf(costs));
}

int main(int argc, char** argv) {
    const std::string mode = argc > 1 ? argv[1] : "";
    if (mode == "gen") modeGen();
    else if (mode == "diff") modeDiff();
    else if (mode == "acctab") modeAccTab();
    else if (mode == "accept") modeAccept();
    else if (mode == "schedule") modeSchedule();
    else if (mode == "temp") modeTemp();
    else if (mode == "hill") modeHill();
    else if (mode == "anneal") modeAnneal();
    else if (mode == "restarts") modeRestarts();
    else if (mode == "hand") modeHand();
    else if (mode == "exp") modeExp();
    else if (mode == "detect") modeDetect();
    else { fprintf(stderr, "unknown mode\n"); return 2; }
    return 0;
}
