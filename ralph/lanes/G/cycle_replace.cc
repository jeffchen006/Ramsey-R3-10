#define main joint_replace_unused_main
#include "joint_replace.cc"
#undef main

struct Group {
    set_t first, second, either, both;
};

static long cycle_replace(const graph_t &graph, long index, const std::array<int, 4> &cycle,
                          int alpha, int min_degree, int lo, int hi, const Masks &all_top,
                          const Masks &all_next, bool tagged)
{
    set_t inside = 0;
    int old = 0;
    for (int vertex : cycle) {
        inside |= BIT(vertex);
        old += POP(graph.adj[vertex]) - 2;
    }
    lo -= g_edges(&graph) - old;
    hi -= g_edges(&graph) - old;
    int minimum = std::max({0, min_degree - 2, lo - 3 * (alpha - 2)});
    int maximum = std::min(alpha - 2, hi - 3 * minimum);
    if (minimum > maximum) return 0;
    set_t outside = (BIT(graph.n) - 1) & ~inside;
    set_t saturated = 0, upper1 = 0, need1 = 0, need2 = 0;
    for (set_t rest = outside; rest; rest &= rest - 1) {
        int vertex = CTZ(rest), degree = POP(graph.adj[vertex] & outside);
        if (degree + 2 < min_degree) return 0;
        if (degree >= alpha) saturated |= BIT(vertex);
        if (degree == alpha - 1) upper1 |= BIT(vertex);
        if (degree < min_degree) need1 |= BIT(vertex);
        if (degree < min_degree - 1) need2 |= BIT(vertex);
    }
    Masks top, next;
    for (set_t mask : all_top) if (!(inside & mask)) top.push_back(mask);
    for (set_t mask : all_next) if (!(inside & mask)) next.push_back(mask);
    Transversals attachments{graph, top, minimum, maximum, {}};
    attachments.search(0, outside & ~saturated, 0);
    std::array<std::vector<Group>, 128> pairs;
    for (int size1 = minimum; size1 <= maximum; ++size1)
        for (set_t first : attachments.by_size[size1]) {
            Masks missed;
            for (set_t witness : next) if (!(witness & first)) missed.push_back(witness);
            for (int size2 = size1; size2 <= maximum; ++size2) {
                int size = size1 + size2;
                if (size + 2 * maximum < lo || size + 2 * minimum > hi) continue;
                for (set_t second : attachments.by_size[size2]) {
                    if (size1 == size2 && second < first) continue;
                    set_t both = first & second;
                    if (both & upper1) continue;
                    if (std::any_of(missed.begin(), missed.end(), [second](set_t miss){ return !(miss & second); })) continue;
                    pairs[size].push_back({first, second, first | second, both});
                }
            }
        }
    long emitted = 0;
    for (int size1 = 2 * minimum; size1 <= 2 * maximum; ++size1)
        for (size_t idx1 = 0; idx1 < pairs[size1].size(); ++idx1) {
            const Group &first = pairs[size1][idx1];
            for (int size2 = std::max(size1, lo - size1); size2 <= std::min(2 * maximum, hi - size1); ++size2)
                for (size_t idx2 = size2 == size1 ? idx1 : 0; idx2 < pairs[size2].size(); ++idx2) {
                    const Group &second = pairs[size2][idx2];
                    if ((first.either & second.either) || (need1 & ~(first.either | second.either))
                        || (need2 & ~(first.both | second.both))) continue;
                    graph_t out = graph;
                    const std::array<set_t, 4> added{first.first, first.second, second.first, second.second};
                    for (set_t rest = outside; rest; rest &= rest - 1) out.adj[CTZ(rest)] &= ~inside;
                    for (int slot = 0; slot < 4; ++slot) {
                        out.adj[cycle[slot]] = (graph.adj[cycle[slot]] & inside) | added[slot];
                        for (set_t rest = added[slot]; rest; rest &= rest - 1) out.adj[CTZ(rest)] |= BIT(cycle[slot]);
                    }
                    if (tagged) std::printf("%ld\t%d\t%d\t%d\t%d\t", index, cycle[0], cycle[1], cycle[2], cycle[3]);
                    g6_write(stdout, &out);
                    ++emitted;
                }
        }
    return emitted;
}

int main(int argc, char **argv)
{
    if (argc != 5 && (argc != 6 || std::strcmp(argv[5], "tagged"))) return 2;
    int alpha = std::atoi(argv[1]), min_degree = std::atoi(argv[2]);
    int lo = std::atoi(argv[3]), hi = std::atoi(argv[4]);
    if (alpha < 2 || alpha > 62 || min_degree < 0 || min_degree > alpha || lo < 0 || lo > hi) return 2;
    char line[4096];
    long index = 0;
    while (std::fgets(line, sizeof line, stdin)) {
        graph_t graph;
        if (g6_read(line, &graph) || !g_trianglefree(&graph) || !alpha_le(&graph, alpha)) return 2;
        long emitted = 0;
        int cycles = 0;
        Masks top, next;
        list_independent(graph, BIT(graph.n) - 1, 0, alpha, top);
        list_independent(graph, BIT(graph.n) - 1, 0, alpha - 1, next);
        ++index;
        for (int first = 0; first < graph.n; ++first)
            for (int second = first + 1; second < graph.n; ++second) {
                set_t common = graph.adj[first] & graph.adj[second] & ~(BIT(first + 1) - 1);
                for (set_t left = common; left; left &= left - 1)
                    for (set_t right = left & (left - 1); right; right &= right - 1) {
                        ++cycles;
                        emitted += cycle_replace(graph, index, {first, second, CTZ(left), CTZ(right)}, alpha,
                                                 min_degree, lo, hi, top, next, argc == 6);
                    }
            }
        std::fprintf(stderr, "%ld e=%d cycles=%d outputs=%ld\n", index, g_edges(&graph), cycles, emitted);
    }
    return std::ferror(stdin) || std::ferror(stdout) ? 2 : 0;
}
