// Harness for the neighborhood-and-delta check. Standard headers are fine here; the lesson code is included below.
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <set>
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

// ---------------------------------------------------------------- neighbourhood enumeration
static void routeMoves(const Route& r, int kinds, std::vector<Move>& out) {  // kinds: bit 0 swap, 1 insert, 2 reverse
    out.clear();
    Move m; m.old = 0;
    for (int a = 0; a < r.n; ++a) for (int b = 0; b < r.n; ++b) {
        if (a == b) continue;
        if ((kinds & 1) && a < b) { m.kind = 0; m.a = a; m.b = b; out.push_back(m); }
        if (kinds & 2) { m.kind = 1; m.a = a; m.b = b; out.push_back(m); }
        if ((kinds & 4) && a < b) { m.kind = 2; m.a = a; m.b = b; out.push_back(m); }
    }
}
static void assignMoves(const Assign& s, int kinds, std::vector<Move>& out) {  // bit 0 move (valid only), bit 1 swap
    out.clear();
    Move m;
    for (int i = 0; i < s.n; ++i) {
        if (kinds & 1) for (int to = 0; to < s.m; ++to) if (to != s.as[i] && s.cnt[to] < s.k) { m.kind = 0; m.a = i; m.b = to; m.old = s.as[i]; out.push_back(m); }
        if (kinds & 2) for (int j = i + 1; j < s.n; ++j) if (s.as[i] != s.as[j]) { m.kind = 1; m.a = i; m.b = j; m.old = 0; out.push_back(m); }
    }
}
static int improvingRoute(Route& r, int kinds) {
    std::vector<Move> mv; routeMoves(r, kinds, mv);
    int c = 0; for (const Move& m : mv) if (r.delta(m) < 0) ++c;
    return c;
}
static int improvingAssign(Assign& s, int kinds) {
    std::vector<Move> mv; assignMoves(s, kinds, mv);
    int c = 0; for (const Move& m : mv) if (s.delta(m) < 0) ++c;
    return c;
}
static int routeKinds(int mask) { return mask & 7; }  // adjacent swap (bit 3) is inside swap and reverse

// ---------------------------------------------------------------- modes
static void modeGen() {
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200);
        ull h = fnv(route.px, 200); h = fnv(route.py, 200, h);
        printf("gen route %d %llu %lld %lld\n", s, h, route.fullCost(), refRoute(route));
        genAssign(assign, s, 120, 8, 18);
        ull g = fnv(assign.d, 120);
        for (int i = 0; i < 120; ++i) g = fnv(assign.c[i], 8, g);
        printf("gen assign %d %llu %lld %lld\n", s, g, assign.fullCost(), refAssign(assign));
    }
}

static void walkRoute(Route& r, hc::Random& rng, int steps) {
    for (int t = 0; t < steps; ++t) { Move mv; if (r.propose(rng, mv)) r.apply(mv); }
}
static void walkAssign(Assign& s, hc::Random& rng, int steps) {
    for (int t = 0; t < steps; ++t) { Move mv; if (s.propose(rng, mv)) s.apply(mv); }
}

// delta(all moves) == reference cost after apply; undo restores the arrays and caches.
static void modeExhaustive() {
    ll moves = 0, bad = 0, invalid = 0;
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 8); route.mask = 7;
        hc::Random rng; rng.reset((unsigned)s);
        for (int state = 0; state < 12; ++state) {
            if (state) walkRoute(route, rng, 3);
            std::vector<Move> mv; routeMoves(route, 7, mv);
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
    printf("exhaustive route %lld %lld %lld\n", moves, bad, invalid);
    moves = bad = invalid = 0; ll cacheBad = 0;
    for (int s = 1; s <= 20; ++s) {
        genAssign(assign, s, 7, 3, 3); assign.mask = 3;
        hc::Random rng; rng.reset((unsigned)s);
        for (int state = 0; state < 12; ++state) {
            if (state) walkAssign(assign, rng, 3);
            std::vector<Move> mv; assignMoves(assign, 3, mv);
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
    printf("exhaustive assign %lld %lld %lld %lld\n", moves, bad, invalid, cacheBad);
}

static void modeRandomCheck() {
    int routeMasks[] = {1, 2, 4, 8, 5, 6, 7, 15};
    for (int mask : routeMasks) for (int s = 1; s <= 3; ++s) {
        genRoute(route, s, 200); route.mask = mask;
        hc::Random rng; rng.reset((unsigned)s);
        printf("random route %d %d %d\n", mask, s, checkDelta(route, rng, 3000));
    }
    for (int mask = 1; mask <= 3; ++mask) for (int s = 1; s <= 3; ++s) {
        genAssign(assign, s, 120, 8, 18); assign.mask = mask;
        hc::Random rng; rng.reset((unsigned)s);
        printf("random assign %d %d %d\n", mask, s, checkDelta(assign, rng, 3000));
    }
    for (int s = 1; s <= 3; ++s) {
        genAssign(assign, s, 24, 8, 3); assign.mask = 3;
        hc::Random rng; rng.reset((unsigned)s);
        printf("random tight %d %d\n", s, checkDelta(assign, rng, 3000));
    }
}

// Reference loops for the trajectory identity: a fixed number of proposals, written here.
template <class P>
static ll replay(P& p, hc::Random& rng, ll cost, ll proposals, bool full) {
    for (ll t = 0; t < proposals; ++t) {
        Move mv;
        if (!p.propose(rng, mv)) continue;
        if (full) { p.apply(mv); const ll now = p.fullCost(); if (now < cost) cost = now; else p.undo(mv); }
        else { const ll d = p.delta(mv); if (d < 0) { p.apply(mv); cost += d; } }
    }
    return cost;
}

static void modeIdentity() {
    for (int s = 1; s <= 5; ++s) for (int full = 0; full <= 1; ++full) {
        // route, reverse + swap + insert
        const ll budget = 300000;
        ll got = runRoute(s, 7, full != 0, budget);
        int a[RN]; std::memcpy(a, route.p, sizeof a);
        const ll props = route.props;
        genRoute(route, s, 200); route.mask = 7;
        hc::Random rng; rng.reset((unsigned)s);
        const ll start = route.fullCost();
        const ll again = replay(route, rng, start, props, full == 0);   // the other strategy
        printf("identity route %d %d %d %lld %lld %lld\n", s, full, std::memcmp(a, route.p, sizeof a) == 0, got, again, refRoute(route));
        got = runAssign(s, 3, full != 0, 60000);
        int b[AN]; std::memcpy(b, assign.as, sizeof b);
        const ll props2 = assign.props;
        genAssign(assign, s, 120, 8, 18); assign.mask = 3;
        hc::Random rng2; rng2.reset((unsigned)s);
        const ll start2 = assign.fullCost();
        const ll again2 = replay(assign, rng2, start2, props2, full == 0);
        printf("identity assign %d %d %d %lld %lld %lld\n", s, full, std::memcmp(b, assign.as, sizeof b) == 0, got, again2, refAssign(assign));
    }
}

// ---------------------------------------------------------------- experiments
static void dumpRoute() { for (int k = 0; k < 200; ++k) printf(" %d", route.p[k]); printf("\n"); }
static void dumpAssign() { for (int k = 0; k < 120; ++k) printf(" %d", assign.as[k]); printf("\n"); }

static void modeExp() {
    const ll routeBudgets[] = {20000, 100000, 500000, 2000000};
    const ll assignBudgets[] = {1000, 5000, 20000, 100000};
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200); printf("start route %d %lld\n", s, route.fullCost());
        genAssign(assign, s, 120, 8, 18); printf("start assign %d %lld\n", s, assign.fullCost());
    }
    for (int bi = 0; bi < 4; ++bi) for (int full = 1; full >= 0; --full) for (int s = 1; s <= 20; ++s) {
        const ll r = runRoute(s, 4, full != 0, routeBudgets[bi]);
        printf("A route %lld %d %d %lld %lld %lld\n", routeBudgets[bi], full, s, r, route.props, refRoute(route));
        if (bi == 3) { printf("final route %d %d", full, s); dumpRoute(); }
        const ll q = runAssign(s, 3, full != 0, assignBudgets[bi]);
        printf("A assign %lld %d %d %lld %lld %lld\n", assignBudgets[bi], full, s, q, assign.props, refAssign(assign));
        if (bi == 2) { printf("final assign %d %d", full, s); dumpAssign(); }
    }
    const int routeMasks[] = {1, 2, 4, 8, 5, 6, 7, 15};
    for (int mask : routeMasks) for (int s = 1; s <= 20; ++s) {
        const ll r = runRoute(s, mask, false, 2000000);
        int lo = (mask == 8) ? 1 : 0;
        if (mask == 8) {                      // adjacent swaps only: scan its own neighbourhood
            Move mv; mv.kind = 0; mv.old = 0;
            for (int a = 0; a + 1 < route.n; ++a) { mv.a = a; mv.b = a + 1; if (route.delta(mv) < 0) lo = 0; }
        } else lo = improvingRoute(route, routeKinds(mask)) == 0;
        printf("B route %d %d %lld %d %lld\n", mask, s, r, lo, refRoute(route));
    }
    for (int mask = 1; mask <= 3; ++mask) for (int s = 1; s <= 20; ++s) {
        const ll r = runAssign(s, mask, false, 100000);
        int all15 = 1; for (int j = 0; j < 8; ++j) if (assign.cnt[j] != 15) all15 = 0;
        printf("B assign %d %d %lld %d %d %lld\n", mask, s, r, improvingAssign(assign, mask) == 0, all15, refAssign(assign));
    }
    // C: same proposals, split of the work
    const ll props = 5000;
    for (int s = 1; s <= 20; ++s) for (int full = 0; full <= 1; ++full) {
        const int masks[] = {4, 1};
        for (int mask : masks) {
            genRoute(route, s, 200); route.mask = mask;
            hc::Random rng; rng.reset((unsigned)s);
            const ll start = route.fullCost(); route.ops = 0;
            const ll r = replay(route, rng, start, props, full != 0);
            printf("C route %d %d %d %lld %lld %lld %lld\n", mask, full, s, props, route.ops, route.writes, r);
        }
        genAssign(assign, s, 120, 8, 18); assign.mask = 3;
        hc::Random rng; rng.reset((unsigned)s);
        const ll start = assign.fullCost(); assign.ops = 0;
        const ll r = replay(assign, rng, start, props, full != 0);
        printf("C assign 3 %d %d %lld %lld %lld %lld\n", full, s, props, assign.ops, assign.writes, r);
    }
}

// ---------------------------------------------------------------- sizes and connectivity
static ull hashRoute(const Route& r) { return fnv(r.p, r.n); }

static void modeSizes() {
    genRoute(route, 1, 200);
    const char* names[] = {"swap", "insert", "reverse"};
    for (int k = 0; k < 3; ++k) {
        std::vector<Move> mv; routeMoves(route, 1 << k, mv);
        std::vector<ull> hs;
        for (const Move& m : mv) { route.apply(m); hs.push_back(hashRoute(route)); route.undo(m); }
        std::sort(hs.begin(), hs.end());
        const ll distinct = std::unique(hs.begin(), hs.end()) - hs.begin();
        printf("size route %s %zu %lld\n", names[k], mv.size(), distinct);
    }
    genAssign(assign, 1, 120, 8, 18);
    std::vector<Move> mv; assignMoves(assign, 1, mv); const size_t moves = mv.size();
    assignMoves(assign, 2, mv);
    printf("size assign %zu %zu\n", moves, mv.size());
}

static void modeBfs() {
    // route, 6 points: neighbourhood graphs on the 720 orders, from the identity
    const char* names[] = {"swap", "insert", "reverse", "adjacent"};
    for (int k = 0; k < 4; ++k) {
        route.n = 6; route.mask = 7;
        std::map<std::vector<int>, int> dist;
        std::vector<std::vector<int>> frontier;
        std::vector<int> id(6); for (int i = 0; i < 6; ++i) id[i] = i;
        dist[id] = 0; frontier.push_back(id);
        size_t perState = 0; int diam = 0;
        while (!frontier.empty()) {
            std::vector<std::vector<int>> next;
            for (const std::vector<int>& st : frontier) {
                for (int i = 0; i < 6; ++i) route.p[i] = st[i];
                std::vector<Move> mv;
                if (k < 3) routeMoves(route, 1 << k, mv);
                else for (int a = 0; a + 1 < 6; ++a) { Move m; m.kind = 0; m.a = a; m.b = a + 1; m.old = 0; mv.push_back(m); }
                perState = mv.size();
                for (const Move& m : mv) {
                    route.apply(m);
                    std::vector<int> ns(route.p, route.p + 6);
                    route.undo(m);
                    if (!dist.count(ns)) { dist[ns] = dist[st] + 1; diam = std::max(diam, dist[ns]); next.push_back(ns); }
                }
            }
            frontier = next;
        }
        printf("bfs route %s %zu %zu %d\n", names[k], perState, dist.size(), diam);
    }
    // assignment, 6 jobs on 3 machines
    for (int kcap = 2; kcap <= 3; ++kcap) for (int kinds = 1; kinds <= 3; ++kinds) {
        genAssign(assign, 3, 6, 3, kcap); assign.mask = 3;
        std::set<std::vector<int>> seen;
        std::vector<std::vector<int>> frontier;
        std::vector<int> st0(assign.as, assign.as + 6);
        seen.insert(st0); frontier.push_back(st0);
        size_t startMoves = 0;
        { std::vector<Move> mv; assignMoves(assign, kinds, mv); startMoves = mv.size(); }
        while (!frontier.empty()) {
            std::vector<std::vector<int>> next;
            for (const std::vector<int>& st : frontier) {
                for (int i = 0; i < 6; ++i) assign.as[i] = st[i];
                assign.build();
                std::vector<Move> mv; assignMoves(assign, kinds, mv);
                for (const Move& m : mv) {
                    assign.apply(m);
                    std::vector<int> ns(assign.as, assign.as + 6);
                    if (!assign.valid()) printf("bfs assign INVALID\n");
                    assign.undo(m);
                    if (!seen.count(ns)) { seen.insert(ns); next.push_back(ns); }
                }
            }
            frontier = next;
        }
        printf("bfs assign %d %d %zu %zu\n", kcap, kinds, startMoves, seen.size());
    }
}

// ---------------------------------------------------------------- detection of the lesson's common mistakes
static void modeDetect() {
    ll moves = 0, bad = 0;
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 8); route.mask = 7;
        hc::Random rng; rng.reset((unsigned)s);
        for (int state = 0; state < 12; ++state) {
            if (state) walkRoute(route, rng, 3);
            std::vector<Move> mv; routeMoves(route, 7, mv);
            for (const Move& m : mv) {
                const ll before = refRoute(route), d = route.delta(m);
                route.apply(m);
                if (refRoute(route) - before != d) ++bad;
                route.undo(m);
                ++moves;
            }
        }
    }
    printf("D1 %lld %lld\n", moves, bad);
    for (int s = 1; s <= 20; ++s) {
        genRoute(route, s, 200); route.mask = 1;
        hc::Random rng; rng.reset((unsigned)s);
        const int big = checkDelta(route, rng, 20000);
        genRoute(route, s, 8); route.mask = 1;
        hc::Random rng2; rng2.reset((unsigned)s);
        const int small = checkDelta(route, rng2, 20000);
        printf("D2 %d %d %d\n", s, big, small);
    }
    for (int s = 1; s <= 20; ++s) {
        genAssign(assign, s, 120, 8, 18); assign.mask = 3;
        hc::Random rng; rng.reset((unsigned)s);
        const int a = checkDelta(assign, rng, 3000);
        genAssign(assign, s, 24, 8, 3); assign.mask = 3;
        hc::Random rng2; rng2.reset((unsigned)s);
        const int tight = checkDelta(assign, rng2, 3000);
        printf("D3 %d %d %d\n", s, a, tight);
    }
    genRoute(route, 1, 200); route.mask = 4;
    hc::Random rng; rng.reset(1);
    std::vector<char> seen(200 * 200, 0); int distinct = 0;
    for (int t = 0; t < 400000; ++t) {
        Move mv;
        if (route.propose(rng, mv) && !seen[mv.a * 200 + mv.b]) { seen[mv.a * 200 + mv.b] = 1; ++distinct; }
    }
    printf("D5 %d\n", distinct);
}


static void modeHand() {
    const int pts[7][2] = {{1,1},{8,2},{2,4},{7,5},{3,8},{9,7},{5,9}};
    route.n = 7; route.mask = 7;
    for (int i = 0; i < 7; ++i) { route.px[i] = pts[i][0]; route.py[i] = pts[i][1]; }
    route.init();
    printf("hand route start %lld\n", route.fullCost());
    const int mv[5][3] = {{0,1,4},{1,5,1},{2,2,4},{2,4,6},{0,2,3}};
    for (int t = 0; t < 5; ++t) {
        Move m; m.kind = mv[t][0]; m.a = mv[t][1]; m.b = mv[t][2]; m.old = 0;
        const ll d = route.delta(m);
        route.apply(m);
        printf("hand route %d %d %d %lld %lld", m.kind, m.a, m.b, d, route.fullCost());
        for (int k = 0; k < 7; ++k) printf(" %d", route.p[k]);
        printf("\n");
        route.undo(m);
    }
    const int dd[6] = {53,28,41,19,62,7};
    const int cc[6][3] = {{12,30,5},{20,8,12},{40,15,22},{3,27,18},{25,10,35},{14,38,9}};
    assign.n = 6; assign.m = 3; assign.k = 3; assign.mask = 3;
    for (int i = 0; i < 6; ++i) { assign.d[i] = dd[i]; for (int j = 0; j < 3; ++j) assign.c[i][j] = cc[i][j]; }
    assign.init();
    printf("hand assign start %lld %d %d %d %lld\n", assign.fullCost(), assign.load[0], assign.load[1], assign.load[2], assign.sq);
    const int am[3][3] = {{0,1,2},{1,0,2},{0,0,2}};   // kind, a, b
    for (int t = 0; t < 3; ++t) {
        Move m; m.kind = am[t][0]; m.a = am[t][1]; m.b = am[t][2]; m.old = assign.as[m.a];
        const ll d = assign.delta(m);
        assign.apply(m);
        printf("hand assign %d %d %d %lld %lld %d %d %d %lld\n", m.kind, m.a, m.b, d, assign.fullCost(), assign.load[0], assign.load[1], assign.load[2], assign.sq);
        assign.undo(m);
    }
}

int main(int argc, char** argv) {
    const std::string mode = argc > 1 ? argv[1] : "";
    if (mode == "gen") modeGen();
    else if (mode == "exhaustive") modeExhaustive();
    else if (mode == "random") modeRandomCheck();
    else if (mode == "identity") modeIdentity();
    else if (mode == "exp") modeExp();
    else if (mode == "sizes") modeSizes();
    else if (mode == "bfs") modeBfs();
    else if (mode == "detect") modeDetect();
    else if (mode == "hand") modeHand();
    else { fprintf(stderr, "unknown mode\n"); return 2; }
    return 0;
}
