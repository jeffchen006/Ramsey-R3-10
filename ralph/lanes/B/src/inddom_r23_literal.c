#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int four_sets(const char *graph, int order, int target)
{
    uint64_t adjacent[62] = {0}, closed[62] = {0};
    uint64_t every = (UINT64_C(1) << order) - 1;
    int bit = 0;
    for (int high = 1; high < order; ++high)
        for (int low = 0; low < high; ++low, ++bit)
            if ((graph[1 + bit / 6] - 63) & (1 << (5 - (bit % 6)))) {
                adjacent[low] |= UINT64_C(1) << high;
                adjacent[high] |= UINT64_C(1) << low;
            }
    for (int index = 0; index < order; ++index)
        closed[index] = adjacent[index] | (UINT64_C(1) << index);
    int answer = 0;
    for (int left = 0; left < order; ++left)
        for (int middle = left + 1; middle < order; ++middle)
            for (int right = middle + 1; right < order; ++right)
                for (int last = right + 1; last < order; ++last) {
                    uint64_t rest = (UINT64_C(1) << middle) | (UINT64_C(1) << right) | (UINT64_C(1) << last);
                    uint64_t tail = (UINT64_C(1) << right) | (UINT64_C(1) << last);
                    if ((adjacent[left] & rest) || (adjacent[middle] & tail) ||
                        (adjacent[right] & (UINT64_C(1) << last))) continue;
                    if ((closed[left] | closed[middle] | closed[right] | closed[last]) != every) continue;
                    if (target >= 0 && __builtin_popcountll(adjacent[left]) + __builtin_popcountll(adjacent[middle]) +
                        __builtin_popcountll(adjacent[right]) + __builtin_popcountll(adjacent[last]) != target) continue;
                    ++answer;
                }
    return answer;
}

int main(int argc, char **argv)
{
    if (argc > 2) return 2;
    int target = argc == 2 ? atoi(argv[1]) : -1;
    char line[1024];
    long long rank = 0;
    while (fgets(line, sizeof line, stdin)) {
        int order = line[0] - 63;
        if (order < 1 || order > 62 || strlen(line) != (size_t)(2 + (order * (order - 1) / 2 + 5) / 6))
            return 2;
        printf("%lld\t%d\t%s", ++rank, four_sets(line, order, target), line);
    }
    return !rank || ferror(stdin);
}
