#include "gutil.h"

#include <cstdio>

static int deletable(const graph_t &graph, int alpha)
{
    int count = 0;
    set_t all = BIT(graph.n) - 1;
    for (int first = 0; first < graph.n; ++first)
        for (set_t rest = graph.adj[first] & ~(BIT(first + 1) - 1); rest; rest &= rest - 1) {
            int second = CTZ(rest);
            if (!has_indep(graph.adj, all & ~(graph.adj[first] | graph.adj[second]), alpha - 1)) ++count;
        }
    return count;
}

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    int alpha = std::atoi(argv[1]);
    if (alpha < 2 || alpha > 62) return 2;
    char line[4096];
    while (std::fgets(line, sizeof line, stdin)) {
        graph_t graph;
        if (g6_read(line, &graph) || !g_trianglefree(&graph) || !alpha_le(&graph, alpha)) return 2;
        int addable = 0;
        for (int first = 0; first < graph.n; ++first)
            for (int second = first + 1; second < graph.n; ++second)
                addable += !(graph.adj[first] & (graph.adj[second] | BIT(second)));
        std::printf("%d\t%d\t%d\t", g_edges(&graph), deletable(graph, alpha), addable);
        g6_write(stdout, &graph);
    }
    return std::ferror(stdin) || std::ferror(stdout) ? 2 : 0;
}
