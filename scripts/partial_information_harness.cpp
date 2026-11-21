// Harness for the partial-information check. Standard headers are fine here; the lesson code is included below.
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
static ull fnv(const int* v, int n, ull h = 1469598103934665603ULL) {
    for (int i = 0; i < n; ++i) { h ^= (ull)(unsigned)v[i]; h *= 1099511628211ULL; }
    return h;
}

// Replays a grid walk from the true values: returns the score, or -1 if a step is not to a neighbouring cell.
static ll refGridScore(const GridJudge& g, const int* moves) {
    std::vector<char> seen(g.h * g.w, 0);
    int pos = 0;
    ll sum = g.v[0];
    seen[0] = 1;
    for (int t = 0; t < g.T; ++t) {
        const int c = moves[t];
        if (c < 0 || c >= g.h * g.w) return -1;
        if (std::abs(c / g.w - pos / g.w) + std::abs(c % g.w - pos % g.w) != 1) return -1;
        pos = c;
        if (!seen[c]) { seen[c] = 1; sum += g.v[c]; }
    }
    return sum;
}

// Independent cost of an assignment (to[i] = machine of task i); -1 if a machine gets more than k tasks.
static ll refOnlineCost(const OnlineJudge& j, const int* to) {
    std::vector<ll> load(j.m, 0), cnt(j.m, 0);
    ll c = 0;
    for (int i = 0; i < j.n; ++i) {
        if (to[i] < 0 || to[i] >= j.m) return -1;
        load[to[i]] += j.d[i]; ++cnt[to[i]]; c += j.c[i][to[i]];
    }
    ll sq = 0;
    for (int q = 0; q < j.m; ++q) { if (cnt[q] > j.k) return -1; sq += load[q] * load[q]; }
    return sq / 100 + c;
}

// Best total gain (x100) over all depth-step walks from pos (revisits allowed, gain only at a first visit): plain recursion.
static ll bruteBest(const int* map100, std::vector<char>& vis, int h, int w, int pos, int depth) {
    if (depth == 0) return 0;
    ll best = -1;
    const int y = pos / w, x = pos % w;
    int nb[4], k = 0;
    if (y > 0) nb[k++] = pos - w;
    if (x + 1 < w) nb[k++] = pos + 1;
    if (y + 1 < h) nb[k++] = pos + w;
    if (x > 0) nb[k++] = pos - 1;
    for (int q = 0; q < k; ++q) {
        const int a = nb[q];
        const bool fresh = !vis[a];
        if (fresh) vis[a] = 1;
        const ll v = (fresh ? map100[a] : 0) + bruteBest(map100, vis, h, w, a, depth - 1);
        if (fresh) vis[a] = 0;
        if (v > best) best = v;
    }
    return best;
}

// ---------------------------------------------------------------- modes
static void modeGen() {
    const int zs[3] = {6, 9, 2};
    for (int zi = 0; zi < 3; ++zi) {
        for (int s = 1; s <= 20; ++s) {
            genGrid(gridJ, s, 20, 20, 60, 2, zs[zi]);
            ll sum = 0; for (int c = 0; c < 400; ++c) sum += gridJ.v[c];
            printf("gen grid %d %d %llu %lld\n", zs[zi], s, fnv(gridJ.v, 400), sum);
        }
    }
    const int ds[2] = {100, 20};
    for (int di = 0; di < 2; ++di) {
        for (int s = 1; s <= 20; ++s) {
            genOnline(onJ, s, 120, 8, 18, ds[di]);
            ull h = fnv(onJ.d, 120);
            for (int i = 0; i < 120; ++i) h = fnv(onJ.c[i], 8, h);
            printf("gen online %d %d %llu %lld %lld\n", ds[di], s, h, roundRobin(onJ), lowerBound(onJ));
        }
    }
}

// Default runs replayed by the independent reference; mirror and map checks; peeking test.
static void modeRef() {
    int mv[400];
    for (int cfg = 0; cfg < 4; ++cfg) {
        const int rad = cfg == 0 ? 2 : cfg == 1 ? 1 : cfg == 2 ? 99 : 0;
        for (int s = 1; s <= 20; ++s) {
            genGrid(gridJ, s, 20, 20, 60, rad, 6);
            gridP.est100 = cfg == 3 ? 0 : -1; gridP.horizon = 12; gridP.period = cfg == 1 ? 12 : 1; gridP.width = 16;
            int bad = -2;
            const ll score = playGrid(gridJ, gridM, gridP, mv, &bad);
            const ll ref = refGridScore(gridJ, mv);
            const int peek = gridNoPeek(gridJ, gridM, gridP) ? 1 : 0;
            printf("ref grid %d %d %lld %lld %d %d\n", cfg, s, score, ref, bad, peek);
        }
    }
    int to[120];
    for (int cfg = 0; cfg < 6; ++cfg) {
        const int fut = cfg == 0 ? FUT_OFF : cfg == 1 ? 0 : cfg == 2 ? FUT_MEAN : cfg == 3 ? 100 : cfg == 4 ? 1 : FUT_MEAN;
        const int dmax = cfg == 5 ? 20 : 100;
        for (int s = 1; s <= 20; ++s) {
            genOnline(onJ, s, 120, 8, 18, dmax);
            onP.fut = fut;
            int bad = -2;
            const ll cost = playOnline(onJ, onM, onP, to, &bad);
            const ll ref = refOnlineCost(onJ, to);
            const int peek = onlineNoPeek(onJ, onM, onP, 100) ? 1 : 0;
            printf("ref online %d %d %lld %lld %d %d\n", cfg, s, cost, ref, bad, peek);
        }
    }
}

// planBeam with a width that never prunes equals brute force; planFull's path replays to its score.
static void modeBeam() {
    long long cases = 0, bad = 0;
    for (int s = 1; s <= 20; ++s) {
        Gen r; r.reset((ull)s * 7919);
        for (int variant = 0; variant < 6; ++variant) {
            const int h = 4 + (variant & 1), w = 5, depth = variant < 3 ? 4 : 3;
            int map100[GN]; bool stepped[GN]; std::vector<char> vis(GN, 0);
            for (int c = 0; c < h * w; ++c) { map100[c] = 100 * (r.next(10) < 5 ? 0 : 1 + r.next(9)); stepped[c] = false; }
            const int pos = variant < 3 ? 0 : r.next(h * w);
            stepped[pos] = true; vis[pos] = 1;
            if (variant == 2 || variant == 5) { int o = r.next(h * w); if (o != pos) { stepped[o] = true; vis[o] = 1; } }
            int path[BD]; long long ev = 0;
            const ll got = planBeam(map100, stepped, h, w, pos, depth, BW, path, ev);
            const ll want = bruteBest(map100, vis, h, w, pos, depth);
            // the path must replay to the value
            std::vector<char> v2 = vis; ll sum = 0; int cur = pos; bool ok = true;
            for (int t = 0; t < depth; ++t) {
                const int c = path[t];
                if (std::abs(c / w - cur / w) + std::abs(c % w - cur % w) != 1) ok = false;
                if (!v2[c]) { v2[c] = 1; sum += map100[c]; }
                cur = c;
            }
            ++cases;
            if (got != want || sum != got || !ok) ++bad;
        }
    }
    printf("beam %lld %lld\n", cases, bad);
    // planFull path replays to its score; wider is not guaranteed better, only valid
    for (int s = 1; s <= 20; ++s) {
        genGrid(gridJ, s, 20, 20, 60, 2, 6);
        int path[BD]; long long ev = 0;
        const ll score = planFull(gridJ, 16, path, ev);
        int mv[64]; for (int t = 0; t < 60; ++t) mv[t] = path[t];
        printf("full %d %lld %lld\n", s, score, refGridScore(gridJ, mv));
    }
}

// Hand example: 5 x 5 grid, start 0, T = 4 (see the lesson). Prints the first observation, plan values per estimate and the mirror after steps.
static const int HAND_GRID[25] = {0, 3, 0, 5, 0,
                                  2, 0, 0, 0, 1,
                                  0, 0, 6, 0, 0,
                                  0, 4, 0, 0, 0,
                                  7, 0, 0, 2, 0};
static void modeHand() {
    gridJ.h = 5; gridJ.w = 5; gridJ.T = 4; gridJ.rad = 2;
    for (int c = 0; c < 25; ++c) gridJ.v[c] = HAND_GRID[c];
    gridJ.start(); gridM.begin(gridJ); gridM.observe(gridJ);
    printf("hand seen %d %lld\n", gridM.nSeen, gridM.sumSeen);
    gridP.est100 = -1;
    printf("hand mean100 %d\n", gridP.guess100(gridM));
    const int ests[3] = {0, -1, 900};
    for (int e = 0; e < 3; ++e) {
        gridP.est100 = ests[e];
        int map100[GN]; gridP.buildMap(gridM, map100);
        int path[BD]; long long ev = 0;
        const ll g = planBeam(map100, gridM.stepped, 5, 5, 0, 4, BW, path, ev);
        std::vector<char> vis(GN, 0); vis[0] = 1;
        printf("hand plan %d %lld %lld %d %d %d %d\n", ests[e], g, ev, path[0], path[1], path[2], path[3]);
    }
    // walk right, right (cells 1, 2) and then down (cell 7), updating the mirror each time
    const int walk[3] = {1, 2, 7};
    for (int k = 0; k < 3; ++k) {
        gridJ.move(walk[k]); gridM.step(walk[k]); gridM.observe(gridJ);
        printf("hand mirror %d %d %lld %d %lld", k + 1, gridM.nSeen, gridM.sumSeen, gridM.pos, gridM.got);
        printf(" mean100 %d\n", (int)(100 * gridM.sumSeen / gridM.nSeen));
    }
    printf("hand mirrorok %d\n", gridMirrorOk(gridJ, gridM) ? 1 : 0);
    // seenAt after the walk
    for (int c = 0; c < 25; ++c) printf("%d%c", gridM.seenAt[c], c == 24 ? '\n' : ' ');
    // online hand example: tasks 6, machines 3, k = 3
    const int dd[6] = {36, 39, 46, 35, 53, 5};
    const int cc[6][3] = {{0, 42, 46}, {32, 50, 20}, {20, 26, 0}, {40, 45, 33}, {46, 19, 19}, {21, 1, 12}};
    onJ.n = 6; onJ.m = 3; onJ.k = 3;
    for (int i = 0; i < 6; ++i) { onJ.d[i] = dd[i]; for (int q = 0; q < 3; ++q) onJ.c[i][q] = cc[i][q]; }
    const int futs[3] = {FUT_OFF, FUT_MEAN, 100};
    (void)futs;
    for (int f = 0; f < 2; ++f) {
        onP.fut = f == 0 ? FUT_OFF : FUT_MEAN;
        onJ.start(); onM.begin(onJ);
        int len, row[AM];
        while (onJ.arrive(len, row)) {
            onM.observe(len, row);
            const ll lam = onP.lambda(onM);
            printf("hand online %d %d %lld", f, onM.seen, lam);
            for (int q = 0; q < 3; ++q) {
                const ll before = onM.load[q] > lam ? onM.load[q] : lam, after = onM.load[q] + len > lam ? onM.load[q] + len : lam;
                printf(" %lld", 100LL * row[q] + after * after - before * before);
            }
            const int q = onP.act(onM);
            printf(" -> %d\n", q);
            onJ.assign(q); onM.commit(q);
        }
        printf("hand onlinecost %d %lld %d %d %d\n", f, onJ.score(), onJ.load[0], onJ.load[1], onJ.load[2]);
    }
    printf("hand offline %lld %lld %lld %lld\n", offlineGreedy(onJ, false), offlineGreedy(onJ, true), lowerBound(onJ), roundRobin(onJ));
}

// ---------------------------------------------------------------- experiments
static void modeExp() {
    const int INFR = 99;
    auto runG = [&](const char* tag, int rad, int est, int H, int per, int W, int z) {
        for (int s = 1; s <= 20; ++s) {
            const ll sc = runGrid(s, rad, est, H, per, W, z);
            printf("G %s %d %d %d %d %d %d %d %lld %d %lld %lld\n", tag, rad, est, H, per, W, z, s, sc, gridM.nSeen, gridP.evals, gridP.plans);
        }
    };
    const int ests[6] = {0, 100, -1, 300, 500, 900};
    for (int e = 0; e < 6; ++e) runG("est", 2, ests[e], 12, 1, 16, 6);
    const int ests1[3] = {0, -1, 900};
    for (int e = 0; e < 3; ++e) runG("est1", 1, ests1[e], 12, 1, 16, 6);
    const int rads[7] = {0, 1, 2, 3, 4, 5, INFR};
    for (int r = 0; r < 7; ++r) runG("rad", rads[r], -1, 12, 1, 16, 6);
    const int pers[6] = {1, 2, 3, 4, 6, 12};
    for (int p = 0; p < 6; ++p) runG("per", 2, -1, 12, pers[p], 16, 6);
    const int hs[5] = {2, 4, 8, 12, 20};
    for (int h = 0; h < 5; ++h) runG("hor", 2, -1, hs[h], 1, 16, 6);
    const int ws[4] = {1, 4, 16, 64};
    for (int w = 0; w < 4; ++w) runG("wid", 2, -1, 12, 1, ws[w], 6);
    const int zs[3] = {2, 6, 9};
    const int ed[3] = {0, -1, 900};
    for (int z = 0; z < 3; ++z) for (int e = 0; e < 3; ++e) runG("den", 2, ed[e], 12, 1, 16, zs[z]);
    // full information
    for (int z = 0; z < 3; ++z) {
        for (int w : {16, 64}) {
            for (int s = 1; s <= 20; ++s) {
                genGrid(gridJ, s, 20, 20, 60, 2, zs[z]);
                int path[BD]; long long ev = 0;
                const ll sc = planFull(gridJ, w, path, ev);
                int mv[64]; for (int t = 0; t < 60; ++t) mv[t] = path[t];
                std::vector<int> v(gridJ.v, gridJ.v + 400); std::sort(v.rbegin(), v.rend());
                ll ub = 0; for (int i = 0; i < 61; ++i) ub += v[i];
                printf("F %d %d %d %lld %lld %lld %lld\n", w, zs[z], s, sc, refGridScore(gridJ, mv), ev, ub);
            }
        }
    }
    // online
    const int futs[5] = {FUT_OFF, 0, 1, FUT_MEAN, 100};
    for (int dmax : {100, 20}) {
        for (int f = 0; f < 5; ++f) for (int s = 1; s <= 20; ++s) {
            const ll cost = runOnline(s, futs[f], dmax);
            int to[120]; onP.fut = futs[f];
            const ll again = playOnline(onJ, onM, onP, to, 0);
            printf("A %d %d %d %lld %lld\n", futs[f], dmax, s, cost, refOnlineCost(onJ, to) == again ? again : -1);
        }
        for (int s = 1; s <= 20; ++s) {
            genOnline(onJ, s, 120, 8, 18, dmax);
            printf("O %d %d %lld %lld %lld %lld\n", dmax, s, roundRobin(onJ), offlineGreedy(onJ, false), offlineGreedy(onJ, true), lowerBound(onJ));
        }
    }
}

// ---------------------------------------------------------------- injected mistakes
static void modeDetect() {
    for (int s = 1; s <= 20; ++s) {
        genGrid(gridJ, s, 20, 20, 60, 2, 6);
        gridP.est100 = -1; gridP.horizon = 12; gridP.period = 1; gridP.width = 16;
        int bad = -2;
        const ll sc = playGrid(gridJ, gridM, gridP, 0, &bad);
        const int peek = gridNoPeek(gridJ, gridM, gridP) ? 1 : 0;
        printf("D grid %d %d %d %lld\n", s, bad, peek, sc);
    }
    for (int s = 1; s <= 20; ++s) {
        genOnline(onJ, s, 120, 8, 18, 100);
        onP.fut = FUT_MEAN;
        int bad = -2;
        const ll cost = playOnline(onJ, onM, onP, 0, &bad);
        const int peek = onlineNoPeek(onJ, onM, onP, 100) ? 1 : 0;
        printf("D online %d %d %d %lld\n", s, bad, peek, cost);
    }
}

int main(int argc, char** argv) {
    const std::string mode = argc > 1 ? argv[1] : "";
    if (mode == "gen") modeGen();
    else if (mode == "ref") modeRef();
    else if (mode == "beam") modeBeam();
    else if (mode == "hand") modeHand();
    else if (mode == "exp") modeExp();
    else if (mode == "detect") modeDetect();
    else { fprintf(stderr, "unknown mode\n"); return 2; }
    return 0;
}
