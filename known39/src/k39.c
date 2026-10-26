/* k39.c - one-vertex extension and vertex-rewire tools for (3,10,n)-graphs.
 *
 * Facts used (G triangle-free, alpha(G) <= 9, n <= 63):
 *  - G + w with N(w) = S is a (3,10)-graph  iff  S is independent in G and
 *    S meets every independent 9-set of G.
 *  - Rewire vertex v (replace N(v) by S, v not in S) keeps a (3,10)-graph iff
 *    S is independent and S meets every independent 9-set of G that avoids v.
 *    (G - v has the same independent sets as G, minus those containing v.)
 *
 * Modes:
 *  k39 stats  IN OUT            per graph: n e mindeg maxdeg |Aut| n9 ext nearmiss
 *  k39 bfs    SEEDS DIR [maxg]  closure of SEEDS under vertex rewires, checking
 *                               every graph for a one-vertex extension. Restartable.
 *
 * Build: see known39/src/Makefile (nauty compiled in, with USE_TLS).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <omp.h>
#include <math.h>
#include "nauty.h"

typedef unsigned long long u64;
#define BIT(i) (1ULL << (i))
#define POP(x) __builtin_popcountll(x)
#define CTZ(x) __builtin_ctzll(x)
static int K = 9;                /* forbidden independent set size is K+1; env K39_K */
#define MAXV 63

typedef struct { int n; u64 a[MAXV]; } graph_t;

/* ---------- graph6 ---------- */
static int parse_g6(const char *s, graph_t *g) {
    while (*s == '\n' || *s == '\r') s++;
    if (s[0] < 63 || s[0] > 125) return -1;
    int n = s[0] - 63; s++;
    if (n > MAXV) return -1;
    g->n = n; memset(g->a, 0, sizeof g->a);
    int k = 0, x = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            if (k == 0) { if (*s < 63 || *s > 126) return -1; x = *s++ - 63; k = 6; }
            k--;
            if ((x >> k) & 1) { g->a[i] |= BIT(j); g->a[j] |= BIT(i); }
        }
    return 0;
}
static void to_g6(const graph_t *g, char *out) {
    int n = g->n, k = 6, x = 0; char *p = out;
    *p++ = (char)(n + 63);
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            x = (x << 1) | ((g->a[i] >> j) & 1);
            if (--k == 0) { *p++ = (char)(x + 63); k = 6; x = 0; }
        }
    if (k != 6) { x <<= k; *p++ = (char)(x + 63); }
    *p = 0;
}

/* ---------- independent K-sets ---------- */
typedef struct { u64 *s; size_t n, cap; } setlist_t;
static void sl_push(setlist_t *L, u64 x) {
    if (L->n == L->cap) { L->cap = L->cap ? 2 * L->cap : 1024; L->s = realloc(L->s, L->cap * sizeof(u64)); }
    L->s[L->n++] = x;
}
static void enum_indep(const graph_t *g, u64 chosen, u64 cand, int need, setlist_t *L) {
    if (need == 0) { sl_push(L, chosen); return; }
    while (cand) {
        if (POP(cand) < need) return;
        int v = CTZ(cand); cand &= cand - 1;
        enum_indep(g, chosen | BIT(v), cand & ~g->a[v], need - 1, L);
    }
}
static int has_indep(const graph_t *g, u64 cand, int need) {
    if (need == 0) return 1;
    while (cand) {
        if (POP(cand) < need) return 0;
        int v = CTZ(cand); cand &= cand - 1;
        if (has_indep(g, cand & ~g->a[v], need - 1)) return 1;
    }
    return 0;
}
static int triangle_free(const graph_t *g) {
    for (int i = 0; i < g->n; i++) {
        u64 b = g->a[i] & ~(BIT(i + 1) - 1);
        while (b) { int j = CTZ(b); b &= b - 1; if (g->a[i] & g->a[j]) return 0; }
    }
    return 1;
}
static u64 allmask(int n) { return n == 64 ? ~0ULL : BIT(n) - 1; }

/* ---------- hitting-set search ----------
 * Find independent S, S within 'allowed', meeting every set in T[0..nt).
 * Branch on the uncovered set with fewest free vertices. Each solution is
 * produced exactly once: at a node with chosen set T, branch i puts u_i in S and
 * excludes u_1..u_{i-1}. At a leaf (all met) every S u X, X an independent
 * subset of the free vertices, is a solution.
 */
typedef struct {
    const graph_t *g;
    u64 **buf;          /* per depth uncovered-set buffers */
    size_t cap;
    int mode;           /* 0: existence; 1: enumerate all */
    void (*cb)(u64 S, void *ctx);
    void *ctx;
    long long nodes;
    long long nsol;
} hs_t;

static void hs_init(hs_t *h, const graph_t *g, size_t nt) {
    memset(h, 0, sizeof *h);
    h->g = g; h->cap = nt ? nt : 1;
    h->buf = malloc((K + 3) * sizeof(u64 *));
    for (int d = 0; d < K + 3; d++) h->buf[d] = malloc(h->cap * sizeof(u64));
}
static void hs_free(hs_t *h) { for (int d = 0; d < K + 3; d++) free(h->buf[d]); free(h->buf); }

static void leaf_enum(hs_t *h, u64 S, u64 freev) {
    h->nsol++;
    h->cb(S, h->ctx);
    while (freev) {
        int v = CTZ(freev); freev &= freev - 1;
        leaf_enum(h, S | BIT(v), freev & ~h->g->a[v]);
    }
}

/* returns 1 if (mode 0) a solution was found */
static int hs_rec(hs_t *h, u64 S, u64 freev, const u64 *T, size_t nt, int depth) {
    h->nodes++;
    if (nt == 0) {
        if (h->mode == 0) { h->nsol++; if (h->cb) h->cb(S, h->ctx); return 1; }
        leaf_enum(h, S, freev);
        return 0;
    }
    /* pick uncovered set with fewest free vertices */
    size_t best = 0; int bc = 99;
    for (size_t i = 0; i < nt; i++) {
        int c = POP(T[i] & freev);
        if (c < bc) { bc = c; best = i; if (c == 0) return 0; }
    }
    u64 br = T[best] & freev;
    u64 *nb = h->buf[depth];
    while (br) {
        int u = CTZ(br); br &= br - 1;
        u64 m = BIT(u);
        size_t k = 0;
        for (size_t i = 0; i < nt; i++) if (!(T[i] & m)) nb[k++] = T[i];
        if (hs_rec(h, S | m, freev & ~m & ~h->g->a[u], nb, k, depth + 1)) return 1;
        freev &= ~m;   /* exclude u in later branches */
    }
    return 0;
}

/* ---------- near miss: independent S with fewest unmet sets (heuristic) ---------- */
static unsigned rng_next(unsigned long long *st) {
    *st ^= *st << 13; *st ^= *st >> 7; *st ^= *st << 17; return (unsigned)(*st >> 11);
}
static int count_unmet(const u64 *T, size_t nt, u64 S) {
    int c = 0; for (size_t i = 0; i < nt; i++) c += !(T[i] & S); return c;
}
/* greedy randomized + 1-swap local search; returns best unmet count, S in *bestS */
static int near_miss(const graph_t *g, const u64 *T, size_t nt, int tries, u64 *bestS, unsigned long long seed) {
    int n = g->n, best = (int)nt + 1; u64 all = allmask(n);
    unsigned long long st = seed | 1;
    int *gain = malloc(n * sizeof(int));
    for (int t = 0; t < tries; t++) {
        u64 S = 0, freev = all;
        for (;;) { /* greedy: add vertex meeting most unmet sets */
            memset(gain, 0, n * sizeof(int));
            for (size_t i = 0; i < nt; i++) if (!(T[i] & S)) {
                u64 b = T[i] & freev; while (b) { int v = CTZ(b); b &= b - 1; gain[v]++; } }
            int bv = -1, bg = 0, ties = 0;
            for (int v = 0; v < n; v++) if (freev & BIT(v)) {
                if (gain[v] > bg) { bg = gain[v]; bv = v; ties = 1; }
                else if (gain[v] == bg && bg > 0 && (rng_next(&st) % (++ties)) == 0) bv = v;
            }
            if (bv < 0) break;
            S |= BIT(bv); freev &= ~BIT(bv) & ~g->a[bv];
        }
        int cur = count_unmet(T, nt, S);
        /* local search: try remove x, add y (y independent of S-x) */
        int improved = 1;
        while (improved && cur > 0) {
            improved = 0;
            u64 sb = S;
            while (sb && !improved) {
                int x = CTZ(sb); sb &= sb - 1;
                u64 S0 = S & ~BIT(x);
                u64 cand = all & ~S0;
                u64 t0 = S0; while (t0) { int z = CTZ(t0); t0 &= t0 - 1; cand &= ~g->a[z]; }
                cand &= ~BIT(x);
                while (cand) {
                    int y = CTZ(cand); cand &= cand - 1;
                    u64 S1 = S0 | BIT(y);
                    /* also try adding a second free vertex greedily */
                    int c1 = count_unmet(T, nt, S1);
                    if (c1 < cur) { S = S1; cur = c1; improved = 1; break; }
                }
            }
        }
        if (cur < best) { best = cur; *bestS = S; }
        if (best == 0) break;
    }
    free(gain);
    return best;
}

/* ---------- nauty canonical form ---------- */
static void canon(const graph_t *g, graph_t *cg, double *grpsize, int *orbits_out) {
    int n = g->n;
    graph gg[MAXV], cgg[MAXV];
    int lab[MAXV], ptn[MAXV], orbits[MAXV];
    DEFAULTOPTIONS_GRAPH(options);
    statsblk stats;
    options.getcanon = TRUE;
    for (int i = 0; i < n; i++) {
        setword w = 0; u64 b = g->a[i];
        while (b) { int j = CTZ(b); b &= b - 1; w |= bit[j]; }
        gg[i] = w;
    }
    densenauty(gg, lab, ptn, orbits, &options, &stats, 1, n, cgg);
    cg->n = n;
    for (int i = 0; i < n; i++) {
        u64 b = 0; setword w = cgg[i];
        for (int j = 0; j < n; j++) if (ISELEMENT(&w, j)) b |= BIT(j);
        cg->a[i] = b;
    }
    if (grpsize) *grpsize = stats.grpsize1 * pow(10.0, stats.grpsize2);
    if (orbits_out) memcpy(orbits_out, orbits, n * sizeof(int));
}

/* ---------- 128-bit hash set ---------- */
typedef struct { u64 h1, h2; } hkey_t;
typedef struct { hkey_t *t; size_t cap, n; } hset_t;
static hkey_t hash_graph(const graph_t *g) {
    u64 h1 = 0x9E3779B97F4A7C15ULL ^ (u64)g->n, h2 = 0xC2B2AE3D27D4EB4FULL;
    for (int i = 0; i < g->n; i++) {
        u64 x = g->a[i] + 0x165667B19E3779F9ULL * (u64)(i + 1);
        h1 ^= x; h1 *= 0xFF51AFD7ED558CCDULL; h1 ^= h1 >> 33;
        h2 += x * 0xC4CEB9FE1A85EC53ULL; h2 = (h2 << 29) | (h2 >> 35); h2 *= 0x9E3779B97F4A7C15ULL;
    }
    if (h1 == 0 && h2 == 0) h1 = 1;
    hkey_t k = {h1, h2}; return k;
}
static int hset_insert(hset_t *H, hkey_t k);
static void hset_grow(hset_t *H) {
    hset_t N = { calloc(H->cap * 2, sizeof(hkey_t)), H->cap * 2, 0 };
    for (size_t i = 0; i < H->cap; i++) if (H->t[i].h1 | H->t[i].h2) hset_insert(&N, H->t[i]);
    free(H->t); *H = N;
}
/* returns 1 if new */
static int hset_insert(hset_t *H, hkey_t k) {
    if (2 * (H->n + 1) > H->cap) hset_grow(H);
    size_t i = k.h1 & (H->cap - 1);
    for (;;) {
        hkey_t *e = &H->t[i];
        if (!(e->h1 | e->h2)) { *e = k; H->n++; return 1; }
        if (e->h1 == k.h1 && e->h2 == k.h2) return 0;
        i = (i + 1) & (H->cap - 1);
    }
}

/* ---------- per-graph analysis ---------- */
typedef struct {
    int n, e, mindeg, maxdeg;
    double aut;
    size_t n9;
    int ext;          /* 1: one-vertex extension exists */
    u64 extS;
    int nearmiss;     /* fewest unmet 9-sets (heuristic upper bound) */
    u64 nmS;
    long long nodes;
} info_t;

static void degstats(const graph_t *g, info_t *I) {
    I->n = g->n; I->e = 0; I->mindeg = 99; I->maxdeg = 0;
    for (int i = 0; i < g->n; i++) {
        int d = POP(g->a[i]); I->e += d;
        if (d < I->mindeg) I->mindeg = d; if (d > I->maxdeg) I->maxdeg = d;
    }
    I->e /= 2;
}
static void save_ext(u64 S, void *ctx) { *(u64 *)ctx = S; }

static int check_ext(const graph_t *g, const setlist_t *L, info_t *I) {
    hs_t h; hs_init(&h, g, L->n);
    h.mode = 0; h.cb = save_ext; h.ctx = &I->extS;
    I->ext = hs_rec(&h, 0, allmask(g->n), L->s, L->n, 0);
    I->nodes = h.nodes;
    hs_free(&h);
    return I->ext;
}

/* build G+w and verify with brute force (independent of hitting-set logic) */
static int verify_plus(const graph_t *g, u64 S, graph_t *out) {
    *out = *g; int w = g->n; out->n = w + 1; out->a[w] = S;
    u64 b = S; while (b) { int v = CTZ(b); b &= b - 1; out->a[v] |= BIT(w); }
    return triangle_free(out) && !has_indep(out, allmask(out->n), K + 1);
}

static void analyse(const graph_t *g, info_t *I, int nm_tries, unsigned long long seed, setlist_t *L) {
    degstats(g, I);
    L->n = 0;
    enum_indep(g, 0, allmask(g->n), K, L);
    I->n9 = L->n;
    check_ext(g, L, I);
    I->nearmiss = I->ext ? 0 : near_miss(g, L->s, L->n, nm_tries, &I->nmS, seed);
}

/* ---------- mode stats ---------- */
static int mode_stats(const char *in, const char *outp, int tries) {
    FILE *f = fopen(in, "r"), *o = strcmp(outp, "-") ? fopen(outp, "w") : stdout;
    if (!f || !o) { perror("open"); return 2; }
    char line[4096]; long idx = 0; int bad = 0;
    fprintf(o, "# idx n e mindeg maxdeg aut n9 ext nearmiss nodes S_ext_or_nm g6\n");
    setlist_t L = {0};
    while (fgets(line, sizeof line, f)) {
        graph_t g; if (line[0] == '>' || line[0] == '#' || parse_g6(line, &g)) continue;
        line[strcspn(line, "\r\n")] = 0;
        if (!triangle_free(&g) || has_indep(&g, allmask(g.n), K + 1)) {
            fprintf(o, "%ld NOT_A_3_10_GRAPH %s\n", idx++, line); bad++; continue; }
        info_t I; double aut;
        analyse(&g, &I, tries, 12345 + idx, &L);
        graph_t cg; canon(&g, &cg, &aut, NULL); I.aut = aut;
        u64 S = I.ext ? I.extS : I.nmS;
        if (I.ext) {
            graph_t h; int ok = verify_plus(&g, S, &h); char buf[512]; to_g6(&h, buf);
            fprintf(stderr, "EXTENSION FOUND idx %ld verified=%d %s\n", idx, ok, buf);
            fprintf(o, "# EXTENSION %s\n", buf);
        }
        fprintf(o, "%ld %d %d %d %d %.0f %zu %d %d %lld %llx %s\n", idx, I.n, I.e, I.mindeg, I.maxdeg,
                I.aut, I.n9, I.ext, I.nearmiss, I.nodes, S, line);
        fflush(o); idx++;
    }
    free(L.s);
    if (o != stdout) fclose(o);
    fclose(f);
    return bad ? 1 : 0;
}

/* ---------- mode bfs ---------- */
/* queue of graphs, packed upper triangle (n <= 40): 13 words per graph */
#define PW 13
typedef struct { u64 *v; unsigned char *nv; size_t n, cap; } glist_t;
static void gl_push(glist_t *G, const graph_t *g) {
    if (G->n == G->cap) { G->cap = G->cap ? 2 * G->cap : 1024;
        G->v = realloc(G->v, G->cap * PW * sizeof(u64)); G->nv = realloc(G->nv, G->cap);
        if (!G->v || !G->nv) { fprintf(stderr, "out of memory\n"); exit(3); } }
    u64 *w = G->v + G->n * PW; memset(w, 0, PW * sizeof(u64));
    int k = 0;
    for (int j = 1; j < g->n; j++) for (int i = 0; i < j; i++, k++)
        if ((g->a[i] >> j) & 1) w[k >> 6] |= BIT(k & 63);
    G->nv[G->n++] = (unsigned char)g->n;
}
static void gl_get(const glist_t *G, size_t idx, graph_t *g) {
    const u64 *w = G->v + idx * PW; int n = G->nv[idx], k = 0;
    g->n = n; memset(g->a, 0, sizeof g->a);
    for (int j = 1; j < n; j++) for (int i = 0; i < j; i++, k++)
        if ((w[k >> 6] >> (k & 63)) & 1) { g->a[i] |= BIT(j); g->a[j] |= BIT(i); }
}

typedef struct {
    const graph_t *g; int v;
    graph_t *out; size_t nout, cap;   /* canonical forms of rewired graphs */
} rw_ctx;
static void rw_cb(u64 S, void *vctx) {
    rw_ctx *c = vctx;
    graph_t h = *c->g;
    int v = c->v;
    u64 old = h.a[v];
    while (old) { int u = CTZ(old); old &= old - 1; h.a[u] &= ~BIT(v); }
    h.a[v] = S;
    u64 b = S; while (b) { int u = CTZ(b); b &= b - 1; h.a[u] |= BIT(v); }
    graph_t cg; canon(&h, &cg, NULL, NULL);
    if (c->nout == c->cap) { c->cap = c->cap ? 2 * c->cap : 64; c->out = realloc(c->out, c->cap * sizeof(graph_t)); }
    c->out[c->nout++] = cg;
}

static int mode_bfs(const char *seeds, const char *dir, size_t maxg, int tries) {
    char p_all[1024], p_res[1024], p_prog[1024], p_found[1024];
    snprintf(p_all, sizeof p_all, "%s/all.g6", dir);
    snprintf(p_res, sizeof p_res, "%s/results.txt", dir);
    snprintf(p_prog, sizeof p_prog, "%s/progress.txt", dir);
    snprintf(p_found, sizeof p_found, "%s/FOUND40.g6", dir);
    hset_t H = { calloc(1 << 20, sizeof(hkey_t)), 1 << 20, 0 };
    glist_t Q = {0};
    char line[4096];
    size_t done = 0, nres = 0;
    FILE *f = fopen(p_all, "r");
    if (f) {   /* restart */
        while (fgets(line, sizeof line, f)) { graph_t g; if (parse_g6(line, &g)) continue;
            if (hset_insert(&H, hash_graph(&g))) gl_push(&Q, &g); }
        fclose(f);
        FILE *pf = fopen(p_prog, "r"); if (pf) { if (fscanf(pf, "%zu", &done) != 1) done = 0; fclose(pf); }
        FILE *rf = fopen(p_res, "r");
        if (rf) { while (fgets(line, sizeof line, rf)) if (line[0] != '#') nres++; fclose(rf); }
        fprintf(stderr, "restart: %zu graphs known, %zu expanded, %zu analysed\n", Q.n, done, nres);
    }
    FILE *fall = fopen(p_all, "a"), *fres = fopen(p_res, "a");
    if (!fall || !fres) { perror("open out"); return 2; }
    if (Q.n == 0) {
        FILE *s = fopen(seeds, "r"); if (!s) { perror(seeds); return 2; }
        while (fgets(line, sizeof line, s)) { graph_t g, cg; if (parse_g6(line, &g)) continue;
            if (!triangle_free(&g) || has_indep(&g, allmask(g.n), K + 1)) { fprintf(stderr, "bad seed\n"); continue; }
            canon(&g, &cg, NULL, NULL);
            if (hset_insert(&H, hash_graph(&cg))) { gl_push(&Q, &cg); char b[512]; to_g6(&cg, b); fprintf(fall, "%s\n", b); } }
        fclose(s); fflush(fall);
        fprintf(fres, "# idx n e mindeg maxdeg aut n9 ext nearmiss nodes nmS\n");
    }
    time_t t0 = time(NULL);
    const size_t CH = 64;
    while (done < Q.n) {
        size_t lo = done, hi = Q.n < done + CH ? Q.n : done + CH;
        size_t m = hi - lo;
        rw_ctx *ctxs = calloc(m * 64, sizeof(rw_ctx));
        info_t *infos = calloc(m, sizeof(info_t));
        /* analyse (ext check + near miss) graphs lo..hi that are not yet analysed */
        #pragma omp parallel for schedule(dynamic, 1)
        for (size_t qi = lo; qi < hi; qi++) {
            graph_t gq; gl_get(&Q, qi, &gq); const graph_t *g = &gq;
            setlist_t L = {0};
            info_t *I = &infos[qi - lo];
            analyse(g, I, tries, 777 + qi, &L);
            double aut; int orb[MAXV]; graph_t cg; canon(g, &cg, &aut, orb); I->aut = aut;
            if (Q.n < maxg) {
                for (int v = 0; v < g->n; v++) {
                    if (orb[v] != v) continue;   /* one vertex per orbit */
                    setlist_t Lv = {0};
                    for (size_t i = 0; i < L.n; i++) if (!(L.s[i] & BIT(v))) sl_push(&Lv, L.s[i]);
                    rw_ctx *c = &ctxs[(qi - lo) * 64 + v];
                    c->g = g; c->v = v;
                    hs_t h; hs_init(&h, g, Lv.n); h.mode = 1; h.cb = rw_cb; h.ctx = c;
                    hs_rec(&h, 0, allmask(g->n) & ~BIT(v), Lv.s, Lv.n, 0);
                    hs_free(&h); free(Lv.s);
                }
            }
            free(L.s);
        }
        /* serial: write results, insert new graphs */
        for (size_t qi = lo; qi < hi; qi++) {
            info_t *I = &infos[qi - lo];
            if (qi >= nres) {
                fprintf(fres, "%zu %d %d %d %d %.0f %zu %d %d %lld %llx\n", qi, I->n, I->e, I->mindeg, I->maxdeg,
                        I->aut, I->n9, I->ext, I->nearmiss, I->nodes, I->ext ? I->extS : I->nmS);
                nres++;
            }
            if (I->ext) {
                graph_t h, gq; gl_get(&Q, qi, &gq); int ok = verify_plus(&gq, I->extS, &h); char b[512]; to_g6(&h, b);
                FILE *ff = fopen(p_found, "a"); fprintf(ff, "%s\n", b); fclose(ff);
                fprintf(stderr, "!!! EXTENSION FOUND from idx %zu verified=%d %s\n", qi, ok, b);
            }
            for (int v = 0; v < 64; v++) {
                rw_ctx *c = &ctxs[(qi - lo) * 64 + v];
                for (size_t j = 0; j < c->nout; j++)
                    if (hset_insert(&H, hash_graph(&c->out[j]))) {
                        gl_push(&Q, &c->out[j]);
                        char b[512]; to_g6(&c->out[j], b); fprintf(fall, "%s\n", b);
                    }
                free(c->out);
            }
        }
        free(ctxs); free(infos);
        fflush(fall); fflush(fres);
        done = hi;
        FILE *pf = fopen(p_prog, "w"); fprintf(pf, "%zu\n", done); fclose(pf);
        if ((done / CH) % 200 == 0 || done == Q.n)
            fprintf(stderr, "[%lds] expanded %zu / known %zu\n", (long)(time(NULL) - t0), done, Q.n);
    }
    fclose(fall); fclose(fres);
    fprintf(stderr, "closure complete: %zu graphs\n", Q.n);
    return 0;
}


/* ---------- mode r2: rewire two vertices a,b at once ----------
 * G' = G - a - b + w1 + w2 (w1, w2 take the labels a, b). With H = G - a - b,
 * G' is a (3,10)-graph iff S1, S2 independent in H, each meets every independent
 * 9-set of H, and: if w1 ~ w2 then S1, S2 disjoint; else S1 u S2 meets every
 * independent 8-set of H.
 */
typedef struct { u64 *S; size_t n, cap; } slist_t;
static void collect_cb(u64 S, void *ctx) {
    slist_t *L = ctx;
    if (L->n == L->cap) { L->cap = L->cap ? 2 * L->cap : 256; L->S = realloc(L->S, L->cap * sizeof(u64)); }
    L->S[L->n++] = S;
}
static void build_r2(const graph_t *g, int a, int b, u64 S1, u64 S2, int edge, graph_t *h) {
    *h = *g;
    for (int i = 0; i < g->n; i++) h->a[i] &= ~(BIT(a) | BIT(b));
    h->a[a] = S1 | (edge ? BIT(b) : 0);
    h->a[b] = S2 | (edge ? BIT(a) : 0);
    u64 x = S1; while (x) { int u = CTZ(x); x &= x - 1; h->a[u] |= BIT(a); }
    x = S2; while (x) { int u = CTZ(x); x &= x - 1; h->a[u] |= BIT(b); }
}
static int mode_r2(const char *in, const char *known, const char *outp, long maxsol) {
    hset_t H = { calloc(1 << 20, sizeof(hkey_t)), 1 << 20, 0 };
    char line[4096]; size_t nk = 0;
    FILE *f = fopen(known, "r"); if (!f) { perror(known); return 2; }
    while (fgets(line, sizeof line, f)) { graph_t g; if (parse_g6(line, &g)) continue; hset_insert(&H, hash_graph(&g)); nk++; }
    fclose(f);
    fprintf(stderr, "known: %zu\n", nk);
    hset_t Hnew = { calloc(1 << 16, sizeof(hkey_t)), 1 << 16, 0 };
    FILE *fi = fopen(in, "r"), *fo = fopen(outp, "a");
    if (!fi || !fo) { perror("open"); return 2; }
    long gi = 0;
    while (fgets(line, sizeof line, fi)) {
        graph_t g; if (parse_g6(line, &g)) continue;
        int n = g.n;
        setlist_t L9 = {0}, L8 = {0};
        enum_indep(&g, 0, allmask(n), K, &L9);
        enum_indep(&g, 0, allmask(n), K - 1, &L8);
        long long tot_pairs = 0, tot_valid = 0, tot_new = 0, tot_A = 0;
        int npair = n * (n - 1) / 2;
        typedef struct { long long A, valid; slist_t newg; } pr_t;
        pr_t *PR = calloc(npair, sizeof(pr_t));
        #pragma omp parallel for schedule(dynamic, 1)
        for (int pi = 0; pi < npair; pi++) {
            int a = 0, r = pi; while (r >= n - 1 - a) { r -= n - 1 - a; a++; } int b = a + 1 + r;
            u64 ab = BIT(a) | BIT(b);
            setlist_t T9 = {0}, T8 = {0};
            for (size_t i = 0; i < L9.n; i++) if (!(L9.s[i] & ab)) sl_push(&T9, L9.s[i]);
            for (size_t i = 0; i < L8.n; i++) if (!(L8.s[i] & ab)) sl_push(&T8, L8.s[i]);
            slist_t A = {0};
            hs_t h; hs_init(&h, &g, T9.n); h.mode = 1; h.cb = collect_cb; h.ctx = &A;
            hs_rec(&h, 0, allmask(n) & ~ab, T9.s, T9.n, 0);
            hs_free(&h);
            PR[pi].A = A.n;
            /* missed 8-sets per S */
            setlist_t *M = calloc(A.n, sizeof(setlist_t));
            for (size_t i = 0; i < A.n; i++)
                for (size_t t = 0; t < T8.n; t++) if (!(T8.s[t] & A.S[i])) sl_push(&M[i], T8.s[t]);
            long cnt = 0;
            for (size_t i = 0; i < A.n && cnt < maxsol; i++)
                for (size_t j = 0; j < A.n && cnt < maxsol; j++) {
                    for (int edge = 0; edge < 2; edge++) {
                        if (edge) { if (A.S[i] & A.S[j]) continue; if (j < i) continue; }
                        else {
                            size_t t = 0; for (; t < M[i].n; t++) if (!(M[i].s[t] & A.S[j])) break;
                            if (t < M[i].n) continue;
                            if (j < i) continue;
                        }
                        PR[pi].valid++; cnt++;
                        graph_t hg, cg; build_r2(&g, a, b, A.S[i], A.S[j], edge, &hg);
                        canon(&hg, &cg, NULL, NULL);
                        hkey_t k = hash_graph(&cg);
                        /* lookup only (H is read-only here) */
                        size_t q = k.h1 & (H.cap - 1); int found = 0;
                        for (;;) { hkey_t *e = &H.t[q]; if (!(e->h1 | e->h2)) break;
                            if (e->h1 == k.h1 && e->h2 == k.h2) { found = 1; break; } q = (q + 1) & (H.cap - 1); }
                        if (!found) {
                            slist_t *ng = &PR[pi].newg;
                            /* store canonical graph as packed rows: n words */
                            for (int v = 0; v < n; v++) collect_cb(cg.a[v], ng);
                        }
                    }
                }
            for (size_t i = 0; i < A.n; i++) free(M[i].s);
            free(M); free(A.S); free(T9.s); free(T8.s);
        }
        for (int pi = 0; pi < npair; pi++) {
            tot_pairs++; tot_A += PR[pi].A; tot_valid += PR[pi].valid;
            slist_t *ng = &PR[pi].newg;
            for (size_t x = 0; x + n <= ng->n; x += n) {
                graph_t cg; cg.n = n; memset(cg.a, 0, sizeof cg.a); memcpy(cg.a, ng->S + x, n * sizeof(u64));
                if (hset_insert(&Hnew, hash_graph(&cg))) {
                    tot_new++;
                    setlist_t L = {0}; info_t I; analyse(&cg, &I, 20, 99 + tot_new, &L); free(L.s);
                    char buf[512]; to_g6(&cg, buf);
                    fprintf(fo, "%ld %d %d %zu %d %d %s\n", gi, I.e, I.maxdeg, I.n9, I.ext, I.nearmiss, buf);
                    if (I.ext) { graph_t h2; int ok = verify_plus(&cg, I.extS, &h2); char b2[512]; to_g6(&h2, b2);
                        fprintf(stderr, "!!! EXTENSION FOUND verified=%d %s\n", ok, b2); fprintf(fo, "# FOUND40 %s\n", b2); }
                }
            }
            free(ng->S);
        }
        free(PR);
        fflush(fo);
        fprintf(stderr, "graph %ld: n9=%zu n8=%zu pairs=%lld avg|A|=%.1f valid=%lld new(not in known, distinct)=%lld\n",
                gi, L9.n, L8.n, tot_pairs, (double)tot_A / tot_pairs, tot_valid, tot_new);
        free(L9.s); free(L8.s); gi++;
    }
    fclose(fi); fclose(fo);
    return 0;
}

/* ---------- mode extall: all one-vertex extensions G + w, up to isomorphism ---------- */
static int mode_extall(const char *in, const char *outp) {
    FILE *fi = fopen(in, "r"), *fo = fopen(outp, "w");
    if (!fi || !fo) { perror("open"); return 2; }
    hset_t H = { calloc(1 << 16, sizeof(hkey_t)), 1 << 16, 0 };
    char line[4096]; long tot = 0;
    while (fgets(line, sizeof line, fi)) {
        graph_t g; if (parse_g6(line, &g)) continue;
        setlist_t L = {0}; enum_indep(&g, 0, allmask(g.n), K, &L);
        slist_t A = {0};
        hs_t h; hs_init(&h, &g, L.n); h.mode = 1; h.cb = collect_cb; h.ctx = &A;
        hs_rec(&h, 0, allmask(g.n), L.s, L.n, 0); hs_free(&h);
        for (size_t i = 0; i < A.n; i++) {
            graph_t g2, cg; if (!verify_plus(&g, A.S[i], &g2)) { fprintf(stderr, "BUG: invalid extension\n"); return 3; }
            canon(&g2, &cg, NULL, NULL);
            if (hset_insert(&H, hash_graph(&cg))) { char b[512]; to_g6(&cg, b); fprintf(fo, "%s\n", b); tot++; }
        }
        free(A.S); free(L.s);
    }
    fclose(fi); fclose(fo);
    fprintf(stderr, "extall: %ld distinct extensions\n", tot);
    return 0;
}

/* ---------- mode canon: canonical graph6 (same labelling as bfs all.g6) ---------- */
static int mode_canon(const char *in) {
    FILE *fi = fopen(in, "r"); if (!fi) { perror(in); return 2; }
    char line[4096];
    while (fgets(line, sizeof line, fi)) {
        graph_t g, cg; if (parse_g6(line, &g)) continue;
        canon(&g, &cg, NULL, NULL); char b[512]; to_g6(&cg, b); printf("%s\n", b);
    }
    fclose(fi); return 0;
}

/* ---------- mode tri1: 40-vertex graphs with alpha <= 9 and exactly one triangle ----------
 * G + w with N(w) = S has alpha <= 9 iff S meets every independent 9-set of G.
 * It has exactly one triangle iff S spans exactly one edge xy (G is triangle-free).
 * For each edge xy: S = {x,y} u X, X independent, X avoids N(x) u N(y).
 * Output: distinct canonical (n+1)-vertex graphs, one line "idx g6".
 */
static int mode_tri1(const char *in, const char *outp, long maxper) {
    FILE *fi = fopen(in, "r"), *fo = fopen(outp, "w");
    if (!fi || !fo) { perror("open"); return 2; }
    hset_t H = { calloc(1 << 16, sizeof(hkey_t)), 1 << 16, 0 };
    char line[4096]; long idx = 0, tot = 0, gwith = 0;
    while (fgets(line, sizeof line, fi)) {
        graph_t g; if (parse_g6(line, &g)) continue;
        int n = g.n;
        setlist_t L = {0}; enum_indep(&g, 0, allmask(n), K, &L);
        u64 *T = malloc((L.n + 1) * sizeof(u64));
        int any = 0;
        for (int x = 0; x < n; x++) {
            u64 nb = g.a[x] & ~(BIT(x + 1) - 1);
            while (nb) {
                int y = CTZ(nb); nb &= nb - 1;
                u64 xy = BIT(x) | BIT(y);
                size_t k = 0;
                for (size_t i = 0; i < L.n; i++) if (!(L.s[i] & xy)) T[k++] = L.s[i];
                slist_t A = {0};
                hs_t h; hs_init(&h, &g, k); h.mode = 1; h.cb = collect_cb; h.ctx = &A;
                hs_rec(&h, xy, allmask(n) & ~xy & ~g.a[x] & ~g.a[y], T, k, 0);
                hs_free(&h);
                for (size_t i = 0; i < A.n && (long)i < maxper; i++) {
                    graph_t g2, cg; g2 = g; g2.n = n + 1; g2.a[n] = A.S[i];
                    u64 b = A.S[i]; while (b) { int v = CTZ(b); b &= b - 1; g2.a[v] |= BIT(n); }
                    if (has_indep(&g2, allmask(n + 1), K + 1)) { fprintf(stderr, "BUG tri1\n"); return 3; }
                    canon(&g2, &cg, NULL, NULL);
                    if (hset_insert(&H, hash_graph(&cg))) { char buf[512]; to_g6(&cg, buf); fprintf(fo, "%ld %s\n", idx, buf); tot++; }
                    any = 1;
                }
                free(A.S);
            }
        }
        gwith += any;
        free(T); free(L.s); idx++;
    }
    fclose(fi); fclose(fo);
    fprintf(stderr, "tri1: %ld graphs read, %ld have a one-triangle extension, %ld distinct 40-vertex graphs\n", idx, gwith, tot);
    return 0;
}

int main(int argc, char **argv) {
    if (getenv("K39_K")) K = atoi(getenv("K39_K"));
    if (argc >= 3 && !strcmp(argv[1], "stats"))
        return mode_stats(argv[2], argc > 3 ? argv[3] : "-", argc > 4 ? atoi(argv[4]) : 20);
    if (argc >= 4 && !strcmp(argv[1], "bfs"))
        return mode_bfs(argv[2], argv[3], argc > 4 ? strtoull(argv[4], 0, 10) : (size_t)-1, argc > 5 ? atoi(argv[5]) : 20);
    if (argc >= 4 && !strcmp(argv[1], "tri1"))
        return mode_tri1(argv[2], argv[3], argc > 4 ? atol(argv[4]) : 1000000000L);
    if (argc >= 3 && !strcmp(argv[1], "canon"))
        return mode_canon(argv[2]);
    if (argc >= 4 && !strcmp(argv[1], "extall"))
        return mode_extall(argv[2], argv[3]);
    if (argc >= 5 && !strcmp(argv[1], "r2"))
        return mode_r2(argv[2], argv[3], argv[4], argc > 5 ? atol(argv[5]) : 1000000000L);
    fprintf(stderr, "usage: k39 stats IN [OUT] [nm_tries] | k39 bfs SEEDS DIR [maxgraphs] [nm_tries]\n");
    return 2;
}
