#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

using Mask = uint32_t;
using Family = std::array<Mask, 3>;

int size(Mask mask) { return std::popcount(mask); }
Mask bit(int vertex) { return Mask(1) << vertex; }
int next(Mask& mask) { int result = std::countr_zero(mask); mask &= mask - 1; return result; }

template<class Visitor>
void subsets(Mask remaining, Mask selected, int count, const Visitor& visitor) {
    if (!count) {
        visitor(selected);
        return;
    }
    while (size(remaining) >= count) {
        int vertex = next(remaining);
        subsets(remaining, selected | bit(vertex), count - 1, visitor);
    }
}

int main(int argc, char* argv[]) {
    assert(argc == 3 || argc == 4);
    const bool pilot = argc == 4;
    const int limit = pilot ? std::stoi(argv[3]) : 191;
    std::ifstream source(argv[1]);
    std::ofstream output(argv[2]);
    assert(source && output);
    constexpr int order = 22;
    constexpr Mask full = (Mask(1) << order) - 1;
    int row = 0;
    std::string line;
    for (; row < limit && source >> line; ++row) {
        assert(line.front() - 63 == order && line.size() == 40);
        std::array<Mask, order> graph{};
        for (int higher = 1, position = 0; higher < order; ++higher)
            for (int lower = 0; lower < higher; ++lower, ++position)
                if ((line[1 + position / 6] - 63) >> (5 - position % 6) & 1) {
                    graph[higher] |= bit(lower);
                    graph[lower] |= bit(higher);
                }
        auto local_mark_check = [&](Mask mask) {
            for (Mask current = mask; current;) {
                const int vertex = next(current);
                if (graph[vertex] & mask) return false;
                for (Mask peers = current; peers;) if (size(graph[vertex] & graph[next(peers)]) > 4) return false;
            }
            return std::ranges::all_of(graph, [&](Mask neighbourhood) { return size(neighbourhood & mask) <= 5; });
        };
        for (int first = 0; first < order; ++first) for (int second = first + 1; second < order; ++second) {
            const Mask common = bit(first) | bit(second);
            const Mask blocked = graph[first] | graph[second];
            if ((blocked & common) || size(blocked) > 8 || size(graph[first] & graph[second]) > 2 ||
                size(graph[first]) > 6 || size(graph[second]) > 6) continue;
            std::vector<Mask> petals;
            subsets(full ^ (blocked | common), 0, 4, [&](Mask set) {
                if (local_mark_check(set | common)) petals.push_back(set);
            });
            for (unsigned one = 0; one < petals.size(); ++one) {
                for (unsigned two = one + 1; two < petals.size(); ++two) {
                    if (petals[one] & petals[two]) continue;
                    const Mask chosen = petals[one] | petals[two];
                    for (unsigned three = two + 1; three < petals.size(); ++three) {
                        if (chosen & petals[three]) continue;
                        const Mask used = common | chosen | petals[three];
                        const Mask core = full ^ used;
                        bool good = true;
                        for (int vertex = 0; vertex < order; ++vertex) {
                            const int marked = (common & bit(vertex)) ? 3 : (used & bit(vertex)) ? 1 : 0;
                            if (marked) {
                                if (size(graph[vertex]) + marked > 9 || size(graph[vertex] & used) + marked < 3) good = false;
                            } else if (size(graph[vertex] & used) < 3 || size(graph[vertex] & used) > 9) good = false;
                        }
                        if (!good) continue;
                        Family family{common | petals[one], common | petals[two], common | petals[three]};
                        std::ranges::sort(family);
                        output << row << ' ' << core << ' ' << family[0] << ' ' << family[1] << ' ' << family[2] << '\n';
                    }
                }
            }
        }
    }
    assert(row == limit);
}
