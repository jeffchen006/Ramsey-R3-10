/* gutil.h - small graph utilities for gluing code (graphs with n <= 64). */
#ifndef GUTIL_H
#define GUTIL_H
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef uint64_t set_t;
#define BIT(i) (((set_t)1) << (i))
#define POP(x) __builtin_popcountll(x)
#define CTZ(x) __builtin_ctzll(x)

typedef struct { int n; set_t adj[64]; } graph_t;

/* Parse one graph6 line (n <= 62). Return 0 on success. */
static int g6_read(const char *s, graph_t *g)
{
    while (*s == '>' ) { s = strchr(s, '<'); if (!s) return -1; s++; } /* header >>graph6<< */
    int n = s[0] - 63;
    if (n < 0 || n > 62) return -1;
    memset(g, 0, sizeof(*g));
    g->n = n;
    const unsigned char *p = (const unsigned char *)s + 1;
    int k = 0, bit = 6, x = 0;
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            if (bit == 6) { x = *p++ - 63; if (x < 0) return -1; bit = 0; }
            if (x & (32 >> bit)) { g->adj[i] |= BIT(j); g->adj[j] |= BIT(i); }
            bit++; k++;
        }
    return 0;
}

static void g6_write(FILE *f, const graph_t *g)
{
    char buf[1024];
    int n = g->n, pos = 0, bit = 0, x = 0;
    buf[pos++] = (char)(63 + n);
    for (int j = 1; j < n; j++)
        for (int i = 0; i < j; i++) {
            if (g->adj[i] & BIT(j)) x |= 32 >> bit;
            if (++bit == 6) { buf[pos++] = (char)(63 + x); bit = 0; x = 0; }
        }
    if (bit) buf[pos++] = (char)(63 + x);
    buf[pos++] = '\n'; buf[pos] = 0;
    fputs(buf, f);
}

static int g_edges(const graph_t *g)
{
    int e = 0;
    for (int i = 0; i < g->n; i++) e += POP(g->adj[i]);
    return e / 2;
}

static int g_trianglefree(const graph_t *g)
{
    for (int i = 0; i < g->n; i++) {
        set_t a = g->adj[i] & ~(BIT(i + 1) - 1) ;
        while (a) { int j = CTZ(a); a &= a - 1; if (g->adj[i] & g->adj[j]) return 0; }
    }
    return 1;
}

/* Does the subgraph induced by m contain an independent set of size k? */
static int has_indep(const set_t *adj, set_t m, int k)
{
    if (k <= 0) return 1;
    for (;;) {
        int c = POP(m);
        if (c < k) return 0;
        if (k == 1) return 1;
        /* take isolated-in-m vertices for free; find max degree vertex */
        int best = -1, bd = -1;
        set_t t = m;
        while (t) {
            int v = CTZ(t); t &= t - 1;
            int d = POP(adj[v] & m);
            if (d == 0) { m &= ~BIT(v); k--; if (k <= 0) return 1; continue; }
            if (d > bd) { bd = d; best = v; }
        }
        if (best < 0) return POP(m) >= k;
        if (POP(m) < k) return 0;
        if (bd == 1) {
            /* m is a matching: alpha = |m|/2 ... each edge gives one */
            return POP(m) / 2 >= k;
        }
        /* branch: include best */
        if (has_indep(adj, m & ~adj[best] & ~BIT(best), k - 1)) return 1;
        m &= ~BIT(best); /* exclude best */
    }
}

static int alpha_le(const graph_t *g, int k) /* alpha(g) <= k ? */
{
    set_t all = (g->n == 64) ? ~(set_t)0 : (BIT(g->n) - 1);
    return !has_indep(g->adj, all, k + 1);
}

#endif
