#include "gutil.h"

#include <algorithm>
#include <cstdio>
#include <random>
#include <vector>

struct Choice { int first, second; };

static void toggle_edge(graph_t &graph, Choice edge)
{
    graph.adj[edge.first] ^= BIT(edge.second);
    graph.adj[edge.second] ^= BIT(edge.first);
}

static bool descend(graph_t &graph, int alpha, std::mt19937_64 &rng)
{
    std::vector<Choice> choices;
    for (int first = 0; first < graph.n; ++first)
        for (set_t tail = graph.adj[first] & ~(BIT(first + 1) - 1); tail; tail &= tail - 1)
            choices.push_back({first, CTZ(tail)});
    std::shuffle(choices.begin(), choices.end(), rng);
    for (Choice edge : choices) {
        set_t exterior = (BIT(graph.n) - 1) & ~(graph.adj[edge.first] | graph.adj[edge.second]);
        if (has_indep(graph.adj, exterior, alpha - 1)) continue;
        toggle_edge(graph, edge);
        return true;
    }
    return false;
}

static bool ascend(graph_t &graph, std::mt19937_64 &rng)
{
    std::vector<Choice> choices;
    for (int first = 0; first < graph.n; ++first)
        for (int second = first + 1; second < graph.n; ++second)
            if (!(graph.adj[first] & (graph.adj[second] | BIT(second)))) choices.push_back({first, second});
    if (choices.empty()) return false;
    toggle_edge(graph, choices[rng() % choices.size()]);
    return true;
}

int main(int argc, char **argv)
{
    if (argc != 7) return 2;
    int alpha = std::atoi(argv[1]), min_output = std::atoi(argv[2]), max_output = std::atoi(argv[3]);
    int up_steps = std::atoi(argv[4]), trials = std::atoi(argv[5]);
    if (alpha < 2 || alpha > 62 || min_output < 0 || max_output < min_output || up_steps < 1 || trials < 1) return 2;
    std::mt19937_64 rng(std::strtoull(argv[6], nullptr, 10));
    char line[4096];
    long seed = 0, lines = 0;
    while (std::fgets(line, sizeof line, stdin)) {
        graph_t source;
        if (g6_read(line, &source) || !g_trianglefree(&source) || !alpha_le(&source, alpha)) return 2;
        int start_edges = g_edges(&source);
        for (int trial = 0; trial < trials; ++trial) {
            graph_t walk = source;
            int edges = start_edges;
            int steps = up_steps;
            while (steps-- && ascend(walk, rng)) ++edges;
            while (edges >= min_output) {
                if (edges <= max_output) { g6_write(stdout, &walk); ++lines; }
                if (!descend(walk, alpha, rng)) break;
                --edges;
            }
        }
        ++seed;
    }
    std::fprintf(stderr, "seeds=%ld trials/seed=%d output=%ld upward=%d\n", seed, trials, lines, up_steps);
    return std::ferror(stdin) || std::ferror(stdout) ? 2 : 0;
}
