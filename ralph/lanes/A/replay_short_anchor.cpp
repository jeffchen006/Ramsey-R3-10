#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {
using Mask = std::uint32_t;

int pop(Mask& mask) {
    const auto index = std::countr_zero(mask);
    mask &= mask - 1;
    return index;
}

struct Scan {
    bool smaller_control;
    std::array<Mask, 21> adjacent{};
    std::array<int, 21> degree{};
    std::uint64_t input = 0;
    std::uint64_t marks = 0;
    std::uint64_t singleton_deficits = 0;
    std::uint64_t double_deficits = 0;
    std::string encoded;
    Mask all = 0;

    bool independent(Mask group) const {
        for (auto peers = group; peers;) {
            if (adjacent[pop(peers)] & group) return false;
        }
        return true;
    }

    bool support_caps(Mask anchors, Mask outside, int single_cap) const {
        std::array<Mask, 4> neighbours{};
        auto width = 0;
        Mask covered = 0, doubles = 0;
        while (anchors) {
            const auto reached = adjacent[pop(anchors)] & outside;
            for (int index = 0; index < width; ++index) {
                const auto slot = neighbours[index] & reached;
                if ((slot & (slot - 1)) || (slot & doubles)) return false;
                doubles |= slot;
            }
            neighbours[width++] = reached;
            covered |= reached;
        }
        if (covered != outside) return false;
        for (int index = 0; index < width; ++index) {
            if (std::popcount(neighbours[index] & ~doubles) > single_cap) return false;
        }
        return true;
    }

    void collect(int short_star, int long_star, int first, int second) {
        Mask short_side = (Mask{1} << short_star) | (Mask{1} << first);
        Mask reach = adjacent[short_star] | adjacent[first];
        if (second >= 0) {
            short_side |= Mask{1} << second;
            reach |= adjacent[second];
        }
        const auto long_rest = all & ~(short_side | reach);
        const auto long_star_bit = Mask{1} << long_star;
        const auto long_side = long_rest | long_star_bit;
        if (std::popcount(long_rest) != (smaller_control ? 1 : 3)) return;
        if ((adjacent[long_star] & long_rest) || !independent(long_rest)) return;
        const auto outside = reach & ~long_star_bit;
        const auto cap = smaller_control ? 2 : 4;
        if (!support_caps(short_side, outside, cap) || !support_caps(long_side, outside, cap)) return;
        ++marks;
        if (!smaller_control) {
            const auto first_double = adjacent[short_star] & adjacent[first];
            const auto second_double = adjacent[short_star] & adjacent[second];
            if (first_double && second_double) ++singleton_deficits;
            else ++double_deficits;
        }
        std::cout << input << ' ' << short_side << ' ' << long_side << ' ' << encoded << '\n';
    }

    void process() {
        const int order = smaller_control ? 8 : 21;
        if (encoded.empty() || encoded.front() - 63 != order ||
            encoded.size() != static_cast<unsigned>(1 + (order * (order - 1) / 2 + 5) / 6)) {
            throw std::runtime_error("bad graph6 record");
        }
        adjacent.fill(0);
        all = (Mask{1} << order) - 1;
        int offset = 0;
        for (int right = 0; right < order; ++right) {
            for (int left = 0; left < right; ++left, ++offset) {
                if (((encoded[1 + offset / 6] - 63) >> (5 - offset % 6)) & 1) {
                    adjacent[left] |= Mask{1} << right;
                    adjacent[right] |= Mask{1} << left;
                }
            }
        }
        Mask eligible = 0;
        for (int vertex = 0; vertex < order; ++vertex) {
            degree[vertex] = std::popcount(adjacent[vertex]);
            if (smaller_control || degree[vertex] >= 5) eligible |= Mask{1} << vertex;
        }
        ++input;
        for (int star = 0; star < order; ++star) {
            if (!smaller_control && degree[star] != 6) continue;
            for (auto peers = adjacent[star]; peers;) {
                const auto long_star = pop(peers);
                auto noncross = eligible & ~(adjacent[star] | adjacent[long_star]);
                while (noncross) {
                    const auto first = pop(noncross);
                    if (smaller_control) collect(star, long_star, first, -1);
                    else {
                        auto seconds = noncross & ~adjacent[first];
                        while (seconds) collect(star, long_star, first, pop(seconds));
                    }
                }
            }
        }
    }
};
}

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    const std::string mode(argv[1]);
    if (mode != "control8" && mode != "core21") return 2;
    Scan scan{};
    scan.smaller_control = mode == "control8";
    while (std::getline(std::cin, scan.encoded)) scan.process();
    std::cerr << "scanned " << scan.input << " marks " << scan.marks
              << " singleton deficits " << scan.singleton_deficits << " double deficits "
              << scan.double_deficits << '\n';
}
