#include "gutil.h"

int main(int argc, char **argv)
{
    if (argc != 4) return 2;
    int minimum = atoi(argv[1]), alpha = atoi(argv[2]), target = atoi(argv[3]);
    if (minimum < 0 || alpha < 2 || alpha > 9 || minimum > alpha || target < 0) return 2;
    graph_t source;
    char line[1024];
    long long count = 0, stems = 0;
    while (fgets(line, sizeof(line), stdin)) {
        int order = line[0]-63;
        if (order < 3 || order > 62 || strlen(line) != (size_t)(2+(order*(order-1)/2+5)/6) ||
            g6_read(line, &source)) return 2;
        ++count;
        int edges = g_edges(&source);
        set_t full = BIT(order)-1;
        for (int first = 0; first < order; ++first)
            for (set_t later = source.adj[first] & ~(BIT(first+1)-1); later; later &= later-1) {
                int second = CTZ(later);
                int size = edges-POP(source.adj[first])-POP(source.adj[second])+1;
                if (target-size < 2*minimum-1 || target-size > 2*alpha-1) continue;
                set_t remain = full & ~(BIT(first) | BIT(second));
                graph_t base = {0};
                int mapping[64];
                for (set_t rest = remain; rest; rest &= rest-1) {
                    int vertex = CTZ(rest);
                    if (POP(source.adj[vertex] & remain) < minimum-1) break;
                    mapping[vertex] = base.n++;
                }
                if (base.n != order-2) continue;
                for (set_t rest = remain; rest; rest &= rest-1) {
                    int vertex = CTZ(rest);
                    for (set_t adj = source.adj[vertex] & remain; adj; adj &= adj-1)
                        base.adj[mapping[vertex]] |= BIT(mapping[CTZ(adj)]);
                }
                g6_write(stdout, &base);
                ++stems;
            }
    }
    fprintf(stderr, "Adjacent stem parents=%lld raw=%lld\n", count, stems);
    return ferror(stdin) || fflush(stdout) == EOF;
}
