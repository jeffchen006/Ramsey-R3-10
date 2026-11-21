#include "gutil.h"

typedef struct { int first, second; } pair_t;
typedef struct { set_t *sets; size_t count, capacity; } witnesses_t;

static void toggle(graph_t *graph, pair_t edge)
{
    graph->adj[edge.first] ^= BIT(edge.second);
    graph->adj[edge.second] ^= BIT(edge.first);
}

static set_t bitpair(pair_t edge)
{
    return BIT(edge.first) | BIT(edge.second);
}

static void collect(const graph_t *graph, witnesses_t *witnesses, set_t vertices, set_t chosen, int need)
{
    if (!need) {
        if (witnesses->count == witnesses->capacity) {
            size_t capacity = witnesses->capacity ? 2 * witnesses->capacity : 128;
            set_t *grown = realloc(witnesses->sets, capacity * sizeof(set_t));
            if (!grown) exit(3);
            witnesses->sets = grown;
            witnesses->capacity = capacity;
        }
        witnesses->sets[witnesses->count++] = chosen;
        return;
    }
    while (POP(vertices) >= need) {
        int vertex = CTZ(vertices);
        vertices &= vertices - 1;
        collect(graph, witnesses, vertices & ~graph->adj[vertex], chosen | BIT(vertex), need - 1);
    }
}

static void collect_pair(const graph_t *graph, witnesses_t *witnesses, pair_t edge, int alpha)
{
    set_t all = BIT(graph->n) - 1;
    set_t forbidden = bitpair(edge) | graph->adj[edge.first] | graph->adj[edge.second];
    collect(graph, witnesses, all & ~forbidden, bitpair(edge), alpha - 1);
}

static int available(const graph_t *graph, pair_t edge, int alpha, set_t removed_first, set_t removed_second)
{
    set_t endpoints = bitpair(edge);
    return endpoints != removed_first && endpoints != removed_second
        && !(graph->adj[edge.first] & BIT(edge.second)) && !(graph->adj[edge.first] & graph->adj[edge.second])
        && POP(graph->adj[edge.first]) < alpha && POP(graph->adj[edge.second]) < alpha;
}

static void repair(graph_t *graph, const witnesses_t *witnesses, int alpha, set_t removed_first, set_t removed_second)
{
    set_t tips = witnesses->count ? witnesses->sets[0] : BIT(graph->n) - 1;
    while (tips) {
        int first = CTZ(tips);
        tips &= tips - 1;
        set_t seconds = tips;
        while (seconds) {
            int second = CTZ(seconds);
            seconds &= seconds - 1;
            pair_t one = {first, second};
            if (!available(graph, one, alpha, removed_first, removed_second)) continue;
            set_t endpoints = bitpair(one);
            set_t left = BIT(graph->n) - 1;
            for (size_t index = 0; index < witnesses->count; index++) {
                set_t witness = witnesses->sets[index];
                if ((witness & endpoints) != endpoints) left &= witness;
                if (POP(left) < 2) break;
            }
            if (POP(left) < 2) continue;
            toggle(graph, one);
            while (left) {
                int third = CTZ(left);
                left &= left - 1;
                set_t fourths = left;
                while (fourths) {
                    int fourth = CTZ(fourths);
                    fourths &= fourths - 1;
                    pair_t two = {third, fourth};
                    if (!available(graph, two, alpha, removed_first, removed_second)) continue;
                    toggle(graph, two);
                    g6_write(stdout, graph);
                    toggle(graph, two);
                }
            }
            toggle(graph, one);
        }
    }
}

int main(int argc, char **argv)
{
    char line[4096];
    int alpha = argc > 1 ? atoi(argv[1]) : 8;
    int removals = argc > 2 ? atoi(argv[2]) : 2;
    witnesses_t witnesses = {0};
    if (alpha < 2 || (removals != 1 && removals != 2)) return 2;
    while (fgets(line, sizeof line, stdin)) {
        graph_t graph;
        pair_t edges[2000];
        int count = 0;
        if (g6_read(line, &graph) || !g_trianglefree(&graph) || !alpha_le(&graph, alpha)) return 2;
        for (int first = 0; first < graph.n; first++)
            for (int second = first + 1; second < graph.n; second++)
                if (graph.adj[first] & BIT(second)) edges[count++] = (pair_t){first, second};
        for (int first = 0; first < count; first++) {
            toggle(&graph, edges[first]);
            if (removals == 1) {
                witnesses.count = 0;
                collect_pair(&graph, &witnesses, edges[first], alpha);
                repair(&graph, &witnesses, alpha, bitpair(edges[first]), 0);
            } else {
                for (int second = first + 1; second < count; second++) {
                    witnesses.count = 0;
                    toggle(&graph, edges[second]);
                    collect_pair(&graph, &witnesses, edges[first], alpha);
                    collect_pair(&graph, &witnesses, edges[second], alpha);
                    repair(&graph, &witnesses, alpha, bitpair(edges[first]), bitpair(edges[second]));
                    toggle(&graph, edges[second]);
                }
            }
            toggle(&graph, edges[first]);
        }
    }
    free(witnesses.sets);
    return 0;
}
