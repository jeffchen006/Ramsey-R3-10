#include "gutil.h"

#include <algorithm>
#include <array>
#include <vector>

class StemSearch {
    const graph_t &stem;
    const set_t full;
    const int alpha, minimum, budget, small, large;
    std::vector<set_t> demands;
    std::array<std::vector<set_t>, 10> rows;
    long long &nodes, &generated, &joins, &valid, &outputs;

    void independent(set_t allowed, set_t selected, int need)
    {
        if (!need) {
            demands.push_back(selected);
            return;
        }
        while (POP(allowed) >= need) {
            int next = CTZ(allowed);
            allowed &= allowed-1;
            independent(allowed & ~stem.adj[next], selected | BIT(next), need-1);
        }
    }

    void extend_row(set_t selected, set_t allowed, int size)
    {
        ++nodes;
        if (size > large || size+POP(allowed) < small) return;
        set_t smallest = 0;
        int best = 64;
        for (set_t demand : demands) {
            if (demand & selected) continue;
            set_t eligible = demand & allowed;
            if (!eligible || size == large) return;
            int count = POP(eligible);
            if (count < best) {
                smallest = eligible;
                best = count;
            }
        }
        if (!smallest) {
            if (size >= small) {
                rows[size].push_back(selected);
                ++generated;
            }
            if (size == large) return;
            smallest = allowed;
        }
        for (set_t bits = smallest; bits; bits &= bits-1) {
            int next = CTZ(bits);
            allowed &= ~BIT(next);
            extend_row(selected | BIT(next), allowed & ~stem.adj[next], size+1);
        }
    }

    bool critical_graph(const graph_t &graph) const
    {
        set_t all = BIT(graph.n)-1;
        for (int vertex = graph.n-1; vertex >= 0; --vertex) {
            for (set_t edges = graph.adj[vertex] & (BIT(vertex)-1); edges; edges &= edges-1) {
                int other = CTZ(edges);
                set_t residual = all & ~(graph.adj[vertex] | graph.adj[other]);
                if (!has_indep(graph.adj, residual, alpha-1)) return false;
            }
        }
        return true;
    }

public:
    StemSearch(const graph_t &base, int bound, int low, int edge_budget, long long &n,
               long long &g, long long &j, long long &v, long long &o)
        : stem(base), full(BIT(base.n)-1), alpha(bound), minimum(low), budget(edge_budget),
          small(std::max(low, edge_budget-bound)), large(std::min(bound, edge_budget-low)),
          nodes(n), generated(g), joins(j), valid(v), outputs(o) {}

    void run()
    {
        if (small > large) return;
        set_t eligible = 0, need_one = 0, need_two = 0, only_one = 0;
        for (int vertex = 0; vertex < stem.n; ++vertex) {
            int degree = POP(stem.adj[vertex]);
            if (degree < minimum-2 || degree > alpha) return;
            if (degree < alpha) eligible |= BIT(vertex);
            if (degree < minimum) need_one |= BIT(vertex);
            if (degree < minimum-1) need_two |= BIT(vertex);
            if (degree == alpha-1) only_one |= BIT(vertex);
        }
        if (need_two & ~eligible) return;
        set_t blocked = 0;
        for (set_t bits = need_two; bits; bits &= bits-1) blocked |= stem.adj[CTZ(bits)];
        if (blocked & need_two) return;
        independent(full, 0, alpha);
        extend_row(need_two, eligible & ~(need_two | blocked), POP(need_two));
        for (int length = small; length <= budget/2 && length <= large; ++length) {
            int partner = budget-length;
            if (partner < small || partner > large) continue;
            for (size_t first_no = 0; first_no < rows[length].size(); ++first_no) {
                set_t first = rows[length][first_no];
                for (size_t second_no = length == partner ? first_no : 0;
                     second_no < rows[partner].size(); ++second_no) {
                    set_t second = rows[partner][second_no];
                    ++joins;
                    if ((first & second & only_one) || (need_one & ~(first | second))) continue;
                    if (has_indep(stem.adj, full & ~(first | second), alpha-1)) continue;
                    ++valid;
                    graph_t candidate = stem;
                    const int left = stem.n, right = stem.n+1;
                    candidate.n += 2;
                    candidate.adj[left] = first;
                    candidate.adj[right] = second;
                    for (set_t bits = first; bits; bits &= bits-1) candidate.adj[CTZ(bits)] |= BIT(left);
                    for (set_t bits = second; bits; bits &= bits-1) candidate.adj[CTZ(bits)] |= BIT(right);
                    if (!critical_graph(candidate)) continue;
                    ++outputs;
                    g6_write(stdout, &candidate);
                }
            }
        }
    }
};

int main(int argc, char **argv)
{
    if (argc != 4) return 2;
    int alpha = atoi(argv[1]), minimum = atoi(argv[2]), size = atoi(argv[3]);
    if (alpha < 2 || alpha > 9 || minimum < 0 || minimum > alpha || size < 1 || size > 300) return 2;
    graph_t stem;
    long long count = 0, nodes = 0, rows = 0, joins = 0, valid = 0, outputs = 0;
    char line[1024];
    while (fgets(line, sizeof(line), stdin)) {
        int order = line[0]-63;
        if (order < 2 || order > 60 || strlen(line) != size_t(2+(order*(order-1)/2+5)/6) ||
            g6_read(line, &stem) || !g_trianglefree(&stem) || !alpha_le(&stem, alpha)) return 1;
        ++count;
        StemSearch search(stem, alpha, minimum, size-g_edges(&stem), nodes, rows, joins, valid, outputs);
        search.run();
    }
    fprintf(stderr, "nonadjacent stems=%lld nodes=%lld rows=%lld joins=%lld valid=%lld outputs=%lld\n",
            count, nodes, rows, joins, valid, outputs);
    return ferror(stdin) || fflush(stdout) == EOF;
}
