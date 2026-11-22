#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static uint32_t adjacency[32];
static unsigned degrees[32], order, need, incidence, edges, mincore, maxcore, minhost, card;
static unsigned long long count, tested;

static unsigned pop(uint32_t mask) {
    return __builtin_popcount(mask);
}

static void visit(uint32_t remain, uint32_t selected, unsigned size, unsigned budget) {
    if (!size) {
        if (budget) return;
        ++tested;
        unsigned total = 0;
        for (uint32_t scan = selected; scan; scan &= scan - 1) {
            unsigned vertex = __builtin_ctz(scan);
            unsigned degree = pop(selected & adjacency[vertex]);
            if (degree < mincore || degree > maxcore || degrees[vertex] < degree + 3) return;
            total += degree;
        }
        if (total == 2 * edges) {
            printf("%u %" PRIu32 "\n", card, selected);
            ++count;
        }
        return;
    }
    if (budget < minhost * size || budget > 7 * size) return;
    while (pop(remain) >= size) {
        unsigned vertex = __builtin_ctz(remain);
        remain &= remain - 1;
        if (degrees[vertex] <= budget && pop(selected & adjacency[vertex]) <= maxcore)
            visit(remain, selected | (UINT32_C(1) << vertex), size - 1, budget - degrees[vertex]);
    }
}

int main(int argc, char **argv) {
    assert(argc == 10);
    need = atoi(argv[1]); incidence = atoi(argv[2]); edges = atoi(argv[3]);
    mincore = atoi(argv[4]); maxcore = atoi(argv[5]); minhost = atoi(argv[6]);
    unsigned offset = atoi(argv[7]), stride = atoi(argv[8]), end = atoi(argv[9]);
    assert(stride && offset < stride && minhost >= mincore + 3);
    unsigned cards = 0;
    char line[1024];
    for (; card < end && fgets(line, sizeof(line), stdin); ++card) {
        if (card % stride != offset) continue;
        ++cards;
        order = line[0] - 63;
        assert(order <= 32 && order >= need && order > 0);
        for (unsigned vertex = 0; vertex < order; ++vertex) adjacency[vertex] = 0;
        unsigned bit = 0;
        for (unsigned right = 1; right < order; ++right) {
            for (unsigned left = 0; left < right; ++left, ++bit) {
                int word = line[1 + bit / 6] - 63;
                assert(word >= 0 && word < 64);
                if ((word >> (5 - bit % 6)) & 1) {
                    adjacency[left] |= UINT32_C(1) << right;
                    adjacency[right] |= UINT32_C(1) << left;
                }
            }
        }
        uint32_t available = 0;
        for (unsigned vertex = 0; vertex < order; ++vertex) {
            degrees[vertex] = pop(adjacency[vertex]);
            if (degrees[vertex] >= minhost && degrees[vertex] <= 7) available |= UINT32_C(1) << vertex;
        }
        visit(available, 0, need, incidence);
    }
    fprintf(stderr, "cards=%u degree_sum_masks=%llu accepted=%llu offset=%u stride=%u\n", cards, tested, count, offset, stride);
}
