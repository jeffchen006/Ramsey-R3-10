#include <stdint.h>

#define BIT(vertex) (UINT64_C(1) << (vertex))
#define POP(mask) __builtin_popcountll(mask)
#define NEXT(mask) __builtin_ctzll(mask)

static int update(int order, int alpha, int target, const uint64_t *lower, uint64_t *upper)
{
    uint64_t saturated = 0, two_hop[32] = {0};
    int forced = 0, over_degree = 0, triangle = 0;
    for (int vertex = 0; vertex < order; ++vertex) {
        int degree = POP(lower[vertex]);
        forced += degree;
        over_degree |= degree > alpha;
        if (degree == alpha) saturated |= BIT(vertex);
        for (uint64_t neighbors = lower[vertex]; neighbors; neighbors &= neighbors-1)
            two_hop[vertex] |= lower[NEXT(neighbors)];
        triangle |= !!(two_hop[vertex] & lower[vertex]);
    }
    if (forced > 2 * target) return 2;
    if (triangle) return 3;
    if (over_degree) return 4;
    int eligible = 0;
    for (int vertex = 0; vertex < order; ++vertex) {
        if (forced == 2 * target || (saturated & BIT(vertex))) upper[vertex] = lower[vertex];
        else upper[vertex] &= lower[vertex] | ~(saturated | two_hop[vertex]);
        eligible += POP(upper[vertex]);
    }
    return eligible < 2 * target ? 5 : 0;
}

int check_trace74(int order, int alpha, int target, int result, uint64_t terminal,
                  const uint64_t *steps, int count, uint64_t *lower, uint64_t *upper)
{
    if (order < 1 || order > 32 || alpha < 0 || alpha > 32 || target < 0 || target > 496 ||
        count < 0 || count > 496 || result < 0 || result > 5) return 0;
    uint64_t limit = BIT(order);
    for (int vertex = 0; vertex < order; ++vertex) {
        if (upper[vertex] >= limit || (upper[vertex] & BIT(vertex)) || (lower[vertex] & ~upper[vertex]))
            return 0;
        for (uint64_t eligible = upper[vertex]; eligible; eligible &= eligible-1) {
            int other = NEXT(eligible);
            if (!(upper[other] & BIT(vertex)) ||
                !!(lower[other] & BIT(vertex)) != !!(lower[vertex] & BIT(other))) return 0;
        }
    }
    for (int index = 0; index < count; ++index) {
        if (update(order, alpha, target, lower, upper)) return 0;
        uint64_t code = steps[index], witness = code >> 10;
        int right = code & 31, left = (code >> 5) & 31;
        if (left >= right || right >= order || witness >= limit || POP(witness) != alpha + 1) return 0;
        uint64_t endpoints = BIT(left) | BIT(right);
        if ((witness & endpoints) != endpoints || !(upper[left] & BIT(right)) || (lower[left] & BIT(right)))
            return 0;
        for (uint64_t vertices = witness; vertices; vertices &= vertices-1) {
            int vertex = NEXT(vertices);
            uint64_t relevant = (endpoints & BIT(vertex)) ? witness & ~endpoints : witness;
            if (upper[vertex] & relevant) return 0;
        }
        lower[left] |= BIT(right);
        lower[right] |= BIT(left);
    }
    int bound = update(order, alpha, target, lower, upper);
    if (result != 1) return bound == result && terminal == 0;
    if (bound || !terminal || terminal >= limit || POP(terminal) != alpha + 1) return 0;
    for (uint64_t vertices = terminal; vertices; vertices &= vertices-1)
        if (upper[NEXT(vertices)] & terminal) return 0;
    return 1;
}
