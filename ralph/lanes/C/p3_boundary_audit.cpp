#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <vector>

using Signature = std::array<unsigned, 7>;

static std::vector<std::array<unsigned, 3>> perms;
static bool perfect[8][8][8] = {};
static bool wing_ok[512] = {};

static unsigned move(unsigned mask, const std::array<unsigned, 3>& positions) {
    unsigned image = 0;
    for (unsigned slot = 0; slot < 3; ++slot) {
        if (mask & (1U << slot)) image |= 1U << positions[slot];
    }
    return image;
}

static Signature canonical(unsigned wings, unsigned left, unsigned right,
                           unsigned left0, unsigned right0, unsigned left1, unsigned right1) {
    Signature best{512, 0, 0, 0, 0, 0, 0};
    for (const auto& pleft : perms) {
        for (const auto& pright : perms) {
            unsigned image = 0;
            for (unsigned slot = 0; slot < 3; ++slot) {
                image |= move((wings >> (3 * slot)) & 7U, pright) << (3 * pleft[slot]);
            }
            auto first = std::array{move(left0, pleft), move(right0, pright)};
            auto last = std::array{move(left1, pleft), move(right1, pright)};
            if (last < first) std::swap(first, last);
            Signature candidate{image, move(left, pleft), move(right, pright),
                                first[0], first[1], last[0], last[1]};
            if (candidate < best) best = candidate;
        }
    }
    return best;
}

static bool disconnected(unsigned wings, unsigned left, unsigned right) {
    for (unsigned vertex = 0; vertex < 3; ++vertex) {
        if ((left & (1U << vertex)) && ((wings >> (3 * vertex)) & right & 7U)) return false;
    }
    return true;
}

static bool hall(unsigned first, unsigned second, unsigned third) {
    for (unsigned subset = 1; subset < 8; ++subset) {
        int seen = bool(first & subset) + bool(second & subset) + bool(third & subset);
        if (seen < std::popcount(subset)) return false;
    }
    return true;
}

int main(int argc, char** argv) {
    std::array<unsigned, 3> perm{0, 1, 2};
    do { perms.push_back(perm); } while (std::next_permutation(perm.begin(), perm.end()));
    for (unsigned one = 0; one < 8; ++one) {
        for (unsigned two = 0; two < 8; ++two) {
            for (unsigned three = 0; three < 8; ++three) perfect[one][two][three] = hall(one, two, three);
        }
    }
    for (unsigned wings = 0; wings < 512; ++wings) {
        wing_ok[wings] = true;
        for (unsigned absent = 0; absent < 6; ++absent) {
            unsigned subset = 63U ^ (1U << absent);
            if (disconnected(wings, subset & 7U, subset >> 3)) wing_ok[wings] = false;
        }
    }
    for (int argument = 1; argument < argc; ++argument) {
        auto total = std::atoi(argv[argument]);
        if (total < 1 || total > 27) return 2;
        std::map<Signature, unsigned> count;
        unsigned labelled = 0;
        for (uint32_t assignment = (1U << total) - 1; assignment < (1U << 27);) {
            unsigned wings = assignment & 511U;
            unsigned left = (assignment >> 9U) & 7U, right = (assignment >> 12U) & 7U;
            unsigned left0 = (assignment >> 15U) & 7U, right0 = (assignment >> 18U) & 7U;
            unsigned left1 = (assignment >> 21U) & 7U, right1 = (assignment >> 24U) & 7U;
            if (wing_ok[wings] && std::array{left0, right0} <= std::array{left1, right1} &&
                perfect[left][left0][left1] && perfect[right][right0][right1] &&
                disconnected(wings, left0, right0) && disconnected(wings, left1, right1)) {
                count[canonical(wings, left, right, left0, right0, left1, right1)]++;
                labelled++;
            }
            uint32_t low = assignment & (0U - assignment);
            uint32_t ripple = assignment + low;
            assignment = ripple | (((assignment ^ ripple) / low) >> 2);
        }
        std::cout << "coverage " << total << ' ' << labelled << ' ' << count.size() << '\n';
        for (const auto& [key, multiplicity] : count) {
            std::cout << "key " << total;
            for (auto part : key) std::cout << ' ' << part;
            std::cout << ' ' << multiplicity << '\n';
        }
    }
}
