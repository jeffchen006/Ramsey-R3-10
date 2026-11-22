#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <ctime>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Mask = uint64_t;
using Graph = std::vector<Mask>;
using Columns = std::array<Mask, 5>;

static Mask bit(int index) { return Mask{1} << index; }
static int pop(Mask mask) { return std::popcount(mask); }

static int take(Mask &mask) {
    int index = std::countr_zero(mask);
    mask &= mask - 1;
    return index;
}

static void require(bool condition, const char *message) {
    if (!condition) throw std::runtime_error(message);
}

static Graph decode(const std::string &row) {
    require(!row.empty(), "empty graph6");
    int order = row[0] - 63, offset = 0;
    require(order >= 1 && order <= 27 && row.size() == size_t(1 + (order*(order-1)/2 + 5)/6),
            "wrong graph6 size");
    for (char byte : row) require(byte >= 63 && byte <= 126, "wrong graph6 digit");
    Graph graph(order);
    for (int high = 1; high < order; ++high) {
        for (int low = 0; low < high; ++low, ++offset) {
            if (((row[1 + offset/6] - 63) >> (5 - offset%6)) & 1) {
                graph[high] |= bit(low);
                graph[low] |= bit(high);
            }
        }
    }
    if (offset % 6) require(((row.back() - 63) & (bit(6 - offset%6) - 1)) == 0, "nonzero padding");
    return graph;
}

static std::string encode(const Graph &graph) {
    std::string row(1, char(63 + graph.size()));
    int offset = 0, digit = 0;
    for (int high = 1; high < int(graph.size()); ++high) {
        for (int low = 0; low < high; ++low) {
            digit |= int(bool(graph[high] & bit(low))) << (5 - offset);
            if (++offset == 6) { row += char(63 + digit); offset = digit = 0; }
        }
    }
    if (offset) row += char(63 + digit);
    return row;
}

struct Bound { Mask variables; int lower, upper; };
struct Witness { Mask vertices; int contacts; };

class Expansion {
    const Graph core;
    const int order, alpha, slots, min_degree, max_degree, min_edges, max_edges;
    const Mask all;
    int base_edges = 0;
    std::vector<Mask> maximal;
    std::vector<Witness> witnesses;
    std::vector<std::vector<int>> pair;
    Columns top{};
    std::set<Columns> results;
    uint64_t pair_edges = 0, full_tuples = 0, envelopes = 0, nodes = 0, completions = 0;
    std::vector<Bound> bounds;
    std::vector<Mask> clauses;
    std::vector<std::pair<int, int>> variable;

    void independent(Mask remaining, Mask selected, Mask closed) {
        int size = pop(selected);
        require(size < alpha, "core independence violates alpha-1");
        if (closed == all) maximal.push_back(selected);
        int needed = slots + size - alpha;
        if (needed > 0) witnesses.push_back({selected, needed});
        while (remaining) {
            int vertex = take(remaining);
            independent(remaining & ~core[vertex], selected | bit(vertex),
                        closed | core[vertex] | bit(vertex));
        }
    }

    void record(Mask ones) {
        Columns actual{};
        while (ones) {
            auto [slot, vertex] = variable[take(ones)];
            actual[slot] |= bit(vertex);
        }
        std::sort(actual.begin(), actual.begin() + slots);
        results.insert(actual);
        ++completions;
    }

    void enumerate(Mask ones, Mask zeros) {
        ++nodes;
        for (;;) {
            Mask fixed = ones | zeros;
            for (const auto &bound : bounds) {
                int present = pop(bound.variables & ones);
                Mask unset = bound.variables & ~(ones | zeros);
                int possible = present + pop(unset);
                if (present > bound.upper || possible < bound.lower) return;
                if (present == bound.upper) zeros |= unset;
                if (possible == bound.lower) ones |= unset;
            }
            if (ones & zeros) return;
            Mask branch = 0;
            int width = 65;
            for (Mask clause : clauses) {
                if (clause & ones) continue;
                Mask possible = clause & ~zeros;
                int count = pop(possible);
                if (count == 0) return;
                if (count == 1) ones |= possible;
                if (count < width) { width = count; branch = possible; }
            }
            if ((ones | zeros) != fixed) continue;
            if (!branch) branch = (bit(variable.size()) - 1) & ~fixed;
            if (!branch) { record(ones); return; }
            Mask pivot = branch & (~branch + 1);
            enumerate(ones | pivot, zeros);
            enumerate(ones, zeros | pivot);
            return;
        }
    }

    void complete_envelope() {
        variable.clear();
        clauses.clear();
        bounds.clear();
        std::vector<Mask> row(order);
        std::array<Mask, 5> column{};
        std::array<std::vector<Mask>, 5> cross;
        for (int slot = 0; slot < slots; ++slot) {
            cross[slot].resize(order);
            for (Mask vertices = top[slot]; vertices;) {
                int vertex = take(vertices);
                require(variable.size() < 62, "too many physical cross variables");
                Mask singleton = bit(variable.size());
                variable.emplace_back(slot, vertex);
                row[vertex] |= singleton;
                column[slot] |= singleton;
                cross[slot][vertex] |= singleton;
            }
            bounds.push_back({column[slot], min_degree - 1, max_degree - 1});
        }
        for (int vertex = 0; vertex < order; ++vertex)
            bounds.push_back({row[vertex], min_degree - pop(core[vertex]), max_degree - pop(core[vertex])});
        bounds.push_back({bit(variable.size()) - 1, min_edges - base_edges, max_edges - base_edges});

        for (const auto &witness : witnesses) {
            std::array<Mask, 5> local{};
            for (Mask vertices = witness.vertices; vertices;) {
                int vertex = take(vertices);
                for (int slot = 0; slot < slots; ++slot) local[slot] |= cross[slot][vertex];
            }
            int threshold = slots + 1 - witness.contacts;
            for (Mask subset = 1; subset < bit(slots); ++subset) {
                if (pop(subset) != threshold) continue;
                Mask clause = 0;
                for (Mask included = subset; included;) clause |= local[take(included)];
                require(clause != 0, "infeasible envelope reached");
                clauses.push_back(clause);
            }
        }
        std::sort(clauses.begin(), clauses.end());
        clauses.erase(std::unique(clauses.begin(), clauses.end()), clauses.end());
        enumerate(0, 0);
    }

    void pick(int depth, const std::vector<int> &domain) {
        if (depth == slots) {
            ++full_tuples;
            for (const auto &witness : witnesses) {
                if (witness.contacts == slots - 1) continue;
                int contacts = 0;
                for (int slot = 0; slot < slots; ++slot) contacts += bool(top[slot] & witness.vertices);
                if (contacts < witness.contacts) return;
            }
            ++envelopes;
            complete_envelope();
            return;
        }
        for (int next : domain) {
            top[depth] = maximal[next];
            if (depth + 1 == slots) {
                pick(depth + 1, {});
            } else {
                std::vector<int> future;
                std::set_intersection(domain.begin(), domain.end(), pair[next].begin(), pair[next].end(),
                                      std::back_inserter(future));
                if (!future.empty()) pick(depth + 1, future);
            }
        }
    }

public:
    Expansion(Graph input, const std::array<int, 6> &limits)
        : core(std::move(input)), order(core.size()), alpha(limits[0]), slots(limits[1]),
          min_degree(limits[2]), max_degree(limits[3]), min_edges(limits[4]), max_edges(limits[5]),
          all(bit(order) - 1) {
        require(2 <= slots && slots <= 5 && slots <= alpha && alpha <= 8 &&
                min_degree >= 1 && max_degree >= min_degree && min_edges <= max_edges, "unsupported limits");
    }

    void run(int source) {
        std::clock_t started = std::clock();
        for (int vertex = 0; vertex < order; ++vertex) {
            base_edges += pop(core[vertex]);
            for (Mask neighbours = core[vertex]; neighbours;)
                require(!(core[vertex] & core[take(neighbours)]), "core triangle");
        }
        base_edges = base_edges/2 + slots;
        independent(all, 0, 0);
        std::vector<int> domain;
        pair.resize(maximal.size());
        if (min_degree <= slots && slots <= max_degree) {
            std::vector<Mask> critical;
            for (const auto &witness : witnesses) if (witness.contacts == slots - 1) critical.push_back(witness.vertices);
            for (int first = 0; first < int(maximal.size()); ++first) {
                domain.push_back(first);
                for (int second = first; second < int(maximal.size()); ++second) {
                    Mask touched = maximal[first] | maximal[second];
                    if (std::all_of(critical.begin(), critical.end(), [=](Mask set) { return set & touched; })) {
                        pair[first].push_back(second);
                        ++pair_edges;
                    }
                }
            }
            pick(0, domain);
        }
        for (const auto &actual : results) {
            Graph graph = core;
            graph.resize(order + slots + 1);
            int root = order + slots, edges = base_edges;
            for (int slot = 0; slot < slots; ++slot) {
                int outer = order + slot;
                graph[root] |= bit(outer);
                graph[outer] = bit(root) | actual[slot];
                edges += pop(actual[slot]);
                for (Mask vertices = actual[slot]; vertices;) graph[take(vertices)] |= bit(outer);
            }
            std::cout << source << '\t' << edges << '\t' << encode(graph) << '\n';
        }
        std::cerr << source << '\t' << maximal.size() << '\t' << pair_edges << '\t' << full_tuples << '\t'
                  << envelopes << '\t' << nodes << '\t' << completions << '\t' << results.size() << '\t'
                  << double(std::clock() - started) / CLOCKS_PER_SEC << '\n';
    }
};

int main(int argc, char **argv) {
    try {
        require(argc == 7, "usage: expand alpha slots dmin dmax emin emax < ID-tab-graph6");
        std::array<int, 6> limits{};
        for (int index = 0; index < 6; ++index) limits[index] = std::stoi(argv[index + 1]);
        std::cerr << "id\tmaximal\tpair_edges\tfull_tuples\tenvelopes\tnodes\tcompletions\tunique\tcpu_s\n";
        std::set<int> seen;
        for (std::string line; std::getline(std::cin, line);) {
            std::istringstream stream(line);
            int source;
            std::string row, extra;
            require(bool(stream >> source >> row) && !(stream >> extra) && source >= 1 && seen.insert(source).second,
                    "bad source record");
            Expansion(decode(row), limits).run(source);
        }
        require(std::cin.eof() && bool(std::cout) && !seen.empty(), "incomplete I/O");
        return 0;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
