#include "gutil.h"

#define MAXHITS (1u << 20)

static graph_t source;
static set_t full, hits[MAXHITS];
static unsigned int hit_count;
static unsigned long valid, calls;
static int alpha, target_edges;

static void targets(set_t candidates, set_t picked, int need)
{
    if (!need) {
        if (hit_count == MAXHITS) exit(3);
        hits[hit_count++] = picked;
        return;
    }
    while (POP(candidates) >= need) {
        int vertex = CTZ(candidates);
        candidates &= candidates-1;
        targets(candidates & ~source.adj[vertex], picked | BIT(vertex), need-1);
    }
}

static void output(set_t kept)
{
    graph_t sub = {0};
    int original[64];
    for (set_t pending = kept; pending; pending &= pending-1) original[sub.n++] = CTZ(pending);
    for (int left = 0; left < sub.n; ++left)
        for (int right = left + 1; right < sub.n; ++right)
            if (source.adj[original[left]] & BIT(original[right])) {
                sub.adj[left] |= BIT(right);
                sub.adj[right] |= BIT(left);
            }
    g6_write(stdout, &sub);
    ++valid;
}

static void search(set_t available, set_t removed, int need, int edge_count)
{
    ++calls;
    if (edge_count < target_edges || POP(available) < need) return;
    set_t critical = 0;
    int best = 64;
    for (unsigned int index = 0; index < hit_count; ++index) {
        if (removed & hits[index]) continue;
        if (!need) return;
        set_t options = available & hits[index];
        int choices = POP(options);
        if (!choices) return;
        if (choices < best) {
            best = choices;
            critical = options;
        }
        if (choices <= 1) break;
    }
    if (!need) {
        if (edge_count == target_edges) output(full & ~removed);
        return;
    }
    if (!critical) critical = available;
    while (critical) {
        int vertex = CTZ(critical);
        critical &= critical-1;
        available &= ~BIT(vertex);
        if (POP(available) < need-1) return;
        search(available, removed | BIT(vertex), need-1, edge_count - POP(source.adj[vertex] & ~removed));
    }
}

int main(int argc, char **argv)
{
    if (argc != 4 && argc != 5) return 2;
    alpha = atoi(argv[1]);
    int order = atoi(argv[2]);
    target_edges = atoi(argv[3]);
    int root = argc == 5 ? atoi(argv[4]) : -1;
    if (alpha < 2 || alpha > 9 || order < 1 || root < -1 || root > 61 || target_edges < 0) return 2;
    char line[1024];
    unsigned long inputs = 0, total_hits = 0;
    while (fgets(line, sizeof line, stdin)) {
        int size = line[0] - 63;
        if (size < order || size > 62 || root >= size || (size == order && root >= 0) ||
            strlen(line) != (size_t)(2 + (size*(size-1)/2+5)/6) ||
            g6_read(line, &source) || !g_trianglefree(&source)) return 2;
        ++inputs;
        full = BIT(size)-1;
        hit_count = 0;
        targets(full, 0, alpha+1);
        total_hits += hit_count;
        set_t removed = root < 0 ? 0 : BIT(root);
        int edge_count = g_edges(&source) - (root < 0 ? 0 : POP(source.adj[root]));
        search(full & ~removed, removed, size-order-(root >= 0), edge_count);
    }
    fprintf(stderr, "induced search: inputs=%lu forbidden=%lu calls=%lu labeled outputs=%lu\n",
            inputs, total_hits, calls, valid);
    return ferror(stdin) || fflush(stdout) == EOF;
}
