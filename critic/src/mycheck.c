/* critic: independent (3,k)-graph checker. Written from the graph6 spec
 * (nauty formats.txt), not from tools/check_graph.py.
 * Usage: mycheck K FILE   -> one line per graph: n e mindeg maxdeg tf alpha ok
 * Strict: rejects bad chars, wrong length, nonzero padding. Accepts the
 * ">>graph6<<" header prefix (no newline after it, as nauty writes it). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 300
static unsigned char A[MAXN][MAXN];
static int n, best;
static void die(const char *m, long ln) { fprintf(stderr, "line %ld: %s\n", ln, m); exit(2); }
static void rec(int *cand, int nc, int size) {
    if (size > best) best = size;
    for (int i = 0; i < nc; i++) {
        if (size + (nc - i) <= best) return;
        int v = cand[i], nxt[MAXN], m = 0;
        for (int j = i + 1; j < nc; j++) if (!A[v][cand[j]]) nxt[m++] = cand[j];
        rec(nxt, m, size + 1);
    }
}
int main(int argc, char **argv) {
    int K = atoi(argv[1]);
    FILE *f = fopen(argv[2], "r");
    if (!f) die("cannot open", 0);
    static char buf[1 << 20];
    long ln = 0; int ngr = 0, allok = 1;
    while (fgets(buf, sizeof buf, f)) {
        ln++;
        size_t L = strlen(buf);
        while (L && (buf[L-1] == '\n' || buf[L-1] == '\r')) buf[--L] = 0;
        char *s = buf;
        if (strncmp(s, ">>graph6<<", 10) == 0) s += 10;
        L = strlen(s);
        if (L == 0) continue;
        for (size_t i = 0; i < L; i++) if (s[i] < 63 || s[i] > 126) die("char out of graph6 range", ln);
        size_t p;
        if (s[0] != 126) { n = s[0] - 63; p = 1; }
        else {
            if (L < 4 || s[1] == 126) die("unsupported/short long form", ln);
            n = ((s[1]-63) << 12) | ((s[2]-63) << 6) | (s[3]-63); p = 4;
            if (n < 63) die("long form used for n<63", ln);
        }
        if (n > MAXN) die("n too large", ln);
        long nb = (long)n * (n - 1) / 2, nbytes = (nb + 5) / 6;
        if ((long)(L - p) != nbytes) die("wrong length", ln);
        memset(A, 0, sizeof A);
        long k = 0;
        for (int j = 1; j < n; j++) for (int i = 0; i < j; i++, k++) {
            int byte = s[p + k / 6] - 63, bit = (byte >> (5 - k % 6)) & 1;
            A[i][j] = A[j][i] = bit;
        }
        for (; k < nbytes * 6; k++) if (((s[p + k / 6] - 63) >> (5 - k % 6)) & 1) die("nonzero padding", ln);
        int e = 0, mind = 1 << 30, maxd = 0, tf = 1;
        for (int i = 0; i < n; i++) {
            int d = 0;
            for (int j = 0; j < n; j++) d += A[i][j];
            e += d; if (d < mind) mind = d; if (d > maxd) maxd = d;
        }
        if (n == 0) mind = 0;
        for (int a = 0; a < n && tf; a++) for (int b = a + 1; b < n && tf; b++) if (A[a][b])
            for (int c = b + 1; c < n; c++) if (A[a][c] && A[b][c]) { tf = 0; break; }
        int cand[MAXN]; for (int i = 0; i < n; i++) cand[i] = i;
        best = 0; rec(cand, n, 0);
        int ok = tf && best < K;
        printf("n=%d e=%d deg=[%d,%d] tf=%d alpha=%d ok=%d\n", n, e / 2, mind, maxd, tf, best, ok);
        ngr++; allok &= ok;
    }
    fprintf(stderr, "graphs=%d allok=%d\n", ngr, allok);
    if (ngr == 0) return 3;
    return allok ? 0 : 1;
}
