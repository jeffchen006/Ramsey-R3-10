#include <algorithm>
#include <bit>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

using Mask = std::uint32_t;
using Graph = std::vector<Mask>;

static Graph decode(const std::string& line) {
    const int order = line.at(0) - 63;
    assert(order > 0 && order <= 22 && line.size() == 1 + (order * (order - 1) / 2 + 5u) / 6);
    Graph graph(order);
    int bit = 0;
    for (int high = 1; high < order; ++high) {
        for (int low = 0; low < high; ++low, ++bit) {
            if (((line[1 + bit / 6] - 63) >> (5 - bit % 6)) & 1) {
                graph[high] |= Mask(1) << low;
                graph[low] |= Mask(1) << high;
            }
        }
    }
    return graph;
}

static Mask all(const Graph& graph) {
    return (Mask(1) << graph.size()) - 1;
}

static bool independent(const Graph& graph, Mask mask) {
    for (Mask todo = mask; todo; todo &= todo - 1)
        if (graph[std::countr_zero(todo)] & mask) return false;
    return true;
}

static void independent_sets(const Graph& graph, Mask available, int size, Mask chosen,
                             std::vector<Mask>& sets) {
    if (size == 0) {
        sets.push_back(chosen);
        return;
    }
    while (std::popcount(available) >= size) {
        int vertex = std::countr_zero(available);
        Mask bit = Mask(1) << vertex;
        available ^= bit;
        independent_sets(graph, available & ~graph[vertex], size - 1, chosen | bit, sets);
    }
}

struct WingRules {
    std::vector<int> support_upper;
    Mask singletons = 0;
    int singleton_slack;
};

static WingRules wing_rules(const Graph& graph, Mask common, Mask core, int cap, int surplus) {
    WingRules rules{std::vector<int>(graph.size()), 0, surplus};
    for (Mask todo = core; todo; todo &= todo - 1) {
        int vertex = std::countr_zero(todo);
        int support = std::popcount(graph[vertex] & common);
        assert(support >= 1);
        rules.support_upper[vertex] = cap - 1 - support;
        if (support == 1) rules.singletons |= Mask(1) << vertex;
        rules.singleton_slack -= std::max(0, support - 2);
    }
    return rules;
}

static bool admissible(const Graph& graph, Mask first, Mask second, Mask third,
                       int total_degree, const WingRules* rules) {
    Mask used = first | second | third;
    if (rules && std::popcount(rules->singletons & ~used) > rules->singleton_slack) return false;
    for (Mask todo = used; todo; todo &= todo - 1) {
        int vertex = std::countr_zero(todo);
        Mask bit = Mask(1) << vertex;
        int attachment = bool(bit & first) + bool(bit & second) + bool(bit & third);
        if ((rules && attachment > rules->support_upper[vertex]) ||
            std::popcount(graph[vertex]) + attachment > total_degree) return false;
    }
    return true;
}

static bool compatible_columns(const Graph& graph, Mask common, Mask core) {
    for (Mask todo = common; todo; todo &= todo - 1) {
        int first = std::countr_zero(todo);
        int forced_partners = 0;
        for (Mask others = common & ~(Mask(1) << first); others; others &= others - 1) {
            int overlap = std::popcount(graph[first] & graph[std::countr_zero(others)] & core);
            if (overlap > 4) return false;
            forced_partners += overlap == 4;
        }
        if (forced_partners > 1) return false;
    }
    return true;
}

static bool pack(const Graph& graph, Mask core, int width, int row_size,
                 int overlap, bool cover_all, int total_degree = 100, const WingRules* rules = nullptr) {
    assert(width == 2 || width == 3);
    std::vector<Mask> sets;
    independent_sets(graph, core, row_size, 0, sets);
    for (std::size_t first = 0; first < sets.size(); ++first) {
        for (std::size_t second = first + 1; second < sets.size(); ++second) {
            Mask shared = sets[first] & sets[second];
            if (std::popcount(shared) > overlap) continue;
            Mask used = sets[first] | sets[second];
            if (width == 2 && (!cover_all || used == core) &&
                admissible(graph, sets[first], sets[second], 0, total_degree, rules)) return true;
            if (width != 3) continue;
            for (std::size_t third = second + 1; third < sets.size(); ++third) {
                Mask last = sets[third];
                if (cover_all && (used | last) != core) continue;
                if (std::popcount(sets[first] & last) > overlap || std::popcount(sets[second] & last) > overlap)
                    continue;
                if (admissible(graph, sets[first], sets[second], last, total_degree, rules)) return true;
            }
        }
    }
    return false;
}

static void control(std::ifstream& input) {
    std::uint64_t graphs = 0, pairs = 0, orientations = 0, strong_orientations = 0;
    for (std::string line; std::getline(input, line);) {
        Graph graph = decode(line);
        ++graphs;
        assert(graph.size() == 22);
        std::vector<Mask> invalid;
        independent_sets(graph, all(graph), 7, 0, invalid);
        assert(invalid.empty());
        for (int first = 0; first < 22; ++first) {
            assert(std::popcount(graph[first]) == 6 && independent(graph, graph[first]));
            for (int second = first + 1; second < 22; ++second) {
                if (graph[first] & (Mask(1) << second)) continue;
                Mask common = graph[first] & graph[second];
                if (std::popcount(common) != 4) continue;
                Mask left = graph[first] ^ common, right = graph[second] ^ common;
                bool complete = true;
                for (Mask todo = left; todo; todo &= todo - 1)
                    complete &= (graph[std::countr_zero(todo)] & right) == right;
                if (!complete) continue;
                ++pairs;
                Mask core = all(graph) & ~(common | left | right | (Mask(1) << first) | (Mask(1) << second));
                int singleton = 0, excess = 0, unused_singleton = 0;
                std::vector<int> avoid_left(22), avoid_right(22);
                for (Mask todo = core; todo; todo &= todo - 1) {
                    int vertex = std::countr_zero(todo);
                    Mask support = graph[vertex] & common;
                    assert(support);
                    bool hit_left = graph[vertex] & left, hit_right = graph[vertex] & right;
                    assert(!hit_left || !hit_right);
                    if (std::has_single_bit(support)) {
                        ++singleton;
                        int column = std::countr_zero(support);
                        if (!hit_left) ++avoid_left[column];
                        if (!hit_right) ++avoid_right[column];
                        unused_singleton += !hit_left && !hit_right;
                    }
                    excess += std::max(0, std::popcount(support) - 2);
                }
                assert(singleton == 2 * std::popcount(core) - 16 + excess);
                assert(excess + unused_singleton <= 24 - 2 * std::popcount(core));
                for (int column = 0; column < 22; ++column) {
                    assert(avoid_left[column] <= 1 && avoid_right[column] <= 1);
                }
                for (int orientation = 0; orientation < 2; ++orientation) {
                    Mask retained = core;
                    for (Mask todo = left; todo; todo &= todo - 1)
                        retained &= ~graph[std::countr_zero(todo)];
                    std::vector<Mask> actual;
                    for (Mask todo = right; todo; todo &= todo - 1) {
                        Mask row = graph[std::countr_zero(todo)] & core;
                        assert((row & retained) == row && std::popcount(row) == 3 && independent(graph, row));
                        actual.push_back(row);
                    }
                    bool isolated = true;
                    for (int vertex = 0; vertex < 22; ++vertex) {
                        if (vertex != first && vertex != second) {
                            isolated &= std::popcount(graph[vertex] & graph[first]) < 4;
                            isolated &= std::popcount(graph[vertex] & graph[second]) < 4;
                        }
                    }
                    if (isolated) {
                        WingRules rules = wing_rules(graph, common, retained, 4, 24 - 2 * std::popcount(core));
                        const int retained_root = orientation == 0 ? second : first;
                        Mask window_mask = common | retained | (Mask(1) << retained_root);
                        Graph window = graph;
                        for (Mask& row : window) row &= window_mask;
                        assert(admissible(window, actual[0], actual[1], 0, 6, &rules));
                        ++strong_orientations;
                    }
                    if (actual[0] != actual[1]) {
                        Mask cover = actual[0] | actual[1];
                        int overlap = std::popcount(actual[0] & actual[1]);
                        assert(pack(graph, cover, 2, 3, overlap, true));
                        assert(!pack(graph, cover, 2, 3, overlap - 1, true));
                        ++orientations;
                    }
                    std::swap(left, right);
                }
            }
        }
    }
    assert(graphs == 10 && pairs >= 7 && orientations > 0 && strong_orientations > 0);
    std::cout << "PASS C22 graphs=" << graphs << " complete k4 pairs=" << pairs
              << " planted packing and impossible-overlap controls=" << orientations
              << " strong support controls=" << strong_orientations << '\n';
}

static void scan(std::ifstream& input, const std::string& mode, std::ofstream& output) {
    std::uint64_t graphs = 0, roots = 0, sums = 0, columns = 0, keep_graphs = 0, keep_roots = 0;
    for (std::string line; std::getline(input, line); ++graphs) {
        Graph graph = decode(line);
        if (mode == "core13") {
            assert(graph.size() == 13);
            if (pack(graph, all(graph), 3, 5, 1, true)) {
                ++keep_graphs;
                output << graphs << '\t' << line << '\n';
            }
            continue;
        }
        assert(graph.size() == 21);
        bool keep = false;
        for (int root = 0; root < 21; ++root) {
            Mask common = graph[root];
            if (std::popcount(common) != 6) continue;
            ++roots;
            int degree_sum = 0;
            for (Mask todo = common; todo; todo &= todo - 1)
                degree_sum += std::popcount(graph[std::countr_zero(todo)]);
            if (degree_sum < 28 || degree_sum > 30) continue;
            ++sums;
            Mask core = all(graph) & ~(common | (Mask(1) << root));
            if (mode == "strong21") {
                if (!compatible_columns(graph, common, core)) continue;
                ++columns;
                WingRules rules = wing_rules(graph, common, core, 6, 2);
                if (!pack(graph, core, 3, 5, 1, false, 9, &rules)) continue;
            } else if (!pack(graph, core, 3, 5, 1, false, 9)) {
                continue;
            }
            keep = true;
            ++keep_roots;
            output << graphs << '\t' << root << '\t' << line << '\n';
        }
        keep_graphs += keep;
    }
    assert(graphs == (mode == "core13" ? 275086u : 1118436u));
    std::cout << mode << " graphs=" << graphs << " roots=" << roots << " sum_pass=" << sums
              << " column_pass=" << columns
              << " packed_graphs=" << keep_graphs << " packed_roots=" << keep_roots << '\n';
}

int main(int argc, char** argv) {
    assert(argc == 3 || argc == 4);
    std::string mode = argv[1];
    std::ifstream input(argv[2]);
    assert(input);
    if (mode == "control") {
        control(input);
    } else {
        assert(argc == 4 && (mode == "core13" || mode == "window21" || mode == "strong21"));
        std::ofstream output(argv[3]);
        assert(output);
        scan(input, mode, output);
    }
}
