#include "gutil.h"

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    int bound = atoi(argv[1]);
    if (bound < 2 || bound > 9) return 2;
    char line[1024];
    graph_t graph;
    unsigned long input = 0, output = 0;
    while (fgets(line, sizeof line, stdin)) {
        int order = line[0] - 63;
        if (order < 1 || order > 62 || strlen(line) != (size_t)(2 + (order*(order-1)/2+5)/6) ||
            g6_read(line, &graph) || !g_trianglefree(&graph) || !alpha_le(&graph, bound)) return 2;
        ++input;
        set_t all = BIT(order) - 1;
        for (int left = 0; left < order; ++left) {
            for (set_t higher = graph.adj[left] & ~(BIT(left+1)-1); higher; higher &= higher - 1) {
                int right = CTZ(higher);
                set_t common_non = all & ~(graph.adj[left] | graph.adj[right]);
                if (has_indep(graph.adj, common_non, bound-1)) continue;
                graph.adj[left] ^= BIT(right);
                graph.adj[right] ^= BIT(left);
                g6_write(stdout, &graph);
                graph.adj[left] ^= BIT(right);
                graph.adj[right] ^= BIT(left);
                ++output;
            }
        }
    }
    fprintf(stderr, "down: inputs=%lu outputs=%lu\n", input, output);
    return ferror(stdin) || fflush(stdout) == EOF;
}
