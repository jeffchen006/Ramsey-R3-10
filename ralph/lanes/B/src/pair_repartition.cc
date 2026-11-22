#include "gutil.h"

#include <algorithm>
#include <array>
#include <vector>

class Repartition {
    graph_t original{}, stem{};
    set_t full{}, pair{}, stem_vertices{}, old_union{};
    int alpha, increment, expand, left{}, right{};
    long long inputs{}, pairs{}, models{}, valid{}, critical{};
    std::vector<set_t> independent, hits;
    std::vector<std::array<set_t, 2>> components;

    void collect(set_t allowed, set_t chosen, int need)
    {
        if (!need) {
            independent.push_back(chosen);
            return;
        }
        while (POP(allowed) >= need) {
            int vertex = CTZ(allowed);
            allowed &= allowed - 1;
            collect(allowed & ~original.adj[vertex], chosen | BIT(vertex), need - 1);
        }
    }

    bool is_critical(const graph_t &graph) const
    {
        for (int vertex = 0; vertex < graph.n; ++vertex) {
            for (set_t edges = graph.adj[vertex] & (BIT(vertex)-1); edges; edges &= edges-1) {
                int other = CTZ(edges);
                if (!has_indep(graph.adj, full & ~(graph.adj[vertex] | graph.adj[other]), alpha-1))
                    return false;
            }
        }
        return true;
    }

    void emit(set_t first, set_t second)
    {
        ++models;
        for (set_t hit : hits)
            if (!(hit & first) || !(hit & second)) return;
        ++valid;
        graph_t graph = stem;
        graph.adj[left] = first;
        graph.adj[right] = second;
        for (set_t rest = first; rest; rest &= rest-1) graph.adj[CTZ(rest)] |= BIT(left);
        for (set_t rest = second; rest; rest &= rest-1) graph.adj[CTZ(rest)] |= BIT(right);
        if (!is_critical(graph)) return;
        ++critical;
        g6_write(stdout, &graph);
    }

    void assign_isolated(set_t isolated, int overlap, set_t first, set_t second)
    {
        if (overlap < 0 || overlap > POP(isolated) || POP(first) > alpha || POP(second) > alpha)
            return;
        if (overlap == POP(isolated)) {
            if (POP(first | isolated) <= alpha && POP(second | isolated) <= alpha)
                emit(first | isolated, second | isolated);
            return;
        }
        set_t next = isolated & -isolated;
        isolated ^= next;
        assign_isolated(isolated, overlap, first | next, second);
        assign_isolated(isolated, overlap, first, second | next);
        if (overlap) assign_isolated(isolated, overlap-1, first | next, second | next);
    }

    void orient(size_t index, set_t isolated, int overlap, set_t first, set_t second)
    {
        if (POP(first) + overlap > alpha || POP(second) + overlap > alpha) return;
        if (index == components.size()) {
            assign_isolated(isolated, overlap, first, second);
            return;
        }
        auto sides = components[index];
        orient(index+1, isolated, overlap, first | sides[0], second | sides[1]);
        orient(index+1, isolated, overlap, first | sides[1], second | sides[0]);
    }

    void try_union(set_t vertices, int overlap)
    {
        if (overlap < 0 || POP(vertices) + overlap > 2*alpha) return;
        set_t isolated = 0;
        components.clear();
        for (set_t pending = vertices; pending;) {
            int start = CTZ(pending);
            pending ^= BIT(start);
            if (!(stem.adj[start] & vertices)) {
                isolated |= BIT(start);
                continue;
            }
            std::array<set_t, 2> sides{BIT(start), 0};
            set_t frontier = BIT(start);
            while (frontier) {
                int vertex = CTZ(frontier);
                frontier &= frontier-1;
                int side = !(sides[0] & BIT(vertex));
                set_t neighbors = stem.adj[vertex] & vertices;
                if (neighbors & sides[side]) return;
                set_t unseen = neighbors & pending;
                sides[1-side] |= unseen;
                pending &= ~unseen;
                frontier |= unseen;
            }
            components.push_back(sides);
        }
        if (POP(isolated) < overlap) return;
        hits.clear();
        set_t forced = 0;
        for (set_t mask : independent) {
            if (mask & pair) continue;
            set_t hit = mask & vertices;
            if (!hit) return;
            if (!(hit & (hit-1))) forced |= hit;
            hits.push_back(hit);
        }
        if ((forced & ~isolated) || POP(forced) > overlap) return;
        hits.erase(std::remove_if(hits.begin(), hits.end(), [forced](set_t hit) {
            return hit & forced;
        }), hits.end());
        orient(0, isolated & ~forced, overlap-POP(forced), forced, forced);
    }

public:
    Repartition(int bound, int plus, int widen) : alpha(bound), increment(plus), expand(widen) {}

    bool run(const char *line)
    {
        int order = line[0]-63;
        if (order < 2 || order > 62 || strlen(line) != size_t(2+(order*(order-1)/2+5)/6) ||
            g6_read(line, &original) || !g_trianglefree(&original) || !alpha_le(&original, alpha))
            return false;
        ++inputs;
        full = BIT(order)-1;
        independent.clear();
        collect(full, 0, alpha);
        for (left = 0; left < order; ++left) {
            for (right = left+1; right < order; ++right) {
                if (original.adj[left] & BIT(right)) continue;
                ++pairs;
                pair = BIT(left) | BIT(right);
                stem_vertices = full ^ pair;
                stem = original;
                stem.adj[left] = stem.adj[right] = 0;
                old_union = original.adj[left] | original.adj[right];
                for (set_t rest = old_union; rest; rest &= rest-1) stem.adj[CTZ(rest)] &= ~pair;
                int overlap = POP(original.adj[left] & original.adj[right]) + increment;
                try_union(old_union, overlap);
                if (expand && overlap > 0) {
                    for (set_t rest = stem_vertices & ~old_union; rest; rest &= rest-1)
                        try_union(old_union | (rest & -rest), overlap-1);
                }
            }
        }
        return true;
    }

    void report() const
    {
        fprintf(stderr, "repartition inputs=%lld pairs=%lld models=%lld valid=%lld critical=%lld\n",
                inputs, pairs, models, valid, critical);
    }
};

int main(int argc, char **argv)
{
    if (argc != 4) return 2;
    int alpha = atoi(argv[1]), increment = atoi(argv[2]), expand = atoi(argv[3]);
    if (alpha < 2 || alpha > 9 || increment < 0 || increment > 1 || expand < 0 || expand > 1) return 2;
    Repartition generate(alpha, increment, expand);
    char line[1024];
    while (fgets(line, sizeof(line), stdin))
        if (!generate.run(line)) return 1;
    generate.report();
    return ferror(stdin) || fflush(stdout) == EOF;
}
