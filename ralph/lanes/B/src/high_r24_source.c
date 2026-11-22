#include "gutil.h"

#ifndef STEM_ORDER
#define STEM_ORDER 20
#endif
#define TARGET_WEIGHT (2 * STEM_ORDER - 20)

static int fits(const graph_t *graph, const int *ids, set_t selected)
{
    int counts[16] = {0};
    set_t rest = ((BIT(graph->n) - 1) & ~selected);
    while (rest) {
        int site = CTZ(rest);
        rest &= rest - 1;
        unsigned mask = 0;
        for (int row = 0; row < 4; ++row)
            if (graph->adj[site] & BIT(ids[row])) mask |= 1U << row;
        if (!mask || POP(mask) > 2 || ++counts[mask] > (POP(mask) == 2 ? 1 : 3))
            return 0;
    }
    for (int row = 0; row < 4; ++row)
        if (counts[1U << row] != 3) return 0;
    return 1;
}

static int screen(const graph_t *graph, set_t pending, set_t chosen,
                  int count, int weight, int *ids, const int *degree)
{
    if (count == 4) return weight == TARGET_WEIGHT && fits(graph, ids, chosen);
    while (POP(pending) >= 4 - count) {
        int site = CTZ(pending);
        pending &= pending - 1;
        int next = weight + degree[site];
        if (next + 6 * (3 - count) < TARGET_WEIGHT || next + 4 * (3 - count) > TARGET_WEIGHT) continue;
        ids[count] = site;
        if (screen(graph, pending & ~graph->adj[site], chosen | BIT(site),
                   count + 1, next, ids, degree)) return 1;
    }
    return 0;
}

static void filtered_write(FILE *out, const graph_t *graph)
{
    if (graph->n != STEM_ORDER) abort();
    int degree[64], ids[4];
    set_t pending = 0;
    for (int site = 0; site < graph->n; ++site) {
        degree[site] = POP(graph->adj[site]);
        if (degree[site] >= 4 && degree[site] <= 6) pending |= BIT(site);
    }
    if (screen(graph, pending, 0, 0, 0, ids, degree)) g6_write(out, graph);
}

#ifdef STREAM
int main(void)
{
    graph_t graph;
    char text[128];
    const size_t length = 2 + (STEM_ORDER * (STEM_ORDER - 1) / 2 + 5) / 6;
    while (fgets(text, sizeof(text), stdin)) {
        if (strlen(text) != length || text[length - 1] != '\n' || g6_read(text, &graph)) return 1;
        filtered_write(stdout, &graph);
    }
    return ferror(stdin) || fflush(stdout) || ferror(stdout);
}
#else
#define g6_write filtered_write
#include "glue5.c"
#endif
