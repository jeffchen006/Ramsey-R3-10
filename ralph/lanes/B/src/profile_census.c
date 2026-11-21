#include "gutil.h"

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    int calibration = !strcmp(argv[1], "22");
    if (!calibration && strcmp(argv[1], "30")) return 2;
    int order = calibration ? 22 : 30;
    int edges = calibration ? 63 : 88;
    long long seen = 0, mask_count[8] = {0};
    long long anchor_count[31] = {0}, branch_count[4] = {0};
    char line[1024];
    while (fgets(line, sizeof line, stdin)) {
        graph_t graph;
        if ((int)strlen(line) != 2 + (order * (order - 1) / 2 + 5) / 6 ||
            line[0] != 63 + order || g6_read(line, &graph) || g_edges(&graph) != edges) {
            fprintf(stderr, "bad input line %lld\n", seen + 1);
            return 1;
        }
        ++seen;
        int degree[64], mask = 0, anchors = 0, branches = 0;
        for (int vertex = 0; vertex < order; ++vertex) degree[vertex] = POP(graph.adj[vertex]);
        for (int vertex = 0; vertex < order; ++vertex) {
            int dual = edges, smallest = order;
            for (set_t neighbors = graph.adj[vertex]; neighbors; neighbors &= neighbors-1) {
                int neighbor_degree = degree[CTZ(neighbors)];
                dual -= neighbor_degree;
                if (neighbor_degree < smallest) smallest = neighbor_degree;
            }
            if (calibration) {
                if (degree[vertex] == 5 && dual <= 33) mask |= 1;
                continue;
            }
            if (degree[vertex] == 5 && dual <= 58) mask |= 1;
            if (degree[vertex] == 6 && dual <= 51) mask |= 2;
            if (degree[vertex] == 7 && dual <= 43) mask |= 4;
            if (smallest >= 5) {
                if (degree[vertex] == 6 && dual == 52) { ++anchors; branches |= 1; }
                if (degree[vertex] == 7 && dual == 44) { ++anchors; branches |= 2; }
            }
        }
        ++mask_count[mask];
        if (!mask) {
            if (!calibration && anchors < 4) {
                fprintf(stderr, "anchor bound failed at input %lld\n", seen);
                return 1;
            }
            ++anchor_count[anchors];
            ++branch_count[branches];
            fputs(line, stdout);
        }
    }
    if (ferror(stdin) || fflush(stdout)) return 1;
    fprintf(stderr, "seen=%lld\n", seen);
    for (int mask = 0; mask < 8; ++mask) fprintf(stderr, "mask %d: %lld\n", mask, mask_count[mask]);
    for (int count = 0; count <= order; ++count)
        if (anchor_count[count]) fprintf(stderr, "uncovered with %d anchors: %lld\n", count, anchor_count[count]);
    for (int mask = 0; mask < 4; ++mask)
        fprintf(stderr, "uncovered branch mask %d: %lld\n", mask, branch_count[mask]);
    return 0;
}
