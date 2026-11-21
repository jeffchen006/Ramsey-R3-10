#include "gutil.h"

int main(int argc, char **argv)
{
    if (argc != 5) return 2;
    int order = atoi(argv[1]), edges = atoi(argv[2]), forbidden = atoi(argv[3]);
    long long expected = atoll(argv[4]), count = 0;
    if (order < 1 || order > 62 || forbidden < 1 || forbidden > order || expected < 1) return 2;
    size_t width = 2 + (order * (order-1) / 2 + 5) / 6;
    char line[1024], previous[1024] = {0};
    while (fgets(line, sizeof line, stdin)) {
        graph_t graph;
        ++count;
        if (strlen(line) != width || line[width-1] != '\n' || line[0] != order+63 ||
            strcmp(previous, line) >= 0 || g6_read(line, &graph) || g_edges(&graph) != edges ||
            !g_trianglefree(&graph) || !alpha_le(&graph, forbidden-1)) {
            fprintf(stderr, "invalid dual or ordering at input %lld\n", count);
            return 1;
        }
        memcpy(previous, line, width+1);
    }
    if (ferror(stdin) || count != expected) {
        fprintf(stderr, "read %lld valid duals; expected %lld\n", count, expected);
        return 1;
    }
    printf("checked %lld order-%d e%d duals, triangle-free and alpha<%d, strictly ordered\n",
           count, order, edges, forbidden);
    return 0;
}
