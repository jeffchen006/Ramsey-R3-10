/* gluefast.c - maximal independent sets, cached alpha and weighted owner refinement.
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
static int mtf_only;
static graph_t H;
static int m, eH, degH[64];
static set_t ALLH;

static int N, W;
static set_t *cand; static int *csz;
static uint64_t *comp, *cont;
static long long nout, nleaf, nnodes, ntuples;
static int chosen[64];
static int cover[64];          /* coverage by chosen maximal sets */
static uint64_t *next_rows;
static int *owner_min;
static size_t *off;
static set_t *owned;
static size_t owned_cap, owned_count;
static int attachment_min, suffix_min[64], suffix_max[64], suffix_hits[64][64];
static set_t alpha_keys[1 << 16];
static unsigned char alpha_values[1 << 16];
static unsigned int alpha_epochs[1 << 16], epoch;
static set_t max_unions[1 << 12], actual_unions[1 << 12];
static const int ramsey3[] = {0,1,3,6,9,14,18,23,28,36};
typedef struct { uint64_t lo, hi; } domain;
static domain *pair_support, domains[12][12];
static unsigned char *support_ready, *dense;

static inline unsigned int cache_slot(set_t mask)
{
    return (mask * UINT64_C(0x9e3779b97f4a7c15)) >> 48;
}

static int alpha(set_t mask)
{
    if (m <= 24) return dense[mask];
    if (!mask) return 0;
    unsigned int slot = cache_slot(mask);
    if (alpha_epochs[slot] == epoch && alpha_keys[slot] == mask)
        return alpha_values[slot];
    int vertex = CTZ(mask);
    set_t rest = mask & (mask - 1), excluded = rest & ~H.adj[vertex];
    int answer = 1 + alpha(excluded);
    if (rest != excluded) {
        int skip = alpha(rest);
        if (skip > answer) answer = skip;
    }
    alpha_epochs[slot] = epoch;
    alpha_keys[slot] = mask;
    alpha_values[slot] = answer;
    return answer;
}

static int domain_min(int owner, domain choices)
{
    if (choices.lo) return POP(owned[off[owner] + CTZ(choices.lo)]);
    if (choices.hi) return POP(owned[off[owner] + 64 + CTZ(choices.hi)]);
    return 1 << 20;
}

static domain support(int owner, int partner)
{
    size_t key = (size_t)owner*N + partner;
    if (support_ready[key]) return pair_support[key];
    domain result = {0, 0};
    for (size_t idx = off[owner]; idx < off[owner+1]; ++idx) {
        if (alpha(ALLH & ~(owned[idx] | cand[partner])) > K-2) continue;
        size_t local = idx - off[owner];
        if (local < 64) result.lo |= BIT(local);
        else result.hi |= BIT(local-64);
    }
    support_ready[key] = 1;
    return pair_support[key] = result;
}

static int pair_domains(int depth, int candidate, int budget)
{
    size_t length = off[candidate+1] - off[candidate];
    domain next = {length >= 64 ? UINT64_MAX : BIT(length) - 1,
                   length >= 128 ? UINT64_MAX : length >= 64 ? BIT(length-64)-1 : 0};
    int lower = 0;
    for (int idx = 0; idx < depth; ++idx) {
        domain other = support(candidate, chosen[idx]);
        next.lo &= other.lo;
        next.hi &= other.hi;
        if (!(next.lo | next.hi)) return 0;
        domain updated = domains[depth][idx], allowed = support(chosen[idx], candidate);
        updated.lo &= allowed.lo;
        updated.hi &= allowed.hi;
        lower += domain_min(chosen[idx], updated);
        if (lower > budget) return 0;
        domains[depth+1][idx] = updated;
    }
    lower += domain_min(candidate, next);
    if (lower > budget) return 0;
    domains[depth+1][depth] = next;
    return 1;
}

static int compatible(set_t set, int depth, int min_previous, const set_t *unions)
{
    int stop = 1 << depth;
    for (int prev = stop - 1; prev > 0; --prev) {
        int count = POP(prev);
        if (count >= min_previous && alpha(ALLH & ~(set | unions[prev])) >= K - count)
            return 0;
    }
    return 1;
}

static void save_union(set_t set, int depth, set_t *unions)
{
    int stop = 1 << depth;
    for (int prev = 0; prev < stop; ++prev)
        unions[prev | stop] = unions[prev] | set;
}

/* ---------- stage 2: subset expansion ---------- */
static set_t S[64];
static int cnt[64];

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
    if (mtf_only)
        for (int x = 0; x < m; ++x)
            for (int y = x+1; y < m; ++y)
                if (!(G.adj[x] & BIT(y)) && !(G.adj[x] & G.adj[y])) return;
    nout++;
    g6_write(stdout, &G);
}

static void expand(int depth, int edges, set_t saturated, set_t union_so_far)
{
    if (depth == D) { leaf(); return; }
    int budget = EMAX - edges;
    if (suffix_min[depth] > budget || suffix_max[depth] + edges < EMIN) return;
    int uncovered = m - POP(union_so_far) - (ramsey3[K-D+1]-1);
    if (uncovered > budget) return;
    set_t required = 0;
    int deficits = 0;
    int owner = chosen[depth];
    for (int vertex = 0; vertex < m; ++vertex) {
        int need = DMIN - degH[vertex] - cnt[vertex];
        if (need <= 0) continue;
        deficits += need;
        int later = suffix_hits[depth + 1][vertex];
        if (need > later) {
            if (need != later + 1 || !(cand[owner] & BIT(vertex))) return;
            required |= BIT(vertex);
        }
    }
    if (deficits > budget) return;
    int cap = budget - suffix_min[depth + 1];
    int floor = EMIN - edges - suffix_max[depth + 1];
    set_t previous = (depth && chosen[depth - 1] == owner) ? S[depth - 1] : 0;
    for (size_t idx = off[owner]; idx < off[owner+1]; ++idx) {
        size_t local = idx-off[owner];
        domain supported = domains[D][depth];
        if (local < 64 ? !(supported.lo & BIT(local)) : !(supported.hi & BIT(local-64))) continue;
        set_t set = owned[idx];
        int size = POP(set);
        if (size > cap || size < floor || set < previous || (set & saturated)
                || (set & required) != required) continue;
        if (!compatible(set, depth, 1, actual_unions)) continue;
        set_t newsat = saturated;
        for (set_t left = set; left; left &= left - 1) {
            int vertex = CTZ(left);
            if (++cnt[vertex] + degH[vertex] == DMAX) newsat |= BIT(vertex);
        }
        S[depth] = set;
        if (depth + 1 < D) save_union(set, depth, actual_unions);
        expand(depth + 1, edges + size, newsat, union_so_far | set);
        for (set_t left = set; left; left &= left - 1) --cnt[CTZ(left)];
    }
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

static void search(int depth, int start, const uint64_t *elig, int maxedges, int minedges)
{
    nnodes++;
    int rem = D - depth;
    if (depth == D) {
        for (int x = 0; x < m; x++) if (degH[x] + cover[x] < DMIN) return;
        if (maxedges < EMIN) return;
        ntuples++;
        if (mtf_only) {
            for (int x = 0; x < m; ++x) {
                if (!cover[x] || degH[x] + cover[x] > DMAX) return;
                cnt[x] = cover[x];
            }
            for (int i = 0; i < D; ++i) S[i] = cand[chosen[i]];
            leaf();
            return;
        }
        suffix_min[D] = suffix_max[D] = 0;
        memset(suffix_hits[D], 0, sizeof suffix_hits[D]);
        for (int level = D - 1; level >= 0; --level) {
            int owner = chosen[level];
            suffix_min[level] = suffix_min[level + 1] + owner_min[owner];
            int actual_cap = csz[owner] < DMAX - 1 ? csz[owner] : DMAX - 1;
            suffix_max[level] = suffix_max[level + 1] + actual_cap;
            for (int vertex = 0; vertex < m; ++vertex)
                suffix_hits[level][vertex] = suffix_hits[level + 1][vertex] + !!(cand[owner] & BIT(vertex));
        }
        expand(0, eH + D, 0, 0);
        return;
    }
    int f = first_bit_from(elig, start);
    if (f < 0) return;
    if (maxedges + rem * (DMAX - 1) < EMIN) return;
    for (int x = 0; x < m; x++) {
        int minimum = DMIN - degH[x];
        if (mtf_only && minimum < 1) minimum = 1;
        int need = minimum - cover[x];
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
    uint64_t *ne = next_rows + (size_t)depth * W;
    for (int c = f; c >= 0; c = first_bit_from(elig, c + 1)) {
        if (minedges + owner_min[c] + (rem - 1) * attachment_min > EMAX) continue;
        if (!mtf_only && !pair_domains(depth, c, EMAX - eH - D - (rem - 1)*attachment_min)) continue;
        set_t s = cand[c];
        if (mtf_only) {
            int ok = 1;
            for (set_t left = s; left; left &= left-1) {
                int x = CTZ(left);
                if (cover[x] + degH[x] >= DMAX) { ok = 0; break; }
            }
            if (!ok) continue;
        }
        if (!compatible(s, depth, 2, max_unions)) continue;
        const uint64_t *cr = comp + (size_t)c * W;
        if (rem > 1) {
            uint64_t any = 0;
            for (int w = c >> 6; w < W; w++) {
                ne[w] = elig[w] & cr[w];
                if (w == (c >> 6)) ne[w] &= UINT64_MAX << (c & 63);
                any |= ne[w];
            }
            if (!any) continue;
        }
        set_t t = s; while (t) { int x = CTZ(t); t &= t - 1; cover[x]++; }
        chosen[depth] = c;
        if (rem > 1) save_union(s, depth, max_unions);
        search(depth + 1, c, ne, maxedges + csz[c], minedges + owner_min[c]);
        t = s; while (t) { int x = CTZ(t); t &= t - 1; cover[x]--; }
    }
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

static void make_owner_lists(void)
{
    size_t capacity = 1;
    size_t upper = 0;
    for (int i = 0; i < N; ++i) upper += (size_t)1 << csz[i];
    while (capacity < 2 * upper + 1) capacity *= 2;
    set_t *seen = calloc(capacity, sizeof *seen);
    if (!seen) { perror("owner map"); exit(1); }
    owned_count = 0;
    off = malloc((N + 1) * sizeof *off);
    owner_min = malloc((N + 1) * sizeof *owner_min);
    for (int i = 0; i < N; ++i) {
        off[i] = owned_count;
        owner_min[i] = 1 << 20;
        const set_t max = cand[i];
        for (set_t child = max; ; child = (child - 1) & max) {
            int size = POP(child);
            if (size >= attachment_min && size < DMAX) {
                size_t idx = ((child + 1) * UINT64_C(0x9e3779b97f4a7c15)) >> 32;
                idx &= capacity - 1;
                while (seen[idx] && seen[idx] != child + 1) idx = (idx + 1) & (capacity - 1);
                if (!seen[idx]) {
                    seen[idx] = child + 1;
                    if (owned_count == owned_cap) {
                        owned_cap = owned_cap ? 2 * owned_cap : 1024;
                        owned = realloc(owned, owned_cap * sizeof *owned);
                        if (!owned) { perror("owned sets"); exit(1); }
                    }
                    owned[owned_count++] = child;
                    if (size < owner_min[i]) owner_min[i] = size;
                }
            }
            if (!child) break;
        }
    }
    off[N] = owned_count;
    for (int i = 0; i < N; ++i) {
        for (size_t pos = off[i]+1; pos < off[i+1]; ++pos) {
            set_t value = owned[pos]; size_t swap = pos;
            while (swap > off[i] && POP(owned[swap-1]) > POP(value)) {
                owned[swap] = owned[swap-1];
                --swap;
            }
            owned[swap] = value;
        }
    }
    free(seen);
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
    ++epoch;
    attachment_min = DMIN > 0 ? DMIN - 1 : 0;
    int budget = EMAX - eH - D;
    if (budget < D * attachment_min || budget < m - (ramsey3[K-D+1] - 1)) return;
    if (m <= 24) {
        dense = realloc(dense, (size_t)1 << m);
        if (!dense) { perror("alpha table"); exit(1); }
        dense[0] = 0;
        for (set_t mask = 1; mask <= ALLH; ++mask) {
            set_t rest = mask & (mask-1);
            int take = 1+ dense[rest & ~H.adj[CTZ(mask)]];
            int drop = dense[rest];
            dense[mask] = take > drop ? take : drop;
        }
    }
    /* critical (K-1)-sets of H (all vertices) */
    nl = 0; enum_size(0, 0, ALLH, K - 1);
    int nL = nl; set_t *L = malloc(sizeof(set_t) * (nL ? nL : 1)); memcpy(L, lst, sizeof(set_t) * nL);
    /* maximal independent sets of H[allowed] */
    nl = 0; bk(0, allowed, 0, allowed);
    int keep = 0;
    for (int i = 0; i < nl; i++) {
        set_t set = lst[i];
        if (POP(set) < DMIN - 1) continue;
        if (mtf_only) {
            if (POP(set) >= DMAX) continue;
            set_t dominated = set;
            for (set_t left = set; left; left &= left-1) dominated |= H.adj[CTZ(left)];
            if (dominated != ALLH) continue;
        }
        lst[keep++] = set;
    }
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
            if (mtf_only && POP(cand[i] | cand[j]) < m + D - ramsey3[K-1] - 1) continue;
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
    if (mtf_only) {
        owner_min = malloc((N + 1) * sizeof *owner_min);
        off = NULL;
        for (int i = 0; i < N; ++i) owner_min[i] = csz[i];
    } else {
        make_owner_lists();
        pair_support = malloc((size_t)N * N * sizeof *pair_support);
        support_ready = calloc((size_t)N * N, 1);
        if (N && (!pair_support || !support_ready)) { perror("pair supports"); exit(1); }
    }
    uint64_t *elig = calloc(W, sizeof(uint64_t));
    next_rows = realloc(next_rows, (size_t)D * W * sizeof *next_rows);
    for (int i = 0; i < N; i++)
        if (owner_min[i] + (D - 1) * attachment_min <= budget)
            elig[i >> 6] |= 1ULL << (i & 63);
    search(0, 0, elig, eH + D, eH + D);
    if (!mtf_only) { free(pair_support); free(support_ready); }
    free(owner_min); free(off);
    free(elig); free(cont); free(comp); free(av); free(csz); free(L);
}

int main(int argc, char **argv)
{
    int c;
    while ((c = getopt(argc, argv, "k:d:e:E:m:M:qX")) != -1) {
        switch (c) {
        case 'k': K = atoi(optarg); break;
        case 'd': D = atoi(optarg); break;
        case 'e': EMAX = atoi(optarg); break;
        case 'E': EMIN = atoi(optarg); break;
        case 'm': DMIN = atoi(optarg); break;
        case 'M': DMAX = atoi(optarg); break;
        case 'q': quiet = 1; break;
        case 'X': mtf_only = 1; break;
        default: fprintf(stderr, "usage: glue2 -k K -d D [-e EMAX] [-E EMIN] [-m DMIN] [-M DMAX]\n"); return 1;
        }
    }
    if (K <= 1 || K > 8 || D <= 0 || D > K || K-D+1 > 9) {
        fprintf(stderr, "need 1 <= d <= k <= 9 and k >= 2\n"); return 1;
    }
    if (DMIN < 0) DMIN = D;
    if (DMAX < 0) DMAX = K;
    if (D > DMAX || D < DMIN) return 0;
    char line[4096];
    long long nin = 0;
    clock_t t0 = clock();
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\r\n")] = 0;
        if (!line[0]) continue;
        if (g6_read(line, &H)) { fprintf(stderr, "bad graph6: %s\n", line); return 1; }
        nin++;
        process();
    }
    if (!quiet)
        fprintf(stderr, "gluefast K=%d d=%d e=[%d,%d] deg=[%d,%d]: in=%lld nodes=%lld tuples=%lld leaves=%lld out=%lld cpu=%.2fs\n",
                K, D, EMIN, EMAX, DMIN, DMAX, nin, nnodes, ntuples, nleaf, nout, (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 0;
}
