#include "gutil.h"

int main(void)
{
    char line[1024];
    graph_t graph;
    long long inputs = 0, outputs = 0;
    while (fgets(line, sizeof line, stdin)) {
        if (g6_read(line, &graph)) return 1;
        ++inputs;
        for (int right = 0; right < graph.n; ++right)
            for (int left = 0; left < right; ++left) {
                if ((graph.adj[left] & BIT(right)) || (graph.adj[left] & graph.adj[right])) continue;
                graph.adj[left] |= BIT(right);
                graph.adj[right] |= BIT(left);
                g6_write(stdout, &graph);
                graph.adj[left] ^= BIT(right);
                graph.adj[right] ^= BIT(left);
                ++outputs;
            }
    }
    fprintf(stderr, "edgeup: in=%lld raw_out=%lld\n", inputs, outputs);
    return ferror(stdin) || fflush(stdout) == EOF;
}
