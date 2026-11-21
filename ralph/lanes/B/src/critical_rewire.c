#include "gutil.h"

static graph_t input, output;
static int alpha, minimum, vertex, target;
static set_t *max_independent;
static size_t used, capacity;
static long long graphs, nodes, rewires;

static void list_independent(set_t available, set_t chosen, int needed)
{
    if (!needed) {
        if (used == capacity) {
            size_t size = capacity ? 2*capacity : 256;
            if (size > 10000000) exit(2);
            set_t *replacement = realloc(max_independent, size*sizeof(*max_independent));
            if (!replacement) exit(2);
            max_independent = replacement;
            capacity = size;
        }
        max_independent[used++] = chosen;
        return;
    }
    while (POP(available) >= needed) {
        int next = CTZ(available);
        available &= available-1;
        list_independent(available & ~input.adj[next], chosen | BIT(next), needed-1);
    }
}

static void search(set_t chosen, set_t available)
{
    ++nodes;
    int count = POP(chosen);
    if (count + POP(available) < target) return;
    set_t private_witnesses = 0, branch = 0;
    int options = 64;
    for (size_t index = 0; index < used; ++index) {
        set_t witness = max_independent[index];
        if (witness & BIT(vertex)) continue;
        set_t covered = witness & chosen;
        if (!covered) {
            set_t eligible = witness & available;
            int remaining = POP(eligible);
            if (!remaining || count == target) return;
            if (remaining < options) {
                branch = eligible;
                options = remaining;
            }
        } else if (!(covered & (covered-1))) {
            private_witnesses |= covered;
        }
    }
    if (private_witnesses != chosen) return;
    if (!branch) {
        if (count != target || chosen == input.adj[vertex]) return;
        output.adj[vertex] = chosen;
        for (set_t rest = chosen; rest; rest &= rest-1) output.adj[CTZ(rest)] |= BIT(vertex);
        g6_write(stdout, &output);
        for (set_t rest = chosen; rest; rest &= rest-1) output.adj[CTZ(rest)] &= ~BIT(vertex);
        ++rewires;
        return;
    }
    while (branch) {
        int next = CTZ(branch);
        branch &= branch-1;
        available &= ~BIT(next);
        search(chosen | BIT(next), available & ~input.adj[next]);
    }
}

int main(int argc, char **argv)
{
    if (argc != 4) return 2;
    alpha = atoi(argv[1]);
    minimum = atoi(argv[2]);
    int increment = atoi(argv[3]);
    if (alpha < 2 || alpha > 9 || minimum < 0 || minimum > alpha || increment < 0 || increment > 2) return 2;
    char line[1024];
    while (fgets(line, sizeof(line), stdin)) {
        int order = line[0]-63;
        if (order < 2 || order > 62 || strlen(line) != (size_t)(2+(order*(order-1)/2+5)/6) ||
                g6_read(line, &input) || !g_trianglefree(&input) || !alpha_le(&input, alpha)) return 2;
        ++graphs;
        set_t full = BIT(order)-1;
        used = 0;
        list_independent(full, 0, alpha);
        for (vertex = 0; vertex < order; ++vertex) {
            target = POP(input.adj[vertex])+increment;
            if (target < minimum || target > alpha) continue;
            output = input;
            output.adj[vertex] = 0;
            set_t forced = 0, available = full ^ BIT(vertex);
            for (int other = 0; other < order; ++other) {
                if (other == vertex) continue;
                output.adj[other] &= ~BIT(vertex);
                int degree = POP(output.adj[other]);
                if (degree >= alpha) available &= ~BIT(other);
                if (degree < minimum) forced |= BIT(other);
                if (degree+1 < minimum) { available = 0; break; }
            }
            if (POP(forced) > target || (forced & ~available)) continue;
            set_t blocked = 0;
            for (set_t rest = forced; rest; rest &= rest-1) blocked |= output.adj[CTZ(rest)];
            if (forced & blocked) continue;
            search(forced, available & ~(forced | blocked));
        }
    }
    fprintf(stderr, "rewire graphs=%lld nodes=%lld labeled edits=%lld\n", graphs, nodes, rewires);
    free(max_independent);
    return ferror(stdin) || fflush(stdout) == EOF;
}
