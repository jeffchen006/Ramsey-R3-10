#include "gutil.h"

static graph_t graph;
static set_t hits[1 << 17];
static size_t hit_count;
static set_t neighborhood;
static int pivot, radius, alpha, delta;
static unsigned long raw;

static void independent_targets(set_t pending, set_t picked, int count)
{
    if (!count) {
        if (hit_count == sizeof hits / sizeof *hits) exit(3);
        hits[hit_count++] = picked;
        return;
    }
    while (POP(pending) >= count) {
        int vertex = CTZ(pending);
        pending &= pending-1;
        independent_targets(pending & ~graph.adj[vertex], picked | BIT(vertex), count-1);
    }
}

static void assign(set_t pending, set_t picked, int count, int changes)
{
    if (!count) {
        if (!changes && !delta) return;
        for (size_t index = 0; index < hit_count; ++index)
            if (!(hits[index] & picked)) return;
        graph.adj[pivot] = picked;
        set_t toggle = picked ^ neighborhood;
        for (set_t todo = toggle; todo; todo &= todo-1) graph.adj[CTZ(todo)] ^= BIT(pivot);
        g6_write(stdout, &graph);
        for (set_t todo = toggle; todo; todo &= todo-1) graph.adj[CTZ(todo)] ^= BIT(pivot);
        graph.adj[pivot] = neighborhood;
        ++raw;
        return;
    }
    if (changes + count - POP(pending & neighborhood) > radius) return;
    while (POP(pending) >= count) {
        int vertex = CTZ(pending);
        pending &= pending-1;
        int next = changes + !(neighborhood & BIT(vertex));
        if (next <= radius) assign(pending & ~graph.adj[vertex], picked | BIT(vertex), count-1, next);
    }
}

int main(int argc, char **argv)
{
    if (argc != 3 && argc != 4) return 2;
    alpha = atoi(argv[1]);
    radius = atoi(argv[2]);
    delta = argc == 4 ? atoi(argv[3]) : 0;
    if (alpha < 2 || alpha > 9 || radius < 1 || radius > alpha) return 2;
    if (delta < -1 || delta > 1) return 2;
    char line[1024];
    unsigned long inputs = 0;
    while (fgets(line, sizeof line, stdin)) {
        int order = line[0]-63;
        if (order < 2 || order > 62 || strlen(line) != (size_t)(2+(order*(order-1)/2+5)/6) ||
                g6_read(line, &graph) || !g_trianglefree(&graph) || !alpha_le(&graph, alpha)) return 2;
        ++inputs;
        for (pivot = 0; pivot < graph.n; ++pivot) {
            set_t domain = (BIT(graph.n)-1) & ~BIT(pivot);
            neighborhood = graph.adj[pivot];
            int target = POP(neighborhood) + delta;
            if (target < 0 || target > alpha) continue;
            hit_count = 0;
            independent_targets(domain, 0, alpha);
            assign(domain, 0, target, 0);
        }
    }
    fprintf(stderr, "stars: inputs=%lu labeled edits=%lu\n", inputs, raw);
    return ferror(stdin) || fflush(stdout) == EOF;
}
