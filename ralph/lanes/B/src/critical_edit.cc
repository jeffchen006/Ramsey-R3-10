#include "gutil.h"

#include <algorithm>
#include <array>
#include <cstdio>
#include <vector>

struct Edge {
    int tail, head;
    set_t mask() const { return BIT(tail) | BIT(head); }
    int index() const { return 64 * tail + head; }
};

using Masks = std::vector<set_t>;

static void toggle(graph_t &graph, Edge edge)
{
    graph.adj[edge.tail] ^= BIT(edge.head);
    graph.adj[edge.head] ^= BIT(edge.tail);
}

static void collect(const graph_t &graph, set_t allowed, set_t chosen, int need, Masks &found)
{
    if (!need) {
        found.push_back(chosen);
        return;
    }
    while (POP(allowed) >= need) {
        int vertex = CTZ(allowed);
        allowed &= allowed - 1;
        collect(graph, allowed & ~graph.adj[vertex], chosen | BIT(vertex), need - 1, found);
    }
}

static void containing(const graph_t &graph, set_t forced, int size, Masks &found)
{
    set_t allowed = (BIT(graph.n) - 1) & ~forced;
    for (set_t left = forced; left; left &= left - 1) {
        set_t neighbours = graph.adj[CTZ(left)];
        if (neighbours & forced) return;
        allowed &= ~neighbours;
    }
    collect(graph, allowed, forced, size - POP(forced), found);
}

struct Edit {
    const graph_t &source;
    graph_t graph;
    int alpha, min_degree, add_count;
    std::array<bool, 4096> banned{};
    std::array<set_t, 3> punctures{};
    std::array<set_t, 4> trail{};
    const Masks *initial = nullptr;
    long outputs = 0;

    bool available(Edge edge) const
    {
        return !banned[edge.index()] && !(source.adj[edge.tail] & BIT(edge.head))
            && !(graph.adj[edge.tail] & BIT(edge.head)) && !(graph.adj[edge.tail] & graph.adj[edge.head])
            && POP(graph.adj[edge.tail]) < alpha && POP(graph.adj[edge.head]) < alpha;
    }

    int deficit() const
    {
        int total = 0;
        for (int vertex = 0; vertex < graph.n; ++vertex)
            total += std::max(0, min_degree - POP(graph.adj[vertex]));
        return total;
    }

    bool reaches_forced_size(set_t forced) const
    {
        set_t allowed = (BIT(graph.n) - 1) & ~forced;
        for (set_t left = forced; left; left &= left - 1) {
            set_t neighbours = graph.adj[CTZ(left)];
            if (neighbours & forced) return false;
            allowed &= ~neighbours;
        }
        return has_indep(graph.adj, allowed, alpha + 1 - POP(forced));
    }

    void emit() {
        if (punctures[2] && (reaches_forced_size(punctures[0] | punctures[1])
                          || reaches_forced_size(punctures[0] | punctures[2])
                          || reaches_forced_size(punctures[1] | punctures[2]))) return;
        unsigned int private_edges = 0;
        for (set_t witness : *initial) {
            unsigned int covered = 0;
            for (int index = 0; index < add_count; ++index)
                if ((witness & trail[index]) == trail[index]) covered |= 1u << index;
            if (covered && !(covered & (covered-1))) private_edges |= covered;
        }
        if (private_edges != (1u << add_count)-1) return;
        set_t all = BIT(graph.n)-1;
        for (int tail = 0; tail < graph.n; ++tail)
            for (set_t left = graph.adj[tail] & (BIT(tail)-1); left; left &= left-1) {
                int head = CTZ(left);
                if (!has_indep(graph.adj, all & ~(graph.adj[head] | graph.adj[tail]), alpha-1)) return;
            }
        ++outputs;
        g6_write(stdout, &graph);
    }

    void search(int depth, const Masks &witnesses)
    {
        if (!depth) initial = &witnesses;
        if (witnesses.empty()) return;
        int needed = add_count - depth;
        if (!needed || deficit() > 2 * needed) return;
        set_t tips = witnesses.front();
        if (needed == 1) {
            for (set_t witness : witnesses) tips &= witness;
            if (POP(tips) < 2) return;
        }
        std::array<Edge, 2016> changes;
        int count = 0;
        for (; tips; tips &= tips - 1) {
            int tail = CTZ(tips);
            for (set_t rest = tips & (tips - 1); rest; rest &= rest - 1) {
                Edge edge{tail, CTZ(rest)};
                if (!available(edge)) continue;
                trail[depth] = edge.mask();
                toggle(graph, edge);
                if (needed == 1) {
                    if (!deficit()) emit();
                } else {
                    Masks remaining;
                    set_t mask = edge.mask();
                    for (set_t witness : witnesses)
                        if ((witness & mask) != mask) remaining.push_back(witness);
                    search(depth + 1, remaining);
                }
                toggle(graph, edge);
                banned[edge.index()] = true;
                changes[count++] = edge;
            }
        }
        for (int index = 0; index < count; ++index)
            banned[changes[index].index()] = false;
    }

    bool quick_reject(const Masks &first, const Masks &second) const
    {
        if (add_count != 1) return false;
        set_t possible = BIT(graph.n) - 1;
        for (const Masks *group : {&first, &second})
            for (set_t witness : *group) {
                possible &= witness;
                if (POP(possible) < 2) return true;
            }
        for (set_t left = possible; left; left &= left - 1)
            for (set_t right = left & (left - 1); right; right &= right - 1)
                if (available({CTZ(left), CTZ(right)})) return false;
        return true;
    }
};

int main(int argc, char **argv)
{
    if (argc != 5) return 2;
    int alpha = std::atoi(argv[1]), min_degree = std::atoi(argv[2]);
    int removals = std::atoi(argv[3]), additions = std::atoi(argv[4]);
    if (alpha < 3 || alpha > 62 || min_degree < 0 || min_degree > alpha
        || removals != 2 || additions < 1 || additions > 4) return 2;
    char line[4096];
    long tag = 0;
    while (std::fgets(line, sizeof(line), stdin)) {
        graph_t source;
        if (g6_read(line, &source) || !g_trianglefree(&source) || !alpha_le(&source, alpha)) return 2;
        Edit edit{source, source, alpha, min_degree, additions};
        std::vector<Edge> edges;
        std::vector<Masks> cache;
        for (int tail = 0; tail < source.n; ++tail)
            for (int head = tail + 1; head < source.n; ++head) {
                Edge edge{tail, head};
                if (!(source.adj[tail] & BIT(head))) continue;
                edges.push_back(edge);
                cache.emplace_back();
                toggle(edit.graph, edge);
                containing(edit.graph, edge.mask(), alpha + 1, cache.back());
                toggle(edit.graph, edge);
            }
        for (size_t first = 0; first < edges.size(); ++first) {
            const Edge old = edges[first];
            toggle(edit.graph, old);
            if (removals == 1) edit.search(0, cache[first]);
            else for (size_t second = first + 1; second < edges.size(); ++second) {
                const Edge other = edges[second];
                toggle(edit.graph, other);
                if (removals == 3) {
                    edit.punctures[0] = old.mask();
                    edit.punctures[1] = other.mask();
                    Masks witnesses = cache[first];
                    witnesses.insert(witnesses.end(), cache[second].begin(), cache[second].end());
                    const size_t pair_size = witnesses.size();
                    for (size_t third = second + 1; third < edges.size(); ++third) {
                        const Edge last = edges[third];
                        toggle(edit.graph, last);
                        if (edit.deficit() <= 2 * additions) {
                            edit.punctures[2] = last.mask();
                            witnesses.insert(witnesses.end(), cache[third].begin(), cache[third].end());
                            edit.search(0, witnesses);
                            witnesses.resize(pair_size);
                        }
                        toggle(edit.graph, last);
                    }
                } else if (edit.deficit() <= 2 * additions && !edit.quick_reject(cache[first], cache[second])) {
                    Masks witnesses = cache[first];
                    witnesses.insert(witnesses.end(), cache[second].begin(), cache[second].end());
                    containing(edit.graph, old.mask() | other.mask(), alpha + 1, witnesses);
                    edit.search(0, witnesses);
                }
                toggle(edit.graph, other);
            }
            toggle(edit.graph, old);
        }
        std::fprintf(stderr, "%ld e=%d outputs=%ld\n", ++tag, g_edges(&source), edit.outputs);
    }
    return std::ferror(stdin) || std::ferror(stdout) ? 2 : 0;
}
