#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

using Mask = std::uint32_t;
using Graph = std::vector<Mask>;
using Profile = std::tuple<int, int, int, int>;
using Census = std::map<Profile, std::uint64_t>;

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

Mask bit(int site) { return Mask{1} << site; }
int size(Mask mask) { return std::popcount(mask); }
int first(Mask mask) { return std::countr_zero(mask); }

template<typename Visit>
void each(Mask mask, Visit visit) {
    while (mask) {
        visit(first(mask));
        mask &= mask - 1;
    }
}

std::vector<Graph> load(const char* path, int order, int expected) {
    std::ifstream input(path);
    require(bool(input), "missing catalogue");
    std::set<std::string> records;
    std::vector<Graph> catalogue;
    const int width = order * (order - 1) / 2;
    for (std::string line; std::getline(input, line);) {
        require(line.size() == 1U + (width + 5) / 6 && line[0] == 63 + order,
                "wrong graph6 order or width");
        require(std::all_of(line.begin(), line.end(), [](unsigned char byte) {
            return byte >= 63 && byte <= 126;
        }), "invalid graph6 byte");
        require(((line.back() - 63) & ((1 << ((6 - width % 6) % 6)) - 1)) == 0,
                "nonzero graph6 padding");
        require(records.insert(line).second, "duplicate literal catalogue record");
        Graph graph(order);
        int offset = 0;
        for (int high = 1; high < order; ++high) for (int low = 0; low < high; ++low, ++offset) {
            if ((line[1 + offset / 6] - 63) & (1 << (5 - offset % 6))) {
                graph[low] |= bit(high);
                graph[high] |= bit(low);
            }
        }
        for (int site = 0; site < order; ++site) each(graph[site], [&](int other) {
            require(!(graph[site] & graph[other]), "triangle in catalogue");
        });
        catalogue.push_back(std::move(graph));
    }
    require(input.eof() && !input.bad() && int(catalogue.size()) == expected,
            "wrong catalogue count");
    return catalogue;
}

template<typename Visit>
void independent(const Graph& graph, Mask available, Mask chosen, int need, Visit& visit) {
    if (!need) {
        visit(chosen);
        return;
    }
    while (size(available) >= need) {
        const int site = first(available);
        available &= available - 1;
        independent(graph, available & ~graph[site], chosen | bit(site), need - 1, visit);
    }
}

struct Enumerator {
    const Graph& graph;
    int roots, degree, cap;
    Mask full;
    std::vector<Mask> marks;
    std::vector<std::vector<int>> successors;
    std::vector<std::vector<bool>> compatible;
    std::array<Mask, 4> chosen{};
    Census counts;
    int total_degree = 0, host;
    bool emit, allowed = true;

    Enumerator(const Graph& graph_, int roots_, int degree_, int cap_, int alpha,
               int host_, bool emit_)
        : graph(graph_), roots(roots_), degree(degree_), cap(cap_), full(bit(graph.size()) - 1),
          host(host_), emit(emit_) {
        auto reject = [](Mask) { require(false, "catalogue alpha bound violated"); };
        independent(graph, full, 0, alpha + 1, reject);
        std::vector<Mask> partner(graph.size());
        for (int site = 0; site < int(graph.size()); ++site) {
            total_degree += size(graph[site]);
            if (size(graph[site]) > degree) allowed = false;
            for (int other = 0; other < site; ++other) {
                const int common = size(graph[site] & graph[other]);
                if (common > cap) allowed = false;
                if (common >= cap) partner[site] |= bit(other);
            }
        }
        if (!allowed) return;
        auto keep = [&](Mask mark) {
            bool good = true;
            each(mark, [&](int site) {
                if ((partner[site] & mark) || size(graph[site]) >= degree) good = false;
            });
            if (good) marks.push_back(mark);
        };
        independent(graph, full, 0, degree - roots, keep);
        std::sort(marks.begin(), marks.end());
        successors.resize(marks.size());
        compatible.assign(marks.size(), std::vector<bool>(marks.size()));
        for (int left = 0; left < int(marks.size()); ++left) {
            for (int right = left + 1; right < int(marks.size()); ++right) {
                if (size(marks[left] & marks[right]) > cap - roots) continue;
                compatible[left][right] = true;
                successors[left].push_back(right);
            }
        }
    }

    void record(Mask united, Mask repeated) {
        const int neutral = first(full ^ united), neutral_degree = size(graph[neutral]);
        const int private_degree = total_degree - neutral_degree;
        std::array<int, 4> singletons{};
        int triples = 0;
        bool admissible = true;
        each(repeated, [&](int site) {
            int incidence = 0;
            for (int root = 0; root < roots; ++root) incidence += bool(chosen[root] & bit(site));
            if (size(graph[site]) + incidence > degree) admissible = false;
            if (incidence == 3) ++triples;
        });
        if (!admissible) return;
        for (int root = 0; root < roots; ++root) singletons[root] = size(chosen[root] & ~repeated);
        std::sort(singletons.begin(), singletons.end(), std::greater<int>());
        int shape = 0;
        for (int root = 0; root < roots; ++root) shape = 10 * shape + singletons[root];
        if (roots == 4 && graph.size() == 16)
            require((shape == 3322 && triples == 0) || (shape == 3332 && triples == 1),
                    "unexpected 16-window incidence shape");
        if (roots == 4 && graph.size() == 17)
            require(((shape == 3333 || shape == 4332) && triples == 0) ||
                    (shape == 4333 && triples == 1), "unexpected 17-window incidence shape");
        ++counts[{private_degree, neutral_degree, shape, triples}];
        if (emit) {
            std::cout << host << '\t' << neutral;
            for (int root = 0; root < roots; ++root) std::cout << '\t' << chosen[root];
            std::cout << '\t' << private_degree << '\t' << neutral_degree << '\n';
        }
    }

    void run() {
        const int target = size(full) - 1;
        const int mark_size = degree - roots;
        for (int one = 0; one < int(marks.size()); ++one) {
            chosen[0] = marks[one];
            for (int two : successors[one]) {
                chosen[1] = marks[two];
                const Mask pair = marks[one] | marks[two];
                const Mask repeated_pair = marks[one] & marks[two];
                if (roots == 2) {
                    if (size(pair) == target) record(pair, repeated_pair);
                    continue;
                }
                for (int three : successors[two]) {
                    if (!compatible[one][three]) continue;
                    const Mask triple = pair | marks[three];
                    if (size(triple) > target || size(triple) + mark_size < target) continue;
                    chosen[2] = marks[three];
                    const Mask repeated_triple = repeated_pair | (pair & marks[three]);
                    for (int four : successors[three]) {
                        if (!compatible[one][four] || !compatible[two][four]) continue;
                        const Mask united = triple | marks[four];
                        if (size(united) != target) continue;
                        chosen[3] = marks[four];
                        record(united, repeated_triple | (triple & marks[four]));
                    }
                }
            }
        }
    }
};

int main(int argc, char** argv) try {
    require(argc == 11, "usage: frames MODE G6 ORDER COUNT ROOTS DEGREE CAP ALPHA LOW HIGH");
    const std::string mode = argv[1];
    require(mode == "frames" || mode == "counts" || mode == "price", "invalid output mode");
    const int order = std::stoi(argv[3]), expected = std::stoi(argv[4]), roots = std::stoi(argv[5]);
    const int degree = std::stoi(argv[6]), cap = std::stoi(argv[7]), alpha = std::stoi(argv[8]);
    const int low = std::stoi(argv[9]), high = std::stoi(argv[10]);
    require(order > 0 && order <= 22 && 0 <= low && low < high && high <= expected,
            "invalid host interval/order");
    require((roots == 2 || roots == 4) && roots < degree && cap >= roots && alpha > 0 &&
            degree - roots <= cap, "unexpected root/degree/cap/alpha parameters");
    const auto catalogue = load(argv[2], order, expected);
    std::ios::sync_with_stdio(false);
    for (int host = low; host < high; ++host) {
        Enumerator engine(catalogue[host], roots, degree, cap, alpha, host, mode == "frames");
        if (mode == "price") {
            std::uint64_t upper = 0;
            for (unsigned index = 0; index < engine.marks.size(); ++index) {
                const std::uint64_t rest = engine.successors[index].size();
                if (roots == 2) upper += rest;
                else if (rest >= 3) upper += rest * (rest - 1) * (rest - 2) / 6;
            }
            std::cout << host << '\t' << engine.marks.size() << '\t' << upper << '\n';
            continue;
        }
        engine.run();
        if (mode == "counts") {
            if (engine.counts.empty()) std::cout << host << "\t0\t0\t0\t0\t0\n";
            for (const auto& [profile, total] : engine.counts) {
                const auto [private_degree, neutral_degree, shape, triples] = profile;
                std::cout << host << '\t' << private_degree << '\t' << neutral_degree << '\t'
                          << shape << '\t' << triples << '\t' << total << '\n';
            }
        }
    }
    require(bool(std::cout), "output failure");
    return 0;
} catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 2;
}
