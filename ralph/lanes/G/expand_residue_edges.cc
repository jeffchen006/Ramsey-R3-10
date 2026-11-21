#include "gutil.h"

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    int independence = atoi(argv[1]);
    if (independence < 2 || independence > 62) return 2;
    char line[4096];
    long count = 0, output = 0;
    while (fgets(line, sizeof(line), stdin)) {
        graph_t source;
        if (g6_read(line, &source) || !g_trianglefree(&source) || !alpha_le(&source, independence)) return 2;
        ++count;
        int order = source.n;
        for (int first = 0; first < order; ++first) {
            if (POP(source.adj[first]) >= independence) continue;
            for (int second = first + 1; second < order; ++second) {
                if (POP(source.adj[second]) >= independence || source.adj[first] & source.adj[second]
                    || source.adj[first] & BIT(second)) continue;
                source.adj[first] |= BIT(second);
                source.adj[second] |= BIT(first);
                g6_write(stdout, &source);
                ++output;
                source.adj[first] ^= BIT(second);
                source.adj[second] ^= BIT(first);
            }
        }
    }
    fprintf(stderr, "%ld inputs; %ld labelled edge additions\n", count, output);
    return ferror(stdin) || ferror(stdout) ? 2 : 0;
}
