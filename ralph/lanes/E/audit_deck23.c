#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static uint32_t adj[26], degrees[8], options[19][4096];
static unsigned counts[19], number, target, split, wanted;
static uint32_t universe = (UINT32_C(1) << 26) - 1;
static uint64_t checked, masks, partitions;

static unsigned pop(uint32_t mask) {
    return __builtin_popcount(mask);
}

static int alpha(uint32_t pending, unsigned size) {
    if (!size) return 1;
    while (pop(pending) >= size) {
        unsigned vertex = __builtin_ctz(pending);
        pending &= pending - 1;
        if (alpha(pending & ~adj[vertex], size - 1)) return 1;
    }
    return 0;
}

static void groups(uint32_t pending, uint32_t chosen, uint32_t core, unsigned size) {
    if (!size) {
        unsigned sum = 0;
        for (uint32_t scan = core; scan; scan &= scan - 1) {
            unsigned row = pop(chosen & adj[__builtin_ctz(scan)]);
            if (!row) return;
            sum += row;
        }
        if (sum < 10 || sum > 18 || (split == 10 && sum != 10)) return;
        if (sum > wanted - 20 || alpha(chosen | core, 7)) return;
        assert(counts[sum] < 4096);
        options[sum][counts[sum]++] = chosen;
        return;
    }
    while (pop(pending) >= size) {
        unsigned vertex = __builtin_ctz(pending);
        uint32_t bit = UINT32_C(1) << vertex;
        pending ^= bit;
        groups(pending & ~adj[vertex], chosen | bit, core, size - 1);
    }
}

static void test(uint32_t core) {
    ++checked;
    unsigned twice = 0;
    for (uint32_t scan = core; scan; scan &= scan - 1) {
        unsigned vertex = __builtin_ctz(scan);
        unsigned degree = pop(core & adj[vertex]);
        if (degree < 2 || degree > (split == 10 ? 4 : 2) || pop(adj[vertex]) < degree + 3) return;
        twice += degree;
    }
    if (twice != split * 2) return;
    printf("M %u %" PRIu32 "\n", number, core);
    ++masks;
    for (unsigned amount = 10; amount <= 18; ++amount) counts[amount] = 0;
    uint32_t other = universe ^ core;
    groups(other, 0, core, 6);
    for (unsigned first = 10; first <= 18; ++first) {
        for (unsigned second = first; second <= 18; ++second) {
            if (first + second >= wanted) break;
            unsigned third = wanted - first - second;
            if (third < second || third > 18) continue;
            for (unsigned left = 0; left < counts[first]; ++left) {
                uint32_t block = options[first][left];
                for (unsigned middle = 0; middle < counts[second]; ++middle) {
                    uint32_t near = options[second][middle];
                    if (block & near || (first == second && block > near)) continue;
                    uint32_t far = other ^ (block | near);
                    if (second == third && near > far) continue;
                    for (unsigned right = 0; right < counts[third]; ++right) {
                        if (far == options[third][right]) {
                            printf("P %u %" PRIu32 " %" PRIu32 " %" PRIu32 " %" PRIu32 "\n", number, core, block, near, far);
                            ++partitions;
                            break;
                        }
                    }
                }
            }
        }
    }
}

static void select_degree(uint32_t remaining, unsigned quantity, unsigned degree, int next5, int next6, uint32_t chosen) {
    if (!quantity) {
        if (degree == 7) select_degree(degrees[6], next6, 6, next5, 0, chosen);
        else if (degree == 6) select_degree(degrees[5], next5, 5, 0, 0, chosen);
        else test(chosen);
        return;
    }
    while (pop(remaining) >= quantity) {
        uint32_t bit = remaining & -remaining;
        remaining ^= bit;
        select_degree(remaining, quantity - 1, degree, next5, next6, chosen | bit);
    }
}

int main(int argc, char **argv) {
    assert(argc == 5);
    split = atoi(argv[1]);
    unsigned offset = atoi(argv[2]), stride = atoi(argv[3]), end = atoi(argv[4]);
    assert((split == 8 || split == 10) && offset < stride);
    char line[128];
    unsigned cards = 0;
    for (; number < end && fgets(line, sizeof(line), stdin); ++number) {
        if (number % stride != offset) continue;
        assert(line[0] == 'Y');
        ++cards;
        for (unsigned site = 0; site < 26; ++site) adj[site] = 0;
        unsigned bit = 0;
        for (unsigned right = 1; right < 26; ++right) {
            for (unsigned left = 0; left < right; ++left, ++bit) {
                unsigned code = line[1 + bit / 6] - 63;
                if (code & (32 >> (bit % 6))) {
                    adj[left] |= UINT32_C(1) << right;
                    adj[right] |= UINT32_C(1) << left;
                }
            }
        }
        for (unsigned degree = 0; degree < 8; ++degree) degrees[degree] = 0;
        unsigned twice = 0;
        for (unsigned vertex = 0; vertex < 26; ++vertex) {
            unsigned degree = pop(adj[vertex]);
            assert(degree <= 7 && !(adj[vertex] >> vertex & 1));
            for (uint32_t scan = adj[vertex]; scan; scan &= scan - 1) assert(!(adj[vertex] & adj[__builtin_ctz(scan)]));
            twice += degree;
            degrees[degree] |= UINT32_C(1) << vertex;
        }
        assert(twice == 148 && !alpha(universe, 8));
        for (target = (split == 8 ? 46 : 50); target <= (split == 8 ? 51 : 50); ++target) {
            wanted = (split == 8 ? 48 : 44) - (64 - target);
            for (unsigned seven = 0; seven <= pop(degrees[7]); ++seven) {
                int six = target - 40 - 2 * seven;
                int five = 8 - seven - six;
                if (six < 0 || five < 0 || six > (int)pop(degrees[6]) || five > (int)pop(degrees[5])) continue;
                select_degree(degrees[7], seven, 7, five, six, 0);
            }
        }
    }
    fprintf(stderr, "independent m%u cards=%u candidates=%" PRIu64 " masks=%" PRIu64 " partitions=%" PRIu64 "\n",
            split, cards, checked, masks, partitions);
}
