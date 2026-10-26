/* Exhaustive search for (3,10,40) Cayley graphs Cay(G,S) on one group G of order 40.
 *
 * Input: groups/G<i>.txt (n, then n rows of the multiplication table, identity 0).
 * Cay(G,S): g ~ h iff g^-1 h in S. S = S^-1, 0 not in S.
 * Triangle-free iff s1*s2 not in S for all s1,s2 in S ("product-free").
 * Every vertex has degree |S|; triangle-free with alpha <= 9 forces |S| <= 9
 * (the neighbourhood is independent).
 * alpha is monotone non-increasing in S, so it suffices to test the
 * product-free inverse-closed S with |S| <= 9 that are MAXIMAL (no further
 * inverse-pair / involution can be added keeping both properties).
 * Vertex-transitive: alpha(G) = 1 + alpha(G - N[e]).
 *
 * Output: number of maximal sets, histogram of alpha, minimum alpha and one S
 * achieving it, and every S with alpha <= 9 (a (3,10,40)-graph).
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define N 40
typedef uint64_t u64;

static int T[N][N], inv_[N];
static int unit_a[N], unit_b[N], nunits;   /* unit = {g, g^-1} */
static u64 adj[N];
static long long nmax = 0, nnodes = 0;
static long long hist[N + 1];
static int best_alpha = 99;
static u64 best_S = 0;
static int maxdeg = 9;

static int popc(u64 x) { return __builtin_popcountll(x); }

/* max independent set size within P, stop early once >= target */
static int target;
static int found;
static void mis_rec(u64 P, int cur) {
    if (found) return;
    if (cur >= target) { found = 1; return; }
    if (cur + popc(P) < target) return;
    if (!P) return;
    /* pick vertex of max degree in P; if all degree 0 then P independent */
    int bv = -1, bd = -1;
    u64 Q = P;
    while (Q) {
        int v = __builtin_ctzll(Q); Q &= Q - 1;
        int d = popc(adj[v] & P);
        if (d > bd) { bd = d; bv = v; }
    }
    if (bd == 0) { if (cur + popc(P) >= target) found = 1; return; }
    /* branch: include bv, or exclude bv */
    mis_rec(P & ~adj[bv] & ~(1ULL << bv), cur + 1);
    mis_rec(P & ~(1ULL << bv), cur);
}

static int has_indep(u64 P, int k) { target = k; found = 0; mis_rec(P, 0); return found; }

static int alpha_of(u64 S) {
    for (int g = 0; g < N; g++) {
        adj[g] = 0;
        for (int h = 0; h < N; h++) if ((S >> T[inv_[g]][h]) & 1) adj[g] |= 1ULL << h;
    }
    u64 P = ((N == 64) ? ~0ULL : ((1ULL << N) - 1)) & ~adj[0] & ~1ULL;
    int a = 0;
    while (has_indep(P, a + 1)) a++;
    return a + 1;
}

static int addable(u64 S, int u) {
    u64 S2 = S | (1ULL << unit_a[u]) | (1ULL << unit_b[u]);
    if (popc(S2) > maxdeg) return 0;
    int xs[2] = {unit_a[u], unit_b[u]};
    for (int i = 0; i < 2; i++) {
        int x = xs[i];
        u64 Q = S2;
        while (Q) {
            int y = __builtin_ctzll(Q); Q &= Q - 1;
            if ((S2 >> T[x][y]) & 1) return 0;
            if ((S2 >> T[y][x]) & 1) return 0;
        }
    }
    return 1;
}

static void print_S(FILE *f, u64 S) {
    fprintf(f, "{");
    int first = 1;
    for (int g = 0; g < N; g++) if ((S >> g) & 1) { fprintf(f, first ? "%d" : ",%d", g); first = 0; }
    fprintf(f, "}");
}

/* DFS over units in index order; "excluded" units must stay non-addable at the
 * leaf for maximality. */
static void dfs(int u, u64 S) {
    nnodes++;
    if (u == nunits) {
        for (int w = 0; w < nunits; w++)
            if (!((S >> unit_a[w]) & 1) && addable(S, w)) return; /* not maximal */
        nmax++;
        int a = alpha_of(S);
        hist[a]++;
        if (a < best_alpha) { best_alpha = a; best_S = S; }
        if (a <= 9) { printf("FOUND alpha=%d S=", a); print_S(stdout, S); printf("\n"); fflush(stdout); }
        return;
    }
    if (addable(S, u)) dfs(u + 1, S | (1ULL << unit_a[u]) | (1ULL << unit_b[u]));
    dfs(u + 1, S);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: cayley groupfile [maxdeg]\n"); return 1; }
    if (argc > 2) maxdeg = atoi(argv[2]);
    FILE *f = fopen(argv[1], "r");
    int n;
    if (fscanf(f, "%d", &n) != 1 || n != N) { fprintf(stderr, "bad n\n"); return 1; }
    for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) if (fscanf(f, "%d", &T[i][j]) != 1) return 1;
    fclose(f);
    for (int g = 0; g < N; g++) for (int h = 0; h < N; h++) if (T[g][h] == 0) inv_[g] = h;
    int seen[N] = {0};
    for (int g = 1; g < N; g++) if (!seen[g]) {
        seen[g] = seen[inv_[g]] = 1;
        unit_a[nunits] = g; unit_b[nunits] = inv_[g]; nunits++;
    }
    dfs(0, 0);
    printf("group=%s units=%d maxdeg=%d nodes=%lld maximal_sets=%lld min_alpha=%d best_S=",
           argv[1], nunits, maxdeg, nnodes, nmax, best_alpha);
    print_S(stdout, best_S);
    printf("\nalpha_hist:");
    for (int a = 0; a <= N; a++) if (hist[a]) printf(" %d:%lld", a, hist[a]);
    printf("\n");
    return 0;
}
