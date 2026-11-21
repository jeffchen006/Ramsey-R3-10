#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>

using Mask = uint32_t;

struct Domain {
    std::array<uint64_t, 16> blocks{};

    void insert(unsigned vertex) { blocks[vertex / 64] |= uint64_t{1} << (vertex % 64); }
    void erase(unsigned vertex) { blocks[vertex / 64] &= ~(uint64_t{1} << (vertex % 64)); }
    void subtract(const Domain &other) {
        for (unsigned index = 0; index < blocks.size(); ++index) blocks[index] &= ~other.blocks[index];
    }
    Domain intersection(const Domain &other) const {
        Domain result;
        for (unsigned index = 0; index < blocks.size(); ++index) result.blocks[index] = blocks[index] & other.blocks[index];
        return result;
    }
    unsigned count() const {
        unsigned total = 0;
        for (uint64_t block : blocks) total += std::popcount(block);
        return total;
    }
};

struct PairConstraint {
    Mask endpoints;
    Domain allowed;
};

class Packing {
public:
    Packing(int degree_arg, int cap_arg, std::vector<Mask> adj_arg)
        : degree(degree_arg), cap(cap_arg), adj(std::move(adj_arg)), width(adj.size()),
          full((Mask{1} << width) - 1), relevant(width) {
        collect(0, full);
        if (colours.size() > Domain{}.blocks.size() * 64) throw std::runtime_error("too many colours");
        forbid.resize(colours.size());
        disjoint_residue.resize(colours.size());
        largest_masks.resize(colours.size());
        allowance.resize(colours.size());
        for (unsigned index = 0; index < colours.size(); ++index) {
            const auto mask = colours[index];
            all.insert(index);
            for (unsigned vertex = 0; vertex < width; ++vertex) {
                if (mask & (Mask{1} << vertex)) relevant[vertex].insert(index);
            }
            for (unsigned other = 0; other < colours.size(); ++other) {
                if (index == other || std::popcount(mask & colours[other]) > cap - 2) forbid[index].insert(other);
                if ((mask & colours[other]) == 0) {
                    disjoint_residue[index].push_back(other);
                    largest_masks[other].insert(index);
                }
            }
        }
        for (unsigned vertex = 0; vertex < width; ++vertex) {
            for (unsigned other = 0; other < vertex; ++other) {
                if ((adj[vertex] & (Mask{1} << other)) || (adj[vertex] & adj[other])) continue;
                missing_pairs.push_back({(Mask{1} << vertex) | (Mask{1} << other), relevant[vertex].intersection(relevant[other])});
            }
        }
        if (missing_pairs.size() > 64) throw std::runtime_error("too many uncovered pairs");
        covered.resize(colours.size());
        for (unsigned index = 0; index < colours.size(); ++index) {
            for (unsigned pair = 0; pair < missing_pairs.size(); ++pair) {
                if ((colours[index] & missing_pairs[pair].endpoints) == missing_pairs[pair].endpoints) {
                    covered[index] |= uint64_t{1} << pair;
                }
            }
        }
    }

    void run(std::array<Mask, 4> side_arg, uint64_t bound_arg, bool profile,
             std::ostream *trace_arg, bool enumerate_arg, uint64_t package_arg) {
        side = side_arg;
        bound = bound_arg;
        trace = trace_arg;
        visits = 0;
        deepest = 0;
        completed = 0;
        found = 0;
        enumerate = enumerate_arg;
        package = package_arg;
        aborted = false;
        chosen.clear();
        demand.fill(0);
        uint64_t required = 0;
        for (unsigned pair = 0; pair < missing_pairs.size(); ++pair) {
            bool already = false;
            for (Mask label : side) already |= (label & missing_pairs[pair].endpoints) == missing_pairs[pair].endpoints;
            if (!already) required |= uint64_t{1} << pair;
        }
        Domain allowed = all;
        int total = 0;
        for (unsigned vertex = 0; vertex < width; ++vertex) {
            const Mask singleton = Mask{1} << vertex;
            demand[vertex] = degree - std::popcount(adj[vertex]);
            for (Mask label : side) demand[vertex] -= (label & singleton) != 0;
            if (demand[vertex] < 1) throw std::runtime_error("package spends all deficit");
            total += demand[vertex];
        }
        if (total != (degree - 2) * (degree - 2)) throw std::runtime_error("bad total C deficit");
        for (unsigned index = 0; index < colours.size(); ++index) {
            allowance[index] = 2 - miss_max(colours[index]);
            if (allowance[index] < 0) throw std::runtime_error("bad package transversal");
            if (allowance[index] == 0) allowed.subtract(largest_masks[index]);
        }
        const bool result = search(allowed, required);
        if (enumerate) {
            std::cout << (aborted ? "cutoff" : "end") << ' ' << package << ' ' << found << ' ' << visits << std::endl;
            return;
        }
        std::cout << (result ? "SAT" : aborted ? "node-limit" : "no-extension") << ' ' << visits;
        if (profile) std::cout << ' ' << deepest << ' ' << completed;
        if (result) {
            for (unsigned index : chosen) std::cout << ' ' << colours[index];
        }
        std::cout << std::endl;
    }

private:
    int degree;
    int cap;
    std::vector<Mask> adj;
    unsigned width;
    Mask full;
    std::vector<Mask> independents;
    std::vector<Mask> colours;
    Domain all;
    std::vector<Domain> relevant;
    std::vector<Domain> forbid;
    std::vector<PairConstraint> missing_pairs;
    std::vector<uint64_t> covered;
    std::vector<Domain> largest_masks;
    std::vector<std::vector<unsigned>> disjoint_residue;
    std::vector<int> allowance;
    std::array<int, 32> demand{};
    std::array<Mask, 4> side{};
    std::vector<unsigned> chosen;
    uint64_t visits = 0;
    uint64_t bound = 0;
    unsigned deepest = 0;
    uint64_t completed = 0;
    uint64_t found = 0;
    uint64_t package = 0;
    bool enumerate = false;
    bool aborted = false;
    std::ostream *trace = nullptr;

    void collect(Mask fixed, Mask rest) {
        const int count = std::popcount(fixed);
        if (count > degree - 2) throw std::runtime_error("residue independence number too large");
        if (count >= 2) independents.push_back(fixed);
        if (count == degree - 2) colours.push_back(fixed);
        while (rest != 0) {
            unsigned vertex = std::countr_zero(rest);
            const Mask singleton = Mask{1} << vertex;
            rest ^= singleton;
            collect(fixed | singleton, rest & ~adj[vertex]);
        }
    }

    int miss_max(Mask indep) const {
        return std::max(int((indep & side[0]) == 0) + int((indep & side[1]) == 0),
                        int((indep & side[2]) == 0) + int((indep & side[3]) == 0));
    }

    bool final_test() const {
        for (Mask indep : independents) {
            int size = std::popcount(indep) + miss_max(indep);
            for (unsigned index : chosen) size += (colours[index] & indep) == 0;
            if (size > degree) return false;
        }
        for (unsigned vertex = 0; vertex < width; ++vertex) {
            for (unsigned other = 0; other < vertex; ++other) {
                if (adj[vertex] & (Mask{1} << other)) continue;
                int codegree = std::popcount(adj[vertex] & adj[other]);
                const Mask endpoints = (Mask{1} << vertex) | (Mask{1} << other);
                for (Mask label : side) codegree += (label & endpoints) == endpoints;
                for (unsigned index : chosen) codegree += (colours[index] & endpoints) == endpoints;
                if (codegree > cap || codegree < 1) return false;
            }
        }
        for (Mask label : side) {
            for (unsigned index : chosen) {
                if (std::popcount(label & colours[index]) + 1 > cap) return false;
            }
        }
        return true;
    }

    bool search(Domain allowed, uint64_t required) {
        deepest = std::max(deepest, unsigned(chosen.size()));
        if (++visits > bound) {
            if (trace) throw std::runtime_error("node cutoff: no complete trace");
            aborted = true;
            return false;
        }
        if (chosen.size() == unsigned(degree - 2)) {
            if (trace) throw std::runtime_error("full selected list: unsupported by trace version 1");
            ++completed;
            if (required != 0 || !final_test()) return false;
            if (!enumerate) return true;
            ++found;
            std::cout << "solution " << package;
            for (unsigned index : chosen) std::cout << ' ' << colours[index];
            std::cout << '\n';
            return false;
        }
        unsigned smallest = std::numeric_limits<unsigned>::max();
        unsigned pivot = 0;
        Domain candidates;
        for (unsigned vertex = 0; vertex < width; ++vertex) {
            if (demand[vertex] < 1) continue;
            const auto domain = allowed.intersection(relevant[vertex]);
            const unsigned count = domain.count();
            if (count < unsigned(demand[vertex])) {
                if (trace) trace->put(0);
                return false;
            }
            if (count < smallest) {
                smallest = count;
                candidates = domain;
                pivot = vertex + 1;
            }
        }
        uint64_t todo = required;
        while (todo) {
            const unsigned pair = std::countr_zero(todo);
            todo &= todo - 1;
            const auto domain = allowed.intersection(missing_pairs[pair].allowed);
            const unsigned count = domain.count();
            if (count == 0) {
                if (trace) trace->put(0);
                return false;
            }
            if (count < smallest) {
                smallest = count;
                candidates = domain;
                pivot = 64 + pair;
            }
        }
        if (trace) {
            if (pivot == 0) throw std::runtime_error("unjustified terminal state");
            trace->put(static_cast<char>(pivot));
        }
        for (unsigned block = 0; block < candidates.blocks.size(); ++block) {
            uint64_t current = candidates.blocks[block];
            while (current) {
                const unsigned index = block * 64 + std::countr_zero(current);
                current &= current - 1;
                allowed.erase(index);
                Domain next = allowed;
                next.subtract(forbid[index]);
                Mask positions = colours[index];
                while (positions) {
                    const unsigned vertex = std::countr_zero(positions);
                    positions &= positions - 1;
                    if (--demand[vertex] == 0) next.subtract(relevant[vertex]);
                }
                for (unsigned indep : disjoint_residue[index]) {
                    if (--allowance[indep] == 0) next.subtract(largest_masks[indep]);
                }
                chosen.push_back(index);
                if (search(next, required & ~covered[index])) return true;
                chosen.pop_back();
                for (unsigned indep : disjoint_residue[index]) ++allowance[indep];
                positions = colours[index];
                while (positions) {
                    const unsigned vertex = std::countr_zero(positions);
                    positions &= positions - 1;
                    ++demand[vertex];
                }
                if (aborted) return false;
            }
        }
        return false;
    }
};

int main(int argc, char **argv) {
    if (argc < 2 || argc > 4) return 2;
    const bool profile = argc == 3 && std::string(argv[2]) == "profile";
    const bool enumerate = argc == 3 && std::string(argv[2]) == "enumerate";
    const bool traced = argc == 4 && std::string(argv[2]) == "trace";
    if (argc != 2 && !profile && !traced && !enumerate) return 2;
    const uint64_t bound = std::strtoull(argv[1], nullptr, 10);
    int degree, cap, order;
    if (!(std::cin >> degree >> cap >> order) || order < 1 || order > 31) return 2;
    std::vector<Mask> adj(order);
    for (auto &value : adj) {
        if (!(std::cin >> value)) return 2;
    }
    Packing solver(degree, cap, std::move(adj));
    std::ofstream trace;
    if (traced) {
        trace.exceptions(std::ios::badbit | std::ios::failbit);
        trace.open(argv[3], std::ios::binary);
        trace.write("R7PACK1\n", 8);
    }
    std::array<Mask, 4> sides;
    uint64_t package = 0;
    while (std::cin >> sides[0] >> sides[1] >> sides[2] >> sides[3]) {
        solver.run(sides, bound, profile, traced ? &trace : nullptr, enumerate, package++);
    }
    if (!std::cin.eof()) return 2;
    if (traced) trace.close();
    return 0;
}
