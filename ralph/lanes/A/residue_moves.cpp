#include <bit>
#include <charconv>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

using Mask = std::uint64_t;
using Graph = std::vector<Mask>;

static Mask bit(int vertex) { return Mask{1} << vertex; }

static std::string encode(const Graph &graph) {
    const int size = static_cast<int>(graph.size());
    std::string row(1, static_cast<char>(63 + size));
    unsigned value = 0, filled = 0;
    for (int second = 1; second < size; ++second) {
        for (int first = 0; first < second; ++first) {
            value = (value << 1) | ((graph[second] >> first) & 1);
            if (++filled == 6) {
                row += static_cast<char>(63 + value);
                value = filled = 0;
            }
        }
    }
    if (filled) row += static_cast<char>(63 + (value << (6 - filled)));
    return row;
}

static Graph decode(const std::string &row) {
    if (row.empty()) throw std::runtime_error("empty graph6 row");
    int size = row.front() - 63;
    if (size < 1 || size > 62 || row.size() != 1 + (size * (size - 1) / 2 + 5u) / 6) {
        throw std::runtime_error("unsupported or malformed graph6 row");
    }
    Graph graph(size);
    int offset = 0;
    for (int second = 1; second < size; ++second) {
        for (int first = 0; first < second; ++first, ++offset) {
            int value = row[1 + offset / 6] - 63;
            if (value < 0 || value > 63) throw std::runtime_error("bad graph6 digit");
            if ((value >> (5 - offset % 6)) & 1) {
                graph[first] |= bit(second);
                graph[second] |= bit(first);
            }
        }
    }
    if (encode(graph) != row) throw std::runtime_error("nonstandard graph6 padding");
    return graph;
}

static bool independent(const Graph &graph, Mask pool, int need) {
    while (std::popcount(pool) >= need) {
        if (need == 1) return true;
        const int vertex = std::countr_zero(pool);
        pool &= pool - 1;
        if (independent(graph, pool & ~graph[vertex], need - 1)) return true;
    }
    return false;
}

int main(int argc, char **argv) try {
    if (argc != 3) return 2;
    const std::string_view modes(argv[1]), cap_text(argv[2]);
    int cap = 0;
    const auto result = std::from_chars(cap_text.begin(), cap_text.end(), cap);
    if ((modes != "up" && modes != "down") || result.ec != std::errc{}
        || result.ptr != cap_text.end() || cap < 2 || cap > 61) return 2;
    std::string input;
    unsigned ordinal = 0, moves = 0, immobile = 0;
    while (std::getline(std::cin, input)) {
        Graph graph = decode(input);
        const int size = static_cast<int>(graph.size());
        const Mask universe = bit(size) - 1;
        if (independent(graph, universe, cap + 1)) throw std::runtime_error("input exceeds alpha cap");
        ++ordinal;
        const auto before = moves;
        for (int lower = 0; lower < size; ++lower) {
            for (int higher = lower + 1; higher < size; ++higher) {
                const bool edge = graph[lower] & bit(higher);
                const Mask common = graph[lower] & graph[higher];
                if (edge && common) throw std::runtime_error("input contains a triangle");
                if (modes == "up" && (edge || common)) continue;
                if (modes == "down" && (!edge || independent(
                    graph, universe & ~(graph[lower] | graph[higher]), cap - 1))) continue;
                graph[lower] ^= bit(higher);
                graph[higher] ^= bit(lower);
                std::cout << ordinal << '\t' << lower << '\t' << higher << '\t' << encode(graph) << '\n';
                graph[lower] ^= bit(higher);
                graph[higher] ^= bit(lower);
                ++moves;
            }
        }
        immobile += moves == before;
    }
    if (!std::cin.eof() || !std::cout) return 2;
    std::cerr << modes << ": " << ordinal << " roots, " << moves << " labelled moves, "
              << immobile << " with no move\n";
    return ordinal ? 0 : 2;
} catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 2;
}
