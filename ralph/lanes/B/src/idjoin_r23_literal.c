#include <stdint.h>
#include <stdio.h>
#include <string.h>

static int mask_size(uint32_t sites)
{
    return __builtin_popcount(sites);
}

static uint32_t bit(int site)
{
    return UINT32_C(1) << site;
}

int main(void)
{
    char line[64];
    int count = 0;
    while (fgets(line, sizeof line, stdin)) {
        if (line[0] != 'T' || strlen(line) != 37) return 2;
        uint32_t adjacent[21] = {0}, closed[21] = {0};
        for (int vertex = 1; vertex < 21; ++vertex)
            for (int other = 0; other < vertex; ++other) {
                int pos = vertex * (vertex - 1) / 2 + other;
                if ((line[1 + pos / 6] - 63) & (32 >> (pos % 6))) {
                    adjacent[vertex] |= bit(other);
                    adjacent[other] |= bit(vertex);
                }
            }
        int degree[21];
        for (int site = 0; site < 21; ++site) {
            degree[site] = mask_size(adjacent[site]);
            closed[site] = adjacent[site] | bit(site);
        }
        uint32_t all = bit(21) - 1;
        uint32_t rows[20349];
        int top = 0;
        for (int first = 0; first < 21; ++first)
            for (int second = first + 1; second < 21; ++second)
                for (int third = second + 1; third < 21; ++third)
                    for (int fourth = third + 1; fourth < 21; ++fourth)
                        for (int fifth = fourth + 1; fifth < 21; ++fifth) {
                            int sites[] = {first, second, third, fourth, fifth};
                            uint32_t tuple = bit(first) | bit(second) | bit(third) | bit(fourth) | bit(fifth);
                            uint32_t seen = 0;
                            int bad = 0;
                            for (int index = 0; index < 5; ++index) {
                                int site = sites[index];
                                if (degree[site] < 3 || (tuple & adjacent[site])) { bad = 1; break; }
                                seen |= closed[site];
                            }
                            if (!bad && seen == all) rows[top++] = tuple;
                        }
        unsigned long long bins[4] = {0};
        for (int first = 0; first < top; ++first)
            for (int second = first + 1; second < top; ++second)
                for (int third = second + 1; third < top; ++third) {
                    uint32_t a = rows[first], b = rows[second], c = rows[third];
                    if (mask_size(a & b) > 1 || mask_size(a & c) > 1 || mask_size(b & c) > 1 || (a & b & c))
                        continue;
                    int cost[3] = {0}, overlaps = 0, bad = 0;
                    for (int site = 0; site < 21; ++site) {
                        uint32_t marker = bit(site);
                        int hits[] = {!!(a & marker), !!(b & marker), !!(c & marker)};
                        int multiplicity = hits[0] + hits[1] + hits[2];
                        if (multiplicity == 2) {
                            if (degree[site] < 4) { bad = 1; break; }
                            ++overlaps;
                        }
                        int charge = multiplicity == 2 ? 2 : (degree[site] < 5 ? 5 - degree[site] : 0);
                        for (int index = 0; index < 3; ++index) cost[index] += hits[index] * charge;
                    }
                    if (!bad && cost[0] <= 4 && cost[1] <= 4 && cost[2] <= 4) ++bins[overlaps];
                }
        printf("%d\t%d\t%llu\t%llu\t%llu\t%llu\t%s", ++count, top,
               bins[0], bins[1], bins[2], bins[3], line);
    }
    return !count || ferror(stdin);
}
