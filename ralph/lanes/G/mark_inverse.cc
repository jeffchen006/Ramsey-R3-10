#include "gutil.h"
#include <array>
#include <cassert>
#include <ctime>

static graph_t upper;
static int width, private_size, added, remaining, alpha;
static long long rows, combinations, structural, accepted;
static std::array<int, 10> mark;
static std::array<int, 64> slack;
static std::array<set_t, 64> compatible;

static void evaluate(set_t selected)
{
    ++combinations;
    std::array<int, 64> singles{};
    std::array<set_t, 64> seen{};
    for (set_t exterior = (BIT(upper.n) - 1) ^ selected; exterior; exterior &= exterior - 1) {
        int vertex = CTZ(exterior);
        set_t signature = upper.adj[vertex] & selected;
        if (!signature) return;
        int first = CTZ(signature);
        signature &= signature - 1;
        if (!signature) {
            if (++singles[first] > private_size) return;
        } else {
            if ((signature & (signature - 1)) || (seen[first] & signature)) return;
            seen[first] |= signature;
        }
    }
    graph_t lower = upper;
    int uncovered = 0;
    for (int index = 0; index < width; ++index) {
        int first = mark[index];
        if (singles[first] != private_size) return;
        for (int other = index + 1; other < width; ++other) {
            int second = mark[other];
            bool covered = (seen[first] & BIT(second)) != 0;
            uncovered += !covered;
            if (upper.adj[first] & BIT(second)) {
                if (covered) return;
                lower.adj[first] &= ~BIT(second);
                lower.adj[second] &= ~BIT(first);
            }
        }
    }
    if (uncovered != added + remaining) return;
    ++structural;
    bool valid = alpha_le(&lower, alpha);
    accepted += valid;
    printf("%lld\t", rows);
    for (int index = 0; index < width; ++index) printf("%s%d", index ? "," : "", mark[index]);
    printf("\t%d\t", valid);
    g6_write(stdout, &lower);
}

static void visit(set_t choices, set_t selected, int depth, int used, int deficit)
{
    if (depth == width) {
        if (used == added && deficit == 2 * remaining) evaluate(selected);
        return;
    }
    while (POP(choices) >= width - depth) {
        int vertex = CTZ(choices);
        choices &= choices - 1;
        int next_used = used + POP(upper.adj[vertex] & selected);
        int next_deficit = deficit + slack[vertex];
        if (next_used > added || next_deficit > 2 * remaining) continue;
        mark[depth] = vertex;
        visit(choices & compatible[vertex], selected | BIT(vertex), depth + 1, next_used, next_deficit);
    }
}

int main(int argc, char **argv)
{
    if (argc != 6 && argc != 7) return 2;
    width = atoi(argv[1]);
    private_size = atoi(argv[2]);
    added = atoi(argv[3]);
    remaining = atoi(argv[4]);
    alpha = atoi(argv[5]);
    int target_edges = argc == 7 ? atoi(argv[6]) : -1;
    assert(width >= 2 && width <= 10 && private_size >= 1 && added >= 1 && remaining >= 0);
    char line[1024];
    std::clock_t start = std::clock();
    while (fgets(line, sizeof(line), stdin)) {
        int order = line[0] - 63;
        assert(order >= 1 && order <= 62);
        int length = 1 + (order * (order - 1) / 2 + 5) / 6;
        assert(strcspn(line, "\r\n") == static_cast<size_t>(length));
        for (int index = 0; index < length; ++index) assert(line[index] >= 63 && line[index] <= 126);
        assert(g6_read(line, &upper) == 0 && g_trianglefree(&upper));
        assert(upper.n == width * (private_size + 1) + width * (width - 1) / 2 - added - remaining);
        ++rows;
        set_t pool = 0;
        for (int vertex = 0; vertex < upper.n; ++vertex) {
            int degree = POP(upper.adj[vertex]);
            slack[vertex] = width + private_size - 1 - degree;
            if (slack[vertex] >= 0 && slack[vertex] <= remaining) pool |= BIT(vertex);
            compatible[vertex] = 0;
        }
        assert(target_edges < 0 || g_edges(&upper) == target_edges);
        for (set_t first_pool = pool; first_pool; first_pool &= first_pool - 1) {
            int first = CTZ(first_pool);
            for (set_t second_pool = first_pool & (first_pool - 1); second_pool; second_pool &= second_pool - 1) {
                int second = CTZ(second_pool);
                bool edge = (upper.adj[first] & BIT(second)) != 0;
                int common = POP(upper.adj[first] & upper.adj[second]);
                if (!edge && (common > added || (!common && (!slack[first] || !slack[second])))) continue;
                compatible[first] |= BIT(second);
            }
        }
        visit(pool, 0, 0, 0, 0);
    }
    fprintf(stderr, "rows=%lld candidate_sets=%lld structural=%lld accepted=%lld cpu=%.3f\n",
            rows, combinations, structural, accepted, double(std::clock() - start) / CLOCKS_PER_SEC);
}
