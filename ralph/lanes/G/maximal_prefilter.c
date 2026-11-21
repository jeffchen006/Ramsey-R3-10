#include "gutil.h"
#include <assert.h>
#include <time.h>

static graph_t core;
static int independence, columns, count, capacity, words, emit_witness;
static set_t full, comp[64], *sets, *compat, *domains, picked[16], unions[1 << 16];
static long long nodes, pair_rows;

static void maximal(set_t set, set_t left, set_t done)
{
    if (!(left | done)) {
        if (count == capacity) {
            capacity = capacity ? 2 * capacity : 256;
            sets = realloc(sets, (size_t)capacity * sizeof(*sets));
            assert(sets);
        }
        sets[count++] = set;
        return;
    }
    int pivot = -1, score = -1;
    for (set_t candidates = left | done; candidates; candidates &= candidates - 1) {
        int vertex = CTZ(candidates), value = POP(comp[vertex] & left);
        if (value > score) {
            score = value;
            pivot = vertex;
        }
    }
    for (set_t extra = left & ~comp[pivot]; extra; extra &= extra - 1) {
        int vertex = CTZ(extra);
        maximal(set | BIT(vertex), left & comp[vertex], done & comp[vertex]);
        left &= ~BIT(vertex);
        done |= BIT(vertex);
    }
}

static int complete(int depth, int start)
{
    ++nodes;
    set_t *domain = domains + (size_t)depth * words;
    for (int word = start / 64; word < words; ++word) {
        for (set_t available = domain[word]; available; available &= available - 1) {
            int idx = 64 * word + CTZ(available);
            set_t chosen = sets[idx];
            int size = 1 << depth, valid = 1;
            for (int mask = 0; mask < size; ++mask) {
                unions[mask | size] = unions[mask] | chosen;
                if (POP(mask) >= 2 && has_indep(core.adj, full & ~unions[mask | size],
                                               independence - POP(mask))) {
                    valid = 0;
                    break;
                }
            }
            if (!valid) continue;
            picked[depth] = chosen;
            if (depth + 1 == columns) return 1;
            set_t *next = domain + words;
            const set_t *row = compat + (size_t)idx * words;
            set_t any = 0;
            for (int suffix = word; suffix < words; ++suffix) {
                next[suffix] = domain[suffix] & row[suffix];
                any |= next[suffix];
            }
            if (any && complete(depth + 1, idx)) return 1;
        }
    }
    return 0;
}

static int survives(void)
{
    full = BIT(core.n) - 1;
    for (int vertex = 0; vertex < core.n; ++vertex)
        comp[vertex] = full & ~(core.adj[vertex] | BIT(vertex));
    count = 0;
    maximal(0, full, 0);
    words = (count + 63) / 64;
    compat = malloc((size_t)count * words * sizeof(*compat));
    domains = calloc((size_t)columns * words, sizeof(*domains));
    assert(compat && domains);
    for (int idx = 0; idx < count; ++idx) domains[idx / 64] |= BIT(idx % 64);
    for (int idx = 0; idx < count; ++idx) {
        set_t *row = compat + (size_t)idx * words;
        memcpy(row, domains, (size_t)words * sizeof(*row));
        row[idx / 64] &= ~(BIT(idx % 64) - 1);
    }
    set_t *avoids = malloc((size_t)count * sizeof(*avoids));
    assert(avoids);
    for (int test = 0; test < count; ++test) {
        if (POP(sets[test]) != independence - 1) continue;
        int found = 0;
        set_t test_set = sets[test];
        for (int idx = 0; idx < count; ++idx)
            if (!(sets[idx] & test_set)) avoids[found++] = (set_t)idx;
        for (int first = 0; first < found; ++first) {
            set_t *row = compat + avoids[first] * words;
            for (int second = first; second < found; ++second) {
                set_t idx = avoids[second];
                row[idx / 64] &= ~BIT(idx % 64);
            }
        }
        pair_rows += found;
    }
    int result = complete(0, 0);
    if (result) {
        graph_t witness = core;
        witness.n += columns + 1;
        int root = witness.n - 1;
        for (int index = 0; index < columns; ++index) {
            int vertex = core.n + index;
            witness.adj[root] |= BIT(vertex);
            witness.adj[vertex] = picked[index] | BIT(root);
            for (set_t mask = picked[index]; mask; mask &= mask - 1)
                witness.adj[CTZ(mask)] |= BIT(vertex);
        }
        assert(g_trianglefree(&witness) && alpha_le(&witness, independence));
        if (emit_witness) g6_write(stdout, &witness);
    }
    free(avoids);
    free(compat);
    free(domains);
    return result;
}

int main(int argc, char **argv)
{
    if (argc < 3 || argc > 4 || (argc == 4 && strcmp(argv[3], "--witness"))) return 2;
    emit_witness = argc == 4;
    independence = atoi(argv[1]);
    columns = atoi(argv[2]);
    if (columns < 1 || columns > 15 || columns > independence) return 2;
    char line[4096];
    long long inputs = 0, outputs = 0;
    clock_t begin = clock();
    while (fgets(line, sizeof(line), stdin)) {
        if (g6_read(line, &core) || core.n + columns + 1 > 62 ||
            !g_trianglefree(&core) || !alpha_le(&core, independence - 1)) return 3;
        ++inputs;
        if (survives()) {
            if (!emit_witness) fputs(line, stdout);
            ++outputs;
        }
    }
    fprintf(stderr, "in=%lld out=%lld nodes=%lld pair_rows=%lld cpu=%.3f s\n", inputs, outputs,
            nodes, pair_rows, (double)(clock() - begin) / CLOCKS_PER_SEC);
    free(sets);
    return ferror(stdin) || fflush(stdout);
}
