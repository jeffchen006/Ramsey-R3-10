#include "gutil.h"

int main(int argc, char **argv)
{
    if (argc != 3) return 2;
    int minimum = atoi(argv[1]), maximum = atoi(argv[2]);
    if (minimum < 0 || maximum < minimum) return 2;
    graph_t host;
    long long graphs = 0, stems = 0;
    char line[1024];
    while (fgets(line, sizeof(line), stdin)) {
        int order = line[0]-63;
        if (order < 4 || order > 62 || strlen(line) != (size_t)(2+(order*(order-1)/2+5)/6) ||
            g6_read(line, &host) || !g_trianglefree(&host)) return 1;
        ++graphs;
        int size = g_edges(&host);
        for (int left = 0; left < order; ++left) {
            for (int right = left + 1; right < order; ++right) {
                if (host.adj[left] & BIT(right)) continue;
                int reduced = size - POP(host.adj[left]) - POP(host.adj[right]);
                if (reduced < minimum || reduced > maximum) continue;
                graph_t stem = {0};
                int permutation[64];
                for (int vertex = 0; vertex < order; ++vertex)
                    if (vertex != left && vertex != right) permutation[stem.n++] = vertex;
                for (int vertex = 0; vertex < stem.n; ++vertex) {
                    for (int other = 0; other < stem.n; ++other)
                        if (host.adj[permutation[vertex]] & BIT(permutation[other])) stem.adj[vertex] |= BIT(other);
                }
                ++stems;
                g6_write(stdout, &stem);
            }
        }
    }
    fprintf(stderr, "hosts=%lld nonadjacent stems=%lld\n", graphs, stems);
    return ferror(stdin) || fflush(stdout) == EOF;
}
