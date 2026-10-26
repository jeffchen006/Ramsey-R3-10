/* glue2.c - neighbourhood gluing with maximal independent sets (Angeltveit 2024, Sec. 4.2).
 * Same interface and output set as glue.c (cross-checked), different algorithm:
 *  1. candidates = maximal independent sets M of H[allowed] with |M| >= DMIN-1;
 *     allowed = vertices with degH <= DMAX-1.
 *  2. search multisets M_1 <= ... <= M_d of candidates, pairwise compatible
 *     (alpha(H - M_i - M_j) <= K-2), with monotone prunings only: min degree
 *     coverage, edge lower bound EMIN, alpha(H - union) <= K - depth.
 *  3. for each such tuple, expand S_i subset of M_i with canonical owner(S_i) = M_i
 *     (owner = lowest-index candidate containing S_i), prune on DMAX, EMAX,
 *     then exact alpha(G) <= K and degree/edge checks at the leaf.
 * Lemma (Angeltveit Lemma 4.1): supersets of compatible sets are compatible, so every
 * valid tuple (S_i) is found exactly under the tuple (owner(S_i)) sorted.
 * usage: glue2 -k K -d D [-e EMAX] [-E EMIN] [-m DMIN] [-M DMAX] [-q]
 */
#include "gutil.h"
#include <getopt.h>
#include <time.h>

static int K, D, EMAX = 1 << 30, EMIN = 0, DMIN = -1, DMAX = -1, quiet = 0;
static graph_t H;
static int m, eH, degH[64];
static set_t ALLH;

static int N, W;
static set_t *cand; static int *csz;
static uint64_t *comp, *cont;
static long long nout, nleaf, nnodes, ntuples;
static int chosen[64];
static int cover[64];          /* coverage by chosen maximal sets */

/* ---------- stage 2: subset expansion ---------- */
static set_t S[64];
static int cnt[64];

static int owner_ok(set_t s, int idx)
{
    for (int j = 0; j < idx; j++) if ((cand[j] & s) == s) return 0;
    return 1;
}

static void leaf(void)
{
    nleaf++;
    int edges = eH + D;
    for (int i = 0; i < D; i++) edges += POP(S[i]);
    if (edges < EMIN || edges > EMAX) return;
    for (int x = 0; x < m; x++) { int dg = degH[x] + cnt[x]; if (dg < DMIN || dg > DMAX) return; }
    graph_t G; memset(&G, 0, sizeof G);
    G.n = m + D + 1;
    for (int x = 0; x < m; x++) G.adj[x] = H.adj[x];
    int v = m + D;
    for (int i = 0; i < D; i++) {
        int u = m + i;
        G.adj[u] |= BIT(v) | S[i]; G.adj[v] |= BIT(u);
        set_t s = S[i]; while (s) { int x = CTZ(s); s &= s - 1; G.adj[x] |= BIT(u); }
    }
    if (!alpha_le(&G, K)) return;
    nout++;
    g6_write(stdout, &G);
}

/* enumerate subsets of M_i: choose S[i] by deciding elements of rest (remaining undecided) */
static void expand(int i, int edges);
static void sub_rec(int i, set_t keep, set_t undecided, int edges)
{
    /* edges: edges so far counting S[0..i-1]; keep: elements included so far */
    if (!undecided) {
        int sz = POP(keep);
        if (sz < DMIN - 1 || sz + 1 > DMAX) return;
        /* duplicate control: if M_i == M_{i-1}, require S[i] >= S[i-1] (as integers) */
        if (i > 0 && chosen[i] == chosen[i - 1] && keep < S[i - 1]) return;
        if (edges + sz + (D - i - 1) * (DMIN - 1 > 0 ? DMIN - 1 : 0) > EMAX) return;
        if (!owner_ok(keep, chosen[i])) return;
        /* subset-level compatibility with earlier S_j (not monotone downwards, so re-check) */
        set_t uni = keep;
        for (int j = 0; j < i; j++) {
            if (has_indep(H.adj, ALLH & ~(keep | S[j]), K - 1)) return;
            uni |= S[j];
        }
        if (i >= 2 && has_indep(H.adj, ALLH & ~uni, K - i)) return;
        S[i] = keep;
        set_t t = keep; while (t) { int x = CTZ(t); t &= t - 1; cnt[x]++; }
        expand(i + 1, edges + sz);
        t = keep; while (t) { int x = CTZ(t); t &= t - 1; cnt[x]--; }
        return;
    }
    int x = CTZ(undecided); set_t u2 = undecided & (undecided - 1);
    /* remaining sets after i: D - i - 1, each adds at most |M_j| */
    /* include x if degree allows */
    if (degH[x] + cnt[x] + 1 <= DMAX && edges + POP(keep) + 1 + (D - i - 1) * (DMIN - 1 > 0 ? DMIN - 1 : 0) <= EMAX)
        sub_rec(i, keep | BIT(x), u2, edges);
    /* exclude x: x must still be able to reach DMIN with remaining sets j > i containing x */
    {
        int later = 0;
        for (int j = i + 1; j < D; j++) if (cand[chosen[j]] & BIT(x)) later++;
        if (degH[x] + cnt[x] + later >= DMIN) sub_rec(i, keep, u2, edges);
    }
}

static void expand(int i, int edges)
{
    if (i == D) { leaf(); return; }
    /* edge bounds: remaining sets at most sum |M_j|, at least (DMIN-1) each */
    int maxrest = 0;
    for (int j = i; j < D; j++) maxrest += csz[chosen[j]];
    if (edges + maxrest < EMIN) return;
    if (edges + (D - i) * (DMIN - 1 > 0 ? DMIN - 1 : 0) > EMAX) return;
    sub_rec(i, 0, cand[chosen[i]], edges);
}

/* ---------- stage 1: maximal tuples ---------- */
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

static void search(int depth, int start, const uint64_t *elig, int maxedges, set_t uni)
{
    nnodes++;
    int rem = D - depth;
    if (depth == D) {
        for (int x = 0; x < m; x++) if (degH[x] + cover[x] < DMIN) return;
        if (maxedges < EMIN) return;
        ntuples++;
        expand(0, eH + D);
        return;
    }
    int f = first_bit_from(elig, start);
    if (f < 0) return;
    if (maxedges + rem * (DMAX - 1) < EMIN) return;
    for (int x = 0; x < m; x++) {
        int need = DMIN - degH[x] - cover[x];
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
    if (depth >= 3 && has_indep(H.adj, ALLH & ~uni, K - depth + 1)) return;
    uint64_t *ne = malloc(sizeof(uint64_t) * W);
    for (int c = f; c >= 0; c = first_bit_from(elig, c + 1)) {
        set_t s = cand[c];
        const uint64_t *cr = comp + (size_t)c * W;
        for (int w = 0; w < W; w++) ne[w] = elig[w] & cr[w];
        set_t t = s; while (t) { int x = CTZ(t); t &= t - 1; cover[x]++; }
        chosen[depth] = c;
        search(depth + 1, c, ne, maxedges + csz[c], uni | s);
        t = s; while (t) { int x = CTZ(t); t &= t - 1; cover[x]--; }
    }
    free(ne);
}

static set_t *lst; static int nl, capl;
static void push(set_t s) {
    if (nl == capl) { capl = capl ? 2 * capl : 1024; lst = realloc(lst, sizeof(set_t) * capl); }
    lst[nl++] = s;
}
/* all independent sets of exact size sz inside allowed */
static void enum_size(set_t cur, int s, set_t allowed, int sz)
{
    if (s == sz) { push(cur); return; }
    while (allowed) {
        if (POP(allowed) < sz - s) return;
        int x = CTZ(allowed); allowed &= allowed - 1;
        enum_size(cur | BIT(x), s + 1, allowed & ~H.adj[x], sz);
    }
}
/* maximal independent sets within allowed (Bron-Kerbosch on complement, with pivot) */
static void bk(set_t R, set_t P, set_t X, set_t allowed)
{
    if (!P && !X) { push(R); return; }
    /* pivot: vertex u in P|X maximising |P & nonnbr(u)| */
    set_t PX = P | X; int best = -1, bc = -1;
    while (PX) {
        int u = CTZ(PX); PX &= PX - 1;
        int c = POP(P & ~H.adj[u] & ~BIT(u));
        if (c > bc) { bc = c; best = u; }
    }
    set_t cands = P & (H.adj[best] | BIT(best));   /* vertices adjacent (in H) to pivot, or pivot */
    while (cands) {
        int v = CTZ(cands); cands &= cands - 1;
        set_t nn = allowed & ~H.adj[v] & ~BIT(v);   /* non-neighbours of v */
        bk(R | BIT(v), P & nn, X & nn, allowed);
        P &= ~BIT(v); X |= BIT(v);
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
    m = H.n; eH = g_edges(&H); ALLH = m ? (BIT(m) - 1) : 0;
    if (m + D + 1 > 64) { fprintf(stderr, "too big\n"); exit(1); }
    set_t allowed = 0;
    for (int x = 0; x < m; x++) {
        degH[x] = POP(H.adj[x]);
        if (degH[x] > DMAX) return;
        if (degH[x] + D < DMIN) return;
        if (degH[x] <= DMAX - 1) allowed |= BIT(x);
        cover[x] = cnt[x] = 0;
    }
    /* critical (K-1)-sets of H (all vertices) */
    nl = 0; enum_size(0, 0, ALLH, K - 1);
    int nL = nl; set_t *L = malloc(sizeof(set_t) * (nL ? nL : 1)); memcpy(L, lst, sizeof(set_t) * nL);
    /* maximal independent sets of H[allowed] */
    nl = 0; bk(0, allowed, 0, allowed);
    int keep = 0;
    for (int i = 0; i < nl; i++) if (POP(lst[i]) >= DMIN - 1) lst[keep++] = lst[i];
    nl = keep;
    qsort(lst, nl, sizeof(set_t), cmp_size);
    N = nl; W = (N + 63) / 64; if (!W) W = 1;
    cand = lst; csz = malloc(sizeof(int) * (N ? N : 1));
    for (int i = 0; i < N; i++) csz[i] = POP(cand[i]);
    int WL = (nL + 63) / 64; if (!WL) WL = 1;
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
    cont = calloc((size_t)(m ? m : 1) * W, sizeof(uint64_t));
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
        default: fprintf(stderr, "usage: glue2 -k K -d D [-e EMAX] [-E EMIN] [-m DMIN] [-M DMAX]\n"); return 1;
        }
    }
    if (K <= 1 || D <= 0) { fprintf(stderr, "need -k and -d\n"); return 1; }
    if (DMIN < 0) DMIN = D;
    if (DMAX < 0) DMAX = K;
    if (D > DMAX || D < DMIN) return 0;
    char line[4096];
    long long nin = 0;
    clock_t t0 = clock();
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\r\n")] = 0;
        if (!line[0]) continue;
        if (g6_read(line, &H)) { fprintf(stderr, "bad graph6: %s\n", line); continue; }
        nin++;
        process();
    }
    if (!quiet)
        fprintf(stderr, "glue2 K=%d d=%d e=[%d,%d] deg=[%d,%d]: in=%lld nodes=%lld tuples=%lld leaves=%lld out=%lld cpu=%.2fs\n",
                K, D, EMIN, EMAX, DMIN, DMAX, nin, nnodes, ntuples, nleaf, nout, (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 0;
}
