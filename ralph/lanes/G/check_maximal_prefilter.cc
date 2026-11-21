#include "gutil.h"
#include <algorithm>
#include <array>
#include <cassert>
#include <ctime>
#include <vector>

using Bits = std::vector<set_t>;
static graph_t core;
static set_t universe;
static int alpha_limit, columns;
static bool emit_all;
static long long maximal_gluings, trimmed_gluings;
static Bits maximal_sets, critical_sets;
static std::vector<Bits> compatible;
static std::array<set_t, 16> chosen;

static void collect(set_t selected, set_t candidates, set_t dominated)
{
    int size = POP(selected);
    if (size == alpha_limit) critical_sets.push_back(selected);
    if (dominated == universe) {
        maximal_sets.push_back(selected);
        return;
    }
    assert(size <= alpha_limit);
    while (candidates) {
        int vertex = CTZ(candidates);
        candidates ^= BIT(vertex);
        collect(selected | BIT(vertex), candidates & ~core.adj[vertex],
                dominated | BIT(vertex) | core.adj[vertex]);
    }
}

static bool contains_independent(set_t candidates, int size)
{
    while (POP(candidates) >= size) {
        if (size <= 1) return true;
        int vertex = CTZ(candidates);
        candidates ^= BIT(vertex);
        if (contains_independent(candidates & ~core.adj[vertex], size - 1)) return true;
    }
    return false;
}

static void emit_trimmed(graph_t &graph, const std::vector<std::pair<int, int>> &cross, size_t start)
{
    for (int vertex = 0; vertex < graph.n; ++vertex)
        if (POP(graph.adj[vertex]) < columns) return;
    g6_write(stdout, &graph);
    ++trimmed_gluings;
    for (size_t index = start; index < cross.size(); ++index) {
        auto [inner, outer] = cross[index];
        if (POP(graph.adj[inner]) <= columns || POP(graph.adj[outer]) <= columns) continue;
        graph.adj[inner] ^= BIT(outer);
        graph.adj[outer] ^= BIT(inner);
        if (alpha_le(&graph, alpha_limit + 1)) emit_trimmed(graph, cross, index + 1);
        graph.adj[inner] ^= BIT(outer);
        graph.adj[outer] ^= BIT(inner);
    }
}

static void emit()
{
    graph_t graph = core;
    graph.n += columns + 1;
    int root = graph.n - 1;
    std::vector<std::pair<int, int>> cross;
    for (int column = 0; column < columns; ++column) {
        int outer = core.n + column;
        graph.adj[root] |= BIT(outer);
        graph.adj[outer] = BIT(root) | chosen[column];
        for (set_t mask = chosen[column]; mask; mask &= mask - 1) {
            int inner = CTZ(mask);
            graph.adj[inner] |= BIT(outer);
            cross.emplace_back(inner, outer);
        }
    }
    assert(g_trianglefree(&graph) && alpha_le(&graph, alpha_limit + 1));
    ++maximal_gluings;
    emit_trimmed(graph, cross, 0);
}

static bool solve(int depth, const Bits &domain)
{
    bool survives = false;
    for (size_t word = 0; word < domain.size(); ++word) {
        for (set_t options = domain[word]; options; options &= options - 1) {
            size_t index = word * 64 + CTZ(options);
            set_t attachment = maximal_sets[index];
            bool passes = true;
            for (int mask = 1; mask < (1 << depth); ++mask) {
                int subset_size = __builtin_popcount(mask);
                if (subset_size < 2) continue;
                set_t touched = attachment;
                for (int bits = mask; bits; bits &= bits - 1)
                    touched |= chosen[__builtin_ctz(bits)];
                if (contains_independent(universe & ~touched, alpha_limit + 1 - subset_size)) {
                    passes = false;
                    break;
                }
            }
            if (!passes) continue;
            chosen[depth] = attachment;
            if (depth + 1 == columns) {
                if (!emit_all) return true;
                emit();
                survives = true;
                continue;
            }
            Bits next(domain.size());
            for (size_t block = word; block < domain.size(); ++block)
                next[block] = domain[block] & compatible[index][block];
            if (solve(depth + 1, next)) {
                if (!emit_all) return true;
                survives = true;
            }
        }
    }
    return survives;
}

static bool extendable()
{
    universe = BIT(core.n) - 1;
    if (!g_trianglefree(&core) || contains_independent(universe, alpha_limit + 1)) abort();
    maximal_sets.clear();
    critical_sets.clear();
    collect(0, universe, 0);
    size_t count = maximal_sets.size(), words = (count + 63) / 64;
    Bits hits((critical_sets.size() + 63) / 64);
    std::vector<Bits> avoid(count, hits);
    for (size_t index = 0; index < count; ++index)
        for (size_t witness = 0; witness < critical_sets.size(); ++witness)
            if (!(maximal_sets[index] & critical_sets[witness]))
                avoid[index][witness / 64] |= BIT(witness % 64);
    compatible.assign(count, Bits(words));
    for (size_t first = 0; first < count; ++first) {
        for (size_t second = first; second < count; ++second) {
            bool passes = true;
            for (size_t word = 0; word < hits.size(); ++word) {
                if (avoid[first][word] & avoid[second][word]) {
                    passes = false;
                    break;
                }
            }
            if (passes) compatible[first][second / 64] |= BIT(second % 64);
        }
    }
    Bits domain(words);
    for (size_t index = 0; index < count; ++index) domain[index / 64] |= BIT(index % 64);
    return solve(0, domain);
}

int main(int argc, char **argv)
{
    if (argc < 3 || argc > 4 || (argc == 4 && strcmp(argv[3], "--emit-all"))) return 2;
    emit_all = argc == 4;
    alpha_limit = atoi(argv[1]) - 1;
    columns = atoi(argv[2]);
    if (columns < 1 || columns > 15 || columns > alpha_limit + 1) return 2;
    char line[4096];
    long long inputs = 0, outputs = 0;
    clock_t begin = clock();
    while (fgets(line, sizeof(line), stdin)) {
        if (g6_read(line, &core) || core.n + columns + 1 > 62) return 3;
        ++inputs;
        if (extendable()) {
            if (!emit_all) fputs(line, stdout);
            ++outputs;
        }
    }
    fprintf(stderr, "in=%lld out=%lld maximal=%lld trimmed=%lld cpu=%.3f s\n", inputs, outputs,
            maximal_gluings, trimmed_gluings, (double)(clock() - begin) / CLOCKS_PER_SEC);
    return ferror(stdin) || fflush(stdout);
}
