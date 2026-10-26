/* Independent-set helpers for CEGAR (loaded via ctypes). Graphs on n <= 64 vertices
 * as adjacency bitmasks. */
#include <stdint.h>
typedef uint64_t u64;

static const u64 *A;
static int K, found;
static u64 best;
static unsigned rng;

static int popc(u64 x) { return __builtin_popcountll(x); }

static void rec(u64 P, u64 cur, int c) {
    if (found) return;
    if (c >= K) { found = 1; best = cur; return; }
    if (c + popc(P) < K) return;
    /* take all vertices isolated in P (never hurts), then branch on a min-degree vertex */
    u64 iso = 0, Q = P;
    int bv = -1, bd = 1 << 30;
    while (Q) {
        int v = __builtin_ctzll(Q); Q &= Q - 1;
        int d = popc(A[v] & P);
        if (d == 0) { iso |= 1ULL << v; continue; }
        if (d < bd || (d == bd && ((rng = rng * 1103515245u + 12345u) >> 16) & 1)) { bd = d; bv = v; }
    }
    if (iso) {
        while (c < K && iso) { int v = __builtin_ctzll(iso); iso &= iso - 1; cur |= 1ULL << v; c++; P &= ~(1ULL << v); }
        if (c >= K) { found = 1; best = cur; return; }
        P &= ~iso;  /* (iso is empty here) */
        if (!P) return;
    }
    u64 b = 1ULL << bv;
    rec(P & ~A[bv] & ~b, cur | b, c + 1);
    /* exclude bv: then some neighbour of bv in P must be chosen, else bv could be added
       (only for maximal sets; we just exclude) */
    rec(P & ~b, cur, c);
}

/* find an independent set of size k containing all vertices of `must` (assumed independent),
   inside `allowed`. Returns 1 and writes mask to *out. */
int indep_with(const u64 *adj, int n, int k, u64 must, u64 allowed, unsigned seed, u64 *out) {
    A = adj; K = k; found = 0; best = 0; rng = seed;
    u64 P = allowed & ~must;
    int c = 0;
    u64 m = must;
    while (m) { int v = __builtin_ctzll(m); m &= m - 1; P &= ~adj[v]; c++; }
    rec(P, must, c);
    if (found) *out = best;
    return found;
}

/* alpha(G) exactly (n <= 64) */
int alpha(const u64 *adj, int n) {
    u64 all = (n == 64) ? ~0ULL : ((1ULL << n) - 1);
    int a = 0;
    u64 dummy;
    while (indep_with(adj, n, a + 1, 0, all, 1, &dummy)) a++;
    return a;
}
