#include "gutil.h"

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    int forbidden = atoi(argv[1]);
    char line[1024];
    long long inputs = 0, irreducible = 0, tests = 0;
    while (fgets(line, sizeof line, stdin)) {
        graph_t graph;
        if (g6_read(line, &graph)) return 1;
        ++inputs;
        int movable = 0;
        const set_t vertices = BIT(graph.n)-1;
        for (int x = 0; !movable && x < graph.n; ++x) {
            for (set_t left = graph.adj[x] & (BIT(x)-1); left; left &= left-1) {
                int y = CTZ(left);
                ++tests;
                set_t residual = vertices & ~(graph.adj[x] | graph.adj[y]);
                if (!has_indep(graph.adj, residual, forbidden-2)) {
                    movable = 1;
                    break;
                }
            }
        }
        if (!movable) {
            ++irreducible;
            fputs(line, stdout);
        }
    }
    fprintf(stderr, "irreducible: in=%lld out=%lld tests=%lld\n", inputs, irreducible, tests);
    return ferror(stdin) || fflush(stdout) == EOF;
}
