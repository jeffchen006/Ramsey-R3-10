#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using Mask = std::uint64_t;
using Graph = std::vector<Mask>;
using Counts = std::array<std::uint64_t, 5>;
using Columns = std::array<Mask, 4>;
using Loads = std::array<int, 4>;

static Mask bit(unsigned index) { return Mask{1} << index; }

static int pop_vertex(Mask& mask) {
    const int vertex = std::countr_zero(mask);
    mask &= mask - 1;
    return vertex;
}

static Graph decode(const std::string& line) {
    if (line.empty() || line.front() < '@' || line.front() > '}') throw std::runtime_error("bad order");
    const unsigned order = line.front() - '?';
    const unsigned bits = order * (order - 1) / 2;
    if (line.size() != 1 + (bits + 5) / 6 || (bits % 6 && (line.back() - '?') % (1 << (6 - bits % 6))))
        throw std::runtime_error("bad graph6 length or padding");
    Graph graph(order);
    unsigned offset = 0;
    for (unsigned right = 1; right < order; ++right)
        for (unsigned left = 0; left < right; ++left, ++offset) {
            const int digit = line[1 + offset / 6] - '?';
            if (digit < 0 || digit > 63) throw std::runtime_error("bad graph6 digit");
            if ((digit >> (5 - offset % 6)) & 1) {
                graph[right] |= bit(left);
                graph[left] |= bit(right);
            }
        }
    return graph;
}

static std::string encode(const Graph& graph) {
    const unsigned order = graph.size();
    std::string line(1 + (order * (order - 1) / 2 + 5) / 6, '?');
    line.front() += order;
    unsigned offset = 0;
    for (unsigned right = 1; right < order; ++right)
        for (unsigned left = 0; left < right; ++left, ++offset)
            if (graph[right] & bit(left)) line[1 + offset / 6] += 1 << (5 - offset % 6);
    return line;
}

template <typename Callback>
static bool independent(const Graph& graph, Mask free, int need, const Callback& visit, Mask picked = 0) {
    if (!need) return visit(picked);
    while (std::popcount(free) >= need) {
        const int vertex = pop_vertex(free);
        if (independent(graph, free & ~graph[vertex], need - 1, visit, picked | bit(vertex))) return true;
    }
    return false;
}

struct Library {
    const Graph& graph;
    int minimum, maximum;
    std::vector<Mask> columns;
    std::vector<std::vector<Mask>> buffer;
    std::uint64_t nodes = 0;

    Library(const Graph& base, int low, int high) : graph(base), minimum(low), maximum(high), buffer(high + 1) {}

    void tails(Mask picked, Mask free, int size) {
        if (size >= minimum) columns.push_back(picked);
        if (size == maximum) return;
        while (size + std::popcount(free) >= minimum && free) {
            const int vertex = pop_vertex(free);
            tails(picked | bit(vertex), free & ~graph[vertex], size + 1);
        }
    }

    void covers(Mask picked, Mask free, int size) {
        ++nodes;
        if (size + std::popcount(free) < minimum) return;
        const auto& demands = buffer[size];
        if (demands.empty()) { tails(picked, free, size); return; }
        if (size == maximum) return;
        int width = 65;
        Mask chosen = 0;
        for (const Mask demand : demands) {
            const Mask options = demand & free;
            if (!options) return;
            if (std::popcount(options) < width) {
                chosen = options;
                width = std::popcount(options);
            }
        }
        while (chosen) {
            const int vertex = pop_vertex(chosen);
            const Mask selected = bit(vertex);
            free ^= selected;
            auto& next = buffer[size + 1];
            next.clear();
            for (const Mask demand : demands)
                if (!(demand & selected)) next.push_back(demand);
            covers(picked | selected, free & ~graph[vertex], size + 1);
        }
    }
};

struct Relation { std::size_t index; unsigned status; };

struct Option {
    std::size_t index;
    std::array<unsigned, 3> statuses{};
};

struct Patterns {
    Mask triangle_free = 0;
    std::array<Mask, 6> edge_on{};
    std::array<Mask, 16> stable{};
    std::vector<std::pair<unsigned, Mask>> independent_triples;
    std::array<Loads, 64> degrees{};

    explicit Patterns(int poles) {
        const unsigned npairs = poles * (poles - 1) / 2;
        const unsigned count = 1u << npairs;
        for (unsigned pattern = 0; pattern < count; ++pattern) {
            unsigned shift = 0;
            for (int right = 1; right < poles; ++right)
                for (int left = 0; left < right; ++left, ++shift)
                    if (pattern & (1u << shift)) {
                        edge_on[shift] |= bit(pattern);
                        ++degrees[pattern][left];
                        ++degrees[pattern][right];
                    }
        }
        Mask cyclic = 0;
        for (int third = 2; third < poles; ++third)
            for (int second = 1; second < third; ++second)
                for (int first = 0; first < second; ++first) {
                    const Mask lh = edge_on[second * (second - 1) / 2 + first];
                    const Mask lr = edge_on[third * (third - 1) / 2 + first];
                    const Mask hr = edge_on[third * (third - 1) / 2 + second];
                    cyclic |= lh & lr & hr;
                    independent_triples.push_back({(1u << first) | (1u << second) | (1u << third), ~(lh | lr | hr)});
                }
        triangle_free = (count == 64 ? ~Mask{0} : bit(count) - 1) & ~cyclic;
        for (unsigned subset = 1; subset < (1u << poles); ++subset) {
            stable[subset] = triangle_free;
            for (int right = 1; right < poles; ++right)
                for (int left = 0; left < right; ++left)
                    if ((subset & (1u << left)) && (subset & (1u << right)))
                        stable[subset] &= ~edge_on[right * (right - 1) / 2 + left];
        }
    }
};

struct Join {
    const Graph& base;
    const int add, forbidden, low, high, low_edges, high_edges;
    const Mask universe;
    std::array<Mask, 5> needs{}, limits{};
    int edges = 0;
    std::uint64_t links = 0, triples = 0, quadruples = 0, cap;
    Counts outputs{};
    std::ostream& models;
    const int row;

    Join(const Graph& core, int poles, int k, int minimum, int min_edges, int max_edges,
         std::uint64_t output_cap, std::ostream& stream, int index)
        : base(core), add(poles), forbidden(k), low(minimum), high(k - 1), low_edges(min_edges),
          high_edges(max_edges), universe(bit(base.size()) - 1), cap(output_cap), models(stream), row(index) {
        for (unsigned vertex = 0; vertex < base.size(); ++vertex) {
            const int degree = std::popcount(base[vertex]);
            edges += degree;
            for (int count = 0; count <= add; ++count) {
                if (degree + count < low && count < add) needs[count + 1] |= bit(vertex);
                if (degree + count > high) limits[count] |= bit(vertex);
            }
        }
        edges /= 2;
    }

    bool misses(Mask neighborhood, int poles) const {
        return independent(base, universe & ~neighborhood, forbidden - poles, [](Mask) { return true; });
    }

    Graph build(const Columns& columns, unsigned pattern) const {
        const unsigned order = base.size();
        Graph graph = base;
        for (int index = 0; index < add; ++index) {
            graph.push_back(columns[index]);
            Mask base_neighbors = columns[index];
            while (base_neighbors) graph[pop_vertex(base_neighbors)] |= bit(order + index);
        }
        unsigned shift = 0;
        for (int right = 1; right < add; ++right)
            for (int left = 0; left < right; ++left, ++shift)
                if ((pattern >> shift) & 1) {
                    graph[order + left] |= bit(order + right);
                    graph[order + right] |= bit(order + left);
                }
        return graph;
    }

    bool keep(const Columns& columns, const Loads& degrees, unsigned pattern) {
        const int internal = std::popcount(pattern);
        int total = edges + internal;
        for (int index = 0; index < add; ++index) {
            const int degree = std::popcount(columns[index]);
            if (degree + degrees[index] < low || degree + degrees[index] > high) return true;
            total += degree;
        }
        if (total < low_edges || total > high_edges) return true;
        if (cap == 0) return false;
        --cap;
        ++outputs[internal];
        models << row << '\t' << internal << '\t' << encode(build(columns, pattern)) << '\n';
        return true;
    }

    bool degrees_ok(const std::array<Mask, 5>& layers) const {
        for (int load = 1; load <= add; ++load)
            if ((needs[load] & ~layers[load]) || (limits[load] & layers[load])) return false;
        return !limits[0];
    }

    bool finish(const Columns& columns, Mask patterns, const Patterns& supported) {
        std::array<Mask, 5> layers{};
        int cross = 0;
        for (int index = 0; index < add; ++index) {
            for (int load = index + 1; load >= 2; --load) layers[load] |= layers[load - 1] & columns[index];
            layers[1] |= columns[index];
            cross += std::popcount(columns[index]);
        }
        if (edges + cross > high_edges || edges + cross + (add == 3 ? 2 : 4) < low_edges || !degrees_ok(layers))
            return true;
        for (const auto& [subset, restricted] : supported.independent_triples) {
            if (!(patterns & restricted)) continue;
            Mask possible = 0;
            Mask members = subset;
            while (members) possible |= columns[pop_vertex(members)];
            if (misses(possible, 3)) patterns &= ~restricted;
        }
        if (add == 4 && (patterns & 1) && misses(layers[1], 4)) patterns ^= 1;
        while (patterns) {
            const int pattern = pop_vertex(patterns);
            if (!keep(columns, supported.degrees[pattern], pattern)) return false;
        }
        return true;
    }

    bool walk(const std::vector<Mask>& columns, const std::vector<std::vector<Relation>>& forward,
              const Patterns& supported, Columns& selected, const std::vector<Option>& offered,
              int depth, Mask patterns) {
        const int pair_start = depth * (depth - 1) / 2;
        for (std::size_t index = 0; index < offered.size(); ++index) {
            const auto& current = offered[index];
            if (depth == 2) ++triples;
            if (depth == 3) ++quadruples;
            selected[depth] = columns[current.index];
            Mask next_patterns = patterns;
            for (int prior = 0; prior < depth; ++prior) {
                const Mask on = supported.edge_on[pair_start + prior];
                if (current.statuses[prior] == 1) next_patterns &= ~on;
                if (current.statuses[prior] == 2) next_patterns &= on;
            }
            if (!next_patterns) continue;
            if (depth + 1 == add) {
                if (!finish(selected, next_patterns, supported)) return false;
            } else {
                const auto& related = forward[current.index];
                std::vector<Option> next;
                std::size_t left = index, right = 0;
                while (left < offered.size() && right < related.size()) {
                    if (offered[left].index < related[right].index) { ++left; continue; }
                    if (offered[left].index > related[right].index) { ++right; continue; }
                    next.push_back(offered[left++]);
                    next.back().statuses[depth] = related[right++].status;
                }
                if (!walk(columns, forward, supported, selected, next, depth + 1, next_patterns)) return false;
            }
        }
        return true;
    }

    bool run(const std::vector<Mask>& columns) {
        std::vector<std::vector<Relation>> forward(columns.size());
        for (std::size_t first = 0; first < columns.size(); ++first) {
            const Mask left = columns[first];
            std::vector<Mask> missing;
            independent(base, universe & ~left, forbidden - 2, [&](Mask set) { missing.push_back(set); return false; });
            for (std::size_t second = first; second < columns.size(); ++second) {
                const Mask right = columns[second];
                const Mask shared = left & right;
                if (limits[2] & shared) continue;
                if (add == 2 && !degrees_ok({0, left | right, shared, 0, 0})) continue;
                unsigned status = !shared ? 2 : 0;
                if (std::all_of(missing.begin(), missing.end(), [&](Mask set) { return bool(set & right); })) status |= 1;
                if (!status) continue;
                ++links;
                if (add == 2) {
                    for (unsigned edge = 0; edge < 2; ++edge)
                        if (status & (1u << edge))
                            if (!keep({left, right, 0, 0}, {int(edge), int(edge), 0, 0}, edge)) return false;
                } else forward[first].push_back({second, status});
            }
        }
        if (add == 2) return true;
        static const Patterns three(3), four(4);
        const auto& supported = add == 3 ? three : four;
        for (std::size_t first = 0; first < columns.size(); ++first) {
            std::vector<Option> options;
            options.reserve(forward[first].size());
            for (const auto relation : forward[first]) options.push_back({relation.index, {relation.status, 0, 0}});
            Columns selected{columns[first], 0, 0, 0};
            if (!walk(columns, forward, supported, selected, options, 1, supported.triangle_free)) return false;
        }
        return true;
    }
};

struct Score {
    Mask mask;
    std::uint64_t misses;
    int degree;
};

struct SoftJoin {
    const Join& join;
    const std::uint64_t ceiling;
    std::uint64_t best;
    std::vector<std::pair<Mask, std::uint64_t>> weighted;
    std::vector<Score> columns;
    Columns optimum{};
    unsigned edges_on_poles = 0;
    std::uint64_t leaves = 0, pairs = 0, triples = 0;
    using Totals = std::array<std::uint64_t, 64>;
    using Layers = std::array<Mask, 5>;

    SoftJoin(const Join& problem, std::uint64_t ceiling_score)
        : join(problem), ceiling(ceiling_score), best(ceiling + 1) {}

    void gather(Mask selected, Mask available, int degree) {
        const int needed = std::max(0, join.low - join.add + 1);
        if (degree + std::popcount(available) < needed) return;
        if (degree >= needed) {
            ++leaves;
            std::uint64_t misses = 0;
            for (const auto& [constraint, weight] : weighted)
                if (!(constraint & selected) && (misses += weight) > ceiling) break;
            if (misses <= ceiling) columns.push_back({selected, misses, degree});
        }
        if (degree == join.high) return;
        while (available) {
            const int vertex = pop_vertex(available);
            gather(selected | bit(vertex), available & ~join.base[vertex], degree + 1);
        }
    }

    void enumerate_columns() {
        const Mask allowed = join.universe & ~join.limits[1];
        std::vector<Mask> projected;
        independent(join.base, join.universe, join.forbidden - 1, [&](Mask set) {
            projected.push_back(set & allowed);
            return false;
        });
        std::sort(projected.begin(), projected.end());
        for (const Mask set : projected) {
            if (!weighted.empty() && weighted.back().first == set) ++weighted.back().second;
            else weighted.push_back({set, 1});
        }
        if (!weighted.empty() && weighted.front().first == 0 && weighted.front().second > ceiling) return;
        gather(0, allowed, 0);
        std::sort(columns.begin(), columns.end(), [](const Score& left, const Score& right) {
            return left.misses != right.misses ? left.misses < right.misses : left.mask < right.mask;
        });
    }

    void search_pairs() {
        for (std::size_t first = 0; first < columns.size(); ++first) {
            const auto& left = columns[first];
            if (left.misses + left.misses >= best) break;
            for (std::size_t second = first; second < columns.size(); ++second) {
                const auto& right = columns[second];
                const std::uint64_t subtotal = left.misses + right.misses;
                if (subtotal >= best) break;
                const Mask both = left.mask | right.mask;
                const Mask shared = left.mask & right.mask;
                if (!join.degrees_ok({0, both, shared, 0, 0})) continue;
                ++pairs;
                const int edges = join.edges + left.degree + right.degree;
                if (!shared && left.degree + 1 >= join.low && right.degree + 1 >= join.low &&
                    left.degree + 1 <= join.high && right.degree + 1 <= join.high &&
                    edges + 1 >= join.low_edges && edges + 1 <= join.high_edges) {
                    best = subtotal;
                    optimum = {left.mask, right.mask, 0, 0};
                    edges_on_poles = 1;
                } else if (left.degree >= join.low && right.degree >= join.low &&
                           edges >= join.low_edges && edges <= join.high_edges) {
                    std::uint64_t total = subtotal;
                    independent(join.base, join.universe & ~both, join.forbidden - 2, [&](Mask) {
                        return ++total >= best;
                    });
                    if (total < best) {
                        best = total;
                        optimum = {left.mask, right.mask, 0, 0};
                        edges_on_poles = 0;
                    }
                }
            }
        }
    }

    void search_triples() {
        static const Patterns supported(3);
        for (std::size_t first = 0; first < columns.size(); ++first) {
            const auto& left = columns[first];
            if (3 * left.misses >= best) break;
            for (std::size_t second = first; second < columns.size(); ++second) {
                const auto& middle = columns[second];
                if (left.misses + 2 * middle.misses >= best) break;
                const Mask first_union = left.mask | middle.mask;
                const Mask first_shared = left.mask & middle.mask;
                if (first_shared & join.limits[2]) continue;
                ++pairs;
                for (std::size_t third = second; third < columns.size(); ++third) {
                    const auto& right = columns[third];
                    const std::uint64_t subtotal = left.misses + middle.misses + right.misses;
                    if (subtotal >= best) break;
                    const Mask all = first_union | right.mask;
                    const Mask shared = first_shared | (first_union & right.mask);
                    if (!join.degrees_ok({0, all, shared, first_shared & right.mask, 0})) continue;
                    const int outside_edges = join.edges + left.degree + middle.degree + right.degree;
                    if (outside_edges > join.high_edges || outside_edges + 2 < join.low_edges) continue;
                    ++triples;
                    const unsigned allowed = (first_shared ? 0 : 1) | ((left.mask & right.mask) ? 0 : 2) |
                                             ((middle.mask & right.mask) ? 0 : 4);
                    const std::array<Mask, 3> pair_unions{first_union, left.mask | right.mask, middle.mask | right.mask};
                    const std::array<int, 3> degrees{left.degree, middle.degree, right.degree};
                    const Columns witness{left.mask, middle.mask, right.mask, 0};
                    std::array<std::uint64_t, 3> pair_misses{};
                    unsigned counted = 0;
                    for (const unsigned pattern : {6u, 5u, 3u, 4u, 2u, 1u, 0u}) {
                        if (subtotal >= best) break;
                        if (pattern & ~allowed) continue;
                        const int total_edges = outside_edges + std::popcount(pattern);
                        if (total_edges < join.low_edges || total_edges > join.high_edges) continue;
                        bool legal = true;
                        for (unsigned pole = 0; pole < degrees.size(); ++pole) {
                            const int degree = degrees[pole] + supported.degrees[pattern][pole];
                            legal &= degree >= join.low && degree <= join.high;
                        }
                        if (!legal) continue;
                        std::uint64_t total = subtotal;
                        for (unsigned pair = 0; pair < pair_unions.size() && total < best; ++pair) {
                            if (pattern & (1u << pair)) continue;
                            if (!(counted & (1u << pair))) {
                                independent(join.base, join.universe & ~pair_unions[pair], join.forbidden - 2, [&](Mask) {
                                    return ++pair_misses[pair] >= best - subtotal;
                                });
                                counted |= 1u << pair;
                            }
                            total += pair_misses[pair];
                        }
                        if (!pattern && total < best)
                            independent(join.base, join.universe & ~all, join.forbidden - 3, [&](Mask) {
                                return ++total >= best;
                            });
                        if (total < best) {
                            best = total;
                            optimum = witness;
                            edges_on_poles = pattern;
                        }
                    }
                }
            }
        }
    }

    void search_quads(const Patterns& supported, std::size_t start, unsigned depth, int cross,
                      Mask active, const Totals& previous, const Layers& layers,
                      std::array<Mask, 16>& unions, Columns& selected) {
        const unsigned marker = 1u << depth;
        const unsigned remaining = 3 - depth;
        std::uint64_t floor = best;
        for (Mask scan = active; scan;) floor = std::min(floor, previous[pop_vertex(scan)]);
        for (std::size_t index = start; index < columns.size(); ++index) {
            const auto& column = columns[index];
            const std::uint64_t tail = remaining * column.misses;
            if (floor + column.misses + tail >= best) break;
            const int edges = cross + column.degree;
            if (edges > join.high_edges || edges + 4 + static_cast<int>(remaining) * join.high < join.low_edges) continue;
            Layers next = layers;
            bool fits = true;
            for (unsigned load = depth + 1; load >= 1; --load) {
                next[load] |= column.mask & (load == 1 ? join.universe : layers[load - 1]);
                if (next[load] & join.limits[load]) fits = false;
            }
            if (!fits || (!remaining && !join.degrees_ok(next))) continue;
            Mask allowed = active;
            for (unsigned earlier = 0; earlier < depth; ++earlier)
                if (column.mask & selected[earlier]) allowed &= ~supported.edge_on[depth * (depth - 1) / 2 + earlier];
            Totals total;
            for (Mask scan = allowed; scan;) {
                const int pattern = pop_vertex(scan);
                const int internal = std::popcount(static_cast<unsigned>(pattern));
                const int degree = column.degree + supported.degrees[pattern][depth];
                if (degree < join.low || degree > join.high || edges + internal > join.high_edges ||
                    edges + internal + static_cast<int>(remaining) * join.high < join.low_edges ||
                    previous[pattern] + column.misses + tail >= best) {
                    allowed &= ~bit(pattern);
                    continue;
                }
                total[pattern] = previous[pattern] + column.misses;
            }
            if (!allowed) continue;
            if (depth == 1) ++pairs;
            if (depth == 2) ++triples;
            for (unsigned subset = 0; subset < marker && allowed; ++subset) {
                unions[marker | subset] = unions[subset] | column.mask;
                if (!subset) continue;
                const Mask charged = allowed & supported.stable[marker | subset];
                if (!charged) continue;
                std::uint64_t min_total = best;
                for (Mask scan = charged; scan;) min_total = std::min(min_total, total[pop_vertex(scan)]);
                std::uint64_t missing = 0;
                independent(join.base, join.universe & ~unions[marker | subset],
                            join.forbidden - 1 - std::popcount(subset), [&](Mask) {
                    return ++missing >= best - tail - min_total;
                });
                for (Mask scan = charged; scan;) {
                    const int pattern = pop_vertex(scan);
                    total[pattern] += missing;
                    if (total[pattern] + tail >= best) allowed &= ~bit(pattern);
                }
            }
            if (!allowed) continue;
            selected[depth] = column.mask;
            if (remaining) {
                search_quads(supported, index, depth + 1, edges, allowed, total, next, unions, selected);
            } else {
                for (Mask scan = allowed; scan;) {
                    const int pattern = pop_vertex(scan);
                    if (total[pattern] < best) {
                        best = total[pattern];
                        optimum = selected;
                        edges_on_poles = pattern;
                    }
                }
            }
        }
    }

    void run(std::uint64_t fixed_score = 0) {
        enumerate_columns();
        if (join.add == 2) search_pairs();
        else if (join.add == 3) search_triples();
        else {
            static const Patterns four(4);
            std::array<Mask, 16> unions{};
            Columns selected{};
            search_quads(four, 0, 0, join.edges, four.triangle_free, {}, {}, unions, selected);
        }
        if (best <= ceiling)
            join.models << join.row << '\t' << best + fixed_score << '\t' << encode(join.build(optimum, edges_on_poles)) << '\n';
    }
};

int main(int argc, char** argv) {
    if (argc < 9 || argc > 11) {
        std::cerr << "usage: pole_join CORES.g6 POLES K MIND MINEDGES MAXEDGES PER_CORE_CAP OUTPUT.tsv [SCORE_CEILING [--include-fixed]]\n";
        return 2;
    }
    const int add = std::stoi(argv[2]), forbidden = std::stoi(argv[3]), low = std::stoi(argv[4]);
    const int min_edges = std::stoi(argv[5]), max_edges = std::stoi(argv[6]);
    const auto cap = std::stoull(argv[7]);
    const bool soft = argc >= 10;
    const auto ceiling = soft ? std::stoull(argv[9]) : 0;
    const bool include_fixed = argc == 11 && std::string(argv[10]) == "--include-fixed";
    if (add < 2 || add > 4 || forbidden <= add || forbidden > 62 || low < 0 || low >= forbidden ||
        min_edges < 0 || min_edges > max_edges || cap == 0 || (soft && ceiling > (1ULL << 60)) ||
        (argc == 11 && !include_fixed)) return 2;
    std::ifstream input(argv[1]);
    std::ofstream models(argv[8]);
    if (!input || !models) return 2;
    if (soft) {
        models << "row\tI_k\tgraph6\n";
        std::cout << "row\tstatus\tcolumns\tleaves\tpairs\ttriples\tI_k\n";
    } else {
        models << "row\tinternal_edges\tgraph6\n";
        std::cout << "row\tstatus\tcolumns\tcover_nodes\tlinks\ttriples\tquadruples\tedges0\tedges1\tedges2\tedges3\tedges4\n";
    }
    std::string line;
    int row = 0, unresolved = 0;
    while (std::getline(input, line)) {
        const Graph base = decode(line);
        if (base.size() + add >= 63) throw std::runtime_error("order out of range");
        Join join(base, add, forbidden, low, min_edges, max_edges, cap, models, row);
        Library library(base, std::max(0, low - add + 1), forbidden - 1);
        bool valid = true, eligible = true;
        for (const Mask mask : base) {
            Mask neighbors = mask;
            while (neighbors) if (base[pop_vertex(neighbors)] & mask) valid = false;
            if (std::popcount(mask) < low - add || std::popcount(mask) >= forbidden) eligible = false;
        }
        std::uint64_t fixed_score = 0;
        if (valid && include_fixed) {
            independent(base, join.universe, forbidden, [&](Mask) { return ++fixed_score > ceiling; });
        } else if (valid && join.misses(0, 0)) valid = false;
        const char* status = valid ? "complete" : "bad_core";
        const bool maybe = valid && eligible && join.edges <= max_edges && join.edges + add * (forbidden - 1) >= min_edges;
        if (soft) {
            const std::uint64_t spare = fixed_score <= ceiling ? ceiling - fixed_score : 0;
            SoftJoin optimization(join, spare);
            if (maybe && fixed_score <= ceiling) optimization.run(fixed_score);
            std::cout << row++ << '\t' << status << '\t' << optimization.columns.size() << '\t'
                      << optimization.leaves << '\t' << optimization.pairs << '\t' << optimization.triples << '\t';
            if (optimization.best <= spare) std::cout << optimization.best + fixed_score;
            else std::cout << "NA";
            std::cout << std::endl;
            models.flush();
            continue;
        }
        if (maybe) {
            const Mask allowed = join.universe & ~join.limits[1];
            independent(base, join.universe, forbidden - 1, [&](Mask set) {
                library.buffer.front().push_back(set & allowed);
                return false;
            });
            auto& constraints = library.buffer.front();
            std::sort(constraints.begin(), constraints.end());
            constraints.erase(std::unique(constraints.begin(), constraints.end()), constraints.end());
            library.covers(0, allowed, 0);
            std::sort(library.columns.begin(), library.columns.end());
            if (std::adjacent_find(library.columns.begin(), library.columns.end()) != library.columns.end())
                throw std::runtime_error("duplicate neighborhood");
            if (!join.run(library.columns)) { status = "output_cap"; ++unresolved; }
        }
        std::cout << row++ << '\t' << status << '\t' << library.columns.size() << '\t' << library.nodes << '\t'
                  << join.links << '\t' << join.triples << '\t' << join.quadruples;
        for (const auto count : join.outputs) std::cout << '\t' << count;
        std::cout << std::endl;
        models.flush();
    }
    if (!row || !input.eof() || !models) return 2;
    std::cerr << "terminal rows=" << row << " capped=" << unresolved << '\n';
    return unresolved ? 3 : 0;
}
