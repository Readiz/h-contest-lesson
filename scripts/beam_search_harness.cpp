// Harness for the beam-search check. Standard headers are fine here; the lesson code is included below.
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>
#include "lesson.cpp"

typedef long long ll;
typedef unsigned long long ull;

// ---------------------------------------------------------------- independent references (this check only)
static const int DY[4] = {-1, 0, 1, 0}, DX[4] = {0, 1, 0, -1};

// Replays a walk on the grid: returns the sum of first-visit values, or -1 if the walk leaves the grid.
static ll refGridReplay(const Grid& g, const int* path, int steps) {
    std::vector<char> seen(g.h * g.w, 0);
    int y = 0, x = 0;
    ll sum = g.v[0];
    seen[0] = 1;
    for (int t = 0; t < steps; ++t) {
        const int c = path[t], cy = c / g.w, cx = c % g.w;
        if (c < 0 || c >= g.h * g.w) return -1;
        if (std::abs(cy - y) + std::abs(cx - x) != 1) return -1;       // must be a step to a neighbouring cell
        y = cy; x = cx;
        if (!seen[c]) { seen[c] = 1; sum += g.v[c]; }
    }
    return sum;
}
// Number of distinct cells a walk stands on, start included.
static int refGridDistinct(const Grid& g, const int* path, int steps) {
    std::set<int> cells;
    cells.insert(0);
    for (int t = 0; t < steps; ++t) cells.insert(path[t]);
    (void)g;
    return (int)cells.size();
}
// Number of steps that go back to the cell two steps earlier (A -> B -> A), counting the start as the first position.
static int refGridBack(const int* path, int steps) {
    int back = 0;
    for (int t = 1; t < steps; ++t) back += path[t] == (t >= 2 ? path[t - 2] : 0);
    return back;
}
// Replays an order of points: returns the path length, or -1 if it is not a permutation.
static ll refRouteReplay(const Route& r, const int* path, int steps) {
    if (steps != r.n) return -1;
    std::vector<char> seen(r.n, 0);
    ll cost = 0;
    for (int t = 0; t < steps; ++t) {
        const int u = path[t];
        if (u < 0 || u >= r.n || seen[u]) return -1;
        seen[u] = 1;
        if (t > 0) cost += std::abs(r.px[u] - r.px[path[t - 1]]) + std::abs(r.py[u] - r.py[path[t - 1]]);
    }
    return cost;
}
static int rdist(const Route& r, int u, int v) { return std::abs(r.px[u] - r.px[v]) + std::abs(r.py[u] - r.py[v]); }
static std::vector<int> refNN(const Route& r) {
    std::vector<int> nn(r.n, 1 << 30);
    for (int u = 0; u < r.n; ++u) for (int v = 0; v < r.n; ++v) if (u != v) nn[u] = std::min(nn[u], rdist(r, u, v));
    return nn;
}

// A reference beam search written for this check: plain vectors, a full copy of the state and the path for every candidate,
// exact state comparison instead of hashing, sorting instead of a heap. The lesson's Beam must agree with it.
struct RS { std::vector<char> vis; int pos; ll g; std::vector<int> path; };
struct RefProblem {
    int steps;
    virtual ~RefProblem() {}
    virtual RS root() = 0;
    virtual std::vector<int> actions(const RS&) = 0;
    virtual ll evalChild(const RS&, int a) = 0;
    virtual ll refine(const RS&, int a) = 0;
    virtual RS apply(const RS&, int a) = 0;
    virtual ll score(const RS&) = 0;
    virtual int elems() = 0;
};
struct RefResult { ll score; std::vector<int> path; ll evals, refined, copiedWhole, copied, dropped, distinctSum, sizeSum; };

struct RefGrid : RefProblem {
    const Grid& g; int est, scale, radius;
    RefGrid(const Grid& gg) : g(gg), est(gg.est), scale(gg.scale), radius(gg.radius) { steps = gg.steps; }
    RS root() override { RS s; s.vis.assign(g.h * g.w, 0); s.vis[0] = 1; s.pos = 0; s.g = g.v[0]; return s; }
    std::vector<int> actions(const RS& s) override {
        std::vector<int> a;
        const int y = s.pos / g.w, x = s.pos % g.w;
        for (int k = 0; k < 4; ++k) { const int ny = y + DY[k], nx = x + DX[k]; if (ny >= 0 && ny < g.h && nx >= 0 && nx < g.w) a.push_back(ny * g.w + nx); }
        return a;
    }
    ll evalChild(const RS& s, int a) override {
        const ll got = s.g + (s.vis[a] ? 0 : g.v[a]);
        ll sum = 0; int nearest = 0;
        for (int c = 0; c < g.h * g.w; ++c) {
            const int d = std::abs(c / g.w - a / g.w) + std::abs(c % g.w - a % g.w);
            if (d < 1 || d > radius || s.vis[c]) continue;
            sum += (ll)g.v[c] * (radius + 1 - d);
            if (g.v[c] > 0 && (nearest == 0 || d < nearest)) nearest = d;
        }
        ll e = 0;
        if (est == 1) e = sum;
        if (est == 2) e = nearest > 0 ? -nearest : -(radius + 1);
        return got * scale + e;
    }
    ll refine(const RS&, int) override { return 0; }
    RS apply(const RS& s, int a) override {
        RS c = s;
        if (!c.vis[a]) { c.vis[a] = 1; c.g += g.v[a]; }
        c.pos = a; c.path.push_back(a);
        return c;
    }
    ll score(const RS& s) override { return s.g; }
    int elems() override { return Grid::ELEMS; }
};
struct RefRoute : RefProblem {
    const Route& r; int est; std::vector<int> nn;
    RefRoute(const Route& rr) : r(rr), est(rr.est), nn(refNN(rr)) { steps = rr.n; }
    RS root() override { RS s; s.vis.assign(r.n, 0); s.pos = -1; s.g = 0; return s; }
    std::vector<int> actions(const RS& s) override { std::vector<int> a; for (int u = 0; u < r.n; ++u) if (!s.vis[u]) a.push_back(u); return a; }
    ll evalChild(const RS& s, int a) override {
        const ll cost = s.g + (s.pos < 0 ? 0 : rdist(r, s.pos, a));
        ll rest = 0;
        for (int u = 0; u < r.n; ++u) if (!s.vis[u] && u != a) rest += nn[u];
        return -(cost + (est >= 1 ? rest : 0));
    }
    ll refine(const RS& s, int a) override {
        const ll cost = s.g + (s.pos < 0 ? 0 : rdist(r, s.pos, a));
        std::vector<char> done = s.vis; done[a] = 1;
        ll total = 0; int cur = a;
        for (;;) {
            int next = -1;
            for (int u = 0; u < r.n; ++u) if (!done[u] && (next < 0 || rdist(r, cur, u) < rdist(r, cur, next))) next = u;
            if (next < 0) break;
            total += rdist(r, cur, next); done[next] = 1; cur = next;
        }
        return -(cost + total);
    }
    RS apply(const RS& s, int a) override {
        RS c = s;
        c.g += s.pos < 0 ? 0 : rdist(r, s.pos, a);
        c.vis[a] = 1; c.pos = a; c.path.push_back(a);
        return c;
    }
    ll score(const RS& s) override { return -s.g; }
    int elems() override { return Route::ELEMS; }
};

static RefResult refBeam(RefProblem& p, int width, int refineK, int quota, int jitter, bool merge, unsigned seed) {
    hc::Random rng; rng.reset(seed);
    RefResult out; out.evals = out.refined = out.copiedWhole = out.copied = out.dropped = out.distinctSum = out.sizeSum = 0;
    std::vector<RS> beam; beam.push_back(p.root());
    struct RC { int parent, act; ll eval; RS child; bool dead; };
    for (int d = 0; d < p.steps; ++d) {
        std::vector<RC> C;
        for (size_t i = 0; i < beam.size(); ++i) {
            for (int a : p.actions(beam[i])) {
                RC c; c.parent = (int)i; c.act = a; c.dead = false;
                c.eval = p.evalChild(beam[i], a);
                if (jitter > 1) c.eval = c.eval * jitter + (ll)rng.below((unsigned)jitter);
                c.child = p.apply(beam[i], a);                          // every candidate gets a full copy with its path
                out.copiedWhole += p.elems() + (ll)c.child.path.size();
                C.push_back(c);
            }
        }
        out.evals += (ll)C.size();
        if (merge) {
            std::map<std::pair<std::vector<char>, int>, int> held;
            for (size_t i = 0; i < C.size(); ++i) {
                const std::pair<std::vector<char>, int> key(C[i].child.vis, C[i].child.pos);
                std::map<std::pair<std::vector<char>, int>, int>::iterator it = held.find(key);
                if (it == held.end()) { held[key] = (int)i; continue; }
                if (C[i].eval > C[it->second].eval) { C[it->second].dead = true; it->second = (int)i; } else C[i].dead = true;
            }
        }
        if (quota > 0) {
            std::map<int, std::vector<int> > byGroup;
            for (size_t i = 0; i < C.size(); ++i) if (!C[i].dead) byGroup[C[i].act].push_back((int)i);
            for (std::map<int, std::vector<int> >::iterator it = byGroup.begin(); it != byGroup.end(); ++it) {
                std::vector<int>& ids = it->second;
                std::stable_sort(ids.begin(), ids.end(), [&](int x, int y) { return C[x].eval > C[y].eval; });
                for (size_t t = (size_t)quota; t < ids.size(); ++t) C[ids[t]].dead = true;
            }
        }
        ll alive = 0;
        std::vector<int> order;
        for (size_t i = 0; i < C.size(); ++i) if (!C[i].dead) { order.push_back((int)i); ++alive; }
        std::stable_sort(order.begin(), order.end(), [&](int x, int y) { return C[x].eval > C[y].eval; });
        const int k = refineK > width ? refineK : width;
        if ((int)order.size() > k) order.resize(k);
        if (refineK > width) {
            for (int idx : order) C[idx].eval = p.refine(beam[C[idx].parent], C[idx].act);
            out.refined += (ll)order.size();
            std::sort(order.begin(), order.end(), [&](int x, int y) { return C[x].eval > C[y].eval || (C[x].eval == C[y].eval && x < y); });
            if ((int)order.size() > width) order.resize(width);
        }
        std::reverse(order.begin(), order.end());                       // the heap hands the survivors over worst first
        out.dropped += alive - (ll)order.size();
        out.sizeSum += (ll)order.size();
        std::set<std::pair<std::vector<char>, int> > distinct;
        std::vector<RS> next;
        for (int idx : order) {
            distinct.insert(std::make_pair(C[idx].child.vis, C[idx].child.pos));
            next.push_back(C[idx].child);
            out.copied += p.elems();
        }
        out.distinctSum += (ll)distinct.size();
        beam.swap(next);
    }
    int best = 0;
    for (size_t j = 1; j < beam.size(); ++j) if (p.score(beam[j]) > p.score(beam[best])) best = (int)j;
    out.score = p.score(beam[best]);
    out.path = beam[best].path;
    return out;
}

// ---------------------------------------------------------------- brute-force optima (independent of the lesson code)
static ll refRouteOptimum(const Route& r) {          // Held-Karp over subsets, start free, no return
    const int n = r.n;
    std::vector<std::vector<int> > dp(1 << n, std::vector<int>(n, 1 << 29));
    for (int j = 0; j < n; ++j) dp[1 << j][j] = 0;
    for (int m = 1; m < (1 << n); ++m) for (int j = 0; j < n; ++j) {
        if (!(m >> j & 1) || dp[m][j] >= (1 << 29)) continue;
        for (int k = 0; k < n; ++k) if (!(m >> k & 1)) dp[m | 1 << k][k] = std::min(dp[m | 1 << k][k], dp[m][j] + rdist(r, j, k));
    }
    int best = 1 << 29;
    for (int j = 0; j < n; ++j) best = std::min(best, dp[(1 << n) - 1][j]);
    return best;
}
static ll g_best;
static void walkAll(const Grid& g, std::vector<char>& seen, int pos, int t, ll got) {
    if (t == g.steps) { if (got > g_best) g_best = got; return; }
    const int y = pos / g.w, x = pos % g.w;
    for (int k = 0; k < 4; ++k) {
        const int ny = y + DY[k], nx = x + DX[k];
        if (ny < 0 || ny >= g.h || nx < 0 || nx >= g.w) continue;
        const int c = ny * g.w + nx;
        const char was = seen[c];
        seen[c] = 1;
        walkAll(g, seen, c, t + 1, got + (was ? 0 : g.v[c]));
        seen[c] = was;
    }
}
static ll refGridOptimum(const Grid& g) {           // every walk of the given length from cell 0
    std::vector<char> seen(g.h * g.w, 0);
    seen[0] = 1; g_best = 0;
    walkAll(g, seen, 0, 0, g.v[0]);
    return g_best;
}

// ---------------------------------------------------------------- helpers
static ull fnv(const int* v, int n, ull h = 1469598103934665603ULL) {
    for (int i = 0; i < n; ++i) { h ^= (ull)(unsigned)v[i]; h *= 1099511628211ULL; }
    return h;
}
static void setGrid(unsigned long long seed, int h, int w, int steps, int est, int scale, int radius) {
    genGrid(grid, seed, h, w, steps);
    grid.est = est; grid.scale = scale; grid.radius = radius;
}
template <class B>
static void setBeam(B& b, int width, int refineK, int quota, int jitter, bool merge) {
    b.width = width; b.refineK = refineK; b.quota = quota; b.jitter = jitter; b.merge = merge;
}
// Runs the lesson beam on the instance that is currently set up and compares everything with the reference.
// Returns 1 if any compared quantity differs, 0 if everything is identical.
static int diffGrid(unsigned seed, int width, int quota, int jitter, bool merge) {
    setBeam(gridBeam, width, 0, quota, jitter, merge);
    hc::Random rng; rng.reset(seed);
    const ll got = gridBeam.run(grid, rng);
    RefGrid rp(grid);
    const RefResult ref = refBeam(rp, width, 0, quota, jitter, merge, seed);
    int bad = 0;
    bad += got != ref.score;
    bad += std::memcmp(gridBeam.path, ref.path.data(), sizeof(int) * grid.steps) != 0;
    bad += gridBeam.evals != ref.evals || gridBeam.copied != ref.copied || gridBeam.copiedWhole != ref.copiedWhole || gridBeam.dropped != ref.dropped;
    bad += gridBeam.distinctSum != ref.distinctSum || gridBeam.sizeSum != ref.sizeSum;
    bad += refGridReplay(grid, gridBeam.path, grid.steps) != got;
    if (bad) fprintf(stderr, "grid mismatch seed %u est %d width %d quota %d jitter %d merge %d: score %lld/%lld evals %lld/%lld copied %lld/%lld whole %lld/%lld dropped %lld/%lld distinct %lld/%lld size %lld/%lld\n",
                     seed, grid.est, width, quota, jitter, (int)merge, got, ref.score, gridBeam.evals, ref.evals, gridBeam.copied, ref.copied, gridBeam.copiedWhole, ref.copiedWhole,
                     gridBeam.dropped, ref.dropped, gridBeam.distinctSum, ref.distinctSum, gridBeam.sizeSum, ref.sizeSum);
    return bad ? 1 : 0;
}
template <class B>
static int diffRoute(B& beam, unsigned seed, int width, int refineK, int quota, int jitter, bool merge) {
    setBeam(beam, width, refineK, quota, jitter, merge);
    hc::Random rng; rng.reset(seed);
    const ll got = beam.run(route, rng);
    RefRoute rp(route);
    const RefResult ref = refBeam(rp, width, refineK, quota, jitter, merge, seed);
    int bad = 0;
    bad += got != ref.score;
    bad += std::memcmp(beam.path, ref.path.data(), sizeof(int) * route.n) != 0;
    bad += beam.evals != ref.evals || beam.refined != ref.refined || beam.copied != ref.copied || beam.copiedWhole != ref.copiedWhole || beam.dropped != ref.dropped;
    bad += beam.distinctSum != ref.distinctSum || beam.sizeSum != ref.sizeSum;
    bad += -refRouteReplay(route, beam.path, route.n) != got;
    if (bad) fprintf(stderr, "route mismatch seed %u n %d est %d width %d refineK %d quota %d jitter %d merge %d: score %lld/%lld evals %lld/%lld refined %lld/%lld copied %lld/%lld whole %lld/%lld dropped %lld/%lld distinct %lld/%lld size %lld/%lld\n",
                     seed, route.n, route.est, width, refineK, quota, jitter, (int)merge, got, ref.score, beam.evals, ref.evals, beam.refined, ref.refined, beam.copied, ref.copied,
                     beam.copiedWhole, ref.copiedWhole, beam.dropped, ref.dropped, beam.distinctSum, ref.distinctSum, beam.sizeSum, ref.sizeSum);
    return bad ? 1 : 0;
}

// The whole battery of configurations the lesson claims to implement.
static int diffBattery(int* runs, unsigned maxSeed) {
    int bad = 0;
    *runs = 0;
    for (unsigned s = 1; s <= maxSeed; ++s) {
        for (int est = 0; est <= 2; ++est) for (int width : {1, 3, 8}) {
            setGrid(s, 20, 20, 60, est, 8, 3);
            bad += diffGrid(s, width, 0, 1, true); ++*runs;
        }
        const int cfg[][3] = {{8, 0, 1}, {8, 1, 1}, {8, 2, 1}, {8, 4, 1}, {8, 0, 4}, {8, 2, 16}, {32, 2, 1}, {32, 1, 1}};
        for (const auto& c : cfg) {
            for (int est : {0, 1}) {
                setGrid(s, 20, 20, 60, est, 8, 3);
                bad += diffGrid(s, c[0], c[1], c[2], true); ++*runs;
            }
        }
        setGrid(s, 20, 20, 60, 1, 8, 3); bad += diffGrid(s, 16, 0, 1, false); ++*runs;
        setGrid(s, 20, 20, 60, 0, 8, 3); bad += diffGrid(s, 16, 0, 1, false); ++*runs;
        setGrid(s, 4, 5, 9, 1, 3, 2); bad += diffGrid(s, 6, 0, 1, true); ++*runs;          // another size and other weights
        setGrid(s, 5, 5, 8, 2, 5, 4); bad += diffGrid(s, 1000, 0, 1, true); ++*runs;
        setGrid(s, 3, 3, 12, 1, 8, 1); bad += diffGrid(s, 5, 0, 1, true); ++*runs;
    }
    for (unsigned s = 1; s <= maxSeed; ++s) {
        for (int est = 0; est <= 1; ++est) {
            genRoute(route, s, 200); route.est = est;
            for (int width : {1, 3}) { bad += diffRoute(routeBeam, s, width, 0, 0, 1, true); ++*runs; }
            bad += diffRoute(routeBeam, s, 3, 0, 0, 1, false); ++*runs;
            bad += diffRoute(routeBeam, s, 3, 0, 1, 1, true); ++*runs;
            bad += diffRoute(routeBeam, s, 3, 0, 2, 4, true); ++*runs;
        }
        genRoute(route, s, 200); route.est = 2;
        bad += diffRoute(routeBeam, s, 1, 4, 0, 1, true); ++*runs;
        bad += diffRoute(routeBeam, s, 2, 6, 0, 1, true); ++*runs;
        for (int n : {6, 9}) for (int est = 0; est <= 2; ++est) {
            genRoute(route, s, n); route.est = est;
            bad += diffRoute(routeSmallBeam, s, 5, est == 2 ? 12 : 0, 0, 1, true); ++*runs;
            bad += diffRoute(routeSmallBeam, s, 1536, 0, 0, 1, true); ++*runs;
            bad += diffRoute(routeSmallBeam, s, 7, 0, 0, 1, false); ++*runs;
            bad += diffRoute(routeSmallBeam, s, 4, 0, 1, 1, true); ++*runs;
        }
    }
    return bad;
}

// ---------------------------------------------------------------- state keys: equal exact state <=> equal key
static int keyCheckGrid(int h, int w, int steps, ll* states) {
    typedef std::pair<std::vector<ull>, int> Exact;       // visited bits + position
    std::map<Exact, ull> keyOf;
    std::map<ull, Exact> exactOf;
    int bad = 0;
    setGrid(1, h, w, steps, 0, 1, 1);
    std::vector<GridState> level(1);
    grid.root(level[0]);
    std::set<Exact> seenStates;
    for (int d = 0; d < steps; ++d) {
        std::vector<GridState> next;
        for (const GridState& s : level) {
            int acts[4];
            const int na = grid.actions(s, acts);
            for (int k = 0; k < na; ++k) {
                Cand c; c.dead = false;
                grid.evalChild(s, acts[k], c);
                GridState t;
                grid.apply(s, acts[k], t);
                const Exact e(std::vector<ull>(t.vis, t.vis + 7), t.pos);
                std::map<Exact, ull>::iterator a = keyOf.find(e);
                if (a == keyOf.end()) keyOf[e] = c.key; else if (a->second != c.key) ++bad;        // same state, different key
                std::map<ull, Exact>::iterator b = exactOf.find(c.key);
                if (b == exactOf.end()) exactOf[c.key] = e; else if (!(b->second == e)) ++bad;     // different state, same key
                if (seenStates.insert(e).second) next.push_back(t);
            }
        }
        level = next;
    }
    *states = (ll)keyOf.size();
    return bad;
}
static int keyCheckRoute(int n, ll* states) {
    typedef std::pair<std::vector<ull>, int> Exact;
    std::map<Exact, ull> keyOf;
    std::map<ull, Exact> exactOf;
    int bad = 0;
    genRoute(route, 1, n); route.est = 0;
    std::vector<RouteState> level(1);
    route.root(level[0]);
    std::set<Exact> seenStates;
    for (int d = 0; d < n; ++d) {
        std::vector<RouteState> next;
        for (const RouteState& s : level) {
            int acts[200];
            const int na = route.actions(s, acts);
            for (int k = 0; k < na; ++k) {
                Cand c; c.dead = false;
                route.evalChild(s, acts[k], c);
                RouteState t;
                route.apply(s, acts[k], t);
                const Exact e(std::vector<ull>(t.vis, t.vis + 4), t.last);
                std::map<Exact, ull>::iterator a = keyOf.find(e);
                if (a == keyOf.end()) keyOf[e] = c.key; else if (a->second != c.key) ++bad;
                std::map<ull, Exact>::iterator b = exactOf.find(c.key);
                if (b == exactOf.end()) exactOf[c.key] = e; else if (!(b->second == e)) ++bad;
                if (seenStates.insert(e).second) next.push_back(t);
            }
        }
        level = next;
    }
    *states = (ll)keyOf.size();
    return bad;
}

// ---------------------------------------------------------------- the lower bound: sum of nn over the unvisited points never exceeds the best completion
static void lowerBound(ll* states, ll* violations, ll* tight) {
    *states = *violations = *tight = 0;
    for (unsigned s = 1; s <= 20; ++s) {
        const int n = 8;
        genRoute(route, s, n);
        const std::vector<int> nn = refNN(route);
        // rem[mask][last]: cheapest way to visit all points outside mask, standing at last
        std::vector<std::vector<int> > rem(1 << n, std::vector<int>(n, 1 << 29));
        for (int j = 0; j < n; ++j) rem[(1 << n) - 1][j] = 0;
        for (int m = (1 << n) - 2; m >= 1; --m) for (int j = 0; j < n; ++j) {
            if (!(m >> j & 1)) continue;
            for (int k = 0; k < n; ++k) if (!(m >> k & 1)) rem[m][j] = std::min(rem[m][j], rdist(route, j, k) + rem[m | 1 << k][k]);
        }
        for (int m = 1; m < (1 << n); ++m) for (int j = 0; j < n; ++j) {
            if (!(m >> j & 1)) continue;
            int h = 0;
            for (int u = 0; u < n; ++u) if (!(m >> u & 1)) h += nn[u];
            ++*states;
            if (h > rem[m][j]) ++*violations;
            if (h == rem[m][j]) ++*tight;
        }
    }
}

// ---------------------------------------------------------------- modes
static void modeGen() {
    for (int s = 1; s <= 20; ++s) {
        genGrid(grid, s, 20, 20, 60);
        printf("gen grid %d %llu\n", s, fnv(grid.v, 400));
        genRoute(route, s, 200);
        ull h = fnv(route.px, 200); h = fnv(route.py, 200, h);
        printf("gen route %d %llu\n", s, h);
    }
}

static void handGrid(const int* vals, int h, int w, int steps, int est, int scale, int radius, int width, bool merge) {
    genGrid(grid, 1, h, w, steps);
    for (int c = 0; c < h * w; ++c) grid.v[c] = vals[c];
    grid.est = est; grid.scale = scale; grid.radius = radius;
    setBeam(gridBeam, width, 0, 0, 1, merge);
    hc::Random rng; rng.reset(1);
    const ll got = gridBeam.run(grid, rng);
    printf("hand grid %d %d %d %d %d %lld %lld %lld", est, scale, radius, width, (int)merge, got, gridBeam.evals, gridBeam.dropped);
    for (int t = 0; t < steps; ++t) printf(" %d", gridBeam.path[t]);
    printf("\n");
}
static void handRoute(const int* xs, const int* ys, int n, int est, int width, bool merge) {
    genRoute(route, 1, n);
    for (int i = 0; i < n; ++i) { route.px[i] = xs[i]; route.py[i] = ys[i]; }
    route.prepare();
    route.est = est;
    setBeam(routeSmallBeam, width, 0, 0, 1, merge);
    hc::Random rng; rng.reset(1);
    const ll cost = -routeSmallBeam.run(route, rng);
    printf("hand route %d %d %d %lld %lld %lld", est, width, (int)merge, cost, routeSmallBeam.evals, routeSmallBeam.dropped);
    for (int t = 0; t < n; ++t) printf(" %d", routeSmallBeam.path[t]);
    printf("\n");
}
static void modeHand() {
    const int g[9] = {0, 6, 0, 0, 0, 0, 9, 8, 4};
    for (int width : {1, 2, 3}) handGrid(g, 3, 3, 4, 0, 1, 1, width, true);
    handGrid(g, 3, 3, 4, 1, 2, 1, 1, true);
    handGrid(g, 3, 3, 4, 1, 2, 1, 2, true);
    handGrid(g, 3, 3, 4, 0, 1, 1, 100, true);                 // wide enough to drop nothing: the full search
    const int xs[6] = {1, 6, 1, 9, 7, 2}, ys[6] = {1, 5, 7, 8, 4, 6};
    handRoute(xs, ys, 6, 0, 1, true);
    handRoute(xs, ys, 6, 0, 2, true);
    handRoute(xs, ys, 6, 1, 1, true);
    handRoute(xs, ys, 6, 1, 2, true);
    handRoute(xs, ys, 6, 1, 2, false);
    handRoute(xs, ys, 6, 1, 3, true);
    handRoute(xs, ys, 6, 1, 1536, true);
    printf("hand opt %lld\n", refRouteOptimum(route));
}

// mergeBySort (sorting, adjacent comparison) must kill exactly the candidates mergeSame (hash table) kills.
static Cand g_copy[51200];
static long long g_keyBuf[51200];
static int g_id[51200], g_tmp[51200];
template <class B>
static void compareMerges(B& beam, int* sets, int* mismatch, ll* duplicates) {
    const int C = beam.lastC;
    for (int i = 0; i < C; ++i) beam.cand[i].dead = false;
    for (int i = 0; i < C; ++i) g_copy[i] = beam.cand[i];
    beam.mergeSame(C);
    mergeBySort(g_copy, C, g_keyBuf, g_id, g_tmp);
    ++*sets;
    for (int i = 0; i < C; ++i) {
        if (beam.cand[i].dead != g_copy[i].dead) ++*mismatch;
        *duplicates += beam.cand[i].dead;
    }
}
static void modeMerges() {
    int sets = 0, mismatch = 0; ll dup = 0;
    for (unsigned s = 1; s <= 5; ++s) {
        genRoute(route, s, 200); route.est = 0; route.steps = 30;
        setBeam(routeBeam, 64, 0, 0, 1, false);
        hc::Random rng; rng.reset(s);
        routeBeam.run(route, rng);
        compareMerges(routeBeam, &sets, &mismatch, &dup);
        setGrid(s, 20, 20, 60, 0, 8, 3); grid.steps = 40;
        setBeam(gridBeam, 1024, 0, 0, 1, false);
        hc::Random rng2; rng2.reset(s);
        gridBeam.run(grid, rng2);
        compareMerges(gridBeam, &sets, &mismatch, &dup);
    }
    printf("merges %d %d %lld\n", sets, mismatch, dup);
}

// The same code paths on a smaller battery, for the sanitizer build (ASan/UBSan are slow).
static void modeMemory() {
    int runs = 0, sets = 0, mismatch = 0;
    const int bad = diffBattery(&runs, 1);
    ll gs, rs;
    const int keys = keyCheckGrid(3, 3, 6, &gs) + keyCheckRoute(6, &rs);
    ll dup = 0;
    genRoute(route, 1, 200); route.est = 0; route.steps = 30;
    setBeam(routeBeam, 64, 0, 0, 1, false);
    hc::Random rng; rng.reset(1);
    routeBeam.run(route, rng);
    compareMerges(routeBeam, &sets, &mismatch, &dup);
    printf("memory %d %d %d %d\n", runs, bad, keys, mismatch);
}

static void modeCorrect() {
    modeMerges();
    int runs = 0;
    const int bad = diffBattery(&runs, 3);
    printf("diff %d %d\n", runs, bad);
    int replayBad = 0, replays = 0;                         // the lesson's own replay functions against the references written here
    for (unsigned s = 1; s <= 5; ++s) {
        setGrid(s, 20, 20, 60, 1, 8, 3);
        setBeam(gridBeam, 4, 0, 0, 1, true);
        hc::Random rng; rng.reset(s);
        const ll got = gridBeam.run(grid, rng);
        replayBad += replayGrid(grid, gridBeam.path) != refGridReplay(grid, gridBeam.path, grid.steps) || replayGrid(grid, gridBeam.path) != got;
        int broken[60]; std::memcpy(broken, gridBeam.path, sizeof broken);
        broken[10] = (broken[10] + 7) % 400;                  // not a neighbouring cell any more (or a far one): both must say invalid
        replayBad += replayGrid(grid, broken) != refGridReplay(grid, broken, grid.steps);
        genRoute(route, s, 200); route.est = 1;
        setBeam(routeBeam, 4, 0, 0, 1, true);
        hc::Random rng2; rng2.reset(s);
        const ll cost = -routeBeam.run(route, rng2);
        int order[200]; std::memcpy(order, routeBeam.path, sizeof order);
        replayBad += replayRoute(route, order) != refRouteReplay(route, order, 200) || replayRoute(route, order) != cost;
        order[5] = order[6];                                  // a repeated point: both must say invalid
        replayBad += replayRoute(route, order) != refRouteReplay(route, order, 200);
        replays += 4;
    }
    printf("replay %d %d\n", replays, replayBad);
    ll gs, rs;
    const int kg = keyCheckGrid(3, 3, 6, &gs) + keyCheckGrid(2, 4, 7, &gs);
    ll gstates = gs;
    const int kr = keyCheckRoute(6, &rs);
    printf("keys %d %d %lld %lld\n", kg, kr, gstates, rs);
    ll st, vio, tight;
    lowerBound(&st, &vio, &tight);
    printf("lowerbound %lld %lld %lld\n", st, vio, tight);
}

// replay and optimum checks that the detect mode and the experiments share
static int replayMismatchesGrid(int est, int width) {            // default size, 20 seeds: how many returned paths replay to a different score
    int bad = 0;
    for (unsigned s = 1; s <= 20; ++s) {
        setGrid(s, 20, 20, 60, est, 8, 3);
        setBeam(gridBeam, width, 0, 0, 1, true);
        hc::Random rng; rng.reset(s);
        const ll got = gridBeam.run(grid, rng);
        bad += refGridReplay(grid, gridBeam.path, grid.steps) != got;
    }
    return bad;
}
static int replayMismatchesRoute(int est, int width) {
    int bad = 0;
    for (unsigned s = 1; s <= 20; ++s) {
        genRoute(route, s, 200); route.est = est;
        setBeam(routeBeam, width, 0, 0, 1, true);
        hc::Random rng; rng.reset(s);
        const ll got = routeBeam.run(route, rng);
        bad += -refRouteReplay(route, routeBeam.path, route.n) != got;
    }
    return bad;
}
static int optimumHitsRoute(int est, bool merge) {      // N = 10, a beam wider than the number of states: how many seeds reach the optimum
    int hits = 0;
    for (unsigned s = 1; s <= 20; ++s) {
        genRoute(route, s, 10); route.est = est;
        setBeam(routeSmallBeam, 1536, 0, 0, 1, merge);
        hc::Random rng; rng.reset(s);
        hits += -routeSmallBeam.run(route, rng) == refRouteOptimum(route);
    }
    return hits;
}

static void modeDetect() {
    int runs = 0;
    ll gs, rs;
    const int bad = diffBattery(&runs, 3);
    const int keys = keyCheckGrid(3, 3, 6, &gs) + keyCheckRoute(6, &rs);
    printf("D diff %d %d\n", runs, bad);
    printf("D keys %d\n", keys);
    printf("D replay %d %d\n", replayMismatchesGrid(1, 8), replayMismatchesRoute(1, 8));
    printf("D optimum %d %d\n", optimumHitsRoute(0, true), optimumHitsRoute(1, true));
    modeHand();
}

static void modeExp() {
    // E1: grid, estimate x width
    for (int est = 0; est <= 2; ++est) for (int width : {1, 2, 4, 8, 16, 64, 256, 1024}) for (unsigned s = 1; s <= 20; ++s) {
        setGrid(s, 20, 20, 60, est, 8, 3);
        setBeam(gridBeam, width, 0, 0, 1, true);
        hc::Random rng; rng.reset(s);
        const ll got = gridBeam.run(grid, rng);
        printf("G1 %d %d %u %lld %lld %lld %lld %lld %lld\n", est, width, s, got, gridBeam.evals, grid.work, gridBeam.copied, gridBeam.copiedWhole, refGridReplay(grid, gridBeam.path, grid.steps));
    }
    for (int est = 0; est <= 2; ++est) for (int width : {1, 2}) for (unsigned s = 1; s <= 20; ++s) {
        setGrid(s, 20, 20, 60, est, 8, 3);
        setBeam(gridBeam, width, 0, 0, 1, true);
        hc::Random rng; rng.reset(s);
        gridBeam.run(grid, rng);
        printf("G4 %d %d %u %d %d\n", est, width, s, refGridDistinct(grid, gridBeam.path, grid.steps), refGridBack(gridBeam.path, grid.steps));
    }
    // E2: the weight of one point and the radius
    for (int scale : {1, 2, 4, 8, 16}) for (int width : {1, 4, 16}) for (unsigned s = 1; s <= 20; ++s) {
        setGrid(s, 20, 20, 60, 1, scale, 3);
        setBeam(gridBeam, width, 0, 0, 1, true);
        hc::Random rng; rng.reset(s);
        const ll got = gridBeam.run(grid, rng);
        printf("G2 scale %d %d %u %lld %lld\n", scale, width, s, got, refGridReplay(grid, gridBeam.path, grid.steps));
    }
    for (int radius : {1, 2, 3, 5}) for (int width : {1, 4, 16}) for (unsigned s = 1; s <= 20; ++s) {
        setGrid(s, 20, 20, 60, 1, 8, radius);
        setBeam(gridBeam, width, 0, 0, 1, true);
        hc::Random rng; rng.reset(s);
        const ll got = gridBeam.run(grid, rng);
        printf("G2 radius %d %d %u %lld %lld\n", radius, width, s, got, refGridReplay(grid, gridBeam.path, grid.steps));
    }
    // E3: diversity on the grid
    struct Cfg { const char* name; bool merge; int quota, jitter; };
    const Cfg cfgs[] = {{"base", true, 0, 1}, {"nomerge", false, 0, 1}, {"q1", true, 1, 1}, {"q2", true, 2, 1}, {"q4", true, 4, 1}, {"j4", true, 0, 4}, {"j16", true, 0, 16}};
    for (const Cfg& c : cfgs) for (int width : {16, 64}) for (int est : {0, 1}) for (unsigned s = 1; s <= 20; ++s) {
        setGrid(s, 20, 20, 60, est, 8, 3);
        setBeam(gridBeam, width, 0, c.quota, c.jitter, c.merge);
        hc::Random rng; rng.reset(s);
        const ll got = gridBeam.run(grid, rng);
        printf("G3 %s %d %d %u %lld %lld %lld %lld\n", c.name, est, width, s, got, gridBeam.distinctSum, gridBeam.sizeSum, refGridReplay(grid, gridBeam.path, grid.steps));
    }
    // E5: route, estimate x width
    for (int est = 0; est <= 2; ++est) {
        const std::vector<int> widths = est == 2 ? std::vector<int>{1, 2, 4, 8} : std::vector<int>{1, 2, 4, 8, 16, 64, 256};
        for (int width : widths) for (unsigned s = 1; s <= 20; ++s) {
            genRoute(route, s, 200); route.est = est;
            setBeam(routeBeam, width, est == 2 ? 4 * width : 0, 0, 1, true);
            hc::Random rng; rng.reset(s);
            const ll cost = -routeBeam.run(route, rng);
            printf("R1 %d %d %u %lld %lld %lld %lld %lld %lld\n", est, width, s, cost, routeBeam.evals, routeBeam.refined, route.work, routeBeam.copied, routeBeam.copiedWhole);
            if (refRouteReplay(route, routeBeam.path, route.n) != cost) printf("R1 replay mismatch\n");
        }
    }
    // E6: route diversity
    for (int est : {0, 1}) for (int width : {4, 16, 64}) for (int variant = 0; variant < 4; ++variant) for (unsigned s = 1; s <= 20; ++s) {
        genRoute(route, s, 200); route.est = est;
        setBeam(routeBeam, width, 0, variant == 2 ? 1 : (variant == 3 ? 2 : 0), 1, variant != 1);
        hc::Random rng; rng.reset(s);
        const ll cost = -routeBeam.run(route, rng);
        printf("R2 %d %d %d %u %lld %lld %lld\n", variant, est, width, s, cost, routeBeam.distinctSum, routeBeam.sizeSum);
        if (refRouteReplay(route, routeBeam.path, route.n) != cost) printf("R2 replay mismatch\n");
    }
    // E7: small inputs against the optimum
    for (int est : {0, 1}) for (int merge = 1; merge >= 0; --merge) for (int width : {1, 2, 4, 8, 16, 64, 256, 1536}) for (unsigned s = 1; s <= 20; ++s) {
        genRoute(route, s, 10); route.est = est;
        setBeam(routeSmallBeam, width, 0, 0, 1, merge != 0);
        hc::Random rng; rng.reset(s);
        const ll cost = -routeSmallBeam.run(route, rng);
        printf("S1 %d %d %d %u %lld %lld %lld\n", est, merge, width, s, cost, refRouteOptimum(route), routeSmallBeam.dropped);
    }
    for (int est : {0, 1}) for (int width : {1, 2, 4, 8, 16, 64, 256}) for (unsigned s = 1; s <= 20; ++s) {
        setGrid(s, 6, 6, 10, est, 8, 3);
        setBeam(gridBeam, width, 0, 0, 1, true);
        hc::Random rng; rng.reset(s);
        const ll got = gridBeam.run(grid, rng);
        printf("S2 %d %d %u %lld %lld %lld\n", est, width, s, got, refGridOptimum(grid), gridBeam.dropped);
    }
    for (int est : {0, 1}) for (int width : {1, 2, 4, 8, 8192}) for (unsigned s = 1; s <= 20; ++s) {     // 5 x 5, T = 8: the optimum is recomputed in Python too, and 8192 never drops a state
        setGrid(s, 5, 5, 8, est, 8, 3);
        setBeam(gridBeam, width, 0, 0, 1, true);
        hc::Random rng; rng.reset(s);
        const ll got = gridBeam.run(grid, rng);
        printf("S3 %d %d %u %lld %lld %lld\n", est, width, s, got, refGridOptimum(grid), gridBeam.dropped);
    }
}

int main(int argc, char** argv) {
    const std::string mode = argc > 1 ? argv[1] : "";
    if (mode == "gen") modeGen();
    else if (mode == "correct") modeCorrect();
    else if (mode == "detect") modeDetect();
    else if (mode == "hand") modeHand();
    else if (mode == "memory") modeMemory();
    else if (mode == "exp") modeExp();
    else { fprintf(stderr, "unknown mode\n"); return 1; }
    return 0;
}
