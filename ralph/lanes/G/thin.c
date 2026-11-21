#include "gutil.h"

int main(int argc, char **argv)
{
    int alpha = argc == 2 ? atoi(argv[1]) : 8;
    char line[4096];
    if (alpha < 2) return 2;
    while (fgets(line, sizeof line, stdin)) {
        graph_t graph;
        if (g6_read(line, &graph) || !g_trianglefree(&graph) || !alpha_le(&graph, alpha)) return 2;
        set_t all = BIT(graph.n) - 1;
        for (int first = 0; first < graph.n; first++) {
            set_t rest = graph.adj[first] & ~(BIT(first + 1) - 1);
            while (rest) {
                int second = CTZ(rest);
                rest &= rest - 1;
                set_t exterior = all & ~(graph.adj[first] | graph.adj[second]);
                if (has_indep(graph.adj, exterior, alpha - 1)) continue;
                graph.adj[first] ^= BIT(second);
                graph.adj[second] ^= BIT(first);
                g6_write(stdout, &graph);
                graph.adj[second] ^= BIT(first);
                graph.adj[first] ^= BIT(second);
            }
        }
    }
    return 0;
}
