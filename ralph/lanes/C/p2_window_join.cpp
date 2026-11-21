#include <array>
#include <chrono>
#include <ctime>
#include <map>
#include <sstream>
#include <tuple>
#include <unordered_map>
#include <utility>

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#define main wing_windows_main
#include "p2_wing_windows.cpp"
#undef main
#pragma GCC diagnostic pop

using Wide = std::uint64_t;
using Pack = std::array<Mask, 3>;
using Key = Wide;

struct Rules {
    int degree, cap, width, total, side;
};

struct Mark {
    std::size_t source;
    int root;
    Graph graph;
    std::vector<int> columns, shared;
    std::vector<Pack> packs;
};

static std::vector<int> vertices(Mask mask) {
    std::vector<int> result;
    for (; mask; mask &= mask - 1) result.push_back(std::countr_zero(mask));
    return result;
}

static int degree(const Graph& graph, int vertex) {
    return std::popcount(graph[vertex]);
}

static Mask mask_of(const std::vector<int>& numbers) {
    Mask mask = 0;
    for (int number : numbers) mask |= Mask(1) << number;
    return mask;
}

static void add_marks(std::vector<Mark>& marks, const Graph& graph, std::size_t source,
                      int root, const Rules& spec, Wide& pack_count) {
    Mask common = graph[root];
    Mask core = all(graph) & ~common & ~(Mask(1) << root);
    if (std::popcount(common) != spec.cap || std::popcount(core) < spec.side ||
        std::popcount(core) - spec.side > 2) return;
    const int row_size = spec.degree - spec.width - 1;
    const int budget = spec.cap * spec.degree - 2 * spec.total;
    WingRules rules = wing_rules(graph, common, core, spec.cap, budget);
    if (rules.singleton_slack < 0) return;
    for (int column : vertices(common))
        if (std::popcount(graph[column] & rules.singletons) > 1) return;
    std::vector<Mask> rows;
    independent_sets(graph, core, row_size, 0, rows);
    std::map<Mask, std::vector<Pack>> local;
    auto record = [&](Mask first, Mask second, Mask third) {
        Mask used = first | second | third;
        if (std::popcount(used) != spec.side ||
            !admissible(graph, first, second, third, spec.degree, &rules)) return;
        Pack pack{first, second, third};
        std::sort(pack.begin(), pack.begin() + spec.width);
        local[core & ~used].push_back(pack);
        ++pack_count;
    };
    for (std::size_t first = 0; first < rows.size(); ++first) {
        for (std::size_t second = first + 1; second < rows.size(); ++second) {
            if (std::popcount(rows[first] & rows[second]) > spec.cap - spec.width - 2) continue;
            if (spec.width == 2) {
                record(rows[first], rows[second], 0);
                continue;
            }
            for (std::size_t third = second + 1; third < rows.size(); ++third) {
                if (std::popcount(rows[first] & rows[third]) > spec.cap - spec.width - 2 ||
                    std::popcount(rows[second] & rows[third]) > spec.cap - spec.width - 2) continue;
                record(rows[first], rows[second], rows[third]);
            }
        }
    }
    for (auto& [shared, packs] : local)
        marks.push_back({source, root, graph, vertices(common), vertices(shared), std::move(packs)});
}

static int pattern(const Mark& mark, int column) {
    int result = 0;
    for (std::size_t index = 0; index < mark.shared.size(); ++index)
        if (mark.graph[column] & (Mask(1) << mark.shared[index])) result |= 1 << index;
    return result;
}

static int shared_edge(const Mark& mark) {
    return mark.shared.size() == 2 && (mark.graph[mark.shared[0]] & (Mask(1) << mark.shared[1])) != 0;
}

static int token(const Mark& mark, int column, const Rules& spec, bool want) {
    int adjacency = pattern(mark, column);
    int deg = degree(mark.graph, column);
    if (want) deg = spec.degree + std::popcount(static_cast<unsigned>(adjacency)) - deg;
    return (adjacency << 4) | deg;
}

static Key signature(const Mark& mark, const Rules& spec, bool want, bool with_shared_degrees) {
    std::vector<int> tokens;
    for (int column : mark.columns) tokens.push_back(token(mark, column, spec, want));
    std::sort(tokens.begin(), tokens.end());
    Key result = shared_edge(mark);
    for (int code : tokens) result = (result << 6) | code;
    if (with_shared_degrees) {
        const Mask overlap = mask_of(mark.columns) | mask_of(mark.shared);
        for (int vertex : mark.shared) {
            int deg = degree(mark.graph, vertex);
            if (want) deg = spec.degree + std::popcount(mark.graph[vertex] & overlap) - deg;
            assert(deg >= 0 && deg < 16);
            result = (result << 4) | deg;
        }
    }
    return result;
}

static bool column_test(const Mark& left, const Mark& right, const std::vector<int>& assignment,
                        const Rules& spec) {
    std::vector<int> partners(spec.cap);
    const Mask left_shared = mask_of(left.shared);
    for (int first = 0; first < spec.cap; ++first) {
        for (int second = first + 1; second < spec.cap; ++second) {
            Mask first_overlap = left.graph[left.columns[first]] & left.graph[left.columns[second]];
            Mask second_overlap = right.graph[assignment[first]] & right.graph[assignment[second]];
            int count = std::popcount(first_overlap) + std::popcount(second_overlap)
                        - std::popcount(first_overlap & left_shared);
            if (count > spec.cap) return false;
            if (count == spec.cap && (++partners[first] > 1 || ++partners[second] > 1)) return false;
        }
    }
    return true;
}

static unsigned assign_columns(const Mark& left, const Mark& right, const Rules& spec,
                               std::vector<int>& assignment, Mask used,
                               auto&& visit) {
    std::size_t index = assignment.size();
    if (index == left.columns.size()) {
        visit(assignment);
        return 1;
    }
    unsigned count = 0;
    int target = token(left, left.columns[index], spec, true);
    for (int column : right.columns) {
        Mask bit = Mask(1) << column;
        if (used & bit || token(right, column, spec, false) != target) continue;
        assignment.push_back(column);
        count += assign_columns(left, right, spec, assignment, used | bit, visit);
        assignment.pop_back();
    }
    return count;
}

static Graph projection(const Graph& graph, Mask keep) {
    auto picked = vertices(keep);
    Graph result(picked.size());
    for (std::size_t first = 0; first < picked.size(); ++first)
        for (std::size_t second = 0; second < picked.size(); ++second)
            if (graph[picked[first]] & (Mask(1) << picked[second])) result[first] |= Mask(1) << second;
    return result;
}

struct Boundary {
    std::vector<Wide> fixed, undecided;
    std::vector<int> rows, columns, deficit;

    void edge(int first, int second) {
        assert(first != second);
        fixed[first] |= Wide(1) << second;
        fixed[second] |= Wide(1) << first;
    }

    void remove(int first, int second) {
        undecided[first] &= ~(Wide(1) << second);
        undecided[second] &= ~(Wide(1) << first);
    }

    void add_possible(int first, int second) {
        undecided[first] |= Wide(1) << second;
        undecided[second] |= Wide(1) << first;
    }
};

static Boundary combine(const Mark& left, const Mark& right, const std::vector<int>& assignment,
                        const Pack& first_pack, const Pack& second_pack, const Rules& spec,
                        std::vector<int>* left_relabel = nullptr, std::vector<int>* right_relabel = nullptr) {
    const int order = 2 + spec.cap + 2 * spec.width + spec.total;
    Boundary boundary{std::vector<Wide>(order), std::vector<Wide>(order), {}, {}, std::vector<int>(order)};
    std::vector<int> left_map(left.graph.size(), -1), right_map(right.graph.size(), -1);
    left_map[left.root] = 0;
    right_map[right.root] = 1;
    const int first_wing = 2 + spec.cap;
    const int second_wing = first_wing + spec.width;
    int next = second_wing + spec.width;
    for (int column = 0; column < spec.cap; ++column) {
        left_map[left.columns[column]] = 2 + column;
        right_map[assignment[column]] = 2 + column;
    }
    for (std::size_t index = 0; index < left.shared.size(); ++index) {
        left_map[left.shared[index]] = next;
        right_map[right.shared[index]] = next++;
    }
    for (auto [map, privates] : {std::pair{&left_map, &boundary.rows}, std::pair{&right_map, &boundary.columns}})
        for (int& label : *map)
            if (label < 0) {
                privates->push_back(next);
                label = next++;
            }
    assert(next == order);
    for (auto [map, graph] : {std::pair{&left_map, &left.graph}, std::pair{&right_map, &right.graph}})
        for (std::size_t first = 0; first < graph->size(); ++first)
            for (Mask rest = (*graph)[first] >> first << first; rest; rest &= rest - 1)
                boundary.edge((*map)[first], (*map)[std::countr_zero(rest)]);
    for (int wing = 0; wing < spec.width; ++wing) {
        const int left_vertex = first_wing + wing, right_vertex = second_wing + wing;
        boundary.edge(0, left_vertex);
        boundary.edge(1, right_vertex);
        for (int other = 0; other < spec.width; ++other) boundary.edge(left_vertex, second_wing + other);
        for (Mask rest = first_pack[wing]; rest; rest &= rest - 1) boundary.edge(left_vertex, left_map[std::countr_zero(rest)]);
        for (Mask rest = second_pack[wing]; rest; rest &= rest - 1) boundary.edge(right_vertex, right_map[std::countr_zero(rest)]);
    }
    for (int row : boundary.rows)
        for (int column : boundary.columns)
            if (!(boundary.fixed[row] & boundary.fixed[column])) boundary.add_possible(row, column);
    for (int vertex = 0; vertex < order; ++vertex) {
        boundary.deficit[vertex] = spec.degree - std::popcount(boundary.fixed[vertex]);
        if (!boundary.undecided[vertex] &&
            std::find(boundary.rows.begin(), boundary.rows.end(), vertex) == boundary.rows.end() &&
            std::find(boundary.columns.begin(), boundary.columns.end(), vertex) == boundary.columns.end())
            assert(boundary.deficit[vertex] == 0);
    }
    if (left_relabel) *left_relabel = std::move(left_map);
    if (right_relabel) *right_relabel = std::move(right_map);
    return boundary;
}

static void control_overlap(const Graph& graph, int root_left, int root_right, Mask shared_columns,
                            Mask private_left, Mask private_right, Mask wing_left, Mask wing_right,
                            const Rules& spec) {
    const auto keep_left = vertices(private_left), keep_right = vertices(private_right);
    assert(keep_left.size() >= 2 && keep_right.size() >= 2);
    for (int size = 1; size <= 2; ++size) {
        auto shared = std::vector<int>{keep_left.front()};
        if (size == 2) shared.push_back(keep_right.front());
        auto make = [&](int root, Mask privates) {
            Mask keep = (Mask(1) << root) | shared_columns | mask_of(shared) | privates;
            auto relabel = [&](int vertex) { return std::popcount(keep & ((Mask(1) << vertex) - 1)); };
            Mark mark{0, relabel(root), projection(graph, keep), {}, {}, {}};
            for (int column : vertices(shared_columns)) mark.columns.push_back(relabel(column));
            for (int vertex : shared) mark.shared.push_back(relabel(vertex));
            return mark;
        };
        Mark left = make(root_left, private_left | wing_left), right = make(root_right, private_right | wing_right);
        if (size == 2) {
            std::reverse(left.shared.begin(), left.shared.end());
            std::reverse(right.shared.begin(), right.shared.end());
        }
        assert(signature(left, spec, true, true) == signature(right, spec, false, true));
        assert(column_test(left, right, right.columns, spec));
        const int vertex = right.shared.back();
        Mask private_core = all(right.graph) & ~(right.graph[right.root] | (Mask(1) << right.root) | mask_of(right.shared));
        assert(private_core);
        right.graph[vertex] ^= private_core & -private_core;
        assert(signature(left, spec, true, false) == signature(right, spec, false, false));
        assert(signature(left, spec, true, true) != signature(right, spec, false, true));
    }
}

static int sum_deficits(const Boundary& boundary, const std::vector<int>& vertices) {
    int sum = 0;
    for (int vertex : vertices) sum += boundary.deficit[vertex];
    return sum;
}

static bool local_degree(const Boundary& boundary) {
    if (sum_deficits(boundary, boundary.rows) != sum_deficits(boundary, boundary.columns)) return false;
    for (std::size_t vertex = 0; vertex < boundary.fixed.size(); ++vertex)
        if (boundary.deficit[vertex] < 0 || boundary.deficit[vertex] > std::popcount(boundary.undecided[vertex]))
            return false;
    return true;
}

static bool degree_propagate(Boundary& boundary) {
    bool changed;
    do {
        changed = false;
        for (std::size_t vertex = 0; vertex < boundary.fixed.size(); ++vertex) {
            Wide possible = boundary.undecided[vertex];
            int count = std::popcount(possible), need = boundary.deficit[vertex];
            if (need < 0 || need > count) return false;
            if (!count || (need && need != count)) continue;
            changed = true;
            for (; possible; possible &= possible - 1) {
                int other = std::countr_zero(possible);
                boundary.remove(vertex, other);
                if (need) {
                    if (boundary.fixed[vertex] & boundary.fixed[other]) return false;
                    boundary.edge(vertex, other);
                    --boundary.deficit[vertex];
                    --boundary.deficit[other];
                    for (Wide common = boundary.fixed[vertex]; common; common &= common - 1) {
                        int neighbor = std::countr_zero(common);
                        boundary.remove(neighbor, other);
                    }
                    for (Wide common = boundary.fixed[other]; common; common &= common - 1) {
                        int neighbor = std::countr_zero(common);
                        boundary.remove(neighbor, vertex);
                    }
                }
            }
        }
    } while (changed);
    return true;
}

static bool flow(const Boundary& boundary) {
    const int order = boundary.fixed.size();
    std::array<Wide, 62> arcs{};
    std::array<int, 62> capacities{};
    const int source = order, sink = order + 1;
    for (int row : boundary.rows) {
        arcs[row] = boundary.undecided[row];
        if ((capacities[row] = boundary.deficit[row])) arcs[source] |= Wide(1) << row;
    }
    for (int column : boundary.columns)
        if ((capacities[column] = boundary.deficit[column])) arcs[column] |= Wide(1) << sink;
    for (int need = sum_deficits(boundary, boundary.rows); need; --need) {
        Wide seen = Wide(1) << source, scan = seen;
        std::array<int, 62> parent{};
        while (scan && !(seen & (Wide(1) << sink))) {
            int vertex = std::countr_zero(scan);
            scan &= scan - 1;
            Wide fresh = arcs[vertex] & ~seen;
            seen |= fresh;
            scan |= fresh;
            for (; fresh; fresh &= fresh - 1) parent[std::countr_zero(fresh)] = vertex;
        }
        if (!(seen & (Wide(1) << sink))) return false;
        int current = parent[sink];
        if (!--capacities[current]) arcs[current] &= ~(Wide(1) << sink);
        while (parent[current] != source) {
            int before = parent[current];
            arcs[before] &= ~(Wide(1) << current);
            arcs[current] |= Wide(1) << before;
            current = before;
        }
        if (!--capacities[current]) arcs[source] &= ~(Wide(1) << current);
    }
    return true;
}

static int full_wings(Boundary& boundary, const Rules& spec) {
    const int order = boundary.fixed.size();
    std::vector<int> partners(order, -1);
    bool changed = false;
    for (int first = 0; first < order; ++first) {
        for (int second = first + 1; second < order; ++second) {
            int count = std::popcount(boundary.fixed[first] & boundary.fixed[second]);
            if (count > spec.cap) return -1;
            if (count != spec.cap) continue;
            if (partners[first] >= 0 || partners[second] >= 0) return -1;
            partners[first] = second;
            partners[second] = first;
            if (boundary.undecided[first] & (Wide(1) << second)) {
                boundary.remove(first, second);
                changed = true;
            }
            Wide left = boundary.fixed[first] & ~boundary.fixed[second];
            Wide right = boundary.fixed[second] & ~boundary.fixed[first];
            for (Wide todo = left & boundary.undecided[second]; todo; todo &= todo - 1) {
                boundary.remove(std::countr_zero(todo), second);
                changed = true;
            }
            for (Wide todo = right & boundary.undecided[first]; todo; todo &= todo - 1) {
                boundary.remove(std::countr_zero(todo), first);
                changed = true;
            }
            for (Wide left_todo = left; left_todo; left_todo &= left_todo - 1) {
                int vertex = std::countr_zero(left_todo);
                if (right & ~(boundary.fixed[vertex] | boundary.undecided[vertex])) return -1;
                for (Wide todo = right & boundary.undecided[vertex]; todo; todo &= todo - 1) {
                    int other = std::countr_zero(todo);
                    if (boundary.fixed[vertex] & boundary.fixed[other]) return -1;
                    boundary.remove(vertex, other);
                    boundary.edge(vertex, other);
                    --boundary.deficit[vertex];
                    --boundary.deficit[other];
                    for (Wide adjacent = boundary.fixed[vertex]; adjacent; adjacent &= adjacent - 1)
                        boundary.remove(std::countr_zero(adjacent), other);
                    for (Wide adjacent = boundary.fixed[other]; adjacent; adjacent &= adjacent - 1)
                        boundary.remove(std::countr_zero(adjacent), vertex);
                    if (right & ~(boundary.fixed[vertex] | boundary.undecided[vertex])) return -1;
                    changed = true;
                }
            }
        }
    }
    return changed;
}

static bool avoid_ten(const std::vector<Wide>& possible, Wide mask, int need) {
    if (!need) return false;
    while (std::popcount(mask) >= need) {
        int vertex = std::countr_zero(mask);
        mask &= mask - 1;
        if (!avoid_ten(possible, mask & ~possible[vertex], need - 1)) return false;
    }
    return true;
}

static int cross_filter(Boundary& boundary, const Rules& spec, bool insist_full_wings) {
    if (!local_degree(boundary)) return 0;
    if (!degree_propagate(boundary)) return 1;
    if (!flow(boundary)) return 2;
    if (insist_full_wings) {
        int update;
        do {
            update = full_wings(boundary, spec);
            if (update < 0 || (update && !degree_propagate(boundary))) return 3;
        } while (update);
        if (!flow(boundary)) return 3;
    }
    std::vector<Wide> possible = boundary.fixed;
    for (std::size_t vertex = 0; vertex < possible.size(); ++vertex) possible[vertex] |= boundary.undecided[vertex];
    if (!avoid_ten(possible, (Wide(1) << possible.size()) - 1, spec.degree + 1)) return 4;
    return 5;
}

static bool independent_capacity(const Mark& mark, const Pack& wing, int other_size, const Rules& spec);

static void control_join(std::ifstream& input) {
    unsigned tested = 0, mismatched = 0, column_negative = 0, graph_count = 0, full_tested = 0;
    std::array<unsigned, 3> shared_counts{};
    for (std::string line; std::getline(input, line);) {
        Graph graph = decode(line);
        ++graph_count;
        for (int first = 0; first < 22; ++first) {
            for (int second = first + 1; second < 22; ++second) {
                Mask common = graph[first] & graph[second];
                if (std::popcount(common) != 4) continue;
                Mask left = graph[first] & ~common, right = graph[second] & ~common;
                auto complete = [&](int vertex) { return (graph[vertex] & right) == right; };
                auto wing_vertices = vertices(left);
                if (!std::all_of(wing_vertices.begin(), wing_vertices.end(), complete)) continue;
                Mask root_bits = (Mask(1) << first) | (Mask(1) << second);
                Mask core = all(graph) & ~(root_bits | common | left | right);
                bool matching = true, every_pair_full = true;
                for (int vertex = 0; vertex < 22; ++vertex) {
                    int partners = 0;
                    for (int other = 0; other < 22; ++other) {
                        if (vertex == other) continue;
                        int overlap = std::popcount(graph[vertex] & graph[other]);
                        matching &= overlap <= 4;
                        partners += overlap == 4;
                        if (vertex < other && overlap == 4) {
                            Mask first_only = graph[vertex] & ~graph[other];
                            Mask second_only = graph[other] & ~graph[vertex];
                            for (int neighbor : vertices(first_only))
                                every_pair_full &= (graph[neighbor] & second_only) == second_only;
                        }
                    }
                    matching &= partners <= 1;
                }
                if (!matching) continue;
                auto make_side = [&](Mask wing, int root) {
                    Mask side = 0;
                    for (int vertex : vertices(wing)) side |= graph[vertex] & core;
                    Mask other_side = 0;
                    for (int vertex : vertices((left | right) & ~wing)) other_side |= graph[vertex] & core;
                    Mask keep = (Mask(1) << root) | common | (core & ~other_side);
                    auto relabel = [&](int vertex) { return std::popcount(keep & ((Mask(1) << vertex) - 1)); };
                    std::vector<Mark> result;
                    Rules spec{6, 4, 2, 22 - 2 - 4 - 4, std::popcount(side)};
                    Wide control_pack_count = 0;
                    add_marks(result, projection(graph, keep), 0, relabel(root), spec, control_pack_count);
                    Mask exact_shared = 0;
                    for (int vertex : vertices(core & ~(side | other_side))) exact_shared |= Mask(1) << relabel(vertex);
                    auto it = std::find_if(result.begin(), result.end(), [&](const Mark& mark) {
                        return mask_of(mark.shared) == exact_shared;
                    });
                    assert(it != result.end());
                    Pack planted{};
                    int index = 0;
                    for (int vertex : vertices(wing)) {
                        for (int neighbor : vertices(graph[vertex] & core))
                            planted[index] |= Mask(1) << relabel(neighbor);
                        ++index;
                    }
                    std::sort(planted.begin(), planted.begin() + 2);
                    assert(std::find(it->packs.begin(), it->packs.end(), planted) != it->packs.end());
                    return std::tuple{*it, planted, vertices(keep)};
                };
                auto [lhs, left_pack, left_keep] = make_side(left, first);
                auto [rhs, right_pack, right_keep] = make_side(right, second);
                Rules spec{6, 4, 2, 12, 0};
                auto side_mask = [&](Mask wing) {
                    Mask attached = 0;
                    for (int vertex : vertices(wing)) attached |= graph[vertex];
                    return attached & core;
                };
                assert(independent_capacity(lhs, left_pack, std::popcount(side_mask(right)), spec));
                assert(independent_capacity(rhs, right_pack, std::popcount(side_mask(left)), spec));
                if (lhs.shared.empty())
                    control_overlap(graph, first, second, common, side_mask(left), side_mask(right), left, right, spec);
                assert(signature(lhs, spec, true, true) == signature(rhs, spec, false, true));
                ++shared_counts[lhs.shared.size()];
                std::vector<int> planted_map, left_map, right_map;
                for (int column : lhs.columns) {
                    auto where = std::find(right_keep.begin(), right_keep.end(), left_keep[column]);
                    assert(where != right_keep.end());
                    planted_map.push_back(where - right_keep.begin());
                }
                assert(column_test(lhs, rhs, planted_map, spec));
                Boundary boundary = combine(lhs, rhs, planted_map, left_pack, right_pack, spec, &left_map, &right_map);
                auto pre = boundary;
                assert(cross_filter(boundary, spec, every_pair_full) == 5);
                full_tested += every_pair_full;
                for (std::size_t pos = 0; pos < left_map.size(); ++pos) {
                    for (std::size_t other = 0; other < right_map.size(); ++other) {
                        bool edge = graph[left_keep[pos]] & (Mask(1) << right_keep[other]);
                        Wide bit = Wide(1) << right_map[other];
                        assert(edge || !(boundary.fixed[left_map[pos]] & bit));
                        assert(!edge || ((boundary.fixed[left_map[pos]] | boundary.undecided[left_map[pos]]) & bit));
                    }
                }
                ++pre.deficit[pre.rows.front()];
                assert(cross_filter(pre, spec, every_pair_full) == 0);
                std::vector<int> assignment, brute = rhs.columns;
                unsigned brute_count = 0, brute_pass = 0, pass = 0;
                do {
                    bool fits = true;
                    for (int index = 0; index < spec.cap; ++index)
                        fits &= token(lhs, lhs.columns[index], spec, true) == token(rhs, brute[index], spec, false);
                    if (fits) {
                        ++brute_count;
                        brute_pass += column_test(lhs, rhs, brute, spec);
                    }
                } while (std::next_permutation(brute.begin(), brute.end()));
                unsigned count = assign_columns(lhs, rhs, spec, assignment, 0, [&](const auto& map) {
                    pass += column_test(lhs, rhs, map, spec);
                });
                assert(count == brute_count && pass == brute_pass && pass != 0);
                column_negative += count - pass;
                int column = rhs.columns.front();
                rhs.graph[column] ^= Mask(1) << rhs.root;
                assert(signature(lhs, spec, true, false) != signature(rhs, spec, false, false));
                ++mismatched;
                ++tested;
            }
        }
    }
    assert(graph_count == 10 && tested == 7 && mismatched == tested && full_tested > 0);
    Boundary hall{std::vector<Wide>(6), std::vector<Wide>(6), {0, 1, 2}, {3, 4, 5}, {1, 1, 1, 1, 1, 1}};
    hall.add_possible(0, 3);
    hall.add_possible(1, 3);
    hall.add_possible(2, 4);
    hall.add_possible(2, 5);
    assert(local_degree(hall) && !flow(hall));
    std::cout << "PASS C22 graphs=" << graph_count << " planted joins=" << tested
              << " corrupted columns rejected=" << mismatched
              << " naturally rejected column maps=" << column_negative << " full-wing propagated=" << full_tested
              << " U0/U1/U2=" << shared_counts[0] << '/' << shared_counts[1] << '/' << shared_counts[2]
              << " inconsistent-deficit and Hall-negative controls"
              << " plus artificial U1/U2 reprojections and damaged U degrees" << '\n';
}

static constexpr Rules target{9, 6, 3, 26, 12};

static int ramsey_small(int k) {
    constexpr std::array<int, 9> numbers{0, 1, 3, 6, 9, 14, 18, 23, 28};
    return numbers.at(k);
}

static bool capacity_search(const Graph& graph, Mask remaining, Mask common,
                            const std::vector<int>& deficit, int need, int hit, int wing_goal,
                            bool hits_common) {
    if (hit >= wing_goal + 1) return true;
    if (need == 0) return hit >= wing_goal + !hits_common;
    while (std::popcount(remaining) >= need) {
        const int vertex = std::countr_zero(remaining);
        Mask bit = Mask(1) << vertex;
        remaining ^= bit;
        if (!capacity_search(graph, remaining & ~graph[vertex], common, deficit, need - 1,
                             hit + deficit[vertex], wing_goal, hits_common || bool(bit & common))) return false;
    }
    return true;
}

static bool independent_capacity(const Mark& mark, const Pack& wing, int other_size, const Rules& spec) {
    const Graph& graph = mark.graph;
    Mask common = graph[mark.root];
    Mask core = all(graph) & ~common & ~(Mask(1) << mark.root);
    std::vector<int> deficit(graph.size());
    for (int vertex : vertices(core)) {
        Mask bit = Mask(1) << vertex;
        int attachments = 0;
        for (int row = 0; row < spec.width; ++row) attachments += bool(wing[row] & bit);
        deficit[vertex] = spec.degree - degree(graph, vertex) - attachments;
    }
    for (int column : mark.columns) deficit[column] = spec.degree - degree(graph, column) - 1;
    for (int size = spec.degree - spec.width; size >= 3; --size) {
        int wing_goal = other_size + spec.width + 1 - ramsey_small(spec.degree - size + 1);
        if (wing_goal >= 0 && !capacity_search(graph, all(graph), common, deficit, size, 0,
                                               wing_goal, false)) return false;
        if (size + 2 <= spec.degree) {
            int core_goal = other_size + 1 - ramsey_small(spec.degree - size - 1);
            if (core_goal > 0 && !capacity_search(graph, core, 0, deficit, size, 0, core_goal - 1, false))
                return false;
        }
    }
    return true;
}

static void asymmetric_profiles(std::ifstream& input, std::ostream& output, bool use_capacity) {
    std::map<std::pair<int, std::vector<int>>, Wide> profiles;
    std::array<Wide, 3> profile_counts{};
    std::array<Wide, 2> pack_counts{}, kept_packs{}, kept_marks{};
    for (std::string line; std::getline(input, line);) {
        std::istringstream fields(line);
        std::size_t source;
        int root;
        std::string text;
        assert(fields >> source >> root >> text);
        Graph graph = decode(text);
        assert(graph.size() == 21);
        for (int side = 13; side <= 14; ++side) {
            Rules spec{9, 6, 3, 26, side};
            std::vector<Mark> marks;
            Wide pack_count = 0;
            add_marks(marks, graph, source, root, spec, pack_count);
            for (const Mark& mark : marks) {
                ++profile_counts[side - 13];
                pack_counts[side - 13] += mark.packs.size();
                Wide passing = 0;
                for (const Pack& pack : mark.packs)
                    passing += !use_capacity || independent_capacity(mark, pack, 12, spec);
                kept_packs[side - 13] += passing;
                kept_marks[side - 13] += passing != 0;
                if (!passing) continue;
                if (side != 14) continue;
                assert(mark.shared.empty());
                std::vector<int> sizes;
                int large_sum = 0;
                for (int column : mark.columns) {
                    int own = degree(graph, column);
                    large_sum += own;
                    sizes.push_back(spec.degree - own - 1);
                }
                std::sort(sizes.begin(), sizes.end());
                if (sizes.front() < 2 || sizes.back() > 5) continue;
                Mask core = all(graph) & ~graph[root] & ~(Mask(1) << root);
                int core_edges = 0;
                for (int vertex : vertices(core)) core_edges += std::popcount(graph[vertex] & core);
                assert(core_edges % 2 == 0);
                int small_edges = core_edges / 2 + large_sum - 36;
                if (small_edges < 0) continue;
                profiles[{small_edges, sizes}] += passing;
                ++profile_counts[2];
            }
        }
    }
    for (const auto& [profile, count] : profiles) {
        output << profile.first;
        for (int size : profile.second) output << '\t' << size;
        output << '\t' << count << '\n';
    }
    std::cout << "H21 marks side13=" << profile_counts[0] << " side14=" << profile_counts[1]
              << " side14_with_degree_keys=" << profile_counts[2] << " H19_profiles=" << profiles.size()
              << " packs13/14=" << pack_counts[0] << '/' << pack_counts[1]
              << " kept_packs13/14=" << kept_packs[0] << '/' << kept_packs[1]
              << " kept_marks13/14=" << kept_marks[0] << '/' << kept_marks[1]
              << " cpu=" << double(std::clock()) / CLOCKS_PER_SEC << '\n';
}

static void run_join(std::ifstream& input, std::ostream& output, bool join_columns, int stride = 0) {
    using Bucket = std::unordered_map<Key, std::vector<std::size_t>>;
    std::vector<Mark> marks;
    Wide roots = 0, packs = 0;
    for (std::string line; std::getline(input, line);) {
        std::istringstream fields(line);
        std::size_t source;
        int root;
        std::string text;
        assert(fields >> source >> root >> text);
        Graph graph = decode(text);
        assert(graph.size() == 21);
        add_marks(marks, graph, source, root, target, packs);
        ++roots;
    }
    assert(roots == 35099);
    Bucket common_only, full;
    for (std::size_t index = 0; index < marks.size(); ++index) {
        Mark swapped = marks[index];
        std::swap(swapped.shared[0], swapped.shared[1]);
        for (int orientation = 0; orientation < 2; ++orientation) {
            const Mark& mark = orientation ? swapped : marks[index];
            common_only[signature(mark, target, false, false)].push_back(2 * index + orientation);
            full[signature(mark, target, false, true)].push_back(2 * index + orientation);
        }
    }
    Wide coarse_pairs = 0, full_pairs = 0, left_hits = 0, max_degree = 0;
    for (const Mark& left : marks) {
        if (auto found = common_only.find(signature(left, target, true, false)); found != common_only.end())
            coarse_pairs += found->second.size();
        if (auto found = full.find(signature(left, target, true, true)); found != full.end()) {
            ++left_hits;
            full_pairs += found->second.size();
            max_degree = std::max<Wide>(max_degree, found->second.size());
        }
    }
    std::cout << "roots=" << roots << " packs=" << packs << " marks=" << marks.size()
              << " columns_keys=" << common_only.size() << " full_keys=" << full.size()
              << " columns_pairs=" << coarse_pairs << " full_pairs=" << full_pairs
              << " left_hits=" << left_hits << " max_degree=" << max_degree
              << " cpu=" << double(std::clock()) / CLOCKS_PER_SEC << std::endl;
    if (!join_columns) return;
    Wide tested = 0, pairs = 0, passed = 0, pack_pairs = 0, cross_survivors = 0;
    std::array<Wide, 6> filters{};
    for (const Mark& left : marks) {
        auto found = full.find(signature(left, target, true, true));
        if (found == full.end()) continue;
        for (auto entry : found->second) {
            const Mark& raw = marks[entry / 2];
            if (std::tie(raw.source, raw.root, raw.shared) < std::tie(left.source, left.root, left.shared)) continue;
            Mark right = raw;
            if (entry % 2) std::swap(right.shared[0], right.shared[1]);
            std::vector<int> assignment;
            ++pairs;
            tested += assign_columns(left, right, target, assignment, 0, [&](const auto& map) {
                if (!column_test(left, right, map, target)) return;
                ++passed;
                pack_pairs += left.packs.size() * right.packs.size();
                auto emit = [&] {
                    output << left.source << '\t' << left.root << '\t' << mask_of(left.shared) << '\t'
                           << right.source << '\t' << right.root << '\t' << right.shared[0] << '\t'
                           << right.shared[1] << '\t';
                    for (int column : map) output << column << ',';
                };
                if (!stride) {
                    emit();
                    output << '\t' << left.packs.size() * right.packs.size() << '\n';
                    return;
                }
                if ((passed - 1) % stride) return;
                for (const Pack& first_pack : left.packs) {
                    for (const Pack& second_pack : right.packs) {
                        Boundary boundary = combine(left, right, map, first_pack, second_pack, target);
                        int outcome = cross_filter(boundary, target, true);
                        ++filters[outcome];
                        if (outcome != 5) continue;
                        ++cross_survivors;
                        emit();
                        for (Mask row : first_pack) output << '\t' << row;
                        for (Mask row : second_pack) output << '\t' << row;
                        output << '\n';
                    }
                }
            });
        }
    }
    std::cout << "ordered_by_mark_pairs=" << pairs << " maps=" << tested << " column_pass=" << passed
              << " pack_pairs=" << pack_pairs << " cpu=" << double(std::clock()) / CLOCKS_PER_SEC << '\n';
    if (stride) {
        std::cout << "stride=" << stride;
        for (std::size_t index = 0; index < filters.size(); ++index)
            std::cout << " filter_" << index << '=' << filters[index];
        std::cout << " survivors=" << cross_survivors << '\n';
    }
}

int main(int argc, char** argv) {
    assert(argc >= 3 && argc <= 5);
    std::ifstream input(argv[2]);
    assert(input);
    std::string mode = argv[1];
    if (mode == "control") control_join(input);
    else if (mode == "count") run_join(input, std::cout, false);
    else if (mode == "profiles" || mode == "capacity") {
        assert(argc == 4);
        std::ofstream output(argv[3]);
        assert(output);
        asymmetric_profiles(input, output, mode == "capacity");
    }
    else {
        assert((mode == "join" && argc == 4) || (mode == "cross" && argc == 5));
        std::ofstream output(argv[3]);
        assert(output);
        int stride = argc == 5 ? std::stoi(argv[4]) : 0;
        assert(argc == 4 || stride > 0);
        run_join(input, output, true, stride);
        assert(output);
    }
    return 0;
}
