#include <stdint.h>
#include <string.h>

typedef struct { uint64_t words[4]; } mask_t;

typedef struct {
    const uint64_t *known;
    const uint16_t *variables;
    mask_t *output;
    unsigned count, limit;
    int width;
} context_t;

static int cuts(context_t *context, uint64_t pending, uint64_t picked, int need, mask_t row)
{
    if (!need) {
        if (context->count == context->limit) return -1;
        context->output[context->count++] = row;
        return 0;
    }
    while (__builtin_popcountll(pending) >= need) {
        int vertex = __builtin_ctzll(pending);
        uint64_t current = UINT64_C(1) << vertex;
        pending ^= current;
        mask_t next = row;
        for (uint64_t prior = picked; prior; prior &= prior-1) {
            int actor = __builtin_ctzll(prior);
            unsigned variable = context->variables[vertex*32 + actor];
            if (variable) {
                --variable;
                next.words[variable / 64] |= UINT64_C(1) << (variable % 64);
            }
        }
        int size = 0;
        for (int word = 0; word < 4; ++word) size += __builtin_popcountll(next.words[word]);
        if (size <= context->width && cuts(context, pending & ~context->known[vertex], picked | current,
                                         need-1, next) < 0) return -1;
    }
    return 0;
}

int m11_fast_cuts(const uint64_t *known, const uint16_t *variables, uint64_t domain,
                  int need, int width, uint64_t *output, unsigned limit)
{
    context_t context = { .known=known, .variables=variables, .output=(mask_t *)output, .count=0,
                          .limit=limit, .width=width };
    mask_t row = {{0}};
    return cuts(&context, domain, 0, need, row) < 0 ? -1 : (int)context.count;
}
