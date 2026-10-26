/* mcount.c - Monte Carlo estimate of edge-count ratios g(e+1)/g(e) for
 * labelled (3,K;n,e)-graphs (triangle-free, alpha < K), K given as -k.
 *
 * Chain: states = valid labelled graphs with elo <= e <= ehi.
 * Moves: toggle a random pair (add/remove one edge), or swap (remove random edge,
 * add random non-edge). Acceptance min(1, w(e')/w(e)), w = exp(-lng) learned by
 * Wang-Landau, then fixed for the production phase.
 * Estimator (broad histogram / transition matrix):
 *   g(e) * <a>_e = g(e+1) * <r>_{e+1}
 * a(G) = #non-edges that can be added (no triangle), r(G) = #edges that can be
 * removed (alpha stays < K). Within a level the chain is uniform, so these
 * level averages are unbiased.
 *
 * usage: mcount -n N -k K -l ELO -h EHI -s SEED -w WLSTEPS -p PRODSTEPS < start.g6
 * start graph: any (3,K;N)-graph; the chain first walks into [ELO,EHI].
 */
#include "gutil.h"
#include <math.h>
#include <getopt.h>
#include <time.h>

static int n, K, elo, ehi;
static set_t adj[64];
static int ne;                  /* current edges */
static uint64_t rng_s[2];
static inline uint64_t rnd(void)
{   /* xorshift128+ */
    uint64_t s1 = rng_s[0], s0 = rng_s[1];
    rng_s[0] = s0; s1 ^= s1 << 23;
    rng_s[1] = s1 ^ s0 ^ (s1 >> 17) ^ (s0 >> 26);
    return rng_s[1] + s0;
}
static inline int rndint(int m) { return (int)((rnd() >> 11) % (uint64_t)m); }
static inline double rnd01(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }

/* edge and non-edge lists with index maps */
static int P;                   /* number of pairs */
static int pu[2048], pv[2048];  /* pair id -> endpoints */
static int pid[64][64];
static int elist[2048], epos[2048], nel;  /* edges */
static int flist[2048], fpos[2048], nfl;  /* non-edges */

static void lists_build(void)
{
    nel = nfl = 0;
    for (int p = 0; p < P; p++) {
        if (adj[pu[p]] & BIT(pv[p])) { epos[p] = nel; elist[nel++] = p; }
        else { fpos[p] = nfl; flist[nfl++] = p; }
    }
    ne = nel;
}
static void move_to_edges(int p)
{
    int i = fpos[p], q = flist[--nfl]; flist[i] = q; fpos[q] = i;
    epos[p] = nel; elist[nel++] = p;
}
static void move_to_nonedges(int p)
{
    int i = epos[p], q = elist[--nel]; elist[i] = q; epos[q] = i;
    fpos[p] = nfl; flist[nfl++] = p;
}

static set_t ALL;
/* after removing edge u-v: is there an independent K-set? (must contain u and v) */
static inline int removal_bad(int u, int v)
{
    set_t m = ALL & ~adj[u] & ~adj[v] & ~BIT(u) & ~BIT(v);
    return has_indep(adj, m, K - 2);
}

static int count_a(void)
{
    int a = 0;
    for (int i = 0; i < nfl; i++) { int p = flist[i]; if (!(adj[pu[p]] & adj[pv[p]])) a++; }
    return a;
}
static int count_r(void)
{
    int r = 0;
    for (int i = 0; i < nel; i++) {
        int p = elist[i], u = pu[p], v = pv[p];
        adj[u] &= ~BIT(v); adj[v] &= ~BIT(u);
        if (!removal_bad(u, v)) r++;
        adj[u] |= BIT(v); adj[v] |= BIT(u);
    }
    return r;
}

#define MAXL 400
static double lng[MAXL];       /* indexed by e */
static double H[MAXL];
static double sa[MAXL], sr[MAXL], sa2[MAXL], sr2[MAXL]; static long long ns[MAXL];

/* one Metropolis step; returns 1 if state changed */
static long long acc_t, acc_s, try_t, try_s;
static int step(void)
{
    if (rnd() & 1) {
        /* toggle */
        int p = rndint(P), u = pu[p], v = pv[p];
        try_t++;
        if (adj[u] & BIT(v)) {
            int e2 = ne - 1;
            if (e2 < elo) return 0;
            double d = lng[ne] - lng[e2];
            if (d < 0 && rnd01() >= exp(d)) return 0;
            adj[u] &= ~BIT(v); adj[v] &= ~BIT(u);
            if (removal_bad(u, v)) { adj[u] |= BIT(v); adj[v] |= BIT(u); return 0; }
            move_to_nonedges(p); ne--; acc_t++; return 1;
        } else {
            int e2 = ne + 1;
            if (e2 > ehi) return 0;
            if (adj[u] & adj[v]) return 0;
            double d = lng[ne] - lng[e2];
            if (d < 0 && rnd01() >= exp(d)) return 0;
            adj[u] |= BIT(v); adj[v] |= BIT(u);
            move_to_edges(p); ne++; acc_t++; return 1;
        }
    } else {
        /* swap: remove edge p, add non-edge q */
        if (nel == 0 || nfl == 0) return 0;
        try_s++;
        int p = elist[rndint(nel)], q = flist[rndint(nfl)];
        int a = pu[p], b = pv[p], c = pu[q], d = pv[q];
        adj[a] &= ~BIT(b); adj[b] &= ~BIT(a);
        if (adj[c] & adj[d]) { adj[a] |= BIT(b); adj[b] |= BIT(a); return 0; }
        adj[c] |= BIT(d); adj[d] |= BIT(c);
        if (removal_bad(a, b)) {
            adj[c] &= ~BIT(d); adj[d] &= ~BIT(c);
            adj[a] |= BIT(b); adj[b] |= BIT(a); return 0;
        }
        move_to_nonedges(p); move_to_edges(q); acc_s++; return 1;
    }
}

int main(int argc, char **argv)
{
    long long wlsteps = 100000000, prodsteps = 100000000;
    uint64_t seed = 1;
    int sampint = 0, c;
    double flat = 0.8, fmin = 1e-5;
    const char *lngfile = NULL, *dumpfile = NULL;
    int dumpe = -1; long long dumpmax = 0, ndump = 0; FILE *df = NULL;
    while ((c = getopt(argc, argv, "n:k:l:h:s:w:p:i:f:L:o:O:N:")) != -1) {
        switch (c) {
        case 'n': n = atoi(optarg); break;
        case 'k': K = atoi(optarg); break;
        case 'l': elo = atoi(optarg); break;
        case 'h': ehi = atoi(optarg); break;
        case 's': seed = strtoull(optarg, 0, 10); break;
        case 'w': wlsteps = atoll(optarg); break;
        case 'p': prodsteps = atoll(optarg); break;
        case 'i': sampint = atoi(optarg); break;
        case 'f': fmin = atof(optarg); break;
        case 'L': lngfile = optarg; break;
        case 'o': dumpe = atoi(optarg); break;
        case 'O': dumpfile = optarg; break;
        case 'N': dumpmax = atoll(optarg); break;
        }
    }
    rng_s[0] = seed * 0x9E3779B97F4A7C15ULL + 12345; rng_s[1] = (seed + 7) * 0xBF58476D1CE4E5B9ULL;
    for (int i = 0; i < 20; i++) rnd();
    char line[4096];
    if (!fgets(line, sizeof line, stdin)) { fprintf(stderr, "no start graph\n"); return 1; }
    line[strcspn(line, "\r\n")] = 0;
    graph_t g; if (g6_read(line, &g)) return 1;
    if (g.n != n) { fprintf(stderr, "start graph has n=%d\n", g.n); return 1; }
    if (!g_trianglefree(&g) || !alpha_le(&g, K - 1)) { fprintf(stderr, "start graph not (3,%d)\n", K); return 1; }
    memcpy(adj, g.adj, sizeof(adj));
    ALL = BIT(n) - 1;
    P = 0;
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) { pu[P] = i; pv[P] = j; pid[i][j] = pid[j][i] = P; P++; }
    lists_build();
    if (!sampint) sampint = n;
    /* phase 0: walk into range with unbiased toggles toward range */
    int lo0 = elo, hi0 = ehi;
    elo = 0; ehi = P;
    for (int e = 0; e < MAXL; e++) lng[e] = 0;
    long long it = 0;
    while (ne < lo0 || ne > hi0) {
        /* bias: favour moving toward range */
        for (int e = 0; e < MAXL; e++) lng[e] = (e < lo0) ? 3.0 * (lo0 - e) : (e > hi0 ? 3.0 * (e - hi0) : 0);
        step();
        if (++it % 100000000 == 0) fprintf(stderr, "phase0 it=%lld e=%d\n", it, ne);
    }
    elo = lo0; ehi = hi0;
    fprintf(stderr, "in range after %lld steps, e=%d\n", it, ne);
    for (int e = 0; e < MAXL; e++) lng[e] = 0;
    if (lngfile) {
        FILE *f = fopen(lngfile, "r");
        int e; double x;
        while (f && fscanf(f, "%d %lf", &e, &x) == 2) if (e >= 0 && e < MAXL) lng[e] = x;
        if (f) fclose(f);
        wlsteps = 0;
    }
    /* phase 1: Wang-Landau */
    double fmod = 1.0;
    long long t = 0;
    clock_t t0 = clock();
    while (t < wlsteps && fmod > fmin) {
        step(); t++;
        lng[ne] += fmod; H[ne] += 1;
        if (t % 1000000 == 0) {
            double mn = 1e300, mean = 0; int L = ehi - elo + 1;
            for (int e = elo; e <= ehi; e++) { mean += H[e]; if (H[e] < mn) mn = H[e]; }
            mean /= L;
            if (mn > flat * mean) {
                fprintf(stderr, "WL t=%lld f=%g flat; lng:", t, fmod);
                for (int e = elo; e <= ehi; e++) fprintf(stderr, " %.2f", lng[e] - lng[elo]);
                fprintf(stderr, "\n");
                fmod /= 2; for (int e = elo; e <= ehi; e++) H[e] = 0;
            }
            if (t % 100000000 == 0) {
                fprintf(stderr, "WL t=%lld f=%g H:", t, fmod);
                for (int e = elo; e <= ehi; e++) fprintf(stderr, " %.0f", H[e]);
                fprintf(stderr, "\n");
            }
        }
    }
    fprintf(stderr, "WL done t=%lld f=%g cpu=%.1fs\n", t, fmod, (double)(clock() - t0) / CLOCKS_PER_SEC);
    /* phase 2: production with fixed weights */
    for (long long s = 0; s < prodsteps; s++) {
        step();
        if (s % sampint == 0) {
            double a = count_a(), r = count_r();
            if (ne == dumpe && ndump < dumpmax && dumpfile) {
                if (!df) df = fopen(dumpfile, "w");
                graph_t gg; gg.n = n; memcpy(gg.adj, adj, sizeof(adj)); g6_write(df, &gg); ndump++;
            }
            sa[ne] += a; sr[ne] += r; sa2[ne] += a * a; sr2[ne] += r * r; ns[ne]++;
        }
        if ((s + 1) % 100000000 == 0) fprintf(stderr, "prod %lld\n", s + 1);
    }
    if (df) fclose(df);
    fprintf(stderr, "acc toggle %.4f swap %.4f cpu=%.1fs\n", (double)acc_t / (try_t + 1), (double)acc_s / (try_s + 1),
            (double)(clock() - t0) / CLOCKS_PER_SEC);
    /* output per level: e ns <a> <r> lngWL */
    printf("# n=%d K=%d seed=%llu\n# e samples mean_a sd_a mean_r sd_r lngWL\n", n, K, (unsigned long long)seed);
    for (int e = elo; e <= ehi; e++) {
        double ma = ns[e] ? sa[e] / ns[e] : 0, mr = ns[e] ? sr[e] / ns[e] : 0;
        double va = ns[e] ? sa2[e] / ns[e] - ma * ma : 0, vr = ns[e] ? sr2[e] / ns[e] - mr * mr : 0;
        printf("%d %lld %.6f %.6f %.6f %.6f %.6f\n", e, ns[e], ma, sqrt(va > 0 ? va : 0), mr, sqrt(vr > 0 ? vr : 0), lng[e] - lng[elo]);
    }
    return 0;
}
