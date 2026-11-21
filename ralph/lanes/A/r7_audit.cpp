#include <algorithm>
#include <array>
#include <bit>
#include <bitset>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using Mask = std::uint32_t;
using Quad = std::array<Mask, 4>;

struct Graph {
    int degree, cap, order;
    Mask full;
    std::vector<Mask> adj;

    explicit Graph(std::istream &input) {
        if (!(input >> degree >> cap >> order) || order <= 0 || order >= 32 ||
            degree < 4 || degree >= 16 || cap >= degree || cap < 3)
            throw std::runtime_error("bad graph header");
        full = (Mask{1} << order) - 1;
        adj.resize(order);
        for (int vertex = 0; vertex < order; ++vertex) {
            if (!(input >> adj[vertex]) || (adj[vertex] & ~full) ||
                (adj[vertex] & (Mask{1} << vertex)))
                throw std::runtime_error("bad adjacency row");
        }
        for (int vertex = 0; vertex < order; ++vertex) {
            for (int other = 0; other < vertex; ++other) {
                bool edge = (adj[vertex] >> other) & 1;
                if (edge != bool((adj[other] >> vertex) & 1) ||
                    (edge && (adj[vertex] & adj[other])))
                    throw std::runtime_error("not a simple triangle-free graph");
            }
        }
    }

    static int next(Mask &mask) {
        int vertex = std::countr_zero(mask);
        mask &= mask - 1;
        return vertex;
    }

    Mask undominated(Mask set) const {
        Mask missing = full & ~set;
        for (Mask rest = set; rest;) missing &= ~adj[next(rest)];
        return missing;
    }

    void choose(int begin, int remaining, Mask selected, Mask unavailable,
                std::vector<Mask> &output) const {
        if (!remaining) {
            output.push_back(selected);
            return;
        }
        for (int vertex = begin; vertex <= order - remaining; ++vertex) {
            Mask singleton = Mask{1} << vertex;
            if (!(singleton & unavailable))
                choose(vertex + 1, remaining - 1, selected | singleton,
                       unavailable | adj[vertex], output);
        }
    }

    std::vector<Mask> choose(int size) const {
        std::vector<Mask> output;
        choose(0, size, 0, 0, output);
        std::sort(output.begin(), output.end());
        return output;
    }
};

struct UnionTrie {
    struct Node {
        unsigned child[2]{};
        Mask all_demands = 0;
        std::vector<std::pair<Mask, unsigned>> demands;
    };
    std::vector<Node> nodes{2};
    int width;

    explicit UnionTrie(int order) : width(order) {}

    void add(Mask used, Mask demand, unsigned count) {
        unsigned index = 1;
        for (int vertex = 0; vertex < width; ++vertex) {
            unsigned turn = (used >> vertex) & 1;
            if (!nodes[index].child[turn]) {
                nodes[index].child[turn] = nodes.size();
                nodes.emplace_back();
            }
            index = nodes[index].child[turn];
        }
        auto &node = nodes[index];
        node.all_demands = node.demands.empty() ? demand : node.all_demands & demand;
        node.demands.emplace_back(demand, count);
    }

    std::uint64_t lookup(unsigned index, int vertex, Mask ban, Mask must, Mask can_require) const {
        if (!index) return 0;
        const auto &node = nodes[index];
        if (vertex == width) {
            if (node.all_demands & ~can_require) return 0;
            std::uint64_t count = 0;
            for (auto [demand, multiplicity] : node.demands)
                if (!(demand & ~can_require)) count += multiplicity;
            return count;
        }
        if ((ban >> vertex) & 1) return lookup(node.child[0], vertex + 1, ban, must, can_require);
        if ((must >> vertex) & 1) return lookup(node.child[1], vertex + 1, ban, must, can_require);
        return lookup(node.child[0], vertex + 1, ban, must, can_require) +
               lookup(node.child[1], vertex + 1, ban, must, can_require);
    }
};

struct SideCover {
    std::map<std::pair<Mask, Mask>, std::pair<Mask, Mask>> packages;
    std::vector<Mask> colors;
    std::uint64_t count = 0;

    explicit SideCover(const Graph &graph) : colors(graph.choose(graph.degree - 2)) {
        auto candidates = graph.choose(graph.degree - 3);
        std::vector<Mask> miss;
        for (Mask candidate : candidates) miss.push_back(graph.undominated(candidate));
        Mask cannot_touch = 0, cannot_double = 0;
        for (int vertex = 0; vertex < graph.order; ++vertex) {
            const int deficit = graph.degree - std::popcount(graph.adj[vertex]);
            if (deficit < 1) throw std::runtime_error("bad residual degree");
            if (deficit <= 1) cannot_touch |= Mask{1} << vertex;
            if (deficit <= 2) cannot_double |= Mask{1} << vertex;
        }
        if (!graph.choose(graph.degree - 1).empty()) throw std::runtime_error("bad residual alpha");
        std::map<std::pair<Mask, Mask>, unsigned> signature;
        for (std::size_t first = 0; first < candidates.size(); ++first) {
            if (candidates[first] & cannot_touch) continue;
            for (std::size_t second = first + 1; second < candidates.size(); ++second) {
                Mask used = candidates[first] | candidates[second];
                Mask shared = candidates[first] & candidates[second];
                Mask demand = miss[first] | miss[second];
                if ((used & (cannot_touch | demand)) || (shared & cannot_double) ||
                    std::popcount(shared) > graph.cap - 3)
                    continue;
                if (std::any_of(colors.begin(), colors.end(), [used](Mask set) { return !(set & used); }))
                    continue;
                packages[{candidates[first], candidates[second]}] = {used, demand};
                ++signature[{used, demand}];
            }
        }
        UnionTrie trie(graph.order);
        for (const auto &[key, multiplicity] : signature) trie.add(key.first, key.second, multiplicity);
        std::uint64_t ordered = 0;
        for (const auto &[key, multiplicity] : signature)
            ordered += multiplicity * trie.lookup(1, 0, key.first, key.second, key.first);
        if (ordered % 2) throw std::runtime_error("odd oriented count");
        count = ordered / 2;
        std::cout << "colors=" << colors.size() << " packages=" << packages.size()
                  << " unordered_pairs=" << count << std::endl;
    }

    Quad validate(Quad sides) const {
        auto left = std::minmax(sides[0], sides[1]);
        auto right = std::minmax(sides[2], sides[3]);
        std::pair<Mask, Mask> side1{left.first, left.second}, side2{right.first, right.second};
        if (side2 < side1) std::swap(side1, side2);
        auto [union1, demand1] = packages.at(side1);
        auto [union2, demand2] = packages.at(side2);
        if ((union1 & union2) || (demand1 & ~union2) || (demand2 & ~union1))
            throw std::runtime_error("incompatible side packages");
        return {side1.first, side1.second, side2.first, side2.second};
    }
};

class TraceReplay {
    static constexpr std::size_t limit = 1024;
    using Choices = std::bitset<limit>;
    struct State {
        Choices permitted;
        std::array<std::int8_t, 32> demand{};
        std::array<std::int8_t, limit> budget{};
        std::uint64_t required = 0;
    };

    const Graph &graph;
    std::istream &proof;
    std::vector<Mask> colors;
    std::vector<Choices> contains, avoids, incompatible;
    std::vector<Mask> pairs;
    std::vector<Choices> pair_choices;
    std::vector<std::uint64_t> witnessed;
    std::vector<std::vector<unsigned>> avoiding_rows;
    Choices all;

    bool shortage(const State &state) const {
        for (int vertex = 0; vertex < graph.order; ++vertex)
            if (state.demand[vertex] > 0 &&
                (state.permitted & contains[vertex]).count() < unsigned(state.demand[vertex])) return true;
        for (auto outstanding = state.required; outstanding; outstanding &= outstanding - 1)
            if ((state.permitted & pair_choices[std::countr_zero(outstanding)]).none()) return true;
        return false;
    }

    void check(State state, unsigned depth) {
        ++nodes;
        if (depth >= unsigned(graph.degree - 2)) throw std::runtime_error("complete choice in trace");
        const int byte = proof.get();
        if (byte == 0) {
            if (!shortage(state)) throw std::runtime_error("unsupported closure");
            return;
        }
        Choices options;
        if (byte >= 1 && byte <= graph.order && state.demand[byte - 1] > 0) {
            options = state.permitted & contains[byte - 1];
        } else if (byte >= 64 && byte < 64 + int(pairs.size()) &&
                   ((state.required >> (byte - 64)) & 1)) {
            options = state.permitted & pair_choices[byte - 64];
        } else {
            throw std::runtime_error("illegal pivot or missing byte");
        }
        if (options.none()) throw std::runtime_error("empty branch");
        for (auto index = options._Find_first(); index < limit; index = options._Find_next(index)) {
            state.permitted.reset(index);
            State child = state;
            child.permitted &= ~incompatible[index];
            child.required &= ~witnessed[index];
            for (Mask vertices = colors[index]; vertices;) {
                const auto vertex = Graph::next(vertices);
                if (child.demand[vertex] <= 0) throw std::runtime_error("negative demand");
                if (--child.demand[vertex] == 0) child.permitted &= ~contains[vertex];
            }
            for (auto row : avoiding_rows[index]) {
                if (child.budget[row] <= 0) throw std::runtime_error("negative budget");
                if (--child.budget[row] == 0) child.permitted &= ~avoids[row];
            }
            check(child, depth + 1);
        }
    }

public:
    std::uint64_t nodes = 0;

    TraceReplay(const Graph &graph_arg, std::istream &proof_arg, std::vector<Mask> color_arg)
        : graph(graph_arg), proof(proof_arg), colors(std::move(color_arg)), contains(graph.order),
          avoids(colors.size()), incompatible(colors.size()), witnessed(colors.size()), avoiding_rows(colors.size()) {
        if (colors.size() > limit) throw std::runtime_error("too many colors");
        std::sort(colors.begin(), colors.end(), [](Mask first, Mask second) {
            const Mask difference = first ^ second;
            return difference && ((first >> std::countr_zero(difference)) & 1);
        });
        for (int high = 1; high < graph.order; ++high) {
            for (int low = 0; low < high; ++low) {
                if (((graph.adj[high] >> low) & 1) || (graph.adj[high] & graph.adj[low])) continue;
                pairs.push_back((Mask{1} << high) | (Mask{1} << low));
            }
        }
        if (pairs.size() > 64) throw std::runtime_error("too many missing pairs");
        pair_choices.resize(pairs.size());
        for (unsigned index = 0; index < colors.size(); ++index) {
            all.set(index);
            for (Mask vertices = colors[index]; vertices;) contains[Graph::next(vertices)].set(index);
            for (unsigned other = 0; other < colors.size(); ++other) {
                const Mask shared = colors[index] & colors[other];
                if (std::popcount(shared) > graph.cap - 2) incompatible[index].set(other);
                if (!shared) {
                    avoiding_rows[index].push_back(other);
                    avoids[other].set(index);
                }
            }
            for (unsigned pair = 0; pair < pairs.size(); ++pair) {
                if ((colors[index] & pairs[pair]) != pairs[pair]) continue;
                pair_choices[pair].set(index);
                witnessed[index] |= std::uint64_t{1} << pair;
            }
        }
        std::string magic(8, '\0');
        if (!proof.read(magic.data(), magic.size()) || magic != "R7PACK1\n")
            throw std::runtime_error("bad trace header");
    }

    void check_root(const Quad &sides) {
        State base;
        base.permitted = all;
        int total = 0;
        for (int vertex = 0; vertex < graph.order; ++vertex) {
            int needed = graph.degree - std::popcount(graph.adj[vertex]);
            for (Mask mask : sides) needed -= (mask >> vertex) & 1;
            if (needed < 1) throw std::runtime_error("bad initial demand");
            base.demand[vertex] = needed;
            total += needed;
        }
        if (total != (graph.degree - 2) * (graph.degree - 2)) throw std::runtime_error("bad total demand");
        for (unsigned index = 0; index < colors.size(); ++index) {
            const Mask fixed = colors[index];
            int left = int(!(sides[0] & fixed)) + int(!(sides[1] & fixed));
            int right = int(!(sides[2] & fixed)) + int(!(sides[3] & fixed));
            base.budget[index] = 2 - std::max(left, right);
            if (base.budget[index] == 0) base.permitted &= ~avoids[index];
        }
        for (unsigned pair = 0; pair < pairs.size(); ++pair) {
            const Mask both = pairs[pair];
            if (std::none_of(sides.begin(), sides.end(), [both](Mask side) { return (side & both) == both; }))
                base.required |= std::uint64_t{1} << pair;
        }
        check(base, 0);
    }
};

int main(int argc, char **argv) {
    try {
        if (argc < 3 || argc > 4) throw std::runtime_error("usage: r7_audit (--cover|--control) package.txt [trace]");
        std::string mode = argv[1];
        if (mode != "--cover" && mode != "--control") throw std::runtime_error("bad mode");
        std::ifstream input(argv[2]);
        Graph graph(input);
        SideCover cover(graph);
        std::ifstream trace;
        if (argc == 4) trace.open(argv[3], std::ios::binary);
        std::unique_ptr<TraceReplay> replay;
        if (argc == 4) replay = std::make_unique<TraceReplay>(graph, trace, cover.colors);
        std::set<Quad> obtained;
        for (Quad tuple; input >> tuple[0];) {
            if (!(input >> tuple[1] >> tuple[2] >> tuple[3])) throw std::runtime_error("partial tuple");
            if (!obtained.insert(cover.validate(tuple)).second) throw std::runtime_error("duplicate tuple");
            if (replay != nullptr) replay->check_root(tuple);
        }
        if (!input.eof()) throw std::runtime_error("bad tuple stream");
        if (mode == "--cover" && obtained.size() != cover.count) throw std::runtime_error("incomplete cover");
        if (mode == "--control" && obtained.empty()) throw std::runtime_error("no control tuple");
        if (replay != nullptr) {
            if (trace.get() != std::char_traits<char>::eof() || !trace.eof() || trace.bad())
                throw std::runtime_error("trailing or damaged trace");
            std::cout << "s VERIFIED packing replay " << obtained.size() << " trees, " << replay->nodes << " nodes\n";
        }
        std::cout << (mode == "--cover" ? "s VERIFIED side cover " : "s VERIFIED control membership ")
                  << obtained.size() << '\n';
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "s FAILED " << error.what() << '\n';
        return 1;
    }
}
