#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

#include <cadical.hpp>

using Mask = std::uint32_t;
using Graph = std::vector<Mask>;
using Clause = std::vector<int>;

Mask bit(int vertex) { return Mask{1} << vertex; }

Graph decode(const std::string &line) {
    if (line.empty() || line[0] < '?' || line[0] > '^') throw std::runtime_error("bad core order");
    const int order = line[0] - '?';
    const int length = order * (order - 1) / 2;
    if (line.size() != static_cast<std::size_t>(1 + (length + 5) / 6))
        throw std::runtime_error("bad graph6 length");
    Graph result(order);
    for (int right = 0, index = 0; right < order; ++right)
        for (int left = 0; left < right; ++left, ++index)
            if (((line[1 + index / 6] - '?') >> (5 - index % 6)) & 1) {
                result[left] |= bit(right);
                result[right] |= bit(left);
            }
    return result;
}

bool linked(const Graph &graph, int left, int right) { return graph[left] & bit(right); }

std::string encode(const Graph &fixed, const std::vector<Mask> &groups, bool full) {
    const int order = fixed.size();
    const int pairs = groups.size();
    const int size = order + (full ? 2 * pairs : 0);
    std::string result(1, '?' + size);
    for (int right = 0, index = 0; right < size; ++right)
        for (int left = 0; left < right; ++left, ++index) {
            if (index % 6 == 0) result += '?';
            const bool edge = right < order ? linked(fixed, left, right)
                            : left < order ? (groups[(right - order) % pairs] & bit(left)) != 0
                            : (right - order) / pairs != (left - order) / pairs &&
                              (right - left) != pairs;
            if (edge) result.back() += 1 << (5 - index % 6);
        }
    return result;
}

class Crown {
    CaDiCaL::Solver solver;
    const int core_size;
    const int order;
    const int alpha_limit;
    const int moved_side;
    const bool full;
    const bool anchor;
    const bool tighten;
    const bool anchor_sort;
    const Mask universe;
    std::vector<Mask> groups;
    std::vector<int> group_of;
    std::vector<std::pair<int, int>> option;
    std::array<std::array<int, 30>, 30> variable{};
    std::set<Clause> generated;
    int next = 0;
    int visited = 0;
    int added = 0;
    int calls = 0;

    void add(const Clause &row) {
        for (int literal : row) solver.add(literal);
        solver.add(0);
    }

    void at_most(Clause inputs, int limit) {
        if (limit < 0) { add({}); return; }
        if (limit >= static_cast<int>(inputs.size())) return;
        if (!limit) { for (int input : inputs) add({-input}); return; }
        Clause prev(limit);
        for (int input : inputs) {
            Clause row(limit);
            std::generate(row.begin(), row.end(), [&] { return ++next; });
            add({-input, row[0]});
            for (int index = 0; index < limit; ++index) {
                if (prev[index]) add({-prev[index], row[index]});
                if (index && prev[index - 1]) add({-input, -prev[index - 1], row[index]});
            }
            if (prev.back()) add({-input, -prev.back()});
            prev = std::move(row);
        }
    }

    void order_words(const std::vector<std::pair<int, int>> &words) {
        int prefix = 0;
        for (const auto &[left, right] : words) {
            const int equal = ++next;
            Clause ascending{-left, right}, equal_false{left, right, equal}, equal_true{-left, -right, equal};
            if (prefix) {
                ascending.push_back(-prefix);
                equal_false.push_back(-prefix);
                equal_true.push_back(-prefix);
            }
            add(ascending);
            add(equal_false);
            add(equal_true);
            prefix = equal;
        }
    }

    void cut(Mask picked) {
        Clause row;
        for (Mask outer = picked; outer; outer &= outer - 1) {
            const int upper = std::countr_zero(outer);
            for (Mask inner = outer & (outer - 1); inner; inner &= inner - 1) {
                const int lower = std::countr_zero(inner);
                if (variable[lower][upper]) row.push_back(variable[lower][upper]);
            }
        }
        std::sort(row.begin(), row.end());
        if (generated.insert(row).second) {
            if (std::getenv("CROWN_TRACE")) std::cout << "CUT " << picked << '\n';
            add(row);
            ++added;
        }
    }

    int cost(int vertex, Mask hit) const {
        return group_of[vertex] < 0 || (hit & bit(group_of[vertex])) ? 1 : 0;
    }

    int upper(Mask pending, Mask hit) const {
        int result = std::popcount(pending);
        for (std::size_t index = 0; index < groups.size(); ++index)
            if (!(hit & bit(index)) && (pending & groups[index])) --result;
        return result;
    }

    void sweep(const Graph &graph, Mask pending, Mask picked, Mask hit,
               int need, int max_size, bool weighted, int budget) {
        if (added >= budget) return;
        ++visited;
        if (need <= 0) { cut(picked); return; }
        if (max_size < need) return;
        while (pending && added < budget) {
            if ((weighted ? upper(pending, hit) : std::popcount(pending)) < need) return;
            const int vertex = std::countr_zero(pending);
            pending ^= bit(vertex);
            const Mask next_hit = group_of[vertex] < 0 ? hit : hit | bit(group_of[vertex]);
            sweep(graph, pending & ~graph[vertex], picked | bit(vertex), next_hit,
                  need - (weighted ? cost(vertex, hit) : 1), max_size - 1, weighted, budget);
        }
    }

public:
    Crown(const Graph &core, const std::vector<int> &sizes, int bound, int side,
          bool include_pairs, bool is_anchor, bool constrained, bool symmetry, int seed, bool tight,
          std::size_t clean, bool sort_anchor, bool seed_pairs)
        : core_size(core.size()), order(core.size() + std::accumulate(sizes.begin(), sizes.end(), 0)),
          alpha_limit(bound), moved_side(side), full(include_pairs), anchor(is_anchor), tighten(tight),
          anchor_sort(sort_anchor), universe(bit(order) - 1),
          group_of(order, -1) {
        if (order >= 30 || side > 10 || side > bound || (full && side != static_cast<int>(sizes.size())))
            throw std::runtime_error("invalid crown shape");
        int start = core_size;
        for (int size : sizes) {
            if (size <= 0) throw std::runtime_error("empty attachment");
            groups.push_back(((bit(size) - 1) << start));
            for (int vertex = start; vertex < start + size; ++vertex) group_of[vertex] = groups.size() - 1;
            start += size;
        }
        for (int right = core_size; right < order; ++right)
            for (int left = 0; left < right; ++left)
                if (group_of[left] != group_of[right]) {
                    option.emplace_back(left, right);
                    variable[left][right] = variable[right][left] = ++next;
                }
        if (clean > groups.size()) throw std::runtime_error("too many pinned clean groups");
        for (std::size_t group = 0; group < clean; ++group) {
            if (sizes[group] != core_size) throw std::runtime_error("clean group/cardinality mismatch");
            int start = std::countr_zero(groups[group]);
            for (int column = 0; column < core_size; ++column)
                for (int fixed = 0; fixed < core_size; ++fixed)
                    add({(column + fixed == core_size - 1 ? 1 : -1) * variable[fixed][start + column]});
        }
        for (int last = 0; last < order; ++last)
            for (int mid = 0; mid < last; ++mid)
                for (int first = 0; first < mid; ++first) {
                    Clause row;
                    bool possible = true;
                    for (const auto &[left, right] : {std::pair{first, mid}, {first, last}, {mid, last}}) {
                        if (right < core_size && linked(core, left, right)) continue;
                        if (variable[left][right]) row.push_back(-variable[left][right]);
                        else possible = false;
                    }
                    if (possible) add(row);
                }
        if (constrained) {
            for (int vertex = 0; vertex < order; ++vertex) {
                Clause edges;
                for (int other = 0; other < order; ++other)
                    if (variable[vertex][other]) edges.push_back(variable[vertex][other]);
                const int pinned = vertex < core_size ? std::popcount(core[vertex]) : 2;
                const int limit = vertex < core_size ? (anchor ? 7 : tighten ? 8 : 9) - pinned : 7;
                at_most(edges, limit);
                if (full && pinned < 4) {
                    for (int &literal : edges) literal = -literal;
                    at_most(edges, static_cast<int>(edges.size()) - (4 - pinned));
                }
            }
        }
        if (symmetry) {
            int offset = core_size;
            for (int size : sizes) {
                for (int vertex = offset; vertex + 1 < offset + size; ++vertex) {
                    std::vector<std::pair<int, int>> words;
                    for (int fixed = 0; fixed < core_size; ++fixed)
                        words.emplace_back(variable[fixed][vertex], variable[fixed][vertex + 1]);
                    order_words(words);
                }
                offset += size;
            }
            for (std::size_t index = 1; index < groups.size(); ++index) {
                if (index == clean || sizes[index - 1] != sizes[index]) continue;
                std::vector<std::pair<int, int>> words;
                const int left = std::countr_zero(groups[index - 1]);
                const int right = std::countr_zero(groups[index]);
                for (int vertex = 0; vertex < sizes[index]; ++vertex)
                    for (int fixed = 0; fixed < core_size; ++fixed)
                        words.emplace_back(variable[fixed][left + vertex], variable[fixed][right + vertex]);
                if (anchor_sort && index >= 2 && clean) {
                    const int ref = std::countr_zero(groups.front());
                    for (int fixed = ref; fixed < ref + sizes.front(); ++fixed)
                        for (int vertex = 0; vertex < sizes[index]; ++vertex)
                            words.emplace_back(variable[fixed][left + vertex], variable[fixed][right + vertex]);
                }
                order_words(words);
            }
        }
        if (seed) {
            Graph graph(order);
            for (int vertex = 0; vertex < core_size; ++vertex) graph[vertex] = core[vertex];
            sweep(graph, universe, 0, 0, bound + 1 - side, seed, true, 1000000);
        }
        if (full && seed_pairs && clean == groups.size()) {
            Graph pinned(order);
            for (int vertex = 0; vertex < core_size; ++vertex) pinned[vertex] = core[vertex];
            for (Mask group : groups) {
                const int start = std::countr_zero(group);
                for (int fixed = 0; fixed < core_size; ++fixed) {
                    const int attached = start + core_size - 1 - fixed;
                    pinned[fixed] |= bit(attached);
                    pinned[attached] |= bit(fixed);
                }
            }
            for (int first = 0; first < core_size; ++first)
                for (int second = first + 1; second < core_size; ++second)
                    if (!linked(pinned, first, second)) {
                        const Mask chosen = bit(first) | bit(second);
                        const Mask eligible = universe & ~(bit(core_size) - 1) &
                                              ~(pinned[first] | pinned[second]);
                        for (Mask group : groups)
                            sweep(pinned, eligible & ~group, chosen, 0, bound - 3, bound - 3, false, 1000000);
                    }
        }
    }

    int solve(const Graph &core, int iterations, bool enumerate) {
        int models = 0;
        for (; !iterations || calls < iterations; ) {
            ++calls;
            const int status = solver.solve();
            if (status == 20) {
                std::cout << "EXHAUSTED models=" << models << " calls=" << calls << " cuts=" << added
                          << " visits=" << visited << '\n';
                return 0;
            }
            if (status != 10) throw std::runtime_error("unexpected solver status");
            Graph graph(order);
            for (int vertex = 0; vertex < core_size; ++vertex) graph[vertex] = core[vertex];
            Clause no_model;
            for (const auto &[left, right] : option) {
                const int id = variable[left][right];
                const bool value = solver.val(id) > 0;
                no_model.push_back(value ? -id : id);
                if (value) { graph[left] |= bit(right); graph[right] |= bit(left); }
            }
            const int before = added;
            sweep(graph, universe, 0, 0, alpha_limit + 1 - moved_side, order, true, before + 128);
            if (full)
                for (Mask group : groups)
                    sweep(graph, universe & ~group, 0, 0, alpha_limit - 1, order, false, before + 256);
            if (anchor)
                sweep(graph, universe, 0, 0, alpha_limit - 1, order, false, before + 256);
            if (before == added) {
                ++models;
                std::cout << "MODEL " << encode(graph, groups, full) << " fixed=" << encode(graph, groups, false)
                          << " calls=" << calls << " cuts=" << added << '\n';
                if (!enumerate) return 0;
                add(no_model);
            }
            if (!(calls % 1000)) std::cout << "PROGRESS calls=" << calls << " cuts=" << added << '\n';
        }
        std::cout << "OPEN capped calls=" << calls << " cuts=" << added << '\n';
        return 0;
    }
};

int main(int argc, char **argv) {
    if (argc < 9) {
        std::cerr << "usage: crown_exact CORE_G6 ALPHA SIDE MODE SEED ITERATIONS SYM SIZES...\n"
                  << "MODE: enum, toy, local, full, anchor\n";
        return 2;
    }
    std::cout << std::unitbuf;
    const Graph graph = decode(argv[1]);
    const std::string mode = argv[4];
    if (mode != "enum" && mode != "toy" && mode != "local" && mode != "full" && mode != "anchor") return 2;
    std::vector<int> sizes;
    for (int index = 8; index < argc; ++index) sizes.push_back(std::stoi(argv[index]));
    const bool full = mode != "local" && mode != "anchor";
    const bool constrained = mode == "local" || mode == "full" || mode == "anchor";
    const bool tighten = mode == "full" && graph.size() == 4 && std::getenv("CROWN_TIGHT");
    const std::size_t clean = std::getenv("CROWN_CLEAN") ? std::stoul(std::getenv("CROWN_CLEAN")) : 0;
    Crown instance(graph, sizes, std::stoi(argv[2]), std::stoi(argv[3]), full,
                   mode == "anchor", constrained, std::stoi(argv[7]), std::stoi(argv[5]), tighten, clean,
                   std::getenv("CROWN_ANCHOR_SORT"), std::getenv("CROWN_SEED_PAIRS"));
    return instance.solve(graph, std::stoi(argv[6]), mode == "enum");
}
