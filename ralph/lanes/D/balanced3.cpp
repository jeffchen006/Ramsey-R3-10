#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using Mask = uint32_t;

bool independent(const std::vector<Mask>& adj, Mask chosen) {
    while (chosen) {
        const int vertex = __builtin_ctz(chosen);
        chosen &= chosen - 1;
        if (adj[vertex] & chosen) return false;
    }
    return true;
}

void independent_groups(const std::vector<Mask>& adj, int target, Mask remain, Mask chosen,
                        std::vector<Mask>& out) {
    if (!target) {
        out.push_back(chosen);
        return;
    }
    while (__builtin_popcount(remain) >= target) {
        const int vertex = __builtin_ctz(remain);
        remain &= remain - 1;
        independent_groups(adj, target - 1, remain & ~adj[vertex], chosen | (1u << vertex), out);
    }
}

bool anchored_codegrees(const std::vector<Mask>& adj, const std::array<Mask, 3>& groups) {
    for (const Mask group : groups) {
        for (size_t vertex = 0; vertex < adj.size(); ++vertex) {
            if (__builtin_popcount(adj[vertex] & group) > 4) return false;
        }
        for (Mask remain = group; remain; remain &= remain - 1) {
            const int vertex = __builtin_ctz(remain);
            for (Mask other = remain & (remain - 1); other; other &= other - 1) {
                const int partner = __builtin_ctz(other);
                if (__builtin_popcount(adj[vertex] & adj[partner]) > 3) return false;
            }
        }
    }
    return true;
}

int main(int argc, char** argv) {
    if (argc != 2) return 1;
    const int group_size = std::stoi(argv[1]);
    if (group_size < 1 || group_size > 10) return 1;
    const int order = 3 * group_size;
    const Mask universe = (1u << order) - 1;
    int graphs = 0, balanced = 0, viable = 0, independent_sets = 0;
    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty() || line[0] - 63 != order || line.size() != 1u + (order * (order - 1) + 11) / 12) {
            throw std::runtime_error("unexpected graph6 line");
        }
        std::vector<Mask> adj(order);
        int bit = 0;
        for (int right = 1; right < order; ++right) {
            for (int left = 0; left < right; ++left, ++bit) {
                if ((line[1 + bit / 6] - 63) & (1 << (5 - bit % 6))) {
                    adj[left] |= 1u << right;
                    adj[right] |= 1u << left;
                }
            }
        }
        for (int vertex = 0; vertex < order; ++vertex) {
            if (!independent(adj, adj[vertex])) throw std::runtime_error("triangle");
        }
        std::vector<Mask> groups;
        independent_groups(adj, group_size + 1, universe, 0, groups);
        if (!groups.empty()) throw std::runtime_error("independent set over cap");
        independent_groups(adj, group_size, universe, 0, groups);
        independent_sets += groups.size();
        bool has_partition = false, has_viable_partition = false;
        for (const Mask first : groups) {
            if (!(first & 1)) continue;
            const Mask rest = universe ^ first;
            const Mask pivot = rest & -rest;
            for (const Mask second : groups) {
                if (!(second & pivot) || (first & second)) continue;
                const Mask third = rest ^ second;
                if (!independent(adj, third)) continue;
                has_partition = true;
                bool codegrees = true;
                for (int vertex = 0; vertex < order; ++vertex) {
                    if (__builtin_popcount(adj[vertex]) > 8) codegrees = false;
                    for (int partner = vertex + 1; partner < order; ++partner) {
                        if (__builtin_popcount(adj[vertex] & adj[partner]) > 4) codegrees = false;
                    }
                }
                if (codegrees && anchored_codegrees(adj, {first, second, third})) {
                    has_viable_partition = true;
                    std::cout << graphs << '\t' << first << '\t' << second << '\t' << third << '\t' << line << '\n';
                }
            }
        }
        balanced += has_partition;
        viable += has_viable_partition;
        ++graphs;
    }
    std::cerr << "graphs=" << graphs << " independent_max_size_sets=" << independent_sets
              << " balanced=" << balanced << " viable=" << viable << '\n';
}
