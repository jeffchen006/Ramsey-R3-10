/* glue3.c - glue.c + per-input table of alpha(H[S]) for all S (GR 2013 Sec. 3; [Ang] 4.3), m <= TMAX.
 * Same interface and output set as glue.c. Changes: on each new set S_j, check every subset T of the
 * chosen sets that contains j: alpha(H - union T) <= K - |T| (table lookup, incremental unions);
 * the leaf alpha(G) <= K test is then implied (independent sets of G containing v are in H + v,
 * those without v are I_H + {u_i : i in T}), so no has_indep at the leaf.
 * Falls back to glue.c behaviour if m > TMAX.
 * glue5: + candidate index range limited by the edge budget (sets sorted by size);
 * glue4: + colouring bound (rem >= COLMIN) (clique search): split eligible sets into greedy classes of pairwise
 * incompatible sets; a valid completion takes <= 1 set per class, so prune if < rem classes, or if
 * edges + sum of the rem smallest class minima > EMAX (sets sorted by size). Skipped if a
 * self-compatible set is eligible (it may be repeated).
 * Based on glue.c - neighbourhood gluing extender (Goedgebeur-Radziszowski 2013, Sec. 3).
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
#ifndef COLMIN
#define COLMIN 3
#endif
#define CUT (void)0

static int K, D, EMAX = 1 << 30, EMIN = 0, DMIN = -1, DMAX = -1, quiet = 0;

static graph_t H;
static int m, eH, degH[64];

/* candidates */
static int N, W;               /* number of candidates, words per bitset over candidates */
static set_t *cand;            /* cand[i] = vertex set */
static int *csz;
static uint64_t *comp;         /* comp[i*W..] compat bitset row */
static uint64_t *cont;
static uint64_t *selfc;        /* self-compatible candidates */
static uint64_t *Pbuf, *Qbuf;         /* cont[x*W..] candidates containing x */
static clock_t pair_time, search_time;
static uint64_t extra_mask, incident[64], edge_id[64][64], *set_mask;
static int from[64], to[64];

static long long nout, nleaf, nnodes;
static int chosen[64];
#define TMAX 26
static unsigned char *atab; static int use_tab;
static set_t uni_m[1 << 12];  /* uni_m[mask] = union of chosen sets in mask */
static void build_tab(void)
{
    size_t N2 = (size_t)1 << m;
    atab = realloc(atab, N2);
    atab[0] = 0;
    for (size_t S = 1; S < N2; S++) {
        int x = CTZ(S);
        unsigned char a = atab[S & (S - 1)], b = 1 + atab[S & ~H.adj[x] & ~BIT(x)];
        atab[S] = a > b ? a : b;
    }
}
static int cnt[64];

static uint64_t core_keys[1<<16], core_masks[1<<16];
static unsigned int core_stamps[1<<16], core_epoch;

static uint64_t repair(set_t residual, int target)
{
    if (atab[residual] < target) return extra_mask;
    if (atab[residual] > target || target < 2) return 0;
    unsigned int slot = (residual*UINT64_C(0x9e3779b97f4a7c15)) >> 48;
    if (core_stamps[slot] == core_epoch && core_keys[slot] == residual)
        return core_masks[slot];
    set_t core = 0;
    uint64_t result = 0;
    for (set_t left = residual; left; left &= left-1) {
        int vertex = CTZ(left);
        if (atab[residual ^ BIT(vertex)] == target) continue;
        for (set_t prior = core; prior; prior &= prior-1) result |= edge_id[vertex][CTZ(prior)];
        core |= BIT(vertex);
    }
    core_stamps[slot] = core_epoch;
    core_keys[slot] = residual;
    core_masks[slot] = result;
    return result;
}

static void output(uint64_t repairs)
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
    for (; repairs; repairs &= repairs-1) {
        int edge = CTZ(repairs), left = from[edge], right = to[edge];
        G.adj[left] ^= BIT(right); G.adj[right] ^= BIT(left);
        ++nout;
        g6_write(stdout, &G);
        G.adj[left] ^= BIT(right); G.adj[right] ^= BIT(left);
    }
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

static int hix[65];            /* hix[s] = last candidate index with size <= s, -1 if none */
static uint64_t *nebuf[16];

static int first_bit_range(const uint64_t *b, int from, int to)
{
    if (from > to) return -1;
    int w = from >> 6, wt = to >> 6;
    uint64_t x = b[w] & (~0ULL << (from & 63));
    for (;;) {
        if (w == wt) { if ((to & 63) != 63) x &= (2ULL << (to & 63)) - 1; return x ? (w << 6) + CTZ(x) : -1; }
        if (x) return (w << 6) + CTZ(x);
        x = b[++w];
    }
}

/* elig is valid on candidate indices [start, hi]; indices > hi count as not eligible */
static void search(int depth, int start, const uint64_t *elig, int hi, int edges, uint64_t repairs)
{
    nnodes++;
    if (depth == D) {
        if (edges < EMIN) return;
        for (int x = 0; x < m; x++) {
            int degree = degH[x] + cnt[x];
            if (degree < DMIN - 1) return;
            if (degree < DMIN) repairs &= incident[x];
            if (degree == DMAX) repairs &= ~incident[x];
        }
        if (repairs) output(repairs);
        return;
    }
    int rem = D - depth, B = EMAX - edges;
    if (B < 0) return;
    int lim = hix[B / rem > 64 ? 64 : B / rem]; if (lim > hi) lim = hi;
    int f = first_bit_range(elig, start, lim);
    if (f < 0) return;
    if (edges + rem * (DMAX - 1) < EMIN) return;
    for (int x = 0; x < m; x++) {
        int need = DMIN - degH[x] - cnt[x] - !!(repairs & incident[x]);
        if (need <= 0) continue;
        if (need > rem) return;
        const uint64_t *cx = cont + (size_t)x * W;
        int ok = 0;
        for (int w = start >> 6; w <= (hi >> 6); w++) {
            uint64_t t = elig[w] & cx[w];
            if (w == (start >> 6)) t &= ~0ULL << (start & 63);
            if (w == (hi >> 6) && (hi & 63) != 63) t &= (2ULL << (hi & 63)) - 1;
            if (t) { ok = 1; break; }
        }
        if (!ok) return;
    }
    if (rem >= COLMIN) {
        int w0 = start >> 6, w1 = hi >> 6, sc = 0;
        for (int w = w0; w <= w1; w++) {
            uint64_t t = elig[w]; if (w == w0) t &= ~0ULL << (start & 63);
            if (w == w1 && (hi & 63) != 63) t &= (2ULL << (hi & 63)) - 1;
            Pbuf[w] = t; if (t & selfc[w]) sc = 1;
        }
        if (!sc) {
            int e2 = edges, k = 0;
            while (k < rem) {
                int v = first_bit_range(Pbuf, start, hi);
                if (v < 0) break;
                e2 += csz[v]; k++;
                for (int w = w0; w <= w1; w++) Qbuf[w] = Pbuf[w];
                while (v >= 0) {
                    Pbuf[v >> 6] &= ~(1ULL << (v & 63));
                    const uint64_t *cr = comp + (size_t)v * W;
                    for (int w = v >> 6; w <= w1; w++) Qbuf[w] &= ~cr[w];
                    Qbuf[v >> 6] &= ~(1ULL << (v & 63));
                    v = first_bit_range(Qbuf, v + 1, hi);
                }
            }
            if (k < rem || e2 > EMAX) { CUT; return; }
        }
    }
    uint64_t *ne = nebuf[depth];
    for (int c = f; c >= 0 && c <= lim; c = first_bit_range(elig, c + 1, lim)) {
        uint64_t new_repairs = repairs & set_mask[c];
        if (!new_repairs) continue;
        set_t s = cand[c];
        int bad = 0;
        set_t t = s;
        while (t) {
            int x = CTZ(t); t &= t - 1;
            if (degH[x] + cnt[x] + 1 > DMAX) { bad = 1; break; }
            if (degH[x] + cnt[x] + 1 == DMAX) new_repairs &= ~incident[x];
        }
        if (bad || !new_repairs) continue;
        if (depth >= 1) {
            set_t full = BIT(m) - 1; int half = 1 << depth;
            for (int mk = 1; mk < half; mk++) {
                set_t u2 = uni_m[mk] | s;
                new_repairs &= repair(full & ~u2, K - POP(mk));
                if (!new_repairs) break;
            }
            if (!new_repairs) continue;
        }
        int r2 = rem - 1, B2 = B - csz[c], hi2 = -1;
        if (r2 > 0) {
            int smax = B2 - (r2 - 1) * csz[c]; if (smax > 64) smax = 64;
            hi2 = hix[smax]; if (hi2 > hi) hi2 = hi;
            int s1 = B2 / r2; if (s1 > 64) s1 = 64;
            int lim1 = hix[s1]; if (lim1 > hi2) lim1 = hi2;
            if (lim1 < c) continue;
            const uint64_t *cr = comp + (size_t)c * W;
            int w0 = c >> 6, wl = lim1 >> 6, w2 = hi2 >> 6, any = 0;
            for (int w = w0; w <= wl; w++) {
                uint64_t x = elig[w] & cr[w];
                if (w == w0) x &= ~0ULL << (c & 63);
                if (w == wl && (lim1 & 63) != 63) any |= (x & ((2ULL << (lim1 & 63)) - 1)) != 0; else any |= x != 0;
                ne[w] = x;
            }
            if (!any) continue;
            for (int w = wl + 1; w <= w2; w++) ne[w] = elig[w] & cr[w];
            t = s;
            while (t) {
                int x = CTZ(t); t &= t - 1;
                if (degH[x] + cnt[x] + 1 == DMAX) {
                    const uint64_t *cx = cont + (size_t)x * W;
                    for (int w = w0; w <= w2; w++) ne[w] &= ~cx[w];
                }
            }
        }
        t = s;
        while (t) { int x = CTZ(t); t &= t - 1; cnt[x]++; }
        if (use_tab) { int half = 1 << depth; for (int mk = 0; mk < half; mk++) uni_m[half + mk] = uni_m[mk] | s; }
        chosen[depth] = c;
        search(depth + 1, c, ne, hi2, edges + csz[c], new_repairs);
        t = s;
        while (t) { int x = CTZ(t); t &= t - 1; cnt[x]--; }
    }
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

static void process_group(int span)
{
    m = H.n; eH = g_edges(&H)+1;
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
    memset(edge_id, 0, sizeof edge_id);
    memset(incident, 0, sizeof incident);
    extra_mask = 0;
    int passed = 0, registered = 0;
    for (int right = 0; right < m && registered < 64; ++right)
        for (int left = 0; left < right && registered < 64; ++left) {
            if ((H.adj[left] & BIT(right)) || (H.adj[left] & H.adj[right]) ||
                    degH[left] == DMAX || degH[right] == DMAX) continue;
            if (passed++ < span) continue;
            uint64_t option = BIT(registered);
            extra_mask |= option;
            from[registered] = left;
            to[registered++] = right;
            edge_id[left][right] = edge_id[right][left] = option;
            incident[left] |= option;
            incident[right] |= option;
        }
    if (!extra_mask) return;
    ++core_epoch;
    use_tab = (m <= TMAX);
    if (!use_tab) exit(2);
    build_tab(); uni_m[0] = 0;
    /* candidates */
    nl = 0;
    int lo = DMIN - 1 < 0 ? 0 : DMIN - 1;
    enum_indep(0, 0, allowed, lo, DMAX - 1);
    qsort(lst, nl, sizeof(set_t), cmp_size);
    N = nl; W = (N + 63) / 64; if (W == 0) W = 1;
    cand = lst; csz = malloc(sizeof(int) * (N ? N : 1));
    set_mask = malloc((N ? N : 1) * sizeof *set_mask);
    if (!set_mask || !csz) { perror("candidate lists"); exit(1); }
    for (int i = 0; i < N; i++) {
        csz[i] = POP(cand[i]);
        uint64_t options = extra_mask;
        for (set_t vertices = cand[i]; vertices; vertices &= vertices-1) {
            int vertex = CTZ(vertices);
            for (set_t prior = vertices & (vertices-1); prior; prior &= prior-1)
                options &= ~edge_id[vertex][CTZ(prior)];
        }
        set_mask[i] = options;
    }
    clock_t started = clock();
    cont = calloc((size_t)m * W, sizeof(uint64_t));
    for (int i = 0; i < N; i++) {
        set_t s = cand[i];
        while (s) { int x = CTZ(s); s &= s - 1; cont[(size_t)x * W + (i >> 6)] |= 1ULL << (i & 63); }
    }
    comp = calloc((size_t)N * W, sizeof *comp);
    if (N && !comp) { perror("compatibility rows"); exit(1); }
    const int budget = EMAX-eH-D;
    const set_t all = BIT(m)-1;
    if (D >= 2) for (int i = 0; i < N; ++i) {
        if (csz[i]*2 + (D-2)*lo > budget) break;
        for (int j = i; j < N && csz[i]+csz[j]+(D-2)*lo <= budget; ++j) {
            uint64_t options = set_mask[i] & set_mask[j];
            if (!(options & repair(all & ~(cand[i] | cand[j]), K-1))) continue;
            comp[(size_t)i*W+(j>>6)] |= BIT(j&63);
            comp[(size_t)j*W+(i>>6)] |= BIT(i&63);
        }
    }
    pair_time += clock() - started;
    selfc = calloc(W, sizeof(uint64_t)); Pbuf = calloc(W, sizeof(uint64_t)); Qbuf = calloc(W, sizeof(uint64_t));
    for (int i = 0; i < N; i++) if (comp[(size_t)i * W + (i >> 6)] >> (i & 63) & 1) selfc[i >> 6] |= 1ULL << (i & 63);
    uint64_t *elig = calloc(W, sizeof(uint64_t));
    for (int i = 0; i < N; i++) elig[i >> 6] |= 1ULL << (i & 63);
    for (int sz = 0, i = -1; sz <= 64; sz++) { while (i + 1 < N && csz[i + 1] <= sz) i++; hix[sz] = i; }
    for (int dd = 0; dd <= D; dd++) nebuf[dd] = realloc(nebuf[dd], sizeof(uint64_t) * W);
    started = clock();
    search(0, 0, elig, N - 1, eH + D, extra_mask);
    search_time += clock() - started;
    free(selfc); free(Pbuf); free(Qbuf);
    free(elig); free(cont); free(comp); free(csz); free(set_mask);
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
    if (K <= 1 || K > 9 || D <= 0 || D > K) { fprintf(stderr, "need 1 <= d <= k <= 9\n"); return 1; }
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
        int eligible = 0;
        for (int right = 0; right < H.n; ++right)
            for (int left = 0; left < right; ++left)
                if (!(H.adj[left] & BIT(right)) && !(H.adj[left] & H.adj[right]) &&
                        POP(H.adj[left]) < DMAX && POP(H.adj[right]) < DMAX) ++eligible;
        for (int offset = 0; offset < eligible; offset += 64) process_group(offset);
    }
    if (!quiet)
        fprintf(stderr, "glue K=%d d=%d e=[%d,%d] deg=[%d,%d]: in=%lld nodes=%lld leaves=%lld out=%lld cpu=%.2fs\n",
                K, D, EMIN, EMAX, DMIN, DMAX, nin, nnodes, nleaf, nout, (double)(clock() - t0) / CLOCKS_PER_SEC);
    if (!quiet)
        fprintf(stderr, "transposed pair CPU %.3fs search CPU %.3fs\n",
                (double)pair_time / CLOCKS_PER_SEC, (double)search_time / CLOCKS_PER_SEC);
    return 0;
}
