/* onepoint.c - one-point extensions: H (alpha <= K-1) -> H + x, N(x) = S independent,
 * alpha(H+x) <= K-1  <=>  alpha(H - S - x) <= K-2.
 * usage: onepoint -k K [-a] [-s MINSIZE] [-S MAXSIZE] [-1]
 *   -1 : output only the first extension per input (with largest |S| found first) */
#include "gutil.h"
#include <getopt.h>

static int K, smin = 0, smax = 63, first = 0, done;
static graph_t H;

static void rec(set_t cur, int sz, set_t allowed)
{
    if (done) return;
    if (sz >= smin) {
        set_t rest = (BIT(H.n) - 1) & ~cur;
        if (!has_indep(H.adj, rest, K - 1)) {
            graph_t G = H; int x = H.n; G.n = H.n + 1; G.adj[x] = cur;
            set_t t = cur; while (t) { int y = CTZ(t); t &= t - 1; G.adj[y] |= BIT(x); }
            g6_write(stdout, &G);
            if (first) { done = 1; return; }
        }
    }
    if (sz == smax) return;
    while (allowed) {
        int y = CTZ(allowed); allowed &= allowed - 1;
        rec(cur | BIT(y), sz + 1, allowed & ~H.adj[y]);
    }
}

int main(int argc, char **argv)
{
    int c;
    while ((c = getopt(argc, argv, "k:s:S:1")) != -1) {
        if (c == 'k') K = atoi(optarg);
        else if (c == 's') smin = atoi(optarg);
        else if (c == 'S') smax = atoi(optarg);
        else if (c == '1') first = 1;
    }
    char line[4096];
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\r\n")] = 0;
        if (!line[0] || g6_read(line, &H)) continue;
        done = 0;
        rec(0, 0, BIT(H.n) - 1);
    }
    return 0;
}
