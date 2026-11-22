#include "gutil.h"

static unsigned long long count_rows(const graph_t *graph, const set_t *closed, set_t remaining,
                                    set_t dominated, set_t all, int need, int degree_sum, int target)
{
    if (!need) return dominated == all && (target < 0 || degree_sum == target);
    unsigned long long matches = 0;
    while (POP(remaining) >= need) {
        int index = CTZ(remaining);
        remaining &= remaining - 1;
        matches += count_rows(graph, closed, remaining & ~graph->adj[index],
                              dominated | closed[index], all, need - 1,
                              degree_sum + POP(graph->adj[index]), target);
    }
    return matches;
}

int main(int argc, char **argv)
{
    if (argc != 2 && argc != 3) return 2;
    int size = atoi(argv[1]);
    int target = argc == 3 ? atoi(argv[2]) : -1;
    if (size < 1 || size > 6) return 2;
    char line[1024], previous[1024] = {0};
    long long rank = 0;
    while (fgets(line, sizeof line, stdin)) {
        graph_t graph;
        if (strcmp(previous, line) >= 0 || g6_read(line, &graph) ||
            strlen(line) != (size_t)(2 + (graph.n * (graph.n - 1) / 2 + 5) / 6)) return 1;
        strcpy(previous, line);
        set_t closed[64], all = BIT(graph.n) - 1;
        for (int index = 0; index < graph.n; ++index) closed[index] = graph.adj[index] | BIT(index);
        printf("%lld\t%llu\t%s", ++rank, count_rows(&graph, closed, all, 0, all, size, 0, target), line);
    }
    return ferror(stdin) || !rank;
}
