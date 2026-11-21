#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>

using Mask = uint32_t;
static constexpr int order = 27;
static constexpr Mask universe = (Mask{1} << order) - 1;
static Mask bit(int vertex) { return Mask{1} << vertex; }
static int count(Mask mask) { return std::popcount(mask); }
static int take(Mask &mask) {
    int vertex = std::countr_zero(mask);
    mask ^= bit(vertex);
    return vertex;
}

struct Replay {
    std::array<Mask, order> edges{};
    std::array<Mask, 3> group{};
    Mask degree_seven = 0;
    int edge_count = 0, budget = 0;
    uint64_t windows = 0;

    explicit Replay(const std::string &graph) {
        if (graph.size() != 60 || graph.front() != 'Z') throw std::runtime_error("expected graph6 of order 27");
        for (char character : graph) if (character < '?' || character > '~') throw std::runtime_error("invalid byte");
        if ((graph.back() - '?') % 8) throw std::runtime_error("nonzero padding");
        int index = 0;
        for (int right = 1; right < order; ++right) for (int left = 0; left < right; ++left, ++index) {
            if ((graph[1 + index / 6] - '?') & (32 >> (index % 6))) {
                edges[left] |= bit(right);
                edges[right] |= bit(left);
                ++edge_count;
            }
        }
        if (edge_count < 85 || edge_count > 87) throw std::runtime_error("bad edge count");
        budget = (272 - 3 * edge_count) / 2;
        for (int vertex = 0; vertex < order; ++vertex) {
            if (count(edges[vertex]) == 7) degree_seven |= bit(vertex);
            for (Mask scan = edges[vertex]; scan;)
                if (edges[vertex] & edges[take(scan)]) throw std::runtime_error("triangle in anchor");
        }
        if (independent(universe, 8)) throw std::runtime_error("I8 in anchor");
    }

    bool independent(Mask pool, int threshold) const {
        if (count(pool) < threshold) return false;
        if (threshold == 1) return true;
        int pivot = -1, max_degree = 0;
        for (Mask scan = pool; scan;) {
            int vertex = take(scan);
            int degree_here = count(edges[vertex] & pool);
            if (degree_here > max_degree) { pivot = vertex; max_degree = degree_here; }
        }
        if (pivot < 0) return true;
        pool ^= bit(pivot);
        return independent(pool & ~edges[pivot], threshold - 1) || independent(pool, threshold);
    }

    bool color(Mask pending, Mask window, unsigned started) {
        constexpr std::array<int, 3> target{6, 5, 5};
        if (!pending) return true;
        int pivot = -1, best_degree = -1;
        unsigned best = 0;
        for (Mask scan = pending; scan;) {
            int vertex = take(scan);
            unsigned available = 0;
            for (int color_index = 0; color_index < 3; ++color_index)
                if (count(group[color_index]) < target[color_index] && !(group[color_index] & edges[vertex]))
                    available |= 1U << color_index;
            if (!available) return false;
            int unassigned_degree = count(edges[vertex] & pending);
            if (!best || count(available) < count(best) ||
                    (count(available) == count(best) && unassigned_degree > best_degree)) {
                pivot = vertex;
                best_degree = unassigned_degree;
                best = available;
            }
        }
        if (!(started & 2U)) best &= ~4U;
        for (; best;) {
            int color_index = take(best);
            group[color_index] ^= bit(pivot);
            const bool can = !independent(group[color_index] | window, 7) &&
                color(pending ^ bit(pivot), window, started | (1U << color_index));
            group[color_index] ^= bit(pivot);
            if (can) return true;
        }
        return false;
    }

    bool window(Mask members) {
        if (count(members & degree_seven) < 11 - budget) return false;
        Mask good = members & degree_seven;
        int needed = 11 - budget;
        while (needed > 0) {
            if (count(good) < needed) return false;
            Mask linked = edges[take(good)] & members;
            needed -= std::has_single_bit(linked);
        }
        for (Mask scan = members; scan;)
            if (!(edges[take(scan)] & members)) return false;
        if (independent(members, 6)) return false;
        ++windows;
        return color(universe ^ members, members, 0);
    }

    bool enumerate_all() {
        Mask members = (Mask{1} << 11) - 1;
        while (!(members & ~universe)) {
            if (window(members)) return true;
            Mask low_bit = members & -members;
            Mask advanced = members + low_bit;
            members = advanced | (((members ^ advanced) >> 2) >> std::countr_zero(low_bit));
        }
        return false;
    }

    bool odd_core(Mask pool, Mask prefix, int need) {
        if (!need) {
            for (Mask scan = prefix; scan;)
                if (count(edges[take(scan)] & prefix) != 2) return false;
            return window(prefix | (universe ^ current_anti));
        }
        while (count(pool) >= need) {
            int vertex = take(pool);
            if (odd_core(pool, prefix | bit(vertex), need - 1)) return true;
        }
        return false;
    }

    Mask current_anti = 0;
    bool choose_matching(Mask pair_pool, Mask endpoints, Mask anti, int remaining) {
        if (!remaining) {
            current_anti = universe ^ endpoints;
            return odd_core(anti, 0, 5);
        }
        while (count(pair_pool) >= 2 * remaining) {
            int first = take(pair_pool);
            for (Mask second_pool = pair_pool & edges[first]; second_pool;) {
                int second = take(second_pool);
                Mask left = (anti ^ bit(first) ^ bit(second)) & ~(edges[first] | edges[second]);
                if (choose_matching(pair_pool & left, endpoints | bit(first) | bit(second), left, remaining - 1))
                    return true;
            }
        }
        return false;
    }
};

int main(int argc, char **argv) {
    const bool naive = argc == 2 && std::string(argv[1]) == "all-windows";
    if (argc > 2 || (argc == 2 && !naive)) return 2;
    try {
        std::string graph;
        int index = 0;
        while (std::getline(std::cin, graph)) {
            Replay check(graph);
            bool partition = check.edge_count < 87 || naive ? check.enumerate_all() :
                check.choose_matching(check.degree_seven, 0, universe, 3);
            std::cout << ++index << ' ' << check.edge_count << ' ' << check.windows << ' '
                      << (partition ? "SURVIVES" : "EMPTY") << std::endl;
            if (partition) return 1;
        }
        return index == 0 ? 2 : 0;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return 2;
    }
}
