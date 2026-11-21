/* glue.c - neighbourhood gluing extender (Goedgebeur-Radziszowski 2013, Sec. 3).
 *
 * Input (stdin): graph6 graphs H with alpha(H) <= K-1, triangle-free.
 * Output (stdout): graph6 graphs G = H + {u_1..u_d} + {v}, where v ~ u_i, u_i ~ S_i,
 *   S_i independent sets of H, such that G is triangle-free, alpha(G) <= K,
 *   EMIN <= e(G) <= EMAX, DMIN <= deg <= DMAX for all vertices.
 *   Vertex order of G: H = 0..m-1, u_i = m..m+d-1, v = m+d.
 *   No isomorphism rejection (pipe through nauty shortg).
 *
 * usage: glue -k K -d D [-e EMAX] [-E EMIN] [-m DMIN] [-M DMAX] [-q]
 *   defaults: EMAX=inf, EMIN=0, DMIN=D (v is a minimum degree vertex), DMAX=K.
 */
#include "gutil.h"
#include <getopt.h>
#include <time.h>

static int K, D, EMAX = 1 << 30, EMIN = 0, DMIN = -1, DMAX = -1, quiet = 0;

static graph_t H;
static int m, eH, degH[64];

/* candidates */
static int N, W;               /* number of candidates, words per bitset over candidates */
static set_t *cand;            /* cand[i] = vertex set */
static int *csz;
static uint64_t *comp;         /* comp[i*W..] compat bitset row */
static uint64_t *cont;         /* cont[x*W..] candidates containing x */

static long long nout, nleaf, nnodes;
static int chosen[64];
static int cnt[64];

static void output(void)
{
    graph_t G;
    memset(&G, 0, sizeof(G));
    G.n = m + D + 1;
    for (int x = 0; x < m; x++) G.adj[x] = H.adj[x];
    int v = m + D;
    for (int i = 0; i < D; i++) {
        int u = m + i;
        G.adj[u] |= BIT(v); G.adj[v] |= BIT(u);
        set_t s = cand[chosen[i]];
        G.adj[u] |= s;
        while (s) { int x = CTZ(s); s &= s - 1; G.adj[x] |= BIT(u); }
    }
    nleaf++;
    if (!alpha_le(&G, K)) return;
    nout++;
    g6_write(stdout, &G);
}

static int first_bit_from(const uint64_t *b, int from)
{
    if (from >= N) return -1;
    int w = from >> 6;
    uint64_t x = b[w] & (~0ULL << (from & 63));
    for (;;) {
        if (x) return (w << 6) + CTZ(x);
        if (++w >= W) return -1;
        x = b[w];
    }
}

static void search(int depth, int start, const uint64_t *elig, int edges, set_t uni)
{
    nnodes++;
    if (depth == D) {
        if (edges < EMIN) return;
        for (int x = 0; x < m; x++) if (degH[x] + cnt[x] < DMIN) return;
        output();
        return;
    }
    int rem = D - depth;
    int f = first_bit_from(elig, start);
    if (f < 0) return;
    if (edges + rem * csz[f] > EMAX) return;
    if (edges + rem * (DMAX - 1) < EMIN) return;
    /* minimum degree: each deficient vertex must be coverable by remaining eligible sets */
    for (int x = 0; x < m; x++) {
        int need = DMIN - degH[x] - cnt[x];
        if (need <= 0) continue;
        if (need > rem) return;
        const uint64_t *cx = cont + (size_t)x * W;
        int ok = 0;
        for (int w = start >> 6; w < W; w++) {
            uint64_t t = elig[w] & cx[w];
            if (w == (start >> 6)) t &= ~0ULL << (start & 63);
            if (t) { ok = 1; break; }
        }
        if (!ok) return;
    }
    /* necessary condition on all chosen sets together */
    if (depth >= 3) {
        set_t all = (BIT(m) - 1) & ~uni;
        if (has_indep(H.adj, all, K - depth + 1)) return;
    }
    uint64_t *ne = malloc(sizeof(uint64_t) * W);
    for (int c = f; c >= 0; c = first_bit_from(elig, c + 1)) {
        if (edges + rem * csz[c] > EMAX) break;  /* sorted by size */
        set_t s = cand[c];
        /* degree upper bound */
        int bad = 0;
        set_t t = s;
        while (t) { int x = CTZ(t); t &= t - 1; if (degH[x] + cnt[x] + 1 > DMAX) { bad = 1; break; } }
        if (bad) continue;
        const uint64_t *cr = comp + (size_t)c * W;
        for (int w = 0; w < W; w++) ne[w] = elig[w] & cr[w];
        t = s;
        while (t) {
            int x = CTZ(t); t &= t - 1;
            cnt[x]++;
            if (degH[x] + cnt[x] == DMAX) {
                const uint64_t *cx = cont + (size_t)x * W;
                for (int w = 0; w < W; w++) ne[w] &= ~cx[w];
            }
        }
        chosen[depth] = c;
        /* repeat of c allowed only if self-compatible (comp row has bit c) */
        search(depth + 1, c, ne, edges + csz[c], uni | s);
        t = s;
        while (t) { int x = CTZ(t); t &= t - 1; cnt[x]--; }
    }
    free(ne);
}

/* enumerate independent sets of H with size in [lo,hi] whose vertices have degH <= DMAX-1 */
static set_t *lst; static int nl, capl;
static void push(set_t s) {
    if (nl == capl) { capl = capl ? 2 * capl : 1024; lst = realloc(lst, sizeof(set_t) * capl); }
    lst[nl++] = s;
}
static void enum_indep(set_t cur, int sz, set_t allowed, int lo, int hi)
{
    if (sz >= lo) push(cur);
    if (sz == hi) return;
    while (allowed) {
        int x = CTZ(allowed); allowed &= allowed - 1;
        enum_indep(cur | BIT(x), sz + 1, allowed & ~H.adj[x], lo, hi);
    }
}
static int cmp_size(const void *a, const void *b)
{
    int pa = POP(*(const set_t *)a), pb = POP(*(const set_t *)b);
    if (pa != pb) return pa - pb;
    set_t x = *(const set_t *)a, y = *(const set_t *)b;
    return x < y ? -1 : x > y;
}

static void process(void)
{
    m = H.n; eH = g_edges(&H);
    if (m + D + 1 > 64) { fprintf(stderr, "too big\n"); exit(1); }
    set_t allowed = 0;
    for (int x = 0; x < m; x++) {
        degH[x] = POP(H.adj[x]);
        if (degH[x] > DMAX) return;
        if (degH[x] + D < DMIN) return;
        if (degH[x] <= DMAX - 1) allowed |= BIT(x);
        cnt[x] = 0;
    }
    if (eH + D + D * (DMIN - 1) > EMAX) return;
    /* critical sets: independent (K-1)-sets of H */
    nl = 0;
    enum_indep(0, 0, BIT(m) - 1, K - 1, K - 1);
    int nL = nl; set_t *L = malloc(sizeof(set_t) * (nL ? nL : 1)); memcpy(L, lst, sizeof(set_t) * nL);
    /* candidates */
    nl = 0;
    int lo = DMIN - 1 < 0 ? 0 : DMIN - 1;
    enum_indep(0, 0, allowed, lo, DMAX - 1);
    qsort(lst, nl, sizeof(set_t), cmp_size);
    N = nl; W = (N + 63) / 64; if (W == 0) W = 1;
    cand = lst; csz = malloc(sizeof(int) * (N ? N : 1));
    for (int i = 0; i < N; i++) csz[i] = POP(cand[i]);
    /* avoid bitsets over L */
    int WL = (nL + 63) / 64; if (WL == 0) WL = 1;
    uint64_t *av = calloc((size_t)N * WL, sizeof(uint64_t));
    for (int i = 0; i < N; i++)
        for (int j = 0; j < nL; j++)
            if (!(cand[i] & L[j])) av[(size_t)i * WL + (j >> 6)] |= 1ULL << (j & 63);
    comp = calloc((size_t)N * W, sizeof(uint64_t));
    for (int i = 0; i < N; i++)
        for (int j = i; j < N; j++) {
            const uint64_t *a = av + (size_t)i * WL, *b = av + (size_t)j * WL;
            int ok = 1;
            for (int w = 0; w < WL; w++) if (a[w] & b[w]) { ok = 0; break; }
            if (ok) {
                comp[(size_t)i * W + (j >> 6)] |= 1ULL << (j & 63);
                comp[(size_t)j * W + (i >> 6)] |= 1ULL << (i & 63);
            }
        }
    cont = calloc((size_t)m * W, sizeof(uint64_t));
    for (int i = 0; i < N; i++) {
        set_t s = cand[i];
        while (s) { int x = CTZ(s); s &= s - 1; cont[(size_t)x * W + (i >> 6)] |= 1ULL << (i & 63); }
    }
    uint64_t *elig = calloc(W, sizeof(uint64_t));
    for (int i = 0; i < N; i++) elig[i >> 6] |= 1ULL << (i & 63);
    search(0, 0, elig, eH + D, 0);
    free(elig); free(cont); free(comp); free(av); free(csz); free(L);
}

int main(int argc, char **argv)
{
    int c;
    while ((c = getopt(argc, argv, "k:d:e:E:m:M:q")) != -1) {
        switch (c) {
        case 'k': K = atoi(optarg); break;
        case 'd': D = atoi(optarg); break;
        case 'e': EMAX = atoi(optarg); break;
        case 'E': EMIN = atoi(optarg); break;
        case 'm': DMIN = atoi(optarg); break;
        case 'M': DMAX = atoi(optarg); break;
        case 'q': quiet = 1; break;
        default: fprintf(stderr, "usage: glue -k K -d D [-e EMAX] [-E EMIN] [-m DMIN] [-M DMAX]\n"); return 1;
        }
    }
    if (K <= 1 || D <= 0) { fprintf(stderr, "need -k and -d\n"); return 1; }
    if (DMIN < 0) DMIN = D;
    if (DMAX < 0) DMAX = K;
    if (D > DMAX || D < DMIN) { return 0; }
    char line[4096];
    long long nin = 0;
    clock_t t0 = clock();
    while (fgets(line, sizeof line, stdin)) {
        if (line[0] == '\n' || line[0] == 0) continue;
        line[strcspn(line, "\r\n")] = 0;
        if (g6_read(line, &H)) { fprintf(stderr, "bad graph6: %s\n", line); continue; }
        nin++;
        process();
    }
    if (!quiet)
        fprintf(stderr, "glue K=%d d=%d e=[%d,%d] deg=[%d,%d]: in=%lld nodes=%lld leaves=%lld out=%lld cpu=%.2fs\n",
                K, D, EMIN, EMAX, DMIN, DMAX, nin, nnodes, nleaf, nout, (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 0;
}
