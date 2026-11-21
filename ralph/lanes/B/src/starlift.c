/* Exact one-vertex degree change by independent transversals of the old maximum sets. */
#include "gutil.h"
#include <unistd.h>

static graph_t graph;
static set_t *maximum, *uncovered[64];
static size_t capacity, count;
static int root, target, shift = 1, stop, local_critical, found;
static long long inputs, outputs, nodes;

static void maximum_sets(set_t set, set_t eligible, int need)
{
    if (!need) {
        if (count == capacity) {
            capacity = capacity ? 2 * capacity : 1024;
            maximum = realloc(maximum, capacity * sizeof(*maximum));
            if (!maximum) exit(2);
        }
        maximum[count++] = set;
        return;
    }
    while (POP(eligible) >= need) {
        int vertex = CTZ(eligible);
        eligible &= eligible - 1;
        maximum_sets(set | BIT(vertex), eligible & ~graph.adj[vertex], need - 1);
    }
}

static void emit(set_t set)
{
    if (local_critical) {
        set_t private_vertices = 0;
        for (size_t index = 0; index < count; ++index) {
            if (maximum[index] & BIT(root)) continue;
            set_t hit = set & maximum[index];
            if (hit && !(hit & (hit - 1))) private_vertices |= hit;
            if (private_vertices == set) break;
        }
        if (private_vertices != set) return;
    }
    graph_t output = graph;
    output.adj[root] = set;
    for (set_t changed = graph.adj[root] ^ set; changed; changed &= changed - 1)
        output.adj[CTZ(changed)] ^= BIT(root);
    ++outputs;
    found = 1;
    g6_write(stdout, &output);
}

static void extras(set_t set, set_t eligible, int need)
{
    if (!need) { emit(set); return; }
    while (POP(eligible) >= need && !(stop && found)) {
        int vertex = CTZ(eligible);
        eligible &= eligible - 1;
        extras(set | BIT(vertex), eligible & ~graph.adj[vertex], need - 1);
    }
}

static void transversal(set_t set, set_t eligible, int need, size_t misses, int depth)
{
    ++nodes;
    if (!misses) {
        if (!local_critical || !need) extras(set, eligible, need);
        return;
    }
    if (need <= 0 || POP(eligible) < need) return;

    const set_t *current = uncovered[depth];
    set_t branch = eligible;
    int choices = POP(branch);
    for (size_t index = 0; index < misses; ++index) {
        set_t hit = current[index] & eligible;
        int size = POP(hit);
        if (size < choices) {
            branch = hit;
            choices = size;
            if (choices <= 1) break;
        }
    }
    set_t *next = uncovered[depth + 1];
    while (branch && !(stop && found)) {
        int vertex = CTZ(branch);
        branch &= branch - 1;
        eligible &= ~BIT(vertex);
        set_t remaining = eligible & ~graph.adj[vertex];
        if (POP(remaining) < need - 1) continue;
        size_t left = 0;
        for (size_t index = 0; index < misses; ++index) {
            if (current[index] & BIT(vertex)) continue;
            if (!need || !(current[index] & remaining)) { left = misses + 1; break; }
            next[left++] = current[index];
        }
        if (left <= misses) transversal(set | BIT(vertex), remaining, need - 1, left, depth + 1);
    }
}

int main(int argc, char **argv)
{
    int alpha = 0, option;
    while ((option = getopt(argc, argv, "a:s:c1")) != -1) {
        if (option == 'a') alpha = atoi(optarg);
        else if (option == 's') shift = atoi(optarg);
        else if (option == 'c') local_critical = 1;
        else if (option == '1') stop = 1;
        else return 2;
    }
    if (alpha <= 0 || alpha > 30 || (shift != -1 && shift != 1) || optind != argc) return 2;
    size_t workspace = 0;
    long long reachable = 0;
    char line[4096];
    while (fgets(line, sizeof(line), stdin)) {
        if (g6_read(line, &graph) || graph.n <= alpha || !g_trianglefree(&graph)) return 2;
        ++inputs;
        set_t vertices = BIT(graph.n) - 1;
        count = 0;
        maximum_sets(0, vertices, alpha);
        if (capacity > workspace) {
            for (int depth = 0; depth <= alpha; ++depth) {
                uncovered[depth] = realloc(uncovered[depth], capacity * sizeof(set_t));
                if (!uncovered[depth]) exit(2);
            }
            workspace = capacity;
        }
        found = 0;
        for (root = 0; root < graph.n && !(stop && found); ++root) {
            target = POP(graph.adj[root]) + shift;
            if (target < 0 || target > alpha) continue;
            size_t misses = 0;
            for (size_t index = 0; index < count; ++index)
                if (!(maximum[index] & BIT(root))) uncovered[0][misses++] = maximum[index];
            transversal(0, vertices ^ BIT(root), target, misses, 0);
        }
        reachable += found;
    }
    if (ferror(stdin) || fflush(stdout) || ferror(stdout)) return 2;
    fprintf(stderr, "starlift: in=%lld reached=%lld out=%lld nodes=%lld\n", inputs, reachable, outputs, nodes);
    return 0;
}
