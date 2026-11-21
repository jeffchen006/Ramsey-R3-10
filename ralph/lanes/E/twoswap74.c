#include "gutil.h"

#define MAXEDGES 325
#define MAXSETS 4096

typedef struct { int left, right; } edge_t;
static set_t witnesses[MAXEDGES][MAXSETS];
static unsigned counts[MAXEDGES];
static edge_t edges[MAXEDGES];
static graph_t graph, original;
static set_t full;
static unsigned long pairs, candidates, outputs;

static void toggle(edge_t edge)
{
    graph.adj[edge.left] ^= BIT(edge.right);
    graph.adj[edge.right] ^= BIT(edge.left);
}

static void all_sets(set_t pending, set_t picked, int need, int index)
{
    if (!need) {
        if (counts[index] == MAXSETS) exit(3);
        witnesses[index][counts[index]++] = picked;
        return;
    }
    while (POP(pending) >= need) {
        int vertex = CTZ(pending);
        pending &= pending - 1;
        all_sets(pending & ~graph.adj[vertex], picked | BIT(vertex), need - 1, index);
    }
}

static set_t first_set(set_t pending, set_t picked, int need)
{
    if (!need) return picked;
    while (POP(pending) >= need) {
        int vertex = CTZ(pending);
        pending &= pending - 1;
        set_t result = first_set(pending & ~graph.adj[vertex], picked | BIT(vertex), need - 1);
        if (result) return result;
    }
    return 0;
}

static int permitted(edge_t edge, int alpha)
{
    return !(original.adj[edge.left] & BIT(edge.right)) &&
           !(graph.adj[edge.left] & graph.adj[edge.right]) &&
           POP(graph.adj[edge.left]) < alpha && POP(graph.adj[edge.right]) < alpha;
}

static void search(int first, int second, int alpha)
{
    set_t initial = 0;
    if (counts[first]) initial = witnesses[first][0];
    else if (counts[second]) initial = witnesses[second][0];
    else {
        set_t forced = BIT(edges[first].left) | BIT(edges[first].right) |
                       BIT(edges[second].left) | BIT(edges[second].right);
        if (POP(forced) > alpha + 1) return;
        set_t possible = full & ~forced;
        for (set_t pending = forced; pending; pending &= pending - 1) {
            int vertex = CTZ(pending);
            if (graph.adj[vertex] & forced) return;
            possible &= ~graph.adj[vertex];
        }
        initial = first_set(possible, forced, alpha + 1 - POP(forced));
        if (!initial) return;
    }
    ++pairs;
    for (set_t low = initial; low; low &= low - 1) {
        int left = CTZ(low);
        for (set_t high = low & (low - 1); high; high &= high - 1) {
            int right = CTZ(high);
            edge_t added = {left, right};
            if (!permitted(added, alpha)) continue;
            set_t endpoints = BIT(left) | BIT(right);
            set_t repair = full;
            const int removed[2] = {first, second};
            for (int index = 0; index < 2 && POP(repair) >= 2; ++index) {
                int label = removed[index];
                for (unsigned ii = 0; ii < counts[label] && POP(repair) >= 2; ++ii) {
                    set_t subset = witnesses[label][ii];
                    if ((subset & endpoints) != endpoints) repair &= subset;
                }
            }
            if (POP(repair) < 2) continue;
            toggle(added);
            for (set_t low_other = repair; low_other; low_other &= low_other - 1) {
                int left_other = CTZ(low_other);
                for (set_t high_other = low_other & (low_other - 1); high_other; high_other &= high_other - 1) {
                    int right_other = CTZ(high_other);
                    set_t other = BIT(left_other) | BIT(right_other);
                    if ((other & initial) == other && (left_other < left ||
                            (left_other == left && right_other <= right))) continue;
                    edge_t also_added = {left_other, right_other};
                    if (!permitted(also_added, alpha)) continue;
                    ++candidates;
                    toggle(also_added);
                    if (alpha_le(&graph, alpha)) {
                        g6_write(stdout, &graph);
                        ++outputs;
                    }
                    toggle(also_added);
                }
            }
            toggle(added);
        }
    }
}

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    int alpha = atoi(argv[1]);
    if (alpha < 2 || alpha > 9) return 2;
    char line[1024];
    unsigned long inputs = 0;
    while (fgets(line, sizeof line, stdin)) {
        int order = line[0] - 63;
        if (order < 1 || order > 26 || strlen(line) != (size_t)(2 + (order*(order-1)/2+5)/6) ||
                g6_read(line, &graph) || !g_trianglefree(&graph) || !alpha_le(&graph, alpha)) return 2;
        ++inputs;
        original = graph;
        full = BIT(order) - 1;
        int size = 0;
        for (int left = 0; left < order; ++left) {
            for (set_t high = graph.adj[left] & ~(BIT(left+1)-1); high; high &= high - 1) {
                int right = CTZ(high);
                edges[size] = (edge_t){left, right};
                counts[size] = 0;
                all_sets(full & ~(graph.adj[left] | graph.adj[right]), BIT(left) | BIT(right), alpha - 1, size);
                ++size;
            }
        }
        for (int first = 0; first < size; ++first) {
            toggle(edges[first]);
            for (int second = first + 1; second < size; ++second) {
                toggle(edges[second]);
                search(first, second, alpha);
                toggle(edges[second]);
            }
            toggle(edges[first]);
        }
    }
    fprintf(stderr, "double swaps: inputs=%lu critical two-deletions=%lu tested=%lu labeled outputs=%lu\n",
            inputs, pairs, candidates, outputs);
    return ferror(stdin) || fflush(stdout) == EOF;
}
