// ls.cpp - local search for (3,k,n)-graphs (triangle-free, alpha < k), n <= 64.
// Agent: anneal. Objective f = wK*I_k + w9*I_{k-1} + wT*T
//   I_k = number of independent k-sets, T = number of triangles (0 in hard mode).
// Flip delta of pair uv uses only the common non-neighbourhood C(u,v):
//   independent k-sets that contain u and v  <->  independent (k-2)-sets of C(u,v).
// Methods: sa (simulated annealing, random + focused moves), tabu (best of a sampled
// neighbourhood). Hard triangle mode uses compound moves: add uv and delete one
// edge to each common neighbour.
#include <bits/stdc++.h>
using namespace std;
typedef uint64_t u64;
typedef int64_t i64;

static int N, K;
static u64 adj[64];
static u64 ALLV;
static inline int pc(u64 x) { return __builtin_popcountll(x); }
static inline int ctz(u64 x) { return __builtin_ctzll(x); }

// a += #independent m-subsets of P, b += #independent (m-1)-subsets of P
static void rec(u64 P, int m, i64 &a, i64 &b) {
    int p = pc(P);
    if (m == 1) { a += p; b += 1; return; }
    if (m == 2) {
        int e = 0;
        u64 Q = P;
        while (Q) { int v = ctz(Q); Q &= Q - 1; e += pc(adj[v] & Q); }
        a += (i64)p * (p - 1) / 2 - e;
        b += p;
        return;
    }
    if (p < m - 1) return;
    u64 Q = P;
    while (pc(Q) >= m - 1) {
        int v = ctz(Q);
        Q &= Q - 1;
        rec(Q & ~adj[v], m - 1, a, b);
    }
}

// only #independent m-subsets of P (faster, used when w9 == 0)
static i64 recA(u64 P, int m) {
    if (m == 2) {
        int p = pc(P), e = 0;
        u64 Q = P;
        while (Q) { int v = ctz(Q); Q &= Q - 1; e += pc(adj[v] & Q); }
        return (i64)p * (p - 1) / 2 - e;
    }
    if (m == 1) return pc(P);
    if (m == 0) return 1;
    i64 a = 0;
    u64 Q = P;
    while (pc(Q) >= m) { int v = ctz(Q); Q &= Q - 1; a += recA(Q & ~adj[v], m - 1); }
    return a;
}

// ---------------- RNG ----------------
static u64 rs[2];
static inline u64 rnd64() {
    u64 s1 = rs[0]; const u64 s0 = rs[1];
    rs[0] = s0; s1 ^= s1 << 23;
    rs[1] = s1 ^ s0 ^ (s1 >> 17) ^ (s0 >> 26);
    return rs[1] + s0;
}
static inline int rndi(int m) { return (int)((rnd64() >> 11) % (u64)m); }
static inline double rndu() { return (rnd64() >> 11) * (1.0 / 9007199254740992.0); }

// ---------------- parameters ----------------
struct Params {
    int n = 40, k = 10;
    u64 seed = 1;
    string method = "sa";
    i64 wK = 64, w9 = 1, wT = 0;   // wT = 0 -> hard triangle-free
    i64 wD = 0; int softcap = -1;
    i64 wX = 0; i64 emax = 1 << 20;   // edge-count penalty   // soft degree penalty wD per unit above softcap (-1 -> k-1)
    int maxdeg = 9;                 // degree cap for random start
    int degcap = -1;                // hard degree cap in moves (-1 -> k-1, 0 -> none)
    double T0 = 4.0, T1 = 0.5;      // temperature range (in units of score)
    i64 sweep = 2000000;            // moves per anneal cycle
    double focus = 0.5;             // prob of focused move (from a bad set)
    double timelimit = 600;         // seconds
    string init = "random";         // random | file:<g6 path> | empty
    string out = "";                // prefix for log/checkpoint files
    int addv = 0;                   // with file init of n-1 vertices: add new vertex
    int tabuLen = 10;
    int tabuSample = 200;
    int stopOnFound = 1;
    double perturb = 0.05;          // fraction of pairs flipped on restart from best
    int symm = 0, symf = 0;         // symmetric mode: Z_m acting on blocks of size m, symf fixed points
    int restartRandom = 0;
    int bench = 0;
    int dlo = 0, dhi = 9;           // degree window (B3); dlo = 0 -> off
    double pswap = 0.5;             // prob of a degree-preserving double-edge swap (window mode)
    i64 sawPeriod = 0; double sawMin = 1, sawMax = 13;  // sawtooth triangle weight (needs soft triangles)
    int addvr = 1;                  // file init with fewer vertices: add vertices by exact VR (else greedy)
    int grow0 = 0;                  // grow mode: start at n = grow0, add a vertex (exact VR) after each solution
    double levelTime = 300;         // grow mode: give up a level after this many seconds
    double vr = 0;                  // prob per move of a vertex-rewiring move
    int vrSlack = 0;                // allow rewiring with up to this many extra bad sets                  // on found: log, fresh random restart, continue          // 1 = random restart each cycle instead of perturb-best
} P;

// ---------------- state ----------------
static i64 cntK, cntK1, cntT, cntE;  // cntE = sum of max(0, deg - softcap)
static i64 nEdges;                   // edge count; penalty wX per edge above emax
static inline i64 score() { return P.wK * cntK + P.w9 * cntK1 + P.wT * cntT + P.wD * cntE + P.wX * max<i64>(0, nEdges - P.emax); }

static void fullCount() {
    i64 a = 0, b = 0;
    rec(ALLV, K, a, b);
    cntK = a; cntK1 = P.w9 ? b : 0;  // K1 is not tracked when w9 == 0
    i64 t = 0;
    for (int u = 0; u < N; u++)
        for (int v = u + 1; v < N; v++)
            if (adj[u] >> v & 1) t += pc(adj[u] & adj[v] & ~((2ULL << v) - 1));
    cntT = t;
    cntE = 0; nEdges = 0;
    for (int u = 0; u < N; u++) { cntE += max(0, pc(adj[u]) - P.softcap); nEdges += pc(adj[u]); }
    nEdges /= 2;
}

// delta of score if pair uv is toggled (computed before the toggle)
struct D { i64 dK, dK1, dT, dE, dX;
    i64 s() const { return P.wK * dK + P.w9 * dK1 + P.wT * dT + P.wD * dE
                    + P.wX * (max<i64>(0, nEdges + dX - P.emax) - max<i64>(0, nEdges - P.emax)); } };
static inline D pairDelta(int u, int v) {
    u64 C = ALLV & ~(adj[u] | adj[v] | (1ULL << u) | (1ULL << v));
    i64 a = 0, b = 0;
    if (P.w9) rec(C, K - 2, a, b); else a = recA(C, K - 2);
    int com = pc(adj[u] & adj[v]);
    int du = pc(adj[u]), dv = pc(adj[v]);
    if (adj[u] >> v & 1) return D{a, b, -com, -(i64)(du > P.softcap) - (dv > P.softcap), -1};
    return D{-a, -b, com, (i64)(du >= P.softcap) + (dv >= P.softcap), 1};
}
static inline void toggle(int u, int v, const D &d) {
    adj[u] ^= 1ULL << v; adj[v] ^= 1ULL << u;
    cntK += d.dK; cntK1 += d.dK1; cntT += d.dT; cntE += d.dE; nEdges += d.dX;
}

// move = list of toggles; apply sequentially computing deltas
struct Tog { int u, v; D d; };
static vector<Tog> mv;
static i64 applyCompoundAdd(int u, int v) {
    // add uv; in hard mode first delete an edge to each common neighbour
    mv.clear();
    i64 tot = 0;
    if (P.wT == 0) {
        u64 W = adj[u] & adj[v];
        while (W) {
            int x = ctz(W); W &= W - 1;
            int y = (rnd64() & 1) ? u : v;
            D d = pairDelta(x, y); tot += d.s(); toggle(x, y, d); mv.push_back({x, y, d});
        }
    }
    // degree cap: delete a random edge at an endpoint that is full
    for (int side = 0; side < 2 && P.degcap > 0; side++) {
        int a = side ? v : u;
        if (pc(adj[a]) >= P.degcap) {
            u64 Na = adj[a] & ~(1ULL << u) & ~(1ULL << v);
            int c = pc(Na), r = rndi(c);
            while (r--) Na &= Na - 1;
            int x = ctz(Na);
            D d = pairDelta(a, x); tot += d.s(); toggle(a, x, d); mv.push_back({a, x, d});
        }
    }
    D d = pairDelta(u, v); tot += d.s(); toggle(u, v, d); mv.push_back({u, v, d});
    return tot;
}
static i64 applyRemove(int u, int v) {
    mv.clear();
    D d = pairDelta(u, v); i64 ds = d.s(); toggle(u, v, d); mv.push_back({u, v, d});
    return ds;
}
static void revertMove() {
    for (int i = (int)mv.size() - 1; i >= 0; i--) {
        D d = mv[i].d; D nd{-d.dK, -d.dK1, -d.dT, -d.dE, -d.dX};
        toggle(mv[i].u, mv[i].v, nd);
    }
    mv.clear();
}

// ---------------- bad sets cache ----------------
static vector<u64> bad;
static void enumBadRec(u64 S, u64 Pm, int need, size_t cap) {
    if (bad.size() >= cap) return;
    if (need == 0) { bad.push_back(S); return; }
    u64 Q = Pm;
    while (pc(Q) >= need) {
        int v = ctz(Q); Q &= Q - 1;
        enumBadRec(S | 1ULL << v, Q & ~adj[v], need - 1, cap);
        if (bad.size() >= cap) return;
    }
}
static void refreshBad(size_t cap) {
    bad.clear();
    // random vertex offset so a truncated list is not always the same region
    enumBadRec(0, ALLV, K, cap);
}
static inline bool isIndep(u64 S) {
    u64 Q = S;
    while (Q) { int v = ctz(Q); Q &= Q - 1; if (adj[v] & S) return false; }
    return true;
}

// ---------------- vertex rewiring (exact large neighbourhood move) ----------------
// For vertex v: F = independent (K-1)-sets of G - v. Find independent S (|S| <= vrMaxDeg)
// minimising #F-sets missed by S. Then N(v) := S. Bad sets after = I_K(G-v) + misses.
static int vrW, vrMaxDeg;
static vector<u64> vrF, vrCover, vrStack;
static long vrNodes, vrNodeLimit = 200000;
static int vrBestMiss; static u64 vrBestS;
static void vrEnum(u64 S, u64 Pm, int need, size_t cap) {
    if (vrF.size() >= cap) return;
    if (need == 0) { vrF.push_back(S); return; }
    u64 Q = Pm;
    while (pc(Q) >= need) {
        int v = ctz(Q); Q &= Q - 1;
        vrEnum(S | 1ULL << v, Q & ~adj[v], need - 1, cap);
    }
}
static void vrDFS(int depth, u64 S, u64 allowed, int misses) {
    if (vrBestMiss == 0 || ++vrNodes > vrNodeLimit) return;
    u64 *U = &vrStack[(size_t)depth * vrW];
    int forced = 0, bestCnt = 99, bestIdx = -1, unhit = 0;
    for (int w = 0; w < vrW; w++) {
        u64 x = U[w];
        while (x) {
            int i = w * 64 + ctz(x); x &= x - 1; unhit++;
            int c = pc(vrF[i] & allowed);
            if (c == 0) forced++;
            else if (c < bestCnt) { bestCnt = c; bestIdx = i; }
        }
    }
    if (bestIdx < 0 || pc(S) >= vrMaxDeg) {
        int tot = misses + unhit;
        if (tot < vrBestMiss) { vrBestMiss = tot; vrBestS = S; }
        return;
    }
    if (misses + forced >= vrBestMiss) return;
    u64 f = vrF[bestIdx] & allowed, tried = 0;
    u64 *U2 = &vrStack[(size_t)(depth + 1) * vrW];
    while (f) {
        int c = pc(f), r = rndi(c); u64 g = f;
        while (r--) g &= g - 1;
        int x = ctz(g); f &= ~(1ULL << x);
        const u64 *cv = &vrCover[(size_t)x * vrW];
        for (int w = 0; w < vrW; w++) U2[w] = U[w] & ~cv[w];
        vrDFS(depth + 1, S | 1ULL << x, allowed & ~adj[x] & ~(1ULL << x) & ~tried, misses);
        tried |= 1ULL << x;
        if (vrBestMiss == 0) return;
    }
    if (misses + forced + 1 < vrBestMiss) {
        for (int w = 0; w < vrW; w++) U2[w] = U[w];
        U2[bestIdx >> 6] &= ~(1ULL << (bestIdx & 63));
        vrDFS(depth + 1, S, allowed & ~vrF[bestIdx], misses + 1);
    }
}
// returns best misses (or -1 if F too large); vrBestS = new neighbourhood
static int vrSolve(int v, int budget, size_t cap = 60000) {
    vrF.clear();
    u64 V = ALLV & ~(1ULL << v);
    vrEnum(0, V, K - 1, cap + 1);
    if (vrF.size() > cap) return -1;
    vrW = (int)((vrF.size() + 63) / 64); if (vrW == 0) vrW = 1;
    vrCover.assign((size_t)N * vrW, 0);
    for (size_t i = 0; i < vrF.size(); i++) {
        u64 x = vrF[i];
        while (x) { int y = ctz(x); x &= x - 1; vrCover[(size_t)y * vrW + (i >> 6)] |= 1ULL << (i & 63); }
    }
    vrMaxDeg = (P.degcap > 0) ? P.degcap : K - 1;
    int maxDepth = vrMaxDeg + budget + 3;
    vrStack.assign((size_t)(maxDepth + 1) * vrW, 0);
    for (size_t i = 0; i < vrF.size(); i++) vrStack[i >> 6] |= 1ULL << (i & 63);
    vrNodes = 0; vrBestMiss = budget + 1; vrBestS = adj[v];
    vrDFS(0, 0, V, 0);
    return vrBestMiss <= budget ? vrBestMiss : -1;
}
static void setNbhd(int v, u64 S) {
    u64 Q = adj[v];
    while (Q) { int x = ctz(Q); Q &= Q - 1; adj[x] &= ~(1ULL << v); }
    adj[v] = S; Q = S;
    while (Q) { int x = ctz(Q); Q &= Q - 1; adj[x] |= 1ULL << v; }
}

// ---------------- I/O ----------------
static string toG6() {
    string s; s += (char)(N + 63);
    int bits = 0, x = 0;
    for (int j = 1; j < N; j++)
        for (int i = 0; i < j; i++) {
            x = (x << 1) | (int)(adj[i] >> j & 1);
            if (++bits == 6) { s += (char)(x + 63); bits = 0; x = 0; }
        }
    if (bits) { x <<= (6 - bits); s += (char)(x + 63); }
    return s;
}
static int fromG6(const string &line, u64 *A) {
    int n = line[0] - 63;
    for (int i = 0; i < 64; i++) A[i] = 0;
    int pos = 1, bit = 5;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            int x = line[pos] - 63;
            if (x >> bit & 1) { A[i] |= 1ULL << j; A[j] |= 1ULL << i; }
            if (--bit < 0) { bit = 5; pos++; }
        }
    return n;
}

static void randomStart() {
    for (int i = 0; i < N; i++) adj[i] = 0;
    vector<pair<int,int>> pr;
    for (int u = 0; u < N; u++) for (int v = u + 1; v < N; v++) pr.push_back({u, v});
    for (int i = (int)pr.size() - 1; i > 0; i--) swap(pr[i], pr[rndi(i + 1)]);
    for (auto [u, v] : pr) {
        if (pc(adj[u]) >= P.maxdeg || pc(adj[v]) >= P.maxdeg) continue;
        if (adj[u] & adj[v]) continue;
        adj[u] |= 1ULL << v; adj[v] |= 1ULL << u;
    }
}

static void setN(int n);
static FILE *LOG = stdout;
static vector<string> initGraphs;
static void loadStart(int which) {
    if (P.init == "random") { randomStart(); return; }
    if (P.init == "empty") { for (int i = 0; i < N; i++) adj[i] = 0; return; }
    const string &g = initGraphs[which % initGraphs.size()];
    u64 A[64];
    int n0 = fromG6(g, A);
    for (int i = 0; i < N; i++) adj[i] = (i < n0) ? A[i] & ALLV : 0;
    if (n0 < N && P.addvr) {
        // new vertices: exact min-miss neighbourhood (vertex rewiring step)
        int NN = N;
        for (int w = n0; w < NN; w++) {
            setN(w + 1); adj[w] = 0;
            int got = vrSolve(w, 400);
            if (got >= 0) setNbhd(w, vrBestS);
            fprintf(LOG, "addv %d misses=%d |F|=%zu\n", w, got, vrF.size());
        }
        setN(NN);
    } else if (n0 < N) {
        // new vertices: join to a random maximal independent set of size <= maxdeg (greedy)
        for (int w = n0; w < N; w++) {
            vector<int> order(w);
            iota(order.begin(), order.end(), 0);
            for (int i = w - 1; i > 0; i--) swap(order[i], order[rndi(i + 1)]);
            u64 S = 0;
            for (int x : order) {
                if (pc(S) >= P.maxdeg) break;
                if (!(adj[x] & S) && pc(adj[x]) < P.maxdeg) S |= 1ULL << x;
            }
            adj[w] = S;
            u64 Q = S;
            while (Q) { int x = ctz(Q); Q &= Q - 1; adj[x] |= 1ULL << w; }
        }
    }
}

static double now() {
    return chrono::duration<double>(chrono::steady_clock::now().time_since_epoch()).count();
}

static u64 bestAdj[64];
static i64 bestScore = LLONG_MAX, bestK = 0, bestK1 = 0;
static double t0;

static void saveBest(const char *tag) {
    if (P.out.empty()) return;
    string fn = P.out + "." + tag + ".g6";
    string tmp = fn + ".tmp";
    FILE *f = fopen(tmp.c_str(), "w");
    if (!f) return;
    u64 save[64]; memcpy(save, adj, sizeof save);
    memcpy(adj, bestAdj, sizeof adj);
    fprintf(f, "%s\n", toG6().c_str());
    memcpy(adj, save, sizeof adj);
    fclose(f);
    rename(tmp.c_str(), fn.c_str());
}

static bool checkFound() {
    if (cntK != 0 || cntT != 0) return false;
    fullCount();  // recompute from scratch
    if (cntK != 0 || cntT != 0) { fprintf(LOG, "WARN incremental mismatch\n"); return false; }
    double t = now() - t0;
    string g = toG6();
    fprintf(LOG, "FOUND t=%.2f e=%d g6=%s\n", t, [&]{int e=0;for(int i=0;i<N;i++)e+=pc(adj[i]);return e/2;}(), g.c_str());
    fflush(LOG);
    if (!P.out.empty()) {
        FILE *f = fopen((P.out + ".found.g6").c_str(), "a");
        if (f) { fprintf(f, "%s\n", g.c_str()); fclose(f); }
    }
    return true;
}

// best metric: weighted score, or (sawtooth mode) unweighted count of bad sets + triangles
static inline i64 metric() { return P.sawPeriod > 0 ? cntK + cntT : score(); }
static void noteBest() {
    i64 s = metric();
    if (s < bestScore) {
        bestScore = s; bestK = cntK; bestK1 = cntK1;
        memcpy(bestAdj, adj, sizeof adj);
    }
}

static int edgesNow() { int e = 0; for (int i = 0; i < N; i++) e += pc(adj[i]); return e / 2; }

// ---------------- symmetric mode ----------------
static vector<vector<pair<int,int>>> orbits;
static int orbitOf[64][64];
static inline int sigma(int v) {
    int q = N - P.symf;
    if (v >= q) return v;
    int b = v / P.symm, r = v % P.symm;
    return b * P.symm + (r + 1) % P.symm;
}
static void buildOrbits() {
    for (int u = 0; u < N; u++) for (int v = 0; v < N; v++) orbitOf[u][v] = -1;
    for (int u = 0; u < N; u++) for (int v = u + 1; v < N; v++) {
        if (orbitOf[u][v] >= 0) continue;
        int id = orbits.size(); orbits.push_back({});
        int a = u, b = v;
        while (orbitOf[a][b] < 0) {
            orbitOf[a][b] = orbitOf[b][a] = id;
            orbits[id].push_back({min(a, b), max(a, b)});
            a = sigma(a); b = sigma(b);
        }
    }
}
static void toggleOrbit(int id) {
    for (auto [u, v] : orbits[id]) { D d = pairDelta(u, v); toggle(u, v, d); mv.push_back({u, v, d}); }
}
static i64 symMove(int id) {
    mv.clear();
    i64 s0 = score();
    auto [u0, v0] = orbits[id][0];
    bool adding = !(adj[u0] >> v0 & 1);
    toggleOrbit(id);
    if (adding && P.wT == 0) {
        // break triangles by deleting orbits of conflicting edges
        for (int guard = 0; cntT > 0 && guard < 64; guard++) {
            bool fixed = false;
            for (auto [u, v] : orbits[id]) {
                u64 W = adj[u] & adj[v];
                if (!W) continue;
                int x = ctz(W);
                int y = (rnd64() & 1) ? u : v;
                toggleOrbit(orbitOf[x][y]);
                fixed = true;
                break;
            }
            if (!fixed) break;
        }
        if (cntT > 0) { revertMove(); mv.clear(); return LLONG_MAX / 4; }
    }
    return score() - s0;
}
static void symRandomStart() {
    for (int i = 0; i < N; i++) adj[i] = 0;
    vector<int> ord(orbits.size());
    iota(ord.begin(), ord.end(), 0);
    for (int i = (int)ord.size() - 1; i > 0; i--) swap(ord[i], ord[rndi(i + 1)]);
    for (int id : ord) {
        u64 save[64]; memcpy(save, adj, sizeof save);
        for (auto [u, v] : orbits[id]) { adj[u] |= 1ULL << v; adj[v] |= 1ULL << u; }
        bool ok = true;
        for (auto [u, v] : orbits[id]) if ((adj[u] & adj[v]) || pc(adj[u]) > P.maxdeg || pc(adj[v]) > P.maxdeg) { ok = false; break; }
        if (!ok) memcpy(adj, save, sizeof save);
    }
}

// one focused or random candidate move; returns delta (move applied, mv set). -1 type = none
// degree window: a move is refused if a touched vertex leaves the window or moves further out of it
static bool windowOK(const int *dold, const int *vs, int nv) {
    for (int i = 0; i < nv; i++) {
        int dn = pc(adj[vs[i]]);
        if ((dn < P.dlo && dn < dold[i]) || (dn > P.dhi && dn > dold[i])) return false;
    }
    return true;
}
static inline int randNbr(int a) {
    u64 Na = adj[a]; int c = pc(Na), r = rndi(c);
    while (r--) Na &= Na - 1;
    return ctz(Na);
}
// double-edge swap ab, cd -> ac, bd (keeps all degrees; hard triangle-free)
static i64 swapMove() {
    mv.clear();
    int a = rndi(N), c = rndi(N);
    if (a == c || !adj[a] || !adj[c]) return LLONG_MAX / 4;
    int b = randNbr(a), d = randNbr(c);
    if (b == c || b == d || d == a) return LLONG_MAX / 4;
    if ((adj[a] >> c & 1) || (adj[b] >> d & 1)) return LLONG_MAX / 4;
    i64 tot = 0;
    D x = pairDelta(a, b); tot += x.s(); toggle(a, b, x); mv.push_back({a, b, x});
    x = pairDelta(c, d); tot += x.s(); toggle(c, d, x); mv.push_back({c, d, x});
    if (P.wT == 0 && (adj[a] & adj[c])) { revertMove(); return LLONG_MAX / 4; }
    x = pairDelta(a, c); tot += x.s(); toggle(a, c, x); mv.push_back({a, c, x});
    if (P.wT == 0 && (adj[b] & adj[d])) { revertMove(); return LLONG_MAX / 4; }
    x = pairDelta(b, d); tot += x.s(); toggle(b, d, x); mv.push_back({b, d, x});
    return tot;
}
static i64 proposeMove0(bool &ok);
static i64 proposeMove(bool &ok) {
    if (P.dlo <= 0 || P.symm) return proposeMove0(ok);
    ok = true;
    if (rndu() < P.pswap) return swapMove();
    // record degrees of all vertices (cheap at n <= 64), apply, check window on touched ones
    int dold[64]; for (int i = 0; i < N; i++) dold[i] = pc(adj[i]);
    i64 d = proposeMove0(ok);
    if (mv.empty()) return d;
    int vs[64], dv[64], nv = 0; u64 seen = 0;
    for (auto &t : mv) for (int y : {t.u, t.v}) if (!(seen >> y & 1)) { seen |= 1ULL << y; vs[nv] = y; dv[nv] = dold[y]; nv++; }
    if (!windowOK(dv, vs, nv)) { revertMove(); return LLONG_MAX / 4; }
    return d;
}
static i64 proposeMove0(bool &ok) {
    ok = true;
    if (P.symm) {
        if (P.focus > 0 && cntK > 0 && rndu() < P.focus) {
            for (int tries = 0; tries < 4; tries++) {
                if (bad.empty()) refreshBad(4096);
                if (bad.empty()) break;
                int i = rndi((int)bad.size());
                u64 S = bad[i];
                if (!isIndep(S)) { bad[i] = bad.back(); bad.pop_back(); continue; }
                int a[64], m = 0; u64 Q = S;
                while (Q) { a[m++] = ctz(Q); Q &= Q - 1; }
                int x = rndi(m), y = rndi(m - 1); if (y >= x) y++;
                return symMove(orbitOf[a[x]][a[y]]);
            }
        }
        return symMove(rndi((int)orbits.size()));
    }
    if (P.focus > 0 && cntK > 0 && rndu() < P.focus) {
        // pick a cached bad set that is still independent
        for (int tries = 0; tries < 4; tries++) {
            if (bad.empty()) refreshBad(4096);
            if (bad.empty()) break;
            int i = rndi((int)bad.size());
            u64 S = bad[i];
            if (!isIndep(S)) { bad[i] = bad.back(); bad.pop_back(); continue; }
            int a[64], m = 0; u64 Q = S;
            while (Q) { a[m++] = ctz(Q); Q &= Q - 1; }
            int x = rndi(m), y = rndi(m - 1); if (y >= x) y++;
            return applyCompoundAdd(a[x], a[y]);
        }
    }
    int u = rndi(N), v = rndi(N - 1); if (v >= u) v++;
    if (adj[u] >> v & 1) return applyRemove(u, v);
    return applyCompoundAdd(u, v);
}

static i64 movesDone = 0, vrCalls = 0, vrAcc = 0;
// Exoo 2013 (EJC 20(1) #P68, Sec 4): triangle weight follows a sawtooth sawMin..sawMax (times wK)
// over sawPeriod moves; it returns to the minimum at each new best (unweighted) count.
static i64 sawStart = 0;
static inline void sawReset(i64 it) { if (P.sawPeriod > 0) sawStart = it; }
static inline void sawSet(i64 it) {
    if (P.sawPeriod <= 0) return;
    double ph = (double)((it - sawStart) % P.sawPeriod) / P.sawPeriod;
    P.wT = (i64)(P.wK * (P.sawMin + (P.sawMax - P.sawMin) * ph));
}
static int targetN;
static double levelStart;
enum { ACT_NONE, ACT_STOP, ACT_RESTART, ACT_GROWN };
static void setN(int n) { N = n; ALLV = (N == 64) ? ~0ULL : ((1ULL << N) - 1); }
static void growOne() {
    // save the level solution, add vertex N with the exact min-miss neighbourhood
    if (!P.out.empty()) {
        FILE *f = fopen((P.out + ".level" + to_string(N) + ".g6").c_str(), "a");
        if (f) { fprintf(f, "%s\n", toG6().c_str()); fclose(f); }
    }
    setN(N + 1);
    int v = N - 1; adj[v] = 0;
    int got = vrSolve(v, 400);
    if (got >= 0) setNbhd(v, vrBestS);
    fullCount();
    bestScore = LLONG_MAX; noteBest();
    levelStart = now();
    fprintf(LOG, "GROW to n=%d t=%.1f misses=%d K=%lld vrnodes=%ld |F|=%zu\n", N, now() - t0, got, (long long)cntK, vrNodes, vrF.size());
    fflush(LOG);
}
static int onFound() {
    // call when cntK == 0 && cntT == 0
    if (N < targetN) { growOne(); return ACT_GROWN; }
    if (!checkFound()) return ACT_NONE;
    noteBest();
    if (P.stopOnFound) return ACT_STOP;
    if (P.bench) return ACT_RESTART;
    return ACT_NONE;
}

static bool runSA() {
    int pending = ACT_NONE;
    levelStart = now();
    i64 it = 0;
    int cycle = 0;
    double lastLog = now();
    while (now() - t0 < P.timelimit) {
        // cycle start
        if (cycle > 0) {
            if (pending == ACT_GROWN) { /* graph already set by growOne */ }
            else if (P.restartRandom || pending == ACT_RESTART) {
                if (P.grow0) setN(P.grow0);
                if (P.symm) symRandomStart(); else loadStart(cycle);
                if (pending == ACT_RESTART) { bestScore = LLONG_MAX; levelStart = now(); }
            }
            else {
                memcpy(adj, bestAdj, sizeof adj);
                int np = (int)(P.perturb * N * (N - 1) / 2);
                if (P.symm) {
                    fullCount();
                    np = max(2, (int)(P.perturb * orbits.size()));
                    for (int i = 0; i < np; i++) { symMove(rndi((int)orbits.size())); mv.clear(); }
                    np = 0;
                }
                for (int i = 0; i < np; i++) {
                    int u = rndi(N), v = rndi(N - 1); if (v >= u) v++;
                    if (adj[u] >> v & 1) { adj[u] ^= 1ULL << v; adj[v] ^= 1ULL << u; }
                    else if ((!(adj[u] & adj[v]) || P.wT) && (P.degcap == 0 || (pc(adj[u]) < P.degcap && pc(adj[v]) < P.degcap))) { adj[u] ^= 1ULL << v; adj[v] ^= 1ULL << u; }
                }
            }
            fullCount();
            pending = ACT_NONE;
        }
        bad.clear();
        if (cntK < 200000) refreshBad(4096);
        i64 cyc0Best = LLONG_MAX;
        for (i64 s = 0; s < P.sweep; s++, it++) {
            double fr = (double)s / P.sweep;
            double T = P.T0 * pow(P.T1 / P.T0, fr) * P.wK;
            sawSet(it);
            bool ok;
            if (P.vr > 0 && !P.symm && cntK > 0 && rndu() < P.vr) {
                // vertex rewiring: pick a vertex of a cached bad set (or random)
                int v = rndi(N);
                if (!bad.empty()) { u64 S = bad[rndi((int)bad.size())]; if (isIndep(S)) { int c = pc(S), r = rndi(c); while (r--) S &= S - 1; v = ctz(S); } }
                u64 Cv = ALLV & ~adj[v] & ~(1ULL << v);
                i64 through = recA(Cv, K - 1);
                int got = vrSolve(v, (int)through + P.vrSlack);
                vrCalls++;
                if (got >= 0 && vrBestS != adj[v]) {
                    i64 s0 = score();
                    u64 save[64]; memcpy(save, adj, sizeof save);
                    i64 sK = cntK, sK1 = cntK1, sT = cntT, sE = cntE, sX = nEdges;
                    setNbhd(v, vrBestS); fullCount();
                    if (P.dlo > 0) {
                        int dv[64], vs[64]; for (int i = 0; i < N; i++) { vs[i] = i; dv[i] = pc(save[i]); }
                        if (!windowOK(dv, vs, N)) { memcpy(adj, save, sizeof adj); cntK = sK; cntK1 = sK1; cntT = sT; cntE = sE; nEdges = sX; continue; }
                    }
                    i64 d = score() - s0;
                    if (d <= 0 || rndu() < exp(-d / T)) {
                        vrAcc++;
                        if (metric() < cyc0Best) { cyc0Best = metric(); noteBest(); sawReset(it); }
                        if (cntK == 0 && cntT == 0) {
                            int act = onFound();
                            if (act == ACT_STOP) return true;
                            if (act != ACT_NONE) { pending = act; break; }
                        }
                        bad.clear(); if (cntK > 0 && cntK < 200000) refreshBad(4096);
                    } else { memcpy(adj, save, sizeof adj); cntK = sK; cntK1 = sK1; cntT = sT; cntE = sE; nEdges = sX; }
                }
                continue;
            }
            i64 d = proposeMove(ok);
            movesDone++;
            if (d <= 0 || rndu() < exp(-d / T)) {
                mv.clear();
                if (metric() < cyc0Best) { cyc0Best = metric(); noteBest(); sawReset(it); }
                if (cntK == 0 && cntT == 0) {
                    int act = onFound();
                    if (act == ACT_STOP) return true;
                    if (act != ACT_NONE) { pending = act; break; }
                }
            } else revertMove();
            if ((it & 1023) == 0) {
                if (bad.size() < 64 && cntK > 0 && cntK < 200000) refreshBad(4096);
                double t = now();
                if (t - lastLog > 30) {
                    lastLog = t;
                    fprintf(LOG, "t=%.0f cyc=%d it=%lld cur K=%lld K1=%lld T=%lld e=%d | best K=%lld K1=%lld score=%lld\n",
                            t - t0, cycle, (long long)it, (long long)cntK, (long long)cntK1, (long long)cntT, edgesNow(),
                            (long long)bestK, (long long)bestK1, (long long)bestScore);
                    fflush(LOG);
                    saveBest("best");
                }
                if (t - t0 > P.timelimit) break;
                if (P.grow0 && N > P.grow0 && t - levelStart > P.levelTime) {
                    fprintf(LOG, "LEVEL timeout n=%d best K=%lld t=%.1f\n", N, (long long)bestK, t - t0);
                    pending = ACT_RESTART; break;
                }
            }
        }
        { i64 a = cntK, b = cntK1, c = cntT; fullCount();
          if (a != cntK || b != cntK1 || c != cntT) fprintf(LOG, "WARN count mismatch %lld/%lld %lld/%lld %lld/%lld\n",
              (long long)a, (long long)cntK, (long long)b, (long long)cntK1, (long long)c, (long long)cntT); }
        fprintf(LOG, "cycle %d end t=%.1f cycleBest=%lld best=%lld (K=%lld) vr=%lld/%lld\n", cycle, now() - t0,
                (long long)cyc0Best, (long long)bestScore, (long long)bestK, (long long)vrAcc, (long long)vrCalls);
        fflush(LOG);
        saveBest("best");
        cycle++;
    }
    return false;
}

// tabu: sample candidate pairs (random + all pairs inside a bad set), take best non-tabu
static bool runTabu() {
    vector<vector<i64>> tabu(N, vector<i64>(N, -1));
    i64 it = 0;
    double lastLog = now();
    i64 sinceImp = 0;
    while (now() - t0 < P.timelimit) {
        if (bad.size() < 16 && cntK > 0) refreshBad(4096);
        vector<pair<int,int>> cand;
        // pairs in a bad set
        for (int tries = 0; tries < 8 && cntK > 0 && !bad.empty(); tries++) {
            int i = rndi((int)bad.size());
            if (!isIndep(bad[i])) { bad[i] = bad.back(); bad.pop_back(); continue; }
            u64 S = bad[i]; int a[64], m = 0; u64 Q = S;
            while (Q) { a[m++] = ctz(Q); Q &= Q - 1; }
            for (int x = 0; x < m; x++) for (int y = x + 1; y < m; y++) cand.push_back({a[x], a[y]});
            break;
        }
        for (int i = 0; i < P.tabuSample; i++) {
            int u = rndi(N), v = rndi(N - 1); if (v >= u) v++;
            cand.push_back({min(u, v), max(u, v)});
        }
        i64 bestD = LLONG_MAX; int bu = -1, bv = -1; u64 bestSeed[2] = {0, 0};
        i64 cur = score();
        for (auto [u, v] : cand) {
            bool isT = tabu[u][v] > it;
            u64 sv[2] = {rs[0], rs[1]};
            i64 d = (adj[u] >> v & 1) ? applyRemove(u, v) : applyCompoundAdd(u, v);
            revertMove();
            bool aspir = cur + d < bestScore;
            if (isT && !aspir) continue;
            if (d < bestD || (d == bestD && rndi(2))) { bestD = d; bu = u; bv = v; bestSeed[0] = sv[0]; bestSeed[1] = sv[1]; }
        }
        if (bu < 0) { it++; continue; }
        rs[0] = bestSeed[0]; rs[1] = bestSeed[1];  // replay same random choices
        if (adj[bu] >> bv & 1) applyRemove(bu, bv); else applyCompoundAdd(bu, bv);
        for (auto &t : mv) { int a = min(t.u, t.v), b = max(t.u, t.v); tabu[a][b] = it + P.tabuLen + rndi(P.tabuLen); }
        rs[0] ^= (u64)it * 0x9E3779B97F4A7C15ULL; rnd64();
        mv.clear();
        movesDone++;
        it++;
        if (score() < bestScore) { noteBest(); sinceImp = 0; if (checkFound() && P.stopOnFound) return true; }
        else sinceImp++;
        if (sinceImp > 20000) {  // restart from perturbed best
            memcpy(adj, bestAdj, sizeof adj);
            int np = (int)(P.perturb * N * (N - 1) / 2);
            for (int i = 0; i < np; i++) {
                int u = rndi(N), v = rndi(N - 1); if (v >= u) v++;
                if ((adj[u] >> v & 1) || ((!(adj[u] & adj[v]) || P.wT) && (P.degcap == 0 || (pc(adj[u]) < P.degcap && pc(adj[v]) < P.degcap)))) { adj[u] ^= 1ULL << v; adj[v] ^= 1ULL << u; }
            }
            fullCount(); bad.clear(); sinceImp = 0;
        }
        double t = now();
        if (t - lastLog > 30) {
            lastLog = t;
            fprintf(LOG, "t=%.0f it=%lld cur K=%lld K1=%lld T=%lld e=%d | best K=%lld K1=%lld score=%lld\n",
                    t - t0, (long long)it, (long long)cntK, (long long)cntK1, (long long)cntT, edgesNow(),
                    (long long)bestK, (long long)bestK1, (long long)bestScore);
            fflush(LOG);
            saveBest("best");
        }
    }
    return false;
}

int main(int argc, char **argv) {
    for (int i = 1; i < argc; i++) {
        string a = argv[i];
        auto val = [&]() { return string(argv[++i]); };
        if (a == "-n") P.n = stoi(val());
        else if (a == "-k") P.k = stoi(val());
        else if (a == "-seed") P.seed = stoull(val());
        else if (a == "-method") P.method = val();
        else if (a == "-wK") P.wK = stoll(val());
        else if (a == "-w9") P.w9 = stoll(val());
        else if (a == "-wT") P.wT = stoll(val());
        else if (a == "-maxdeg") P.maxdeg = stoi(val());
        else if (a == "-degcap") P.degcap = stoi(val());
        else if (a == "-wD") P.wD = stoll(val());
        else if (a == "-wX") P.wX = stoll(val());
        else if (a == "-emax") P.emax = stoll(val());
        else if (a == "-softcap") P.softcap = stoi(val());
        else if (a == "-T0") P.T0 = stod(val());
        else if (a == "-T1") P.T1 = stod(val());
        else if (a == "-sweep") P.sweep = stoll(val());
        else if (a == "-focus") P.focus = stod(val());
        else if (a == "-time") P.timelimit = stod(val());
        else if (a == "-init") P.init = val();
        else if (a == "-out") P.out = val();
        else if (a == "-tabulen") P.tabuLen = stoi(val());
        else if (a == "-tabusample") P.tabuSample = stoi(val());
        else if (a == "-perturb") P.perturb = stod(val());
        else if (a == "-rr") P.restartRandom = stoi(val());
        else if (a == "-keepgoing") P.stopOnFound = 0;
        else if (a == "-bench") { P.bench = 1; P.stopOnFound = 0; }
        else if (a == "-sym") P.symm = stoi(val());
        else if (a == "-grow") P.grow0 = stoi(val());
        else if (a == "-dlo") P.dlo = stoi(val());
        else if (a == "-dhi") P.dhi = stoi(val());
        else if (a == "-pswap") P.pswap = stod(val());
        else if (a == "-saw") P.sawPeriod = stoll(val());
        else if (a == "-sawmin") P.sawMin = stod(val());
        else if (a == "-sawmax") P.sawMax = stod(val());
        else if (a == "-addvr") P.addvr = stoi(val());
        else if (a == "-leveltime") P.levelTime = stod(val());
        else if (a == "-vr") P.vr = stod(val());
        else if (a == "-vrslack") P.vrSlack = stoi(val());
        else if (a == "-vrnodes") vrNodeLimit = stol(val());
        else if (a == "-symf") P.symf = stoi(val());
        else { fprintf(stderr, "unknown arg %s\n", a.c_str()); return 2; }
    }
    N = P.n; K = P.k; targetN = P.n;
    if (P.grow0) N = P.grow0;
    if (P.degcap < 0) P.degcap = K - 1;
    if (P.softcap < 0) P.softcap = K - 1;
    if (P.sawPeriod > 0) P.wT = (i64)(P.wK * P.sawMin);
    if (P.degcap > 0 && P.maxdeg > P.degcap) P.maxdeg = P.degcap;
    ALLV = (N == 64) ? ~0ULL : ((1ULL << N) - 1);
    rs[0] = P.seed * 0x9E3779B97F4A7C15ULL + 12345; rs[1] = (P.seed + 7) * 0xBF58476D1CE4E5B9ULL;
    for (int i = 0; i < 20; i++) rnd64();
    if (P.init.rfind("file:", 0) == 0) {
        ifstream in(P.init.substr(5));
        string l;
        while (getline(in, l)) if (!l.empty() && l[0] != '>') initGraphs.push_back(l);
        if (initGraphs.empty()) { fprintf(stderr, "no graphs in init file\n"); return 2; }
        // choose start graph by seed
        string g = initGraphs[P.seed % initGraphs.size()];
        initGraphs = {g};
    }
    if (!P.out.empty()) { LOG = fopen((P.out + ".log").c_str(), "a"); if (!LOG) LOG = stdout; }
    fprintf(LOG, "# ls n=%d k=%d seed=%llu method=%s wK=%lld w9=%lld wT=%lld wD=%lld degcap=%d maxdeg=%d T0=%g T1=%g sweep=%lld focus=%g init=%s perturb=%g rr=%d\n",
            N, K, (unsigned long long)P.seed, P.method.c_str(), (long long)P.wK, (long long)P.w9, (long long)P.wT, (long long)P.wD,
            P.degcap, P.maxdeg, P.T0, P.T1, (long long)P.sweep, P.focus, P.init.c_str(), P.perturb, P.restartRandom);
    t0 = now();
    if (P.symm) {
        if ((N - P.symf) % P.symm) { fprintf(stderr, "n - symf not divisible by sym\n"); return 2; }
        P.degcap = 0;
        buildOrbits();
        fprintf(LOG, "sym m=%d f=%d orbits=%zu\n", P.symm, P.symf, orbits.size());
        if (P.init == "random") symRandomStart(); else loadStart((int)P.seed);
    } else loadStart((int)P.seed);
    fullCount();
    noteBest();
    fprintf(LOG, "start K=%lld K1=%lld T=%lld e=%d (count %.3fs)\n", (long long)cntK, (long long)cntK1, (long long)cntT, edgesNow(), now() - t0);
    fflush(LOG);
    bool f = (P.method == "tabu") ? runTabu() : runSA();
    saveBest("best");
    fprintf(LOG, "END found=%d t=%.2f moves=%lld best K=%lld K1=%lld score=%lld\n", (int)f, now() - t0,
            (long long)movesDone, (long long)bestK, (long long)bestK1, (long long)bestScore);
    fclose(LOG);
    return f ? 0 : 1;
}
