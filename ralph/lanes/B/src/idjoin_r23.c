#include "gutil.h"

typedef struct {
    set_t masks[70000];
    int size;
} rows_t;

static void rows(const graph_t *graph, set_t remaining, set_t chosen, set_t dominated,
                 set_t all, int need, rows_t *out)
{
    if (!need) {
        if (dominated == all) {
            if (out->size == 70000) exit(2);
            out->masks[out->size++] = chosen;
        }
        return;
    }
    while (POP(remaining) >= need) {
        int index = CTZ(remaining);
        remaining &= remaining - 1;
        rows(graph, remaining & ~graph->adj[index], chosen | BIT(index),
             dominated | graph->adj[index] | BIT(index), all, need - 1, out);
    }
}

static int degree_room(set_t row, set_t overlap, set_t low_three, set_t low_four)
{
    if (overlap & low_three) return 0;
    int needed = 2 * POP(row & low_three) + POP(row & low_four & ~overlap);
    return needed <= 2 * (2 - POP(overlap));
}

int main(int argc, char **argv)
{
    if (argc != 2 && argc != 3) return 2;
    int size = atoi(argv[1]);
    int two_paths = argc == 3 && !strcmp(argv[2], "2p3");
    int use_degrees = argc == 2 || two_paths;
    if (argc == 3 && !two_paths && strcmp(argv[2], "no-degree")) return 2;
    if (size < 1 || size > 5) return 2;
    char line[1024];
    int nrows = 0;
    while (fgets(line, sizeof line, stdin)) {
        graph_t graph;
        if (g6_read(line, &graph) || graph.n > 21) return 2;
        set_t all = BIT(graph.n) - 1, low_three = 0, low_four = 0, too_low = 0;
        set_t degree_five = 0, degree_six = 0;
        for (int site = 0; site < graph.n; ++site) {
            int degree = POP(graph.adj[site]);
            if (degree <= 2) too_low |= BIT(site);
            if (degree == 3) low_three |= BIT(site);
            if (degree == 4) low_four |= BIT(site);
            if (degree == 5) degree_five |= BIT(site);
            if (degree == 6) degree_six |= BIT(site);
        }
        rows_t sets;
        sets.size = 0;
        rows(&graph, use_degrees ? all & ~too_low : all, 0, 0, all, size, &sets);
        unsigned long long counts[4] = {0};
        for (int first = 0; first < sets.size; ++first) {
            set_t left = sets.masks[first];
            for (int second = first + 1; second < sets.size; ++second) {
                set_t middle = sets.masks[second], left_mid = left & middle;
                if (POP(left_mid) > 1) continue;
                for (int third = second + 1; third < sets.size; ++third) {
                    set_t right = sets.masks[third], left_right = left & right, mid_right = middle & right;
                    if (POP(left_right) > 1 || POP(mid_right) > 1 || (left_mid & right)) continue;
                    if (use_degrees && (!degree_room(left, left_mid | left_right, low_three, low_four) ||
                        !degree_room(middle, left_mid | mid_right, low_three, low_four) ||
                        !degree_room(right, left_right | mid_right, low_three, low_four))) continue;
                    int j = !!left_mid + !!left_right + !!mid_right;
                    if (two_paths) {
                        if (j != 1) continue;
                        set_t used = left | middle | right;
                        set_t singles = used & ~(left_mid | left_right | mid_right);
                        if ((low_three | too_low) & ~used) continue;
                        set_t candidates = degree_six & ~used;
                        int feasible = 0;
                        while (candidates) {
                            int center = CTZ(candidates);
                            candidates &= candidates - 1;
                            set_t neighbors = graph.adj[center];
                            if (neighbors & ~(singles & (degree_five | degree_six))) continue;
                            set_t low_neighbors = neighbors & degree_five;
                            set_t prohibited = (degree_six & ~BIT(center)) | (degree_five & ~singles);
                            while (low_neighbors && !(graph.adj[CTZ(low_neighbors)] & prohibited))
                                low_neighbors &= low_neighbors - 1;
                            if (!low_neighbors) { feasible = 1; break; }
                        }
                        if (!feasible) continue;
                    }
                    ++counts[j];
                }
            }
        }
        printf("%d\t%d\t%llu\t%llu\t%llu\t%llu\t%s", ++nrows, sets.size,
               counts[0], counts[1], counts[2], counts[3], line);
    }
    return !nrows || ferror(stdin);
}
