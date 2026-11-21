#include "gutil.h"

typedef struct { int first, second; } pair_t;

static void toggle(graph_t *graph, pair_t edge)
{
    graph->adj[edge.first] ^= BIT(edge.second);
    graph->adj[edge.second] ^= BIT(edge.first);
}

static int witnesses(const graph_t *graph, pair_t edge, int alpha)
{
    set_t all = BIT(graph->n) - 1;
    set_t occupied = graph->adj[edge.first] | graph->adj[edge.second]
                   | BIT(edge.first) | BIT(edge.second);
    return has_indep(graph->adj, all & ~occupied, alpha - 1);
}

static int available(const graph_t *graph, pair_t edge)
{
    return !(graph->adj[edge.first] & BIT(edge.second))
        && !(graph->adj[edge.first] & graph->adj[edge.second]);
}

static void examine(graph_t *graph, pair_t one, pair_t two, int alpha)
{
    if (one.first == two.first || one.first == two.second
        || one.second == two.first || one.second == two.second) return;
    pair_t alternatives[2][2] = {
        {{one.first, two.first}, {one.second, two.second}},
        {{one.first, two.second}, {one.second, two.first}}
    };
    toggle(graph, one);
    toggle(graph, two);
    for (int option = 0; option < 2; option++) {
        pair_t first = alternatives[option][0], second = alternatives[option][1];
        if (!available(graph, first) || !available(graph, second)) continue;
        toggle(graph, first);
        toggle(graph, second);
        if (!witnesses(graph, one, alpha) && !witnesses(graph, two, alpha)) g6_write(stdout, graph);
        toggle(graph, second);
        toggle(graph, first);
    }
    toggle(graph, two);
    toggle(graph, one);
}

int main(int argc, char **argv)
{
    char line[4096];
    int alpha = argc == 2 ? atoi(argv[1]) : 8;
    if (alpha < 2) return 2;
    while (fgets(line, sizeof line, stdin)) {
        graph_t graph;
        pair_t edges[2000];
        int count = 0;
        if (g6_read(line, &graph) || !g_trianglefree(&graph) || !alpha_le(&graph, alpha)) return 2;
        for (int first = 0; first < graph.n; first++)
            for (int second = first + 1; second < graph.n; second++)
                if (graph.adj[first] & BIT(second)) edges[count++] = (pair_t){first, second};
        for (int first = 0; first < count; first++)
            for (int second = first + 1; second < count; second++)
                examine(&graph, edges[first], edges[second], alpha);
    }
    return 0;
}
