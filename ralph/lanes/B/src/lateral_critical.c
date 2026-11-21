#include "gutil.h"

static graph_t graph;
static set_t endpoints, intersection;
static int found;

static int intersect_witnesses(set_t untried, set_t picked, int need)
{
    if (!need) {
        found = 1;
        intersection &= picked | endpoints;
        return intersection == endpoints;
    }
    while (POP(untried) >= need) {
        int vertex = CTZ(untried);
        untried &= untried-1;
        if (intersect_witnesses(untried & ~graph.adj[vertex], picked | BIT(vertex), need-1)) return 1;
    }
    return 0;
}

static void toggle(int first, int second)
{
    graph.adj[first] ^= BIT(second);
    graph.adj[second] ^= BIT(first);
}

int main(int argc, char **argv)
{
    if (argc != 3) return 2;
    int alpha = atoi(argv[1]), minimum = atoi(argv[2]);
    if (alpha < 2 || alpha > 9 || minimum < 0 || minimum > alpha) return 2;
    char line[1024];
    long long graphs = 0, edits = 0, tries = 0, no_witness = 0;
    while (fgets(line, sizeof line, stdin)) {
        int order = line[0]-63;
        if (order < 1 || order > 62 || strlen(line) != (size_t)(2+(order*(order-1)/2+5)/6) ||
                g6_read(line, &graph) || !g_trianglefree(&graph) || !alpha_le(&graph, alpha)) return 2;
        ++graphs;
        set_t full = BIT(graph.n)-1;
        int degrees[64];
        for (int vertex = 0; vertex < graph.n; ++vertex) degrees[vertex] = POP(graph.adj[vertex]);
        for (int first = 0; first < graph.n; ++first) {
            for (set_t left = graph.adj[first] & (BIT(first)-1); left; left &= left-1) {
                int second = CTZ(left);
                ++tries;
                endpoints = BIT(first) | BIT(second);
                intersection = full;
                found = 0;
                if (intersect_witnesses(full & ~(graph.adj[first] | graph.adj[second]), 0, alpha-1)) continue;
                if (!found) { ++no_witness; continue; }
                toggle(first, second);
                --degrees[first];
                --degrees[second];
                set_t forced = 0;
                for (int vertex = 0; vertex < graph.n; ++vertex)
                    if (degrees[vertex] < minimum) forced |= BIT(vertex);
                for (set_t low = intersection; low; low &= low-1) {
                    int tail = CTZ(low);
                    if (degrees[tail] >= alpha) continue;
                    for (set_t high = low & (low-1); high; high &= high-1) {
                        int head = CTZ(high);
                        set_t edge = BIT(tail) | BIT(head);
                        if (edge == endpoints || (forced & ~edge) || degrees[head] >= alpha ||
                                degrees[tail]+1 < minimum || degrees[head]+1 < minimum ||
                                (graph.adj[tail] & BIT(head)) || (graph.adj[tail] & graph.adj[head])) continue;
                        toggle(tail, head);
                        g6_write(stdout, &graph);
                        toggle(tail, head);
                        ++edits;
                    }
                }
                ++degrees[first];
                ++degrees[second];
                toggle(first, second);
            }
        }
    }
    fprintf(stderr, "lateral graphs=%lld tries=%lld reducible deletions=%lld labeled edits=%lld\n",
            graphs, tries, no_witness, edits);
    return ferror(stdin) || fflush(stdout) == EOF;
}
