#include <cstddef>
#include <cstdint>

using Mask = std::uint64_t;

static bool enumerate(const Mask* edges, Mask candidates, int left, Mask seen,
                      Mask* output, std::size_t limit, std::size_t& count) {
    if (left == 0) {
        output[count++] = seen;
        return count < limit;
    }
    while (__builtin_popcountll(candidates) >= left) {
        Mask bit = candidates & -candidates;
        candidates ^= bit;
        if (!enumerate(edges, candidates & ~edges[__builtin_ctzll(bit)], left - 1,
                       seen | bit, output, limit, count)) return false;
    }
    return true;
}

extern "C" std::size_t window_sets(const Mask* edges, Mask candidates, int size,
                                   Mask* output, std::size_t limit) {
    if (!limit) return 0;
    std::size_t count = 0;
    enumerate(edges, candidates, size, 0, output, limit, count);
    return count;
}
