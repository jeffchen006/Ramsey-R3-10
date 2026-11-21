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

struct SoftPair {
    const Join& join;
    const std::uint64_t ceiling;
    std::uint64_t best;
    std::vector<std::pair<Mask, std::uint64_t>> weighted;
    std::vector<Score> columns;
    Columns optimum{};
    unsigned edge = 0;
    std::uint64_t leaves = 0, pairs = 0;

    SoftPair(const Join& problem, std::uint64_t ceiling_score)
        : join(problem), ceiling(ceiling_score), best(ceiling + 1) {}

    void gather(Mask selected, Mask available, int degree) {
        const int needed = std::max(0, join.low - 1);
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

    void run() {
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
                    edge = 1;
                } else if (left.degree >= join.low && right.degree >= join.low &&
                           edges >= join.low_edges && edges <= join.high_edges) {
                    std::uint64_t total = subtotal;
                    independent(join.base, join.universe & ~both, join.forbidden - 2, [&](Mask) {
                        return ++total >= best;
                    });
                    if (total < best) {
                        best = total;
                        optimum = {left.mask, right.mask, 0, 0};
                        edge = 0;
                    }
                }
            }
        }
        if (best <= ceiling)
            join.models << join.row << '\t' << best << '\t' << encode(join.build(optimum, edge)) << '\n';
    }
};

int main(int argc, char** argv) {
    if (argc != 9 && argc != 10) {
        std::cerr << "usage: pole_join CORES.g6 POLES K MIND MINEDGES MAXEDGES PER_CORE_CAP OUTPUT.tsv [PAIR_SCORE_CEILING]\n";
        return 2;
    }
    const int add = std::stoi(argv[2]), forbidden = std::stoi(argv[3]), low = std::stoi(argv[4]);
    const int min_edges = std::stoi(argv[5]), max_edges = std::stoi(argv[6]);
    const auto cap = std::stoull(argv[7]);
    const bool soft = argc == 10;
    const auto ceiling = soft ? std::stoull(argv[9]) : 0;
    if (add < 2 || add > 4 || forbidden <= add || forbidden > 62 || low < 0 || low >= forbidden ||
        min_edges < 0 || min_edges > max_edges || cap == 0 || (soft && (add != 2 || ceiling > (1ULL << 60)))) return 2;
    std::ifstream input(argv[1]);
    std::ofstream models(argv[8]);
    if (!input || !models) return 2;
    if (soft) {
        models << "row\tI_k\tgraph6\n";
        std::cout << "row\tstatus\tcolumns\tleaves\tpairs\tI_k\n";
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
        if (valid && join.misses(0, 0)) valid = false;
        const char* status = valid ? "complete" : "bad_core";
        const bool maybe = valid && eligible && join.edges <= max_edges && join.edges + add * (forbidden - 1) >= min_edges;
        if (soft) {
            SoftPair optimization(join, ceiling);
            if (maybe) optimization.run();
            std::cout << row++ << '\t' << status << '\t' << optimization.columns.size() << '\t'
                      << optimization.leaves << '\t' << optimization.pairs << '\t';
            if (optimization.best <= ceiling) std::cout << optimization.best;
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
